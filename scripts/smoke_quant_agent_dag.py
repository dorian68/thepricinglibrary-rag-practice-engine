"""Smoke test for the quant-research agent DAG and anti-p-hacking gates."""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ["TPL_LLM_PROVIDER"] = "template"

from pricinglibrary_rag.tool_registry import QUANT_RESEARCH_ROLES, get_tool_registry  # noqa: E402

FAILS: list[str] = []


def check(cond: bool, label: str, detail: str = "") -> None:
    print(f"[STATUS] {'ok' if cond else 'fail'} | {label}" + (f" | {detail}" if detail else ""))
    if not cond:
        FAILS.append(label)


def _role_tools(role: str) -> list[str]:
    registry = get_tool_registry()
    return [name for name, spec in registry.tools.items() if spec.owner_agent == role and spec.orchestration == "quant_pipeline"]


def main() -> int:
    registry = get_tool_registry()

    print("[STEP] DAG order and artifacts")
    for idx, role in enumerate(QUANT_RESEARCH_ROLES, start=1):
        spec = registry.agent(role)
        tools = _role_tools(role)
        check(spec["orchestration"] == "quant_pipeline", f"{idx}. {role}: quant orchestration")
        check(len(tools) >= 17, f"{role}: minimum tool depth", str(len(tools)))
        check(bool(spec["required_outputs"]), f"{role}: required output declared")

    print("[STEP] anti-p-hacking controls")
    required = {
        "Quant Researcher": ["pre_registration_writer", "pre_registration_hash", "spec_freeze", "n_trials_estimator"],
        "Data Engineer": ["survivorship_audit", "lookahead_audit", "train_validation_lockbox_split", "dataset_hash"],
        "Feature Engineer": ["leakage_scan_center_true", "negative_shift_scan", "shift_invariance_test", "stationarity_test_adf"],
        "ML / Quant Dev": ["purged_kfold", "cpcv_splitter", "sample_uniqueness_weights", "trial_ledger_record"],
        "Validator / Skeptic": ["deflated_sharpe", "pbo_cscv", "lockbox_evaluate_once", "bh_fdr_correction"],
        "Research Risk Manager": ["kill_switch", "var_cvar", "tail_stress", "paper_risk_policy"],
        "Portfolio Manager": ["edge_correlation_matrix", "max_corr_gate", "crisis_correlation_stress", "allocation_freeze"],
        "Execution / Cost": ["slippage_model", "market_impact_model", "capacity_curve", "net_edge_after_costs"],
    }
    for role, suffixes in required.items():
        names = _role_tools(role)
        for suffix in suffixes:
            check(any(name.endswith(f".{suffix}") for name in names), f"{role}: has {suffix}")

    print("[STEP] execute handoff chain")
    query = "pre-register trend-following signal on liquid futures with CPCV and single-use lockbox"
    for role in QUANT_RESEARCH_ROLES:
        handoffs = [name for name in _role_tools(role) if "handoff" in name]
        run_tool = handoffs[0] if handoffs else _role_tools(role)[0]
        result = registry.run(run_tool, payload={"query": query})
        check(result["ok"], f"{role}: executable handoff/tool", run_tool)
        check(result["output"]["artifact"] == registry.agents[role].required_outputs[0], f"{role}: artifact matches")

    if FAILS:
        print(f"[OUTPUT] QUANT AGENT DAG SMOKE: FAIL ({len(FAILS)})")
        return 1
    print("[OUTPUT] QUANT AGENT DAG SMOKE: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())

