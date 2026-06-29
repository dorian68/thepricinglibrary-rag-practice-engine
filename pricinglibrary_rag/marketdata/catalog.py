"""Default multi-asset universe to aspirate.

Chosen so the *keyless* providers (yfinance + FRED) already cover the near-total
asset-class span from the data-sourcing brief: equities, ETFs, FX, indices,
commodities, crypto and rates/macro. Each entry maps a canonical symbol to its
provider, asset class and a human label used by the trading-room UI.
"""
from __future__ import annotations

# (symbol, provider, asset_class, label)
DEFAULT_CATALOG: list[tuple[str, str, str, str]] = [
    # --- Equities (yfinance) ----------------------------------------------
    ("AAPL", "yfinance", "equity", "Apple"),
    ("MSFT", "yfinance", "equity", "Microsoft"),
    ("NVDA", "yfinance", "equity", "NVIDIA"),
    ("JPM", "yfinance", "equity", "JPMorgan"),
    # --- Indices (yfinance) -----------------------------------------------
    ("^GSPC", "yfinance", "index", "S&P 500"),
    ("^NDX", "yfinance", "index", "Nasdaq 100"),
    ("^STOXX50E", "yfinance", "index", "Euro Stoxx 50"),
    ("^VIX", "yfinance", "index", "VIX"),
    # --- FX (yfinance) ----------------------------------------------------
    ("EURUSD=X", "yfinance", "fx", "EUR/USD"),
    ("GBPUSD=X", "yfinance", "fx", "GBP/USD"),
    ("USDJPY=X", "yfinance", "fx", "USD/JPY"),
    # --- Commodities (yfinance) -------------------------------------------
    ("CL=F", "yfinance", "commodity", "WTI Crude"),
    ("BZ=F", "yfinance", "commodity", "Brent Crude"),
    ("GC=F", "yfinance", "commodity", "Gold"),
    # --- Crypto spot (yfinance) -------------------------------------------
    ("BTC-USD", "yfinance", "crypto", "Bitcoin"),
    ("ETH-USD", "yfinance", "crypto", "Ethereum"),
    # --- Rates / macro (FRED, keyless) ------------------------------------
    ("DGS10", "fred", "rates", "US 10Y Treasury"),
    ("DGS2", "fred", "rates", "US 2Y Treasury"),
    ("DGS30", "fred", "rates", "US 30Y Treasury"),
    ("DFF", "fred", "rates", "Fed Funds Rate"),
    ("T10Y2Y", "fred", "rates", "10Y-2Y Spread"),
    ("BAMLH0A0HYM2", "fred", "credit", "US HY OAS"),
    ("DEXUSEU", "fred", "fx", "USD/EUR (FRED)"),
    ("DCOILWTICO", "fred", "commodity", "WTI (FRED)"),
    # --- extended universe: everything the desks / strategy lab reference -----
    # FX majors (yfinance)
    ("USDCHF=X", "yfinance", "fx", "USD/CHF"),
    ("AUDUSD=X", "yfinance", "fx", "AUD/USD"),
    ("USDCAD=X", "yfinance", "fx", "USD/CAD"),
    # Commodities (yfinance)
    ("SI=F", "yfinance", "commodity", "Silver"),
    ("NG=F", "yfinance", "commodity", "Natural Gas"),
    ("HG=F", "yfinance", "commodity", "Copper"),
    # Equity indices (yfinance) — deep history
    ("^DJI", "yfinance", "index", "Dow Jones"),
    ("^RUT", "yfinance", "index", "Russell 2000"),
    ("^GDAXI", "yfinance", "index", "DAX"),
    ("^N225", "yfinance", "index", "Nikkei 225"),
    ("^FTSE", "yfinance", "index", "FTSE 100"),
    # US Treasury curve points (FRED) — the rates desk
    ("DGS1MO", "fred", "rates", "US 1M Treasury"),
    ("DGS3MO", "fred", "rates", "US 3M Treasury"),
    ("DGS1", "fred", "rates", "US 1Y Treasury"),
    ("DGS5", "fred", "rates", "US 5Y Treasury"),
    ("DGS7", "fred", "rates", "US 7Y Treasury"),
    ("DGS20", "fred", "rates", "US 20Y Treasury"),
    # EUR / global rates (FRED)
    ("IRLTLT01EZM156N", "fred", "rates", "Euro area 10Y govt yield"),
    ("IRLTLT01GBM156N", "fred", "rates", "UK 10Y govt yield"),
    ("IRLTLT01JPM156N", "fred", "rates", "Japan 10Y govt yield"),
    # Credit (FRED). NB: ICE BofA OAS (BAMLH/BAMLC) are relicensed on FRED and
    # only expose ~2023+ even with a key; Moody's Aaa/Baa go deep and are free.
    ("BAMLC0A0CM", "fred", "credit", "US IG OAS (recent)"),
    ("DAAA", "fred", "credit", "Moody's Aaa yield (daily, 1983+)"),
    ("DBAA", "fred", "credit", "Moody's Baa yield (daily, 1986+)"),
    ("BAA10Y", "fred", "credit", "Baa−10Y credit spread (1986+)"),
    ("AAA", "fred", "credit", "Moody's Aaa yield (monthly, 1919+)"),
    ("BAA", "fred", "credit", "Moody's Baa yield (monthly, 1919+)"),
    # Commodity / FX benchmarks (FRED, very long history)
    ("DCOILBRENTEU", "fred", "commodity", "Brent (FRED)"),
    ("DEXJPUS", "fred", "fx", "JPY/USD (FRED)"),
    ("DEXUSUK", "fred", "fx", "USD/GBP (FRED)"),
]


def by_asset_class() -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {}
    for sym, prov, cls, label in DEFAULT_CATALOG:
        out.setdefault(cls, []).append({"symbol": sym, "provider": prov, "label": label})
    return out
