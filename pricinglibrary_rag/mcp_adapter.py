"""MCP-style adapter for the TPL ToolRegistry.

The adapter intentionally delegates execution to ToolRegistry.  It only adds a
thin discovery/call/audit layer and optional ConversationLedger attachment so
external agent clients can use the same governed tools as the native CLI/API.
"""
from __future__ import annotations

import json
import sys
from typing import Any

from .agent_runtime_hooks import AgentRuntimeHooks
from .conversation_ledger import ConversationLedger, _hash_payload
from .storage import LocalStore
from .tool_registry import ToolRegistry, get_tool_registry


SERVER_INSTRUCTIONS = (
    "ThePricingLibrary MCP adapter exposes audited agent tools. Use tool_search "
    "or tools/list to discover compact descriptors, tools/describe for schemas, "
    "and tools/call to execute. Sensitive tools still require the underlying "
    "ToolRegistry confirmation policy. Conversation history returned by this "
    "adapter is sanitized and bounded. Runtime methods expose session history, "
    "turns, approvals, events, compact, fork, inject and rollback primitives."
)


class TplMcpAdapter:
    def __init__(
        self,
        *,
        registry: ToolRegistry | None = None,
        store: LocalStore | None = None,
    ) -> None:
        self.registry = registry or get_tool_registry()
        self.ledger = ConversationLedger(store) if store is not None else None
        self.hooks = AgentRuntimeHooks(self.ledger)

    def tool_search(
        self,
        *,
        query: str | None = None,
        agent_role: str | None = None,
        permission: str | None = None,
        limit: int = 25,
    ) -> dict[str, Any]:
        terms = [t for t in (query or "").lower().split() if t]
        specs = self.registry.list(agent_role=agent_role, permission_scope=permission)
        matches = []
        for spec in specs:
            haystack = " ".join(
                str(spec.get(k, ""))
                for k in ("name", "owner_agent", "permission", "category", "description", "artifact")
            ).lower()
            if terms and not all(term in haystack for term in terms):
                continue
            matches.append(self._compact_tool(spec))
        return {
            "tools": matches[: max(1, min(limit, 100))],
            "count": len(matches),
            "query": query or "",
            "agent_role": agent_role,
        }

    def describe_tool(self, tool_name: str) -> dict[str, Any]:
        return self.registry.describe(tool_name)

    def call_tool(
        self,
        tool_name: str,
        *,
        payload: dict[str, Any] | None = None,
        context: dict[str, Any] | None = None,
        session_id: str | None = None,
        agent_id: str | None = None,
    ) -> dict[str, Any]:
        payload = payload or {}
        context = context or {}
        approved_confirmation = None
        tool_spec = self.registry.describe(tool_name)
        if (
            self.ledger is not None
            and session_id
            and tool_spec.get("requires_confirmation")
            and not payload.get("confirmed")
            and not context.get("confirmed")
        ):
            approved_confirmation = self.ledger.find_approved_approval(
                session_id=session_id,
                agent_id=agent_id,
                tool_name=str(tool_spec["name"]),
                payload=payload,
            )
            if approved_confirmation is not None:
                context = {
                    **context,
                    "confirmed": True,
                    "approval_id": approved_confirmation["id"],
                }
        if session_id:
            self.hooks.emit(
                "before_tool_run",
                session_id=session_id,
                payload={
                    "tool_name": tool_name,
                    "agent_id": agent_id,
                    "payload_hash": _hash_payload(payload),
                    "payload_keys": sorted(str(key) for key in payload.keys()),
                    "approval_id": approved_confirmation["id"] if approved_confirmation else None,
                },
            )
        try:
            result = self.registry.run(tool_name, payload=payload, context=context)
        except Exception as exc:
            if session_id:
                self.hooks.emit(
                    "after_tool_run",
                    session_id=session_id,
                    payload={
                        "tool_name": tool_name,
                        "agent_id": agent_id,
                        "status": "exception",
                        "error": str(exc),
                    },
                )
            raise
        ledger_record = None
        if self.ledger is not None and session_id:
            resolved_agent = agent_id or result.get("agent_role") or result.get("tool_name", "Unknown")
            ledger_record = self.ledger.record_tool_result(
                session_id,
                agent_id=str(resolved_agent),
                tool_name=str(result.get("tool_name") or tool_name),
                payload=payload,
                tool_result=result,
            )
            self.hooks.emit(
                "after_tool_run",
                session_id=session_id,
                payload={
                    "tool_name": str(result.get("tool_name") or tool_name),
                    "agent_id": str(resolved_agent),
                    "status": "ok" if result.get("ok") else "failed",
                    "audit_id": result.get("id"),
                    "ledger_tool_call_id": ledger_record["id"],
                },
            )
        return {"tool_result": result, "ledger_record": ledger_record}

    def audit_tool(self, tool_call_id: str) -> dict[str, Any]:
        return self.registry.audit(tool_call_id)

    def replay_tool(self, tool_call_id: str) -> dict[str, Any]:
        return self.registry.replay(tool_call_id)

    def agents_coverage(self) -> dict[str, Any]:
        return self.registry.coverage_report()

    def conversation_search(
        self,
        *,
        query: str,
        agent_id: str | None = None,
        limit: int = 20,
    ) -> dict[str, Any]:
        if self.ledger is None:
            return {"matches": [], "count": 0, "warning": "conversation_ledger_unavailable"}
        matches = self.ledger.search_history(query, agent_id=agent_id, limit=limit)
        return {"matches": matches, "count": len(matches), "query": query}

    def artifact_read(self, artifact_id: str) -> dict[str, Any]:
        if self.ledger is None:
            raise KeyError("conversation_ledger_unavailable")
        artifact = self.ledger.get_artifact(artifact_id)
        if artifact is None:
            raise KeyError(f"Unknown artifact id: {artifact_id}")
        return artifact

    def handle(self, method: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        params = params or {}
        if method == "initialize":
            return {
                "protocolVersion": "2024-11-05",
                "serverInfo": {"name": "thepricinglibrary-tool-registry", "version": "0.1.0"},
                "capabilities": {"tools": {}},
                "instructions": SERVER_INSTRUCTIONS,
            }
        if method in {"tools/list", "tool_search", "tpl/tool_search"}:
            return self._mcp_tools_list(params)
        if method in {"tools/describe", "tool_describe", "tpl/tool_describe"}:
            return self.describe_tool(str(params["name"]))
        if method in {"tools/call", "tool_call", "tpl/tool_call"}:
            return self._mcp_tool_call(params)
        if method in {"tpl/tool_audit", "tool_audit"}:
            return self.audit_tool(str(params["tool_call_id"]))
        if method in {"tpl/tool_replay", "tool_replay"}:
            return self.replay_tool(str(params["tool_call_id"]))
        if method in {"tpl/agents_coverage", "agents_coverage"}:
            return self.agents_coverage()
        if method in {"tpl/conversation_search", "conversation_search"}:
            return self.conversation_search(
                query=str(params.get("query") or ""),
                agent_id=params.get("agent_id"),
                limit=int(params.get("limit") or 20),
            )
        if method in {"tpl/artifact_read", "artifact_read"}:
            return self.artifact_read(str(params["artifact_id"]))
        if method in {"tpl/session_history", "session_history"}:
            ledger = self._require_ledger()
            return ledger.history(
                str(params["session_id"]),
                limit=int(params.get("limit") or 20),
                offset=int(params.get("offset") or 0),
                sanitized=bool(params.get("sanitized", True)),
            )
        if method in {"tpl/session_compact", "session_compact"}:
            ledger = self._require_ledger()
            return ledger.compact_session(
                str(params["session_id"]),
                max_messages=int(params.get("max_messages") or 20),
                metadata=params.get("metadata") or {},
            )
        if method in {"tpl/session_fork", "session_fork"}:
            ledger = self._require_ledger()
            return ledger.fork_session(
                str(params["session_id"]),
                target_agent=params.get("target_agent"),
                title=params.get("title"),
                include_last_messages=int(params.get("include_last_messages") or 10),
            )
        if method in {"tpl/session_inject", "session_inject"}:
            ledger = self._require_ledger()
            return ledger.inject_items(
                str(params["session_id"]),
                list(params.get("items") or []),
                source=str(params.get("source") or "mcp:inject"),
            )
        if method in {"tpl/session_events", "session_events"}:
            ledger = self._require_ledger()
            return {
                "events": ledger.list_events(
                    session_id=str(params["session_id"]),
                    event_type=params.get("event_type"),
                    limit=int(params.get("limit") or 100),
                )
            }
        if method in {"tpl/turn_start", "turn_start"}:
            ledger = self._require_ledger()
            return ledger.start_turn(
                str(params["session_id"]),
                objective=str(params["objective"]),
                input_payload=params.get("input_payload") or {},
                parent_turn_id=params.get("parent_turn_id"),
                status=str(params.get("status") or "running"),
            )
        if method in {"tpl/turn_complete", "turn_complete"}:
            ledger = self._require_ledger()
            return ledger.complete_turn(
                str(params["turn_id"]),
                output_payload=params.get("output_payload") or {},
                status=str(params.get("status") or "completed"),
            )
        if method in {"tpl/approval_request", "approval_request"}:
            ledger = self._require_ledger()
            return ledger.request_approval(
                str(params["session_id"]),
                agent_id=str(params["agent_id"]),
                tool_name=str(params["tool_name"]),
                payload=params.get("payload") or {},
                reason=str(params.get("reason") or ""),
                scope=str(params.get("scope") or "once"),
                status=str(params.get("status") or "requested"),
            )
        if method in {"tpl/approval_resolve", "approval_resolve"}:
            ledger = self._require_ledger()
            return ledger.resolve_approval(
                str(params["approval_id"]),
                status=str(params["status"]),
                decision_note=params.get("decision_note"),
            )
        if method in {"tpl/approval_list", "approval_list"}:
            ledger = self._require_ledger()
            return {
                "approvals": ledger.list_approvals(
                    session_id=params.get("session_id"),
                    status=params.get("status"),
                    limit=int(params.get("limit") or 50),
                )
            }
        raise KeyError(f"Unknown MCP method: {method}")

    def jsonrpc(self, request: dict[str, Any]) -> dict[str, Any]:
        request_id = request.get("id")
        try:
            result = self.handle(str(request.get("method")), request.get("params") or {})
            return {"jsonrpc": "2.0", "id": request_id, "result": result}
        except Exception as exc:  # noqa: BLE001 - JSON-RPC error envelope
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32000, "message": str(exc)},
            }

    def serve_stdio(self) -> None:
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            try:
                request = json.loads(line)
            except json.JSONDecodeError as exc:
                response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {"code": -32700, "message": f"Invalid JSON: {exc}"},
                }
            else:
                response = self.jsonrpc(request)
            print(json.dumps(response, ensure_ascii=True, default=str), flush=True)

    def _mcp_tools_list(self, params: dict[str, Any]) -> dict[str, Any]:
        search = self.tool_search(
            query=params.get("query"),
            agent_role=params.get("agent_role"),
            permission=params.get("permission"),
            limit=int(params.get("limit") or 100),
        )
        return {
            "tools": [
                {
                    "name": item["name"],
                    "description": item["description"],
                    "inputSchema": self.registry.describe(item["name"])["input_schema"],
                    "metadata": item,
                }
                for item in search["tools"]
            ]
        }

    def _mcp_tool_call(self, params: dict[str, Any]) -> dict[str, Any]:
        name = str(params.get("name") or params.get("tool_name") or "")
        args = params.get("arguments")
        if args is None:
            args = params.get("payload") or {}
        result = self.call_tool(
            name,
            payload=args,
            context=params.get("context") or {},
            session_id=params.get("session_id"),
            agent_id=params.get("agent_id"),
        )
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(result, ensure_ascii=False, indent=2, default=str),
                }
            ],
            "isError": not bool(result["tool_result"].get("ok")),
            "structuredContent": result,
        }

    def _require_ledger(self) -> ConversationLedger:
        if self.ledger is None:
            raise KeyError("conversation_ledger_unavailable")
        return self.ledger

    @staticmethod
    def _compact_tool(spec: dict[str, Any]) -> dict[str, Any]:
        return {
            "name": spec["name"],
            "owner_agent": spec["owner_agent"],
            "permission": spec["permission"],
            "category": spec["category"],
            "description": spec["description"],
            "artifact": spec["artifact"],
            "requires_confirmation": spec["requires_confirmation"],
            "mutates_state": spec["mutates_state"],
        }
