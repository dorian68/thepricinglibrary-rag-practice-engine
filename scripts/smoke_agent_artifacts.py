"""Smoke test that every agent exposes a signed artifact contract."""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ["TPL_LLM_PROVIDER"] = "template"

from pricinglibrary_rag.desk import DeskOrchestrator  # noqa: E402
from pricinglibrary_rag.llm import TemplateLLM  # noqa: E402
from pricinglibrary_rag.tool_registry import QUANT_RESEARCH_ROLES, get_tool_registry  # noqa: E402

FAILS: list[str] = []


def check(cond: bool, label: str, detail: str = "") -> None:
    print(f"[STATUS] {'ok' if cond else 'fail'} | {label}" + (f" | {detail}" if detail else ""))
    if not cond:
        FAILS.append(label)


def main() -> int:
    registry = get_tool_registry()
    desk = DeskOrchestrator(TemplateLLM())
    result = desk.run("Build me a protected autocall on SPX with 1 year maturity")

    print("[STEP] desk artifacts")
    expected_keys = [
        "rfq", "product_spec", "market_snapshot", "model_choice",
        "pricing_result", "quote", "risk", "report",
    ]
    for key in expected_keys:
        check(result.get(key) is not None, f"desk result has {key}")
    check(result["tool_registry"]["all_ok"], "desk response carries passing registry coverage")
    for agent in result["agents"]:
        check(len(agent.get("tools", [])) >= 21, f"{agent['name']}: rich tool list", str(len(agent.get("tools", []))))
        check(agent.get("data") is not None, f"{agent['name']}: data artifact produced")

    print("[STEP] quant DAG artifacts")
    for role in QUANT_RESEARCH_ROLES:
        agent = registry.agents[role]
        role_tools = [t for t in agent.allowed_tools if registry.tools[t].owner_agent == role]
        check(bool(role_tools), f"{role}: tools registered")
        run = registry.run(role_tools[0], payload={"query": "pre-registered trend-following hypothesis"})
        check(run["ok"], f"{role}: representative tool executes")
        check(run["output"]["artifact"] == agent.required_outputs[0], f"{role}: produces {agent.required_outputs[0]}")

    if FAILS:
        print(f"[OUTPUT] AGENT ARTIFACT SMOKE: FAIL ({len(FAILS)})")
        return 1
    print("[OUTPUT] AGENT ARTIFACT SMOKE: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())

