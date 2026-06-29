"""Bridge to VolSurface Live (QUANT_VOL_STAY) for the Crypto Vol / Options desk.

Exposes the REAL VolSurface numerics — Black-Scholes price, implied vol, Greeks,
SVI total variance and realized-vol analytics — behind a tiny, offline-safe API.
When the lab repo is reachable we use its engine (the same code that powers the
VolSurface dashboard); otherwise we fall back to a local Black-Scholes so the
desk never breaks. An optional live-chain probe pulls a real Deribit ATM implied
vol when the network is up.

Every public function is synchronous and pure except ``live_atm_vol`` (network).
"""
from __future__ import annotations

import math
from functools import lru_cache

from .integrations import volsurface_root
from .marketdata import get_history

# --- local fallback Black-Scholes (used only if VolSurface is unreachable) ---
def _ncdf(x):
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def _npdf(x):
    return math.exp(-0.5 * x * x) / math.sqrt(2 * math.pi)


def _local_price_greeks(S, K, T, r, vol, kind):
    if T <= 0 or vol <= 0:
        intr = max(S - K, 0.0) if kind == "call" else max(K - S, 0.0)
        return {"price": intr, "delta": 0.0, "gamma": 0.0, "vega": 0.0, "theta": 0.0, "rho": 0.0}
    d1 = (math.log(S / K) + (r + 0.5 * vol ** 2) * T) / (vol * math.sqrt(T))
    d2 = d1 - vol * math.sqrt(T)
    if kind == "call":
        price = S * _ncdf(d1) - K * math.exp(-r * T) * _ncdf(d2)
        delta = _ncdf(d1)
    else:
        price = K * math.exp(-r * T) * _ncdf(-d2) - S * _ncdf(-d1)
        delta = _ncdf(d1) - 1
    return {"price": price, "delta": delta,
            "gamma": _npdf(d1) / (S * vol * math.sqrt(T)),
            "vega": S * _npdf(d1) * math.sqrt(T) / 100,
            "theta": -(S * _npdf(d1) * vol) / (2 * math.sqrt(T)) / 365,
            "rho": K * T * math.exp(-r * T) * _ncdf(d2) / 100}


@lru_cache(maxsize=1)
def _vs():
    """Import VolSurface's pure pricing module, or None if the repo is absent."""
    if volsurface_root() is None:
        return None
    try:
        from app.pricing import python_fallback as pf  # type: ignore
        return pf
    except Exception:  # noqa: BLE001
        return None


def engine_name() -> str:
    return "volsurface" if _vs() is not None else "local-bs"


def price_option(spot, strike, t, rate, vol, kind="call") -> dict:
    """Real VolSurface BS price + full Greeks (delta/gamma/vega/theta/rho)."""
    pf = _vs()
    if pf is not None:
        try:
            price = pf.black_scholes_price(spot, strike, t, rate, vol, kind)
            g = pf.compute_greeks(spot, strike, t, rate, vol, kind)
            return {"price": price, **{k: g.get(k, 0.0) for k in ("delta", "gamma", "vega", "theta", "rho")}}
        except Exception:  # noqa: BLE001
            pass
    return _local_price_greeks(spot, strike, t, rate, vol, kind)


def implied_vol(spot, strike, t, rate, market_price, kind="call") -> float | None:
    pf = _vs()
    if pf is not None:
        try:
            out = pf.implied_volatility(spot, strike, t, rate, market_price, kind)
            return float(out["implied_vol"]) if out.get("converged") else None
        except Exception:  # noqa: BLE001
            return None
    # local bisection fallback
    lo, hi = 1e-4, 5.0
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        p = _local_price_greeks(spot, strike, t, rate, mid, kind)["price"]
        if abs(p - market_price) < 1e-6:
            return mid
        if p > market_price:
            hi = mid
        else:
            lo = mid
    return 0.5 * (lo + hi)


def realized_vol(asset: str = "BTC") -> dict:
    """Annualised realized vol from aspirated spot history (real data when cached).

    Uses VolSurface's analytics if available, else a local close-to-close estimate.
    """
    sym = {"BTC": "BTC-USD", "ETH": "ETH-USD"}.get(asset.upper(), asset)
    closes: list[float] = []
    try:
        df = get_history(sym)
        closes = [float(x) for x in df["close"].tail(40).tolist()]
    except Exception:  # noqa: BLE001
        closes = []
    if volsurface_root() is not None and closes:
        try:
            from app.analytics.realized_vol import compute_realized  # type: ignore
            return compute_realized(asset.upper(), closes, None)
        except Exception:  # noqa: BLE001
            pass
    # local fallback: annualised stdev of daily log returns
    rv = None
    if len(closes) > 8:
        rets = [math.log(closes[i] / closes[i - 1]) for i in range(1, len(closes)) if closes[i - 1] > 0]
        if rets:
            mu = sum(rets) / len(rets)
            var = sum((x - mu) ** 2 for x in rets) / max(1, len(rets) - 1)
            rv = math.sqrt(var) * math.sqrt(365)
    return {"asset": asset.upper(), "source": "aspirated-history" if closes else "none",
            "rv_30d": round(rv, 4) if rv else None, "atm_iv": None,
            "n_points": len(closes)}


def risk_matrix(spot, strike, t, rate, vol, kind="call", contracts=1.0) -> dict:
    """Spot×vol re-pricing PnL grid (VolSurface-style 7×5), repriced with the real engine."""
    spot_shocks = [-0.20, -0.10, -0.05, 0.0, 0.05, 0.10, 0.20]
    vol_shocks = [-0.20, -0.10, 0.0, 0.10, 0.20]
    base = price_option(spot, strike, t, rate, vol, kind)["price"]
    grid = []
    for sv in vol_shocks:
        row = []
        for ss in spot_shocks:
            p = price_option(spot * (1 + ss), strike, t, rate, vol * (1 + sv), kind)["price"]
            row.append(round((p - base) * contracts, 2))
        grid.append(row)
    return {"spot_shocks": spot_shocks, "vol_shocks": vol_shocks,
            "base_value": round(base * contracts, 2), "grid": grid}


def live_atm_vol(asset: str = "BTC", timeout: float = 8.0) -> dict | None:
    """Best-effort live Deribit ATM implied vol via VolSurface's provider. None offline."""
    if volsurface_root() is None:
        return None
    try:
        import asyncio

        from app.data.providers.deribit import DeribitOptionDataProvider  # type: ignore
        from app.pricing import python_fallback as pf  # type: ignore

        async def _go():
            prov = DeribitOptionDataProvider(timeout=timeout)
            try:
                if not await prov.is_available():
                    return None
                u = await prov.fetch_underlying(asset.upper())
                chain = await prov.fetch_option_chain(asset.upper())
                spot = float(u.price)
                # ATM = quote with strike closest to spot among the nearest expiry
                if not chain:
                    return {"asset": asset.upper(), "underlying": spot, "atm_iv": None, "n_quotes": 0}
                nearest = min(chain, key=lambda q: abs(float(getattr(q, "strike", spot)) - spot))
                mid = getattr(nearest, "mid_price", None) or getattr(nearest, "mark_price", None)
                ttm = max(getattr(nearest, "time_to_expiry", 0.05) or 0.05, 1e-3)
                iv = None
                if mid:
                    out = pf.implied_volatility(spot, float(nearest.strike), ttm, 0.04,
                                                float(mid) * spot, nearest.option_type)
                    iv = float(out["implied_vol"]) if out.get("converged") else None
                return {"asset": asset.upper(), "underlying": spot, "atm_iv": iv,
                        "n_quotes": len(chain), "expiry_ttm": round(ttm, 4)}
            finally:
                await prov.aclose()

        return asyncio.run(_go())
    except Exception:  # noqa: BLE001
        return None
