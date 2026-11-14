from __future__ import annotations

import json
import math
import re
from pathlib import Path

import pytest

from pricinglibrary_rag.calculators import PracticeCalculator
from pricinglibrary_rag.yield_curve import (
    YieldCurveError,
    build_yield_curve,
    interpolate_log_discount_factor,
)


FIXTURE_PATH = Path(__file__).resolve().parents[3] / "fixtures" / "yield_curve_golden.json"
FIXTURE = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
CASES = {case["id"]: case for case in FIXTURE["cases"]}


def assert_close(actual: float, expected: float, tolerance: float) -> None:
    assert math.isfinite(actual)
    assert abs(actual - expected) <= tolerance


@pytest.mark.parametrize("case", FIXTURE["cases"], ids=lambda case: case["id"])
def test_python_curve_engine_matches_shared_js_golden_fixture(case: dict) -> None:
    result = build_yield_curve(case["instruments"], FIXTURE["conventions"])
    assert result["diagnostics"]["converged"] is True
    assert result["diagnostics"]["positiveDiscountFactors"] is True
    assert result["diagnostics"]["maxAbsPvResidual"] <= FIXTURE["tolerances"]["repricing"]
    assert result["diagnostics"]["maxAbsQuoteResidual"] <= FIXTURE["tolerances"]["repricing"]
    for actual, expected in zip(result["anchors"], case["expectedAnchors"], strict=True):
        assert_close(actual["time"], expected["time"], 1e-12)
        assert_close(
            actual["discountFactor"],
            expected["discountFactor"],
            FIXTURE["tolerances"]["discountFactor"],
        )
    assert result == build_yield_curve(case["instruments"], FIXTURE["conventions"])


def test_deposit_fra_and_future_conventions_match() -> None:
    fra = build_yield_curve(CASES["deposit_fra"]["instruments"])
    future = build_yield_curve(
        CASES["deposit_future_with_convexity"]["instruments"]
    )
    assert_close(fra["anchors"][0]["discountFactor"], 0.975609756097561, 1e-12)
    assert_close(fra["anchors"][1]["discountFactor"], 0.950655060752800, 1e-12)
    assert_close(future["inputs"][1]["quote"], 0.0525, 1e-15)
    assert_close(future["repricing"][1]["futurePriceResidual"], 0.0, 1e-10)
    assert [anchor["discountFactor"] for anchor in fra["anchors"]] == pytest.approx(
        [anchor["discountFactor"] for anchor in future["anchors"]], abs=1e-14
    )


def test_sparse_swaps_build_every_coupon_and_reprice() -> None:
    result = build_yield_curve(CASES["current_sparse_swaps"]["instruments"])
    expected = CASES["current_sparse_swaps"]
    for expected_node in expected["expectedInterpolatedNodes"]:
        actual = next(
            node for node in result["curve"] if node["time"] == expected_node["time"]
        )
        assert actual["source"] == "interpolated-cashflow"
        assert_close(
            actual["discountFactor"],
            expected_node["discountFactor"],
            FIXTURE["tolerances"]["discountFactor"],
        )
    df3 = next(node["discountFactor"] for node in result["curve"] if node["time"] == 3)
    df4 = next(node["discountFactor"] for node in result["curve"] if node["time"] == 4)
    df5 = next(node["discountFactor"] for node in result["curve"] if node["time"] == 5)
    assert_close(df4, math.sqrt(df3 * df5), FIXTURE["tolerances"]["interpolation"])
    assert result["diagnostics"]["interpolatedCouponCount"] == 5
    for expected_forward in expected["expectedSegmentContinuousForwards"]:
        start = expected_forward["start"]
        end = expected_forward["end"]
        start_df = 1.0 if start == 0 else next(
            node["discountFactor"] for node in result["curve"] if node["time"] == start
        )
        end_df = next(
            node["discountFactor"] for node in result["curve"] if node["time"] == end
        )
        forward = math.log(start_df / end_df) / (end - start)
        assert_close(forward, expected_forward["rate"], FIXTURE["tolerances"]["rate"])


def test_negative_and_inverted_curves_are_diagnostics_not_false_failures() -> None:
    negative = build_yield_curve(CASES["negative_rates"]["instruments"])
    assert negative["anchors"][0]["discountFactor"] > 1
    assert negative["diagnostics"]["negativeForwardIntervals"]
    inverted = build_yield_curve(
        [
            {"type": "swap", "maturity": maturity, "quote": quote}
            for maturity, quote in zip(
                [1, 2, 3, 5, 10], [0.05, 0.04, 0.03, 0.02, 0.01], strict=True
            )
        ]
    )
    assert inverted["diagnostics"]["converged"] is True
    assert inverted["diagnostics"]["negativeForwardIntervals"]


@pytest.mark.parametrize(
    ("instruments", "message"),
    [
        (
            [
                {"type": "deposit", "maturity": 0.5, "quote": float("nan")},
                {"type": "swap", "maturity": 1, "quote": 0.03},
            ],
            "non-finite",
        ),
        (
            [
                {"type": "deposit", "maturity": 0.5, "quote": 0.03},
                {"type": "swap", "maturity": 0.5, "quote": 0.03},
            ],
            "strictly increasing",
        ),
        (
            [
                {"type": "deposit", "maturity": 0.25, "quote": 0.03},
                {"type": "fra", "start": 0.5, "maturity": 1, "quote": 0.03},
            ],
            "not covered",
        ),
        (
            [
                {"type": "deposit", "maturity": 0.5, "quote": 0.03},
                {"type": "future", "start": 0.5, "maturity": 1, "futurePrice": 95},
            ],
            "explicit convexityAdjustment",
        ),
        (
            [
                {"type": "swap", "maturity": 1, "quote": 0.01},
                {"type": "swap", "maturity": 50, "quote": -0.25},
            ],
            "not bracketed",
        ),
    ],
)
def test_curve_engine_fails_closed_on_adversarial_inputs(
    instruments: list[dict], message: str
) -> None:
    with pytest.raises(YieldCurveError, match=message):
        build_yield_curve(instruments)


def test_curve_engine_rejects_extrapolation_and_implicit_stub() -> None:
    with pytest.raises(YieldCurveError, match="extrapolation"):
        interpolate_log_discount_factor(
            2,
            [
                {"time": 0, "discountFactor": 1},
                {"time": 1, "discountFactor": 0.95},
            ],
        )
    with pytest.raises(YieldCurveError, match="implicit stub"):
        build_yield_curve(
            [
                {"type": "deposit", "maturity": 0.5, "quote": 0.03},
                {"type": "swap", "maturity": 1.25, "quote": 0.03},
            ],
            {"fixedLegFrequency": 2},
        )


def test_practice_calculator_uses_sparse_curve_engine_and_interval_labels() -> None:
    pack = PracticeCalculator().build_pack(
        "Bootstrap de courbe, swaps par annuels: 1 an 3.00%, 2 ans 3.20%, "
        "3 ans 3.35%, 5 ans 3.55%, 10 ans 3.80%.",
        family_hint="yield_curve_bootstrap",
    )
    assert pack.family == "yield_curve_bootstrap"
    assert pack.steps
    df5_step = next(step for step in pack.steps if step.label.startswith("DF 5a"))
    df5 = float(re.search(r"DF=([\d.]+)", df5_step.result).group(1))
    assert_close(df5, 0.839305280384191, 1e-10)
    assert "residu PV=" in df5_step.result
    assert any(step.label == "Forward 3a->4a" for step in pack.steps)
    assert any(step.label == "Forward 4a->5a" for step in pack.steps)
    assert "taux forward 1 an" not in pack.as_markdown().lower()
    assert any("log-lineaire" in assumption for assumption in pack.assumptions)


def test_practice_calculator_surfaces_invalid_curve_instead_of_faking_results() -> None:
    pack = PracticeCalculator().build_pack(
        "Bootstrap de courbe, swaps par annuels: 1 an 3.00%, 1 an 3.20%, 3 ans 3.35%.",
        family_hint="yield_curve_bootstrap",
    )
    assert pack.family == "yield_curve_bootstrap"
    assert not pack.steps
    assert any("strictly increasing" in warning for warning in pack.warnings)
