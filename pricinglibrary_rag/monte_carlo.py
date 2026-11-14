"""Deterministic, provider-free Monte Carlo engine for F-CAL-6.

The module deliberately keeps simulation, validation and serialization free of
web-framework concerns.  One validated run supplies every path, terminal,
metric and export; charts and risk/pricing statistics therefore cannot drift
onto hidden secondary simulations.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import os
import stat
import sys
from typing import Any, Mapping, Sequence


INPUT_SCHEMA_VERSION = "tpl.monte-carlo.input.v1"
SCHEMA_VERSION = "tpl.monte-carlo.analysis.v1"
ENGINE_VERSION = "1.0.0"
TERMINAL_CSV_SCHEMA = "tpl.monte-carlo.terminals.v1"
PATHS_CSV_SCHEMA = "tpl.monte-carlo.paths.v1"
MAX_INPUT_BYTES = 1_000_000
PARK_MILLER_MODULUS = 2_147_483_647
PARK_MILLER_MULTIPLIER = 16_807

TERMINAL_CSV_HEADERS = (
    "schemaVersion", "engineVersion", "analysisId", "mode", "pathIndex",
    "terminalSpot", "discountedPayoff", "pnl", "loss",
)
PATHS_CSV_HEADERS = (
    "schemaVersion", "engineVersion", "analysisId", "mode", "pathIndex",
    "step", "timeYears", "spot",
)

_COMMON_FIELDS = {
    "schemaVersion", "mode", "spot", "volatility", "maturityYears",
    "dayCount", "paths", "timeSteps", "seed", "method", "samplePaths",
    "histogramBins", "currency", "quantity", "contractMultiplier", "position",
}
_RISK_FIELDS = _COMMON_FIELDS | {"physicalDrift", "confidence"}
_PRICING_FIELDS = _COMMON_FIELDS | {
    "riskFreeRate", "dividendYield", "strike", "optionType", "payoffType",
}

_LIMITS: dict[str, float | int] = {
    "minSpot": 1e-8,
    "maxSpot": 1e12,
    "minStrike": 1e-8,
    "maxStrike": 1e12,
    "minVolatility": 0.0,
    "maxVolatility": 5.0,
    "minMaturityYears": 1.0 / 365_000.0,
    "maxMaturityYears": 30.0,
    "minRate": -1.0,
    "maxRate": 1.0,
    "minPhysicalDrift": -2.0,
    "maxPhysicalDrift": 2.0,
    "minPaths": 100,
    "maxPaths": 50_000,
    "minTimeSteps": 1,
    "maxTimeSteps": 366,
    "maxSamplePaths": 24,
    "minHistogramBins": 10,
    "maxHistogramBins": 80,
    "maxQuantity": 1_000_000,
    "minContractMultiplier": 1e-8,
    "maxContractMultiplier": 1e12,
}


class MonteCarloError(ValueError):
    """Explicit input, numerical or serialization contract failure."""


class ParkMiller16807:
    """Minimal-standard Park-Miller generator with a portable state update."""

    def __init__(self, seed: int) -> None:
        if isinstance(seed, bool) or not isinstance(seed, int) or not 1 <= seed < PARK_MILLER_MODULUS:
            raise MonteCarloError("seed must be an integer in [1, 2147483646].")
        self.state = seed

    def uniform(self) -> float:
        self.state = (self.state * PARK_MILLER_MULTIPLIER) % PARK_MILLER_MODULUS
        return self.state / PARK_MILLER_MODULUS

    def normal(self) -> float:
        # Park-Miller never returns zero for a valid state.
        u1 = self.uniform()
        u2 = self.uniform()
        return math.sqrt(-2.0 * math.log(u1)) * math.cos(2.0 * math.pi * u2)


def monte_carlo_contract_snapshot() -> dict[str, Any]:
    """Return the executable projection of the shared F-CAL-6 contract."""

    return {
        "schemaVersion": SCHEMA_VERSION,
        "engineVersion": ENGINE_VERSION,
        "rng": {
            "algorithm": "park_miller_16807",
            "normalTransform": "box_muller_cosine",
            "modulus": PARK_MILLER_MODULUS,
            "multiplier": PARK_MILLER_MULTIPLIER,
            "seedDomain": [1, PARK_MILLER_MODULUS - 1],
        },
        "modes": ["risk_physical", "pricing_risk_neutral"],
        "measures": {"risk_physical": "P", "pricing_risk_neutral": "Q"},
        "dayCounts": ["ACT/365F"],
        "methods": ["none", "antithetic", "control_variate"],
        "optionTypes": ["call", "put"],
        "payoffTypes": ["european", "arithmetic_asian"],
        "positions": ["long", "short"],
        "confidenceLevels": [0.95, 0.99],
        "limits": {"maxInputBytes": MAX_INPUT_BYTES, **_LIMITS, "maxCurrencyLength": 3},
        "riskConvention": {
            "pnl": "position_sign * quantity * contract_multiplier * (terminal_spot - initial_spot)",
            "loss": "-pnl",
            "quantile": "linear_type_7",
            "valueAtRisk": "max(0, confidence_quantile_of_loss)",
            "expectedShortfall": "max(0, arithmetic_mean_of_worst_ceil((1-confidence)*paths)_losses)",
            "reportedUnits": "portfolio_currency_amount",
        },
        "pricingConvention": {
            "measure": "risk_neutral_Q",
            "drift": "risk_free_rate_minus_dividend_yield",
            "discounting": "exp(-risk_free_rate * maturity_years)",
            "asianAverage": "arithmetic_mean_of_monitoring_spots_excluding_time_zero",
            "confidenceInterval": "estimate_plus_or_minus_1.96_standard_errors",
            "antitheticStandardError": "sample_standard_error_of_pair_means",
            "controlVariate": "discounted_terminal_spot_with_known_mean_spot_times_exp(-dividend_yield*maturity_years)",
        },
        "exports": {
            "terminalCsvSchema": TERMINAL_CSV_SCHEMA,
            "pathsCsvSchema": PATHS_CSV_SCHEMA,
            "terminalCsvHeaders": list(TERMINAL_CSV_HEADERS),
            "pathsCsvHeaders": list(PATHS_CSV_HEADERS),
            "lineEnding": "LF",
            "finalNewline": True,
            "numericFormat": "finite_decimal_12",
        },
    }


def _assert_recursive_finite(value: Any, label: str = "input") -> None:
    if isinstance(value, float) and not math.isfinite(value):
        raise MonteCarloError(f"{label} contains NaN or Infinity.")
    if isinstance(value, Mapping):
        for key, child in value.items():
            _assert_recursive_finite(child, f"{label}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            _assert_recursive_finite(child, f"{label}[{index}]")


def _number(value: Any, name: str, low: float, high: float) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise MonteCarloError(f"{name} must be a finite JSON number in [{low}, {high}].")
    try:
        result = float(value)
    except (OverflowError, ValueError) as exc:
        raise MonteCarloError(f"{name} must be a finite JSON number in [{low}, {high}].") from exc
    if not math.isfinite(result) or result < low or result > high:
        raise MonteCarloError(f"{name} must be a finite JSON number in [{low}, {high}].")
    return result


def _integer(value: Any, name: str, low: int, high: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < low or value > high:
        raise MonteCarloError(f"{name} must be an integer in [{low}, {high}].")
    return value


def _enum(value: Any, name: str, allowed: Sequence[str]) -> str:
    if not isinstance(value, str) or value not in allowed:
        raise MonteCarloError(f"{name} must be one of: {', '.join(allowed)}.")
    return value


def validate_request(raw: Mapping[str, Any]) -> dict[str, Any]:
    """Validate and normalize one request without coercion or silent defaults."""

    if not isinstance(raw, Mapping):
        raise MonteCarloError("input must be a JSON object.")
    _assert_recursive_finite(raw)
    mode = raw.get("mode")
    if mode not in ("risk_physical", "pricing_risk_neutral"):
        raise MonteCarloError("mode must be one of: risk_physical, pricing_risk_neutral.")
    expected = _RISK_FIELDS if mode == "risk_physical" else _PRICING_FIELDS
    actual = set(raw)
    if actual != expected:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        details = []
        if missing:
            details.append("missing fields: " + ", ".join(missing))
        if extra:
            details.append("unexpected fields: " + ", ".join(extra))
        raise MonteCarloError("input schema mismatch (" + "; ".join(details) + ").")

    if raw["schemaVersion"] != INPUT_SCHEMA_VERSION:
        raise MonteCarloError(f"schemaVersion must equal {INPUT_SCHEMA_VERSION}.")
    result: dict[str, Any] = {
        "schemaVersion": INPUT_SCHEMA_VERSION,
        "mode": mode,
        "spot": _number(raw["spot"], "spot", _LIMITS["minSpot"], _LIMITS["maxSpot"]),
        "volatility": _number(raw["volatility"], "volatility", _LIMITS["minVolatility"], _LIMITS["maxVolatility"]),
        "maturityYears": _number(raw["maturityYears"], "maturityYears", _LIMITS["minMaturityYears"], _LIMITS["maxMaturityYears"]),
        "dayCount": _enum(raw["dayCount"], "dayCount", ("ACT/365F",)),
        "paths": _integer(raw["paths"], "paths", int(_LIMITS["minPaths"]), int(_LIMITS["maxPaths"])),
        "timeSteps": _integer(raw["timeSteps"], "timeSteps", int(_LIMITS["minTimeSteps"]), int(_LIMITS["maxTimeSteps"])),
        "seed": _integer(raw["seed"], "seed", 1, PARK_MILLER_MODULUS - 1),
        "method": _enum(raw["method"], "method", ("none", "antithetic", "control_variate")),
        "samplePaths": _integer(raw["samplePaths"], "samplePaths", 0, int(_LIMITS["maxSamplePaths"])),
        "histogramBins": _integer(raw["histogramBins"], "histogramBins", int(_LIMITS["minHistogramBins"]), int(_LIMITS["maxHistogramBins"])),
        "currency": raw["currency"],
        "quantity": _integer(raw["quantity"], "quantity", 1, int(_LIMITS["maxQuantity"])),
        "contractMultiplier": _number(raw["contractMultiplier"], "contractMultiplier", _LIMITS["minContractMultiplier"], _LIMITS["maxContractMultiplier"]),
        "position": _enum(raw["position"], "position", ("long", "short")),
    }
    if not isinstance(result["currency"], str) or len(result["currency"]) != 3 or not result["currency"].isascii() or not result["currency"].isalpha() or result["currency"].upper() != result["currency"]:
        raise MonteCarloError("currency must be exactly three uppercase ASCII letters.")
    if result["samplePaths"] > result["paths"]:
        raise MonteCarloError("samplePaths must not exceed paths.")
    if result["method"] == "antithetic" and result["paths"] % 2:
        raise MonteCarloError("paths must be even when method is antithetic.")
    if mode == "risk_physical":
        if result["method"] == "control_variate":
            raise MonteCarloError("control_variate is available only in pricing_risk_neutral mode.")
        result["physicalDrift"] = _number(raw["physicalDrift"], "physicalDrift", _LIMITS["minPhysicalDrift"], _LIMITS["maxPhysicalDrift"])
        if isinstance(raw["confidence"], bool) or raw["confidence"] not in (0.95, 0.99):
            raise MonteCarloError("confidence must be one of: 0.95, 0.99.")
        result["confidence"] = float(raw["confidence"])
    else:
        result.update({
            "riskFreeRate": _number(raw["riskFreeRate"], "riskFreeRate", _LIMITS["minRate"], _LIMITS["maxRate"]),
            "dividendYield": _number(raw["dividendYield"], "dividendYield", _LIMITS["minRate"], _LIMITS["maxRate"]),
            "strike": _number(raw["strike"], "strike", _LIMITS["minStrike"], _LIMITS["maxStrike"]),
            "optionType": _enum(raw["optionType"], "optionType", ("call", "put")),
            "payoffType": _enum(raw["payoffType"], "payoffType", ("european", "arithmetic_asian")),
        })
    return result


def _canonical_number(value: int | float) -> str:
    number = float(value)
    if number == 0.0:
        return "0"
    mantissa, exponent = format(number, ".16e").split("e")
    mantissa = mantissa.rstrip("0").rstrip(".")
    return f"{mantissa}e{int(exponent)}"


def _canonicalize(value: Any) -> Any:
    if isinstance(value, bool) or value is None or isinstance(value, str):
        return value
    if isinstance(value, (int, float)):
        return _canonical_number(value)
    if isinstance(value, Mapping):
        return {key: _canonicalize(value[key]) for key in sorted(value)}
    if isinstance(value, (list, tuple)):
        return [_canonicalize(item) for item in value]
    raise MonteCarloError(f"unsupported canonical value type: {type(value).__name__}.")


def canonical_input_json(config: Mapping[str, Any]) -> str:
    """Canonical cross-engine JSON used for the deterministic analysis id."""

    normalized = validate_request(config)
    return json.dumps(_canonicalize(normalized), ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def analysis_id(config: Mapping[str, Any]) -> str:
    return hashlib.sha256(canonical_input_json(config).encode("utf-8")).hexdigest()


def _mean(values: Sequence[float]) -> float:
    # Deliberately use ordered IEEE-754 additions to mirror Array.reduce in JS.
    return sum(values) / len(values)


def _sample_variance(values: Sequence[float]) -> float:
    if len(values) < 2:
        return 0.0
    center = _mean(values)
    if all(value == values[0] for value in values):
        return 0.0
    return sum((value - center) ** 2 for value in values) / (len(values) - 1)


def _standard_error(values: Sequence[float]) -> float:
    return math.sqrt(_sample_variance(values) / len(values)) if values else 0.0


def _quantile_type7(values: Sequence[float], probability: float) -> float:
    if not values:
        raise MonteCarloError("quantile requires at least one observation.")
    ordered = sorted(values)
    h = (len(ordered) - 1) * probability
    lower = int(math.floor(h))
    upper = int(math.ceil(h))
    if lower == upper:
        return ordered[lower]
    return ordered[lower] + (h - lower) * (ordered[upper] - ordered[lower])


def _histogram(values: Sequence[float], bins: int) -> list[dict[str, float | int]]:
    low, high = min(values), max(values)
    if high == low:
        return [{"lower": low, "upper": high, "midpoint": low, "count": len(values), "probability": 1.0}]
    width = (high - low) / bins
    counts = [0] * bins
    for value in values:
        index = min(max(int((value - low) / width), 0), bins - 1)
        counts[index] += 1
    return [
        {
            "lower": low + index * width,
            "upper": low + (index + 1) * width,
            "midpoint": low + (index + 0.5) * width,
            "count": count,
            "probability": count / len(values),
        }
        for index, count in enumerate(counts)
    ]


def _black_scholes(config: Mapping[str, Any]) -> float:
    s = config["spot"]
    k = config["strike"]
    r = config["riskFreeRate"]
    q = config["dividendYield"]
    sigma = config["volatility"]
    maturity = config["maturityYears"]
    if sigma == 0.0:
        forward_terminal = s * math.exp((r - q) * maturity)
        intrinsic = max(forward_terminal - k, 0.0) if config["optionType"] == "call" else max(k - forward_terminal, 0.0)
        return math.exp(-r * maturity) * intrinsic
    root_t = math.sqrt(maturity)
    d1 = (math.log(s / k) + (r - q + 0.5 * sigma * sigma) * maturity) / (sigma * root_t)
    d2 = d1 - sigma * root_t
    def cdf(raw_x: float) -> float:
        sign = -1.0 if raw_x < 0 else 1.0
        x = abs(raw_x) / math.sqrt(2.0)
        t = 1.0 / (1.0 + 0.3275911 * x)
        c0, c1, c2, c3, c4 = 0.254829592, -0.284496736, 1.421413741, -1.453152027, 1.061405429
        erf = 1.0 - (((((c4 * t + c3) * t) + c2) * t + c1) * t + c0) * t * math.exp(-x * x)
        return 0.5 * (1.0 + sign * erf)
    if config["optionType"] == "call":
        return s * math.exp(-q * maturity) * cdf(d1) - k * math.exp(-r * maturity) * cdf(d2)
    return k * math.exp(-r * maturity) * cdf(-d2) - s * math.exp(-q * maturity) * cdf(-d1)


def _pricing_summary(payoffs: Sequence[float], controls: Sequence[float], config: Mapping[str, Any]) -> dict[str, Any]:
    count = len(payoffs)
    raw = list(payoffs)
    raw_center = _mean(raw)
    raw_variance = _sample_variance(raw)
    samples = raw
    beta = 0.0
    if config["method"] == "antithetic":
        samples = [(raw[index] + raw[index + 1]) / 2.0 for index in range(0, count, 2)]
    elif config["method"] == "control_variate":
        control_mean = _mean(controls)
        covariance = sum(
            (value - control_mean) * (raw[index] - raw_center)
            for index, value in enumerate(controls)
        ) / max(1, count - 1)
        control_variance = _sample_variance(controls)
        beta = covariance / control_variance if control_variance > 0 else 0.0
        expected_control = config["spot"] * math.exp(-config["dividendYield"] * config["maturityYears"])
        samples = [value - beta * (controls[index] - expected_control) for index, value in enumerate(raw)]
    price = _mean(samples)
    standard_error = math.sqrt(_sample_variance(samples) / len(samples))
    raw_standard_error = math.sqrt(raw_variance / len(raw))
    return {
        "paths": count,
        "effectiveSamples": len(samples),
        "price": price,
        "standardError": standard_error,
        "ci95": {"lower": price - 1.96 * standard_error, "upper": price + 1.96 * standard_error},
        "rawPrice": raw_center,
        "rawStandardError": raw_standard_error,
        "beta": beta,
        "varianceReductionRatio": (raw_standard_error ** 2) / (standard_error ** 2) if standard_error > 0 else (1.0 if raw_standard_error == 0 else sys.float_info.max),
    }


def _convergence_sizes(paths: int, method: str) -> list[int]:
    minimum = 2 if method == "antithetic" else 1
    sizes = [max(minimum, paths // 4), max(minimum, paths // 2), paths]
    if method == "antithetic":
        sizes = [size - size % 2 for size in sizes]
    return sorted(set(size for size in sizes if size >= 2))


def run_monte_carlo(raw: Mapping[str, Any]) -> dict[str, Any]:
    """Validate and run the Python mirror of the browser Monte Carlo engine."""

    config = validate_request(raw)
    run_id = analysis_id(config)
    rng = ParkMiller16807(config["seed"])
    observations: list[dict[str, Any]] = []
    sample_paths: list[dict[str, Any]] = []
    discounted_payoffs: list[float] = []
    discounted_terminals: list[float] = []
    discount = math.exp(-config["riskFreeRate"] * config["maturityYears"]) if config["mode"] == "pricing_risk_neutral" else 1.0
    sign = 1 if config["position"] == "long" else -1
    drift = config["physicalDrift"] if config["mode"] == "risk_physical" else config["riskFreeRate"] - config["dividendYield"]
    dt = config["maturityYears"] / config["timeSteps"]
    diffusion = config["volatility"] * math.sqrt(dt)
    drift_step = (drift - 0.5 * config["volatility"] ** 2) * dt

    def append_path(normals: Sequence[float], path_index: int) -> None:
        spot = config["spot"]
        monitored_sum = 0.0
        capture = path_index < config["samplePaths"]
        points = [{"step": 0, "timeYears": 0.0, "spot": spot}] if capture else None
        for step in range(1, config["timeSteps"] + 1):
            spot *= math.exp(drift_step + diffusion * normals[step - 1])
            monitored_sum += spot
            if capture:
                points.append({"step": step, "timeYears": step * dt, "spot": spot})
        row = {"pathIndex": path_index, "terminalSpot": spot, "discountedPayoff": None, "pnl": None, "loss": None}
        if config["mode"] == "risk_physical":
            row["pnl"] = sign * config["quantity"] * config["contractMultiplier"] * (spot - config["spot"])
            row["loss"] = -row["pnl"]
        else:
            underlying = spot if config["payoffType"] == "european" else monitored_sum / config["timeSteps"]
            payoff = max(underlying - config["strike"], 0.0) if config["optionType"] == "call" else max(config["strike"] - underlying, 0.0)
            row["discountedPayoff"] = discount * payoff
            discounted_payoffs.append(row["discountedPayoff"])
            discounted_terminals.append(discount * spot)
        observations.append(row)
        if points is not None:
            sample_paths.append({"pathIndex": path_index, "points": points})

    if config["method"] == "antithetic":
        for path_index in range(0, config["paths"], 2):
            normals = [rng.normal() for _ in range(config["timeSteps"])]
            append_path(normals, path_index)
            append_path([-value for value in normals], path_index + 1)
    else:
        for path_index in range(config["paths"]):
            append_path([rng.normal() for _ in range(config["timeSteps"])], path_index)

    terminals = [row["terminalSpot"] for row in observations]
    sorted_terminals = sorted(terminals)
    analytical_mean = config["spot"] * math.exp(drift * config["maturityYears"])
    analytical_variance = config["spot"] ** 2 * math.exp(2 * drift * config["maturityYears"]) * (math.exp(config["volatility"] ** 2 * config["maturityYears"]) - 1)
    terminal_mean = _mean(terminals)
    terminal_stddev = math.sqrt(_sample_variance(terminals))
    measure_text = "Physical P measure using the declared expected return." if config["mode"] == "risk_physical" else "Risk-neutral Q measure using drift r-q and discounting at r."
    limitations = (
        ["Parametric GBM, constant drift and volatility.", "VaR and ES are model estimates, not guarantees or historical backtests.", "No jumps, volatility smile, transaction costs or liquidity stress."]
        if config["mode"] == "risk_physical"
        else ["Constant-rate, constant-volatility GBM.", "European benchmark uses Black-Scholes; arithmetic Asian has no closed-form benchmark here.", "No smile/skew, jumps, early exercise, transaction costs or liquidity model."]
    )
    result: dict[str, Any] = {
        "schemaVersion": SCHEMA_VERSION,
        "engineVersion": ENGINE_VERSION,
        "analysisId": run_id,
        "mode": config["mode"],
        "measure": "P" if config["mode"] == "risk_physical" else "Q",
        "input": config,
        "run": {
            "requestedPaths": config["paths"],
            "simulatedPaths": len(observations),
            "timeSteps": config["timeSteps"],
            "samplePathCount": len(sample_paths),
            "seed": config["seed"],
            "method": config["method"],
            "rng": "park_miller_16807",
            "normalTransform": "box_muller_cosine",
        },
        "distribution": {
            "terminalMean": terminal_mean,
            "terminalStdDev": terminal_stddev,
            "analyticalTerminalMean": analytical_mean,
            "analyticalTerminalStdDev": math.sqrt(max(0.0, analytical_variance)),
            "meanRelativeError": 0.0 if analytical_mean == 0 else (terminal_mean - analytical_mean) / analytical_mean,
            "quantiles": {
                "p01": _quantile_type7(sorted_terminals, 0.01),
                "p05": _quantile_type7(sorted_terminals, 0.05),
                "p50": _quantile_type7(sorted_terminals, 0.5),
                "p95": _quantile_type7(sorted_terminals, 0.95),
                "p99": _quantile_type7(sorted_terminals, 0.99),
            },
            "probabilityBelowInitialSpot": sum(value < config["spot"] for value in terminals) / len(terminals),
            "histogram": _histogram(terminals, config["histogramBins"]),
        },
        "samplePaths": sample_paths,
        "observations": observations,
        "risk": None,
        "pricing": None,
        "conventions": {
            "dayCount": config["dayCount"],
            "measure": measure_text,
            "rng": "Park-Miller 16807 uniforms with Box-Muller cosine normals; seed and all inputs are reproducible.",
            "limitations": limitations,
        },
    }
    if config["mode"] == "risk_physical":
        losses = sorted(row["loss"] for row in observations)
        raw_loss_quantile = _quantile_type7(losses, config["confidence"])
        tail_count = max(1, math.ceil((1.0 - config["confidence"]) * len(losses) - 1e-12))
        tail_losses = losses[len(losses) - tail_count:]
        result["risk"] = {
            "confidence": config["confidence"],
            "pnlMean": _mean([row["pnl"] for row in observations]),
            "probabilityOfLoss": sum(row["pnl"] < 0 for row in observations) / len(observations),
            "rawLossQuantile": raw_loss_quantile,
            "valueAtRisk": max(0.0, raw_loss_quantile),
            "expectedShortfall": max(0.0, _mean(tail_losses)),
            "tailCount": tail_count,
            "convention": "Loss = -P&L; VaR is the confidence quantile of loss floored at zero; ES is the mean of the worst ceil((1-confidence)*N) losses, floored at zero.",
        }
    else:
        counts = _convergence_sizes(config["paths"], config["method"])
        estimates = [
            _pricing_summary(discounted_payoffs[:count], discounted_terminals[:count], config)
            for count in counts
        ]
        final_estimate = estimates[-1]
        benchmark = _black_scholes(config) if config["payoffType"] == "european" else None
        bias = None if benchmark is None else final_estimate["price"] - benchmark
        pricing = dict(final_estimate)
        pricing.update({
            "portfolioValue": sign * config["quantity"] * config["contractMultiplier"] * final_estimate["price"],
            "blackScholesBenchmark": benchmark,
            "bias": bias,
            "zScore": None if benchmark is None or final_estimate["standardError"] == 0 else bias / final_estimate["standardError"],
            "benchmarkInsideCi95": None if benchmark is None else final_estimate["ci95"]["lower"] <= benchmark <= final_estimate["ci95"]["upper"],
            "convergence": [
                {key: estimate[key] for key in ("paths", "effectiveSamples", "price", "standardError", "ci95")}
                for estimate in estimates
            ],
        })
        result["pricing"] = pricing
    _assert_recursive_finite(result, "result")
    return result


def _export_number(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(float(value)):
        raise MonteCarloError("CSV export encountered a non-finite numeric value.")
    number = float(value)
    if abs(number) < 1e-15:
        return "0"
    mantissa, exponent = format(number, ".11e").split("e")
    mantissa = mantissa.rstrip("0").rstrip(".")
    return f"{mantissa}e{int(exponent)}"


def export_terminal_csv(result: Mapping[str, Any]) -> str:
    stream = io.StringIO(newline="")
    writer = csv.writer(stream, lineterminator="\n")
    writer.writerow(TERMINAL_CSV_HEADERS)
    for row in result["observations"]:
        writer.writerow([
            TERMINAL_CSV_SCHEMA, ENGINE_VERSION, result["analysisId"], result["mode"],
            _export_number(row["pathIndex"]), _export_number(row["terminalSpot"]),
            _export_number(row["discountedPayoff"]), _export_number(row["pnl"]),
            _export_number(row["loss"]),
        ])
    return stream.getvalue()


def export_paths_csv(result: Mapping[str, Any]) -> str:
    stream = io.StringIO(newline="")
    writer = csv.writer(stream, lineterminator="\n")
    writer.writerow(PATHS_CSV_HEADERS)
    for path in result["samplePaths"]:
        for point in path["points"]:
            writer.writerow([
                PATHS_CSV_SCHEMA, ENGINE_VERSION, result["analysisId"], result["mode"],
                _export_number(path["pathIndex"]), _export_number(point["step"]), _export_number(point["timeYears"]),
                _export_number(point["spot"]),
            ])
    return stream.getvalue()


def export_json(result: Mapping[str, Any]) -> str:
    _assert_recursive_finite(result, "result")
    return json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + "\n"


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise MonteCarloError(f"duplicate JSON field: {key}.")
        result[key] = value
    return result


def load_request_file(path: str) -> dict[str, Any]:
    try:
        info = os.stat(path)
    except OSError as exc:
        raise MonteCarloError(f"cannot stat input file: {exc}.") from exc
    if not stat.S_ISREG(info.st_mode):
        raise MonteCarloError("input path must be a regular file.")
    if info.st_size > MAX_INPUT_BYTES:
        raise MonteCarloError(f"input file exceeds {MAX_INPUT_BYTES} bytes.")
    try:
        with open(path, "rb") as handle:
            payload = handle.read(MAX_INPUT_BYTES + 1)
    except OSError as exc:
        raise MonteCarloError(f"cannot read input file: {exc}.") from exc
    if len(payload) > MAX_INPUT_BYTES:
        raise MonteCarloError(f"input file exceeds {MAX_INPUT_BYTES} bytes.")
    try:
        text = payload.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise MonteCarloError("input file must be UTF-8 JSON.") from exc
    try:
        raw = json.loads(text, object_pairs_hook=_reject_duplicate_keys, parse_constant=lambda value: (_ for _ in ()).throw(MonteCarloError(f"JSON constant {value} is forbidden.")))
    except MonteCarloError:
        raise
    except json.JSONDecodeError as exc:
        raise MonteCarloError(f"invalid JSON: {exc.msg} at line {exc.lineno}, column {exc.colno}.") from exc
    return validate_request(raw)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the deterministic F-CAL-6 Monte Carlo engine.")
    parser.add_argument("--input", required=True, help="UTF-8 JSON request file")
    parser.add_argument("--format", required=True, choices=("json", "terminal-csv", "paths-csv"))
    args = parser.parse_args(argv)
    try:
        result = run_monte_carlo(load_request_file(args.input))
        output = export_json(result) if args.format == "json" else (export_terminal_csv(result) if args.format == "terminal-csv" else export_paths_csv(result))
    except MonteCarloError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    # Write the contract bytes directly.  Text-mode stdout rewrites ``\n`` to
    # ``\r\n`` on Windows, which would make the CLI CSV differ from the browser
    # export even though both engines produced the same canonical string.
    sys.stdout.buffer.write(output.encode("utf-8"))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
