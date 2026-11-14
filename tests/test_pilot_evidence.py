from __future__ import annotations

import importlib.util
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "validate_pilot_evidence.py"
SPEC = importlib.util.spec_from_file_location("validate_pilot_evidence", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def _participant(alias: str, *, satisfied: int = 5) -> dict[str, object]:
    return {
        "alias": alias,
        "persona": "quant-junior",
        "device": "desktop",
        "checkout_success": True,
        "download_sha256_matches": True,
        "opened_workbook": True,
        "recalculated_workbook": True,
        "golden_case_verified": True,
        "completed_core_journey": True,
        "satisfaction": satisfied,
        "blocking_issue": False,
        "refund_intent": "no",
    }


def test_completed_five_user_pilot_passes() -> None:
    errors, summary = MODULE.validate(
        {"schema_version": 1, "pilot_id": "pilot-1", "participants": [_participant(f"P{i}") for i in range(1, 6)]}
    )
    assert errors == []
    assert summary["valid"] is True


def test_incomplete_pilot_fails_closed() -> None:
    errors, summary = MODULE.validate(
        {"schema_version": 1, "pilot_id": "pilot-1", "participants": [_participant("P01", satisfied=3)]}
    )
    assert summary["valid"] is False
    assert any("five" in error for error in errors)
    assert any("rate value" in error for error in errors)


def test_pii_like_fields_are_rejected() -> None:
    payload = {"schema_version": 1, "participants": [_participant(f"P{i}") for i in range(1, 6)]}
    payload["participants"][0]["email"] = "buyer@example.invalid"
    errors, _ = MODULE.validate(payload)
    assert any("PII" in error for error in errors)
