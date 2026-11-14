"""Smoke test for Quant Researcher preregistration tools."""
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
    payload = {"query": "economic prior: time-series momentum after crisis de-risking"}
    tools = [
        "quant.quant_researcher.economic_prior_builder",
        "quant.quant_researcher.n_trials_estimator",
        "quant.quant_researcher.pre_registration_writer",
        "quant.quant_researcher.pre_registration_hash",
        "quant.quant_researcher.spec_freeze",
    ]
    ok = True
    print("[STEP] preregistration contract")
    for tool in tools:
        result = registry.run(tool, payload=payload)
        status = result["ok"] and result["output"]["artifact"] == "PreRegistration"
        ok = ok and status
        print(f"[STATUS] {'ok' if status else 'fail'} | {tool}")
    print(f"[OUTPUT] PREREGISTRATION SMOKE: {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
