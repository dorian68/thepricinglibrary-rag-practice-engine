"""Concrete data providers, one class per source from the data-sourcing brief.

Keyless (work out of the box):
    * ``yfinance``  — equities, ETFs, FX, indices, commodities, crypto spot
    * ``fred``      — macro / rates / commodity benchmarks (keyless CSV endpoint)

Freemium (activate when the matching env key is set):
    * ``alphavantage`` (ALPHAVANTAGE_API_KEY)
    * ``finnhub``      (FINNHUB_API_KEY)
    * ``tiingo``       (TIINGO_API_KEY)

Every ``history()`` returns the canonical OHLCV frame defined in ``base``.
"""
from __future__ import annotations

import datetime as dt

import pandas as pd
import requests

from .base import Provider, ProviderError

_TIMEOUT = 30


# yfinance only serves intraday bars over a short trailing window per interval.
_INTRADAY_PERIOD = {"1m": "7d", "2m": "60d", "5m": "60d", "15m": "60d",
                    "30m": "60d", "60m": "730d", "90m": "60d", "1h": "730d"}


class YFinanceProvider(Provider):
    name = "yfinance"

    def history(self, symbol, *, start=None, end=None, interval="1d"):
        import yfinance as yf
        kw = {"interval": interval, "auto_adjust": True, "progress": False, "threads": False}
        if start:
            kw["start"] = start
            if end:
                kw["end"] = end
        elif interval in _INTRADAY_PERIOD:
            kw["period"] = _INTRADAY_PERIOD[interval]  # 'max' is rejected for intraday
        else:
            kw["period"] = "max"
        df = yf.download(symbol, **kw)
        if df is None or len(df) == 0:
            raise ProviderError(f"yfinance returned no data for {symbol}")
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return self._normalise(df)


class FredProvider(Provider):
    """St. Louis Fed — keyless CSV download endpoint (one series = one column)."""
    name = "fred"

    def history(self, symbol, *, start=None, end=None, interval="1d"):
        import os
        # Full history for licensed series (e.g. ICE BofA OAS, which the keyless
        # graph CSV caps at ~recent years) needs a FRED API key. Use it when set.
        key = os.environ.get("FRED_API_KEY")
        if key:
            url = (f"https://api.stlouisfed.org/fred/series/observations?series_id={symbol}"
                   f"&api_key={key}&file_type=json&observation_start={start or '1776-07-04'}")
            if end:
                url += f"&observation_end={end}"
            d = requests.get(url, timeout=_TIMEOUT, headers={"User-Agent": "tpl-marketdata/1.0"}).json()
            obs = d.get("observations", [])
            df = pd.DataFrame([(o["date"], o["value"]) for o in obs], columns=["date", "close"])
            df["close"] = pd.to_numeric(df["close"], errors="coerce")
            df = df.dropna(subset=["close"])
            df["date"] = pd.to_datetime(df["date"], errors="coerce")
            return self._normalise(df.set_index("date")[["close"]])
        # Keyless graph CSV. Force the series start ("depuis qu'ils existent"):
        # without cosd, some series return only a recent default window.
        url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={symbol}&cosd={start or '1776-07-04'}"
        if end:
            url += f"&coed={end}"
        r = requests.get(url, timeout=_TIMEOUT, headers={"User-Agent": "tpl-marketdata/1.0"})
        if r.status_code != 200 or not r.text.strip():
            raise ProviderError(f"FRED {symbol}: HTTP {r.status_code}")
        from io import StringIO
        df = pd.read_csv(StringIO(r.text))
        date_col = df.columns[0]
        val_col = df.columns[1]
        df[val_col] = pd.to_numeric(df[val_col], errors="coerce")  # '.' -> NaN
        df = df.dropna(subset=[val_col]).rename(columns={val_col: "close"})
        df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
        return self._normalise(df.set_index(date_col)[["close"]])


class AlphaVantageProvider(Provider):
    name = "alphavantage"
    requires_key = True
    env_key = "ALPHAVANTAGE_API_KEY"

    def history(self, symbol, *, start=None, end=None, interval="1d"):
        key = self.api_key()
        if not key:
            raise ProviderError("ALPHAVANTAGE_API_KEY not set")
        url = ("https://www.alphavantage.co/query?function=TIME_SERIES_DAILY"
               f"&symbol={symbol}&outputsize=full&apikey={key}")
        r = requests.get(url, timeout=_TIMEOUT)
        data = r.json()
        ts = data.get("Time Series (Daily)")
        if not ts:
            raise ProviderError(f"AlphaVantage {symbol}: {data.get('Note') or data.get('Information') or 'no series'}")
        df = pd.DataFrame(ts).T
        df.columns = [c.split(". ", 1)[-1] for c in df.columns]  # '1. open' -> 'open'
        df.index = pd.to_datetime(df.index, errors="coerce")
        return self._normalise(df)


class FinnhubProvider(Provider):
    name = "finnhub"
    requires_key = True
    env_key = "FINNHUB_API_KEY"

    def history(self, symbol, *, start=None, end=None, interval="1d"):
        key = self.api_key()
        if not key:
            raise ProviderError("FINNHUB_API_KEY not set")
        to_ts = int(dt.datetime.now().timestamp()) if not end else int(pd.Timestamp(end).timestamp())
        frm = int(pd.Timestamp(start).timestamp()) if start else to_ts - 30 * 365 * 86400
        url = (f"https://finnhub.io/api/v1/stock/candle?symbol={symbol}"
               f"&resolution=D&from={frm}&to={to_ts}&token={key}")
        r = requests.get(url, timeout=_TIMEOUT)
        d = r.json()
        if d.get("s") != "ok":
            raise ProviderError(f"Finnhub {symbol}: status {d.get('s')}")
        df = pd.DataFrame({"open": d["o"], "high": d["h"], "low": d["l"],
                           "close": d["c"], "volume": d["v"]},
                          index=pd.to_datetime(d["t"], unit="s"))
        return self._normalise(df)


class TiingoProvider(Provider):
    name = "tiingo"
    requires_key = True
    env_key = "TIINGO_API_KEY"

    def history(self, symbol, *, start=None, end=None, interval="1d"):
        key = self.api_key()
        if not key:
            raise ProviderError("TIINGO_API_KEY not set")
        start = start or "1990-01-01"
        url = (f"https://api.tiingo.com/tiingo/daily/{symbol}/prices"
               f"?startDate={start}&token={key}")
        if end:
            url += f"&endDate={end}"
        r = requests.get(url, timeout=_TIMEOUT, headers={"Content-Type": "application/json"})
        rows = r.json()
        if not isinstance(rows, list) or not rows:
            raise ProviderError(f"Tiingo {symbol}: no rows")
        df = pd.DataFrame(rows)
        df = df.rename(columns={"adjOpen": "open", "adjHigh": "high", "adjLow": "low",
                                "adjClose": "close", "adjVolume": "volume"})
        df.index = pd.to_datetime(df["date"], errors="coerce")
        return self._normalise(df[["open", "high", "low", "close", "volume"]])


_REGISTRY: dict[str, Provider] = {
    p.name: p for p in (
        YFinanceProvider(), FredProvider(), AlphaVantageProvider(),
        FinnhubProvider(), TiingoProvider(),
    )
}


def get_provider(name: str) -> Provider:
    if name not in _REGISTRY:
        raise KeyError(f"unknown provider '{name}' (have {sorted(_REGISTRY)})")
    return _REGISTRY[name]


def provider_status() -> list[dict]:
    return [{"name": p.name, "requires_key": p.requires_key,
             "available": p.available(), "env_key": p.env_key}
            for p in _REGISTRY.values()]
