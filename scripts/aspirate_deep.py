"""Aspirate the deepest datasets found (since-inception history, more assets).
Single-series sets are normalised + cached; big multi-ticker archives are
downloaded raw (kaggle_raw/) and their structure reported.
"""
from __future__ import annotations

import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pricinglibrary_rag import marketdata as md
from pricinglibrary_rag.marketdata import kaggle_provider as kg

# normalise + cache (single OHLCV series)
SINGLE = [
    "mczielinski/bitcoin-historical-data",
    "imetomi/eur-usd-forex-pair-historical-data-2002-2019",
    "mr1rameez/historical-gold-prices-19952026",
]
# download raw + report (multi-ticker / options archives)
RAW = [
    "jakewright/9000-tickers-of-stock-market-data-full-history",
    "dudesurfin/spy-options-eod-volatility-surface-2010-2023",
]
HF = ["tradecatlabs/binance-futures-ohlcv-2018-2026"]


def main():
    out = {"single": [], "raw": [], "hf": []}
    for ds in SINGLE:
        try:
            df = kg.load_kaggle_ohlcv(ds)
            md.cache.save("kaggle", ds.replace("/", "__"), df)
            out["single"].append({"ds": ds, "rows": len(df), "from": str(df.index.min()), "to": str(df.index.max())})
            print(f"single {ds}: {len(df):,} rows {df.index.min()}..{df.index.max()}", flush=True)
        except Exception as exc:  # noqa: BLE001
            out["single"].append({"ds": ds, "error": f"{type(exc).__name__}: {exc}"})
            print(f"single {ds}: ERR {exc}", flush=True)
    for ds in RAW:
        try:
            dest = kg.download(ds)
            files = glob.glob(os.path.join(dest, "**", "*.csv"), recursive=True)
            sizes = sorted(((round(os.path.getsize(f) / 1e6, 1), os.path.basename(f)) for f in files), reverse=True)
            out["raw"].append({"ds": ds, "files": len(files), "top": sizes[:4], "dir": dest})
            print(f"raw {ds}: {len(files)} csv files; biggest {sizes[:3]}", flush=True)
        except Exception as exc:  # noqa: BLE001
            out["raw"].append({"ds": ds, "error": f"{type(exc).__name__}: {exc}"})
            print(f"raw {ds}: ERR {exc}", flush=True)
    for ds in HF:
        try:
            rep = md.aspirate_hf(ds, only=())
            out["hf"].append({"ds": ds, "files": rep["ok"], "rows": rep["total_rows"]})
            print(f"hf {ds}: files={rep['ok']} rows={rep['total_rows']:,}", flush=True)
        except Exception as exc:  # noqa: BLE001
            out["hf"].append({"ds": ds, "error": f"{type(exc).__name__}: {exc}"})
            print(f"hf {ds}: ERR {exc}", flush=True)
    inv = md.cache.inventory()
    out["cache_files"] = len(inv)
    out["cache_rows"] = sum(i["rows"] for i in inv)
    print("\n=== DEEP DONE ===")
    print(json.dumps(out, indent=2, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
