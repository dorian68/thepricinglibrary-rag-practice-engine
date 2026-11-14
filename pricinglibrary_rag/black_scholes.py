"""Canonical Black-Scholes-Merton European option engine for F-CAL10.

The module is deliberately strict: canonical inputs use decimal rates and
volatility, maturity in ACT/365F years, and exact schemas.  Human-unit adapters
belong at integration boundaries such as AG-UI.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any, Mapping


BLACK_SCHOLES_INPUT_SCHEMA = "tpl.black-scholes.input.v1"
BLACK_SCHOLES_SCHEMA_VERSION = "tpl.black-scholes.analysis.v1"
BLACK_SCHOLES_ENGINE_VERSION = "1.0.0"
BLACK_SCHOLES_SCENARIO_CSV_SCHEMA = "tpl.black-scholes.scenarios.v1"
BLACK_SCHOLES_SENSITIVITY_CSV_SCHEMA = "tpl.black-scholes.sensitivities.v1"

INPUT_KEYS = (
    "schemaVersion", "quoteMode", "optionType", "spot", "strike",
    "maturityYears", "dayCount", "riskFreeRate", "dividendYield",
    "volatility", "marketPrice", "currency", "position", "quantity",
    "multiplier", "shocks",
)
SHOCK_KEYS = ("spotPct", "volPoints", "days")

BLACK_SCHOLES_CONTRACT: dict[str, Any] = {
    "schemaVersion": "tpl.black-scholes.contract.v1",
    "inputSchemaVersion": BLACK_SCHOLES_INPUT_SCHEMA,
    "analysisSchemaVersion": BLACK_SCHOLES_SCHEMA_VERSION,
    "engineVersion": BLACK_SCHOLES_ENGINE_VERSION,
    "model": "black_scholes_merton_european",
    "measure": "risk_neutral_Q",
    "quoteModes": ["volatility", "market_price"],
    "optionTypes": ["call", "put"],
    "dayCounts": ["ACT/365F"],
    "positions": ["long", "short"],
    "inputKeys": list(INPUT_KEYS),
    "shockKeys": list(SHOCK_KEYS),
    "limits": {
        "maxInputBytes": 1_000_000,
        "minSpot": 1e-8, "maxSpot": 1_000_000_000_000,
        "minStrike": 1e-8, "maxStrike": 1_000_000_000_000,
        "minVolatility": 0, "maxVolatility": 5,
        "minMaturityYears": 0, "maxMaturityYears": 30,
        "minRate": -1, "maxRate": 1,
        "minMarketPrice": 0, "maxMarketPrice": 1_000_000_000_000,
        "maxQuantity": 1_000_000,
        "minMultiplier": 1e-8, "maxMultiplier": 1_000_000_000_000,
        "maxSpotShockPct": 99.999999,
        "maxVolShockPoints": 500,
        "maxTimeShockDays": 10_950,
        "sensitivityPoints": 21,
    },
    "numeric": {
        "cdf": "abramowitz_stegun_7_1_26",
        "ivMaxIterations": 120,
        "ivPriceTolerance": 1e-12,
        "ivMaxVolatility": 5,
        "parityTolerance": 1e-12,
        "exportSignificantDigits": 9,
        "hashSignificantDigits": 17,
    },
    "conventions": {
        "exercise": "european",
        "rates": "continuously_compounded_decimals",
        "dividends": "continuous_yield_decimal",
        "dayCount": "ACT/365F",
        "atExpiry": "exact_intrinsic_with_half_delta_at_the_money",
        "zeroVolatility": "discounted_deterministic_forward_payoff",
        "zeroVolatilityKink": "at_discounted_forward_atm_use_half_delta_half_theta_half_rho_and_zero_gamma_vega_as_declared_limiting_convention",
        "zeroVolatilityKinkLimit": "the_sigma_zero_forward_atm_payoff_is_not_classically_differentiable; reported_greeks_are_a_symmetric_limiting_convention",
        "delta": "unit_price_change_per_one_spot_unit",
        "gamma": "delta_change_per_one_spot_unit",
        "vega": "unit_price_change_per_plus_one_volatility_percentage_point",
        "theta": "unit_price_change_for_one_calendar_day_elapsed",
        "rho": "unit_price_change_per_plus_one_rate_percentage_point",
        "portfolioScale": "position_sign_times_quantity_times_multiplier",
        "spotShockPct": "human_percentage_points_divided_by_100",
        "volShockPoints": "human_volatility_points_divided_by_100",
        "timeShockDays": "calendar_days_elapsed_with_maturity_floored_at_zero",
    },
    "scenarios": ["base", "spotDown", "spotUp", "volDown", "volUp", "timeForward"],
    "sensitivities": ["spot", "volatility", "maturity"],
    "exports": {
        "scenarioCsvSchema": BLACK_SCHOLES_SCENARIO_CSV_SCHEMA,
        "sensitivityCsvSchema": BLACK_SCHOLES_SENSITIVITY_CSV_SCHEMA,
        "scenarioCsvHeaders": ["schemaVersion", "engineVersion", "analysisId", "scenario", "spot", "volatility", "maturityYears", "unitPrice", "portfolioValue", "pnl"],
        "sensitivityCsvHeaders": ["schemaVersion", "engineVersion", "analysisId", "axis", "x", "unitPrice", "portfolioValue"],
        "lineEnding": "LF", "finalNewline": True, "numericFormat": "finite_significant_9",
    },
}

LIMITS = BLACK_SCHOLES_CONTRACT["limits"]


def black_scholes_contract_snapshot() -> dict[str, Any]:
    return deepcopy(BLACK_SCHOLES_CONTRACT)


def _number(value: Any, label: str, minimum: float, maximum: float) -> float:
    if isinstance(value, bool) or type(value) not in (int, float):
        raise ValueError(f"{label} must be a finite JSON number; strings and booleans are rejected.")
    converted = float(value)
    if not math.isfinite(converted):
        raise ValueError(f"{label} must be finite.")
    if converted < minimum or converted > maximum:
        raise ValueError(f"{label} is outside the supported domain [{minimum}, {maximum}].")
    return 0.0 if converted == 0 else converted


def _enum(value: Any, values: list[str], label: str) -> str:
    if type(value) is not str or value not in values:
        raise ValueError(f"{label} is unsupported.")
    return value


def _exact_keys(raw: Any, keys: tuple[str, ...], label: str) -> None:
    if type(raw) is not dict:
        raise ValueError(f"{label} must be a plain object.")
    missing = sorted(set(keys) - set(raw))
    unknown = sorted(set(raw) - set(keys))
    if missing or unknown:
        raise ValueError(f"{label} schema is invalid; missing={'|'.join(missing) or 'none'}; unknown={'|'.join(unknown) or 'none'}.")


def normalize_black_scholes_input(raw: Any) -> dict[str, Any]:
    _exact_keys(raw, INPUT_KEYS, "Black-Scholes input")
    if raw["schemaVersion"] != BLACK_SCHOLES_INPUT_SCHEMA:
        raise ValueError(f"schemaVersion must be '{BLACK_SCHOLES_INPUT_SCHEMA}'.")
    _exact_keys(raw["shocks"], SHOCK_KEYS, "shocks")
    result = {
        "schemaVersion": BLACK_SCHOLES_INPUT_SCHEMA,
        "quoteMode": _enum(raw["quoteMode"], BLACK_SCHOLES_CONTRACT["quoteModes"], "quoteMode"),
        "optionType": _enum(raw["optionType"], BLACK_SCHOLES_CONTRACT["optionTypes"], "optionType"),
        "spot": _number(raw["spot"], "spot", LIMITS["minSpot"], LIMITS["maxSpot"]),
        "strike": _number(raw["strike"], "strike", LIMITS["minStrike"], LIMITS["maxStrike"]),
        "maturityYears": _number(raw["maturityYears"], "maturityYears", LIMITS["minMaturityYears"], LIMITS["maxMaturityYears"]),
        "dayCount": _enum(raw["dayCount"], BLACK_SCHOLES_CONTRACT["dayCounts"], "dayCount"),
        "riskFreeRate": _number(raw["riskFreeRate"], "riskFreeRate", LIMITS["minRate"], LIMITS["maxRate"]),
        "dividendYield": _number(raw["dividendYield"], "dividendYield", LIMITS["minRate"], LIMITS["maxRate"]),
        "volatility": None,
        "marketPrice": None,
        "currency": raw["currency"],
        "position": _enum(raw["position"], BLACK_SCHOLES_CONTRACT["positions"], "position"),
        "quantity": _number(raw["quantity"], "quantity", math.nextafter(0.0, 1.0), LIMITS["maxQuantity"]),
        "multiplier": _number(raw["multiplier"], "multiplier", LIMITS["minMultiplier"], LIMITS["maxMultiplier"]),
        "shocks": {
            "spotPct": _number(raw["shocks"]["spotPct"], "shocks.spotPct", 0, LIMITS["maxSpotShockPct"]),
            "volPoints": _number(raw["shocks"]["volPoints"], "shocks.volPoints", 0, LIMITS["maxVolShockPoints"]),
            "days": _number(raw["shocks"]["days"], "shocks.days", 0, LIMITS["maxTimeShockDays"]),
        },
    }
    if type(result["currency"]) is not str or len(result["currency"]) != 3 or not result["currency"].isascii() or not result["currency"].isalpha() or not result["currency"].isupper():
        raise ValueError("currency must be an uppercase three-letter code.")
    if result["quoteMode"] == "volatility":
        if raw["marketPrice"] is not None:
            raise ValueError("marketPrice must be null when quoteMode is volatility.")
        result["volatility"] = _number(raw["volatility"], "volatility", LIMITS["minVolatility"], LIMITS["maxVolatility"])
    else:
        if raw["volatility"] is not None:
            raise ValueError("volatility must be null when quoteMode is market_price.")
        result["marketPrice"] = _number(raw["marketPrice"], "marketPrice", LIMITS["minMarketPrice"], LIMITS["maxMarketPrice"])
        if result["maturityYears"] == 0:
            raise ValueError("Implied volatility is not identifiable at expiry; use quoteMode volatility.")
    return result


def _norm_cdf(raw_x: float) -> float:
    # A&S 7.1.26, intentionally mirrored byte-for-byte in the JS engine.
    coefficients = (0.254829592, -0.284496736, 1.421413741, -1.453152027, 1.061405429)
    sign = -1 if raw_x < 0 else 1
    x = abs(raw_x) / math.sqrt(2.0)
    t = 1.0 / (1.0 + 0.3275911 * x)
    erf = 1.0 - (((((coefficients[4] * t + coefficients[3]) * t) + coefficients[2]) * t + coefficients[1]) * t + coefficients[0]) * t * math.exp(-x * x)
    return 0.5 * (1.0 + sign * erf)


def _norm_pdf(x: float) -> float:
    return math.exp(-0.5 * x * x) / math.sqrt(2.0 * math.pi)


def _intrinsic(spot: float, strike: float, option_type: str) -> float:
    return max(spot - strike, 0.0) if option_type == "call" else max(strike - spot, 0.0)


def _option(spot: float, strike: float, maturity: float, rate: float, dividend: float, volatility: float, option_type: str) -> dict[str, Any]:
    if maturity == 0:
        relation = 1 if spot > strike else (-1 if spot < strike else 0)
        delta = (1.0 if relation > 0 else (0.0 if relation < 0 else 0.5)) if option_type == "call" else (0.0 if relation > 0 else (-1.0 if relation < 0 else -0.5))
        return {"type": option_type, "unitPrice": _intrinsic(spot, strike, option_type), "greeks": {"delta": delta, "gamma": 0.0, "vega": 0.0, "theta": 0.0, "rho": 0.0}, "limit": "expiry"}
    disc_q = math.exp(-dividend * maturity)
    disc_r = math.exp(-rate * maturity)
    discounted_spot = spot * disc_q
    discounted_strike = strike * disc_r
    if volatility == 0:
        difference = discounted_spot - discounted_strike
        kink_tolerance = 1e-14 * max(1.0, abs(discounted_spot), abs(discounted_strike))
        relation = 1 if difference > kink_tolerance else (-1 if difference < -kink_tolerance else 0)
        weight = 1.0 if relation > 0 else (0.0 if relation < 0 else 0.5)
        if option_type == "call":
            price = max(difference, 0.0)
            delta = weight * disc_q
            theta = weight * (dividend * discounted_spot - rate * discounted_strike) / 365.0
            rho = weight * maturity * discounted_strike / 100.0
        else:
            put_weight = 1.0 if relation < 0 else (0.0 if relation > 0 else 0.5)
            price = max(-difference, 0.0)
            delta = -put_weight * disc_q
            theta = put_weight * (rate * discounted_strike - dividend * discounted_spot) / 365.0
            rho = -put_weight * maturity * discounted_strike / 100.0
        return {"type": option_type, "unitPrice": price, "greeks": {"delta": delta, "gamma": 0.0, "vega": 0.0, "theta": theta, "rho": rho}, "limit": "zero_volatility"}
    sqrt_t = math.sqrt(maturity)
    d1 = (math.log(spot / strike) + (rate - dividend + 0.5 * volatility * volatility) * maturity) / (volatility * sqrt_t)
    d2 = d1 - volatility * sqrt_t
    pdf = _norm_pdf(d1)
    if option_type == "call":
        nd1, nd2 = _norm_cdf(d1), _norm_cdf(d2)
        price = discounted_spot * nd1 - discounted_strike * nd2
        delta = disc_q * nd1
        theta = (-spot * disc_q * pdf * volatility / (2.0 * sqrt_t) - rate * discounted_strike * nd2 + dividend * discounted_spot * nd1) / 365.0
        rho = maturity * discounted_strike * nd2 / 100.0
    else:
        nmd1, nmd2 = _norm_cdf(-d1), _norm_cdf(-d2)
        price = discounted_strike * nmd2 - discounted_spot * nmd1
        delta = -disc_q * nmd1
        theta = (-spot * disc_q * pdf * volatility / (2.0 * sqrt_t) + rate * discounted_strike * nmd2 - dividend * discounted_spot * nmd1) / 365.0
        rho = -maturity * discounted_strike * nmd2 / 100.0
    return {
        "type": option_type,
        "unitPrice": price,
        "greeks": {"delta": delta, "gamma": disc_q * pdf / (spot * volatility * sqrt_t), "vega": spot * disc_q * pdf * sqrt_t / 100.0, "theta": theta, "rho": rho},
        "limit": "closed_form",
    }


def _bounds(data: Mapping[str, Any], option_type: str) -> tuple[float, float]:
    discounted_spot = data["spot"] * math.exp(-data["dividendYield"] * data["maturityYears"])
    discounted_strike = data["strike"] * math.exp(-data["riskFreeRate"] * data["maturityYears"])
    return (max(discounted_spot - discounted_strike, 0.0), discounted_spot) if option_type == "call" else (max(discounted_strike - discounted_spot, 0.0), discounted_strike)


def _implied_volatility(data: Mapping[str, Any]) -> tuple[float, dict[str, Any]]:
    target = data["marketPrice"]
    lower_bound, upper_bound = _bounds(data, data["optionType"])
    tolerance = BLACK_SCHOLES_CONTRACT["numeric"]["ivPriceTolerance"]
    scale_tolerance = tolerance * max(1.0, abs(target), abs(lower_bound), abs(upper_bound))
    if target < lower_bound - scale_tolerance or target > upper_bound + scale_tolerance:
        raise ValueError(f"marketPrice violates no-arbitrage bounds [{lower_bound}, {upper_bound}].")
    lower_price = _option(data["spot"], data["strike"], data["maturityYears"], data["riskFreeRate"], data["dividendYield"], 0.0, data["optionType"])["unitPrice"]
    if abs(lower_price - target) <= scale_tolerance:
        return 0.0, {"method": "lower_bound", "iterations": 0, "residual": lower_price - target, "converged": True}
    high = BLACK_SCHOLES_CONTRACT["numeric"]["ivMaxVolatility"]
    high_price = _option(data["spot"], data["strike"], data["maturityYears"], data["riskFreeRate"], data["dividendYield"], high, data["optionType"])["unitPrice"]
    if target > high_price + scale_tolerance:
        raise ValueError(f"marketPrice requires volatility above the supported maximum {high}.")
    low = 0.0
    residual = high_price - target
    for iteration in range(1, BLACK_SCHOLES_CONTRACT["numeric"]["ivMaxIterations"] + 1):
        mid = (low + high) / 2.0
        price = _option(data["spot"], data["strike"], data["maturityYears"], data["riskFreeRate"], data["dividendYield"], mid, data["optionType"])["unitPrice"]
        residual = price - target
        if abs(residual) <= scale_tolerance:
            return mid, {"method": "bisection", "iterations": iteration, "residual": residual, "converged": True}
        if residual > 0:
            high = mid
        else:
            low = mid
    raise ValueError(f"Implied-volatility bisection did not converge; residual={residual}.")


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
    raise ValueError("Canonical data contains an unsupported value.")


def _analysis_id(input_data: Mapping[str, Any]) -> str:
    text = json.dumps(_canonical_tree(input_data), ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _scaled(option: dict[str, Any], scale: float) -> dict[str, Any]:
    result = deepcopy(option)
    result["portfolioValue"] = option["unitPrice"] * scale
    result["portfolioGreeks"] = {key: value * scale for key, value in option["greeks"].items()}
    return result


def _scenario_rows(data: Mapping[str, Any], volatility: float, scale: float, base_value: float) -> list[dict[str, Any]]:
    spot_shift = data["shocks"]["spotPct"] / 100.0
    vol_shift = data["shocks"]["volPoints"] / 100.0
    time_shift = data["shocks"]["days"] / 365.0
    definitions = [
        ("base", data["spot"], volatility, data["maturityYears"]),
        ("spotDown", data["spot"] * (1.0 - spot_shift), volatility, data["maturityYears"]),
        ("spotUp", data["spot"] * (1.0 + spot_shift), volatility, data["maturityYears"]),
        ("volDown", data["spot"], max(0.0, volatility - vol_shift), data["maturityYears"]),
        ("volUp", data["spot"], volatility + vol_shift, data["maturityYears"]),
        ("timeForward", data["spot"], volatility, max(0.0, data["maturityYears"] - time_shift)),
    ]
    rows = []
    for name, spot, sigma, maturity in definitions:
        if spot < LIMITS["minSpot"] or spot > LIMITS["maxSpot"] or sigma > LIMITS["maxVolatility"]:
            raise ValueError(f"Scenario {name} is outside the supported numerical domain.")
        price = _option(spot, data["strike"], maturity, data["riskFreeRate"], data["dividendYield"], sigma, data["optionType"])["unitPrice"]
        portfolio = price * scale
        rows.append({"scenario": name, "spot": spot, "volatility": sigma, "maturityYears": maturity, "unitPrice": price, "portfolioValue": portfolio, "pnl": portfolio - base_value})
    return rows


def _linspace(low: float, high: float, count: int) -> list[float]:
    return [low + (high - low) * index / (count - 1) for index in range(count)]


def _sensitivities(data: Mapping[str, Any], volatility: float, scale: float) -> dict[str, list[dict[str, float]]]:
    count = LIMITS["sensitivityPoints"]
    axes = {
        "spot": _linspace(data["spot"] * 0.6, data["spot"] * 1.4, count),
        "volatility": _linspace(max(0.0, volatility - 0.10), min(LIMITS["maxVolatility"], volatility + 0.10), count),
        "maturity": _linspace(0.0, min(LIMITS["maxMaturityYears"], max(data["maturityYears"] * 2.0, 1.0)), count),
    }
    output: dict[str, list[dict[str, float]]] = {}
    for axis, values in axes.items():
        rows = []
        for x in values:
            spot = x if axis == "spot" else data["spot"]
            sigma = x if axis == "volatility" else volatility
            maturity = x if axis == "maturity" else data["maturityYears"]
            price = _option(spot, data["strike"], maturity, data["riskFreeRate"], data["dividendYield"], sigma, data["optionType"])["unitPrice"]
            rows.append({"x": x, "unitPrice": price, "portfolioValue": price * scale})
        output[axis] = rows
    return output


def analyze_black_scholes(raw: Any) -> dict[str, Any]:
    data = normalize_black_scholes_input(raw)
    if data["quoteMode"] == "market_price":
        volatility, solver = _implied_volatility(data)
    else:
        volatility, solver = data["volatility"], None
    sign = 1.0 if data["position"] == "long" else -1.0
    scale = sign * data["quantity"] * data["multiplier"]
    call = _scaled(_option(data["spot"], data["strike"], data["maturityYears"], data["riskFreeRate"], data["dividendYield"], volatility, "call"), scale)
    put = _scaled(_option(data["spot"], data["strike"], data["maturityYears"], data["riskFreeRate"], data["dividendYield"], volatility, "put"), scale)
    selected = deepcopy(call if data["optionType"] == "call" else put)
    lhs = call["unitPrice"] - put["unitPrice"]
    rhs = data["spot"] * math.exp(-data["dividendYield"] * data["maturityYears"]) - data["strike"] * math.exp(-data["riskFreeRate"] * data["maturityYears"])
    residual = lhs - rhs
    parity_tolerance = BLACK_SCHOLES_CONTRACT["numeric"]["parityTolerance"] * max(1.0, abs(lhs), abs(rhs))
    analysis_id = _analysis_id(data)
    result = {
        "schemaVersion": BLACK_SCHOLES_SCHEMA_VERSION,
        "engineVersion": BLACK_SCHOLES_ENGINE_VERSION,
        "analysisId": analysis_id,
        "input": data,
        "quote": {"mode": data["quoteMode"], "observedMarketPrice": data["marketPrice"], "impliedVolatility": volatility, "solver": solver},
        "call": call,
        "put": put,
        "selected": selected,
        "parity": {"lhs": lhs, "rhs": rhs, "residual": residual, "holds": abs(residual) <= parity_tolerance},
        "scenarios": _scenario_rows(data, volatility, scale, selected["portfolioValue"]),
        "sensitivities": _sensitivities(data, volatility, scale),
        "conventions": deepcopy(BLACK_SCHOLES_CONTRACT["conventions"]),
    }
    return result


def _export_number(value: float) -> str:
    converted = float(value)
    if not math.isfinite(converted):
        raise ValueError("Evidence export contains a non-finite number.")
    if converted == 0 or abs(converted) < 1e-15:
        return "0"
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


def build_black_scholes_scenario_csv(result: Mapping[str, Any]) -> str:
    if result.get("schemaVersion") != BLACK_SCHOLES_SCHEMA_VERSION:
        raise ValueError("Expected a canonical Black-Scholes analysis result.")
    rows = [{"schemaVersion": BLACK_SCHOLES_SCENARIO_CSV_SCHEMA, "engineVersion": result["engineVersion"], "analysisId": result["analysisId"], **row} for row in result["scenarios"]]
    return _csv(BLACK_SCHOLES_CONTRACT["exports"]["scenarioCsvHeaders"], rows)


def build_black_scholes_sensitivity_csv(result: Mapping[str, Any]) -> str:
    if result.get("schemaVersion") != BLACK_SCHOLES_SCHEMA_VERSION:
        raise ValueError("Expected a canonical Black-Scholes analysis result.")
    rows = []
    for axis in BLACK_SCHOLES_CONTRACT["sensitivities"]:
        rows.extend({"schemaVersion": BLACK_SCHOLES_SENSITIVITY_CSV_SCHEMA, "engineVersion": result["engineVersion"], "analysisId": result["analysisId"], "axis": axis, **row} for row in result["sensitivities"][axis])
    return _csv(BLACK_SCHOLES_CONTRACT["exports"]["sensitivityCsvHeaders"], rows)


def build_black_scholes_json(result: Mapping[str, Any]) -> str:
    if result.get("schemaVersion") != BLACK_SCHOLES_SCHEMA_VERSION:
        raise ValueError("Expected a canonical Black-Scholes analysis result.")
    return json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + "\n"


def _write_stdout(output: str) -> None:
    sys.stdout.buffer.write(output.encode("utf-8"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run canonical F-CAL10 Black-Scholes analysis.")
    parser.add_argument("input_path", nargs="?", help="Input JSON path; stdin when omitted.")
    parser.add_argument("--input", dest="named_input", help="Explicit input JSON path.")
    parser.add_argument("--contract", action="store_true", help="Print the canonical contract and exit.")
    parser.add_argument("--format", choices=("json", "scenario-csv", "sensitivity-csv"), default="json")
    args = parser.parse_args(argv)
    try:
        if args.contract:
            if args.input_path or args.named_input:
                raise ValueError("--contract cannot be combined with an input path.")
            _write_stdout(json.dumps(BLACK_SCHOLES_CONTRACT, ensure_ascii=False, separators=(",", ":")) + "\n")
            return 0
        if args.input_path and args.named_input:
            raise ValueError("Use either positional input or --input, not both.")
        input_path = args.named_input or args.input_path
        text = Path(input_path).read_text(encoding="utf-8") if input_path else sys.stdin.read()
        if len(text.encode("utf-8")) > LIMITS["maxInputBytes"]:
            raise ValueError("Input exceeds maxInputBytes.")
        result = analyze_black_scholes(json.loads(text))
        output = build_black_scholes_json(result) if args.format == "json" else (build_black_scholes_scenario_csv(result) if args.format == "scenario-csv" else build_black_scholes_sensitivity_csv(result))
        _write_stdout(output)
        return 0
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
