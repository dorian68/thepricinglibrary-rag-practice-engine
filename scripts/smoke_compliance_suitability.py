"""Smoke test for compliance and suitability guard tools."""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ["TPL_LLM_PROVIDER"] = "template"

from pricinglibrary_rag.tool_registry import get_tool_registry  # noqa: E402

FAILS: list[str] = []


def check(cond: bool, label: str, detail: str = "") -> None:
    print(f"[STATUS] {'ok' if cond else 'fail'} | {label}" + (f" | {detail}" if detail else ""))
    if not cond:
        FAILS.append(label)


def main() -> int:
    registry = get_tool_registry()
    payload = {
        "query": "Retail client asks for a leveraged autocall recommendation on crypto.",
        "payload": {"client_type": "retail", "product": "leveraged autocall", "asset": "crypto"},
    }

    print("[STEP] shared compliance tools")
    shared = [
        "compliance.classify_client",
        "compliance.check_product_eligibility",
        "compliance.detect_advice_boundary",
        "compliance.check_disclaimer_required",
        "compliance.approval_required",
    ]
    for tool in shared:
        spec = registry.describe(tool)
        check(spec["permission"] == "compliance", f"{tool}: compliance permission")
        run = registry.run(tool, payload=payload)
        check(run["ok"], f"{tool}: executes")
        check(bool(run["output"]["evidence"]), f"{tool}: evidence attached")

    print("[STEP] Sales-owned prechecks")
    sales_tools = [
        "desk.sales.suitability_precheck",
        "desk.sales.product_eligibility_precheck",
        "desk.sales.advice_boundary_check",
        "desk.sales.log_client_language",
    ]
    for tool in sales_tools:
        run = registry.run(tool, payload=payload)
        check(run["ok"], f"{tool}: executes")
        check(run["agent_role"] == "Sales", f"{tool}: owned by Sales")

    if FAILS:
        print(f"[OUTPUT] COMPLIANCE SMOKE: FAIL ({len(FAILS)})")
        return 1
    print("[OUTPUT] COMPLIANCE SMOKE: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())

