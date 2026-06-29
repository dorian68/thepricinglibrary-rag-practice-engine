# Part 2 (iter 3) — Vol-Targeted Trend Portfolio + ML-into-OOS

Two honest, look-ahead-free attempts at a deployable positive-PnL edge, building on the broad single-instrument OOS run (which found **no** broad single-instrument edge surviving multiple-comparison correction). All numbers below are TEST-window (OOS) only.

## Lever A — Diversified vol-targeted trend portfolio

- **Construction**: per-instrument trend_following OOS daily return streams (same selected params as the broad run), combined on a common daily calendar. Inverse-vol (risk-parity) weights from a 63-day TRAILING realized vol (shifted 1 day — no look-ahead), then a portfolio-level overlay scaling to ~10% annualized vol using trailing portfolio vol (leverage capped 3x).
- **Instruments combined**: 33 (those with >=30 OOS days and non-zero vol).
- **Per-trade costs** (half-spread entry+exit + vol-scaled slippage) are already baked into each leg's return stream. Overnight financing is NOT modelled (small optimistic bias). Daily bars.

### Portfolio vs benchmarks (OOS)

| Series | OOS window | ann.ret | ann.vol | Sharpe | Sortino | maxDD | Calmar | total ret |
|---|---|---|---|---|---|---|---|---|
| Trend portfolio (inverse-vol, 10% vol target) | 2001-12-27→2026-06-28 | 0.52% | 6.10% | 0.12 | 0.14 | 21.56% | 0.02 | 14.57% |
| Trend portfolio (equal-weight, 10% vol target) | 2001-11-28→2026-06-28 | 0.72% | 6.25% | 0.15 | 0.18 | 21.56% | 0.03 | 20.80% |
| Trend portfolio (equal-weight, no vol target) | 2001-11-28→2026-06-28 | 0.31% | 2.15% | 0.16 | 0.19 | 7.92% | 0.04 | 8.62% |
| Benchmark: buy&hold SPX | 2001-12-27→2026-06-26 | 7.88% | 19.05% | 0.49 | 0.62 | 56.78% | 0.14 | 539.83% |
| Benchmark: 60/40 SPX/AGG | 2001-12-27→2026-06-26 | 6.36% | 11.57% | 0.59 | 0.74 | 36.06% | 0.18 | 351.82% |

- **Best single instrument OOS Sharpe** (for context): GOLD = 1.05 (ann.ret 4.18%, maxDD 6.37%).
- **Average pairwise correlation** of instrument OOS return streams: 0.062. On the worst 10% portfolio days, average pairwise correlation rises to 0.028 — trend bets DO cluster in crises, the standard CTA caveat.

### Per-instrument single-leg OOS Sharpe (the legs, incl. losers)

| Symbol | OOS Sharpe | ann.ret | maxDD |
|---|---|---|---|
| GOLD | 1.05 | 4.18% | 6.37% |
| AAPL | 0.70 | 2.52% | 8.02% |
| MMM | 0.53 | 1.67% | 6.59% |
| ETHUSD | 0.52 | 2.03% | 5.61% |
| MSFT | 0.47 | 2.18% | 10.99% |
| NDX | 0.47 | 1.39% | 7.65% |
| EURUSD | 0.47 | 0.99% | 3.40% |
| BTCUSD | 0.29 | 0.94% | 7.19% |
| GS | 0.25 | 0.63% | 4.97% |
| DIS | 0.25 | 0.72% | 10.16% |
| GE | 0.25 | 0.69% | 13.69% |
| OIL | 0.24 | 0.57% | 5.97% |
| SPX | 0.22 | 0.68% | 9.09% |
| AMZN | 0.18 | 0.90% | 14.77% |
| DJI | 0.14 | 0.39% | 9.00% |
| USDJPY | 0.11 | 0.43% | 7.47% |
| GBPUSD | 0.04 | 0.09% | 10.73% |
| KO | 0.03 | 0.05% | 16.63% |
| WMT | 0.00 | -0.14% | 26.02% |
| JPM | -0.00 | -0.05% | 13.52% |
| CAT | -0.06 | -0.25% | 21.77% |
| JNJ | -0.13 | -0.37% | 16.85% |
| PG | -0.14 | -0.45% | 10.65% |
| IBM | -0.16 | -0.53% | 18.96% |
| MCD | -0.20 | -0.63% | 13.09% |
| NIKKEI | -0.31 | -1.29% | 33.35% |
| INTC | -0.33 | -1.31% | 22.78% |
| CVX | -0.34 | -1.03% | 20.69% |
| SILVER | -0.41 | -3.21% | 31.32% |
| XOM | -0.42 | -1.47% | 23.84% |
| COPPER | -0.48 | -3.46% | 36.16% |
| DAX | -0.65 | -4.51% | 39.48% |
| FTSE | -0.89 | -3.13% | 32.88% |

## Lever B — Meta-labeling wired into the walk-forward (train-only, applied to TEST)

Meta-classifier trained on TRAIN+VALIDATION events only (triple-barrier labels, embargoed so no training label resolves inside the test window), then used to filter signals on the held-out TEST window. RAW vs ML run on **identical frozen signals** — the ML filter is the only difference. Subset = top-trade-count instruments + GOLD.

| Symbol | Model | raw Sharpe | ML Sharpe | raw PF | ML PF | raw maxDD | ML maxDD | raw ret% | ML ret% | raw tr | ML tr | trained | kept% |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| WMT | logistic | 0.01 | 0.01 | 0.99 | 1.00 | 26.02 | 17.63 | -1.48 | -0.30 | 171 | 94 | True | 29% |
| WMT | random_forest | 0.01 | 0.00 | 0.99 | 0.99 | 26.02 | 8.10 | -1.48 | -0.17 | 171 | 30 | True | 5% |
| DAX | logistic | -0.66 | -0.54 | 0.65 | 0.59 | 39.48 | 17.15 | -36.18 | -15.53 | 173 | 52 | True | 13% |
| DAX | random_forest | -0.66 | 0.03 | 0.65 | 1.03 | 39.48 | 4.90 | -36.18 | 0.33 | 173 | 15 | True | 3% |
| SPX | logistic | 0.22 | 0.33 | 1.22 | 1.43 | 9.09 | 7.78 | 18.12 | 24.71 | 129 | 90 | True | 17% |
| SPX | random_forest | 0.22 | 0.33 | 1.22 | 1.60 | 9.09 | 5.66 | 18.12 | 21.02 | 129 | 60 | True | 17% |
| SILVER | logistic | -0.42 | 0.11 | 0.77 | 1.09 | 31.32 | 11.15 | -19.08 | 2.53 | 125 | 39 | True | 31% |
| SILVER | random_forest | -0.42 | -0.15 | 0.77 | 0.83 | 31.32 | 14.36 | -19.08 | -2.93 | 125 | 24 | True | 11% |
| NIKKEI | logistic | -0.33 | -0.19 | 0.76 | 0.78 | 33.35 | 12.29 | -18.35 | -6.33 | 119 | 42 | True | 11% |
| NIKKEI | random_forest | -0.33 | 0.14 | 0.76 | 1.17 | 33.35 | 7.80 | -18.35 | 3.90 | 119 | 38 | True | 8% |
| COPPER | logistic | -0.48 | -0.62 | 0.75 | 0.60 | 36.16 | 19.19 | -20.24 | -14.81 | 120 | 48 | True | 20% |
| COPPER | random_forest | -0.48 | -0.12 | 0.75 | 0.88 | 36.16 | 13.73 | -20.24 | -4.51 | 120 | 49 | True | 21% |
| MSFT | logistic | 0.47 | 0.02 | 1.35 | 1.00 | 10.99 | 11.38 | 23.13 | -0.04 | 103 | 52 | True | 21% |
| MSFT | random_forest | 0.47 | 0.59 | 1.35 | 2.14 | 10.99 | 5.89 | 23.13 | 13.80 | 103 | 23 | True | 9% |
| CAT | logistic | -0.06 | 0.04 | 0.94 | 1.02 | 21.77 | 14.26 | -3.88 | 0.94 | 97 | 59 | True | 21% |
| CAT | random_forest | -0.06 | 0.09 | 0.94 | 1.12 | 21.77 | 12.60 | -3.88 | 2.74 | 97 | 31 | True | 12% |
| XOM | logistic | -0.42 | -0.23 | 0.67 | 0.78 | 23.84 | 14.55 | -20.71 | -8.35 | 97 | 54 | True | 28% |
| XOM | random_forest | -0.42 | -0.31 | 0.67 | 0.65 | 23.84 | 14.18 | -20.71 | -9.96 | 97 | 39 | True | 16% |
| FTSE | logistic | -0.89 | -0.43 | 0.45 | 0.62 | 32.88 | 14.37 | -28.71 | -9.39 | 79 | 34 | True | 13% |
| FTSE | random_forest | -0.89 | 0.15 | 0.45 | 1.31 | 32.88 | 3.84 | -28.71 | 2.30 | 79 | 12 | True | 3% |
| GOLD | logistic | 1.05 | 0.96 | 2.21 | 2.30 | 6.37 | 4.79 | 30.01 | 21.26 | 50 | 34 | True | 31% |
| GOLD | random_forest | 1.05 | 0.90 | 2.21 | 2.06 | 6.37 | 8.02 | 30.01 | 19.33 | 50 | 37 | True | 25% |

- Across 22 trained (symbol,model) runs, ML improved OOS Sharpe in **17/22**; mean ΔSharpe = **+0.187** (median +0.116). Mean raw Sharpe -0.14 vs ML 0.05.
- Mean ΔProfitFactor = +0.156; mean ΔmaxDD = -13.59 pp (negative = ML reduced drawdown).

### The critical honesty caveat on Lever B

The headline "+0.187 Sharpe" is **not** evidence the model found alpha. The filter keeps only 3–31% of trades, i.e. it mostly *removes exposure*, and the improvement is concentrated entirely on the legs whose RAW strategy was already a **loser**:

- **On the loser legs** (raw Sharpe < 0: DAX, FTSE, SILVER, COPPER, NIKKEI, XOM, CAT), mean ΔSharpe ≈ **+0.40** — but this is just "trade much less on a losing instrument", which mechanically cuts losses and drawdown. It is loss-mitigation, not edge.
- **On the genuinely positive legs** (raw Sharpe > 0.1: GOLD, MSFT, SPX), mean ΔSharpe ≈ **−0.06** — the filter is neutral-to-slightly-harmful. It HURTS the best instrument (GOLD 1.05→0.96 logistic, →0.90 RF) and is mixed on MSFT (logistic 0.47→0.02 harmful, RF 0.47→0.59 helpful). Only SPX improves on both models (0.22→0.33).
- Random-forest vs logistic also disagree on sign for several legs (DAX, NIKKEI, FTSE, MSFT) — a model-selection coin-flip, the opposite of a robust effect.

**Read:** meta-labeling here is a risk/exposure overlay that reduces damage on instruments that shouldn't be traded at all; it does **not** add alpha to the instruments worth trading. That is consistent with the literature — meta-labels rarely rescue an already-thin trend signal.

## Honest verdict

**NO — no deployable risk-adjusted edge over the benchmark was found.**

- Portfolio OOS Sharpe **0.12** (ann.ret 0.5%, maxDD 21.6%, Calmar 0.02) vs buy&hold SPX Sharpe 0.49 and 60/40 Sharpe 0.59.
- Does NOT beat SPX risk-adjusted; does NOT beat 60/40; does NOT beat the best single instrument (GOLD, Sharpe 1.05).
- ML (meta-labeling): mean ΔSharpe +0.187 across 22 runs looks positive, but (see Lever-B caveat) it is **loss-mitigation on losing legs, not alpha** — it slightly HURTS the genuinely positive legs (GOLD, MSFT-logistic) and the two model families disagree on sign. **Ship WITHOUT ML as an alpha source.** It could only be justified as a conservative exposure-reduction overlay, never as the edge.

No spec is featured for production: neither the diversified portfolio nor the ML overlay clears a passive benchmark risk-adjusted, OOS. Anything surfaced on the platform must be labelled research/educational, not a live edge claim.

### What WOULD be defensible to feature (research-grade, not "alpha")

- The single most robust artefact remains **trend_following on GOLD** (OOS Sharpe 1.05, DSR 0.96, maxDD 6.4%, OOS>train) — but as one bet it does not survive multiple-comparison correction across 33 instruments, so it is a teaching example of survivorship/luck, not a deployable edge.
- The honest, valuable lesson to teach: a naive equal/risk-parity blend of many classic trend bets diversifies *volatility* (portfolio vol 6.1% vs legs 15-40%, avg pairwise corr 0.06) but **not into positive Sharpe**, because roughly half the single-instrument trend bets are negative OOS and they cancel. Real CTA edge needs better instrument selection, faster data, and carry/cross-sectional signals this universe/params don't capture.

## Caveats / honesty

- Daily bars; intrabar path unknown (engine takes the adverse stop-first fill).
- Overnight financing/swap not modelled (small optimistic bias, <1x leverage per leg).
- The portfolio overlaps instruments with very different OOS start dates (deep-history stocks from ~2009, crypto from ~2023); early portfolio days hold fewer legs, so early diversification is weaker than the full-universe count suggests.
- Circuit-breakers relaxed for edge measurement (as in the broad run).
- Vol-target leverage is capped at 3x; uncapped numbers would be more volatile.
- This is a research portfolio on indicative yfinance daily history, not a live track record.
