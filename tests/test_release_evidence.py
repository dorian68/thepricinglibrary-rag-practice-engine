from __future__ import annotations

import importlib.util
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "validate_release_evidence.py"
SPEC = importlib.util.spec_from_file_location("validate_release_evidence", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

OLD_DIGEST = "sha256:" + "1" * 64
NEW_DIGEST = "sha256:" + "2" * 64
REQUEST_ID = "a" * 32


def _staging_payload() -> dict[str, object]:
    checks = {field: True for field in MODULE.STAGING_CHECKS}
    purchases = [
        {"alias": f"P{index:02d}", **{field: True for field in MODULE.PURCHASE_CHECKS}}
        for index in range(1, 4)
    ]
    return {
        "schema_version": 1,
        "deployment": {
            "base_url": "https://staging.tpl.example",
            "release_version": "starter-kit-v1.0.0",
            "image_digest": OLD_DIGEST,
        },
        "checks": checks,
        "purchases": purchases,
        "request_ids": [REQUEST_ID],
    }


def _rollback_payload() -> dict[str, object]:
    return {
        "schema_version": 1,
        "trigger": "drill",
        "started_at": "2026-07-25T00:00:00+00:00",
        "completed_at": "2026-07-25T00:10:00+00:00",
        "previous": {"release_version": "release-old", "image_digest": OLD_DIGEST},
        "candidate": {"release_version": "release-new", "image_digest": NEW_DIGEST},
        "restored": {"release_version": "release-old", "image_digest": OLD_DIGEST},
        "database_backup": {"created": True, "verified": True, "reference": "backup-20260725"},
        "checks": {field: True for field in MODULE.ROLLBACK_CHECKS},
        "request_ids": [REQUEST_ID],
    }


def test_complete_staging_evidence_passes() -> None:
    errors, summary = MODULE.validate_staging(_staging_payload())
    assert errors == []
    assert summary["valid"] is True
    assert summary["purchases_passed"] == 3


def test_staging_evidence_requires_three_successful_purchases() -> None:
    payload = _staging_payload()
    payload["purchases"] = payload["purchases"][:2]
    errors, summary = MODULE.validate_staging(payload)
    assert summary["valid"] is False
    assert any("exactly three" in error for error in errors)


def test_staging_evidence_rejects_local_origin_and_pii_keys() -> None:
    payload = _staging_payload()
    payload["deployment"]["base_url"] = "http://localhost:8000"
    payload["purchases"][0]["email"] = "buyer@example.invalid"
    errors, _ = MODULE.validate_staging(payload)
    assert any("HTTPS" in error for error in errors)
    assert any("PII" in error for error in errors)


def test_complete_rollback_evidence_passes() -> None:
    errors, summary = MODULE.validate_rollback(_rollback_payload())
    assert errors == []
    assert summary["valid"] is True
    assert summary["checks_passed"] == len(MODULE.ROLLBACK_CHECKS)


def test_rollback_requires_restoring_previous_digest() -> None:
    payload = _rollback_payload()
    payload["restored"]["image_digest"] = NEW_DIGEST
    errors, summary = MODULE.validate_rollback(payload)
    assert summary["valid"] is False
    assert any("restored.image_digest" in error for error in errors)

