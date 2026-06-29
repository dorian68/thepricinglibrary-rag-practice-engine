"""Strict Hull-practical quality gate for ThePricingLibrary course scripts.

This audit is intentionally severe. A course is not allowed to pass because it
contains a few headings. It must be large enough, source-grounded, calculator
backed, UI-block rich, and convincing for two demanding personas:

- a quant-finance student who wants Hull-level understanding;
- a young front-office professional who needs practical pricing/risk reflexes.

Default terminal condition: every course, every persona score, and the aggregate
score must be >= 98/100.
"""

from __future__ import annotations

import argparse
import json
import re
import unicodedata
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DIR = BACKEND_ROOT / "generated" / "course_scripts"

REQUIRED_UI_TYPES = {
    "equation",
    "scenario_table",
}
PRACTICAL_UI_TYPES = {
    "payoff",
    "price_chart",
    "vol_smile",
    "greeks_scenario",
    "monte_carlo",
    "corr_matrix",
    "covariance_matrix",
    "rate_shock_table",
    "stress_table",
    "pnl_grid",
}


def _norm(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    return text.lower()


def _word_count(text: str) -> int:
    return len(re.findall(r"\b[\w'-]+\b", text, flags=re.UNICODE))


def _section(text: str, heading: str) -> str:
    pattern = rf"(?ims)^##\s+{re.escape(heading)}\b.*?\n(.*?)(?=^##\s+|\Z)"
    match = re.search(pattern, text)
    return match.group(1).strip() if match else ""


def _scale(value: float, target: float) -> int:
    if target <= 0:
        return 100
    return int(round(min(100, max(0, value / target * 100))))


def _bool_score(flag: bool) -> int:
    return 100 if flag else 0


def _weighted(parts: list[tuple[int, float]]) -> int:
    total_weight = sum(weight for _, weight in parts)
    return int(round(sum(score * weight for score, weight in parts) / total_weight))


def _lesson_word_counts(cours_redige: str) -> list[int]:
    chunks = re.split(r"(?im)^###\s+Lecon\s+\d+\s+-\s+.+$", cours_redige)
    return [_word_count(chunk) for chunk in chunks[1:] if chunk.strip()]


def _source_stats(text: str) -> dict:
    sources = re.findall(r"(?m)^-\s+\[S\d+\]\s+(.+)$", text)
    noisy = 0
    clean = 0
    for line in sources:
        low = line.lower()
        if "extrait non cite" in low:
            continue
        excerpt = line.split(":", 1)[1].strip() if ":" in line else ""
        if not excerpt or re.fullmatch(r"[.,;\s]+", excerpt):
            noisy += 1
        elif re.match(r"^[a-z]{1,3}[,.\s]", excerpt) and len(excerpt) < 80:
            noisy += 1
        else:
            clean += 1
    return {"count": len(sources), "clean": clean, "noisy": noisy}


def audit_one(path: Path, threshold: int = 98) -> dict:
    text = path.read_text(encoding="utf-8", errors="ignore")
    normalized = _norm(text)
    cours_redige = _section(text, "Cours redige")
    lesson_words = _lesson_word_counts(cours_redige)

    modules = len(re.findall(r"(?im)^###\s+Module\s+\d+\s+-", text))
    lessons = len(re.findall(r"(?im)^###\s+Lecon\s+\d+\s+-", cours_redige))
    h2_sections = len(re.findall(r"(?m)^##\s+", text))
    full_words = _word_count(text)
    course_words = _word_count(cours_redige)
    avg_lesson_words = round(sum(lesson_words) / max(1, len(lesson_words)))
    min_lesson_words = min(lesson_words) if lesson_words else 0

    ui_types = re.findall(r"(?im)^\s*type:\s*([a-z_]+)", text)
    ui_type_set = set(ui_types)
    uiblocks = len(re.findall(r"(?m)^```uiblock\s*$", text))
    equations = len(re.findall(r"\$\$[\s\S]*?\$\$", text))
    equation_blocks = ui_types.count("equation")
    formulas = equations + equation_blocks
    source_stats = _source_stats(text)
    quiz_questions = len(re.findall(r"(?im)^\*\*Q\d+\.", text))

    solved_example = bool(re.search(r"(?im)^##\s+Exemple numerique resolu", text)) and bool(
        re.search(r"(?im)\bResultat\s*:", text)
    )
    corrected_exercise = bool(re.search(r"(?im)^##\s+Exercices? corriges?", text)) and bool(
        re.search(r"(?im)\bCorrection\b", text)
    )
    synthesis_case = bool(re.search(r"(?im)^##\s+Cas pratique de synthese", text))
    persona_checkpoint = bool(re.search(r"(?im)^##\s+Checkpoint personas exigeants", text))
    provenance = "legende de provenance" in normalized and "[extrait]" in normalized
    decision_language = len(
        re.findall(r"\b(quote|hedge|monitor|reduce|reject|escalate|decision|trader|sales|risk)\b", normalized)
    )
    market_language = len(
        re.findall(r"\b(prix|pricing|p&l|sensibilite|dv01|delta|gamma|vega|spread|vol|stress|scenario)\b", normalized)
    )

    structure_score = _weighted(
        [
            (_scale(modules, 8), 2.0),
            (_scale(lessons, max(8, modules)), 2.0),
            (_scale(h2_sections, 14), 1.0),
            (_bool_score("objectifs d'apprentissage" in normalized), 1.0),
            (_bool_score("prerequis" in normalized), 1.0),
        ]
    )
    depth_score = _weighted(
        [
            (_scale(full_words, 6500), 1.4),
            (_scale(course_words, 3000), 2.0),
            (_scale(avg_lesson_words, 320), 1.3),
            (_scale(min_lesson_words, 220), 1.0),
            (_scale(formulas, 6), 1.0),
        ]
    )
    grounded_score = _weighted(
        [
            (_scale(source_stats["count"], 16), 2.0),
            (_bool_score(source_stats["noisy"] == 0), 1.0),
            (_bool_score(provenance), 1.0),
            (_bool_score("couverture pedagogique des sources" in normalized), 1.0),
        ]
    )
    practice_score = _weighted(
        [
            (_bool_score(solved_example), 1.6),
            (_bool_score(corrected_exercise), 1.6),
            (_bool_score(synthesis_case), 1.2),
            (_scale(quiz_questions, 5), 1.0),
            (_scale(decision_language, 28), 1.0),
            (_scale(market_language, 45), 1.0),
        ]
    )
    ui_score = _weighted(
        [
            (_scale(uiblocks, 5), 2.0),
            (_bool_score(REQUIRED_UI_TYPES.issubset(ui_type_set)), 1.5),
            (_bool_score(bool(ui_type_set & PRACTICAL_UI_TYPES)), 1.5),
            (_scale(len(ui_type_set), 4), 1.0),
        ]
    )
    student_score = _weighted(
        [
            (structure_score, 1.3),
            (depth_score, 1.8),
            (grounded_score, 1.4),
            (_scale(formulas, 7), 1.2),
            (_bool_score(solved_example), 1.0),
            (_scale(quiz_questions, 5), 0.8),
            (_bool_score(persona_checkpoint), 0.8),
        ]
    )
    young_professional_score = _weighted(
        [
            (practice_score, 2.0),
            (ui_score, 1.5),
            (grounded_score, 1.0),
            (_scale(decision_language, 35), 1.3),
            (_bool_score(corrected_exercise), 1.0),
            (_bool_score(synthesis_case), 1.0),
        ]
    )
    overall = _weighted(
        [
            (structure_score, 1.2),
            (depth_score, 1.8),
            (grounded_score, 1.5),
            (practice_score, 1.7),
            (ui_score, 1.4),
            (student_score, 1.2),
            (young_professional_score, 1.2),
        ]
    )

    issues: list[str] = []
    criticals = {
        "minimum_8_modules": modules >= 8,
        "minimum_8_written_lessons": lessons >= 8,
        "cours_redige_min_3000_words": course_words >= 3000,
        "avg_lesson_min_320_words": avg_lesson_words >= 320,
        "sources_min_16": source_stats["count"] >= 16,
        "ui_blocks_min_5": uiblocks >= 5,
        "required_ui_types": REQUIRED_UI_TYPES.issubset(ui_type_set),
        "practical_ui_type": bool(ui_type_set & PRACTICAL_UI_TYPES),
        "solved_example": solved_example,
        "corrected_exercise": corrected_exercise,
        "quiz_min_5": quiz_questions >= 5,
        "student_persona_98": student_score >= threshold,
        "young_professional_persona_98": young_professional_score >= threshold,
    }
    for name, ok in criticals.items():
        if not ok:
            issues.append(name)
    if source_stats["noisy"]:
        issues.append(f"noisy_sources={source_stats['noisy']}")

    gate = (
        "PASS"
        if overall >= threshold
        and student_score >= threshold
        and young_professional_score >= threshold
        and all(criticals.values())
        and source_stats["noisy"] == 0
        else "FAIL"
    )
    return {
        "slug": path.stem,
        "gate": gate,
        "quality_score": overall,
        "student_quant_persona": student_score,
        "young_professional_persona": young_professional_score,
        "axes": {
            "structure": structure_score,
            "depth": depth_score,
            "grounding": grounded_score,
            "practice": practice_score,
            "ui_blocks": ui_score,
        },
        "metrics": {
            "words_total": full_words,
            "words_cours_redige": course_words,
            "h2_sections": h2_sections,
            "modules": modules,
            "lessons": lessons,
            "avg_lesson_words": avg_lesson_words,
            "min_lesson_words": min_lesson_words,
            "formulas": formulas,
            "uiblocks": uiblocks,
            "uiblock_types": sorted(ui_type_set),
            "sources": source_stats["count"],
            "noisy_sources": source_stats["noisy"],
            "quiz_questions": quiz_questions,
            "decision_language_hits": decision_language,
            "market_language_hits": market_language,
        },
        "criticals": criticals,
        "issues": issues,
    }


def audit_dir(course_dir: Path, threshold: int) -> dict:
    files = sorted(p for p in course_dir.glob("*.md") if not p.name.startswith("_"))
    if not files:
        return {
            "course_dir": str(course_dir),
            "courses_audited": 0,
            "threshold": threshold,
            "section_gate": "FAIL",
            "error": "no course markdown found",
            "per_course": [],
        }
    per_course = [audit_one(path, threshold=threshold) for path in files]
    n = len(per_course)
    avg = lambda key: round(sum(item[key] for item in per_course) / n)  # noqa: E731
    axes = {
        name: round(sum(item["axes"][name] for item in per_course) / n)
        for name in ["structure", "depth", "grounding", "practice", "ui_blocks"]
    }
    passed = sum(1 for item in per_course if item["gate"] == "PASS")
    all_pass = passed == n
    return {
        "course_dir": str(course_dir),
        "courses_audited": n,
        "threshold": threshold,
        "course_section_quality_score": avg("quality_score"),
        "student_quant_persona": avg("student_quant_persona"),
        "young_professional_persona": avg("young_professional_persona"),
        "axes": axes,
        "courses_passing_gate": passed,
        "section_gate": "PASS" if all_pass else "FAIL",
        "per_course": per_course,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Strict audit of Hull-level course quality.")
    parser.add_argument("--dir", default=str(DEFAULT_DIR))
    parser.add_argument("--threshold", type=int, default=98)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    report = audit_dir(Path(args.dir).resolve(), threshold=args.threshold)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print("[Strict Course Quality Gate]\n")
        print(f"Course dir: {report['course_dir']}")
        print(f"Courses audited: {report['courses_audited']}")
        print(f"Threshold: {report['threshold']}/100\n")
        print(f"Aggregate quality:          {report.get('course_section_quality_score', 0)}/100")
        print(f"Student quant persona:      {report.get('student_quant_persona', 0)}/100")
        print(f"Young professional persona: {report.get('young_professional_persona', 0)}/100")
        print(f"Axes: {json.dumps(report.get('axes', {}), ensure_ascii=False)}")
        print(f"Courses passing: {report.get('courses_passing_gate', 0)}/{report.get('courses_audited', 0)}")
        print(f"Section Quality Gate: {report['section_gate']}")
        failures = [item for item in report.get("per_course", []) if item["gate"] != "PASS"]
        if failures:
            print("\nFailing courses:")
            for item in failures:
                print(
                    f"- {item['slug']}: quality={item['quality_score']}, "
                    f"student={item['student_quant_persona']}, "
                    f"young_pro={item['young_professional_persona']}, "
                    f"issues={', '.join(item['issues'])}"
                )
    return 0 if report["section_gate"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
