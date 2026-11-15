"""Account-owned learning actions shared by the HTTP, CLI and browser clients.

No browser state, client score, user-selected identity or uploaded Python code is
authoritative. Existing course/exercise/Interview records are not rewritten.
"""
from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone, timedelta
import csv
import hashlib
import io
import json
import math
from pathlib import Path
import re
import sqlite3
import time
from typing import Literal
import uuid

from fastapi import FastAPI, HTTPException, Request, Response
from pydantic import BaseModel, ConfigDict, Field, StrictBool, field_validator

from .interview_lab import InterviewLabStore, CASE_IDS, _full_case
from .platform_store import PlatformStore
from .security import AuthenticatedIdentity, IDENTITY, OPERATOR

ASSETS = Path(__file__).parent / "learning_assets"
BANK = json.loads((ASSETS / "survival_questions.json").read_text(encoding="utf-8"))["questions"]
NOTEBOOKS = {item["id"]: item for item in json.loads(
    (ASSETS / "notebook_catalog.json").read_text(encoding="utf-8"))["notebooks"]}
PRACTICE_EXERCISES = {item["id"]: item for item in json.loads(
    (ASSETS / "practice_exercises.json").read_text(encoding="utf-8"))["exercises"]}
PRACTICE_REFERENCES = {item["id"]: item for item in json.loads(
    (ASSETS / "practice_references.json").read_text(encoding="utf-8"))["references"]}
SCHEMA = "tpl.learning.v1"


def _json(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


class StrictBody(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ActionBody(StrictBody):
    client_request_id: str = Field(min_length=8, max_length=80, pattern=r"^[A-Za-z0-9-]+$")


class SurvivalStart(ActionBody):
    wave: Literal["core"] = "core"


class SurvivalAnswer(ActionBody):
    question_id: str = Field(max_length=100)
    answer: Literal["A", "B", "C", "D", "timeout"]


class WrittenAttempt(ActionBody):
    answers: dict[str, str] = Field(min_length=1, max_length=12)
    reasoning: str = Field(default="", max_length=8000)

    @field_validator("answers")
    @classmethod
    def written_answers(cls, value):
        if any(not re.fullmatch(r"[1-9][0-9]?", key) or not text.strip() or len(text) > 8000
               for key, text in value.items()):
            raise ValueError("Each numbered answer must contain 1–8000 characters.")
        return value


class WrittenReview(ActionBody):
    criteria: dict[str, StrictBool] = Field(min_length=1, max_length=12)
    notes: str = Field(default="", max_length=8000)


class NotebookRun(StrictBody):
    ticket: dict | None = None


class StudyCalendar(StrictBody):
    starts_at: datetime
    minutes: Literal[15, 30, 60] = 30
    sessions: int = Field(default=6, ge=1, le=12, strict=True)

    @field_validator("starts_at")
    @classmethod
    def require_timezone(cls, value):
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("Use an ISO date/time with an explicit UTC offset.")
        return value


class LearningStore:
    @staticmethod
    def progress_summary(db, owner):
        """Project existing owner records without initialising or mutating state.

        This takes the caller's read transaction so dashboard events, interview
        and learning counts describe one snapshot. Written reviews are learner
        actions; a finished Survival run is not a mastery certificate.
        """
        result={"schema_version":"tpl.learning.progress.v1",
            "exercise_attempt_count":0,"exercise_review_count":0,
            "survival_run_count":0,"survival_answer_count":0,"survival_completed_count":0,
            "last_activity_at":None,"exercise_last_activity_at":None,"survival_last_activity_at":None,
            "exercise_resume":None,"survival_resume":None,"mastery_certified":False}
        tables={row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name IN "
            "('learning_exercise_attempts','learning_exercise_reviews','learning_survival')")}
        def timestamp(value):
            try:
                value=float(value)
                if not math.isfinite(value) or value<0:return None
                datetime.fromtimestamp(value,timezone.utc)
                return value
            except (TypeError,ValueError,OverflowError,OSError):
                return None
        def iso(value):
            return datetime.fromtimestamp(value,timezone.utc).isoformat() if value is not None else None
        exercise_last=survival_last=None
        exercise_candidates=[]
        if "learning_exercise_attempts" in tables:
            if "learning_exercise_reviews" in tables:
                rows=db.execute("SELECT a.id,a.exercise_id,a.created_at,a.rowid AS insertion_order,"
                    "COUNT(r.id) AS reviews,MAX(r.created_at) AS reviewed_at "
                    "FROM learning_exercise_attempts a LEFT JOIN learning_exercise_reviews r "
                    "ON r.attempt_id=a.id AND r.owner_id=a.owner_id WHERE a.owner_id=? "
                    "GROUP BY a.id,a.exercise_id,a.created_at,a.rowid",(owner,))
            else:
                rows=db.execute("SELECT id,exercise_id,created_at,rowid AS insertion_order,0 AS reviews,"
                    "NULL AS reviewed_at FROM learning_exercise_attempts WHERE owner_id=?",(owner,))
            for row in rows:
                result["exercise_attempt_count"]+=1
                result["exercise_review_count"]+=row["reviews"]
                times=[value for value in (timestamp(row["created_at"]),timestamp(row["reviewed_at"])) if value is not None]
                latest=max(times) if times else None
                if latest is not None:exercise_last=max(exercise_last or latest,latest)
                if (re.fullmatch(r"exa_[a-f0-9]{32}",str(row["id"]))
                        and re.fullmatch(r"[a-z][a-z0-9_-]{0,99}",str(row["exercise_id"]))):
                    exercise_candidates.append((latest if latest is not None else -1,row["insertion_order"],
                        {"exercise_id":row["exercise_id"],"attempt_id":row["id"],"review_count":row["reviews"],
                         "last_activity_at":iso(latest),"path":f"/exercises/{row['exercise_id']}?attempt={row['id']}"}))
            if exercise_candidates:result["exercise_resume"]=max(exercise_candidates,key=lambda item:item[:2])[2]
        survival_candidates=[]
        if "learning_survival" in tables:
            for row in db.execute("SELECT id,state,updated_at,rowid AS insertion_order FROM learning_survival WHERE owner_id=?",(owner,)):
                result["survival_run_count"]+=1
                latest=timestamp(row["updated_at"])
                if latest is not None:survival_last=max(survival_last or latest,latest)
                try:state=json.loads(row["state"])
                except (TypeError,ValueError):continue
                if not isinstance(state,dict):continue
                history=state.get("history")
                answered=len(history) if isinstance(history,list) else 0
                completed=state.get("completed") is True
                result["survival_answer_count"]+=answered
                result["survival_completed_count"]+=int(completed)
                if not re.fullmatch(r"srv_[a-f0-9]{32}",str(row["id"])):continue
                phase="complete" if completed else "feedback" if state.get("feedback") is not None else "answer"
                survival_candidates.append((not completed,latest if latest is not None else -1,row["insertion_order"],
                    {"run_id":row["id"],"wave":"core","phase":phase,"answered_count":answered,
                     "total_questions":len(BANK),"completed":completed,"last_activity_at":iso(latest),
                     "path":f"/survival/core?run={row['id']}"}))
            if survival_candidates:result["survival_resume"]=max(survival_candidates,key=lambda item:item[:3])[3]
        result["exercise_last_activity_at"]=iso(exercise_last)
        result["survival_last_activity_at"]=iso(survival_last)
        times=[value for value in (exercise_last,survival_last) if value is not None]
        result["last_activity_at"]=iso(max(times)) if times else None
        return result

    def __init__(self, db_path):
        self.db_path = str(db_path)
        with self.connect() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS learning_actions(
                    owner_id TEXT NOT NULL, request_id TEXT NOT NULL,
                    request_hash TEXT NOT NULL, result TEXT NOT NULL,
                    PRIMARY KEY(owner_id,request_id));
                CREATE TABLE IF NOT EXISTS learning_survival(
                    id TEXT PRIMARY KEY, owner_id TEXT NOT NULL, state TEXT NOT NULL,
                    created_at REAL NOT NULL, updated_at REAL NOT NULL);
                CREATE INDEX IF NOT EXISTS ix_learning_survival_owner ON learning_survival(owner_id,updated_at);
                CREATE TABLE IF NOT EXISTS learning_exercise_attempts(
                    id TEXT PRIMARY KEY, owner_id TEXT NOT NULL, exercise_id TEXT NOT NULL,
                    payload TEXT NOT NULL, created_at REAL NOT NULL);
                CREATE INDEX IF NOT EXISTS ix_learning_attempt_owner ON learning_exercise_attempts(owner_id,exercise_id);
                CREATE TABLE IF NOT EXISTS learning_exercise_reviews(
                    id TEXT PRIMARY KEY, owner_id TEXT NOT NULL, attempt_id TEXT NOT NULL,
                    payload TEXT NOT NULL, created_at REAL NOT NULL);
            """)

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.db_path, timeout=15)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA busy_timeout=15000")
        try:
            with db:
                yield db
        finally:
            db.close()

    def action(self, owner, kind, body, handler):
        data = body.model_dump(mode="json")
        fingerprint = hashlib.sha256(_json({"kind": kind, "body": data}).encode()).hexdigest()
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            old = db.execute("SELECT * FROM learning_actions WHERE owner_id=? AND request_id=?",
                             (owner, body.client_request_id)).fetchone()
            if old:
                if old["request_hash"] != fingerprint:
                    raise HTTPException(409, "This request ID already belongs to a different action.")
                return json.loads(old["result"])
            result = handler(db, data)
            db.execute("INSERT INTO learning_actions VALUES(?,?,?,?)",
                       (owner, body.client_request_id, fingerprint, _json(result)))
            return result

    @staticmethod
    def survival_row(db, owner, run_id):
        row = db.execute("SELECT * FROM learning_survival WHERE owner_id=? AND id=?", (owner, run_id)).fetchone()
        if row is None:
            raise HTTPException(404, "Practice run not found.")
        return row, json.loads(row["state"])

    @staticmethod
    def survival_view(state):
        question = BANK[state["index"]]
        answered = state["feedback"] is not None
        elapsed = max(0, time.time() - state["question_started_at"])
        remaining = max(0, 30 - math.floor(elapsed)) if not answered and not state["completed"] else None
        return {"schema_version": SCHEMA, "id": state["id"], "wave": "core", "total_questions": len(BANK),
                "index": state["index"], "answered_count": len(state["history"]), "lives": state["lives"],
                "score": state["score"], "streak": state["streak"], "best_streak": state["best_streak"],
                "completed": state["completed"], "phase": "complete" if state["completed"] else "feedback" if answered else "answer",
                "question": {key: question[key] for key in ("id", "topic", "prompt", "context", "options")},
                "remaining_seconds": remaining, "question_started_at": state["question_started_at"],
                "feedback": state["feedback"], "history": state["history"], "ranked": False,
                "score_server_computed": True, "proctored": False,
                "limitations": ["Practice timing uses the server clock; no proctoring or certified mastery.",
                                "This question bank can be studied elsewhere; server scoring does not establish independence."]}

    def survival_start(self, owner, body):
        def create(db, _):
            run_id, now = "srv_" + uuid.uuid4().hex, time.time()
            state = {"id": run_id, "index": 0, "score": 0, "streak": 0, "best_streak": 0,
                     "lives": 3, "completed": False, "feedback": None, "history": [], "question_started_at": now}
            db.execute("INSERT INTO learning_survival VALUES(?,?,?,?,?)", (run_id, owner, _json(state), now, now))
            return self.survival_view(state)
        return self.action(owner, "survival:start", body, create)

    def survival_get(self, owner, run_id):
        with self.connect() as db:
            _, state = self.survival_row(db, owner, run_id)
            return self.survival_view(state)

    def survival_list(self, owner):
        with self.connect() as db:
            rows = db.execute("SELECT state FROM learning_survival WHERE owner_id=? ORDER BY updated_at DESC LIMIT 100", (owner,)).fetchall()
            return {"runs": [self.survival_view(json.loads(row["state"])) for row in rows]}

    def survival_answer(self, owner, run_id, body):
        def answer(db, _):
            _, state = self.survival_row(db, owner, run_id)
            question = BANK[state["index"]]
            if state["completed"] or state["feedback"] is not None or body.question_id != question["id"]:
                raise HTTPException(409, "Answer the current question once, then review its feedback before Next.")
            elapsed = max(0, time.time() - state["question_started_at"])
            selected = "timeout" if elapsed >= 30 else body.answer
            correct = selected == question["correct"]
            remaining = max(0, 30 - math.floor(elapsed))
            earned = max(50, remaining * 12) if correct else 0
            state["score"] += earned
            state["streak"] = state["streak"] + 1 if correct else 0
            state["best_streak"] = max(state["best_streak"], state["streak"])
            if not correct:
                state["lives"] -= 1
            state["feedback"] = {"question_id": question["id"], "selected": selected,
                                 "correct_answer": question["correct"], "correct": correct,
                                 "explanation": question["explanation"], "earned": earned,
                                 "elapsed_seconds": min(30, elapsed)}
            state["history"].append(state["feedback"])
            db.execute("UPDATE learning_survival SET state=?,updated_at=? WHERE id=? AND owner_id=?",
                       (_json(state), time.time(), run_id, owner))
            return self.survival_view(state)
        return self.action(owner, "survival:answer:" + run_id, body, answer)

    def survival_next(self, owner, run_id, body):
        def advance(db, _):
            _, state = self.survival_row(db, owner, run_id)
            if state["completed"] or state["feedback"] is None:
                raise HTTPException(409, "Review the answered question before advancing.")
            if state["lives"] <= 0 or state["index"] + 1 >= len(BANK):
                state["completed"] = True
            else:
                state["index"] += 1
                state["feedback"] = None
                state["question_started_at"] = time.time()
            db.execute("UPDATE learning_survival SET state=?,updated_at=? WHERE id=? AND owner_id=?",
                       (_json(state), time.time(), run_id, owner))
            return self.survival_view(state)
        return self.action(owner, "survival:next:" + run_id, body, advance)

    @staticmethod
    def exercise_record(db, owner, exercise_id):
        if exercise_id in PRACTICE_EXERCISES:
            exercise = PRACTICE_EXERCISES[exercise_id]
            reference = PRACTICE_REFERENCES[exercise_id]
            # These are the existing authored practice tasks, not user-owned
            # generated documents. Attempts/reviews remain private to the actor.
            assessment = {
                "questions": [{"number": i, "prompt": step,
                               "criterion": "Compare your answer with the original worked reference and its stated conventions.",
                               "answer": reference["output"] + "\n\n```python\n" + reference["solution"] + "\n```"}
                              for i, step in enumerate(exercise.get("steps", []), 1)],
                "assessment_type": "learner_self_review", "grading_mode": "self_review",
                "original_rubric": exercise.get("grading", []),
                "reference": {key: reference[key] for key in ("ticket", "result", "checks", "conventions", "limitations", "assumptions", "dependencies")},
            }
            brief = ["# " + exercise["title"], exercise.get("description", ""), exercise.get("objective", ""),
                     "## Ticket", *[f"- {label}: {value}" for label, value in exercise.get("marketData", [])],
                     "## Tasks", *[f"{i}. {step}" for i, step in enumerate(exercise.get("steps", []), 1)],
                     "## Python starter", "```python\n" + exercise.get("starterCode", "") + "\n```",
                     "## Reference conventions", *["- " + value for value in reference["conventions"]],
                     "## Additional assumptions", *["- " + value for value in reference["assumptions"]],
                     "## Complete reference ticket", "```json\n" + json.dumps(reference["ticket"], ensure_ascii=False, indent=2) + "\n```"]
            return {"title": exercise["title"], "content": "\n\n".join(brief), "canonical_id": exercise_id,
                    "metadata": {"assessment": assessment, "language": "en"}}, assessment
        row = db.execute("SELECT response_json FROM platform_exercises WHERE id=? AND user_id=?", (exercise_id, owner)).fetchone()
        if not row:
            raise HTTPException(404, "Exercise not found.")
        record = json.loads(row["response_json"])
        assessment = record.get("metadata", {}).get("assessment", {})
        if not assessment.get("questions"):
            raise HTTPException(409, "This historical document has no structured question contract. Its original export remains available.")
        return record, assessment

    def exercise_task(self, owner, exercise_id):
        with self.connect() as db:
            record, assessment = self.exercise_record(db, owner, exercise_id)
        brief = re.split(r"(?mi)^## (?:Verified solution|Corrig[^\n]*)\s*$", record.get("content", ""), maxsplit=1)[0]
        return {"schema_version": SCHEMA, "exercise_id": exercise_id, "title": record["title"], "brief": brief,
                "questions": [{key: q[key] for key in ("number", "prompt", "criterion", "points") if key in q}
                              for q in assessment["questions"]],
                "assessment_type": "learner_self_review", "automatic_grade": None,
                "notice": "Your written attempt is saved before the feedback. This document may already have been read with its solution; independence is not certified."}

    def exercise_attempt(self, owner, exercise_id, body):
        def save(db, _):
            record, assessment = self.exercise_record(db, owner, exercise_id)
            if set(body.answers) != {str(q["number"]) for q in assessment["questions"]}:
                raise HTTPException(422, "Submit one written answer for each numbered question, without extra keys.")
            attempt_id = "exa_" + uuid.uuid4().hex
            value = {"schema_version": SCHEMA, "id": attempt_id, "exercise_id": exercise_id,
                     "title": record["title"], "answers": body.answers, "reasoning": body.reasoning,
                     "created_at": datetime.now(timezone.utc).isoformat(), "persisted": True,
                     "assessment_type": "learner_self_review", "automatic_grade": None,
                     "independence_verified": False, "feedback": assessment,
                     "exercise_snapshot_sha256": hashlib.sha256(_json(record).encode()).hexdigest()}
            db.execute("INSERT INTO learning_exercise_attempts VALUES(?,?,?,?,?)",
                       (attempt_id, owner, exercise_id, _json(value), time.time()))
            return value
        return self.action(owner, "exercise:answer:" + exercise_id, body, save)

    def exercise_get_attempt(self, owner, attempt_id, db=None):
        if db is None:
            with self.connect() as connection:
                return self.exercise_get_attempt(owner, attempt_id, connection)
        row = db.execute("SELECT payload FROM learning_exercise_attempts WHERE owner_id=? AND id=?", (owner, attempt_id)).fetchone()
        if not row:
            raise HTTPException(404, "Attempt not found.")
        result = json.loads(row["payload"])
        reviews = db.execute("SELECT payload FROM learning_exercise_reviews WHERE owner_id=? AND attempt_id=? ORDER BY rowid", (owner, attempt_id)).fetchall()
        result["self_reviews"] = [json.loads(row["payload"]) for row in reviews]
        return result

    def exercise_attempts(self, owner, exercise_id):
        with self.connect() as db:
            self.exercise_record(db, owner, exercise_id)
            rows = db.execute("SELECT id FROM learning_exercise_attempts WHERE owner_id=? AND exercise_id=? ORDER BY rowid DESC LIMIT 100", (owner, exercise_id)).fetchall()
            return {"attempts": [self.exercise_get_attempt(owner, row["id"], db) for row in rows]}

    def exercise_review(self, owner, attempt_id, body):
        def save(db, _):
            attempt = self.exercise_get_attempt(owner, attempt_id, db)
            if set(body.criteria) != set(attempt["answers"]):
                raise HTTPException(422, "Self-review each numbered answer; unknown or missing criteria are rejected.")
            value = {"id": "exr_" + uuid.uuid4().hex, "attempt_id": attempt_id,
                     "criteria": body.criteria, "notes": body.notes,
                     "created_at": datetime.now(timezone.utc).isoformat(),
                     "assessment_type": "learner_self_review", "automatic_grade": None}
            db.execute("INSERT INTO learning_exercise_reviews VALUES(?,?,?,?,?)",
                       (value["id"], owner, attempt_id, _json(value), time.time()))
            return value
        return self.action(owner, "exercise:review:" + attempt_id, body, save)


def _notebook(notebook_id):
    item = NOTEBOOKS.get(notebook_id)
    if not item:
        raise HTTPException(404, "Notebook not found.")
    return item


def run_notebook(notebook_id, ticket=None):
    item = _notebook(notebook_id)
    params = dict(item["ticket"] if ticket is None else ticket)
    if set(params) != set(item["ticket"]):
        raise HTTPException(422, "Provide exactly the named parameters in this notebook's ticket.")
    for key, value in params.items():
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or abs(value) > 1e12:
            raise HTTPException(422, "Notebook parameters must be bounded finite numbers.")
    if notebook_id == "black-scholes-intro":
        from .builtin_notebooks.black_scholes_intro import run
        if not (0 < params["spot"] <= 1e9 and 0 < params["strike"] <= 1e9
                and abs(params["rate"]) <= .5 and abs(params["dividend_yield"]) <= .5
                and 0 < params["volatility"] <= 3 and 0 < params["maturity_years"] <= 30):
            raise HTTPException(422, "Use positive spot/strike, rate and yield within ±50%, volatility ≤300%, maturity ≤30 years.")
    else:
        from .builtin_notebooks.barrier_down_out import run
    try:
        return run(params)
    except (ValueError, OverflowError, TypeError) as exc:
        raise HTTPException(422, str(exc)) from exc


def notebook_export(notebook_id, format):
    item = _notebook(notebook_id)
    if format == "py":
        return item["code"], "text/x-python", item["id"] + ".py"
    document = {"nbformat": 4, "nbformat_minor": 5,
                "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                             "language_info": {"name": "python"}},
                "cells": [{"id": "instructions", "cell_type": "markdown", "metadata": {},
                           "source": [f"# {item['title']}\n", item["description"] + "\n", "\n".join(item["limitations"])]},
                          {"id": "calculation", "cell_type": "code", "metadata": {},
                           "execution_count": None, "outputs": [], "source": item["code"].splitlines(keepends=True)}]}
    return json.dumps(document, ensure_ascii=False, indent=2), "application/x-ipynb+json", item["filename"]


def _csv(rows, delimiter=","):
    output = io.StringIO(newline="")
    writer = csv.writer(output, delimiter=delimiter, lineterminator="\n")
    # Text from learner answers is never interpreted as an Excel formula.
    for row in rows:
        writer.writerow([("'" + cell if cell.lstrip().startswith(("=", "+", "-", "@")) else cell)
                         if isinstance(cell, str) else cell for cell in row])
    return output.getvalue()


def interview_portable(state, format):
    if format == "report":
        lines = ["# Pricing & Greeks practice record", "", "Private learning record; no expert grade, hiring certification or proctored result.", ""]
        for attempt in state["attempts"]:
            lines += [f"## {attempt['task_snapshot']['title']} — {attempt['variant']}",
                      f"Recorded: {attempt['created_at']}",
                      f"Numerical check: {'within tolerance' if attempt['numerical_pass'] else 'needs revision'}.",
                      f"First attempt without recorded correction exposure: {bool(attempt['independent'])}; not proctored.", ""]
            for question in attempt["task_snapshot"]["questions"]:
                lines.append(f"- {question['label']}: {attempt['answers'].get(question['id'])} {question['unit']}")
            lines += [f"Reasoning self-review recorded: {bool(attempt.get('self_review'))}.", ""]
        if not state["attempts"]:
            lines.append("No submitted attempt recorded. Open a case and save your own answer first.")
        lines += ["", "Personal reasoning and account identifiers are omitted from this portable report. Use the private JSON export for your full record."]
        return "\n".join(lines) + "\n", "text/markdown", "tpl-practice-report.md"
    if format == "csv":
        rows = [["case_id", "variant", "attempt_at", "question", "answer", "unit", "within_tolerance", "recorded_independent", "self_reviewed"]]
        for attempt in state["attempts"]:
            for q in attempt["task_snapshot"]["questions"]:
                rows.append([attempt["case_id"], attempt["variant"], attempt["created_at"], q["label"],
                             attempt["answers"].get(q["id"]), q["unit"], attempt["numerical_pass"],
                             attempt["independent"], bool(attempt.get("self_review"))])
        return _csv(rows), "text/csv", "tpl-practice-record.csv"
    rows = []
    # The revision deck must not reveal a still-unseen numerical correction and
    # subsequently let the same answer masquerade as an independent first try.
    exposed = {a["case_id"] for a in state["attempts"] if a["variant"] == "primary"}
    exposed.update(e["case_id"] for e in state.get("exposures", []) if e["variant"] == "primary")
    if not exposed:
        raise HTTPException(409, "Attempt a primary case or explicitly reveal its correction before exporting its revision cards.")
    for case_id in CASE_IDS:
        if case_id not in exposed:
            continue
        case = _full_case(case_id, "primary")
        context = _json(case["ticket"])
        for question in case["questions"]:
            rows.append([f"{case['title']} — {question['label']}. Ticket: {context}",
                         f"{question['expected']:.6g} {question['unit']}. {question['explanation']}",
                         "TPL::PricingAndGreeks " + case_id])
    # Anki comment headers are not imported as a bogus Front/Back flashcard.
    # The first field is stable for re-import deduplication; no invented Anki
    # internal GUID or claim of a live synchronisation is introduced.
    headers = "#separator:Tab\n#html:false\n#columns:Front\tBack\tTags\n#tags column:3\n"
    return headers + _csv(rows, "\t"), "text/tab-separated-values", "tpl-pricing-greeks-anki.tsv"


def study_calendar(body):
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//ThePricingLibrary//Study Plan 1//EN", "CALSCALE:GREGORIAN", "METHOD:PUBLISH"]
    start = body.starts_at.astimezone(timezone.utc)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    for index in range(body.sessions):
        case_id = CASE_IDS[index % len(CASE_IDS)]
        at = start + timedelta(days=index * 2)
        uid = hashlib.sha256(f"{case_id}:{at.isoformat()}:{body.minutes}".encode()).hexdigest()[:28]
        lines += ["BEGIN:VEVENT", f"UID:{uid}@thepricinglibrary.com", f"DTSTAMP:{stamp}",
                  "DTSTART:" + at.strftime("%Y%m%dT%H%M%SZ"),
                  "DTEND:" + (at + timedelta(minutes=body.minutes)).strftime("%Y%m%dT%H%M%SZ"),
                  "SUMMARY:TPL - Pricing and Greeks practice", "DESCRIPTION:Voluntary study plan. Not a record of attendance.",
                  f"URL:https://thepricinglibrary.com/interview/{case_id}", "END:VEVENT"]
    # RFC 5545 content lines use CRLF and fold at 75 UTF-8 octets without
    # splitting a character. A continuation's leading space counts as an octet.
    folded = []
    for line in [*lines, "END:VCALENDAR"]:
        current = ""
        for character in line:
            if len((current + character).encode("utf-8")) > 75:
                folded.append(current)
                current = " "
            current += character
        folded.append(current)
    return "\r\n".join([*folded, ""])


def register_learning_routes(app: FastAPI, services, security):
    store = LearningStore(services.settings.db_path)
    platform = PlatformStore(services.settings.db_path)
    lab = InterviewLabStore(services.settings.db_path)
    app.state.learning_store = store

    def identity(request, plan=None):
        signed = getattr(request.state, "tpl_identity", None)
        if not isinstance(signed, AuthenticatedIdentity):
            security.authorize(request, IDENTITY)
            signed = getattr(request.state, "tpl_identity", None)
        if not isinstance(signed, AuthenticatedIdentity):
            raise HTTPException(401, "A verified learner identity is required.")
        if plan and signed.role != OPERATOR and (services.settings.security_enforced or services.settings.enforce_entitlements):
            entitlement = services.store.get_entitlement_by_user_id(signed.user_id) or {}
            rank = {"starter": 1, "student": 2, "pro": 3}
            if entitlement.get("status") not in ("active", "trialing") or rank.get(entitlement.get("plan"), 0) < rank[plan]:
                raise HTTPException(403, f"This learning workspace requires the {plan} plan.")
        return signed

    def private(response):
        response.headers["Cache-Control"] = "private, no-store"
        response.headers["Vary"] = "Authorization"

    def attachment(content, media_type, filename):
        return Response(content, media_type=media_type,
                        headers={"Cache-Control": "private, no-store", "Vary": "Authorization",
                                 "X-Content-Type-Options": "nosniff", "Content-Disposition": f'attachment; filename="{filename}"'})

    @app.get("/learning/catalog")
    def catalog(request: Request, response: Response):
        identity(request); private(response)
        return {"schema_version": SCHEMA, "survival": {"wave": "core", "question_count": 20, "seconds_per_question": 30, "lives": 3, "minimum_plan": "student", "ranked": False},
                "notebooks": [{key: item[key] for key in ("id", "title", "language", "description", "limitations")} for item in NOTEBOOKS.values()],
                "exercise_attempts": {"minimum_plan": "starter", "assessment_type": "learner_self_review", "automatic_grade": None},
                "practice_exercises": [{key: item[key] for key in ("id", "title", "cat", "level", "time", "courseIds") if key in item}
                                       for item in PRACTICE_EXERCISES.values()],
                "interview_exports": ["report", "csv", "anki", "calendar"]}

    @app.get("/learning/notebooks")
    def notebooks(request: Request, response: Response):
        identity(request, "student"); private(response)
        return {"schema_version": SCHEMA, "notebooks": list(NOTEBOOKS.values())}

    @app.get("/learning/notebooks/{notebook_id}")
    def notebook(notebook_id: str, request: Request, response: Response):
        identity(request, "student"); private(response)
        return _notebook(notebook_id)

    @app.get("/learning/notebooks/{notebook_id}/export")
    def export_notebook(notebook_id: str, request: Request, format: Literal["ipynb", "py"] = "ipynb"):
        identity(request, "student")
        return attachment(*notebook_export(notebook_id, format))

    @app.post("/learning/notebooks/{notebook_id}/run")
    def execute_notebook(notebook_id: str, body: NotebookRun, request: Request, response: Response):
        identity(request, "student"); private(response)
        return run_notebook(notebook_id, body.ticket)

    @app.post("/learning/survival/runs")
    def survival_start(body: SurvivalStart, request: Request, response: Response):
        owner = identity(request, "student").user_id; private(response)
        return store.survival_start(owner, body)

    @app.get("/learning/survival/runs")
    def survival_list(request: Request, response: Response):
        owner = identity(request, "student").user_id; private(response)
        return store.survival_list(owner)

    @app.get("/learning/survival/runs/{run_id}")
    def survival_get(run_id: str, request: Request, response: Response):
        owner = identity(request, "student").user_id; private(response)
        return store.survival_get(owner, run_id)

    @app.post("/learning/survival/runs/{run_id}/answers")
    def survival_answer(run_id: str, body: SurvivalAnswer, request: Request, response: Response):
        owner = identity(request, "student").user_id; private(response)
        return store.survival_answer(owner, run_id, body)

    @app.post("/learning/survival/runs/{run_id}/next")
    def survival_next(run_id: str, body: ActionBody, request: Request, response: Response):
        owner = identity(request, "student").user_id; private(response)
        result = store.survival_next(owner, run_id, body)
        if result["completed"]:
            platform.record_progress(user_id=owner, username=None, kind="survival", ref="server-run:" + run_id,
                                     score=None, meta={"run_id": run_id, "ranked": False, "assessment_type": "timed_practice"})
        return result

    @app.get("/learning/exercises/{exercise_id}/task")
    def exercise_task(exercise_id: str, request: Request, response: Response):
        owner = identity(request, "starter").user_id; private(response)
        return store.exercise_task(owner, exercise_id)

    @app.get("/learning/exercises/{exercise_id}/reference")
    def practice_reference(exercise_id: str, request: Request, response: Response):
        identity(request, "starter"); private(response)
        if exercise_id not in PRACTICE_REFERENCES:
            raise HTTPException(404, "Authored executable reference not found. Generated exercises retain their original worked correction.")
        return PRACTICE_REFERENCES[exercise_id]

    @app.post("/learning/exercises/{exercise_id}/reference/run")
    def execute_reference(exercise_id: str, body: StrictBody, request: Request, response: Response):
        identity(request, "starter"); private(response)
        if exercise_id not in PRACTICE_REFERENCES:
            raise HTTPException(404, "Authored executable reference not found.")
        from .practice_references import run_reference
        return run_reference(exercise_id)

    @app.get("/learning/exercises/{exercise_id}/reference/export")
    def export_practice_reference(exercise_id: str, request: Request, format: Literal["python", "ipynb"] = "python"):
        identity(request, "starter")
        if exercise_id not in PRACTICE_REFERENCES:
            raise HTTPException(404, "Authored executable reference not found.")
        from .practice_references import export_reference
        return attachment(export_reference(exercise_id, format),
                          "text/x-python" if format == "python" else "application/x-ipynb+json",
                          exercise_id + (".py" if format == "python" else ".ipynb"))

    @app.get("/learning/exercises/{exercise_id}/attempts")
    def exercise_attempts(exercise_id: str, request: Request, response: Response):
        owner = identity(request, "starter").user_id; private(response)
        return store.exercise_attempts(owner, exercise_id)

    @app.post("/learning/exercises/{exercise_id}/attempts")
    def exercise_answer(exercise_id: str, body: WrittenAttempt, request: Request, response: Response):
        owner = identity(request, "starter").user_id; private(response)
        return store.exercise_attempt(owner, exercise_id, body)

    @app.get("/learning/exercise-attempts/{attempt_id}")
    def attempt_get(attempt_id: str, request: Request, response: Response):
        owner = identity(request, "starter").user_id; private(response)
        return store.exercise_get_attempt(owner, attempt_id)

    @app.post("/learning/exercise-attempts/{attempt_id}/review")
    def attempt_review(attempt_id: str, body: WrittenReview, request: Request, response: Response):
        owner = identity(request, "starter").user_id; private(response)
        return store.exercise_review(owner, attempt_id, body)

    @app.get("/learning/exercise-attempts/{attempt_id}/export")
    def attempt_export(attempt_id: str, request: Request, format: Literal["json", "md"] = "json"):
        owner = identity(request, "starter").user_id
        value = store.exercise_get_attempt(owner, attempt_id)
        if format == "json":
            return attachment(json.dumps(value, ensure_ascii=False, indent=2), "application/json", attempt_id + ".json")
        lines = ["# Written exercise attempt", value["title"], "Self-review practice; no automatic grade or certified mastery."]
        for number, answer in value["answers"].items():
            lines += [f"## Answer {number}", answer]
        lines += ["## Worked correction", _json(value["feedback"]), "## Self-reviews", _json(value["self_reviews"])]
        return attachment("\n\n".join(lines), "text/markdown", attempt_id + ".md")

    @app.get("/learning/interview/export")
    def portable_interview(request: Request, format: Literal["report", "csv", "anki"] = "report"):
        owner = identity(request).user_id
        return attachment(*interview_portable(lab.state(owner), format))

    @app.post("/learning/interview/calendar")
    def calendar(body: StudyCalendar, request: Request):
        identity(request)
        return attachment(study_calendar(body), "text/calendar", "tpl-study-plan.ics")
