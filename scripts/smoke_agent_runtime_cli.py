"""CLI smoke for runtime turns, approvals, events, and session transforms."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

TMP = Path(tempfile.mkdtemp(prefix="tpl_runtime_cli_"))
os.environ["TPL_DATA_DIR"] = str(TMP)
os.environ["TPL_DB_PATH"] = str(TMP / "runtime_cli.sqlite3")
os.environ["GENERATION_MODE"] = "template"
os.environ["LLM_PROVIDER"] = "template"
os.environ["TPL_LLM_PROVIDER"] = "template"
os.environ["TPL_EMBEDDING_BACKEND"] = "local-hashing"

FAILS: list[str] = []


def check(cond: bool, label: str, detail: str = "") -> None:
    print(f"[STATUS] {'ok' if cond else 'fail'} | {label}" + (f" | {detail}" if detail else ""))
    if not cond:
        FAILS.append(label)


def run_cli(*args: str) -> dict[str, Any]:
    env = os.environ.copy()
    proc = subprocess.run(
        [sys.executable, "-m", "pricinglibrary_rag.cli", *args],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        timeout=60,
        check=False,
    )
    if proc.returncode != 0:
        return {"_error": proc.stderr[-1000:], "_returncode": proc.returncode}
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        return {"_error": f"Invalid JSON: {exc}", "_stdout": proc.stdout[-1000:]}


def main() -> int:
    print("[STEP] create session and turn through CLI")
    session = run_cli("session-create", "--agent", "Chief of Staff", "--channel", "runtime-cli")
    check(bool(session.get("id")), "session-create", str(session.get("_error", ""))[:120])
    session_id = session["id"]
    message = run_cli("session-add-message", session_id, "--role", "user", "--text", "CLI runtime smoke")
    check(bool(message.get("id")), "session-add-message", str(message.get("_error", ""))[:120])
    turn = run_cli("turn-start", session_id, "--objective", "CLI runtime validation", "--input", '{"source":"smoke"}')
    check(turn.get("status") == "running", "turn-start", str(turn.get("_error", ""))[:120])
    turn = run_cli("turn-complete", turn["id"], "--output", '{"verdict":"PASS"}')
    check(turn.get("status") == "completed", "turn-complete", str(turn.get("_error", ""))[:120])
    turns = run_cli("turn-list", session_id)
    check(len(turns.get("turns", [])) == 1, "turn-list", str(turns.get("_error", ""))[:120])

    print("[STEP] approvals and transforms through CLI")
    approval = run_cli(
        "approval-request",
        session_id,
        "--agent",
        "Chief of Staff",
        "--tool-name",
        "desk.trader.stage_order",
        "--payload",
        '{"instrument":"EURUSD"}',
        "--reason",
        "cli smoke",
    )
    check(approval.get("status") == "requested", "approval-request", str(approval.get("_error", ""))[:120])
    approval = run_cli("approval-resolve", approval["id"], "--status", "approved", "--decision-note", "ok")
    check(approval.get("status") == "approved", "approval-resolve", str(approval.get("_error", ""))[:120])
    injected = run_cli(
        "session-inject",
        session_id,
        "--items",
        '[{"kind":"message","role":"system","body":"Injected by CLI smoke."}]',
    )
    check(len(injected.get("injected", [])) == 1, "session-inject", str(injected.get("_error", ""))[:120])
    summary = run_cli("session-compact", session_id, "--max-messages", "5")
    check("Recent sanitized context" in summary.get("summary", ""), "session-compact", str(summary.get("_error", ""))[:120])
    rollback = run_cli("session-rollback", session_id, "--message-id", message["id"], "--reason", "cli smoke")
    check(rollback.get("event", {}).get("event_type") == "session_rollback_marked", "session-rollback")
    events = run_cli("session-events", session_id)
    check(any(e["event_type"] == "session_compacted" for e in events.get("events", [])), "session-events")

    print("[STEP] fork through CLI")
    forked = run_cli("session-fork", session_id, "--target-agent", "Validator / Skeptic", "--include-last-messages", "2")
    check(forked.get("forked_session", {}).get("agent_id") == "Validator / Skeptic", "session-fork")

    import shutil

    shutil.rmtree(TMP, ignore_errors=True)
    if FAILS:
        print(f"[OUTPUT] AGENT RUNTIME CLI SMOKE: FAIL ({len(FAILS)})")
        return 1
    print("[OUTPUT] AGENT RUNTIME CLI SMOKE: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
