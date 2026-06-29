"""Refresh ONLY the deterministic verified blocks in already-generated courses.

Regenerates the three engine-backed sections (worked example, corrected
exercises, mini-quiz) from the current course_blocks/calculators code and
splices them back into each course markdown, leaving the LLM-authored prose
untouched. Idempotent: re-running on an up-to-date file is a no-op.

Usage:
    python scripts/refresh_verified_blocks.py            # apply
    python scripts/refresh_verified_blocks.py --check     # report drift only
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pricinglibrary_rag.course_blocks import (
    corrected_exercise_markdown,
    quiz_markdown,
    theory_block_markdown,
    worked_example_markdown,
)

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]  # THEPRICINGLIBRARY

TARGET_DIRS = [
    ROOT / "generated" / "course_scripts",
    REPO / "WEBSITE" / "thepricinglab" / "public" / "course-scripts",
]

FILE_TOPIC = {
    "vanilla-options-quote.md": "vanilla_bs",
    "rates-swaps-dv01.md": "swap",
    "yield-curve-bootstrapping.md": "yield_curve",
    "fixed-income-bonds-duration.md": "bond",
    "barrier-options-gap-risk.md": "barrier",
    "structured-products-autocall.md": "autocall",
    "options-book-greeks-pnl.md": "greeks",
    "implied-volatility-smile.md": "vol_smile",
    "monte-carlo-pricing.md": "monte_carlo",
    "stochastic-calculus-for-hedging.md": "stochastic",
    "credit-derivatives-cds.md": "cds",
    "market-risk-var-stress.md": "var",
}

# (header, generator, insert_before) — insert_before is used only when the
# header is absent from the file (new section spliced in at that anchor).
SECTIONS = [
    ("## Fondements theoriques (ancres sources)", theory_block_markdown, "## Exemple numerique resolu"),
    ("## Exemple numerique resolu", worked_example_markdown, None),
    ("## Exercices corriges", corrected_exercise_markdown, None),
    ("## Mini-quiz", quiz_markdown, None),
]


def replace_section(text: str, header: str, new_body: str, insert_before: str | None) -> str:
    lines = text.split("\n")
    try:
        start = next(i for i, ln in enumerate(lines) if ln.strip() == header)
    except StopIteration:
        if not insert_before:
            return text  # header absent and no anchor: leave file alone
        try:
            anchor = next(i for i, ln in enumerate(lines) if ln.strip() == insert_before)
        except StopIteration:
            return text
        block = [header, new_body, ""]
        new = lines[:anchor] + block + lines[anchor:]
        return "\n".join(new)
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if lines[j].startswith("## "):
            end = j
            break
    new = lines[:start + 1] + [new_body, ""] + lines[end:]
    return "\n".join(new)


def refresh_text(text: str, topic_key: str) -> str:
    for header, fn, insert_before in SECTIONS:
        body = fn(topic_key)
        text = replace_section(text, header, body, insert_before)
    return text


def main() -> int:
    check_only = "--check" in sys.argv
    changed, scanned = 0, 0
    for d in TARGET_DIRS:
        if not d.exists():
            print(f"[skip] {d} (absent)")
            continue
        for fname, topic in FILE_TOPIC.items():
            path = d / fname
            if not path.exists():
                continue
            scanned += 1
            old = path.read_text(encoding="utf-8")
            new = refresh_text(old, topic)
            if new != old:
                changed += 1
                tag = "DRIFT" if check_only else "updated"
                print(f"[{tag}] {path.relative_to(REPO)}  (topic={topic})")
                if not check_only:
                    path.write_text(new, encoding="utf-8")
            else:
                print(f"[ok]      {path.relative_to(REPO)}  (topic={topic})")
    print(f"\n{scanned} files scanned, {changed} {'would change' if check_only else 'updated'}.")
    return 1 if (check_only and changed) else 0


if __name__ == "__main__":
    raise SystemExit(main())
