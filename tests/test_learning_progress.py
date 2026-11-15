"""Read-only dashboard projection of saved exercise and Survival work."""
from datetime import datetime,timezone
import json
from pathlib import Path
import sqlite3

from fastapi.testclient import TestClient

from pricinglibrary_rag.api import create_app
from pricinglibrary_rag.learning_workflows import BANK,LearningStore
from pricinglibrary_rag.platform_store import PlatformStore
from test_learning_workflows import learning


def _readonly(path):
    db=sqlite3.connect(Path(path).resolve().as_uri()+"?mode=ro",uri=True)
    db.row_factory=sqlite3.Row
    db.execute("PRAGMA query_only=ON")
    return db


def _snapshot(path):
    with _readonly(path) as db:
        tables={row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        names=[name for name in tables if name.startswith("learning_") or name in {"platform_progress","interview_profiles","interview_events"}]
        return {name:[tuple(row) for row in db.execute(f'SELECT * FROM "{name}" ORDER BY rowid')] for name in sorted(names)}


def test_old_database_progress_read_returns_zeros_without_initialising_learning_or_profiles(tmp_path):
    store=PlatformStore(tmp_path/"old-platform.sqlite3")
    with _readonly(store.db_path) as db:
        before=list(db.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"))
        projected=LearningStore.progress_summary(db,"old-owner")
        assert all(projected[key]==0 for key in projected if key.endswith("_count"))
        assert projected["exercise_resume"] is projected["survival_resume"] is None
        assert projected["last_activity_at"] is None and projected["mastery_certified"] is False
        assert db.total_changes==0
    result=store.progress_summary("old-owner")
    assert result["learning"]==projected and result["events"]==0 and result["avg_score"] is None
    with _readonly(store.db_path) as db:
        after=list(db.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"))
        assert before==after
        assert not any(name[0].startswith("learning_") or name[0]=="interview_profiles" for name in after)


def test_projection_is_owner_strict_and_resumes_latest_review_without_exposing_payloads(tmp_path):
    store=LearningStore(tmp_path/"owned.sqlite3")
    first="exa_"+"a"*32;second="exa_"+"b"*32;other="exa_"+"c"*32
    with store.connect() as db:
        for identifier,owner,exercise,when in [(first,"alice","exo_"+"a"*12,1000),(second,"alice","bs-eur-call",1010),(other,"bob","private-bob",5000)]:
            db.execute("INSERT INTO learning_exercise_attempts VALUES(?,?,?,?,?)",(identifier,owner,exercise,'{"answers":"PRIVATE-WRITTEN-ANSWER","feedback":"PRIVATE-CORRECTION"}',when))
        for identifier,owner,attempt,when in [("review-a1","alice",first,1020),("review-a2","alice",first,1030),("review-b","bob",other,9000),("invalid-cross-owner","alice",other,10000)]:
            db.execute("INSERT INTO learning_exercise_reviews VALUES(?,?,?,?,?)",(identifier,owner,attempt,'{"notes":"PRIVATE-REVIEW-NOTES"}',when))
    before=_snapshot(store.db_path)
    with _readonly(store.db_path) as db:
        value=LearningStore.progress_summary(db,"alice")
        assert value["exercise_attempt_count"]==2 and value["exercise_review_count"]==2
        assert value["exercise_resume"]["attempt_id"]==first and value["exercise_resume"]["review_count"]==2
        assert value["exercise_resume"]["path"]==f"/exercises/exo_{'a'*12}?attempt={first}"
        assert value["last_activity_at"]==datetime.fromtimestamp(1030,timezone.utc).isoformat()
        assert db.total_changes==0
        assert LearningStore.progress_summary(db,"nobody")["exercise_attempt_count"]==0
    serialised=json.dumps(value)
    assert not any(marker in serialised for marker in ("PRIVATE-","private-bob",other,"criteria","answers","feedback","score"))
    assert _snapshot(store.db_path)==before


def test_survival_counts_all_saved_answers_and_prefers_a_live_run_without_revealing_feedback(tmp_path):
    store=LearningStore(tmp_path/"survival.sqlite3")
    active="srv_"+"a"*32;finished="srv_"+"b"*32;foreign="srv_"+"c"*32
    def state(count,completed):
        return json.dumps({"history":[{"question_id":f"question-{i}","selected":"A","correct_answer":"SECRET-ANSWER"} for i in range(count)],
            "completed":completed,"feedback":{"explanation":"PRIVATE-EXPLANATION"},"score":4321})
    with store.connect() as db:
        for identifier,owner,count,completed,when in [(active,"alice",4,False,1000),(finished,"alice",20,True,2000),(foreign,"bob",20,True,9000)]:
            db.execute("INSERT INTO learning_survival VALUES(?,?,?,?,?)",(identifier,owner,state(count,completed),when-10,when))
    before=_snapshot(store.db_path)
    with _readonly(store.db_path) as db:
        value=LearningStore.progress_summary(db,"alice")
        assert (value["survival_run_count"],value["survival_answer_count"],value["survival_completed_count"])==(2,24,1)
        resume=value["survival_resume"]
        assert resume["run_id"]==active and resume["phase"]=="feedback" and resume["answered_count"]==4
        assert resume["path"]==f"/survival/core?run={active}" and not resume["completed"]
        assert value["survival_last_activity_at"]==datetime.fromtimestamp(2000,timezone.utc).isoformat()
        assert db.total_changes==0
    assert not any(word in json.dumps(value) for word in ("SECRET","PRIVATE","correct_answer","explanation","score","selected"))
    assert _snapshot(store.db_path)==before


def test_invalid_stored_identifiers_cannot_create_unbounded_or_external_resume_links(tmp_path):
    store=LearningStore(tmp_path/"invalid-identifiers.sqlite3")
    with store.connect() as db:
        db.execute("INSERT INTO learning_exercise_attempts VALUES(?,?,?,?,?)",("exa_"+"a"*32,"alice","//outside.example/path","{}",1000))
        db.execute("INSERT INTO learning_survival VALUES(?,?,?,?,?)",("srv_bad/../../x","alice",'{"history":[],"completed":false}',1000,1001))
    with _readonly(store.db_path) as db:
        value=LearningStore.progress_summary(db,"alice")
        assert value["exercise_attempt_count"]==value["survival_run_count"]==1
        assert value["exercise_resume"] is value["survival_resume"] is None
        assert "outside.example" not in json.dumps(value)


def test_actual_api_actions_appear_on_dashboard_after_reload_without_new_events_or_owner_leaks(learning):
    client,services,headers=learning
    signed=headers("student")
    generated=client.post("/agent/exercise",headers=signed,json={"topic":"Black-Scholes","language":"en","number_of_questions":3,
        "free_prompt":"European call S=100 K=100 r=5% sigma=20% T=1 year","client_request_id":"progress-generated-001"})
    assert generated.status_code==200,generated.text
    exercise=generated.json()["metadata"]["library_id"]
    base=f"/learning/exercises/{exercise}"
    task=client.get(base+"/task",headers=signed).json()
    answers={str(q["number"]):"Private original written method that must not appear in the dashboard." for q in task["questions"]}
    body={"answers":answers,"reasoning":"PRIVATE-REASONING","client_request_id":"progress-attempt-001"}
    response=client.post(base+"/attempts",headers=signed,json=body)
    assert response.status_code==200,response.text
    attempt=response.json()["id"]
    assert client.post(base+"/attempts",headers=signed,json=body).json()["id"]==attempt
    review={"criteria":{key:True for key in answers},"notes":"PRIVATE-SELF-REVIEW","client_request_id":"progress-review-001"}
    assert client.post(f"/learning/exercise-attempts/{attempt}/review",headers=signed,json=review).status_code==200
    assert client.post(f"/learning/exercise-attempts/{attempt}/review",headers=signed,json=review).status_code==200
    run=client.post("/learning/survival/runs",headers=signed,json={"client_request_id":"progress-survival-001"}).json()
    for i in range(4):
        question=BANK[i]
        answer=client.post(f"/learning/survival/runs/{run['id']}/answers",headers=signed,json={"question_id":question["id"],"answer":question["correct"],"client_request_id":f"progress-answer-{i:03}"})
        assert answer.status_code==200,answer.text
        run=answer.json()
        if i<3:run=client.post(f"/learning/survival/runs/{run['id']}/next",headers=signed,json={"client_request_id":f"progress-next-{i:03}"}).json()
    before=_snapshot(services.settings.db_path)
    reloaded=TestClient(create_app(services))
    response=reloaded.get("/platform/progress/student",headers=signed)
    assert response.status_code==200 and response.headers["cache-control"]=="private, no-store"
    summary=response.json();value=summary["learning"]
    assert summary["events"]==0 and summary["avg_score"] is None
    assert value["exercise_attempt_count"]==value["exercise_review_count"]==1
    assert value["exercise_resume"]["exercise_id"]==exercise and value["exercise_resume"]["attempt_id"]==attempt
    assert value["survival_run_count"]==1 and value["survival_answer_count"]==4 and value["survival_completed_count"]==0
    assert value["survival_resume"]["run_id"]==run["id"] and value["survival_resume"]["phase"]=="feedback"
    assert value["last_activity_at"] and value["mastery_certified"] is False
    assert "PRIVATE-" not in json.dumps(value) and "original written method" not in json.dumps(value)
    empty=reloaded.get("/platform/progress/other",headers=headers("other")).json()["learning"]
    assert all(empty[key]==0 for key in empty if key.endswith("_count"))
    assert empty["exercise_resume"] is empty["survival_resume"] is None
    assert reloaded.get("/platform/progress/student",headers=headers("other")).status_code==403
    assert _snapshot(services.settings.db_path)==before
