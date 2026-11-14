"""Smoke test for the OpenClaw-inspired TPL interaction gateway."""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

TMP = Path(tempfile.mkdtemp(prefix="tpl_gateway_"))
os.environ["TPL_DATA_DIR"] = str(TMP)
os.environ["TPL_DB_PATH"] = str(TMP / "gateway.sqlite3")
os.environ["GENERATION_MODE"] = "template"
os.environ["LLM_PROVIDER"] = "template"
os.environ["TPL_LLM_PROVIDER"] = "template"
os.environ["TPL_EMBEDDING_BACKEND"] = "local-hashing"

from pricinglibrary_rag.agent_gateway import AgentInteractionGateway  # noqa: E402
from pricinglibrary_rag.conversation_ledger import ConversationLedger  # noqa: E402
from pricinglibrary_rag.factory import build_services  # noqa: E402

FAILS: list[str] = []


def check(cond: bool, label: str, detail: str = "") -> None:
    print(f"[STATUS] {'ok' if cond else 'fail'} | {label}" + (f" | {detail}" if detail else ""))
    if not cond:
        FAILS.append(label)


def main() -> int:
    services = build_services()
    gateway = AgentInteractionGateway(services.store)
    ledger = ConversationLedger(services.store)

    print("[STEP] first inbound routed to Sales and tool")
    first = gateway.handle_inbound(
        channel="openclaw-webchat",
        external_user_id="client-a",
        body="Please capture this EURUSD hedge RFQ.",
        target_agent="Sales",
        tool_name="desk.sales.capture_rfq",
    )
    session_id = first["session"]["id"]
    check(first["session"]["agent_id"] == "Sales", "session routed to Sales")
    check(first["tool_result"]["tool_result"]["ok"], "gateway tool call succeeds")
    check(bool(first["assistant_message"]), "gateway writes assistant summary")

    print("[STEP] second inbound reuses same route/session")
    second = gateway.handle_inbound(
        channel="openclaw-webchat",
        external_user_id="client-a",
        body="Add a 3 month tenor to that same RFQ.",
        target_agent="Sales",
    )
    check(second["session"]["id"] == session_id, "same sender/channel reuses session")
    hist = ledger.history(session_id, limit=10)
    check(len(hist["messages"]) >= 3, "session history accumulates messages", str(len(hist["messages"])))
    artifacts = ledger.list_artifacts(session_id)
    check(len(artifacts) >= 1, "session has tool artifact")

    import shutil

    shutil.rmtree(TMP, ignore_errors=True)
    if FAILS:
        print(f"[OUTPUT] AGENT GATEWAY SMOKE: FAIL ({len(FAILS)})")
        return 1
    print("[OUTPUT] AGENT GATEWAY SMOKE: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
