from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
import math
import json
from pathlib import Path
import sqlite3
import time
from urllib.parse import parse_qs, urlparse

from fastapi.testclient import TestClient
import pytest

from pricinglibrary_rag.api import create_app
from pricinglibrary_rag.config import Settings
from pricinglibrary_rag.factory import build_services
from pricinglibrary_rag.interview_lab import CASE_IDS, _full_case, case_task
from pricinglibrary_rag.security import mint_session_token


SECRET="interview-identity-test-"+"s"*40
REASONING="I used the European option model with continuous rates and checked the position sign. The result depends on constant volatility and excludes trading costs."


@pytest.fixture
def lab(tmp_path):
    settings=Settings(
        data_dir=tmp_path,db_path=tmp_path/"interview.sqlite3",embedding_backend="local-hashing",embedding_dim=32,
        sentence_transformer_model=None,llm_provider="template",openai_api_key=None,openai_model="unused",
        openai_base_url=None,openai_timeout_seconds=5,openai_max_retries=0,ollama_url="http://127.0.0.1:1",
        ollama_model="unused",transformers_model_path=None,chunk_target_chars=500,chunk_overlap_chars=50,max_context_chunks=2,
        environment="production",api_key="member-"+"m"*40,operator_api_key="operator-"+"o"*40,
        auth_token_secret=SECRET,rate_limit_per_min=10000,source_rights_cleared=False)
    services=build_services(settings)
    client=TestClient(create_app(services))
    def headers(user="alice"):
        token=mint_session_token(SECRET,user_id=user,email=f"{user}@interview.test",expires_at=int(time.time())+600)
        return {"Authorization":"Bearer "+token}
    return client,services,headers


def _oracle(ticket):
    s,k,t,r,q,v=[ticket[x] for x in ("spot","strike","maturityYears","riskFreeRate","dividendYield","volatility")]
    d1=(math.log(s/k)+(r-q+v*v/2)*t)/(v*math.sqrt(t)); d2=d1-v*math.sqrt(t)
    cdf=lambda x:0.5*(1+math.erf(x/math.sqrt(2)))
    pdf=math.exp(-d1*d1/2)/math.sqrt(2*math.pi)
    c=s*math.exp(-q*t)*cdf(d1)-k*math.exp(-r*t)*cdf(d2)
    p=k*math.exp(-r*t)*cdf(-d2)-s*math.exp(-q*t)*cdf(-d1)
    delta=math.exp(-q*t)*(cdf(d1) if ticket["optionType"]=="call" else cdf(d1)-1)
    return {"price":c if ticket["optionType"]=="call" else p,"call":c,"put":p,"delta":delta,
            "gamma":math.exp(-q*t)*pdf/(s*v*math.sqrt(t)),"vega":s*math.exp(-q*t)*pdf*math.sqrt(t)/100}


def _answers(case_id,variant="primary"):
    full=_full_case(case_id,variant)
    return {q["id"]:q["expected"] for q in full["questions"]}


def _body(case_id="call-quote",variant="primary",request_id="request-0001"):
    return {"case_id":case_id,"variant":variant,"answers":_answers(case_id,variant),
            "reasoning":REASONING,"client_request_id":request_id}


@pytest.mark.parametrize("case_id",CASE_IDS)
@pytest.mark.parametrize("variant",["primary","transfer"])
def test_all_twelve_tasks_have_independent_numeric_oracles(case_id,variant):
    full=_full_case(case_id,variant); t=full["ticket"]; o=_oracle(t); transfer=variant=="transfer"
    scale=(-1 if t["position"]=="short" else 1)*t["quantity"]*t["multiplier"]
    if case_id=="call-quote": expected={"price":o["price"],"delta":o["delta"]}
    elif case_id=="dividend-parity":
        zero=_oracle({**t,"dividendYield":0})
        expected=({"put_price":zero["put"],"call_change":zero["call"]-o["call"]} if transfer
                  else {"put_price":o["put"],"call_minus_put":o["call"]-o["put"]})
    elif case_id=="delta-hedge":expected={"option_delta":o["delta"],"hedge_shares":-scale*o["delta"]}
    elif case_id=="gamma-vega":
        g=0.5*scale*o["gamma"]*25; v=scale*o["vega"]*(-2 if transfer else 2)
        expected={"gamma_pnl":g,"vega_pnl":v,"hedged_pnl":g+v}
    elif case_id=="time-rates":
        expected={"time_pnl":_oracle({**t,"maturityYears":t["maturityYears"]-30/365})["price"]-o["price"],
                  "rate_pnl":_oracle({**t,"riskFreeRate":t["riskFreeRate"]+0.01})["price"]-o["price"]}
    else:
        hedge=-scale*o["delta"]
        expected={"premium":-scale*o["price"],"hedge_shares":hedge,
                  "stress_pnl":scale*(_oracle({**t,"spot":t["spot"]*1.1,"volatility":t["volatility"]+0.05})["price"]-o["price"])+hedge*t["spot"]*0.1}
    for q in full["questions"]:
        assert q["expected"]==pytest.approx(expected[q["id"]],abs=max(1e-5,q["tolerance_abs"]*0.002))
    task=case_task(case_id,variant)
    assert "worked_solution" not in task
    assert all("expected" not in q and "explanation" not in q for q in task["questions"])
    query=parse_qs(urlparse(task["tool_url"]).query)
    assert float(query["spot"][0])==t["spot"]
    assert float(query["volatility"][0])==100*t["volatility"]
    assert float(query["maturityDays"][0])==365*t["maturityYears"]


def test_public_catalog_and_real_preview_without_answer_or_identity_leak(lab):
    client,services,headers=lab
    catalog=client.get("/interview/catalog")
    assert catalog.status_code==200
    assert len(catalog.json()["cases"])==6
    task=client.get("/interview/cases/call-quote").json()
    assert all("expected" not in q for q in task["questions"])
    assert client.get("/interview/cases/dividend-parity").status_code==401
    assert client.get("/interview/state").status_code==401
    preview=client.post("/interview/preview/check",json=_body()).json()["attempt"]
    assert preview["numerical_pass"] and not preview["persisted"] and not preview["independent"]
    assert client.post("/interview/preview/check",json=_body("delta-hedge")).status_code==403
    assert client.get("/interview/state",headers=headers()).json()["attempts"]==[]


def test_dashboard_projects_interview_without_fabricated_legacy_scores_or_private_answers(lab):
    client, services, headers = lab
    signed = headers()
    before = client.get("/platform/progress/alice", headers=signed)
    assert before.status_code == 200
    assert before.json()["interview"]["attempt_count"] == 0
    with sqlite3.connect(services.settings.db_path) as db:
        assert db.execute("SELECT COUNT(*) FROM interview_profiles").fetchone()[0] == 0
    first = client.post("/interview/attempts", json=_body(), headers=signed).json()["attempt"]
    client.post("/interview/attempts", json=_body(request_id="dashboard-retry-001"), headers=signed)
    review = {"criteria": {"assumptions": True, "decision": True, "limitations": False},
              "notes": "Private reasoning must not appear in the dashboard DTO.",
              "client_request_id": "dashboard-review-001"}
    assert client.post(f"/interview/attempts/{first['id']}/review", json=review, headers=signed).status_code == 200
    dashboard = client.get("/platform/progress/alice", headers=signed).json()
    summary = dashboard["interview"]
    assert dashboard["events"] == 0 and dashboard["avg_score"] is None
    assert summary["attempt_count"] == 2 and summary["case_count"] == 1
    assert summary["numerical_pass_count"] == summary["independent_check_count"] == 1
    assert summary["reasoning_review_count"] == 1 and summary["last_activity_at"]
    assert summary["resume"] == {"case_id": "call-quote", "variant": "primary", "phase": "feedback",
                                 "path": "/interview/call-quote?variant=primary"}
    assert not summary["certified_mastery"]
    assert "Private reasoning" not in json.dumps(dashboard) and REASONING not in json.dumps(dashboard)
    assert client.get("/platform/progress/alice", headers=headers("bob")).status_code == 403
    assert client.get("/platform/progress/bob", headers=headers("bob")).json()["interview"]["attempt_count"] == 0


def test_dashboard_does_not_turn_corrected_retry_into_independent_success(lab):
    client, _, headers = lab
    signed = headers()
    body = _body()
    body["answers"]["delta"] = 0
    client.post("/interview/attempts", json=body, headers=signed)
    client.post("/interview/attempts", json=_body(request_id="dashboard-corrected-retry"), headers=signed)
    client.post("/interview/attempts", json=_body(variant="transfer", request_id="dashboard-put-transfer"), headers=signed)
    summary = client.get("/platform/progress/alice", headers=signed).json()["interview"]
    assert summary["attempt_count"] == 3 and summary["case_count"] == 1
    assert summary["numerical_pass_count"] == 2 and summary["independent_check_count"] == 1
    assert summary["resume"]["variant"] == "transfer"


def test_legacy_platform_only_progress_read_does_not_create_interview_records(tmp_path):
    from pricinglibrary_rag.platform_store import PlatformStore

    store = PlatformStore(tmp_path / "legacy.sqlite3")
    result = store.progress_summary("legacy-owner")
    assert result["interview"]["event_count"] == 0 and result["interview"]["resume"] is None
    with sqlite3.connect(store.db_path) as db:
        assert db.execute("SELECT COUNT(*) FROM sqlite_master WHERE name='interview_profiles'").fetchone()[0] == 0


def test_signed_pilot_does_not_require_paid_plan_but_paid_courses_remain_closed(lab):
    client,services,headers=lab
    assert client.get("/interview/cases/quote-memo",headers=headers()).status_code==200
    assert client.get("/courses/greeks/script",headers=headers()).status_code==403
    assert client.get("/interview/state",headers={"X-API-Key":services.settings.api_key}).status_code==401
    assert client.post("/interview/attempts",json=_body(),headers={"X-API-Key":services.settings.operator_api_key}).status_code==401


def test_attempts_persist_originals_and_different_accounts_cannot_review_them(lab):
    client,services,headers=lab
    signed=headers()
    response=client.post("/interview/attempts",json=_body(),headers=signed)
    assert response.status_code==200
    first=response.json()["attempt"]
    assert first["numerical_pass"] and first["independent"] and not first["reasoning_reviewed"]
    retry=client.post("/interview/attempts",json=_body(request_id="request-0002"),headers=signed).json()["attempt"]
    assert not retry["independent"]
    review={"criteria":{"assumptions":True,"decision":True,"limitations":False},"notes":"Need to explain skew.","client_request_id":"review-request-001"}
    assert client.post(f"/interview/attempts/{first['id']}/review",json=review,headers=headers("bob")).status_code==404
    assert client.post(f"/interview/attempts/{first['id']}/review",json=review,headers=signed).json()["review"]["reasoning_reviewed"]
    fresh=TestClient(create_app(build_services(services.settings)))
    state=fresh.get("/interview/state",headers=headers()).json()
    assert len(state["attempts"])==2 and state["attempts"][0]["reasoning"]==REASONING
    assert state["metrics"]["numerical_passes"]==1 and state["metrics"]["reasoning_reviews"]==1
    assert state["attempts"][0]["task_snapshot"]["ticket"]["optionType"]=="call"
    assert state["attempts"][0]["schema_version"]=="tpl.interview-lab.v1"
    assert not state["metrics"]["certified_mastery"]
    assert fresh.get("/interview/state",headers=headers("bob")).json()["attempts"]==[]
    export=fresh.get("/interview/export",headers=headers())
    assert export.headers["cache-control"]=="private, no-store"
    assert export.json()["attempts"][0]["answers"]==first["answers"]


def test_reveal_and_incorrect_first_attempt_cannot_be_laundered_into_independent_pass(lab):
    client,_,headers=lab
    signed=headers()
    body=_body();body["answers"]["delta"]=0
    first=client.post("/interview/attempts",json=body,headers=signed).json()["attempt"]
    assert not first["numerical_pass"]
    assert not client.post("/interview/attempts",json=_body(request_id="correct-retry"),headers=signed).json()["attempt"]["independent"]
    reveal={"case_id":"delta-hedge","variant":"primary","client_request_id":"reveal-request"}
    assert client.post("/interview/reveal",json=reveal,headers=signed).status_code==200
    after=client.post("/interview/attempts",json=_body("delta-hedge",request_id="revealed-attempt"),headers=signed).json()["attempt"]
    assert not after["independent"]
    assert client.get("/interview/state",headers=signed).json()["metrics"]["numerical_passes"]==0


def test_transfer_is_a_conceptual_change_and_retains_separate_evidence(lab):
    client,_,headers=lab
    signed=headers()
    primary=client.get("/interview/cases/call-quote").json()
    transfer=client.get("/interview/cases/call-quote?variant=transfer").json()
    assert primary["ticket"]["optionType"]=="call" and transfer["ticket"]["optionType"]=="put"
    assert primary["ticket"]["spot"]==transfer["ticket"]["spot"]
    client.post("/interview/attempts",json=_body(),headers=signed)
    check=client.post("/interview/attempts",json=_body(variant="transfer",request_id="transfer-request"),headers=signed).json()["attempt"]
    assert check["independent"] and check["numerical_pass"]
    state=client.get("/interview/state",headers=signed).json()
    assert state["metrics"]["transfer_passes"]==1 and state["metrics"]["numerical_passes"]==1
    assert state["next_task"]=={"case_id":"dividend-parity","variant":"primary"}


def test_double_submit_is_transactional_and_conflicting_request_is_rejected(lab):
    client,_,headers=lab;signed=headers();body=_body()
    with ThreadPoolExecutor(max_workers=3) as pool:
        results=list(pool.map(lambda _:client.post("/interview/attempts",json=body,headers=signed),range(3)))
    assert {r.status_code for r in results}=={200}
    assert len({r.json()["attempt"]["id"] for r in results})==1
    body["answers"]["delta"]=0
    assert client.post("/interview/attempts",json=body,headers=signed).status_code==409
    assert len(client.get("/interview/state",headers=signed).json()["attempts"])==1


def test_review_request_id_is_bound_to_the_attempt_url(lab):
    client,_,headers=lab;signed=headers()
    first=client.post("/interview/attempts",json=_body(),headers=signed).json()["attempt"]
    second=client.post("/interview/attempts",json=_body(variant="transfer",request_id="transfer-request"),headers=signed).json()["attempt"]
    review={"criteria":{"assumptions":True,"decision":True,"limitations":False},"client_request_id":"same-review-request"}
    first_url=f"/interview/attempts/{first['id']}/review"
    assert client.post(first_url,json=review,headers=signed).status_code==200
    assert client.post(first_url,json=review,headers=signed).status_code==200
    assert client.post(f"/interview/attempts/{second['id']}/review",json=review,headers=signed).status_code==409


def test_anonymous_check_is_rate_limited_and_never_unlocks_an_account(lab):
    _,services,headers=lab
    settings=replace(services.settings,rate_limit_per_min=1)
    client=TestClient(create_app(build_services(settings)))
    assert client.post("/interview/preview/check",json=_body()).status_code==200
    limited=client.post("/interview/preview/check",json=_body(request_id="second-preview"))
    assert limited.status_code==429 and "retry-after" in limited.headers
    assert client.get("/interview/state",headers=headers()).json()["attempts"]==[]


def test_transfer_before_primary_is_practice_and_cannot_be_relabelled(lab):
    client,_,headers=lab;signed=headers()
    premature=client.post("/interview/attempts",json=_body(variant="transfer"),headers=signed).json()["attempt"]
    assert premature["numerical_pass"] and not premature["independent"]
    client.post("/interview/attempts",json=_body(request_id="primary-after-transfer"),headers=signed)
    retry=client.post("/interview/attempts",json=_body(variant="transfer",request_id="transfer-after-primary"),headers=signed).json()["attempt"]
    assert not retry["independent"]
    assert client.get("/interview/state",headers=signed).json()["metrics"]["transfer_passes"]==0


@pytest.mark.parametrize("mutation",[
    {"reasoning":" "*100}, {"reasoning":"short"}, {"answers":{"price":10.45}},
    {"answers":{"price":"10.45","delta":0.63}}, {"answers":{"price":True,"delta":0.63}},
    {"variant":"unknown"},{"user_id":"bob"},{"client_request_id":"bad/../key"},
])
def test_strict_validation_rejects_incomplete_or_forged_attempts(lab,mutation):
    client,_,headers=lab
    assert client.post("/interview/attempts",json={**_body(),**mutation},headers=headers()).status_code==422


def test_onboarding_resume_and_bounded_active_time(lab):
    client,services,headers=lab;signed=headers()
    profile={"role":"structuring","deadline":"2026-12-10","minutes_per_session":30}
    saved=client.post("/interview/onboarding",json=profile,headers=signed)
    assert saved.status_code==200
    session={"case_id":"gamma-vega","variant":"transfer","active_seconds":300,"client_request_id":"session-request"}
    result=client.post("/interview/session",json=session,headers=signed).json()
    assert result["credited_active_seconds"]<5
    state=client.get("/interview/state",headers=signed).json()
    assert state["current_task"]=={"case_id":"gamma-vega","variant":"transfer"}
    assert state["onboarding"]["role"]=="structuring" and len(state["attempts"])==0
    assert client.post("/interview/session",json={**session,"active_seconds":301,"client_request_id":"session-too-long"},headers=signed).status_code==422
    with sqlite3.connect(services.settings.db_path) as db:
        db.execute("UPDATE interview_profiles SET last_seen=? WHERE owner_id='alice'",(time.time()-22,))
    assert client.post("/interview/session",json={**session,"client_request_id":"session-second"},headers=signed).json()["credited_active_seconds"]==22
    assert client.post("/interview/session",json={**session,"client_request_id":"session-second"},headers=signed).json()["credited_active_seconds"]==22
    assert client.get("/interview/state",headers=signed).json()["metrics"]["active_seconds"]<30


def test_course_position_is_owner_owned_entitled_and_never_completion(lab):
    client,services,headers=lab;signed=headers()
    route="/platform/courses/black-scholes/position"
    assert client.put(route,json={"module_index":1}).status_code==401
    assert client.put(route,json={"module_index":1},headers=signed).status_code==200
    assert client.put(route,json={"module_index":2},headers=signed).status_code==403
    services.store.upsert_entitlement("alice@interview.test","starter",user_id="alice",status="active",source="test")
    assert client.put(route,json={"module_index":5},headers=signed).json()["position"]["module_index"]==5
    assert client.put(route,json={"module_index":8},headers=signed).status_code==422
    assert client.put(route,json={"module_index":False},headers=signed).status_code==422
    assert client.put(route,json={"module_index":2,"user_id":"bob"},headers=signed).status_code==422
    state=client.get("/platform/progress/alice",headers=signed).json()
    assert state["course_positions"][0]["module_index"]==5
    assert state["events"]==0 and state["completed_lessons"]==[] and state["courses"]==[]
    assert client.get("/platform/progress/bob",headers=signed).status_code==403
    assert client.get("/platform/progress/bob",headers=headers("bob")).json()["course_positions"]==[]


def test_pilot_metrics_requires_verified_operator_even_in_relaxed_local_mode(lab):
    client,services,headers=lab
    url="/interview/pilot/metrics"
    assert client.get(url).status_code==401
    assert client.get(url,headers=headers()).status_code==403
    assert client.get(url,headers={"X-API-Key":services.settings.api_key}).status_code==403
    operator={"X-API-Key":services.settings.operator_api_key}
    response=client.get(url,headers=operator)
    assert response.status_code==200 and response.json()["learners_seen"]==0
    assert response.headers["cache-control"]=="private, no-store"
    signed=mint_session_token(SECRET,user_id="operator-test",email="operator@interview.test",role="operator",expires_at=int(time.time())+600)
    assert client.get(url,headers={"Authorization":"Bearer "+signed}).status_code==200
    relaxed=replace(services.settings,environment="development",api_key=None,operator_api_key=None,auth_token_secret=None)
    local_client=TestClient(create_app(build_services(relaxed)))
    assert local_client.get(url).status_code==403
    local_signed=replace(services.settings,environment="local")
    local_client=TestClient(create_app(build_services(local_signed)))
    local=local_client.get(url,headers=operator).json()
    assert local["environment"]=="local" and "Local/test activity" in local["scope_notice"]


def test_pilot_metrics_aggregate_events_without_private_text_or_retry_inflation(lab):
    client,services,headers=lab
    url="/interview/pilot/metrics"
    # Four accounts opened saved state; only three submitted a primary attempt.
    for user in ("alice","bob","carol","viewer"):
        client.get("/interview/state",headers=headers(user))
    alice=headers("alice");bob=headers("bob");carol=headers("carol")
    original=_body();original["reasoning"]+=" PRIVATE_MEMO_NOT_TO_EXPORT_12345"
    primary=client.post("/interview/attempts",json=original,headers=alice).json()["attempt"]
    client.post("/interview/attempts",json=_body(variant="transfer",request_id="alice-transfer"),headers=alice)
    client.post("/interview/attempts",json=_body(request_id="alice-retry-later"),headers=alice)
    wrong=_body();wrong["answers"]["delta"]=0
    client.post("/interview/attempts",json=wrong,headers=bob)
    client.post("/interview/attempts",json=_body(request_id="bob-correct-retry"),headers=bob)
    client.post("/interview/attempts",json=_body(variant="transfer"),headers=carol)
    client.post("/interview/attempts",json=_body(request_id="carol-primary"),headers=carol)
    for i in range(2):
        review={"criteria":{"assumptions":True,"decision":True,"limitations":False},
                "notes":"PRIVATE_NOTES_NOT_TO_EXPORT_12345","client_request_id":f"alice-review-{i}"}
        client.post(f"/interview/attempts/{primary['id']}/review",json=review,headers=alice)
    # Fixtures represent genuine event timestamps on two UTC dates, not a mocked counter.
    with sqlite3.connect(services.settings.db_path) as db:
        db.execute("UPDATE interview_events SET created_at='2026-11-13T12:00:00+00:00' WHERE owner_id='alice' AND kind='attempt'")
        db.execute("UPDATE interview_events SET created_at='2026-11-12T12:00:00+00:00' WHERE id=?",(primary["id"],))
        db.execute("UPDATE interview_profiles SET active_seconds=37 WHERE owner_id='alice'")
    result=client.get(url,headers={"X-API-Key":services.settings.operator_api_key})
    assert result.status_code==200
    metrics=result.json()
    assert metrics["learners_seen"]==4 and metrics["activated_learners"]==3
    assert metrics["transfer_attempted_learners"]==2 and metrics["transfer_passed_learners"]==1
    assert metrics["returned_on_later_day"]==1
    assert metrics["per_case"][0]=={"case_id":"call-quote","learners_attempted":3,"first_attempts_passed":2,"transfer_attempted":2,"transfer_passed":1}
    assert len(metrics["per_case"])==6 and metrics["per_case"][1]["learners_attempted"]==0
    assert metrics["totals"]=={"attempts":7,"primary_attempts":5,"transfer_attempts":2,
                               "independent_primary_passes":2,"independent_transfer_passes":1,
                               "reasoning_self_reviews":1,"reported_active_seconds":37}
    text=json.dumps(metrics)
    assert all(private not in text for private in ("alice","bob","carol","viewer","@interview.test","PRIVATE_MEMO","PRIVATE_NOTES","owner_id","\"answers\""))


def test_local_signed_learner_entitlement_flag_preserves_admin_and_real_grants(lab,tmp_path):
    _,services,headers=lab
    scripts=tmp_path/"private-lessons";scripts.mkdir()
    (scripts/"options-book-greeks-pnl.md").write_text("# Test-owned Greek lesson\n\nThis fixture is original test content, not a corpus excerpt.\n",encoding="utf-8")
    settings=replace(services.settings,environment="local",enforce_entitlements=True,course_scripts_dir=scripts)
    local_services=build_services(settings)
    client=TestClient(create_app(local_services))
    signed=headers()
    assert client.get("/courses/greeks/script",headers=signed).status_code==403
    assert client.put("/platform/courses/greeks/position",json={"module_index":1},headers=signed).status_code==403
    assert client.get("/interview/cases/quote-memo",headers=signed).status_code==200
    local_services.store.upsert_entitlement("alice@interview.test","starter",user_id="alice",status="active",source="test")
    assert client.get("/courses/greeks/script",headers=signed).status_code==200
    assert client.put("/platform/courses/greeks/position",json={"module_index":1},headers=signed).status_code==200
    operator=mint_session_token(SECRET,user_id="local-admin",email="admin@interview.test",role="operator",expires_at=int(time.time())+600)
    assert client.get("/courses/greeks/script",headers={"Authorization":"Bearer "+operator}).status_code==200
    assert client.get("/health").json()["security"]["entitlements_enforced"] is True


def test_local_entitlement_flag_is_explicit_and_parsed_from_environment(monkeypatch,tmp_path):
    from pricinglibrary_rag import config
    monkeypatch.setattr(config,"_load_env_file",lambda:None)
    monkeypatch.setenv("TPL_ENVIRONMENT","local")
    monkeypatch.setenv("TPL_DATA_DIR",str(tmp_path))
    monkeypatch.setenv("TPL_DB_PATH",str(tmp_path/"settings.sqlite3"))
    monkeypatch.delenv("TPL_ENFORCE_ENTITLEMENTS",raising=False)
    assert Settings.from_env().enforce_entitlements is False
    monkeypatch.setenv("TPL_ENFORCE_ENTITLEMENTS","true")
    settings=Settings.from_env()
    assert settings.enforce_entitlements is True and settings.environment=="local" and not settings.security_enforced
