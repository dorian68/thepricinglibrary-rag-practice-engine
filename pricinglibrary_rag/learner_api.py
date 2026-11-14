"""User-facing discovery and canonical calculations shared by UI and CLI."""
from __future__ import annotations

from fastapi import FastAPI, HTTPException, Request, Response
from pydantic import BaseModel, ConfigDict, Field

from .canonical_tools import TOOL_PLANS, ToolUnavailable, list_canonical_tools, run_canonical_tool, tool_example, tool_name
from .course_publication import accepted_english_course
from .platform_store import PlatformStore
from .security import IDENTITY, AuthenticatedIdentity

SCHEMA = "tpl.learner.catalog.v1"
COURSES = {
    "black-scholes": ("Black-Scholes Model", 8, "starter"), "yield-curves": ("Yield Curves", 9, "starter"),
    "greeks": ("Option Greeks", 9, "starter"), "rates-swaps": ("Rates and Swaps", 9, "starter"),
    "fixed-income-bonds": ("Fixed Income Bonds", 8, "starter"), "implied-vol": ("Implied Volatility", 9, "student"),
    "credit-derivatives": ("Credit Derivatives", 8, "student"), "market-risk-var": ("Market Risk", 9, "student"),
    "exotics": ("Exotic Options", 9, "pro"), "monte-carlo": ("Monte Carlo Methods", 10, "pro"),
    "stochastic": ("Stochastic Calculus", 10, "pro"), "structured-products": ("Structured Products", 10, "pro"),
}


class ToolBody(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)
    input: dict
    format: str = Field(default="json", max_length=32)


class CompleteBody(BaseModel):
    model_config = ConfigDict(extra="forbid")
    module_index: int = Field(strict=True, ge=0, le=63)


def register_learner_routes(app: FastAPI, services, security) -> None:
    platform = PlatformStore(services.settings.db_path)

    def signed(request: Request) -> AuthenticatedIdentity:
        security.authorize(request, IDENTITY)
        identity = getattr(request.state, "tpl_identity", None)
        if not isinstance(identity, AuthenticatedIdentity):
            raise HTTPException(401, "A signed learner session is required.")
        return identity

    def gate(request: Request, minimum: str) -> AuthenticatedIdentity | None:
        if minimum == "free":
            return None
        identity = signed(request)
        if identity.role != "operator":
            ent = services.store.get_entitlement_by_user_id(identity.user_id) or {}
            rank = {"free": 0, "starter": 1, "student": 2, "pro": 3}
            if ent.get("status") != "active" or rank.get(ent.get("plan"), 0) < rank[minimum]:
                raise HTTPException(403, f"Active {minimum} entitlement required.")
        return identity

    def private(response: Response) -> None:
        response.headers["Cache-Control"] = "private, no-store"
        response.headers["Vary"] = "Authorization"

    def course(identifier: str):
        if identifier not in COURSES:
            raise HTTPException(404, "Course not found.")
        return COURSES[identifier]

    @app.get("/learner/catalog")
    def catalog() -> dict:
        from .api import COURSE_SCRIPT_FILES
        root = services.settings.course_scripts_dir
        def languages(cid):
            if root is None:
                return []
            filename = COURSE_SCRIPT_FILES[cid]
            available = ["fr"] if (root / filename).is_file() else []
            if accepted_english_course(root, filename) is not None:
                available.append("en")
            return available
        return {"schema_version": SCHEMA,
                "courses": [{"id": cid, "title": v[0], "module_count": v[1], "minimum_plan": v[2],
                             "language": "fr", "available_languages": languages(cid), "preview_available": cid == "black-scholes"} for cid, v in COURSES.items()],
                "tools": list_canonical_tools(),
                "interview_catalog": "/interview/catalog", "learning_catalog": "/learning/catalog",
                "notice": "Course completion is self-declared activity; interview checks and reasoning self-reviews are separate."}

    @app.get("/learner/me")
    def me(request: Request, response: Response) -> dict:
        identity = signed(request)
        private(response)
        return {"user_id": identity.user_id, "email": identity.email, "role": identity.role,
                "entitlement": services.billing.entitlement(user_id=identity.user_id)}

    @app.get("/learner/courses/{course_id}/preview")
    def preview(course_id: str) -> dict:
        course(course_id)
        if course_id != "black-scholes":
            raise HTTPException(404, "No public preview exists for this course.")
        return {"course_id": course_id, "language": "en", "preview_only": True,
                "content": "# European call preview\n\nA European call pays max(S_T-K,0) at expiry. "
                "Under constant volatility and continuous rates/dividends, its Black-Scholes-Merton value is "
                "C=S exp(-qT)N(d1)-K exp(-rT)N(d2).\n\nUse the free Black-Scholes tool to check a ticket, "
                "then try the English Interview Lab. This short preview does not include the full private course.",
                "next": "/interview/cases/call-quote"}

    @app.get("/learner/courses/{course_id}/state")
    def course_state(course_id: str, request: Request, response: Response) -> dict:
        _, count, _ = course(course_id)
        identity = signed(request)
        private(response)
        progress = platform.progress_summary(identity.user_id)
        completed = [i for i in range(count) if f"{course_id}#L{i}" in progress["completed_lessons"]]
        position = next((row["module_index"] for row in progress["course_positions"] if row["course"] == course_id), None)
        next_incomplete = next((i for i in range(count) if i not in completed), None)
        return {"course_id": course_id, "module_count": count, "completed_modules": completed,
                "last_module_index": position, "resume_module_index": position if position is not None else (next_incomplete or 0),
                "next_incomplete_module": next_incomplete, "progress_kind": "self_declared_completion"}

    @app.post("/learner/courses/{course_id}/complete")
    def complete(course_id: str, body: CompleteBody, request: Request, response: Response) -> dict:
        _, count, plan = course(course_id)
        identity = signed(request)
        if body.module_index >= count:
            raise HTTPException(422, "Module index is outside this course.")
        if not (course_id == "black-scholes" and body.module_index < 2):
            gate(request, plan)
        private(response)
        result = platform.record_progress(user_id=identity.user_id, username=None, kind="lesson",
                                          ref=f"{course_id}#L{body.module_index}", score=None,
                                          meta={"course": course_id, "module_index": body.module_index})
        return {"activity": result, "progress_kind": "self_declared_completion", "mastery_awarded": False}

    @app.get("/learner/tools")
    def tools() -> dict:
        return {"tools": list_canonical_tools()}

    @app.get("/learner/tools/{name}/example")
    def example(name: str) -> dict:
        try:
            return {"tool": tool_name(name), "input": tool_example(name), "data_kind": "synthetic_teaching_inputs"}
        except ValueError as exc:
            raise HTTPException(404, str(exc)) from exc

    @app.post("/learner/tools/{name}")
    def calculate(name: str, body: ToolBody, request: Request, response: Response):
        try:
            resolved = tool_name(name)
        except ValueError as exc:
            raise HTTPException(404, str(exc)) from exc
        gate(request, TOOL_PLANS[resolved])
        private(response)
        try:
            output = run_canonical_tool(resolved, body.input, body.format)
        except ToolUnavailable as exc:
            raise HTTPException(503, str(exc)) from exc
        except (ValueError, TypeError, KeyError, ArithmeticError, RuntimeError) as exc:
            raise HTTPException(422, str(exc)) from exc
        if isinstance(output, str):
            return Response(output, media_type="text/csv", headers={"Cache-Control": "private, no-store", "Vary": "Authorization"})
        return output

    @app.get("/learner/services")
    def services_status() -> dict:
        return {"schema_version": "tpl.services.v1",
                "mentoring": {"status": "not_bookable", "reason": "No verified, bookable mentor service is configured."},
                "qa": {"status": "conditional", "reason": "Human support availability is not certified by this API."},
                "support": {"status": "issue_recording_available", "route": "/platform/bug-reports", "email_delivery_verified": False},
                "jobs": {"published": len(platform.list_jobs(limit=100)), "apply_route": "/platform/jobs/{id}/apply"},
                "blog": {"published": len(platform.list_blog(limit=100))},
                "billing": {"configured": services.settings.billing_configured, "rights_cleared": services.settings.source_rights_cleared},
                "notebooks": {"catalog_route": "/learning/catalog", "arbitrary_server_code": False},
                "limits": ["A capability response is not a real purchase, delivered email, human review or market-demand measurement."]}
