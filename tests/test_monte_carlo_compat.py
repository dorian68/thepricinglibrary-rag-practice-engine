from pathlib import Path

import pytest

from pricinglibrary_rag.agui import mc_simulation
from pricinglibrary_rag.calculators import PracticeCalculator
from pricinglibrary_rag.monte_carlo import MonteCarloError


def test_agui_adapter_uses_canonical_physical_engine() -> None:
    first = mc_simulation(100.0, 5.0, 20.0, 252.0, 400, 50, 7)
    repeated = mc_simulation(100.0, 5.0, 20.0, 252.0, 400, 50, 7)

    assert first == repeated
    assert first["engine_version"] == "1.0.0"
    assert first["measure"] == "P"
    assert first["day_count"] == "ACT/365F"
    assert first["n"] == 400
    assert first["steps"] == 50
    assert len(first["paths"]) == 12
    assert len(first["paths"][0]) == 51
    assert sum(row["count"] for row in first["histogram"]) == 400


def test_agui_adapter_fails_closed_instead_of_clamping() -> None:
    with pytest.raises(MonteCarloError, match="paths must be"):
        mc_simulation(100.0, 5.0, 20.0, 252.0, 50, 50, 7)
    with pytest.raises(MonteCarloError, match="timeSteps must be"):
        mc_simulation(100.0, 5.0, 20.0, 252.0, 400, 500, 7)
    with pytest.raises(MonteCarloError, match="seed must be"):
        mc_simulation(100.0, 5.0, 20.0, 252.0, 400, 50, 0)


@pytest.mark.parametrize(
    ("overrides", "message"),
    (
        ({"N": 400.9}, "N must be a JSON integer"),
        ({"steps": 50.9}, "steps must be a JSON integer"),
        ({"seed": "7"}, "seed must be a JSON integer"),
        ({"S": "100"}, "S must be a finite JSON number"),
        ({"sigma": True}, "sigma must be a finite JSON number"),
    ),
)
def test_agui_adapter_rejects_coercible_values(overrides: dict, message: str) -> None:
    values = {"S": 100.0, "mu": 5.0, "sigma": 20.0, "T_days": 252.0, "N": 400, "steps": 50, "seed": 7}
    values.update(overrides)
    with pytest.raises(ValueError, match=message):
        mc_simulation(**values)


def test_practice_pack_uses_canonical_q_pricing_and_visible_evidence() -> None:
    pack = PracticeCalculator()._monte_carlo_pack(
        "Monte Carlo spot 100 strike 100 vol 20% maturite 1 taux 5% 10000 trajectoires"
    )

    assert pack is not None
    assert pack.family == "monte_carlo_gbm"
    assert any("mesure risque-neutre Q" in item for item in pack.assumptions)
    assert any("F-CAL-6 v1.0.0" in item for item in pack.assumptions)
    assert any("graine visible 20240617" in item for item in pack.assumptions)
    assert pack.steps[1].result == "10.5818"
    assert pack.steps[2].result == "0.1057"
    assert pack.steps[3].result == "[10.3746; 10.7890]"
    assert pack.steps[4].result == "10.4506"


@pytest.mark.parametrize("paths", (99, 101, 50001))
def test_practice_pack_rejects_out_of_contract_path_counts(paths: int) -> None:
    pack = PracticeCalculator()._monte_carlo_pack(
        f"Monte Carlo spot 100 strike 100 vol 20% maturite 1 taux 5% {paths} trajectoires"
    )

    assert pack is not None
    assert not pack.steps
    assert "refusee" in pack.title
    assert any("Aucun prix n'a ete calcule" in warning for warning in pack.warnings)


def test_practice_pack_surfaces_domain_errors_without_crashing_generation() -> None:
    pack = PracticeCalculator()._monte_carlo_pack(
        "Monte Carlo spot -100 strike 100 vol 20% maturite 1 taux 5% 10000 trajectoires"
    )

    assert pack is not None
    assert not pack.steps
    assert "refusee" in pack.title
    assert any("spot must be" in warning for warning in pack.warnings)


def test_no_independent_legacy_rng_remains_in_active_backend_consumers() -> None:
    package_root = Path(__file__).resolve().parents[1] / "pricinglibrary_rag"
    agui_source = (package_root / "agui.py").read_text(encoding="utf-8")
    calculator_source = (package_root / "calculators.py").read_text(encoding="utf-8")
    mc_tool_source = agui_source.split("def tool_simulate_monte_carlo", 1)[1].split("\ndef ", 1)[0]

    assert "def _gauss" not in agui_source
    assert "1103515245" not in agui_source
    assert "float(" not in mc_tool_source
    assert "int(" not in mc_tool_source
    assert "random.Random" not in calculator_source
    assert "rng.gauss" not in calculator_source
    assert "run_monte_carlo" in agui_source
    assert "run_monte_carlo" in calculator_source
