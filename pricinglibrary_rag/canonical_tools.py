"""Bounded adapters to the actual nine product engines, never ToolRegistry stubs."""
from __future__ import annotations

import csv
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
from typing import Any

TOOL_PLANS = {"bs-pricer": "free", "binomial": "student", "payoff": "starter", "mc": "starter",
              "iv-calc": "starter", "bond": "starter", "curve": "starter", "calib": "student", "volsurface": "student"}
TOOL_FORMATS = {"bs-pricer": ("json", "scenario-csv", "sensitivity-csv"), "binomial": ("json", "convergence-csv", "frontier-csv"),
                "payoff": ("json", "curve-csv", "scenario-csv"), "mc": ("json", "terminal-csv", "paths-csv"),
                "iv-calc": ("json", "rolling-csv", "observations-csv"), "bond": ("json", "cashflows-csv", "scenario-csv"),
                "curve": ("json", "curve-csv", "repricing-csv"), "calib": ("json", "points-csv"),
                "volsurface": ("json", "points-csv", "diagnostics-csv")}
ALIASES = {"black-scholes": "bs-pricer", "monte-carlo": "mc", "realized-volatility": "iv-calc", "yield-curve": "curve", "calibration": "calib", "vol-surface": "volsurface"}


class ToolUnavailable(RuntimeError):
    pass


def tool_name(name: str) -> str:
    name = ALIASES.get(name, name)
    if name not in TOOL_PLANS:
        raise ValueError("Unknown canonical tool.")
    return name


def list_canonical_tools() -> list[dict]:
    return [{"id": name, "minimum_plan": plan, "formats": list(TOOL_FORMATS[name]),
             "available": bool(shutil.which("node")) if name == "calib" else True,
             "engine": "canonical-js-node" if name == "calib" else "canonical-python"}
            for name, plan in TOOL_PLANS.items()]


def tool_example(name: str) -> dict:
    name = tool_name(name)
    return json.loads((Path(__file__).parent / "learner_examples.json").read_text(encoding="utf-8"))[name]


def _csv(rows: list[dict]) -> str:
    columns = list(dict.fromkeys(key for row in rows for key in row))
    out = io.StringIO(newline="")
    writer = csv.DictWriter(out, columns, lineterminator="\n")
    writer.writeheader()
    for row in rows:
        safe = {}
        for key, value in row.items():
            if isinstance(value, (dict, list)):
                value = json.dumps(value, sort_keys=True, allow_nan=False)
            if isinstance(value, str) and value.startswith(("=", "+", "-", "@")):
                value = "'" + value
            safe[key] = value
        writer.writerow(safe)
    return out.getvalue()


def _calibrate(payload: dict) -> dict:
    if set(payload) - {"model", "surface", "options"} or not isinstance(payload.get("surface"), list):
        raise ValueError("Calibration requires model, surface and optional options.")
    if not 3 <= len(payload["surface"]) <= 250:
        raise ValueError("Calibration surface must have 3..250 points.")
    options = payload.get("options") or {}
    if not isinstance(options, dict) or set(options) - {"objective", "maxIterations", "integrationUpper", "integrationIntervals", "tolerance"}:
        raise ValueError("Unknown calibration option.")
    for key, minimum, maximum in [("maxIterations", 1, 500), ("integrationIntervals", 16, 256), ("integrationUpper", 10, 150), ("tolerance", 1e-8, .1)]:
        if key in options and (type(options[key]) not in (int, float) or not minimum <= options[key] <= maximum):
            raise ValueError(f"{key} is outside its supported bounds.")
    if any(key in options and type(options[key]) is not int for key in ("maxIterations", "integrationIntervals")):
        raise ValueError("Iteration and integration counts must be integers.")
    node = shutil.which("node")
    if not node:
        raise ToolUnavailable("Calibration requires Node.js; no result was computed.")
    env = {key: value for key, value in os.environ.items() if key.upper() in {"PATH", "SYSTEMROOT", "WINDIR", "TEMP", "TMP"}}
    try:
        process = subprocess.run([node, str(Path(__file__).parent / "js" / "calibrate.mjs")],
                                 input=json.dumps(payload, allow_nan=False), text=True, capture_output=True,
                                 encoding="utf-8", timeout=30, env=env,
                                 creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
    except subprocess.TimeoutExpired as exc:
        raise ToolUnavailable("Calibration exceeded its 30-second budget; no result was returned.") from exc
    if process.returncode:
        raise ValueError("Calibration rejected the inputs: " + process.stderr.strip()[:400])
    return json.loads(process.stdout)


def run_canonical_tool(name: str, payload: dict, format: str = "json") -> dict | str:
    name = tool_name(name)
    if format not in TOOL_FORMATS[name]:
        raise ValueError(f"Unsupported export format for {name}.")
    if not isinstance(payload, dict) or len(json.dumps(payload, allow_nan=False).encode()) > 2_000_000:
        raise ValueError("Tool input must be an object of at most 2 MB.")
    if name == "bs-pricer":
        from .black_scholes import analyze_black_scholes, build_black_scholes_scenario_csv, build_black_scholes_sensitivity_csv
        result = analyze_black_scholes(payload)
        exports = {"scenario-csv": build_black_scholes_scenario_csv, "sensitivity-csv": build_black_scholes_sensitivity_csv}
    elif name == "binomial":
        from .binomial import analyze_binomial, build_binomial_convergence_csv, build_binomial_frontier_csv
        result = analyze_binomial(payload)
        exports = {"convergence-csv": build_binomial_convergence_csv, "frontier-csv": build_binomial_frontier_csv}
    elif name == "bond":
        from .bond import analyze_bond, build_bond_cashflows_csv, build_bond_scenarios_csv
        result = analyze_bond(payload)
        exports = {"cashflows-csv": build_bond_cashflows_csv, "scenario-csv": build_bond_scenarios_csv}
    elif name == "payoff":
        from .payoff_strategy import analyze_payoff_strategy, build_payoff_curve_csv, build_payoff_scenario_csv
        result = analyze_payoff_strategy(payload)
        exports = {"curve-csv": build_payoff_curve_csv, "scenario-csv": build_payoff_scenario_csv}
    elif name == "mc":
        from .monte_carlo import run_monte_carlo, export_terminal_csv, export_paths_csv
        result = run_monte_carlo(payload)
        exports = {"terminal-csv": export_terminal_csv, "paths-csv": export_paths_csv}
    elif name == "iv-calc":
        from .realized_volatility import analyze_realized_volatility, export_rolling_csv, export_observations_csv
        if set(payload) - {"rows", "config"}:
            raise ValueError("Realized volatility accepts rows and config only.")
        result = analyze_realized_volatility(payload.get("rows", []), payload.get("config"))
        exports = {"rolling-csv": export_rolling_csv, "observations-csv": export_observations_csv}
    elif name == "curve":
        from .yield_curve import build_yield_curve
        if set(payload) - {"instruments", "conventions"}:
            raise ValueError("Curve accepts instruments and conventions only.")
        result = build_yield_curve(payload.get("instruments", []), payload.get("conventions"))
        exports = {"curve-csv": lambda value: _csv(value["curve"]), "repricing-csv": lambda value: _csv(value["repricing"])}
    elif name == "volsurface":
        from .vol_surface import analyze_vol_surface, build_vol_surface_points_csv, build_vol_surface_diagnostics_csv
        result = analyze_vol_surface(payload)
        exports = {"points-csv": build_vol_surface_points_csv, "diagnostics-csv": build_vol_surface_diagnostics_csv}
    else:
        result = _calibrate(payload)
        exports = {"points-csv": lambda value: _csv(value["calibratedSurface"])}
    json.dumps(result, allow_nan=False)
    return result if format == "json" else exports[format](result)
