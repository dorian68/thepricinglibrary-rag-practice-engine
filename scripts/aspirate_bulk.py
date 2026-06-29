"""Mass aspiration across yfinance (intraday), HuggingFace (enriched crypto) and
Kaggle (deep FX). Run in the background; prints a JSON summary at the end.
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pricinglibrary_rag import marketdata as md
from pricinglibrary_rag.marketdata import kaggle_provider as kg

HF_DATASETS = ["zongowo111/v2-crypto-ohlcv-data"]
KAGGLE_DATASETS = [
    "imetomi/eur-usd-forex-pair-historical-data-2002-2019",
    "amin233/forex-top-currency-pairs-20002020",
    "meehau/EURUSD",
]


def main():
    summary = {}

    print(">> yfinance intraday (1h, 15m) over the universe…", flush=True)
    summary["intraday"] = md.aspirate_intraday(intervals=("1h", "15m"))
    print(f"   intraday: ok={summary['intraday']['ok']} rows={summary['intraday']['total_rows']:,}", flush=True)

    print(">> HuggingFace enriched crypto klines…", flush=True)
    summary["hf"] = []
    for ds in HF_DATASETS:
        try:
            rep = md.aspirate_hf(ds, only=("1m", "1h", "1d"))
            summary["hf"].append({"dataset": ds, "files": rep["ok"], "rows": rep["total_rows"]})
            print(f"   HF {ds}: files={rep['ok']}/{rep['files']} rows={rep['total_rows']:,}", flush=True)
        except Exception as exc:  # noqa: BLE001
            summary["hf"].append({"dataset": ds, "error": f"{type(exc).__name__}: {exc}"})

    print(">> Kaggle deep FX…", flush=True)
    summary["kaggle"] = []
    for ds in KAGGLE_DATASETS:
        try:
            df = kg.load_kaggle_ohlcv(ds)
            md.cache.save("kaggle", ds.replace("/", "__"), df)
            row = {"dataset": ds, "rows": len(df), "from": str(df.index.min()), "to": str(df.index.max())}
            summary["kaggle"].append(row)
            print(f"   Kaggle {ds}: rows={len(df):,} {row['from']}..{row['to']}", flush=True)
        except Exception as exc:  # noqa: BLE001
            summary["kaggle"].append({"dataset": ds, "error": f"{type(exc).__name__}: {exc}"})

    inv = md.cache.inventory()
    summary["cache_total_files"] = len(inv)
    summary["cache_total_rows"] = sum(i["rows"] for i in inv)
    print("\n=== BULK ASPIRATION DONE ===")
    print(json.dumps(summary, indent=2, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
