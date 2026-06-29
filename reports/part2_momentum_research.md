# Part 2 — Cross-Sectional Equity Momentum & Risk-Parity (OOS, net of costs)

Honest test of the two best-documented "real" factors against an SPX buy-and-hold benchmark.
Integrity over pretty numbers: losers and failed sub-periods are reported in full; signals are
causal; costs and survivorship bias are stated openly. No parameter search was run — 12-1 momentum
is a fixed economic prior, so there is nothing to p-hack here, only to confirm or reject.

## TL;DR verdict

- **Cross-sectional 12-1 momentum is REAL but NOT deployably better than SPX out-of-sample.**
  Full-sample (1973–2024) the long-only winner decile beats SPX on Sharpe (0.73 net vs 0.59) and
  the long-short spread is statistically significant (t = 3.0 net). **But the entire edge is
  pre-2000.** Post-2000 the long-only Sharpe (0.36) *loses* to SPX (0.45); post-2010 it loses too
  (0.62 vs 0.85). The long-short premium is dead post-2000 (Sharpe 0.08, negative return). Add a
  catastrophic crash profile (long-only maxDD −67%, long-short −92%) and **survivorship bias that
  inflates every number**, and there is no robust, deployable, risk-adjusted edge in the modern era.
- **Risk parity does NOT robustly beat 60/40.** Unlevered inverse-vol wins the full 2006–2026 sample
  on Sharpe by a hair (0.81 vs 0.78) thanks to the bond bull and lower drawdowns, but it **loses to
  60/40 post-2010 (0.83 vs 0.97)** and gives up ~3.3%/yr of return to SPX. The small edge reverses
  out of sample. Not a clear win.

Consistent with prior reports (`part2_oos_broad.md`, `part2_portfolio_oos.md`,
`part2_regime_switching_oos.md`): **nothing here beats passive SPX risk-adjusted OOS after costs, robustly.**

---

## Methodology

### Data & universe
- Source: farmed daily cache `data/market_history/us_stocks/*.csv` (8,784 of 9,314 tickers had
  ≥260 daily bars). Resampled to **month-end close** and **monthly average daily dollar volume**
  (`close × volume`); cached to `monthly_close.parquet` / `monthly_dvol.parquet`.
- Benchmark: `yfinance/_GSPC.csv` (S&P 500), month-end, total price return (dividends excluded for
  both stocks and benchmark — symmetric, so Sharpe comparison is fair; absolute returns are a touch
  understated for all).
- **Dynamic liquid universe:** each rebalance month, eligible names = those with a valid 12-1 signal
  and a live price, then **top 500 by trailing monthly dollar volume**. Average realised universe
  ≈ 451 names; deciles average ≈ 45 names each. Backtest starts 1973-08 (first month with ≥50
  eligible names) and ends 2024-11 (the stock cache ends Nov-2024).

### Signal (causal 12-1)
- At end of month *m*: `mom = close[m-1] / close[m-13] − 1` — the trailing 12-month return that
  **skips the most recent month** (avoids 1-month reversal). Uses only data through *m−1*.
- Rank eligible names cross-sectionally; split into deciles.
- **Hold month *m+1*** (forward return realised over the next month). Month *m* itself is the skip
  month. No look-ahead in either the signal window or the ranking.

### Portfolios, costs, turnover
- **Long-only:** top decile (highest momentum), equal-weight, monthly rebalance.
- **Long-short:** +top decile / −bottom decile, equal-weight, 100% gross each side.
- **Costs:** round-trip transaction cost charged on traded notional each month (one-way turnover
  computed against drift-adjusted prior weights). Base case **15 bps round-trip**; sensitivity at
  10 and 20 bps. Realised one-way turnover ≈ 395%/yr (long) and 415%/yr (long-short).
- **Metrics:** annualised geometric return, vol, Sharpe & Sortino (rf = 0, applied to both strategy
  and benchmark), max drawdown, Calmar, and the long-short spread's Newey-naïve t-stat.

### Honesty caveats (these inflate the momentum numbers)
1. **Survivorship bias — the big one.** The cache holds *current* tickers only; delisted/bankrupt
   names are absent. Momentum's worst realisations (winners that later imploded; shorts that went to
   zero are missing from the long side's competition) are systematically pruned. Published live
   momentum is weaker than back-tests on current-constituent data. **Read every momentum number
   below as optimistic.**
2. **Delisting return handling:** a name with no next-month price is dropped from that month's
   realised return (survivor-take). Mildly favourable to the long side.
3. **No dividends, no borrow cost / hard-to-borrow constraints on the short leg, no market-impact
   beyond the flat bps** (small/mid winners have real impact; 15 bps is generous for a 45-name
   equal-weight decile that tilts small).

---

## Results — Cross-sectional momentum

### Full sample (1973-08 → 2024-11, 616 months)

| Portfolio | Ann.Ret | Sharpe | Sortino | maxDD | Calmar | Vol |
|---|---|---|---|---|---|---|
| Momentum long-only, GROSS | 20.4% | 0.75 | 1.24 | −66.3% | 0.31 | 30.9% |
| Momentum long-only, **NET 15bps** | **19.7%** | **0.73** | 1.20 | −67.0% | 0.29 | 30.9% |
| Momentum long-short, GROSS | 8.8% | 0.45 | 0.56 | −92.1% | 0.10 | 28.1% |
| Momentum long-short, **NET 15bps** | **8.1%** | **0.42** | 0.53 | −92.6% | 0.09 | 28.1% |
| **SPX buy & hold** | 8.2% | **0.59** | 0.82 | −52.6% | 0.16 | 15.4% |

- **Long-short spread:** monthly mean 0.99% net, **t = 3.0** (gross 1.04%, t = 3.2). The momentum
  premium is statistically real over the full half-century — exactly as the literature says.
- **Costs are not what kills it.** Turnover is high (~400%/yr one-way) but at these bps the drag is
  ~0.5–0.9%/yr; Sharpe barely moves across 10/15/20 bps. The problems are (a) era-decay and (b) tail risk.
- **Tail risk is brutal:** long-only −67% drawdown, long-short −92% (the 2009 momentum crash). The
  long-only Sharpe edge over SPX (+0.14) comes with 2× the volatility and a far uglier drawdown.

### Cost sensitivity (net Sharpe / ann.ret)

| Round-trip | Long-only | Long-short |
|---|---|---|
| 10 bps | 0.74 / 20.0% | 0.43 / 8.3% |
| 15 bps | 0.73 / 19.7% | 0.42 / 8.1% |
| 20 bps | 0.72 / 19.5% | 0.42 / 7.9% |

### Sub-period stability (NET 15 bps vs SPX) — where it fails

| Period | Long Sharpe | Long Ret | LS Sharpe | LS Ret | SPX Sharpe | SPX Ret |
|---|---|---|---|---|---|---|
| 1970s | 0.75 | 31.6% | 0.87 | 25.0% | 0.08 | −0.0% |
| 1980s | 1.25 | 31.4% | 1.08 | 18.6% | 0.81 | 12.6% |
| 1990s | 1.37 | 37.2% | 0.87 | 17.7% | 1.14 | 15.3% |
| **2000s** | **0.07** | **−3.1%** | **−0.25** | **−18.7%** | −0.09 | −2.7% |
| 2010s | 0.65 | 12.0% | 0.37 | 5.7% | **0.92** | 11.2% |
| 2020s | 0.63 | 17.3% | 0.68 | 16.7% | 0.79 | 13.5% |
| **PRE-2000** | **1.06** | 33.6% | **0.91** | 19.8% | 0.72 | 10.4% |
| **POST-2000 (OOS)** | **0.36** | 6.6% | **0.08** | −3.0% | **0.45** | 5.8% |
| **POST-2010 (OOS)** | **0.62** | 13.7% | **0.49** | 9.2% | **0.85** | 12.0% |

**The verdict is written in this table.** Momentum dominated SPX in the 1970s–1990s (long Sharpe
1.06 vs 0.72 pre-2000; LS Sharpe 0.91). Then it broke:
- **2000s:** long-only −3.1% (Sharpe 0.07); long-short −18.7% (the great momentum crash). 
- **Post-2000 (the genuine out-of-sample era):** long-only Sharpe **0.36 < SPX 0.45** — it *loses*.
  Long-short Sharpe **0.08** with a *negative* return — the premium has decayed to noise.
- **Post-2010:** long-only **0.62 < SPX 0.85** — loses again, and SPX has a third the volatility.

This is the textbook "momentum is real but decayed and crash-prone" result, and the decay is
*before* you account for the survivorship inflation baked into the cache.

---

## Results — Risk parity vs 60/40 (stretch)

- Assets: SPX (`_GSPC`), 7–10y Treasuries (`IEF`), gold (`GC=F`), commodities (`USO`). Common
  history forces a **2006-05 → 2026-06 (242 months)** window — itself only a post-2000 sample.
- Risk parity = **inverse-vol** weights (trailing 63-day annualised vol, lagged one month so it is
  causal), long-only, fully invested, **no leverage**, monthly rebalance, 15 bps costs.
- 60/40 = 60% SPX / 40% IEF, no rebalance cost modelled (drift).

| Portfolio | Ann.Ret | Sharpe | Sortino | maxDD | Calmar | Vol |
|---|---|---|---|---|---|---|
| Risk-parity (inv-vol) NET | 5.6% | **0.81** | 1.12 | −14.0% | 0.40 | 7.1% |
| Equal-weight 4-asset NET | 5.2% | 0.48 | 0.63 | −35.2% | 0.15 | 12.1% |
| 60/40 SPX/Bonds NET | 7.1% | 0.78 | 1.03 | −30.9% | 0.23 | 9.4% |
| SPX buy & hold | 8.9% | 0.64 | 0.86 | −52.6% | 0.17 | 15.3% |

Sub-periods:

| Period | RP Sharpe | 60/40 Sharpe | SPX Sharpe |
|---|---|---|---|
| Full 2006–26 | **0.81** | 0.78 | 0.64 |
| Post-2010 | 0.83 | **0.97** | 0.87 |
| Post-2015 | 0.81 | 0.82 | 0.81 |
| Post-2020 | **0.86** | 0.75 | 0.82 |

**Verdict: risk parity is not a robust winner.** Unlevered inverse-vol edges 60/40 on full-sample
Sharpe (0.81 vs 0.78) and crushes it on drawdown (−14% vs −31%) — but the edge is driven by the
2006–2011 bond tailwind and **reverses post-2010 (0.83 < 0.97)**. It also surrenders ~1.5%/yr to
60/40 and ~3.3%/yr to SPX in absolute return. The classic "RP beats 60/40" claim only works *with
leverage* to lift its return to equity-like levels — and leverage means financing cost (not
modelled, ~SOFR + spread) plus the 2022 bond/equity-correlated drawdown that hammered levered RP in
reality. As an unlevered passive sleeve it is a fine low-vol diversifier, not a benchmark-beater.

---

## Honest call on deployability

- **Cross-sectional 12-1 momentum: DO NOT deploy as an SPX-beating strategy.** It is a genuine,
  statistically significant factor over 50 years (LS t = 3.0), but: (1) its risk-adjusted edge over
  SPX is **entirely pre-2000**; (2) **post-2000 and post-2010 it loses to SPX on Sharpe**; (3) the
  long-short premium decayed to ~zero post-2000; (4) it carries 2× equity vol and −67%/−92%
  drawdowns; and (5) every number is **optimistically biased by survivorship** in the current-
  constituent cache, so the true live edge is weaker still. Costs (10–20 bps) are *not* the binding
  constraint — decay and tail risk are.
- **Risk parity: DO NOT deploy as a 60/40-beater.** The Sharpe edge is marginal and not robust out
  of sample; unlevered it underperforms on return, levered it inherits financing cost and 2022-style
  crash risk that this study cannot model on the available proxies.
- **No deployable spec is recommended for the Lab.** If momentum is added at all, it should be
  framed honestly as an *educational* factor demo (the decay/crash story is the lesson), not as a
  live alpha — and any live version must be re-validated on a survivorship-bias-free, delisting-
  return-inclusive dataset (e.g. CRSP), which this cache is not.

## Reproducibility
- Panels: `scratchpad/build_panel.py` → `data/market_history/monthly_close.parquet`, `monthly_dvol.parquet`
- Momentum backtest: `scratchpad/momentum.py` → `data/market_history/mom_returns.csv`
- Risk parity: `scratchpad/riskparity.py`
- Window: stocks 1973-08→2024-11 (cache end); risk-parity 2006-05→2026-06.
