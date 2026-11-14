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
import sqlite3
import sys
import unicodedata
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from pricinglibrary_rag.api import (
    _COURSE_REFERENCE_ALLOWLIST,
    _public_course_markdown,
    _reference_match_text,
)

DEFAULT_DIR = BACKEND_ROOT / "pricinglibrary_rag" / "course_scripts"
DEFAULT_CORPUS_DB = BACKEND_ROOT / "data" / "pricinglibrary_rag.sqlite3"

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

# Trust blockers observed during independent business review. These are not
# stylistic preferences: each pattern encodes a materially false quant claim
# that must fail the release gate even when the course is structurally rich.
FORBIDDEN_QUANT_CLAIMS = {
    "rates_must_be_positive": r"un taux d(?:'|’)interet doit etre positif",
    "inverted_curve_is_invalid": r"taux a 3 ans ne sont pas superieurs a ceux a 5 ans",
    "negative_curve_implies_bad_interpolation": r"taux negatifs[^.]{0,160}interpolation mal realisee",
    "fixed_seed_biases_estimator": r"meme graine[^.]{0,180}resultats biaises",
    "small_sample_biases_estimator": r"taille d(?:'|’)echantillon[^.]{0,180}resultats biaises",
    "seed_change_completely_changes_result": r"change la graine[^.]{0,180}resultats completement differents",
    "monte_carlo_predicts_future": r"capacite a predire[^.]{0,240}monte carlo",
    "historical_prices_are_q_pricing_inputs": r"rassembler[^.]{0,140}(?:prix|donnees) historiques[^.]{0,220}(?:tarif|pricing|monte carlo)",
    "risk_neutral_means_risk_indifferent_investors": r"investisseurs sont indifferents au risque",
    "q_drift_depends_on_historical_return": r"drift neutre au risque[^.]{0,180}rendements historiques",
    "volatility_predicts_spot_direction": r"hausse de la volatilite[^.]{0,180}(?:tendance haussiere|signal haussier|spot (?:monte|augmente))",
    "volatility_growth_predicts_higher_prices": r"volatilite croissante[^.]{0,180}tendance a la hausse des prix",
    "cds_positive_carry_means_profitable": r"signe du carry doit etre positif[^.]{0,120}profitable",
    "cds_widening_is_always_negative": r"impact d(?:'|’)un widening est negatif",
    "cds_existing_carry_rises_with_market_spread": r"si le spread augmente, le carry peut egalement augmenter",
    "positive_convexity_understates_rate_up_loss": r"neglig(?:e|er)[^.]{0,120}convexite[^.]{0,220}sous-estim(?:e|er)[^.]{0,80}pertes",
    "delta_is_always_percentage": r"delta (?:doit etre|est) exprime en pourcentage",
    "gamma_is_always_percentage_squared": r"gamma (?:doit etre|est) exprime en pourcentage au carre",
    "positive_delta_means_in_the_money": r"delta positif indique que l(?:'|’)option est dans la monnaie",
    "positive_delta_means_long_position": r"delta positif (?:doit etre interprete comme|indique) une position (?:acheteuse|longue)",
    "positive_delta_means_buy_underlying_to_hedge": r"delta positif[^.]{0,160}acheter des actions[^.]{0,80}couvr",
    "delta_hedge_cannot_lose": r"couvre mon option[^.]{0,120}ne peux pas perdre",
    "positive_cs01_always_means_loss": r"cs01 positif indique une perte",
    "long_cds_always_loses_on_widening": r"spread qui s.elargit[^.]{0,180}pertes sur des positions longues en cds",
    "cds_carry_is_always_revenue": r"carry represente le revenu genere par la detention d.un cds",
    "historical_volatility_is_quote_input": r"prix propose est base sur une volatilite historique",
    "call_put_delta_sign_ignores_position": r"delta est bien positif pour les options d.achat et negatif pour les options de vente",
    "long_spread_always_positive": r"spread long doit toujours aboutir a un resultat positif",
    "static_spread_requires_correlation_adjustment": r"prix d(?:'|’)un spread n(?:'|’)est pas simplement la somme[^.]{0,180}correlation",
    "static_spread_leg_values_need_correlation": r"valeurs de chaque option[^.]{0,180}mais aussi leur correlation",
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


def _registered_public_reference_count(public_text: str, slug: str) -> int:
    rules = _COURSE_REFERENCE_ALLOWLIST.get(slug, ())
    section = _section(public_text, "References du cours")
    entries = re.findall(r"(?m)^-\s+\*.+?\*\s+—\s+«(.+)»\s*$", section)
    return sum(
        1
        for entry in entries
        if any(anchor in _reference_match_text(entry) for anchor, _, _ in rules)
    )


def _corpus_reference_anchors_verified(slug: str) -> bool:
    rules = _COURSE_REFERENCE_ALLOWLIST.get(slug, ())
    if not rules or not DEFAULT_CORPUS_DB.is_file():
        return False
    with sqlite3.connect(f"file:{DEFAULT_CORPUS_DB.as_posix()}?mode=ro", uri=True) as connection:
        for anchor, document_id, chunk_index in rules:
            row = connection.execute(
                "SELECT content FROM chunks WHERE document_id = ? AND chunk_index = ?",
                (document_id, chunk_index),
            ).fetchone()
            if row is None or anchor not in _reference_match_text(str(row[0])):
                return False
    return True


def audit_one(path: Path, threshold: int = 98) -> dict:
    text = path.read_text(encoding="utf-8", errors="ignore")
    public_text = _public_course_markdown(text)
    # Learner-facing metrics must ignore archived/replaced markdown blocks.
    # Otherwise a course with one visible quiz plus one commented legacy quiz
    # is incorrectly reported as having duplicate content.
    visible_text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
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
    public_reference_section = _section(public_text, "References du cours")
    public_reference_count = len(re.findall(r"(?m)^-\s+\*.+?\*\s+—\s+«.+»\s*$", public_reference_section))
    registered_public_reference_count = _registered_public_reference_count(public_text, path.stem)
    corpus_reference_anchors_verified = _corpus_reference_anchors_verified(path.stem)
    public_citation_ghosts = len(
        re.findall(
            r"\bextraits?\b|\[s(?:\d+|x)\]|\b[ld]['’]source\b",
            _norm(public_text),
        )
    )
    quiz_questions = len(re.findall(r"(?im)^\*\*Q\d+\.", visible_text))

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
    quant_truth_violations = [
        name for name, pattern in FORBIDDEN_QUANT_CLAIMS.items()
        if re.search(pattern, _norm(cours_redige))
    ]

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
        "quant_truth_claims": not quant_truth_violations,
        "public_reference_present": public_reference_count >= 1,
        "public_references_reviewed": registered_public_reference_count == public_reference_count,
        "corpus_reference_anchors_verified": corpus_reference_anchors_verified,
        "public_citation_ghosts_absent": public_citation_ghosts == 0,
    }
    for name, ok in criticals.items():
        if not ok:
            issues.append(name)
    if source_stats["noisy"]:
        issues.append(f"noisy_sources={source_stats['noisy']}")
    issues.extend(f"forbidden_quant_claim={name}" for name in quant_truth_violations)

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
            "quant_truth_violations": quant_truth_violations,
            "public_reference_count": public_reference_count,
            "registered_public_reference_count": registered_public_reference_count,
            "corpus_reference_anchors_verified": corpus_reference_anchors_verified,
            "public_citation_ghosts": public_citation_ghosts,
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
