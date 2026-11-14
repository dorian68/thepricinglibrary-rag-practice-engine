from __future__ import annotations

import json
import math
from pathlib import Path

import pytest

from pricinglibrary_rag.bond import (
    BOND_CONTRACT,
    analyze_bond,
    build_bond_cashflows_csv,
    build_bond_scenarios_csv,
    normalize_bond_input,
)
from pricinglibrary_rag.agui import bond_analytics


ROOT = Path(__file__).resolve().parents[3]


def base(**overrides):
    value = {
        "schemaVersion": "tpl.bond.input.v1",
        "settlementDate": "2026-07-31",
        "maturityDate": "2036-07-31",
        "dayCount": "ACT/ACT ICMA",
        "couponRate": 0.05,
        "couponFrequency": 2,
        "quoteMode": "yield",
        "yieldToMaturity": 0.05,
        "cleanPrice": None,
        "currency": "EUR",
        "notional": 1_000_000,
        "position": "long",
        "shockBp": 25,
    }
    value.update(overrides)
    return value


def test_runtime_contract_matches_json_authority():
    assert BOND_CONTRACT == json.loads((ROOT / "fixtures/bond_contract.json").read_text(encoding="utf-8"))


def test_par_bond_on_coupon_date_is_exact():
    result = analyze_bond(base())
    assert result["quote"]["cleanPricePer100"] == pytest.approx(100, abs=1e-11)
    assert result["quote"]["dirtyPricePer100"] == pytest.approx(100, abs=1e-11)
    assert result["quote"]["accruedInterestPer100"] == 0
    assert result["schedule"]["previousCouponDate"] == "2026-07-31"
    assert result["schedule"]["nextCouponDate"] == "2027-01-31"


def test_between_coupon_accrued_and_clean_dirty_identity():
    result = analyze_bond(base(settlementDate="2026-10-17", maturityDate="2033-01-31", couponRate=0.0375, yieldToMaturity=0.042))
    quote = result["quote"]
    assert quote["accruedInterestPer100"] > 0
    assert quote["dirtyPricePer100"] == pytest.approx(quote["cleanPricePer100"] + quote["accruedInterestPer100"], abs=1e-12)
    assert 0 < result["schedule"]["accruedPeriodFraction"] < 1
    assert result["cashflows"][0]["paymentDate"] == result["schedule"]["nextCouponDate"]


def test_ytm_clean_price_round_trip_and_solver_residual():
    priced = analyze_bond(base(settlementDate="2026-09-15", yieldToMaturity=0.037125))
    solved = analyze_bond(base(settlementDate="2026-09-15", quoteMode="clean_price", yieldToMaturity=None, cleanPrice=priced["quote"]["cleanPricePer100"]))
    assert solved["quote"]["yieldToMaturity"] == pytest.approx(0.037125, abs=2e-13)
    assert abs(solved["quote"]["solver"]["residualPer100"]) <= 1e-10
    assert solved["quote"]["cleanPricePer100"] == pytest.approx(priced["quote"]["cleanPricePer100"], abs=1e-10)


def test_zero_coupon_six_month_is_not_rounded_to_one_year():
    result = analyze_bond(base(settlementDate="2026-01-31", maturityDate="2026-07-31", couponRate=0, couponFrequency=1, yieldToMaturity=0.04))
    exponent = result["cashflows"][0]["exponentPeriods"]
    assert 0.49 < exponent < 0.50
    assert result["quote"]["dirtyPricePer100"] == pytest.approx(100 / 1.04**exponent, abs=1e-12)
    assert result["analytics"]["macaulayDurationYears"] == pytest.approx(exponent, abs=1e-12)


def test_duration_convexity_and_dv01_match_independent_repricing():
    result = analyze_bond(base(settlementDate="2026-10-17", yieldToMaturity=0.042, shockBp=1))
    analytics = result["analytics"]
    assert analytics["dv01Per100"] == pytest.approx((analytics["priceDown1bpPer100"] - analytics["priceUp1bpPer100"]) / 2, abs=1e-14)
    one_bp = result["selectedScenario"]
    assert abs(one_bp["approximationErrorPer100"]) < 1e-7
    assert analytics["modifiedDuration"] > 0
    assert analytics["convexity"] > 0
    assert abs(analytics["cashflowDv01ReconciliationError"]) < 1e-13
    assert sum(row["cashflowDv01Per100"] for row in result["cashflows"]) == pytest.approx(analytics["dv01Per100"], abs=1e-13)
    assert sum(row["positionDv01"] for row in result["cashflows"]) == pytest.approx(result["position"]["dv01"], abs=1e-9)


def test_negative_yield_and_monthly_eom_schedule_are_supported():
    negative = analyze_bond(base(maturityDate="2031-07-31", couponRate=0.01, yieldToMaturity=-0.0075, shockBp=-50))
    assert negative["quote"]["cleanPricePer100"] > 100
    assert "NEGATIVE_YIELD" in {row["code"] for row in negative["diagnostics"]}
    monthly = analyze_bond(base(settlementDate="2026-07-19", maturityDate="2028-02-29", couponFrequency=12, couponRate=0.024, yieldToMaturity=0.031))
    assert monthly["schedule"]["nextCouponDate"] == "2026-07-31"
    assert monthly["cashflows"][-1]["paymentDate"] == "2028-02-29"
    assert all(row["paymentDate"].endswith(("-28", "-29", "-30", "-31")) for row in monthly["cashflows"])


def test_30e_360_and_signed_position_values():
    long = analyze_bond(base(settlementDate="2026-08-30", maturityDate="2041-02-28", dayCount="30E/360", couponRate=0.0675, couponFrequency=4, yieldToMaturity=0.0725, currency="USD", notional=2_500_000, shockBp=100))
    short = analyze_bond({**base(settlementDate="2026-08-30", maturityDate="2041-02-28", dayCount="30E/360", couponRate=0.0675, couponFrequency=4, yieldToMaturity=0.0725, currency="USD", notional=2_500_000, shockBp=100), "position": "short"})
    assert long["schedule"]["dayCount"] == "30E/360"
    assert long["position"]["dirtyMarketValue"] == pytest.approx(-short["position"]["dirtyMarketValue"])
    assert long["position"]["dv01"] == pytest.approx(-short["position"]["dv01"])
    assert long["selectedScenario"]["exactPnl"] == pytest.approx(-short["selectedScenario"]["exactPnl"])


@pytest.mark.parametrize("settlement", ["2029-08-28", "2029-08-29", "2029-08-30"])
def test_30e_360_february_to_august_eom_normalizes_by_actual_coupon_period(settlement):
    result = analyze_bond(base(
        settlementDate=settlement,
        maturityDate="2033-08-31",
        dayCount="30E/360",
        couponFrequency=2,
        couponRate=0.05,
        yieldToMaturity=0.05,
    ))
    expected = ((2029 - 2029) * 360 + (8 - 2) * 30 + (min(int(settlement[-2:]), 30) - 28)) / 360
    full_period = ((2029 - 2029) * 360 + (8 - 2) * 30 + (30 - 28)) / 360
    expected_fraction = expected / full_period
    assert result["schedule"]["previousCouponDate"] == "2029-02-28"
    assert result["schedule"]["nextCouponDate"] == "2029-08-31"
    assert result["schedule"]["accruedPeriodFraction"] == pytest.approx(expected_fraction, abs=1e-14)
    assert result["schedule"]["remainingCouponFraction"] == pytest.approx(1 - expected_fraction, abs=1e-14)
    assert result["quote"]["accruedInterestPer100"] == pytest.approx(2.5 * expected_fraction, abs=1e-14)
    assert result["cashflows"][0]["exponentPeriods"] == pytest.approx(1 - expected_fraction, abs=1e-14)


@pytest.mark.parametrize(
    "change",
    [
        {"couponFrequency": 0}, {"couponFrequency": 2.5}, {"couponFrequency": "2"},
        {"couponRate": "0.05"}, {"yieldToMaturity": float("inf")}, {"notional": True},
        {"currency": "eur"}, {"position": "flat"}, {"dayCount": "ACT/365F"},
        {"settlementDate": "31/07/2026"}, {"maturityDate": "2026-07-31"},
    ],
)
def test_invalid_inputs_fail_closed(change):
    with pytest.raises(ValueError):
        analyze_bond(base(**change))


def test_quote_mode_exclusivity_and_unknown_missing_fields_fail_closed():
    with pytest.raises(ValueError, match="cleanPrice must be null"):
        analyze_bond(base(cleanPrice=99))
    with pytest.raises(ValueError, match="yieldToMaturity must be null"):
        analyze_bond(base(quoteMode="clean_price", cleanPrice=99))
    unknown = base(fake=True); missing = base(); del missing["couponRate"]
    with pytest.raises(ValueError, match="unknown=fake"):
        normalize_bond_input(unknown)
    with pytest.raises(ValueError, match="missing=couponRate"):
        normalize_bond_input(missing)


def test_singular_bump_and_out_of_domain_shock_fail_closed():
    with pytest.raises(ValueError, match="symmetric"):
        analyze_bond(base(yieldToMaturity=-0.95))
    with pytest.raises(ValueError, match="Selected shock"):
        analyze_bond(base(yieldToMaturity=4.9, shockBp=2000))


def test_repeatability_sha_cashflows_scenarios_and_exports():
    first = analyze_bond(base(settlementDate="2026-10-17", quoteMode="clean_price", yieldToMaturity=None, cleanPrice=98.25, shockBp=-75))
    second = analyze_bond(base(settlementDate="2026-10-17", quoteMode="clean_price", yieldToMaturity=None, cleanPrice=98.25, shockBp=-75))
    assert first == second
    assert len(first["analysisId"]) == 64
    assert first["cashflows"] and first["scenarios"]
    assert all(math.isfinite(value) for row in first["cashflows"] for value in row.values() if isinstance(value, float))
    cashflows = build_bond_cashflows_csv(first); scenarios = build_bond_scenarios_csv(first)
    assert cashflows.endswith("\n") and "\r" not in cashflows
    assert scenarios.endswith("\n") and "\r" not in scenarios
    assert first["analysisId"] in cashflows and first["analysisId"] in scenarios


def test_agui_adapter_preserves_canonical_payload_and_outputs():
    payload = base()
    del payload["schemaVersion"]
    adapted = bond_analytics(payload)
    canonical = analyze_bond(base())
    assert adapted["analysis_id"] == canonical["analysisId"]
    assert adapted["clean_price_per_100"] == canonical["quote"]["cleanPricePer100"]
    assert adapted["position_dv01"] == canonical["position"]["dv01"]
    assert adapted["cashflow_count"] == 20


@pytest.mark.parametrize("change", [{"couponFrequency": "2"}, {"couponRate": "0.05"}, {"notional": True}, {"shockBp": "25"}, {"fake": 1}])
def test_agui_adapter_rejects_coercion_and_unknown_fields(change):
    payload = base()
    del payload["schemaVersion"]
    payload.update(change)
    with pytest.raises(ValueError):
        bond_analytics(payload)
