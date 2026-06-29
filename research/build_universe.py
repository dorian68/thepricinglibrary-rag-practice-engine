"""Scan the us_stocks cache and build a liquid, long-history universe.

Liquidity = median daily dollar volume over the last LOOKBACK_DAYS.
We require data extending to >= END_MIN and a minimum history length.
Outputs research/artifacts/universe.csv (ranked) and a parquet close panel
for the selected names.
"""
from __future__ import annotations
import sys, os, glob, time
sys.path.insert(0, r'C:\Users\Labry\documents\THEPRICINGLIBRARY\Tools\pricinglibrary_rag_backend')
import numpy as np
import pandas as pd

DATA = r'C:\Users\Labry\documents\THEPRICINGLIBRARY\Tools\pricinglibrary_rag_backend\data\market_history\us_stocks'
OUT = r'C:\Users\Labry\documents\THEPRICINGLIBRARY\Tools\pricinglibrary_rag_backend\research\artifacts'
os.makedirs(OUT, exist_ok=True)

TOP_N = 600
MIN_ROWS = 2500           # ~10y of trading days
END_MIN = pd.Timestamp('2024-06-01')
START_MAX = pd.Timestamp('2012-01-01')  # must have history at least back to here
LOOKBACK = 756            # ~3y for liquidity

files = sorted(glob.glob(os.path.join(DATA, '*.csv')))
print(f'scanning {len(files)} files', flush=True)
rows = []
t0 = time.time()
for i, f in enumerate(files):
    if i % 1000 == 0:
        print(f'  {i}/{len(files)}  {time.time()-t0:.0f}s', flush=True)
    sym = os.path.splitext(os.path.basename(f))[0]
    try:
        df = pd.read_csv(f, usecols=['datetime', 'close', 'volume'])
    except Exception:
        continue
    if len(df) < MIN_ROWS:
        continue
    df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce')
    df = df.dropna(subset=['datetime']).sort_values('datetime')
    if df.empty:
        continue
    last = df['datetime'].iloc[-1]
    first = df['datetime'].iloc[0]
    if last < END_MIN or first > START_MAX:
        continue
    tail = df.tail(LOOKBACK)
    dv = (tail['close'] * tail['volume']).median()
    if not np.isfinite(dv) or dv <= 0:
        continue
    rows.append({'symbol': sym, 'rows': len(df), 'first': first, 'last': last,
                 'med_dollar_vol': float(dv), 'last_close': float(df['close'].iloc[-1])})

uni = pd.DataFrame(rows).sort_values('med_dollar_vol', ascending=False).reset_index(drop=True)
uni.to_csv(os.path.join(OUT, 'universe_full_scan.csv'), index=False)
# Drop obvious non-common-stock tickers (leveraged ETFs etc.) only lightly: keep top by liquidity.
sel = uni.head(TOP_N).copy()
sel.to_csv(os.path.join(OUT, 'universe.csv'), index=False)
print(f'scanned ok rows={len(uni)} selected={len(sel)}', flush=True)
print(sel.head(20).to_string(), flush=True)

# Build aligned close panel for selected names (1995+).
syms = sel['symbol'].tolist()
closes = {}
for sym in syms:
    f = os.path.join(DATA, f'{sym}.csv')
    try:
        df = pd.read_csv(f, usecols=['datetime', 'close'])
    except Exception:
        continue
    df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce')
    df = df.dropna(subset=['datetime']).set_index('datetime')['close'].sort_index()
    df = df[~df.index.duplicated(keep='last')]
    closes[sym] = df
panel = pd.DataFrame(closes)
panel = panel[panel.index >= pd.Timestamp('1998-01-01')]
panel.to_parquet(os.path.join(OUT, 'equity_close_panel.parquet'))
print(f'panel shape {panel.shape} {panel.index.min()}..{panel.index.max()}', flush=True)
print('DONE', flush=True)
