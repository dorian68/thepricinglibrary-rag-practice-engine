"""Kaggle dataset loader — deep history yfinance/HF lack (e.g. FX minute 2000+).

Needs Kaggle creds: ``~/.kaggle/kaggle.json`` ({"username","key"}) or env
``KAGGLE_USERNAME``/``KAGGLE_KEY`` (a new-style ``KGAT_…`` token works as the key).
Downloads a dataset, finds the OHLCV CSV(s) and normalises to the canonical schema.
"""
from __future__ import annotations

import glob
import os

import pandas as pd

from .cache import data_dir

_MAP = {"o": "open", "h": "high", "l": "low", "c": "close", "v": "volume",
        "vol": "volume", "<open>": "open", "<high>": "high", "<low>": "low",
        "<close>": "close", "<vol>": "volume", "adj close": "close",
        # bid OHLC (e.g. HistData FX dumps: bo/bh/bl/bc + ao/ah/al/ac) -> use bid
        "bo": "open", "bh": "high", "bl": "low", "bc": "close", "bidclose": "close"}
_DATE = ("datetime", "date", "timestamp", "time", "<date>", "<dtyyyymmdd>", "gmt time")


def _api():
    os.environ.setdefault("KAGGLE_USERNAME", "tpl")
    from kaggle.api.kaggle_api_extended import KaggleApi
    api = KaggleApi()
    api.authenticate()
    return api


def list_files(dataset: str) -> list[str]:
    return [f.name for f in _api().dataset_list_files(dataset).files]


def download(dataset: str) -> str:
    dest = str(data_dir() / "kaggle_raw" / dataset.replace("/", "__"))
    os.makedirs(dest, exist_ok=True)
    _api().dataset_download_files(dataset, path=dest, unzip=True, quiet=True)
    return dest


def _normalise(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [str(c).strip().lower() for c in df.columns]
    df = df.rename(columns=_MAP)
    if "close" not in df.columns:
        raise RuntimeError(f"no close column in {list(df.columns)[:8]}")
    date_cols = [c for c in df.columns if c in _DATE]

    def _to_dt(col):
        s = df[col]
        if pd.api.types.is_numeric_dtype(s):  # epoch (BTC 'Timestamp' = seconds)
            v = float(s.dropna().iloc[0]) if len(s.dropna()) else 0
            unit = "ms" if v > 1e11 else ("s" if v > 1e8 else "ns")
            return pd.to_datetime(s, unit=unit, errors="coerce")
        return pd.to_datetime(s, errors="coerce")

    if len(date_cols) >= 2:  # separate <date> + <time>
        idx = pd.to_datetime(df[date_cols[0]].astype(str) + " " + df[date_cols[1]].astype(str), errors="coerce")
    elif date_cols:
        idx = _to_dt(date_cols[0])
    else:
        idx = _to_dt(df.columns[0])
    df.index = idx
    keep = [c for c in ("open", "high", "low", "close", "volume") if c in df.columns]
    out = df[keep].apply(pd.to_numeric, errors="coerce")
    out = out[~out.index.isna()].dropna(subset=["close"]).sort_index()
    out.index.name = "date"
    return out


def load_kaggle_ohlcv(dataset: str, *, file: str | None = None, max_rows: int | None = None) -> pd.DataFrame:
    dest = download(dataset)
    csvs = sorted(glob.glob(os.path.join(dest, "**", "*.csv"), recursive=True),
                  key=lambda p: -os.path.getsize(p))
    if not csvs:
        raise RuntimeError(f"no CSV in kaggle dataset '{dataset}'")
    target = next((c for c in csvs if file and file.lower() in c.lower()), csvs[0])
    df = _normalise(pd.read_csv(target))
    return df.tail(max_rows) if max_rows else df
