"""Chief-of-Staff validation loop for agent teams and tools."""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ["TPL_LLM_PROVIDER"] = "template"

from pricinglibrary_rag.tool_registry import DESK_ROLES, QUANT_RESEARCH_ROLES, get_tool_registry  # noqa: E402

FAILS: list[str] = []


def check(cond: bool, label: str, detail: str = "") -> None:
    print(f"[STATUS] {'ok' if cond else 'fail'} | {label}" + (f" | {detail}" if detail else ""))
    if not cond:
        FAILS.append(label)


def main() -> int:
    registry = get_tool_registry()

    print("[STEP] Chief of Staff scoring")
    coverage = registry.coverage_report()
    criteria: list[tuple[str, bool, float]] = []
    criteria.append(("all 16 agents registered", coverage["agent_count"] == 16, 0.08))
    criteria.append(("registry has broad tool surface", coverage["tool_count"] >= 500, 0.08))
    criteria.append(("all per-agent thresholds pass", coverage["all_ok"], 0.10))
    criteria.append(("two orchestrations separated", _has_two_orchestrations(registry), 0.08))
    criteria.append(("common services cover every agent", _common_services_attached(registry), 0.08))
    criteria.append(("every agent has >=5 job/profile sources", _job_sources(registry), 0.08))
    criteria.append(("every tool has schemas", _tool_schemas(registry), 0.08))
    criteria.append(("permissions valid and sensitive tools guarded", _permissions(registry), 0.08))
    criteria.append(("required artifacts declared", _artifacts(registry), 0.08))
    criteria.append(("audit/replay works", _audit_replay(registry), 0.08))
    criteria.append(("desk tools executable", _executable(registry, DESK_ROLES), 0.09))
    criteria.append(("quant DAG tools executable", _executable(registry, QUANT_RESEARCH_ROLES), 0.09))
    criteria.append(("anti-p-hacking gates present", _anti_p_hacking_gates(registry), 0.10))

    score = 0.0
    max_score = sum(weight for _, _, weight in criteria)
    for label, ok, weight in criteria:
        check(ok, label)
        if ok:
            score += weight
    satisfaction = score / max_score
    print(f"[OUTPUT] Chief of Staff satisfaction: {satisfaction:.4%}")
    check(satisfaction > 0.98, "Chief of Staff satisfaction > 98%", f"{satisfaction:.4%}")

    if FAILS:
        print(f"[OUTPUT] CHIEF OF STAFF VALIDATION: FAIL ({len(FAILS)})")
        return 1
    print("[OUTPUT] CHIEF OF STAFF VALIDATION: PASS")
    return 0


def _has_two_orchestrations(registry) -> bool:
    values = {spec.orchestration for spec in registry.tools.values()}
    return {"agentic_desk", "quant_pipeline", "common"}.issubset(values)


def _common_services_attached(registry) -> bool:
    return all(any(registry.tools[t].owner_agent == "Common" for t in spec.allowed_tools) for spec in registry.agents.values())


def _job_sources(registry) -> bool:
    return all(len(spec.job_profile_sources) >= 5 for spec in registry.agents.values())


def _tool_schemas(registry) -> bool:
    return all(spec.input_schema and spec.output_schema for spec in registry.tools.values())


def _permissions(registry) -> bool:
    guarded = all((not spec.requires_confirmation) or spec.permission in {"book_live", "trade_live"} for spec in registry.tools.values())
    valid = all(spec.permission for spec in registry.tools.values())
    return valid and guarded


def _artifacts(registry) -> bool:
    return all(spec.required_outputs for spec in registry.agents.values()) and all(spec.artifact for spec in registry.tools.values())


def _audit_replay(registry) -> bool:
    tool = next(name for name, spec in registry.tools.items() if spec.owner_agent == "Validator / Skeptic")
    run = registry.run(tool, payload={"query": "validate locked strategy"})
    replay = registry.replay(run["id"])
    return bool(run["ok"] and replay["ok"] and registry.audit(run["id"]))


def _executable(registry, roles) -> bool:
    for role in roles:
        names = [name for name, spec in registry.tools.items() if spec.owner_agent == role and not spec.requires_confirmation]
        if not names:
            return False
        if not registry.run(names[0], payload={"query": "sample"}).get("ok"):
            return False
    return True


def _anti_p_hacking_gates(registry) -> bool:
    names = set(registry.tools)
    required_suffixes = (
        "pre_registration_writer", "n_trials_estimator", "survivorship_audit",
        "lookahead_audit", "purged_kfold", "cpcv_splitter",
        "sample_uniqueness_weights", "deflated_sharpe", "pbo_cscv",
        "lockbox_evaluate_once", "bh_fdr_correction", "capacity_curve",
        "net_edge_after_costs",
    )
    return all(any(name.endswith(f".{suffix}") for name in names) for suffix in required_suffixes)


if __name__ == "__main__":
    sys.exit(main())

