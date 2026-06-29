"""Curated registry of the DEEPEST financial datasets found across sources —
maximum assets, history ideally since the asset's inception.

Each entry: (source, ref, asset_class, note). Pull single-series ones with
get_kaggle_ohlcv / get_hf_ohlcv; multi-ticker archives are downloaded raw
(kaggle_raw/) for custom slicing.
"""
from __future__ import annotations

# (source, ref, asset_class, note)
DEEP_DATASETS = [
    # --- Kaggle: the big archives -----------------------------------------
    ("kaggle", "jakewright/9000-tickers-of-stock-market-data-full-history", "equity",
     "~9000 US tickers, full history since IPO — the asset-count win"),
    ("kaggle", "mczielinski/bitcoin-historical-data", "crypto",
     "BTC 1-minute since 2012 (the canonical deep BTC minute set)"),
    ("kaggle", "jorijnsmit/binance-full-history", "crypto",
     "All Binance pairs, full minute history (large)"),
    ("kaggle", "dudesurfin/spy-options-eod-volatility-surface-2010-2023", "options",
     "SPY EOD options + implied-vol surface 2010-2023 — for the vol desk"),
    ("kaggle", "kylegraupe/spy-daily-eod-options-quotes-2020-2022", "options",
     "SPY daily EOD option quotes"),
    ("kaggle", "imetomi/eur-usd-forex-pair-historical-data-2002-2019", "fx",
     "EUR/USD minute (bid/ask) 2002-2019"),
    ("kaggle", "amin233/forex-top-currency-pairs-20002020", "fx",
     "Top FX pairs 2000-2020"),
    ("kaggle", "mr1rameez/historical-gold-prices-19952026", "commodity",
     "Gold since 1995"),
    ("kaggle", "macrosynergy/fixed-income-returns-and-macro-trends", "rates",
     "Fixed-income returns + macro trends"),
    # --- HuggingFace -------------------------------------------------------
    ("hf", "zongowo111/v2-crypto-ohlcv-data", "crypto",
     "Binance klines 1m/1h/1d + microstructure (number_of_trades, taker flow)"),
    ("hf", "tradecatlabs/binance-futures-ohlcv-2018-2026", "crypto",
     "Binance futures OHLCV 2018-2026"),
    ("hf", "arthurneuron/cryptocurrency-futures-ohlcv-dataset-1m", "crypto",
     "Crypto futures 1-minute"),
    ("hf", "jwigginton/timeseries-daily-sp500", "equity",
     "S&P 500 daily time series"),
]


def by_source() -> dict:
    out: dict = {}
    for source, ref, cls, note in DEEP_DATASETS:
        out.setdefault(source, []).append({"ref": ref, "asset_class": cls, "note": note})
    return out
