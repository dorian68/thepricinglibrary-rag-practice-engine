"""Local interaction gateway for TPL agent teams.

This is the TPL-native version of the OpenClaw-inspired gateway pattern:
resolve a sender/channel to a durable session, append inbound messages, run
governed tools when requested, and keep route metadata for later delivery.
"""
from __future__ import annotations

from typing import Any

from .agent_runtime_hooks import AgentRuntimeHooks
from .conversation_ledger import ConversationLedger
from .mcp_adapter import TplMcpAdapter
from .storage import LocalStore


class AgentInteractionGateway:
    def __init__(self, store: LocalStore) -> None:
        self.ledger = ConversationLedger(store)
        self.adapter = TplMcpAdapter(store=store)
        self.hooks = AgentRuntimeHooks(self.ledger)

    def handle_inbound(
        self,
        *,
        channel: str,
        external_user_id: str,
        body: str,
        target_agent: str = "Chief of Staff",
        route_metadata: dict[str, Any] | None = None,
        tool_name: str | None = None,
        payload: dict[str, Any] | None = None,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        session = self._resolve_or_create_session(
            agent_id=target_agent,
            channel=channel,
            external_user_id=external_user_id,
            route_metadata=route_metadata or {},
        )
        inbound = self.ledger.add_message(
            session["id"],
            role="user",
            body=body,
            visibility="agent_visible",
            source=f"gateway:{channel}",
            metadata={"external_user_id": external_user_id},
        )
        self.hooks.emit(
            "inbound_message_received",
            session_id=session["id"],
            payload={
                "channel": channel,
                "external_user_id": external_user_id,
                "target_agent": target_agent,
                "message_id": inbound["id"],
            },
        )
        tool_result = None
        assistant = None
        if tool_name:
            tool_result = self.adapter.call_tool(
                tool_name,
                payload=payload or {"query": body},
                context={**(context or {}), "query": body},
                session_id=session["id"],
                agent_id=target_agent,
            )
            summary = (
                tool_result.get("tool_result", {})
                .get("output", {})
                .get("summary", "Tool completed.")
            )
            self.hooks.emit(
                "before_client_send",
                session_id=session["id"],
                payload={
                    "channel": channel,
                    "external_user_id": external_user_id,
                    "source": "tool_result",
                    "tool_name": tool_name,
                },
            )
            assistant = self.ledger.add_message(
                session["id"],
                role="assistant",
                body=str(summary),
                visibility="agent_visible",
                source="gateway:tool_result",
                metadata={"tool_name": tool_name},
            )
        return {
            "session": self.ledger.get_session(session["id"]),
            "inbound_message": inbound,
            "assistant_message": assistant,
            "tool_result": tool_result,
        }

    def _resolve_or_create_session(
        self,
        *,
        agent_id: str,
        channel: str,
        external_user_id: str,
        route_metadata: dict[str, Any],
    ) -> dict[str, Any]:
        for session in self.ledger.list_sessions(agent_id=agent_id, channel=channel, status="active", limit=200):
            if session.get("external_user_id") == external_user_id:
                return session
        return self.ledger.create_session(
            agent_id=agent_id,
            channel=channel,
            external_user_id=external_user_id,
            title=f"{channel}:{external_user_id}:{agent_id}",
            route_metadata=route_metadata,
        )
