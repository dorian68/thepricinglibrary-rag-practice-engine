"""Codex/CI-friendly runner for TPL agent-team validation.

This script is intentionally plain subprocess orchestration: Codex can run it
with `codex exec`, CI can run it directly, and the final JSON/Markdown report is
stable enough for a Chief of Staff review turn.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

BACKEND_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[3]

DEFAULT_COMMANDS = [
    ["python", "scripts/smoke_tool_registry.py"],
    ["python", "scripts/smoke_conversation_ledger.py"],
    ["python", "scripts/smoke_agent_mcp_adapter.py"],
    ["python", "scripts/smoke_agent_gateway.py"],
    ["python", "scripts/smoke_agent_interaction_api.py"],
    ["python", "scripts/smoke_agent_runtime_state.py"],
    ["python", "scripts/smoke_agent_runtime_cli.py"],
    ["python", "scripts/smoke_agent_runtime_api.py"],
    ["python", "scripts/smoke_chief_of_staff_validation.py"],
]


def _run(command: list[str]) -> dict[str, Any]:
    started = time.time()
    env = os.environ.copy()
    env.setdefault("GENERATION_MODE", "template")
    env.setdefault("LLM_PROVIDER", "template")
    env.setdefault("TPL_LLM_PROVIDER", "template")
    proc = subprocess.run(
        command,
        cwd=BACKEND_ROOT,
        env=env,
        text=True,
        capture_output=True,
        timeout=300,
        check=False,
    )
    elapsed = round(time.time() - started, 3)
    return {
        "command": command,
        "exit_code": proc.returncode,
        "elapsed_seconds": elapsed,
        "stdout_tail": proc.stdout[-6000:],
        "stderr_tail": proc.stderr[-3000:],
        "ok": proc.returncode == 0,
    }


def _write_report(results: list[dict[str, Any]]) -> Path:
    report_dir = REPO_ROOT / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y-%m-%d_%H%M%S")
    path = report_dir / f"{stamp}_codex-agent-audit.json"
    summary = {
        "kind": "codex_agent_audit",
        "all_ok": all(r["ok"] for r in results),
        "results": results,
    }
    path.write_text(json.dumps(summary, ensure_ascii=True, indent=2), encoding="utf-8")
    md = path.with_suffix(".md")
    lines = [
        "# Codex Agent Audit",
        "",
        f"All OK: `{summary['all_ok']}`",
        "",
        "| Command | Exit | Seconds |",
        "|---|---:|---:|",
    ]
    for result in results:
        cmd = " ".join(result["command"])
        lines.append(f"| `{cmd}` | {result['exit_code']} | {result['elapsed_seconds']} |")
    md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run TPL agent-team smoke audits.")
    parser.add_argument("--json", action="store_true", help="Print full JSON result.")
    args = parser.parse_args(argv)

    results = []
    for command in DEFAULT_COMMANDS:
        print(f"[STEP] run {' '.join(command)}", flush=True)
        result = _run(command)
        print(
            f"[STATUS] {'ok' if result['ok'] else 'fail'} | exit={result['exit_code']} | {result['elapsed_seconds']}s",
            flush=True,
        )
        if not result["ok"] and result["stderr_tail"]:
            print(f"[ERROR] {result['stderr_tail'][-1000:]}", flush=True)
        results.append(result)

    report = _write_report(results)
    payload = {"all_ok": all(r["ok"] for r in results), "report": str(report), "results": results}
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"[OUTPUT] report={report}")
        print(f"[OUTPUT] CODEX AGENT AUDIT: {'PASS' if payload['all_ok'] else 'FAIL'}")
    return 0 if payload["all_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
