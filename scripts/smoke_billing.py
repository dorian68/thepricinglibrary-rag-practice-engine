"""Stripe billing smoke — full state machine, fully offline, no real money.

Validates the payment backend WITHOUT calling Stripe or charging anything:
- checkout session creation in mock mode (no secret key);
- webhook signature verification using a locally-signed payload (the exact
  Stripe HMAC scheme) with a test webhook secret;
- entitlement activation in SQLite on checkout.session.completed;
- entitlement identity bound to a stable authenticated user_id;
- cancellation, refund and chargeback revoke paid rights;
- idempotency (a replayed event does not double-process);
- error paths (unknown plan, bad signature).

Run live (test mode) instead by exporting STRIPE_SECRET_KEY / STRIPE_PRICE_* —
this script stays offline by design so it can gate CI.

Usage:
    python scripts/smoke_billing.py
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import sys
import tempfile
import time
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

_TMP = Path(tempfile.mkdtemp(prefix="tpl_smoke_billing_"))
os.environ["TPL_DATA_DIR"] = str(_TMP)
os.environ["TPL_DB_PATH"] = str(_TMP / "billing.sqlite3")
os.environ["TPL_LLM_PROVIDER"] = "template"
os.environ["TPL_EMBEDDING_BACKEND"] = "local-hashing"
os.environ["TPL_ENVIRONMENT"] = "test"
os.environ["TPL_AUTH_TOKEN_SECRET"] = ""
# Mock checkout (no secret key) but a real webhook secret so signature
# verification is exercised end to end.
os.environ.pop("STRIPE_SECRET_KEY", None)
os.environ.pop("TPL_STRIPE_SECRET_KEY", None)
_WEBHOOK_SECRET = "whsec_smoke_testsecret_0123456789"
os.environ["STRIPE_WEBHOOK_SECRET"] = _WEBHOOK_SECRET

from pricinglibrary_rag.billing import BillingError  # noqa: E402
from pricinglibrary_rag.factory import build_services  # noqa: E402

_failures: list[str] = []
_step = 0


def log(status: str, what: str, output: str = "") -> None:
    global _step
    _step += 1
    print(f"[STEP {_step}] {what}")
    print(f"  [STATUS] {status}" + (f"  [OUTPUT] {output}" if output else ""))


def check(cond: bool, label: str, output: str = "") -> bool:
    if cond:
        log("ok", label, output)
    else:
        _failures.append(label)
        log("fail", label, output)
    return cond


def _signed(event: dict, secret: str) -> tuple[bytes, str]:
    payload = json.dumps(event, separators=(",", ":"))
    ts = int(time.time())
    mac = hmac.new(secret.encode(), f"{ts}.{payload}".encode(), hashlib.sha256).hexdigest()
    return payload.encode(), f"t={ts},v1={mac}"


def _completed_event(event_id: str, email: str, plan: str, user_id: str) -> dict:
    return {
        "id": event_id,
        "object": "event",
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "id": "cs_test_123",
                "customer_email": email,
                "customer": "cus_test_123",
                "subscription": "sub_test_123",
                "metadata": {"plan": plan, "user_id": user_id, "email": email},
            }
        },
    }


def main() -> int:
    print("=" * 60)
    print("  SMOKE TEST - Stripe billing (offline, no charge)")
    print("=" * 60)

    services = build_services()
    billing = services.billing
    email = "buyer@desk.com"
    user_id = "user_billing_smoke_1"

    # 1) config summary -> mock mode (no secret key)
    cfg = billing.config_summary()
    check(cfg["mode"] == "mock" and cfg["configured"] is False,
          "config: offline mock mode (Stripe not configured)", str(cfg))
    check(cfg["webhook_secret_present"] is True, "config: webhook secret present")

    # 2) checkout session (mock) -> shape
    session = billing.create_checkout_session("starter", email=email, user_id=user_id)
    check(session.mode == "mock", "checkout: mock session (no real charge)", session.id)
    check(bool(session.id) and bool(session.url), "checkout: has id + url")

    # 3) unknown plan -> BillingError
    try:
        billing.create_checkout_session("enterprise")
        check(False, "checkout: unknown plan rejected")
    except BillingError:
        check(True, "checkout: unknown plan rejected")

    # 4) entitlement starts inactive
    check(billing.entitlement(email)["active"] is False, "entitlement: inactive before payment")

    # 5) signed webhook -> entitlement granted
    evt = _completed_event("evt_smoke_1", email, "starter", user_id)
    payload, header = _signed(evt, _WEBHOOK_SECRET)
    res = billing.handle_webhook(payload, header)
    check(res.get("handled") is True and res.get("plan") == "starter",
          "webhook: checkout.completed -> entitlement granted", str(res))
    ent = billing.entitlement(user_id=user_id)
    check(ent["active"] is True and ent["plan"] == "starter",
          "entitlement: active 'starter' after webhook", str(ent))
    check(ent.get("user_id") == user_id, "entitlement: bound to authenticated user_id", str(ent))

    # 6) idempotency -> replay not double-processed
    res2 = billing.handle_webhook(payload, header)
    check(res2.get("duplicate") is True and res2.get("handled") is False,
          "webhook: replay is idempotent (de-duplicated)", str(res2))

    # 7) tampered signature -> rejected
    try:
        billing.handle_webhook(payload, header.replace("v1=", "v1=deadbeef"))
        check(False, "webhook: bad signature rejected")
    except BillingError:
        check(True, "webhook: bad signature rejected")

    # 8) subscription cancellation revokes rights
    canceled = {
        "id": "evt_smoke_cancel",
        "type": "customer.subscription.deleted",
        "data": {"object": {"id": "sub_test_123", "customer": "cus_test_123", "metadata": {"user_id": user_id}}},
    }
    payload_cancel, header_cancel = _signed(canceled, _WEBHOOK_SECRET)
    res_cancel = billing.handle_webhook(payload_cancel, header_cancel)
    check(res_cancel.get("status") == "canceled", "webhook: cancellation revokes entitlement", str(res_cancel))
    check(billing.entitlement(user_id=user_id)["active"] is False, "entitlement: inactive after cancellation")

    # 9) reactivation then refund revokes rights
    payload_reactivate, header_reactivate = _signed(
        _completed_event("evt_smoke_2", email, "starter", user_id), _WEBHOOK_SECRET
    )
    billing.handle_webhook(payload_reactivate, header_reactivate)
    refunded = {
        "id": "evt_smoke_refund",
        "type": "charge.refunded",
        "data": {"object": {"id": "ch_test_1", "customer": "cus_test_123", "metadata": {}}},
    }
    payload_refund, header_refund = _signed(refunded, _WEBHOOK_SECRET)
    res_refund = billing.handle_webhook(payload_refund, header_refund)
    check(res_refund.get("status") == "revoked_refund", "webhook: refund revokes entitlement", str(res_refund))
    check(billing.entitlement(user_id=user_id)["active"] is False, "entitlement: inactive after refund")

    # 10) reactivation then chargeback revokes rights
    payload_reactivate2, header_reactivate2 = _signed(
        _completed_event("evt_smoke_3", email, "starter", user_id), _WEBHOOK_SECRET
    )
    billing.handle_webhook(payload_reactivate2, header_reactivate2)
    disputed = {
        "id": "evt_smoke_dispute",
        "type": "charge.dispute.created",
        "data": {
            "object": {
                "id": "dp_test_1",
                "charge": {"id": "ch_test_1", "customer": "cus_test_123", "metadata": {}},
                "metadata": {},
            }
        },
    }
    payload_dispute, header_dispute = _signed(disputed, _WEBHOOK_SECRET)
    res_dispute = billing.handle_webhook(payload_dispute, header_dispute)
    check(res_dispute.get("status") == "revoked_chargeback", "webhook: chargeback revokes entitlement", str(res_dispute))
    check(billing.entitlement(user_id=user_id)["active"] is False, "entitlement: inactive after chargeback")

    # 11) only one entitlement row persisted across state transitions
    rows = services.store.list_entitlements()
    check(len(rows) == 1, "storage: exactly one entitlement row persisted", f"{len(rows)} rows")

    import shutil
    shutil.rmtree(_TMP, ignore_errors=True)

    print("=" * 60)
    if _failures:
        print("SMOKE: FAIL")
        for f in _failures:
            print(f"  - {f}")
        return 1
    print("SMOKE: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
