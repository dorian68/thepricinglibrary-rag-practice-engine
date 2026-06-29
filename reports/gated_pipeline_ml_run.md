# ML/DL-Augmented Gated Anti-P-Hacking Pipeline — Honest Verdict

**Strategy:** `trend_following` + meta-labeling (calibrated, conviction-sized) + nested `regime_router` + DL sequence-filter contest  
**Headline instrument:** GOLD  
**Universe:** 10 liquid instruments  
**Program-wide TRUE trial count (grown by ML/DL):** 420

## VERDICT

### NO DEPLOYABLE EDGE

Every ML/DL configuration searched was charged to the SAME trial ledger, so the program-wide N grew to **420** and the Deflated Sharpe benchmark rose accordingly — ML/DL can only TIGHTEN the deflation here, never loosen it. The verdict defaults to *no deployable edge* unless all three primary gates pass.

| Gate | Threshold | Value | Pass |
|---|---|---|---|
| Median-path Deflated Sharpe (TRUE N=420) | > 0.95 | 0.0000 | FAIL |
| PBO (CSCV) | < 0.5 | 0.7000 | FAIL |
| Lockbox Sharpe retention (single-use) | >= 70% | N/A (no CV edge) | FAIL |

- LOCKBOX consumed exactly once (status `consumed(e5a6cb8db432)`); CV Sharpe **+0.0031**, lockbox Sharpe **+0.1169**.

## STEP 5 — ML conviction SIZING (calibrated meta-labeling on purged CPCV)

Meta-classifier fit per CPCV fold on PURGED+EMBARGOED, sample-uniqueness-weighted train events; probabilities calibrated IN-FOLD; out-of-fold probas reconstructed and mapped to a bounded `risk_multiplier`. Per-split train/test overlap = **0** (0 ⇒ no look-ahead).

| Variant | median-path Sharpe | worst-path Sharpe |
|---|---|---|
| raw | +0.0719 | +0.0282 |
| filter | +0.0724 | +0.0282 |
| sized | +0.0424 | +0.0119 |
| kelly | +0.0000 | +0.0000 |

- Meta threshold = breakeven hit rate **0.333** (payoff-implied, pre-registered). Filter vs raw: **+0.0005**; conviction sizing vs raw: **-0.0296** median-path Sharpe (did NOT improve OOS).
- `kelly` mode degenerates to ~0 here: symmetric Kelly's breakeven is P=0.5, but the trend profit-barrier hit rate sits below 0.5, so Kelly zeroes almost every trade — the asymmetric edge is in payoff, not hit-rate, which Kelly-on-hit-rate cannot size.
- Meta-model PBO across {raw,filter,sized,kelly}: **0.000**; DSR at true N: **0.0084**.
- NOTE: the engine clamps the per-trade `risk_multiplier` to <= 1.0 (risk caps are never levered up), so conviction sizing acts as fractional DOWN-weighting within the base risk budget — it cannot manufacture edge from leverage.

## STEP 6 — MDA feature importance (same CPCV splits)

Mean-Decrease-Accuracy under the purged scheme (OOS-faithful; MDI/Gini avoided). Top features by weighted OOS accuracy drop:

| Feature | MDA mean | std | folds | flag |
|---|---|---|---|---|
| volume_zscore_50 | +0.0061 | 0.0084 | 15 |  |
| realized_vol_20 | +0.0005 | 0.0095 | 15 |  |
| trend_strength | +0.0005 | 0.0077 | 15 |  |
| regime_low_volatility | +0.0003 | 0.0019 | 15 |  |
| regime_range | +0.0003 | 0.0007 | 15 |  |
| strategy_trend_following | +0.0000 | 0.0000 | 15 |  |
| strategy_ensemble | +0.0000 | 0.0000 | 15 |  |
| regime_crisis | +0.0000 | 0.0000 | 15 |  |
| regime_high_volatility | +0.0000 | 0.0000 | 15 |  |
| regime_trend | -0.0003 | 0.0023 | 15 |  |

- Leakage flags: none (no feature dominates implausibly ⇒ no obvious leak).

## STEP 8 — soft regime-as-FEATURE vs hard regime switch

Pre-registered rule (no peeking): the soft meta-model (regime one-hot as a feature) supersedes the hard switch ONLY if its median-path DSR is higher AND its PBO is lower/equal, both on identical CPCV splits with all trials counted.

| Model | median-path Sharpe | PBO | DSR (true N) |
|---|---|---|---|
| hard switch (regime router) | -0.0206 | 0.800 | 0.0000 |
| soft regime-as-feature | +0.0400 | 0.000 | 0.0068 |

- **Decision:** soft SUPERSEDES the hard switch (pre-registered DSR+PBO rule).

## STEP 9 — DL sequence-filter contest

LSTM/Transformer refit fold-by-fold on the SAME CPCV splits; the architecture grid is charged to the ledger. Accept DL over tabular ONLY IF DL median-path DSR > tabular AND DL PBO <= tabular.

| Model | median sized Sharpe | PBO | DSR (true N) |
|---|---|---|---|
| tabular meta-model | +0.0424 | 0.000 | 0.0084 |
| DL ({'model_type': 'lstm', 'hidden_size': 16, 'num_layers': 1}) | +0.0699 | 0.800 | 0.0633 |

- **Decision:** DL REJECTED vs the tabular meta-model (pre-registered rule). Archs searched: [{'model_type': 'lstm', 'hidden_size': 16, 'num_layers': 1}, {'model_type': 'lstm', 'hidden_size': 32, 'num_layers': 1}, {'model_type': 'transformer', 'd_model': 16, 'nhead': 2, 'num_layers': 1}].

## STEP 4/G5 — breadth across the universe (CPCV, true-N deflation)

| Instrument | median-path Sharpe | worst-path Sharpe | PBO | DSR (true N) | events |
|---|---|---|---|---|---|
| GOLD | +0.003 | -0.029 | 0.700 | 0.0000 | 5824 |
| SPX | +0.006 | -0.020 | 0.050 | 0.0000 | 22257 |
| NDX | +0.023 | -0.002 | 0.250 | 0.0000 | 9229 |
| OIL | +0.018 | -0.012 | 0.100 | 0.0000 | 5831 |
| SILVER | -0.023 | -0.050 | 0.800 | 0.0000 | 5825 |
| COPPER | +0.001 | -0.032 | 0.150 | 0.0000 | 5828 |
| EURUSD | +0.013 | -0.008 | 0.100 | 0.0000 | 5263 |
| GBPUSD | +0.000 | -0.047 | 0.350 | 0.0000 | 5274 |
| USDJPY | +0.012 | -0.008 | 0.100 | 0.0000 | 6914 |
| BTCUSD | +0.060 | +0.016 | 0.300 | 0.0169 | 3864 |

- Positive median-path Sharpe: **90%**; BH-FDR (q=0.05) discoveries: **0/10**; Bonferroni: **0/10**.

## Charter compliance & honest conclusion

- **True trial count** grown to 420 by counting EVERY ML/DL config (meta folds×variants, soft regime-feature, DL arch×folds×variants) — deflation tightened.
- **No look-ahead**: meta features purged+embargoed per fold (train/test overlap 0); calibration fit in-fold only; regime labels causal.
- **Single-use lockbox** consumed exactly once on the frozen config; a second read raises.
- **Breadth over best-of**: judged by BH/Bonferroni across the universe.

**Honest conclusion:** ML conviction-sizing, the soft regime-as-feature meta-model, and the DL sequence filter were each implemented correctly and judged by the SAME anti-p-hacking gates. The design steps 1-10 are now complete. Whether any of them clears the gates is reported above on the numbers — the null result remains the cheap, expected default.
