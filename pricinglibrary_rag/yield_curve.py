"""Deterministic single-curve bootstrap shared by CLI/API calculation paths.

This mirrors the browser engine's financial contract.  It supports spot
deposits, sequential FRAs, explicitly convexity-adjusted STIR futures and
regular spot-starting par swaps.  Sparse swap pillars are completed with
log-linear discount-factor interpolation; extrapolation and implicit stubs are
rejected.
"""

from __future__ import annotations

import math
from typing import Any, Mapping, Sequence


YIELD_CURVE_VERSION = "1.0.0"
YIELD_CURVE_RESULT_SCHEMA = "tpl.yield-curve.result.v1"
MAX_CURVE_INSTRUMENTS = 64

_EPSILON = 1e-12
_TIME_TOLERANCE = 1e-10
_REPRICING_TOLERANCE = 1e-10
_SUPPORTED_TYPES = {"deposit", "fra", "future", "swap"}
_SUPPORTED_FREQUENCIES = {1, 2, 4}

DEFAULT_CONVENTIONS: dict[str, Any] = {
    "timeInput": "ACT/365F year fractions supplied by the user",
    "rateUnit": "decimal",
    "depositCompounding": "simple",
    "fraCompounding": "simple",
    "futureQuote": "price points; futures rate = (100 - price) / 100",
    "futureConvexity": "FRA-equivalent rate = futures rate - explicit convexity adjustment",
    "fixedLegFrequency": 1,
    "fixedLegSchedule": "regular spot-starting periods; no implicit stubs",
    "floatingLeg": "single-curve par identity: PV(float) = 1 - DF(T)",
    "interpolation": "log-linear discount factors",
    "extrapolation": "forbidden",
    "zeroRates": "continuous and annually compounded",
    "forwardRates": "continuous and simply annualized over the displayed interval",
}

LIMITATIONS = [
    "Educational deterministic mono-curve: discounting and projection use the same curve.",
    "Maturities are year fractions, not calendar dates; holidays, settlement lags and business-day rules are not modeled.",
    "Only regular spot-starting swap schedules are supported; explicit stubs are rejected.",
    "STIR futures require an explicit convexity adjustment, including an explicit 0 bp assumption.",
    "No discount-factor extrapolation is performed beyond the final market pillar.",
]


class YieldCurveError(ValueError):
    """Explicit input, bootstrap or repricing failure."""


def _is_close(left: float, right: float, tolerance: float = _TIME_TOLERANCE) -> bool:
    return abs(left - right) <= tolerance


def _round_time(value: float) -> float:
    return round(value, 12)


def _number(raw: Any) -> float:
    try:
        return float(raw)
    except (TypeError, ValueError) as exc:
        raise YieldCurveError("Curve input contains a non-numeric value.") from exc


def _normalize_conventions(raw: Mapping[str, Any] | None = None) -> dict[str, Any]:
    raw = raw or {}
    frequency = int(raw.get("fixedLegFrequency", DEFAULT_CONVENTIONS["fixedLegFrequency"]))
    if frequency not in _SUPPORTED_FREQUENCIES:
        raise YieldCurveError("Fixed-leg frequency must be 1, 2 or 4 payments per year.")
    interpolation = raw.get("interpolation", DEFAULT_CONVENTIONS["interpolation"])
    if interpolation != DEFAULT_CONVENTIONS["interpolation"]:
        raise YieldCurveError("Only 'log-linear discount factors' interpolation is supported.")
    extrapolation = raw.get("extrapolation", "forbidden")
    if extrapolation != "forbidden":
        raise YieldCurveError("Discount-factor extrapolation is forbidden.")
    return {**DEFAULT_CONVENTIONS, "fixedLegFrequency": frequency}


def _normalize_instrument(raw: Mapping[str, Any], index: int) -> dict[str, Any]:
    if not isinstance(raw, Mapping):
        raise YieldCurveError(f"Instrument {index + 1} must be an object.")
    instrument_type = str(raw.get("type", raw.get("instrument", ""))).strip().lower()
    if instrument_type not in _SUPPORTED_TYPES:
        raise YieldCurveError(
            f"Instrument {index + 1} has unsupported type '{instrument_type or 'empty'}'."
        )
    maturity = _number(raw.get("maturity", raw.get("maturityYears")))
    start = (
        _number(raw.get("start", raw.get("startYears")))
        if instrument_type in {"fra", "future"}
        else 0.0
    )
    future_price: float | None = None
    convexity_adjustment: float | None = None
    futures_rate: float | None = None
    if instrument_type == "future":
        if "futurePrice" not in raw:
            raise YieldCurveError(
                f"Instrument {index + 1}: a STIR future requires futurePrice in price points."
            )
        if "convexityAdjustment" not in raw:
            raise YieldCurveError(
                f"Instrument {index + 1}: a STIR future requires an explicit convexityAdjustment, including 0."
            )
        future_price = _number(raw["futurePrice"])
        convexity_adjustment = _number(raw["convexityAdjustment"])
        futures_rate = (100.0 - future_price) / 100.0
        quote = futures_rate - convexity_adjustment
    else:
        quote = _number(raw.get("quote", raw.get("quoteDecimal")))
    return {
        "id": f"{instrument_type}-{index + 1}",
        "type": instrument_type,
        "start": start,
        "maturity": maturity,
        "quote": quote,
        "futurePrice": future_price,
        "futuresRate": futures_rate,
        "convexityAdjustment": convexity_adjustment,
    }


def validate_curve_instruments(
    raw_instruments: Sequence[Mapping[str, Any]],
    convention_input: Mapping[str, Any] | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    conventions = _normalize_conventions(convention_input)
    if not isinstance(raw_instruments, Sequence) or isinstance(raw_instruments, (str, bytes)):
        raise YieldCurveError("Curve instruments must be an array.")
    if len(raw_instruments) < 2:
        raise YieldCurveError("Curve construction requires at least two instruments.")
    if len(raw_instruments) > MAX_CURVE_INSTRUMENTS:
        raise YieldCurveError(
            f"Curve construction accepts at most {MAX_CURVE_INSTRUMENTS} instruments."
        )
    instruments = [_normalize_instrument(raw, index) for index, raw in enumerate(raw_instruments)]
    previous_maturity = 0.0
    for index, instrument in enumerate(instruments):
        label = f"Instrument {index + 1} ({instrument['type']})"
        values = (instrument["start"], instrument["maturity"], instrument["quote"])
        if not all(math.isfinite(value) for value in values):
            raise YieldCurveError(f"{label} contains a non-finite start, maturity or quote.")
        maturity = instrument["maturity"]
        quote = instrument["quote"]
        if maturity <= 0 or maturity > 50:
            raise YieldCurveError(f"{label}: maturity must be in (0, 50] years.")
        if index and maturity <= previous_maturity + _TIME_TOLERANCE:
            raise YieldCurveError(
                f"{label}: maturities must be strictly increasing with no duplicate or quasi-duplicate pillar."
            )
        if instrument["type"] == "future":
            future_values = (
                instrument["futurePrice"],
                instrument["convexityAdjustment"],
                instrument["futuresRate"],
            )
            if not all(value is not None and math.isfinite(value) for value in future_values):
                raise YieldCurveError(
                    f"{label}: future price and convexity adjustment must be finite."
                )
            if instrument["futurePrice"] <= 0 or instrument["futurePrice"] >= 200:
                raise YieldCurveError(
                    f"{label}: future price must be in (0, 200) price points."
                )
            if abs(instrument["convexityAdjustment"]) > 0.1:
                raise YieldCurveError(
                    f"{label}: absolute convexity adjustment cannot exceed 1,000 bp."
                )
        if quote < -0.25 or quote > 2:
            raise YieldCurveError(f"{label}: decimal rate must be between -0.25 and 2.")
        if instrument["type"] == "deposit" and 1 + quote * maturity <= _EPSILON:
            raise YieldCurveError(f"{label}: 1 + rate x accrual must be positive.")
        if instrument["type"] in {"fra", "future"}:
            start = instrument["start"]
            if start < 0 or start >= maturity - _TIME_TOLERANCE:
                raise YieldCurveError(f"{label}: start must satisfy 0 <= start < maturity.")
            if start > previous_maturity + _TIME_TOLERANCE:
                raise YieldCurveError(
                    f"{label}: start {start}Y is not covered by the curve built through "
                    f"{previous_maturity}Y; extrapolation is forbidden."
                )
            if 1 + quote * (maturity - start) <= _EPSILON:
                raise YieldCurveError(
                    f"{label}: 1 + forward rate x accrual must be positive."
                )
        if instrument["type"] == "swap":
            periods = maturity * conventions["fixedLegFrequency"]
            if not _is_close(periods, round(periods)):
                raise YieldCurveError(
                    f"{label}: maturity creates an implicit stub at "
                    f"{conventions['fixedLegFrequency']} payments/year; provide a regular maturity."
                )
        previous_maturity = maturity
    return instruments, conventions


def regular_swap_schedule(maturity: float, fixed_leg_frequency: int = 1) -> list[dict[str, float]]:
    if not math.isfinite(maturity) or maturity <= 0:
        raise YieldCurveError("Swap maturity must be positive and finite.")
    if fixed_leg_frequency not in _SUPPORTED_FREQUENCIES:
        raise YieldCurveError("Fixed-leg frequency must be 1, 2 or 4.")
    periods = maturity * fixed_leg_frequency
    if not _is_close(periods, round(periods)):
        raise YieldCurveError(
            "Swap maturity would require an implicit stub, which is not supported."
        )
    accrual = 1.0 / fixed_leg_frequency
    return [
        {"time": _round_time((index + 1) * accrual), "accrual": accrual}
        for index in range(round(periods))
    ]


def interpolate_log_discount_factor(time: float, anchors: Sequence[Mapping[str, float]]) -> float:
    if not math.isfinite(time) or time < 0:
        raise YieldCurveError("Discount-factor time must be finite and >= 0.")
    if not anchors:
        raise YieldCurveError("At least the t=0 curve anchor is required.")
    if not _is_close(float(anchors[0]["time"]), 0) or not _is_close(
        float(anchors[0]["discountFactor"]), 1
    ):
        raise YieldCurveError("Curve anchors must start at t=0 with DF=1.")
    for index, anchor in enumerate(anchors):
        anchor_time = float(anchor["time"])
        discount_factor = float(anchor["discountFactor"])
        if not math.isfinite(anchor_time) or not math.isfinite(discount_factor) or discount_factor <= 0:
            raise YieldCurveError(
                "Curve anchors must have finite times and strictly positive discount factors."
            )
        if index and anchor_time <= float(anchors[index - 1]["time"]) + _TIME_TOLERANCE:
            raise YieldCurveError("Curve anchor times must be strictly increasing.")
    last_time = float(anchors[-1]["time"])
    if time > last_time + _TIME_TOLERANCE:
        raise YieldCurveError(
            f"Discount factor at {time}Y requires extrapolation beyond {last_time}Y, which is forbidden."
        )
    for anchor in anchors:
        if _is_close(float(anchor["time"]), time):
            return float(anchor["discountFactor"])
    for index in range(1, len(anchors)):
        left = anchors[index - 1]
        right = anchors[index]
        left_time = float(left["time"])
        right_time = float(right["time"])
        if left_time < time < right_time:
            weight = (time - left_time) / (right_time - left_time)
            return math.exp(
                (1 - weight) * math.log(float(left["discountFactor"]))
                + weight * math.log(float(right["discountFactor"]))
            )
    raise YieldCurveError(
        f"Discount factor at {time}Y is outside the supported interpolation domain."
    )


def _swap_pv_residual(
    quote: float,
    schedule: Sequence[Mapping[str, float]],
    anchors: Sequence[Mapping[str, float]],
) -> float:
    annuity = sum(
        float(payment["accrual"])
        * interpolate_log_discount_factor(float(payment["time"]), anchors)
        for payment in schedule
    )
    terminal_discount = interpolate_log_discount_factor(
        float(schedule[-1]["time"]), anchors
    )
    return quote * annuity - (1 - terminal_discount)


def _solve_sparse_swap(
    instrument: Mapping[str, Any],
    anchors: list[dict[str, Any]],
    conventions: Mapping[str, Any],
) -> tuple[float, int, int]:
    schedule = regular_swap_schedule(
        float(instrument["maturity"]), int(conventions["fixedLegFrequency"])
    )
    last_anchor = anchors[-1]

    def residual(log_discount: float) -> float:
        candidate_anchors = [
            *anchors,
            {
                "time": float(instrument["maturity"]),
                "discountFactor": math.exp(log_discount),
                "instrumentId": instrument["id"],
            },
        ]
        return _swap_pv_residual(float(instrument["quote"]), schedule, candidate_anchors)

    lower = -30.0
    upper = math.log(100.0)
    scan_steps = 512
    brackets: list[tuple[float, float]] = []
    previous_log = lower
    previous_residual = residual(previous_log)
    if not math.isfinite(previous_residual):
        raise YieldCurveError(f"{instrument['id']}: swap root residual is not finite.")
    for step in range(1, scan_steps + 1):
        current_log = lower + (upper - lower) * step / scan_steps
        current_residual = residual(current_log)
        if not math.isfinite(current_residual):
            raise YieldCurveError(f"{instrument['id']}: swap root residual is not finite.")
        if abs(previous_residual) <= 1e-15:
            brackets.append((previous_log, previous_log))
        elif abs(current_residual) <= 1e-15:
            brackets.append((current_log, current_log))
        elif math.copysign(1.0, previous_residual) != math.copysign(1.0, current_residual):
            brackets.append((previous_log, current_log))
        previous_log = current_log
        previous_residual = current_residual
    unique_brackets: list[tuple[float, float]] = []
    for bracket in brackets:
        if not unique_brackets or not _is_close(bracket[0], unique_brackets[-1][0], 1e-9):
            unique_brackets.append(bracket)
    if len(unique_brackets) != 1:
        description = "not unique" if unique_brackets else "not bracketed"
        raise YieldCurveError(
            f"{instrument['id']}: swap discount-factor root is {description} in the supported positive domain."
        )
    low, high = unique_brackets[0]
    iterations = 0
    if not _is_close(low, high, 1e-15):
        low_residual = residual(low)
        for iterations in range(200):
            mid = 0.5 * (low + high)
            mid_residual = residual(mid)
            if abs(mid_residual) <= 1e-15 or abs(high - low) <= 1e-14:
                low = high = mid
                break
            if math.copysign(1.0, low_residual) == math.copysign(1.0, mid_residual):
                low = mid
                low_residual = mid_residual
            else:
                high = mid
    discount_factor = math.exp(0.5 * (low + high))
    if not math.isfinite(discount_factor) or discount_factor <= 0:
        raise YieldCurveError(
            f"{instrument['id']}: solved discount factor is not finite and positive."
        )
    solved_anchors = [
        *anchors,
        {
            "time": float(instrument["maturity"]),
            "discountFactor": discount_factor,
            "instrumentId": instrument["id"],
        },
    ]
    final_residual = _swap_pv_residual(
        float(instrument["quote"]), schedule, solved_anchors
    )
    if not math.isfinite(final_residual) or abs(final_residual) > _REPRICING_TOLERANCE:
        raise YieldCurveError(
            f"{instrument['id']}: swap root did not converge within the repricing tolerance."
        )
    interpolated_count = sum(
        float(payment["time"]) > float(last_anchor["time"]) + _TIME_TOLERANCE
        and float(payment["time"]) < float(instrument["maturity"]) - _TIME_TOLERANCE
        for payment in schedule
    )
    return discount_factor, iterations, interpolated_count


def _reprice(
    instrument: Mapping[str, Any],
    anchors: Sequence[Mapping[str, Any]],
    conventions: Mapping[str, Any],
) -> dict[str, Any]:
    maturity = float(instrument["maturity"])
    quote = float(instrument["quote"])
    discount_end = interpolate_log_discount_factor(maturity, anchors)
    annuity: float | None = None
    discount_start = 1.0
    if instrument["type"] == "deposit":
        implied_quote = (1 / discount_end - 1) / maturity
        pv_residual = discount_end * (1 + quote * maturity) - 1
    elif instrument["type"] in {"fra", "future"}:
        start = float(instrument["start"])
        discount_start = interpolate_log_discount_factor(start, anchors)
        accrual = maturity - start
        implied_quote = (discount_start / discount_end - 1) / accrual
        pv_residual = discount_end * (1 + quote * accrual) - discount_start
    else:
        schedule = regular_swap_schedule(
            maturity, int(conventions["fixedLegFrequency"])
        )
        annuity = sum(
            float(payment["accrual"])
            * interpolate_log_discount_factor(float(payment["time"]), anchors)
            for payment in schedule
        )
        implied_quote = (1 - discount_end) / annuity
        pv_residual = quote * annuity - (1 - discount_end)
    output: dict[str, Any] = {
        "instrumentId": instrument["id"],
        "type": instrument["type"],
        "start": float(instrument["start"]),
        "maturity": maturity,
        "marketQuote": quote,
        "impliedQuote": implied_quote,
        "quoteResidual": implied_quote - quote,
        "pvResidual": pv_residual,
        "discountStart": discount_start,
        "discountEnd": discount_end,
        "annuity": annuity,
    }
    if instrument["type"] == "future":
        convexity = float(instrument["convexityAdjustment"])
        implied_future_price = 100 - 100 * (implied_quote + convexity)
        output.update(
            {
                "marketFuturePrice": float(instrument["futurePrice"]),
                "futuresRate": float(instrument["futuresRate"]),
                "convexityAdjustment": convexity,
                "fraEquivalentRate": quote,
                "impliedFuturePrice": implied_future_price,
                "futurePriceResidual": implied_future_price
                - float(instrument["futurePrice"]),
            }
        )
    return output


def _curve_nodes(
    instruments: Sequence[Mapping[str, Any]],
    anchors: Sequence[Mapping[str, Any]],
    conventions: Mapping[str, Any],
) -> list[dict[str, Any]]:
    times = {_round_time(float(anchor["time"])) for anchor in anchors[1:]}
    for instrument in instruments:
        if instrument["type"] in {"fra", "future"}:
            times.add(_round_time(float(instrument["start"])))
        if instrument["type"] == "swap":
            times.update(
                _round_time(float(payment["time"]))
                for payment in regular_swap_schedule(
                    float(instrument["maturity"]),
                    int(conventions["fixedLegFrequency"]),
                )
            )
    ordered_times: list[float] = []
    for value in sorted(times):
        if value > _TIME_TOLERANCE and (
            not ordered_times or not _is_close(value, ordered_times[-1])
        ):
            ordered_times.append(value)
    anchor_by_time = {
        _round_time(float(anchor["time"])): anchor for anchor in anchors[1:]
    }
    previous_time = 0.0
    previous_discount = 1.0
    output: list[dict[str, Any]] = []
    for time in ordered_times:
        discount_factor = interpolate_log_discount_factor(time, anchors)
        interval = time - previous_time
        ratio = previous_discount / discount_factor
        anchor = anchor_by_time.get(_round_time(time))
        output.append(
            {
                "time": time,
                "intervalStart": previous_time,
                "intervalEnd": time,
                "intervalYears": interval,
                "intervalLabel": f"{previous_time:g}Y->{time:g}Y",
                "source": "market-pillar" if anchor else "interpolated-cashflow",
                "instrumentId": anchor.get("instrumentId") if anchor else None,
                "discountFactor": discount_factor,
                "zeroContinuous": -math.log(discount_factor) / time,
                "zeroAnnual": discount_factor ** (-1 / time) - 1,
                "forwardContinuous": math.log(ratio) / interval,
                "forwardSimple": (ratio - 1) / interval,
                "forwardAnnualCompounded": ratio ** (1 / interval) - 1,
            }
        )
        previous_time = time
        previous_discount = discount_factor
    return output


def build_yield_curve(
    raw_instruments: Sequence[Mapping[str, Any]],
    convention_input: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    instruments, conventions = validate_curve_instruments(
        raw_instruments, convention_input
    )
    anchors: list[dict[str, Any]] = [
        {"time": 0.0, "discountFactor": 1.0, "instrumentId": "origin"}
    ]
    total_root_iterations = 0
    interpolated_coupon_count = 0
    for instrument in instruments:
        maturity = float(instrument["maturity"])
        quote = float(instrument["quote"])
        if instrument["type"] == "deposit":
            discount_factor = 1 / (1 + quote * maturity)
        elif instrument["type"] in {"fra", "future"}:
            start = float(instrument["start"])
            start_discount = interpolate_log_discount_factor(start, anchors)
            discount_factor = start_discount / (1 + quote * (maturity - start))
        else:
            (
                discount_factor,
                iterations,
                interpolated_count,
            ) = _solve_sparse_swap(instrument, anchors, conventions)
            total_root_iterations += iterations
            interpolated_coupon_count += interpolated_count
        if not math.isfinite(discount_factor) or discount_factor <= 0:
            raise YieldCurveError(
                f"{instrument['id']}: bootstrapped discount factor must be finite and > 0."
            )
        anchors.append(
            {
                "time": maturity,
                "discountFactor": discount_factor,
                "instrumentId": instrument["id"],
            }
        )
    repricing = [
        _reprice(instrument, anchors, conventions) for instrument in instruments
    ]
    max_abs_pv_residual = max(abs(item["pvResidual"]) for item in repricing)
    max_abs_quote_residual = max(abs(item["quoteResidual"]) for item in repricing)
    if (
        max_abs_pv_residual > _REPRICING_TOLERANCE
        or max_abs_quote_residual > _REPRICING_TOLERANCE
    ):
        raise YieldCurveError(
            "Curve repricing failed: "
            f"max PV residual={max_abs_pv_residual}, "
            f"max quote residual={max_abs_quote_residual}."
        )
    curve = _curve_nodes(instruments, anchors, conventions)
    negative_intervals = [
        node["intervalLabel"]
        for node in curve
        if node["forwardContinuous"] < -1e-12
    ]
    rising_intervals = [
        node["intervalLabel"]
        for index, node in enumerate(curve)
        if node["discountFactor"]
        > (1.0 if index == 0 else curve[index - 1]["discountFactor"]) + 1e-12
    ]
    large_intervals = [
        node["intervalLabel"]
        for node in curve
        if abs(node["forwardContinuous"]) > 0.5
    ]
    zero_convexity = [
        instrument["id"]
        for instrument in instruments
        if instrument["type"] == "future"
        and instrument["convexityAdjustment"] == 0
    ]
    warnings: list[str] = []
    if interpolated_coupon_count:
        warnings.append(
            f"{interpolated_coupon_count} swap coupon nodes were constructed by declared log-DF interpolation."
        )
    if negative_intervals:
        warnings.append(
            "Negative forward rates observed on "
            + ", ".join(negative_intervals)
            + "; allowed, but review the curve shape."
        )
    if rising_intervals:
        warnings.append(
            "Discount factors rise on "
            + ", ".join(rising_intervals)
            + "; consistent with negative forwards, not an automatic arbitrage failure."
        )
    if large_intervals:
        warnings.append(
            "Absolute continuous forwards exceed 50% on "
            + ", ".join(large_intervals)
            + "; check quote units and input quality."
        )
    if zero_convexity:
        warnings.append(
            "Explicit 0 bp futures convexity assumption used for "
            + ", ".join(zero_convexity)
            + "."
        )
    return {
        "schema": YIELD_CURVE_RESULT_SCHEMA,
        "engineVersion": YIELD_CURVE_VERSION,
        "conventions": conventions,
        "limitations": list(LIMITATIONS),
        "inputs": instruments,
        "anchors": anchors[1:],
        "curve": curve,
        "repricing": repricing,
        "diagnostics": {
            "converged": True,
            "positiveDiscountFactors": all(
                math.isfinite(anchor["discountFactor"])
                and anchor["discountFactor"] > 0
                for anchor in anchors
            ),
            "instrumentCount": len(instruments),
            "marketPillarCount": len(anchors) - 1,
            "curveNodeCount": len(curve),
            "interpolatedCouponCount": interpolated_coupon_count,
            "totalRootIterations": total_root_iterations,
            "maxAbsPvResidual": max_abs_pv_residual,
            "maxAbsQuoteResidual": max_abs_quote_residual,
            "negativeForwardIntervals": negative_intervals,
            "risingDiscountFactorIntervals": rising_intervals,
            "largeForwardIntervals": large_intervals,
            "warnings": warnings,
        },
    }
