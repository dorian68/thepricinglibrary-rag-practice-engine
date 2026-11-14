"""Smoke test for Data Engineer dataset-manifest tools."""
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
    payload = {"query": "point-in-time futures dataset with delisting/corporate-action controls"}
    tools = [
        "quant.data_engineer.provider_status",
        "quant.data_engineer.survivorship_audit",
        "quant.data_engineer.lookahead_audit",
        "quant.data_engineer.asof_snapshot_freeze",
        "quant.data_engineer.dataset_hash",
        "quant.data_engineer.dataset_lineage_report",
    ]
    ok = True
    print("[STEP] dataset manifest contract")
    for tool in tools:
        result = registry.run(tool, payload=payload)
        status = result["ok"] and result["output"]["artifact"] == "DatasetManifest"
        ok = ok and status
        print(f"[STATUS] {'ok' if status else 'fail'} | {tool}")
    print(f"[OUTPUT] DATASET MANIFEST SMOKE: {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

