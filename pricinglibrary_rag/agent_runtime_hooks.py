"""Lifecycle hooks for TPL agent runtimes.

Hooks are deliberately small and durable: callers can emit events before/after
tool execution, before client delivery, or after subagent work without coupling
the gateway/MCP adapter to a specific orchestrator.
"""
from __future__ import annotations

from collections.abc import Callable
from typing import Any

from .conversation_ledger import ConversationLedger

HookHandler = Callable[[dict[str, Any]], None]


class AgentRuntimeHooks:
    def __init__(self, ledger: ConversationLedger | None = None) -> None:
        self.ledger = ledger
        self._handlers: dict[str, list[HookHandler]] = {}

    def register(self, event_type: str, handler: HookHandler) -> None:
        self._handlers.setdefault(event_type, []).append(handler)

    def emit(
        self,
        event_type: str,
        *,
        session_id: str | None = None,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        event = {
            "event_type": event_type,
            "session_id": session_id,
            "payload": payload or {},
            "recorded": False,
        }
        if self.ledger is not None:
            stored = self.ledger.record_event(session_id, event_type, payload or {})
            event = {**stored, "recorded": True}
        for handler in self._handlers.get(event_type, []):
            handler(event)
        for handler in self._handlers.get("*", []):
            handler(event)
        return event
