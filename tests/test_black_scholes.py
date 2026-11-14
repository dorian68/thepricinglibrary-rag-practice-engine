from __future__ import annotations

import hashlib
import json
import math
import subprocess
import sys
from pathlib import Path

import pytest

from pricinglibrary_rag.black_scholes import (
    BLACK_SCHOLES_CONTRACT,
    BLACK_SCHOLES_INPUT_SCHEMA,
    analyze_black_scholes,
    build_black_scholes_json,
    build_black_scholes_scenario_csv,
    build_black_scholes_sensitivity_csv,
    normalize_black_scholes_input,
)
from pricinglibrary_rag.agui import (
    black_scholes as agui_black_scholes,
    openai_tool_specs,
    tool_black_scholes,
    tool_compute_greeks,
    tool_greeks_sensitivity,
    tool_put_call_parity,
)


ROOT = Path(__file__).resolve().parents[3]
CONTRACT_PATH = ROOT / "fixtures" / "black_scholes_contract.json"


def request(**changes):
    data = {
        "schemaVersion": BLACK_SCHOLES_INPUT_SCHEMA,
        "quoteMode": "volatility",
        "optionType": "call",
        "spot": 100.0,
        "strike": 100.0,
        "maturityYears": 1.0,
        "dayCount": "ACT/365F",
        "riskFreeRate": 0.05,
        "dividendYield": 0.0,
        "volatility": 0.2,
        "marketPrice": None,
        "currency": "EUR",
        "position": "long",
        "quantity": 2.0,
        "multiplier": 100.0,
        "shocks": {"spotPct": 10.0, "volPoints": 5.0, "days": 30.0},
    }
    data.update(changes)
    return data


def test_contract_fixture_is_exact_authority():
    assert BLACK_SCHOLES_CONTRACT == json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))


def test_atm_price_greeks_parity_and_units():
    result = analyze_black_scholes(request())
    assert result["call"]["unitPrice"] == pytest.approx(10.4505754154, abs=2e-10)
    assert result["put"]["unitPrice"] == pytest.approx(5.5735178655, abs=2e-10)
    assert result["call"]["greeks"]["delta"] == pytest.approx(0.636830586, abs=2e-9)
    assert result["call"]["greeks"]["vega"] == pytest.approx(0.375240347, abs=2e-9)
    assert result["parity"]["holds"] is True
    assert abs(result["parity"]["residual"]) < 1e-12
    assert result["conventions"]["vega"].endswith("percentage_point")
    assert result["conventions"]["theta"].endswith("calendar_day_elapsed")


def test_dividend_parity_and_short_position_scaling():
    result = analyze_black_scholes(request(dividendYield=0.03, optionType="put", position="short", quantity=3.0, multiplier=10.0))
    assert result["parity"]["holds"] is True
    assert result["selected"]["portfolioValue"] == pytest.approx(-30 * result["put"]["unitPrice"])
    assert result["selected"]["portfolioGreeks"]["delta"] == pytest.approx(-30 * result["put"]["greeks"]["delta"])


def test_zero_volatility_is_discounted_deterministic_forward_limit():
    result = analyze_black_scholes(request(spot=120.0, volatility=0.0, riskFreeRate=0.05, dividendYield=0.02, quantity=1.0, multiplier=1.0))
    expected = max(120 * math.exp(-0.02) - 100 * math.exp(-0.05), 0.0)
    assert result["call"]["unitPrice"] == pytest.approx(expected, abs=1e-13)
    assert result["call"]["greeks"]["delta"] == pytest.approx(math.exp(-0.02))
    assert result["call"]["greeks"]["rho"] != 0
    assert result["call"]["limit"] == "zero_volatility"


def test_zero_volatility_forward_atm_uses_declared_symmetric_kink_convention():
    result = analyze_black_scholes(request(volatility=0.0, riskFreeRate=0.05, dividendYield=0.05, quantity=1.0, multiplier=1.0))
    discount = math.exp(-0.05)
    assert result["call"]["unitPrice"] == pytest.approx(0.0, abs=1e-13)
    assert result["put"]["unitPrice"] == pytest.approx(0.0, abs=1e-13)
    assert result["call"]["greeks"]["delta"] == pytest.approx(0.5 * discount)
    assert result["put"]["greeks"]["delta"] == pytest.approx(-0.5 * discount)
    assert result["call"]["greeks"]["rho"] == pytest.approx(0.5 * 100 * discount / 100)
    assert result["put"]["greeks"]["rho"] == pytest.approx(-0.5 * 100 * discount / 100)
    assert result["call"]["greeks"]["gamma"] == result["call"]["greeks"]["vega"] == 0.0
    assert "not_classically_differentiable" in result["conventions"]["zeroVolatilityKinkLimit"]


@pytest.mark.parametrize(
    ("spot", "call_delta", "put_delta"),
    [(120.0, 1.0, 0.0), (80.0, 0.0, -1.0), (100.0, 0.5, -0.5)],
)
def test_expiry_has_exact_intrinsic_and_documented_delta(spot, call_delta, put_delta):
    result = analyze_black_scholes(request(spot=spot, maturityYears=0.0, quantity=1.0, multiplier=1.0))
    assert result["call"]["unitPrice"] == max(spot - 100, 0)
    assert result["put"]["unitPrice"] == max(100 - spot, 0)
    assert result["call"]["greeks"]["delta"] == call_delta
    assert result["put"]["greeks"]["delta"] == put_delta


def test_implied_vol_round_trip_and_solver_evidence():
    priced = analyze_black_scholes(request(quantity=1.0, multiplier=1.0))
    inverted = analyze_black_scholes(request(
        quoteMode="market_price", volatility=None,
        marketPrice=priced["call"]["unitPrice"], quantity=1.0, multiplier=1.0,
    ))
    assert inverted["quote"]["impliedVolatility"] == pytest.approx(0.2, abs=2e-12)
    assert inverted["quote"]["solver"]["method"] == "bisection"
    assert inverted["quote"]["solver"]["converged"] is True
    assert abs(inverted["quote"]["solver"]["residual"]) <= 1e-12 * priced["call"]["unitPrice"]


def test_iv_rejects_arbitrage_and_unsupported_finite_solution():
    with pytest.raises(ValueError, match="no-arbitrage"):
        analyze_black_scholes(request(quoteMode="market_price", volatility=None, marketPrice=101.0))
    with pytest.raises(ValueError, match="supported maximum"):
        analyze_black_scholes(request(quoteMode="market_price", volatility=None, marketPrice=99.999999))
    with pytest.raises(ValueError, match="not identifiable"):
        analyze_black_scholes(request(quoteMode="market_price", volatility=None, marketPrice=0.0, maturityYears=0.0))


@pytest.mark.parametrize(
    "mutation",
    [
        lambda x: x.update(spot="100"),
        lambda x: x.update(spot=True),
        lambda x: x.update(spot=float("inf")),
        lambda x: x.update(currency="eur"),
        lambda x: x.update(extra=1),
        lambda x: x.update(volatility=None),
        lambda x: x.update(marketPrice=10.0),
        lambda x: x.update(shocks={"spotPct": 10.0, "volPoints": 5.0, "days": 30.0, "extra": 1}),
    ],
)
def test_strict_schema_and_exclusive_quote_fields(mutation):
    data = request()
    mutation(data)
    with pytest.raises(ValueError):
        normalize_black_scholes_input(data)


def test_scenarios_sensitivities_sha_and_exports_are_deterministic():
    first = analyze_black_scholes(request())
    second = analyze_black_scholes(dict(reversed(list(request().items()))))
    assert first["analysisId"] == second["analysisId"]
    assert len(first["analysisId"]) == 64
    assert [row["scenario"] for row in first["scenarios"]] == BLACK_SCHOLES_CONTRACT["scenarios"]
    assert all(len(first["sensitivities"][axis]) == 21 for axis in BLACK_SCHOLES_CONTRACT["sensitivities"])
    scenario_csv = build_black_scholes_scenario_csv(first)
    sensitivity_csv = build_black_scholes_sensitivity_csv(first)
    assert scenario_csv.endswith("\n") and "\r" not in scenario_csv
    assert sensitivity_csv.endswith("\n") and "\r" not in sensitivity_csv
    assert first["analysisId"] in scenario_csv and first["analysisId"] in sensitivity_csv
    assert hashlib.sha256(scenario_csv.encode()).hexdigest() == hashlib.sha256(build_black_scholes_scenario_csv(second).encode()).hexdigest()
    assert json.loads(build_black_scholes_json(first))["analysisId"] == first["analysisId"]


def test_cli_json_and_csv():
    command = [sys.executable, "-m", "pricinglibrary_rag.black_scholes"]
    payload = json.dumps(request())
    completed = subprocess.run(command, cwd=Path(__file__).parents[1], input=payload, capture_output=True, text=True, check=False)
    assert completed.returncode == 0, completed.stderr
    assert json.loads(completed.stdout)["schemaVersion"] == "tpl.black-scholes.analysis.v1"
    csv_run = subprocess.run(command + ["--format", "scenario-csv"], cwd=Path(__file__).parents[1], input=payload, capture_output=True, text=True, check=False)
    assert csv_run.returncode == 0, csv_run.stderr
    assert csv_run.stdout.startswith("schemaVersion,engineVersion,analysisId,scenario")
    contract_run = subprocess.run(
        [sys.executable, "-m", "pricinglibrary_rag.black_scholes", "--contract"],
        cwd=Path(__file__).parents[1], capture_output=True, text=True, check=False,
    )
    assert contract_run.returncode == 0, contract_run.stderr
    assert json.loads(contract_run.stdout) == BLACK_SCHOLES_CONTRACT


def test_agui_human_adapter_delegates_and_fails_closed():
    adapted = agui_black_scholes(100, 100, 5, 0, 20, 365)
    canonical = analyze_black_scholes(request(quantity=1.0, multiplier=1.0))
    assert adapted["call"] == canonical["call"]["unitPrice"]
    assert adapted["analysis_id"] == canonical["analysisId"]
    for tool in (tool_black_scholes, tool_compute_greeks, tool_put_call_parity):
        result, events = tool(None, {"S": "100"})
        assert "error" in result and events == []
        result, events = tool(None, {"S": 100, "unknown": 1})
        assert "unknown parameters" in result["error"] and events == []
    result, events = tool_greeks_sensitivity(None, {"greek": True, "param": "time"})
    assert "error" in result and events == []


def test_black_scholes_openai_schemas_are_closed():
    specs = {item["function"]["name"]: item["function"] for item in openai_tool_specs()}
    for name in ("compute_black_scholes", "compute_greeks", "compute_put_call_parity", "greeks_sensitivity"):
        assert specs[name]["parameters"]["additionalProperties"] is False
