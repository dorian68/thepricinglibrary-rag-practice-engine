from __future__ import annotations

import copy
import json
import math
from pathlib import Path

import pytest

from pricinglibrary_rag.vol_surface import (
    ENGINE_VERSION, INPUT_SCHEMA, SCHEMA_VERSION, POINTS_CSV_SCHEMA,
    DIAGNOSTICS_CSV_SCHEMA, INPUT_KEYS, QUOTE_KEYS, SOURCE_KINDS, LIMITS,
    CONVENTIONS, LIMITATIONS, POINTS_HEADERS, DIAGNOSTICS_HEADERS, analyze_vol_surface,
    build_deterministic_vol_surface, build_vol_surface_diagnostics_csv,
    build_vol_surface_points_csv, normalize_vol_surface_input,
)
from pricinglibrary_rag.agui import TOOL_EXECUTORS, openai_tool_specs, vol_surface_analysis


def payload(variant: str = "clean") -> dict:
    return {"schemaVersion": INPUT_SCHEMA, "surfaceName": f"SPX {variant}", "asOfDate": "2026-07-19", "sourceKind": "deterministic_fixture", "interpolationMode": "total_variance_bilinear", "selectedMaturity": 0.75, "selectedLogMoneyness": 0.075, "quotes": build_deterministic_vol_surface(variant)}


def test_contract_fixture_matches_runtime():
    contract = json.loads((Path(__file__).parents[3] / "fixtures" / "vol_surface_contract.json").read_text(encoding="utf-8"))
    assert contract["engineVersion"] == ENGINE_VERSION
    assert contract["inputSchemaVersion"] == INPUT_SCHEMA
    assert contract["analysisSchemaVersion"] == SCHEMA_VERSION
    assert contract["pointsCsvSchemaVersion"] == POINTS_CSV_SCHEMA
    assert contract["diagnosticsCsvSchemaVersion"] == DIAGNOSTICS_CSV_SCHEMA
    assert contract["interpolationMode"] == "total_variance_bilinear"
    assert contract["inputKeys"] == INPUT_KEYS
    assert contract["quoteKeys"] == QUOTE_KEYS
    assert contract["sourceKinds"] == SOURCE_KINDS
    assert contract["limits"] == LIMITS
    assert contract["conventions"] == CONVENTIONS
    assert contract["limitations"] == LIMITATIONS
    assert contract["pointsCsvHeaders"] == POINTS_HEADERS
    assert contract["diagnosticsCsvHeaders"] == DIAGNOSTICS_HEADERS


def test_clean_surface_golden_metrics():
    result = analyze_vol_surface(payload())
    assert result["quality"]["status"] == "PASS"
    assert result["quality"]["quoteCount"] == 20
    assert result["slices"][1]["skew"] == pytest.approx(-0.06, abs=1e-12)
    assert result["slices"][1]["curvature"] == pytest.approx(0.2, abs=1e-12)
    assert result["slices"][0]["atmTotalVariance"] == pytest.approx(result["slices"][0]["atmVolatility"] ** 2 * 0.25)


def test_total_variance_bilinear_interpolation():
    result = analyze_vol_surface(payload())
    low = (result["slices"][1]["points"][2]["totalVariance"] + result["slices"][1]["points"][3]["totalVariance"]) / 2
    high = (result["slices"][2]["points"][2]["totalVariance"] + result["slices"][2]["points"][3]["totalVariance"]) / 2
    expected = (low + high) / 2
    assert result["selectedPoint"]["totalVariance"] == pytest.approx(expected)
    assert result["selectedPoint"]["impliedVolatility"] == pytest.approx(math.sqrt(expected / 0.75))
    assert result["selectedPoint"]["maturityBracket"] == [0.5, 1.0]
    assert result["selectedPoint"]["logMoneynessBracket"] == [0.0, 0.15]


def test_exact_node_and_boundary_interpolation():
    exact = payload(); exact["selectedMaturity"] = 1; exact["selectedLogMoneyness"] = 0
    result = analyze_vol_surface(exact)
    assert result["selectedPoint"]["impliedVolatility"] == pytest.approx(result["slices"][2]["atmVolatility"])
    boundary = payload(); boundary["selectedMaturity"] = 0.25; boundary["selectedLogMoneyness"] = -0.3
    result = analyze_vol_surface(boundary)
    assert result["selectedPoint"]["totalVariance"] == pytest.approx(result["points"][0]["totalVariance"])


def test_calendar_violation_is_retained_not_repaired():
    original = payload("calendar")
    result = analyze_vol_surface(original)
    assert result["quality"]["status"] == "POTENTIAL_ARBITRAGE"
    assert sum(row["code"] == "CALENDAR_VARIANCE_VIOLATION" for row in result["diagnostics"]) == 5
    assert result["input"]["quotes"] == original["quotes"]


def test_butterfly_and_vertical_violations():
    result = analyze_vol_surface(payload("butterfly"))
    codes = {row["code"] for row in result["diagnostics"]}
    assert "BUTTERFLY_CONVEXITY_VIOLATION" in codes
    assert "VERTICAL_SPREAD_VIOLATION" in codes


def test_hash_and_exports_are_deterministic():
    first, second = analyze_vol_surface(payload()), analyze_vol_surface(payload())
    assert first["analysisId"] == second["analysisId"]
    points = build_vol_surface_points_csv(first)
    diagnostics = build_vol_surface_diagnostics_csv(first)
    assert points == build_vol_surface_points_csv(second)
    assert diagnostics == build_vol_surface_diagnostics_csv(second)
    assert points.endswith("\n") and "\r" not in points
    assert diagnostics.endswith("\n") and first["analysisId"] in diagnostics
    assert len(points.splitlines()) == 21


def test_bid_ask_coverage_and_wide_warning():
    data = payload(); data["quotes"][0]["bidVolatility"] = 0.1; data["quotes"][0]["askVolatility"] = 0.3
    result = analyze_vol_surface(data)
    assert result["quality"]["bidAskCoverage"] == 1
    assert any(row["code"] == "WIDE_BID_ASK" for row in result["diagnostics"])
    no_spread = payload()
    for row in no_spread["quotes"]: row["bidVolatility"] = row["askVolatility"] = None
    assert analyze_vol_surface(no_spread)["quality"]["bidAskCoverage"] == 0


@pytest.mark.parametrize(
    "mutator, pattern",
    [
        (lambda p: p.update(extra=True), "unknown"),
        (lambda p: p.pop("asOfDate"), "missing"),
        (lambda p: p["quotes"][0].update(impliedVolatility="0.2"), "finite number"),
        (lambda p: p["quotes"][0].update(forward=float("inf")), "finite number"),
        (lambda p: p["quotes"][1].update(logMoneyness=p["quotes"][0]["logMoneyness"]), "Duplicate|strictly increasing"),
        (lambda p: p["quotes"].__setitem__(slice(0, 2), list(reversed(p["quotes"][:2]))), "strictly increasing"),
        (lambda p: p["quotes"].pop(7), "rectangular"),
        (lambda p: p.update(quotes=[{**row, "logMoneyness": 0.05 if row["logMoneyness"] == 0 else row["logMoneyness"]} for row in p["quotes"]]), "ATM"),
        (lambda p: p["quotes"][0].update(askVolatility=None), "both be null"),
        (lambda p: p["quotes"][0].update(bidVolatility=0.5), "bid <= implied"),
        (lambda p: p.update(asOfDate="2026-02-30"), "invalid"),
        (lambda p: p.update(selectedMaturity=5), "extrapolation"),
        (lambda p: p.update(selectedLogMoneyness=0.5), "extrapolation"),
        (lambda p: p.update(interpolationMode="vol_bilinear"), "interpolationMode"),
        (lambda p: p.update(sourceKind="live"), "sourceKind"),
    ],
)
def test_fail_closed_adversaries(mutator, pattern):
    data = copy.deepcopy(payload())
    mutator(data)
    with pytest.raises(ValueError, match=pattern):
        normalize_vol_surface_input(data)


def test_boolean_is_not_numeric():
    data = payload(); data["selectedMaturity"] = True
    with pytest.raises(ValueError, match="finite number"):
        normalize_vol_surface_input(data)


def test_agui_adapter_delegates_without_coercion():
    data = payload(); data.pop("schemaVersion")
    summary = vol_surface_analysis(data)
    canonical = analyze_vol_surface(payload())
    assert summary["analysis_id"] == canonical["analysisId"]
    assert summary["selected_total_variance"] == canonical["selectedPoint"]["totalVariance"]
    assert summary["diagnostic_codes"] == ["NO_DISCRETE_ARBITRAGE_FLAGS"]


def test_agui_rejects_unknown_and_coercible_values():
    unknown = payload(); unknown.pop("schemaVersion"); unknown["extra"] = True
    with pytest.raises(ValueError, match="unknown"):
        vol_surface_analysis(unknown)
    coercible = payload(); coercible.pop("schemaVersion"); coercible["quotes"][0]["impliedVolatility"] = "0.2"
    with pytest.raises(ValueError, match="finite number"):
        vol_surface_analysis(coercible)


def test_agui_registry_and_openai_schema_are_closed():
    assert "vol_surface_analysis" in TOOL_EXECUTORS
    spec = next(item["function"] for item in openai_tool_specs() if item["function"]["name"] == "vol_surface_analysis")
    assert spec["parameters"]["additionalProperties"] is False
    assert spec["parameters"]["properties"]["quotes"]["items"]["additionalProperties"] is False
