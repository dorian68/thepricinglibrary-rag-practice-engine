"""Release audit for the learner-facing course requirements in the product brief.

The existing quality gate measures depth and grounding. This audit adds the
commercially important invariants that headings alone cannot prove: visible
course-specific quizzes, no repeated question stems, a complete desk workflow
and a deterministic course/tool route contract.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = BACKEND_ROOT.parents[1]
COURSE_DIR = BACKEND_ROOT / "pricinglibrary_rag" / "course_scripts"
MANIFEST = REPO_ROOT / "WEBSITE" / "thepricinglab" / "src" / "claude" / "courseManifest.js"
FRONTEND = REPO_ROOT / "WEBSITE" / "thepricinglab" / "src" / "claude" / "ClaudeFrontend.jsx"


def visible(text: str) -> str:
    return re.sub(r"<!--.*?-->", "", text, flags=re.S)


def norm(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def main() -> int:
    manifest_text = MANIFEST.read_text(encoding="utf-8")
    frontend_text = FRONTEND.read_text(encoding="utf-8")
    entries = re.findall(r"\{ id: '([^']+)', scriptSlug: '([^']+)'", manifest_text)
    if len(entries) != 12 or len({course_id for course_id, _ in entries}) != 12:
        print("COURSE OBJECTIVE FAIL: canonical manifest is not 12 unique entries")
        return 1

    required_markers = {
        "promesse": r"^## Promesse du module",
        "prerequis": r"^## Prerequis",
        "objectifs": r"^## Objectifs d'apprentissage",
        "exemple": r"^## Exemple numerique resolu",
        "exercice": r"^## Exercices corriges",
        "synthese": r"^## Cas pratique de synthese",
        "checkpoint": r"^## Checkpoint personas exigeants",
        "source_map": r"Sources RAG a citer",
        "limits": r"limites? du modele|limites? du modèle",
    }
    all_stems: dict[str, str] = {}
    failures: list[str] = []
    checked = 0
    for course_id, script_slug in entries:
        path = COURSE_DIR / f"{script_slug}.md"
        if not path.is_file():
            failures.append(f"{course_id}: missing script {script_slug}")
            continue
        text = visible(path.read_text(encoding="utf-8", errors="ignore"))
        checked += 1
        for label, pattern in required_markers.items():
            if not re.search(pattern, text, re.I | re.M):
                failures.append(f"{course_id}: missing {label}")
        questions = re.findall(r"^\*\*Q\d+\.\s+(.+?)\*\*$", text, re.M)
        answers = re.findall(r"R[ée]ponse:\s*\*\*[A-D]\*\*", text, re.I)
        if len(questions) != 5 or len(answers) != 5:
            failures.append(f"{course_id}: visible quiz is {len(questions)}/5 questions and {len(answers)}/5 answers")
        for stem in questions:
            key = norm(stem)
            owner = all_stems.get(key)
            if owner and owner != course_id:
                failures.append(f"{course_id}: repeated visible quiz stem from {owner}: {stem}")
            else:
                all_stems[key] = course_id

        if course_id == "fixed-income-bonds" and any("swap" in norm(question) for question in questions):
            failures.append("fixed-income-bonds: quiz still tests swaps instead of bonds")
        if "Quiz spécifique" not in text:
            failures.append(f"{course_id}: course-specific quiz heading missing")

    # Each course must have a visible calculator or an explicit deterministic
    # course-bound scenario. The fallback Browse tools copy is not enough.
    course_calculator_block = re.search(r"function CourseCalculator\(\{c\}\) \{([\s\S]*?)\n\}\n\nfunction CourseExercises", frontend_text)
    if not course_calculator_block:
        failures.append("frontend: CourseCalculator contract missing")
    else:
        block = course_calculator_block.group(1)
        for course_id in [course_id for course_id, _ in entries]:
            if course_id not in block:
                failures.append(f"frontend: course calculator has no explicit branch for {course_id}")

    if failures:
        print(f"COURSE OBJECTIVE FAIL: {len(failures)} issue(s)")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print(f"COURSE OBJECTIVE PASS: {checked}/12 courses have complete desk structure, visible unique quizzes and explicit calculator/scenario routing")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
