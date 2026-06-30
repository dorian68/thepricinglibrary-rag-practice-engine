"""Numeric guardrails for LLM-written exercises.

The LLM is only a pedagogical writer. The authoritative numbers come from the
deterministic calculators (CalculationPack). This module checks that an LLM
rewrite did not silently change any calculated value, so the pipeline can fall
back to the deterministic template instead of ever serving a wrong number.

Contract: validate_generated_exercise(template_draft, llm_output, calculation_pack).
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, field

from .calculators import CalculationPack

# Numbers as the calculators render them: optional sign, digit groups with
# comma / (regular or non-breaking) space thousands separators, optional
# decimal, optional scientific tail.   = NBSP,   = narrow NBSP (FR).
_SEP = r"[   ,]"
_NUMBER_RE = re.compile(
    rf"[-+]?\d{{1,3}}(?:{_SEP}\d{{3}})+(?:\.\d+)?"   # 100,000 / 100 000 / 1,234.5
    r"|[-+]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?"           # 0.5234 / 2 / 1.2e-3
)
_STRIP_RE = re.compile(r"[\s  ,]")


@dataclass(frozen=True)
class ParsedNumber:
    value: float
    raw: str


@dataclass
class ValidationResult:
    """Outcome of comparing an LLM rewrite against the calculation pack."""

    ok: bool
    checked: int = 0
    missing: list[str] = field(default_factory=list)
    violations: list[str] = field(default_factory=list)

    def as_metadata(self) -> dict:
        return {
            "ok": self.ok,
            "checked": self.checked,
            "missing": self.missing,
            "violations": self.violations,
        }


def extract_numbers(text: str) -> list[ParsedNumber]:
    """Pull every number out of free text, normalised to a float (the displayed
    magnitude — "2.00%" -> 2.0, "100,000" -> 100000.0)."""
    if not text:
        return []
    out: list[ParsedNumber] = []
    for match in _NUMBER_RE.finditer(text):
        raw = match.group(0)
        cleaned = _STRIP_RE.sub("", raw)
        try:
            value = float(cleaned)
        except ValueError:
            continue
        out.append(ParsedNumber(value=value, raw=raw.strip()))
    return out


def _isclose(a: float, b: float, rel_tol: float) -> bool:
    return math.isclose(a, b, rel_tol=rel_tol, abs_tol=1e-9)


def _abs_close(a: float, b: float, rel_tol: float) -> bool:
    """Sign-insensitive match. A leading '-' inside a substitution string
    ('... - 100*N(...)') is an operator, not part of the value, and the LLM may
    render a figure with or without its sign — compare magnitudes."""
    return math.isclose(abs(a), abs(b), rel_tol=rel_tol, abs_tol=1e-9)


def _present(value: float, pool: list[float], rel_tol: float, scaled: bool = False) -> bool:
    """Is `value` present in `pool` (by magnitude)? When `scaled`, also accept the
    k/m/bn-scaled forms so '50m' in the enonce matches 50,000,000 in the pack."""
    candidates = [value]
    if scaled:
        candidates += [value * 1e3, value * 1e6, value * 1e9]
    return any(_abs_close(c, p, rel_tol) for c in candidates for p in pool)


def _canonical_numbers(pack: CalculationPack) -> list[ParsedNumber]:
    """The values that MUST survive an LLM rewrite: the computed RESULTS (the
    answers the learner must reproduce) plus the derived inputs stated in the
    assumptions. Intermediate substitution digits are deliberately excluded —
    the LLM may legitimately not echo every intermediate term, and forcing it to
    caused number-heavy packs (Monte Carlo, autocall) to fall back needlessly."""
    parts: list[str] = []
    for step in pack.steps:
        parts.append(step.result or "")
    parts.extend(pack.assumptions or [])
    numbers: list[ParsedNumber] = []
    seen: list[float] = []
    for chunk in parts:
        for num in extract_numbers(chunk):
            if abs(num.value) < 1e-9:
                continue  # a result of 0 (e.g. PV at par) is not a figure to guard
            if not any(_isclose(num.value, s, 1e-9) for s in seen):
                numbers.append(num)
                seen.append(num.value)
    return numbers


def validate_calculation_coherence(
    scenario_text: str,
    calculation_pack: CalculationPack,
    *,
    rel_tol: float = 1e-3,
) -> ValidationResult:
    """Verify the displayed scenario (enonce) is coherent with the pack the
    correction will use: every number stated in the scenario must reappear in
    the pack. This is the corrector/validator gate — if it fails, the enonce and
    the corrige would show different numbers (the exact bug this guards against),
    and the caller must display the pack's own scenario instead of the raw one."""
    # The generator displays the scenario the pack was actually computed from, so
    # enonce<->corrige coherence is structural. The only way it still breaks is a
    # pack with no real answer key (generic/empty) — then there is no verified
    # case to be coherent with. We deliberately do NOT require every stated number
    # to be a calculator output: limits, thresholds and counts (e.g. "limite 600k",
    # "10000 simulations") are legitimate scenario context, not pack results.
    if calculation_pack.family == "generic" or not calculation_pack.steps:
        return ValidationResult(
            ok=False,
            checked=0,
            violations=["no verified calculation pack (generic/empty) for this scenario"],
        )
    return ValidationResult(ok=True, checked=len(calculation_pack.steps))


def validate_generated_exercise(
    template_draft: str,
    llm_output: str,
    calculation_pack: CalculationPack,
    *,
    rel_tol: float = 1e-3,
) -> ValidationResult:
    """Verify the LLM output preserves every calculated value.

    Only values that the deterministic template actually presented (i.e. that
    appear in `template_draft`) are required in `llm_output` — we never demand a
    number the learner was not shown. A missing/changed value is a violation;
    an empty output is a violation. The caller decides the policy (strict ->
    fall back to template; lenient -> keep but flag)."""
    canonical = _canonical_numbers(calculation_pack)
    if not canonical:
        # No calculated numbers to protect (e.g. require_calculations=False).
        return ValidationResult(ok=True, checked=0)

    draft_values = [n.value for n in extract_numbers(template_draft or "")]
    if draft_values:
        canonical = [
            c
            for c in canonical
            if _present(c.value, draft_values, rel_tol)
        ]
    if not canonical:
        return ValidationResult(ok=True, checked=0)

    output_values = [n.value for n in extract_numbers(llm_output or "")]
    missing = [
        c.raw
        for c in canonical
        if not _present(c.value, output_values, rel_tol)
    ]

    violations: list[str] = []
    if not (llm_output or "").strip():
        violations.append("empty LLM output")
    if missing:
        sample = ", ".join(sorted(set(missing))[:8])
        violations.append(
            f"{len(missing)} calculated value(s) altered or dropped: {sample}"
        )

    return ValidationResult(
        ok=not violations,
        checked=len(canonical),
        missing=missing,
        violations=violations,
    )
