"""Validate anonymised, real-user pilot evidence without printing PII."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REQUIRED_BOOLEAN_FIELDS = (
    "checkout_success",
    "download_sha256_matches",
    "opened_workbook",
    "recalculated_workbook",
    "golden_case_verified",
    "completed_core_journey",
    "blocking_issue",
)
ALLOWED_REFUND_INTENTS = {"unknown", "no", "maybe", "yes"}
FORBIDDEN_KEY_PARTS = ("email", "phone", "payment", "secret", "token", "password")


def _contains_forbidden_key(value: Any) -> bool:
    if isinstance(value, dict):
        for key, child in value.items():
            lowered = str(key).casefold()
            if any(part in lowered for part in FORBIDDEN_KEY_PARTS):
                return True
            if _contains_forbidden_key(child):
                return True
    elif isinstance(value, list):
        return any(_contains_forbidden_key(item) for item in value)
    return False


def validate(payload: Any) -> tuple[list[str], dict[str, Any]]:
    errors: list[str] = []
    if not isinstance(payload, dict):
        return ["root must be an object"], {}
    if payload.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if _contains_forbidden_key(payload):
        errors.append("PII or credential-like field names are forbidden")
    participants = payload.get("participants")
    if not isinstance(participants, list):
        return errors + ["participants must be a list"], {}

    aliases: list[str] = []
    completed = 0
    satisfied = 0
    hash_matches = 0
    blocking = 0
    for index, participant in enumerate(participants, start=1):
        label = f"participant[{index}]"
        if not isinstance(participant, dict):
            errors.append(f"{label} must be an object")
            continue
        alias = participant.get("alias")
        if not isinstance(alias, str) or not alias or len(alias) > 12:
            errors.append(f"{label}.alias must be a short non-empty string")
        elif alias in aliases:
            errors.append(f"duplicate participant alias: {alias}")
        else:
            aliases.append(alias)
        for field in REQUIRED_BOOLEAN_FIELDS:
            if not isinstance(participant.get(field), bool):
                errors.append(f"{label}.{field} must be boolean")
        satisfaction = participant.get("satisfaction")
        if not isinstance(satisfaction, int) or isinstance(satisfaction, bool) or not 1 <= satisfaction <= 5:
            errors.append(f"{label}.satisfaction must be an integer from 1 to 5")
        refund_intent = participant.get("refund_intent")
        if refund_intent not in ALLOWED_REFUND_INTENTS:
            errors.append(f"{label}.refund_intent is invalid")
        if participant.get("completed_core_journey") is True:
            completed += 1
        if isinstance(satisfaction, int) and satisfaction >= 4:
            satisfied += 1
        if participant.get("download_sha256_matches") is True:
            hash_matches += 1
        if participant.get("blocking_issue") is True:
            blocking += 1

    if len(participants) < 5:
        errors.append("at least five real participants are required")
    if len(participants) != len(aliases):
        errors.append("every participant must have a unique alias")
    if hash_matches != len(participants):
        errors.append("every recorded download must match the published SHA-256")
    if completed < 4:
        errors.append("at least four participants must complete the core journey")
    if satisfied < 4:
        errors.append("at least four participants must rate value at least 4/5")
    if blocking:
        errors.append("blocking issues must be resolved before pilot PASS")

    summary = {
        "participant_count": len(participants),
        "download_hash_matches": hash_matches,
        "core_journey_completed": completed,
        "satisfaction_at_least_4": satisfied,
        "blocking_issues": blocking,
        "valid": not errors,
    }
    return errors, summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    args = parser.parse_args()
    try:
        payload = json.loads(args.input.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"PILOT EVIDENCE FAIL: cannot read JSON ({type(exc).__name__})")
        return 1
    errors, summary = validate(payload)
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    if errors:
        print("PILOT EVIDENCE FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print("PILOT EVIDENCE PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
