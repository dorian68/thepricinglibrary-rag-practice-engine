"""Offline API smoke for secure one-shot Starter Kit fulfillment."""

from __future__ import annotations

import hashlib
import hmac
import gc
import json
from pathlib import Path
import sys
import tempfile
import time
from types import SimpleNamespace

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from fastapi.testclient import TestClient

from pricinglibrary_rag.api import create_app
from pricinglibrary_rag.config import Settings
from pricinglibrary_rag.factory import build_services
from pricinglibrary_rag.security import mint_session_token


PRODUCT_ID = "market-finance-starter-kit"
AUTH_SECRET = "smoke_identity_" + "s" * 40
WEBHOOK_SECRET = "whsec_starter_kit_smoke"


def report(step: int, what: str, ok: bool, *, request: str, input_: str, output: str) -> None:
    status = "ok" if ok else "fail"
    error = "none" if ok else output
    next_ = "continue" if ok else "stop and inspect this fulfillment stage"
    print(
        f"[STEP {step}] {what} · [STATUS] {status} · [REQUEST] {request} · "
        f"[INPUT] {input_} · [OUTPUT] {output} · [ERROR] {error} · [NEXT] {next_}"
    )
    if not ok:
        raise AssertionError(f"step {step} failed: {output}")


def signed(event: dict) -> tuple[bytes, str]:
    payload = json.dumps(event, separators=(",", ":")).encode("utf-8")
    timestamp = int(time.time())
    signature = hmac.new(
        WEBHOOK_SECRET.encode("utf-8"),
        f"{timestamp}.{payload.decode('utf-8')}".encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return payload, f"t={timestamp},v1={signature}"


class FakeSessionApi:
    last_params: dict | None = None

    @classmethod
    def create(cls, **params):
        cls.last_params = params
        return SimpleNamespace(id="cs_smoke_kit", url="https://checkout.stripe.test/starter-kit")


def settings(root: Path, bundle: Path, manifest: Path) -> Settings:
    return Settings(
        data_dir=root,
        db_path=root / "starter-kit-smoke.sqlite3",
        embedding_backend="local-hashing",
        embedding_dim=64,
        sentence_transformer_model=None,
        llm_provider="template",
        openai_api_key=None,
        openai_model="gpt-4o-mini",
        openai_base_url=None,
        openai_timeout_seconds=10,
        openai_max_retries=0,
        ollama_url="http://localhost:11434",
        ollama_model="dummy",
        transformers_model_path=None,
        chunk_target_chars=700,
        chunk_overlap_chars=80,
        max_context_chunks=4,
        environment="production",
        # Local fulfillment fixture: commercial rights are an explicit input,
        # never an implicit default in production Settings.
        source_rights_cleared=True,
        api_key="member_" + "m" * 40,
        operator_api_key="operator_" + "o" * 40,
        auth_token_secret=AUTH_SECRET,
        rate_limit_per_min=100,
        stripe_secret_key="sk_test_redacted",
        stripe_webhook_secret=WEBHOOK_SECRET,
        starter_kit_price_id="price_starter_kit_smoke",
        starter_kit_bundle_path=bundle,
        starter_kit_manifest_path=manifest,
    )


def run() -> None:
    with tempfile.TemporaryDirectory(prefix="tpl-starter-kit-smoke-") as tmp:
        root = Path(tmp)
        bundle_bytes = b"verified starter kit smoke bundle\n"
        bundle = root / "market-finance-starter-kit.zip"
        bundle.write_bytes(bundle_bytes)
        manifest_path = root / "manifest.json"
        manifest = {
            "schema_version": 1,
            "product_id": PRODUCT_ID,
            "version": "smoke-1",
            "ready": True,
            "deliverable_count": 7,
            "deliverables": [
                {"id": f"deliverable-{index}", "title": f"Deliverable {index}", "complete": True, "files": []}
                for index in range(1, 8)
            ],
            "missing": [],
            "bundle": {
                "path": bundle.name,
                "size": len(bundle_bytes),
                "sha256": hashlib.sha256(bundle_bytes).hexdigest(),
            },
        }
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        services = build_services(settings(root, bundle, manifest_path))
        services.billing._stripe = SimpleNamespace(
            checkout=SimpleNamespace(Session=FakeSessionApi)
        )
        client = TestClient(create_app(services))
        token = mint_session_token(
            AUTH_SECRET,
            user_id="starter-kit-smoke-user",
            email="starter-kit-smoke@desk.test",
            expires_at=int(time.time()) + 300,
        )
        headers = {"Authorization": f"Bearer {token}"}
        base = "/products/market-finance-starter-kit"

        availability = client.get(f"{base}/availability")
        expected_availability = {
            "product_id": PRODUCT_ID,
            "sale_ready": True,
            "checkout_configured": True,
            "artifact_ready": True,
            "version": "smoke-1",
        }
        report(1, "public product availability", availability.status_code == 200 and availability.json() == expected_availability, request="GET availability", input_="anonymous; no secrets", output=f"status={availability.status_code}; body={availability.json()}")

        denied = client.get(f"{base}/download", headers=headers)
        report(2, "free user denied", denied.status_code == 403, request="GET download", input_="signed JWT; no product entitlement", output=f"status={denied.status_code}")

        checkout = client.post(f"{base}/checkout", headers=headers)
        params = FakeSessionApi.last_params or {}
        checkout_ok = (
            checkout.status_code == 200
            and checkout.json().get("mode") == "payment"
            and params.get("mode") == "payment"
            and params.get("metadata") == {"product_id": PRODUCT_ID, "user_id": "starter-kit-smoke-user"}
            and params.get("success_url") == "http://localhost:5173/#/starter-kit/success"
            and params.get("cancel_url") == "http://localhost:5173/#/starter-kit/cancel"
        )
        report(3, "one-shot checkout", checkout_ok, request="POST checkout", input_="signed JWT; server-side product and return URLs", output=f"status={checkout.status_code}; mode={params.get('mode')}; server_urls={checkout_ok}")

        services.store.upsert_entitlement(
            "starter-kit-smoke@desk.test", "student", user_id="starter-kit-smoke-user",
            stripe_customer_id="cus_shared_smoke", stripe_subscription_id="sub_existing_smoke",
            source="smoke:subscription",
        )
        completed = {
            "id": "evt_smoke_kit_complete",
            "type": "checkout.session.completed",
            "data": {"object": {
                "id": "cs_smoke_kit", "mode": "payment", "payment_status": "paid",
                "payment_intent": "pi_smoke_kit", "customer": "cus_shared_smoke",
                "client_reference_id": "starter-kit-smoke-user",
                "metadata": {"product_id": PRODUCT_ID, "user_id": "starter-kit-smoke-user"},
            }},
        }
        payload, signature = signed(completed)
        purchased = client.post("/billing/webhook", content=payload, headers={"stripe-signature": signature})
        report(4, "signed purchase webhook", purchased.status_code == 200 and purchased.json().get("status") == "active", request="POST billing webhook", input_="signed checkout.session.completed; payment_status=paid", output=f"status={purchased.status_code}; result={purchased.json()}")

        duplicate = client.post("/billing/webhook", content=payload, headers={"stripe-signature": signature})
        report(5, "webhook idempotency", duplicate.status_code == 200 and duplicate.json().get("duplicate") is True and len(services.store.list_product_entitlements()) == 1, request="POST same billing webhook", input_="same Stripe event id", output=f"status={duplicate.status_code}; product_rows={len(services.store.list_product_entitlements())}")

        product_manifest = client.get(f"{base}/manifest", headers=headers)
        download = client.get(f"{base}/download", headers=headers)
        fulfilled = product_manifest.status_code == 200 and download.status_code == 200 and download.content == bundle_bytes
        report(6, "manifest and bundle fulfillment", fulfilled, request="GET manifest + GET download", input_="signed JWT; active product entitlement", output=f"manifest={product_manifest.status_code}; download={download.status_code}; bytes={len(download.content)}")

        manifest["ready"] = False
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        incomplete = client.get(f"{base}/download", headers=headers)
        unavailable = client.get(f"{base}/availability")
        availability_closed = unavailable.status_code == 200 and unavailable.json() == {
            "product_id": PRODUCT_ID,
            "sale_ready": False,
            "checkout_configured": True,
            "artifact_ready": False,
            "version": None,
        }
        report(7, "incomplete manifest fails closed", incomplete.status_code == 503 and availability_closed, request="GET download + GET availability", input_="manifest ready=false", output=f"download={incomplete.status_code}; availability={unavailable.json()}")
        manifest["ready"] = True
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

        refunded = {
            "id": "evt_smoke_kit_refund",
            "type": "charge.refunded",
            "data": {"object": {
                "id": "ch_smoke_kit", "customer": "cus_shared_smoke",
                "payment_intent": "pi_smoke_kit",
                "metadata": {"product_id": PRODUCT_ID, "user_id": "starter-kit-smoke-user"},
            }},
        }
        refund_payload, refund_signature = signed(refunded)
        refund = client.post("/billing/webhook", content=refund_payload, headers={"stripe-signature": refund_signature})
        after_refund = client.get(f"{base}/download", headers=headers)
        subscription = services.store.get_entitlement_by_user_id("starter-kit-smoke-user")
        revoked_only_product = refund.status_code == 200 and after_refund.status_code == 403 and subscription and subscription["status"] == "active"
        report(8, "refund revokes product only", bool(revoked_only_product), request="POST refund webhook + GET download", input_="signed charge.refunded for product payment intent", output=f"refund={refund.json()}; download={after_refund.status_code}; subscription_status={(subscription or {}).get('status')}")
        client.close()
        del client, services
        gc.collect()

    print("[VERDICT] PASS · one-shot starter kit availability and fulfillment are CLI/API reproducible and fail-closed")


if __name__ == "__main__":
    run()
