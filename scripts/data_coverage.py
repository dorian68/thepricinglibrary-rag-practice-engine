"""Aspirate the full platform asset universe (max history) and report coverage:
per asset — source, first date, last date, rows. Answers "how far back does the
price history of every asset we use go?".

    python scripts/data_coverage.py
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pricinglibrary_rag import marketdata as md
from pricinglibrary_rag.marketdata.catalog import DEFAULT_CATALOG


def main():
    print(f"Aspirating {len(DEFAULT_CATALOG)} assets (max history)…\n")
    rep = md.aspirate(refresh=True)
    rows = []
    for sym, provider, asset_class, label in DEFAULT_CATALOG:
        df = md.cache.load(provider, sym)
        if df is None or not len(df):
            rows.append((asset_class, label, sym, provider, "—", "—", 0))
            continue
        first = str(df.index.min().date())
        last = str(df.index.max().date())
        rows.append((asset_class, label, sym, provider, first, last, len(df)))

    rows.sort(key=lambda r: (r[0], r[4]))
    cur = None
    print(f"{'ASSET':32} {'SYMBOL':18} {'SRC':9} {'FROM':12} {'TO':12} {'BARS':>8}")
    print("-" * 95)
    for asset_class, label, sym, provider, first, last, n in rows:
        if asset_class != cur:
            cur = asset_class
            print(f"\n# {asset_class.upper()}")
        print(f"{label[:32]:32} {sym[:18]:18} {provider[:9]:9} {first:12} {last:12} {n:>8,}")

    ok = sum(1 for r in rows if r[6] > 0)
    total_bars = sum(r[6] for r in rows)
    earliest = min((r[4] for r in rows if r[4] != "—"), default="—")
    print("\n" + "=" * 95)
    print(f"Assets covered: {ok}/{len(rows)} | total bars: {total_bars:,} | "
          f"earliest data point: {earliest} | elapsed {rep['elapsed_s']}s | dir: {rep['data_dir']}")
    fails = [r for r in rows if r[6] == 0]
    if fails:
        print("MISSING:", ", ".join(f"{r[1]} ({r[2]})" for r in fails))
    return 0


if __name__ == "__main__":
    sys.exit(main())
