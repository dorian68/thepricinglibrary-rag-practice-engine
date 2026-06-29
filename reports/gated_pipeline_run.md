# Gated Anti-P-Hacking Pipeline — Honest Verdict

**Strategy:** `trend_following` (+ nested `regime_router`)  
**Headline instrument:** GOLD  
**Universe:** 10 liquid instruments  
**Program-wide TRUE trial count (TrialLedger):** 195

## VERDICT

### NO DEPLOYABLE EDGE

The pipeline DEFAULTS to *no deployable edge* and only promotes a strategy if ALL three gates pass. This is the integrity-preserving design: a positive result is expensive and pre-committed; the null is the cheap default.

| Gate | Threshold | Value | Pass |
|---|---|---|---|
| Median-path Deflated Sharpe (at TRUE N=195) | > 0.95 | 0.0051 | FAIL |
| PBO (CSCV over CPCV perf matrix) | < 0.5 | 0.7000 | FAIL |
| Lockbox Sharpe retention (single-use) | >= 70% | N/A (no CV edge) | FAIL |

- CV (median-path) Sharpe of frozen config: **+0.0031**
- LOCKBOX Sharpe (consumed exactly once, status `consumed(e5a6cb8db432)`): **+0.1169**
- Lockbox retention gate is **vacuous here**: the CV Sharpe (+0.0031) is below the materiality floor (0.02), so there is no edge to retain. The raw ratio (3718%) is noise on a near-zero denominator and does NOT count as a pass.

## STEP 4 — trend_following across the universe (CPCV)

Every candidate evaluated across the CPCV out-of-sample blocks; EVERY trial recorded to the program-wide ledger. DSR re-deflated at the TRUE program-wide trial count.

| Instrument | median-path Sharpe | worst-path Sharpe | PBO | DSR (true N) | events | selected params |
|---|---|---|---|---|---|---|
| GOLD | +0.003 | -0.029 | 0.700 | 0.0051 | 5824 | `{"fast_ema": 20, "slow_ema": 100, "atr_stop_mult": 2.0, "trailing_stop": false}` |
| SPX | +0.006 | -0.020 | 0.050 | 0.0000 | 22257 | `{"fast_ema": 10, "slow_ema": 100, "atr_stop_mult": 2.5, "trailing_stop": false}` |
| NDX | +0.023 | -0.002 | 0.250 | 0.0172 | 9229 | `{"fast_ema": 20, "slow_ema": 50, "atr_stop_mult": 2.5, "trailing_stop": true}` |
| OIL | +0.018 | -0.012 | 0.100 | 0.0275 | 5831 | `{"fast_ema": 10, "slow_ema": 100, "atr_stop_mult": 3.0, "trailing_stop": true}` |
| SILVER | -0.023 | -0.050 | 0.800 | 0.0001 | 5825 | `{"fast_ema": 10, "slow_ema": 100, "atr_stop_mult": 2.5, "trailing_stop": false}` |
| COPPER | +0.001 | -0.032 | 0.150 | 0.0038 | 5828 | `{"fast_ema": 20, "slow_ema": 50, "atr_stop_mult": 3.0, "trailing_stop": false}` |
| EURUSD | +0.013 | -0.008 | 0.100 | 0.0208 | 5263 | `{"fast_ema": 20, "slow_ema": 50, "atr_stop_mult": 3.0, "trailing_stop": false}` |
| GBPUSD | +0.000 | -0.047 | 0.350 | 0.0052 | 5274 | `{"fast_ema": 20, "slow_ema": 50, "atr_stop_mult": 3.0, "trailing_stop": false}` |
| USDJPY | +0.012 | -0.008 | 0.100 | 0.0087 | 6914 | `{"fast_ema": 10, "slow_ema": 100, "atr_stop_mult": 3.0, "trailing_stop": true}` |
| BTCUSD | +0.060 | +0.016 | 0.300 | 0.4736 | 3864 | `{"fast_ema": 10, "slow_ema": 50, "atr_stop_mult": 2.5, "trailing_stop": false}` |

## STEP 5/G5 — breadth across instruments (multiple-comparison correction)

- Instruments with positive median-path Sharpe: **90%**
- Benjamini-Hochberg (q=0.05) discoveries across the universe: **0 / 10**
- Bonferroni discoveries: **0 / 10**

A lone high-Sharpe instrument that does not survive BH/Bonferroni correction across the tested universe is consistent with luck, not edge.

## STEP 7 — nested regime-router CV (report-(4) trap fixed)

The `{regime -> sub-strategy}` mapping is selected INSIDE each CPCV train fold and scored on that fold's PURGED test block (never fit on all-train then applied). Every per-regime selection is charged to the trial ledger.

- median-path Sharpe (per-fold routing): **-0.0206**
- economic-prior baseline (zero-trial) median Sharpe: **-0.0025**
- DSR at true N: **0.0001**, PBO: **0.8000**
- distinct mappings across folds: **9** (modal mapping recurs 27% of folds — a mapping that flips every fold is overfit)
- modal mapping: `{"crisis": "mean_reversion", "high_volatility": "flat", "low_volatility": "mean_reversion", "range": "mean_reversion", "trend": "trend_following"}`
- per-regime selections recorded to ledger: **75**

## Charter compliance

- **True trial count**: DSR/breadth use the program-wide ledger count (195), not the per-instrument grid size.
- **Single-use lockbox**: consumed exactly once on the frozen config (`consumed(e5a6cb8db432)`); a second evaluation raises and is structurally impossible.
- **No look-ahead**: CPCV purges train events whose label horizon overlaps a test block and embargoes the post-test band; regime labels are causal (trailing windows only).
- **Breadth over best-of**: the verdict is judged by BH/Bonferroni across the universe, not by the single best instrument.

## Caveats

- Daily OHLC, scale-free unit-CFD sizing; half-spread + vol-scaled slippage modelled; overnight financing not modelled; live circuit-breakers relaxed for edge measurement.
- This run wires STEPS 4/7/10. STEPS 5/6/8/9 (ML conviction-sizing + calibration, MDA feature importance, soft regime-feature meta-model, DL contest) remain for later and would only ADD trials to the ledger — tightening, never loosening, the deflation.
