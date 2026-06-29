"""ASPIRE EVERYTHING — the maximal free universe, deepest history.

yfinance daily (since inception) for: S&P 500 constituents + world indices +
futures + ETFs + FX pairs + top crypto; PLUS a big FRED macro/rates set (CPI
1913, money supply, long Treasury curve, FX, commodity benchmarks); PLUS 1h
intraday (~2y) for the liquid subset. Batched + resilient. Run in background.
"""
from __future__ import annotations

import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd

from pricinglibrary_rag import marketdata as md

# ----------------------------- universe ------------------------------------
INDICES = "^GSPC ^DJI ^IXIC ^NDX ^RUT ^VIX ^GDAXI ^FTSE ^FCHI ^N225 ^STOXX50E ^HSI ^BVSP ^GSPTSE ^AXJO ^KS11 ^TWII ^BSESN ^MXX".split()
FUTURES = "ES=F NQ=F YM=F RTY=F CL=F BZ=F NG=F GC=F SI=F HG=F PL=F PA=F ZC=F ZS=F ZW=F ZB=F ZN=F ZF=F ZT=F 6E=F 6J=F 6B=F 6A=F 6C=F 6S=F DX=F".split()
ETFS = "SPY QQQ DIA IWM EEM EFA VTI VOO XLK XLF XLE XLV XLI XLY XLP XLU XLB XLRE GLD SLV USO UNG TLT IEF SHY HYG LQD AGG VNQ ARKK".split()
FX = "EURUSD=X GBPUSD=X USDJPY=X USDCHF=X AUDUSD=X USDCAD=X NZDUSD=X EURGBP=X EURJPY=X GBPJPY=X EURCHF=X AUDJPY=X USDMXN=X USDSEK=X USDNOK=X USDSGD=X USDZAR=X USDTRY=X USDCNY=X".split()
CRYPTO = "BTC-USD ETH-USD BNB-USD XRP-USD SOL-USD ADA-USD DOGE-USD AVAX-USD DOT-USD LINK-USD LTC-USD BCH-USD XLM-USD ATOM-USD ETC-USD UNI-USD FIL-USD APT-USD ARB-USD OP-USD".split()

FRED = [
    "CPIAUCSL", "CPIAUCNS", "PCEPI", "GDP", "GDPC1", "UNRATE", "PAYEMS", "INDPRO", "HOUST",
    "M1SL", "M2SL", "FEDFUNDS", "DFF", "TB3MS", "GS1", "GS2", "GS5", "GS10", "GS20", "GS30",
    "MORTGAGE30US", "UMCSENT", "VIXCLS", "T10YIE", "T5YIFR", "T10Y2Y", "T10Y3M",
    "AAA", "BAA", "DAAA", "DBAA", "BAA10Y", "DGS1MO", "DGS3MO", "DGS6MO", "DGS1", "DGS2",
    "DGS3", "DGS5", "DGS7", "DGS10", "DGS20", "DGS30",
    "DTWEXBGS", "DEXUSEU", "DEXJPUS", "DEXUSUK", "DEXCAUS", "DEXCHUS", "DEXKOUS", "DEXSZUS",
    "DEXUSAL", "DEXMXUS", "DEXBZUS", "DEXINUS",
    "DCOILWTICO", "DCOILBRENTEU", "DHHNGSP", "GASREGW", "PPIACO", "PPIIDC",
    "NASDAQCOM", "SP500", "WILL5000IND", "DJIA", "WTISPLC",
]


def cache_frame(provider, sym, df):
    if df is None or len(df) == 0:
        return 0
    md.cache.save(provider, sym, df)
    return len(df)


def batch_daily(symbols, label, report):
    import yfinance as yf
    ok = rows = fail = 0
    for i in range(0, len(symbols), 40):
        chunk = symbols[i:i + 40]
        try:
            data = yf.download(chunk, period="max", auto_adjust=True, progress=False,
                               threads=True, group_by="ticker")
        except Exception as exc:  # noqa: BLE001
            fail += len(chunk)
            print(f"  [{label}] batch err: {exc}", flush=True)
            continue
        for sym in chunk:
            try:
                sub = data[sym] if isinstance(data.columns, pd.MultiIndex) else data
                sub = sub.dropna(how="all")
                sub.columns = [str(c).strip().lower() for c in sub.columns]
                keep = [c for c in ("open", "high", "low", "close", "volume") if c in sub.columns]
                if not keep or "close" not in keep:
                    fail += 1
                    continue
                out = sub[keep].copy()
                try:
                    out.index = out.index.tz_localize(None)
                except (TypeError, AttributeError):
                    pass
                out.index.name = "date"
                n = cache_frame("yfinance", sym, out.dropna(subset=["close"]))
                if n:
                    ok += 1; rows += n
                else:
                    fail += 1
            except Exception:  # noqa: BLE001
                fail += 1
        time.sleep(1.0)  # gentle on the API
    report[label] = {"ok": ok, "rows": rows, "fail": fail}
    print(f">> {label}: {ok} assets, {rows:,} rows ({fail} failed)", flush=True)


def sp500_tickers():
    import io

    import requests
    sources = [
        "https://raw.githubusercontent.com/datasets/s-and-p-500-companies/main/data/constituents.csv",
        "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies",
    ]
    for url in sources:
        try:
            r = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0 (tpl-data)"})
            if url.endswith(".csv"):
                df = pd.read_csv(io.StringIO(r.text))
            else:
                df = pd.read_html(io.StringIO(r.text))[0]
            col = "Symbol" if "Symbol" in df.columns else df.columns[0]
            syms = [str(s).strip().replace(".", "-") for s in df[col].tolist() if s]
            print(f">> fetched {len(syms)} S&P 500 tickers from {url.split('/')[2]}", flush=True)
            return syms
        except Exception as exc:  # noqa: BLE001
            print(f">> {url.split('/')[2]} failed ({exc})", flush=True)
    print(">> all S&P 500 sources failed; using core mega-caps", flush=True)
    return "AAPL MSFT NVDA AMZN GOOGL META BRK-B JPM V JNJ WMT PG MA HD CVX KO PEP".split()


def main():
    report = {}
    t0 = time.time()
    sp = sp500_tickers()
    batch_daily(INDICES, "indices", report)
    batch_daily(FUTURES, "futures", report)
    batch_daily(ETFS, "etfs", report)
    batch_daily(FX, "fx", report)
    batch_daily(CRYPTO, "crypto", report)
    batch_daily(sp, "sp500", report)

    # FRED macro (one by one; deep + free)
    ok = rows = fail = 0
    for sid in FRED:
        try:
            df = md.get_history(sid, provider="fred", use_cache=False)
            n = cache_frame("fred", sid, df)
            if n: ok += 1; rows += n
        except Exception:  # noqa: BLE001
            fail += 1
    report["fred"] = {"ok": ok, "rows": rows, "fail": fail}
    print(f">> fred: {ok} series, {rows:,} rows ({fail} failed)", flush=True)

    # 1h intraday (~2y) for liquid subset
    liquid = INDICES[:6] + FUTURES[:12] + ETFS[:12] + FX[:12] + CRYPTO[:12]
    intr = md.aspirate_intraday(intervals=("1h",), symbols=liquid)
    report["intraday_1h"] = {"ok": intr["ok"], "rows": intr["total_rows"]}
    print(f">> intraday 1h: {intr['ok']} assets, {intr['total_rows']:,} rows", flush=True)

    inv = md.cache.inventory()
    report["cache_total_files"] = len(inv)
    report["cache_total_rows"] = sum(i["rows"] for i in inv)
    report["elapsed_min"] = round((time.time() - t0) / 60, 1)
    print("\n=== ASPIRATE EVERYTHING DONE ===")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
