"""Smoke test for Codex/OpenClaw-inspired runtime state primitives."""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

TMP = Path(tempfile.mkdtemp(prefix="tpl_runtime_state_"))
os.environ["TPL_DATA_DIR"] = str(TMP)
os.environ["TPL_DB_PATH"] = str(TMP / "runtime_state.sqlite3")
os.environ["GENERATION_MODE"] = "template"
os.environ["LLM_PROVIDER"] = "template"
os.environ["TPL_LLM_PROVIDER"] = "template"
os.environ["TPL_EMBEDDING_BACKEND"] = "local-hashing"

from pricinglibrary_rag.agent_gateway import AgentInteractionGateway  # noqa: E402
from pricinglibrary_rag.conversation_ledger import ConversationLedger  # noqa: E402
from pricinglibrary_rag.factory import build_services  # noqa: E402
from pricinglibrary_rag.mcp_adapter import TplMcpAdapter  # noqa: E402

FAILS: list[str] = []


def check(cond: bool, label: str, detail: str = "") -> None:
    print(f"[STATUS] {'ok' if cond else 'fail'} | {label}" + (f" | {detail}" if detail else ""))
    if not cond:
        FAILS.append(label)


def main() -> int:
    services = build_services()
    ledger = ConversationLedger(services.store)
    session = ledger.create_session(agent_id="Chief of Staff", channel="runtime-smoke")
    msg = ledger.add_message(session["id"], role="user", body="Validate this workflow.")

    print("[STEP] turn lifecycle")
    turn = ledger.start_turn(session["id"], objective="Validate runtime", input_payload={"message_id": msg["id"]})
    check(turn["status"] == "running", "turn starts")
    turn = ledger.complete_turn(turn["id"], output_payload={"verdict": "PASS"})
    check(turn["status"] == "completed" and bool(turn["ended_at"]), "turn completes")

    print("[STEP] approvals")
    approval = ledger.request_approval(
        session["id"],
        agent_id="Chief of Staff",
        tool_name="desk.trader.stage_order",
        payload={"instrument": "EURUSD", "notional": 1},
        reason="sensitive staged order",
    )
    check(approval["status"] == "requested" and approval["payload_hash"], "approval requested")
    approval = ledger.resolve_approval(approval["id"], status="approved", decision_note="ok in smoke")
    check(approval["status"] == "approved" and approval["resolved_at"], "approval resolved")

    print("[STEP] approval-backed sensitive tool confirmation")
    adapter = TplMcpAdapter(store=services.store)
    sensitive_payload = {"query": "guard EURUSD"}
    blocked = adapter.call_tool(
        "quant.execution_cost.live_trading_guard",
        payload=sensitive_payload,
        session_id=session["id"],
        agent_id="Execution / Cost",
    )
    check(not blocked["tool_result"]["ok"], "sensitive tool blocked without matching approval")
    sensitive_approval = ledger.request_approval(
        session["id"],
        agent_id="Execution / Cost",
        tool_name="quant.execution_cost.live_trading_guard",
        payload=sensitive_payload,
        reason="smoke approval",
    )
    ledger.resolve_approval(sensitive_approval["id"], status="approved")
    allowed = adapter.call_tool(
        "quant.execution_cost.live_trading_guard",
        payload=sensitive_payload,
        session_id=session["id"],
        agent_id="Execution / Cost",
    )
    check(allowed["tool_result"]["ok"], "approved sensitive tool runs")

    print("[STEP] compact, inject, fork, rollback")
    injected = ledger.inject_items(
        session["id"],
        [{"kind": "message", "role": "system", "body": "Injected context for subagent."}],
        source="smoke:inject",
    )
    check(len(injected["injected"]) == 1, "item injected")
    summary = ledger.compact_session(session["id"], max_messages=5)
    check(summary["source_message_count"] >= 2 and "Recent sanitized context" in summary["summary"], "session compacted")
    forked = ledger.fork_session(session["id"], target_agent="Validator / Skeptic", include_last_messages=3)
    child_id = forked["forked_session"]["id"]
    check(child_id != session["id"] and forked["injected_message"], "session forked with context")
    rollback = ledger.rollback_session(session["id"], message_id=msg["id"], reason="smoke rollback")
    check(rollback["event"]["event_type"] == "session_rollback_marked", "rollback event recorded")
    check(len(rollback["effective_history"]) == 1, "rollback effective history bounded")

    print("[STEP] lifecycle hooks from adapter and gateway")
    tool = adapter.call_tool(
        "desk.sales.capture_rfq",
        payload={"query": "hedge EURUSD"},
        session_id=session["id"],
        agent_id="Sales",
    )
    check(tool["tool_result"]["ok"], "adapter tool call ok")
    gateway = AgentInteractionGateway(services.store)
    inbound = gateway.handle_inbound(
        channel="runtime-gateway",
        external_user_id="client",
        body="Capture RFQ",
        target_agent="Sales",
        tool_name="desk.sales.capture_rfq",
    )
    check(inbound["tool_result"]["tool_result"]["ok"], "gateway tool call ok")
    events = ledger.list_events(session_id=session["id"], limit=50)
    event_types = {event["event_type"] for event in events}
    check({"before_tool_run", "after_tool_run", "session_compacted"} <= event_types, "runtime events captured")

    import shutil

    shutil.rmtree(TMP, ignore_errors=True)
    if FAILS:
        print(f"[OUTPUT] AGENT RUNTIME STATE SMOKE: FAIL ({len(FAILS)})")
        return 1
    print("[OUTPUT] AGENT RUNTIME STATE SMOKE: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
