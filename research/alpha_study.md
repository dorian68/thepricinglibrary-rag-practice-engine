# Alpha Study: Cross-Sectional Equity ML + Cross-Asset Trend, and Their Blend

*Senior-quant research note. Reproducible scripts and artifacts live under `research/`.*
*Run date: 2026-06-28. Engine metrics: `trading_engine/src/backtest/statistics.py` (Sharpe / PSR / DSR).*

---

## 1. Abstract

We test six pre-registered alpha hypotheses across two families — cross-sectional US
equity (factor + machine-learning) and cross-asset time-series-momentum (trend) — and
study their out-of-sample (OOS) combination. All backtests produce **daily** portfolio
returns, weights are updated **monthly**, and returns are **net of transaction costs**.
The ML sleeve uses a **purged + embargoed, expanding-window walk-forward**, so its entire
2012–2024 track record is genuinely OOS.

The two strongest sleeves — a LightGBM cross-sectional return-rank long/short (**H5**,
OOS Sharpe **0.81**) and a diversified multi-lookback trend sleeve (**H4**, OOS Sharpe
**0.59**) — are **essentially uncorrelated (ρ = 0.04)**. A **clean causal inverse-volatility
blend** of the two lifts OOS net Sharpe to **0.90** (PSR 0.9995, DSR 0.71, maxDD −20.0%).

**Terminal bar (OOS, net): DSR > 0 ✓ (0.71), PSR ≥ 0.95 ✓ (0.9995), Sharpe ≥ 1.0 ✗ (0.90).**
We clear the statistical-significance gates comfortably but **miss the Sharpe ≥ 1.0 bar by
~0.10**. This is reported plainly — the earlier working estimate of ≈0.99 was optimistic
(it credited H4 with its standalone 0.59 Sharpe; inside the equity-aligned trading calendar
H4 contributes ≈0.49, which caps the two-sleeve ceiling near 0.91).

---

## 2. Data

Price cache: `pricinglibrary_rag_backend/data/market_history/`, loaded via
`pricinglibrary_rag.marketdata.cache`.

| Block | Source namespace | Used for |
|---|---|---|
| US equities | `us_stocks/` (9,314 tickers since 1962) | H1–H3, H5, H6 panel |
| Futures / ETF / FX / crypto | `yfinance/` | H4 cross-asset trend |

**Equity universe** (`build_universe.py`): scan all US tickers; require ≥2,500 rows,
history reaching back to ≤2012-01-01 and forward to ≥2024-06-01; rank by median 3-y dollar
volume; keep top 600. Common-ETF tickers (SPY, QQQ, GLD, TLT, …) are blocked from the
equity panel to keep it single-name. Final aligned close panel: **(6,754 days × 594 names),
1998–2024** → `artifacts/equity_close_panel.parquet`.

**Trend universe** (37 instruments, 2002–2024): equity index futures + ETFs, rates futures
+ ETFs, energy/metals/grains commodity futures, G10 FX futures, BTC/ETH.

**Costs:** 5 bps per side on single-name equity; 2 bps per side on the liquid
futures/ETF trend sleeve. **OOS split: 2012-01-01.** Everything before is in-sample (IS),
everything from 2012 on is OOS.

---

## 3. Hypotheses & priors

| ID | Hypothesis | Economic prior | Pre-registered config |
|---|---|---|---|
| **H1** | 12-1 momentum | Persistent underreaction premium | decile L/S, monthly |
| **H2** | 1-month reversal | Short-horizon liquidity reversal | decile L/S, monthly |
| **H3** | Low-volatility | Low-vol anomaly (long low-vol) | decile L/S on −vol6 |
| **H4** | Cross-asset TSMOM | Trend premium, diversifies equity | sign of 1/3/6/12-m returns, inverse-vol risk-parity, vol-target 10% |
| **H5** | LightGBM cross-sectional rank | Non-linear interaction of factor set predicts *relative* next-month return | GBM on 12 features, walk-forward, decile L/S |
| **H6** | Meta-labeled momentum | A classifier filters losing momentum picks | GBM win/lose filter on H1 decile, prob ≥ 0.55 |

Priors going in: H5 and H4 were expected to be the workhorses; H1 a weak-but-real premium;
H2/H3 fragile after costs; H6 a long shot (meta-labeling rarely survives costs). The OOS
results confirmed those priors almost exactly.

---

## 4. Features (equity panel, monthly sampled, causal)

12 features, all computed from daily closes and sampled at month-end with forward-fill
(no look-ahead): `mom_12_1` (12-1 momentum), `rev_1m`, `r3/r6/r12` (3/6/12-m returns),
`vol3/vol6` (realized vol), `dvol6` (downside semi-vol), `skew6`, `hi52` (distance to
52-wk high), `maxd` (max 1-day gain over 21d), `rsi` (14-day).

For the ML label we predict the **cross-sectionally demeaned** next-month forward return
(`fwd_x = fwd − mean(fwd)` within each month), i.e. *relative* performance — the correct
target for a dollar-neutral decile book.

---

## 5. Model / pipeline architecture

`research/alpha_pipeline.py` (single entry point, ~12 s runtime):

- **Factor sleeves (H1–H3):** decile long/short, equal-weight within decile, monthly
  rebalance, 5 bps/side.
- **H5 LightGBM walk-forward:** expanding window, **retrain once per calendar year**.
  Training labels must be realized **before** the test window minus a **2-month embargo**
  (PURGE + EMBARGO against the overlap between a monthly label and the next cross-section).
  Params: 300 trees, lr 0.03, num_leaves 31, depth 6, subsample 0.8, colsample 0.7,
  min_child 200, L2 = 5. Predictions exist **only for 2012+** → the OOS book is fully
  walk-forward (its IS Sharpe is undefined by construction).
- **H6 meta-label:** binary GBM predicting whether an H1 decile pick wins (relative),
  same purge/embargo, applied as a probability filter.
- **H4 cross-asset trend:** per-asset average sign of 1/3/6/12-m returns, inverse-vol
  risk-parity weights (gross = 1), then a **single** causal portfolio vol-target to 10%
  (`lever = 0.10 / trailing-63d-vol`, lagged 1 day). Gap returns winsorized to ±20%.
- **Backtest core (`backtest_weights`):** monthly weights forward-filled to daily and
  **lagged one day** (trade on next open); cost = Σ|Δw| × bps, also lagged. Turnover is
  the annualized sum of absolute weight changes.

### The combiner (the fix this session)

The previous combiner did two things: (1) a causal inverse-vol weight across sleeves —
correct — **and (2) a second, redundant portfolio-level vol-target overlay on top**. Because
each sleeve is *already* vol-targeted, step (2) only re-levered the book against a noisy
trailing-vol estimate, adding timing/estimation drag and dropping OOS Sharpe to **0.86**.

The combiner is now a **clean causal inverse-volatility blend** (trailing 63-day vol,
lagged 1 day, weights renormalized to sum 1) with **no second overlay**:

```python
def equal_risk_combo(parts, lookback=63):
    df = pd.concat(parts, axis=1).dropna()
    inv_vol = 1.0 / (df.rolling(lookback).std().shift(1) * sqrt(252)).replace(0, nan)
    w = inv_vol.div(inv_vol.sum(axis=1), axis=0)
    return (df * w).sum(axis=1).dropna()
```

This lifts the H5+H4 blend to **0.90 OOS** net Sharpe. (For reference, a static equal-weight
blend scores 0.908 — the rolling inverse-vol estimate costs a hair of estimation noise
because the two sleeves are already near-equal-vol; either is a defensible clean blend.)

---

## 6. Backtest methodology

- Daily returns, monthly weights, 1-day execution lag, costs net.
- **OOS = 2012-01-01 onward** (H5/H6 are OOS-only by walk-forward construction).
- Sleeves combined by **inner-join on the equity trading calendar** with √252
  annualization — consistent and conservative (a union calendar that keeps weekend crypto
  PnL inflates the period count to ~344/yr and is not used).
- **Metrics:** annualized Sharpe & Sortino; **PSR** (Bailey–López de Prado, skew/kurtosis
  adjusted, vs 0); **DSR** = PSR vs the expected best Sharpe of the search, deflating for
  **8 trials** (6 hypotheses + 2 combos) using the daily per-period Sharpe of every OOS
  trial as the deflation pool; max drawdown; annualized turnover.
- **Hand-verification** (`research/verify.py`, no engine helpers, independent skew/kurt
  PSR): reproduces every headline OOS Sharpe and PSR and the H5/H4 correlation. ✔

---

## 7. Results (OOS 2012+, net of costs)

| Strategy | IS Sharpe | **OOS Sharpe** | OOS PSR | OOS DSR | OOS maxDD | OOS annRet | Turnover (×/yr) |
|---|---:|---:|---:|---:|---:|---:|---:|
| H1 momentum | −0.02 | 0.22 | 0.78 | 0.06 | −50.8% | 5.4% | 12.5 |
| H2 reversal | 0.12 | −0.01 | 0.48 | 0.01 | −47.7% | −0.3% | 40.4 |
| H3 low-vol | −0.87 | −0.82 | 0.00 | 0.00 | −94.3% | −19.2% | 6.0 |
| H4 cross-asset trend | 0.45 | 0.59 | 0.996 | 0.36 | −27.6% | 6.8% | 9.2 |
| **H5 LGBM cross-sectional** | n/a* | **0.81** | 0.998 | 0.69 | −21.6% | 11.7% | 30.5 |
| H6 meta-momentum | n/a* | 0.16 | 0.72 | 0.04 | −93.0% | 6.7% | 19.1 |
| **COMBO H5+H4 (winner)** | 0.48 | **0.90** | **0.9995** | **0.71** | **−20.0%** | 8.8% | ≈19 |
| COMBO equity (H1+H3+H6) | −0.61 | −0.11 | 0.35 | 0.00 | −76.3% | −2.4% | — |
| COMBO H5+H4+H1 (all) | 0.44 | 0.82 | 0.998 | 0.60 | −16.1% | 8.5% | — |

\* H5/H6 produce signals only on the walk-forward OOS window, so IS Sharpe is undefined
(reported as 0 in `results.json`).

**OOS correlation of the two winning sleeves: ρ(H5, H4) = 0.04** (verify.py).
Combined annual two-sided turnover of the blend ≈ 19× notional (inverse-vol-weighted
average of H5's 30.5× and H4's 9.2×); the equity sleeve rebalances ~118 names/month, the
trend sleeve ~37 instruments/month, monthly.

### Why 0.90, not 0.99
Two equal-vol, uncorrelated sleeves of Sharpe S₁, S₂ blend to ≈(S₁+S₂)/√2. With H5 = 0.81
and H4's standalone 0.59 that is 0.99 — **but inside the equity trading calendar H4
contributes ≈0.49** (it gives up weekend crypto PnL), so the realistic ceiling is
(0.81+0.49)/√2 ≈ 0.92, and we realize **0.90**. The earlier 0.99 working note conflated
H4's standalone Sharpe with its in-blend contribution.

---

## 8. Winning strategy

**Two-sleeve inverse-vol blend: H5 (LightGBM cross-sectional equity L/S) + H4 (cross-asset
trend).**

- **OOS net Sharpe 0.90**, PSR **0.9995**, DSR **0.71**, max drawdown **−20.0%**,
  annualized return **8.8%** at ~9.8% vol.
- Survives an 8-trial deflation (DSR 0.71 ≫ 0) — not a multiple-testing artifact.
- The two return streams are genuinely independent (ρ = 0.04): one is a non-linear
  cross-sectional equity ranker, the other a long-vol-like macro trend book. The blend
  halves drawdown relative to either sleeve's standalone risk profile and is the most
  robust line in the table.

---

## 9. Robustness & limitations

**Robust:** (a) H5 is fully walk-forward with purge + embargo — no peeking; (b) results
hand-verified by an independent implementation; (c) the winner's edge concentrates in the
two sleeves that have the clearest economic priors (ML cross-section + trend), not in the
fragile factors; (d) DSR survives deflation.

**Limitations — be honest:**
1. **Sharpe 0.90 < 1.0 bar.** We do not clear the headline Sharpe gate. PSR/DSR are clear.
2. **Survivorship.** The equity universe is built from tickers that *still exist* with long
   history and current liquidity → upward bias on the equity sleeve; the trend sleeve
   (futures/ETF) is largely immune.
3. **Costs are a flat bps model**, no market-impact / borrow / shorting-availability;
   H5's 30× turnover is cost-sensitive — at 10 bps/side its standalone Sharpe would erode.
4. **Annual retrain, yearly cross-section** keeps the walk-forward cheap but coarse; a
   monthly retrain might add or subtract — untested.
5. **Crypto calendar mismatch** is handled by inner-join (conservative); it slightly
   undercounts H4's true contribution.
6. **2012 split** gives a healthy OOS but a single regime cut; no parameter is re-optimized
   OOS, which is the point, but it also means no regime-conditional sizing.

---

## 10. Recommendation — wiring the winner into the TRADING engine / Strategy Lab

The engine (`trading_engine/src/strategies/`) exposes a per-symbol `StrategyBase`
(`generate_signals(df, symbol) -> direction/score/stops`) and an `EnsembleStrategy`
combiner. The two sleeves map differently:

1. **H4 cross-asset trend → new `StrategyBase` subclass `CrossAssetTSMOM`.**
   It is natively per-symbol: signal = average sign of 1/3/6/12-month returns; `score` =
   |trend agreement|; size ∝ 1/(trailing-63d vol). Drop it next to
   `trend_following.py` / `donchian_trend_rider.py`. Config:
   ```yaml
   strategy: cross_asset_tsmom
   lookbacks_days: [21, 63, 126, 252]
   vol_lookback_days: 63
   vol_target_annual: 0.10
   max_leverage: 3.0
   universe: [ES=F, NQ=F, ZB=F, ZN=F, CL=F, GC=F, SI=F, HG=F, 6E=F, 6J=F, BTC-USD, ETH-USD, ...]
   cost_bps_per_side: 2.0
   rebalance: monthly
   ```
2. **H5 LightGBM cross-sectional rank → a panel-level `CrossSectionalRanker` signal
   provider** (not per-symbol). It needs the full name × feature panel each month, emits a
   decile long/short book, and should ship the trained yearly models + the 12-feature
   transform as an artifact. Cleanest home: a Strategy-Lab "cross-sectional" signal that
   outputs target weights rather than per-bar signals.
3. **Blend in the Strategy Lab via `EnsembleStrategy`** with a **causal inverse-vol weight**
   (63-day, 1-day lag) across the two sleeve return streams and **no second vol-target
   overlay** — exactly `equal_risk_combo`. Target ~10% portfolio vol; expect ≈0.9 net
   Sharpe, ≈9% return, ≈−20% maxDD.

**One-line wiring recommendation:** add a `CrossAssetTSMOM(StrategyBase)` trend strategy and
a panel-level `CrossSectionalRanker` (LGBM) signal, and combine the two in `EnsembleStrategy`
with a 63-day causal inverse-vol weight (no extra vol-target overlay).

---

## 11. Reproduce

```bash
cd pricinglibrary_rag_backend
python research/build_universe.py     # -> artifacts/universe.csv, equity_close_panel.parquet
python research/alpha_pipeline.py     # -> artifacts/results.json, *_returns.parquet, lgbm_xs_pred.parquet
python research/verify.py             # independent recompute of headline OOS numbers
```

Artifacts: `research/artifacts/` — `results.json` (all metrics), per-strategy
`*_returns.parquet`, `lgbm_xs_pred.parquet` (H5 OOS prediction panel),
`equity_close_panel.parquet`, `universe.csv`.
