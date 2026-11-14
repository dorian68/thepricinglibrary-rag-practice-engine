from __future__ import annotations

import hashlib
import hmac
import base64
import json
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from fastapi import HTTPException, Request

from .config import Settings

if TYPE_CHECKING:
    from .storage import LocalStore


PUBLIC = "public"
PUBLIC_RATE_LIMITED = "public_rate_limited"
MEMBER = "member"
OPERATOR = "operator"
IDENTITY = "identity"
WEBHOOK = "webhook"


@dataclass(frozen=True)
class SecurityReadiness:
    ready: bool
    environment: str
    enforcement: str
    errors: tuple[str, ...]

    def as_dict(self) -> dict:
        return {
            "ready": self.ready,
            "environment": self.environment,
            "enforcement": self.enforcement,
            "errors": list(self.errors),
        }


@dataclass(frozen=True)
class AuthenticatedIdentity:
    user_id: str
    email: str
    role: str = MEMBER


class ExternalJwtVerifier:
    """Validate Supabase/OIDC access tokens against pinned issuer/audience/JWKS."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._remote_client = None

    @property
    def configured(self) -> bool:
        return bool(
            self.settings.auth_issuer
            and self.settings.auth_audience
            and (self.settings.auth_jwks_url or self.settings.auth_jwks_json)
            and self.settings.auth_algorithms
        )

    def verify(self, token: str) -> AuthenticatedIdentity:
        import jwt

        try:
            header = jwt.get_unverified_header(token)
            algorithm = str(header.get("alg") or "")
            if algorithm not in self.settings.auth_algorithms:
                raise HTTPException(status_code=401, detail="Session token algorithm is not allowed.")
            if self.settings.auth_jwks_json:
                jwks = json.loads(self.settings.auth_jwks_json)
                kid = header.get("kid")
                match = next((item for item in jwks.get("keys", []) if item.get("kid") == kid), None)
                if match is None:
                    raise HTTPException(status_code=401, detail="Session token signing key is unknown.")
                signing_key = jwt.PyJWK.from_dict(match, algorithm=algorithm).key
            else:
                if self._remote_client is None:
                    self._remote_client = jwt.PyJWKClient(
                        self.settings.auth_jwks_url,
                        cache_keys=True,
                        timeout=5,
                    )
                signing_key = self._remote_client.get_signing_key_from_jwt(token).key
            claims = jwt.decode(
                token,
                signing_key,
                algorithms=list(self.settings.auth_algorithms),
                audience=self.settings.auth_audience,
                issuer=self.settings.auth_issuer,
                options={"require": ["exp", "sub"]},
            )
        except HTTPException:
            raise
        except Exception as exc:
            # Provider/JWKS transport failures are operational, not an invalid
            # credential. PyJWT exposes this class on supported versions.
            connection_error = getattr(jwt, "PyJWKClientConnectionError", ())
            if connection_error and isinstance(exc, connection_error):
                raise HTTPException(status_code=503, detail="Identity provider keys are unavailable.") from exc
            raise HTTPException(status_code=401, detail="Invalid session token.") from exc

        user_id = str(claims.get("sub") or "").strip()
        email = str(claims.get("email") or "").strip().lower()
        if not user_id or not email or "@" not in email:
            raise HTTPException(status_code=401, detail="Session token has no usable identity.")
        # Supabase ``app_metadata`` is signed and server-controlled, unlike
        # user_metadata.  Only that claim may elevate a browser session to the
        # operator role used by the small admin surface.
        app_metadata = claims.get("app_metadata")
        app_role = str(app_metadata.get("role") or "").strip().lower() if isinstance(app_metadata, dict) else ""
        role = OPERATOR if app_role == "admin" else MEMBER
        return AuthenticatedIdentity(user_id=user_id, email=email, role=role)


def _b64url_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def _b64url_decode(raw: str) -> bytes:
    return base64.urlsafe_b64decode(raw + "=" * (-len(raw) % 4))


def mint_session_token(
    secret: str,
    *,
    user_id: str,
    email: str,
    expires_at: int,
    role: str = MEMBER,
) -> str:
    """Mint an HS256 session token for a trusted identity gateway or tests."""

    header = _b64url_encode(json.dumps({"alg": "HS256", "typ": "JWT"}, separators=(",", ":")).encode())
    payload = _b64url_encode(
        json.dumps(
            {"sub": user_id, "email": email, "exp": int(expires_at), "role": role},
            separators=(",", ":"),
        ).encode()
    )
    signing_input = f"{header}.{payload}"
    signature = _b64url_encode(hmac.new(secret.encode(), signing_input.encode(), hashlib.sha256).digest())
    return f"{signing_input}.{signature}"


def verify_session_token(token: str, secret: str, *, now: int | None = None) -> AuthenticatedIdentity:
    """Verify a compact HS256 identity token without accepting algorithm changes."""

    try:
        header_raw, payload_raw, signature = token.split(".", 2)
        header = json.loads(_b64url_decode(header_raw))
        payload = json.loads(_b64url_decode(payload_raw))
    except Exception as exc:  # malformed base64/JSON/token structure
        raise HTTPException(status_code=401, detail="Invalid session token.") from exc
    if header != {"alg": "HS256", "typ": "JWT"}:
        raise HTTPException(status_code=401, detail="Invalid session token.")
    expected = _b64url_encode(
        hmac.new(secret.encode(), f"{header_raw}.{payload_raw}".encode(), hashlib.sha256).digest()
    )
    if not hmac.compare_digest(signature, expected):
        raise HTTPException(status_code=401, detail="Invalid session token.")
    current = int(time.time() if now is None else now)
    try:
        expires_at = int(payload["exp"])
    except (KeyError, TypeError, ValueError) as exc:
        raise HTTPException(status_code=401, detail="Invalid session token.") from exc
    if expires_at <= current:
        raise HTTPException(status_code=401, detail="Session token expired.")
    user_id = str(payload.get("sub") or "").strip()
    email = str(payload.get("email") or "").strip().lower()
    if not user_id or not email or "@" not in email:
        raise HTTPException(status_code=401, detail="Session token has no usable identity.")
    return AuthenticatedIdentity(user_id=user_id, email=email, role=str(payload.get("role") or MEMBER))


class SQLiteRateLimiter:
    """Atomic fixed-window limiter shared by API workers using the same DB.

    The previous process-local deque could be bypassed by switching workers and
    lost all state on restart. SQLite's ``BEGIN IMMEDIATE`` makes the increment
    atomic across processes while keeping the deployment dependency-free.
    Only hashed principals are persisted; API keys are never stored.
    """

    def __init__(self, db_path: Path, *, window_seconds: int = 60) -> None:
        self.db_path = Path(db_path)
        self.window_seconds = max(1, int(window_seconds))
        self._ensure_schema()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path, timeout=5.0)
        connection.execute("PRAGMA busy_timeout = 5000")
        return connection

    def _ensure_schema(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS api_rate_limits (
                    scope TEXT NOT NULL,
                    principal_hash TEXT NOT NULL,
                    window_start INTEGER NOT NULL,
                    hits INTEGER NOT NULL,
                    PRIMARY KEY (scope, principal_hash)
                )
                """
            )

    def consume(self, *, scope: str, principal: str, limit: int, now: float | None = None) -> int:
        """Consume one request and return remaining capacity.

        Raises a 429 HTTP error with a Retry-After header when the window is
        exhausted. ``principal`` is hashed before persistence.
        """

        if limit <= 0:
            return 0
        timestamp = int(time.time() if now is None else now)
        window_start = timestamp - (timestamp % self.window_seconds)
        principal_hash = hashlib.sha256(principal.encode("utf-8")).hexdigest()

        connection = self._connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute(
                "SELECT window_start, hits FROM api_rate_limits WHERE scope = ? AND principal_hash = ?",
                (scope, principal_hash),
            ).fetchone()
            hits = int(row[1]) if row and int(row[0]) == window_start else 0
            if hits >= limit:
                connection.rollback()
                retry_after = max(1, window_start + self.window_seconds - timestamp)
                raise HTTPException(
                    status_code=429,
                    detail="Rate limit exceeded.",
                    headers={"Retry-After": str(retry_after)},
                )
            hits += 1
            connection.execute(
                """
                INSERT INTO api_rate_limits(scope, principal_hash, window_start, hits)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(scope, principal_hash) DO UPDATE SET
                    window_start = excluded.window_start,
                    hits = excluded.hits
                """,
                (scope, principal_hash, window_start, hits),
            )
            connection.commit()
            return max(0, limit - hits)
        finally:
            connection.close()


class ApiSecurity:
    """Production auth/RBAC and rate-limit policy for the FastAPI surface."""

    _PUBLIC_MUTATIONS = {
        "/interview/preview/check",
        "/calculate/practice",
        "/platform/bug-reports",
        "/platform/newsletter",
        "/telemetry/rum",
    }
    _MEMBER_MUTATIONS = {
        "/agent/ag-ui/run",
        "/agent/course",
        "/agent/desk/run",
        "/agent/desk/trade",
        "/agent/desk/tick",
        "/agent/exercise",
        "/evaluation/response",
        "/platform/progress",
        "/platform/survival",
        "/rag/search",
    }
    _OPERATOR_READ_PREFIXES = (
        "/agent/approvals",
        "/agent/sessions",
        "/agent/tasks",
        "/agent/tools",
        "/documents",
        "/evaluation",
        "/library",
    )
    _OPERATOR_READ_EXACT = {
        "/",
        "/market/providers",
        "/metrics",
        "/platform/admin/counts",
        "/platform/bug-reports",
        "/platform/jobs/sources",
        "/ui",
    }
    _MEMBER_READ_PREFIXES = (
        "/agent/crypto/vol",
        "/agent/desk/state",
        "/market/catalog",
        "/market/history/",
        "/market/intraday/",
        "/market/universe",
        "/platform/progress/",
    )
    _PLAN_RANK = {"starter": 1, "student": 2, "pro": 3}
    _PREMIUM_MUTATIONS = {
        "/agent/exercise": "starter",
        "/generate/exercise": "starter",
        "/rag/search": "starter",
        "/agent/course": "student",
        "/evaluation/response": "student",
        "/generate/course": "student",
        "/platform/survival": "student",
        "/agent/ag-ui/run": "pro",
        "/agent/desk/run": "pro",
        "/agent/desk/trade": "pro",
        "/agent/desk/tick": "pro",
        "/generate/material-pack": "pro",
    }

    def __init__(self, settings: Settings, *, store: "LocalStore | None" = None) -> None:
        self.settings = settings
        self.store = store
        self.external_identity = ExternalJwtVerifier(settings)
        self.readiness = self._readiness()
        self._limiter: SQLiteRateLimiter | None = None
        if settings.rate_limit_per_min > 0:
            self._limiter = SQLiteRateLimiter(
                settings.db_path,
                window_seconds=settings.rate_limit_window_seconds,
            )

    def _readiness(self) -> SecurityReadiness:
        errors: list[str] = []
        if self.settings.security_enforced:
            if not self.settings.api_key or len(self.settings.api_key) < 32:
                errors.append("member_api_key_missing_or_too_short")
            if not self.settings.operator_api_key or len(self.settings.operator_api_key) < 32:
                errors.append("operator_api_key_missing_or_too_short")
            if (
                self.settings.api_key
                and self.settings.operator_api_key
                and hmac.compare_digest(self.settings.api_key, self.settings.operator_api_key)
            ):
                errors.append("member_and_operator_keys_must_differ")
            if self.settings.rate_limit_per_min <= 0:
                errors.append("rate_limit_must_be_positive")
            external_fields_present = any(
                (
                    self.settings.auth_issuer,
                    self.settings.auth_audience,
                    self.settings.auth_jwks_url,
                    self.settings.auth_jwks_json,
                )
            )
            if external_fields_present and not self.external_identity.configured:
                errors.append("external_identity_configuration_incomplete")
            if self.settings.auth_jwks_url and not self.settings.auth_jwks_url.startswith("https://"):
                errors.append("auth_jwks_url_must_use_https")
            internal_identity_ready = bool(
                self.settings.auth_token_secret and len(self.settings.auth_token_secret) >= 32
            )
            if not self.external_identity.configured and not internal_identity_ready:
                errors.append("identity_provider_not_configured")
        return SecurityReadiness(
            ready=not errors,
            environment=self.settings.environment,
            enforcement="strict" if self.settings.security_enforced else "local-compatible",
            errors=tuple(errors),
        )

    @staticmethod
    def access_for(method: str, path: str) -> str:
        method = method.upper()
        if method in {"HEAD", "OPTIONS"}:
            return PUBLIC
        if path.startswith("/learner/"):
            if method == "GET" and (path in {"/learner/catalog", "/learner/services", "/learner/tools"}
                                    or path.endswith("/example") or path.endswith("/preview")):
                return PUBLIC
            if method == "POST" and path in {"/learner/tools/bs-pricer", "/learner/tools/black-scholes"}:
                return PUBLIC_RATE_LIMITED
            return IDENTITY
        if path.startswith("/learning/"):
            return IDENTITY
        if method == "GET":
            if path == "/interview/pilot/metrics":
                return OPERATOR
            if path.startswith("/interview/"):
                if path in {"/interview/catalog", "/interview/cases/call-quote"}:
                    return PUBLIC
                return IDENTITY
            if path == "/platform/exercises" or path.startswith("/platform/exercises/"):
                return IDENTITY
            if path.startswith("/courses/") and path.endswith("/script"):
                return MEMBER
            if path == "/products/market-finance-starter-kit/availability":
                return PUBLIC
            if path == "/billing/entitlement" or path in {
                "/products/market-finance-starter-kit/manifest",
                "/products/market-finance-starter-kit/download",
            }:
                return IDENTITY
            if path in ApiSecurity._OPERATOR_READ_EXACT or path.startswith(ApiSecurity._OPERATOR_READ_PREFIXES):
                return OPERATOR
            if path.startswith("/platform/community/") or path == "/platform/survival/leaderboard":
                return MEMBER
            if path.startswith(ApiSecurity._MEMBER_READ_PREFIXES):
                return MEMBER
            return PUBLIC
        if path == "/billing/webhook":
            return WEBHOOK
        if path.startswith("/interview/") and path != "/interview/preview/check":
            return IDENTITY
        if path.startswith("/platform/courses/") and path.endswith("/position"):
            return IDENTITY
        if path in {
            "/billing/checkout",
            "/products/market-finance-starter-kit/checkout",
        }:
            return IDENTITY
        if path in ApiSecurity._PUBLIC_MUTATIONS:
            return PUBLIC_RATE_LIMITED
        if path in ApiSecurity._MEMBER_MUTATIONS or path.startswith("/generate/"):
            return MEMBER
        if path.startswith("/strategy/"):
            return MEMBER
        if path.startswith("/platform/community/"):
            return MEMBER
        if path.startswith("/platform/jobs/") and path.endswith("/apply"):
            return MEMBER
        # Fail closed for every unclassified mutation, including future routes.
        return OPERATOR

    @staticmethod
    def required_plan_for(method: str, path: str) -> str | None:
        """Return the authoritative minimum Stripe plan for premium mutations.

        Unknown generation/strategy mutations default to the highest plan so a
        newly introduced premium endpoint cannot silently become a free route.
        """

        method = method.upper()
        if method == "GET":
            if path.startswith("/courses/") and path.endswith("/script"):
                course_id = path.removeprefix("/courses/").removesuffix("/script").strip("/")
                return {
                    "black-scholes": "starter",
                    "yield-curves": "starter",
                    "greeks": "starter",
                    "rates-swaps": "starter",
                    "fixed-income-bonds": "starter",
                    "implied-vol": "student",
                    "credit-derivatives": "student",
                    "market-risk-var": "student",
                    "exotics": "pro",
                    "monte-carlo": "pro",
                    "stochastic": "pro",
                    "structured-products": "pro",
                }.get(course_id, "pro")
            if path.startswith("/agent/desk/state"):
                return "pro"
            if path.startswith("/platform/community/"):
                return "starter"
            if path == "/platform/survival/leaderboard":
                return "student"
            return None
        if method not in {"POST", "PUT", "PATCH", "DELETE"}:
            return None
        if path.startswith("/platform/community/"):
            return "starter"
        if path in ApiSecurity._PREMIUM_MUTATIONS:
            return ApiSecurity._PREMIUM_MUTATIONS[path]
        if path.startswith("/generate/") or path.startswith("/strategy/"):
            return "pro"
        return None

    @staticmethod
    def _presented_key(request: Request) -> str | None:
        direct = request.headers.get("x-api-key")
        if direct:
            return direct.strip()
        authorization = request.headers.get("authorization", "")
        scheme, _, token = authorization.partition(" ")
        if scheme.lower() == "bearer" and token.strip():
            return token.strip()
        return None

    def _role_for_key(self, presented: str | None) -> str | None:
        if not presented:
            return None
        if self.settings.operator_api_key and hmac.compare_digest(presented, self.settings.operator_api_key):
            return OPERATOR
        if self.settings.api_key and hmac.compare_digest(presented, self.settings.api_key):
            return MEMBER
        return None

    def _verify_identity_token(self, token: str) -> AuthenticatedIdentity:
        try:
            header = json.loads(_b64url_decode(token.split(".", 1)[0]))
        except Exception as exc:
            raise HTTPException(status_code=401, detail="Invalid session token.") from exc
        if header.get("alg") == "HS256" and self.settings.auth_token_secret:
            return verify_session_token(token, self.settings.auth_token_secret)
        if self.external_identity.configured:
            return self.external_identity.verify(token)
        raise HTTPException(status_code=401, detail="Invalid session token.")

    def _client_identity(self, request: Request, *, role: str | None, presented: str | None) -> str:
        client_ip = request.client.host if request.client else "unknown"
        if self.settings.trust_proxy_headers:
            forwarded = request.headers.get("x-forwarded-for", "").split(",", 1)[0].strip()
            if forwarded:
                client_ip = forwarded
        key_fingerprint = hashlib.sha256((presented or "anonymous").encode("utf-8")).hexdigest()[:16]
        return f"{role or 'public'}:{client_ip}:{key_fingerprint}"

    def _enforce_entitlement(self, request: Request, *, role: str | None) -> None:
        required_plan = self.required_plan_for(request.method, request.url.path)
        if not required_plan or not (self.settings.security_enforced or self.settings.enforce_entitlements) or role == OPERATOR:
            return
        identity = getattr(request.state, "tpl_identity", None)
        if identity is None:
            raise HTTPException(
                status_code=403,
                detail=f"Authenticated user entitlement required (minimum plan: {required_plan}).",
            )
        if self.store is None:
            raise HTTPException(
                status_code=503,
                detail="Entitlement store is unavailable; premium route is closed.",
            )
        entitlement = self.store.get_entitlement_by_user_id(identity.user_id)
        actual_plan = str((entitlement or {}).get("plan") or "").strip().lower()
        status = str((entitlement or {}).get("status") or "").strip().lower()
        actual_rank = self._PLAN_RANK.get(actual_plan, 0)
        required_rank = self._PLAN_RANK[required_plan]
        if status != "active" or actual_rank < required_rank:
            raise HTTPException(
                status_code=403,
                detail=f"Active {required_plan} entitlement required.",
            )
        request.state.tpl_entitlement = entitlement

    def authorize(self, request: Request, access: str) -> None:
        if access in {PUBLIC, WEBHOOK}:
            request.state.tpl_security_role = PUBLIC
            return
        if self.settings.security_enforced and not self.readiness.ready:
            raise HTTPException(
                status_code=503,
                detail="Production security is not configured; protected route is unavailable.",
            )

        presented = self._presented_key(request)
        role = self._role_for_key(presented)
        if access == IDENTITY:
            identity_required = (
                self.settings.security_enforced
                or bool(self.settings.auth_token_secret)
                or self.external_identity.configured
            )
            if identity_required:
                authorization = request.headers.get("authorization", "")
                scheme, _, token = authorization.partition(" ")
                if scheme.lower() != "bearer" or not token.strip():
                    raise HTTPException(
                        status_code=401,
                        detail="Authenticated user session required.",
                        headers={"WWW-Authenticate": "Bearer"},
                    )
                identity = self._verify_identity_token(token.strip())
                request.state.tpl_identity = identity
                role = identity.role
                presented = f"identity:{identity.user_id}"
        if access in {MEMBER, OPERATOR} and role is None and presented:
            authorization = request.headers.get("authorization", "")
            scheme, _, token = authorization.partition(" ")
            if scheme.lower() == "bearer" and token.count(".") == 2:
                identity = self._verify_identity_token(token.strip())
                request.state.tpl_identity = identity
                role = identity.role
                presented = f"identity:{identity.user_id}"
        if access in {MEMBER, OPERATOR}:
            # Local defaults remain CLI/test compatible. Explicitly configuring
            # either key opts local mode into the same authentication behavior.
            auth_configured = bool(self.settings.api_key or self.settings.operator_api_key)
            if self.settings.security_enforced or auth_configured:
                if role is None:
                    raise HTTPException(
                        status_code=401,
                        detail="Invalid or missing API key.",
                        headers={"WWW-Authenticate": "ApiKey"},
                    )
                if access == OPERATOR and role != OPERATOR:
                    # Backwards compatibility: in relaxed local mode, the old
                    # single TPL_API_KEY remains sufficient for operator calls.
                    if self.settings.security_enforced or self.settings.operator_api_key:
                        raise HTTPException(status_code=403, detail="Operator role required.")

        request.state.tpl_security_role = role or access
        self._enforce_entitlement(request, role=role)

        if self._limiter is not None:
            principal = self._client_identity(request, role=role, presented=presented)
            self._limiter.consume(
                scope=access,
                principal=principal,
                limit=self.settings.rate_limit_per_min,
            )

    def summary(self) -> dict:
        return {
            **self.readiness.as_dict(),
            "member_key_configured": bool(self.settings.api_key),
            "operator_key_configured": bool(self.settings.operator_api_key),
            "auth_token_secret_configured": bool(self.settings.auth_token_secret),
            "external_identity_configured": self.external_identity.configured,
            "identity_mode": (
                "oidc_jwks"
                if self.external_identity.configured
                else "internal_hs256"
                if self.settings.auth_token_secret
                else "disabled"
            ),
            "entitlements_enforced": self.settings.security_enforced or self.settings.enforce_entitlements,
            "rate_limit_per_min": self.settings.rate_limit_per_min,
            "rate_limit_backend": "sqlite" if self._limiter else "disabled",
        }
