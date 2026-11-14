"""Canonical deterministic implied-volatility surface quality engine (F-CAL-9)."""
from __future__ import annotations

import hashlib
import json
import math
import re
from datetime import date
from typing import Any, Mapping

INPUT_SCHEMA = "tpl.vol-surface.input.v1"
SCHEMA_VERSION = "tpl.vol-surface.analysis.v1"
ENGINE_VERSION = "1.0.0"
POINTS_CSV_SCHEMA = "tpl.vol-surface.points.v1"
DIAGNOSTICS_CSV_SCHEMA = "tpl.vol-surface.diagnostics.v1"
INPUT_KEYS = ["schemaVersion", "surfaceName", "asOfDate", "sourceKind", "interpolationMode", "selectedMaturity", "selectedLogMoneyness", "quotes"]
QUOTE_KEYS = ["maturity", "forward", "discountFactor", "logMoneyness", "impliedVolatility", "bidVolatility", "askVolatility"]
SOURCE_KINDS = ["deterministic_fixture", "user_csv"]
INTERPOLATION_MODE = "total_variance_bilinear"
LIMITS = {"minMaturities": 2, "minLogMoneynessPoints": 5, "maxQuotes": 500, "minMaturity": 1 / 365, "maxMaturity": 30, "minForward": 1e-6, "maxForward": 1e9, "minDiscountFactor": 1e-6, "maxDiscountFactor": 2, "minLogMoneyness": -2, "maxLogMoneyness": 2, "minVolatility": 1e-4, "maxVolatility": 5}
CONVENTIONS = {"coordinate": "k = ln(K/F)", "variance": "w(k,T) = impliedVolatility^2 * T", "interpolation": "piecewise linear in log-moneyness and maturity on total variance; no extrapolation", "pricing": "forward-normalized undiscounted Black call, then multiplied by discountFactor * forward", "arbitrage": "discrete diagnostics on submitted nodes; not a proof between nodes"}
LIMITATIONS = ["Educational deterministic surface-quality analysis; inputs are user assumptions or a labelled fixture, never live quotes.", "Diagnostics are discrete necessary checks on submitted nodes, not a continuous global arbitrage proof.", "Interpolation is inside the rectangular grid only; no extrapolation, smoothing, sorting, filling or clipping is performed.", "No SVI/SABR/Heston calibration, Dupire local volatility, stochastic rates, dividends, American exercise or trading signal is inferred."]
POINTS_HEADERS = ["schemaVersion", "engineVersion", "analysisId", "surfaceName", "asOfDate", "sourceKind", "maturityYears", "forward", "discountFactor", "logMoneyness", "strike", "impliedVolatility", "bidVolatility", "askVolatility", "totalVariance", "normalizedCall", "discountedCallPrice"]
DIAGNOSTICS_HEADERS = ["schemaVersion", "engineVersion", "analysisId", "surfaceName", "asOfDate", "status", "severity", "code", "maturityYears", "logMoneyness", "message"]
EPS, ARB_EPS = 1e-12, 1e-10


def _exact_keys(value: Mapping[str, Any], keys: list[str], label: str) -> None:
    missing = [key for key in keys if key not in value]
    unknown = [key for key in value if key not in keys]
    if missing or unknown:
        raise ValueError(f"{label} schema is invalid; missing={'|'.join(missing) or 'none'}; unknown={'|'.join(unknown) or 'none'}.")


def _finite(value: Any, label: str, minimum: float, maximum: float) -> float:
    if isinstance(value, bool) or type(value) not in (int, float) or not math.isfinite(value):
        raise ValueError(f"{label} must be a finite number.")
    result = float(value)
    if result < minimum or result > maximum:
        raise ValueError(f"{label} is outside the supported domain.")
    return 0.0 if result == 0 else result


def _nullable_vol(value: Any, label: str) -> float | None:
    return None if value is None else _finite(value, label, LIMITS["minVolatility"], LIMITS["maxVolatility"])


def _strict_date(value: Any) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        raise ValueError("asOfDate must use strict YYYY-MM-DD format.")
    try:
        if date.fromisoformat(value).isoformat() != value:
            raise ValueError
    except ValueError as exc:
        raise ValueError("asOfDate is invalid.") from exc
    return value


def normalize_vol_surface_input(raw: Any) -> dict[str, Any]:
    if type(raw) is not dict:
        raise ValueError("Vol-surface input must be a plain object.")
    _exact_keys(raw, INPUT_KEYS, "Vol-surface input")
    if raw["schemaVersion"] != INPUT_SCHEMA:
        raise ValueError(f"schemaVersion must be '{INPUT_SCHEMA}'.")
    if not isinstance(raw["surfaceName"], str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9 ._/-]{0,79}", raw["surfaceName"]):
        raise ValueError("surfaceName must contain 1-80 safe display characters.")
    if raw["sourceKind"] not in SOURCE_KINDS:
        raise ValueError("sourceKind is unsupported.")
    if raw["interpolationMode"] != INTERPOLATION_MODE:
        raise ValueError(f"interpolationMode must be '{INTERPOLATION_MODE}'.")
    if type(raw["quotes"]) is not list or len(raw["quotes"]) > LIMITS["maxQuotes"]:
        raise ValueError(f"quotes must be an array with at most {LIMITS['maxQuotes']} rows.")
    quotes: list[dict[str, Any]] = []
    for index, quote in enumerate(raw["quotes"]):
        if type(quote) is not dict:
            raise ValueError(f"quotes[{index}] must be a plain object.")
        _exact_keys(quote, QUOTE_KEYS, f"quotes[{index}]")
        row = {"maturity": _finite(quote["maturity"], f"quotes[{index}].maturity", LIMITS["minMaturity"], LIMITS["maxMaturity"]), "forward": _finite(quote["forward"], f"quotes[{index}].forward", LIMITS["minForward"], LIMITS["maxForward"]), "discountFactor": _finite(quote["discountFactor"], f"quotes[{index}].discountFactor", LIMITS["minDiscountFactor"], LIMITS["maxDiscountFactor"]), "logMoneyness": _finite(quote["logMoneyness"], f"quotes[{index}].logMoneyness", LIMITS["minLogMoneyness"], LIMITS["maxLogMoneyness"]), "impliedVolatility": _finite(quote["impliedVolatility"], f"quotes[{index}].impliedVolatility", LIMITS["minVolatility"], LIMITS["maxVolatility"]), "bidVolatility": _nullable_vol(quote["bidVolatility"], f"quotes[{index}].bidVolatility"), "askVolatility": _nullable_vol(quote["askVolatility"], f"quotes[{index}].askVolatility")}
        if (row["bidVolatility"] is None) != (row["askVolatility"] is None):
            raise ValueError(f"quotes[{index}] bid/ask must both be null or both be finite.")
        if row["bidVolatility"] is not None and not (row["bidVolatility"] <= row["impliedVolatility"] <= row["askVolatility"]):
            raise ValueError(f"quotes[{index}] must satisfy bid <= implied <= ask.")
        quotes.append(row)
    slices: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    seen: set[tuple[float, float]] = set()
    for row in quotes:
        key = (row["maturity"], row["logMoneyness"])
        if key in seen:
            raise ValueError(f"Duplicate quote node at maturity={row['maturity']}, k={row['logMoneyness']}.")
        seen.add(key)
        if current is None or abs(row["maturity"] - current["maturity"]) > EPS:
            if current is not None and row["maturity"] <= current["maturity"]:
                raise ValueError("Quote rows must be ordered by strictly increasing maturity without hidden sorting.")
            current = {"maturity": row["maturity"], "forward": row["forward"], "discountFactor": row["discountFactor"], "rows": []}
            slices.append(current)
        if abs(row["maturity"] - current["maturity"]) > EPS or abs(row["forward"] - current["forward"]) > EPS or abs(row["discountFactor"] - current["discountFactor"]) > EPS:
            raise ValueError(f"All rows in maturity slice {current['maturity']} must share forward and discountFactor.")
        if current["rows"] and row["logMoneyness"] <= current["rows"][-1]["logMoneyness"]:
            raise ValueError(f"Log-moneyness rows inside maturity {current['maturity']} must be strictly increasing without hidden sorting.")
        current["rows"].append(row)
    if len(slices) < LIMITS["minMaturities"]:
        raise ValueError(f"Surface requires at least {LIMITS['minMaturities']} maturities.")
    grid = [row["logMoneyness"] for row in slices[0]["rows"]]
    if len(grid) < LIMITS["minLogMoneynessPoints"]:
        raise ValueError(f"Each maturity requires at least {LIMITS['minLogMoneynessPoints']} log-moneyness points.")
    if not any(abs(value) <= EPS for value in grid):
        raise ValueError("The rectangular grid must contain an exact ATM k=0 node.")
    for surface_slice in slices:
        if len(surface_slice["rows"]) != len(grid) or any(abs(row["logMoneyness"] - grid[i]) > EPS for i, row in enumerate(surface_slice["rows"])):
            raise ValueError("Every maturity must use the same complete rectangular log-moneyness grid; no filling is performed.")
    selected_maturity = _finite(raw["selectedMaturity"], "selectedMaturity", LIMITS["minMaturity"], LIMITS["maxMaturity"])
    selected_k = _finite(raw["selectedLogMoneyness"], "selectedLogMoneyness", LIMITS["minLogMoneyness"], LIMITS["maxLogMoneyness"])
    if selected_maturity < slices[0]["maturity"] - EPS or selected_maturity > slices[-1]["maturity"] + EPS or selected_k < grid[0] - EPS or selected_k > grid[-1] + EPS:
        raise ValueError("Selected interpolation point is outside the submitted grid; extrapolation is forbidden.")
    return {"schemaVersion": INPUT_SCHEMA, "surfaceName": raw["surfaceName"], "asOfDate": _strict_date(raw["asOfDate"]), "sourceKind": raw["sourceKind"], "interpolationMode": raw["interpolationMode"], "selectedMaturity": selected_maturity, "selectedLogMoneyness": selected_k, "quotes": quotes}


def _norm_cdf(x: float) -> float:
    sign = -1 if x < 0 else 1
    z = abs(x) / math.sqrt(2)
    t = 1 / (1 + 0.3275911 * z)
    erf = 1 - (((((1.061405429 * t - 1.453152027) * t) + 1.421413741) * t - 0.284496736) * t + 0.254829592) * t * math.exp(-z * z)
    return 0.5 * (1 + sign * erf)


def _black_normalized_call(k: float, total_variance: float) -> float:
    if total_variance <= 0:
        return max(1 - math.exp(k), 0)
    root = math.sqrt(total_variance)
    d1 = -k / root + 0.5 * root
    return _norm_cdf(d1) - math.exp(k) * _norm_cdf(d1 - root)


def _canonical_number(value: float) -> str:
    if not math.isfinite(value): raise ValueError("Canonical data contains a non-finite number.")
    if value == 0: return "0"
    mantissa, exponent = format(value, ".16e").lower().split("e")
    return f"{mantissa.rstrip('0').rstrip('.')}e{int(exponent)}"


def _canonical_tree(value: Any) -> Any:
    if isinstance(value, bool) or value is None or isinstance(value, str): return value
    if type(value) in (int, float): return _canonical_number(float(value))
    if isinstance(value, list): return [_canonical_tree(item) for item in value]
    if isinstance(value, Mapping): return {key: _canonical_tree(value[key]) for key in sorted(value)}
    return value


def _analysis_id(input_data: Mapping[str, Any]) -> str:
    payload = json.dumps(_canonical_tree(input_data), ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


def _bracket(values: list[float], target: float) -> tuple[int, int, float]:
    if target <= values[0] + EPS: return 0, 0, 0.0
    if target >= values[-1] - EPS: return len(values) - 1, len(values) - 1, 0.0
    for index in range(len(values) - 1):
        if values[index] - EPS <= target <= values[index + 1] + EPS:
            weight = (target - values[index]) / (values[index + 1] - values[index])
            return index, index + 1, max(0.0, min(1.0, weight))
    raise ValueError("Interpolation bracket is unavailable.")


def analyze_vol_surface(raw: Any) -> dict[str, Any]:
    input_data = normalize_vol_surface_input(raw)
    analysis_id = _analysis_id(input_data)
    maturities = list(dict.fromkeys(row["maturity"] for row in input_data["quotes"]))
    width = len(input_data["quotes"]) // len(maturities)
    ks = [row["logMoneyness"] for row in input_data["quotes"][:width]]
    slices = []
    for maturity in maturities:
        submitted = [row for row in input_data["quotes"] if row["maturity"] == maturity]
        points = []
        for row in submitted:
            strike = row["forward"] * math.exp(row["logMoneyness"])
            total_variance = row["impliedVolatility"] ** 2 * row["maturity"]
            normalized_call = _black_normalized_call(row["logMoneyness"], total_variance)
            points.append({**row, "strike": strike, "totalVariance": total_variance, "normalizedCall": normalized_call, "discountedCallPrice": row["discountFactor"] * row["forward"] * normalized_call})
        atm_index = next(index for index, row in enumerate(points) if abs(row["logMoneyness"]) <= EPS)
        if atm_index == 0 or atm_index == len(points) - 1:
            raise ValueError("ATM k=0 must have at least one submitted node on each side.")
        left, atm, right = points[atm_index - 1], points[atm_index], points[atm_index + 1]
        skew = (right["impliedVolatility"] - left["impliedVolatility"]) / (right["logMoneyness"] - left["logMoneyness"])
        left_slope = (atm["impliedVolatility"] - left["impliedVolatility"]) / (atm["logMoneyness"] - left["logMoneyness"])
        right_slope = (right["impliedVolatility"] - atm["impliedVolatility"]) / (right["logMoneyness"] - atm["logMoneyness"])
        curvature = 2 * (right_slope - left_slope) / (right["logMoneyness"] - left["logMoneyness"])
        slices.append({"maturity": maturity, "forward": atm["forward"], "discountFactor": atm["discountFactor"], "atmVolatility": atm["impliedVolatility"], "atmTotalVariance": atm["totalVariance"], "skew": skew, "curvature": curvature, "points": points})
    diagnostics = []
    for surface_slice in slices:
        for point in surface_slice["points"]:
            lower = max(surface_slice["discountFactor"] * (surface_slice["forward"] - point["strike"]), 0)
            upper = surface_slice["discountFactor"] * surface_slice["forward"]
            if point["discountedCallPrice"] < lower - ARB_EPS or point["discountedCallPrice"] > upper + ARB_EPS:
                diagnostics.append({"severity": "error", "code": "CALL_BOUND_VIOLATION", "maturityYears": surface_slice["maturity"], "logMoneyness": point["logMoneyness"], "message": "Discounted Black call falls outside intrinsic/forward bounds."})
            if point["bidVolatility"] is not None and point["askVolatility"] - point["bidVolatility"] > 0.05:
                diagnostics.append({"severity": "warning", "code": "WIDE_BID_ASK", "maturityYears": surface_slice["maturity"], "logMoneyness": point["logMoneyness"], "message": "Bid/ask width exceeds five volatility points."})
        slopes = []
        for index in range(len(surface_slice["points"]) - 1):
            a, b = surface_slice["points"][index:index + 2]
            slope = (b["discountedCallPrice"] - a["discountedCallPrice"]) / (b["strike"] - a["strike"])
            slopes.append(slope)
            if slope > ARB_EPS or slope < -surface_slice["discountFactor"] - ARB_EPS:
                diagnostics.append({"severity": "error", "code": "VERTICAL_SPREAD_VIOLATION", "maturityYears": surface_slice["maturity"], "logMoneyness": b["logMoneyness"], "message": "Discrete call slope is outside [-discountFactor, 0]."})
        for index in range(1, len(slopes)):
            if slopes[index] < slopes[index - 1] - ARB_EPS:
                diagnostics.append({"severity": "error", "code": "BUTTERFLY_CONVEXITY_VIOLATION", "maturityYears": surface_slice["maturity"], "logMoneyness": surface_slice["points"][index]["logMoneyness"], "message": "Discrete call slopes decrease with strike, violating convexity."})
    for maturity_index in range(1, len(slices)):
        for k_index, k in enumerate(ks):
            if slices[maturity_index]["points"][k_index]["totalVariance"] < slices[maturity_index - 1]["points"][k_index]["totalVariance"] - ARB_EPS:
                previous_maturity = format(slices[maturity_index - 1]["maturity"], ".15g")
                diagnostics.append({"severity": "error", "code": "CALENDAR_VARIANCE_VIOLATION", "maturityYears": slices[maturity_index]["maturity"], "logMoneyness": k, "message": f"Total variance is below the preceding maturity {previous_maturity}."})
    error_count = sum(row["severity"] == "error" for row in diagnostics)
    warning_count = sum(row["severity"] == "warning" for row in diagnostics)
    status = "POTENTIAL_ARBITRAGE" if error_count else "PASS"
    if not diagnostics:
        diagnostics.append({"severity": "info", "code": "NO_DISCRETE_ARBITRAGE_FLAGS", "maturityYears": None, "logMoneyness": None, "message": "All submitted-node bound, vertical, convexity and calendar checks passed."})
    t0, t1, tw = _bracket(maturities, input_data["selectedMaturity"])
    k0, k1, kw = _bracket(ks, input_data["selectedLogMoneyness"])
    variance_at = lambda ti: slices[ti]["points"][k0]["totalVariance"] + kw * (slices[ti]["points"][k1]["totalVariance"] - slices[ti]["points"][k0]["totalVariance"])
    selected_variance = variance_at(t0) + tw * (variance_at(t1) - variance_at(t0))
    selected_forward = slices[t0]["forward"] + tw * (slices[t1]["forward"] - slices[t0]["forward"])
    selected_discount = math.exp(math.log(slices[t0]["discountFactor"]) + tw * (math.log(slices[t1]["discountFactor"]) - math.log(slices[t0]["discountFactor"])))
    selected_vol = math.sqrt(selected_variance / input_data["selectedMaturity"])
    selected_strike = selected_forward * math.exp(input_data["selectedLogMoneyness"])
    selected_normalized_call = _black_normalized_call(input_data["selectedLogMoneyness"], selected_variance)
    points = [point for surface_slice in slices for point in surface_slice["points"]]
    vols = [row["impliedVolatility"] for row in points]
    bid_ask_count = sum(row["bidVolatility"] is not None for row in points)
    return {"schemaVersion": SCHEMA_VERSION, "engineVersion": ENGINE_VERSION, "analysisId": analysis_id, "input": input_data, "quality": {"status": status, "errorCount": error_count, "warningCount": warning_count, "quoteCount": len(points), "maturityCount": len(maturities), "logMoneynessCount": len(ks), "bidAskCoverage": bid_ask_count / len(points), "minImpliedVolatility": min(vols), "maxImpliedVolatility": max(vols)}, "selectedPoint": {"maturity": input_data["selectedMaturity"], "logMoneyness": input_data["selectedLogMoneyness"], "forward": selected_forward, "discountFactor": selected_discount, "strike": selected_strike, "totalVariance": selected_variance, "impliedVolatility": selected_vol, "normalizedCall": selected_normalized_call, "discountedCallPrice": selected_discount * selected_forward * selected_normalized_call, "maturityBracket": [maturities[t0], maturities[t1]], "logMoneynessBracket": [ks[k0], ks[k1]]}, "slices": slices, "points": points, "diagnostics": diagnostics, "conventions": CONVENTIONS, "limitations": LIMITATIONS}


def _export_number(value: float | None) -> str:
    if value is None: return ""
    if not math.isfinite(value): raise ValueError("Evidence export contains a non-finite number.")
    if value == 0 or abs(value) < 1e-15: return "0"
    mantissa, exponent = format(value, ".8e").lower().split("e")
    return f"{mantissa.rstrip('0').rstrip('.')}e{int(exponent)}"


def _csv_escape(value: Any) -> str:
    text = "" if value is None else str(value)
    return f'"{text.replace(chr(34), chr(34) * 2)}"' if any(char in text for char in ',"\n\r') else text


def _csv(headers: list[str], rows: list[dict[str, Any]]) -> str:
    output = [",".join(headers)]
    output.extend(",".join(_csv_escape(_export_number(row.get(header)) if type(row.get(header)) is float else row.get(header)) for header in headers) for row in rows)
    return "\n".join(output) + ("\n" if rows else "")


def build_vol_surface_points_csv(result: Mapping[str, Any]) -> str:
    rows = [{"schemaVersion": POINTS_CSV_SCHEMA, "engineVersion": result["engineVersion"], "analysisId": result["analysisId"], "surfaceName": result["input"]["surfaceName"], "asOfDate": result["input"]["asOfDate"], "sourceKind": result["input"]["sourceKind"], "maturityYears": row["maturity"], "forward": row["forward"], "discountFactor": row["discountFactor"], "logMoneyness": row["logMoneyness"], "strike": row["strike"], "impliedVolatility": row["impliedVolatility"], "bidVolatility": row["bidVolatility"], "askVolatility": row["askVolatility"], "totalVariance": row["totalVariance"], "normalizedCall": row["normalizedCall"], "discountedCallPrice": row["discountedCallPrice"]} for row in result["points"]]
    return _csv(POINTS_HEADERS, rows)


def build_vol_surface_diagnostics_csv(result: Mapping[str, Any]) -> str:
    rows = [{"schemaVersion": DIAGNOSTICS_CSV_SCHEMA, "engineVersion": result["engineVersion"], "analysisId": result["analysisId"], "surfaceName": result["input"]["surfaceName"], "asOfDate": result["input"]["asOfDate"], "status": result["quality"]["status"], **row} for row in result["diagnostics"]]
    return _csv(DIAGNOSTICS_HEADERS, rows)


def build_deterministic_vol_surface(variant: str = "clean") -> list[dict[str, Any]]:
    quotes = []
    for maturity in [0.25, 0.5, 1.0, 2.0]:
        forward, discount_factor = 100 * math.exp(0.02 * maturity), math.exp(-0.03 * maturity)
        for k in [-0.3, -0.15, 0.0, 0.15, 0.3]:
            vol = 0.2 - 0.06 * k + 0.1 * k * k + 0.01 * math.log1p(maturity)
            if variant == "calendar" and maturity == 1: vol = 0.1 + 0.01 * k * k
            if variant == "butterfly" and maturity == 1 and k == 0: vol = 0.8
            quotes.append({"maturity": maturity, "forward": forward, "discountFactor": discount_factor, "logMoneyness": k, "impliedVolatility": vol, "bidVolatility": max(0.0001, vol - 0.005), "askVolatility": vol + 0.005})
    return quotes
