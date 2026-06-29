"""Smoke test for the local platform API (community/jobs/blog/progress/...).

Runs in-process against a TEMP SQLite DB (no OpenAI, no network). Asserts every
CRUD round-trip persists and reads back. Exit 0 = platform API functional.

    python scripts/smoke_platform.py
"""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# Isolate: temp DB + offline provider, set BEFORE importing the app.
_tmpdir = tempfile.mkdtemp(prefix="tpl_platform_smoke_")
os.environ["TPL_DB_PATH"] = str(Path(_tmpdir) / "smoke.sqlite3")
os.environ["TPL_DATA_DIR"] = _tmpdir
os.environ["TPL_LLM_PROVIDER"] = "template"

from starlette.testclient import TestClient  # noqa: E402

from pricinglibrary_rag.api import app  # noqa: E402

c = TestClient(app, raise_server_exceptions=False)
FAILS: list[str] = []
N = 0


def check(cond: bool, label: str, extra: str = "") -> None:
    global N
    N += 1
    print(f"  [{'ok ' if cond else 'FAIL'}] {label}{(' - ' + extra) if extra and not cond else ''}")
    if not cond:
        FAILS.append(label)


print("=" * 64)
print("PLATFORM API SMOKE")

r = c.get("/platform/health")
check(r.status_code == 200 and r.json().get("status") == "ok", "GET /platform/health", r.text[:120])

# --- community ---
r = c.post("/platform/community/threads", json={"channel": "forum", "title": "Pricing a digital", "body": "How to hedge a digital near expiry?", "author": "quanta"})
check(r.status_code == 200 and r.json().get("id"), "create thread", r.text[:120])
tid = r.json().get("id")
r = c.get("/platform/community/threads")
threads = r.json().get("threads", [])
check(any(t["id"] == tid for t in threads), "thread appears in list")
r = c.post(f"/platform/community/threads/{tid}/comments", json={"body": "Use a tight call spread.", "author": "mentor"})
check(r.status_code == 200, "add comment")
r = c.get(f"/platform/community/threads/{tid}/comments")
check(len(r.json().get("comments", [])) == 1, "comment persisted")
r = c.post(f"/platform/community/threads/{tid}/vote", json={})
check(r.status_code == 200 and r.json().get("votes") == 1, "vote increments")
r = c.post("/platform/community/threads/does-not-exist/comments", json={"body": "x", "author": "y"})
check(r.status_code == 404, "comment on missing thread -> 404")

# --- jobs ---
r = c.post("/platform/jobs", json={"title": "Junior Quant", "company": "DeskCo", "location": "Paris", "kind": "full-time", "tags": ["pricing", "python"]})
check(r.status_code == 200 and r.json().get("id"), "create job")
jid = r.json().get("id")
r = c.post(f"/platform/jobs/{jid}/apply", json={"applicant": "jordan@desk.com", "note": "Keen on rates."})
check(r.status_code == 200, "apply to job")
r = c.get("/platform/jobs")
check(any(j["id"] == jid for j in r.json().get("jobs", [])), "job appears in list")

# --- bug reports ---
r = c.post("/platform/bug-reports", json={"summary": "Chart axis flips", "severity": "low", "reporter": "qa@x.com"})
check(r.status_code == 200 and r.json().get("status") == "open", "create bug report")

# --- newsletter ---
r = c.post("/platform/newsletter", json={"email": "Reader@X.com"})
check(r.status_code == 200 and r.json().get("subscribed"), "newsletter subscribe")
r = c.post("/platform/newsletter", json={"email": "reader@x.com"})
check(r.status_code == 200, "newsletter subscribe is idempotent (no dup error)")

# --- progress + leaderboard ---
for i in range(3):
    c.post("/platform/progress", json={"user_id": "u1", "username": "alice", "kind": "lesson", "ref": f"vanilla#L{i}", "score": 10, "meta": {"course": "vanilla"}})
c.post("/platform/progress", json={"user_id": "u1", "username": "alice", "kind": "quiz", "ref": "vanilla-quiz", "score": 80})
c.post("/platform/progress", json={"user_id": "u2", "username": "bob", "kind": "lesson", "ref": "swap#L0", "score": 5, "meta": {"course": "swap"}})
r = c.get("/platform/progress/u1")
summ = r.json()
check(summ.get("events") == 4, "progress summary counts events", str(summ.get("events")))
check(any(ccc["course"] == "vanilla" for ccc in summ.get("courses", [])), "course progress derived")
r = c.get("/platform/leaderboard")
lb = r.json().get("leaderboard", [])
check(len(lb) >= 2 and lb[0]["username"] == "alice" and lb[0]["points"] >= lb[-1]["points"], "leaderboard ranks by points", str(lb[:2]))

# --- survival ---
c.post("/platform/survival", json={"username": "alice", "wave": "advanced", "score": 1200, "streak": 7})
c.post("/platform/survival", json={"username": "bob", "wave": "beginner", "score": 800})
r = c.get("/platform/survival/leaderboard")
sl = r.json().get("leaderboard", [])
check(sl and sl[0]["username"] == "alice" and sl[0]["score"] == 1200, "survival leaderboard top", str(sl[:2]))

# --- blog ---
r = c.post("/platform/blog", json={"slug": "delta-hedging-101", "title": "Delta hedging 101", "author": "Desk", "excerpt": "Intro", "body": "# Body\nReal content", "tags": ["greeks"], "read_minutes": 6})
check(r.status_code == 200, "upsert blog post")
r = c.get("/platform/blog/delta-hedging-101")
check(r.status_code == 200 and "Real content" in (r.json().get("body") or ""), "blog body persisted")
r = c.get("/platform/blog")
check(any(p["slug"] == "delta-hedging-101" for p in r.json().get("posts", [])), "blog appears in index")
r = c.get("/platform/blog/missing")
check(r.status_code == 404, "missing blog -> 404")

print("=" * 64)
if FAILS:
    print(f"PLATFORM SMOKE: FAIL ({len(FAILS)}/{N})")
    for f in FAILS:
        print("  -", f)
    sys.exit(1)
print(f"PLATFORM SMOKE: PASS ({N}/{N} checks)")
