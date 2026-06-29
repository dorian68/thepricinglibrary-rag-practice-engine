"""Provider contract for the shared market-data layer.

Every provider returns a *normalised* OHLCV pandas DataFrame:

    - index:   tz-naive DatetimeIndex named ``date`` (ascending)
    - columns: ``open, high, low, close, volume`` (lowercase, float)

Single-value macro series (e.g. FRED yields) only populate ``close`` and leave
the OHLC siblings equal to it, so every consumer can treat the frame uniformly.
This is the same CSV schema the TRADING engine's ``CSVMarketDataSource`` expects,
so an aspirated file feeds the trading room AND the algo lab unchanged.
"""
from __future__ import annotations

import os
from abc import ABC, abstractmethod

import pandas as pd

OHLCV = ["open", "high", "low", "close", "volume"]


class ProviderError(RuntimeError):
    """Raised when a provider cannot return data (network, key, empty)."""


class Provider(ABC):
    name: str = "provider"
    requires_key: bool = False
    env_key: str | None = None  # name of the env var holding the API key

    def api_key(self) -> str | None:
        return os.environ.get(self.env_key) if self.env_key else None

    def available(self) -> bool:
        """True when this provider can be used right now (key present if needed)."""
        return (not self.requires_key) or bool(self.api_key())

    @abstractmethod
    def history(self, symbol: str, *, start: str | None = None,
                end: str | None = None, interval: str = "1d") -> pd.DataFrame:
        """Return normalised OHLCV history for ``symbol``."""

    # -- helpers shared by concrete providers --------------------------------
    @staticmethod
    def _normalise(df: pd.DataFrame) -> pd.DataFrame:
        """Coerce an arbitrary OHLCV frame to the canonical schema."""
        if df is None or len(df) == 0:
            raise ProviderError("empty frame")
        df = df.copy()
        df.columns = [str(c).strip().lower() for c in df.columns]
        rename = {"adj close": "close", "adjclose": "close", "value": "close",
                  "price": "close", "vol": "volume", "v": "volume",
                  "o": "open", "h": "high", "l": "low", "c": "close"}
        df = df.rename(columns=rename)
        if "close" not in df.columns:
            raise ProviderError(f"no close column in {list(df.columns)}")
        for col in ("open", "high", "low"):
            if col not in df.columns:
                df[col] = df["close"]
        if "volume" not in df.columns:
            df["volume"] = 0.0
        df = df[OHLCV].apply(pd.to_numeric, errors="coerce")
        df = df.dropna(subset=["close"])
        if not isinstance(df.index, pd.DatetimeIndex):
            df.index = pd.to_datetime(df.index, errors="coerce")
        df = df[~df.index.isna()]
        try:
            df.index = df.index.tz_localize(None)
        except (TypeError, AttributeError):
            pass
        df.index.name = "date"
        return df.sort_index()
