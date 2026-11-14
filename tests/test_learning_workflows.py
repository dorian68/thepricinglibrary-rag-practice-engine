from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import subprocess
import sys
import time
from types import SimpleNamespace

from fastapi.testclient import TestClient
import pytest

from pricinglibrary_rag.api import create_app
from pricinglibrary_rag.config import Settings
from pricinglibrary_rag.factory import build_services
from pricinglibrary_rag.interview_lab import _full_case
from pricinglibrary_rag.learning_workflows import BANK, NOTEBOOKS, PRACTICE_EXERCISES, PRACTICE_REFERENCES, LearningStore, run_notebook
from pricinglibrary_rag.security import mint_session_token


@pytest.fixture
def learning(tmp_path):
    secret = "learning-contract-fixture-" + "q" * 40
    settings = Settings(data_dir=tmp_path, db_path=tmp_path / "learning.sqlite3",
                        embedding_backend="local-hashing", embedding_dim=32, sentence_transformer_model=None,
                        llm_provider="template", openai_api_key=None, openai_model="unused", openai_base_url=None,
                        openai_timeout_seconds=2, openai_max_retries=0, ollama_url="http://127.0.0.1:1",
                        ollama_model="unused", transformers_model_path=None, chunk_target_chars=500,
                        chunk_overlap_chars=50, max_context_chunks=2, environment="production",
                        api_key="member-" + "a" * 40, operator_api_key="operator-" + "o" * 40,
                        auth_token_secret=secret, rate_limit_per_min=10000)
    services = build_services(settings)
    for owner, plan in [("starter", "starter"), ("student", "student"), ("other", "student")]:
        services.store.upsert_entitlement(f"{owner}@learning.test", plan, user_id=owner, status="active", source="test-fixture")
    client = TestClient(create_app(services))
    def headers(owner="student"):
        token = mint_session_token(secret, user_id=owner, email=f"{owner}@learning.test", expires_at=int(time.time()) + 1800)
        return {"Authorization": "Bearer " + token}
    return client, services, headers


def _start(client, headers, key="start-practice-001"):
    response = client.post("/learning/survival/runs", headers=headers, json={"client_request_id": key})
    assert response.status_code == 200, response.text
    return response.json()


def test_learning_requires_verified_identity_and_real_server_plan(learning):
    client, _, headers = learning
    assert client.get("/learning/catalog").status_code == 401
    assert client.get("/learning/catalog", headers=headers("free")).status_code == 200
    assert client.get("/learning/notebooks", headers=headers("free")).status_code == 403
    assert client.get("/learning/notebooks", headers=headers("starter")).status_code == 403
    response = client.get("/learning/notebooks", headers=headers())
    assert response.status_code == 200 and len(response.json()["notebooks"]) == 2
    assert response.headers["cache-control"] == "private, no-store"
    assert client.post("/learning/notebooks/black-scholes-intro/run", headers=headers(), json={"code": "arbitrary()"}).status_code == 422
    assert client.post("/learning/notebooks/unknown/run", headers=headers(), json={}).status_code == 404


def test_notebook_vanilla_matches_independent_formula_and_changes_with_ticket():
    ticket = dict(NOTEBOOKS["black-scholes-intro"]["ticket"])
    s, k, r, q, v, t = [ticket[key] for key in ("spot", "strike", "rate", "dividend_yield", "volatility", "maturity_years")]
    cdf = lambda x: .5 * (1 + math.erf(x / math.sqrt(2)))
    d1 = (math.log(s / k) + (r - q + v*v/2)*t)/(v*math.sqrt(t))
    expected = s*math.exp(-q*t)*cdf(d1) - k*math.exp(-r*t)*cdf(d1-v*math.sqrt(t))
    result = run_notebook("black-scholes-intro")
    assert result["price_per_unit"] == pytest.approx(expected, abs=1e-12)
    changed = run_notebook("black-scholes-intro", {**ticket, "spot": 120, "dividend_yield": .03})
    assert changed["ticket"]["spot"] == 120 and changed["price_per_unit"] > result["price_per_unit"]
    assert result["limits"]


def test_barrier_closed_form_matches_independent_quadrature_and_pair_mc():
    # Integrate the conditional bridge payoff against a normal density. This
    # oracle uses no reflected-call closed form from the implementation.
    s, k, h, r, v, t = 100, 100, 85, .02, .2, .5
    left, right, n = -8, 8, 16000
    step = (right-left)/n
    def f(z):
        terminal = s*math.exp((r-v*v/2)*t+v*math.sqrt(t)*z)
        if terminal <= k:
            return 0
        survival = -math.expm1(-2*math.log(s/h)*math.log(terminal/h)/(v*v*t))
        return math.exp(-r*t)*(terminal-k)*survival*math.exp(-z*z/2)/math.sqrt(2*math.pi)
    expected = step/3 * (f(left)+f(right)+sum((4 if i % 2 else 2)*f(left+i*step) for i in range(1,n)))
    result = run_notebook("barrier-down-out")
    assert result["closed_form_price"] == pytest.approx(expected, abs=1e-6)
    assert result["independent_pairs"] == 50000 and result["standard_error"] > 0
    assert result["ci95"][0] < result["closed_form_price"] < result["ci95"][1]
    assert result["ci95"][1] - result["mc_price"] == pytest.approx(1.96*result["standard_error"])
    higher_barrier = run_notebook("barrier-down-out", {**result["ticket"], "barrier": 95})
    assert higher_barrier["mc_price"] < result["mc_price"]
    assert "sampling error only" in " ".join(result["limits"])


@pytest.mark.parametrize("change", [{"paths": 200002}, {"paths": 3}, {"seed": True}, {"barrier": 101}, {"volatility": float("nan")}, {"unknown": 2}])
def test_notebook_bounds_do_not_run_unknown_or_unbounded_code(change):
    with pytest.raises(Exception) as error:
        run_notebook("barrier-down-out", {**NOTEBOOKS["barrier-down-out"]["ticket"], **change})
    assert getattr(error.value, "status_code", None) == 422


def test_exported_notebooks_are_valid_documents_and_reproduce_the_run(learning, tmp_path):
    client, _, headers = learning
    for notebook_id in NOTEBOOKS:
        result = client.post(f"/learning/notebooks/{notebook_id}/run", headers=headers(), json={}).json()
        response = client.get(f"/learning/notebooks/{notebook_id}/export?format=ipynb", headers=headers())
        document = response.json()
        assert document["nbformat"] == 4 and document["nbformat_minor"] == 5
        assert document["cells"][1]["outputs"] == []
        source = "".join(document["cells"][1]["source"])
        script = client.get(f"/learning/notebooks/{notebook_id}/export?format=py", headers=headers())
        assert script.text == source
        target = tmp_path / f"{notebook_id}.py"
        target.write_text(source, encoding="utf-8")
        process = subprocess.run([sys.executable, str(target)], capture_output=True, text=True, timeout=20, check=True)
        assert json.loads(process.stdout) == result


def test_notebook_frontend_and_backend_share_original_code_when_workspace_present():
    frontend = Path(__file__).resolve().parents[3] / "WEBSITE/thepricinglab/src/data/notebookExamples.json"
    if not frontend.exists():
        pytest.skip("Paired frontend checkout not present in standalone backend CI.")
    for item in json.loads(frontend.read_text(encoding="utf-8"))["notebooks"]:
        assert NOTEBOOKS[item["id"]] == item


def test_survival_resumes_feedback_and_has_atomic_idempotent_answers(learning):
    client, services, headers = learning
    signed = headers()
    run = _start(client, signed)
    assert "correct" not in run["question"] and "explanation" not in run["question"]
    assert _start(client, signed)["id"] == run["id"]
    url = f"/learning/survival/runs/{run['id']}"
    body = {"question_id": run["question"]["id"], "answer": BANK[0]["correct"], "client_request_id": "answer-atomic-001"}
    with ThreadPoolExecutor(max_workers=3) as pool:
        responses = list(pool.map(lambda _: client.post(url + "/answers", headers=signed, json=body), range(3)))
    assert {r.status_code for r in responses} == {200}
    first = responses[0].json()
    assert all(r.json() == first for r in responses)
    assert first["phase"] == "feedback" and first["answered_count"] == 1
    assert first["feedback"]["question_id"] == run["question"]["id"]
    assert first["feedback"]["correct"] and not first["ranked"] and not first["proctored"]
    assert client.post(url + "/answers", headers=signed, json={**body, "client_request_id": "answer-again-002"}).status_code == 409
    fresh = TestClient(create_app(build_services(services.settings)))
    assert fresh.get(url, headers=signed).json()["feedback"] == first["feedback"]
    assert fresh.get(url, headers=headers("other")).status_code == 404
    next_state = fresh.post(url + "/next", headers=signed, json={"client_request_id": "next-question-001"}).json()
    assert next_state["index"] == 1 and next_state["phase"] == "answer" and next_state["remaining_seconds"] <= 30


def test_survival_deadline_is_server_owned_and_reloading_does_not_reset_it(learning):
    client, services, headers = learning
    signed = headers(); run = _start(client, signed)
    store = LearningStore(services.settings.db_path)
    with store.connect() as db:
        row, state = store.survival_row(db, "student", run["id"])
        state["question_started_at"] -= 31
        db.execute("UPDATE learning_survival SET state=? WHERE id=?", (json.dumps(state), row["id"]))
    url = f"/learning/survival/runs/{run['id']}"
    assert client.get(url, headers=signed).json()["remaining_seconds"] == 0
    response = client.post(url + "/answers", headers=signed, json={"question_id": BANK[0]["id"], "answer": BANK[0]["correct"], "client_request_id": "late-correct-001"}).json()
    assert response["feedback"]["selected"] == "timeout" and response["lives"] == 2 and response["score"] == 0
    assert response["phase"] == "feedback"


def test_survival_twenty_question_run_has_reproducible_rules_and_private_history(learning, monkeypatch):
    import pricinglibrary_rag.learning_workflows as module
    monkeypatch.setattr(module, "time", SimpleNamespace(time=lambda: 1800000000.0))
    client, _, headers = learning; signed = headers(); run = _start(client, signed)
    url = f"/learning/survival/runs/{run['id']}"
    for index, question in enumerate(BANK):
        answer = client.post(url + "/answers", headers=signed, json={"question_id": question["id"], "answer": question["correct"], "client_request_id": f"correct-answer-{index:02d}"})
        assert answer.status_code == 200
        assert answer.json()["feedback"]["question_id"] == question["id"]
        run = client.post(url + "/next", headers=signed, json={"client_request_id": f"next-question-{index:02d}"}).json()
    assert run["completed"] and run["score"] == 7200 and run["best_streak"] == 20
    assert run["answered_count"] == 20 and run["lives"] == 3 and not run["ranked"]
    assert client.get("/learning/survival/runs", headers=signed).json()["runs"][0]["id"] == run["id"]
    assert client.get("/learning/survival/runs", headers=headers("other")).json()["runs"] == []
    assert client.get("/platform/progress/student", headers=signed).json()["events"] == 1


def test_survival_three_lives_end_only_after_reviewing_last_feedback(learning):
    client, _, headers = learning; signed = headers(); run = _start(client, signed)
    url = f"/learning/survival/runs/{run['id']}"
    for index, question in enumerate(BANK[:3]):
        wrong = next(key for key, _ in question["options"] if key != question["correct"])
        run = client.post(url + "/answers", headers=signed, json={"question_id": question["id"], "answer": wrong, "client_request_id": f"wrong-answer-{index}"}).json()
        assert run["phase"] == "feedback" and run["feedback"]["question_id"] == question["id"]
        run = client.post(url + "/next", headers=signed, json={"client_request_id": f"wrong-next-{index}"}).json()
    assert run["completed"] and run["score"] == 0 and run["lives"] == 0 and run["answered_count"] == 3


def test_generated_exercise_attempts_preserve_written_work_without_fake_automatic_grade(learning):
    client, _, headers = learning; signed = headers("starter")
    generated = client.post("/agent/exercise", headers=signed, json={"topic": "Black-Scholes", "language": "en", "number_of_questions": 3,
                           "free_prompt": "Price a European call with S=100 K=100 r=5% sigma=20% T=1 year", "client_request_id": "original-generator-001"})
    assert generated.status_code == 200, generated.text
    exercise_id = generated.json()["metadata"]["library_id"]
    base = f"/learning/exercises/{exercise_id}"
    task = client.get(base + "/task", headers=signed).json()
    assert len(task["questions"]) == 3 and "## Verified solution" not in task["brief"]
    assert all("answer" not in q for q in task["questions"])
    body = {"answers": {"1": "I identify the European call and use matching spot and strike units.", "2": "I calculate the premium with continuous rates and constant volatility.", "3": "I would hedge delta and monitor model assumptions."},
            "reasoning": "Private written reasoning.", "client_request_id": "written-attempt-001"}
    response = client.post(base + "/attempts", headers=signed, json=body)
    assert response.status_code == 200, response.text
    attempt = response.json()
    assert attempt["automatic_grade"] is None and not attempt["independence_verified"]
    assert len(attempt["feedback"]["questions"]) == 3 and attempt["answers"] == body["answers"]
    assert client.post(base + "/attempts", headers=signed, json=body).json() == attempt
    assert client.post(base + "/attempts", headers=signed, json={**body, "reasoning": "changed"}).status_code == 409
    assert client.get(base + "/task", headers=headers("other")).status_code == 404
    attempt_url = f"/learning/exercise-attempts/{attempt['id']}"
    assert client.get(attempt_url, headers=headers("other")).status_code == 404
    review = {"criteria": {"1": True, "2": False, "3": True}, "notes": "Review the discount factor.", "client_request_id": "written-review-001"}
    assert client.post(attempt_url + "/review", headers=signed, json=review).status_code == 200
    assert client.post(attempt_url + "/review", headers=signed, json=review).status_code == 200
    resumed = client.get(attempt_url, headers=signed).json()
    assert resumed["answers"] == body["answers"] and len(resumed["self_reviews"]) == 1
    exported = client.get(attempt_url + "/export", headers=signed)
    assert exported.json() == resumed and exported.headers["cache-control"] == "private, no-store"
    assert len(client.get(base + "/attempts", headers=signed).json()["attempts"]) == 1


@pytest.mark.parametrize("exercise_id", list(PRACTICE_EXERCISES))
def test_all_authored_practice_tasks_have_private_attempt_and_review_contract(learning, exercise_id):
    client, _, headers = learning; signed = headers("starter")
    catalog = client.get("/learning/catalog", headers=signed).json()
    assert exercise_id in {item["id"] for item in catalog["practice_exercises"]}
    task = client.get(f"/learning/exercises/{exercise_id}/task", headers=signed)
    assert task.status_code == 200 and task.json()["questions"]
    assert "## Python starter" in task.json()["brief"]
    original = PRACTICE_EXERCISES[exercise_id]
    assert original["objective"] in task.json()["brief"]
    answers = {str(q["number"]): "My written response to the original task." for q in task.json()["questions"]}
    response = client.post(f"/learning/exercises/{exercise_id}/attempts", headers=signed,
                           json={"answers": answers, "client_request_id": f"canonical-{exercise_id}-answer"})
    assert response.status_code == 200, response.text
    attempt = response.json()
    assert attempt["automatic_grade"] is None and attempt["feedback"]["original_rubric"] == original["grading"]
    assert PRACTICE_REFERENCES[exercise_id]["output"] in attempt["feedback"]["questions"][0]["answer"]
    assert attempt["feedback"]["reference"]["ticket"] == PRACTICE_REFERENCES[exercise_id]["ticket"]
    assert client.get(f"/learning/exercises/{exercise_id}/attempts", headers=headers("other")).json()["attempts"] == []


def test_executable_references_use_reviewed_tickets_and_never_execute_uploaded_code(learning):
    client, _, headers = learning; signed = headers("starter")
    url = "/learning/exercises/iv-newton/reference"
    reference = client.get(url, headers=signed).json()
    result = client.post(url + "/run", headers=signed, json={})
    assert result.status_code == 200 and result.json()["result"] == reference["result"]
    assert client.post(url + "/run", headers=signed, json={"code": "print('not allowed')"}).status_code == 422
    assert client.get(url, headers=headers("free")).status_code == 403
    assert client.get("/learning/exercises/not-a-reference/reference", headers=signed).status_code == 404
    script = client.get(url + "/export?format=python", headers=signed)
    assert script.status_code == 200 and script.text == reference["solution"]
    assert script.headers["cache-control"] == "private, no-store"


def test_private_portable_interview_exports_use_real_attempt_and_original_cards(learning):
    client, _, headers = learning; signed = headers("free")
    case = _full_case("call-quote", "primary")
    submitted = {"case_id": "call-quote", "variant": "primary", "client_request_id": "portable-attempt-001",
                 "answers": {q["id"]: q["expected"] for q in case["questions"]}, "reasoning": "This private reasoning should be omitted from portable reports."}
    assert client.post("/interview/attempts", headers=signed, json=submitted).status_code == 200
    report = client.get("/learning/interview/export?format=report", headers=signed)
    assert report.status_code == 200 and "within tolerance" in report.text
    assert "private reasoning should" not in report.text and "free@learning" not in report.text
    assert client.get("/learning/interview/export?format=csv", headers=signed).text.count("call-quote") == 2
    deck = client.get("/learning/interview/export?format=anki", headers=signed)
    assert deck.status_code == 200 and "TPL::PricingAndGreeks" in deck.text and "10.4506" in deck.text
    assert "dividend-parity" not in deck.text and "quote-memo" not in deck.text
    assert client.get("/learning/interview/export?format=anki", headers=headers("other")).status_code == 409
    assert client.get("/learning/interview/export?format=report", headers=headers("other")).text.find("No submitted attempt") >= 0
    calendar = client.post("/learning/interview/calendar", headers=signed, json={"starts_at": "2026-11-16T18:00:00+01:00", "minutes": 30, "sessions": 2})
    assert calendar.status_code == 200 and calendar.text.count("BEGIN:VEVENT") == 2
    assert "DTSTART:20261116T170000Z" in calendar.text and "DTEND:20261116T173000Z" in calendar.text
    assert "free@learning" not in calendar.text and "Not a record of attendance" in calendar.text
    assert client.post("/learning/interview/calendar", headers=signed, json={"starts_at": "2026-11-16T18:00:00"}).status_code == 422
