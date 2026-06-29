"""HuggingFace dataset loader for enriched OHLCV (deep intraday + microstructure).

yfinance caps intraday history (1m → 7 days). HuggingFace hosts community crypto
datasets with YEARS of minute bars AND microstructure columns yfinance never
exposes (number_of_trades, taker buy/sell flow). This loader downloads a dataset
file via huggingface_hub and normalises it to the canonical OHLCV schema, keeping
the enriched columns when present. Public datasets need no token; gated ones use
``HF_TOKEN``.
"""
from __future__ import annotations

import os

import pandas as pd

_MAP = {"o": "open", "h": "high", "l": "low", "c": "close", "v": "volume",
        "vol": "volume", "t": "open_time"}
_DATE_COLS = ("open_time", "timestamp", "datetime", "date", "time", "d", "t")
_ENRICHED = ("number_of_trades", "quote_asset_volume", "taker_buy_base_asset_volume",
             "taker_buy_quote_asset_volume")


def list_files(dataset: str) -> list[dict]:
    from huggingface_hub import HfApi
    api = HfApi(token=os.environ.get("HF_TOKEN"))
    info = api.dataset_info(dataset, files_metadata=True)
    return sorted(({"name": s.rfilename, "size": getattr(s, "size", None)}
                   for s in info.siblings if s.rfilename.endswith((".parquet", ".csv"))),
                  key=lambda x: (x["size"] or 1e18))


def load_hf_ohlcv(dataset: str, *, filename: str | None = None, symbol: str | None = None,
                  max_rows: int | None = None) -> pd.DataFrame:
    """Download + normalise one OHLCV file from a HuggingFace dataset."""
    from huggingface_hub import hf_hub_download
    files = list_files(dataset)
    if not files:
        raise RuntimeError(f"no .parquet/.csv files in dataset '{dataset}'")
    target = filename or next((f["name"] for f in files
                               if symbol and symbol.lower() in f["name"].lower()), files[0]["name"])
    path = hf_hub_download(dataset, target, repo_type="dataset", token=os.environ.get("HF_TOKEN"))
    df = pd.read_parquet(path) if path.endswith(".parquet") else pd.read_csv(path)
    df.columns = [str(c).strip().lower() for c in df.columns]
    df = df.rename(columns=_MAP)
    date_col = next((c for c in _DATE_COLS if c in df.columns), df.columns[0])
    s = df[date_col]
    if pd.api.types.is_numeric_dtype(s):
        unit = "ms" if float(s.iloc[0]) > 1e11 else "s"
        idx = pd.to_datetime(s, unit=unit, errors="coerce")
    else:
        idx = pd.to_datetime(s, errors="coerce")
    df.index = idx
    keep = [c for c in ("open", "high", "low", "close", "volume", *_ENRICHED) if c in df.columns]
    out = df[keep].apply(pd.to_numeric, errors="coerce").dropna(subset=["close"])
    out = out[~out.index.isna()].sort_index()
    out.index.name = "date"
    return out.tail(max_rows) if max_rows else out
