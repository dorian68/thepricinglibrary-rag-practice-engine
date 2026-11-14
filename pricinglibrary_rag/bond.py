"""Canonical fixed-rate bullet bond analytics for F-CAL-8.

This mirrors ``WEBSITE/thepricinglab/src/lib/bond.mjs``. Prices are per 100
nominal and schedules are regular, unadjusted and maturity-anchored.
"""

from __future__ import annotations

import argparse
import calendar
import hashlib
import json
import math
import re
import sys
from copy import deepcopy
from datetime import date
from pathlib import Path
from typing import Any, Mapping


BOND_INPUT_SCHEMA = "tpl.bond.input.v1"
BOND_SCHEMA_VERSION = "tpl.bond.analysis.v1"
BOND_ENGINE_VERSION = "1.0.0"
BOND_CASHFLOWS_CSV_SCHEMA = "tpl.bond.cashflows.v1"
BOND_SCENARIOS_CSV_SCHEMA = "tpl.bond.scenarios.v1"

BOND_CONTRACT: dict[str, Any] = {
    "schemaVersion": "tpl.bond.contract.v1", "inputSchemaVersion": BOND_INPUT_SCHEMA,
    "analysisSchemaVersion": BOND_SCHEMA_VERSION, "engineVersion": BOND_ENGINE_VERSION,
    "instrument": "fixed_rate_bullet_bond", "quoteModes": ["yield", "clean_price"],
    "dayCounts": ["ACT/ACT ICMA", "30E/360"], "couponFrequencies": [1, 2, 4, 12],
    "positions": ["long", "short"],
    "limits": {
        "maxInputBytes": 1_000_000, "minCouponRate": 0, "maxCouponRate": 1,
        "minYield": -0.95, "maxYield": 5, "minCleanPrice": 1e-8,
        "maxCleanPrice": 1_000_000, "minNotional": 1e-8,
        "maxNotional": 1_000_000_000_000, "maxMaturityYears": 100,
        "minShockBp": -5_000, "maxShockBp": 5_000, "maxCashflows": 1_200,
        "maxRootIterations": 256,
    },
    "numeric": {"rootPriceTolerance": 1e-11, "rootYieldTolerance": 1e-14, "exportSignificantDigits": 9, "hashSignificantDigits": 17},
    "conventions": {
        "priceBasis": "per 100 nominal", "couponRate": "annual nominal decimal",
        "yield": "annual nominal decimal compounded at coupon frequency",
        "settlement": "cash flows strictly after settlement are included",
        "schedule": "unadjusted regular schedule generated backwards from maturity with end-of-month preservation",
        "accruedInterest": "coupon per period multiplied by elapsed regular-period fraction",
        "dirtyPrice": "present value of contractual cash flows per 100 nominal",
        "cleanPrice": "dirty price minus accrued interest per 100 nominal",
        "dv01": "positive central price sensitivity: (P(y-1bp)-P(y+1bp))/2",
        "positionRisk": "long=+1, short=-1; monetary values scale by notional/100",
        "shock": "parallel yield shock in basis points with exact repricing and duration-convexity approximation",
    },
    "limitations": [
        "Educational fixed-rate bullet bonds only; no calls, puts, sinking funds, amortisation, floating coupons or inflation linkage.",
        "Coupon schedules are regular and unadjusted; holiday calendars, settlement lags, business-day conventions and irregular stubs are outside v1.",
        "A single yield-to-maturity discounts every cash flow; this is not a curve, z-spread, OAS or credit valuation model.",
        "Taxes, fees, default, recovery and liquidity are not modeled.",
    ],
    "exports": {
        "cashflowsCsvSchema": BOND_CASHFLOWS_CSV_SCHEMA, "scenariosCsvSchema": BOND_SCENARIOS_CSV_SCHEMA,
        "cashflowsCsvHeaders": ["schemaVersion", "engineVersion", "analysisId", "paymentDate", "periodIndex", "exponentPeriods", "timeYears", "couponPer100", "principalPer100", "totalCashflowPer100", "discountFactor", "presentValuePer100", "cashflowDv01Per100", "positionDv01"],
        "scenariosCsvHeaders": ["schemaVersion", "engineVersion", "analysisId", "shockBp", "yield", "dirtyPricePer100", "cleanPricePer100", "exactChangePer100", "durationApproxChangePer100", "durationConvexityApproxChangePer100", "approximationErrorPer100"],
        "lineEnding": "LF", "finalNewline": True, "numericFormat": "finite_significant_9",
    },
}

LIMITS = BOND_CONTRACT["limits"]
INPUT_KEYS = (
    "schemaVersion", "settlementDate", "maturityDate", "dayCount", "couponRate",
    "couponFrequency", "quoteMode", "yieldToMaturity", "cleanPrice", "currency",
    "notional", "position", "shockBp",
)


def bond_contract_snapshot() -> dict[str, Any]:
    return deepcopy(BOND_CONTRACT)


def _number(value: Any, label: str, minimum: float, maximum: float) -> float:
    if isinstance(value, bool) or type(value) not in (int, float):
        raise ValueError(f"{label} must be a finite number.")
    converted = float(value)
    if not math.isfinite(converted):
        raise ValueError(f"{label} must be a finite number.")
    if converted < minimum or converted > maximum:
        raise ValueError(f"{label} is outside the supported domain.")
    return 0.0 if converted == 0 else converted


def _one_of(value: Any, values: list[Any], label: str) -> Any:
    if value not in values:
        raise ValueError(f"{label} is unsupported.")
    return value


def _parse_date(value: Any, label: str) -> date:
    if type(value) is not str or re.fullmatch(r"\d{4}-\d{2}-\d{2}", value) is None:
        raise ValueError(f"{label} must use strict YYYY-MM-DD format.")
    try:
        parsed = date.fromisoformat(value)
    except ValueError:
        raise ValueError(f"{label} is not a valid supported Gregorian date.") from None
    if parsed.year < 1900 or parsed.year > 2300:
        raise ValueError(f"{label} is not a valid supported Gregorian date.")
    return parsed


def normalize_bond_input(raw: Any) -> dict[str, Any]:
    if type(raw) is not dict:
        raise ValueError("Bond input must be a plain object.")
    missing = sorted(set(INPUT_KEYS) - set(raw)); unknown = sorted(set(raw) - set(INPUT_KEYS))
    if missing or unknown:
        raise ValueError(f"Bond input schema is invalid; missing={'|'.join(missing) or 'none'}; unknown={'|'.join(unknown) or 'none'}.")
    if raw["schemaVersion"] != BOND_INPUT_SCHEMA:
        raise ValueError(f"schemaVersion must be '{BOND_INPUT_SCHEMA}'.")
    settlement = _parse_date(raw["settlementDate"], "settlementDate"); maturity = _parse_date(raw["maturityDate"], "maturityDate")
    if settlement >= maturity:
        raise ValueError("settlementDate must be strictly before maturityDate.")
    if (maturity - settlement).days / 365.25 > LIMITS["maxMaturityYears"]:
        raise ValueError(f"Remaining maturity cannot exceed {LIMITS['maxMaturityYears']} years.")
    quote_mode = _one_of(raw["quoteMode"], BOND_CONTRACT["quoteModes"], "quoteMode")
    if quote_mode == "yield" and raw["cleanPrice"] is not None:
        raise ValueError("cleanPrice must be null when quoteMode is yield.")
    if quote_mode == "clean_price" and raw["yieldToMaturity"] is not None:
        raise ValueError("yieldToMaturity must be null when quoteMode is clean_price.")
    frequency = raw["couponFrequency"]
    if type(frequency) is not int or frequency not in BOND_CONTRACT["couponFrequencies"]:
        raise ValueError("couponFrequency must be one of 1, 2, 4, 12.")
    result = {
        "schemaVersion": BOND_INPUT_SCHEMA, "settlementDate": settlement.isoformat(), "maturityDate": maturity.isoformat(),
        "dayCount": _one_of(raw["dayCount"], BOND_CONTRACT["dayCounts"], "dayCount"),
        "couponRate": _number(raw["couponRate"], "couponRate", LIMITS["minCouponRate"], LIMITS["maxCouponRate"]),
        "couponFrequency": frequency, "quoteMode": quote_mode,
        "yieldToMaturity": _number(raw["yieldToMaturity"], "yieldToMaturity", LIMITS["minYield"], LIMITS["maxYield"]) if quote_mode == "yield" else None,
        "cleanPrice": _number(raw["cleanPrice"], "cleanPrice", LIMITS["minCleanPrice"], LIMITS["maxCleanPrice"]) if quote_mode == "clean_price" else None,
        "currency": raw["currency"], "notional": _number(raw["notional"], "notional", LIMITS["minNotional"], LIMITS["maxNotional"]),
        "position": _one_of(raw["position"], BOND_CONTRACT["positions"], "position"),
        "shockBp": _number(raw["shockBp"], "shockBp", LIMITS["minShockBp"], LIMITS["maxShockBp"]),
    }
    if type(result["currency"]) is not str or re.fullmatch(r"[A-Z]{3}", result["currency"]) is None:
        raise ValueError("currency must be an uppercase three-letter code.")
    return result


def _anchored_date(maturity: date, months_back: int) -> date:
    zero_month = maturity.month - 1 - months_back
    year = maturity.year + zero_month // 12; month = zero_month % 12 + 1
    last = calendar.monthrange(year, month)[1]
    maturity_eom = maturity.day == calendar.monthrange(maturity.year, maturity.month)[1]
    day = last if maturity_eom else min(maturity.day, last)
    return date(year, month, day)


def _year_fraction_30e_360(start: date, end: date) -> float:
    return ((end.year - start.year) * 360 + (end.month - start.month) * 30 + (min(end.day, 30) - min(start.day, 30))) / 360


def build_bond_schedule(input_data: Mapping[str, Any]) -> dict[str, Any]:
    settlement = _parse_date(input_data["settlementDate"], "settlementDate"); maturity = _parse_date(input_data["maturityDate"], "maturityDate")
    months_per_period = 12 // input_data["couponFrequency"]; descending: list[str] = []; index = 0
    while True:
        candidate = _anchored_date(maturity, index * months_per_period)
        if candidate <= settlement:
            future = list(reversed(descending))
            if not future:
                raise ValueError("Bond schedule has no cash flow after settlement.")
            next_coupon = _parse_date(future[0], "nextCouponDate")
            if input_data["dayCount"] == "ACT/ACT ICMA":
                elapsed = (settlement - candidate).days / (next_coupon - candidate).days
            else:
                full_period = _year_fraction_30e_360(candidate, next_coupon)
                if full_period <= 0:
                    raise ValueError("Generated 30E/360 coupon period must have a positive year fraction.")
                elapsed = _year_fraction_30e_360(candidate, settlement) / full_period
            if not math.isfinite(elapsed) or elapsed < -1e-12 or elapsed >= 1 + 1e-12:
                raise ValueError("Settlement does not fall inside the generated regular coupon period.")
            elapsed = max(0.0, min(1.0, elapsed))
            return {"previousCouponDate": candidate.isoformat(), "nextCouponDate": next_coupon.isoformat(), "paymentDates": future, "accruedPeriodFraction": elapsed, "remainingCouponFraction": 1 - elapsed}
        descending.append(candidate.isoformat()); index += 1
        if index > LIMITS["maxCashflows"]:
            raise ValueError(f"Bond schedule exceeds {LIMITS['maxCashflows']} cash flows.")


def _price_at_yield(schedule: Mapping[str, Any], input_data: Mapping[str, Any], annual_yield: float, include_cashflows: bool = False) -> dict[str, Any]:
    if not math.isfinite(annual_yield) or annual_yield < LIMITS["minYield"] or annual_yield > LIMITS["maxYield"]:
        raise ValueError("Yield is outside the supported repricing domain.")
    periodic_base = 1 + annual_yield / input_data["couponFrequency"]
    if periodic_base <= 0:
        raise ValueError("Yield and coupon frequency create a non-positive discounting base.")
    coupon = 100 * input_data["couponRate"] / input_data["couponFrequency"]
    rows: list[dict[str, Any]] = []; dirty = 0.0; count = len(schedule["paymentDates"])
    for position, payment_date in enumerate(schedule["paymentDates"]):
        exponent = schedule["remainingCouponFraction"] + position; discount = periodic_base ** (-exponent)
        principal = 100 if position == count - 1 else 0; total = coupon + principal; present_value = total * discount; dirty += present_value
        if include_cashflows:
            rows.append({"paymentDate": payment_date, "periodIndex": position + 1, "exponentPeriods": exponent, "timeYears": exponent / input_data["couponFrequency"], "couponPer100": coupon, "principalPer100": principal, "totalCashflowPer100": total, "discountFactor": discount, "presentValuePer100": present_value})
    if not math.isfinite(dirty) or dirty <= 0:
        raise ValueError("Bond repricing produced an unsupported non-finite or non-positive value.")
    return {"dirtyPricePer100": dirty, "cashflows": rows}


def _solve_yield(schedule: Mapping[str, Any], input_data: Mapping[str, Any], target_dirty: float) -> dict[str, Any]:
    low = LIMITS["minYield"]; high = LIMITS["maxYield"]
    low_residual = _price_at_yield(schedule, input_data, low)["dirtyPricePer100"] - target_dirty
    high_residual = _price_at_yield(schedule, input_data, high)["dirtyPricePer100"] - target_dirty
    if low_residual < 0 or high_residual > 0:
        raise ValueError(f"cleanPrice has no yield solution inside [{LIMITS['minYield']}, {LIMITS['maxYield']}].")
    mid = 0.0; residual = 0.0; iterations = 0
    while iterations < LIMITS["maxRootIterations"]:
        mid = (low + high) / 2; residual = _price_at_yield(schedule, input_data, mid)["dirtyPricePer100"] - target_dirty
        if abs(residual) <= BOND_CONTRACT["numeric"]["rootPriceTolerance"] or high - low <= BOND_CONTRACT["numeric"]["rootYieldTolerance"]:
            break
        if residual > 0:
            low = mid; low_residual = residual
        else:
            high = mid; high_residual = residual
        iterations += 1
    _ = low_residual, high_residual
    return {"yieldToMaturity": mid, "iterations": iterations + 1, "residualPer100": residual}


def _canonical_number(value: float) -> str:
    if not math.isfinite(value):
        raise ValueError("Canonical data contains a non-finite number.")
    if value == 0:
        return "0"
    mantissa, exponent = format(value, ".16e").lower().split("e")
    return f"{mantissa.rstrip('0').rstrip('.')}e{int(exponent)}"


def _canonical_tree(value: Any) -> Any:
    if isinstance(value, bool) or value is None or isinstance(value, str):
        return value
    if type(value) in (int, float):
        return _canonical_number(float(value))
    if isinstance(value, list):
        return [_canonical_tree(item) for item in value]
    if isinstance(value, Mapping):
        return {key: _canonical_tree(value[key]) for key in sorted(value)}
    return value


def _analysis_id(input_data: Mapping[str, Any]) -> str:
    payload = json.dumps(_canonical_tree(input_data), ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _finite_tree(value: Any, path: str = "result") -> None:
    if type(value) is float and not math.isfinite(value):
        raise ValueError(f"{path} contains a non-finite number.")
    if isinstance(value, list):
        for index, item in enumerate(value): _finite_tree(item, f"{path}[{index}]")
    elif isinstance(value, Mapping):
        for key, item in value.items(): _finite_tree(item, f"{path}.{key}")


def analyze_bond(raw: Any) -> dict[str, Any]:
    input_data = normalize_bond_input(raw); schedule = build_bond_schedule(input_data)
    coupon = 100 * input_data["couponRate"] / input_data["couponFrequency"]
    accrued = coupon * schedule["accruedPeriodFraction"]; solver = None
    if input_data["quoteMode"] == "yield":
        ytm = input_data["yieldToMaturity"]
    else:
        solver = _solve_yield(schedule, input_data, input_data["cleanPrice"] + accrued); ytm = solver["yieldToMaturity"]
    if ytm - 0.0001 < LIMITS["minYield"] or ytm + 0.0001 > LIMITS["maxYield"]:
        raise ValueError("Resolved yield must allow symmetric +/-1bp DV01 repricing inside the supported domain.")
    shocked_yield = ytm + input_data["shockBp"] / 10_000
    if shocked_yield < LIMITS["minYield"] or shocked_yield > LIMITS["maxYield"]:
        raise ValueError("Selected shock moves yield outside the supported repricing domain.")
    base = _price_at_yield(schedule, input_data, ytm, True); dirty = base["dirtyPricePer100"]; clean = dirty - accrued
    weighted_time = sum(row["timeYears"] * row["presentValuePer100"] for row in base["cashflows"])
    macaulay = weighted_time / dirty; modified = macaulay / (1 + ytm / input_data["couponFrequency"])
    convexity = sum(row["presentValuePer100"] * row["exponentPeriods"] * (row["exponentPeriods"] + 1) / (input_data["couponFrequency"] ** 2 * (1 + ytm / input_data["couponFrequency"]) ** 2) for row in base["cashflows"]) / dirty
    down = _price_at_yield(schedule, input_data, ytm - 0.0001)["dirtyPricePer100"]
    up = _price_at_yield(schedule, input_data, ytm + 0.0001)["dirtyPricePer100"]
    dv01 = (down - up) / 2; sign = 1 if input_data["position"] == "long" else -1; money_scale = sign * input_data["notional"] / 100
    cashflows = []
    for row in base["cashflows"]:
        down_discount = (1 + (ytm - 0.0001) / input_data["couponFrequency"]) ** (-row["exponentPeriods"])
        up_discount = (1 + (ytm + 0.0001) / input_data["couponFrequency"]) ** (-row["exponentPeriods"])
        cashflow_dv01 = row["totalCashflowPer100"] * (down_discount - up_discount) / 2
        cashflows.append({**row, "cashflowDv01Per100": cashflow_dv01, "positionDv01": cashflow_dv01 * money_scale})
    cashflow_dv01_reconciliation_error = sum(row["cashflowDv01Per100"] for row in cashflows) - dv01
    shocks = sorted(set([-200, -100, -50, -25, -1, 0, 1, 25, 50, 100, 200, input_data["shockBp"]])); scenarios = []
    for shock in shocks:
        scenario_yield = ytm + shock / 10_000
        if scenario_yield < LIMITS["minYield"] or scenario_yield > LIMITS["maxYield"]: continue
        scenario_dirty = _price_at_yield(schedule, input_data, scenario_yield)["dirtyPricePer100"]
        exact = scenario_dirty - dirty; delta_yield = shock / 10_000; duration_change = -dirty * modified * delta_yield
        duration_convexity = dirty * (-modified * delta_yield + 0.5 * convexity * delta_yield ** 2)
        scenarios.append({"shockBp": shock, "yield": scenario_yield, "dirtyPricePer100": scenario_dirty, "cleanPricePer100": scenario_dirty - accrued, "exactChangePer100": exact, "durationApproxChangePer100": duration_change, "durationConvexityApproxChangePer100": duration_convexity, "approximationErrorPer100": duration_convexity - exact})
    selected = next((row for row in scenarios if row["shockBp"] == input_data["shockBp"]), None)
    if selected is None: raise ValueError("Selected shock scenario was not produced.")
    diagnostics = [
        {"code": "REGULAR_UNADJUSTED_SCHEDULE", "severity": "info", "message": "Coupon dates are contractual unadjusted dates generated backwards from maturity; no holiday calendar or stub is inferred."},
        {"code": "YIELD_SOLVED_FROM_CLEAN_PRICE" if input_data["quoteMode"] == "clean_price" else "PRICE_FROM_YIELD", "severity": "info", "message": "Yield-to-maturity was solved deterministically from clean price plus accrued interest." if input_data["quoteMode"] == "clean_price" else "Clean and dirty prices were discounted from the supplied nominal yield."},
    ]
    if ytm < 0: diagnostics.append({"code": "NEGATIVE_YIELD", "severity": "info", "message": "Negative nominal yield is supported while the periodic discounting base remains positive."})
    result = {
        "schemaVersion": BOND_SCHEMA_VERSION, "engineVersion": BOND_ENGINE_VERSION, "analysisId": _analysis_id(input_data), "input": input_data,
        "instrument": {"type": "fixed-rate bullet", "priceBasis": "per 100 nominal", "couponRate": input_data["couponRate"], "couponFrequency": input_data["couponFrequency"], "couponPerPeriodPer100": coupon, "redemptionPer100": 100, "currency": input_data["currency"]},
        "schedule": {"previousCouponDate": schedule["previousCouponDate"], "nextCouponDate": schedule["nextCouponDate"], "maturityDate": input_data["maturityDate"], "dayCount": input_data["dayCount"], "accruedPeriodFraction": schedule["accruedPeriodFraction"], "remainingCouponFraction": schedule["remainingCouponFraction"], "cashflowCount": len(schedule["paymentDates"])},
        "quote": {"quoteMode": input_data["quoteMode"], "yieldToMaturity": ytm, "cleanPricePer100": clean, "dirtyPricePer100": dirty, "accruedInterestPer100": accrued, "solver": solver},
        "analytics": {"macaulayDurationYears": macaulay, "modifiedDuration": modified, "convexity": convexity, "dv01Per100": dv01, "priceDown1bpPer100": down, "priceUp1bpPer100": up, "cashflowDv01ReconciliationError": cashflow_dv01_reconciliation_error, "currentYield": input_data["couponRate"] * 100 / clean if clean > 0 else None},
        "position": {"side": input_data["position"], "sign": sign, "notional": input_data["notional"], "cleanMarketValue": clean * money_scale, "dirtyMarketValue": dirty * money_scale, "accruedInterest": accrued * money_scale, "dv01": dv01 * money_scale},
        "selectedScenario": {**selected, "exactPnl": selected["exactChangePer100"] * money_scale, "durationPnl": selected["durationApproxChangePer100"] * money_scale, "durationConvexityPnl": selected["durationConvexityApproxChangePer100"] * money_scale},
        "scenarios": scenarios, "cashflows": cashflows, "diagnostics": diagnostics,
        "conventions": deepcopy(BOND_CONTRACT["conventions"]), "limitations": list(BOND_CONTRACT["limitations"]),
    }
    _finite_tree(result); return result


def _export_number(value: float | int | None) -> str:
    if value is None: return ""
    converted = float(value)
    if not math.isfinite(converted): raise ValueError("Evidence export contains a non-finite number.")
    if converted == 0 or abs(converted) < 1e-15: return "0"
    mantissa, exponent = format(converted, ".8e").lower().split("e")
    return f"{mantissa.rstrip('0').rstrip('.')}e{int(exponent)}"


def _csv_escape(value: Any) -> str:
    text = "" if value is None else str(value)
    return f'"{text.replace(chr(34), chr(34) * 2)}"' if any(char in text for char in ',"\n\r') else text


def _csv(headers: list[str], rows: list[Mapping[str, Any]]) -> str:
    lines = [",".join(headers)]
    for row in rows:
        lines.append(",".join(_csv_escape(_export_number(row.get(header)) if type(row.get(header)) in (int, float) and not isinstance(row.get(header), bool) else row.get(header)) for header in headers))
    return "\n".join(lines) + ("\n" if rows else "")


def build_bond_cashflows_csv(result: Mapping[str, Any]) -> str:
    rows = [{"schemaVersion": BOND_CASHFLOWS_CSV_SCHEMA, "engineVersion": result["engineVersion"], "analysisId": result["analysisId"], **row} for row in result["cashflows"]]
    return _csv(BOND_CONTRACT["exports"]["cashflowsCsvHeaders"], rows)


def build_bond_scenarios_csv(result: Mapping[str, Any]) -> str:
    rows = [{"schemaVersion": BOND_SCENARIOS_CSV_SCHEMA, "engineVersion": result["engineVersion"], "analysisId": result["analysisId"], **row} for row in result["scenarios"]]
    return _csv(BOND_CONTRACT["exports"]["scenariosCsvHeaders"], rows)


def _write_stdout(text: str) -> None:
    sys.stdout.buffer.write(text.encode("utf-8"))


def _main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Canonical TPL fixed-rate bond analytics")
    parser.add_argument("--contract", action="store_true"); parser.add_argument("--input", type=Path)
    parser.add_argument("--cashflows-csv", action="store_true"); parser.add_argument("--scenarios-csv", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.contract:
            _write_stdout(json.dumps(BOND_CONTRACT, ensure_ascii=False, separators=(",", ":")) + "\n"); return 0
        if args.input is None: raise ValueError("--input is required unless --contract is used.")
        if args.input.stat().st_size > LIMITS["maxInputBytes"]: raise ValueError("Bond input exceeds the maximum supported size.")
        raw = json.loads(args.input.read_text(encoding="utf-8")); result = analyze_bond(raw)
        if args.cashflows_csv: _write_stdout(build_bond_cashflows_csv(result))
        elif args.scenarios_csv: _write_stdout(build_bond_scenarios_csv(result))
        else: _write_stdout(json.dumps(result, ensure_ascii=False, allow_nan=False, separators=(",", ":")) + "\n")
        return 0
    except (OSError, json.JSONDecodeError, ValueError) as error:
        print(str(error), file=sys.stderr); return 2


if __name__ == "__main__":
    raise SystemExit(_main())
