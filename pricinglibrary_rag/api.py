from __future__ import annotations

import hashlib
import logging
import re
import time
import unicodedata
import uuid

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, Response, StreamingResponse
from pydantic import BaseModel, ConfigDict, Field

from .agui import run_agui_stream
from .billing import BillingError, STARTER_KIT_PRODUCT_ID
from .desk import DeskOrchestrator
from .factory import Services, build_services
from .observability import ProductionMetrics
from .platform_store import PlatformStore
from .calculators import ExerciseInputError
from .security import MEMBER, ApiSecurity, AuthenticatedIdentity
from .interview_lab import register_interview_routes


COURSE_SCRIPT_FILES = {
    "black-scholes": "vanilla-options-quote.md",
    "yield-curves": "yield-curve-bootstrapping.md",
    "greeks": "options-book-greeks-pnl.md",
    "rates-swaps": "rates-swaps-dv01.md",
    "fixed-income-bonds": "fixed-income-bonds-duration.md",
    "implied-vol": "implied-volatility-smile.md",
    "credit-derivatives": "credit-derivatives-cds.md",
    "market-risk-var": "market-risk-var-stress.md",
    "exotics": "barrier-options-gap-risk.md",
    "monte-carlo": "monte-carlo-pricing.md",
    "stochastic": "stochastic-calculus-for-hedging.md",
    "structured-products": "structured-products-autocall.md",
}
COURSE_MODULE_COUNTS = {
    "black-scholes":8,"yield-curves":9,"greeks":9,"rates-swaps":9,
    "fixed-income-bonds":8,"implied-vol":9,"credit-derivatives":8,
    "market-risk-var":9,"exotics":9,"monte-carlo":10,"stochastic":10,"structured-products":10,
}

if len(set(COURSE_SCRIPT_FILES.values())) != len(COURSE_SCRIPT_FILES):
    raise RuntimeError("Every commercial course id must map to a unique course script.")

_COURSE_REFERENCE_TERMS = {
    "vanilla-options-quote": ("option", "black-scholes", "call", "put", "delta", "vega", "volatil"),
    "yield-curve-bootstrapping": ("curve", "courbe", "discount", "forward", "swap", "zero", "yield", "taux"),
    "options-book-greeks-pnl": ("delta", "gamma", "vega", "theta", "greek", "hedg", "option"),
    "rates-swaps-dv01": ("swap", "dv01", "pv01", "rate", "taux", "annuity", "forward", "libor", "caplet"),
    "fixed-income-bonds-duration": ("bond", "obligation", "duration", "convex", "dv01", "yield", "coupon", "mortgage"),
    "implied-volatility-smile": ("volatil", "smile", "skew", "svi", "implied", "delta strike"),
    "credit-derivatives-cds": ("credit", "cds", "default", "spread", "counterparty", "recovery"),
    "market-risk-var-stress": ("value at risk", "var", "stress", "market risk", "tail", "expected shortfall"),
    "barrier-options-gap-risk": ("barrier", "knock", "gap", "delta", "option"),
    "monte-carlo-pricing": ("monte carlo", "simulation", "brownian", "option", "hedg", "path", "variance reduction"),
    "stochastic-calculus-for-hedging": ("stochastic", "brownian", "ito", "girsanov", "martingale", "hedg", "risk-neutral"),
    "structured-products-autocall": ("autocall", "structured", "barrier", "coupon", "downside", "put", "note", "redemption"),
}

# Client references are deliberately fail-closed. Each anchor identifies a
# reviewed excerpt and records the corpus location that supports it. Adding a
# new public reference therefore requires an explicit review instead of merely
# matching one broad topic keyword.
_COURSE_REFERENCE_ALLOWLIST: dict[str, tuple[tuple[str, str, int], ...]] = {
    "barrier-options-gap-risk": (
        ("before the maturity if the underlying asset", "5fef34696d4919ee321eedc2", 981),
        ("standard calls and puts have payoffs", "8f292c84fb20b98ec20d68a9", 241),
    ),
    "credit-derivatives-cds": (
        ("as the hazard rate", "cfaa75bef8262d25be5eeea5", 457),
        ("the cds consists of two legs", "3c7b933fc836ae04d190683d", 103),
        ("the value of a cds position is primarily affected", "5fef34696d4919ee321eedc2", 1434),
    ),
    "fixed-income-bonds-duration": (
        ("concept of a bond", "7332bf13ceb6be957f7a99e9", 515),
        ("mortgage bond", "455d02c4f156cc344d2c935b", 256),
        ("many market participants take dv01", "0c0b188db8b70c2604072901", 110),
    ),
    "implied-volatility-smile": (
        ("risk reversal contract describes the skew", "a60f9e162aea3fecee16e7cb", 66),
        ("options of different maturities also display", "cd1a58bae03e584bd8d907fa", 110),
        ("in the sticky strike approach", "078c587900548fc376d955c0", 201),
    ),
    "market-risk-var-stress": (
        ("banks assume market risk", "4197a76dff2f5a4081a5400e", 190),
        ("single number to look at", "cd1a58bae03e584bd8d907fa", 154),
    ),
    "monte-carlo-pricing": (
        ("antithetic variate technique consists", "c6842f2edd337cf58fa6e105", 355),
        ("fair comparison between estimators", "51991c731c0b36214c36fefa", 113),
        ("after m simulations", "4fa5876dbb1e2b66501f85a5", 151),
    ),
    "options-book-greeks-pnl": (
        ("discrete delta hedging can cause", "a030fbe888bd4a5323e3fc77", 81),
        ("theta is greater", "b80113029d4ff56d2c7a69ad", 304),
    ),
    "rates-swaps-dv01": (
        ("fixed rate in such a swap", "04b8571bb2eb15a84225f866", 294),
        ("swaps are valued on the basis", "17771555d8b712b4715966e1", 35),
        ("to calculate the cash flows", "47465261a3bbab12ec38aec3", 161),
    ),
    "stochastic-calculus-for-hedging": (
        ("the theoretical elimination of risk by delta hedging", "7130adb5f703b1a2afaee6b0", 72),
        ("discrete delta hedging can cause", "a030fbe888bd4a5323e3fc77", 81),
        ("the delta hedge is implemented daily", "455d02c4f156cc344d2c935b", 312),
    ),
    "structured-products-autocall": (
        ("payoff of worst of autocallables", "04b8571bb2eb15a84225f866", 211),
        ("financial engineering provides ways to construct", "0c0b188db8b70c2604072901", 751),
        ("zero coupon bond were that of any non government issuer", "aaf56220b6593cc2cbef21d4", 205),
    ),
    "vanilla-options-quote": (
        ("peak vega on a vanilla option", "a60f9e162aea3fecee16e7cb", 58),
        ("mathematical description of option valuation", "a030fbe888bd4a5323e3fc77", 47),
        ("capture the salient features of an option", "0f57ddde5130ec63b0bf251c", 265),
        ("purchase the cheaper portfolio", "cd1a58bae03e584bd8d907fa", 49),
    ),
    "yield-curve-bootstrapping": (
        ("distinguishing forward curves from discount curves", "99c3bae30c77ead757e078b0", 238),
        ("these two curves are interchangeable", "af20d09bf6b73c8360a5e541", 153),
        ("best fit", "3c7b933fc836ae04d190683d", 349),
    ),
}
_COURSE_REFERENCE_NOISE_TERMS = (
    "references and bibliography",
    "references bibliography",
    "bibliography",
    "journal of finance",
    "journal of derivatives",
    "working paper",
    "doi.org",
    "the author(s)",
    "isbn",
)

_COURSE_BACK_OFFICE_SECTION_RE = re.compile(
    r"^##[ \t]+Source Appendix \(back-office\)[ \t]*\r?\n"
    r".*?(?=^##[ \t]+|\Z)",
    flags=re.IGNORECASE | re.MULTILINE | re.DOTALL,
)

_COURSE_AUTHORING_SECTION_RE = re.compile(
    r"^##[ \t]+(?:"
    r"Couverture pedagogique des sources|"
    r"Plan pedagogique adaptatif[^\r\n]*|"
    r"Trous pedagogiques[^\r\n]*|"
    r"Faits et angles extraits de la base|"
    r"Positionnement bibliotheque|"
    r"Supports a produire|"
    r"Script enseignant|"
    r"Checkpoint personas[^\r\n]*"
    r")[ \t]*\r?\n.*?(?=^##[ \t]+|\Z)",
    flags=re.IGNORECASE | re.MULTILINE | re.DOTALL,
)
_COURSE_FRONTMATTER_RE = re.compile(r"\A---[ \t]*\r?\n.*?\r?\n---[ \t]*\r?\n", flags=re.DOTALL)
_COURSE_PROVENANCE_LEGEND_RE = re.compile(
    r"^>[ \t]+Legende de provenance du contenu:[^\r\n]*\r?\n"
    r"(?:^>[^\r\n]*(?:\r?\n|\Z))+",
    flags=re.IGNORECASE | re.MULTILINE,
)
_COURSE_PROVENANCE_TAG_RE = re.compile(
    r"_?\[(?:extrait|reformule|genere(?:[ \t]+a[ \t]+partir[ \t]+des[ \t]+concepts)?)\]_?",
    flags=re.IGNORECASE,
)
_COURSE_SOURCE_MARKER_RE = re.compile(
    r"(?:[ \t]*\([ \t]*)?\[S(?:\d+|x)\](?:[ \t]*\))?",
    flags=re.IGNORECASE,
)
_COURSE_AUTHORING_UIBLOCK_RE = re.compile(
    r"```uiblock\s*\r?\n"
    r"(?:(?!```).)*?^title:[ \t]+Controle de provenance[^\r\n]*\r?\n"
    r"(?:(?!```).)*?```[ \t]*(?:\r?\n)?",
    flags=re.IGNORECASE | re.MULTILINE | re.DOTALL,
)
_COURSE_REFERENCE_SECTION_RE = re.compile(
    r"^##[ \t]+Sources RAG a citer[ \t]*\r?\n"
    r"(?P<body>.*?)(?=^##[ \t]+|\Z)",
    flags=re.IGNORECASE | re.MULTILINE | re.DOTALL,
)


def _fold_course_text(value: str) -> str:
    value = unicodedata.normalize("NFKD", value)
    return "".join(char for char in value if not unicodedata.combining(char)).lower()


def _reference_match_text(value: str) -> str:
    """Normalize OCR typography and line-break hyphenation for anchor checks."""
    folded = _fold_course_text(value).replace("\u00ad", "")
    folded = re.sub(r"(?<=[a-z])[-‐‑‒–—]\s+(?=[a-z])", "", folded)
    return re.sub(r"[^a-z0-9]+", " ", folded).strip()


def _course_slug(markdown: str) -> str:
    match = re.search(r"(?m)^slug:[ \t]*([a-z0-9-]+)[ \t]*$", markdown)
    return match.group(1) if match else ""


def _clean_public_reference_entry(entry: str, slug: str) -> str | None:
    compact = re.sub(r"\s+", " ", entry).strip()
    if "—" not in compact or "«" not in compact or "»" not in compact:
        return None
    excerpt = compact.split("—", 1)[1]
    folded_excerpt = _fold_course_text(excerpt)
    matchable_excerpt = _reference_match_text(excerpt)
    if len(re.sub(r"[^a-z0-9]+", "", folded_excerpt)) < 45:
        return None
    if any(noise in folded_excerpt for noise in _COURSE_REFERENCE_NOISE_TERMS):
        return None
    reviewed_references = _COURSE_REFERENCE_ALLOWLIST.get(slug, ())
    if reviewed_references:
        if not any(anchor in matchable_excerpt for anchor, _, _ in reviewed_references):
            return None
    else:
        topic_terms = _COURSE_REFERENCE_TERMS.get(slug, ())
        if topic_terms and not any(term in folded_excerpt for term in topic_terms):
            return None
    compact = re.sub(r"\s*\[\d+\]\s*", " ", compact)
    compact = re.sub(r"\s+", " ", compact).strip()
    return f"- {compact}"


def _project_public_references(markdown: str, slug: str) -> str:
    def replace(match: re.Match[str]) -> str:
        entries = re.findall(
            r"(?ms)^-[ \t]+(.+?)(?=^-[ \t]+|\Z)",
            match.group("body").strip(),
        )
        clean = [
            projected
            for entry in entries
            if (projected := _clean_public_reference_entry(entry, slug)) is not None
        ][:4]
        if not clean:
            return ""
        return "## References du cours\n" + "\n".join(clean) + "\n\n"

    return _COURSE_REFERENCE_SECTION_RE.sub(replace, markdown)


def _remove_public_citation_ghosts(markdown: str) -> str:
    cleaned = re.sub(
        r"\b(?:En effet,[ \t]*)?[Cc]omme (?:le souligne|l['’]indique|l['’]illustre) "
        r"(?:un[ \t]+)?extrait(?:[ \t]+pertinent)?[ \t]*:?[ \t]*",
        "",
        markdown,
    )
    cleaned = re.sub(
        r"\b[Cc]omme mentionn[ée] dans (?:un[ \t]+|l['’])?extrait(?:[ \t]+pertinent)?[ \t]*:?[ \t]*",
        "",
        cleaned,
    )
    cleaned = re.sub(
        r"\b[Ll]['’]extrait(?:[ \t]+pertinent)? (?:mentionne|indique|souligne) que[ \t]*",
        "",
        cleaned,
    )
    cleaned = re.sub(r"\b[Ss]elon l['’]extrait[ \t]*:?[ \t]*", "", cleaned)
    # Keep French morphology valid when authoring vocabulary remains in otherwise
    # client-facing prose. A blind ``extrait -> source`` replacement produced
    # visible defects such as ``l'source``.
    replacements = (
        (r"\b[Ll]['’]extrait\b", "la source"),
        (r"\b[Dd]['’]extrait\b", "de source"),
        (r"\b[Ll]es extraits\b", "les sources"),
        (r"\b[Dd]es extraits\b", "des sources"),
        (r"\b[Uu]n extrait\b", "une source"),
        (r"\bextraits\b", "sources"),
        (r"\bextrait\b", "source"),
    )
    for pattern, replacement in replacements:
        cleaned = re.sub(pattern, replacement, cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\bEn effet,[ \t]*([,.;:])", r"\1", cleaned)
    return cleaned


def _public_course_markdown(markdown: str) -> str:
    """Project authoring Markdown into a clean, client-facing course."""
    public = _project_public_references(markdown, _course_slug(markdown))
    public = _COURSE_FRONTMATTER_RE.sub("", public)
    public = _COURSE_PROVENANCE_LEGEND_RE.sub("", public)
    public = _COURSE_AUTHORING_SECTION_RE.sub("", public)
    public = _COURSE_BACK_OFFICE_SECTION_RE.sub("", public)
    public = _COURSE_AUTHORING_UIBLOCK_RE.sub("", public)
    public = _COURSE_PROVENANCE_TAG_RE.sub("", public)
    public = _COURSE_SOURCE_MARKER_RE.sub("", public)
    public = _remove_public_citation_ghosts(public)
    public = re.sub(r"(?<=\S)[ \t]{2,}(?=\S)", " ", public)
    public = re.sub(r"[ \t]+(?=[,.;:])", "", public)
    public = re.sub(r"\n{3,}", "\n\n", public)
    return public.strip()


class CheckoutBody(BaseModel):
    plan: str
    email: str | None = None
    success_url: str | None = None
    cancel_url: str | None = None


class RumMeasurementBody(BaseModel):
    model_config = ConfigDict(extra="forbid")

    metric: str = Field(min_length=1, max_length=20)
    value: float
    route: str | None = Field(default=None, max_length=160)
    navigation_type: str | None = Field(default=None, max_length=30)


# --- platform (community/jobs/blog/progress...) request bodies -------------
class ThreadBody(BaseModel):
    model_config = ConfigDict(extra="forbid")
    channel: str = Field(default="forum", min_length=1, max_length=40, pattern=r"^[a-z0-9-]+$")
    title: str = Field(min_length=3, max_length=160)
    body: str = Field(min_length=3, max_length=5000)
    author: str = Field(default="anon", max_length=120)
    author_id: str | None = Field(default=None, max_length=160)
    tags: list[str] | None = Field(default=None, max_length=8)


class CommentBody(BaseModel):
    model_config = ConfigDict(extra="forbid")
    body: str = Field(min_length=1, max_length=5000)
    author: str = Field(default="anon", max_length=120)
    author_id: str | None = Field(default=None, max_length=160)


class JobBody(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: str = Field(min_length=2, max_length=160)
    company: str = Field(min_length=2, max_length=160)
    location: str | None = Field(default=None, max_length=160)
    kind: str | None = Field(default=None, max_length=40)
    tags: list[str] | None = Field(default=None, max_length=12)
    description: str | None = Field(default=None, max_length=10000)
    posted_by: str | None = Field(default=None, max_length=160)


class ApplyBody(BaseModel):
    model_config = ConfigDict(extra="forbid")
    applicant: str | None = Field(default=None, max_length=320)
    note: str | None = Field(default=None, max_length=4000)


class BugBody(BaseModel):
    model_config = ConfigDict(extra="forbid")
    summary: str = Field(min_length=3, max_length=240)
    kind: str | None = Field(default=None, max_length=40)
    severity: str | None = Field(default=None, max_length=20)
    detail: str | None = Field(default=None, max_length=12000)
    reporter: str | None = Field(default=None, max_length=320)


class NewsletterBody(BaseModel):
    model_config = ConfigDict(extra="forbid")
    email: str = Field(min_length=3, max_length=320, pattern=r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
    source: str | None = Field(default=None, max_length=80)


class ProgressBody(BaseModel):
    model_config = ConfigDict(extra="forbid")
    user_id: str | None = Field(default=None, max_length=160)
    username: str | None = Field(default=None, max_length=120)
    kind: str = Field(pattern=r"^(lesson|quiz|exercise|survival)$")
    ref: str = Field(min_length=1, max_length=240)
    score: float | None = Field(default=None, ge=0, le=1000000)
    meta: dict | None = None


class CoursePositionBody(BaseModel):
    model_config = ConfigDict(extra="forbid")
    module_index: int = Field(strict=True, ge=0, le=63)


class SurvivalBody(BaseModel):
    model_config = ConfigDict(extra="forbid")
    username: str = Field(default="member", max_length=120)
    user_id: str | None = Field(default=None, max_length=160)
    wave: str | None = Field(default=None, max_length=80)
    score: int = Field(ge=0, le=7200)
    streak: int = Field(default=0, ge=0, le=20)


class BlogBody(BaseModel):
    slug: str
    title: str
    author: str | None = None
    excerpt: str | None = None
    body: str | None = None
    tags: list[str] | None = None
    read_minutes: int | None = None


class DeskBody(BaseModel):
    query: str


class ToolRunBody(BaseModel):
    payload: dict | None = None
    context: dict | None = None


class SessionCreateBody(BaseModel):
    agent_id: str
    channel: str = "cli"
    external_user_id: str | None = None
    title: str | None = None
    route_metadata: dict | None = None
    status: str = "active"


class SessionMessageBody(BaseModel):
    role: str
    body: str
    visibility: str = "agent_visible"
    source: str = "api"
    metadata: dict | None = None


class SessionArtifactBody(BaseModel):
    artifact_type: str
    payload: dict
    provenance: dict | None = None
    tool_call_id: str | None = None


class SessionToolRunBody(BaseModel):
    payload: dict | None = None
    context: dict | None = None
    agent_id: str | None = None


class TaskCreateBody(BaseModel):
    agent_id: str
    title: str
    task_type: str = "subagent"
    parent_session_id: str | None = None
    child_session_id: str | None = None
    payload: dict | None = None
    status: str = "queued"


class TaskUpdateBody(BaseModel):
    status: str | None = None
    result_summary: str | None = None
    child_session_id: str | None = None


class McpHandleBody(BaseModel):
    jsonrpc: str | None = None
    id: str | int | None = None
    method: str
    params: dict | None = None


class GatewayInboundBody(BaseModel):
    channel: str = "cli"
    external_user_id: str
    body: str
    target_agent: str = "Chief of Staff"
    route_metadata: dict | None = None
    tool_name: str | None = None
    payload: dict | None = None
    context: dict | None = None


class TurnStartBody(BaseModel):
    objective: str
    input_payload: dict | None = None
    parent_turn_id: str | None = None
    status: str = "running"


class TurnCompleteBody(BaseModel):
    output_payload: dict | None = None
    status: str = "completed"


class SessionCompactBody(BaseModel):
    max_messages: int = 20
    metadata: dict | None = None


class SessionForkBody(BaseModel):
    target_agent: str | None = None
    title: str | None = None
    include_last_messages: int = 10


class SessionInjectBody(BaseModel):
    items: list[dict]
    source: str = "api:inject"


class SessionRollbackBody(BaseModel):
    message_id: str | None = None
    keep_last: int | None = None
    reason: str | None = None


class ApprovalRequestBody(BaseModel):
    session_id: str
    agent_id: str
    tool_name: str
    payload: dict | None = None
    reason: str = ""
    scope: str = "once"
    status: str = "requested"


class ApprovalResolveBody(BaseModel):
    status: str
    decision_note: str | None = None
from .practice_agent import PracticeAgent
from .schemas import (
    CalculationRequest,
    CalculationResponse,
    CourseRequest,
    ExerciseRequest,
    EvaluationReport,
    GenerationResponse,
    IngestRequest,
    IngestResult,
    LibraryItem,
    MaterialPackRequest,
    SearchRequest,
    SearchResponse,
)


def create_app(services: Services | None = None) -> FastAPI:
    services = services or build_services()
    app = FastAPI(
        title="ThePricingLibrary Local RAG Backend",
        version="0.1.0",
        description=(
            "Local backend for ingesting finance PDFs and generating "
            "practice-first courses and exercises."
        ),
    )
    app.add_middleware(
        CORSMiddleware,
        # Localhost is always allowed (dev). Production origins (the Lovable
        # frontend, custom domain) are added via TPL_CORS_ORIGINS.
        allow_origins=list(services.settings.cors_origins),
        allow_origin_regex=(
            None
            if services.settings.security_enforced
            else r"https?://(localhost|127\.0\.0\.1|\[::1\])(:\d+)?"
        ),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID", "Server-Timing"],
    )
    agent = PracticeAgent(services.generator)
    security = ApiSecurity(services.settings, store=services.store)
    metrics = ProductionMetrics()
    operations_logger = logging.getLogger("pricinglibrary_rag.operations")

    # Central policy: every mutation is classified before route execution.
    # Unclassified mutations default to OPERATOR, so newly added endpoints do
    # not accidentally become public. Local/test mode stays CLI-compatible.
    @app.middleware("http")
    async def enforce_api_security(request: Request, call_next):
        access = security.access_for(request.method, request.url.path)
        try:
            security.authorize(request, access)
        except HTTPException as exc:
            return JSONResponse(
                status_code=exc.status_code,
                content={"detail": exc.detail},
                headers=exc.headers or {},
            )
        request.state.tpl_security_authorized = True
        request.state.tpl_security_access = access
        response = await call_next(request)
        response.headers["X-TPL-Security"] = access
        return response

    @app.middleware("http")
    async def observe_requests(request: Request, call_next):
        request_id = uuid.uuid4().hex
        request.state.tpl_request_id = request_id
        started = time.perf_counter()
        status_code = 500
        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception:
            duration = max(0.0, time.perf_counter() - started)
            route = getattr(request.scope.get("route"), "path", "unmatched")
            metrics.record_request(
                method=request.method,
                route=route,
                status=500,
                duration_seconds=duration,
            )
            operations_logger.exception(
                "request_failed request_id=%s method=%s route=%s duration_ms=%.3f",
                request_id,
                request.method,
                route,
                duration * 1000,
            )
            raise
        duration = max(0.0, time.perf_counter() - started)
        route = getattr(request.scope.get("route"), "path", "unmatched")
        if route != "/metrics":
            metrics.record_request(
                method=request.method,
                route=route,
                status=status_code,
                duration_seconds=duration,
            )
        response.headers["X-Request-ID"] = request_id
        response.headers["Server-Timing"] = f"app;dur={duration * 1000:.3f}"
        if status_code >= 500:
            operations_logger.error(
                "request_error request_id=%s method=%s route=%s status=%s duration_ms=%.3f",
                request_id,
                request.method,
                route,
                status_code,
                duration * 1000,
            )
        return response

    def guard_paid(request: Request) -> None:
        """Compatibility dependency for routes that historically used it.

        The middleware is authoritative and has already authenticated/rate
        limited the request. Direct dependency execution remains secure.
        """
        if not getattr(request.state, "tpl_security_authorized", False):
            security.authorize(request, MEMBER)

    @app.get("/health")
    def health() -> dict:
        payload = {
            "status": "ok",
            "embedding_backend": services.embeddings.name,
            "embedding_dim": services.embeddings.dim,
            "llm": services.llm.name,
            "openai_configured": bool(services.settings.openai_api_key),
            "rag_available": bool(services.retriever.store.list_documents(limit=1)),
            "retrieval_mode": services.settings.retrieval_mode,
            "security": security.summary(),
        }
        if not services.settings.security_enforced:
            payload["db_path"] = str(services.settings.db_path)
        return payload

    @app.get("/ready")
    def ready() -> JSONResponse:
        status_code = 200 if security.readiness.ready else 503
        return JSONResponse(
            status_code=status_code,
            content={
                "status": "ready" if security.readiness.ready else "not_ready",
                "security": security.summary(),
            },
        )

    @app.get("/metrics", response_class=Response)
    def prometheus_metrics() -> Response:
        return Response(
            content=metrics.render_prometheus(),
            media_type="text/plain; version=0.0.4",
        )

    @app.get("/courses/{course_id}/script", response_class=Response)
    def course_script(course_id: str) -> Response:
        """Deliver course IP only after the central entitlement middleware.

        The filename is selected from a closed mapping; user input is never
        joined into a filesystem path.
        """
        filename = COURSE_SCRIPT_FILES.get(course_id)
        if filename is None:
            raise HTTPException(status_code=404, detail="Course script not found.")
        root = services.settings.course_scripts_dir
        if root is None:
            raise HTTPException(status_code=503, detail="Course content is not configured.")
        path = root / filename
        if not path.is_file():
            raise HTTPException(status_code=503, detail="Course content is unavailable.")
        return Response(
            content=_public_course_markdown(path.read_text(encoding="utf-8")),
            media_type="text/markdown; charset=utf-8",
            headers={"Cache-Control": "private, no-store", "X-Content-Type-Options": "nosniff"},
        )

    @app.post("/telemetry/rum", status_code=202)
    def record_rum_measurement(body: RumMeasurementBody) -> dict:
        try:
            accepted = metrics.record_rum(
                metric=body.metric,
                value=body.value,
                route=body.route,
                navigation_type=body.navigation_type,
            )
        except (TypeError, ValueError) as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        return {"accepted": True, **accepted}

    @app.get("/", response_class=HTMLResponse)
    @app.get("/ui", response_class=HTMLResponse)
    def ui() -> str:
        return _ui_html()

    @app.get("/documents")
    def list_documents(limit: int = 100, offset: int = 0) -> list[dict]:
        return [
            {
                "id": doc.id,
                "title": doc.title,
                "source": doc.source,
                "path": doc.path,
                "metadata": doc.metadata,
                "status": doc.status,
                "created_at": doc.created_at,
            }
            for doc in services.store.list_documents(limit=limit, offset=offset)
        ]

    @app.get("/sources/pedagogy-stats")
    def pedagogy_stats() -> dict:
        """Pedagogical coverage of the ingested corpus.

        Lets a UI surface: usable chunks, average pedagogical score, content-type
        distribution and overall usability — without scanning the corpus itself.
        """
        from .pedagogy import detect_pedagogical_gaps

        stats = services.store.pedagogy_stats()
        usable = services.store.iter_chunks(usable_only=True, limit=4000)
        items = [
            (c.metadata or {}).get("pedagogy")
            for c in usable
            if (c.metadata or {}).get("pedagogy")
        ]
        stats["gaps"] = detect_pedagogical_gaps(items)
        return stats

    @app.post("/documents/ingest", response_model=list[IngestResult])
    def ingest(request: IngestRequest) -> list[IngestResult]:
        if request.recursive:
            results = services.ingestion.ingest_directory(
                request.path,
                metadata=request.metadata,
                glob=request.glob,
                recursive=True,
                force=request.force,
            )
            services.retriever.refresh()
            return results
        results = [
            services.ingestion.ingest_file(
                request.path,
                metadata=request.metadata,
                force=request.force,
            )
        ]
        services.retriever.refresh()
        return results

    @app.post("/rag/search", response_model=SearchResponse)
    def search(request: SearchRequest) -> SearchResponse:
        if not request.query.strip():
            raise HTTPException(status_code=400, detail="query is required")
        return services.retriever.search(request)

    @app.post("/calculate/practice", response_model=CalculationResponse)
    def calculate_practice(request: CalculationRequest) -> CalculationResponse:
        pack = services.generator.calculator.build_pack(
            request.prompt,
            family_hint=request.family_hint,
        )
        return CalculationResponse(
            family=pack.family,
            title=pack.title,
            markdown=pack.as_markdown(),
            pack=pack.model_dump(),
        )

    @app.get("/library/generations", response_model=list[LibraryItem])
    def list_generations(
        kind: str | None = None,
        limit: int = 30,
        offset: int = 0,
    ) -> list[LibraryItem]:
        return [
            LibraryItem(
                id=item.id,
                kind=item.kind,
                title=item.title,
                created_at=item.created_at,
                request=item.request,
                response=item.response,
            )
            for item in services.store.list_generation_runs(
                kind=kind,
                limit=limit,
                offset=offset,
            )
        ]

    @app.get("/library/generations/{run_id}", response_model=LibraryItem)
    def get_generation(run_id: str) -> LibraryItem:
        item = services.store.get_generation_run(run_id)
        if item is None:
            raise HTTPException(status_code=404, detail="generation not found")
        return LibraryItem(
            id=item.id,
            kind=item.kind,
            title=item.title,
            created_at=item.created_at,
            request=item.request,
            response=item.response,
        )

    @app.get("/evaluation/cases")
    def evaluation_cases() -> list[dict]:
        return [
            {"name": name, "request": request.model_dump()}
            for name, request in services.evaluator.default_cases()
        ]

    @app.post("/evaluation/response")
    def evaluate_response(response: GenerationResponse) -> dict:
        return services.evaluator.evaluate_response(response)

    @app.post("/evaluation/suite", response_model=EvaluationReport)
    def run_evaluation_suite(limit: int | None = None) -> EvaluationReport:
        try:
            return services.evaluator.run_generation_suite(
                services.generator,
                limit=limit,
            )
        except RuntimeError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    def saved_attempt(request: ExerciseRequest, http_request: Request) -> GenerationResponse | None:
        identity = getattr(http_request.state, "tpl_identity", None)
        if identity and request.client_request_id:
            existing = platform.get_exercise_request(identity.user_id, request.client_request_id)
            if existing:
                if existing["request"] != request.model_dump():
                    raise HTTPException(status_code=409, detail="La tentative existe avec d’autres paramètres. Lance une nouvelle création.")
                return GenerationResponse.model_validate(existing["response"])
        return None

    def persist_exercise(request: ExerciseRequest, http_request: Request, response: GenerationResponse) -> GenerationResponse:
        identity = getattr(http_request.state, "tpl_identity", None)
        if identity:
            try:
                saved = platform.save_exercise(user_id=identity.user_id, request=request.model_dump(), response=response.model_dump())
                return GenerationResponse.model_validate(saved["response"])
            except ValueError as exc:
                raise HTTPException(status_code=409, detail=str(exc)) from exc
        return response

    @app.post(
        "/generate/exercise",
        response_model=GenerationResponse,
        dependencies=[Depends(guard_paid)],
    )
    def generate_exercise(request: ExerciseRequest, http_request: Request) -> GenerationResponse:
        try:
            cached = saved_attempt(request, http_request)
            if cached:
                return cached
            response = services.generator.generate_exercise(request)
            return persist_exercise(request, http_request, response)
        except ExerciseInputError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        except RuntimeError as exc:
            raise HTTPException(status_code=503, detail="Le service de rédaction est temporairement indisponible. Réessayez.") from exc

    @app.post(
        "/agent/exercise",
        response_model=GenerationResponse,
        dependencies=[Depends(guard_paid)],
    )
    def agent_exercise(request: ExerciseRequest, http_request: Request) -> GenerationResponse:
        try:
            cached = saved_attempt(request, http_request)
            if cached:
                return cached
            response = agent.create_exercise(request)
            return persist_exercise(request, http_request, response)
        except ExerciseInputError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        except RuntimeError as exc:
            raise HTTPException(status_code=503, detail="Le service de rédaction est temporairement indisponible. Réessayez.") from exc

    @app.post(
        "/agent/course",
        response_model=GenerationResponse,
        dependencies=[Depends(guard_paid)],
    )
    def agent_course(request: CourseRequest) -> GenerationResponse:
        try:
            return agent.create_course(request)
        except RuntimeError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post(
        "/generate/course",
        response_model=GenerationResponse,
        dependencies=[Depends(guard_paid)],
    )
    def generate_course(request: CourseRequest) -> GenerationResponse:
        try:
            return services.generator.generate_course(request)
        except RuntimeError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post(
        "/generate/material-pack",
        response_model=GenerationResponse,
        dependencies=[Depends(guard_paid)],
    )
    def generate_material_pack(request: MaterialPackRequest) -> GenerationResponse:
        try:
            return services.generator.generate_material_pack(request)
        except RuntimeError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    # --- AG-UI agentic assistant (SSE streaming) --------------------------
    @app.post("/agent/ag-ui/run", dependencies=[Depends(guard_paid)])
    async def agent_ag_ui_run(request: Request) -> StreamingResponse:
        payload = await request.json()

        def _gen():
            yield from run_agui_stream(services, payload)

        return StreamingResponse(
            _gen(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "Connection": "keep-alive", "X-Accel-Buffering": "no"},
        )

    # --- billing (Stripe) -------------------------------------------------
    @app.get("/billing/config")
    def billing_config() -> dict:
        return services.billing.config_summary()

    @app.post("/billing/checkout")
    def billing_checkout(body: CheckoutBody, request: Request) -> dict:
        identity = getattr(request.state, "tpl_identity", None)
        try:
            session = services.billing.create_checkout_session(
                body.plan,
                email=identity.email if identity else body.email,
                user_id=identity.user_id if identity else None,
                # Production redirects are operator configuration, never
                # client-controlled URLs.
                success_url=None if services.settings.security_enforced else body.success_url,
                cancel_url=None if services.settings.security_enforced else body.cancel_url,
            )
        except BillingError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return {"id": session.id, "url": session.url, "plan": session.plan, "mode": session.mode}

    @app.post("/billing/webhook")
    async def billing_webhook(request: Request) -> dict:
        payload = await request.body()
        sig = request.headers.get("stripe-signature", "")
        try:
            return services.billing.handle_webhook(payload, sig)
        except BillingError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get("/billing/entitlement")
    def billing_entitlement(request: Request, email: str | None = None) -> dict:
        identity = getattr(request.state, "tpl_identity", None)
        if identity:
            return services.billing.entitlement(user_id=identity.user_id)
        if not email:
            raise HTTPException(status_code=400, detail="email is required in local mode")
        return services.billing.entitlement(email)

    def require_product_identity(request: Request):
        identity = getattr(request.state, "tpl_identity", None)
        if identity is None:
            raise HTTPException(status_code=401, detail="Authenticated user session required.")
        return identity

    @app.get("/products/market-finance-starter-kit/availability")
    def starter_kit_availability() -> dict:
        return services.billing.product_availability(STARTER_KIT_PRODUCT_ID)

    def require_starter_kit_access(request: Request):
        identity = require_product_identity(request)
        entitlement = services.billing.product_entitlement(
            identity.user_id, STARTER_KIT_PRODUCT_ID
        )
        if not entitlement["active"]:
            raise HTTPException(
                status_code=403,
                detail="Active starter kit product entitlement required.",
            )
        return identity

    @app.post("/products/market-finance-starter-kit/checkout")
    def starter_kit_checkout(request: Request) -> dict:
        identity = require_product_identity(request)
        try:
            session = services.billing.create_product_checkout_session(
                STARTER_KIT_PRODUCT_ID,
                user_id=identity.user_id,
                email=identity.email,
            )
        except BillingError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc
        return {
            "id": session.id,
            "url": session.url,
            "product_id": session.product_id,
            "mode": session.mode,
        }

    @app.get("/products/market-finance-starter-kit/manifest")
    def starter_kit_manifest(request: Request) -> dict:
        require_starter_kit_access(request)
        try:
            return services.billing.product_artifact(STARTER_KIT_PRODUCT_ID).manifest
        except BillingError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc

    @app.get("/products/market-finance-starter-kit/download")
    def starter_kit_download(request: Request) -> FileResponse:
        require_starter_kit_access(request)
        try:
            artifact = services.billing.product_artifact(STARTER_KIT_PRODUCT_ID)
        except BillingError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc
        return FileResponse(
            path=artifact.path,
            media_type="application/octet-stream",
            filename=artifact.manifest["bundle"]["path"],
            headers={
                "Cache-Control": "private, no-store",
                "X-Content-Type-Options": "nosniff",
            },
        )

    # ===================== AGENTIC DESK (multi-agent trading room) ========
    desk = DeskOrchestrator(services.llm)

    @app.post("/agent/desk/run", dependencies=[Depends(guard_paid)])
    def desk_run(body: DeskBody) -> dict:
        return desk.run(body.query)

    # --- audited agent/tool registry -------------------------------------
    from .tool_registry import get_tool_registry
    from .conversation_ledger import ConversationLedger
    from .mcp_adapter import TplMcpAdapter

    @app.get("/agent/tools")
    def agent_tools(agent_role: str | None = None, desk: str | None = None, permission_scope: str | None = None) -> dict:
        registry = get_tool_registry()
        return {"tools": registry.list(agent_role=agent_role, desk=desk, permission_scope=permission_scope)}

    @app.get("/agent/tools/search")
    def agent_tools_search(
        q: str | None = None,
        agent_role: str | None = None,
        permission: str | None = None,
        limit: int = 25,
    ) -> dict:
        adapter = TplMcpAdapter(registry=get_tool_registry(), store=services.store)
        return adapter.tool_search(query=q, agent_role=agent_role, permission=permission, limit=limit)

    @app.get("/agent/tools/coverage")
    def agent_tools_coverage() -> dict:
        return get_tool_registry().coverage_report()

    @app.get("/agent/tools/audit/{tool_call_id}")
    def agent_tool_audit(tool_call_id: str) -> dict:
        try:
            return get_tool_registry().audit(tool_call_id)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.post("/agent/tools/replay/{tool_call_id}", dependencies=[Depends(guard_paid)])
    def agent_tool_replay(tool_call_id: str) -> dict:
        try:
            return get_tool_registry().replay(tool_call_id)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.post("/agent/tools/{tool_name:path}/run", dependencies=[Depends(guard_paid)])
    def agent_tool_run(tool_name: str, body: ToolRunBody) -> dict:
        try:
            return get_tool_registry().run(tool_name, payload=body.payload or {}, context=body.context or {})
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.get("/agent/tools/{tool_name:path}")
    def agent_tool_describe(tool_name: str) -> dict:
        try:
            return get_tool_registry().describe(tool_name)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    # --- conversation/session/task ledger --------------------------------
    def _ledger() -> ConversationLedger:
        return ConversationLedger(services.store)

    @app.post("/agent/sessions", dependencies=[Depends(guard_paid)])
    def session_create(body: SessionCreateBody) -> dict:
        return _ledger().create_session(
            agent_id=body.agent_id,
            channel=body.channel,
            external_user_id=body.external_user_id,
            title=body.title,
            route_metadata=body.route_metadata or {},
            status=body.status,
        )

    @app.get("/agent/sessions", dependencies=[Depends(guard_paid)])
    def session_list(
        agent_id: str | None = None,
        channel: str | None = None,
        status: str | None = None,
        limit: int = 50,
    ) -> dict:
        return {"sessions": _ledger().list_sessions(agent_id=agent_id, channel=channel, status=status, limit=limit)}

    @app.get("/agent/sessions/{session_id}", dependencies=[Depends(guard_paid)])
    def session_get(session_id: str) -> dict:
        session = _ledger().get_session(session_id)
        if session is None:
            raise HTTPException(status_code=404, detail="session not found")
        return session

    @app.post("/agent/sessions/{session_id}/messages", dependencies=[Depends(guard_paid)])
    def session_add_message(session_id: str, body: SessionMessageBody) -> dict:
        try:
            return _ledger().add_message(
                session_id,
                role=body.role,
                body=body.body,
                visibility=body.visibility,
                source=body.source,
                metadata=body.metadata or {},
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.get("/agent/sessions/{session_id}/history", dependencies=[Depends(guard_paid)])
    def session_history(session_id: str, limit: int = 20, offset: int = 0, sanitized: bool = True) -> dict:
        try:
            return _ledger().history(session_id, limit=limit, offset=offset, sanitized=sanitized)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.post("/agent/sessions/{session_id}/artifacts", dependencies=[Depends(guard_paid)])
    def session_add_artifact(session_id: str, body: SessionArtifactBody) -> dict:
        try:
            return _ledger().add_artifact(
                session_id,
                artifact_type=body.artifact_type,
                payload=body.payload,
                provenance=body.provenance or {},
                tool_call_id=body.tool_call_id,
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.get("/agent/sessions/{session_id}/artifacts", dependencies=[Depends(guard_paid)])
    def session_artifacts(session_id: str) -> dict:
        try:
            return {"artifacts": _ledger().list_artifacts(session_id)}
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.post("/agent/sessions/{session_id}/tools/{tool_name:path}/run", dependencies=[Depends(guard_paid)])
    def session_tool_run(session_id: str, tool_name: str, body: SessionToolRunBody) -> dict:
        try:
            adapter = TplMcpAdapter(registry=get_tool_registry(), store=services.store)
            return adapter.call_tool(
                tool_name,
                payload=body.payload or {},
                context=body.context or {},
                session_id=session_id,
                agent_id=body.agent_id,
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.post("/agent/sessions/{session_id}/turns", dependencies=[Depends(guard_paid)])
    def session_turn_start(session_id: str, body: TurnStartBody) -> dict:
        try:
            return _ledger().start_turn(
                session_id,
                objective=body.objective,
                input_payload=body.input_payload or {},
                parent_turn_id=body.parent_turn_id,
                status=body.status,
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.get("/agent/sessions/{session_id}/turns", dependencies=[Depends(guard_paid)])
    def session_turns(session_id: str, status: str | None = None, limit: int = 50) -> dict:
        try:
            return {"turns": _ledger().list_turns(session_id, status=status, limit=limit)}
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.post("/agent/turns/{turn_id}/complete", dependencies=[Depends(guard_paid)])
    def turn_complete(turn_id: str, body: TurnCompleteBody) -> dict:
        try:
            return _ledger().complete_turn(
                turn_id,
                output_payload=body.output_payload or {},
                status=body.status,
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.post("/agent/sessions/{session_id}/compact", dependencies=[Depends(guard_paid)])
    def session_compact(session_id: str, body: SessionCompactBody) -> dict:
        try:
            return _ledger().compact_session(
                session_id,
                max_messages=body.max_messages,
                metadata=body.metadata or {},
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.get("/agent/sessions/{session_id}/summaries", dependencies=[Depends(guard_paid)])
    def session_summaries(session_id: str, limit: int = 20) -> dict:
        try:
            return {"summaries": _ledger().list_summaries(session_id, limit=limit)}
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.post("/agent/sessions/{session_id}/fork", dependencies=[Depends(guard_paid)])
    def session_fork(session_id: str, body: SessionForkBody) -> dict:
        try:
            return _ledger().fork_session(
                session_id,
                target_agent=body.target_agent,
                title=body.title,
                include_last_messages=body.include_last_messages,
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.post("/agent/sessions/{session_id}/inject", dependencies=[Depends(guard_paid)])
    def session_inject(session_id: str, body: SessionInjectBody) -> dict:
        try:
            return _ledger().inject_items(session_id, body.items, source=body.source)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.post("/agent/sessions/{session_id}/rollback", dependencies=[Depends(guard_paid)])
    def session_rollback(session_id: str, body: SessionRollbackBody) -> dict:
        try:
            return _ledger().rollback_session(
                session_id,
                message_id=body.message_id,
                keep_last=body.keep_last,
                reason=body.reason,
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.get("/agent/sessions/{session_id}/events", dependencies=[Depends(guard_paid)])
    def session_events(session_id: str, event_type: str | None = None, limit: int = 100) -> dict:
        try:
            return {"events": _ledger().list_events(session_id=session_id, event_type=event_type, limit=limit)}
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.post("/agent/approvals", dependencies=[Depends(guard_paid)])
    def approval_request(body: ApprovalRequestBody) -> dict:
        try:
            return _ledger().request_approval(
                body.session_id,
                agent_id=body.agent_id,
                tool_name=body.tool_name,
                payload=body.payload or {},
                reason=body.reason,
                scope=body.scope,
                status=body.status,
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.get("/agent/approvals", dependencies=[Depends(guard_paid)])
    def approval_list(session_id: str | None = None, status: str | None = None, limit: int = 50) -> dict:
        try:
            return {"approvals": _ledger().list_approvals(session_id=session_id, status=status, limit=limit)}
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.post("/agent/approvals/{approval_id}/resolve", dependencies=[Depends(guard_paid)])
    def approval_resolve(approval_id: str, body: ApprovalResolveBody) -> dict:
        try:
            return _ledger().resolve_approval(
                approval_id,
                status=body.status,
                decision_note=body.decision_note,
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/agent/tasks", dependencies=[Depends(guard_paid)])
    def task_create(body: TaskCreateBody) -> dict:
        try:
            return _ledger().create_task(
                agent_id=body.agent_id,
                title=body.title,
                task_type=body.task_type,
                parent_session_id=body.parent_session_id,
                child_session_id=body.child_session_id,
                payload=body.payload or {},
                status=body.status,
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.get("/agent/tasks", dependencies=[Depends(guard_paid)])
    def task_list(status: str | None = None, agent_id: str | None = None, limit: int = 50) -> dict:
        return {"tasks": _ledger().list_tasks(status=status, agent_id=agent_id, limit=limit)}

    @app.post("/agent/tasks/{task_id}/status", dependencies=[Depends(guard_paid)])
    def task_update(task_id: str, body: TaskUpdateBody) -> dict:
        try:
            return _ledger().update_task(
                task_id,
                status=body.status,
                result_summary=body.result_summary,
                child_session_id=body.child_session_id,
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    # --- MCP-style bridge for Codex/OpenClaw/agent clients ----------------
    @app.post("/agent/mcp/handle", dependencies=[Depends(guard_paid)])
    def agent_mcp_handle(body: McpHandleBody) -> dict:
        adapter = TplMcpAdapter(registry=get_tool_registry(), store=services.store)
        return adapter.jsonrpc(body.model_dump())

    @app.post("/agent/gateway/inbound", dependencies=[Depends(guard_paid)])
    def agent_gateway_inbound(body: GatewayInboundBody) -> dict:
        from .agent_gateway import AgentInteractionGateway

        gateway = AgentInteractionGateway(services.store)
        try:
            return gateway.handle_inbound(
                channel=body.channel,
                external_user_id=body.external_user_id,
                body=body.body,
                target_agent=body.target_agent,
                route_metadata=body.route_metadata or {},
                tool_name=body.tool_name,
                payload=body.payload,
                context=body.context,
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    # --- stateful FIC trading room (live market + live books) -------------
    from .desk_state import get_room

    @app.get("/agent/desk/state")
    def desk_state() -> dict:
        room = get_room()
        room.auto_tick()  # time passes with the wall clock
        return room.snapshot()

    @app.post("/agent/desk/tick")
    def desk_tick(seconds: float = 1.0) -> dict:
        room = get_room()
        room.tick(seconds)
        return room.snapshot()

    @app.post("/agent/desk/trade")
    def desk_trade(body: DeskBody) -> dict:
        room = get_room()
        room.auto_tick()
        result = desk.run(body.query)
        kind = result["product_spec"]["kind"]
        factor = result["parsed"]["factor"]
        if kind == "swap":
            room.add_swap("EUR", 50_000_000, +1, result["product_spec"]["maturity_years"] or 5.0,
                          label=f"RFQ {result['parsed']['underlying']} payer")
        elif kind == "cds":
            room.add_cds(50_000_000, +1, label="RFQ IG protection")
        elif factor in ("fx",):
            room.add_fx_forward(25_000_000, +1, label="RFQ EURUSD fwd")
        elif factor == "crypto":
            pr = result["pricing_result"] or {}
            asset = pr.get("strike") and result["product_spec"].get("asset") or "BTC"
            room.add_option(asset, 10, +1, pr.get("strike") or room.market.spots.get(asset, 61250.0),
                            result["product_spec"]["maturity_years"] or 0.25, label=f"RFQ {asset} option")
        else:
            room.add_option("WTI" if factor == "oil" else "SPX", 1000, +1, 80.0,
                            result["product_spec"]["maturity_years"] or 0.4, label="RFQ option")
        room.revalue()
        return {"result": result, "snapshot": room.snapshot()}

    # ===================== MARKET DATA (shared multi-asset history) =======
    from . import marketdata as md
    from .integrations import status as integ_status

    @app.get("/market/providers")
    def market_providers() -> dict:
        return {"providers": md.provider_status(), "integrations": integ_status(),
                "data_dir": str(md.cache.data_dir())}

    @app.get("/market/catalog")
    def market_catalog() -> dict:
        return {"asset_classes": md.by_asset_class(), "inventory": md.cache.inventory()}

    @app.get("/market/history/{symbol}")
    def market_history(symbol: str, points: int = 260, provider: str | None = None) -> dict:
        resolved_provider, resolved_symbol = md.resolve_source(symbol, provider)
        cache_hit = md.cache.exists(resolved_provider, resolved_symbol)
        try:
            df = md.get_history(symbol, provider=provider)
        except Exception as exc:  # noqa: BLE001
            raise HTTPException(status_code=404, detail=f"{symbol}: {exc}") from exc
        tail = df.tail(max(2, points))
        return {"symbol": symbol, "rows": int(len(df)),
                "provenance": md.history_provenance(symbol, provider, df, cache_hit=cache_hit),
                "series": [{"date": str(idx.date()), "close": round(float(r['close']), 4),
                            "open": round(float(r['open']), 4), "high": round(float(r['high']), 4),
                            "low": round(float(r['low']), 4), "volume": float(r['volume'])}
                           for idx, r in tail.iterrows()]}

    @app.post("/market/aspirate")
    def market_aspirate(refresh: bool = False) -> dict:
        return md.aspirate(refresh=refresh)

    @app.get("/market/universe")
    def market_universe() -> dict:
        """Full cached price universe grouped by namespace (asset family) — the
        ~11k assets / ~63M rows aspirated since 1962. Foundation for the Strategy
        Lab to backtest the whole universe, not just the 6 native instruments."""
        inv = md.cache.inventory()
        groups: dict = {}
        for it in inv:
            g = groups.setdefault(it["provider"], {"symbols": 0, "rows": 0})
            g["symbols"] += 1
            g["rows"] += it["rows"]
        return {"total_symbols": len(inv), "total_rows": sum(i["rows"] for i in inv),
                "by_namespace": dict(sorted(groups.items(), key=lambda kv: -kv[1]["rows"]))}

    @app.get("/market/intraday/{symbol}")
    def market_intraday(symbol: str, interval: str = "15m", points: int = 300) -> dict:
        if interval not in ("1m", "5m", "15m", "30m", "1h"):
            raise HTTPException(status_code=400, detail="interval must be 1m/5m/15m/30m/1h")
        try:
            df = md.get_intraday(symbol, interval=interval)
        except Exception as exc:  # noqa: BLE001
            raise HTTPException(status_code=404, detail=f"{symbol} {interval}: {exc}") from exc
        tail = df.tail(max(2, points))
        return {"symbol": symbol, "interval": interval, "rows": int(len(df)),
                "series": [{"t": str(idx), "close": round(float(r['close']), 6),
                            "open": round(float(r['open']), 6), "high": round(float(r['high']), 6),
                            "low": round(float(r['low']), 6), "volume": float(r['volume'])}
                           for idx, r in tail.iterrows()]}

    @app.get("/agent/crypto/vol")
    def crypto_vol(asset: str = "BTC") -> dict:
        from . import volsurface_bridge as vb
        return {"asset": asset.upper(), "engine": vb.engine_name(),
                "realized": vb.realized_vol(asset), "live": vb.live_atm_vol(asset)}

    # ===================== STRATEGY LAB (algo trading engine) =============
    from . import strategylab as lab

    @app.get("/strategy/instruments")
    def strategy_instruments() -> dict:
        return {**lab.list_instruments(), "strategies": lab.strategies().get("strategies", [])}

    @app.post("/strategy/backtest")
    def strategy_backtest(instrument: str = "EURUSD", max_bars: int = 40000,
                          capital: float | None = None) -> dict:
        return lab.backtest(instrument, max_bars=max_bars, capital=capital)

    @app.post("/strategy/scan")
    def strategy_scan(max_bars: int = 30000) -> dict:
        return lab.scan(max_bars=max_bars)

    @app.post("/strategy/walkforward")
    def strategy_walkforward(instrument: str = "EURUSD", strategy_name: str = "trend_following",
                             max_bars: int = 30000) -> dict:
        return lab.walkforward(instrument, strategy_name=strategy_name, max_bars=max_bars)

    # ===================== PLATFORM (community/jobs/blog/...) =============
    platform = PlatformStore(services.settings.db_path)
    register_interview_routes(app, services.settings.db_path, security)

    def platform_identity(request: Request) -> AuthenticatedIdentity | None:
        """Return the verified browser identity for user-owned platform data.

        Local mode deliberately remains CLI-compatible.  In production, a
        shared API key is not an identity and therefore cannot author content,
        claim progress or submit an application on somebody else's behalf.
        """

        identity = getattr(request.state, "tpl_identity", None)
        if isinstance(identity, AuthenticatedIdentity):
            return identity
        if services.settings.security_enforced:
            raise HTTPException(
                status_code=401,
                detail="Authenticated user session required for identity-bound platform data.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return None

    def _identity_display(identity: AuthenticatedIdentity) -> str:
        digest = hashlib.sha256(identity.user_id.encode("utf-8")).hexdigest()[:10]
        return f"member-{digest}"

    @app.get("/platform/health")
    def platform_health() -> dict:
        return {"status": "ok"}

    @app.get("/platform/admin/counts")
    def platform_admin_counts() -> dict:
        return {"counts": platform.counts()}

    @app.get("/platform/exercises")
    def private_exercises(request: Request, limit: int = 30, offset: int = 0) -> dict:
        identity = platform_identity(request)
        if identity is None:
            raise HTTPException(status_code=401, detail="Authenticated user session required.")
        limit, offset = max(1,min(limit,50)), max(0,offset)
        records = platform.list_exercises(identity.user_id, limit+1, offset)
        return {"owner_id": identity.user_id, "exercises": records[:limit], "has_more": len(records)>limit}

    @app.get("/platform/exercises/{exercise_id}")
    def private_exercise(exercise_id: str, request: Request) -> dict:
        identity = platform_identity(request)
        if identity is None:
            raise HTTPException(status_code=401, detail="Authenticated user session required.")
        record = platform.get_exercise(identity.user_id, exercise_id)
        if record is None:
            raise HTTPException(status_code=404, detail="Exercise not found.")
        return {**record, "owner_id": identity.user_id}

    # community
    @app.get("/platform/community/threads")
    def community_threads(channel: str | None = None, limit: int = 50) -> dict:
        return {"threads": platform.list_threads(channel, limit)}

    @app.post("/platform/community/threads")
    def community_create_thread(body: ThreadBody, request: Request) -> dict:
        identity = platform_identity(request)
        return platform.create_thread(channel=body.channel, title=body.title, body=body.body,
                                      author=_identity_display(identity) if identity else body.author,
                                      author_id=identity.user_id if identity else body.author_id,
                                      tags=body.tags)

    @app.post("/platform/community/threads/{thread_id}/vote")
    def community_vote(thread_id: str, request: Request) -> dict:
        identity = platform_identity(request)
        out = platform.vote_thread(thread_id, 1, voter_id=identity.user_id if identity else None)
        if out is None:
            raise HTTPException(status_code=404, detail="thread not found")
        return out

    @app.get("/platform/community/threads/{thread_id}/comments")
    def community_comments(thread_id: str) -> dict:
        return {"comments": platform.list_comments(thread_id)}

    @app.post("/platform/community/threads/{thread_id}/comments")
    def community_add_comment(thread_id: str, body: CommentBody, request: Request) -> dict:
        identity = platform_identity(request)
        out = platform.add_comment(
            thread_id=thread_id,
            body=body.body,
            author=_identity_display(identity) if identity else body.author,
            author_id=identity.user_id if identity else body.author_id,
        )
        if out is None:
            raise HTTPException(status_code=404, detail="thread not found")
        return out

    # jobs
    @app.get("/platform/jobs")
    def jobs_list(kind: str | None = None, limit: int = 100) -> dict:
        return {"jobs": platform.list_jobs(kind, limit)}

    @app.post("/platform/jobs")
    def jobs_create(body: JobBody) -> dict:
        return platform.create_job(title=body.title, company=body.company, location=body.location,
                                   kind=body.kind, tags=body.tags, description=body.description, posted_by=body.posted_by)

    @app.post("/platform/jobs/{job_id}/apply")
    def jobs_apply(job_id: str, body: ApplyBody, request: Request) -> dict:
        identity = platform_identity(request)
        applicant = identity.email if identity else (body.applicant or "guest")
        out = platform.apply_job(job_id=job_id, applicant=applicant, note=body.note)
        if out is None:
            raise HTTPException(status_code=404, detail="job not found")
        return out

    @app.get("/platform/jobs/sources")
    def jobs_sources() -> dict:
        from . import jobs_sourcing as js
        return {"providers": js.provider_status(), "counts": platform.jobs_source_counts()}

    @app.post("/platform/jobs/source")
    def jobs_source(limit_per: int = 60, query: str = "finance") -> dict:
        from . import jobs_sourcing as js
        return js.source_jobs(platform, limit_per=limit_per, query=query)

    # bug reports
    @app.post("/platform/bug-reports")
    def bug_create(body: BugBody) -> dict:
        return platform.create_bug(kind=body.kind, severity=body.severity, summary=body.summary,
                                   detail=body.detail, reporter=body.reporter)

    @app.get("/platform/bug-reports")
    def bug_list(limit: int = 100) -> dict:
        return {"bug_reports": platform.list_bugs(limit)}

    # newsletter
    @app.post("/platform/newsletter")
    def newsletter_subscribe(body: NewsletterBody) -> dict:
        return platform.subscribe(body.email, body.source)

    # progress + leaderboard
    @app.put("/platform/courses/{course_id}/position")
    def course_position_record(course_id: str, body: CoursePositionBody, request: Request, response: Response) -> dict:
        identity = platform_identity(request)
        if identity is None:
            raise HTTPException(status_code=401, detail="A signed learner session is required.")
        if course_id not in COURSE_MODULE_COUNTS:
            raise HTTPException(status_code=404, detail="Course not found.")
        if body.module_index >= COURSE_MODULE_COUNTS[course_id]:
            raise HTTPException(status_code=422, detail="Module index is outside this course.")
        is_free_preview = course_id == "black-scholes" and body.module_index < 2
        if (services.settings.security_enforced or services.settings.enforce_entitlements) and identity.role != "operator" and not is_free_preview:
            minimum = security.required_plan_for("GET", f"/courses/{course_id}/script")
            entitlement = services.store.get_entitlement_by_user_id(identity.user_id) or {}
            rank = security._PLAN_RANK
            if entitlement.get("status") != "active" or rank.get(str(entitlement.get("plan")),0) < rank.get(minimum,3):
                raise HTTPException(status_code=403, detail=f"Active {minimum} entitlement required for this module.")
        response.headers["Cache-Control"] = "private, no-store"
        response.headers["Vary"] = "Authorization"
        return {"position": platform.course_position(identity.user_id, course_id, body.module_index)}

    @app.post("/platform/progress")
    def progress_record(body: ProgressBody, request: Request) -> dict:
        identity = platform_identity(request)
        user_id = identity.user_id if identity else (body.user_id or "local-user")
        username = _identity_display(identity) if identity else body.username
        # Browser-declared scores are not evidence of grading. Until a grading
        # endpoint signs a result, retain the activity event but no score.
        trusted_score = body.score if not services.settings.security_enforced else None
        return platform.record_progress(user_id=user_id, username=username, kind=body.kind,
                                        ref=body.ref, score=trusted_score, meta=body.meta)

    @app.get("/platform/progress/{user_id}")
    def progress_get(user_id: str, request: Request, response: Response) -> dict:
        identity = platform_identity(request)
        if identity and user_id != identity.user_id:
            raise HTTPException(status_code=403, detail="Progress belongs to another account.")
        response.headers["Cache-Control"] = "private, no-store"
        response.headers["Vary"] = "Authorization"
        return platform.progress_summary(user_id)

    @app.get("/platform/leaderboard")
    def leaderboard(limit: int = 20) -> dict:
        return {"leaderboard": platform.leaderboard(limit)}

    # survival
    @app.post("/platform/survival")
    def survival_record(body: SurvivalBody, request: Request) -> dict:
        identity = platform_identity(request)
        return platform.record_survival(user_id=identity.user_id if identity else body.user_id,
                                        username=_identity_display(identity) if identity else body.username,
                                        wave=body.wave,
                                        score=body.score, streak=body.streak,
                                        verified=not services.settings.security_enforced)

    @app.get("/platform/survival/leaderboard")
    def survival_leaderboard(limit: int = 20) -> dict:
        return {"leaderboard": platform.survival_leaderboard(limit)}

    # blog
    @app.get("/platform/blog")
    def blog_list(limit: int = 50) -> dict:
        return {"posts": platform.list_blog(limit)}

    @app.get("/platform/blog/{slug}")
    def blog_get(slug: str) -> dict:
        out = platform.get_blog(slug)
        if out is None:
            raise HTTPException(status_code=404, detail="post not found")
        return out

    @app.post("/platform/blog")
    def blog_upsert(body: BlogBody) -> dict:
        return platform.upsert_blog(slug=body.slug, title=body.title, author=body.author, excerpt=body.excerpt,
                                    body=body.body, tags=body.tags, read_minutes=body.read_minutes)

    return app


app = create_app()


def _ui_html() -> str:
    return """
<!doctype html>
<html lang="fr">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>ThePricingLibrary Practice Engine</title>
  <style>
    :root {
      color-scheme: light;
      font-family: Inter, Segoe UI, Arial, sans-serif;
      background: #f7f8fb;
      color: #172033;
    }
    * { box-sizing: border-box; }
    body { margin: 0; }
    header {
      padding: 22px 28px;
      background: #ffffff;
      border-bottom: 1px solid #e3e7ee;
      display: flex;
      justify-content: space-between;
      gap: 16px;
      align-items: center;
    }
    h1 { font-size: 22px; margin: 0; letter-spacing: 0; }
    .status { font-size: 13px; color: #536176; }
    main {
      max-width: 1280px;
      margin: 0 auto;
      padding: 24px;
      display: grid;
      grid-template-columns: 420px 1fr;
      gap: 22px;
    }
    section {
      background: #ffffff;
      border: 1px solid #e3e7ee;
      border-radius: 8px;
      padding: 18px;
    }
    h2 { font-size: 16px; margin: 0 0 14px; }
    label {
      display: block;
      font-size: 12px;
      font-weight: 650;
      color: #4b5870;
      margin: 12px 0 6px;
    }
    input, select, textarea {
      width: 100%;
      border: 1px solid #cfd6e2;
      border-radius: 6px;
      padding: 10px 11px;
      font: inherit;
      background: #fff;
      color: #172033;
    }
    textarea { min-height: 78px; resize: vertical; }
    .row { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
    button {
      border: 0;
      background: #145c9e;
      color: #fff;
      border-radius: 6px;
      padding: 10px 14px;
      font-weight: 700;
      cursor: pointer;
      margin-top: 14px;
    }
    button.secondary { background: #2f3b52; }
    button:disabled { opacity: .55; cursor: wait; }
    #output {
      white-space: pre-wrap;
      line-height: 1.48;
      font-size: 14px;
      min-height: 520px;
    }
    .sources {
      margin-top: 18px;
      border-top: 1px solid #e3e7ee;
      padding-top: 12px;
      font-size: 13px;
      color: #3c485c;
    }
    .source {
      padding: 10px 0;
      border-bottom: 1px solid #edf0f5;
    }
    .error {
      background: #fff2f0;
      border: 1px solid #ffccc7;
      color: #8c1d18;
      padding: 10px;
      border-radius: 6px;
      margin-top: 12px;
      display: none;
    }
    .toolbar { display: flex; gap: 8px; flex-wrap: wrap; }
    .preset-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 10px; }
    .preset-grid button { margin-top: 0; background: #eef3f8; color: #1b304b; }
    .meta {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 10px;
      margin-bottom: 12px;
    }
    .metric {
      border: 1px solid #e3e7ee;
      border-radius: 6px;
      padding: 10px;
      background: #fafbfc;
      font-size: 12px;
    }
    .metric b { display: block; font-size: 18px; color: #172033; }
    .library-list { margin-top: 12px; display: grid; gap: 8px; }
    .library-item {
      border: 1px solid #e3e7ee;
      border-radius: 6px;
      padding: 10px;
      cursor: pointer;
      background: #fff;
    }
    .library-item:hover { background: #f4f7fb; }
    @media (max-width: 920px) {
      main { grid-template-columns: 1fr; padding: 14px; }
      header { align-items: flex-start; flex-direction: column; }
    }
  </style>
</head>
<body>
  <header>
    <div>
      <h1>ThePricingLibrary Practice Engine</h1>
      <div class="status" id="status">Chargement...</div>
    </div>
    <div class="toolbar">
      <button class="secondary" onclick="searchOnly()">Tester le retrieval</button>
      <button class="secondary" onclick="calculateOnly()">Tester les calculs</button>
      <button class="secondary" onclick="loadLibrary()">Bibliotheque</button>
      <button class="secondary" onclick="runEvaluation()">Evaluation</button>
    </div>
  </header>

  <main>
    <section>
      <h2>Parametres</h2>
      <label>Mode</label>
      <select id="mode">
        <option value="exercise">Exercice pratique</option>
        <option value="course">Cours / module</option>
        <option value="pack">Pack pedagogique</option>
      </select>

      <label>Exemples desk</label>
      <div class="preset-grid">
        <button onclick="loadPreset('greeks')">Book greeks</button>
        <button onclick="loadPreset('swap')">Swap DV01</button>
        <button onclick="loadPreset('barrier')">Barriere FX</button>
        <button onclick="loadPreset('cds')">CDS CS01</button>
        <button onclick="loadPreset('var')">VaR</button>
        <button onclick="loadPreset('vanilla')">Call BS</button>
      </div>

      <label>Sujet</label>
      <input id="topic" placeholder="Ex: Options exotiques, VaR, credit derivatives" />

      <div class="row">
        <div>
          <label>Produit</label>
          <input id="product" placeholder="Ex: option, swap, CDS" />
        </div>
        <div>
          <label>Concept</label>
          <input id="concept" placeholder="Ex: barrier option" />
        </div>
      </div>

      <div class="row">
        <div>
          <label>Niveau</label>
          <select id="level">
            <option value="beginner">Beginner</option>
            <option value="intermediate" selected>Intermediate</option>
            <option value="advanced">Advanced</option>
            <option value="expert">Expert</option>
          </select>
        </div>
        <div>
          <label>Top K sources</label>
          <input id="topk" type="number" value="8" min="3" max="20" />
        </div>
      </div>

      <label>Prompt libre</label>
      <textarea id="freePrompt" placeholder="Ex: Genere un cas pratique de desk sur la couverture gamma proche d'une barriere."></textarea>

      <button id="generateBtn" onclick="generate()">Generer</button>
      <div class="error" id="error"></div>
    </section>

    <section>
      <div class="meta">
        <div class="metric"><span>Sources</span><b id="metricSources">-</b></div>
        <div class="metric"><span>Calculateur</span><b id="metricCalc">-</b></div>
        <div class="metric"><span>Type</span><b id="metricKind">-</b></div>
        <div class="metric"><span>Score</span><b id="metricScore">-</b></div>
      </div>
      <h2 id="resultTitle">Resultat</h2>
      <div id="output">Choisis un mode, remplis un sujet ou un produit, puis genere.</div>
      <div class="sources" id="sources"></div>
      <div class="sources">
        <strong>Bibliotheque locale</strong>
        <div class="library-list" id="library"></div>
      </div>
    </section>
  </main>

  <script>
    async function health() {
      const res = await fetch('/health');
      const data = await res.json();
      document.getElementById('status').textContent =
        `LLM: ${data.llm} | OpenAI key: ${data.openai_configured ? 'configuree' : 'manquante'} | Embeddings: ${data.embedding_backend}`;
    }

    function payloadBase() {
      return {
        topic: value('topic') || null,
        product: value('product') || null,
        concept: value('concept') || null,
        difficulty: value('level'),
        level: value('level'),
        top_k: Number(value('topk') || 8),
        language: 'fr'
      };
    }

    function value(id) {
      return document.getElementById(id).value.trim();
    }

    function setBusy(flag) {
      document.getElementById('generateBtn').disabled = flag;
      document.getElementById('generateBtn').textContent = flag ? 'Generation...' : 'Generer';
    }

    function showError(text) {
      const box = document.getElementById('error');
      box.style.display = text ? 'block' : 'none';
      box.textContent = text || '';
    }

    function renderSources(items) {
      document.getElementById('metricSources').textContent = items ? items.length : 0;
      const box = document.getElementById('sources');
      if (!items || !items.length) {
        box.innerHTML = '<strong>Sources</strong><div>Aucune source retournee.</div>';
        return;
      }
      box.innerHTML = '<strong>Sources</strong>' + items.map((s, i) => `
        <div class="source">
          <b>[S${i + 1}] ${s.title || s.source || s.document_id}</b><br>
          score ${s.score} | chunk ${s.chunk_index}<br>
          ${s.snippet}
        </div>
      `).join('');
    }

    function updateMetrics(data, evaluation) {
      const pack = data && data.metadata && data.metadata.calculation_pack;
      document.getElementById('metricKind').textContent = data ? data.kind : '-';
      document.getElementById('metricCalc').textContent = pack ? pack.family : '-';
      document.getElementById('metricScore').textContent = evaluation ? Math.round(evaluation.score * 100) + '%' : '-';
    }

    async function generate() {
      showError('');
      setBusy(true);
      try {
        const mode = value('mode');
        const base = payloadBase();
        let endpoint;
        let payload;
        if (mode === 'course') {
          endpoint = '/generate/course';
          payload = {
            topic: base.topic || base.product || base.concept || 'Finance de marche',
            product: base.product,
            concepts: base.concept ? [base.concept] : [],
            level: base.level,
            top_k: base.top_k,
            duration_minutes: 90,
            module_count: 4,
            language: 'fr'
          };
        } else if (mode === 'pack') {
          endpoint = '/generate/material-pack';
          payload = {
            topic: base.topic || base.product || base.concept || 'Finance de marche',
            product: base.product,
            concepts: base.concept ? [base.concept] : [],
            level: base.level,
            duration_minutes: 120,
            exercise_count: 3,
            language: 'fr'
          };
        } else {
          endpoint = '/generate/exercise';
          payload = {
            topic: base.topic,
            product: base.product,
            concept: base.concept,
            free_prompt: value('freePrompt') || null,
            difficulty: base.difficulty,
            top_k: base.top_k,
            exercise_format: 'mixed',
            number_of_questions: 5,
            language: 'fr'
          };
        }
        const res = await fetch(endpoint, {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || JSON.stringify(data));
        let evaluation = null;
        if (data.kind === 'exercise') {
          const ev = await fetch('/evaluation/response', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
          });
          evaluation = await ev.json();
        }
        document.getElementById('resultTitle').textContent = data.title;
        document.getElementById('output').textContent = data.content;
        updateMetrics(data, evaluation);
        renderSources(data.sources);
        loadLibrary();
      } catch (err) {
        showError(err.message);
      } finally {
        setBusy(false);
      }
    }

    async function searchOnly() {
      showError('');
      const q = [value('freePrompt'), value('topic'), value('product'), value('concept')].filter(Boolean).join(' ');
      if (!q) {
        showError('Ajoute au moins un sujet, produit, concept ou prompt.');
        return;
      }
      const res = await fetch('/rag/search', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({query: q, top_k: Number(value('topk') || 8)})
      });
      const data = await res.json();
      document.getElementById('resultTitle').textContent = 'Retrieval';
      document.getElementById('output').textContent = JSON.stringify(data.results, null, 2);
      renderSources(data.results);
    }

    async function calculateOnly() {
      showError('');
      const prompt = [value('freePrompt'), value('topic'), value('product'), value('concept')].filter(Boolean).join(' ');
      if (!prompt) {
        showError('Ajoute un prompt ou un sujet avec des donnees numeriques.');
        return;
      }
      const res = await fetch('/calculate/practice', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({prompt})
      });
      const data = await res.json();
      document.getElementById('resultTitle').textContent = data.title;
      document.getElementById('output').textContent = data.markdown;
      document.getElementById('metricCalc').textContent = data.family;
      document.getElementById('metricKind').textContent = 'calculation';
      document.getElementById('metricScore').textContent = '-';
      renderSources([]);
    }

    async function loadLibrary() {
      const res = await fetch('/library/generations?limit=12');
      const items = await res.json();
      const box = document.getElementById('library');
      if (!items.length) {
        box.innerHTML = '<div>Aucun contenu sauvegarde pour l instant.</div>';
        return;
      }
      box.innerHTML = items.map(item => `
        <div class="library-item" onclick="openLibraryItem('${item.id}')">
          <b>${item.title}</b><br>
          ${item.kind} | ${item.created_at}
        </div>
      `).join('');
    }

    async function openLibraryItem(id) {
      const res = await fetch('/library/generations/' + id);
      const item = await res.json();
      const data = item.response;
      document.getElementById('resultTitle').textContent = item.title;
      document.getElementById('output').textContent = data.content || JSON.stringify(data, null, 2);
      updateMetrics(data, null);
      renderSources(data.sources || []);
    }

    async function runEvaluation() {
      showError('');
      document.getElementById('resultTitle').textContent = 'Evaluation produit';
      document.getElementById('output').textContent = 'Execution des cas de controle...';
      const res = await fetch('/evaluation/suite?limit=3', {method: 'POST'});
      const data = await res.json();
      if (!res.ok) {
        showError(data.detail || JSON.stringify(data));
        return;
      }
      document.getElementById('output').textContent = JSON.stringify(data, null, 2);
      document.getElementById('metricScore').textContent = Math.round(data.average_score * 100) + '%';
      document.getElementById('metricKind').textContent = 'evaluation';
    }

    function loadPreset(name) {
      const presets = {
        greeks: {
          topic: 'Options book risk management',
          product: 'equity options book',
          concept: 'delta gamma vega theta hedging',
          prompt: "Genere un exercice pratique de risk management sur un book d'options actions. Donnees imposees: book delta +250k EUR par 1%, gamma -80k EUR par 1%^2, vega +120k EUR par vol point, theta -15k EUR par jour. Scenario: spot -2%, vol +3 points, un jour passe. L'etudiant doit estimer P&L delta-gamma-vega-theta, identifier le risque dominant, proposer une couverture delta et vega."
        },
        swap: {
          topic: 'Interest rate swap valuation and DV01',
          product: 'EUR interest rate swap',
          concept: 'PV par rate DV01 hedge PnL',
          prompt: 'Genere un exercice operationnel de desk rates. Donnees imposees: payer swap EUR 5Y, notionnel 100m, fixed coupon 3.20%, par swap rate actuel 3.00%, annuity approx 4.55, la courbe monte de 10bp. Calculer PV, DV01, P&L et couverture.'
        },
        barrier: {
          topic: 'FX barrier option desk case',
          product: 'FX barrier option',
          concept: 'down-and-out call gap risk',
          prompt: 'Option barriere FX. EUR/USD spot 1.0800, strike 1.1000, barriere down-and-out 1.0000, notionnel EUR 10m. Scenarios spot a 1.0500, spot a 1.0000, spot a 1.2000 sans knock-out. Evaluer payoff et gap risk.'
        },
        cds: {
          topic: 'CDS CS01 and spread shock',
          product: 'single-name CDS',
          concept: 'CS01 carry spread shock',
          prompt: 'CDS notionnel 50m spread 120bp risky annuity 4.2 shock 25bp. Calculer CS01, carry et P&L spread.'
        },
        var: {
          topic: 'Parametric VaR desk limit',
          product: 'portfolio',
          concept: 'VaR stress risk limit',
          prompt: 'VaR portefeuille 20m volatilite 2% confiance 95% horizon 1 jour. Calculer VaR et discuter limite.'
        },
        vanilla: {
          topic: 'Black-Scholes call desk approximation',
          product: 'equity call option',
          concept: 'price delta gamma vega',
          prompt: 'Call vanilla spot 100 strike 100 vol 20% maturite 1 taux 5%. Calculer prix et greeks.'
        }
      };
      const p = presets[name];
      document.getElementById('topic').value = p.topic;
      document.getElementById('product').value = p.product;
      document.getElementById('concept').value = p.concept;
      document.getElementById('freePrompt').value = p.prompt;
    }

    health();
    loadLibrary();
  </script>
</body>
</html>
"""
