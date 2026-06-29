"""Shared, modular market-data layer for ThePricingLibrary.

One foundation used by BOTH the agentic trading room (live market context) and
the algo Strategy Lab (CSV histories for backtests). Multi-provider, cached
locally, degrades gracefully when an API key is missing.

    from pricinglibrary_rag.marketdata import aspirate, get_history
    aspirate()                       # pull the default multi-asset universe
    df = get_history("AAPL")         # normalised OHLCV DataFrame
"""
from __future__ import annotations

import pandas as pd

from . import cache
from .aspirate import aspirate, aspirate_hf, aspirate_intraday, download_one
from .base import OHLCV, Provider, ProviderError
from .catalog import DEFAULT_CATALOG, by_asset_class
from .providers import get_provider, provider_status

__all__ = ["aspirate", "aspirate_intraday", "aspirate_hf", "download_one", "get_history",
           "get_intraday", "get_hf_ohlcv", "get_kaggle_ohlcv", "latest_price", "cache",
           "get_provider", "provider_status", "DEFAULT_CATALOG", "by_asset_class",
           "Provider", "ProviderError", "OHLCV", "csv_path_for", "INTRADAY_INTERVALS"]

INTRADAY_INTERVALS = ["1m", "5m", "15m", "30m", "1h"]

# canonical-symbol -> (provider, symbol) for the default universe, so callers
# can ask for "AAPL" without knowing which source serves it.
_SYMBOL_INDEX = {sym: (prov, sym) for sym, prov, _cls, _label in DEFAULT_CATALOG}


def _resolve(symbol: str, provider: str | None):
    if provider:
        return provider, symbol
    if symbol in _SYMBOL_INDEX:
        return _SYMBOL_INDEX[symbol][0], symbol
    return "yfinance", symbol


def get_history(symbol: str, *, provider: str | None = None,
                use_cache: bool = True, start: str | None = None,
                end: str | None = None) -> pd.DataFrame:
    """Return normalised OHLCV history, from cache when present else live."""
    prov, sym = _resolve(symbol, provider)
    if use_cache:
        df = cache.load(prov, sym)
        if df is not None and len(df):
            return df
    fresh = get_provider(prov).history(sym, start=start, end=end)
    cache.save(prov, sym, fresh)
    return fresh


def get_intraday(symbol: str, *, interval: str = "15m", provider: str = "yfinance",
                 use_cache: bool = True) -> pd.DataFrame:
    """Intraday OHLCV (yfinance, short trailing window per interval). Cached under
    a per-interval namespace so it never collides with the daily history."""
    ns = f"{provider}_{interval}"
    if use_cache:
        df = cache.load(ns, symbol)
        if df is not None and len(df):
            return df
    fresh = get_provider(provider).history(symbol, interval=interval)
    cache.save(ns, symbol, fresh)
    return fresh


def get_hf_ohlcv(dataset: str, *, filename: str | None = None, symbol: str | None = None,
                 max_rows: int | None = None, use_cache: bool = True) -> pd.DataFrame:
    """Enriched OHLCV from a HuggingFace dataset (deep intraday + microstructure
    like number_of_trades / taker buy-sell flow). Cached under 'huggingface/'."""
    from . import hf_provider
    tag = (filename or symbol or dataset).replace("/", "_")
    if use_cache:
        df = cache.load("huggingface", f"{dataset.replace('/', '_')}__{tag}")
        if df is not None and len(df):
            return df
    out = hf_provider.load_hf_ohlcv(dataset, filename=filename, symbol=symbol, max_rows=max_rows)
    cache.save("huggingface", f"{dataset.replace('/', '_')}__{tag}", out)
    return out


def get_kaggle_ohlcv(dataset: str, *, file: str | None = None, max_rows: int | None = None,
                     use_cache: bool = True) -> pd.DataFrame:
    """Enriched/deep OHLCV from a Kaggle dataset (e.g. FX minute since 2000).
    Needs Kaggle creds (~/.kaggle/kaggle.json or KAGGLE_USERNAME/KAGGLE_KEY)."""
    from . import kaggle_provider
    tag = (file or dataset).replace("/", "_")
    if use_cache:
        df = cache.load("kaggle", f"{dataset.replace('/', '_')}__{tag}")
        if df is not None and len(df):
            return df
    out = kaggle_provider.load_kaggle_ohlcv(dataset, file=file, max_rows=max_rows)
    cache.save("kaggle", f"{dataset.replace('/', '_')}__{tag}", out)
    return out


def latest_price(symbol: str, *, provider: str | None = None) -> float | None:
    try:
        df = get_history(symbol, provider=provider)
        return float(df["close"].iloc[-1]) if len(df) else None
    except Exception:  # noqa: BLE001
        return None


def csv_path_for(symbol: str, provider: str | None = None):
    prov, sym = _resolve(symbol, provider)
    return cache.path_for(prov, sym)
