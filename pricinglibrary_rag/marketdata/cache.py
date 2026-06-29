"""Local CSV cache for aspirated histories.

Layout (one file per symbol, CSV so the TRADING engine reads it directly):

    <data_dir>/<provider>/<SAFE_SYMBOL>.csv     # datetime,open,high,low,close,volume

``<data_dir>`` defaults to ``<backend>/data/market_history`` and is overridable
with the ``TPL_MARKET_DATA_DIR`` env var so the same store can back the live
trading room and the algo lab.
"""
from __future__ import annotations

import os
import re
import time
from pathlib import Path

import pandas as pd

_DEFAULT = Path(__file__).resolve().parents[2] / "data" / "market_history"


def data_dir() -> Path:
    d = Path(os.environ.get("TPL_MARKET_DATA_DIR", _DEFAULT))
    d.mkdir(parents=True, exist_ok=True)
    return d


def _safe(symbol: str) -> str:
    return re.sub(r"[^A-Za-z0-9._=-]", "_", symbol)


def path_for(provider: str, symbol: str) -> Path:
    sub = data_dir() / provider
    sub.mkdir(parents=True, exist_ok=True)
    return sub / f"{_safe(symbol)}.csv"


def save(provider: str, symbol: str, df: pd.DataFrame) -> Path:
    p = path_for(provider, symbol)
    out = df.copy()
    out.index.name = "datetime"
    out.to_csv(p, index=True)
    return p


def load(provider: str, symbol: str) -> pd.DataFrame | None:
    p = path_for(provider, symbol)
    if not p.exists():
        return None
    df = pd.read_csv(p)
    col = "datetime" if "datetime" in df.columns else df.columns[0]
    df[col] = pd.to_datetime(df[col], errors="coerce")
    return df.dropna(subset=[col]).set_index(col).sort_index()


def exists(provider: str, symbol: str) -> bool:
    return path_for(provider, symbol).exists()


def age_seconds(provider: str, symbol: str) -> float | None:
    p = path_for(provider, symbol)
    if not p.exists():
        return None
    return time.time() - p.stat().st_mtime


def inventory() -> list[dict]:
    """List every cached series with row count + freshness, for a UI."""
    out: list[dict] = []
    root = data_dir()
    for prov_dir in sorted(p for p in root.iterdir() if p.is_dir()):
        for f in sorted(prov_dir.glob("*.csv")):
            try:
                rows = sum(1 for _ in f.open("r", encoding="utf-8")) - 1
            except OSError:
                rows = 0
            out.append({"provider": prov_dir.name, "symbol": f.stem, "rows": max(rows, 0),
                        "bytes": f.stat().st_size, "age_seconds": round(time.time() - f.stat().st_mtime)})
    return out
