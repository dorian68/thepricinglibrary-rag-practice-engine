# Part 2 — Broad Out-of-Sample Evaluation on the Farmed Daily Database

Honest, statistically-meaningful walk-forward OOS run. Integrity over pretty numbers: the full distribution incl. losers is reported, and edge is judged by **breadth across instruments** with a multiple-comparison correction.

## Method

- **Universe**: 33 instruments (equity indices, large-cap US stocks, commodities, FX, crypto), daily bars over full available history (decades for stocks/indices).
- **Walk-forward**: train 50% / validation 25% / **test (OOS) 25%**. Params chosen on the validation window; only TEST-window numbers are reported below.
- **Deflated Sharpe (DSR)**: probability the OOS Sharpe beats the *expected best Sharpe of the grid search* (Bailey & López de Prado). It already corrects for the number of grid trials per instrument. DSR is a probability in [0,1]; DSR>0.5 = more-likely-than-not real, DSR>0.95 = 5% level.
- **Sizing**: scale-free unit-CFD, 1% equity risk/trade. Single backtests now FILL hundreds of trades on deep data (sanity check passed on SPX).
- **Costs modelled**: half bid/ask spread on entry+exit + volatility-scaled slippage. **Not** modelled: overnight financing/swap (effective leverage <1x, so ~1-2%/yr optimistic bias) and live circuit-breakers (relaxed: they are capital-preservation overlays, not alpha).
- **Multiple comparisons across instruments**: per strategy we treat p = 1 − DSR as a pseudo p-value and apply Benjamini-Hochberg FDR (q=0.05) and Bonferroni across the universe.

## Per-strategy breadth summary (OOS / TEST window only)

| Strategy | N inst | median OOS Sharpe | median OOS ret% | % positive ret | median #trades | #inst DSR>0.5 & trades>=30 | #inst DSR>0.95 | BH(0.05) discoveries | Bonferroni |
|---|---|---|---|---|---|---|---|---|---|
| trend_following | 33 | 0.04 | 0.37 | 55% | 74 | 7 | 1 | 0 | 0 |
| volatility_breakout | 33 | 0.00 | 0.00 | 39% | 1 | 0 | 1 | 0 | 0 |
| mean_reversion | 33 | -0.15 | -1.01 | 18% | 2 | 0 | 0 | 0 | 0 |

## Equal-weight OOS aggregate per strategy

Mean across instruments of each OOS metric (a crude equal-weight portfolio proxy).

| Strategy | mean OOS ret% | mean OOS Sharpe | mean OOS maxDD% | mean profit factor |
|---|---|---|---|---|
| trend_following | -0.25 | 0.04 | 15.74 | 1.11 |
| volatility_breakout | 0.32 | 0.06 | 1.27 | 0.52 |
| mean_reversion | -1.03 | -0.15 | 2.30 | 0.37 |

## Single best robust config

- **trend_following on GOLD** (commodity), params `{"fast_ema": 10, "slow_ema": 100, "atr_stop_mult": 2.5, "trailing_stop": false}`
- OOS window 2020-01-21 → 2026-06-26: return 30.068%, Sharpe 1.052, deflated Sharpe 0.9591, maxDD 6.372%, profit factor 2.209, 50 OOS trades, CAGR 2.862%.
- Train return 4.268% on 139 trades (overfit check: compare to OOS return 30.068%).

## Full per (strategy, instrument) OOS table

| Strategy | Symbol | Class | bars | OOS window | OOS ret% | OOS Sharpe | DSR | maxDD% | PF | #trades | train ret% | overfit? |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| mean_reversion | AAPL | equity | 11066 | 2013-11-07→2024-11-04 | -4.842 | -0.553 | 0.0056 | 4.842 | 0.0 | 5 | 1.589 | thin |
| mean_reversion | AMZN | equity | 6914 | 2017-12-21→2024-11-04 | 0.276 | 0.038 | 0.0802 | 3.035 | 1.091 | 5 | 5.468 | thin |
| mean_reversion | BTCUSD | crypto | 4302 | 2023-07-19→2026-06-28 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0 | 0.0 | thin |
| mean_reversion | CAT | equity | 15819 | 2009-02-20→2024-11-04 | -5.49 | -0.666 | 0.0 | 5.49 | 0.0 | 5 | -1.415 | thin |
| mean_reversion | COPPER | commodity | 6484 | 2020-01-21→2026-06-26 | 2.13 | 0.185 | 0.5088 | 2.236 | 2.492 | 2 | -3.032 | thin |
| mean_reversion | CVX | equity | 15819 | 2009-02-20→2024-11-04 | -0.757 | -0.234 | 0.0157 | 1.383 | 0.0 | 1 | -1.007 | thin |
| mean_reversion | DAX | index | 9732 | 2016-11-23→2026-06-26 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0 | -2.015 | thin |
| mean_reversion | DIS | equity | 15819 | 2009-02-20→2024-11-04 | -5.932 | -0.3 | 0.0647 | 8.983 | 0.286 | 10 | -16.397 | thin |
| mean_reversion | DJI | index | 8682 | 2017-11-06→2026-06-26 | -1.239 | -0.273 | 0.0034 | 2.004 | 0.386 | 3 | 1.115 | thin |
| mean_reversion | ETHUSD | crypto | 3153 | 2024-05-01→2026-06-28 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0 | 0.0 | thin |
| mean_reversion | EURUSD | fx | 5856 | 2020-11-11→2026-06-26 | -1.045 | -0.322 | 0.0312 | 1.899 | 0.0 | 1 | -1.012 | thin |
| mean_reversion | FTSE | index | 10731 | 2015-11-11→2026-06-26 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0 | -0.763 | thin |
| mean_reversion | GBPUSD | fx | 5868 | 2020-11-06→2026-06-26 | -1.013 | -0.29 | 0.0342 | 1.578 | 0.0 | 1 | -3.03 | thin |
| mean_reversion | GE | equity | 15819 | 2009-02-20→2024-11-04 | -3.219 | -0.22 | 0.0141 | 4.436 | 0.283 | 5 | 0.594 | thin |
| mean_reversion | GOLD | commodity | 6479 | 2020-01-21→2026-06-26 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0 | 0.0 | thin |
| mean_reversion | GS | equity | 6419 | 2018-06-21→2024-11-04 | 2.066 | 0.339 | 0.75 | 1.577 | 3.021 | 3 | 0.654 | thin |
| mean_reversion | IBM | equity | 15819 | 2009-02-20→2024-11-04 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0 | -0.646 | thin |
| mean_reversion | INTC | equity | 11254 | 2013-09-03→2024-11-04 | 0.958 | 0.116 | 0.4259 | 2.325 | 1.92 | 2 | 2.091 | thin |
| mean_reversion | JNJ | equity | 15819 | 2009-02-20→2024-11-04 | -3.493 | -0.713 | 0.0 | 3.493 | 0.0 | 4 | -9.496 | thin |
| mean_reversion | JPM | equity | 11254 | 2013-09-03→2024-11-04 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0 | -1.007 | thin |
| mean_reversion | KO | equity | 15819 | 2009-02-20→2024-11-04 | -3.229 | -0.335 | 0.017 | 4.407 | 0.0 | 3 | -2.567 | thin |
| mean_reversion | MCD | equity | 14684 | 2010-04-08→2024-11-04 | -2.023 | -0.389 | 0.0001 | 2.109 | 0.0 | 2 | -4.928 | thin |
| mean_reversion | MMM | equity | 15819 | 2009-02-20→2024-11-04 | 0.469 | 0.055 | 0.2279 | 1.851 | 1.231 | 4 | 0.009 | thin |
| mean_reversion | MSFT | equity | 9740 | 2015-03-06→2024-11-04 | 6.044 | 0.447 | 0.5448 | 2.763 | inf | 2 | -1.239 | thin |
| mean_reversion | NDX | index | 10263 | 2016-04-14→2026-06-26 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0 | -3.572 | thin |
| mean_reversion | NIKKEI | index | 15113 | 2011-01-18→2026-06-26 | -3.128 | -0.399 | 0.001 | 4.083 | 0.234 | 5 | -10.508 | thin |
| mean_reversion | OIL | commodity | 6487 | 2020-01-15→2026-06-26 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0 | -1.007 | thin |
| mean_reversion | PG | equity | 15819 | 2009-02-20→2024-11-04 | -2.515 | -0.207 | 0.0064 | 4.23 | 0.326 | 5 | 1.741 | thin |
| mean_reversion | SILVER | commodity | 6481 | 2020-01-17→2026-06-26 | -1.028 | -0.395 | 0.0034 | 1.028 | 0.0 | 1 | 2.226 | thin |
| mean_reversion | SPX | index | 24738 | 2001-11-27→2026-06-26 | -2.994 | -0.273 | 0.0006 | 2.994 | 0.0 | 3 | -8.758 | thin |
| mean_reversion | USDJPY | fx | 7691 | 2019-02-07→2026-06-27 | -1.058 | -0.289 | 0.0323 | 1.835 | 0.0 | 1 | -2.017 | thin |
| mean_reversion | WMT | equity | 13160 | 2011-10-10→2024-11-04 | -1.014 | -0.15 | 0.0074 | 2.161 | 0.0 | 1 | 1.613 | thin |
| mean_reversion | XOM | equity | 15819 | 2009-02-20→2024-11-04 | -2.018 | -0.154 | 0.0254 | 5.313 | 0.608 | 8 | 9.485 | YES |
| trend_following | AAPL | equity | 11066 | 2013-11-07→2024-11-04 | 25.845 | 0.593 | 0.8486 | 8.021 | 1.492 | 77 | 17.162 |  |
| trend_following | AMZN | equity | 6914 | 2017-12-21→2024-11-04 | 6.116 | 0.18 | 0.5119 | 14.773 | 1.114 | 74 | 28.346 |  |
| trend_following | BTCUSD | crypto | 4302 | 2023-07-19→2026-06-28 | 4.055 | 0.288 | 0.4689 | 7.19 | 1.204 | 33 | 50.466 |  |
| trend_following | CAT | equity | 15819 | 2009-02-20→2024-11-04 | -3.883 | -0.063 | 0.0259 | 21.769 | 0.944 | 97 | 20.414 | YES |
| trend_following | COPPER | commodity | 6484 | 2020-01-21→2026-06-26 | -23.581 | -0.589 | 0.0083 | 36.157 | 0.697 | 116 | -44.412 |  |
| trend_following | CVX | equity | 15819 | 2009-02-20→2024-11-04 | -16.545 | -0.382 | 0.0053 | 20.687 | 0.698 | 78 | 26.668 | YES |
| trend_following | DAX | index | 9732 | 2016-11-23→2026-06-26 | -36.42 | -0.668 | 0.0026 | 39.485 | 0.639 | 168 | -63.015 |  |
| trend_following | DIS | equity | 15819 | 2009-02-20→2024-11-04 | 12.456 | 0.257 | 0.5118 | 10.161 | 1.245 | 76 | 32.123 |  |
| trend_following | DJI | index | 8682 | 2017-11-06→2026-06-26 | 3.386 | 0.136 | 0.2633 | 8.996 | 1.109 | 51 | 10.862 |  |
| trend_following | ETHUSD | crypto | 3153 | 2024-05-01→2026-06-28 | 6.5 | 0.516 | 0.5935 | 5.882 | 1.551 | 23 | 31.998 | thin |
| trend_following | EURUSD | fx | 5856 | 2020-11-11→2026-06-26 | 5.659 | 0.452 | 0.587 | 3.403 | 1.935 | 13 | 8.337 | thin |
| trend_following | FTSE | index | 10731 | 2015-11-11→2026-06-26 | -28.71 | -0.894 | 0.0 | 32.877 | 0.451 | 79 | 18.24 | YES |
| trend_following | GBPUSD | fx | 5868 | 2020-11-06→2026-06-26 | 0.366 | 0.036 | 0.2352 | 10.73 | 1.014 | 38 | -8.561 |  |
| trend_following | GE | equity | 15819 | 2009-02-20→2024-11-04 | 11.573 | 0.249 | 0.4105 | 13.685 | 1.285 | 71 | -5.63 |  |
| trend_following | GOLD | commodity | 6479 | 2020-01-21→2026-06-26 | 30.068 | 1.052 | 0.9591 | 6.372 | 2.209 | 50 | 4.268 |  |
| trend_following | GS | equity | 6419 | 2018-06-21→2024-11-04 | 3.995 | 0.245 | 0.481 | 4.974 | 1.345 | 20 | 5.202 | thin |
| trend_following | IBM | equity | 15819 | 2009-02-20→2024-11-04 | -7.924 | -0.153 | 0.1757 | 18.964 | 0.849 | 74 | 53.404 | YES |
| trend_following | INTC | equity | 11254 | 2013-09-03→2024-11-04 | -13.43 | -0.325 | 0.012 | 22.776 | 0.755 | 78 | -17.555 |  |
| trend_following | JNJ | equity | 15819 | 2009-02-20→2024-11-04 | -5.511 | -0.123 | 0.006 | 16.855 | 0.877 | 64 | -20.516 |  |
| trend_following | JPM | equity | 11254 | 2013-09-03→2024-11-04 | -0.539 | -0.0 | 0.3405 | 13.52 | 0.985 | 61 | 5.244 | YES |
| trend_following | KO | equity | 15819 | 2009-02-20→2024-11-04 | 0.098 | 0.018 | 0.0842 | 16.626 | 1.002 | 75 | 86.373 |  |
| trend_following | MCD | equity | 14684 | 2010-04-08→2024-11-04 | -10.556 | -0.24 | 0.0098 | 13.093 | 0.79 | 74 | 87.155 | YES |
| trend_following | MMM | equity | 15819 | 2009-02-20→2024-11-04 | 29.813 | 0.536 | 0.8475 | 6.586 | 1.797 | 64 | -4.921 |  |
| trend_following | MSFT | equity | 9740 | 2015-03-06→2024-11-04 | 23.125 | 0.471 | 0.8399 | 11.455 | 1.345 | 103 | 23.147 |  |
| trend_following | NDX | index | 10263 | 2016-04-14→2026-06-26 | 15.986 | 0.492 | 0.7656 | 7.646 | 1.454 | 59 | 18.947 |  |
| trend_following | NIKKEI | index | 15113 | 2011-01-18→2026-06-26 | -18.348 | -0.327 | 0.0024 | 33.347 | 0.756 | 119 | 69.366 | YES |
| trend_following | OIL | commodity | 6487 | 2020-01-15→2026-06-26 | 3.881 | 0.248 | 0.2468 | 5.969 | 1.318 | 21 | 2.312 | thin |
| trend_following | PG | equity | 15819 | 2009-02-20→2024-11-04 | -6.751 | -0.14 | 0.1737 | 10.651 | 0.846 | 65 | 13.282 | YES |
| trend_following | SILVER | commodity | 6481 | 2020-01-17→2026-06-26 | -19.539 | -0.426 | 0.0843 | 30.197 | 0.776 | 128 | -35.056 |  |
| trend_following | SPX | index | 24738 | 2001-11-27→2026-06-26 | 18.116 | 0.22 | 0.2792 | 9.085 | 1.224 | 129 | -15.14 |  |
| trend_following | USDJPY | fx | 7691 | 2019-02-07→2026-06-27 | 3.229 | 0.112 | 0.4068 | 7.47 | 1.075 | 66 | -8.426 |  |
| trend_following | WMT | equity | 13160 | 2011-10-10→2024-11-04 | -2.889 | -0.014 | 0.2022 | 26.017 | 0.973 | 168 | 2.384 |  |
| trend_following | XOM | equity | 15819 | 2009-02-20→2024-11-04 | -17.907 | -0.366 | 0.009 | 23.843 | 0.719 | 96 | 8.388 | YES |
| volatility_breakout | AAPL | equity | 11066 | 2013-11-07→2024-11-04 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0 | 0.934 | thin |
| volatility_breakout | AMZN | equity | 6914 | 2017-12-21→2024-11-04 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0 | -1.998 | thin |
| volatility_breakout | BTCUSD | crypto | 4302 | 2023-07-19→2026-06-28 | 1.544 | 0.408 | 0.3361 | 1.403 | inf | 1 | 1.833 | thin |
| volatility_breakout | CAT | equity | 15819 | 2009-02-20→2024-11-04 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0 | -2.0 | thin |
| volatility_breakout | COPPER | commodity | 6484 | 2020-01-21→2026-06-26 | 1.398 | 0.77 | 0.9585 | 0.153 | inf | 1 | 2.069 | thin |
| volatility_breakout | CVX | equity | 15819 | 2009-02-20→2024-11-04 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0 | 1.263 | thin |
| volatility_breakout | DAX | index | 9732 | 2016-11-23→2026-06-26 | 0.737 | 0.069 | 0.1632 | 3.789 | 1.188 | 7 | -0.092 | thin |
| volatility_breakout | DIS | equity | 15819 | 2009-02-20→2024-11-04 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0 | 1.252 | thin |
| volatility_breakout | DJI | index | 8682 | 2017-11-06→2026-06-26 | 1.565 | 0.391 | 0.5132 | 0.632 | inf | 1 | -1.007 | thin |
| volatility_breakout | ETHUSD | crypto | 3153 | 2024-05-01→2026-06-28 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0 | -0.771 | thin |
| volatility_breakout | EURUSD | fx | 5856 | 2020-11-11→2026-06-26 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0 | 4.791 | thin |
| volatility_breakout | FTSE | index | 10731 | 2015-11-11→2026-06-26 | 0.193 | 0.035 | 0.0974 | 1.225 | 1.189 | 2 | -2.015 | thin |
| volatility_breakout | GBPUSD | fx | 5868 | 2020-11-06→2026-06-26 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0 | 2.129 | thin |
| volatility_breakout | GE | equity | 15819 | 2009-02-20→2024-11-04 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0 | 1.242 | thin |
| volatility_breakout | GOLD | commodity | 6479 | 2020-01-21→2026-06-26 | 3.874 | 0.386 | 0.3374 | 4.799 | 1.741 | 10 | -5.135 | thin |
| volatility_breakout | GS | equity | 6419 | 2018-06-21→2024-11-04 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0 | 0.0 | thin |
| volatility_breakout | IBM | equity | 15819 | 2009-02-20→2024-11-04 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0 | -2.01 | thin |
| volatility_breakout | INTC | equity | 11254 | 2013-09-03→2024-11-04 | -1.078 | -0.571 | 0.0 | 1.078 | 0.0 | 1 | -1.066 | thin |
| volatility_breakout | JNJ | equity | 15819 | 2009-02-20→2024-11-04 | 1.457 | 0.158 | 0.3655 | 0.997 | inf | 1 | -2.323 | thin |
| volatility_breakout | JPM | equity | 11254 | 2013-09-03→2024-11-04 | -1.009 | -0.044 | 0.3328 | 5.088 | 0.774 | 5 | -5.395 | thin |
| volatility_breakout | KO | equity | 15819 | 2009-02-20→2024-11-04 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0 | -0.303 | thin |
| volatility_breakout | MCD | equity | 14684 | 2010-04-08→2024-11-04 | 0.925 | 0.086 | 0.5339 | 2.729 | 1.284 | 5 | 4.418 | thin |
| volatility_breakout | MMM | equity | 15819 | 2009-02-20→2024-11-04 | 1.563 | 0.264 | 0.5272 | 0.896 | inf | 1 | 1.269 | thin |
| volatility_breakout | MSFT | equity | 9740 | 2015-03-06→2024-11-04 | -1.252 | -0.191 | 0.1375 | 3.205 | 0.582 | 4 | 0.541 | thin |
| volatility_breakout | NDX | index | 10263 | 2016-04-14→2026-06-26 | -4.401 | -0.372 | 0.0299 | 7.897 | 0.363 | 9 | 3.051 | thin |
| volatility_breakout | NIKKEI | index | 15113 | 2011-01-18→2026-06-26 | 3.132 | 0.33 | 0.8149 | 1.616 | 3.084 | 3 | 22.318 | thin |
| volatility_breakout | OIL | commodity | 6487 | 2020-01-15→2026-06-26 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0 | -2.996 | thin |
| volatility_breakout | PG | equity | 15819 | 2009-02-20→2024-11-04 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0 | -0.76 | thin |
| volatility_breakout | SILVER | commodity | 6481 | 2020-01-17→2026-06-26 | 1.892 | 0.465 | 0.6729 | 0.644 | inf | 1 | 11.071 | thin |
| volatility_breakout | SPX | index | 24738 | 2001-11-27→2026-06-26 | 0.009 | 0.003 | 0.2196 | 2.189 | 1.003 | 5 | -6.648 | thin |
| volatility_breakout | USDJPY | fx | 7691 | 2019-02-07→2026-06-27 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0 | 1.361 | thin |
| volatility_breakout | WMT | equity | 13160 | 2011-10-10→2024-11-04 | -2.023 | -0.386 | 0.0026 | 2.023 | 0.0 | 2 | -1.581 | thin |
| volatility_breakout | XOM | equity | 15819 | 2009-02-20→2024-11-04 | 2.059 | 0.234 | 0.5362 | 1.586 | 2.787 | 3 | -4.341 | thin |

## Honest verdict

**No deployable, statistically-meaningful broad edge was found, even on the deep farmed data.** Isolated instruments may post high OOS Sharpes, but they do not survive correction for the number of instruments tested — consistent with luck, not edge. 'No deployable edge even on deep data' is the honest result for these three classic strategies as currently parameterised.

- **trend_following**: median OOS Sharpe 0.04, 55% of instruments positive OOS, 7/33 pass the DSR>0.5 & >=30-trade guard, 0 survive Benjamini-Hochberg FDR and 0 survive Bonferroni across the universe — no broad edge.
- **volatility_breakout**: median OOS Sharpe 0.00, 39% of instruments positive OOS, 0/33 pass the DSR>0.5 & >=30-trade guard, 0 survive Benjamini-Hochberg FDR and 0 survive Bonferroni across the universe — no broad edge.
- **mean_reversion**: median OOS Sharpe -0.15, 18% of instruments positive OOS, 0/33 pass the DSR>0.5 & >=30-trade guard, 0 survive Benjamini-Hochberg FDR and 0 survive Bonferroni across the universe — no broad edge.

## Caveats

- Daily OHLC backtest: intrabar path unknown, the engine assumes the adverse (stop-first) fill when stop and target sit inside the same bar — conservative.
- Overnight financing not modelled (small optimistic bias, see Method).
- Live circuit-breakers relaxed for edge measurement; a deployed system with the shipped institutional 10% drawdown kill-switch would realise fewer/smaller trades.
- yfinance index/commodity history is indicative (some flat early bars, no live spread); spreads are static per-asset-class estimates, not tick data.
- DSR here is the engine's PSR-against-expected-max benchmark, a probability, not a ratio.
