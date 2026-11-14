from __future__ import annotations

import json
import math
from pathlib import Path

import pytest

from pricinglibrary_rag.binomial import (
    BINOMIAL_CONTRACT,
    analyze_binomial,
    build_binomial_convergence_csv,
    build_binomial_frontier_csv,
    normalize_binomial_input,
)
from pricinglibrary_rag.agui import binomial_tree


ROOT = Path(__file__).resolve().parents[3]


def base(**overrides):
    value = {
        "schemaVersion": "tpl.binomial.input.v1",
        "spot": 100,
        "strike": 100,
        "volatility": 0.2,
        "maturityYears": 1,
        "dayCount": "ACT/365F",
        "riskFreeRate": 0.05,
        "dividendYield": 0,
        "steps": 400,
        "optionType": "call",
        "exerciseStyle": "european",
        "currency": "USD",
        "quantity": 2,
        "contractMultiplier": 100,
        "position": "long",
    }
    value.update(overrides)
    return value


def test_runtime_contract_matches_json_authority():
    assert BINOMIAL_CONTRACT == json.loads((ROOT / "fixtures/binomial_contract.json").read_text(encoding="utf-8"))


def test_european_call_converges_to_black_scholes_and_has_sensible_greeks():
    result = analyze_binomial(base(steps=1000))
    assert result["valuation"]["pricePerUnit"] == pytest.approx(10.4506, abs=0.003)
    assert result["valuation"]["benchmarkAbsoluteError"] < 0.003
    assert result["greeks"]["perUnit"]["delta"] == pytest.approx(0.6368, abs=0.002)
    assert result["greeks"]["perUnit"]["gamma"] == pytest.approx(0.01876, abs=0.001)
    assert result["greeks"]["perUnit"]["vega"] == pytest.approx(0.3752, abs=0.003)
    assert result["valuation"]["positionValue"] == pytest.approx(result["valuation"]["pricePerUnit"] * 200)


def test_european_put_call_parity_with_dividend():
    call = analyze_binomial(base(dividendYield=0.02, steps=800))["valuation"]["pricePerUnit"]
    put = analyze_binomial(base(dividendYield=0.02, steps=800, optionType="put"))["valuation"]["pricePerUnit"]
    target = 100 * math.exp(-0.02) - 100 * math.exp(-0.05)
    assert call - put == pytest.approx(target, abs=1e-10)


def test_american_put_has_positive_premium_and_frontier():
    result = analyze_binomial(base(optionType="put", exerciseStyle="american", steps=300))
    assert result["valuation"]["pricePerUnit"] >= result["valuation"]["europeanPricePerUnit"]
    assert result["valuation"]["earlyExercisePremiumPerUnit"] > 0
    assert result["earlyExercise"]["exercisedNodeCount"] > 0
    assert result["earlyExercise"]["boundary"]
    assert all(row["boundarySpot"] > 0 for row in result["earlyExercise"]["boundary"])


def test_non_dividend_american_call_has_no_early_exercise():
    result = analyze_binomial(base(exerciseStyle="american", dividendYield=0, steps=300))
    assert result["valuation"]["pricePerUnit"] == result["valuation"]["europeanPricePerUnit"]
    assert result["valuation"]["earlyExercisePremiumPerUnit"] == 0
    assert result["earlyExercise"]["exercisedNodeCount"] == 0


def test_high_dividend_american_call_exercises():
    result = analyze_binomial(base(spot=100, strike=90, riskFreeRate=0.01, dividendYield=0.12, exerciseStyle="american", steps=300))
    assert result["valuation"]["earlyExercisePremiumPerUnit"] > 3
    assert result["earlyExercise"]["exercisedNodeCount"] > 0


def test_zero_volatility_and_expiry_are_exact_and_finite():
    zero = analyze_binomial(base(volatility=0, optionType="put", exerciseStyle="american"))
    expired = analyze_binomial(base(spot=90, maturityYears=0, optionType="put", exerciseStyle="american"))
    assert zero["valuation"]["pricePerUnit"] == 0
    assert expired["valuation"]["pricePerUnit"] == 10
    assert expired["model"]["riskNeutralUpProbability"] is None
    assert {row["code"] for row in expired["diagnostics"]} >= {"AT_EXPIRY_INTRINSIC"}


def test_greeks_stay_inside_declared_spot_volatility_and_rate_bounds():
    upper = analyze_binomial(base(spot=1_000_000_000_000, strike=1_000_000_000_000, volatility=5, riskFreeRate=1, steps=200))
    lower_spot = analyze_binomial(base(spot=1e-8, strike=1e-8, volatility=0, riskFreeRate=0, steps=10))
    assert all(math.isfinite(value) for value in upper["greeks"]["perUnit"].values())
    assert all(math.isfinite(value) for value in lower_spot["greeks"]["perUnit"].values())


def test_rho_uses_an_admissible_one_sided_bump_near_probability_boundary():
    result = analyze_binomial(base(riskFreeRate=0.2828, volatility=0.2, steps=2))
    assert 0 <= result["model"]["riskNeutralUpProbability"] <= 1
    assert math.isfinite(result["greeks"]["perUnit"]["rho"])


def test_negative_rate_non_dividend_call_has_no_false_no_exercise_diagnostic():
    result = analyze_binomial(base(riskFreeRate=-0.1, exerciseStyle="american", steps=300))
    assert result["earlyExercise"]["exercisedNodeCount"] > 0
    assert result["valuation"]["earlyExercisePremiumPerUnit"] > 0
    assert "NON_DIVIDEND_CALL_CHECK" not in {row["code"] for row in result["diagnostics"]}


def test_no_arbitrage_probability_fails_closed_without_clamping():
    with pytest.raises(ValueError, match=r"outside \[0,1\]"):
        analyze_binomial(base(volatility=0.01, riskFreeRate=0.15, steps=5))


@pytest.mark.parametrize(
    "change",
    [
        {"steps": 3.5}, {"steps": "400"}, {"spot": "100"}, {"spot": float("inf")},
        {"volatility": -0.1}, {"maturityYears": -1}, {"currency": "usd"},
        {"exerciseStyle": "bermudan"}, {"position": "flat"}, {"quantity": True},
    ],
)
def test_invalid_inputs_fail_closed(change):
    with pytest.raises(ValueError):
        analyze_binomial(base(**change))


def test_unknown_and_missing_fields_fail_closed():
    unknown = base(fake=True)
    missing = base()
    del missing["strike"]
    with pytest.raises(ValueError, match="unknown=fake"):
        normalize_binomial_input(unknown)
    with pytest.raises(ValueError, match="missing=strike"):
        normalize_binomial_input(missing)


def test_repeatability_analysis_id_and_exports():
    first = analyze_binomial(base(optionType="put", exerciseStyle="american", steps=200))
    second = analyze_binomial(base(optionType="put", exerciseStyle="american", steps=200))
    assert first == second
    assert len(first["analysisId"]) == 64
    convergence = build_binomial_convergence_csv(first)
    frontier = build_binomial_frontier_csv(first)
    assert convergence.endswith("\n") and "\r" not in convergence
    assert frontier.endswith("\n") and "\r" not in frontier
    assert first["analysisId"] in convergence and first["analysisId"] in frontier


def test_tree_nodes_expose_continuation_and_decision():
    result = analyze_binomial(base(optionType="put", exerciseStyle="american", steps=50))
    assert result["tree"]["displayDepth"] == 6
    assert any(node["continuation"] is not None for node in result["tree"]["nodes"])
    assert all(set(node) == {"step", "upMoves", "spot", "intrinsic", "continuation", "value", "exercise"} for node in result["tree"]["nodes"])


def test_agui_adapter_preserves_requested_steps_and_canonical_price():
    adapted = binomial_tree(100, 100, 5, 20, 365, 200, "call", False, 0)
    canonical = analyze_binomial(base(quantity=1, contractMultiplier=1, currency="EUR", steps=200))
    assert adapted["steps"] == 200
    assert adapted["price"] == round(canonical["valuation"]["pricePerUnit"], 4)
    assert adapted["analysis_id"] == canonical["analysisId"]
    assert len(adapted["nodes"]) == 7


@pytest.mark.parametrize("change", [{"steps": "200"}, {"steps": 3.5}, {"american": "false"}, {"sigma": "20"}])
def test_agui_adapter_rejects_coercion(change):
    args = {"S": 100, "K": 100, "r": 5, "sigma": 20, "T_days": 365, "steps": 200, "kind": "call", "american": False, "q": 0}
    args.update(change)
    with pytest.raises(ValueError):
        binomial_tree(**args)
