"""Local platform data store (community, jobs, leaderboard, blog, progress...).

Real persistence for the website features that used to render hardcoded mock
arrays. SQLite-backed, self-contained, and Dockerizable for a VPS. Identity is
the Supabase user id/email passed from the authenticated frontend (no secret
needed here); ownership is by that id. Hardening note: verify the Supabase JWT
at the edge before trusting `user_id` in production.
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

    def vote_thread(self, thread_id: str, delta: int = 1) -> dict | None:
        with self._connect() as conn:
            cur = conn.execute("UPDATE platform_threads SET votes=votes+? WHERE id=?", (delta, thread_id))
            if cur.rowcount == 0:
                return None
            return self._thread(conn.execute("SELECT * FROM platform_threads WHERE id=?", (thread_id,)).fetchone())

    def list_comments(self, thread_id: str) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM platform_comments WHERE thread_id=? ORDER BY created_at ASC", (thread_id,)
            ).fetchall()
            return [dict(id=r["id"], thread_id=r["thread_id"], body=r["body"], author=r["author"],
                        author_id=r["author_id"], created_at=r["created_at"]) for r in rows]

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
            return dict(id=cid, thread_id=thread_id, body=body, author=author, author_id=author_id, created_at=_now())

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

    # --- progress + leaderboard -------------------------------------------
    def record_progress(self, *, user_id: str, username: str | None, kind: str,
                        ref: str | None, score: float | None, meta: dict | None) -> dict:
        pid = _uid("prg")
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO platform_progress(id,user_id,username,kind,ref,score,meta,created_at)"
                " VALUES(?,?,?,?,?,?,?,?)",
                (pid, user_id, username, kind, ref, score, json.dumps(meta or {}), _now()),
            )
        return {"id": pid, "ok": True}

    def progress_summary(self, user_id: str) -> dict:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT kind, ref, score, meta, created_at FROM platform_progress WHERE user_id=? ORDER BY created_at DESC",
                (user_id,),
            ).fetchall()
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
            "active_days": active_days,
            "heatmap": [{"day": d, "count": c} for d, c in sorted(heat.items())],
            "courses": [{"course": k, "lessons_done": len(v)} for k, v in courses.items()],
            "quizzes": quizzes[:20],
            "exercises": exercises[:20],
            "avg_score": round(sum(scored) / len(scored), 1) if scored else None,
            "today": today,
        }

    def leaderboard(self, limit: int = 20) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT user_id,
                       COALESCE(MAX(username),'anon') AS username,
                       COALESCE(SUM(score),0) AS points,
                       COUNT(*) AS events
                FROM platform_progress
                GROUP BY user_id
                ORDER BY points DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [dict(rank=i + 1, user_id=r["user_id"], username=r["username"],
                     points=round(r["points"] or 0, 1), events=r["events"])
                for i, r in enumerate(rows)]

    # --- survival ----------------------------------------------------------
    def record_survival(self, *, user_id: str | None, username: str, wave: str | None,
                        score: int, streak: int = 0) -> dict:
        sid = _uid("srv")
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO platform_survival(id,user_id,username,wave,score,streak,created_at) VALUES(?,?,?,?,?,?,?)",
                (sid, user_id, username, wave, int(score), int(streak), _now()),
            )
        return {"id": sid, "ok": True}

    def survival_leaderboard(self, limit: int = 20) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT username, MAX(score) AS best, MAX(streak) AS streak FROM platform_survival"
                " GROUP BY username ORDER BY best DESC LIMIT ?",
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
                    author=r["author"], author_id=r["author_id"], tags=json.loads(r["tags"] or "[]"),
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
