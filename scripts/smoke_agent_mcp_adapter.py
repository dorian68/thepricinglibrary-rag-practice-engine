"""Smoke test for the TPL MCP-style adapter."""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

TMP = Path(tempfile.mkdtemp(prefix="tpl_mcp_"))
os.environ["TPL_DATA_DIR"] = str(TMP)
os.environ["TPL_DB_PATH"] = str(TMP / "mcp.sqlite3")
os.environ["GENERATION_MODE"] = "template"
os.environ["LLM_PROVIDER"] = "template"
os.environ["TPL_LLM_PROVIDER"] = "template"
os.environ["TPL_EMBEDDING_BACKEND"] = "local-hashing"

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
    adapter = TplMcpAdapter(store=services.store)
    session = ledger.create_session(agent_id="Sales", channel="mcp", external_user_id="codex")
    ledger.add_message(session["id"], role="user", body="Need a EURUSD hedge RFQ.")

    print("[STEP] discovery")
    init = adapter.handle("initialize")
    check(init["serverInfo"]["name"] == "thepricinglibrary-tool-registry", "initialize returns server info")
    search = adapter.tool_search(query="capture rfq", agent_role="Sales")
    check(any(t["name"] == "desk.sales.capture_rfq" for t in search["tools"]), "tool_search finds Sales RFQ tool")
    listed = adapter.handle("tools/list", {"agent_role": "Sales", "query": "capture rfq"})
    check(bool(listed["tools"][0]["inputSchema"]), "tools/list includes input schema")

    print("[STEP] call/audit/replay")
    call = adapter.handle(
        "tools/call",
        {
            "name": "desk.sales.capture_rfq",
            "arguments": {"query": "hedge EURUSD"},
            "session_id": session["id"],
            "agent_id": "Sales",
        },
    )
    structured = call["structuredContent"]
    check(not call["isError"], "tools/call succeeds")
    audit_id = structured["tool_result"]["id"]
    audit = adapter.handle("tpl/tool_audit", {"tool_call_id": audit_id})
    check(audit["id"] == audit_id, "tool audit works")
    replay = adapter.handle("tpl/tool_replay", {"tool_call_id": audit_id})
    check(replay["ok"], "tool replay works")
    conv = adapter.handle("tpl/conversation_search", {"query": "EURUSD"})
    check(conv["count"] >= 1, "conversation_search returns sanitized match")

    print("[STEP] runtime methods")
    turn = adapter.handle(
        "tpl/turn_start",
        {
            "session_id": session["id"],
            "objective": "MCP runtime smoke",
            "input_payload": {"source": "smoke"},
        },
    )
    check(turn["status"] == "running", "turn_start works")
    turn = adapter.handle("tpl/turn_complete", {"turn_id": turn["id"], "output_payload": {"ok": True}})
    check(turn["status"] == "completed", "turn_complete works")
    summary = adapter.handle("tpl/session_compact", {"session_id": session["id"], "max_messages": 5})
    check("Recent sanitized context" in summary["summary"], "session_compact works")
    events = adapter.handle("tpl/session_events", {"session_id": session["id"]})
    check(any(e["event_type"] == "session_compacted" for e in events["events"]), "session_events works")

    print("[STEP] JSON-RPC envelope")
    rpc = adapter.jsonrpc({"jsonrpc": "2.0", "id": 7, "method": "tpl/agents_coverage", "params": {}})
    check(rpc["id"] == 7 and rpc["result"]["agent_count"] == 16, "jsonrpc coverage response")

    import shutil

    shutil.rmtree(TMP, ignore_errors=True)
    if FAILS:
        print(f"[OUTPUT] MCP ADAPTER SMOKE: FAIL ({len(FAILS)})")
        return 1
    print("[OUTPUT] MCP ADAPTER SMOKE: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
