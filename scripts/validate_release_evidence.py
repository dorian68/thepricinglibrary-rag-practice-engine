"""Validate anonymised staging and rollback evidence without printing secrets or PII."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit


SHA256_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
ALIAS_RE = re.compile(r"^P[0-9]{2}$")
REQUEST_ID_RE = re.compile(r"^[0-9a-f]{32}$")
REFERENCE_RE = re.compile(r"^(?:backup|evidence)-[A-Za-z0-9._-]+$")
FORBIDDEN_KEY_PARTS = ("email", "phone", "payment", "secret", "token", "password", "cookie")

STAGING_CHECKS = (
    "public_ready",
    "availability_sale_ready",
    "anonymous_checkout_denied",
    "anonymous_download_denied",
    "cancellation_without_grant",
    "refund_revocation",
    "chargeback_revocation",
    "subscription_isolation",
    "frontend_no_localhost",
    "no_stale_assets",
    "metrics_scrape_verified",
    "rum_received",
    "alerts_configured",
    "proxy_request_id_correlation",
    "no_sensitive_telemetry",
)
PURCHASE_CHECKS = (
    "checkout_completed",
    "entitlement_after_refresh",
    "manifest_ready",
    "download_sha256_matches",
    "webhook_idempotent",
)
ROLLBACK_CHECKS = (
    "candidate_ready",
    "candidate_availability",
    "rollback_command_succeeded",
    "restored_ready",
    "restored_availability",
    "restored_entitled_download_sha256_matches",
    "post_rollback_data_integrity",
)


def _contains_forbidden_key(value: Any) -> bool:
    if isinstance(value, dict):
        for key, child in value.items():
            if any(part in str(key).casefold() for part in FORBIDDEN_KEY_PARTS):
                return True
            if _contains_forbidden_key(child):
                return True
    elif isinstance(value, list):
        return any(_contains_forbidden_key(item) for item in value)
    return False


def _require_true(mapping: Any, fields: tuple[str, ...], label: str, errors: list[str]) -> int:
    if not isinstance(mapping, dict):
        errors.append(f"{label} must be an object")
        return 0
    passed = 0
    for field in fields:
        value = mapping.get(field)
        if value is not True:
            errors.append(f"{label}.{field} must be true")
        else:
            passed += 1
        if value not in (True, False):
            errors.append(f"{label}.{field} must be boolean")
    return passed


def _validate_request_ids(payload: dict[str, Any], errors: list[str]) -> int:
    request_ids = payload.get("request_ids")
    if not isinstance(request_ids, list) or not request_ids:
        errors.append("request_ids must contain at least one sanitised request id")
        return 0
    valid = sum(isinstance(item, str) and REQUEST_ID_RE.fullmatch(item) is not None for item in request_ids)
    if valid != len(request_ids):
        errors.append("request_ids must contain only 32-character hexadecimal ids")
    return valid


def _validate_deployment(payload: dict[str, Any], errors: list[str]) -> None:
    deployment = payload.get("deployment")
    if not isinstance(deployment, dict):
        errors.append("deployment must be an object")
        return
    base_url = deployment.get("base_url")
    parsed = urlsplit(base_url) if isinstance(base_url, str) else None
    if parsed is None or parsed.scheme != "https" or not parsed.hostname or parsed.query or parsed.fragment:
        errors.append("deployment.base_url must be a query-free HTTPS origin")
    elif parsed.hostname.casefold() in {"localhost", "127.0.0.1", "::1"}:
        errors.append("deployment.base_url must not be local")
    digest = deployment.get("image_digest")
    if not isinstance(digest, str) or SHA256_RE.fullmatch(digest) is None:
        errors.append("deployment.image_digest must be a sha256 digest")
    version = deployment.get("release_version")
    if not isinstance(version, str) or not version.strip() or len(version) > 80:
        errors.append("deployment.release_version must be a short non-empty string")


def validate_staging(payload: Any) -> tuple[list[str], dict[str, Any]]:
    errors: list[str] = []
    if not isinstance(payload, dict):
        return ["root must be an object"], {}
    if payload.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if _contains_forbidden_key(payload):
        errors.append("PII or credential-like field names are forbidden")
    _validate_deployment(payload, errors)
    check_count = _require_true(payload.get("checks"), STAGING_CHECKS, "checks", errors)
    purchases = payload.get("purchases")
    aliases: list[str] = []
    purchase_pass_count = 0
    if not isinstance(purchases, list) or len(purchases) != 3:
        errors.append("exactly three purchase records are required")
        purchases = purchases if isinstance(purchases, list) else []
    for index, purchase in enumerate(purchases, start=1):
        label = f"purchases[{index}]"
        if not isinstance(purchase, dict):
            errors.append(f"{label} must be an object")
            continue
        alias = purchase.get("alias")
        if not isinstance(alias, str) or ALIAS_RE.fullmatch(alias) is None:
            errors.append(f"{label}.alias must use P01-style aliases")
        elif alias in aliases:
            errors.append(f"duplicate purchase alias: {alias}")
        else:
            aliases.append(alias)
        passed = _require_true(purchase, PURCHASE_CHECKS, label, errors)
        if passed == len(PURCHASE_CHECKS):
            purchase_pass_count += 1
    request_count = _validate_request_ids(payload, errors)
    if len(aliases) != len(purchases):
        errors.append("purchase aliases must be unique and present")
    summary = {
        "kind": "staging",
        "checks_passed": check_count,
        "checks_total": len(STAGING_CHECKS),
        "purchases_passed": purchase_pass_count,
        "purchases_total": len(purchases),
        "request_ids": request_count,
        "valid": not errors,
    }
    return errors, summary


def _parse_aware_timestamp(value: Any, label: str, errors: list[str]) -> datetime | None:
    if not isinstance(value, str):
        errors.append(f"{label} must be an ISO-8601 timestamp")
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        errors.append(f"{label} must be an ISO-8601 timestamp")
        return None
    if parsed.tzinfo is None:
        errors.append(f"{label} must include a timezone")
        return None
    return parsed


def _validate_release_pair(mapping: Any, label: str, errors: list[str]) -> tuple[str | None, str | None]:
    if not isinstance(mapping, dict):
        errors.append(f"{label} must be an object")
        return None, None
    digest = mapping.get("image_digest")
    version = mapping.get("release_version")
    if not isinstance(digest, str) or SHA256_RE.fullmatch(digest) is None:
        errors.append(f"{label}.image_digest must be a sha256 digest")
    if not isinstance(version, str) or not version.strip() or len(version) > 80:
        errors.append(f"{label}.release_version must be a short non-empty string")
    return digest if isinstance(digest, str) else None, version if isinstance(version, str) else None


def validate_rollback(payload: Any) -> tuple[list[str], dict[str, Any]]:
    errors: list[str] = []
    if not isinstance(payload, dict):
        return ["root must be an object"], {}
    if payload.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if _contains_forbidden_key(payload):
        errors.append("PII or credential-like field names are forbidden")
    trigger = payload.get("trigger")
    if trigger not in {"alert", "manual", "drill"}:
        errors.append("trigger must be alert, manual or drill")
    started = _parse_aware_timestamp(payload.get("started_at"), "started_at", errors)
    completed = _parse_aware_timestamp(payload.get("completed_at"), "completed_at", errors)
    if started and completed and completed <= started:
        errors.append("completed_at must be later than started_at")
    previous_digest, previous_version = _validate_release_pair(payload.get("previous"), "previous", errors)
    candidate_digest, _ = _validate_release_pair(payload.get("candidate"), "candidate", errors)
    restored_digest, restored_version = _validate_release_pair(payload.get("restored"), "restored", errors)
    if previous_digest and restored_digest and previous_digest != restored_digest:
        errors.append("restored.image_digest must equal previous.image_digest")
    if previous_version and restored_version and previous_version != restored_version:
        errors.append("restored.release_version must equal previous.release_version")
    if candidate_digest and previous_digest and candidate_digest == previous_digest:
        errors.append("candidate.image_digest must differ from previous.image_digest")
    backup = payload.get("database_backup")
    if not isinstance(backup, dict):
        errors.append("database_backup must be an object")
    else:
        _require_true(backup, ("created", "verified"), "database_backup", errors)
        reference = backup.get("reference")
        if not isinstance(reference, str) or REFERENCE_RE.fullmatch(reference) is None:
            errors.append("database_backup.reference must be an anonymised reference")
    check_count = _require_true(payload.get("checks"), ROLLBACK_CHECKS, "checks", errors)
    request_count = _validate_request_ids(payload, errors)
    summary = {
        "kind": "rollback",
        "checks_passed": check_count,
        "checks_total": len(ROLLBACK_CHECKS),
        "request_ids": request_count,
        "valid": not errors,
    }
    return errors, summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kind", choices=("staging", "rollback"), required=True)
    parser.add_argument("--input", required=True, type=Path)
    args = parser.parse_args()
    try:
        payload = json.loads(args.input.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"RELEASE EVIDENCE FAIL: cannot read JSON ({type(exc).__name__})")
        return 1
    validator = validate_staging if args.kind == "staging" else validate_rollback
    errors, summary = validator(payload)
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    if errors:
        print("RELEASE EVIDENCE FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"RELEASE EVIDENCE PASS ({args.kind})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
