"""The authenticated product CLI (`tpl`), separate from the operator CLI.

No token minting, raw HTTP proxy, fabricated fallback or desktop interaction.
Local development sessions require an explicit gateway command; all identity
and premium decisions belong to the server.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import socket
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener
import uuid

SCHEMA = "tpl.cli.result.v1"
MAX_INPUT = 2_000_000
MAX_RESPONSE = 32_000_000
EXITS = {401: 3, 403: 4, 404: 5, 409: 6, 400: 7, 422: 7, 429: 8, 501: 9}


class CliFailure(Exception):
    def __init__(self, message, exit_code=2, status=None):
        self.message, self.exit_code, self.status = message, exit_code, status
        super().__init__(message)


class Parser(argparse.ArgumentParser):
    def error(self, message):
        # argparse can echo an accidentally supplied token in unknown arguments.
        raise CliFailure("Invalid command or option. Use --help. Supply tokens through TPL_ACCESS_TOKEN or --token-file.")


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *_args, **_kwargs):
        return None  # Never forward an Authorization header to another origin.


def strict_json(text):
    def pairs(items):
        value = {}
        for key, item in items:
            if key in value:
                raise ValueError("Duplicate JSON key.")
            value[key] = item
        return value
    return json.loads(text, object_pairs_hook=pairs, parse_constant=lambda _value: (_ for _ in ()).throw(ValueError("Non-finite JSON number.")))


def input_object(filename):
    try:
        raw = sys.stdin.read(MAX_INPUT + 1) if filename == "-" else Path(filename).read_bytes()
        if len(raw) > MAX_INPUT:
            raise ValueError()
        value = strict_json(raw)
        if not isinstance(value, dict):
            raise ValueError()
        return value
    except (OSError, ValueError, TypeError):
        raise CliFailure("Input must be a readable JSON object of at most 2 MB, without duplicate keys or non-finite numbers.") from None


def token_value(filename=None):
    filename = filename or os.environ.get("TPL_TOKEN_FILE")
    if not filename and not os.environ.get("TPL_ACCESS_TOKEN"):
        from .cli_auth import default_session_file
        if default_session_file().is_file():
            filename = default_session_file()
    try:
        if filename:
            if Path(filename).stat().st_size > 65536:
                raise ValueError()
            token = Path(filename).read_text(encoding="utf-8-sig").strip()
            if token.startswith("{"):
                token = strict_json(token).get("access_token", "")
        else:
            token = os.environ.get("TPL_ACCESS_TOKEN", "").strip()
        if not isinstance(token, str) or len(token) > 16384 or re.search(r"\s", token):
            raise ValueError()
        return token
    except (OSError, ValueError, TypeError, AttributeError):
        raise CliFailure("Token source is unreadable or invalid; no credential value was printed.") from None


class Client:
    def __init__(self, base, token="", timeout=30, retries=1):
        value = urlsplit(base)
        if value.username or value.password or value.query or value.fragment or value.scheme not in {"http", "https"} or not value.hostname:
            raise CliFailure("API URL must be an HTTP(S) origin/path without credentials, query or fragment.")
        if value.scheme == "http" and value.hostname not in {"localhost", "127.0.0.1", "::1"}:
            raise CliFailure("Bearer HTTP is restricted to loopback. Use HTTPS for a remote API.")
        self.base, self.token = base.rstrip("/"), token
        self.timeout, self.retries = timeout, retries
        self.opener = build_opener(NoRedirect())
        self.last_request_id = None

    def call(self, route, method="GET", body=None, query=None, *, binary=False, idempotent=False):
        url = self.base + route + (("?" + urlencode({k: v for k, v in query.items() if v is not None})) if query else "")
        headers = {"Accept": "application/json, text/csv, text/markdown, application/zip", "User-Agent": "ThePricingLibrary-CLI/1"}
        if self.token:
            headers["Authorization"] = "Bearer " + self.token
        data = None
        if body is not None:
            data = json.dumps(body, allow_nan=False).encode("utf-8")
            if len(data) > MAX_INPUT:
                raise CliFailure("Request exceeds the 2 MB input budget.")
            headers["Content-Type"] = "application/json"
        attempts = 1 + (self.retries if method == "GET" or idempotent else 0)
        for attempt in range(attempts):
            try:
                with self.opener.open(Request(url, data=data, headers=headers, method=method), timeout=self.timeout) as response:
                    raw = response.read(MAX_RESPONSE + 1)
                    self.last_request_id = response.headers.get("X-Request-ID")
                    if len(raw) > MAX_RESPONSE:
                        raise CliFailure("Response exceeds the 32 MB budget.", 8)
                    content_type = response.headers.get_content_type()
                    if binary:
                        return raw
                    if content_type == "application/json":
                        return strict_json(raw)
                    return {"content": raw.decode("utf-8"), "content_type": content_type}
            except HTTPError as exc:
                if exc.code in {429, 502, 503, 504} and attempt + 1 < attempts:
                    time.sleep(min(attempt + 1, 2))
                    continue
                try:
                    detail = strict_json(exc.read(16384)).get("detail", "Request was rejected.")
                    if isinstance(detail, dict) and isinstance(detail.get("message"), str):
                        detail = detail["message"]
                    if not isinstance(detail, str):
                        detail = "Request failed server-side validation."
                except (ValueError, AttributeError):
                    detail = "The server rejected the request."
                if self.token:
                    detail = detail.replace(self.token, "[REDACTED]")
                raise CliFailure(detail[:1000], EXITS.get(exc.code, 8 if exc.code >= 500 else 7), exc.code) from None
            except (URLError, socket.timeout, TimeoutError, ConnectionError):
                if attempt + 1 < attempts:
                    time.sleep(min(attempt + 1, 2))
                    continue
                raise CliFailure("API connection failed or timed out; no fallback result was generated.", 8) from None
            except (UnicodeError, ValueError):
                raise CliFailure("The API returned an invalid response format.", 8) from None


def segment(value):
    if not value or len(value) > 160 or value in {".", ".."} or "/" in value or "\\" in value:
        raise CliFailure("Invalid resource identifier.")
    return quote(value, safe="")


def bounded(value, minimum=1, maximum=100):
    if type(value) is not int or not minimum <= value <= maximum:
        raise CliFailure(f"Value must be an integer from {minimum} to {maximum}.")
    return value


def save_output(value, filename, overwrite=False):
    if isinstance(value, bytes):
        raw = value
    elif isinstance(value, dict) and "content" in value and set(value) <= {"content", "content_type"}:
        raw = value["content"].encode("utf-8")
    else:
        raw = (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode("utf-8")
    path = Path(filename)
    try:
        with path.open("wb" if overwrite else "xb") as handle:
            handle.write(raw)
    except OSError:
        raise CliFailure("Output could not be written. Existing files require --overwrite.") from None
    return {"file": str(path.resolve()), "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}


def parser():
    root = Parser(prog="tpl", description="Authenticated ThePricingLibrary product CLI; operator maintenance remains pricinglibrary_rag.cli.")
    root.add_argument("--api", default=os.environ.get("TPL_API_URL", os.environ.get("TPL_BASE_URL")))
    root.add_argument("--token-file", help="Plain token or JSON access_token file. Never pass a token as an argument.")
    root.add_argument("--timeout", type=int, default=30)
    root.add_argument("--retries", type=int, default=1, help="GET/idempotent retry budget only, 0..2.")
    groups = root.add_subparsers(dest="group", required=True)
    def leaf(group, action, *, resource=False, input=False, variant=False, request_id=False):
        if group not in subs:
            subs[group] = groups.add_parser(group).add_subparsers(dest="action", required=True)
        p = subs[group].add_parser(action)
        if resource:
            p.add_argument("id")
        if input:
            p.add_argument("--input", required=True, help="JSON file, or - for stdin.")
        if variant:
            p.add_argument("--variant", choices=("primary", "transfer"), default="primary")
        if request_id:
            p.add_argument("--request-id", help="Reuse the same key to recover a retry; changed inputs with that key are rejected.")
        p.add_argument("--output", help="Export result to a file; stdout remains a JSON receipt.")
        p.add_argument("--overwrite", action="store_true")
        return p
    subs = {}
    d = groups.add_parser("doctor"); d.set_defaults(action="check")
    groups.add_parser("coverage").set_defaults(action="list")
    leaf("auth", "whoami")
    from .cli_auth import add_parsers as add_auth_parsers
    add_auth_parsers(leaf)
    leaf("courses", "list")
    for action in ("preview", "read", "resume"):
        p = leaf("courses", action, resource=True)
        if action == "read": p.add_argument("--language", choices=("fr", "en"), default="en")
    for action in ("open", "complete"):
        p = leaf("courses", action, resource=True); p.add_argument("--module", type=int, required=True)
    leaf("courses", "progress")
    for action in ("catalog", "state", "resume", "export", "metrics"):
        p = leaf("interview", action)
        if action == "export": p.add_argument("--format", choices=("json", "report", "csv", "anki"), default="json")
    leaf("interview", "calendar", input=True)
    leaf("interview", "onboard", input=True)
    leaf("interview", "task", resource=True, variant=True)
    leaf("interview", "answer", resource=True, input=True, variant=True, request_id=True).add_argument("--preview", action="store_true")
    leaf("interview", "reveal", resource=True, variant=True, request_id=True)
    leaf("interview", "review", resource=True, input=True, request_id=True)
    leaf("exercises", "generate", input=True, request_id=True)
    leaf("exercises", "catalog")
    p = leaf("exercises", "library"); p.add_argument("--limit", type=int, default=30); p.add_argument("--offset", type=int, default=0)
    leaf("exercises", "open", resource=True)
    for action in ("task", "attempts", "attempt"):
        leaf("exercises", action, resource=True)
    leaf("exercises", "answer", resource=True, input=True, request_id=True)
    leaf("exercises", "review", resource=True, input=True, request_id=True)
    p = leaf("exercises", "export-attempt", resource=True); p.add_argument("--format", choices=("json", "md"), default="json")
    leaf("exercises", "reference", resource=True)
    leaf("exercises", "run-reference", resource=True)
    p = leaf("exercises", "export-reference", resource=True); p.add_argument("--format", choices=("python", "ipynb"), default="python")
    p = leaf("exercises", "export", resource=True); p.add_argument("--format", choices=("json", "markdown"), default="json")
    leaf("tools", "list")
    leaf("tools", "example", resource=True)
    p = leaf("tools", "run", resource=True, input=True); p.add_argument("--format", default="json")
    p = leaf("forum", "list"); p.add_argument("--channel", default="forum"); p.add_argument("--limit", type=int, default=30)
    leaf("forum", "create", input=True)
    for action in ("thread", "vote"):
        leaf("forum", action, resource=True)
    leaf("forum", "reply", resource=True, input=True)
    p = leaf("jobs", "list"); p.add_argument("--limit", type=int, default=30); p.add_argument("--kind")
    leaf("jobs", "publish", input=True)
    leaf("jobs", "sources")
    leaf("jobs", "apply", resource=True, input=True)
    leaf("blog", "list")
    leaf("blog", "open", resource=True)
    leaf("blog", "publish", input=True)
    leaf("newsletter", "subscribe", input=True)
    p = leaf("leaderboard", "activity"); p.add_argument("--limit", type=int, default=20)
    p = leaf("leaderboard", "survival"); p.add_argument("--limit", type=int, default=20)
    leaf("admin", "counts")
    p = leaf("admin", "support"); p.add_argument("--limit", type=int, default=30)
    leaf("admin", "market-providers")
    leaf("market", "catalog"); leaf("market", "universe")
    p = leaf("market", "history", resource=True); p.add_argument("--points", type=int, default=260); p.add_argument("--provider")
    leaf("backtest", "instruments")
    for action in ("run", "walkforward", "scan"):
        p = leaf("backtest", action); p.add_argument("--instrument", default="EURUSD"); p.add_argument("--max-bars", type=int, default=1000); p.add_argument("--strategy", default="trend_following"); p.add_argument("--capital", type=float)
    leaf("rfq", "run", input=True)
    leaf("rfq", "trade", input=True, request_id=True)
    p = leaf("rfq", "tick"); p.add_argument("--seconds", type=float, default=1)
    leaf("rfq", "state")
    leaf("services", "availability")
    for action in ("list", "entitlement", "status"):
        leaf("plans", action)
    p = leaf("plans", "checkout"); p.add_argument("--plan", choices=("starter", "student", "pro"), required=True)
    for action in ("availability", "manifest", "download", "checkout"):
        leaf("kit", action)
    leaf("support", "status"); leaf("support", "report", input=True)
    # Learning-workflow routes are registered independently; no browser coupling.
    leaf("learning", "catalog")
    p = leaf("survival", "start", request_id=True); p.add_argument("--input", help="Optional JSON settings; default wave is core.")
    leaf("survival", "list")
    leaf("survival", "state", resource=True)
    leaf("survival", "answer", resource=True, input=True, request_id=True)
    leaf("survival", "next", resource=True, request_id=True)
    leaf("notebooks", "list")
    p = leaf("notebooks", "export", resource=True); p.add_argument("--format", choices=("ipynb", "py"), default="ipynb")
    leaf("notebooks", "open", resource=True)
    p = leaf("notebooks", "run", resource=True); p.add_argument("--input", help="Optional JSON ticket; defaults are explicit teaching inputs.")
    return root


def dispatch(args, client):
    group, action = args.group, args.action
    key = f"{group}.{action}"
    get, post = client.call, lambda path, body=None, **kw: client.call(path, "POST", body, **kw)
    identifier = segment(args.id) if hasattr(args, "id") else None
    body = input_object(args.input) if getattr(args, "input", None) else None
    if group == "doctor":
        identity = get("/learner/me") if client.token else None
        return {"health": get("/health"), "readiness": get("/ready"), "catalog": get("/learner/catalog"),
                "authentication": {"status": "verified", "user_id": identity["user_id"], "role": identity["role"]} if identity else "anonymous"}
    if group == "coverage":
        top = next(value for value in parser()._actions if isinstance(value, argparse._SubParsersAction))
        commands = {}
        for name, child in top.choices.items():
            nested = next((value for value in child._actions if isinstance(value, argparse._SubParsersAction)), None)
            commands[name] = sorted(nested.choices) if nested else []
        return {"schema": "tpl.cli.coverage.v1", "commands": commands, "command_count": sum(len(v) or 1 for v in commands.values()),
                "notice": "Command coverage is not proof of a public sale, external service, human support or market demand."}
    if group == "auth":
        return get("/learner/me")
    if group == "courses":
        if action == "list": return get("/learner/catalog")["courses"]
        if action == "read": return get(f"/courses/{identifier}/script", query={"language": args.language})
        if action in {"preview", "resume"}: return get(f"/learner/courses/{identifier}/{'state' if action == 'resume' else action}")
        if action == "progress": return get("/platform/progress/" + segment(get("/learner/me")["user_id"]))
        module = bounded(args.module, 0, 63)
        if action == "open": return client.call(f"/platform/courses/{identifier}/position", "PUT", {"module_index": module}, idempotent=True)
        return post(f"/learner/courses/{identifier}/complete", {"module_index": module}, idempotent=True)
    if group == "interview":
        if action in {"catalog", "state"}: return get(f"/interview/{action}")
        if action == "export":
            return get("/interview/export") if args.format == "json" else get("/learning/interview/export", query={"format": args.format})
        if action == "calendar": return post("/learning/interview/calendar", body)
        if action == "metrics": return get("/interview/pilot/metrics")
        if action == "resume": return get("/interview/state")
        if action == "onboard": return post("/interview/onboarding", body, idempotent=True)
        if action == "task": return get(f"/interview/cases/{identifier}", query={"variant": args.variant})
        request_id = args.request_id or (body or {}).get("client_request_id") or str(uuid.uuid4())
        args.used_request_id = request_id
        if action == "review": return post(f"/interview/attempts/{identifier}/review", {**body, "client_request_id": request_id}, idempotent=True)
        value = {**(body or {}), "case_id": args.id, "variant": args.variant, "client_request_id": request_id}
        endpoint = "preview/check" if action == "answer" and args.preview else "attempts" if action == "answer" else "reveal"
        return post("/interview/" + endpoint, value, idempotent=True)
    if group == "exercises":
        if action == "reference": return get(f"/learning/exercises/{identifier}/reference")
        if action == "run-reference": return post(f"/learning/exercises/{identifier}/reference/run", {}, idempotent=True)
        if action == "export-reference": return get(f"/learning/exercises/{identifier}/reference/export", query={"format": args.format})
        if action == "catalog": return get("/learning/catalog")["practice_exercises"]
        if action == "generate":
            request_id = args.request_id or body.get("client_request_id") or str(uuid.uuid4())
            args.used_request_id = request_id
            return post("/agent/exercise", {"language": "en", **body, "client_request_id": request_id}, idempotent=True)
        if action == "library": return get("/platform/exercises", query={"limit": bounded(args.limit), "offset": bounded(args.offset, 0, 100000)})
        if action in {"task", "attempts"}: return get(f"/learning/exercises/{identifier}/{action}")
        if action in {"attempt", "export-attempt"}:
            return get(f"/learning/exercise-attempts/{identifier}" + ("/export" if action == "export-attempt" else ""), query={"format": args.format} if action == "export-attempt" else None)
        if action in {"answer", "review"}:
            request_id = args.request_id or body.get("client_request_id") or str(uuid.uuid4()); args.used_request_id = request_id
            path = f"/learning/exercises/{identifier}/attempts" if action == "answer" else f"/learning/exercise-attempts/{identifier}/review"
            return post(path, {**body, "client_request_id": request_id}, idempotent=True)
        try:
            record = get(f"/platform/exercises/{identifier}")
        except CliFailure as exc:
            if exc.status != 404:
                raise
            task = get(f"/learning/exercises/{identifier}/task")
            if action == "open": return task
            if args.format == "markdown": return {"content": task["brief"], "content_type": "text/markdown"}
            return {"schema": "tpl.exercise-task.v1", "task": task}
        if action == "open": return record
        if args.format == "markdown": return {"content": record["response"]["content"], "content_type": "text/markdown"}
        return {"schema": "tpl.exercise-record.v1", "record": record}
    if group == "tools":
        if action == "list": return get("/learner/tools")
        if action == "example": return get(f"/learner/tools/{identifier}/example")["input"]
        return post(f"/learner/tools/{identifier}", {"input": body, "format": args.format}, idempotent=True)
    if group == "forum":
        prefix = "/platform/community/threads"
        if action == "list": return get(prefix, query={"channel": args.channel, "limit": bounded(args.limit)})
        if action == "create": return post(prefix, body)
        if action == "reply": return post(f"{prefix}/{identifier}/comments", body)
        if action == "vote": return post(f"{prefix}/{identifier}/vote")
        threads = get(prefix, query={"limit": 100})["threads"]
        item = next((row for row in threads if row["id"] == args.id), None)
        if item is None: raise CliFailure("Thread was not found in the current listing.", 5, 404)
        return {"thread": item, **get(f"{prefix}/{identifier}/comments")}
    if group == "jobs":
        if action == "publish": return post("/platform/jobs", body)
        if action == "sources": return get("/platform/jobs/sources")
        if action == "list": return get("/platform/jobs", query={"limit": bounded(args.limit), "kind": args.kind})
        return post(f"/platform/jobs/{identifier}/apply", body)
    if group == "blog":
        if action == "publish": return post("/platform/blog", body)
        return get("/platform/blog" + (f"/{identifier}" if action == "open" else ""))
    if group == "newsletter": return post("/platform/newsletter", body)
    if group == "leaderboard":
        path = "/platform/leaderboard" if action == "activity" else "/platform/survival/leaderboard"
        return get(path, query={"limit": bounded(args.limit, 1, 100)})
    if group == "admin":
        path = {"counts": "/platform/admin/counts", "support": "/platform/bug-reports", "market-providers": "/market/providers"}[action]
        return get(path, query={"limit": bounded(args.limit, 1, 100)} if action == "support" else None)
    if group == "market":
        if action != "history": return get("/market/" + action)
        return get(f"/market/history/{identifier}", query={"points": bounded(args.points, 2, 2000), "provider": args.provider})
    if group == "backtest":
        if action == "instruments": return get("/strategy/instruments")
        query = {"max_bars": bounded(args.max_bars, 100, 40000)}
        if action != "scan": query["instrument"] = args.instrument
        if action == "walkforward": query["strategy_name"] = args.strategy
        if action == "run" and args.capital is not None:
            if not 1 <= args.capital <= 1e12: raise CliFailure("Capital is outside its supported range.")
            query["capital"] = args.capital
        return post("/strategy/" + ("backtest" if action == "run" else action), query=query)
    if group == "rfq":
        if action == "state": return get("/agent/desk/state")
        if action == "tick":
            if not 0 < args.seconds <= 86400: raise CliFailure("Paper time advance must be more than zero and at most one day.")
            return post("/agent/desk/tick", query={"seconds": args.seconds})
        if action == "trade":
            request_id = args.request_id or (body or {}).get("idempotency_key") or str(uuid.uuid4())
            if args.request_id and (body or {}).get("idempotency_key") not in (None, args.request_id):
                raise CliFailure("The --request-id and input idempotency_key disagree; no trade was submitted.")
            args.used_request_id = request_id
            return post("/agent/desk/trade", {**(body or {}), "idempotency_key": request_id}, idempotent=True)
        return post("/agent/desk/" + action, body)
    if group == "services": return get("/learner/services")
    if group == "plans":
        if action == "entitlement": return get("/billing/entitlement")
        if action == "checkout": return post("/billing/checkout", {"plan": args.plan})
        value = get("/billing/config")
        if action == "status" and client.token:
            value["account_entitlement"] = get("/billing/entitlement")
            value["transaction_verified_by_cli"] = False
        return value
    if group == "kit":
        path = "/products/market-finance-starter-kit/"
        if action == "checkout": return post(path + action, {})
        if action != "download": return get(path + action)
        if not args.output: raise CliFailure("Kit download requires --output <zip-file>.")
        manifest = get(path + "manifest")
        data = get(path + "download", binary=True)
        expected = manifest.get("bundle", {}).get("sha256")
        if not expected or hashlib.sha256(data).hexdigest() != expected:
            raise CliFailure("Downloaded bundle does not match the entitled manifest checksum.", 8)
        return data
    if group == "support": return post("/platform/bug-reports", body) if action == "report" else get("/learner/services")["support"]
    if group == "learning": return get("/learning/catalog")
    if group == "notebooks":
        if action == "list": return get("/learning/notebooks")
        if action == "open": return get(f"/learning/notebooks/{identifier}")
        if action == "export": return get(f"/learning/notebooks/{identifier}/export", query={"format": args.format})
        return post(f"/learning/notebooks/{identifier}/run", body or {})
    if group == "survival":
        if action == "list": return get("/learning/survival/runs")
        if action == "start":
            request_id = args.request_id or (body or {}).get("client_request_id") or str(uuid.uuid4()); args.used_request_id = request_id
            return post("/learning/survival/runs", {"wave": "core", **(body or {}), "client_request_id": request_id}, idempotent=True)
        if action == "state": return get(f"/learning/survival/runs/{identifier}")
        request_id = args.request_id or (body or {}).get("client_request_id") or str(uuid.uuid4())
        args.used_request_id = request_id
        return post(f"/learning/survival/runs/{identifier}/{'next' if action == 'next' else 'answers'}", {**(body or {}), "client_request_id": request_id}, idempotent=True)
    raise CliFailure("Command is not implemented.", 9)


def main(argv=None):
    command, args, client = "parse", None, None
    try:
        args = parser().parse_args(argv)
        command = f"{args.group}.{args.action}"
        from .cli_auth import AuthFailure, dispatch_auth, stored_api_url
        auth_action = args.group == "auth" and args.action != "whoami"
        api_url = args.api or stored_api_url(args.token_file) or "http://127.0.0.1:8000"
        client = Client(api_url, "" if auth_action else token_value(args.token_file), bounded(args.timeout, 1, 120), bounded(args.retries, 0, 2))
        if auth_action:
            try:
                result = dispatch_auth(args)
            except AuthFailure as exc:
                raise CliFailure(exc.message, exc.exit_code, exc.status) from None
        else:
            result = dispatch(args, client)
        if getattr(args, "output", None):
            result = save_output(result, args.output, args.overwrite)
        meta = {"request_id": client.last_request_id}
        if getattr(args, "used_request_id", None): meta["idempotency_key"] = args.used_request_id
        print(json.dumps({"schema": SCHEMA, "ok": True, "command": command, "data": result, "meta": meta}, ensure_ascii=False, allow_nan=False))
        return 0
    except CliFailure as exc:
        meta = {"idempotency_key": args.used_request_id} if args and getattr(args, "used_request_id", None) else {}
        print(json.dumps({"schema": SCHEMA, "ok": False, "command": command, "error": {"message": exc.message, "exit_code": exc.exit_code, "http_status": exc.status}, "meta": meta}, ensure_ascii=False))
        return exc.exit_code
    except (OSError, ValueError, TypeError, KeyError):
        print(json.dumps({"schema": SCHEMA, "ok": False, "command": command,
                          "error": {"message": "The command could not complete its data contract; no fallback result was generated.", "exit_code": 8}}))
        return 8


if __name__ == "__main__":
    raise SystemExit(main())
