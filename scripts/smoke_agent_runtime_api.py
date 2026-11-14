"""HTTP smoke for agent runtime turns, approvals, thread transforms, and events."""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

TMP = Path(tempfile.mkdtemp(prefix="tpl_runtime_api_"))
os.environ["TPL_DATA_DIR"] = str(TMP)
os.environ["TPL_DB_PATH"] = str(TMP / "runtime_api.sqlite3")
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

    print("[STEP] create session and turn")
    r = client.post("/agent/sessions", json={"agent_id": "Chief of Staff", "channel": "runtime-api"})
    check(r.status_code == 200, "POST /agent/sessions", r.text[:80])
    session_id = r.json()["id"]
    r = client.post(f"/agent/sessions/{session_id}/messages", json={"role": "user", "body": "Audit runtime."})
    check(r.status_code == 200, "POST message")
    message_id = r.json()["id"]
    r = client.post(
        f"/agent/sessions/{session_id}/turns",
        json={"objective": "API runtime validation", "input_payload": {"message_id": message_id}},
    )
    check(r.status_code == 200 and r.json()["status"] == "running", "POST turn start")
    turn_id = r.json()["id"]
    r = client.post(f"/agent/turns/{turn_id}/complete", json={"output_payload": {"ok": True}})
    check(r.status_code == 200 and r.json()["status"] == "completed", "POST turn complete")
    r = client.get(f"/agent/sessions/{session_id}/turns")
    check(r.status_code == 200 and len(r.json()["turns"]) == 1, "GET turns")

    print("[STEP] approvals and transforms")
    r = client.post(
        "/agent/approvals",
        json={
            "session_id": session_id,
            "agent_id": "Chief of Staff",
            "tool_name": "desk.trader.stage_order",
            "payload": {"instrument": "EURUSD"},
            "reason": "sensitive action",
        },
    )
    check(r.status_code == 200 and r.json()["status"] == "requested", "POST approval")
    approval_id = r.json()["id"]
    r = client.post(f"/agent/approvals/{approval_id}/resolve", json={"status": "approved"})
    check(r.status_code == 200 and r.json()["status"] == "approved", "POST approval resolve")
    r = client.post(
        f"/agent/sessions/{session_id}/inject",
        json={"items": [{"kind": "message", "role": "system", "body": "Injected via API."}]},
    )
    check(r.status_code == 200 and len(r.json()["injected"]) == 1, "POST inject")
    r = client.post(f"/agent/sessions/{session_id}/compact", json={"max_messages": 5})
    check(r.status_code == 200 and "Recent sanitized context" in r.json()["summary"], "POST compact")
    r = client.get(f"/agent/sessions/{session_id}/summaries")
    check(r.status_code == 200 and len(r.json()["summaries"]) == 1, "GET summaries")
    r = client.post(f"/agent/sessions/{session_id}/fork", json={"target_agent": "Validator / Skeptic"})
    check(r.status_code == 200 and r.json()["forked_session"]["id"] != session_id, "POST fork")
    r = client.post(f"/agent/sessions/{session_id}/rollback", json={"message_id": message_id, "reason": "api smoke"})
    check(r.status_code == 200 and r.json()["event"]["event_type"] == "session_rollback_marked", "POST rollback")

    print("[STEP] runtime events")
    r = client.get(f"/agent/sessions/{session_id}/events")
    event_types = {event["event_type"] for event in r.json()["events"]}
    check(r.status_code == 200 and "session_compacted" in event_types, "GET events")

    import shutil

    shutil.rmtree(TMP, ignore_errors=True)
    if FAILS:
        print(f"[OUTPUT] AGENT RUNTIME API SMOKE: FAIL ({len(FAILS)})")
        return 1
    print("[OUTPUT] AGENT RUNTIME API SMOKE: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
