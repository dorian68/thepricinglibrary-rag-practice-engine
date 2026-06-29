"""Split the 3.5GB Kaggle 'all_stock_data.csv' (9000 US tickers, full history
since 1962) into per-ticker cached CSVs under the 'us_stocks' namespace.
Streamed in chunks so it never loads the whole file into memory.
"""
from __future__ import annotations

import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd

from pricinglibrary_rag.marketdata import cache

NS = "us_stocks"
SRC = os.path.join(cache.data_dir(), "kaggle_raw",
                   "jakewright__9000-tickers-of-stock-market-data-full-history",
                   "all_stock_data.csv")


def main():
    if not os.path.exists(SRC):
        print("source CSV not found:", SRC)
        return 1
    t0 = time.time()
    tickers: set[str] = set()
    started: set[str] = set()
    rows = 0
    cols = ["date", "open", "high", "low", "close", "volume"]
    for ci, chunk in enumerate(pd.read_csv(SRC, chunksize=2_000_000)):
        chunk.columns = [str(c).strip().lower() for c in chunk.columns]
        if "ticker" not in chunk.columns:
            print("no ticker column:", list(chunk.columns)); return 1
        chunk = chunk.rename(columns={"date": "date"})
        for tic, g in chunk.groupby("ticker"):
            tic = str(tic).strip()
            if not tic or tic.lower() == "nan":
                continue
            keep = [c for c in cols if c in g.columns]
            sub = g[keep].dropna(subset=["close"])
            if not len(sub):
                continue
            path = cache.path_for(NS, tic)
            header = tic not in started and not path.exists()
            started.add(tic)
            sub.rename(columns={"date": "datetime"}).to_csv(
                path, mode="a", header=header, index=False)
            tickers.add(tic)
            rows += len(sub)
        print(f"  chunk {ci}: tickers so far {len(tickers)}, rows {rows:,}", flush=True)
    print(f"\n=== US STOCKS SLICE DONE === {len(tickers)} tickers, {rows:,} rows, "
          f"{round((time.time()-t0)/60,1)} min")
    return 0


if __name__ == "__main__":
    sys.exit(main())
