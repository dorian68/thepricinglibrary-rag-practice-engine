"""Offline HTTP smoke for production auth, RBAC and fail-closed behavior."""

from __future__ import annotations

import os
import hashlib
import hmac
import json
import shutil
import sys
import tempfile
import time
from dataclasses import replace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

TMP = Path(tempfile.mkdtemp(prefix="tpl_security_smoke_"))
MEMBER_KEY = "member_" + "m" * 40
OPERATOR_KEY = "operator_" + "o" * 40
AUTH_SECRET = "identity_" + "s" * 40
WEBHOOK_SECRET = "whsec_production_security_smoke_0123456789"
os.environ.pop("STRIPE_SECRET_KEY", None)
os.environ.pop("TPL_STRIPE_SECRET_KEY", None)
os.environ.update(
    {
        "TPL_ENVIRONMENT": "production",
        # This offline checkout fixture explicitly opts into the approved
        # rights state; production defaults fail closed until operators prove it.
        "TPL_SOURCE_RIGHTS_CLEARED": "true",
        "TPL_DATA_DIR": str(TMP),
        "TPL_DB_PATH": str(TMP / "production.sqlite3"),
        "TPL_API_KEY": MEMBER_KEY,
        "TPL_OPERATOR_API_KEY": OPERATOR_KEY,
        "TPL_AUTH_TOKEN_SECRET": AUTH_SECRET,
        "TPL_RATE_LIMIT_PER_MIN": "100",
        "STRIPE_WEBHOOK_SECRET": WEBHOOK_SECRET,
        "TPL_LLM_PROVIDER": "template",
        "GENERATION_MODE": "template",
        "TPL_EMBEDDING_BACKEND": "local-hashing",
        "TPL_EMBEDDING_DIM": "64",
    }
)

from fastapi.testclient import TestClient  # noqa: E402

from pricinglibrary_rag.api import create_app  # noqa: E402
from pricinglibrary_rag.config import Settings  # noqa: E402
from pricinglibrary_rag.factory import build_services  # noqa: E402
from pricinglibrary_rag.security import mint_session_token  # noqa: E402


failures: list[str] = []
step = 0


def check(condition: bool, request: str, output: str = "") -> None:
    global step
    step += 1
    status = "ok" if condition else "fail"
    print(f"[STEP {step}] {request}")
    print(f"  [STATUS] {status}")
    if output:
        print(f"  [OUTPUT] {output}")
    if not condition:
        failures.append(request)
        print("  [ERROR] assertion failed")


def signed(event: dict) -> tuple[bytes, str]:
    payload = json.dumps(event, separators=(",", ":"))
    timestamp = int(time.time())
    signature = hmac.new(
        WEBHOOK_SECRET.encode(),
        f"{timestamp}.{payload}".encode(),
        hashlib.sha256,
    ).hexdigest()
    return payload.encode(), f"t={timestamp},v1={signature}"


def main() -> int:
    try:
        settings = Settings.from_env()
        services = build_services(settings)
        client = TestClient(create_app(services))
        member = {"X-API-Key": MEMBER_KEY}
        operator = {"Authorization": f"Bearer {OPERATOR_KEY}"}
        token = mint_session_token(
            AUTH_SECRET,
            user_id="smoke-user-1",
            email="buyer@desk.test",
            expires_at=int(time.time()) + 300,
        )
        identity = {"Authorization": f"Bearer {token}"}

        response = client.get("/ready")
        check(response.status_code == 200, "GET /ready with valid production security", str(response.json()))
        response = client.get("/platform/blog")
        check(response.status_code == 200, "public GET /platform/blog remains reachable")
        response = client.post("/rag/search", json={"query": "DV01"})
        check(response.status_code == 401, "member mutation rejected without authentication", f"status={response.status_code}")
        response = client.post("/rag/search", json={"query": "DV01"}, headers=member)
        check(response.status_code == 403, "shared member key cannot bypass user entitlement", f"status={response.status_code}")
        response = client.post("/rag/search", json={"query": "DV01"}, headers=identity)
        check(response.status_code == 403, "authenticated free user is refused on starter route", f"status={response.status_code}")

        blog = {"slug": "security-smoke", "title": "Security smoke"}
        response = client.post("/platform/blog", json=blog, headers=member)
        check(response.status_code == 403, "operator route rejects member role", f"status={response.status_code}")
        response = client.post("/platform/blog", json=blog, headers=operator)
        check(response.status_code == 200, "operator route accepts operator role", f"status={response.status_code}")
        response = client.post("/billing/checkout", json={"plan": "starter", "email": "spoof@evil.test"})
        check(response.status_code == 401, "checkout rejects client email without identity token", f"status={response.status_code}")
        response = client.post(
            "/billing/checkout",
            json={"plan": "starter", "email": "spoof@evil.test"},
            headers=identity,
        )
        check(response.status_code == 200, "checkout accepts signed user identity", f"status={response.status_code}")
        unbound = {
            "id": "evt_unbound_identity",
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "customer_email": "spoof@evil.test",
                    "customer": "cus_unbound",
                    "subscription": "sub_unbound",
                    "metadata": {"plan": "starter"},
                }
            },
        }
        payload, signature = signed(unbound)
        result = services.billing.handle_webhook(payload, signature)
        check(
            result.get("handled") is False and "identity" in result.get("error", ""),
            "production webhook with client email but no user_id grants no rights",
            str(result),
        )
        bound = {
            "id": "evt_bound_identity",
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "customer_email": "buyer@desk.test",
                    "customer": "cus_bound",
                    "subscription": "sub_bound",
                    "metadata": {"plan": "starter", "user_id": "smoke-user-1"},
                }
            },
        }
        payload, signature = signed(bound)
        result = services.billing.handle_webhook(payload, signature)
        check(result.get("handled") is True, "production webhook grants identity-bound rights", str(result))
        response = client.get("/billing/entitlement?email=spoof@evil.test", headers=identity)
        check(
            response.status_code == 200
            and response.json().get("user_id") == "smoke-user-1"
            and response.json().get("email") == "buyer@desk.test"
            and response.json().get("active") is True,
            "entitlement derives from signed subject and ignores query email",
            str(response.json()),
        )
        response = client.post("/rag/search", json={"query": "DV01"}, headers=identity)
        check(response.status_code == 200, "starter entitlement opens starter route", f"status={response.status_code}")
        response = client.post("/agent/course", json={}, headers=identity)
        check(response.status_code == 403, "starter entitlement is refused on student route", f"status={response.status_code}")
        response = client.post("/agent/ag-ui/run", json={}, headers=identity)
        check(response.status_code == 403, "starter entitlement is refused on pro AG-UI route", f"status={response.status_code}")
        response = client.get("/agent/desk/state", headers=identity)
        check(response.status_code == 403, "starter entitlement is refused on pro desk state", f"status={response.status_code}")
        response = client.post(
            "/platform/survival",
            json={"username": "smoke", "score": 1, "streak": 0},
            headers=identity,
        )
        check(response.status_code == 403, "starter entitlement is refused on Student survival", f"status={response.status_code}")
        services.store.upsert_entitlement(
            "buyer@desk.test", "student", user_id="smoke-user-1", status="active", source="smoke:upgrade"
        )
        response = client.post("/agent/course", json={}, headers=identity)
        check(response.status_code == 422, "student entitlement passes gate on student route", f"status={response.status_code}")
        response = client.post(
            "/platform/survival",
            json={"username": "smoke", "score": 1, "streak": 0},
            headers=identity,
        )
        check(response.status_code == 200, "student entitlement opens Student survival", f"status={response.status_code}")
        response = client.post("/agent/desk/run", json={}, headers=identity)
        check(response.status_code == 403, "student entitlement is refused on pro desk route", f"status={response.status_code}")
        response = client.get("/agent/desk/state", headers=identity)
        check(response.status_code == 403, "student entitlement is refused on pro desk state", f"status={response.status_code}")
        services.store.upsert_entitlement(
            "buyer@desk.test", "pro", user_id="smoke-user-1", status="active", source="smoke:upgrade"
        )
        response = client.post("/agent/desk/run", json={}, headers=identity)
        check(response.status_code == 422, "pro entitlement passes gate on pro desk route", f"status={response.status_code}")
        response = client.get("/agent/desk/state", headers=identity)
        check(response.status_code == 200, "pro entitlement opens pro desk state", f"status={response.status_code}")
        response = client.post(
            "/agent/ag-ui/run",
            json={
                "threadId": "entitlement-smoke",
                "runId": "entitlement-smoke-run",
                "messages": [{"id": "m1", "role": "user", "content": "Explique le delta"}],
                "state": {"lang": "fr"},
            },
            headers=identity,
        )
        check(response.status_code == 200, "pro entitlement opens pro AG-UI route", f"status={response.status_code}")

        broken = replace(
            settings,
            data_dir=TMP / "broken",
            db_path=TMP / "broken" / "broken.sqlite3",
            api_key=None,
            operator_api_key=None,
            auth_token_secret=None,
            rate_limit_per_min=0,
        )
        broken_client = TestClient(create_app(build_services(broken)))
        response = broken_client.post("/platform/blog", json=blog)
        check(response.status_code == 503, "misconfigured production mutation fails closed", f"status={response.status_code}")
        response = broken_client.get("/ready")
        check(response.status_code == 503, "misconfigured production readiness fails", str(response.json()))
    finally:
        shutil.rmtree(TMP, ignore_errors=True)

    print("SMOKE: PASS" if not failures else "SMOKE: FAIL")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
