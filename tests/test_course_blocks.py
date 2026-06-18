from pricinglibrary_rag.course_blocks import (
    corrected_exercise_markdown,
    detect_topic_key,
    quiz_markdown,
    worked_example_markdown,
)
from pricinglibrary_rag.text_utils import clean_ocr_text, clean_snippet


def test_clean_ocr_text_fixes_ligatures_and_double_periods():
    assert clean_ocr_text("proﬁle") == "profile"
    assert clean_ocr_text("Pricing sheet..") == "Pricing sheet."
    assert clean_ocr_text("hedg-\ning") == "hedging"


def test_clean_snippet_rejects_midword_fragment():
    assert clean_snippet("ty, call and put options have the same vega") == ""


def test_clean_snippet_truncates_at_figure_noise():
    text = (
        "The option may be replicated by holding a European bond and a forward. "
        "[Page 698] 2 Put Call Parity S Payoff K Call Short put Forward"
    )
    out = clean_snippet(text)
    assert out
    assert "Page" not in out
    assert "Payoff K Call" not in out
    assert out.startswith("The option may be replicated")


def test_clean_snippet_keeps_clean_prose():
    text = "A barrier option is path dependent. It can be knocked out at the barrier."
    out = clean_snippet(text)
    assert "barrier option is path dependent" in out


def test_detect_topic_key():
    assert detect_topic_key("Vanilla options desk quote", "equity option", ["Black-Scholes"]) == "vanilla_bs"
    assert detect_topic_key("Options book Greeks", "book", ["delta", "gamma"]) == "greeks"
    assert detect_topic_key("Interest-rate swaps and DV01", "swap", ["par rate"]) == "swap"
    assert detect_topic_key("Random unrelated topic", None, []) == "generic"


def test_worked_example_has_real_numbers():
    md = worked_example_markdown("vanilla_bs")
    assert "calcul verifie" in md
    assert "d1=" in md
    assert "Prix call" in md
    # Black-Scholes ATM call ~ 10.45
    assert "10.45" in md


def test_corrected_exercise_has_two_exercises_and_correction():
    md = corrected_exercise_markdown("greeks")
    assert "Exercice 1" in md
    assert "Exercice 2" in md
    assert "Correction" in md


def test_quiz_has_five_questions_with_answers():
    md = quiz_markdown("vanilla_bs")
    assert md.count("**Q") == 5
    assert "Reponse:" in md
