from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


EXPECTED_KEYWORDS = {
    "vanilla-options-quote": ["vanilla", "black-scholes", "parity", "greeks"],
    "options-book-greeks-pnl": ["greek", "p&l", "hedge", "risk"],
    "rates-swaps-dv01": ["swap", "dv01", "hedge", "basis"],
    "yield-curve-bootstrapping": ["curve", "bootstrap", "discount", "forward"],
    "implied-volatility-smile": ["option", "iv", "smile", "fit"],
    "monte-carlo-pricing": ["simulation", "paths", "interval", "variance"],
    "barrier-options-gap-risk": ["barrier", "payoff", "gap", "monitoring"],
    "structured-products-autocall": ["term sheet", "autocall", "protection", "scenario"],
    "credit-derivatives-cds": ["cds", "carry", "cs01", "credit"],
    "market-risk-var-stress": ["var", "stress", "limit", "escalation"],
    "fixed-income-bonds-duration": ["cash-flow", "yield", "duration", "convexity"],
    "stochastic-calculus-for-hedging": ["sde", "ito", "risk-neutral", "hedge"],
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit generated course scripts for product readiness.")
    parser.add_argument(
        "--course-dir",
        default=str(Path(__file__).resolve().parents[1] / "generated" / "course_scripts"),
    )
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    course_dir = Path(args.course_dir).resolve()
    report = {
        "course_dir": str(course_dir),
        "courses": [],
        "summary": {"passed": 0, "failed": 0},
    }

    for path in sorted(course_dir.glob("*.md")):
        if path.name.startswith("_"):
            continue
        audit = audit_course(path)
        report["courses"].append(audit)
        report["summary"]["passed" if audit["status"] == "pass" else "failed"] += 1

    output = Path(args.output).resolve() if args.output else course_dir / "_quality_report.json"
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report["summary"], ensure_ascii=False))
    print(f"[audit] {output}")


def audit_course(path: Path) -> dict:
    content = path.read_text(encoding="utf-8")
    slug = path.stem
    body = content.lower()
    modules = re.findall(r"^### Module\s+\d+\s+-\s+(.+)$", content, flags=re.MULTILINE)
    written_lessons = re.findall(r"^### Lecon\s+\d+\s+-\s+(.+)$", content, flags=re.MULTILINE)
    formulas = re.findall(r"^### F\d+\s+-\s+(.+)$", content, flags=re.MULTILINE)
    sources = re.findall(r"^- \[S\d+\]", content, flags=re.MULTILINE)
    source_count = int(re.search(r"^source_count:\s*(\d+)", content, flags=re.MULTILINE).group(1))
    expected = EXPECTED_KEYWORDS.get(slug, [])
    missing = [keyword for keyword in expected if keyword not in body]

    issues = []
    if len(modules) < 4:
        issues.append(f"only {len(modules)} modules")
    if len(written_lessons) < len(modules):
        issues.append(f"{len(written_lessons)} written lessons for {len(modules)} modules")
    if len(formulas) < 3:
        issues.append(f"only {len(formulas)} formulas")
    if len(sources) != source_count:
        issues.append(f"{len(sources)} source refs for source_count={source_count}")
    if missing:
        issues.append("missing expected keywords: " + ", ".join(missing))

    score = 100
    score -= max(0, 4 - len(modules)) * 15
    score -= max(0, len(modules) - len(written_lessons)) * 10
    score -= max(0, 3 - len(formulas)) * 15
    score -= abs(len(sources) - source_count) * 4
    score -= len(missing) * 10
    score = max(score, 0)

    return {
        "slug": slug,
        "status": "pass" if not issues else "fail",
        "quality_score": score,
        "module_count": len(modules),
        "written_lesson_count": len(written_lessons),
        "formula_count": len(formulas),
        "source_ref_count": len(sources),
        "source_count": source_count,
        "modules": modules,
        "issues": issues,
    }


if __name__ == "__main__":
    main()
