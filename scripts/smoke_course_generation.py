"""End-to-end smoke test for the sources -> course-generation pipeline.

Self-contained and fully offline:
- spins up a throwaway SQLite DB and the template LLM (no OpenAI call);
- ingests a small set of mock finance sources;
- chunks + classifies + scores them (pedagogical metadata);
- builds a course outline and generates one course section;
- checks the sources are actually cited ([S1] markers);
- detects pedagogical gaps;
- prints the report in the requested format and exits non-zero on failure.

Usage:
    python scripts/smoke_course_generation.py
    python scripts/smoke_course_generation.py --keep   # keep the temp dir
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import tempfile
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

# Force a deterministic, offline configuration BEFORE importing the package.
_TMP = Path(tempfile.mkdtemp(prefix="tpl_smoke_"))
os.environ["TPL_DATA_DIR"] = str(_TMP)
os.environ["TPL_DB_PATH"] = str(_TMP / "smoke.sqlite3")
os.environ["TPL_LLM_PROVIDER"] = "template"
os.environ["TPL_EMBEDDING_BACKEND"] = "local-hashing"
os.environ["TPL_EMBEDDING_DIM"] = "512"

from pricinglibrary_rag.factory import build_services  # noqa: E402
from pricinglibrary_rag.pedagogy import detect_pedagogical_gaps, summarize_pedagogy  # noqa: E402
from pricinglibrary_rag.schemas import CourseRequest, DocumentMetadata  # noqa: E402


# --- Mock sources: a deliberately rich teaching set for one topic ----------
MOCK_SOURCES: dict[str, str] = {
    "barrier_definition.md": """
# Barrier options - definition and intuition

A barrier option is defined as an option whose payoff depends on whether the
underlying asset reaches a predetermined barrier level during the option's life.
We define a knock-out option as one that ceases to exist if the barrier is
touched, and a knock-in option as one that only becomes active once the barrier
is touched.

Intuitively, you can think of a down-and-out call as a cheaper call: it behaves
like a vanilla call as long as the spot stays above the barrier, but it is
extinguished the moment the spot trades through the barrier. Because the option
can disappear, it must be cheaper than the equivalent vanilla option.
""",
    "barrier_formula.md": """
# Barrier option pricing relationship

For a down-and-out call with barrier H below the strike, the in-out parity holds:
C_vanilla = C_down_and_out + C_down_and_in. Therefore the price of the knock-out
equals the vanilla price minus the knock-in price. The reflection principle gives
a closed-form expression under Black-Scholes where the barrier term scales with
(H / S)^(2r / sigma^2 - 1). The key sensitivity is the distance from spot to the
barrier, measured as log(S / H) / sigma.
""",
    "barrier_worked_example.md": """
# Worked example - down-and-out call payoff

Consider a down-and-out call. For example, suppose the spot is 100, the strike is
100, the barrier is 90, and the notional is 1,000,000. Compute the payoff in three
scenarios. Scenario 1: spot ends at 110 without touching 90, payoff = 10 x 1,000,000
/ 100 = 100,000. Scenario 2: spot touches 90 then recovers to 110, payoff = 0 because
the option knocked out. Scenario 3: spot ends at 95 without touching the barrier,
payoff = 0 because it expires out of the money. This illustrates the path dependency.
""",
    "barrier_exercise.md": """
# Exercise - gap risk near the barrier

Exercise: a trader is short a down-and-out call with barrier at 1.0000 in EUR/USD,
spot at 1.0080. Calculate the approximate delta exposure and show that the delta
becomes unstable as the spot approaches the barrier. Determine what hedge action
the desk should take and prove that a standard delta hedge fails to control the
gap risk when the spot is within 20 pips of the barrier.

Solution: near the barrier the option value drops discontinuously to zero on a
knock-out, so the local delta spikes. We have a hedge that must be rebalanced far
too aggressively to be practical; therefore the desk should monitor the barrier
distance, cap the position, and escalate when spot is within the danger zone.
""",
    "barrier_case_study.md": """
# Case study - 2015 CHF de-peg and barrier monitoring

In practice the desk learned this the hard way. During the 2015 Swiss franc
de-peg, several knock-out structures gapped through their barriers overnight when
liquidity vanished. The trading desk could not rebalance hedges because the market
moved discontinuously. In summary, the takeaway is that barrier risk is not a
smooth Greek: monitoring, position caps and escalation matter more than a precise
continuous delta hedge. To sum up, gap risk dominates model risk near the barrier.
""",
}


def _write_sources(root: Path) -> Path:
    src_dir = root / "mock_sources"
    src_dir.mkdir(parents=True, exist_ok=True)
    for name, body in MOCK_SOURCES.items():
        (src_dir / name).write_text(body.strip() + "\n", encoding="utf-8")
    return src_dir


def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke test the course pipeline.")
    parser.add_argument("--keep", action="store_true", help="Keep the temp working dir.")
    args = parser.parse_args()

    failures: list[str] = []
    services = build_services()
    src_dir = _write_sources(_TMP)

    # 1) Ingest mock sources (chunk + classify + score happen here) ----------
    results = services.ingestion.ingest_directory(
        src_dir,
        metadata=DocumentMetadata(
            product="FX barrier option",
            asset_class="fx",
            concepts=["barrier", "gap risk", "monitoring"],
            tags=["mock", "smoke"],
        ),
        glob="*.md",
        recursive=False,
    )
    services.retriever.refresh()
    ingested = sum(1 for r in results if r.status == "ingested")
    chunks_inserted = sum(r.chunks_inserted for r in results)
    if ingested == 0:
        failures.append("no source ingested")

    # 2) Inspect classified chunks ------------------------------------------
    chunks = services.store.iter_chunks()
    items = [
        (c.metadata or {}).get("pedagogy")
        for c in chunks
        if (c.metadata or {}).get("pedagogy")
    ]
    summary = summarize_pedagogy(items)
    gaps = detect_pedagogical_gaps(items)
    if summary["total"] == 0:
        failures.append("no chunk carried pedagogy metadata")
    if summary["usable"] == 0:
        failures.append("no usable chunk for course generation")

    # 3) Generate a course (outline + written section) ----------------------
    course = services.generator.generate_course(
        CourseRequest(
            topic="Barrier options and gap risk",
            product="FX barrier option",
            concepts=["down-and-out", "knock-out", "gap risk", "monitoring"],
            level="advanced",
            duration_minutes=120,
            module_count=4,
            language="fr",
        )
    )
    content = course.content
    outline_ok = bool(re.search(r"(?im)^###\s+Module\s+\d+", content))
    section_ok = bool(re.search(r"(?im)^###\s+Lecon\s+\d+", content))
    grounding_ok = bool(course.sources) and bool(re.search(r"\[S\d+\]", content))
    coverage_section_ok = "Couverture pedagogique des sources" in content
    gaps_section_ok = "Trous pedagogiques" in content
    prereqs_ok = bool(re.search(r"(?im)^##\s+Prerequis", content))
    solved_ok = bool(re.search(r"(?im)^##\s+Exemple numerique resolu", content)) and \
        bool(re.search(r"(?im)resultat\s*:", content))
    exercise_ok = bool(re.search(r"(?im)^##\s+Exercices? corriges?", content)) and \
        "Correction" in content
    quiz_ok = len(re.findall(r"(?im)^\*\*Q\d+\.", content)) >= 3
    summary_ok = bool(re.search(r"(?im)^##\s+Resume", content))
    # boilerplate: the old identical-scaffolding sentence must be gone
    boilerplate_ok = content.count("l'apprenant doit transformer la demande en inputs") < 2
    # clean snippets: no mid-word OCR fragment injected as a quote
    clean_snippets_ok = not re.search(r"« [a-z]{1,3}, ", content)

    if not outline_ok:
        failures.append("course outline missing (no '### Module N')")
    if not section_ok:
        failures.append("written course section missing (no '### Lecon N')")
    if not grounding_ok:
        failures.append("source grounding missing (no [Sx] markers or no sources)")
    if not coverage_section_ok:
        failures.append("coverage section missing from course")
    if not gaps_section_ok:
        failures.append("gaps section missing from course")
    if not prereqs_ok:
        failures.append("prerequisites section missing")
    if not solved_ok:
        failures.append("solved numerical example missing")
    if not exercise_ok:
        failures.append("corrected exercise missing")
    if not quiz_ok:
        failures.append("real quiz (>=3 MCQ) missing")
    if not summary_ok:
        failures.append("summary section missing")
    if not boilerplate_ok:
        failures.append("boilerplate repetition detected")
    if not clean_snippets_ok:
        failures.append("mid-word OCR fragment shown as a quote")

    # 4) Report -------------------------------------------------------------
    print("=" * 64)
    print("  SMOKE TEST - sources -> course generation")
    print("=" * 64)
    print(f"Sources loaded:                  {ingested}")
    print(f"Chunks generated:                {chunks_inserted}")
    print(f"Chunks usable for course gen:    {summary['usable']} "
          f"({summary['usable_ratio'] * 100:.0f}%)")
    print(f"Definitions found:               {summary['definitions']}")
    print(f"Examples found:                  {summary['examples']}")
    print(f"Exercises found:                 {summary['exercises']}")
    print(f"Formulas found:                  {summary['formulas']}")
    print(f"Case studies found:              {summary['case_studies']}")
    print(f"Average pedagogical score:       {summary['average_pedagogical_value']}/100")
    print(f"Content-type distribution:       {summary['content_type_distribution']}")
    print(f"Missing content types:           {', '.join(gaps['missing']) or 'none'}")
    print(f"Corpus pedagogical status:       {gaps['status']}")
    print(f"Generated with:                  {services.llm.name}")
    print("-" * 64)
    print(f"Generated course outline:        {'OK' if outline_ok else 'FAIL'}")
    print(f"Written course section:          {'OK' if section_ok else 'FAIL'}")
    print(f"Prerequisites:                   {'OK' if prereqs_ok else 'FAIL'}")
    print(f"Solved numerical example:        {'OK' if solved_ok else 'FAIL'}")
    print(f"Corrected exercise:              {'OK' if exercise_ok else 'FAIL'}")
    print(f"Quiz (>=3 MCQ):                  {'OK' if quiz_ok else 'FAIL'}")
    print(f"Summary:                         {'OK' if summary_ok else 'FAIL'}")
    print(f"Source grounding ([Sx]):         {'OK' if grounding_ok else 'FAIL'}")
    print(f"Clean snippets (no OCR frag):    {'OK' if clean_snippets_ok else 'FAIL'}")
    print(f"Boilerplate repetition:          {'PASS' if boilerplate_ok else 'FAIL'}")
    print(f"Coverage section in course:      {'OK' if coverage_section_ok else 'FAIL'}")
    print(f"Gaps section in course:          {'OK' if gaps_section_ok else 'FAIL'}")
    print(f"Course sources cited:            {len(course.sources)}")
    print("=" * 64)

    if args.keep:
        print(f"[kept] working dir: {_TMP}")
    else:
        import shutil

        shutil.rmtree(_TMP, ignore_errors=True)

    if failures:
        print("SMOKE: FAIL")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("SMOKE: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
