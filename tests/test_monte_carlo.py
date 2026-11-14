from __future__ import annotations

import csv
import hashlib
import io
import json
import math
import subprocess
import sys
from pathlib import Path

import pytest

from pricinglibrary_rag.monte_carlo import (
    ENGINE_VERSION,
    INPUT_SCHEMA_VERSION,
    MAX_INPUT_BYTES,
    PATHS_CSV_HEADERS,
    SCHEMA_VERSION,
    TERMINAL_CSV_HEADERS,
    MonteCarloError,
    ParkMiller16807,
    analysis_id,
    canonical_input_json,
    export_json,
    export_paths_csv,
    export_terminal_csv,
    load_request_file,
    monte_carlo_contract_snapshot,
    run_monte_carlo,
    validate_request,
)


CONTRACT_PATH = Path(__file__).resolve().parents[3] / "fixtures" / "monte_carlo_contract.json"
CONTRACT = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
JS_ENGINE_PATH = Path(__file__).resolve().parents[3] / "WEBSITE" / "thepricinglab" / "src" / "lib" / "monteCarlo.mjs"


def risk_request(**changes: object) -> dict[str, object]:
    request: dict[str, object] = {
        "schemaVersion": INPUT_SCHEMA_VERSION,
        "mode": "risk_physical",
        "spot": 100,
        "volatility": 0.2,
        "maturityYears": 1,
        "dayCount": "ACT/365F",
        "paths": 100,
        "timeSteps": 10,
        "seed": 7,
        "method": "none",
        "samplePaths": 2,
        "histogramBins": 10,
        "currency": "EUR",
        "quantity": 1,
        "contractMultiplier": 1,
        "position": "long",
        "physicalDrift": 0.05,
        "confidence": 0.95,
    }
    request.update(changes)
    return request


def pricing_request(**changes: object) -> dict[str, object]:
    request: dict[str, object] = {
        "schemaVersion": INPUT_SCHEMA_VERSION,
        "mode": "pricing_risk_neutral",
        "spot": 100,
        "volatility": 0.2,
        "maturityYears": 1,
        "dayCount": "ACT/365F",
        "paths": 400,
        "timeSteps": 12,
        "seed": 7,
        "method": "none",
        "samplePaths": 3,
        "histogramBins": 12,
        "currency": "USD",
        "quantity": 10,
        "contractMultiplier": 100,
        "position": "long",
        "riskFreeRate": 0.03,
        "dividendYield": 0.01,
        "strike": 100,
        "optionType": "call",
        "payoffType": "european",
    }
    request.update(changes)
    return request


def javascript_result(request: dict[str, object]) -> dict[str, object]:
    script = f"""
import {{ analyzeMonteCarlo, buildMonteCarloTerminalCsv, buildMonteCarloPathsCsv }} from {json.dumps(JS_ENGINE_PATH.as_uri())};
let body = '';
for await (const chunk of process.stdin) body += chunk;
const result = await analyzeMonteCarlo(JSON.parse(body));
process.stdout.write(JSON.stringify({{ result, terminalCsv: buildMonteCarloTerminalCsv(result), pathsCsv: buildMonteCarloPathsCsv(result) }}));
"""
    completed = subprocess.run(
        ["node", "--input-type=module", "-e", script],
        input=json.dumps(request),
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    return json.loads(completed.stdout)


def assert_recursive_close(python_value, javascript_value, path: str = "result") -> None:
    if isinstance(javascript_value, bool) or javascript_value is None or isinstance(javascript_value, str):
        assert python_value == javascript_value, path
    elif isinstance(javascript_value, (int, float)):
        assert isinstance(python_value, (int, float)) and not isinstance(python_value, bool), path
        assert abs(float(python_value) - float(javascript_value)) <= 1e-11, path
    elif isinstance(javascript_value, list):
        assert isinstance(python_value, list) and len(python_value) == len(javascript_value), path
        for index, (left, right) in enumerate(zip(python_value, javascript_value)):
            assert_recursive_close(left, right, f"{path}[{index}]")
    else:
        assert isinstance(python_value, dict), path
        assert list(python_value) == list(javascript_value), path
        for key in javascript_value:
            assert_recursive_close(python_value[key], javascript_value[key], f"{path}.{key}")


def test_runtime_projection_matches_shared_contract_authority() -> None:
    assert monte_carlo_contract_snapshot() == CONTRACT


def test_park_miller_and_box_muller_golden_sequence() -> None:
    rng = ParkMiller16807(1)
    assert [rng.uniform() for _ in range(5)] == pytest.approx([
        7.826369259425611e-06,
        0.13153778814316625,
        0.7556053221950332,
        0.4586501319234493,
        0.5327672374121692,
    ], abs=1e-16)
    rng = ParkMiller16807(1)
    assert [rng.normal() for _ in range(3)] == pytest.approx([
        3.2852859526035707,
        -0.7235216428387968,
        0.21748427203148357,
    ], abs=1e-15)


def test_canonical_json_and_analysis_id_are_golden_and_key_order_independent() -> None:
    request = risk_request()
    canonical = canonical_input_json(request)
    assert canonical == (
        '{"confidence":"9.4999999999999996e-1","contractMultiplier":"1e0","currency":"EUR","dayCount":"ACT/365F",'
        '"histogramBins":"1e1","maturityYears":"1e0","method":"none",'
        '"mode":"risk_physical","paths":"1e2","physicalDrift":"5.0000000000000003e-2",'
        '"position":"long","quantity":"1e0","samplePaths":"2e0",'
        '"schemaVersion":"tpl.monte-carlo.input.v1","seed":"7e0","spot":"1e2",'
        '"timeSteps":"1e1","volatility":"2.0000000000000001e-1"}'
    )
    assert analysis_id(request) == "42a7c42782b0e73123367b09d0b05278c3d8e2aff78af36fd12f6af1bfb5d473"
    reversed_request = dict(reversed(list(request.items())))
    assert analysis_id(reversed_request) == analysis_id(request)
    assert analysis_id(request) == hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def test_risk_engine_golden_results_and_same_run_paths() -> None:
    result = run_monte_carlo(risk_request())
    assert result["schemaVersion"] == SCHEMA_VERSION
    assert result["engineVersion"] == ENGINE_VERSION
    assert result["measure"] == "P"
    assert result["run"] == {
        "requestedPaths": 100,
        "simulatedPaths": 100,
        "timeSteps": 10,
        "samplePathCount": 2,
        "seed": 7,
        "method": "none",
        "rng": "park_miller_16807",
        "normalTransform": "box_muller_cosine",
    }
    assert [row["terminalSpot"] for row in result["observations"][:5]] == pytest.approx([
        115.73804548866009,
        76.04829374624894,
        97.17622739346818,
        72.42532151824201,
        127.03472008828811,
    ], abs=1e-12)
    assert result["risk"]["valueAtRisk"] == pytest.approx(25.052850991296918)
    assert result["risk"]["expectedShortfall"] == pytest.approx(34.56708898232588)
    assert result["risk"]["tailCount"] == 5
    for sampled in result["samplePaths"]:
        assert sampled["points"][-1]["spot"] == result["observations"][sampled["pathIndex"]]["terminalSpot"]
    assert sum(bin_["count"] for bin_ in result["distribution"]["histogram"]) == 100
    assert result == run_monte_carlo(risk_request())


def test_var_es_are_positive_loss_amounts_and_position_aware() -> None:
    long_result = run_monte_carlo(risk_request(physicalDrift=0.25, volatility=0.01))
    short_result = run_monte_carlo(risk_request(physicalDrift=0.25, volatility=0.01, position="short"))
    assert long_result["risk"]["valueAtRisk"] == 0
    assert all(
        long_row["pnl"] == pytest.approx(-short_row["pnl"])
        and long_row["loss"] == pytest.approx(-short_row["loss"])
        for long_row, short_row in zip(long_result["observations"], short_result["observations"])
    )
    assert short_result["risk"]["valueAtRisk"] > 0


def test_antithetic_paths_are_exact_pairs_from_one_run() -> None:
    request = risk_request(paths=100, timeSteps=1, method="antithetic", samplePaths=4)
    result = run_monte_carlo(request)
    deterministic_log_sum = 2 * (request["physicalDrift"] - 0.5 * request["volatility"] ** 2) * request["maturityYears"]
    for index in range(0, 100, 2):
        first = math.log(result["observations"][index]["terminalSpot"] / request["spot"])
        second = math.log(result["observations"][index + 1]["terminalSpot"] / request["spot"])
        assert first + second == pytest.approx(deterministic_log_sum, abs=1e-14)


def test_pricing_european_reports_unit_portfolio_ci_and_bs_benchmark() -> None:
    result = run_monte_carlo(pricing_request(paths=2000, timeSteps=1))
    pricing = result["pricing"]
    assert result["measure"] == "Q"
    assert pricing["portfolioValue"] == pytest.approx(pricing["price"] * 1000)
    assert pricing["blackScholesBenchmark"] == pytest.approx(8.827318817102572, abs=1e-12)
    assert abs(pricing["price"] - pricing["blackScholesBenchmark"]) < 4 * pricing["standardError"]


def test_short_pricing_portfolio_value_is_signed_and_interval_ordered() -> None:
    long_result = run_monte_carlo(pricing_request(position="long"))["pricing"]
    short_result = run_monte_carlo(pricing_request(position="short"))["pricing"]
    assert short_result["portfolioValue"] == pytest.approx(-long_result["portfolioValue"])
    assert short_result["ci95"]["lower"] <= short_result["ci95"]["upper"]


def test_antithetic_and_control_variate_have_declared_se_bases() -> None:
    anti = run_monte_carlo(pricing_request(method="antithetic", paths=400))["pricing"]
    control = run_monte_carlo(pricing_request(method="control_variate", paths=400))["pricing"]
    plain = run_monte_carlo(pricing_request(method="none", paths=400))["pricing"]
    assert anti["effectiveSamples"] == 200
    assert control["effectiveSamples"] == 400
    assert math.isfinite(control["beta"])
    assert anti["standardError"] < plain["standardError"]
    assert control["standardError"] < plain["standardError"]


def test_arithmetic_asian_excludes_time_zero_and_has_no_bs_benchmark() -> None:
    request = pricing_request(
        volatility=0,
        riskFreeRate=0.12,
        dividendYield=0.02,
        maturityYears=1,
        timeSteps=2,
        strike=100,
        payoffType="arithmetic_asian",
    )
    result = run_monte_carlo(request)
    monitored = (100 * math.exp(0.1 * 0.5) + 100 * math.exp(0.1)) / 2
    expected = math.exp(-0.12) * max(monitored - 100, 0)
    assert result["pricing"]["price"] == pytest.approx(expected, abs=1e-12)
    assert result["pricing"]["blackScholesBenchmark"] is None
    assert result["pricing"]["standardError"] == pytest.approx(0, abs=1e-15)


def test_zero_volatility_is_finite_and_histogram_keeps_all_paths() -> None:
    result = run_monte_carlo(risk_request(volatility=0, physicalDrift=0))
    assert result["distribution"]["terminalStdDev"] == 0
    assert sum(item["count"] for item in result["distribution"]["histogram"]) == 100
    assert len(result["distribution"]["histogram"]) == 1
    assert "NaN" not in export_json(result)
    assert "Infinity" not in export_json(result)


def test_convergence_uses_prefixes_of_the_same_run() -> None:
    result = run_monte_carlo(pricing_request(paths=120))
    assert [row["paths"] for row in result["pricing"]["convergence"]] == [30, 60, 120]
    anti = run_monte_carlo(pricing_request(paths=102, method="antithetic"))
    assert [row["paths"] for row in anti["pricing"]["convergence"]] == [24, 50, 102]


@pytest.mark.parametrize(
    "mutator",
    [
        lambda value: value.pop("spot"),
        lambda value: value.update(extra=1),
        lambda value: value.update(schemaVersion=SCHEMA_VERSION),
        lambda value: value.update(spot="100"),
        lambda value: value.update(paths=100.0),
        lambda value: value.update(paths=True),
        lambda value: value.update(seed=0),
        lambda value: value.update(currency="eur"),
        lambda value: value.update(dayCount="ACT/252"),
        lambda value: value.update(samplePaths=25),
        lambda value: value.update(volatility=float("nan")),
        lambda value: value.update(paths=101, method="antithetic"),
        lambda value: value.update(method="control_variate"),
    ],
)
def test_validation_is_strict_fail_closed(mutator) -> None:
    request = risk_request()
    mutator(request)
    with pytest.raises(MonteCarloError):
        validate_request(request)


def test_mode_specific_fields_are_forbidden() -> None:
    risk = risk_request(riskFreeRate=0.03)
    pricing = pricing_request(physicalDrift=0.05)
    with pytest.raises(MonteCarloError, match="unexpected fields"):
        validate_request(risk)
    with pytest.raises(MonteCarloError, match="unexpected fields"):
        validate_request(pricing)


def test_recursive_non_finite_guard_rejects_nested_values() -> None:
    request = risk_request(extra={"nested": [1, float("inf")]})
    with pytest.raises(MonteCarloError, match="NaN or Infinity"):
        validate_request(request)


def test_unbounded_python_integer_fails_as_a_domain_error() -> None:
    with pytest.raises(MonteCarloError, match="spot must be a finite JSON number"):
        run_monte_carlo({**pricing_request(), "spot": 10**10_000})


def test_terminal_and_path_csv_are_exact_schema_lf_and_same_run() -> None:
    result = run_monte_carlo(risk_request(samplePaths=2, timeSteps=3))
    terminal_text = export_terminal_csv(result)
    path_text = export_paths_csv(result)
    assert terminal_text.endswith("\n") and "\r" not in terminal_text
    assert path_text.endswith("\n") and "\r" not in path_text
    terminal_rows = list(csv.DictReader(io.StringIO(terminal_text)))
    path_rows = list(csv.DictReader(io.StringIO(path_text)))
    assert tuple(terminal_rows[0]) == TERMINAL_CSV_HEADERS
    assert tuple(path_rows[0]) == PATHS_CSV_HEADERS
    assert len(terminal_rows) == 100
    assert len(path_rows) == 2 * 4
    assert terminal_rows[0]["analysisId"] == result["analysisId"]
    final_path_row = [row for row in path_rows if row["pathIndex"] == "0"][-1]
    assert float(final_path_row["spot"]) == pytest.approx(result["observations"][0]["terminalSpot"], rel=1e-11)
    assert terminal_rows[0]["discountedPayoff"] == ""
    assert "e+" not in terminal_text and "e-0" not in terminal_text


@pytest.mark.parametrize("format_name", ["json", "terminal-csv", "paths-csv"])
def test_cli_formats_are_deterministic_and_stdout_clean(tmp_path: Path, format_name: str) -> None:
    path = tmp_path / "request.json"
    path.write_text(json.dumps(pricing_request()), encoding="utf-8")
    command = [sys.executable, "-m", "pricinglibrary_rag.monte_carlo", "--input", str(path), "--format", format_name]
    first = subprocess.run(command, text=True, capture_output=True, check=False)
    second = subprocess.run(command, text=True, capture_output=True, check=False)
    assert first.returncode == 0, first.stderr
    assert first.stderr == ""
    assert first.stdout == second.stdout
    if format_name == "json":
        assert json.loads(first.stdout)["analysisId"] == analysis_id(pricing_request())
    else:
        assert first.stdout.endswith("\n")


def test_loader_rejects_duplicate_keys_invalid_constants_and_oversize_before_json(tmp_path: Path) -> None:
    duplicate = tmp_path / "duplicate.json"
    duplicate.write_text('{"mode":"risk_physical","mode":"risk_physical"}', encoding="utf-8")
    with pytest.raises(MonteCarloError, match="duplicate"):
        load_request_file(str(duplicate))
    invalid = tmp_path / "invalid.json"
    invalid.write_text('{"x":NaN}', encoding="utf-8")
    with pytest.raises(MonteCarloError, match="forbidden"):
        load_request_file(str(invalid))
    oversized = tmp_path / "oversized.json"
    with oversized.open("wb") as handle:
        handle.seek(MAX_INPUT_BYTES)
        handle.write(b"x")
    with pytest.raises(MonteCarloError, match="exceeds"):
        load_request_file(str(oversized))


def test_cli_validation_error_is_fail_closed(tmp_path: Path) -> None:
    path = tmp_path / "bad.json"
    path.write_text(json.dumps(risk_request(extra=1)), encoding="utf-8")
    completed = subprocess.run(
        [sys.executable, "-m", "pricinglibrary_rag.monte_carlo", "--input", str(path), "--format", "json"],
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 2
    assert completed.stdout == ""
    assert completed.stderr.startswith("ERROR:")


@pytest.mark.parametrize(
    "case_input",
    [
        risk_request(paths=120, timeSteps=7, confidence=0.95),
        risk_request(paths=120, timeSteps=7, confidence=0.99, method="antithetic", position="short"),
        pricing_request(paths=120, timeSteps=7, method="none"),
        pricing_request(paths=120, timeSteps=7, method="antithetic", optionType="put"),
        pricing_request(paths=120, timeSteps=7, method="control_variate", payoffType="arithmetic_asian"),
    ],
    ids=("risk-95", "risk-99-antithetic", "pricing-none", "pricing-antithetic", "pricing-control-asian"),
)
def test_python_matches_javascript_recursively_and_csv_byte_for_byte(case_input: dict[str, object]) -> None:
    javascript = javascript_result(case_input)
    python_result = run_monte_carlo(case_input)
    assert_recursive_close(python_result, javascript["result"])
    assert export_terminal_csv(python_result) == javascript["terminalCsv"]
    assert export_paths_csv(python_result) == javascript["pathsCsv"]
