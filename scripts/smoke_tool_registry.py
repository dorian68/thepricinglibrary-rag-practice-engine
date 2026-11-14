"""Smoke test for the audited agent tool registry."""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ["TPL_LLM_PROVIDER"] = "template"

from pricinglibrary_rag.tool_registry import (  # noqa: E402
    DESK_ROLES,
    QUANT_RESEARCH_ROLES,
    PERMISSIONS,
    get_tool_registry,
)

FAILS: list[str] = []


def step(label: str) -> None:
    print(f"[STEP] {label}")


def check(cond: bool, label: str, detail: str = "") -> None:
    status = "ok" if cond else "fail"
    print(f"[STATUS] {status} | {label}" + (f" | {detail}" if detail else ""))
    if not cond:
        FAILS.append(label)


def main() -> int:
    registry = get_tool_registry()
    coverage = registry.coverage_report()

    step("registry coverage")
    check(coverage["agent_count"] == 16, "16 agent personas registered", str(coverage["agent_count"]))
    check(coverage["tool_count"] >= 500, "large desk/quant tool surface registered", str(coverage["tool_count"]))
    check(coverage["all_descriptors_valid"], "per-agent descriptor thresholds pass")
    check(not coverage["all_ok"], "unimplemented adapters are not presented as operational coverage")

    step("tool contracts")
    for spec in registry.tools.values():
        check(bool(spec.input_schema), f"{spec.name}: input schema present")
        check(bool(spec.output_schema), f"{spec.name}: output schema present")
        check(spec.permission in PERMISSIONS, f"{spec.name}: valid permission")
        check(spec.audit_level == "full", f"{spec.name}: full audit level")
        check(bool(spec.artifact), f"{spec.name}: artifact declared")

    step("each agent capability reports its real implementation state")
    for role in (*DESK_ROLES, *QUANT_RESEARCH_ROLES):
        role_tools = [
            name for name, spec in registry.tools.items()
            if spec.owner_agent == role and spec.orchestration != "common" and not spec.requires_confirmation
        ]
        check(bool(role_tools), f"{role}: role tools exist")
        if role_tools:
            result = registry.run(role_tools[0], payload={"query": "sample RFQ / strategy hypothesis"})
            if registry.describe(role_tools[0])["executable"]:
                check(result["ok"] or result["output"]["status"]=="failed", f"{role}: implemented adapter validates or executes", result["tool_name"])
            else:
                check(not result["ok"] and result["output"]["status"]=="unavailable",f"{role}: unavailable adapter is explicit")
            check(result["output"]["artifact"] in registry.agents[role].required_outputs, f"{role}: artifact contract")

    step("audit and replay")
    first_tool = next(name for name, spec in registry.tools.items() if spec.owner_agent == "Sales")
    result = registry.run(first_tool, payload={"query": "hedge EURUSD exposure"})
    audit = registry.audit(result["id"])
    replay = registry.replay(result["id"])
    check(audit["tool_name"] == result["tool_name"], "audit record can be loaded")
    check(replay["ok"], "audit replay runs")

    if FAILS:
        print(f"[OUTPUT] TOOL REGISTRY SMOKE: FAIL ({len(FAILS)})")
        for fail in FAILS:
            print(f"[ERROR] {fail}")
        return 1
    print("[OUTPUT] TOOL REGISTRY SMOKE: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())

