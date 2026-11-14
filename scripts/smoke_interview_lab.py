"""Actual API journey for the English pilot; no corpus, provider or payment call.

Run from the backend: python scripts/smoke_interview_lab.py [--output report.json]
The isolated signed learners are test identities, not production user grants.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tempfile
import time

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient
from pricinglibrary_rag.api import create_app
from pricinglibrary_rag.config import Settings
from pricinglibrary_rag.factory import build_services
from pricinglibrary_rag.security import mint_session_token


def run() -> dict:
    root=Path(__file__).resolve().parents[1]
    scratch=root/".pytest_tmp_interview_smoke"
    scratch.mkdir(exist_ok=True)
    checks=[]
    def check(name,condition):
        if not condition:
            raise AssertionError(name)
        checks.append({"check":name,"status":"PASS"})
    secret="isolated-smoke-identity-"+"s"*40
    with tempfile.TemporaryDirectory(dir=scratch) as temp:
        data=Path(temp)
        settings=Settings(data_dir=data,db_path=data/"smoke.sqlite3",embedding_backend="local-hashing",embedding_dim=32,
            sentence_transformer_model=None,llm_provider="template",openai_api_key=None,openai_model="unused",
            openai_base_url=None,openai_timeout_seconds=5,openai_max_retries=0,ollama_url="http://127.0.0.1:1",
            ollama_model="unused",transformers_model_path=None,chunk_target_chars=500,chunk_overlap_chars=50,max_context_chunks=2,
            environment="production",api_key="smoke-member-"+"m"*40,operator_api_key="smoke-operator-"+"o"*40,
            auth_token_secret=secret,rate_limit_per_min=1000,source_rights_cleared=False)
        def identity(user):
            token=mint_session_token(secret,user_id=user,email=user+"@smoke.test",expires_at=int(time.time())+600)
            return {"Authorization":"Bearer "+token}
        alice=identity("pilot-alice");bob=identity("pilot-bob")
        with TestClient(create_app(build_services(settings))) as client:
            cat=client.get("/interview/catalog").json()
            check("six English authored cases",cat["language"]=="en" and len(cat["cases"])==6)
            public=client.get("/interview/cases/call-quote").json()
            check("task has no solution or reference answers","worked_solution" not in public and all("expected" not in q for q in public["questions"]))
            check("account state requires signed identity",client.get("/interview/state").status_code==401)
            body={"case_id":"call-quote","variant":"primary","answers":{"price":10.4506,"delta":0.63683},
                  "reasoning":"I used European exercise with continuous rates and zero dividends. A long call has positive delta; model values omit spread and execution costs.",
                  "client_request_id":"smoke-attempt-01"}
            preview=client.post("/interview/preview/check",json=body).json()["attempt"]
            check("anonymous preview genuinely checks numbers without saving",preview["numerical_pass"] and not preview["persisted"] and not preview["independent"])
            check("signed pilot usable without a paid-course grant",client.get("/interview/cases/quote-memo",headers=alice).status_code==200)
            check("paid courses remain entitlement-protected",client.get("/courses/greeks/script",headers=alice).status_code==403)
            onboard=client.post("/interview/onboarding",headers=alice,json={"role":"structuring","minutes_per_session":30,"deadline":None})
            check("onboarding produces a bounded session",onboard.status_code==200 and onboard.json()["onboarding"]["suggested_session"]["minutes"]==30)
            attempt=client.post("/interview/attempts",headers=alice,json=body).json()["attempt"]
            check("first unseen answer saved before correction",attempt["persisted"] and attempt["independent"] and attempt["numerical_pass"] and "worked_solution" in attempt["feedback"])
            duplicate=client.post("/interview/attempts",headers=alice,json=body).json()["attempt"]
            check("duplicate submit preserves first attempt",duplicate["id"]==attempt["id"])
            conflict=client.post("/interview/attempts",headers=alice,json={**body,"answers":{"price":0,"delta":0}})
            check("request replay cannot overwrite the answer",conflict.status_code==409)
            transfer=client.post("/interview/attempts",headers=alice,json={**body,"variant":"transfer","client_request_id":"smoke-transfer-01","answers":{"price":5.5735,"delta":-0.36317}}).json()["attempt"]
            check("put variant checks conceptual sign transfer",transfer["numerical_pass"] and transfer["independent"])
            review={"criteria":{"assumptions":True,"decision":True,"limitations":False},"notes":"I still need to explain skew.","client_request_id":"smoke-review-001"}
            check("cross-account attempt access rejected",client.post(f"/interview/attempts/{attempt['id']}/review",headers=bob,json=review).status_code==404)
            reviewed=client.post(f"/interview/attempts/{attempt['id']}/review",headers=alice,json=review).json()["review"]
            check("reasoning review remains explicitly self-reported",reviewed["assessment_type"]=="learner_self_review" and not reviewed["all_criteria_self_reported"])
            session=client.post("/interview/session",headers=alice,json={"case_id":"gamma-vega","variant":"transfer","active_seconds":300,"client_request_id":"smoke-session-01"}).json()
            check("active time cannot exceed elapsed server time",session["credited_active_seconds"]<30)
            state=client.get("/interview/state",headers=alice).json()
            check("progress separates attempts, numeric and transfer checks",state["metrics"]["cases_attempted"]==1 and state["metrics"]["numerical_passes"]==1 and state["metrics"]["transfer_passes"]==1 and state["metrics"]["reasoning_reviews"]==1 and not state["metrics"]["certified_mastery"])
            check("second account has no inherited progress",client.get("/interview/state",headers=bob).json()["attempts"]==[])
            check("learners cannot read operator pilot aggregates",client.get("/interview/pilot/metrics",headers=alice).status_code==403)
            pilot=client.get("/interview/pilot/metrics",headers={"X-API-Key":settings.operator_api_key}).json()
            check("pilot aggregates count recorded participation",pilot["learners_seen"]==2 and pilot["activated_learners"]==1 and pilot["transfer_passed_learners"]==1 and pilot["totals"]["attempts"]==2)
            check("pilot aggregates expose no learner identity or memo","pilot-alice" not in json.dumps(pilot) and "pilot-bob" not in json.dumps(pilot) and body["reasoning"] not in json.dumps(pilot))
            check("public first lesson position saves without completion points",client.put("/platform/courses/black-scholes/position",headers=alice,json={"module_index":1}).status_code==200 and client.get("/platform/progress/pilot-alice",headers=alice).json()["events"]==0)
            reveal=client.post("/interview/reveal",headers=alice,json={"case_id":"dividend-parity","variant":"primary","client_request_id":"smoke-reveal-001"}).json()
            check("revealing a correction records exposure",not reveal["independent"] and reveal["persisted"])
            export=client.get("/interview/export",headers=alice)
            check("private export contains original reasoning and limitations",export.headers["cache-control"]=="private, no-store" and export.json()["attempts"][0]["reasoning"]==body["reasoning"] and len(export.json()["limitations"])==4)
        with TestClient(create_app(build_services(settings))) as fresh:
            restored=fresh.get("/interview/state",headers=alice).json()
            check("fresh process restores exact task and both attempts",restored["current_task"]=={"case_id":"gamma-vega","variant":"transfer"} and len(restored["attempts"])==2)
    return {"status":"PASS","scope":"Local real FastAPI handlers and SQLite; signed isolated learners, not public sales evidence.",
            "checks_passed":len(checks),"checks":checks,"external_llm_calls":0,"real_payments":0}


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path)
    args=parser.parse_args()
    report=run()
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,indent=2))
