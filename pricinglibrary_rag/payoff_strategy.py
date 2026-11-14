"""Canonical backend engine for European vanilla payoff strategies (F-CAL-5).

The browser mirror is ``src/lib/payoffStrategy.mjs``.  Keep the public result,
the canonical input text, the A&S normal CDF and the CSV formats byte-compatible
with that implementation.  Bounds and break-even points are derived from the
piecewise-linear terminal P&L; the display curve never drives risk metrics.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any, Mapping, Sequence


PAYOFF_STRATEGY_ENGINE_VERSION = "1.0.1"
PAYOFF_STRATEGY_SCHEMA_VERSION = "tpl.payoff-strategy.analysis.v1"
PAYOFF_STRATEGY_CURVE_CSV_SCHEMA = "tpl.payoff-strategy.curve.v1"
PAYOFF_STRATEGY_SCENARIO_CSV_SCHEMA = "tpl.payoff-strategy.scenarios.v1"

PAYOFF_STRATEGY_CONTRACT: dict[str, Any] = {
    "schemaVersion": "tpl.payoff-strategy.contract.v1",
    "analysisSchemaVersion": PAYOFF_STRATEGY_SCHEMA_VERSION,
    "engineVersion": PAYOFF_STRATEGY_ENGINE_VERSION,
    "limits": {
        "maxInputBytes": 1_000_000,
        "maxLegs": 20,
        "maxIdentifierLength": 64,
        "maxCurrencyLength": 3,
        "minSpot": 1e-8,
        "maxSpot": 1_000_000_000,
        "minStrike": 1e-8,
        "maxStrike": 1_000_000_000,
        "maxPremium": 1_000_000_000,
        "maxQuantity": 1_000_000,
        "minContractMultiplier": 1e-8,
        "maxContractMultiplier": 1_000_000_000,
        "minMaturityYears": 1e-8,
        "maxMaturityYears": 100,
        "minVolatility": 1e-6,
        "maxVolatility": 5,
        "minRate": -1,
        "maxRate": 1,
        "minGridPoints": 101,
        "maxGridPoints": 2001,
    },
    "enums": {
        "optionTypes": ["call", "put"],
        "sides": ["long", "short"],
        "premiumSources": ["model", "manual"],
        "boundKinds": ["finite", "unlimited"],
    },
    "units": {
        "spotStrikePremium": "currency per underlying unit",
        "quantity": "positive integer contracts",
        "contractMultiplier": "underlying units per contract",
        "volatilityRatesDividendYield": "decimal",
        "maturity": "years",
        "pnlPrice": "currency",
        "delta": "currency P&L per +1 spot unit",
        "gamma": "currency P&L per +1 spot-unit squared",
        "vega": "currency P&L per +1 volatility point",
        "theta": "currency P&L per calendar day",
        "rho": "currency P&L per +1 rate point",
    },
    "numeric": {
        "comparisonTolerance": 1e-12,
        "zeroTolerance": 1e-10,
        "exportSignificantDigits": 12,
        "hashSignificantDigits": 17,
    },
    "exports": {
        "curveCsvSchema": PAYOFF_STRATEGY_CURVE_CSV_SCHEMA,
        "scenarioCsvSchema": PAYOFF_STRATEGY_SCENARIO_CSV_SCHEMA,
        "curveHeaders": [
            "schemaVersion",
            "engineVersion",
            "analysisId",
            "terminalSpot",
            "grossPayoff",
            "terminalPnl",
        ],
        "scenarioHeaders": [
            "schemaVersion",
            "engineVersion",
            "analysisId",
            "terminalSpot",
            "grossPayoff",
            "terminalPnl",
            "legContributions",
        ],
    },
}

LIMITS = PAYOFF_STRATEGY_CONTRACT["limits"]
ZERO = PAYOFF_STRATEGY_CONTRACT["numeric"]["zeroTolerance"]
INPUT_KEYS = frozenset(
    {
        "spot",
        "volatility",
        "timeToMaturity",
        "riskFreeRate",
        "dividendYield",
        "currency",
        "contractMultiplier",
        "gridPoints",
        "legs",
    }
)
LEG_KEYS = frozenset(
    {"id", "type", "side", "strike", "quantity", "premiumSource", "manualPremium"}
)


def payoff_strategy_contract_snapshot() -> dict[str, Any]:
    """Return the runtime contract as an isolated value for parity tests/CLI."""

    return deepcopy(PAYOFF_STRATEGY_CONTRACT)


def _assert_plain_object(value: Any, label: str) -> Mapping[str, Any]:
    if type(value) is not dict:
        raise ValueError(f"{label} must be a plain object.")
    return value


def _assert_exact_keys(
    value: Mapping[str, Any], allowed: frozenset[str], required: Sequence[str], label: str
) -> None:
    unknown = sorted(set(value) - allowed)
    missing = sorted(key for key in required if key not in value)
    if unknown or missing:
        raise ValueError(
            f"{label} schema is invalid; missing={'|'.join(missing) or 'none'}; "
            f"unknown={'|'.join(unknown) or 'none'}."
        )


def _finite_number(
    value: Any,
    label: str,
    *,
    minimum: float = -math.inf,
    maximum: float = math.inf,
    exclusive_minimum: bool = False,
) -> int | float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"{label} must be a finite number.")
    if (value <= minimum if exclusive_minimum else value < minimum) or value > maximum:
        raise ValueError(f"{label} is outside the supported domain.")
    return 0 if value == 0 else value


def _canonical_number(value: int | float) -> str:
    """Mirror JS ``Number.toExponential(16)`` (17 significant digits)."""

    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError("Canonical input contains a non-finite number.")
    if value == 0:
        return "0"
    mantissa, exponent = format(value, ".16e").lower().split("e")
    mantissa = mantissa.rstrip("0").rstrip(".")
    return f"{mantissa}e{int(exponent)}"


def _export_number(value: int | float) -> str:
    """Mirror JS ``Number.toExponential(11)`` (12 significant digits)."""

    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError("Evidence export contains a non-finite number.")
    if value == 0 or abs(value) < 1e-15:
        return "0"
    mantissa, exponent = format(value, ".11e").lower().split("e")
    mantissa = mantissa.rstrip("0").rstrip(".")
    return f"{mantissa}e{int(exponent)}"


def _assert_finite_tree(value: Any, path: str = "result") -> None:
    if isinstance(value, bool) or value is None or isinstance(value, str):
        return
    if isinstance(value, (int, float)):
        if not math.isfinite(value):
            raise ValueError(f"{path} contains a non-finite number.")
        return
    if isinstance(value, list):
        for index, item in enumerate(value):
            _assert_finite_tree(item, f"{path}[{index}]")
        return
    if isinstance(value, Mapping):
        for key, item in value.items():
            _assert_finite_tree(item, f"{path}.{key}")


def norm_cdf(raw_x: float) -> float:
    """Deterministic A&S normal CDF, deliberately identical to the JS engine."""

    a1, a2, a3, a4, a5 = (
        0.254829592,
        -0.284496736,
        1.421413741,
        -1.453152027,
        1.061405429,
    )
    sign = -1 if raw_x < 0 else 1
    x = abs(raw_x) / math.sqrt(2)
    t = 1 / (1 + 0.3275911 * x)
    erf = 1 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * math.exp(-x * x)
    return 0.5 * (1 + sign * erf)


def _norm_pdf(x: float) -> float:
    return math.exp(-0.5 * x * x) / math.sqrt(2 * math.pi)


def black_scholes_leg(raw: Mapping[str, Any]) -> dict[str, Any]:
    """Price one already-validated European vanilla leg under BSM."""

    spot = raw["spot"]
    strike = raw["strike"]
    time_to_maturity = raw["timeToMaturity"]
    risk_free_rate = raw["riskFreeRate"]
    dividend_yield = raw["dividendYield"]
    volatility = raw["volatility"]
    option_type = raw["type"]
    sqrt_t = math.sqrt(time_to_maturity)
    d1 = (
        math.log(spot / strike)
        + (risk_free_rate - dividend_yield + 0.5 * volatility * volatility)
        * time_to_maturity
    ) / (volatility * sqrt_t)
    d2 = d1 - volatility * sqrt_t
    discounted_spot = spot * math.exp(-dividend_yield * time_to_maturity)
    discounted_strike = strike * math.exp(-risk_free_rate * time_to_maturity)
    density = _norm_pdf(d1)
    if option_type == "call":
        price = discounted_spot * norm_cdf(d1) - discounted_strike * norm_cdf(d2)
        delta = math.exp(-dividend_yield * time_to_maturity) * norm_cdf(d1)
        theta_annual = (
            -(discounted_spot * density * volatility) / (2 * sqrt_t)
            - risk_free_rate * discounted_strike * norm_cdf(d2)
            + dividend_yield * discounted_spot * norm_cdf(d1)
        )
        rho_per_point = (
            strike
            * time_to_maturity
            * math.exp(-risk_free_rate * time_to_maturity)
            * norm_cdf(d2)
            / 100
        )
    else:
        price = discounted_strike * norm_cdf(-d2) - discounted_spot * norm_cdf(-d1)
        delta = -math.exp(-dividend_yield * time_to_maturity) * norm_cdf(-d1)
        theta_annual = (
            -(discounted_spot * density * volatility) / (2 * sqrt_t)
            + risk_free_rate * discounted_strike * norm_cdf(-d2)
            - dividend_yield * discounted_spot * norm_cdf(-d1)
        )
        rho_per_point = (
            -strike
            * time_to_maturity
            * math.exp(-risk_free_rate * time_to_maturity)
            * norm_cdf(-d2)
            / 100
        )
    result = {
        "price": price,
        "greeks": {
            "delta": delta,
            "gamma": math.exp(-dividend_yield * time_to_maturity)
            * density
            / (spot * volatility * sqrt_t),
            "vega": discounted_spot * density * sqrt_t / 100,
            "theta": theta_annual / 365,
            "rho": rho_per_point,
        },
        "d1": d1,
        "d2": d2,
    }
    _assert_finite_tree(result, "Black-Scholes result")
    return result


def normalize_payoff_strategy_input(raw: Mapping[str, Any]) -> dict[str, Any]:
    raw = _assert_plain_object(raw, "strategy input")
    required = [
        "spot",
        "volatility",
        "timeToMaturity",
        "riskFreeRate",
        "dividendYield",
        "currency",
        "contractMultiplier",
        "gridPoints",
        "legs",
    ]
    _assert_exact_keys(raw, INPUT_KEYS, required, "strategy input")
    spot = _finite_number(raw["spot"], "spot", minimum=LIMITS["minSpot"], maximum=LIMITS["maxSpot"])
    volatility = _finite_number(raw["volatility"], "volatility", minimum=LIMITS["minVolatility"], maximum=LIMITS["maxVolatility"])
    time_to_maturity = _finite_number(raw["timeToMaturity"], "timeToMaturity", minimum=LIMITS["minMaturityYears"], maximum=LIMITS["maxMaturityYears"])
    risk_free_rate = _finite_number(raw["riskFreeRate"], "riskFreeRate", minimum=LIMITS["minRate"], maximum=LIMITS["maxRate"])
    dividend_yield = _finite_number(raw["dividendYield"], "dividendYield", minimum=LIMITS["minRate"], maximum=LIMITS["maxRate"])
    contract_multiplier = _finite_number(raw["contractMultiplier"], "contractMultiplier", minimum=LIMITS["minContractMultiplier"], maximum=LIMITS["maxContractMultiplier"])
    currency = raw["currency"]
    if not isinstance(currency, str) or len(currency) != 3 or not currency.isascii() or not currency.isalpha() or currency.upper() != currency:
        raise ValueError("currency must be an uppercase three-letter code.")
    grid_points = raw["gridPoints"]
    if isinstance(grid_points, bool) or not isinstance(grid_points, int) or not -(2**53 - 1) <= grid_points <= 2**53 - 1 or grid_points < LIMITS["minGridPoints"] or grid_points > LIMITS["maxGridPoints"] or grid_points % 2 == 0:
        raise ValueError(
            f"gridPoints must be an odd safe integer between {LIMITS['minGridPoints']} and {LIMITS['maxGridPoints']}."
        )
    raw_legs = raw["legs"]
    if not isinstance(raw_legs, list) or len(raw_legs) < 1 or len(raw_legs) > LIMITS["maxLegs"]:
        raise ValueError(f"legs must contain between 1 and {LIMITS['maxLegs']} entries.")
    ids: set[str] = set()
    legs: list[dict[str, Any]] = []
    for index, raw_leg in enumerate(raw_legs):
        leg = _assert_plain_object(raw_leg, f"leg {index + 1}")
        required_leg = ["id", "type", "side", "strike", "quantity", "premiumSource", "manualPremium"]
        _assert_exact_keys(leg, LEG_KEYS, required_leg, f"leg {index + 1}")
        identifier = leg["id"]
        if (
            not isinstance(identifier, str)
            or not 1 <= len(identifier) <= LIMITS["maxIdentifierLength"]
            or not identifier[0].isascii()
            or not identifier[0].isalnum()
            or any(not (char.isascii() and (char.isalnum() or char in "._-")) for char in identifier)
        ):
            raise ValueError(f"leg {index + 1} id is invalid.")
        if identifier in ids:
            raise ValueError(f"leg id '{identifier}' is duplicated.")
        ids.add(identifier)
        option_type = leg["type"]
        side = leg["side"]
        premium_source = leg["premiumSource"]
        if option_type not in PAYOFF_STRATEGY_CONTRACT["enums"]["optionTypes"]:
            raise ValueError(f"leg {identifier} type is unsupported.")
        if side not in PAYOFF_STRATEGY_CONTRACT["enums"]["sides"]:
            raise ValueError(f"leg {identifier} side is unsupported.")
        if premium_source not in PAYOFF_STRATEGY_CONTRACT["enums"]["premiumSources"]:
            raise ValueError(f"leg {identifier} premiumSource is unsupported.")
        strike = _finite_number(leg["strike"], f"leg {identifier} strike", minimum=LIMITS["minStrike"], maximum=LIMITS["maxStrike"])
        quantity = leg["quantity"]
        if isinstance(quantity, bool) or not isinstance(quantity, int) or not -(2**53 - 1) <= quantity <= 2**53 - 1 or quantity < 1 or quantity > LIMITS["maxQuantity"]:
            raise ValueError(f"leg {identifier} quantity must be a positive safe integer.")
        manual_premium = None
        if premium_source == "manual":
            manual_premium = _finite_number(leg["manualPremium"], f"leg {identifier} manualPremium", minimum=0, maximum=LIMITS["maxPremium"])
        elif leg["manualPremium"] is not None:
            raise ValueError(f"leg {identifier} manualPremium must be null when premiumSource is model.")
        legs.append(
            {
                "id": identifier,
                "type": option_type,
                "side": side,
                "strike": strike,
                "quantity": quantity,
                "premiumSource": premium_source,
                "manualPremium": manual_premium,
            }
        )
    result = {
        "spot": spot,
        "volatility": volatility,
        "timeToMaturity": time_to_maturity,
        "riskFreeRate": risk_free_rate,
        "dividendYield": dividend_yield,
        "currency": currency,
        "contractMultiplier": contract_multiplier,
        "gridPoints": grid_points,
        "legs": legs,
    }
    _assert_finite_tree(result)
    return result


def _canonical_input_text(input_data: Mapping[str, Any]) -> str:
    rows = [
        PAYOFF_STRATEGY_SCHEMA_VERSION,
        f"spot={_canonical_number(input_data['spot'])}",
        f"volatility={_canonical_number(input_data['volatility'])}",
        f"timeToMaturity={_canonical_number(input_data['timeToMaturity'])}",
        f"riskFreeRate={_canonical_number(input_data['riskFreeRate'])}",
        f"dividendYield={_canonical_number(input_data['dividendYield'])}",
        f"currency={input_data['currency']}",
        f"contractMultiplier={_canonical_number(input_data['contractMultiplier'])}",
        f"gridPoints={input_data['gridPoints']}",
    ]
    rows.extend(
        "leg="
        + "|".join(
            [
                leg["id"],
                leg["type"],
                leg["side"],
                _canonical_number(leg["strike"]),
                str(leg["quantity"]),
                leg["premiumSource"],
                "null" if leg["manualPremium"] is None else _canonical_number(leg["manualPremium"]),
            ]
        )
        for leg in input_data["legs"]
    )
    return "\n".join(rows) + "\n"


def _unique_sorted(values: Sequence[int | float]) -> list[int | float]:
    normalized = [0 if abs(value) < ZERO else value for value in values]
    return sorted(set(normalized))


def _direction_of(side: str) -> int:
    return 1 if side == "long" else -1


def _strategy_values_at(terminal_spot: int | float, legs: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    gross_payoff = 0
    terminal_pnl = 0
    contributions: list[dict[str, Any]] = []
    for leg in legs:
        intrinsic = max(terminal_spot - leg["strike"], 0) if leg["type"] == "call" else max(leg["strike"] - terminal_spot, 0)
        gross = leg["direction"] * leg["scale"] * intrinsic
        pnl = gross - leg["direction"] * leg["scale"] * leg["entryPremium"]
        gross_payoff += gross
        terminal_pnl += pnl
        contributions.append({"id": leg["id"], "grossPayoff": gross, "terminalPnl": pnl})
    return {
        "terminalSpot": terminal_spot,
        "grossPayoff": gross_payoff,
        "terminalPnl": terminal_pnl,
        "legContributions": contributions,
    }


def _coefficients_at(terminal_spot: int | float, legs: Sequence[Mapping[str, Any]]) -> tuple[int | float, int | float]:
    slope = 0
    intercept = 0
    for leg in legs:
        intercept -= leg["direction"] * leg["scale"] * leg["entryPremium"]
        if leg["type"] == "call" and terminal_spot > leg["strike"]:
            slope += leg["direction"] * leg["scale"]
            intercept -= leg["direction"] * leg["scale"] * leg["strike"]
        if leg["type"] == "put" and terminal_spot < leg["strike"]:
            slope -= leg["direction"] * leg["scale"]
            intercept += leg["direction"] * leg["scale"] * leg["strike"]
    return slope, intercept


def _piecewise_analysis(legs: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    boundaries = _unique_sorted([0, *(leg["strike"] for leg in legs)])
    segments: list[dict[str, Any]] = []
    breakevens: list[int | float] = []
    zero_intervals: list[dict[str, Any]] = []
    for index, lower_spot in enumerate(boundaries):
        upper_spot = boundaries[index + 1] if index + 1 < len(boundaries) else None
        probe = lower_spot + max(1, lower_spot * 0.1) if upper_spot is None else (lower_spot + upper_spot) / 2
        slope, intercept = _coefficients_at(probe, legs)
        lower_pnl = slope * lower_spot + intercept
        upper_pnl = None if upper_spot is None else slope * upper_spot + intercept
        segments.append(
            {
                "lowerSpot": lower_spot,
                "upperSpot": upper_spot,
                "slope": slope,
                "intercept": intercept,
                "lowerPnl": lower_pnl,
                "upperPnl": upper_pnl,
            }
        )
        if abs(slope) <= ZERO and abs(intercept) <= ZERO:
            zero_intervals.append({"lowerSpot": lower_spot, "upperSpot": upper_spot})
        if abs(slope) > ZERO:
            root = -intercept / slope
            inside = root >= lower_spot - ZERO and (upper_spot is None or root <= upper_spot + ZERO)
            if inside and root >= -ZERO:
                breakevens.append(max(0, root))
    exact_breakevens: list[int | float] = []
    for value in _unique_sorted(breakevens):
        if not exact_breakevens or abs(value - exact_breakevens[-1]) > ZERO:
            exact_breakevens.append(value)
    candidate_pnls = [_strategy_values_at(spot, legs)["terminalPnl"] for spot in boundaries]
    terminal_slope = segments[-1]["slope"]
    max_profit = (
        {"kind": "unlimited", "amount": None}
        if terminal_slope > ZERO
        else {"kind": "finite", "amount": max(0, *candidate_pnls)}
    )
    max_loss = (
        {"kind": "unlimited", "amount": None}
        if terminal_slope < -ZERO
        else {"kind": "finite", "amount": max(0, -min(0, *candidate_pnls))}
    )
    return {
        "segments": segments,
        "breakevens": exact_breakevens,
        "zeroIntervals": zero_intervals,
        "bounds": {"maxProfit": max_profit, "maxLoss": max_loss},
    }


def analyze_payoff_strategy(raw_input: Mapping[str, Any]) -> dict[str, Any]:
    input_data = normalize_payoff_strategy_input(raw_input)
    analysis_id = hashlib.sha256(_canonical_input_text(input_data).encode("utf-8")).hexdigest()
    legs: list[dict[str, Any]] = []
    for leg in input_data["legs"]:
        model = black_scholes_leg({**input_data, "strike": leg["strike"], "type": leg["type"]})
        direction = _direction_of(leg["side"])
        scale = leg["quantity"] * input_data["contractMultiplier"]
        entry_premium = model["price"] if leg["premiumSource"] == "model" else leg["manualPremium"]
        legs.append(
            {
                **leg,
                "direction": direction,
                "scale": scale,
                "modelPremium": model["price"],
                "entryPremium": entry_premium,
                "modelValue": direction * scale * model["price"],
                "entryPremiumAmount": direction * scale * entry_premium,
                "greeks": {
                    key: direction * scale * value for key, value in model["greeks"].items()
                },
            }
        )
    piecewise = _piecewise_analysis(legs)
    important = [
        0,
        input_data["spot"],
        *(leg["strike"] for leg in legs),
        *piecewise["breakevens"],
    ]
    maximum_strike = max(leg["strike"] for leg in legs)
    maximum_breakeven = max(piecewise["breakevens"], default=0)
    maximum_spot = max(
        input_data["spot"] * 2,
        maximum_strike * 1.5,
        maximum_breakeven * 1.1,
        1,
    )
    regular_grid = [
        maximum_spot * index / (input_data["gridPoints"] - 1)
        for index in range(input_data["gridPoints"])
    ]
    curve = []
    for spot in _unique_sorted([*regular_grid, *(value for value in important if value <= maximum_spot)]):
        point = _strategy_values_at(spot, legs)
        curve.append(
            {
                "terminalSpot": point["terminalSpot"],
                "grossPayoff": point["grossPayoff"],
                "terminalPnl": point["terminalPnl"],
            }
        )
    scenario_spots = _unique_sorted(
        [
            0,
            input_data["spot"] * 0.5,
            input_data["spot"] * 0.75,
            input_data["spot"],
            input_data["spot"] * 1.25,
            input_data["spot"] * 1.5,
            input_data["spot"] * 2,
            *(leg["strike"] for leg in legs),
            *piecewise["breakevens"],
        ]
    )
    scenarios = [_strategy_values_at(spot, legs) for spot in scenario_spots]
    net_entry_premium = sum(leg["entryPremiumAmount"] for leg in legs)
    current_model_value = sum(leg["modelValue"] for leg in legs)
    at_spot = _strategy_values_at(input_data["spot"], legs)
    greeks = {
        key: sum(leg["greeks"][key] for leg in legs)
        for key in ["delta", "gamma", "vega", "theta", "rho"]
    }
    manual_count = sum(leg["premiumSource"] == "manual" for leg in legs)
    return {
        "schemaVersion": PAYOFF_STRATEGY_SCHEMA_VERSION,
        "engineVersion": PAYOFF_STRATEGY_ENGINE_VERSION,
        "analysisId": analysis_id,
        "input": input_data,
        "legs": legs,
        "summary": {
            "grossPayoffAtSpot": at_spot["grossPayoff"],
            "terminalPnlAtSpot": at_spot["terminalPnl"],
            "netEntryPremium": net_entry_premium,
            "entryCashflow": -net_entry_premium,
            "currentModelValue": current_model_value,
            "inceptionModelPnl": current_model_value - net_entry_premium,
        },
        "greeks": greeks,
        "bounds": piecewise["bounds"],
        "breakevens": piecewise["breakevens"],
        "zeroIntervals": piecewise["zeroIntervals"],
        "segments": piecewise["segments"],
        "curve": curve,
        "scenarios": scenarios,
        "diagnostics": {
            "warnings": [
                *(
                    [
                        {
                            "code": "MANUAL_PREMIUM",
                            "message": f"{manual_count} leg(s) use user-entered premiums; they are not live market quotes.",
                        }
                    ]
                    if manual_count
                    else []
                ),
                {
                    "code": "EUROPEAN_TERMINAL_ONLY",
                    "message": "Terminal P&L covers European vanilla exercise only; no early exercise, margin, costs or path dependence.",
                },
            ],
            "manualPremiumLegCount": manual_count,
        },
        "conventions": {
            "priceModel": "Black-Scholes-Merton European vanilla",
            "terminalDomain": "S_T >= 0",
            "premiumRule": "terminalPnl = signed intrinsic payoff - signed entry premium",
            "marketDataStatus": "user assumptions only; no live quote or market-data request",
            "greekUnits": PAYOFF_STRATEGY_CONTRACT["units"],
            "limitations": [
                "European exercise only",
                "constant volatility by strike and maturity",
                "no transaction costs",
                "no margin or liquidity model",
                "no early exercise or path dependence",
            ],
        },
    }


def _write_csv(headers: Sequence[str], rows: Sequence[Sequence[Any]]) -> str:
    stream = io.StringIO(newline="")
    writer = csv.writer(stream, lineterminator="\n")
    writer.writerow(headers)
    writer.writerows(rows)
    return stream.getvalue()


def build_payoff_curve_csv(result: Mapping[str, Any]) -> str:
    if not isinstance(result, Mapping) or result.get("schemaVersion") != PAYOFF_STRATEGY_SCHEMA_VERSION or not isinstance(result.get("curve"), list):
        raise ValueError("Invalid payoff-strategy result.")
    rows = [
        [
            PAYOFF_STRATEGY_CURVE_CSV_SCHEMA,
            result["engineVersion"],
            result["analysisId"],
            _export_number(point["terminalSpot"]),
            _export_number(point["grossPayoff"]),
            _export_number(point["terminalPnl"]),
        ]
        for point in result["curve"]
    ]
    return _write_csv(PAYOFF_STRATEGY_CONTRACT["exports"]["curveHeaders"], rows)


def build_payoff_scenario_csv(result: Mapping[str, Any]) -> str:
    if not isinstance(result, Mapping) or result.get("schemaVersion") != PAYOFF_STRATEGY_SCHEMA_VERSION or not isinstance(result.get("scenarios"), list):
        raise ValueError("Invalid payoff-strategy result.")
    rows = []
    for point in result["scenarios"]:
        contributions = "|".join(
            f"{leg['id']}:{_export_number(leg['terminalPnl'])}"
            for leg in point["legContributions"]
        )
        rows.append(
            [
                PAYOFF_STRATEGY_SCENARIO_CSV_SCHEMA,
                result["engineVersion"],
                result["analysisId"],
                _export_number(point["terminalSpot"]),
                _export_number(point["grossPayoff"]),
                _export_number(point["terminalPnl"]),
                contributions,
            ]
        )
    return _write_csv(PAYOFF_STRATEGY_CONTRACT["exports"]["scenarioHeaders"], rows)


def build_payoff_json(result: Mapping[str, Any]) -> str:
    if not isinstance(result, Mapping) or result.get("schemaVersion") != PAYOFF_STRATEGY_SCHEMA_VERSION:
        raise ValueError("Invalid payoff-strategy result.")
    _assert_finite_tree(result)
    return json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False) + "\n"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Analyze a canonical F-CAL-5 payoff strategy.")
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--input", type=Path, help="Strict strategy JSON input.")
    action.add_argument("--contract", action="store_true", help="Print the runtime contract snapshot.")
    parser.add_argument(
        "--format",
        choices=("json", "curve-csv", "scenario-csv"),
        default="json",
        help="Evidence format for --input (default: json).",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        if args.contract:
            output = json.dumps(payoff_strategy_contract_snapshot(), indent=2, ensure_ascii=False) + "\n"
        else:
            if args.input.stat().st_size > LIMITS["maxInputBytes"]:
                raise ValueError(f"input exceeds {LIMITS['maxInputBytes']} bytes.")
            raw = json.loads(args.input.read_text(encoding="utf-8"))
            result = analyze_payoff_strategy(raw)
            if args.format == "curve-csv":
                output = build_payoff_curve_csv(result)
            elif args.format == "scenario-csv":
                output = build_payoff_scenario_csv(result)
            else:
                output = build_payoff_json(result)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        print(f"payoff-strategy: {exc}", file=sys.stderr)
        return 2
    # Write canonical UTF-8 bytes so CLI evidence keeps LF line endings on
    # Windows and remains byte-identical to the browser/Node export.
    sys.stdout.buffer.write(output.encode("utf-8"))
    return 0


if __name__ == "__main__":  # pragma: no cover - exercised by subprocess test
    raise SystemExit(main())
