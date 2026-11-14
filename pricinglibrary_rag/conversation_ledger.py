"""Durable conversation and task ledger for TPL agent teams.

This module is the backend substrate proposed in the OpenClaw/Codex audit:
sessions, sanitized history, artifacts, tool-call links, and detached agent
tasks.  It deliberately stores state in the existing SQLite database so CLI,
API, smokes, and future MCP/OpenClaw/Codex clients share one source of truth.
"""
from __future__ import annotations

import hashlib
import json
import re
import uuid
from typing import Any

from .storage import LocalStore


CONTROL_TAGS = (
    "tool_call",
    "tool_calls",
    "function_call",
    "function_calls",
    "relevant_memories",
    "relevant-memories",
)


def _json(data: Any) -> str:
    return json.dumps(data or {}, ensure_ascii=True, sort_keys=True, default=str)


def _load(raw: str | None, default: Any) -> Any:
    if not raw:
        return default
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return default


def _new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:16]}"


def _hash_payload(payload: Any) -> str:
    return hashlib.sha256(_json(payload).encode("utf-8")).hexdigest()[:16]


def sanitize_history_text(text: str, *, max_chars: int = 4000) -> str:
    """Return a model-safe recall view of a transcript message.

    The raw transcript remains in SQLite.  This recall view strips model/tool
    scaffolding, obvious control tokens, and token-like secrets before the text
    is shown to another agent or external client.
    """

    clean = str(text or "")
    for tag in CONTROL_TAGS:
        clean = re.sub(
            rf"<{tag}\b[^>]*>.*?</{tag}>",
            f"[{tag} omitted]",
            clean,
            flags=re.IGNORECASE | re.DOTALL,
        )
        clean = re.sub(
            rf"<{tag}\b[^>]*>.*",
            f"[{tag} omitted]",
            clean,
            flags=re.IGNORECASE | re.DOTALL,
        )
    clean = re.sub(r"<\|[^|]{1,80}\|>", "[control-token omitted]", clean)
    clean = re.sub(r"<｜[^｜]{1,80}｜>", "[control-token omitted]", clean)
    clean = re.sub(
        r"(?i)\b(api[_-]?key|token|secret|password|authorization|bearer)\b\s*[:=]\s*['\"]?([^\s,'\";]{8,})",
        lambda m: f"{m.group(1)}=[redacted len={len(m.group(2))}]",
        clean,
    )
    clean = re.sub(r"\n{4,}", "\n\n\n", clean).strip()
    if len(clean) > max_chars:
        return clean[:max_chars].rstrip() + "\n[conversation_history truncated]"
    return clean


class ConversationLedger:
    def __init__(self, store: LocalStore) -> None:
        self.store = store
        self._init_schema()

    def _init_schema(self) -> None:
        with self.store.connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS conversation_sessions (
                    id TEXT PRIMARY KEY,
                    agent_id TEXT NOT NULL,
                    channel TEXT NOT NULL,
                    external_user_id TEXT,
                    title TEXT,
                    route_metadata_json TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'active',
                    created_at TEXT NOT NULL DEFAULT (datetime('now')),
                    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
                );

                CREATE TABLE IF NOT EXISTS conversation_messages (
                    id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL REFERENCES conversation_sessions(id) ON DELETE CASCADE,
                    role TEXT NOT NULL,
                    body TEXT NOT NULL,
                    visibility TEXT NOT NULL DEFAULT 'agent_visible',
                    source TEXT NOT NULL DEFAULT 'cli',
                    metadata_json TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT (datetime('now'))
                );

                CREATE TABLE IF NOT EXISTS conversation_artifacts (
                    id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL REFERENCES conversation_sessions(id) ON DELETE CASCADE,
                    artifact_type TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    provenance_json TEXT NOT NULL,
                    tool_call_id TEXT,
                    created_at TEXT NOT NULL DEFAULT (datetime('now'))
                );

                CREATE TABLE IF NOT EXISTS conversation_tool_calls (
                    id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL REFERENCES conversation_sessions(id) ON DELETE CASCADE,
                    agent_id TEXT NOT NULL,
                    tool_name TEXT NOT NULL,
                    payload_hash TEXT NOT NULL,
                    audit_id TEXT,
                    artifact_ids_json TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT (datetime('now'))
                );

                CREATE TABLE IF NOT EXISTS agent_tasks (
                    id TEXT PRIMARY KEY,
                    parent_session_id TEXT REFERENCES conversation_sessions(id) ON DELETE SET NULL,
                    child_session_id TEXT REFERENCES conversation_sessions(id) ON DELETE SET NULL,
                    agent_id TEXT NOT NULL,
                    task_type TEXT NOT NULL DEFAULT 'subagent',
                    title TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'queued',
                    result_summary TEXT,
                    created_at TEXT NOT NULL DEFAULT (datetime('now')),
                    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
                    ended_at TEXT
                );

                CREATE TABLE IF NOT EXISTS conversation_turns (
                    id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL REFERENCES conversation_sessions(id) ON DELETE CASCADE,
                    parent_turn_id TEXT REFERENCES conversation_turns(id) ON DELETE SET NULL,
                    objective TEXT NOT NULL,
                    input_json TEXT NOT NULL,
                    output_json TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'running',
                    created_at TEXT NOT NULL DEFAULT (datetime('now')),
                    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
                    ended_at TEXT
                );

                CREATE TABLE IF NOT EXISTS conversation_summaries (
                    id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL REFERENCES conversation_sessions(id) ON DELETE CASCADE,
                    source_message_count INTEGER NOT NULL,
                    summary TEXT NOT NULL,
                    metadata_json TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT (datetime('now'))
                );

                CREATE TABLE IF NOT EXISTS agent_approvals (
                    id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL REFERENCES conversation_sessions(id) ON DELETE CASCADE,
                    agent_id TEXT NOT NULL,
                    tool_name TEXT NOT NULL,
                    payload_hash TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    scope TEXT NOT NULL DEFAULT 'once',
                    status TEXT NOT NULL DEFAULT 'requested',
                    created_at TEXT NOT NULL DEFAULT (datetime('now')),
                    resolved_at TEXT,
                    decision_note TEXT
                );

                CREATE TABLE IF NOT EXISTS runtime_events (
                    id TEXT PRIMARY KEY,
                    session_id TEXT REFERENCES conversation_sessions(id) ON DELETE CASCADE,
                    event_type TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT (datetime('now'))
                );

                CREATE INDEX IF NOT EXISTS idx_conversation_sessions_agent
                    ON conversation_sessions(agent_id, updated_at);
                CREATE INDEX IF NOT EXISTS idx_conversation_messages_session
                    ON conversation_messages(session_id, created_at);
                CREATE INDEX IF NOT EXISTS idx_conversation_artifacts_session
                    ON conversation_artifacts(session_id, created_at);
                CREATE INDEX IF NOT EXISTS idx_conversation_tool_calls_session
                    ON conversation_tool_calls(session_id, created_at);
                CREATE INDEX IF NOT EXISTS idx_agent_tasks_status
                    ON agent_tasks(status, updated_at);
                CREATE INDEX IF NOT EXISTS idx_conversation_turns_session
                    ON conversation_turns(session_id, updated_at);
                CREATE INDEX IF NOT EXISTS idx_conversation_summaries_session
                    ON conversation_summaries(session_id, created_at);
                CREATE INDEX IF NOT EXISTS idx_agent_approvals_status
                    ON agent_approvals(status, created_at);
                CREATE INDEX IF NOT EXISTS idx_runtime_events_session
                    ON runtime_events(session_id, created_at);
                """
            )

    # --- sessions -----------------------------------------------------
    def create_session(
        self,
        *,
        agent_id: str,
        channel: str = "cli",
        external_user_id: str | None = None,
        title: str | None = None,
        route_metadata: dict[str, Any] | None = None,
        status: str = "active",
    ) -> dict[str, Any]:
        session_id = _new_id("sess")
        with self.store.connect() as conn:
            conn.execute(
                """
                INSERT INTO conversation_sessions(
                    id, agent_id, channel, external_user_id, title,
                    route_metadata_json, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    session_id,
                    agent_id,
                    channel,
                    external_user_id,
                    title,
                    _json(route_metadata or {}),
                    status,
                ),
            )
        return self.get_session(session_id) or {}

    def get_session(self, session_id: str) -> dict[str, Any] | None:
        with self.store.connect() as conn:
            row = conn.execute(
                "SELECT * FROM conversation_sessions WHERE id = ?",
                (session_id,),
            ).fetchone()
        return self._session(row) if row else None

    def list_sessions(
        self,
        *,
        agent_id: str | None = None,
        channel: str | None = None,
        status: str | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        query = "SELECT * FROM conversation_sessions WHERE 1=1"
        params: list[Any] = []
        if agent_id:
            query += " AND agent_id = ?"
            params.append(agent_id)
        if channel:
            query += " AND channel = ?"
            params.append(channel)
        if status:
            query += " AND status = ?"
            params.append(status)
        query += " ORDER BY updated_at DESC LIMIT ?"
        params.append(limit)
        with self.store.connect() as conn:
            rows = conn.execute(query, params).fetchall()
        return [self._session(row) for row in rows]

    # --- messages and history ----------------------------------------
    def add_message(
        self,
        session_id: str,
        *,
        role: str,
        body: str,
        visibility: str = "agent_visible",
        source: str = "cli",
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        self._require_session(session_id)
        message_id = _new_id("msg")
        with self.store.connect() as conn:
            conn.execute(
                """
                INSERT INTO conversation_messages(
                    id, session_id, role, body, visibility, source, metadata_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    message_id,
                    session_id,
                    role,
                    body,
                    visibility,
                    source,
                    _json(metadata or {}),
                ),
            )
            conn.execute(
                "UPDATE conversation_sessions SET updated_at = datetime('now') WHERE id = ?",
                (session_id,),
            )
        return self.get_message(message_id) or {}

    def get_message(self, message_id: str) -> dict[str, Any] | None:
        with self.store.connect() as conn:
            row = conn.execute(
                "SELECT * FROM conversation_messages WHERE id = ?",
                (message_id,),
            ).fetchone()
        return self._message(row, sanitized=False) if row else None

    def history(
        self,
        session_id: str,
        *,
        limit: int = 20,
        offset: int = 0,
        sanitized: bool = True,
    ) -> dict[str, Any]:
        self._require_session(session_id)
        limit = max(1, min(limit, 100))
        offset = max(0, offset)
        with self.store.connect() as conn:
            rows = conn.execute(
                """
                SELECT * FROM conversation_messages
                WHERE session_id = ?
                ORDER BY created_at DESC, id DESC
                LIMIT ? OFFSET ?
                """,
                (session_id, limit + 1, offset),
            ).fetchall()
        has_more = len(rows) > limit
        page = rows[:limit]
        messages = [self._message(row, sanitized=sanitized) for row in reversed(page)]
        return {
            "session_id": session_id,
            "messages": messages,
            "next_offset": offset + limit if has_more else None,
            "sanitized": sanitized,
        }

    def search_history(
        self,
        query: str,
        *,
        agent_id: str | None = None,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        query = query.strip()
        if not query:
            return []
        sql = """
            SELECT m.*, s.agent_id, s.channel
            FROM conversation_messages m
            JOIN conversation_sessions s ON s.id = m.session_id
            WHERE m.body LIKE ?
        """
        params: list[Any] = [f"%{query}%"]
        if agent_id:
            sql += " AND s.agent_id = ?"
            params.append(agent_id)
        sql += " ORDER BY m.created_at DESC LIMIT ?"
        params.append(max(1, min(limit, 100)))
        with self.store.connect() as conn:
            rows = conn.execute(sql, params).fetchall()
        return [
            {
                **self._message(row, sanitized=True),
                "agent_id": row["agent_id"],
                "channel": row["channel"],
            }
            for row in rows
        ]

    # --- artifacts and tool calls ------------------------------------
    def add_artifact(
        self,
        session_id: str,
        *,
        artifact_type: str,
        payload: dict[str, Any],
        provenance: dict[str, Any] | None = None,
        tool_call_id: str | None = None,
    ) -> dict[str, Any]:
        self._require_session(session_id)
        artifact_id = _new_id("art")
        with self.store.connect() as conn:
            conn.execute(
                """
                INSERT INTO conversation_artifacts(
                    id, session_id, artifact_type, payload_json,
                    provenance_json, tool_call_id
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    artifact_id,
                    session_id,
                    artifact_type,
                    _json(payload),
                    _json(provenance or {}),
                    tool_call_id,
                ),
            )
            conn.execute(
                "UPDATE conversation_sessions SET updated_at = datetime('now') WHERE id = ?",
                (session_id,),
            )
        return self.get_artifact(artifact_id) or {}

    def get_artifact(self, artifact_id: str) -> dict[str, Any] | None:
        with self.store.connect() as conn:
            row = conn.execute(
                "SELECT * FROM conversation_artifacts WHERE id = ?",
                (artifact_id,),
            ).fetchone()
        return self._artifact(row) if row else None

    def list_artifacts(self, session_id: str) -> list[dict[str, Any]]:
        self._require_session(session_id)
        with self.store.connect() as conn:
            rows = conn.execute(
                """
                SELECT * FROM conversation_artifacts
                WHERE session_id = ?
                ORDER BY created_at ASC
                """,
                (session_id,),
            ).fetchall()
        return [self._artifact(row) for row in rows]

    def record_tool_result(
        self,
        session_id: str,
        *,
        agent_id: str,
        tool_name: str,
        payload: dict[str, Any],
        tool_result: dict[str, Any],
    ) -> dict[str, Any]:
        self._require_session(session_id)
        artifact_type = str(
            (tool_result.get("output") or {}).get("artifact")
            or (tool_result.get("tool_spec") or {}).get("artifact")
            or "ToolResult"
        )
        artifact = self.add_artifact(
            session_id,
            artifact_type=artifact_type,
            payload=tool_result,
            provenance={
                "source": "ToolRegistry",
                "tool_name": tool_name,
                "audit_id": tool_result.get("id"),
            },
            tool_call_id=tool_result.get("id"),
        )
        call_id = _new_id("ctool")
        status = "ok" if tool_result.get("ok") else "failed"
        with self.store.connect() as conn:
            conn.execute(
                """
                INSERT INTO conversation_tool_calls(
                    id, session_id, agent_id, tool_name, payload_hash,
                    audit_id, artifact_ids_json, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    call_id,
                    session_id,
                    agent_id,
                    tool_name,
                    _hash_payload(payload),
                    tool_result.get("id"),
                    _json([artifact["id"]]),
                    status,
                ),
            )
        return {
            "id": call_id,
            "session_id": session_id,
            "agent_id": agent_id,
            "tool_name": tool_name,
            "payload_hash": _hash_payload(payload),
            "audit_id": tool_result.get("id"),
            "artifact_ids": [artifact["id"]],
            "status": status,
            "artifact": artifact,
        }

    # --- tasks --------------------------------------------------------
    def create_task(
        self,
        *,
        agent_id: str,
        title: str,
        task_type: str = "subagent",
        parent_session_id: str | None = None,
        child_session_id: str | None = None,
        payload: dict[str, Any] | None = None,
        status: str = "queued",
    ) -> dict[str, Any]:
        if parent_session_id:
            self._require_session(parent_session_id)
        if child_session_id:
            self._require_session(child_session_id)
        task_id = _new_id("task")
        with self.store.connect() as conn:
            conn.execute(
                """
                INSERT INTO agent_tasks(
                    id, parent_session_id, child_session_id, agent_id,
                    task_type, title, payload_json, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    task_id,
                    parent_session_id,
                    child_session_id,
                    agent_id,
                    task_type,
                    title,
                    _json(payload or {}),
                    status,
                ),
            )
        return self.get_task(task_id) or {}

    def get_task(self, task_id: str) -> dict[str, Any] | None:
        with self.store.connect() as conn:
            row = conn.execute(
                "SELECT * FROM agent_tasks WHERE id = ?",
                (task_id,),
            ).fetchone()
        return self._task(row) if row else None

    def update_task(
        self,
        task_id: str,
        *,
        status: str | None = None,
        result_summary: str | None = None,
        child_session_id: str | None = None,
    ) -> dict[str, Any]:
        current = self.get_task(task_id)
        if current is None:
            raise KeyError(f"Unknown task id: {task_id}")
        terminal = status in {"done", "failed", "cancelled", "lost"}
        with self.store.connect() as conn:
            conn.execute(
                """
                UPDATE agent_tasks
                SET status = COALESCE(?, status),
                    result_summary = COALESCE(?, result_summary),
                    child_session_id = COALESCE(?, child_session_id),
                    ended_at = CASE WHEN ? THEN datetime('now') ELSE ended_at END,
                    updated_at = datetime('now')
                WHERE id = ?
                """,
                (status, result_summary, child_session_id, terminal, task_id),
            )
        return self.get_task(task_id) or {}

    def list_tasks(
        self,
        *,
        status: str | None = None,
        agent_id: str | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        query = "SELECT * FROM agent_tasks WHERE 1=1"
        params: list[Any] = []
        if status:
            query += " AND status = ?"
            params.append(status)
        if agent_id:
            query += " AND agent_id = ?"
            params.append(agent_id)
        query += " ORDER BY updated_at DESC LIMIT ?"
        params.append(max(1, min(limit, 200)))
        with self.store.connect() as conn:
            rows = conn.execute(query, params).fetchall()
        return [self._task(row) for row in rows]

    # --- runtime turns ------------------------------------------------
    def start_turn(
        self,
        session_id: str,
        *,
        objective: str,
        input_payload: dict[str, Any] | None = None,
        parent_turn_id: str | None = None,
        status: str = "running",
    ) -> dict[str, Any]:
        self._require_session(session_id)
        if parent_turn_id and self.get_turn(parent_turn_id) is None:
            raise KeyError(f"Unknown parent turn id: {parent_turn_id}")
        turn_id = _new_id("turn")
        with self.store.connect() as conn:
            conn.execute(
                """
                INSERT INTO conversation_turns(
                    id, session_id, parent_turn_id, objective, input_json,
                    output_json, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    turn_id,
                    session_id,
                    parent_turn_id,
                    objective,
                    _json(input_payload or {}),
                    _json({}),
                    status,
                ),
            )
            conn.execute(
                "UPDATE conversation_sessions SET updated_at = datetime('now') WHERE id = ?",
                (session_id,),
            )
        self.record_event(
            session_id,
            "turn_started",
            {"turn_id": turn_id, "objective": objective, "parent_turn_id": parent_turn_id},
        )
        return self.get_turn(turn_id) or {}

    def get_turn(self, turn_id: str) -> dict[str, Any] | None:
        with self.store.connect() as conn:
            row = conn.execute(
                "SELECT * FROM conversation_turns WHERE id = ?",
                (turn_id,),
            ).fetchone()
        return self._turn(row) if row else None

    def list_turns(
        self,
        session_id: str,
        *,
        status: str | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        self._require_session(session_id)
        query = "SELECT * FROM conversation_turns WHERE session_id = ?"
        params: list[Any] = [session_id]
        if status:
            query += " AND status = ?"
            params.append(status)
        query += " ORDER BY created_at ASC LIMIT ?"
        params.append(max(1, min(limit, 200)))
        with self.store.connect() as conn:
            rows = conn.execute(query, params).fetchall()
        return [self._turn(row) for row in rows]

    def complete_turn(
        self,
        turn_id: str,
        *,
        output_payload: dict[str, Any] | None = None,
        status: str = "completed",
    ) -> dict[str, Any]:
        current = self.get_turn(turn_id)
        if current is None:
            raise KeyError(f"Unknown turn id: {turn_id}")
        terminal = status in {"completed", "failed", "cancelled"}
        with self.store.connect() as conn:
            conn.execute(
                """
                UPDATE conversation_turns
                SET output_json = ?,
                    status = ?,
                    ended_at = CASE WHEN ? THEN datetime('now') ELSE ended_at END,
                    updated_at = datetime('now')
                WHERE id = ?
                """,
                (_json(output_payload or {}), status, terminal, turn_id),
            )
        self.record_event(
            current["session_id"],
            "turn_completed" if terminal else "turn_updated",
            {"turn_id": turn_id, "status": status},
        )
        return self.get_turn(turn_id) or {}

    # --- runtime summaries / thread transforms -----------------------
    def compact_session(
        self,
        session_id: str,
        *,
        max_messages: int = 20,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        self._require_session(session_id)
        max_messages = max(1, min(max_messages, 100))
        recent = self.history(session_id, limit=max_messages, sanitized=True)["messages"]
        source_message_count = self._message_count(session_id)
        lines = [
            f"Session {session_id} compacted from {source_message_count} messages.",
            "Recent sanitized context:",
        ]
        for message in recent:
            snippet = sanitize_history_text(message["body"], max_chars=260).replace("\n", " ")
            lines.append(f"- {message['role']}: {snippet}")
        summary_text = "\n".join(lines)
        summary_id = _new_id("sum")
        with self.store.connect() as conn:
            conn.execute(
                """
                INSERT INTO conversation_summaries(
                    id, session_id, source_message_count, summary, metadata_json
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (
                    summary_id,
                    session_id,
                    source_message_count,
                    summary_text,
                    _json(metadata or {}),
                ),
            )
            conn.execute(
                "UPDATE conversation_sessions SET updated_at = datetime('now') WHERE id = ?",
                (session_id,),
            )
        summary = self.get_summary(summary_id) or {}
        self.record_event(
            session_id,
            "session_compacted",
            {"summary_id": summary_id, "max_messages": max_messages, "source_message_count": source_message_count},
        )
        return summary

    def get_summary(self, summary_id: str) -> dict[str, Any] | None:
        with self.store.connect() as conn:
            row = conn.execute(
                "SELECT * FROM conversation_summaries WHERE id = ?",
                (summary_id,),
            ).fetchone()
        return self._summary(row) if row else None

    def list_summaries(self, session_id: str, *, limit: int = 20) -> list[dict[str, Any]]:
        self._require_session(session_id)
        with self.store.connect() as conn:
            rows = conn.execute(
                """
                SELECT * FROM conversation_summaries
                WHERE session_id = ?
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (session_id, max(1, min(limit, 100))),
            ).fetchall()
        return [self._summary(row) for row in rows]

    def fork_session(
        self,
        session_id: str,
        *,
        target_agent: str | None = None,
        title: str | None = None,
        include_last_messages: int = 10,
    ) -> dict[str, Any]:
        parent = self.get_session(session_id)
        if parent is None:
            raise KeyError(f"Unknown session id: {session_id}")
        include_last_messages = max(0, min(include_last_messages, 50))
        child = self.create_session(
            agent_id=target_agent or parent["agent_id"],
            channel=parent["channel"],
            external_user_id=parent["external_user_id"],
            title=title or f"Fork of {parent.get('title') or session_id}",
            route_metadata={
                **(parent.get("route_metadata") or {}),
                "forked_from_session_id": session_id,
                "fork_include_last_messages": include_last_messages,
            },
        )
        injected = None
        if include_last_messages:
            history = self.history(session_id, limit=include_last_messages, sanitized=True)["messages"]
            lines = ["Forked sanitized context:"]
            for message in history:
                lines.append(f"{message['role']}: {message['body']}")
            injected = self.add_message(
                child["id"],
                role="system",
                body="\n".join(lines),
                visibility="agent_visible",
                source="runtime:fork",
                metadata={"parent_session_id": session_id},
            )
        self.record_event(
            session_id,
            "session_forked",
            {"child_session_id": child["id"], "target_agent": child["agent_id"]},
        )
        self.record_event(
            child["id"],
            "session_fork_created",
            {"parent_session_id": session_id, "injected_message_id": injected["id"] if injected else None},
        )
        return {
            "parent_session": parent,
            "forked_session": self.get_session(child["id"]),
            "injected_message": injected,
        }

    def inject_items(
        self,
        session_id: str,
        items: list[dict[str, Any]],
        *,
        source: str = "runtime:inject",
    ) -> dict[str, Any]:
        self._require_session(session_id)
        injected: list[dict[str, Any]] = []
        for item in items:
            kind = str(item.get("kind") or item.get("type") or "message")
            if kind == "artifact":
                artifact = self.add_artifact(
                    session_id,
                    artifact_type=str(item.get("artifact_type") or "InjectedArtifact"),
                    payload=item.get("payload") or {},
                    provenance={**(item.get("provenance") or {}), "source": source},
                    tool_call_id=item.get("tool_call_id"),
                )
                injected.append({"kind": "artifact", "item": artifact})
                continue
            body = str(item.get("body") or item.get("text") or item.get("payload") or "")
            message = self.add_message(
                session_id,
                role=str(item.get("role") or "system"),
                body=body,
                visibility=str(item.get("visibility") or "agent_visible"),
                source=source,
                metadata=item.get("metadata") or {},
            )
            injected.append({"kind": "message", "item": message})
        self.record_event(
            session_id,
            "session_items_injected",
            {"count": len(injected), "source": source},
        )
        return {"session_id": session_id, "injected": injected}

    def rollback_session(
        self,
        session_id: str,
        *,
        message_id: str | None = None,
        keep_last: int | None = None,
        reason: str | None = None,
    ) -> dict[str, Any]:
        self._require_session(session_id)
        rows = self._message_rows(session_id)
        if message_id:
            if not any(row["id"] == message_id for row in rows):
                raise KeyError(f"Unknown message id for session {session_id}: {message_id}")
            cutoff_seen = False
            retained_rows = []
            for row in rows:
                retained_rows.append(row)
                if row["id"] == message_id:
                    cutoff_seen = True
                    break
            if not cutoff_seen:
                retained_rows = rows
        elif keep_last is not None:
            retained_rows = rows[-max(0, min(keep_last, len(rows))):] if keep_last else []
        else:
            retained_rows = rows
        retained_ids = [row["id"] for row in retained_rows]
        event = self.record_event(
            session_id,
            "session_rollback_marked",
            {
                "message_id": message_id,
                "keep_last": keep_last,
                "reason": reason,
                "retained_message_ids": retained_ids,
                "non_destructive": True,
            },
        )
        return {
            "session_id": session_id,
            "event": event,
            "effective_history": [self._message(row, sanitized=True) for row in retained_rows],
        }

    # --- approvals and lifecycle events -------------------------------
    def request_approval(
        self,
        session_id: str,
        *,
        agent_id: str,
        tool_name: str,
        payload: dict[str, Any] | None = None,
        reason: str = "",
        scope: str = "once",
        status: str = "requested",
    ) -> dict[str, Any]:
        self._require_session(session_id)
        approval_id = _new_id("appr")
        payload = payload or {}
        with self.store.connect() as conn:
            conn.execute(
                """
                INSERT INTO agent_approvals(
                    id, session_id, agent_id, tool_name, payload_hash,
                    payload_json, reason, scope, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    approval_id,
                    session_id,
                    agent_id,
                    tool_name,
                    _hash_payload(payload),
                    _json(payload),
                    reason,
                    scope,
                    status,
                ),
            )
        self.record_event(
            session_id,
            "approval_requested",
            {"approval_id": approval_id, "tool_name": tool_name, "agent_id": agent_id, "scope": scope},
        )
        return self.get_approval(approval_id) or {}

    def get_approval(self, approval_id: str) -> dict[str, Any] | None:
        with self.store.connect() as conn:
            row = conn.execute(
                "SELECT * FROM agent_approvals WHERE id = ?",
                (approval_id,),
            ).fetchone()
        return self._approval(row) if row else None

    def resolve_approval(
        self,
        approval_id: str,
        *,
        status: str,
        decision_note: str | None = None,
    ) -> dict[str, Any]:
        current = self.get_approval(approval_id)
        if current is None:
            raise KeyError(f"Unknown approval id: {approval_id}")
        if status not in {"approved", "denied", "expired", "requested"}:
            raise ValueError("approval status must be approved, denied, expired, or requested")
        resolved = status in {"approved", "denied", "expired"}
        with self.store.connect() as conn:
            conn.execute(
                """
                UPDATE agent_approvals
                SET status = ?,
                    decision_note = COALESCE(?, decision_note),
                    resolved_at = CASE WHEN ? THEN datetime('now') ELSE resolved_at END
                WHERE id = ?
                """,
                (status, decision_note, resolved, approval_id),
            )
        self.record_event(
            current["session_id"],
            "approval_resolved" if resolved else "approval_reopened",
            {"approval_id": approval_id, "status": status},
        )
        return self.get_approval(approval_id) or {}

    def list_approvals(
        self,
        *,
        session_id: str | None = None,
        status: str | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        query = "SELECT * FROM agent_approvals WHERE 1=1"
        params: list[Any] = []
        if session_id:
            self._require_session(session_id)
            query += " AND session_id = ?"
            params.append(session_id)
        if status:
            query += " AND status = ?"
            params.append(status)
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(max(1, min(limit, 200)))
        with self.store.connect() as conn:
            rows = conn.execute(query, params).fetchall()
        return [self._approval(row) for row in rows]

    def find_approved_approval(
        self,
        *,
        session_id: str,
        agent_id: str | None,
        tool_name: str,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        self._require_session(session_id)
        payload_hash = _hash_payload(payload or {})
        query = """
            SELECT * FROM agent_approvals
            WHERE session_id = ?
              AND tool_name = ?
              AND payload_hash = ?
              AND status = 'approved'
        """
        params: list[Any] = [session_id, tool_name, payload_hash]
        if agent_id:
            query += " AND agent_id = ?"
            params.append(agent_id)
        query += " ORDER BY resolved_at DESC, created_at DESC LIMIT 1"
        with self.store.connect() as conn:
            row = conn.execute(query, params).fetchone()
        return self._approval(row) if row else None

    def record_event(
        self,
        session_id: str | None,
        event_type: str,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if session_id:
            self._require_session(session_id)
        event_id = _new_id("evt")
        with self.store.connect() as conn:
            conn.execute(
                """
                INSERT INTO runtime_events(id, session_id, event_type, payload_json)
                VALUES (?, ?, ?, ?)
                """,
                (event_id, session_id, event_type, _json(payload or {})),
            )
        return self.get_event(event_id) or {}

    def get_event(self, event_id: str) -> dict[str, Any] | None:
        with self.store.connect() as conn:
            row = conn.execute(
                "SELECT * FROM runtime_events WHERE id = ?",
                (event_id,),
            ).fetchone()
        return self._event(row) if row else None

    def list_events(
        self,
        *,
        session_id: str | None = None,
        event_type: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        query = "SELECT * FROM runtime_events WHERE 1=1"
        params: list[Any] = []
        if session_id:
            self._require_session(session_id)
            query += " AND session_id = ?"
            params.append(session_id)
        if event_type:
            query += " AND event_type = ?"
            params.append(event_type)
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(max(1, min(limit, 500)))
        with self.store.connect() as conn:
            rows = conn.execute(query, params).fetchall()
        return [self._event(row) for row in rows]

    # --- row mapping --------------------------------------------------
    def _require_session(self, session_id: str) -> None:
        if self.get_session(session_id) is None:
            raise KeyError(f"Unknown session id: {session_id}")

    def _message_count(self, session_id: str) -> int:
        with self.store.connect() as conn:
            row = conn.execute(
                "SELECT COUNT(*) AS count FROM conversation_messages WHERE session_id = ?",
                (session_id,),
            ).fetchone()
        return int(row["count"] if row else 0)

    def _message_rows(self, session_id: str) -> list[Any]:
        with self.store.connect() as conn:
            rows = conn.execute(
                """
                SELECT * FROM conversation_messages
                WHERE session_id = ?
                ORDER BY rowid ASC
                """,
                (session_id,),
            ).fetchall()
        return list(rows)

    @staticmethod
    def _session(row) -> dict[str, Any]:
        return {
            "id": row["id"],
            "agent_id": row["agent_id"],
            "channel": row["channel"],
            "external_user_id": row["external_user_id"],
            "title": row["title"],
            "route_metadata": _load(row["route_metadata_json"], {}),
            "status": row["status"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        }

    @staticmethod
    def _message(row, *, sanitized: bool) -> dict[str, Any]:
        body = str(row["body"])
        return {
            "id": row["id"],
            "session_id": row["session_id"],
            "role": row["role"],
            "body": sanitize_history_text(body) if sanitized else body,
            "visibility": row["visibility"],
            "source": row["source"],
            "metadata": _load(row["metadata_json"], {}),
            "created_at": row["created_at"],
        }

    @staticmethod
    def _artifact(row) -> dict[str, Any]:
        return {
            "id": row["id"],
            "session_id": row["session_id"],
            "artifact_type": row["artifact_type"],
            "payload": _load(row["payload_json"], {}),
            "provenance": _load(row["provenance_json"], {}),
            "tool_call_id": row["tool_call_id"],
            "created_at": row["created_at"],
        }

    @staticmethod
    def _task(row) -> dict[str, Any]:
        return {
            "id": row["id"],
            "parent_session_id": row["parent_session_id"],
            "child_session_id": row["child_session_id"],
            "agent_id": row["agent_id"],
            "task_type": row["task_type"],
            "title": row["title"],
            "payload": _load(row["payload_json"], {}),
            "status": row["status"],
            "result_summary": row["result_summary"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
            "ended_at": row["ended_at"],
        }

    @staticmethod
    def _turn(row) -> dict[str, Any]:
        return {
            "id": row["id"],
            "session_id": row["session_id"],
            "parent_turn_id": row["parent_turn_id"],
            "objective": row["objective"],
            "input": _load(row["input_json"], {}),
            "output": _load(row["output_json"], {}),
            "status": row["status"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
            "ended_at": row["ended_at"],
        }

    @staticmethod
    def _summary(row) -> dict[str, Any]:
        return {
            "id": row["id"],
            "session_id": row["session_id"],
            "source_message_count": row["source_message_count"],
            "summary": row["summary"],
            "metadata": _load(row["metadata_json"], {}),
            "created_at": row["created_at"],
        }

    @staticmethod
    def _approval(row) -> dict[str, Any]:
        return {
            "id": row["id"],
            "session_id": row["session_id"],
            "agent_id": row["agent_id"],
            "tool_name": row["tool_name"],
            "payload_hash": row["payload_hash"],
            "payload": _load(row["payload_json"], {}),
            "reason": row["reason"],
            "scope": row["scope"],
            "status": row["status"],
            "created_at": row["created_at"],
            "resolved_at": row["resolved_at"],
            "decision_note": row["decision_note"],
        }

    @staticmethod
    def _event(row) -> dict[str, Any]:
        return {
            "id": row["id"],
            "session_id": row["session_id"],
            "event_type": row["event_type"],
            "payload": _load(row["payload_json"], {}),
            "created_at": row["created_at"],
        }
