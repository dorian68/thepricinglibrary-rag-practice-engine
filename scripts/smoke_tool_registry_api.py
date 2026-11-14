"""Smoke test for the HTTP tool-registry endpoints."""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ["GENERATION_MODE"] = "template"
os.environ["LLM_PROVIDER"] = "template"
os.environ["TPL_LLM_PROVIDER"] = "template"

from fastapi.testclient import TestClient  # noqa: E402

from pricinglibrary_rag.api import create_app  # noqa: E402

FAILS: list[str] = []


def check(cond: bool, label: str, detail: str = "") -> None:
    print(f"[STATUS] {'ok' if cond else 'fail'} | {label}" + (f" | {detail}" if detail else ""))
    if not cond:
        FAILS.append(label)


def main() -> int:
    client = TestClient(create_app())

    print("[STEP] registry API coverage")
    coverage = client.get("/agent/tools/coverage")
    check(coverage.status_code == 200, "GET /agent/tools/coverage -> 200")
    body = coverage.json()
    check(body.get("agent_count") == 16, "coverage: 16 agents")
    check(body.get("tool_count", 0) >= 500, "coverage: broad tool surface", str(body.get("tool_count")))
    check(body.get("all_ok") is True, "coverage: all_ok true")

    print("[STEP] list/describe/run/audit")
    listed = client.get("/agent/tools?agent_role=Sales")
    check(listed.status_code == 200 and listed.json().get("tools"), "GET /agent/tools?agent_role=Sales")
    desc = client.get("/agent/tools/desk.sales.capture_rfq")
    check(desc.status_code == 200 and desc.json().get("artifact") == "RFQTicket", "GET /agent/tools/{tool}")
    run = client.post("/agent/tools/desk.sales.capture_rfq/run", json={"payload": {"query": "hedge rates"}})
    check(run.status_code == 200 and run.json().get("ok"), "POST /agent/tools/{tool}/run")
    call_id = run.json().get("id")
    audit = client.get(f"/agent/tools/audit/{call_id}")
    check(audit.status_code == 200 and audit.json().get("id") == call_id, "GET /agent/tools/audit/{id}")

    if FAILS:
        print(f"[OUTPUT] TOOL REGISTRY API SMOKE: FAIL ({len(FAILS)})")
        return 1
    print("[OUTPUT] TOOL REGISTRY API SMOKE: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())

