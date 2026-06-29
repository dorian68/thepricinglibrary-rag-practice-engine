# Part 2 (iter 4) — Regime-Switching Meta-Strategy: Honest Walk-Forward OOS

Directed hypothesis: single classic strategies show no broad OOS edge, so route each bar to the strategy adequate for the **causally-detected** regime. TEST-window (OOS) numbers only; fixed default sub-strategy params (no param mining); the train-fitted mapping is the only thing fit on train.

## No-look-ahead status of the regime label

**Verified causal — no fix needed.** The regime (`add_regime_features` -> `MarketRegimeClassifier`) is a function of `trend_strength`, `vol_percentile_100`, `abs_return_z_100`, `ema_slope_20`. Every one is a TRAILING rolling/ewm window of close/high/low only:
- `trend_strength = |ema20-ema50|/atr14` (ewm + trailing ATR)
- `vol_percentile_100 = realized_vol_20.rolling(100).rank(pct=True)` (rank of the current value within the trailing 100-window)
- `abs_return_z_100 = rolling_zscore(|log_return|,100)` (trailing mean/std)
- `ema_slope_20 = ema20.diff(5)` (current minus 5 bars ago)
A repo-wide search found **no `center=True` and no negative `.shift(-n)`** anywhere in `src/`. The backtester additionally acts on `signals.iloc[i-1]` at bar i's open, so the realized routing lags the label by a full bar. regime[t] uses only data <= t. The {regime->strategy} mapping for the train-fitted variant is fit on the TRAIN slice only.

## Walk-forward / portfolio method

- Per instrument: train 50% / val 25% / **test 25% (OOS)**; features computed on full history then sliced so the first test bar has full trailing warm-up.
- Vol-targeted portfolio: inverse trailing-vol weights (60d, lagged 1d) across the 33 instruments, then scaled to a 10% annual vol target (trailing 60d, lagged), leverage capped 3x — all weights causal.
- Train-fitted mapping: best of the 8 strategies per regime by total TRAIN PnL (min 4 train trades, else economic-prior fallback).
- Benchmarks: SPX buy&hold and a 60/40 proxy (0.6xSPX + 0.4% cash; no bond series in the universe) over the same calendar window as the portfolio.

## Portfolio OOS curve stats vs benchmarks

| Strategy / benchmark | ann.ret% | Sharpe | Sortino | maxDD% | Calmar | profit factor | days |
|---|---|---|---|---|---|---|---|
| Meta — economic prior (crisis=flat) | -2.51 | -0.266 | -0.317 | -56.21 | -0.045 | 0.95 | 6631 |
| Meta — economic prior (crisis=trend) | -3.18 | -0.336 | -0.415 | -62.93 | -0.050 | 0.94 | 6631 |
| Meta — train-fitted mapping | 1.09 | 0.184 | 0.222 | -23.82 | 0.046 | 1.04 | 6631 |
| Single trend_following (all regimes) | -2.90 | -0.296 | -0.357 | -60.64 | -0.048 | 0.94 | 6631 |
| Plain ensemble | -3.49 | -0.379 | -0.450 | -63.55 | -0.055 | 0.93 | 6631 |
| **Benchmark: SPX buy&hold** | 7.81 | 0.491 | 0.614 | -56.78 | 0.138 | 1.10 | 6184 |
| **Benchmark: 60/40 proxy** | 5.07 | 0.491 | 0.614 | -38.03 | 0.133 | 1.10 | 6184 |

## Per-mapping breadth summary (OOS, across instruments)

| Variant | N inst | median Sharpe | median ret% | % inst positive | total #trades | #inst PSR>0.95 | BH(0.05) | Bonferroni |
|---|---|---|---|---|---|---|---|---|
| Meta — economic prior (crisis=flat) | 33 | -0.288 | -15.98 | 21% | 4339 | 1 | 0 | 0 |
| Meta — economic prior (crisis=trend) | 33 | -0.239 | -18.82 | 15% | 4819 | 0 | 0 | 0 |
| Meta — train-fitted mapping | 33 | -0.140 | -6.39 | 27% | 2740 | 2 | 0 | 0 |
| Single trend_following (all regimes) | 33 | -0.314 | -15.61 | 27% | 4961 | 0 | 0 | 0 |
| Plain ensemble | 33 | -0.321 | -19.41 | 21% | 4931 | 0 | 0 | 0 |

## Regime-conditional performance (OOS, total PnL $ across all instruments)

Descriptive 'which strategy wins in which regime' on the TEST window (NOT used for selection — selection is train-only). Each strategy run standalone across all regimes; trades grouped by the regime at entry.

| Strategy | trend | range | low_volatility | high_volatility | crisis |
|---|---|---|---|---|---|
| trend_following | -1,694,940 | -571,169 | -445,102 | -162,660 | -2,193,808 |
| volatility_breakout | -2,680,183 | -32,169 | -523,796 | · | -19,312 |
| mean_reversion | -378,209 | -232,809 | -120,421 | -22,096 | 1,557 |
| opening_range_breakout | · | · | · | · | · |
| pullback_trend_continuation | -1,165,235 | -452,866 | 95,502 | 26,641 | -659,650 |
| volatility_squeeze | -1,661,941 | -120,224 | 18,642 | -106,276 | -121,061 |
| intraday_momentum_burst | -957,761 | -256,656 | 26,939 | -228,784 | -2,184,514 |
| donchian_trend_rider | 800,081 | 152,326 | -19,948 | -688 | -388,709 |

Per-regime OOS winner (max total PnL): 
**trend** -> donchian_trend_rider (800,081); **range** -> donchian_trend_rider (152,326); **low_volatility** -> pullback_trend_continuation (95,502); **high_volatility** -> pullback_trend_continuation (26,641); **crisis** -> mean_reversion (1,557)

## Train-fitted mapping (consensus across instruments)

| Regime | most-picked strategy (count / N) | distribution |
|---|---|---|
| trend | donchian_trend_rider (13/33) | donchian_trend_rider:13, trend_following:11, pullback_trend_continuation:3, volatility_breakout:3, volatility_squeeze:2, mean_reversion:1 |
| range | mean_reversion (11/33) | mean_reversion:11, pullback_trend_continuation:6, volatility_squeeze:5, volatility_breakout:5, donchian_trend_rider:4, trend_following:2 |
| low_volatility | mean_reversion (10/33) | mean_reversion:10, volatility_breakout:8, volatility_squeeze:5, pullback_trend_continuation:5, trend_following:3, donchian_trend_rider:2 |
| high_volatility | volatility_breakout (27/33) | volatility_breakout:27, pullback_trend_continuation:3, donchian_trend_rider:2, trend_following:1 |
| crisis | donchian_trend_rider (12/33) | donchian_trend_rider:12, flat:8, pullback_trend_continuation:7, trend_following:3, volatility_squeeze:2, volatility_breakout:1 |

## Honest verdict

**Regime-switching did NOT deliver a deployable, benchmark-beating OOS edge.** Best meta variant `Meta — train-fitted mapping`: Sharpe 0.184 vs SPX buy&hold 0.491; ann.ret 1.09% vs SPX 7.81%; maxDD -23.82% vs -56.78%. Instrument-level discoveries surviving Benjamini-Hochberg across the universe: Meta — economic prior (crisis=flat)=0, Meta — economic prior (crisis=trend)=0, Meta — train-fitted mapping=0. Routing reshapes the risk profile (lower drawdown, far fewer trades) but does not manufacture risk-adjusted alpha that beats simply holding the index. Reported honestly: no deployable spec.

## Caveats

- Daily OHLC; intrabar adverse (stop-first) fills; overnight financing not modelled (~1-2%/yr optimistic); circuit-breakers relaxed for edge measurement; per-trade spread+slippage modelled.
- 60/40 uses a cash proxy for the 40% (no bond series in the farmed universe) — understates a real 60/40 total return.
- PSR (n_trials=1, no param grid here) is used as the per-instrument pseudo p-value; the train-fitted variant additionally selects 1-of-8 per regime, a mild extra multiple-comparison the BH-across-instruments correction does not fully absorb.

