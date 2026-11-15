"""Local platform data store (community, jobs, leaderboard, blog, progress...).

Real persistence for the website features that used to render hardcoded mock
arrays. SQLite-backed, self-contained, and Dockerizable for a VPS. Production
callers pass only identities derived from a verified JWT at the API boundary;
client-declared ids and author names are never authoritative.
"""
from __future__ import annotations

import json
import sqlite3
import time
import uuid
from pathlib import Path
from typing import Any


def _now() -> int:
    return int(time.time())


def _uid(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


class PlatformStore:
    def __init__(self, db_path: str | Path) -> None:
        self.db_path = str(db_path)
        self._init_schema()
        self._migrate()

    def _migrate(self) -> None:
        """Idempotent additive migrations (real sourced-jobs need an apply URL
        and a dedup key). Safe to run on every boot."""
        with self._connect() as conn:
            columns = {row[1] for row in conn.execute("PRAGMA table_info(platform_exercises)")}
            if "client_request_id" not in columns:
                conn.execute("ALTER TABLE platform_exercises ADD COLUMN client_request_id TEXT")
            conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS ux_exercise_request ON platform_exercises(user_id,client_request_id)")
            for col, ddl in (("url", "TEXT"), ("source", "TEXT"),
                             ("external_id", "TEXT"), ("remote", "INTEGER")):
                try:
                    conn.execute(f"ALTER TABLE platform_jobs ADD COLUMN {col} {ddl}")
                except sqlite3.OperationalError:
                    pass  # column already exists
            # NULLs are allowed multiple times in a UNIQUE index, so legacy
            # manually-posted jobs (external_id NULL) are unaffected.
            conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS ux_jobs_external "
                         "ON platform_jobs(external_id)")
            try:
                conn.execute("ALTER TABLE platform_survival ADD COLUMN verified INTEGER NOT NULL DEFAULT 0")
            except sqlite3.OperationalError:
                pass
            # Collapse historical duplicate activity events before enforcing
            # the atomic idempotency key used by concurrent API requests.
            conn.execute(
                "DELETE FROM platform_progress WHERE rowid NOT IN ("
                "SELECT MIN(rowid) FROM platform_progress GROUP BY user_id,kind,ref)"
            )
            conn.execute(
                "CREATE UNIQUE INDEX IF NOT EXISTS ux_progress_identity_event "
                "ON platform_progress(user_id,kind,ref)"
            )

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS platform_threads (
                    id TEXT PRIMARY KEY, channel TEXT NOT NULL, title TEXT NOT NULL,
                    body TEXT NOT NULL, author TEXT NOT NULL, author_id TEXT,
                    tags TEXT, votes INTEGER NOT NULL DEFAULT 0,
                    comment_count INTEGER NOT NULL DEFAULT 0, created_at INTEGER NOT NULL
                );
                CREATE TABLE IF NOT EXISTS platform_comments (
                    id TEXT PRIMARY KEY, thread_id TEXT NOT NULL, body TEXT NOT NULL,
                    author TEXT NOT NULL, author_id TEXT, created_at INTEGER NOT NULL,
                    FOREIGN KEY(thread_id) REFERENCES platform_threads(id) ON DELETE CASCADE
                );
                CREATE TABLE IF NOT EXISTS platform_thread_votes (
                    thread_id TEXT NOT NULL, voter_id TEXT NOT NULL,
                    created_at INTEGER NOT NULL,
                    PRIMARY KEY(thread_id, voter_id),
                    FOREIGN KEY(thread_id) REFERENCES platform_threads(id) ON DELETE CASCADE
                );
                CREATE TABLE IF NOT EXISTS platform_jobs (
                    id TEXT PRIMARY KEY, title TEXT NOT NULL, company TEXT NOT NULL,
                    location TEXT, kind TEXT, tags TEXT, description TEXT,
                    posted_by TEXT, created_at INTEGER NOT NULL
                );
                CREATE TABLE IF NOT EXISTS platform_job_applications (
                    id TEXT PRIMARY KEY, job_id TEXT NOT NULL, applicant TEXT NOT NULL,
                    note TEXT, created_at INTEGER NOT NULL,
                    FOREIGN KEY(job_id) REFERENCES platform_jobs(id) ON DELETE CASCADE
                );
                CREATE TABLE IF NOT EXISTS platform_bug_reports (
                    id TEXT PRIMARY KEY, kind TEXT, severity TEXT, summary TEXT NOT NULL,
                    detail TEXT, reporter TEXT, status TEXT NOT NULL DEFAULT 'open',
                    created_at INTEGER NOT NULL
                );
                CREATE TABLE IF NOT EXISTS platform_newsletter (
                    email TEXT PRIMARY KEY, source TEXT, created_at INTEGER NOT NULL
                );
                CREATE TABLE IF NOT EXISTS platform_progress (
                    id TEXT PRIMARY KEY, user_id TEXT NOT NULL, username TEXT,
                    kind TEXT NOT NULL, ref TEXT, score REAL, meta TEXT,
                    created_at INTEGER NOT NULL
                );
                CREATE TABLE IF NOT EXISTS platform_course_positions (
                    user_id TEXT NOT NULL, course TEXT NOT NULL,
                    module_index INTEGER NOT NULL, updated_at INTEGER NOT NULL,
                    PRIMARY KEY(user_id, course)
                );
                CREATE TABLE IF NOT EXISTS platform_exercises (
                    id TEXT PRIMARY KEY, user_id TEXT NOT NULL,
                    request_json TEXT NOT NULL, response_json TEXT NOT NULL,
                    created_at INTEGER NOT NULL
                );
                CREATE INDEX IF NOT EXISTS ix_exercises_owner ON platform_exercises(user_id, created_at DESC);
                CREATE TABLE IF NOT EXISTS platform_survival (
                    id TEXT PRIMARY KEY, user_id TEXT, username TEXT NOT NULL,
                    wave TEXT, score INTEGER NOT NULL, streak INTEGER DEFAULT 0,
                    created_at INTEGER NOT NULL
                );
                CREATE TABLE IF NOT EXISTS platform_blog (
                    slug TEXT PRIMARY KEY, title TEXT NOT NULL, author TEXT,
                    excerpt TEXT, body TEXT, tags TEXT, read_minutes INTEGER,
                    published_at INTEGER NOT NULL
                );
                CREATE INDEX IF NOT EXISTS ix_threads_created ON platform_threads(created_at DESC);
                CREATE INDEX IF NOT EXISTS ix_progress_user ON platform_progress(user_id, created_at DESC);
                CREATE INDEX IF NOT EXISTS ix_survival_score ON platform_survival(score DESC);
                """
            )

    # --- community ---------------------------------------------------------
    def list_threads(self, channel: str | None = None, limit: int = 50) -> list[dict]:
        q = "SELECT * FROM platform_threads"
        args: list[Any] = []
        if channel and channel != "all":
            q += " WHERE channel = ?"
            args.append(channel)
        q += " ORDER BY created_at DESC LIMIT ?"
        args.append(limit)
        with self._connect() as conn:
            return [self._thread(r) for r in conn.execute(q, args).fetchall()]

    def create_thread(self, *, channel: str, title: str, body: str, author: str,
                      author_id: str | None = None, tags: list[str] | None = None) -> dict:
        tid = _uid("thr")
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO platform_threads(id,channel,title,body,author,author_id,tags,votes,comment_count,created_at)"
                " VALUES(?,?,?,?,?,?,?,0,0,?)",
                (tid, channel, title, body, author, author_id, json.dumps(tags or []), _now()),
            )
            return self._thread(conn.execute("SELECT * FROM platform_threads WHERE id=?", (tid,)).fetchone())

    def vote_thread(self, thread_id: str, delta: int = 1, *, voter_id: str | None = None) -> dict | None:
        with self._connect() as conn:
            if not conn.execute("SELECT 1 FROM platform_threads WHERE id=?", (thread_id,)).fetchone():
                return None
            should_increment = True
            if voter_id:
                cur = conn.execute(
                    "INSERT OR IGNORE INTO platform_thread_votes(thread_id,voter_id,created_at) VALUES(?,?,?)",
                    (thread_id, voter_id, _now()),
                )
                should_increment = cur.rowcount > 0
            if should_increment:
                # Public votes are one signed account = one positive vote.
                # ``delta`` remains in the local store signature for backwards
                # compatible seed scripts but cannot amplify an identified vote.
                increment = 1 if voter_id else max(-1, min(1, int(delta)))
                conn.execute("UPDATE platform_threads SET votes=votes+? WHERE id=?", (increment, thread_id))
            return self._thread(conn.execute("SELECT * FROM platform_threads WHERE id=?", (thread_id,)).fetchone())

    def list_comments(self, thread_id: str) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM platform_comments WHERE thread_id=? ORDER BY created_at ASC", (thread_id,)
            ).fetchall()
            return [dict(id=r["id"], thread_id=r["thread_id"], body=r["body"], author=r["author"],
                        created_at=r["created_at"]) for r in rows]

    def add_comment(self, *, thread_id: str, body: str, author: str, author_id: str | None = None) -> dict | None:
        with self._connect() as conn:
            if not conn.execute("SELECT 1 FROM platform_threads WHERE id=?", (thread_id,)).fetchone():
                return None
            cid = _uid("cmt")
            conn.execute(
                "INSERT INTO platform_comments(id,thread_id,body,author,author_id,created_at) VALUES(?,?,?,?,?,?)",
                (cid, thread_id, body, author, author_id, _now()),
            )
            conn.execute("UPDATE platform_threads SET comment_count=comment_count+1 WHERE id=?", (thread_id,))
            return dict(id=cid, thread_id=thread_id, body=body, author=author, created_at=_now())

    # --- jobs --------------------------------------------------------------
    def list_jobs(self, kind: str | None = None, limit: int = 100) -> list[dict]:
        q = "SELECT * FROM platform_jobs"
        args: list[Any] = []
        if kind and kind != "all":
            q += " WHERE kind = ?"
            args.append(kind)
        q += " ORDER BY created_at DESC LIMIT ?"
        args.append(limit)
        with self._connect() as conn:
            return [self._job(r) for r in conn.execute(q, args).fetchall()]

    def create_job(self, *, title: str, company: str, location: str | None, kind: str | None,
                   tags: list[str] | None, description: str | None, posted_by: str | None,
                   url: str | None = None, source: str | None = None, remote: bool = False) -> dict:
        jid = _uid("job")
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO platform_jobs(id,title,company,location,kind,tags,description,posted_by,created_at,url,source,remote)"
                " VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
                (jid, title, company, location, kind, json.dumps(tags or []), description, posted_by,
                 _now(), url, source, 1 if remote else 0),
            )
            return self._job(conn.execute("SELECT * FROM platform_jobs WHERE id=?", (jid,)).fetchone())

    def upsert_job(self, *, external_id: str, title: str, company: str, location: str | None,
                   kind: str | None, tags: list[str] | None, description: str | None,
                   url: str | None, source: str, remote: bool = False) -> str:
        """Insert a sourced job, deduped by external_id. Returns 'inserted' or 'skipped'."""
        with self._connect() as conn:
            exists = conn.execute("SELECT 1 FROM platform_jobs WHERE external_id=?", (external_id,)).fetchone()
            if exists:
                return "skipped"
            conn.execute(
                "INSERT OR IGNORE INTO platform_jobs(id,title,company,location,kind,tags,description,"
                "posted_by,created_at,url,source,external_id,remote) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (_uid("job"), title, company, location, kind, json.dumps(tags or []), description,
                 source, _now(), url, source, external_id, 1 if remote else 0),
            )
            return "inserted"

    def clear_sourced_jobs(self) -> int:
        """Delete only auto-sourced jobs (source IS NOT NULL); keep manual posts."""
        with self._connect() as conn:
            cur = conn.execute("DELETE FROM platform_jobs WHERE source IS NOT NULL")
            return cur.rowcount

    def jobs_source_counts(self) -> dict:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT COALESCE(source,'manual') s, COUNT(*) n FROM platform_jobs GROUP BY s"
            ).fetchall()
            return {r["s"]: r["n"] for r in rows}

    def apply_job(self, *, job_id: str, applicant: str, note: str | None) -> dict | None:
        with self._connect() as conn:
            if not conn.execute("SELECT 1 FROM platform_jobs WHERE id=?", (job_id,)).fetchone():
                return None
            aid = _uid("app")
            conn.execute(
                "INSERT INTO platform_job_applications(id,job_id,applicant,note,created_at) VALUES(?,?,?,?,?)",
                (aid, job_id, applicant, note, _now()),
            )
            return dict(id=aid, job_id=job_id, applicant=applicant, note=note, created_at=_now())

    # --- bug reports -------------------------------------------------------
    def create_bug(self, *, kind: str | None, severity: str | None, summary: str,
                   detail: str | None, reporter: str | None) -> dict:
        bid = _uid("bug")
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO platform_bug_reports(id,kind,severity,summary,detail,reporter,status,created_at)"
                " VALUES(?,?,?,?,?,?, 'open', ?)",
                (bid, kind, severity, summary, detail, reporter, _now()),
            )
        return dict(id=bid, kind=kind, severity=severity, summary=summary, detail=detail,
                    reporter=reporter, status="open", created_at=_now())

    def list_bugs(self, limit: int = 100) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM platform_bug_reports ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
            return [dict(r) for r in rows]

    # --- newsletter --------------------------------------------------------
    def subscribe(self, email: str, source: str | None = None) -> dict:
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO platform_newsletter(email,source,created_at) VALUES(?,?,?)"
                " ON CONFLICT(email) DO NOTHING",
                (email.lower().strip(), source, _now()),
            )
        return {"email": email.lower().strip(), "subscribed": True}

    def subscriber_count(self) -> int:
        with self._connect() as conn:
            return conn.execute("SELECT COUNT(*) c FROM platform_newsletter").fetchone()["c"]

    # --- private generated exercise library -------------------------------
    def save_exercise(self, *, user_id: str, request: dict, response: dict) -> dict:
        exercise_id, created = _uid("exo"), _now()
        response = {**response, "metadata": {**response.get("metadata", {}),
                    "library_id": exercise_id, "created_at": created, "persistence": "account", "owner_id": user_id}}
        with self._connect() as conn:
            inserted = conn.execute("INSERT OR IGNORE INTO platform_exercises(id,user_id,request_json,response_json,created_at,client_request_id) VALUES(?,?,?,?,?,?)",
                         (exercise_id, user_id, json.dumps(request, ensure_ascii=False),
                          json.dumps(response, ensure_ascii=False), created, request.get("client_request_id")))
            if inserted.rowcount == 0:
                existing = self.get_exercise_request(user_id, request["client_request_id"])
                if existing and existing["request"] == request:
                    return existing
                raise ValueError("Cette tentative utilise déjà d’autres paramètres. Relance une nouvelle création.")
        return {"id": exercise_id, "created_at": created, "request": request, "response": response}

    def list_exercises(self, user_id: str, limit: int = 100, offset: int = 0) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute("SELECT id,request_json,response_json,created_at FROM platform_exercises WHERE user_id=? ORDER BY created_at DESC,rowid DESC LIMIT ? OFFSET ?",
                                (user_id, max(1, min(limit, 100)), max(0,offset))).fetchall()
        return [{"id": r["id"], "created_at": r["created_at"], "request": json.loads(r["request_json"]),
                 "response": json.loads(r["response_json"])} for r in rows]

    def get_exercise(self, user_id: str, exercise_id: str) -> dict | None:
        with self._connect() as conn:
            row = conn.execute("SELECT id,request_json,response_json,created_at FROM platform_exercises WHERE id=? AND user_id=?",
                               (exercise_id, user_id)).fetchone()
        return {"id": row["id"], "created_at": row["created_at"], "request": json.loads(row["request_json"]),
                "response": json.loads(row["response_json"])} if row else None

    def get_exercise_request(self, user_id: str, request_id: str) -> dict | None:
        with self._connect() as conn:
            row = conn.execute("SELECT id FROM platform_exercises WHERE user_id=? AND client_request_id=?", (user_id, request_id)).fetchone()
        return self.get_exercise(user_id, row["id"]) if row else None

    # --- progress + leaderboard -------------------------------------------
    def record_progress(self, *, user_id: str, username: str | None, kind: str,
                        ref: str | None, score: float | None, meta: dict | None) -> dict:
        pid = _uid("prg")
        with self._connect() as conn:
            inserted = conn.execute(
                "INSERT OR IGNORE INTO platform_progress(id,user_id,username,kind,ref,score,meta,created_at)"
                " VALUES(?,?,?,?,?,?,?,?)",
                (pid, user_id, username, kind, ref, score, json.dumps(meta or {}), _now()),
            )
            if inserted.rowcount > 0:
                return {"id": pid, "ok": True, "created": True}
            existing = conn.execute(
                "SELECT id FROM platform_progress WHERE user_id=? AND kind=? AND ref=?",
                (user_id, kind, ref),
            ).fetchone()
            return {"id": existing["id"], "ok": True, "created": False}

    def progress_summary(self, user_id: str) -> dict:
        from .interview_lab import InterviewLabStore
        from .learning_workflows import LearningStore

        with self._connect() as conn:
            # One consistent read snapshot; no fabricated legacy completion or
            # score is created from an interview attempt or self-review.
            conn.execute("BEGIN")
            rows = conn.execute(
                "SELECT kind, ref, score, meta, created_at FROM platform_progress WHERE user_id=? ORDER BY created_at DESC",
                (user_id,),
            ).fetchall()
            positions = conn.execute(
                "SELECT course,module_index,updated_at FROM platform_course_positions WHERE user_id=? ORDER BY course",
                (user_id,),
            ).fetchall()
            interview = InterviewLabStore.progress_summary(conn, user_id)
            learning = LearningStore.progress_summary(conn, user_id)
        events = [dict(kind=r["kind"], ref=r["ref"], score=r["score"],
                       meta=json.loads(r["meta"] or "{}"), created_at=r["created_at"]) for r in rows]
        # day buckets for the heatmap (last 91 days)
        day = 86400
        today = (_now() // day) * day
        heat = {}
        for e in events:
            d = (e["created_at"] // day) * day
            heat[d] = heat.get(d, 0) + 1
        # per-course progress: fraction of distinct lessons completed events of kind 'lesson'
        courses: dict[str, set] = {}
        quizzes: list[dict] = []
        exercises: list[dict] = []
        for e in events:
            if e["kind"] == "lesson" and e["ref"]:
                cid = e["meta"].get("course") or e["ref"].split("#")[0]
                courses.setdefault(cid, set()).add(e["ref"])
            elif e["kind"] == "quiz":
                quizzes.append(e)
            elif e["kind"] == "exercise":
                exercises.append(e)
        scored = [e["score"] for e in events if e["score"] is not None]
        active_days = len({(e["created_at"] // day) for e in events})
        return {
            "events": len(events),
            "interview": interview,
            "learning": learning,
            "completed_lessons": sorted({e["ref"] for e in events if e["kind"] == "lesson" and e["ref"]}),
            "course_positions": [dict(row) for row in positions],
            "active_days": active_days,
            "heatmap": [{"day": d, "count": c} for d, c in sorted(heat.items())],
            "courses": [{"course": k, "lessons_done": len(v)} for k, v in courses.items()],
            "quizzes": quizzes[:20],
            "exercises": exercises[:20],
            "avg_score": round(sum(scored) / len(scored), 1) if scored else None,
            "today": today,
        }

    def course_position(self, user_id: str, course_id: str, module_index: int) -> dict:
        """Remember navigation separately from completed lessons and points."""
        now = _now()
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO platform_course_positions(user_id,course,module_index,updated_at) VALUES(?,?,?,?) "
                "ON CONFLICT(user_id,course) DO UPDATE SET module_index=excluded.module_index,updated_at=excluded.updated_at",
                (user_id, course_id, module_index, now),
            )
        return {"course":course_id,"module_index":module_index,"updated_at":now}

    def leaderboard(self, limit: int = 20) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT user_id, COALESCE(MAX(username),'member') AS username,
                       COALESCE(SUM(CASE kind
                           WHEN 'lesson' THEN 5
                           WHEN 'quiz' THEN 10
                           WHEN 'exercise' THEN 15
                           WHEN 'survival' THEN 10
                           ELSE 0 END),0) AS points,
                       COUNT(*) AS events
                FROM (
                    SELECT user_id, username, kind, ref
                    FROM platform_progress
                    GROUP BY user_id, kind, ref
                ) identity_bound_events
                GROUP BY user_id
                ORDER BY points DESC, events DESC, user_id ASC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [dict(rank=i + 1, username=r["username"],
                     points=round(r["points"] or 0, 1), events=r["events"])
                for i, r in enumerate(rows)]

    # --- survival ----------------------------------------------------------
    def record_survival(self, *, user_id: str | None, username: str, wave: str | None,
                        score: int, streak: int = 0, verified: bool = False) -> dict:
        sid = _uid("srv")
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO platform_survival(id,user_id,username,wave,score,streak,created_at,verified) VALUES(?,?,?,?,?,?,?,?)",
                (sid, user_id, username, wave, int(score), int(streak), _now(), int(verified)),
            )
        return {"id": sid, "ok": True, "ranked": bool(verified)}

    def survival_leaderboard(self, limit: int = 20) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT username, MAX(score) AS best, MAX(streak) AS streak FROM platform_survival"
                " WHERE verified=1 GROUP BY username ORDER BY best DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [dict(rank=i + 1, username=r["username"], score=r["best"], streak=r["streak"])
                for i, r in enumerate(rows)]

    # --- blog --------------------------------------------------------------
    def list_blog(self, limit: int = 50) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT slug,title,author,excerpt,tags,read_minutes,published_at FROM platform_blog"
                " ORDER BY published_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
            return [self._blog_row(r, with_body=False) for r in rows]

    def get_blog(self, slug: str) -> dict | None:
        with self._connect() as conn:
            r = conn.execute("SELECT * FROM platform_blog WHERE slug=?", (slug,)).fetchone()
            return self._blog_row(r, with_body=True) if r else None

    def upsert_blog(self, *, slug: str, title: str, author: str | None, excerpt: str | None,
                    body: str | None, tags: list[str] | None, read_minutes: int | None) -> dict:
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO platform_blog(slug,title,author,excerpt,body,tags,read_minutes,published_at)"
                " VALUES(?,?,?,?,?,?,?,?)"
                " ON CONFLICT(slug) DO UPDATE SET title=excluded.title,author=excluded.author,"
                " excerpt=excluded.excerpt,body=excluded.body,tags=excluded.tags,read_minutes=excluded.read_minutes",
                (slug, title, author, excerpt, body, json.dumps(tags or []), read_minutes, _now()),
            )
        return self.get_blog(slug)  # type: ignore[return-value]  # after commit

    def counts(self) -> dict:
        with self._connect() as conn:
            def c(t: str) -> int:
                return conn.execute(f"SELECT COUNT(*) c FROM {t}").fetchone()["c"]
            return {
                "threads": c("platform_threads"), "comments": c("platform_comments"),
                "jobs": c("platform_jobs"), "applications": c("platform_job_applications"),
                "bug_reports": c("platform_bug_reports"), "subscribers": c("platform_newsletter"),
                "progress_events": c("platform_progress"), "survival_runs": c("platform_survival"),
                "blog_posts": c("platform_blog"),
            }

    # --- row mappers -------------------------------------------------------
    @staticmethod
    def _thread(r: sqlite3.Row) -> dict:
        return dict(id=r["id"], channel=r["channel"], title=r["title"], body=r["body"],
                    author=r["author"], tags=json.loads(r["tags"] or "[]"),
                    votes=r["votes"], comment_count=r["comment_count"], created_at=r["created_at"])

    @staticmethod
    def _job(r: sqlite3.Row) -> dict:
        keys = r.keys()
        return dict(id=r["id"], title=r["title"], company=r["company"], location=r["location"],
                    kind=r["kind"], tags=json.loads(r["tags"] or "[]"), description=r["description"],
                    posted_by=r["posted_by"], created_at=r["created_at"],
                    url=r["url"] if "url" in keys else None,
                    source=r["source"] if "source" in keys else None,
                    remote=bool(r["remote"]) if "remote" in keys and r["remote"] is not None else False)

    @staticmethod
    def _blog_row(r: sqlite3.Row, with_body: bool) -> dict:
        d = dict(slug=r["slug"], title=r["title"], author=r["author"], excerpt=r["excerpt"],
                 tags=json.loads(r["tags"] or "[]"), read_minutes=r["read_minutes"],
                 published_at=r["published_at"])
        if with_body:
            d["body"] = r["body"]
        return d
