"""Verify that every private course script projects to a safe public view.

The authoring files intentionally retain a back-office source appendix. The
public API must expose only reviewed, readable excerpts and must not leak
retrieval identifiers, scores, corpus storage labels or PDF-ingestion labels.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# Keep the script runnable as `python scripts/audit_public_course_projection.py`,
# which is the invocation used by the release gate.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pricinglibrary_rag.api import COURSE_SCRIPT_FILES, _public_course_markdown


REPO_ROOT = Path(__file__).resolve().parents[3]
COURSE_ROOT = REPO_ROOT / "Tools" / "pricinglibrary_rag_backend" / "pricinglibrary_rag" / "course_scripts"
REFERENCE_ROW = re.compile(r"^- \*([^*\r\n]+)\* — «(.+)»$", re.MULTILINE)
FORBIDDEN_PUBLIC_PATTERNS = (
    r"^##\s+Script enseignant",
    r"^##\s+Checkpoint personas",
    r"Source Appendix \(back-office\)",
    r"Sources RAG a citer",
    r"PDFDrive",
    r"\bchunk\s+[0-9]",
    r"\bscore\s+0\.\d",
    r"\bdocument\s+[0-9a-f]{16,}",
    r"\[S(?:\d+|x)\]",
)


def main() -> int:
    failures: list[str] = []
    counts: list[str] = []
    for course_id, filename in COURSE_SCRIPT_FILES.items():
        path = COURSE_ROOT / filename
        if not path.is_file():
            failures.append(f"{course_id}: missing private script {filename}")
            continue
        public = _public_course_markdown(path.read_text(encoding="utf-8"))
        rows = REFERENCE_ROW.findall(public)
        if not 2 <= len(rows) <= 4:
            failures.append(f"{course_id}: expected 2-4 reviewed public references, got {len(rows)}")
        for index, (title, excerpt) in enumerate(rows, start=1):
            if len(excerpt.strip()) < 45:
                failures.append(f"{course_id}: reference {index} excerpt is too short")
            if not title.strip() or re.search(r"PDFDrive|\bdocument\b|\bchunk\b|\bscore\b", title, re.IGNORECASE):
                failures.append(f"{course_id}: reference {index} title is not client-safe")
        for pattern in FORBIDDEN_PUBLIC_PATTERNS:
            if re.search(pattern, public, flags=re.IGNORECASE | re.MULTILINE):
                failures.append(f"{course_id}: public projection leaks forbidden pattern {pattern}")
        counts.append(f"{course_id}={len(rows)}")

    if failures:
        print("PUBLIC COURSE PROJECTION FAIL")
        print("\n".join(f"- {failure}" for failure in failures))
        return 1
    print(
        "PUBLIC COURSE PROJECTION PASS: "
        f"{len(COURSE_SCRIPT_FILES)}/{len(COURSE_SCRIPT_FILES)} public projections are client-safe; "
        + ", ".join(counts)
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
