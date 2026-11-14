"""Render the exact client-facing projection used by the course API."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from pricinglibrary_rag.api import _public_course_markdown


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("course", type=Path, help="Private Markdown course script")
    args = parser.parse_args()
    course = args.course.resolve()
    if course.suffix.lower() != ".md" or not course.is_file():
        parser.error("course must be an existing Markdown file")
    sys.stdout.write(_public_course_markdown(course.read_text(encoding="utf-8")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
