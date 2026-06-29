# Quant Dev Design — Regime-Switching + ML/DL Done Properly in the Backtester

Author: Quant Dev. Status: DESIGN ONLY (do not implement; an orchestrator sequences the build).
Scope: `C:\Users\Labry\documents\TRADING\trading_engine`. Output of this design only;
no code changed.

## 0. What went wrong before (grounded in the reports + code)

Three honest failures, each traceable to a concrete methodological hole that this
design fixes:

1. **`part2_oos_broad.md`** — classic strategies, single 50/25/25 split per
   instrument (`research/walk_forward_optimizer.optimize_walk_forward`,
   `research/experiment_runner._train_test_metrics`). One OOS path → high-variance
   verdict; DSR `n_trials` = only the per-instrument grid size, ignoring that the
   *universe of strategies/instruments/timeframes* is the real search.
2. **`part2_portfolio_oos.md`** — meta-labeling wired into OOS
   (`research/meta_label_oos.run_meta_labeled_oos`) but only as a **filter**
   (`ml/meta_labeling.apply_probability_filter` zeros `direction`); ML can only
   *remove* trades → pure loss-mitigation, never sizes up conviction. Single
   train/test split again.
3. **`part2_regime_switching_oos.md`** — the **report-(4) trap**: the
   `{regime→strategy}` mapping is fit on the *whole TRAIN slice* then applied to
   TEST (see `strategies/regime_router.py`, mapping passed frozen by caller). The
   1-of-8-per-regime selection is an extra multiple-comparison the across-instrument
   Benjamini-Hochberg never absorbs (admitted in that report's Caveats). Not nested.

Common root cause: **no leakage-free cross-validation core**. A single chronological
split (a) wastes data, (b) gives one noisy estimate, (c) cannot measure backtest
overfitting (PBO needs many train/test recombinations), and (d) makes the *true*
trial count invisible. Everything below is built on fixing that first.

### What is already correct and reusable (do NOT rebuild)

- **Causality of the regime label** — verified in code: `MarketRegimeClassifier`
  (`strategies/regime_switching.py`) reads only `trend_strength`,
  `vol_percentile_100`, `abs_return_z_100`, `ema_slope_20`, all trailing
  rolling/ewm of close/high/low (`data/feature_engineering.add_features`). No
  `center=True`, no negative `.shift(-n)`. Engine acts on `signals.iloc[i-1]`
  (`backtest/engine.py:63`) → one-bar execution lag. **Regime label needs no fix.**
- **Triple-barrier labels with `touched_at`** (`ml/triple_barrier.py`) — already
  emits the label-resolution timestamp per event. **This is exactly the `t1`
  (label endtime) the purging/embargo and uniqueness logic require.** Reuse as-is.
- **Purge+embargo primitive** — `dl/sequence_filter.purged_train_indices(...)`
  already drops train events whose `touched_at` overlaps `[test_start − embargo]`.
  Correct for a single split; **generalize it into the CV core** rather than
  duplicate it.
- **DSR / PSR / E[max SR]** — `backtest/statistics.{deflated_sharpe_ratio,
  probabilistic_sharpe_ratio,expected_max_sharpe}` are textbook Bailey & López de
  Prado. Keep; only fix *what `n_trials` is fed*.
- **Meta feature matrix** — `ml/meta_labeling.build_meta_feature_matrix` already
  one-hot-encodes `regime` and `strategy`. This is the seam for "regime as a
  feature of a meta-model".
- **FrozenSignalStrategy** (`research/meta_label_oos.py`) already carries a
  `risk_multiplier` column through to the engine — the sizing hook exists; today
  it is left at 1.0.

---

## 1. VALIDATION CORE — Purged K-Fold / CPCV with embargo + sample-uniqueness weights

New module: **`src/research/cpcv.py`**. This is the foundation; regime selection
and ML both consume it. Pure pandas/numpy, no engine dependency, unit-testable.

### 1.1 Label endtimes (`t1`) — the bridge from triple_barrier

```python
def label_endtimes(labels: pd.DataFrame) -> pd.Series:
    """t1 series: index = event start ts, value = touched_at ts.
    Built directly from ml.triple_barrier.triple_barrier_labels output."""
    return pd.to_datetime(labels["touched_at"]).reindex(labels.index)
```

`t1` is the spine of every leakage control: an event "occupies" the bar span
`[event_start, touched_at]`. Two events overlap iff their spans intersect.

### 1.2 Purged K-Fold

```python
@dataclass(frozen=True)
class PurgedSplit:
    train_idx: np.ndarray   # positional indices into the event list
    test_idx:  np.ndarray
    test_group: int         # which contiguous fold is the test block

def purged_kfold(t1: pd.Series, n_splits: int = 6,
                 embargo_pct: float = 0.01) -> list[PurgedSplit]:
    """López de Prado PurgedKFold. Test folds are CONTIGUOUS in time
    (never shuffled). For each fold:
      - PURGE: drop train events whose [start, t1] overlaps the test
        span [test_start, test_t1_max].
      - EMBARGO: additionally drop train events that start within
        embargo_pct * n_bars AFTER the test block ends (serial-correlation
        leakage into the immediate post-test future)."""
```

Implementation notes:
- Operates on the **event index** (active signals), not all bars — matches how
  `meta_label_oos` already selects `signals.direction != 0`.
- Purge predicate reuses the logic in `dl/sequence_filter.purged_train_indices`,
  promoted here as the canonical implementation; `sequence_filter` then imports it.
- Embargo length = `ceil(embargo_pct * len(bar_index))` bars, mapped through the
  bar index (not event index) so it is calendar-correct.

### 1.3 Combinatorial Purged CV (CPCV)

```python
def cpcv(t1: pd.Series, n_groups: int = 6, n_test_groups: int = 2,
         embargo_pct: float = 0.01
         ) -> tuple[list[PurgedSplit], np.ndarray]:
    """Combinatorial Purged CV (López de Prado, AFML ch. 12).
    Split the timeline into n_groups contiguous blocks; every split uses
    C(n_groups, n_test_groups) combinations as the test set, purge+embargo
    the rest as train. Returns:
      - splits: list of PurgedSplit (len = C(n_groups, n_test_groups))
      - paths:  (n_paths, n_groups) matrix telling which split supplies the
                OOS prediction for each (path, group) cell, where
                n_paths = C(n_groups, n_test_groups) * n_test_groups / n_groups.
    The paths let us reconstruct φ distinct full-length OOS equity curves
    instead of one — this is what feeds PBO and DSR dispersion in §4."""
```

For `n_groups=6, n_test_groups=2` → 15 splits → 5 reconstructed OOS paths.
This directly replaces the "one TEST window" of the prior reports with a
*distribution* of OOS outcomes.

### 1.4 Sample-uniqueness weights (López de Prado AFML ch. 4)

```python
def concurrency(t1: pd.Series, bar_index: pd.Index) -> pd.Series:
    """# of label spans live at each bar."""

def average_uniqueness(t1: pd.Series, bar_index: pd.Index) -> pd.Series:
    """Per-event mean of 1/concurrency over its [start, t1] span.
    Overlapping labels (the norm with max_holding_bars=20) are NOT iid;
    this down-weights redundant events so the classifier is not fooled
    into thinking it has 6000 independent samples when it has ~600."""

def time_decay_weights(avg_uniq: pd.Series, last_weight: float = 0.5) -> pd.Series:
    """Optional linear time-decay on top of uniqueness (recent>old)."""
```

These weights are passed as `sample_weight=` to sklearn `.fit()` and used to
weight per-fold scoring. (Optional `sequential_bootstrap` can come later; not on
the critical path.)

### 1.5 How it plugs into `walk_forward_optimizer`

`optimize_walk_forward` keeps its public signature but internally:
1. Compute causal signals + triple-barrier labels on full history (as today).
2. `t1 = label_endtimes(labels)`; `w = average_uniqueness(t1, df.index)`.
3. Replace the `train/validation/test = iloc[...]` block with
   `splits = cpcv(t1, n_groups, n_test_groups, embargo_pct)`.
4. For each grid candidate, run the variant backtest restricted to each split's
   test events; aggregate the reconstructed OOS paths.
5. Select params by **median score across CPCV paths** (robust to one lucky path),
   not by a single validation window.
6. Report DSR with the **true** trial count (§4) and PBO (§4) instead of the
   single-split DSR currently at lines 99–121.

A thin compatibility shim keeps the old 50/25/25 path available behind a
`method="holdout"|"cpcv"` flag so existing callers/scripts don't break during
migration.

---

## 2. REGIME-SWITCHING DONE RIGHT

### 2.1 Causality — already satisfied

No change needed (see §0). Add one *regression test* asserting the no-look-ahead
property mechanically so it can never silently regress:
`tests/test_regime_causality.py` — perturb bars `> t` and assert `regime[:t]`
unchanged.

### 2.2 Fix the report-(4) trap — nested, per-fold mapping selection

The mapping must be **chosen inside each CPCV train fold and evaluated on that
fold's purged test block**, never fit on all-train then applied to all-test.

New module: **`src/research/regime_selection.py`**.

```python
def select_regime_mapping(
    train_signals_by_strategy: dict[str, pd.DataFrame],  # frozen causal signals
    regime: pd.Series,            # causal regime label, restricted to TRAIN
    t1: pd.Series, weights: pd.Series,
    candidate_strategies: list[str],
    scorer: Callable,             # uniqueness-weighted per-regime objective
) -> dict[str, str]:
    """For each regime value, pick the sub-strategy whose TRAIN events in that
    regime maximize the weighted scorer (incl. a 'flat' option). Returns the
    {regime->strategy} mapping. Selection happens ONLY on train events of the
    current fold."""
```

Wiring into `RegimeRouterStrategy` (no API change to the strategy itself — it
already accepts `config["router"]`):

```python
# research/regime_router_cv.py  (new orchestration, not in strategies/)
for split in cpcv(t1, ...):
    train_regime = regime.iloc[split.train_idx-aligned]
    mapping = select_regime_mapping(..., train_regime, ...)   # per-fold!
    router = RegimeRouterStrategy({**cfg, "router": mapping})
    oos = backtest_on(router, test_events=split.test_idx)     # purged test
    record(oos, mapping, split)
# aggregate across reconstructed CPCV paths -> median OOS, PBO, DSR
```

Key correctness points:
- Each fold yields a *possibly different* mapping. Report the **distribution** of
  mappings across folds (stability is itself evidence; a mapping that flips every
  fold is overfit). Compare to the fixed `ECONOMIC_PRIOR` (zero-trial baseline).
- The 1-of-K-per-regime choice is a real search: it contributes
  `K_strategies ^ N_regimes` (effective, reduced by economic priors) to the trial
  ledger in §4. This is the multiple-comparison the old report could not absorb.

### 2.3 Regime as a *feature* vs a *hard switch* — test both, decide by CV

Two hypotheses, evaluated on the **same** CPCV splits so the comparison is fair:

- **Hard switch**: `RegimeRouterStrategy` with per-fold mapping (§2.2).
- **Soft / meta**: a single meta-model that receives the regime one-hot columns
  (already produced by `build_meta_feature_matrix`, lines 90–92) as features and
  outputs a per-event conviction → size (§3). No discrete routing.

Decision rule (pre-registered, no peeking): the soft meta-model supersedes the
hard switch only if its **median CPCV-path DSR is higher AND its PBO is lower**,
both with the regime-feature variant's trials counted. Otherwise keep the simpler
hard switch (or neither, if both fail — the honest outcome remains on the table).

---

## 3. ML/DL DONE RIGHT — meta-labeling that SIZES, on a purged CV

### 3.1 Principle

ML is **meta-labeling on top of an economically-motivated primary signal**
(López de Prado): the primary model (trend/MR/breakout sub-strategy, or the
regime router) decides *direction*; the meta-model decides *trade-or-not and how
big*. ML never invents a direction. This is already the architecture of
`meta_label_oos`; the two fixes are **CV** and **sizing**.

### 3.2 Extend `meta_label_oos.py` to purged CV (replace the single split)

Add `run_meta_labeled_cpcv(...)` alongside the existing `run_meta_labeled_oos`:

```python
def run_meta_labeled_cpcv(df, instrument, risk, broker, strategy_config,
                          strategy_name, selected_params, meta_config,
                          model_type="logistic",
                          n_groups=6, n_test_groups=2, embargo_pct=0.01):
    # 1. causal signals + triple_barrier labels (reuse existing code path)
    # 2. t1 = label_endtimes(labels); w = average_uniqueness(t1, df.index)
    # 3. for each cpcv split:
    #       Xtr, ytr, wtr = features/labels/weights on split.train_idx (PURGED)
    #       model.fit(Xtr, ytr, sample_weight=wtr)        # <-- weights
    #       proba[test_events] = model.predict_proba(...)[:,1]
    # 4. reconstruct phi OOS proba paths -> phi OOS backtests (raw vs sized)
    # 5. report median metrics, DSR(true trials), PBO across paths
```

This deletes the dependency on the lone `validation_end` cutoff (current
`meta_label_oos.py:131-169`) — the single biggest source of the iter-3 fragility.

### 3.3 Sizing, not just filtering

Today `apply_probability_filter` only sets `direction=0` below threshold. Add a
**sizing map** that writes `risk_multiplier` (FrozenSignalStrategy already passes
it to the engine, lines 82–83):

```python
def proba_to_size(proba, threshold=0.55, max_mult=2.0, mode="linear"):
    """Calibrated conviction -> position multiplier.
      below threshold -> 0 (no trade)
      above           -> scale in [0, max_mult], e.g.
                         linear: max_mult * (p - thr) / (1 - thr)
                         kelly : capped fractional-Kelly on calibrated edge."""
```

Requirements:
- **Probability calibration** (`sklearn.CalibratedClassifierCV`, isotonic) fit
  *inside the train fold only* so the threshold and Kelly fraction are meaningful.
- Per-trade risk stays bounded by existing `RiskConfig` caps — `risk_multiplier`
  scales within, never overrides, the risk engine.
- Report sized vs unsized vs filter-only so we can see whether conviction sizing
  (not just trade removal) is what adds value — the thing iter-3 could not do.

### 3.4 Feature importance via MDA (purged)

```python
# src/research/feature_importance.py
def mda_importance(estimator_factory, X, y, t1, weights, splits) -> pd.DataFrame:
    """Mean-Decrease-Accuracy: per purged split, score OOS; permute each
    feature's column and re-score; importance = drop in (weighted) score.
    Permutation respects sample weights; CV is the SAME cpcv splits."""
```

MDA (not MDI/Gini) because MDI is biased toward high-cardinality features and is
in-sample; MDA is OOS-faithful and works for any estimator (logistic, RF, DL).
Output drives feature pruning and is logged with every run.

### 3.5 DL gate (LSTM/Transformer in `src/dl`) — justified only if it BEATS tabular

`dl/sequence_filter.walk_forward_deep_probabilities` already exists and already
purges (`purged_train_indices`). Refit it onto the **same `cpcv` splits** for an
apples-to-apples contest. Acceptance criterion (pre-registered):

> Accept DL over the tabular meta-model **iff** DL's **median CPCV-path DSR
> exceeds the tabular model's by a margin that survives counting DL's
> hyperparameter search in the trial ledger, AND DL's PBO ≤ tabular PBO.**
> On daily bars with ~hundreds of unique (uniqueness-weighted) events, the prior
> is that DL will *not* clear this bar; that negative result is an acceptable,
> honest deliverable.

No DL is deployed on a "looks slightly better in-sample" basis.

---

## 4. ANTI-OVERFIT INSTRUMENTATION

### 4.1 True trial count — `TrialLedger`

New: **`src/research/trial_ledger.py`**. A small accumulator threaded through the
runner that increments for *every* configuration actually evaluated:
grid params × strategies × instruments × timeframes × regimes-per-mapping ×
thresholds × model types. `deflated_sharpe_ratio` is then called with
`n_trials = ledger.total()` instead of the per-instrument `len(candidates)` used
today (`walk_forward_optimizer.py:108`). This is the single most important honesty
fix: the old DSR understated the search by 1–3 orders of magnitude.

### 4.2 Probability of Backtest Overfitting (PBO) via CSCV

New: **`src/research/pbo.py`**.

```python
def pbo_cscv(perf_matrix: pd.DataFrame) -> dict:
    """Combinatorially-Symmetric CV (Bailey, Borwein, López de Prado, 2017).
    perf_matrix: rows = time slices, cols = candidate configs, values = a
    per-slice performance stat (e.g. non-annualized Sharpe).
    Split rows into S even slices; for every C(S, S/2) way of choosing the
    IS half, find the IS-best config and look up its OOS rank in the
    complementary half. PBO = P[ IS-best is below median OOS ] estimated
    from the logit of the OOS ranks.
    Returns {pbo, logits, oos_rank_of_is_best, perf_degradation}."""
```

Fed naturally by the CPCV machinery: the per-(config, slice) performance grid is
a by-product of §1.3. PBO > 0.5 ⇒ the selection procedure is overfit; the result
must be reported as such regardless of headline Sharpe.

### 4.3 Deflated Sharpe with dispersion

For every reported strategy, report DSR computed from each reconstructed CPCV
path and quote the **median and the worst path**, not a point estimate. A
strategy whose edge lives in one path is flagged.

### 4.4 Single-use lockbox

New: **`src/research/lockbox.py`** + a `lockbox_manifest.json`.

- The most recent N% of each instrument's history (e.g. final 10%) is **sealed**:
  excluded from CPCV, never touched during research/selection.
- The final, frozen, pre-registered configuration may be evaluated on the lockbox
  **exactly once**. `lockbox.evaluate(config_hash)` writes the config hash +
  timestamp + result to the manifest and **refuses** any second evaluation of a
  different config (raises). This kills the "tweak → re-test on holdout" loop that
  silently turns a holdout into a training set.
- Every report carries a `lockbox_status` field: `untouched` / `consumed(hash)`.

### 4.5 Runner integration

Refactor `research/experiment_runner.run_quant_search` and
`research/model_selection.run_research_suite` so every result row carries:
`dsr_true_trials`, `n_trials_ledger`, `pbo`, `cpcv_paths`, `dsr_median`,
`dsr_worst`, `lockbox_status`. Reports are auto-failed (verdict = "no deployable
edge") unless: `dsr_median > 0.95` AND `pbo < 0.5` AND `lockbox_status` confirms a
single consume. This makes the honest verdict the *default*.

---

## 5. IMPLEMENTATION PLAN (ordered, minimal-risk)

Legend: **[R]** reuses existing code, **[N]** new, effort S/M/L, risk Lo/Md/Hi.

| # | Step | Files | Effort | Risk | Notes |
|---|------|-------|--------|------|-------|
| 1 | **Validation core: `cpcv.py`** — `label_endtimes`, `purged_kfold`, `cpcv`, uniqueness weights. Promote `purged_train_indices` here. | [N] `src/research/cpcv.py`; [R] `dl/sequence_filter.purged_train_indices`, `ml/triple_barrier.touched_at` | M | Lo | Pure numpy/pandas, fully unit-testable offline. No engine coupling. Foundation for all else. |
| 2 | **Unit + leakage tests** for the core and a causality regression test. | [N] `tests/test_cpcv.py`, `tests/test_regime_causality.py` | S | Lo | Assert purge removes overlaps, embargo math, path reconstruction count = φ. |
| 3 | **PBO + TrialLedger + lockbox** (instrumentation, standalone). | [N] `src/research/pbo.py`, `trial_ledger.py`, `lockbox.py`; [R] `backtest/statistics.deflated_sharpe_ratio` | M | Lo | Independent of 1–2; can be built in parallel. |
| 4 | **Refactor `walk_forward_optimizer`** to `method="cpcv"` using step 1; keep `holdout` shim. Feed DSR from TrialLedger; emit PBO. | [R]+edit `research/walk_forward_optimizer.py` | M | Md | Behaviour change behind a flag → low blast radius. Re-run `part2_oos_broad` to confirm honest numbers reproduce. |
| 5 | **ML sizing + purged-CV meta**: `proba_to_size`, calibration, `run_meta_labeled_cpcv`. | [R]+edit `research/meta_label_oos.py`, `ml/meta_labeling.py` (`apply_probability_filter` gains a sizing sibling) | M | Md | FrozenSignalStrategy `risk_multiplier` hook already exists — low integration risk. |
| 6 | **MDA feature importance** on the same splits. | [N] `src/research/feature_importance.py` | S | Lo | Drives feature pruning; logged per run. |
| 7 | **Regime nested selection**: `regime_selection.select_regime_mapping` + `research/regime_router_cv.py` orchestration. | [N] both; [R] `strategies/regime_router.py` (unchanged API), `regime_switching.MarketRegimeClassifier` | M | Md | Fixes the report-(4) trap. Compare per-fold mapping vs `ECONOMIC_PRIOR` baseline. |
| 8 | **Soft regime-feature meta-model vs hard switch** comparison on shared CPCV. | [R] `build_meta_feature_matrix` regime dummies + step 5 | S | Lo | Pre-registered decision rule (§2.3). |
| 9 | **DL contest** on the same `cpcv` splits; apply the acceptance gate. | [R] `dl/sequence_filter.walk_forward_deep_probabilities` (swap rolling loop for `cpcv` splits) | M | Md | Expect negative result; that is acceptable. GPU optional. |
| 10 | **Runner integration + auto-honest verdict**; lockbox single-consume on the final frozen config; regenerate the three `part2_*` reports with DSR(true trials)/PBO/lockbox columns. | [R]+edit `research/experiment_runner.py`, `research/model_selection.py` | M | Md | The last step — only after 1–9 validated. |

### Reusable vs new — summary

- **Reuse unchanged**: `ml/triple_barrier` (`touched_at`=t1), `MarketRegimeClassifier`
  + `add_regime_features` (causal, verified), `backtest/statistics` DSR/PSR,
  `RegimeRouterStrategy` (config-driven mapping), `FrozenSignalStrategy`
  (`risk_multiplier` carrier), `build_meta_feature_matrix` (regime/strategy dummies).
- **Reuse + edit**: `walk_forward_optimizer` (CPCV behind a flag),
  `meta_label_oos` (CV + sizing), `meta_labeling.apply_probability_filter`
  (add sizing sibling), `dl/sequence_filter` (consume `cpcv` splits; export its
  purge primitive), `experiment_runner`/`model_selection` (report new columns).
- **New**: `research/cpcv.py`, `research/pbo.py`, `research/trial_ledger.py`,
  `research/lockbox.py`, `research/regime_selection.py`,
  `research/regime_router_cv.py`, `research/feature_importance.py`, two test files.

### Critical-path ordering rationale

Steps 1–2 unblock everything (the leakage-free CV core). Step 3 (instrumentation)
is parallelizable. Steps 4–9 each depend only on 1–3 and are independently
shippable/verifiable. Step 10 is integration and must come last so the
single-use lockbox is consumed exactly once, by the final frozen config.
