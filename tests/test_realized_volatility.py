from __future__ import annotations

import copy
import csv
import io
import json
import math
import subprocess
import sys
from pathlib import Path

import pytest

from pricinglibrary_rag.realized_volatility import (
    ESTIMATORS,
    MAX_CSV_BYTES,
    RealizedVolatilityError,
    analyze_realized_volatility,
    analyze_realized_volatility_csv,
    export_analysis_json,
    export_observations_csv,
    export_rolling_csv,
    normalize_config,
    parse_realized_volatility_csv,
    realized_volatility_contract_snapshot,
)


FIXTURE_PATH = (
    Path(__file__).resolve().parents[3] / "fixtures" / "realized_volatility_golden.json"
)
FIXTURE = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
CASES = {case["id"]: case for case in FIXTURE["cases"]}
CONTRACT_PATH = FIXTURE_PATH.with_name("realized_volatility_contract.json")
CONTRACT = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))


def test_runtime_rules_equal_canonical_contract() -> None:
    projection = {
        key: CONTRACT[key]
        for key in (
            "csv",
            "config",
            "diagnostics",
            "provenance",
            "exportNumericSignificantDigits",
            "exportNumericFormat",
        )
    }
    assert realized_volatility_contract_snapshot() == projection


def assert_close(actual: float, expected: float, tolerance: float) -> None:
    assert math.isfinite(actual)
    assert abs(actual - expected) <= tolerance


def rows_to_csv(rows: list[dict], delimiter: str = ",", bom: bool = False) -> str:
    stream = io.StringIO(newline="")
    writer = csv.writer(stream, delimiter=delimiter, lineterminator="\n")
    header = ["date", "open", "high", "low", "close"]
    if "volume" in rows[0]:
        header.append("volume")
    writer.writerow(header)
    for row in rows:
        writer.writerow([row[column] for column in header])
    return ("\ufeff" if bom else "") + stream.getvalue()


@pytest.mark.parametrize("case", FIXTURE["cases"], ids=lambda case: case["id"])
def test_python_engine_matches_shared_golden_fixture(case: dict) -> None:
    result = analyze_realized_volatility(case["rows"], FIXTURE["baseConfig"])
    expected = case["expected"]
    tolerances = FIXTURE["tolerances"]
    assert result["engineVersion"] == FIXTURE["engineVersion"]
    assert result["diagnostics"]["alignedSessionCount"] == expected["n"]
    assert_close(
        result["yangZhangK"], expected["yangZhangK"], tolerances["yangZhangK"]
    )
    for estimator in ESTIMATORS:
        assert_close(
            result["summary"][estimator]["dailyVariance"],
            expected["dailyVariance"][estimator],
            tolerances["variance"],
        )
        assert_close(
            result["summary"][estimator]["annualizedVol"],
            expected["annualizedVol"][estimator],
            tolerances["annualizedVol"],
        )
    assert [warning["code"] for warning in result["diagnostics"]["warnings"]] == expected[
        "warningCodes"
    ]
    assert result == analyze_realized_volatility(case["rows"], FIXTURE["baseConfig"])


def test_mixed_case_rolling_window_and_annualization_scaling() -> None:
    case = CASES["mixed_ohlc_7"]
    result = analyze_realized_volatility(case["rows"], FIXTURE["baseConfig"])
    expected = case["expected"]["rollingLast"]
    latest = result["rolling"][-1]
    assert latest["endDate"] == expected["date"]
    assert latest["sessionCount"] == expected["n"]
    assert_close(latest["yangZhangK"], expected["yangZhangK"], FIXTURE["tolerances"]["yangZhangK"])
    for estimator in ESTIMATORS:
        assert_close(
            latest["estimators"][estimator]["annualizedVolatility"],
            expected[estimator],
            FIXTURE["tolerances"]["annualizedVol"],
        )
    result_365 = analyze_realized_volatility(
        case["rows"], {**FIXTURE["baseConfig"], "annualization": 365}
    )
    scale = math.sqrt(365 / 252)
    for estimator in ESTIMATORS:
        assert_close(
            result_365["summary"][estimator]["annualizedVol"],
            case["expected"]["annualizedVol365"][estimator],
            FIXTURE["tolerances"]["annualizedVol"],
        )
        assert_close(
            result_365["summary"][estimator]["annualizedVol"],
            result["summary"][estimator]["annualizedVol"] * scale,
            FIXTURE["tolerances"]["annualizedVol"],
        )


def test_observation_contributions_sum_to_each_full_sample_variance() -> None:
    result = analyze_realized_volatility(
        CASES["mixed_ohlc_7"]["rows"], FIXTURE["baseConfig"]
    )
    for estimator in ESTIMATORS:
        contribution_sum = math.fsum(
            row["varianceContributions"][estimator]
            for row in result["observations"]
            if row["varianceContributions"] is not None
        )
        assert_close(
            contribution_sum,
            result["summary"][estimator]["dailyVariance"],
            FIXTURE["tolerances"]["contribution"],
        )


@pytest.mark.parametrize("delimiter", [",", ";"])
@pytest.mark.parametrize("bom", [False, True])
def test_csv_contract_accepts_canonical_delimiters_bom_and_real_volume(
    delimiter: str, bom: bool
) -> None:
    rows = [dict(row, volume=1_000 + index) for index, row in enumerate(CASES["mixed_ohlc_7"]["rows"])]
    text = rows_to_csv(rows, delimiter=delimiter, bom=bom)
    parsed = parse_realized_volatility_csv(text)
    assert parsed == rows
    result = analyze_realized_volatility_csv(text, FIXTURE["baseConfig"])
    assert result["provenance"]["provider"] is None
    assert result["provenance"]["persistence"] == "none"
    assert all("volume" in row for row in result["observations"])


@pytest.mark.parametrize(
    ("text", "message"),
    [
        ("date,open,high,low,adj_close\n", "exactly"),
        ("date,open;high,low,close\n", "mixes"),
        ("date|open|high|low|close\n", "comma or semicolon"),
        ("date,open,high,low,close\n2024-01-01,100,101,99,NaN\n", "dot-decimal"),
        ("date;open;high;low;close\n2024-01-01;100,5;101;99;100\n", "dot-decimal"),
        ("date,open,high,low,close\n\n", "blank"),
        ("date,open,high,low,close\n2024-01-01,100,101,99\n", "fields"),
    ],
)
def test_csv_parser_fails_closed_on_ambiguous_or_invalid_data(
    text: str, message: str
) -> None:
    with pytest.raises(RealizedVolatilityError, match=message):
        parse_realized_volatility_csv(text)


def test_csv_parser_enforces_byte_limit() -> None:
    with pytest.raises(RealizedVolatilityError, match="byte limit"):
        parse_realized_volatility_csv("x" * (MAX_CSV_BYTES + 1))


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (lambda rows: rows[1].update(close=float("nan")), "finite"),
        (lambda rows: rows[1].update(open=0), "strictly positive"),
        (lambda rows: rows[1].update(high=99), "high must be"),
        (lambda rows: rows[1].update(low=102.5), "low must be"),
        (lambda rows: rows[1].update(date=rows[0]["date"]), "duplicate"),
        (lambda rows: rows[1].update(date="2023-12-31"), "out-of-order"),
        (lambda rows: rows[1].update(date="01/03/2024"), "ISO date"),
        (lambda rows: rows[0].update(date="1899-01-01"), "between 1900-01-01"),
        (lambda rows: rows[1].update(adj_close=102), "invalid schema"),
        (lambda rows: rows[1].update(volume=10), "every row or on no rows"),
    ],
)
def test_row_validation_fails_closed(mutation, message: str) -> None:
    rows = copy.deepcopy(CASES["mixed_ohlc_7"]["rows"])
    mutation(rows)
    with pytest.raises(RealizedVolatilityError, match=message):
        analyze_realized_volatility(rows, FIXTURE["baseConfig"])


@pytest.mark.parametrize(
    ("config", "message"),
    [
        ({"window": 4}, "window"),
        ({"window": 253}, "window"),
        ({"window": 5.5}, "window"),
        ({"annualization": 0}, "annualization"),
        ({"annualization": float("inf")}, "annualization"),
        ({"calendarMode": "exchange_calendar"}, "calendarMode"),
        ({"priceBasis": "adjusted_close_only"}, "priceBasis"),
        ({"sourceLabel": "bad\nlabel"}, "sourceLabel"),
    ],
)
def test_config_validation_is_explicit(config: dict, message: str) -> None:
    with pytest.raises(RealizedVolatilityError, match=message):
        normalize_config(config)


def test_window_requires_seed_plus_exact_number_of_sessions() -> None:
    rows = CASES["mixed_ohlc_7"]["rows"][:6]
    with pytest.raises(RealizedVolatilityError, match="requires at least 7 rows"):
        analyze_realized_volatility(rows, {**FIXTURE["baseConfig"], "window": 6})


def test_quality_diagnostics_retain_gaps_jumps_and_outliers() -> None:
    rows = [
        {"date": "2024-01-01", "open": 100, "high": 101, "low": 99, "close": 100},
        {"date": "2024-01-02", "open": 100, "high": 101, "low": 99, "close": 100},
        {"date": "2024-01-04", "open": 50, "high": 51, "low": 49, "close": 50},
        {"date": "2024-01-05", "open": 50, "high": 51, "low": 49, "close": 50},
        {"date": "2024-01-06", "open": 50, "high": 51, "low": 49, "close": 50},
        {"date": "2024-01-07", "open": 50, "high": 51, "low": 49, "close": 50},
    ]
    result = analyze_realized_volatility(
        rows,
        {
            **FIXTURE["baseConfig"],
            "calendarMode": "calendar_daily",
            "priceBasis": "unknown",
        },
    )
    event_codes = {event["code"] for event in result["diagnostics"]["events"]}
    warning_codes = {warning["code"] for warning in result["diagnostics"]["warnings"]}
    assert "POSSIBLE_MISSING_SESSION" in event_codes
    assert "LARGE_CLOSE_JUMP" in event_codes
    assert "ROBUST_RETURN_OUTLIER_MAD_ZERO" in event_codes
    assert "POSSIBLE_MISSING_SESSIONS" in warning_codes
    assert "LARGE_MOVE_REVIEW" in warning_codes
    assert "RETURN_OUTLIERS" in warning_codes
    assert "UNKNOWN_PRICE_BASIS" in warning_codes
    assert result["inputs"][2]["close"] == 50
    assert result["diagnostics"]["status"] == "WARN"


def test_versioned_exports_are_deterministic_finite_and_formula_injection_free() -> None:
    result = analyze_realized_volatility(
        CASES["mixed_ohlc_7"]["rows"],
        {
            **FIXTURE["baseConfig"],
            "sourceLabel": "=HYPERLINK(attack)",
            "symbolLabel": "+CMD",
        },
    )
    json_export = export_analysis_json(result)
    rolling_export = export_rolling_csv(result)
    observations_export = export_observations_csv(result)
    decoded = json.loads(json_export)
    assert decoded["schema"] == "tpl.realized-volatility-analysis.v1"
    assert decoded["analysisId"] == result["analysisId"]
    assert "NaN" not in json_export and "Infinity" not in json_export
    assert rolling_export.startswith("schema,engineVersion,sourceSha256,annualization")
    assert observations_export.startswith("schema,engineVersion,sourceSha256,date,open")
    assert "=HYPERLINK" not in rolling_export + observations_export
    assert "+CMD" not in rolling_export + observations_export
    assert rolling_export == export_rolling_csv(result)
    assert observations_export == export_observations_csv(result)


def test_cli_reads_user_csv_and_emits_versioned_json(tmp_path: Path) -> None:
    csv_path = tmp_path / "fixture.csv"
    csv_path.write_text(rows_to_csv(CASES["mixed_ohlc_7"]["rows"]), encoding="utf-8")
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "pricinglibrary_rag.realized_volatility",
            str(csv_path),
            "--window",
            "5",
            "--price-basis",
            "split_adjusted_ohlc",
            "--source-label",
            "pytest fixture",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr
    result = json.loads(completed.stdout)
    assert result["schema"] == "tpl.realized-volatility-analysis.v1"
    assert result["provenance"]["filename"] == "fixture.csv"
    assert_close(
        result["summary"]["yangZhang"]["annualizedVol"],
        CASES["mixed_ohlc_7"]["expected"]["annualizedVol"]["yangZhang"],
        FIXTURE["tolerances"]["annualizedVol"],
    )
