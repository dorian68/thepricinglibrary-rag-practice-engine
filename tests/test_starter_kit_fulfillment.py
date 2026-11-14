from __future__ import annotations

from dataclasses import replace
import hashlib
import hmac
import json
from pathlib import Path
from types import SimpleNamespace
import time

from fastapi.testclient import TestClient

from pricinglibrary_rag.api import create_app
from pricinglibrary_rag.config import Settings
from pricinglibrary_rag.factory import build_services
from pricinglibrary_rag.security import ApiSecurity, mint_session_token


AUTH_SECRET = "identity_" + "s" * 40
WEBHOOK_SECRET = "whsec_starter_kit_test"


def _settings(tmp_path: Path, bundle: Path, manifest: Path, **overrides) -> Settings:
    base = Settings(
        data_dir=tmp_path,
        db_path=tmp_path / "starter-kit.sqlite3",
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
        api_key="member_" + "m" * 40,
        operator_api_key="operator_" + "o" * 40,
        auth_token_secret=AUTH_SECRET,
        rate_limit_per_min=100,
        source_rights_cleared=True,
        stripe_secret_key="sk_test_starter_kit",
        stripe_webhook_secret=WEBHOOK_SECRET,
        starter_kit_price_id="price_starter_kit",
        starter_kit_bundle_path=bundle,
        starter_kit_manifest_path=manifest,
    )
    return replace(base, **overrides)


def _write_artifact(tmp_path: Path) -> tuple[Path, Path, bytes]:
    payload = b"starter-kit-verified-bundle\n"
    bundle = tmp_path / "market-finance-starter-kit.zip"
    bundle.write_bytes(payload)
    manifest = tmp_path / "market-finance-starter-kit.manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "product_id": "market-finance-starter-kit",
                "version": "1.0.0-test",
                "ready": True,
                "deliverable_count": 7,
                "deliverables": [
                    {"id": f"deliverable-{index}", "title": f"Deliverable {index}", "complete": True, "files": []}
                    for index in range(1, 8)
                ],
                "missing": [],
                "bundle": {
                    "path": bundle.name,
                    "size": len(payload),
                    "sha256": hashlib.sha256(payload).hexdigest(),
                },
            }
        ),
        encoding="utf-8",
    )
    return bundle, manifest, payload


def _identity(user_id: str = "starter-kit-buyer") -> dict[str, str]:
    token = mint_session_token(
        AUTH_SECRET,
        user_id=user_id,
        email=f"{user_id}@desk.test",
        expires_at=int(time.time()) + 300,
    )
    return {"Authorization": f"Bearer {token}"}


def _signed(event: dict) -> tuple[bytes, str]:
    payload = json.dumps(event, separators=(",", ":")).encode("utf-8")
    timestamp = int(time.time())
    signature = hmac.new(
        WEBHOOK_SECRET.encode("utf-8"),
        f"{timestamp}.{payload.decode('utf-8')}".encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return payload, f"t={timestamp},v1={signature}"


class _FakeSessionApi:
    last_params: dict | None = None

    @classmethod
    def create(cls, **params):
        cls.last_params = params
        return SimpleNamespace(
            id="cs_test_starter_kit",
            url="https://checkout.stripe.test/starter-kit",
        )


def test_starter_kit_checkout_fails_closed_without_identity_or_product_config(tmp_path: Path) -> None:
    bundle, manifest, _ = _write_artifact(tmp_path)
    services = build_services(
        _settings(tmp_path, bundle, manifest, stripe_secret_key=None, starter_kit_price_id=None)
    )
    client = TestClient(create_app(services))

    path = "/products/market-finance-starter-kit/checkout"
    availability_path = "/products/market-finance-starter-kit/availability"
    assert ApiSecurity.access_for("GET", availability_path) == "public"
    availability = client.get(availability_path)
    assert availability.status_code == 200
    assert availability.json() == {
        "product_id": "market-finance-starter-kit",
        "sale_ready": False,
        "checkout_configured": False,
        "artifact_ready": True,
        "version": "1.0.0-test",
    }
    assert client.post(path).status_code == 401
    assert client.post(path, headers=_identity()).status_code == 503


def test_one_shot_purchase_download_idempotency_and_refund(tmp_path: Path) -> None:
    bundle, manifest, payload = _write_artifact(tmp_path)
    services = build_services(_settings(tmp_path, bundle, manifest))
    services.billing._stripe = SimpleNamespace(
        checkout=SimpleNamespace(Session=_FakeSessionApi)
    )
    client = TestClient(create_app(services))
    headers = _identity()
    base = "/products/market-finance-starter-kit"

    availability = client.get(f"{base}/availability")
    assert availability.status_code == 200
    assert availability.json() == {
        "product_id": "market-finance-starter-kit",
        "sale_ready": True,
        "checkout_configured": True,
        "artifact_ready": True,
        "version": "1.0.0-test",
    }

    # A signed-in free user may start checkout but cannot read the paid artifact.
    assert client.get(f"{base}/manifest", headers=headers).status_code == 403
    assert client.get(f"{base}/download", headers=headers).status_code == 403
    checkout = client.post(f"{base}/checkout", headers=headers)
    assert checkout.status_code == 200
    assert checkout.json()["mode"] == "payment"
    assert _FakeSessionApi.last_params["mode"] == "payment"
    assert _FakeSessionApi.last_params["metadata"] == {
        "product_id": "market-finance-starter-kit",
        "user_id": "starter-kit-buyer",
    }
    assert _FakeSessionApi.last_params["payment_intent_data"]["metadata"] == _FakeSessionApi.last_params["metadata"]
    assert _FakeSessionApi.last_params["success_url"] == "http://localhost:5173/#/starter-kit/success"
    assert _FakeSessionApi.last_params["cancel_url"] == "http://localhost:5173/#/starter-kit/cancel"

    # Keep an existing subscription active to prove the product lifecycle is separate.
    services.store.upsert_entitlement(
        "starter-kit-buyer@desk.test",
        "student",
        user_id="starter-kit-buyer",
        status="active",
        stripe_customer_id="cus_shared",
        stripe_subscription_id="sub_existing",
        source="test:existing-subscription",
    )
    completed = {
        "id": "evt_starter_kit_completed",
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "id": "cs_test_starter_kit",
                "mode": "payment",
                "payment_status": "paid",
                "payment_intent": "pi_starter_kit",
                "customer": "cus_shared",
                "client_reference_id": "starter-kit-buyer",
                "metadata": {
                    "product_id": "market-finance-starter-kit",
                    "user_id": "starter-kit-buyer",
                },
            }
        },
    }
    body, signature = _signed(completed)
    first = client.post("/billing/webhook", content=body, headers={"stripe-signature": signature})
    assert first.status_code == 200
    assert first.json()["kind"] == "product"
    duplicate = client.post("/billing/webhook", content=body, headers={"stripe-signature": signature})
    assert duplicate.status_code == 200
    assert duplicate.json()["duplicate"] is True
    assert len(services.store.list_product_entitlements()) == 1

    product_manifest = client.get(f"{base}/manifest", headers=headers)
    assert product_manifest.status_code == 200
    assert product_manifest.json()["ready"] is True
    assert product_manifest.json()["deliverable_count"] == 7
    assert product_manifest.json()["bundle"]["path"] == bundle.name
    download = client.get(f"{base}/download", headers=headers)
    assert download.status_code == 200
    assert download.content == payload
    assert download.headers["cache-control"] == "private, no-store"

    # An incomplete manifest closes both fulfillment and new checkout.
    invalid = json.loads(manifest.read_text(encoding="utf-8"))
    invalid["ready"] = False
    manifest.write_text(json.dumps(invalid), encoding="utf-8")
    assert client.get(f"{base}/manifest", headers=headers).status_code == 503
    assert client.get(f"{base}/download", headers=headers).status_code == 503
    assert client.post(f"{base}/checkout", headers=headers).status_code == 503
    assert client.get(f"{base}/availability").json() == {
        "product_id": "market-finance-starter-kit",
        "sale_ready": False,
        "checkout_configured": True,
        "artifact_ready": False,
        "version": None,
    }
    invalid["ready"] = True
    valid_version = invalid["version"]
    invalid["version"] = ""
    manifest.write_text(json.dumps(invalid), encoding="utf-8")
    assert client.get(f"{base}/manifest", headers=headers).status_code == 503
    invalid["version"] = valid_version
    invalid["deliverable_count"] = 6
    manifest.write_text(json.dumps(invalid), encoding="utf-8")
    assert client.get(f"{base}/manifest", headers=headers).status_code == 503
    invalid["deliverable_count"] = 7
    valid_sha = invalid["bundle"]["sha256"]
    invalid["bundle"]["sha256"] = "0" * 64
    manifest.write_text(json.dumps(invalid), encoding="utf-8")
    assert client.get(f"{base}/download", headers=headers).status_code == 503
    invalid["bundle"]["sha256"] = valid_sha
    manifest.write_text(json.dumps(invalid), encoding="utf-8")

    refunded = {
        "id": "evt_starter_kit_refund",
        "type": "charge.refunded",
        "data": {
            "object": {
                "id": "ch_starter_kit",
                "customer": "cus_shared",
                "payment_intent": "pi_starter_kit",
                "metadata": {
                    "product_id": "market-finance-starter-kit",
                    "user_id": "starter-kit-buyer",
                },
            }
        },
    }
    refund_body, refund_signature = _signed(refunded)
    refund = client.post(
        "/billing/webhook",
        content=refund_body,
        headers={"stripe-signature": refund_signature},
    )
    assert refund.status_code == 200
    assert refund.json()["status"] == "revoked_refund"
    assert client.get(f"{base}/download", headers=headers).status_code == 403
    assert services.store.get_entitlement_by_user_id("starter-kit-buyer")["status"] == "active"

    # A later paid purchase can reactivate; a chargeback revokes product only.
    reactivated = {
        **completed,
        "id": "evt_starter_kit_reactivated",
        "data": {"object": {
            **completed["data"]["object"],
            "id": "cs_test_starter_kit_2",
            "payment_intent": "pi_starter_kit_2",
        }},
    }
    reactivate_body, reactivate_signature = _signed(reactivated)
    assert client.post(
        "/billing/webhook",
        content=reactivate_body,
        headers={"stripe-signature": reactivate_signature},
    ).json()["status"] == "active"
    late_old_refund = {
        **refunded,
        "id": "evt_starter_kit_late_old_refund",
    }
    late_body, late_signature = _signed(late_old_refund)
    late = client.post(
        "/billing/webhook",
        content=late_body,
        headers={"stripe-signature": late_signature},
    )
    assert late.status_code == 200
    assert late.json()["handled"] is False
    assert client.get(f"{base}/download", headers=headers).status_code == 200
    dispute = {
        "id": "evt_starter_kit_chargeback",
        "type": "charge.dispute.created",
        "data": {"object": {
            "id": "dp_starter_kit",
            "charge": {
                "id": "ch_starter_kit_2",
                "customer": "cus_shared",
                "payment_intent": "pi_starter_kit_2",
                "metadata": {
                    "product_id": "market-finance-starter-kit",
                    "user_id": "starter-kit-buyer",
                },
            },
        }},
    }
    dispute_body, dispute_signature = _signed(dispute)
    chargeback = client.post(
        "/billing/webhook",
        content=dispute_body,
        headers={"stripe-signature": dispute_signature},
    )
    assert chargeback.status_code == 200
    assert chargeback.json()["status"] == "revoked_chargeback"
    assert client.get(f"{base}/download", headers=headers).status_code == 403
    assert services.store.get_entitlement_by_user_id("starter-kit-buyer")["status"] == "active"
