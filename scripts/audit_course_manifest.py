"""Verify that the active frontend manifest matches every private course script.

The browser owns presentation, but the backend course files own the actual
curriculum. This gate prevents a catalogue/sidebar denominator from drifting
away from the script that a learner can really open.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = BACKEND_ROOT.parents[1]
MANIFEST = REPO_ROOT / "WEBSITE" / "thepricinglab" / "src" / "claude" / "courseManifest.js"
COURSE_DIR = BACKEND_ROOT / "pricinglibrary_rag" / "course_scripts"


def main() -> int:
    text = MANIFEST.read_text(encoding="utf-8")
    entries = re.findall(
        r"id:\s*'([^']+)',\s*scriptSlug:\s*'([^']+)'[\s\S]*?modules:\s*(\d+),",
        text,
    )
    errors: list[str] = []
    if len(entries) != 12:
        errors.append(f"manifest entry count is {len(entries)}, expected 12")
    if len({entry[0] for entry in entries}) != len(entries):
        errors.append("manifest contains duplicate course ids")
    if len({entry[1] for entry in entries}) != len(entries):
        errors.append("manifest contains duplicate script slugs")

    for course_id, script_slug, declared_modules in entries:
        path = COURSE_DIR / f"{script_slug}.md"
        if not path.is_file():
            errors.append(f"{course_id}: missing private script {path.name}")
            continue
        script = path.read_text(encoding="utf-8", errors="ignore")
        frontmatter = re.search(r"(?ms)^---\s*(.*?)\s*---", script)
        actual_slug = re.search(r"(?m)^slug:\s*(\S+)", frontmatter.group(1) if frontmatter else "")
        actual_modules = len(re.findall(r"(?m)^###\s+Module\s+\d+\s+-", script))
        if not actual_slug or actual_slug.group(1) != script_slug:
            errors.append(f"{course_id}: frontmatter slug does not match {script_slug}")
        if actual_modules != int(declared_modules):
            errors.append(f"{course_id}: manifest modules={declared_modules}, script modules={actual_modules}")

    if errors:
        print("COURSE MANIFEST FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"COURSE MANIFEST PASS: {len(entries)}/12 active courses map to private scripts with matching module counts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
