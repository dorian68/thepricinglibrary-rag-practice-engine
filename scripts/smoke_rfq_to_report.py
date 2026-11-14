"""End-to-end RFQ -> report smoke for the agentic trading floor."""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ["TPL_LLM_PROVIDER"] = "template"

from pricinglibrary_rag.desk import DeskOrchestrator  # noqa: E402
from pricinglibrary_rag.llm import TemplateLLM  # noqa: E402
from pricinglibrary_rag.tool_registry import get_tool_registry  # noqa: E402

FAILS: list[str] = []


def check(cond: bool, label: str, detail: str = "") -> None:
    print(f"[STATUS] {'ok' if cond else 'fail'} | {label}" + (f" | {detail}" if detail else ""))
    if not cond:
        FAILS.append(label)


def main() -> int:
    print("[STEP] run desk chain")
    desk = DeskOrchestrator(TemplateLLM())
    result = desk.run("I need to hedge a EURUSD exposure with a 6 month option, notional 1m EUR.")
    check(result["desk"] == "FX", "RFQ routed to FX", result["desk"])
    check(len(result["agents"]) == 8, "8 role agents executed")
    check(len(result["audit_trail"]) >= 8, "agent audit trail covers full chain", str(len(result["audit_trail"])))

    print("[STEP] verify deterministic analytics")
    pricing = result["pricing_result"]
    quote = result["quote"]
    risk = result["risk"]
    check(pricing.get("theoretical_price") is not None, "theoretical price present")
    check(quote["bid"] < quote["mid"] < quote["ask"], "bid < mid < ask")
    check(risk["status"] in {"GREEN", "AMBER", "RED"}, "risk status present", risk["status"])
    check(result["report"]["disclaimer"].lower().find("not investment advice") >= 0, "client disclaimer present")

    print("[STEP] run one registry-backed report tool")
    registry = get_tool_registry()
    tool_name = "desk.report.generate_pricing_note"
    run = registry.run(tool_name, payload={"query": result["report"]["client_summary"]})
    check(run["ok"], "pricing-note tool executes")
    check(run["output"]["artifact"] == "ClientReport", "report tool emits ClientReport")
    check(bool(registry.audit(run["id"])), "report tool audit can be loaded")

    if FAILS:
        print(f"[OUTPUT] RFQ TO REPORT SMOKE: FAIL ({len(FAILS)})")
        return 1
    print("[OUTPUT] RFQ TO REPORT SMOKE: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())

