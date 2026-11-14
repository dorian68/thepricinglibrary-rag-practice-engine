"""Deterministic realized-volatility and OHLC data-quality engine.

The module is intentionally provider-free.  It accepts one daily OHLC series,
uses the first row only as the previous-close seed, and computes all estimators
on the same subsequent sessions.  Inputs are never sorted, dropped, adjusted,
winsorized or imputed silently.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import re
import statistics
import sys
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Mapping, Sequence


REALIZED_VOLATILITY_VERSION = "1.0.0"
REALIZED_VOLATILITY_RESULT_SCHEMA = "tpl.realized-volatility-analysis.v1"
REALIZED_VOLATILITY_ROLLING_CSV_SCHEMA = "tpl.realized-volatility.rolling.v1"
REALIZED_VOLATILITY_OBSERVATIONS_CSV_SCHEMA = "tpl.realized-volatility.observations.v1"
MAX_CSV_BYTES = 10 * 1024 * 1024
MAX_ROWS = 50_001
MIN_WINDOW = 5
MAX_WINDOW = 252
NEGATIVE_ROUNDOFF_TOLERANCE = 1e-15

_REQUIRED_COLUMNS = ("date", "open", "high", "low", "close")
_OPTIONAL_COLUMNS = ("volume",)
_NUMBER_PATTERN = re.compile(
    r"^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?$"
)
_CONTROL_PATTERN = re.compile(r"[\x00-\x1f\x7f]")
_CALENDAR_MODES = {"weekday_sessions", "calendar_daily"}
_PRICE_BASES = {
    "unadjusted_ohlc",
    "split_adjusted_ohlc",
    "provider_adjusted_ohlc",
    "unknown",
}
_JUMP_THRESHOLD = math.log(1.25)
_ROBUST_Z_THRESHOLD = 8.0
_DIVERGENCE_RATIO = 1.5

ESTIMATORS = (
    "closeToClose",
    "parkinson",
    "garmanKlass",
    "rogersSatchell",
    "yangZhang",
)

ESTIMATOR_LABELS = {
    "closeToClose": "Close-to-close",
    "parkinson": "Parkinson",
    "garmanKlass": "Garman-Klass",
    "rogersSatchell": "Rogers-Satchell",
    "yangZhang": "Yang-Zhang",
}

DEFAULT_CONFIG: dict[str, Any] = {
    "window": 20,
    "annualization": 252,
    "calendarMode": "weekday_sessions",
    "priceBasis": "unknown",
    "sourceLabel": "user-provided CSV",
    "symbolLabel": "unlabelled single series",
    "filename": None,
}

CONVENTIONS: dict[str, Any] = {
    "frequency": "daily sessions; no resampling",
    "returnUnit": "natural-log returns in decimal form",
    "alignment": (
        "row 0 is the previous-close seed; all estimators use rows 1..N-1"
    ),
    "closeToClose": "sample variance of demeaned close-to-close log returns",
    "parkinson": "mean(log(high/low)^2 / (4*log(2)))",
    "garmanKlass": (
        "mean(0.5*log(high/low)^2 - (2*log(2)-1)*log(close/open)^2)"
    ),
    "rogersSatchell": (
        "mean(log(high/close)*log(high/open) + "
        "log(low/close)*log(low/open))"
    ),
    "yangZhang": (
        "sample variance(overnight) + k*sample variance(open-to-close) + "
        "(1-k)*Rogers-Satchell; k=0.34/(1.34+(n+1)/(n-1))"
    ),
    "annualization": "annualized volatility = sqrt(explicit sessionsPerYear * daily variance)",
    "missingData": "no sorting, dropping, interpolation, resampling or imputation",
}

LIMITATIONS = [
    "Descriptive historical estimators only: no volatility forecast, implied-volatility comparison or trading signal.",
    "No market-data provider is contacted; provenance is supplied by the user and the dataset hash.",
    "Corporate actions are not identified or adjusted automatically; large moves are retained and flagged.",
    "The weekday calendar has no holiday database, so missing weekdays are possible missing-session-or-holiday warnings.",
    "Daily OHLC only; intraday bars, timezone conversion, microstructure corrections and multi-asset panels are out of scope.",
    "Range estimators have model assumptions and may diverge materially on jumps, stale prices and illiquid instruments.",
]


def realized_volatility_contract_snapshot() -> dict[str, Any]:
    """Return the runtime rules that must match the repository contract JSON."""

    return {
        "csv": {
            "requiredHeader": list(_REQUIRED_COLUMNS),
            "optionalTrailingHeader": "volume",
            "delimiters": [",", ";"],
            "maxUtf8Bytes": MAX_CSV_BYTES,
            "maxRows": MAX_ROWS,
            "blankRows": "reject",
            "headerOrder": "exact",
            "dateOrder": "strictly_increasing",
            "dateMinimum": "1900-01-01",
            "dateMaximum": "2200-12-31",
            "numberFormat": "finite_dot_decimal_no_thousands_separator",
        },
        "config": {
            "windowMinimum": MIN_WINDOW,
            "windowMaximum": MAX_WINDOW,
            "annualizationMinimum": 1,
            "annualizationMaximum": 366,
            "calendarModes": ["weekday_sessions", "calendar_daily"],
            "priceBases": [
                "unadjusted_ohlc",
                "split_adjusted_ohlc",
                "provider_adjusted_ohlc",
                "unknown",
            ],
        },
        "diagnostics": {
            "largeMoveAbsoluteLogThreshold": _JUMP_THRESHOLD,
            "robustReturnZThreshold": _ROBUST_Z_THRESHOLD,
            "flatAndRepeatedFractionThreshold": 0.05,
            "estimatorDivergenceRatioThreshold": _DIVERGENCE_RATIO,
            "overnightDominanceThreshold": 0.5,
        },
        "provenance": {
            "datasetHash": "sha256_utf8_canonical_csv",
            "canonicalCsvHeaderOrder": [
                "date",
                "open",
                "high",
                "low",
                "close",
                "volume",
            ],
            "canonicalCsvLineEnding": "LF",
            "canonicalCsvFinalNewline": True,
            "canonicalNumericSignificantDigits": 17,
            "canonicalNumericFormat": "normalized_scientific",
            "rawUploadHashForbidden": True,
        },
        "exportNumericSignificantDigits": 12,
        "exportNumericFormat": "normalized_scientific",
    }


class RealizedVolatilityError(ValueError):
    """Explicit schema, validation or estimator failure."""


def _finite_number(raw: Any, label: str) -> float:
    if isinstance(raw, bool):
        raise RealizedVolatilityError(f"{label} must be a finite number.")
    try:
        value = float(raw)
    except (TypeError, ValueError) as exc:
        raise RealizedVolatilityError(f"{label} must be a finite number.") from exc
    if not math.isfinite(value):
        raise RealizedVolatilityError(f"{label} must be finite; NaN and Infinity are forbidden.")
    return value


def _csv_number(raw: str | None, label: str) -> float:
    value = "" if raw is None else raw.strip()
    if not value or not _NUMBER_PATTERN.fullmatch(value):
        raise RealizedVolatilityError(
            f"{label} must use a finite dot-decimal number without thousands separators."
        )
    return _finite_number(value, label)


def _integer(raw: Any, label: str, minimum: int, maximum: int) -> int:
    if isinstance(raw, bool):
        raise RealizedVolatilityError(f"{label} must be an integer in [{minimum}, {maximum}].")
    try:
        numeric = float(raw)
    except (TypeError, ValueError) as exc:
        raise RealizedVolatilityError(
            f"{label} must be an integer in [{minimum}, {maximum}]."
        ) from exc
    if not math.isfinite(numeric) or not numeric.is_integer():
        raise RealizedVolatilityError(f"{label} must be an integer in [{minimum}, {maximum}].")
    value = int(numeric)
    if value < minimum or value > maximum:
        raise RealizedVolatilityError(f"{label} must be an integer in [{minimum}, {maximum}].")
    return value


def _label(raw: Any, name: str, default: str, maximum: int) -> str:
    value = default if raw is None else str(raw).strip()
    if not value:
        value = default
    if len(value) > maximum or _CONTROL_PATTERN.search(value):
        raise RealizedVolatilityError(
            f"{name} must be non-empty, control-character-free and at most {maximum} characters."
        )
    return value


def normalize_config(raw: Mapping[str, Any] | None = None) -> dict[str, Any]:
    raw = raw or {}
    if not isinstance(raw, Mapping):
        raise RealizedVolatilityError("Analysis config must be an object.")
    window = _integer(raw.get("window", DEFAULT_CONFIG["window"]), "window", MIN_WINDOW, MAX_WINDOW)
    annualization = _integer(
        raw.get("annualization", DEFAULT_CONFIG["annualization"]),
        "annualization",
        1,
        366,
    )
    calendar_mode = str(raw.get("calendarMode", DEFAULT_CONFIG["calendarMode"])).strip()
    if calendar_mode not in _CALENDAR_MODES:
        raise RealizedVolatilityError(
            "calendarMode must be 'weekday_sessions' or 'calendar_daily'."
        )
    price_basis = str(raw.get("priceBasis", DEFAULT_CONFIG["priceBasis"])).strip()
    if price_basis not in _PRICE_BASES:
        raise RealizedVolatilityError(
            "priceBasis must be unadjusted_ohlc, split_adjusted_ohlc, "
            "provider_adjusted_ohlc or unknown."
        )
    filename_raw = raw.get("filename", DEFAULT_CONFIG["filename"])
    filename = None if filename_raw in (None, "") else _label(filename_raw, "filename", "input.csv", 255)
    return {
        "window": window,
        "rollingWindow": window,
        "annualization": annualization,
        "calendarMode": calendar_mode,
        "expectedFrequency": "calendar-daily" if calendar_mode == "calendar_daily" else "business-daily",
        "priceBasis": price_basis,
        "sourceLabel": _label(
            raw.get("sourceLabel"), "sourceLabel", DEFAULT_CONFIG["sourceLabel"], 200
        ),
        "symbolLabel": _label(
            raw.get("symbolLabel"), "symbolLabel", DEFAULT_CONFIG["symbolLabel"], 120
        ),
        "filename": filename,
    }


def _parse_iso_date(raw: Any, label: str) -> tuple[str, date]:
    value = str(raw).strip()
    try:
        parsed = date.fromisoformat(value)
    except ValueError as exc:
        raise RealizedVolatilityError(f"{label} must be an ISO date YYYY-MM-DD.") from exc
    if parsed.isoformat() != value:
        raise RealizedVolatilityError(f"{label} must be an ISO date YYYY-MM-DD.")
    if parsed < date(1900, 1, 1) or parsed > date(2200, 12, 31):
        raise RealizedVolatilityError(f"{label} must be between 1900-01-01 and 2200-12-31.")
    return value, parsed


def parse_realized_volatility_csv(text: str) -> list[dict[str, Any]]:
    """Parse the strict v1 OHLC CSV contract without silently fixing data."""

    if not isinstance(text, str):
        raise RealizedVolatilityError("CSV input must be UTF-8 text.")
    if len(text.encode("utf-8")) > MAX_CSV_BYTES:
        raise RealizedVolatilityError(f"CSV input exceeds the {MAX_CSV_BYTES}-byte limit.")
    normalized = text.removeprefix("\ufeff")
    if not normalized.strip():
        raise RealizedVolatilityError("CSV input is empty.")
    first_line = normalized.splitlines()[0]
    if "," in first_line and ";" in first_line:
        raise RealizedVolatilityError("CSV header mixes comma and semicolon delimiters.")
    delimiter = "," if "," in first_line else ";" if ";" in first_line else None
    if delimiter is None:
        raise RealizedVolatilityError("CSV header must use comma or semicolon delimiters.")
    try:
        reader = csv.reader(io.StringIO(normalized), delimiter=delimiter, strict=True)
        records = list(reader)
    except csv.Error as exc:
        raise RealizedVolatilityError(f"Malformed CSV: {exc}.") from exc
    if not records:
        raise RealizedVolatilityError("CSV input is empty.")
    header = tuple(cell.strip() for cell in records[0])
    accepted_headers = (_REQUIRED_COLUMNS, (*_REQUIRED_COLUMNS, *_OPTIONAL_COLUMNS))
    if header not in accepted_headers:
        raise RealizedVolatilityError(
            "CSV header must be exactly date,open,high,low,close with optional trailing volume; "
            "adjusted-close or unknown columns are forbidden."
        )
    rows: list[dict[str, Any]] = []
    for line_number, cells in enumerate(records[1:], start=2):
        if not cells or all(not cell.strip() for cell in cells):
            raise RealizedVolatilityError(f"CSV row {line_number} is blank.")
        if len(cells) != len(header):
            raise RealizedVolatilityError(
                f"CSV row {line_number} has {len(cells)} fields; expected {len(header)}."
            )
        record = dict(zip(header, cells, strict=True))
        row: dict[str, Any] = {"date": record["date"].strip()}
        for column in ("open", "high", "low", "close"):
            row[column] = _csv_number(record[column], f"CSV row {line_number} {column}")
        if "volume" in record:
            row["volume"] = _csv_number(record["volume"], f"CSV row {line_number} volume")
        rows.append(row)
        if len(rows) > MAX_ROWS:
            raise RealizedVolatilityError(f"CSV input exceeds the {MAX_ROWS}-row limit.")
    return rows


def _normalize_rows(raw_rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    if not isinstance(raw_rows, Sequence) or isinstance(raw_rows, (str, bytes)):
        raise RealizedVolatilityError("OHLC rows must be an array.")
    if len(raw_rows) > MAX_ROWS:
        raise RealizedVolatilityError(f"OHLC input exceeds the {MAX_ROWS}-row limit.")
    if len(raw_rows) < MIN_WINDOW + 1:
        raise RealizedVolatilityError(
            f"OHLC input requires at least {MIN_WINDOW + 1} rows: one seed plus {MIN_WINDOW} sessions."
        )
    rows: list[dict[str, Any]] = []
    previous_date: date | None = None
    volume_presence: bool | None = None
    for index, raw in enumerate(raw_rows):
        if not isinstance(raw, Mapping):
            raise RealizedVolatilityError(f"OHLC row {index + 1} must be an object.")
        unknown = set(raw) - {*_REQUIRED_COLUMNS, *_OPTIONAL_COLUMNS}
        missing = set(_REQUIRED_COLUMNS) - set(raw)
        if missing or unknown:
            raise RealizedVolatilityError(
                f"OHLC row {index + 1} has invalid schema; missing={sorted(missing)}, unknown={sorted(unknown)}."
            )
        date_text, parsed_date = _parse_iso_date(raw["date"], f"OHLC row {index + 1} date")
        if previous_date is not None and parsed_date <= previous_date:
            kind = "duplicate" if parsed_date == previous_date else "out-of-order"
            raise RealizedVolatilityError(
                f"OHLC row {index + 1} date is {kind}; dates must be strictly increasing."
            )
        previous_date = parsed_date
        row = {"date": date_text, "_date": parsed_date}
        for field in ("open", "high", "low", "close"):
            value = _finite_number(raw[field], f"OHLC row {index + 1} {field}")
            if value <= 0:
                raise RealizedVolatilityError(
                    f"OHLC row {index + 1} {field} must be strictly positive."
                )
            row[field] = value
        if row["high"] < max(row["open"], row["low"], row["close"]):
            raise RealizedVolatilityError(
                f"OHLC row {index + 1} high must be >= open, low and close."
            )
        if row["low"] > min(row["open"], row["high"], row["close"]):
            raise RealizedVolatilityError(
                f"OHLC row {index + 1} low must be <= open, high and close."
            )
        has_volume = "volume" in raw
        if volume_presence is None:
            volume_presence = has_volume
        elif has_volume != volume_presence:
            raise RealizedVolatilityError("volume must be present on every row or on no rows.")
        if has_volume:
            volume = _finite_number(raw["volume"], f"OHLC row {index + 1} volume")
            if volume < 0:
                raise RealizedVolatilityError(f"OHLC row {index + 1} volume must be >= 0.")
            row["volume"] = volume
        rows.append(row)
    return rows


def _sample_variance(values: Sequence[float]) -> float:
    if len(values) < 2:
        raise RealizedVolatilityError("Sample variance requires at least two observations.")
    mean = math.fsum(values) / len(values)
    return math.fsum((value - mean) ** 2 for value in values) / (len(values) - 1)


def _nonnegative(value: float, estimator: str) -> tuple[float, bool]:
    if not math.isfinite(value):
        raise RealizedVolatilityError(f"{estimator} variance is not finite.")
    if value < -NEGATIVE_ROUNDOFF_TOLERANCE:
        raise RealizedVolatilityError(
            f"{estimator} variance is materially negative ({value}); the estimator is unavailable."
        )
    if value < 0:
        return 0.0, True
    return value, False


def _estimator_core(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    n = len(rows) - 1
    if n < MIN_WINDOW:
        raise RealizedVolatilityError(f"At least {MIN_WINDOW} aligned sessions are required.")
    close_returns: list[float] = []
    overnight_returns: list[float] = []
    intraday_returns: list[float] = []
    log_ranges: list[float] = []
    parkinson_terms: list[float] = []
    garman_klass_terms: list[float] = []
    rogers_satchell_terms: list[float] = []
    for index in range(1, len(rows)):
        previous_close = float(rows[index - 1]["close"])
        current = rows[index]
        open_price = float(current["open"])
        high = float(current["high"])
        low = float(current["low"])
        close = float(current["close"])
        close_return = math.log(close / previous_close)
        overnight = math.log(open_price / previous_close)
        intraday = math.log(close / open_price)
        log_range = math.log(high / low)
        close_returns.append(close_return)
        overnight_returns.append(overnight)
        intraday_returns.append(intraday)
        log_ranges.append(log_range)
        parkinson_terms.append(log_range**2 / (4 * math.log(2)))
        garman_klass_terms.append(
            0.5 * log_range**2 - (2 * math.log(2) - 1) * intraday**2
        )
        rogers_satchell_terms.append(
            math.log(high / close) * math.log(high / open_price)
            + math.log(low / close) * math.log(low / open_price)
        )
    close_mean = math.fsum(close_returns) / n
    overnight_mean = math.fsum(overnight_returns) / n
    intraday_mean = math.fsum(intraday_returns) / n
    k = 0.34 / (1.34 + (n + 1) / (n - 1))
    raw_variances = {
        "closeToClose": _sample_variance(close_returns),
        "parkinson": math.fsum(parkinson_terms) / n,
        "garmanKlass": math.fsum(garman_klass_terms) / n,
        "rogersSatchell": math.fsum(rogers_satchell_terms) / n,
    }
    raw_variances["yangZhang"] = (
        _sample_variance(overnight_returns)
        + k * _sample_variance(intraday_returns)
        + (1 - k) * raw_variances["rogersSatchell"]
    )
    variances: dict[str, float] = {}
    floored: list[str] = []
    for estimator, value in raw_variances.items():
        variances[estimator], was_floored = _nonnegative(value, estimator)
        if was_floored:
            floored.append(estimator)
    contributions: list[dict[str, float]] = []
    for index in range(n):
        contributions.append(
            {
                "closeToClose": (close_returns[index] - close_mean) ** 2 / (n - 1),
                "parkinson": parkinson_terms[index] / n,
                "garmanKlass": garman_klass_terms[index] / n,
                "rogersSatchell": rogers_satchell_terms[index] / n,
                "yangZhang": (
                    (overnight_returns[index] - overnight_mean) ** 2 / (n - 1)
                    + k * (intraday_returns[index] - intraday_mean) ** 2 / (n - 1)
                    + (1 - k) * rogers_satchell_terms[index] / n
                ),
            }
        )
    return {
        "n": n,
        "k": k,
        "variances": variances,
        "floored": floored,
        "closeReturns": close_returns,
        "overnightReturns": overnight_returns,
        "intradayReturns": intraday_returns,
        "logRanges": log_ranges,
        "contributions": contributions,
        "overnightVariance": _sample_variance(overnight_returns),
    }


def _canonical_number(value: float) -> str:
    if value == 0:
        return "0"
    mantissa, exponent = format(value, ".16e").lower().split("e", 1)
    mantissa = mantissa.rstrip("0").rstrip(".")
    return f"{mantissa}e{int(exponent)}"


def _export_number(value: float) -> str:
    if value == 0:
        return "0"
    mantissa, exponent = format(value, ".11e").lower().split("e", 1)
    mantissa = mantissa.rstrip("0").rstrip(".")
    return f"{mantissa}e{int(exponent)}"


def _canonical_dataset(rows: Sequence[Mapping[str, Any]]) -> str:
    has_volume = "volume" in rows[0]
    header = "date,open,high,low,close" + (",volume" if has_volume else "")
    lines = [header]
    for row in rows:
        fields = [
            str(row["date"]),
            _canonical_number(float(row["open"])),
            _canonical_number(float(row["high"])),
            _canonical_number(float(row["low"])),
            _canonical_number(float(row["close"])),
        ]
        if has_volume:
            fields.append(_canonical_number(float(row["volume"])))
        lines.append(",".join(fields))
    return "\n".join(lines) + "\n"


def _hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _quality_events(
    rows: Sequence[Mapping[str, Any]], core: Mapping[str, Any], config: Mapping[str, Any]
) -> tuple[list[dict[str, Any]], dict[str, list[str]], dict[str, Any]]:
    events: list[dict[str, Any]] = []
    flags_by_date: dict[str, list[str]] = {str(row["date"]): [] for row in rows[1:]}

    def add(code: str, row_index: int, message: str, value: float | int | None = None) -> None:
        event = {
            "code": code,
            "date": str(rows[row_index]["date"]),
            "row": row_index + 1,
            "message": message,
        }
        if value is not None:
            event["value"] = value
        events.append(event)
        flags_by_date[str(rows[row_index]["date"])].append(code)

    possible_missing = 0
    for index in range(1, len(rows)):
        previous = rows[index - 1]["_date"]
        current = rows[index]["_date"]
        gap = (current - previous).days
        if config["calendarMode"] == "calendar_daily":
            missing = max(0, gap - 1)
        else:
            missing = sum(
                1
                for offset in range(1, gap)
                if (previous + timedelta(days=offset)).weekday() < 5
            )
        if missing:
            possible_missing += missing
            add(
                "POSSIBLE_MISSING_SESSION",
                index,
                f"{missing} expected dates are absent before this row; holidays are not modeled.",
                missing,
            )

    close_returns = list(core["closeReturns"])
    log_ranges = list(core["logRanges"])
    median_return = statistics.median(close_returns)
    mad = statistics.median(abs(value - median_return) for value in close_returns)
    for position, value in enumerate(close_returns, start=1):
        if abs(value) >= _JUMP_THRESHOLD:
            add(
                "LARGE_CLOSE_JUMP",
                position,
                "Absolute close-to-close log return is at least log(1.25); possible gap or corporate action retained.",
                value,
            )
        if mad > 1e-15:
            robust_z = 0.6744897501960817 * (value - median_return) / mad
            if abs(robust_z) > _ROBUST_Z_THRESHOLD:
                add(
                    "ROBUST_RETURN_OUTLIER",
                    position,
                    "Absolute median/MAD robust z-score exceeds 8; observation retained.",
                    robust_z,
                )
        elif abs(value - median_return) > 1e-12:
            add(
                "ROBUST_RETURN_OUTLIER_MAD_ZERO",
                position,
                "Return differs from the median while MAD is zero; observation retained.",
                value,
            )
        if log_ranges[position - 1] >= _JUMP_THRESHOLD:
            add(
                "LARGE_INTRADAY_RANGE",
                position,
                "Log high/low range is at least log(1.25); observation retained.",
                log_ranges[position - 1],
            )

    flat_count = 0
    repeated_close_count = 0
    longest_flat_run = 0
    current_flat_run = 0
    for index in range(1, len(rows)):
        row = rows[index]
        is_flat = row["open"] == row["high"] == row["low"] == row["close"]
        if is_flat:
            flat_count += 1
            current_flat_run += 1
            longest_flat_run = max(longest_flat_run, current_flat_run)
            add("FLAT_BAR", index, "Open, high, low and close are identical.")
        else:
            current_flat_run = 0
        if row["close"] == rows[index - 1]["close"]:
            repeated_close_count += 1
            add("REPEATED_CLOSE", index, "Close is unchanged from the previous row.")

    return events, flags_by_date, {
        "possibleMissingSessionCount": possible_missing,
        "flatBarCount": flat_count,
        "flatBarFraction": flat_count / core["n"],
        "repeatedCloseCount": repeated_close_count,
        "repeatedCloseFraction": repeated_close_count / core["n"],
        "longestFlatRun": longest_flat_run,
        "medianCloseReturn": median_return,
        "returnMad": mad,
    }


def analyze_realized_volatility(
    raw_rows: Sequence[Mapping[str, Any]], config_input: Mapping[str, Any] | None = None
) -> dict[str, Any]:
    """Validate one OHLC series and return deterministic estimators and evidence."""

    config = normalize_config(config_input)
    rows = _normalize_rows(raw_rows)
    if len(rows) < config["window"] + 1:
        raise RealizedVolatilityError(
            f"window={config['window']} requires at least {config['window'] + 1} rows including the seed."
        )
    core = _estimator_core(rows)
    annualization = config["annualization"]
    summary = {
        estimator: {
            "n": core["n"],
            "dailyVariance": core["variances"][estimator],
            "dailyVol": math.sqrt(core["variances"][estimator]),
            "annualizedVol": math.sqrt(annualization * core["variances"][estimator]),
        }
        for estimator in ESTIMATORS
    }
    rolling: list[dict[str, Any]] = []
    window = config["window"]
    for end in range(window, len(rows)):
        window_core = _estimator_core(rows[end - window : end + 1])
        window_estimators = {
            estimator: {
                "key": estimator,
                "label": ESTIMATOR_LABELS[estimator],
                "sessionCount": window,
                "variance": window_core["variances"][estimator],
                "annualizedVolatility": math.sqrt(
                    annualization * window_core["variances"][estimator]
                ),
            }
            for estimator in ESTIMATORS
        }
        rolling.append(
            {
                "startDate": rows[end - window]["date"],
                "endDate": rows[end]["date"],
                "sessionCount": window,
                "yangZhangK": window_core["k"],
                "estimators": window_estimators,
            }
        )
    events, flags_by_date, counts = _quality_events(rows, core, config)
    observations: list[dict[str, Any]] = [
        {
            "date": rows[0]["date"],
            "open": rows[0]["open"],
            "high": rows[0]["high"],
            "low": rows[0]["low"],
            "close": rows[0]["close"],
            "closeToCloseReturn": None,
            "overnightReturn": None,
            "openToCloseReturn": None,
            "intradayReturn": None,
            "logRange": None,
            "varianceContributions": None,
            "flags": [],
            **({"volume": rows[0]["volume"]} if "volume" in rows[0] else {}),
        }
    ]
    for position in range(core["n"]):
        row = rows[position + 1]
        observation: dict[str, Any] = {
            "date": row["date"],
            "open": row["open"],
            "high": row["high"],
            "low": row["low"],
            "close": row["close"],
            "closeToCloseReturn": core["closeReturns"][position],
            "overnightReturn": core["overnightReturns"][position],
            "openToCloseReturn": core["intradayReturns"][position],
            "intradayReturn": core["intradayReturns"][position],
            "logRange": core["logRanges"][position],
            "varianceContributions": core["contributions"][position],
            "flags": flags_by_date[str(row["date"])],
        }
        if "volume" in row:
            observation["volume"] = row["volume"]
        observations.append(observation)

    warnings: list[dict[str, Any]] = []
    if core["n"] < 20:
        warnings.append(
            {"code": "SMALL_SAMPLE", "message": "Fewer than 20 aligned sessions; estimates are statistically fragile."}
        )
    if config["priceBasis"] == "unknown":
        warnings.append(
            {"code": "UNKNOWN_PRICE_BASIS", "message": "OHLC adjustment status is unknown; corporate-action contamination cannot be excluded."}
        )
    if counts["possibleMissingSessionCount"]:
        warnings.append(
            {"code": "POSSIBLE_MISSING_SESSIONS", "message": f"{counts['possibleMissingSessionCount']} expected dates are absent; no holiday calendar is available."}
        )
    if counts["flatBarFraction"] > 0.05:
        warnings.append(
            {"code": "MANY_FLAT_BARS", "message": f"Flat bars represent {counts['flatBarFraction']:.2%} of aligned sessions."}
        )
    if counts["repeatedCloseFraction"] > 0.05:
        warnings.append(
            {"code": "MANY_REPEATED_CLOSES", "message": f"Repeated closes represent {counts['repeatedCloseFraction']:.2%} of aligned sessions."}
        )
    event_codes = {event["code"] for event in events}
    if {"LARGE_CLOSE_JUMP", "LARGE_INTRADAY_RANGE"} & event_codes:
        warnings.append(
            {"code": "LARGE_MOVE_REVIEW", "message": "Large close jumps or intraday ranges were retained; review corporate actions, units and source quality."}
        )
    if {"ROBUST_RETURN_OUTLIER", "ROBUST_RETURN_OUTLIER_MAD_ZERO"} & event_codes:
        warnings.append(
            {"code": "RETURN_OUTLIERS", "message": "Robust return outliers were retained and identified by date."}
        )
    positive_vols = [summary[name]["annualizedVol"] for name in ESTIMATORS if summary[name]["annualizedVol"] > 0]
    estimator_ratio = max(positive_vols) / min(positive_vols) if len(positive_vols) >= 2 else None
    if estimator_ratio is not None and estimator_ratio > _DIVERGENCE_RATIO:
        warnings.append(
            {"code": "ESTIMATOR_DIVERGENCE", "message": f"Maximum/minimum positive annualized volatility ratio is {estimator_ratio:.6g} (> 1.5)."}
        )
    yang_variance = core["variances"]["yangZhang"]
    overnight_share = core["overnightVariance"] / yang_variance if yang_variance > 0 else None
    if overnight_share is not None and overnight_share > 0.5:
        warnings.append(
            {"code": "OVERNIGHT_DOMINANT", "message": f"Overnight sample variance is {overnight_share:.2%} of Yang-Zhang variance."}
        )
    for estimator in core["floored"]:
        warnings.append(
            {"code": "NUMERICAL_ROUNDOFF_FLOOR", "message": f"{estimator} variance was within 1e-15 below zero and explicitly floored to zero."}
        )

    canonical_dataset = _canonical_dataset(rows)
    dataset_hash = _hash(canonical_dataset)
    analysis_identity_config = {
        "annualization": annualization,
        "calendarMode": config["calendarMode"],
        "filename": config["filename"],
        "priceBasis": config["priceBasis"],
        "sourceLabel": config["sourceLabel"],
        "symbolLabel": config["symbolLabel"],
        "window": window,
    }
    analysis_config = json.dumps(
        analysis_identity_config, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )
    analysis_id = _hash(dataset_hash + "\n" + analysis_config)
    serializable_inputs = [
        {key: value for key, value in row.items() if key != "_date"} for row in rows
    ]
    estimators = {
        estimator: {
            "key": estimator,
            "label": ESTIMATOR_LABELS[estimator],
            "sessionCount": core["n"],
            "variance": summary[estimator]["dailyVariance"],
            "annualizedVolatility": summary[estimator]["annualizedVol"],
        }
        for estimator in ESTIMATORS
    }
    adjustment_basis = (
        "adjusted"
        if config["priceBasis"] in {"split_adjusted_ohlc", "provider_adjusted_ohlc"}
        else "unadjusted" if config["priceBasis"] == "unadjusted_ohlc" else "unknown"
    )
    source = {
        "filename": config["filename"],
        "sha256": dataset_hash,
        "hashBasis": "canonical-observations-utf8",
        "adjustmentBasis": adjustment_basis,
    }
    warning_range = {"startDate": rows[0]["date"], "endDate": rows[-1]["date"]}
    public_warnings = [
        {**event, "severity": "warning", "includedInCalculation": True}
        for event in events
    ] + [
        {
            **warning,
            **warning_range,
            "severity": "warning",
            "includedInCalculation": True,
        }
        for warning in warnings
    ]
    return {
        "schema": REALIZED_VOLATILITY_RESULT_SCHEMA,
        "engineVersion": REALIZED_VOLATILITY_VERSION,
        "analysisId": analysis_id,
        "source": source,
        "provenance": {
            "sourceLabel": config["sourceLabel"],
            "symbolLabel": config["symbolLabel"],
            "filename": config["filename"],
            "priceBasis": config["priceBasis"],
            "datasetSha256": dataset_hash,
            "provider": None,
            "persistence": "none",
        },
        "config": config,
        "conventions": {
            "frequency": "daily sessions; no resampling",
            "returnUnit": "natural-log returns in decimal form",
            "alignment": "row 0 is the previous-close seed; all estimators use rows 1..N-1",
            "closeToClose": "sample variance of log(C_t/C_{t-1})",
            "parkinson": "mean(log(H/L)^2 / (4 ln 2))",
            "garmanKlass": "mean(0.5 log(H/L)^2 - (2 ln 2 - 1) log(C/O)^2)",
            "rogersSatchell": "mean(log(H/O)log(H/C) + log(L/O)log(L/C))",
            "yangZhang": "sample overnight variance + k sample open-close variance + (1-k) Rogers-Satchell",
            "yangZhangWeight": "k = 0.34 / (1.34 + (n+1)/(n-1))",
            "annualization": "annualized volatility = sqrt(explicit sessionsPerYear * daily variance)",
            "missingData": "no sorting, dropping, winsorization, resampling, interpolation or imputation",
            "sessionsPerYear": annualization,
            "rollingWindow": window,
        },
        "limitations": [
            "Historical realized volatility is not a forecast or trading signal.",
            "Calendar and business-day checks do not infer exchange-specific holidays.",
            "Unknown adjustment basis can leave splits and distributions in the estimates.",
            "Daily OHLC estimators do not model microstructure noise or intraday path ordering.",
        ],
        "inputs": serializable_inputs,
        "dateRange": {"start": rows[0]["date"], "end": rows[-1]["date"]},
        "observationCount": len(rows),
        "sessionCount": core["n"],
        "summary": summary,
        "estimators": estimators,
        "yangZhangK": core["k"],
        "rolling": rolling,
        "observations": observations,
        "warnings": public_warnings,
        "diagnostics": {
            "status": "WARN" if public_warnings else "PASS",
            "rowCount": len(rows),
            "seedRowCount": 1,
            "alignedSessionCount": core["n"],
            "rollingPointCount": len(rolling),
            "counts": counts,
            "estimatorMaxMinRatio": estimator_ratio,
            "overnightVarianceShareOfYangZhang": overnight_share,
            "events": events,
            "warnings": warnings,
            "errors": [],
        },
    }


def analyze_realized_volatility_csv(
    text: str, config_input: Mapping[str, Any] | None = None
) -> dict[str, Any]:
    return analyze_realized_volatility(parse_realized_volatility_csv(text), config_input)


def export_analysis_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, ensure_ascii=False, allow_nan=False, sort_keys=True, indent=2) + "\n"


def _write_csv(header: Sequence[str], rows: Sequence[Sequence[Any]]) -> str:
    stream = io.StringIO(newline="")
    writer = csv.writer(stream, lineterminator="\n")
    writer.writerow(header)
    writer.writerows(rows)
    return stream.getvalue()


def export_rolling_csv(result: Mapping[str, Any]) -> str:
    return _write_csv(
        (
            "schema",
            "engineVersion",
            "sourceSha256",
            "annualization",
            "windowSessions",
            "startDate",
            "endDate",
            *(
                field
                for estimator in ESTIMATORS
                for field in (
                    f"{estimator}Variance",
                    f"{estimator}AnnualizedVolatility",
                )
            ),
        ),
        [
            (
                REALIZED_VOLATILITY_ROLLING_CSV_SCHEMA,
                result["engineVersion"],
                result["source"]["sha256"],
                result["config"]["annualization"],
                row["sessionCount"],
                row["startDate"],
                row["endDate"],
                *(
                    _export_number(float(row["estimators"][estimator][metric]))
                    for estimator in ESTIMATORS
                    for metric in ("variance", "annualizedVolatility")
                ),
            )
            for row in result["rolling"]
        ],
    )


def export_observations_csv(result: Mapping[str, Any]) -> str:
    def number_or_blank(value: Any) -> str:
        return "" if value is None else _export_number(float(value))

    return _write_csv(
        (
            "schema",
            "engineVersion",
            "sourceSha256",
            "date",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "closeToCloseReturn",
            "overnightReturn",
            "openToCloseReturn",
            "logRange",
            "flags",
            *(f"{name}VarianceContribution" for name in ESTIMATORS),
        ),
        [
            (
                REALIZED_VOLATILITY_OBSERVATIONS_CSV_SCHEMA,
                result["engineVersion"],
                result["source"]["sha256"],
                row["date"],
                _export_number(float(row["open"])),
                _export_number(float(row["high"])),
                _export_number(float(row["low"])),
                _export_number(float(row["close"])),
                number_or_blank(row.get("volume")),
                number_or_blank(row["closeToCloseReturn"]),
                number_or_blank(row["overnightReturn"]),
                number_or_blank(row["openToCloseReturn"]),
                number_or_blank(row["logRange"]),
                "|".join(row["flags"]),
                *(
                    number_or_blank(
                        None
                        if row["varianceContributions"] is None
                        else row["varianceContributions"][name]
                    )
                    for name in ESTIMATORS
                ),
            )
            for row in result["observations"]
        ],
    )


def _main(argv: Sequence[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(newline="\n")
    parser = argparse.ArgumentParser(
        description="Analyze one user-provided daily OHLC CSV without contacting a data provider."
    )
    parser.add_argument("csv_path", type=Path)
    parser.add_argument("--window", type=int, default=20)
    parser.add_argument("--annualization", type=int, default=252)
    parser.add_argument("--calendar-mode", choices=sorted(_CALENDAR_MODES), default="weekday_sessions")
    parser.add_argument("--price-basis", choices=sorted(_PRICE_BASES), default="unknown")
    parser.add_argument("--source-label", default="user-provided CSV")
    parser.add_argument("--symbol-label", default="unlabelled single series")
    parser.add_argument("--format", choices=("json", "rolling-csv", "observations-csv"), default="json")
    args = parser.parse_args(argv)
    try:
        if args.csv_path.stat().st_size > MAX_CSV_BYTES:
            raise RealizedVolatilityError(f"CSV input exceeds the {MAX_CSV_BYTES}-byte limit.")
        text = args.csv_path.read_text(encoding="utf-8")
        result = analyze_realized_volatility_csv(
            text,
            {
                "window": args.window,
                "annualization": args.annualization,
                "calendarMode": args.calendar_mode,
                "priceBasis": args.price_basis,
                "sourceLabel": args.source_label,
                "symbolLabel": args.symbol_label,
                "filename": args.csv_path.name,
            },
        )
    except (OSError, UnicodeError, RealizedVolatilityError) as exc:
        print(f"[VERDICT] FAIL · {exc}", file=sys.stderr)
        return 2
    if args.format == "rolling-csv":
        output = export_rolling_csv(result)
    elif args.format == "observations-csv":
        output = export_observations_csv(result)
    else:
        output = export_analysis_json(result)
    sys.stdout.write(output)
    return 0


if __name__ == "__main__":  # pragma: no cover - exercised through subprocess tests
    raise SystemExit(_main())
