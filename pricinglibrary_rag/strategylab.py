"""Strategy Lab bridge — drives the TRADING engine from the trading room.

Runs the full algo engine (backtest / multi-asset scan / walk-forward) in an
ISOLATED subprocess (``trading_engine/tpl_runner.py``) so the engine's generic
top-level packages and heavy deps (torch/sklearn) never load into the FastAPI
process. The engine stays the source of truth in its own repo; we only invoke it.

Native 15-min datasets shipped with the engine are the default (the strategies
are tuned for them); aspirated daily histories back any instrument without one.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys

from .integrations import trading_root

# lab instrument -> (engine instrument key, native 15min CSV available?, asset class, label)
INSTRUMENTS = [
    {"key": "EURUSD", "native": True, "asset_class": "fx", "label": "EUR/USD", "capital": 5000},
    {"key": "GBPUSD", "native": True, "asset_class": "fx", "label": "GBP/USD", "capital": 5000},
    {"key": "USDJPY", "native": True, "asset_class": "fx", "label": "USD/JPY", "capital": 5000},
    {"key": "XAUUSD", "native": True, "asset_class": "commodity", "label": "Gold", "capital": 5000},
    {"key": "BTCUSD", "native": True, "asset_class": "crypto", "label": "Bitcoin", "capital": 100000},
    {"key": "ETHUSD", "native": True, "asset_class": "crypto", "label": "Ethereum", "capital": 50000},
]
_INSTR_BY_KEY = {i["key"]: i for i in INSTRUMENTS}


def available() -> bool:
    root = trading_root()
    return root is not None and (root / "tpl_runner.py").exists()


def _invoke(payload: dict, timeout: float = 150.0) -> dict:
    root = trading_root()
    if root is None:
        return {"error": "trading engine repo not found"}
    runner = root / "tpl_runner.py"
    if not runner.exists():
        return {"error": f"runner missing at {runner}"}
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join([str(root), str(root / "src"), env.get("PYTHONPATH", "")])
    try:
        proc = subprocess.run([sys.executable, str(runner), json.dumps(payload)],
                              cwd=str(root), env=env, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return {"error": f"engine timed out after {timeout:.0f}s"}
    out = (proc.stdout or "").strip()
    if not out:
        return {"error": f"engine produced no output (stderr: {(proc.stderr or '')[-300:]})"}
    try:
        return json.loads(out.splitlines()[-1])
    except json.JSONDecodeError:
        return {"error": f"unparseable engine output: {out[-300:]}"}


def list_instruments() -> dict:
    return {"instruments": INSTRUMENTS, "available": available()}


def strategies() -> dict:
    return _invoke({"action": "strategies"}, timeout=60)


def backtest(instrument: str, max_bars: int | None = 40000, capital: float | None = None) -> dict:
    info = _INSTR_BY_KEY.get(instrument)
    if info is None:
        return {"error": f"unknown instrument '{instrument}'"}
    return _invoke({"action": "backtest", "instrument": instrument, "source": "native",
                    "max_bars": max_bars, "capital": capital or info["capital"]})


def scan(max_bars: int | None = 30000) -> dict:
    assets = [{"instrument": i["key"], "label": i["label"], "asset_class": i["asset_class"],
               "source": "native", "max_bars": max_bars, "capital": i["capital"]} for i in INSTRUMENTS]
    return _invoke({"action": "scan", "assets": assets}, timeout=300)


def walkforward(instrument: str, strategy_name: str = "trend_following",
                max_bars: int | None = 30000, capital: float | None = None) -> dict:
    info = _INSTR_BY_KEY.get(instrument, {})
    return _invoke({"action": "walkforward", "instrument": instrument, "strategy_name": strategy_name,
                    "source": "native", "max_bars": max_bars, "capital": capital or info.get("capital")},
                   timeout=300)
