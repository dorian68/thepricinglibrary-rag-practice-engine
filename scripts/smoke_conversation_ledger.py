"""Smoke test for ConversationLedger and AgentTaskLedger."""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

TMP = Path(tempfile.mkdtemp(prefix="tpl_ledger_"))
os.environ["TPL_DATA_DIR"] = str(TMP)
os.environ["TPL_DB_PATH"] = str(TMP / "ledger.sqlite3")
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

    print("[STEP] create session and sanitized history")
    session = ledger.create_session(agent_id="Sales", channel="cli", external_user_id="client-1")
    check(session["agent_id"] == "Sales", "session created", session["id"])
    ledger.add_message(
        session["id"],
        role="user",
        body="RFQ hedge EURUSD. api_key=sk-test-secret-123456 <tool_call>{bad}</tool_call>",
    )
    hist = ledger.history(session["id"])
    body = hist["messages"][0]["body"]
    check("sk-test-secret" not in body, "history redacts token-like text")
    check("<tool_call>" not in body, "history strips tool-call scaffolding")

    print("[STEP] run tool and attach artifact")
    adapter = TplMcpAdapter(store=services.store)
    result = adapter.call_tool(
        "desk.sales.capture_rfq",
        payload={"query": "hedge EURUSD"},
        session_id=session["id"],
        agent_id="Sales",
    )
    check(result["tool_result"]["ok"], "tool call ok")
    check(bool(result["ledger_record"]["artifact"]["id"]), "tool result attached as artifact")
    artifacts = ledger.list_artifacts(session["id"])
    check(len(artifacts) == 1, "artifact list includes tool result")

    print("[STEP] task lifecycle")
    task = ledger.create_task(agent_id="Validator / Skeptic", title="Validate pricing pack", parent_session_id=session["id"])
    check(task["status"] == "queued", "task queued", task["id"])
    task = ledger.update_task(task["id"], status="done", result_summary="Validation passed")
    check(task["status"] == "done" and bool(task["ended_at"]), "task terminal update")
    tasks = ledger.list_tasks(status="done")
    check(any(t["id"] == task["id"] for t in tasks), "task list finds terminal task")

    import shutil

    shutil.rmtree(TMP, ignore_errors=True)
    if FAILS:
        print(f"[OUTPUT] CONVERSATION LEDGER SMOKE: FAIL ({len(FAILS)})")
        return 1
    print("[OUTPUT] CONVERSATION LEDGER SMOKE: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
