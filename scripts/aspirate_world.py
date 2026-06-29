"""World constituents — pull index membership lists (FTSE 100, DAX, CAC 40,
Nikkei 225, IBEX, AEX, SMI, FTSE MIB, ASX 200, TSX 60, OMX, Hang Seng) from
Wikipedia and the CoinGecko top-250 crypto list, then batch-aspirate via yfinance.
Resilient: bad tickers just fail and are skipped.
"""
from __future__ import annotations

import importlib.util
import io
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import requests

_spec = importlib.util.spec_from_file_location(
    "ae", os.path.join(os.path.dirname(os.path.abspath(__file__)), "aspirate_everything.py"))
ae = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ae)

UA = {"User-Agent": "Mozilla/5.0 (tpl-data)"}
_TICKER_COLS = ("ticker", "symbol", "code", "epic", "ric", "trading symbol")

# (name, wikipedia url, yfinance suffix, zero_pad_to)
INDEXES = [
    ("FTSE 100", "https://en.wikipedia.org/wiki/FTSE_100_Index", ".L", 0),
    ("DAX", "https://en.wikipedia.org/wiki/DAX", ".DE", 0),
    ("CAC 40", "https://en.wikipedia.org/wiki/CAC_40", ".PA", 0),
    ("Nikkei 225", "https://en.wikipedia.org/wiki/Nikkei_225", ".T", 0),
    ("IBEX 35", "https://en.wikipedia.org/wiki/IBEX_35", ".MC", 0),
    ("AEX", "https://en.wikipedia.org/wiki/AEX_index", ".AS", 0),
    ("SMI", "https://en.wikipedia.org/wiki/Swiss_Market_Index", ".SW", 0),
    ("FTSE MIB", "https://en.wikipedia.org/wiki/FTSE_MIB", ".MI", 0),
    ("ASX 200", "https://en.wikipedia.org/wiki/S%26P/ASX_200", ".AX", 0),
    ("TSX 60", "https://en.wikipedia.org/wiki/S%26P/TSX_60", ".TO", 0),
    ("OMXS30", "https://en.wikipedia.org/wiki/OMX_Stockholm_30", ".ST", 0),
    ("Hang Seng", "https://en.wikipedia.org/wiki/Hang_Seng_Index", ".HK", 4),
    ("STOXX 50", "https://en.wikipedia.org/wiki/EURO_STOXX_50", "", 0),
]


def index_tickers(url, suffix, pad):
    html = requests.get(url, timeout=30, headers=UA).text
    tables = pd.read_html(io.StringIO(html))
    best = None
    for t in tables:
        cols = {str(c).strip().lower(): c for c in t.columns}
        hit = next((cols[c] for c in _TICKER_COLS if c in cols), None)
        if hit is not None and len(t) >= 15:
            best = (t, hit)
            break
    if not best:
        return []
    t, col = best
    out = []
    for v in t[col].tolist():
        s = str(v).strip().upper().split(":")[-1]
        s = re.sub(r"[^A-Z0-9.\-]", "", s)
        if not s or s == "NAN":
            continue
        if pad and s.isdigit():
            s = s.zfill(pad)
        # only append the exchange suffix when the source ticker lacks one
        if suffix and "." not in s:
            s += suffix
        out.append(s)
    return list(dict.fromkeys(out))  # dedup, preserve order


def crypto_top(n=250):
    url = ("https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd"
           f"&order=market_cap_desc&per_page={min(n,250)}&page=1")
    try:
        rows = requests.get(url, timeout=30, headers=UA).json()
        return [f"{r['symbol'].upper()}-USD" for r in rows if r.get("symbol")]
    except Exception:  # noqa: BLE001
        return []


def main():
    report = {}
    for name, url, suffix, pad in INDEXES:
        try:
            tickers = index_tickers(url, suffix, pad)
        except Exception as exc:  # noqa: BLE001
            report[name] = {"error": f"{type(exc).__name__}: {exc}"}
            print(f">> {name}: list ERR {exc}", flush=True)
            continue
        if not tickers:
            report[name] = {"tickers": 0, "note": "no constituent table found"}
            print(f">> {name}: no table", flush=True)
            continue
        print(f">> {name}: {len(tickers)} constituents -> aspirating", flush=True)
        ae.batch_daily(tickers, name.replace(" ", "_").lower(), report)

    crypto = crypto_top(250)
    if crypto:
        print(f">> CoinGecko top crypto: {len(crypto)} -> aspirating", flush=True)
        ae.batch_daily(crypto, "crypto_top250", report)

    inv = ae.md.cache.inventory()
    report["cache_total_files"] = len(inv)
    report["cache_total_rows"] = sum(i["rows"] for i in inv)
    print("\n=== WORLD CONSTITUENTS DONE ===")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
