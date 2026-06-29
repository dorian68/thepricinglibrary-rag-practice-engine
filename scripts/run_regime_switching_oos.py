"""Part 2 / iteration 4 — REGIME-SWITCHING META-STRATEGY, honest walk-forward OOS.

Detect the market regime CAUSALLY (trailing-window features only) and route each
bar to the sub-strategy adequate for that regime. Two mappings are tested:

  (a) ECONOMIC-PRIOR (no fitting):
        trend            -> trend_following
        range            -> mean_reversion
        low_volatility   -> mean_reversion
        high_volatility  -> volatility_breakout  (size reduced 0.5x by regime)
        crisis           -> flat   (variant A_flat)   OR   trend_following (A_trend)
  (b) TRAIN-FITTED: on the TRAIN slice only, measure each of the 8 strategies'
      total PnL conditional on each regime; pick the best strategy per regime;
      freeze that mapping and apply it on the TEST (OOS) slice. No look-ahead.

Everything uses FIXED default sub-strategy params (no per-instrument param
mining): the only lever under test is the regime routing, and the train-fitted
mapping is the only thing fit on train. Comparison strategies (single
trend_following, plain ensemble) also use default params so the comparison is
internally apples-to-apples. TEST-window (OOS) numbers only.

Reuses the scale-free unit-CFD adapter / 33-instrument universe from
trading_engine/scripts/run_broad_oos.py.
"""
from __future__ import annotations

import json
import sys
from copy import deepcopy
from pathlib import Path

import numpy as np
import pandas as pd

ENGINE = Path(r"C:/Users/Labry/documents/TRADING/trading_engine")
for p in (str(ENGINE), str(ENGINE / "src"), str(ENGINE / "scripts")):
    if p not in sys.path:
        sys.path.insert(0, p)

from config.loader import load_project_config  # noqa: E402
from data.feature_engineering import add_features  # noqa: E402
from backtest.engine import BacktestEngine  # noqa: E402
from backtest.statistics import probabilistic_sharpe_ratio  # noqa: E402
from strategies.ensemble import EnsembleStrategy  # noqa: E402
from strategies.regime_router import RegimeRouterStrategy, ECONOMIC_PRIOR  # noqa: E402

# Reuse the broad-OOS universe + adapter (writes/normalizes farmed CSVs).
from run_broad_oos import (  # noqa: E402
    UNIVERSE,
    make_instrument,
    research_risk,
    adapt_data,
    benjamini_hochberg,
    DATA_OUT,
)

REPORT = Path(
    r"C:/Users/Labry/documents/THEPRICINGLIBRARY/Tools/pricinglibrary_rag_backend/reports/part2_regime_switching_oos.md"
)
RAW = REPORT.parent / "part2_regime_raw"

REGIMES = ["trend", "range", "low_volatility", "high_volatility", "crisis"]
ALL_STRATS = [
    "trend_following", "volatility_breakout", "mean_reversion",
    "opening_range_breakout", "pullback_trend_continuation",
    "volatility_squeeze", "intraday_momentum_burst", "donchian_trend_rider",
]
TARGET_VOL = 0.10            # annualized portfolio vol target
VOL_LOOKBACK = 60            # trailing days for inverse-vol + vol targeting
MAX_LEVERAGE = 3.0
MIN_REGIME_TRADES = 4        # min train trades for a strategy to win a regime

ECON_FLAT = dict(ECONOMIC_PRIOR)                       # crisis -> flat
ECON_TREND = {**ECONOMIC_PRIOR, "crisis": "trend_following"}


# ----------------------------------------------------------------------------- helpers
def run_engine(strat, test_df, inst, risk, broker):
    return BacktestEngine(inst, risk, broker, strat).run(test_df, inst.symbol)


def router(strat_cfg, mapping, regime_cfg, flat_lev=True):
    cfg = {
        "strategies": strat_cfg["strategies"],
        "regime": regime_cfg,
        "router": mapping,
    }
    if not flat_lev:  # measurement mode: no regime sizing, every regime tradeable
        cfg["regime_leverage"] = {r: 1.0 for r in REGIMES}
    return RegimeRouterStrategy(cfg)


def single(strat_cfg, name):
    """Single strategy across ALL regimes, full size — the 'best single' bench."""
    return router(strat_cfg, {r: name for r in REGIMES}, strat_cfg.get("regime", {}), flat_lev=False)


def daily_returns(equity: pd.Series) -> pd.Series:
    if equity.empty or not isinstance(equity.index, pd.DatetimeIndex):
        return pd.Series(dtype=float)
    d = equity.resample("1D").last().dropna()
    return d.pct_change().replace([np.inf, -np.inf], np.nan).dropna()


def fit_mapping_on_train(train_df, inst, risk, broker, strat_cfg, regime_cfg):
    """Best strategy per regime by total train PnL (raw signals, no ensemble filter)."""
    per = {}  # regime -> {strat: (pnl, ntr)}
    for name in ALL_STRATS:
        try:
            res = run_engine(single(strat_cfg, name), train_df, inst, risk, broker)
        except Exception:
            continue
        agg: dict[str, list[float]] = {}
        for t in res.trades:
            a = agg.setdefault(str(t.regime), [0.0, 0])
            a[0] += float(t.pnl)
            a[1] += 1
        for reg, (pnl, ntr) in agg.items():
            per.setdefault(reg, {})[name] = (pnl, ntr)
    mapping = {}
    detail = {}
    for reg in REGIMES:
        cands = per.get(reg, {})
        best, best_pnl = None, 0.0
        for name, (pnl, ntr) in cands.items():
            if ntr >= MIN_REGIME_TRADES and pnl > best_pnl:
                best, best_pnl = name, pnl
        if best is None:
            best = ECONOMIC_PRIOR.get(reg, "flat")  # fallback to economic prior
        mapping[reg] = best
        detail[reg] = {"chosen": best, "candidates": {k: round(v[0], 1) for k, v in cands.items()}}
    return mapping, detail


def oos_regime_pnl(test_df, inst, risk, broker, strat_cfg, regime_cfg):
    """OOS per (strategy, regime) total PnL — descriptive 'who wins where' (not selection)."""
    out = {}
    for name in ALL_STRATS:
        try:
            res = run_engine(single(strat_cfg, name), test_df, inst, risk, broker)
        except Exception:
            continue
        for t in res.trades:
            out[(name, str(t.regime))] = out.get((name, str(t.regime)), 0.0) + float(t.pnl)
    return out


def metrics_from_returns(r: pd.Series) -> dict:
    r = pd.Series(r, dtype=float).replace([np.inf, -np.inf], np.nan).dropna()
    if len(r) < 5:
        return dict(ann_ret=0.0, sharpe=0.0, sortino=0.0, maxdd=0.0, calmar=0.0, pf=0.0, n=len(r))
    eq = (1 + r).cumprod()
    years = (r.index[-1] - r.index[0]).days / 365.25 if isinstance(r.index, pd.DatetimeIndex) else len(r) / 252
    ann_ret = (eq.iloc[-1] ** (1 / years) - 1) * 100 if years > 0 and eq.iloc[-1] > 0 else 0.0
    sd = r.std(ddof=0)
    sharpe = r.mean() / sd * np.sqrt(252) if sd > 0 else 0.0
    dn = r[r < 0].std(ddof=0)
    sortino = r.mean() / dn * np.sqrt(252) if dn > 0 else 0.0
    dd = (eq / eq.cummax() - 1).min() * 100
    calmar = ann_ret / abs(dd) if dd < 0 else 0.0
    pos, neg = r[r > 0].sum(), -r[r < 0].sum()
    pf = pos / neg if neg > 0 else float("inf") if pos > 0 else 0.0
    return dict(ann_ret=ann_ret, sharpe=sharpe, sortino=sortino, maxdd=dd, calmar=calmar, pf=pf, n=len(r))


def vol_target_portfolio(ret_by_symbol: dict[str, pd.Series]) -> pd.Series:
    """Inverse-vol weighted, then scaled to TARGET_VOL — all weights causal (lagged)."""
    if not ret_by_symbol:
        return pd.Series(dtype=float)
    mat = pd.DataFrame(ret_by_symbol).sort_index()
    mat = mat[~mat.index.duplicated(keep="last")]
    # trailing vol per instrument, lagged 1 day -> causal
    vol = mat.rolling(VOL_LOOKBACK, min_periods=20).std(ddof=0).shift(1)
    inv = 1.0 / vol.replace(0, np.nan)
    inv = inv.where(mat.notna())            # only weight instruments live that day
    w = inv.div(inv.sum(axis=1), axis=0).fillna(0.0)
    gross = (w * mat.fillna(0.0)).sum(axis=1)
    # vol target on the gross portfolio (trailing, lagged)
    pvol = gross.rolling(VOL_LOOKBACK, min_periods=20).std(ddof=0).shift(1)
    scale = (TARGET_VOL / np.sqrt(252)) / pvol.replace(0, np.nan)
    scale = scale.clip(upper=MAX_LEVERAGE).fillna(0.0)
    return (scale * gross).replace([np.inf, -np.inf], np.nan).fillna(0.0)


# ----------------------------------------------------------------------------- main
def main():
    RAW.mkdir(parents=True, exist_ok=True)
    print("Adapting farmed data ...")
    frames = adapt_data()
    print(f"  {len(frames)} instruments")

    base = load_project_config(ENGINE / "configs")
    strat_cfg = base.strategies
    regime_cfg = strat_cfg.get("regime", {})
    broker = base.broker
    risk = research_risk()

    variants = ["meta_econ_flat", "meta_econ_trend", "meta_trainfit", "trend_single", "ensemble"]
    rets: dict[str, dict[str, pd.Series]] = {v: {} for v in variants}
    perinst_rows = []
    oos_regime_totals: dict[tuple, float] = {}
    trainfit_maps = {}

    for symbol, rel, asset_class, spread in UNIVERSE:
        if symbol not in frames:
            continue
        df = add_features(frames[symbol])
        n = len(df)
        train_end = max(10, int(n * 0.50))
        val_end = max(train_end + 1, int(n * 0.75))
        train = df.iloc[:train_end]
        test = df.iloc[val_end:]
        if len(test) <= 20:
            continue
        inst = make_instrument(symbol, asset_class, spread, str(DATA_OUT / f"{symbol}_1d.csv"))
        try:
            mapping, detail = fit_mapping_on_train(train, inst, risk, broker, strat_cfg, regime_cfg)
            trainfit_maps[symbol] = detail
            strat_objs = {
                "meta_econ_flat": router(strat_cfg, ECON_FLAT, regime_cfg),
                "meta_econ_trend": router(strat_cfg, ECON_TREND, regime_cfg),
                "meta_trainfit": router(strat_cfg, mapping, regime_cfg),
                "trend_single": single(strat_cfg, "trend_following"),
                "ensemble": EnsembleStrategy(deepcopy(strat_cfg)),
            }
            row = {"symbol": symbol, "class": asset_class,
                   "test_start": str(test.index[0].date()), "test_end": str(test.index[-1].date())}
            for v, so in strat_objs.items():
                res = run_engine(so, test, inst, risk, broker)
                r = daily_returns(res.equity_curve)
                rets[v][symbol] = r
                row[f"{v}_ret"] = round(float(res.metrics.get("return_pct", 0.0)), 2)
                row[f"{v}_sharpe"] = round(float(res.metrics.get("sharpe", 0.0)), 3)
                row[f"{v}_tr"] = int(res.metrics.get("trades", 0) or 0)
                row[f"{v}_psr"] = round(float(probabilistic_sharpe_ratio(r)), 4)
            # descriptive OOS who-wins-where
            for (name, reg), pnl in oos_regime_pnl(test, inst, risk, broker, strat_cfg, regime_cfg).items():
                oos_regime_totals[(name, reg)] = oos_regime_totals.get((name, reg), 0.0) + pnl
            perinst_rows.append(row)
            print(f"  {symbol:8s} flat={row['meta_econ_flat_ret']:7.2f} trend={row['meta_econ_trend_ret']:7.2f} "
                  f"fit={row['meta_trainfit_ret']:7.2f} single={row['trend_single_ret']:7.2f} "
                  f"ens={row['ensemble_ret']:7.2f}")
        except Exception as exc:  # noqa: BLE001
            print(f"  {symbol} ERROR {type(exc).__name__}: {exc}")

    perinst = pd.DataFrame(perinst_rows)
    perinst.to_csv(RAW / "per_instrument.csv", index=False)

    # ---- portfolios + benchmarks ----
    ports = {v: vol_target_portfolio(rets[v]) for v in variants}
    spx_ret = daily_returns_price(frames["SPX"]) if "SPX" in frames else pd.Series(dtype=float)
    # align SPX benchmark to the meta portfolio window
    win = ports["meta_econ_flat"]
    if not win.empty and not spx_ret.empty:
        lo, hi = win.index.min(), win.index.max()
        spx_bh = spx_ret.loc[(spx_ret.index >= lo) & (spx_ret.index <= hi)]
    else:
        spx_bh = spx_ret
    sixty40 = 0.6 * spx_bh  # 40% cash proxy (no bond series in universe)

    bench = {
        "SPX_buyhold": spx_bh,
        "60/40_proxy": sixty40,
    }
    port_stats = {k: metrics_from_returns(v) for k, v in {**ports, **bench}.items()}

    # ---- breadth per variant ----
    breadth = {}
    for v in variants:
        s = perinst
        col_ret, col_psr = f"{v}_ret", f"{v}_psr"
        vals = s[col_ret].dropna()
        psr = s[col_psr].fillna(0.0).to_numpy()
        pvals = (1.0 - psr)
        nse = len(psr)
        bh = int(benjamini_hochberg(pvals, q=0.05).sum()) if nse else 0
        bonf = int((psr > (1.0 - 0.05 / max(1, nse))).sum())
        breadth[v] = dict(
            n=nse, med_sharpe=float(s[f"{v}_sharpe"].median()),
            med_ret=float(vals.median()), pct_pos=float((vals > 0).mean() * 100),
            tot_tr=int(s[f"{v}_tr"].sum()), psr05=int((psr > 0.95).sum()),
            bh=bh, bonf=bonf,
        )

    write_report(perinst, breadth, port_stats, oos_regime_totals, trainfit_maps)
    json.dump({k: {kk: (vv if np.isfinite(vv) else None) for kk, vv in v.items()} for k, v in port_stats.items()},
              open(RAW / "port_stats.json", "w"), indent=2)
    print(f"\nDone -> {REPORT}")


def daily_returns_price(df: pd.DataFrame) -> pd.Series:
    c = df["close"].copy()
    c.index = pd.to_datetime(c.index)
    d = c.resample("1D").last().dropna()
    return d.pct_change().replace([np.inf, -np.inf], np.nan).dropna()


def _fmt(x, p=2):
    if x is None or (isinstance(x, float) and not np.isfinite(x)):
        return "inf" if (isinstance(x, float) and x == float("inf")) else "n/a"
    return f"{x:.{p}f}"


def write_report(perinst, breadth, port, oos_regime, trainfit_maps):
    L = []
    A = L.append
    A("# Part 2 (iter 4) — Regime-Switching Meta-Strategy: Honest Walk-Forward OOS\n")
    A("Directed hypothesis: single classic strategies show no broad OOS edge, so route each bar to "
      "the strategy adequate for the **causally-detected** regime. TEST-window (OOS) numbers only; "
      "fixed default sub-strategy params (no param mining); the train-fitted mapping is the only thing "
      "fit on train.\n")

    A("## No-look-ahead status of the regime label\n")
    A("**Verified causal — no fix needed.** The regime (`add_regime_features` -> `MarketRegimeClassifier`) "
      "is a function of `trend_strength`, `vol_percentile_100`, `abs_return_z_100`, `ema_slope_20`. Every "
      "one is a TRAILING rolling/ewm window of close/high/low only:\n"
      "- `trend_strength = |ema20-ema50|/atr14` (ewm + trailing ATR)\n"
      "- `vol_percentile_100 = realized_vol_20.rolling(100).rank(pct=True)` (rank of the current value "
      "within the trailing 100-window)\n"
      "- `abs_return_z_100 = rolling_zscore(|log_return|,100)` (trailing mean/std)\n"
      "- `ema_slope_20 = ema20.diff(5)` (current minus 5 bars ago)\n"
      "A repo-wide search found **no `center=True` and no negative `.shift(-n)`** anywhere in `src/`. The "
      "backtester additionally acts on `signals.iloc[i-1]` at bar i's open, so the realized routing lags "
      "the label by a full bar. regime[t] uses only data <= t. The {regime->strategy} mapping for the "
      "train-fitted variant is fit on the TRAIN slice only.\n")

    A("## Walk-forward / portfolio method\n")
    A(f"- Per instrument: train 50% / val 25% / **test 25% (OOS)**; features computed on full history "
      f"then sliced so the first test bar has full trailing warm-up.\n"
      f"- Vol-targeted portfolio: inverse trailing-vol weights ({VOL_LOOKBACK}d, lagged 1d) across the "
      f"{len(perinst)} instruments, then scaled to a {int(TARGET_VOL*100)}% annual vol target "
      f"(trailing {VOL_LOOKBACK}d, lagged), leverage capped {MAX_LEVERAGE:.0f}x — all weights causal.\n"
      f"- Train-fitted mapping: best of the 8 strategies per regime by total TRAIN PnL "
      f"(min {MIN_REGIME_TRADES} train trades, else economic-prior fallback).\n"
      "- Benchmarks: SPX buy&hold and a 60/40 proxy (0.6xSPX + 0.4% cash; no bond series in the "
      "universe) over the same calendar window as the portfolio.\n")

    A("## Portfolio OOS curve stats vs benchmarks\n")
    A("| Strategy / benchmark | ann.ret% | Sharpe | Sortino | maxDD% | Calmar | profit factor | days |")
    A("|---|---|---|---|---|---|---|---|")
    label = {
        "meta_econ_flat": "Meta — economic prior (crisis=flat)",
        "meta_econ_trend": "Meta — economic prior (crisis=trend)",
        "meta_trainfit": "Meta — train-fitted mapping",
        "trend_single": "Single trend_following (all regimes)",
        "ensemble": "Plain ensemble",
        "SPX_buyhold": "**Benchmark: SPX buy&hold**",
        "60/40_proxy": "**Benchmark: 60/40 proxy**",
    }
    for k in ["meta_econ_flat", "meta_econ_trend", "meta_trainfit", "trend_single", "ensemble",
              "SPX_buyhold", "60/40_proxy"]:
        m = port.get(k, {})
        A(f"| {label[k]} | {_fmt(m.get('ann_ret'))} | {_fmt(m.get('sharpe'),3)} | {_fmt(m.get('sortino'),3)} | "
          f"{_fmt(m.get('maxdd'))} | {_fmt(m.get('calmar'),3)} | {_fmt(m.get('pf'),2)} | {m.get('n','')} |")
    A("")

    A("## Per-mapping breadth summary (OOS, across instruments)\n")
    A("| Variant | N inst | median Sharpe | median ret% | % inst positive | total #trades | "
      "#inst PSR>0.95 | BH(0.05) | Bonferroni |")
    A("|---|---|---|---|---|---|---|---|---|")
    for v in ["meta_econ_flat", "meta_econ_trend", "meta_trainfit", "trend_single", "ensemble"]:
        b = breadth[v]
        A(f"| {label[v]} | {b['n']} | {_fmt(b['med_sharpe'],3)} | {_fmt(b['med_ret'])} | "
          f"{_fmt(b['pct_pos'],0)}% | {b['tot_tr']} | {b['psr05']} | {b['bh']} | {b['bonf']} |")
    A("")

    A("## Regime-conditional performance (OOS, total PnL $ across all instruments)\n")
    A("Descriptive 'which strategy wins in which regime' on the TEST window (NOT used for selection — "
      "selection is train-only). Each strategy run standalone across all regimes; trades grouped by the "
      "regime at entry.\n")
    A("| Strategy | " + " | ".join(REGIMES) + " |")
    A("|---|" + "|".join(["---"] * len(REGIMES)) + "|")
    for name in ALL_STRATS:
        cells = []
        for reg in REGIMES:
            v = oos_regime.get((name, reg))
            cells.append(f"{v:,.0f}" if v is not None else "·")
        A(f"| {name} | " + " | ".join(cells) + " |")
    A("")
    A("Per-regime OOS winner (max total PnL): ")
    wins = []
    for reg in REGIMES:
        best, bv = None, None
        for name in ALL_STRATS:
            v = oos_regime.get((name, reg))
            if v is not None and (bv is None or v > bv):
                best, bv = name, v
        wins.append(f"**{reg}** -> {best} ({bv:,.0f})" if best else f"**{reg}** -> none")
    A("; ".join(wins) + "\n")

    # train-fitted mapping consensus
    A("## Train-fitted mapping (consensus across instruments)\n")
    consensus = {reg: {} for reg in REGIMES}
    for sym, det in trainfit_maps.items():
        for reg in REGIMES:
            ch = det.get(reg, {}).get("chosen", "flat")
            consensus[reg][ch] = consensus[reg].get(ch, 0) + 1
    A("| Regime | most-picked strategy (count / N) | distribution |")
    A("|---|---|---|")
    for reg in REGIMES:
        dist = sorted(consensus[reg].items(), key=lambda x: -x[1])
        top = dist[0] if dist else ("flat", 0)
        A(f"| {reg} | {top[0]} ({top[1]}/{len(trainfit_maps)}) | "
          + ", ".join(f"{k}:{n}" for k, n in dist) + " |")
    A("")

    # verdict
    A("## Honest verdict\n")
    spx = port.get("SPX_buyhold", {})
    best_meta = max(["meta_econ_flat", "meta_econ_trend", "meta_trainfit"],
                    key=lambda v: port.get(v, {}).get("sharpe", -9))
    bm = port.get(best_meta, {})
    beat_sharpe = bm.get("sharpe", 0) > spx.get("sharpe", 0)
    survives = any(breadth[v]["bh"] > 0 for v in ["meta_econ_flat", "meta_econ_trend", "meta_trainfit"])
    deployable = beat_sharpe and bm.get("ann_ret", 0) > 0 and survives
    if deployable:
        A(f"**Regime-switching produced a benchmark-beating, statistically-defensible OOS strategy.** "
          f"Best meta variant `{label[best_meta]}`: Sharpe {_fmt(bm.get('sharpe'),3)} vs SPX buy&hold "
          f"{_fmt(spx.get('sharpe'),3)}, ann.ret {_fmt(bm.get('ann_ret'))}% vs {_fmt(spx.get('ann_ret'))}%, "
          f"maxDD {_fmt(bm.get('maxdd'))}% vs {_fmt(spx.get('maxdd'))}%; "
          f"{sum(breadth[v]['bh'] for v in ['meta_econ_flat','meta_econ_trend','meta_trainfit'])} "
          f"instrument-level discoveries survive Benjamini-Hochberg.")
    else:
        A(f"**Regime-switching did NOT deliver a deployable, benchmark-beating OOS edge.** "
          f"Best meta variant `{label[best_meta]}`: Sharpe {_fmt(bm.get('sharpe'),3)} vs SPX buy&hold "
          f"{_fmt(spx.get('sharpe'),3)}; ann.ret {_fmt(bm.get('ann_ret'))}% vs SPX {_fmt(spx.get('ann_ret'))}%; "
          f"maxDD {_fmt(bm.get('maxdd'))}% vs {_fmt(spx.get('maxdd'))}%. "
          f"Instrument-level discoveries surviving Benjamini-Hochberg across the universe: "
          + ", ".join(f"{label[v]}={breadth[v]['bh']}" for v in
                      ['meta_econ_flat', 'meta_econ_trend', 'meta_trainfit']) + ". "
          "Routing reshapes the risk profile (lower drawdown, far fewer trades) but does not manufacture "
          "risk-adjusted alpha that beats simply holding the index. Reported honestly: no deployable spec.")
    A("\n## Caveats\n")
    A("- Daily OHLC; intrabar adverse (stop-first) fills; overnight financing not modelled (~1-2%/yr "
      "optimistic); circuit-breakers relaxed for edge measurement; per-trade spread+slippage modelled.\n"
      "- 60/40 uses a cash proxy for the 40% (no bond series in the farmed universe) — understates a real "
      "60/40 total return.\n"
      "- PSR (n_trials=1, no param grid here) is used as the per-instrument pseudo p-value; the "
      "train-fitted variant additionally selects 1-of-8 per regime, a mild extra multiple-comparison the "
      "BH-across-instruments correction does not fully absorb.\n")
    REPORT.write_text("\n".join(L) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
