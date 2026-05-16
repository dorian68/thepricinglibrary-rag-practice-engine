from pricinglibrary_rag.generation import MaterialGenerator
from pricinglibrary_rag.schemas import ExerciseRequest
from pricinglibrary_rag.calculators import PracticeCalculator


def _generator() -> MaterialGenerator:
    generator = MaterialGenerator.__new__(MaterialGenerator)
    generator.calculator = PracticeCalculator()
    return generator


def test_options_book_numeric_controls_respect_percent_units() -> None:
    generator = _generator()
    request = ExerciseRequest(
        topic="Options book risk",
        free_prompt=(
            "delta +250k EUR par 1%, gamma -80k EUR par 1%^2, "
            "vega +120k EUR par vol point, theta -15k EUR par jour. "
            "Scenario: spot -2%, vol +3 points."
        ),
    )
    block = generator._numeric_control_block(request)
    assert "Resultat: -500,000 EUR" in block
    assert "Resultat: -160,000 EUR" in block
    assert "Resultat: 360,000 EUR" in block
    assert "Resultat: -315,000 EUR" in block


def test_swap_numeric_controls_use_million_notional() -> None:
    generator = _generator()
    request = ExerciseRequest(
        topic="Swap DV01",
        free_prompt=(
            "payer swap EUR 5Y, notionnel 100m, fixed coupon 3.20%, "
            "par swap rate actuel 3.00%, annuity approx 4.55, "
            "la courbe monte de 10bp."
        ),
    )
    block = generator._numeric_control_block(request)
    assert "45,500 EUR/bp" in block
    assert "-910,000 EUR" in block
    assert "455,000 EUR" in block


def test_barrier_controls_do_not_parse_initial_spot_as_barrier() -> None:
    generator = _generator()
    request = ExerciseRequest(
        topic="FX barrier",
        free_prompt=(
            "option barriere FX. Donnees imposees: EUR/USD spot 1.0800, "
            "strike 1.1000, barriere down-and-out 1.0000, notionnel EUR 10m. "
            "scenarios spot a 1.0500, spot a 1.0000, spot a 1.2000 sans knock-out."
        ),
    )
    block = generator._numeric_control_block(request)
    assert "max(1.05 - 1.1, 0) * 10,000,000" in block
    assert "spot 1 <= barriere 1" in block
    assert "1,000,000 USD approx" in block
    assert "Distance initiale a la barriere: 8.00%" in block


def test_vanilla_option_calculator_outputs_greeks() -> None:
    generator = _generator()
    request = ExerciseRequest(
        topic="Black-Scholes call",
        free_prompt="call vanilla spot 100 strike 100 vol 20% maturite 1 taux 5%",
    )
    block = generator._numeric_control_block(request)
    assert "Option vanilla Black-Scholes" in block
    assert "Delta=" in block
    assert "Vega/vol pt" in block


def test_cds_and_var_calculators_are_available() -> None:
    generator = _generator()
    cds = generator._numeric_control_block(
        ExerciseRequest(
            topic="CDS",
            free_prompt="CDS notionnel 50m spread 120bp risky annuity 4.2 shock 25bp",
        )
    )
    var = generator._numeric_control_block(
        ExerciseRequest(
            topic="VaR",
            free_prompt="VaR portefeuille 20m volatilite 2% confiance 95% horizon 1 jour",
        )
    )
    assert "CS01" in cds
    assert "VaR parametrique" in var


def test_calculator_family_hint_is_supported() -> None:
    pack = PracticeCalculator().build_pack(
        "CDS notionnel 50m spread 120bp risky annuity 4.2 shock 25bp",
        family_hint="cds_cs01",
    )
    assert pack.family == "cds_cs01"
