"""English learner output, calculator invariants and source-quality regressions."""
from __future__ import annotations

import math
import re

import pytest

from pricinglibrary_rag.calculators import PracticeCalculator
from pricinglibrary_rag.course_blocks import _WORKED_SEEDS
from pricinglibrary_rag.exercise_assessment import build_assessment, assessment_matches_document
from pricinglibrary_rag.exercise_english import english_pack, quant_english
from pricinglibrary_rag.generation import GenerationContext, MaterialGenerator
from pricinglibrary_rag.schemas import ExerciseRequest, SourceRef
from test_exercise_generation import PROMPT, auth, services  # isolated real ingestion/generation fixture


def context(sources=()):
    return GenerationContext(query="English test", retrieved=[], sources=list(sources),
                             facts=[], keywords=[], coverage={}, gaps={}, source_pedagogy=[])


def source(title, snippet, number):
    return SourceRef(document_id=f"test-doc-{number}", chunk_id=f"test-chunk-{number}",
                     title=title, source="synthetic-test-reference.txt", chunk_index=number,
                     score=1, vector_score=0, lexical_score=1, snippet=snippet)


READABLE = ("European option valuation uses a continuously compounded discount rate and a dividend yield. "
            "An option delta hedge offsets the local direction of underlying exposure; gamma and vega remain separate risks.")


@pytest.mark.parametrize("count", [1, 3, 5, 8, 12])
def test_real_template_generation_uses_english_without_changing_verified_numbers(services, count):
    request = ExerciseRequest(language="en", product="European call option", concept="Black Scholes",
                              free_prompt=PROMPT, number_of_questions=count)
    result = services.generator.generate_exercise(request)
    assessment = result.metadata["assessment"]
    assert result.title.startswith("Desk case - ")
    assert result.metadata["language"] == assessment["language"] == "en"
    assert result.metadata["generation_mode"] == "template"
    assert len(assessment["questions"]) == count
    assert sum(q["points"] for q in assessment["questions"]) == 100
    assert len(re.findall(r"^### Answer \d+", result.content, re.M)) == count
    assert assessment_matches_document(result.content, assessment)
    assert "## Desk brief" in result.content and "## Verified solution" in result.content
    assert "## Assessment rubric" in result.content and "Self-review" in result.content
    assert "## Corrige" not in result.content and "Réponse" not in result.content
    assert "Moteur canonique" not in result.content
    # An independent elementary normal-CDF oracle, not the production BS helper.
    s, k, sigma, t, r, q = 125, 110, .30, .75, .03, .01
    cdf = lambda x: (1 + math.erf(x / math.sqrt(2))) / 2
    d1 = (math.log(s/k) + (r-q+sigma*sigma/2)*t) / (sigma*math.sqrt(t))
    call = s*math.exp(-q*t)*cdf(d1)-k*math.exp(-r*t)*cdf(d1-sigma*math.sqrt(t))
    expected = f"{call:.4f}"
    assert expected not in result.content.split("## Verified solution")[0]
    assert expected in result.content.split("## Verified solution")[1]
    assert result.metadata["calculation_pack"]["steps"][1]["result"] == expected
    assert assessment_matches_document(result.content, assessment)
    assert not assessment_matches_document(result.content.replace("### Answer 1", "### Answer 99"), assessment)


@pytest.mark.parametrize("topic", list(_WORKED_SEEDS))
def test_all_supported_families_have_english_questions_and_unchanged_numerical_steps(topic):
    family, ticket, _ = _WORKED_SEEDS[topic]
    pack = PracticeCalculator().build_pack(ticket, family_hint=family)
    original = pack.model_dump()
    view = english_pack(pack)
    assert pack.steps, topic
    assert len(view.steps) == len(pack.steps)
    for raw, shown in zip(pack.steps, view.steps):
        # Translation may change unit names; every numerical literal stays exact.
        assert re.findall(r"[-+]?\d[\d,.]*(?:e[-+]?\d+)?", shown.result) == re.findall(r"[-+]?\d[\d,.]*(?:e[-+]?\d+)?", raw.result)
    request = ExerciseRequest(language="en", topic=topic, number_of_questions=5)
    generator = MaterialGenerator.__new__(MaterialGenerator)
    document = generator._exercise_template(request, "English practice case", context(), pack, ticket)
    assessment = build_assessment(request, pack)
    assert assessment_matches_document(document, assessment)
    assert "## Given data and assumptions" in document
    assert "### Model limitations" in document
    assert "## Corrige" not in document and "### Réponse" not in document
    assert not re.search(r"\b(?:maturite|notionnel|barriere|volatilite|confiance|portefeuille|annuite|perte|moyenne)\b", document, re.I)
    assert pack.model_dump() == original  # English view must not mutate the audit pack.


def test_beginner_and_expert_tasks_change_and_french_remains_supported(services):
    args = dict(product="European call", free_prompt=PROMPT, number_of_questions=3)
    beginner = services.generator.generate_exercise(ExerciseRequest(language="en", difficulty="beginner", **args))
    expert = services.generator.generate_exercise(ExerciseRequest(language="en", difficulty="expert", **args))
    french = services.generator.generate_exercise(ExerciseRequest(language="fr", **args))
    assert "Hint:" in beginner.content and "Audit the assumptions" in expert.content
    assert beginner.metadata["calculation_pack"] == expert.metadata["calculation_pack"] == french.metadata["calculation_pack"]
    assert "## Brief de desk" in french.content and "### Réponse 1" in french.content
    assert french.metadata["language"] == "fr"


def test_localisation_preserves_financial_par_and_operational_units():
    text = quant_english("Payer swap par swap rate 3.00%, delta 20 EUR par 1%, theta -2 EUR par jour.")
    assert "par swap rate 3.00%" in text
    assert "20 EUR per 1%" in text and "-2 EUR per day" in text
    assert "annual par swaps" in quant_english("Bootstrap de courbe, swaps par annuels: 1 an 3.00%")


def test_reference_layer_rejects_ocr_fragments_and_deduplicates_books_without_rewriting_sources():
    sources = [
        source("Test Book ( PDFDrive ).pdf", "", 1),
        source("Test Book ( PDFDrive ).pdf", "1.387) " + READABLE, 2),
        source("Test Book ( PDFDrive ).pdf", READABLE, 3),
        source("TEST BOOK [PDFDrive].PDF", READABLE + " Additional clean context.", 4),
        source("Broken Formula", "= _ ^ { } | " + READABLE, 5),
        source("Replacement Glyphs", "\ufffd " + READABLE, 6),
    ]
    original = [s.model_dump() for s in sources]
    generator = MaterialGenerator.__new__(MaterialGenerator)
    shown = generator._source_lines(context(sources), "vanilla_option_black_scholes", "en")
    assert shown.count("- *") == 1
    assert "*test book*" in shown.lower() and READABLE in shown
    assert "PDFDrive" not in shown and "1.387)" not in shown
    assert "test-chunk" not in shown and "Broken Formula" not in shown
    assert [s.model_dump() for s in sources] == original


def test_reference_layer_does_not_show_an_unreadable_or_unrelated_title_as_evidence():
    generator = MaterialGenerator.__new__(MaterialGenerator)
    invalid = context([source("Unreadable book", "1.387) " + READABLE, 1)])
    missing = generator._verified_sources_block(invalid, "vanilla_option_black_scholes", "en")
    assert "No readable source excerpt" in missing and "Unreadable book" not in missing
    unrelated = context([source("Synthetic credit reference", "Credit default swaps have a protection leg and premium payments. "
                            "The credit spread and recovery assumptions affect survival probabilities over the contract horizon.", 2)])
    assert "No readable source excerpt" in generator._source_lines(unrelated, "vanilla_option_black_scholes", "en")
    assert "No readable source excerpt" in generator._source_lines(context(), language="en")


def test_writer_reference_section_is_replaced_with_the_single_authoritative_list(services):
    class Writer:
        name = "test:reference-writer"

        def generate(self, prompt, **_):
            draft = prompt.split("[TEMPLATE_OUTPUT]", 1)[1].strip()
            return draft.split("## References", 1)[0] + "## References\n- Invented writer book and citation."

    services.generator.llm = Writer()
    result = services.generator.generate_exercise(ExerciseRequest(language="en", product="European call", free_prompt=PROMPT))
    assert "Invented writer book" not in result.content
    assert result.content.count("## References") == 1
    assert "European option desk reference" in result.content
    assert result.metadata["generation_mode"] == "llm"


def test_wrong_language_writer_headings_fall_back_to_authored_english(services):
    class Writer:
        name = "test:wrong-language-writer"

        def generate(self, prompt, **_):
            draft = prompt.split("[TEMPLATE_OUTPUT]", 1)[1].strip()
            return draft.replace("## Desk brief", "## Brief de desk")

    services.generator.llm = Writer()
    result = services.generator.generate_exercise(ExerciseRequest(language="en", product="European call", free_prompt=PROMPT))
    assert result.metadata["generation_mode"] == "template_after_validation"
    assert "## Desk brief" in result.content and "## Brief de desk" not in result.content


def test_signed_api_preserves_english_in_the_private_account_library(services):
    from fastapi.testclient import TestClient
    from pricinglibrary_rag.api import create_app

    services.store.upsert_entitlement("english-learner@test.invalid", "starter", user_id="english-learner")
    client = TestClient(create_app(services))
    headers = auth(services, "english-learner")
    body = {"product": "European call", "free_prompt": PROMPT, "language": "en",
            "client_request_id": "english-http-persistence", "number_of_questions": 3}
    response = client.post("/agent/exercise", headers=headers, json=body)
    assert response.status_code == 200
    result = response.json()
    assert result["metadata"]["language"] == "en" and "## Verified solution" in result["content"]
    saved = client.get(f'/platform/exercises/{result["metadata"]["library_id"]}', headers=headers)
    assert saved.status_code == 200
    assert saved.json()["request"]["language"] == "en" and saved.json()["response"] == result
    assert client.get(f'/platform/exercises/{result["metadata"]["library_id"]}').status_code == 401


@pytest.mark.parametrize("notional_millions", [1, 10])
@pytest.mark.parametrize("barrier", [1.0, 1.03])
def test_english_fx_barrier_keeps_the_requested_notional_barrier_and_terminal_scenarios(notional_millions, barrier):
    ticket = (f"EUR/USD down-and-out call spot 1.0800 strike 1.1000, barrier down-and-out {barrier:.4f}, "
              f"notional EUR {notional_millions}m. Terminal scenarios: spot at 0.9900, spot at {barrier:.4f}, "
              "spot at 1.2000. For terminal spots above the barrier, assume it was not hit earlier.")
    pack = PracticeCalculator().build_pack(ticket, family_hint="fx_barrier_option")
    assert pack.family == "fx_barrier_option" and len(pack.steps) == 3
    assert pack.steps[0].result == pack.steps[1].result == "0 USD"
    assert pack.steps[-1].result == f"{notional_millions * 100_000:,.0f} USD"
    assert f"<= barriere {barrier:g}" in pack.steps[1].substitution
    french = ticket.replace("barrier down-and-out", "barriere down-and-out").replace("notional EUR", "notionnel EUR").replace("spot at", "spot a")
    original = PracticeCalculator().build_pack(french, family_hint="fx_barrier_option")
    assert [s.result for s in original.steps] == [s.result for s in pack.steps]


def test_reference_layer_withholds_control_glyphs_and_flattened_positive_parts_and_prefers_intact_prose():
    generator = MaterialGenerator.__new__(MaterialGenerator)
    # Original synthetic teaching prose, not excerpts copied from the corpus.
    broken = "A call payoff is written X - K+ = X - K+ in this flattened mathematical expression. " + READABLE
    controls = "An option model uses a volatility parameter \x16 and a dividend assumption. " + READABLE
    generic = ("The development of numerical methods for multiasset American options remains a subject of research "
               "and implementation work (see [AA12, BB14, CC15]).")
    intact = ("A forward contract is entered at the equilibrium forward price F0. "
              "At inception its present value is zero under the same discounting convention.")
    sources = [source("Synthetic derivatives book", broken, 1),
               source("Synthetic derivatives book", controls, 2),
               source("Synthetic derivatives book", generic, 3),
               source("Synthetic derivatives book", intact, 4)]
    before = [s.model_dump() for s in sources]
    shown = generator._source_lines(context(sources), "vanilla_option_black_scholes", "en")
    assert shown.count("- *") == 1
    assert intact in shown and generic not in shown
    assert broken not in shown and controls not in shown
    assert [s.model_dump() for s in sources] == before
    # A sound isolated equality in explanatory prose is not treated as OCR.
    assert generator._presentable_source_snippet(intact.replace("present value is zero", "present value V = 0"))
    assert not generator._presentable_source_snippet(READABLE.replace("option", "option\x03", 1))
