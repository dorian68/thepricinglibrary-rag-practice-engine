from pricinglibrary_rag.generation import MaterialGenerator
from pricinglibrary_rag.schemas import ExerciseRequest


def test_options_book_numeric_controls_respect_percent_units() -> None:
    generator = MaterialGenerator.__new__(MaterialGenerator)
    request = ExerciseRequest(
        topic="Options book risk",
        free_prompt=(
            "delta +250k EUR par 1%, gamma -80k EUR par 1%^2, "
            "vega +120k EUR par vol point, theta -15k EUR par jour. "
            "Scenario: spot -2%, vol +3 points."
        ),
    )
    block = generator._numeric_control_block(request)
    assert "P&L delta = 250,000 * (-2) = -500,000 EUR" in block
    assert "P&L gamma = 0.5 * -80,000 * (-2)^2 = -160,000 EUR" in block
    assert "P&L vega = 120,000 * (3) = 360,000 EUR" in block
    assert "P&L total approx = -315,000 EUR" in block


def test_swap_numeric_controls_use_million_notional() -> None:
    generator = MaterialGenerator.__new__(MaterialGenerator)
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
    generator = MaterialGenerator.__new__(MaterialGenerator)
    request = ExerciseRequest(
        topic="FX barrier",
        free_prompt=(
            "option barriere FX. Donnees imposees: EUR/USD spot 1.0800, "
            "strike 1.1000, barriere down-and-out 1.0000, notionnel EUR 10m. "
            "scenarios spot a 1.0500, spot a 1.0000, spot a 1.2000 sans knock-out."
        ),
    )
    block = generator._numeric_control_block(request)
    assert "Scenario spot 1.05 sans knock-out" in block
    assert "Scenario spot 1: barriere touchee/atteinte => payoff = 0" in block
    assert "1,000,000 USD approx" in block
    assert "distance a la barriere = 8.00%" in block
