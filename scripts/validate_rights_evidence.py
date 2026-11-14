"""Validate operator-provided source-rights evidence.

This validator never asserts that rights exist on its own. It only checks a
later, human/legal-reviewed evidence file against the exact source titles
currently projected to learners. The evidence file is intentionally absent
until an operator has completed the real review.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pricinglibrary_rag.api import COURSE_SCRIPT_FILES, _public_course_markdown


REPO_ROOT = Path(__file__).resolve().parents[3]
COURSE_ROOT = REPO_ROOT / "Tools" / "pricinglibrary_rag_backend" / "pricinglibrary_rag" / "course_scripts"
REFERENCE_ROW = re.compile(r"^- \*([^*\r\n]+)\* — «(.+)»$", re.MULTILINE)
ALLOWED_BASES = {"licensed", "public_domain", "permission", "original"}
FORBIDDEN_KEY_PARTS = ("email", "phone", "payment", "secret", "token", "password")


def _contains_forbidden_key(value: Any) -> bool:
    if isinstance(value, dict):
        return any(
            any(part in str(key).casefold() for part in FORBIDDEN_KEY_PARTS)
            or _contains_forbidden_key(child)
            for key, child in value.items()
        )
    if isinstance(value, list):
        return any(_contains_forbidden_key(item) for item in value)
    return False


def public_source_titles() -> set[str]:
    titles: set[str] = set()
    for filename in COURSE_SCRIPT_FILES.values():
        public = _public_course_markdown((COURSE_ROOT / filename).read_text(encoding="utf-8"))
        titles.update(title.strip() for title, _ in REFERENCE_ROW.findall(public))
    return titles


def validate(payload: Any) -> tuple[list[str], dict[str, Any]]:
    errors: list[str] = []
    if not isinstance(payload, dict):
        return ["root must be an object"], {}
    if payload.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if payload.get("status") != "PASS":
        errors.append("status must be PASS after real legal/content review")
    reviewer_role = payload.get("reviewer_role")
    if not isinstance(reviewer_role, str) or len(reviewer_role.strip()) < 3:
        errors.append("reviewer_role must identify the reviewing role")
    reviewed_at = payload.get("reviewed_at")
    if not isinstance(reviewed_at, str):
        errors.append("reviewed_at must be an ISO date/time")
    else:
        try:
            datetime.fromisoformat(reviewed_at.replace("Z", "+00:00"))
        except ValueError:
            errors.append("reviewed_at must be an ISO date/time")
    if _contains_forbidden_key(payload):
        errors.append("PII or credential-like field names are forbidden")

    expected = public_source_titles()
    sources = payload.get("sources")
    if not isinstance(sources, list) or not sources:
        return errors + ["sources must be a non-empty list"], {"expected_source_count": len(expected), "valid": False}

    seen: set[str] = set()
    for index, source in enumerate(sources, start=1):
        label = f"sources[{index}]"
        if not isinstance(source, dict):
            errors.append(f"{label} must be an object")
            continue
        title = source.get("title")
        if not isinstance(title, str) or not title.strip():
            errors.append(f"{label}.title must be non-empty")
            continue
        title = title.strip()
        if title in seen:
            errors.append(f"duplicate source title: {title}")
        seen.add(title)
        if title not in expected:
            errors.append(f"{label}.title is not currently exposed by a course: {title}")
        if source.get("basis") not in ALLOWED_BASES:
            errors.append(f"{label}.basis must be one of {sorted(ALLOWED_BASES)}")
        for field in ("evidence_ref", "attribution"):
            if not isinstance(source.get(field), str) or not source[field].strip():
                errors.append(f"{label}.{field} must be a non-empty review record")
        course_ids = source.get("course_ids")
        if not isinstance(course_ids, list) or not course_ids or not all(isinstance(item, str) for item in course_ids):
            errors.append(f"{label}.course_ids must be a non-empty list of course ids")

    missing = sorted(expected - seen)
    if missing:
        errors.append(f"missing rights record for {len(missing)} exposed source title(s)")
    summary = {
        "expected_source_count": len(expected),
        "recorded_source_count": len(seen),
        "missing_source_count": len(missing),
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
        print(f"RIGHTS EVIDENCE MISSING/FAIL: cannot read JSON ({type(exc).__name__})")
        return 1
    errors, summary = validate(payload)
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    if errors:
        print("RIGHTS EVIDENCE FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print("RIGHTS EVIDENCE PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
