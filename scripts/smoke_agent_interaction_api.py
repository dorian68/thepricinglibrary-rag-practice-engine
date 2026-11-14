"""HTTP smoke for sessions, tasks, MCP adapter, and gateway endpoints."""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

TMP = Path(tempfile.mkdtemp(prefix="tpl_interaction_api_"))
os.environ["TPL_DATA_DIR"] = str(TMP)
os.environ["TPL_DB_PATH"] = str(TMP / "interaction_api.sqlite3")
os.environ["GENERATION_MODE"] = "template"
os.environ["LLM_PROVIDER"] = "template"
os.environ["TPL_LLM_PROVIDER"] = "template"
os.environ["TPL_EMBEDDING_BACKEND"] = "local-hashing"

from fastapi.testclient import TestClient  # noqa: E402

from pricinglibrary_rag.api import create_app  # noqa: E402
from pricinglibrary_rag.factory import build_services  # noqa: E402

FAILS: list[str] = []


def check(cond: bool, label: str, detail: str = "") -> None:
    print(f"[STATUS] {'ok' if cond else 'fail'} | {label}" + (f" | {detail}" if detail else ""))
    if not cond:
        FAILS.append(label)


def main() -> int:
    client = TestClient(create_app(build_services()))

    print("[STEP] sessions and sanitized history")
    r = client.post("/agent/sessions", json={"agent_id": "Sales", "channel": "api", "external_user_id": "c1"})
    check(r.status_code == 200, "POST /agent/sessions", r.text[:80])
    session_id = r.json()["id"]
    r = client.post(
        f"/agent/sessions/{session_id}/messages",
        json={"role": "user", "body": "RFQ token=super-secret-token-123 <tool_call>bad</tool_call>"},
    )
    check(r.status_code == 200, "POST /agent/sessions/{id}/messages")
    r = client.get(f"/agent/sessions/{session_id}/history")
    body = r.json()["messages"][0]["body"]
    check(r.status_code == 200 and "super-secret-token" not in body, "GET history redacts secrets")
    check("<tool_call>" not in body, "GET history strips tool calls")

    print("[STEP] session-bound tool run and artifacts")
    r = client.post(
        f"/agent/sessions/{session_id}/tools/desk.sales.capture_rfq/run",
        json={"payload": {"query": "hedge EURUSD"}, "agent_id": "Sales"},
    )
    check(r.status_code == 200 and r.json()["tool_result"]["ok"], "POST session tool run")
    r = client.get(f"/agent/sessions/{session_id}/artifacts")
    check(r.status_code == 200 and len(r.json()["artifacts"]) == 1, "GET session artifacts")

    print("[STEP] task lifecycle")
    r = client.post("/agent/tasks", json={"agent_id": "Validator / Skeptic", "title": "Validate", "parent_session_id": session_id})
    check(r.status_code == 200, "POST /agent/tasks")
    task_id = r.json()["id"]
    r = client.post(f"/agent/tasks/{task_id}/status", json={"status": "done", "result_summary": "ok"})
    check(r.status_code == 200 and r.json()["status"] == "done", "POST /agent/tasks/{id}/status")

    print("[STEP] MCP handle and gateway inbound")
    r = client.post(
        "/agent/mcp/handle",
        json={"jsonrpc": "2.0", "id": "m1", "method": "tpl/agents_coverage", "params": {}},
    )
    check(r.status_code == 200 and r.json()["result"]["agent_count"] == 16, "POST /agent/mcp/handle")
    r = client.post(
        "/agent/gateway/inbound",
        json={
            "channel": "openclaw-webchat",
            "external_user_id": "client-x",
            "body": "Capture this RFQ",
            "target_agent": "Sales",
            "tool_name": "desk.sales.capture_rfq",
        },
    )
    check(r.status_code == 200 and r.json()["tool_result"]["tool_result"]["ok"], "POST /agent/gateway/inbound")

    import shutil

    shutil.rmtree(TMP, ignore_errors=True)
    if FAILS:
        print(f"[OUTPUT] AGENT INTERACTION API SMOKE: FAIL ({len(FAILS)})")
        return 1
    print("[OUTPUT] AGENT INTERACTION API SMOKE: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
