from __future__ import annotations

import math
import re
import time
from concurrent.futures import ThreadPoolExecutor

import pytest

from pricinglibrary_rag.calculators import PracticeCalculator
from pricinglibrary_rag.factory import build_services
from pricinglibrary_rag.practice_agent import PracticeAgent
from pricinglibrary_rag.retrieval import build_retriever
from pricinglibrary_rag.schemas import DocumentMetadata, ExerciseRequest
from test_api_security import _settings
from fastapi.testclient import TestClient
from pricinglibrary_rag.api import create_app
from pricinglibrary_rag.security import mint_session_token
from pricinglibrary_rag.platform_store import PlatformStore


PROMPT = "European call spot125 strike110 volatility30% maturity0.75 risk-free rate3% dividend yield1%"


def oracle_call(q):
    s, k, vol, t, r = 125, 110, .3, .75, .03
    d1 = (math.log(s/k) + (r-q+vol*vol/2)*t)/(vol*math.sqrt(t))
    cdf = lambda x: .5*(1+math.erf(x/math.sqrt(2)))
    return s*math.exp(-q*t)*cdf(d1)-k*math.exp(-r*t)*cdf(d1-vol*math.sqrt(t))


@pytest.mark.parametrize("dividend", [0, 1, -1, 4])
def test_custom_dividend_reaches_prices_parity_and_greeks(dividend):
    pack = PracticeCalculator().build_pack(PROMPT.replace("yield1%", f"yield{dividend}%"), family_hint="vanilla_option_black_scholes")
    price = next(s for s in pack.steps if s.label == "Prix call")
    assert float(price.result) == pytest.approx(oracle_call(dividend/100), abs=5e-5)
    assert "exp(-qT)" in price.formula
    assert f"{dividend/100:.4f}" in price.substitution
    assert any("q=" in assumption for assumption in pack.assumptions)


def test_formula_aliases_and_invalid_or_unsupported_constraints():
    calculator = PracticeCalculator()
    pack = calculator.build_pack("Black Scholes call S=125 K=110 sigma=30% T=0.75 r=3% q=1%", family_hint="vanilla_option_black_scholes")
    assert float(next(s.result for s in pack.steps if s.label == "Prix call")) == pytest.approx(oracle_call(.01), abs=5e-5)
    with pytest.raises(RuntimeError, match="pourcentage"):
        calculator.build_pack(PROMPT.replace("yield1%", "yield1"), family_hint="vanilla_option_black_scholes")
    with pytest.raises(RuntimeError, match="taux sans risque"):
        calculator.build_pack(PROMPT.replace("rate3%", "rate3"), family_hint="vanilla_option_black_scholes")
    with pytest.raises(RuntimeError, match="européen"):
        calculator.build_pack(PROMPT.replace("European", "American"), family_hint="vanilla_option_black_scholes")
    months = calculator.build_pack(PROMPT.replace("maturity0.75", "maturity9 months"), family_hint="vanilla_option_black_scholes")
    assert float(next(s.result for s in months.steps if s.label == "Prix call")) == pytest.approx(oracle_call(.01), abs=5e-5)


@pytest.fixture
def services(tmp_path):
    service = build_services(_settings(tmp_path))
    source = tmp_path / "European-options-reference.txt"
    source.write_text("European options use continuous dividend yield in Black Scholes valuation. "
                      "Delta and gamma measure market risk. A call option and a put option share a put call parity control. "
                      "The risk free rate discounts the strike, whereas the dividend yield discounts the spot. "
                      "A hedge decision uses the calculated delta, explicit units, model assumptions and risk limits.", encoding="utf-8")
    service.ingestion.ingest_file(source, DocumentMetadata(title="European option desk reference", product="option"))
    return service


@pytest.mark.parametrize("count", [1, 3, 5, 8, 12])
def test_questions_answers_rubric_share_the_requested_count_and_real_pack(services, count):
    result = PracticeAgent(services.generator).create_exercise(ExerciseRequest(
        product="European call option", concept="Black Scholes", free_prompt=PROMPT, number_of_questions=count))
    assessment = result.metadata["assessment"]
    assert len(assessment["questions"]) == count
    assert sum(q["points"] for q in assessment["questions"]) == 100
    assert len(re.findall(r"^### Réponse \d+", result.content, re.M)) == count
    questions = result.content.split("## Questions\n")[1].split("\n---")[0]
    assert len(re.findall(r"^\d+\. ", questions, re.M)) == count
    assert "Mission produit" not in result.content and "Structure obligatoire" not in result.content
    assert "Moteur canonique" not in result.content
    assert "21.9775" not in result.content.split("## Corrige verifie")[0]
    assert "21.9775" in result.content
    assert result.metadata["source_grounded"] and result.sources
    assert result.metadata["generation_mode"] == "template"


def test_difficulty_and_format_change_the_tasks_and_not_the_verified_answer(services):
    agent = PracticeAgent(services.generator)
    beginner = agent.create_exercise(ExerciseRequest(free_prompt=PROMPT, product="option", difficulty="beginner", exercise_format="quantitative_problem"))
    expert = agent.create_exercise(ExerciseRequest(free_prompt=PROMPT, product="option", difficulty="expert", exercise_format="risk_management"))
    bq = beginner.metadata["assessment"]["questions"]
    eq = expert.metadata["assessment"]["questions"]
    assert bq != eq and "Aide" in str(bq) and "Auditer" in str(eq)
    assert "unités" in bq[0]["prompt"] and "couverture" in eq[0]["prompt"]
    assert beginner.metadata["calculation_pack"] == expert.metadata["calculation_pack"]


def test_partial_numeric_request_is_not_replaced_with_an_unrelated_seed(services):
    with pytest.raises(RuntimeError, match="substitué"):
        services.generator.generate_exercise(ExerciseRequest(product="European call", free_prompt="volatility20%"))


def test_lexical_retrieval_does_not_read_the_corpus_embedding_matrix(services, monkeypatch):
    lexical = build_retriever("lexical", services.store, services.embeddings)
    monkeypatch.setattr(services.embeddings, "embed_one", lambda text: pytest.fail("Lexical mode loaded vectors"))
    hits = lexical.retrieve('call + option (risk-free) "dividend" 1%', top_k=3)
    assert hits and all(h.vector_score == 0 for h in hits)


def auth(service, subject):
    return {"Authorization": "Bearer " + mint_session_token(service.settings.auth_token_secret,
            user_id=subject, email=f"{subject}@test.invalid", expires_at=int(time.time()) + 3600)}


def test_api_library_uses_verified_owner_and_survives_a_new_api_instance(services):
    services.store.upsert_entitlement("alice@test.invalid", "starter", user_id="alice")
    services.store.upsert_entitlement("bob@test.invalid", "starter", user_id="bob")
    alice, bob = auth(services, "alice"), auth(services, "bob")
    client = TestClient(create_app(services))
    body = {"product": "European call option", "concept": "Black Scholes", "free_prompt": PROMPT,
            "client_request_id": "owned-generation-one", "number_of_questions": 5}
    created = client.post("/agent/exercise", headers=alice, json=body)
    assert created.status_code == 200, created.text
    record_id = created.json()["metadata"]["library_id"]
    assert created.json()["metadata"]["persistence"] == "account"
    assert client.get("/platform/exercises").status_code == 401
    assert client.get("/platform/exercises", headers=bob).json()["exercises"] == []
    assert client.get(f"/platform/exercises/{record_id}", headers=bob).status_code == 404
    assert client.get(f"/platform/exercises/{record_id}", headers=alice).json()["response"] == created.json()
    assert client.post("/platform/exercises", headers=bob, json=created.json()).status_code in {403, 405}
    reloaded = TestClient(create_app(services))
    records = reloaded.get("/platform/exercises", headers=alice).json()["exercises"]
    assert len(records) == 1 and records[0]["id"] == record_id
    retry = reloaded.post("/agent/exercise", headers=alice, json=body)
    assert retry.json() == created.json()
    conflict = reloaded.post("/agent/exercise", headers=alice, json={**body, "difficulty": "expert"})
    assert conflict.status_code == 409
    invalid = reloaded.post("/agent/exercise", headers=alice,
                            json={**body, "client_request_id": "bad-dividend", "free_prompt": PROMPT.replace("yield1%", "yield1")})
    assert invalid.status_code == 422
    bad_rate = reloaded.post("/agent/exercise", headers=alice,
                            json={**body, "client_request_id": "bad-rate", "free_prompt": PROMPT.replace("rate3%", "rate3")})
    assert bad_rate.status_code == 422
    assert len(reloaded.get("/platform/exercises", headers=alice).json()["exercises"]) == 1


def test_duplicate_save_is_atomic_under_concurrent_requests(services):
    store = PlatformStore(services.settings.db_path)
    body = {"client_request_id": "concurrent-one", "free_prompt": PROMPT}
    response = {"kind": "exercise", "title": "Concurrent", "content": "Real test record", "sources": [], "metadata": {}}
    with ThreadPoolExecutor(max_workers=6) as pool:
        records = list(pool.map(lambda _: store.save_exercise(user_id="alice", request=body, response=response), range(12)))
    assert len({r["id"] for r in records}) == 1
    assert len(store.list_exercises("alice")) == 1
    assert store.list_exercises("bob") == []


def test_a_writer_cannot_change_question_answer_rubric_mapping(services):
    from pricinglibrary_rag.exercise_assessment import assessment_matches_document
    result = PracticeAgent(services.generator).create_exercise(ExerciseRequest(product="option", free_prompt=PROMPT))
    assessment = result.metadata["assessment"]
    assert assessment_matches_document(result.content, assessment)
    first = assessment["questions"][0]["prompt"]
    assert not assessment_matches_document(result.content.replace(first, "Calculate a different unsupported quantity"), assessment)
    assert not assessment_matches_document(result.content.replace("### Réponse 1", "### Réponse 6"), assessment)
    assert not assessment_matches_document(result.content.replace("| 20 |", "| 25 |", 1), assessment)
