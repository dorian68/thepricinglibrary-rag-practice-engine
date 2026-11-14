"""Real CLI processes against a real isolated HTTP app; identities are test fixtures."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import threading
import time

import pytest
import uvicorn

from pricinglibrary_rag.api import create_app
from pricinglibrary_rag.canonical_tools import TOOL_FORMATS, run_canonical_tool, tool_example
from pricinglibrary_rag.factory import build_services
from pricinglibrary_rag.platform_store import PlatformStore
from pricinglibrary_rag.security import mint_session_token
from test_api_security import _settings


@pytest.fixture(scope="module")
def cli_server(tmp_path_factory):
    root = tmp_path_factory.mktemp("real-cli-http")
    courses = root / "private-courses"; courses.mkdir(); (courses / "en").mkdir()
    (courses / "vanilla-options-quote.md").write_text("# Test privé français\n\nContenu synthétique de fixture, pas un cours commercial.",encoding="utf-8")
    (courses / "en" / "vanilla-options-quote.md").write_text("# English fixture\n\nOriginal synthetic access-control fixture, not a commercial course.",encoding="utf-8")
    (courses / "en" / "_index.json").write_text(json.dumps({
        "schema_version":"tpl.course.language-index.v1", "approval_basis":"synthetic_test_fixture_only",
        "courses":[{"slug":"vanilla-options-quote", "status":"accepted_98_and_independent_review",
                    "sha256":hashlib.sha256((courses / "en" / "vanilla-options-quote.md").read_bytes()).hexdigest()}]
    }),encoding="utf-8")
    settings = _settings(root, course_scripts_dir=courses, rate_limit_per_min=10000)
    services = build_services(settings)
    roles = {"free": "cli-free", "starter": "cli-starter", "pro": "cli-pro", "other": "cli-other", "operator": "cli-operator"}
    tokens = {}
    for role, subject in roles.items():
        tokens[role] = mint_session_token(settings.auth_token_secret,user_id=subject,email=f"{subject}@test.invalid",
                                           role="operator" if role == "operator" else "member",expires_at=int(time.time())+3600)
        if role in {"starter", "pro", "other"}:
            services.store.upsert_entitlement(f"{subject}@test.invalid", "starter" if role == "starter" else "pro",user_id=subject)
    tokens["expired"] = mint_session_token(settings.auth_token_secret,user_id="expired-cli",email="expired@test.invalid",expires_at=int(time.time())-10)
    platform = PlatformStore(settings.db_path)
    job = platform.create_job(title="Synthetic test role",company="Fixture organisation",location="Test",kind="internship",tags=[],description="Fixture job only.",posted_by="test")
    platform.upsert_blog(slug="cli-fixture",title="CLI fixture article",author="Fixture",excerpt="Test only",body="Synthetic fixture article.",tags=[],read_minutes=1)
    sock = socket.socket(); sock.bind(("127.0.0.1",0)); port = sock.getsockname()[1]
    server = uvicorn.Server(uvicorn.Config(create_app(services),log_level="critical",access_log=False,lifespan="off"))
    thread = threading.Thread(target=server.run,kwargs={"sockets":[sock]},daemon=True); thread.start()
    deadline=time.monotonic()+15
    while not server.started and time.monotonic()<deadline: time.sleep(.01)
    assert server.started
    value={"root":root,"api":f"http://127.0.0.1:{port}","tokens":tokens,"services":services,"job":job}
    yield value
    server.should_exit=True; thread.join(timeout=10); sock.close()


def cli(server, role, *arguments, body=None, expected=0):
    args=list(arguments)
    if body is not None:
        f=server["root"] / ("input-"+str(time.time_ns())+".json")
        f.write_text(json.dumps(body,allow_nan=False),encoding="utf-8");args += ["--input",str(f)]
    env={**os.environ,"PYTHONIOENCODING":"utf-8"}
    env.pop("TPL_TOKEN_FILE",None)
    if role:env["TPL_ACCESS_TOKEN"]=server["tokens"][role]
    else:env.pop("TPL_ACCESS_TOKEN",None)
    p=subprocess.run([sys.executable,"-m","pricinglibrary_rag.learner_cli","--api",server["api"],"--retries","0",*args],
                     cwd=Path(__file__).resolve().parents[1],env=env,capture_output=True,text=True,encoding="utf-8",timeout=90,
                     creationflags=subprocess.CREATE_NO_WINDOW if os.name=="nt" else 0)
    assert p.returncode==expected,(arguments,p.stdout,p.stderr)
    data=json.loads(p.stdout)
    assert data["schema"]=="tpl.cli.result.v1"
    assert data["ok"]==(expected==0)
    assert all(token not in p.stdout+p.stderr for token in server["tokens"].values())
    return data.get("data") if expected==0 else data


def test_identity_catalog_and_no_local_admin_bootstrap(cli_server):
    s=cli_server
    assert cli(s,None,"doctor")["authentication"]=="anonymous"
    assert cli(s,"free","auth","whoami")["user_id"]=="cli-free"
    token_file=s["root"]/"identity.private.json"
    token_file.write_text(json.dumps({"access_token":s["tokens"]["free"]}),encoding="utf-8")
    assert cli(s,"pro","--token-file",str(token_file),"auth","whoami")["user_id"]=="cli-free"
    cli(s,None,"auth","whoami",expected=3)
    cli(s,"expired","auth","whoami",expected=3)
    assert len(cli(s,None,"courses","list"))==12
    assert len(cli(s,None,"tools","list")["tools"])==9
    cli(s,"starter","tools","run","binomial",body=tool_example("binomial"),expected=4)
    assert cli(s,None,"courses","preview","black-scholes")["preview_only"]
    cli(s,None,"courses","read","black-scholes",expected=3)
    cli(s,"free","courses","read","black-scholes",expected=4)
    assert "English fixture" in cli(s,"starter","courses","read","black-scholes","--language","en")["content"]
    english = s["services"].settings.course_scripts_dir / "en" / "vanilla-options-quote.md"
    approved = english.read_bytes()
    try:
        english.write_bytes(approved + b"\nUnreviewed local edit.")
        cli(s,"starter","courses","read","black-scholes","--language","en",expected=5)
        listed = cli(s,None,"courses","list")
        assert next(row for row in listed if row["id"] == "black-scholes")["available_languages"] == ["fr"]
    finally:
        english.write_bytes(approved)
    assert "English fixture" in cli(s,"starter","courses","read","black-scholes","--language","en")["content"]
    cli(s,"starter","courses","read","greeks","--language","en",expected=5)
    assert cli(s,None,"services","availability")["mentoring"]["status"]=="not_bookable"


def test_real_course_position_completion_and_owner(cli_server):
    s=cli_server
    cli(s,"free","courses","open","black-scholes","--module","1")
    before=cli(s,"free","courses","resume","black-scholes")
    assert before["resume_module_index"]==1 and before["completed_modules"]==[]
    completed=cli(s,"free","courses","complete","black-scholes","--module","1")
    assert completed["mastery_awarded"] is False
    assert cli(s,"free","courses","resume","black-scholes")["completed_modules"]==[1]
    assert cli(s,"other","courses","resume","black-scholes")["completed_modules"]==[]
    cli(s,"free","courses","complete","black-scholes","--module","2",expected=4)
    cli(s,"pro","courses","complete","black-scholes","--module","99",expected=2)


@pytest.mark.parametrize("name",list(TOOL_FORMATS))
def test_nine_real_engines_and_exports(cli_server,name):
    s=cli_server
    example=cli(s,None,"tools","example",name)
    result=cli(s,"pro","tools","run",name,body=example)
    expected=run_canonical_tool(name,example)
    assert result==expected
    for fmt in TOOL_FORMATS[name][1:]:
        output=s["root"]/(name+"-"+fmt+".csv")
        receipt=cli(s,"pro","tools","run",name,"--format",fmt,"--output",str(output),body=example)
        assert receipt["bytes"]>10 and output.read_text(encoding="utf-8")==run_canonical_tool(name,example,fmt)
    if name=="bs-pricer":
        assert result["selected"]["unitPrice"]==pytest.approx(10.450575619322287,abs=1e-5)
        changed={**example,"spot":120}
        assert cli(s,None,"tools","run",name,body=changed)["selected"]["unitPrice"]>result["selected"]["unitPrice"]
    else:
        cli(s,"free","tools","run",name,body=example,expected=4)


def test_interview_real_attempt_idempotence_review_private_export(cli_server):
    s=cli_server
    assert len(cli(s,None,"interview","catalog")["cases"])==6
    task=cli(s,None,"interview","task","call-quote")
    assert "expected" not in json.dumps(task)
    cli(s,"free","interview","onboard",body={"role":"structuring","minutes_per_session":30,"deadline":None})
    answer={"answers":{"price":10.4506,"delta":.63683},"reasoning":"I used European exercise and continuous rates with no dividend yield. The long call delta is positive and the hedge sells underlying shares."}
    created=cli(s,"free","interview","answer","call-quote","--request-id","cli-independent-attempt",body=answer)["attempt"]
    repeated=cli(s,"free","interview","answer","call-quote","--request-id","cli-independent-attempt",body=answer)["attempt"]
    assert created["id"]==repeated["id"] and created["numerical_pass"] and created["independent"]
    cli(s,"free","interview","answer","call-quote","--request-id","cli-independent-attempt",body={**answer,"answers":{"price":0,"delta":0}},expected=6)
    cli(s,"free","interview","review",created["id"],"--request-id","cli-review-request",body={"criteria":{"assumptions":True,"decision":True,"limitations":False},"notes":"Self-review, not expert feedback."})
    cli(s,"other","interview","review",created["id"],"--request-id","cli-other-review",body={"criteria":{"assumptions":True,"decision":True,"limitations":True}},expected=5)
    state=cli(s,"free","interview","resume")
    assert state["current_task"]["case_id"]=="call-quote"
    report=s["root"]/"private-practice.json"
    cli(s,"free","interview","export","--output",str(report))
    assert json.loads(report.read_text(encoding="utf-8"))["owner_id"]=="cli-free"
    assert not cli(s,"other","interview","export")["attempts"]
    cli(s,"free","interview","metrics",expected=4)
    assert "activated_learners" in cli(s,"operator","interview","metrics")


def test_forum_jobs_blog_support_and_commercial_status(cli_server):
    s=cli_server
    thread=cli(s,"starter","forum","create",body={"channel":"forum","title":"CLI discussion fixture","body":"A reproducible forum test thread."})
    identifier=thread["id"]
    cli(s,"starter","forum","reply",identifier,body={"body":"Actual fixture reply."})
    cli(s,"starter","forum","vote",identifier)
    actual=cli(s,"starter","forum","thread",identifier)
    assert actual["comments"] and actual["thread"]["title"]=="CLI discussion fixture"
    cli(s,"free","forum","list",expected=4)
    assert cli(s,None,"jobs","list")["jobs"]
    cli(s,"free","jobs","apply",s["job"]["id"],body={"note":"Synthetic application test."})
    assert cli(s,None,"blog","open","cli-fixture")["title"]=="CLI fixture article"
    assert cli(s,"free","support","report",body={"summary":"CLI fixture support issue","detail":"Test issue; no email delivery claim."})["id"]
    assert cli(s,None,"kit","availability")["sale_ready"] is False
    assert cli(s,None,"plans","status")["configured"] is False
    cli(s,None,"kit","download",expected=2)


def test_rejected_inputs_do_not_leak_credentials_or_invent_fallbacks(cli_server):
    s=cli_server
    cli(s,"pro","tools","run","bs-pricer",body={"bad":"payload"},expected=7)
    cli(s,None,"--token","credential-must-not-be-echoed",expected=2)
    cli(s,"pro","market","history","EURUSD","--points","999999",expected=2)


def test_operator_publications_subscription_and_private_admin_contracts(cli_server):
    s = cli_server
    job_body = {"title":"CLI published fixture", "company":"Synthetic fixture only", "kind":"internship"}
    cli(s,"pro","jobs","publish",body=job_body,expected=4)
    job = cli(s,"operator","jobs","publish",body=job_body)
    assert any(row["id"] == job["id"] for row in cli(s,None,"jobs","list")["jobs"])
    article = {"slug":"cli-published-fixture", "title":"CLI authored fixture", "body":"Original synthetic QA article; no commercial claim."}
    cli(s,"pro","blog","publish",body=article,expected=4)
    cli(s,"operator","blog","publish",body=article)
    assert cli(s,None,"blog","open",article["slug"])["body"] == article["body"]
    before = cli(s,"operator","admin","counts")["counts"]["subscribers"]
    subscription = {"email":"newsletter-cli-fixture@test.invalid", "source":"isolated_cli_test"}
    cli(s,None,"newsletter","subscribe",body=subscription)
    cli(s,None,"newsletter","subscribe",body=subscription)
    assert cli(s,"operator","admin","counts")["counts"]["subscribers"] == before + 1
    cli(s,None,"jobs","sources",expected=3)
    cli(s,"pro","jobs","sources",expected=4)
    assert "providers" in cli(s,"operator","jobs","sources")
    for name in ("activity", "survival"):
        assert "leaderboard" in cli(s,"pro","leaderboard",name,"--limit","3")
    assert "bug_reports" in cli(s,"operator","admin","support","--limit","3")
    assert "providers" in cli(s,"operator","admin","market-providers")
    for action in ("counts", "support", "market-providers"):
        cli(s,"pro","admin",action,expected=4)


def test_real_paper_trade_recovery_uses_same_intent_and_keeps_other_owner_empty(cli_server):
    s = cli_server
    query = json.dumps({"underlying":"EUR/USD", "ticket":{"spot":1.1, "strike":1.05,
                        "riskFreeRate":.03, "dividendYield":.02, "volatility":.2,
                        "maturityYears":1, "quantity":7654321}})
    body = {"query":query, "side":-1}
    cli(s,"starter","rfq","trade","--request-id","cli-paper-denied",body=body,expected=4)
    created = cli(s,"pro","rfq","trade","--request-id","cli-paper-one-intent",body=body)
    assert created["paper_position"]["quantity"] == 7654321 and not created["replayed"]
    cli(s,"pro","rfq","tick","--seconds","60")
    recovered = cli(s,"pro","rfq","trade","--request-id","cli-paper-one-intent",body=body)
    assert recovered["replayed"] and recovered["paper_position"]["id"] == created["paper_position"]["id"]
    assert recovered["result"] == created["result"]
    assert len(cli(s,"pro","rfq","state")["paper_positions"]) == 1
    assert cli(s,"other","rfq","state")["paper_positions"] == []
    cli(s,"pro","rfq","trade","--request-id","cli-paper-one-intent",body={**body,"side":1},expected=7)
    cli(s,"pro","rfq","trade","--request-id","cli-paper-one-intent",body={**body,"idempotency_key":"another-key"},expected=2)
    assert len(cli(s,"pro","rfq","state")["paper_positions"]) == 1


def test_real_survival_question_feedback_next_and_owner(cli_server):
    from pricinglibrary_rag.learning_workflows import BANK
    s=cli_server
    started=cli(s,"pro","survival","start","--request-id","cli-survival-start",body={"wave":"core"})
    assert started["phase"]=="answer" and started["total_questions"]==20
    repeated=cli(s,"pro","survival","start","--request-id","cli-survival-start",body={"wave":"core"})
    assert repeated["id"]==started["id"]
    assert "correct" not in started["question"]
    answer={"question_id":started["question"]["id"],"answer":BANK[0]["correct"]}
    answered=cli(s,"pro","survival","answer",started["id"],"--request-id","cli-survival-answer",body=answer)
    assert answered["phase"]=="feedback" and answered["index"]==0
    assert answered["feedback"]["question_id"]==started["question"]["id"] and answered["feedback"]["correct"]
    assert cli(s,"pro","survival","state",started["id"])["phase"]=="feedback"
    assert cli(s,"pro","survival","list")["runs"]
    cli(s,"other","survival","state",started["id"],expected=5)
    next_question=cli(s,"pro","survival","next",started["id"],"--request-id","cli-survival-next")
    assert next_question["index"]==1 and next_question["phase"]=="answer"
    cli(s,"free","survival","start",body={"wave":"core"},expected=4)


def test_portable_notebooks_are_real_files_and_builtin_runs(cli_server):
    s=cli_server
    entries=cli(s,"pro","notebooks","list")["notebooks"]
    assert {item["id"] for item in entries}=={"black-scholes-intro","barrier-down-out"}
    for item in entries:
        identifier=item["id"]
        opened=cli(s,"pro","notebooks","open",identifier)
        assert opened["code"] and opened["language"]=="en"
        notebook=s["root"]/(identifier+".ipynb")
        cli(s,"pro","notebooks","export",identifier,"--output",str(notebook))
        assert json.loads(notebook.read_text(encoding="utf-8"))["nbformat"]==4
        python_file=s["root"]/(identifier+".py")
        cli(s,"pro","notebooks","export",identifier,"--format","py","--output",str(python_file))
        assert "def run(" in python_file.read_text(encoding="utf-8")
        result=cli(s,"pro","notebooks","run",identifier,body={})
        assert isinstance(result,dict) and result
    cli(s,"free","notebooks","list",expected=4)
    cli(s,"pro","notebooks","run","unknown",body={},expected=5)


def test_interview_portable_exports_and_calendar_are_native_files(cli_server):
    s=cli_server
    for fmt,extension in [("report","md"),("csv","csv"),("anki","tsv")]:
        out=s["root"]/("practice."+extension)
        cli(s,"free","interview","export","--format",fmt,"--output",str(out))
        content=out.read_text(encoding="utf-8")
        assert len(content)>20 and "cli-free" not in content
    out=s["root"]/"study.ics"
    cli(s,"free","interview","calendar","--output",str(out),body={"starts_at":"2026-12-01T18:00:00+01:00","minutes":30,"sessions":3})
    content=out.read_text(encoding="utf-8")
    assert content.count("BEGIN:VEVENT")==3 and "20261201T170000Z" in content
    cli(s,"free","interview","calendar",body={"starts_at":"2026-12-01T18:00:00","sessions":3},expected=7)


def test_canonical_and_generated_exercise_attempts_keep_their_real_assessment_type(cli_server):
    s=cli_server
    catalog=cli(s,"starter","exercises","catalog")
    assert len(catalog)==14 and any(item["id"]=="realized-vol-estimators" for item in catalog)
    opened=cli(s,"starter","exercises","open","bs-eur-call")
    assert opened["questions"]
    generated=cli(s,"starter","exercises","generate","--request-id","cli-generated-exercise",
                  body={"product":"European call option","concept":"Black Scholes","free_prompt":"European call spot125 strike110 volatility30% maturity0.75 risk-free rate3% dividend yield1%","number_of_questions":3})
    identifier=generated["metadata"]["library_id"]
    assert generated["metadata"]["language"]=="en" and generated["metadata"]["persistence"]=="account"
    assert any(item["id"]==identifier for item in cli(s,"starter","exercises","library")["exercises"])
    cli(s,"other","exercises","open",identifier,expected=5)
    task=cli(s,"starter","exercises","task",identifier)
    assert "### Answer" not in task["brief"]
    answer={"answers":{str(q["number"]):"My written numerical method and interpretation for this question." for q in task["questions"]},"reasoning":"I checked the conventions and units against the supplied ticket."}
    attempt=cli(s,"starter","exercises","answer",identifier,"--request-id","cli-written-attempt",body=answer)
    assert attempt["automatic_grade"] is None and attempt["assessment_type"]=="learner_self_review"
    cli(s,"starter","exercises","review",attempt["id"],"--request-id","cli-written-review",body={"criteria":{key:False for key in answer["answers"]},"notes":"A genuine self-review, not a machine grade."})
    assert cli(s,"starter","exercises","attempt",attempt["id"])["self_reviews"]
    cli(s,"other","exercises","attempt",attempt["id"],expected=5)
    out=s["root"]/"written-attempt.md"
    cli(s,"starter","exercises","export-attempt",attempt["id"],"--format","md","--output",str(out))
    assert out.read_text(encoding="utf-8")
