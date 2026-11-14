"""Smoke test for Execution/Cost capacity and net-edge tools."""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ["TPL_LLM_PROVIDER"] = "template"

from pricinglibrary_rag.tool_registry import get_tool_registry  # noqa: E402


def main() -> int:
    registry = get_tool_registry()
    payload = {"query": "validated signal net of spread, slippage, market impact and capacity"}
    tools = [
        "quant.execution_cost.spread_model",
        "quant.execution_cost.slippage_model",
        "quant.execution_cost.market_impact_model",
        "quant.execution_cost.capacity_curve",
        "quant.execution_cost.net_edge_after_costs",
        "quant.execution_cost.execution_report",
    ]
    ok = True
    print("[STEP] capacity/net-of-cost contract")
    for tool in tools:
        result = registry.run(tool, payload=payload)
        status = result["ok"] and result["output"]["artifact"] == "ExecutionVerdict"
        ok = ok and status
        print(f"[STATUS] {'ok' if status else 'fail'} | {tool}")
    print(f"[OUTPUT] CAPACITY CURVE SMOKE: {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

