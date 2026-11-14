"""Canonical Cox-Ross-Rubinstein option lattice for F-CAL-7.

Mirrors ``WEBSITE/thepricinglab/src/lib/binomial.mjs``. Inputs are strict,
CRR probabilities are never clamped, and all evidence exports use LF endings.
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


BINOMIAL_INPUT_SCHEMA = "tpl.binomial.input.v1"
BINOMIAL_SCHEMA_VERSION = "tpl.binomial.analysis.v1"
BINOMIAL_ENGINE_VERSION = "1.0.0"
BINOMIAL_CONVERGENCE_CSV_SCHEMA = "tpl.binomial.convergence.v1"
BINOMIAL_FRONTIER_CSV_SCHEMA = "tpl.binomial.frontier.v1"

BINOMIAL_CONTRACT: dict[str, Any] = {
    "schemaVersion": "tpl.binomial.contract.v1",
    "inputSchemaVersion": BINOMIAL_INPUT_SCHEMA,
    "analysisSchemaVersion": BINOMIAL_SCHEMA_VERSION,
    "engineVersion": BINOMIAL_ENGINE_VERSION,
    "model": "cox_ross_rubinstein",
    "measure": "risk_neutral_Q",
    "dayCounts": ["ACT/365F"],
    "optionTypes": ["call", "put"],
    "exerciseStyles": ["european", "american"],
    "positions": ["long", "short"],
    "limits": {
        "maxInputBytes": 1_000_000, "minSpot": 1e-8, "maxSpot": 1_000_000_000_000,
        "minStrike": 1e-8, "maxStrike": 1_000_000_000_000, "minVolatility": 0,
        "maxVolatility": 5, "minMaturityYears": 0, "maxMaturityYears": 30,
        "minRate": -1, "maxRate": 1, "minSteps": 2, "maxSteps": 2_000,
        "maxDisplayDepth": 6, "maxQuantity": 1_000_000,
        "minContractMultiplier": 1e-8, "maxContractMultiplier": 1_000_000_000_000,
    },
    "numeric": {"exerciseTolerance": 1e-12, "probabilityTolerance": 1e-14, "exportSignificantDigits": 9, "hashSignificantDigits": 17},
    "conventions": {
        "up": "exp(volatility * sqrt(dt))", "down": "1 / up",
        "probability": "(exp((risk_free_rate-dividend_yield)*dt)-down)/(up-down)",
        "discount": "exp(-risk_free_rate*dt)",
        "americanExercise": "max(intrinsic, discounted_risk_neutral_continuation)",
        "earlyExercisePremium": "american_price_minus_european_price",
        "zeroVolatility": "deterministic risk-neutral path with backward optimal stopping",
        "atExpiry": "exact intrinsic value", "vega": "price change per +1 volatility percentage point",
        "rho": "price change per +1 rate percentage point", "theta": "price change for one calendar day elapsed",
    },
    "exports": {
        "convergenceCsvSchema": BINOMIAL_CONVERGENCE_CSV_SCHEMA,
        "frontierCsvSchema": BINOMIAL_FRONTIER_CSV_SCHEMA,
        "convergenceCsvHeaders": ["schemaVersion", "engineVersion", "analysisId", "exerciseStyle", "optionType", "steps", "pricePerUnit", "europeanPricePerUnit", "blackScholesBenchmark", "absoluteBenchmarkError"],
        "frontierCsvHeaders": ["schemaVersion", "engineVersion", "analysisId", "optionType", "step", "timeYears", "boundarySpot", "exerciseNodeCount"],
        "lineEnding": "LF", "finalNewline": True, "numericFormat": "finite_significant_9",
    },
}

LIMITS = BINOMIAL_CONTRACT["limits"]
INPUT_KEYS = (
    "schemaVersion", "spot", "strike", "volatility", "maturityYears", "dayCount",
    "riskFreeRate", "dividendYield", "steps", "optionType", "exerciseStyle",
    "currency", "quantity", "contractMultiplier", "position",
)


def binomial_contract_snapshot() -> dict[str, Any]:
    return deepcopy(BINOMIAL_CONTRACT)


def _number(value: Any, label: str, minimum: float, maximum: float) -> float:
    if isinstance(value, bool) or type(value) not in (int, float):
        raise ValueError(f"{label} must be a finite number.")
    try:
        converted = float(value)
    except (OverflowError, ValueError):
        raise ValueError(f"{label} must be a finite number.") from None
    if not math.isfinite(converted):
        raise ValueError(f"{label} must be a finite number.")
    if converted < minimum or converted > maximum:
        raise ValueError(f"{label} is outside the supported domain.")
    return 0.0 if converted == 0 else converted


def _integer(value: Any, label: str, minimum: int, maximum: int) -> int:
    if type(value) is not int or value < minimum or value > maximum or abs(value) > 9_007_199_254_740_991:
        raise ValueError(f"{label} must be a safe integer between {minimum} and {maximum}.")
    return value


def _enum(value: Any, values: list[str], label: str) -> str:
    if value not in values:
        raise ValueError(f"{label} is unsupported.")
    return str(value)


def normalize_binomial_input(raw: Any) -> dict[str, Any]:
    if type(raw) is not dict:
        raise ValueError("Binomial input must be a plain object.")
    missing = sorted(set(INPUT_KEYS) - set(raw))
    unknown = sorted(set(raw) - set(INPUT_KEYS))
    if missing or unknown:
        raise ValueError(f"Binomial input schema is invalid; missing={'|'.join(missing) or 'none'}; unknown={'|'.join(unknown) or 'none'}.")
    if raw["schemaVersion"] != BINOMIAL_INPUT_SCHEMA:
        raise ValueError(f"schemaVersion must be '{BINOMIAL_INPUT_SCHEMA}'.")
    result = {
        "schemaVersion": BINOMIAL_INPUT_SCHEMA,
        "spot": _number(raw["spot"], "spot", LIMITS["minSpot"], LIMITS["maxSpot"]),
        "strike": _number(raw["strike"], "strike", LIMITS["minStrike"], LIMITS["maxStrike"]),
        "volatility": _number(raw["volatility"], "volatility", LIMITS["minVolatility"], LIMITS["maxVolatility"]),
        "maturityYears": _number(raw["maturityYears"], "maturityYears", LIMITS["minMaturityYears"], LIMITS["maxMaturityYears"]),
        "dayCount": _enum(raw["dayCount"], BINOMIAL_CONTRACT["dayCounts"], "dayCount"),
        "riskFreeRate": _number(raw["riskFreeRate"], "riskFreeRate", LIMITS["minRate"], LIMITS["maxRate"]),
        "dividendYield": _number(raw["dividendYield"], "dividendYield", LIMITS["minRate"], LIMITS["maxRate"]),
        "steps": _integer(raw["steps"], "steps", LIMITS["minSteps"], LIMITS["maxSteps"]),
        "optionType": _enum(raw["optionType"], BINOMIAL_CONTRACT["optionTypes"], "optionType"),
        "exerciseStyle": _enum(raw["exerciseStyle"], BINOMIAL_CONTRACT["exerciseStyles"], "exerciseStyle"),
        "currency": raw["currency"],
        "quantity": _integer(raw["quantity"], "quantity", 1, LIMITS["maxQuantity"]),
        "contractMultiplier": _number(raw["contractMultiplier"], "contractMultiplier", LIMITS["minContractMultiplier"], LIMITS["maxContractMultiplier"]),
        "position": _enum(raw["position"], BINOMIAL_CONTRACT["positions"], "position"),
    }
    if type(result["currency"]) is not str or len(result["currency"]) != 3 or not result["currency"].isalpha() or not result["currency"].isupper() or not result["currency"].isascii():
        raise ValueError("currency must be an uppercase three-letter code.")
    extreme_log = math.log(result["spot"]) + result["volatility"] * math.sqrt(result["maturityYears"] * result["steps"])
    if not math.isfinite(extreme_log) or extreme_log > 700:
        raise ValueError("spot/volatility/maturity/steps create an unsupported numerical tree range.")
    return result


def _intrinsic(spot: float, strike: float, option_type: str) -> float:
    return max(spot - strike, 0.0) if option_type == "call" else max(strike - spot, 0.0)


def _canonical_number(value: float) -> str:
    if not math.isfinite(value):
        raise ValueError("Canonical data contains a non-finite number.")
    if value == 0:
        return "0"
    mantissa, exponent = format(value, ".16e").lower().split("e")
    mantissa = mantissa.rstrip("0").rstrip(".")
    return f"{mantissa}e{int(exponent)}"


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
    text = json.dumps(_canonical_tree(input_data), ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _norm_cdf(raw_x: float) -> float:
    a = [0.254829592, -0.284496736, 1.421413741, -1.453152027, 1.061405429]
    sign = -1 if raw_x < 0 else 1
    x = abs(raw_x) / math.sqrt(2)
    t = 1 / (1 + 0.3275911 * x)
    erf = 1 - (((((a[4] * t + a[3]) * t) + a[2]) * t + a[1]) * t + a[0]) * t * math.exp(-x * x)
    return 0.5 * (1 + sign * erf)


def _black_scholes(input_data: Mapping[str, Any]) -> float:
    if input_data["maturityYears"] == 0:
        return _intrinsic(input_data["spot"], input_data["strike"], input_data["optionType"])
    if input_data["volatility"] == 0:
        terminal = input_data["spot"] * math.exp((input_data["riskFreeRate"] - input_data["dividendYield"]) * input_data["maturityYears"])
        return math.exp(-input_data["riskFreeRate"] * input_data["maturityYears"]) * _intrinsic(terminal, input_data["strike"], input_data["optionType"])
    sqrt_t = math.sqrt(input_data["maturityYears"])
    d1 = (math.log(input_data["spot"] / input_data["strike"]) + (input_data["riskFreeRate"] - input_data["dividendYield"] + 0.5 * input_data["volatility"] ** 2) * input_data["maturityYears"]) / (input_data["volatility"] * sqrt_t)
    d2 = d1 - input_data["volatility"] * sqrt_t
    s = input_data["spot"] * math.exp(-input_data["dividendYield"] * input_data["maturityYears"])
    k = input_data["strike"] * math.exp(-input_data["riskFreeRate"] * input_data["maturityYears"])
    return s * _norm_cdf(d1) - k * _norm_cdf(d2) if input_data["optionType"] == "call" else k * _norm_cdf(-d2) - s * _norm_cdf(-d1)


def _lattice(input_data: Mapping[str, Any], steps: int, exercise_style: str | None = None, details: bool = False) -> dict[str, Any]:
    exercise_style = exercise_style or input_data["exerciseStyle"]
    dt = input_data["maturityYears"] / steps
    discount = math.exp(-input_data["riskFreeRate"] * dt)
    deterministic = input_data["volatility"] == 0 or input_data["maturityYears"] == 0
    up = down = 1.0
    probability: float | None = None
    log_up = 0.0
    if not deterministic:
        log_up = input_data["volatility"] * math.sqrt(dt)
        up, down = math.exp(log_up), math.exp(-log_up)
        probability = (math.exp((input_data["riskFreeRate"] - input_data["dividendYield"]) * dt) - down) / (up - down)
        tolerance = BINOMIAL_CONTRACT["numeric"]["probabilityTolerance"]
        if not math.isfinite(probability) or probability < -tolerance or probability > 1 + tolerance:
            raise ValueError(f"CRR no-arbitrage probability is outside [0,1] at {steps} steps; increase steps or revise rate/dividend/volatility inputs.")
        if probability < 0 or probability > 1:
            raise ValueError(f"CRR probability is numerically outside [0,1] at {steps} steps.")

    def spot_at(step: int, up_moves: int) -> float:
        if deterministic:
            return input_data["spot"] * math.exp((input_data["riskFreeRate"] - input_data["dividendYield"]) * step * dt)
        return input_data["spot"] * math.exp((2 * up_moves - step) * log_up)

    values = [_intrinsic(spot_at(steps, j), input_data["strike"], input_data["optionType"]) for j in range(steps + 1)]
    european = list(values)
    boundary: list[dict[str, Any]] = []
    nodes: list[dict[str, Any]] = []
    exercised_count = 0
    first_exercise: int | None = None
    if details and steps <= LIMITS["maxDisplayDepth"]:
        for j in range(steps + 1):
            nodes.append({"step": steps, "upMoves": j, "spot": spot_at(steps, j), "intrinsic": values[j], "continuation": None, "value": values[j], "exercise": False})
    for step in range(steps - 1, -1, -1):
        next_values: list[float] = []
        next_european: list[float] = []
        exercised_spots: list[float] = []
        for j in range(step + 1):
            continuation = discount * values[j] if deterministic else discount * ((1 - probability) * values[j] + probability * values[j + 1])
            european_continuation = discount * european[j] if deterministic else discount * ((1 - probability) * european[j] + probability * european[j + 1])
            spot = spot_at(step, j)
            immediate = _intrinsic(spot, input_data["strike"], input_data["optionType"])
            exercise = exercise_style == "american" and immediate > continuation + BINOMIAL_CONTRACT["numeric"]["exerciseTolerance"] * max(1, abs(continuation))
            next_values.append(immediate if exercise else continuation)
            next_european.append(european_continuation)
            if exercise:
                exercised_spots.append(spot)
            if details and step <= LIMITS["maxDisplayDepth"]:
                nodes.append({"step": step, "upMoves": j, "spot": spot, "intrinsic": immediate, "continuation": continuation, "value": next_values[-1], "exercise": exercise})
        if details and exercised_spots:
            exercised_count += len(exercised_spots)
            first_exercise = step if first_exercise is None else min(first_exercise, step)
            boundary.append({"step": step, "timeYears": step * dt, "boundarySpot": max(exercised_spots) if input_data["optionType"] == "put" else min(exercised_spots), "exerciseNodeCount": len(exercised_spots)})
        values, european = next_values, next_european
    boundary.sort(key=lambda row: row["step"])
    nodes.sort(key=lambda row: (row["step"], row["upMoves"]))
    return {"price": values[0], "europeanPrice": european[0], "up": up, "down": down, "probability": probability, "discountFactor": discount, "dt": dt, "deterministic": deterministic, "boundary": boundary, "nodes": nodes, "exercisedNodeCount": exercised_count, "firstExerciseStep": first_exercise}


def _price_only(input_data: Mapping[str, Any], **overrides: Any) -> float:
    changed = {**input_data, **overrides}
    return _lattice(changed, overrides.get("steps", input_data["steps"]), overrides.get("exerciseStyle", input_data["exerciseStyle"]), False)["price"]


def _greeks(input_data: Mapping[str, Any], price: float, detailed: Mapping[str, Any]) -> dict[str, float]:
    level_one = [node for node in detailed["nodes"] if node["step"] == 1]
    level_two = [node for node in detailed["nodes"] if node["step"] == 2]
    if not detailed["deterministic"] and len(level_one) == 2 and len(level_two) == 3:
        delta = (level_one[1]["value"] - level_one[0]["value"]) / (level_one[1]["spot"] - level_one[0]["spot"])
        delta_down = (level_two[1]["value"] - level_two[0]["value"]) / (level_two[1]["spot"] - level_two[0]["spot"])
        delta_up = (level_two[2]["value"] - level_two[1]["value"]) / (level_two[2]["spot"] - level_two[1]["spot"])
        gamma = (delta_up - delta_down) / ((level_two[2]["spot"] - level_two[0]["spot"]) / 2)
        theta = (level_two[1]["value"] - price) / (2 * detailed["dt"] * 365)
    else:
        spot_bump = min(
            max(input_data["spot"] * 0.01, min(1e-6, input_data["spot"] * 0.5)),
            (LIMITS["maxSpot"] - LIMITS["minSpot"]) / 4,
        )
        if input_data["spot"] - spot_bump >= LIMITS["minSpot"] and input_data["spot"] + spot_bump <= LIMITS["maxSpot"]:
            up_spot = _price_only(input_data, spot=input_data["spot"] + spot_bump)
            down_spot = _price_only(input_data, spot=input_data["spot"] - spot_bump)
            delta = (up_spot - down_spot) / (2 * spot_bump)
            gamma = (up_spot - 2 * price + down_spot) / spot_bump ** 2
        elif input_data["spot"] + 2 * spot_bump <= LIMITS["maxSpot"]:
            first = _price_only(input_data, spot=input_data["spot"] + spot_bump)
            second = _price_only(input_data, spot=input_data["spot"] + 2 * spot_bump)
            delta = (-3 * price + 4 * first - second) / (2 * spot_bump)
            gamma = (price - 2 * first + second) / spot_bump ** 2
        else:
            first = _price_only(input_data, spot=input_data["spot"] - spot_bump)
            second = _price_only(input_data, spot=input_data["spot"] - 2 * spot_bump)
            delta = (3 * price - 4 * first + second) / (2 * spot_bump)
            gamma = (price - 2 * first + second) / spot_bump ** 2
        shorter = input_data["maturityYears"] - 1 / 365 if input_data["maturityYears"] > 1 / 365 else LIMITS["minMaturityYears"]
        theta = _price_only(input_data, maturityYears=shorter) - price
    vol_bump = 1e-4
    floor = abs(input_data["riskFreeRate"] - input_data["dividendYield"]) * math.sqrt(input_data["maturityYears"] / input_data["steps"])
    up_volatility = max(input_data["volatility"] + vol_bump, floor * 1.000001 + sys.float_info.epsilon)
    down_volatility = input_data["volatility"] - vol_bump
    can_use_up_vol = up_volatility <= LIMITS["maxVolatility"]
    can_use_down_vol = down_volatility >= LIMITS["minVolatility"] and down_volatility > floor * 1.000001
    if can_use_up_vol and can_use_down_vol:
        vega = (_price_only(input_data, volatility=up_volatility) - _price_only(input_data, volatility=down_volatility)) / (up_volatility - down_volatility) * 0.01
    elif can_use_up_vol:
        vega = (_price_only(input_data, volatility=up_volatility) - price) / (up_volatility - input_data["volatility"]) * 0.01
    elif can_use_down_vol:
        vega = (price - _price_only(input_data, volatility=down_volatility)) / (input_data["volatility"] - down_volatility) * 0.01
    else:
        raise ValueError("Vega cannot be estimated inside the supported volatility and CRR probability domain.")
    rate_bump = 1e-4

    def admissible_rate_price(risk_free_rate: float) -> float | None:
        if risk_free_rate < LIMITS["minRate"] or risk_free_rate > LIMITS["maxRate"]:
            return None
        try:
            return _price_only(input_data, riskFreeRate=risk_free_rate)
        except ValueError as error:
            if "CRR no-arbitrage probability" in str(error):
                return None
            raise

    up_rate_price = admissible_rate_price(input_data["riskFreeRate"] + rate_bump)
    down_rate_price = admissible_rate_price(input_data["riskFreeRate"] - rate_bump)
    if up_rate_price is not None and down_rate_price is not None:
        rho = (up_rate_price - down_rate_price) / (2 * rate_bump) * 0.01
    elif up_rate_price is not None:
        rho = (up_rate_price - price) / rate_bump * 0.01
    elif down_rate_price is not None:
        rho = (price - down_rate_price) / rate_bump * 0.01
    else:
        raise ValueError("Rho cannot be estimated inside the supported rate and CRR probability domain.")
    return {"delta": delta, "gamma": gamma, "vega": vega, "theta": theta, "rho": rho}


def _finite_tree(value: Any, path: str = "result") -> None:
    if type(value) is float and not math.isfinite(value):
        raise ValueError(f"{path} contains a non-finite number.")
    if isinstance(value, list):
        for index, item in enumerate(value):
            _finite_tree(item, f"{path}[{index}]")
    elif isinstance(value, Mapping):
        for key, item in value.items():
            _finite_tree(item, f"{path}.{key}")


def analyze_binomial(raw: Any) -> dict[str, Any]:
    input_data = normalize_binomial_input(raw)
    analysis_id = _analysis_id(input_data)
    detailed = _lattice(input_data, input_data["steps"], input_data["exerciseStyle"], True)
    benchmark = _black_scholes(input_data)
    step_values = sorted(set([max(2, input_data["steps"] // 8), max(2, input_data["steps"] // 4), max(2, input_data["steps"] // 2), max(2, input_data["steps"] - 1), input_data["steps"]]))
    convergence = []
    for steps in step_values:
        run = _lattice(input_data, steps, input_data["exerciseStyle"], False)
        convergence.append({"steps": steps, "pricePerUnit": run["price"], "europeanPricePerUnit": run["europeanPrice"], "blackScholesBenchmark": benchmark, "absoluteBenchmarkError": abs((run["price"] if input_data["exerciseStyle"] == "european" else run["europeanPrice"]) - benchmark)})
    adjacent = _lattice(input_data, max(2, input_data["steps"] - 1), input_data["exerciseStyle"], False)["price"]
    per_unit_greeks = _greeks(input_data, detailed["price"], detailed)
    sign = 1 if input_data["position"] == "long" else -1
    scale = sign * input_data["quantity"] * input_data["contractMultiplier"]
    adjacent_gap = abs(detailed["price"] - adjacent)
    early_exercise_premium = detailed["price"] - detailed["europeanPrice"]
    premium_tolerance = BINOMIAL_CONTRACT["numeric"]["exerciseTolerance"] * max(1, abs(detailed["price"]), abs(detailed["europeanPrice"]))
    if early_exercise_premium < -premium_tolerance:
        raise ValueError("American value fell below the same-tree European value.")
    reported_early_exercise_premium = 0.0 if abs(early_exercise_premium) <= premium_tolerance else early_exercise_premium
    diagnostics = []
    if input_data["maturityYears"] == 0:
        diagnostics.append({"code": "AT_EXPIRY_INTRINSIC", "severity": "info", "message": "At expiry, the value is the exact intrinsic payoff and no probability is required."})
    elif detailed["deterministic"]:
        diagnostics.append({"code": "ZERO_VOLATILITY_DETERMINISTIC", "severity": "info", "message": "Zero volatility uses the deterministic risk-neutral path and backward optimal stopping."})
    if adjacent_gap > max(1e-6, abs(detailed["price"]) * 1e-3):
        diagnostics.append({"code": "ADJACENT_STEP_OSCILLATION", "severity": "warning", "message": "N and N-1 prices still differ materially; increase steps before relying on the estimate."})
    if input_data["exerciseStyle"] == "american" and detailed["exercisedNodeCount"] == 0:
        diagnostics.append({"code": "NO_EARLY_EXERCISE_REGION", "severity": "info", "message": "No pre-maturity node exercised on this lattice."})
    if input_data["exerciseStyle"] == "american" and input_data["optionType"] == "call" and input_data["dividendYield"] <= 0 and input_data["riskFreeRate"] >= 0:
        diagnostics.append({"code": "NON_DIVIDEND_CALL_CHECK", "severity": "info", "message": "With non-negative rates, a non-dividend American call should not exercise early and should converge to its European value."})
    result = {
        "schemaVersion": BINOMIAL_SCHEMA_VERSION, "engineVersion": BINOMIAL_ENGINE_VERSION, "analysisId": analysis_id, "input": input_data,
        "model": {"name": "Cox-Ross-Rubinstein", "measure": "Q", "dayCount": input_data["dayCount"], "timeStepYears": detailed["dt"], "upFactor": detailed["up"], "downFactor": detailed["down"], "riskNeutralUpProbability": detailed["probability"], "discountFactorPerStep": detailed["discountFactor"], "noArbitrageProbability": detailed["probability"] is None or 0 <= detailed["probability"] <= 1},
        "valuation": {"pricePerUnit": detailed["price"], "positionValue": detailed["price"] * scale, "europeanPricePerUnit": detailed["europeanPrice"], "earlyExercisePremiumPerUnit": reported_early_exercise_premium, "intrinsicAtSpot": _intrinsic(input_data["spot"], input_data["strike"], input_data["optionType"]), "blackScholesBenchmark": benchmark, "benchmarkComparisonPrice": detailed["price"] if input_data["exerciseStyle"] == "european" else detailed["europeanPrice"], "benchmarkAbsoluteError": abs((detailed["price"] if input_data["exerciseStyle"] == "european" else detailed["europeanPrice"]) - benchmark), "adjacentStepPrice": adjacent, "adjacentStepGap": adjacent_gap, "adjacentStepAverage": (detailed["price"] + adjacent) / 2},
        "greeks": {"perUnit": per_unit_greeks, "position": {key: value * scale for key, value in per_unit_greeks.items()}},
        "convergence": convergence,
        "earlyExercise": {"available": input_data["exerciseStyle"] == "american", "exercisedNodeCount": detailed["exercisedNodeCount"], "firstExerciseStep": detailed["firstExerciseStep"], "firstExerciseTimeYears": None if detailed["firstExerciseStep"] is None else detailed["firstExerciseStep"] * detailed["dt"], "boundary": detailed["boundary"]},
        "tree": {"displayDepth": min(input_data["steps"], LIMITS["maxDisplayDepth"]), "nodes": detailed["nodes"]},
        "diagnostics": diagnostics,
        "limitations": ["Constant risk-free rate, continuous dividend yield and constant volatility.", "No discrete dividends, term structures, smile/skew, jumps, transaction costs, liquidity or margin.", "Finite-difference Greeks for an American lattice may oscillate with the step count; convergence must be inspected.", "Educational local calculation; inputs are user assumptions, not live market data."],
    }
    _finite_tree(result)
    return result


def _export_number(value: float | None) -> str:
    if value is None:
        return ""
    if not math.isfinite(value):
        raise ValueError("Evidence export contains a non-finite number.")
    if value == 0 or abs(value) < 1e-15:
        return "0"
    mantissa, exponent = format(value, ".8e").lower().split("e")
    return f"{mantissa.rstrip('0').rstrip('.')}e{int(exponent)}"


def _csv(headers: list[str], rows: list[Mapping[str, Any]]) -> str:
    def escape(value: Any) -> str:
        text = _export_number(float(value)) if type(value) in (int, float) else str(value if value is not None else "")
        return f'"{text.replace(chr(34), chr(34) * 2)}"' if any(char in text for char in ',"\n\r') else text
    lines = [",".join(headers)] + [",".join(escape(row.get(header)) for header in headers) for row in rows]
    return "\n".join(lines) + "\n"


def build_binomial_convergence_csv(result: Mapping[str, Any]) -> str:
    rows = [{"schemaVersion": BINOMIAL_CONVERGENCE_CSV_SCHEMA, "engineVersion": result["engineVersion"], "analysisId": result["analysisId"], "exerciseStyle": result["input"]["exerciseStyle"], "optionType": result["input"]["optionType"], **row} for row in result["convergence"]]
    return _csv(BINOMIAL_CONTRACT["exports"]["convergenceCsvHeaders"], rows)


def build_binomial_frontier_csv(result: Mapping[str, Any]) -> str:
    rows = [{"schemaVersion": BINOMIAL_FRONTIER_CSV_SCHEMA, "engineVersion": result["engineVersion"], "analysisId": result["analysisId"], "optionType": result["input"]["optionType"], **row} for row in result["earlyExercise"]["boundary"]]
    return _csv(BINOMIAL_CONTRACT["exports"]["frontierCsvHeaders"], rows)


def build_binomial_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, ensure_ascii=False, indent=2) + "\n"


def _write_stdout(text: str) -> None:
    sys.stdout.buffer.write(text.encode("utf-8"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the canonical TPL CRR binomial engine")
    parser.add_argument("--input", type=Path)
    parser.add_argument("--contract", action="store_true")
    parser.add_argument("--convergence-csv", action="store_true")
    parser.add_argument("--frontier-csv", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.contract:
            _write_stdout(json.dumps(BINOMIAL_CONTRACT, ensure_ascii=False, indent=2) + "\n")
            return 0
        if args.input is None:
            raise ValueError("--input is required unless --contract is used.")
        if args.input.stat().st_size > LIMITS["maxInputBytes"]:
            raise ValueError("input file exceeds the 1,000,000-byte limit.")
        raw = json.loads(args.input.read_text(encoding="utf-8"))
        result = analyze_binomial(raw)
        if args.convergence_csv:
            _write_stdout(build_binomial_convergence_csv(result))
        elif args.frontier_csv:
            _write_stdout(build_binomial_frontier_csv(result))
        else:
            _write_stdout(build_binomial_json(result))
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        sys.stderr.write(f"Binomial analysis failed: {exc}\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
