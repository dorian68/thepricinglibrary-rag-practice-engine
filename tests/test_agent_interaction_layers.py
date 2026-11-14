from pricinglibrary_rag.agent_gateway import AgentInteractionGateway
from pricinglibrary_rag.conversation_ledger import ConversationLedger
from pricinglibrary_rag.mcp_adapter import TplMcpAdapter
from pricinglibrary_rag.storage import LocalStore


def test_conversation_ledger_sanitizes_and_tracks_tasks(tmp_path):
    store = LocalStore(tmp_path / "ledger.sqlite3")
    ledger = ConversationLedger(store)
    session = ledger.create_session(agent_id="Sales", channel="pytest", external_user_id="u1")
    ledger.add_message(
        session["id"],
        role="user",
        body="hello token=super-secret-value <tool_call>{bad}</tool_call>",
    )

    body = ledger.history(session["id"])["messages"][0]["body"]
    assert "super-secret-value" not in body
    assert "<tool_call>" not in body

    task = ledger.create_task(agent_id="Validator / Skeptic", title="Validate", parent_session_id=session["id"])
    task = ledger.update_task(task["id"], status="done", result_summary="ok")
    assert task["status"] == "done"
    assert task["ended_at"]


def test_mcp_adapter_calls_tool_and_attaches_artifact(tmp_path):
    store = LocalStore(tmp_path / "mcp.sqlite3")
    ledger = ConversationLedger(store)
    session = ledger.create_session(agent_id="Sales", channel="pytest")
    adapter = TplMcpAdapter(store=store)

    search = adapter.tool_search(query="capture rfq", agent_role="Sales")
    assert any(t["name"] == "desk.sales.capture_rfq" for t in search["tools"])

    result = adapter.call_tool(
        "desk.sales.capture_rfq",
        payload={"query": "hedge EURUSD"},
        session_id=session["id"],
        agent_id="Sales",
    )
    assert result["tool_result"]["ok"]
    assert ledger.list_artifacts(session["id"])


def test_agent_gateway_reuses_sender_session(tmp_path):
    store = LocalStore(tmp_path / "gateway.sqlite3")
    gateway = AgentInteractionGateway(store)

    first = gateway.handle_inbound(
        channel="webchat",
        external_user_id="client",
        body="Capture RFQ",
        target_agent="Sales",
        tool_name="desk.sales.capture_rfq",
    )
    second = gateway.handle_inbound(
        channel="webchat",
        external_user_id="client",
        body="Follow up",
        target_agent="Sales",
    )

    assert first["session"]["id"] == second["session"]["id"]
    assert first["tool_result"]["tool_result"]["ok"]


def test_runtime_turns_approvals_and_thread_transforms(tmp_path):
    store = LocalStore(tmp_path / "runtime.sqlite3")
    ledger = ConversationLedger(store)
    session = ledger.create_session(agent_id="Chief of Staff", channel="pytest-runtime")
    first_message = ledger.add_message(session["id"], role="user", body="Patch runtime.")

    turn = ledger.start_turn(session["id"], objective="Implement runtime", input_payload={"message_id": first_message["id"]})
    assert turn["status"] == "running"
    turn = ledger.complete_turn(turn["id"], output_payload={"verdict": "PASS"})
    assert turn["status"] == "completed"
    assert ledger.list_turns(session["id"])[0]["id"] == turn["id"]

    approval = ledger.request_approval(
        session["id"],
        agent_id="Chief of Staff",
        tool_name="desk.trader.stage_order",
        payload={"instrument": "EURUSD"},
        reason="sensitive tool",
    )
    assert approval["status"] == "requested"
    approval = ledger.resolve_approval(approval["id"], status="approved")
    assert approval["status"] == "approved"
    assert ledger.list_approvals(session_id=session["id"], status="approved")

    adapter = TplMcpAdapter(store=store)
    sensitive_payload = {"query": "guard EURUSD"}
    blocked = adapter.call_tool(
        "quant.execution_cost.live_trading_guard",
        payload=sensitive_payload,
        session_id=session["id"],
        agent_id="Execution / Cost",
    )
    assert not blocked["tool_result"]["ok"]
    assert "confirmation_required" in blocked["tool_result"]["output"]["warnings"]
    sensitive_approval = ledger.request_approval(
        session["id"],
        agent_id="Execution / Cost",
        tool_name="quant.execution_cost.live_trading_guard",
        payload=sensitive_payload,
        reason="allow smoke execution",
    )
    ledger.resolve_approval(sensitive_approval["id"], status="approved")
    allowed = adapter.call_tool(
        "quant.execution_cost.live_trading_guard",
        payload=sensitive_payload,
        session_id=session["id"],
        agent_id="Execution / Cost",
    )
    assert allowed["tool_result"]["ok"]

    injected = ledger.inject_items(
        session["id"],
        [{"kind": "message", "role": "system", "body": "Injected context."}],
        source="pytest:inject",
    )
    assert len(injected["injected"]) == 1
    summary = ledger.compact_session(session["id"], max_messages=5)
    assert "Recent sanitized context" in summary["summary"]

    forked = ledger.fork_session(session["id"], target_agent="Validator / Skeptic")
    assert forked["forked_session"]["agent_id"] == "Validator / Skeptic"
    assert forked["injected_message"]["source"] == "runtime:fork"

    rollback = ledger.rollback_session(session["id"], message_id=first_message["id"])
    assert rollback["event"]["event_type"] == "session_rollback_marked"
    assert [message["id"] for message in rollback["effective_history"]] == [first_message["id"]]
