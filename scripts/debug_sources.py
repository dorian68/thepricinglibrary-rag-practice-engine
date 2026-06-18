"""Debug the pedagogical quality of the ingested source corpus.

Reads the live SQLite corpus, reports pedagogical coverage (content-type
distribution, usable chunks, average pedagogical score, detected definitions /
examples / exercises / formulas), and flags missing content types.

Usage:
    python scripts/debug_sources.py
    python scripts/debug_sources.py --sample 2000   # classify-on-the-fly sample
    python scripts/debug_sources.py --json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from pricinglibrary_rag.factory import build_services
from pricinglibrary_rag.pedagogy import (
    classify_chunk,
    detect_pedagogical_gaps,
    summarize_pedagogy,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit source pedagogical quality.")
    parser.add_argument(
        "--sample",
        type=int,
        default=0,
        help="Classify N chunks on the fly instead of reading stored columns.",
    )
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON only.")
    args = parser.parse_args()

    services = build_services()
    store = services.store

    if args.sample > 0:
        chunks = store.iter_chunks(limit=args.sample)
        items = [
            classify_chunk(c.content, section_title=c.section_title).to_metadata()
            for c in chunks
        ]
        summary = summarize_pedagogy(items)
        gaps = detect_pedagogical_gaps(items)
        report = {"mode": "sample", "sample_size": len(items), "summary": summary, "gaps": gaps}
    else:
        stats = store.pedagogy_stats()
        # Pull a usable sample for gap detection across the corpus.
        usable_chunks = store.iter_chunks(usable_only=True, limit=4000)
        items = [
            (c.metadata or {}).get("pedagogy")
            or classify_chunk(c.content, section_title=c.section_title).to_metadata()
            for c in usable_chunks
        ]
        gaps = detect_pedagogical_gaps(items)
        report = {"mode": "stored", "stats": stats, "gaps": gaps}

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0

    _print_human(report)
    return 0


def _print_human(report: dict) -> None:
    print("=" * 64)
    print("  ThePricingLibrary - Source pedagogical audit")
    print("=" * 64)

    if report["mode"] == "stored":
        s = report["stats"]
        print(f"Documents loaded:            {s['documents']}")
        print(f"Chunks total:                {s['chunks']}")
        print(f"Chunks classified:           {s['classified']} "
              f"(unclassified: {s['unclassified']})")
        print(f"Chunks usable for course:    {s['usable_for_course']} "
              f"({s['usable_ratio'] * 100:.1f}%)")
        print(f"Average pedagogical score:   {s['average_pedagogical_value']}/100")
        print(f"Average structural quality:  {s['average_quality_score']}/100")
        print("-" * 64)
        print("Content-type distribution:")
        for ct, n in s["content_type_distribution"].items():
            print(f"  {ct:<22} {n}")
        if s["unclassified"] > 0:
            print("-" * 64)
            print(f"!! {s['unclassified']} chunks predate pedagogical metadata.")
            print("   Run: python -m pricinglibrary_rag.cli backfill-pedagogy")
    else:
        s = report["summary"]
        print(f"Sampled chunks:              {report['sample_size']}")
        print(f"Usable for course:           {s['usable']} ({s['usable_ratio'] * 100:.1f}%)")
        print(f"Average pedagogical score:   {s['average_pedagogical_value']}/100")
        print(f"Average structural quality:  {s['average_quality_score']}/100")
        print(f"Definitions found:           {s['definitions']}")
        print(f"Examples found:              {s['examples']}")
        print(f"Exercises found:             {s['exercises']}")
        print(f"Formulas found:              {s['formulas']}")
        print(f"Case studies found:          {s['case_studies']}")
        print("-" * 64)
        print("Content-type distribution:")
        for ct, n in s["content_type_distribution"].items():
            print(f"  {ct:<22} {n}")

    g = report["gaps"]
    print("-" * 64)
    print(f"Corpus pedagogical status:   {g['status'].upper()}")
    print(f"Present blocks:              {', '.join(g['present']) or 'none'}")
    print(f"Missing content types:       {', '.join(g['missing']) or 'none'}")
    print("=" * 64)


if __name__ == "__main__":
    raise SystemExit(main())
