"""Pedagogical quality audit of the SHIPPED course scripts.

Unlike `audit_course_scripts.py` (which only counts modules/sources), this scans
each generated course markdown and scores it on the pedagogical checklist a real
student/instructor cares about: objectives, prerequisites, intuition, formulas,
examples, exercises, corrections, quiz, summary, source grounding — and detects
quality smells (OCR/mid-word source fragments, empty/"." snippets, boilerplate
repetition across lessons, double-period concatenation bugs).

It is read-only. Output mirrors the requested "[Course Audit Smoke Test]" format.

Usage:
    python scripts/audit_course_quality.py
    python scripts/audit_course_quality.py --dir ../../WEBSITE/thepricinglab/public/course-scripts
    python scripts/audit_course_quality.py --json
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DIR = BACKEND_ROOT / "generated" / "course_scripts"


def _verdict(ratio: float) -> str:
    if ratio >= 0.85:
        return "OK"
    if ratio >= 0.4:
        return "PARTIAL"
    return "MISSING"


def audit_one(path: Path) -> dict:
    text = path.read_text(encoding="utf-8", errors="ignore")
    body = text.lower()

    has_title = bool(re.search(r"^#\s+\S", text, re.MULTILINE))
    has_objectives = "objectifs d'apprentissage" in body or "learning objective" in body
    has_prereqs = "prerequis" in body or "prérequis" in body or "prerequisite" in body
    has_intuition = "intuition" in body or "intuitivement" in body
    formulas = len(re.findall(r"^\$\$", text, re.MULTILINE)) // 2
    has_formulas = formulas >= 1 or "### f1" in body
    lessons = re.findall(r"^###\s+Lecon\s+\d+\s+-\s+(.+)$", text, re.MULTILINE)
    has_explanation = len(lessons) >= 1
    has_examples = bool(re.search(r"exemple|example|cas de depart|application pratique", body))
    exercise_bank = re.findall(r"(?im)^##\s+Banque d'exercices", text)
    has_exercises = bool(exercise_bank) or "exercice" in body
    has_correction = bool(re.search(r"corrig|correction|solution", body))
    has_quiz = "quiz" in body
    has_summary = bool(re.search(r"resume|résumé|synthese|en conclusion|takeaway", body))
    sources = re.findall(r"^- \[S\d+\]\s+(.+)$", text, re.MULTILINE)
    has_sources = len(sources) >= 1

    # Precise richness signals (beyond keyword presence).
    solved_example = bool(re.search(r"(?im)^##\s+Exemple numerique resolu", text)) and \
        bool(re.search(r"(?im)resultat\s*:", text))
    corrected_exercise = bool(re.search(r"(?im)^##\s+Exercices? corriges?", text)) and \
        bool(re.search(r"(?im)\bcorrection\b", text))
    quiz_questions = len(re.findall(r"(?im)^\*\*Q\d+\.", text))
    real_quiz = quiz_questions >= 3

    # --- quality smells ----------------------------------------------------
    # Distinguish three cases per cited source:
    #  - a clean quote shown            -> good
    #  - excerpt honestly withheld      -> neutral (desired behaviour, not a defect)
    #  - garbled/empty/mid-word excerpt -> bad
    empty_snippets = 0
    midword_snippets = 0
    reference_only = 0
    clean_quotes = 0
    for s in sources:
        if "extrait non cite" in s.lower():
            reference_only += 1
            continue
        snippet = s.split("score", 1)[-1]
        snippet = snippet.split(":", 1)[1].strip() if ":" in snippet else ""
        if not snippet or re.fullmatch(r"[.\s,;]+", snippet):
            empty_snippets += 1
        elif re.match(r"^[a-z]{1,3}[,.\s]", snippet) or snippet[:1].islower():
            # starts mid-word / lowercase fragment (OCR / chunk boundary)
            midword_snippets += 1
        else:
            clean_quotes += 1

    # injected source fragments inside lessons that start mid-word
    midword_in_lessons = len(
        re.findall(r"\*\*Ce que la source apporte\.\*\*\s+[a-z]{1,4}[, ]", text)
    )
    ligatures = len(re.findall(r"[ﬁﬂﬀﬃﬄ]", text))
    double_periods = len(re.findall(r"\w\.\.(?:\s|$)", text))

    # boilerplate repetition: detect, GENERICALLY, any sentence repeated
    # verbatim across 3+ lessons of the same course (the fill-in-the-blank
    # skeleton smell). This replaces a brittle single-phrase grep that missed
    # the real templated scaffolding.
    lesson_section = ""
    m = re.search(r"(?ims)^##\s+Cours redige\b(.*?)(?=^##\s)", text)
    if m:
        lesson_section = m.group(1)
    lesson_chunks = re.split(r"(?im)^###\s+Lecon\s+\d+", lesson_section)[1:]

    def _norm(sent: str) -> str:
        s = sent.lower()
        s = re.sub(r"\[s\d+\]|_\[[a-z]+\]_|\*+", " ", s)  # drop [Sx], _[extrait]_, bold
        s = re.sub(r"[0-9]+", "", s)                        # drop numbers
        s = re.sub(r"[^a-zàâäéèêëîïôöùûüç ]+", " ", s)       # keep letters only
        return re.sub(r"\s+", " ", s).strip()

    sentence_lessons: dict[str, set[int]] = {}
    for li, chunk in enumerate(lesson_chunks):
        seen_here: set[str] = set()
        for raw in re.split(r"(?<=[.!?])\s+", chunk):
            norm = _norm(raw)
            if len(norm) < 40 or norm in seen_here:
                continue
            seen_here.add(norm)
            sentence_lessons.setdefault(norm, set()).add(li)
    boilerplate_hits = sum(1 for lessons_with in sentence_lessons.values() if len(lessons_with) >= 3)
    repetitive = boilerplate_hits >= 1

    checks = {
        "title": has_title,
        "objectives": has_objectives,
        "prerequisites": has_prereqs,
        "intuition": has_intuition,
        "formulas": has_formulas,
        "explanation": has_explanation,
        "examples": has_examples,
        "exercises": has_exercises,
        "correction": has_correction,
        "quiz": has_quiz,
        "summary": has_summary,
        "source_grounding": has_sources,
    }
    present = sum(1 for v in checks.values() if v)
    structure_score = round(100 * present / len(checks))

    # Grounding quality: among sources that DO show an excerpt, what share is
    # clean? Reference-only citations (excerpt withheld) are neutral, not bad.
    grounding_quality = 1.0
    shown = clean_quotes + empty_snippets + midword_snippets
    if shown:
        grounding_quality = clean_quotes / shown
    elif reference_only:
        # all excerpts honestly withheld: acceptable, not strongly grounded
        grounding_quality = 0.6
    grounding_score = round(100 * grounding_quality)

    # hallucination/credibility guardrails (lower is worse)
    smell_penalty = (
        empty_snippets * 6
        + midword_snippets * 3
        + midword_in_lessons * 4
        + ligatures
        + double_periods * 2
        + (20 if repetitive else 0)
    )
    guardrails_score = max(0, 100 - smell_penalty)

    # Richness penalties: a "course" without solved example / corrected
    # exercise / real quiz is not a real course regardless of structure.
    richness_penalty = 0
    reasons: list[str] = []
    if not solved_example:
        richness_penalty += 12
        reasons.append("no solved numerical example")
    if not corrected_exercise:
        richness_penalty += 10
        reasons.append("no corrected exercise")
    if not real_quiz:
        richness_penalty += 8
        reasons.append("no real quiz (>=3 MCQ)")
    if grounding_score < 50:
        reasons.append("weak source grounding")
    if repetitive:
        reasons.append("high boilerplate repetition")
    if not has_prereqs:
        reasons.append("no prerequisites")
    if not has_summary:
        reasons.append("no summary")

    quality = round(
        0.4 * structure_score
        + 0.28 * grounding_score
        + 0.22 * guardrails_score
        - richness_penalty
    )
    quality = max(0, min(100, quality))
    gate = "PASS" if quality >= 70 else "FAIL"

    return {
        "slug": path.stem,
        "checks": checks,
        "structure_score": structure_score,
        "grounding_score": grounding_score,
        "guardrails_score": guardrails_score,
        "quality": quality,
        "gate": gate,
        "reasons": reasons,
        "solved_example": solved_example,
        "corrected_exercise": corrected_exercise,
        "quiz_questions": quiz_questions,
        "lessons": len(lessons),
        "formulas": formulas,
        "sources": len(sources),
        "smells": {
            "empty_or_dot_snippets": empty_snippets,
            "midword_source_snippets": midword_snippets,
            "midword_fragments_in_lessons": midword_in_lessons,
            "pdf_ligatures": ligatures,
            "double_period_bugs": double_periods,
            "boilerplate_repetition": repetitive,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit shipped course pedagogical quality.")
    parser.add_argument("--dir", default=str(DEFAULT_DIR))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    course_dir = Path(args.dir).resolve()
    files = sorted(p for p in course_dir.glob("*.md") if not p.name.startswith("_"))
    if not files:
        print(f"No course markdown found in {course_dir}")
        return 1

    audits = [audit_one(p) for p in files]
    n = len(audits)
    agg = lambda key: round(sum(a[key] for a in audits) / n)  # noqa: E731
    overall = agg("quality")

    def axis(check: str) -> str:
        hits = sum(1 for a in audits if a["checks"][check])
        return _verdict(hits / n)

    passed = sum(1 for a in audits if a["gate"] == "PASS")
    section_gate = "PASS" if overall >= 70 and passed >= (n + 1) // 2 else "FAIL"
    report = {
        "course_dir": str(course_dir),
        "courses_audited": n,
        "axes": {
            "structure": agg("structure_score"),
            "grounding": agg("grounding_score"),
            "guardrails": agg("guardrails_score"),
        },
        "course_section_quality_score": overall,
        "courses_passing_gate": passed,
        "section_gate": section_gate,
        "per_course": audits,
    }

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0

    print("[Course Audit Smoke Test]\n")
    print(f"Course dir: {course_dir}")
    print(f"Courses audited: {n}\n")
    print(f"Title:                 {axis('title')}")
    print(f"Learning objectives:   {axis('objectives')}")
    print(f"Prerequisites:         {axis('prerequisites')}")
    print(f"Intuition:             {axis('intuition')}")
    print(f"Formulas:              {axis('formulas')}")
    print(f"Explanations:          {axis('explanation')}")
    print(f"Examples:              {axis('examples')}")
    print(f"Exercises:             {axis('exercises')}")
    print(f"Corrections:           {axis('correction')}")
    print(f"Quiz:                  {axis('quiz')}")
    print(f"Summary:               {axis('summary')}")
    print(f"Source grounding:      {axis('source_grounding')}")
    print("-" * 56)
    print(f"Structure score:       {report['axes']['structure']}/100")
    print(f"Grounding quality:     {report['axes']['grounding']}/100")
    print(f"Hallucination guardrails: {report['axes']['guardrails']}/100")
    print("-" * 56)
    tot = sum(a["smells"]["empty_or_dot_snippets"] for a in audits)
    midl = sum(a["smells"]["midword_fragments_in_lessons"] for a in audits)
    lig = sum(a["smells"]["pdf_ligatures"] for a in audits)
    dp = sum(a["smells"]["double_period_bugs"] for a in audits)
    rep = sum(1 for a in audits if a["smells"]["boilerplate_repetition"])
    print("Quality smells (corpus-wide):")
    print(f"  empty/'.'-only source snippets:   {tot}")
    print(f"  mid-word source fragments in body: {midl}")
    print(f"  PDF ligature artifacts:            {lig}")
    print(f"  double-period bugs:                {dp}")
    print(f"  courses with boilerplate repetition: {rep}/{n}")
    print(f"Solved numerical example: {axis('title') if False else _verdict(sum(1 for a in audits if a['solved_example'])/n)}")
    print(f"Corrected exercise:    {_verdict(sum(1 for a in audits if a['corrected_exercise'])/n)}")
    print(f"Real quiz (>=3 MCQ):   {_verdict(sum(1 for a in audits if a['quiz_questions']>=3)/n)}")
    print("-" * 56)
    print(f"Course Section Quality Score: {overall}/100")
    print(f"Courses passing gate (>=70): {report['courses_passing_gate']}/{n}")
    print(f"Section Quality Gate: {report['section_gate']}")
    # worst offenders with reasons
    worst = sorted(audits, key=lambda a: a["quality"])[:5]
    print("\nLowest-scoring courses:")
    for a in worst:
        print(f"  {a['slug']:<34} {a['quality']}/100 [{a['gate']}]  "
              f"(struct {a['structure_score']}, ground {a['grounding_score']}, guard {a['guardrails_score']})")
        if a["reasons"]:
            print(f"      reasons: {', '.join(a['reasons'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
