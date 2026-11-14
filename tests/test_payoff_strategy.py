from __future__ import annotations

import hashlib
import json
import math
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

import pytest

from pricinglibrary_rag.payoff_strategy import (
    PAYOFF_STRATEGY_CURVE_CSV_SCHEMA,
    PAYOFF_STRATEGY_SCENARIO_CSV_SCHEMA,
    analyze_payoff_strategy,
    black_scholes_leg,
    build_payoff_curve_csv,
    build_payoff_json,
    build_payoff_scenario_csv,
    payoff_strategy_contract_snapshot,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
CONTRACT_PATH = REPOSITORY_ROOT / "fixtures" / "payoff_strategy_contract.json"
GOLDEN_PATH = REPOSITORY_ROOT / "fixtures" / "payoff_strategy_golden.json"

MARKET = {
    "spot": 100,
    "volatility": 0.2,
    "timeToMaturity": 1,
    "riskFreeRate": 0,
    "dividendYield": 0,
    "currency": "USD",
    "contractMultiplier": 100,
    "gridPoints": 401,
}


def leg(
    identifier: str,
    option_type: str,
    side: str,
    strike: float,
    quantity: int = 1,
    manual_premium: float | None = None,
) -> dict:
    return {
        "id": identifier,
        "type": option_type,
        "side": side,
        "strike": strike,
        "quantity": quantity,
        "premiumSource": "model" if manual_premium is None else "manual",
        "manualPremium": manual_premium,
    }


def analyze(legs: list[dict], **overrides) -> dict:
    return analyze_payoff_strategy({**MARKET, **overrides, "legs": legs})


def test_runtime_snapshot_equals_canonical_contract() -> None:
    assert payoff_strategy_contract_snapshot() == json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))


def test_shared_strategy_golden_fixture() -> None:
    fixture = json.loads(GOLDEN_PATH.read_text(encoding="utf-8"))
    assert fixture["schemaVersion"] == "tpl.payoff-strategy.golden.v1"
    assert len(fixture["cases"]) == 7
    for case in fixture["cases"]:
        result = analyze_payoff_strategy({**fixture["market"], **case["overrides"], "legs": case["legs"]})
        assert result["breakevens"] == case["expected"]["breakevens"], case["id"]
        assert result["bounds"] == case["expected"]["bounds"], case["id"]
        assert result["summary"]["netEntryPremium"] == pytest.approx(case["expected"]["netEntryPremium"], abs=1e-12)
        if "analysisId" in case["expected"]:
            assert result["analysisId"] == case["expected"]["analysisId"]


def test_black_scholes_golden_parity_and_every_short_greek_is_signed() -> None:
    call = black_scholes_leg({**MARKET, "strike": 100, "type": "call"})
    put = black_scholes_leg({**MARKET, "strike": 100, "type": "put"})
    assert call["price"] == pytest.approx(7.965578879433949, abs=1e-12)
    assert call["price"] - put["price"] == pytest.approx(0, abs=1e-12)

    long_model = analyze([leg("call", "call", "long", 100)])
    short_model = analyze([leg("call", "call", "short", 100)])
    for greek in ("delta", "gamma", "vega", "theta", "rho"):
        assert short_model["greeks"][greek] == pytest.approx(-long_model["greeks"][greek], abs=1e-12)
    assert long_model["summary"]["netEntryPremium"] == pytest.approx(call["price"] * 100, abs=1e-10)
    assert long_model["summary"]["inceptionModelPnl"] == pytest.approx(0, abs=1e-12)


def test_analytical_tails_and_break_evens_outside_legacy_window() -> None:
    long_call = analyze([leg("call", "call", "long", 200, 1, 5)], contractMultiplier=1)
    assert long_call["bounds"] == {
        "maxProfit": {"kind": "unlimited", "amount": None},
        "maxLoss": {"kind": "finite", "amount": 5},
    }
    assert long_call["breakevens"] == [205]

    short_call = analyze([leg("call", "call", "short", 100, 1, 5)], contractMultiplier=1)
    assert short_call["bounds"] == {
        "maxProfit": {"kind": "finite", "amount": 5},
        "maxLoss": {"kind": "unlimited", "amount": None},
    }

    long_put = analyze([leg("put", "put", "long", 200, 1, 5)], contractMultiplier=1)
    assert long_put["bounds"] == {
        "maxProfit": {"kind": "finite", "amount": 195},
        "maxLoss": {"kind": "finite", "amount": 5},
    }
    assert long_put["breakevens"] == [195]
    assert any(point["terminalSpot"] == 195 for point in long_put["curve"])


@pytest.mark.parametrize(
    ("legs", "breakevens", "bounds"),
    [
        (
            [leg("lower", "call", "long", 100, 1, 6), leg("upper", "call", "short", 110, 1, 2.5)],
            [103.5],
            {"maxProfit": {"kind": "finite", "amount": 650}, "maxLoss": {"kind": "finite", "amount": 350}},
        ),
        (
            [leg("call", "call", "long", 100, 1, 5), leg("put", "put", "long", 100, 1, 5)],
            [90, 110],
            {"maxProfit": {"kind": "unlimited", "amount": None}, "maxLoss": {"kind": "finite", "amount": 1000}},
        ),
        (
            [
                leg("c95", "call", "long", 95, 1, 7),
                leg("c100", "call", "short", 100, 2, 4),
                leg("c105", "call", "long", 105, 1, 2),
            ],
            [96, 104],
            {"maxProfit": {"kind": "finite", "amount": 400}, "maxLoss": {"kind": "finite", "amount": 100}},
        ),
        (
            [
                leg("p85", "put", "long", 85, 1, 1),
                leg("p95", "put", "short", 95, 1, 2.5),
                leg("c105", "call", "short", 105, 1, 2.5),
                leg("c115", "call", "long", 115, 1, 1),
            ],
            [92, 108],
            {"maxProfit": {"kind": "finite", "amount": 300}, "maxLoss": {"kind": "finite", "amount": 700}},
        ),
    ],
    ids=("bull-spread-x100", "straddle", "butterfly", "iron-condor"),
)
def test_strategy_goldens(legs: list[dict], breakevens: list[float], bounds: dict) -> None:
    result = analyze(legs)
    assert result["breakevens"] == breakevens
    assert result["bounds"] == bounds
    assert {0, MARKET["spot"], *breakevens, *(item["strike"] for item in legs)} <= {
        point["terminalSpot"] for point in result["curve"]
    }


def test_gross_payoff_pnl_multiplier_summary_and_leg_contributions() -> None:
    bull = analyze(
        [leg("lower", "call", "long", 100, 1, 6), leg("upper", "call", "short", 110, 1, 2.5)]
    )
    assert bull["summary"]["netEntryPremium"] == pytest.approx(350, abs=1e-12)
    assert bull["summary"]["entryCashflow"] == pytest.approx(-350, abs=1e-12)
    scenario = next(point for point in bull["scenarios"] if point["terminalSpot"] == 110)
    assert scenario["grossPayoff"] == 1000
    assert scenario["terminalPnl"] == 650
    assert scenario["legContributions"] == [
        {"id": "lower", "grossPayoff": 1000, "terminalPnl": 400},
        {"id": "upper", "grossPayoff": 0, "terminalPnl": 250.0},
    ]


def test_zero_intervals_are_explicit_and_not_fabricated_as_single_roots() -> None:
    offset = analyze(
        [leg("long", "call", "long", 100, 1, 5), leg("short", "call", "short", 100, 1, 5)],
        contractMultiplier=1,
    )
    assert offset["zeroIntervals"] == [
        {"lowerSpot": 0, "upperSpot": 100},
        {"lowerSpot": 100, "upperSpot": None},
    ]
    assert offset["breakevens"] == []
    assert offset["bounds"] == {
        "maxProfit": {"kind": "finite", "amount": 0},
        "maxLoss": {"kind": "finite", "amount": 0},
    }


def test_deterministic_hash_result_and_versioned_exports() -> None:
    legs = [leg("lower", "call", "long", 100, 1, 6), leg("upper", "call", "short", 110, 1, 2.5)]
    first = analyze(legs)
    second = analyze(deepcopy(legs))
    assert first == second
    # Golden fingerprints produced independently by the canonical JS engine.
    assert first["analysisId"] == "009ec55254f314a17faf2498e45ab16310342504c22116958e45ef278bd25e44"
    assert len(first["analysisId"]) == 64
    assert all(character in "0123456789abcdef" for character in first["analysisId"])
    assert json.loads(build_payoff_json(first))["analysisId"] == first["analysisId"]
    curve_csv = build_payoff_curve_csv(first)
    scenario_csv = build_payoff_scenario_csv(first)
    assert curve_csv.startswith(
        "schemaVersion,engineVersion,analysisId,terminalSpot,grossPayoff,terminalPnl\n"
        f"{PAYOFF_STRATEGY_CURVE_CSV_SCHEMA},"
    )
    assert scenario_csv.startswith(
        "schemaVersion,engineVersion,analysisId,terminalSpot,grossPayoff,terminalPnl,legContributions\n"
        f"{PAYOFF_STRATEGY_SCENARIO_CSV_SCHEMA},"
    )
    assert curve_csv == build_payoff_curve_csv(first)
    assert scenario_csv == build_payoff_scenario_csv(first)
    assert hashlib.sha256(curve_csv.encode("utf-8")).hexdigest() == "89f093dfe07175764e846fd5b7e7825853bdeed75cb9c4227ad06bf84b57b7ca"
    assert hashlib.sha256(scenario_csv.encode("utf-8")).hexdigest() == "a978744d940887304501daef93b53b0ebc802535ca4f851ad13a1f7fe3aee2f6"
    assert "NaN" not in build_payoff_json(first)
    assert "Infinity" not in build_payoff_json(first)


def test_strict_schema_domain_and_enum_adversaries_fail_closed() -> None:
    valid = {**MARKET, "legs": [leg("x", "call", "long", 100, 1, 5)]}
    candidates = [
        {**valid, "extra": True},
        {**valid, "spot": math.nan},
        {**valid, "spot": 5e-324},
        {**valid, "volatility": 5e-324},
        {**valid, "timeToMaturity": 5e-324},
        {**valid, "contractMultiplier": 5e-324},
        {**valid, "contractMultiplier": 0},
        {**valid, "gridPoints": 100},
        {**valid, "legs": []},
        {**valid, "currency": "usd"},
        {**valid, "legs": [{**valid["legs"][0], "strike": -1}]},
        {**valid, "legs": [{**valid["legs"][0], "quantity": 1.5}]},
        {**valid, "legs": [valid["legs"][0], deepcopy(valid["legs"][0])]},
        {**valid, "legs": [{**valid["legs"][0], "type": "digital"}]},
        {**valid, "legs": [{**valid["legs"][0], "side": "flat"}]},
        {**valid, "legs": [{**valid["legs"][0], "premiumSource": "model", "manualPremium": 5}]},
        {**valid, "legs": [{**valid["legs"][0], "premiumSource": "manual", "manualPremium": None}]},
        {**valid, "legs": [{**valid["legs"][0], "manualPremium": -1}]},
        {**valid, "legs": [{**valid["legs"][0], "unknown": 1}]},
    ]
    for candidate in candidates:
        with pytest.raises(ValueError):
            analyze_payoff_strategy(candidate)


def test_non_finite_result_tree_is_rejected_before_json_export() -> None:
    result = analyze([leg("x", "call", "long", 100, 1, 5)])
    result["greeks"]["gamma"] = math.inf
    with pytest.raises(ValueError, match="non-finite"):
        build_payoff_json(result)


def test_cli_contract_analysis_and_fail_closed_error(tmp_path: Path) -> None:
    input_path = tmp_path / "strategy.json"
    input_path.write_text(
        json.dumps({**MARKET, "legs": [leg("call", "call", "long", 100, 1, 5)]}),
        encoding="utf-8",
    )
    contract = subprocess.run(
        [sys.executable, "-m", "pricinglibrary_rag.payoff_strategy", "--contract"],
        cwd=Path(__file__).resolve().parents[1],
        capture_output=True,
        text=True,
        check=True,
    )
    assert json.loads(contract.stdout) == payoff_strategy_contract_snapshot()
    analysis = subprocess.run(
        [sys.executable, "-m", "pricinglibrary_rag.payoff_strategy", "--input", str(input_path)],
        cwd=Path(__file__).resolve().parents[1],
        capture_output=True,
        text=True,
        check=True,
    )
    assert json.loads(analysis.stdout)["schemaVersion"] == "tpl.payoff-strategy.analysis.v1"
    input_path.write_text("{}", encoding="utf-8")
    rejected = subprocess.run(
        [sys.executable, "-m", "pricinglibrary_rag.payoff_strategy", "--input", str(input_path)],
        cwd=Path(__file__).resolve().parents[1],
        capture_output=True,
        text=True,
        check=False,
    )
    assert rejected.returncode == 2
    assert "schema is invalid" in rejected.stderr

    input_path.write_bytes(b" " * (payoff_strategy_contract_snapshot()["limits"]["maxInputBytes"] + 1))
    oversized = subprocess.run(
        [sys.executable, "-m", "pricinglibrary_rag.payoff_strategy", "--input", str(input_path)],
        cwd=Path(__file__).resolve().parents[1],
        capture_output=True,
        text=True,
        check=False,
    )
    assert oversized.returncode == 2
    assert "input exceeds" in oversized.stderr
