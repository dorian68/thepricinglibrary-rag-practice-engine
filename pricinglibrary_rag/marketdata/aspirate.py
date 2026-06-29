"""Bulk history aspiration driver.

Downloads every symbol in a catalog through its provider and caches it as CSV.
Resilient: a failing symbol is recorded and skipped, never aborts the run.
Re-runs are cheap — a symbol fresher than ``max_age`` is served from cache.
"""
from __future__ import annotations

import time

from . import cache
from .catalog import DEFAULT_CATALOG
from .providers import get_provider


def download_one(symbol: str, provider: str, *, start: str | None = None,
                 end: str | None = None, interval: str = "1d", refresh: bool = False,
                 max_age: float = 6 * 3600):
    """Return (rows, from_cache, error). Caches on success."""
    if not refresh:
        age = cache.age_seconds(provider, symbol)
        if age is not None and age < max_age:
            df = cache.load(provider, symbol)
            if df is not None and len(df):
                return len(df), True, None
    try:
        prov = get_provider(provider)
        if not prov.available():
            return 0, False, f"{provider} unavailable (missing {prov.env_key})"
        df = prov.history(symbol, start=start, end=end, interval=interval)
        cache.save(provider, symbol, df)
        return len(df), False, None
    except Exception as exc:  # noqa: BLE001 - one symbol must not kill the run
        return 0, False, f"{type(exc).__name__}: {exc}"


def aspirate_intraday(*, intervals=("1h", "15m"), symbols=None, refresh: bool = False) -> dict:
    """Bulk intraday aspiration over the yfinance universe (per-interval cache)."""
    from . import cache, get_intraday
    from .providers import get_provider
    syms = symbols or [s for s, prov, _c, _l in DEFAULT_CATALOG if prov == "yfinance"]
    t0, results, ok, failed, rows = time.time(), [], 0, 0, 0
    for interval in intervals:
        for sym in syms:
            ns = f"yfinance_{interval}"
            try:
                if not refresh:
                    age = cache.age_seconds(ns, sym)
                    if age is not None and age < 12 * 3600:
                        df = cache.load(ns, sym)
                        if df is not None and len(df):
                            ok += 1; rows += len(df)
                            results.append({"symbol": sym, "interval": interval, "rows": len(df), "cached": True})
                            continue
                df = get_provider("yfinance").history(sym, interval=interval)
                cache.save(ns, sym, df)
                ok += 1; rows += len(df)
                results.append({"symbol": sym, "interval": interval, "rows": len(df), "cached": False})
            except Exception as exc:  # noqa: BLE001
                failed += 1
                results.append({"symbol": sym, "interval": interval, "rows": 0, "error": f"{type(exc).__name__}: {exc}"})
    return {"ok": ok, "failed": failed, "total_rows": rows, "elapsed_s": round(time.time() - t0, 1), "results": results}


def aspirate_hf(dataset: str, *, only=("1m", "1h", "1d"), limit=None, refresh: bool = False) -> dict:
    """Bulk-pull every OHLCV file from a HuggingFace dataset into the cache."""
    from . import cache, get_hf_ohlcv
    from .hf_provider import list_files
    files = list_files(dataset)
    if only:
        files = [f for f in files if any(f"_{iv}." in f["name"] or f"-{iv}." in f["name"] for iv in only)]
    if limit:
        files = files[:limit]
    t0, results, ok, failed, rows = time.time(), [], 0, 0, 0
    for f in files:
        name = f["name"]
        try:
            df = get_hf_ohlcv(dataset, filename=name, use_cache=not refresh)
            ok += 1; rows += len(df)
            results.append({"file": name, "rows": len(df), "cols": list(df.columns)})
        except Exception as exc:  # noqa: BLE001
            failed += 1
            results.append({"file": name, "error": f"{type(exc).__name__}: {exc}"})
    return {"dataset": dataset, "ok": ok, "failed": failed, "files": len(files),
            "total_rows": rows, "elapsed_s": round(time.time() - t0, 1), "results": results}


def aspirate(catalog=None, *, start: str | None = None, end: str | None = None,
             interval: str = "1d", refresh: bool = False) -> dict:
    """Aspirate a whole catalog. Returns a structured report."""
    catalog = catalog or DEFAULT_CATALOG
    t0 = time.time()
    results, ok, failed, total_rows = [], 0, 0, 0
    for entry in catalog:
        symbol, provider, asset_class, label = entry[0], entry[1], entry[2], entry[3]
        rows, cached_, err = download_one(symbol, provider, start=start, end=end,
                                          interval=interval, refresh=refresh)
        if err:
            failed += 1
        else:
            ok += 1
            total_rows += rows
        results.append({"symbol": symbol, "provider": provider, "asset_class": asset_class,
                        "label": label, "rows": rows, "cached": cached_, "error": err})
    return {"ok": ok, "failed": failed, "total_rows": total_rows,
            "elapsed_s": round(time.time() - t0, 2),
            "data_dir": str(cache.data_dir()), "results": results}
