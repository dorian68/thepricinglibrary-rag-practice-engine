# Validation Core — Status (STEPS 1–3 of `quant_dev_design.md`)

Status: **BUILT + TESTED**. Foundational anti-p-hacking machinery only; no full
pipeline run, no lockbox holdout consumed, no `walk_forward_optimizer` behaviour
changed yet. Engine: `C:\Users\Labry\documents\TRADING\trading_engine`.

## What was built

All new modules are pure pandas/numpy (no engine/sklearn/torch import on the path),
so they unit-test fully offline and cannot break existing backtests.

| File | Provides | Design ref |
|------|----------|-----------|
| `src/research/cpcv.py` | `label_endtimes` (bridge off `triple_barrier.touched_at`), `purged_kfold`, `cpcv` (returns splits **and** the reconstructed OOS path matrix), `concurrency` / `average_uniqueness` / `time_decay_weights` sample weights, plus a re-exported `purged_train_indices` single-split primitive | §1.1–1.4, G3 |
| `src/research/trial_ledger.py` | append-only program-wide `TrialLedger` (persisted to `reports/trial_ledger.jsonl`): `record_trial`, `trial_count(scope)`, `sharpes`, `total`; plus `deflated_sharpe(sr, n_trials, …)` and `harvey_liu_haircut(…)` deflators that read off the true `N` | §4.1, §4.3, G4 |
| `src/research/pbo.py` | `pbo_cscv(perf_matrix)` — Probability of Backtest Overfitting via Combinatorially-Symmetric CV (Bailey/Borwein/LdP) | §4.2, G4 |
| `src/research/lockbox.py` | single-use `Lockbox` manifest (`reports/lockbox_manifest.json`): `register`, `evaluate` (raises `LockboxConsumedError` on a 2nd use), `status`, `is_consumed` | §4.4, G6 |
| `tests/test_validation_core.py` | 12 correctness tests (below) | §5 step 2 |

Reuse honoured per design: `purged_kfold`/`cpcv` purge logic generalises
`dl/sequence_filter.purged_train_indices`; `t1` comes from `ml/triple_barrier`
`touched_at`; the scalar DSR reuses `backtest/statistics.expected_max_sharpe` /
`_inverse_normal_cdf` / `_standard_normal_cdf`. `dl/sequence_filter` was **not**
edited (kept torch off the test path); it can later `import` the promoted primitive.

## Test results — `12 passed`

`python -m pytest tests/test_validation_core.py` → **12 passed in ~0.6s**.

Key correctness proofs (not just "it runs"):

- **Purging** removes a train event whose label horizon reaches into the test
  window (event 9, `touched_at` = bar 12, purged from test-fold 1) while a
  non-overlapping pre-test event survives.
- **Embargo** removes exactly the configured fraction after a test block
  (`embargo_pct=0.05` over 100 bars → events 20–24 dropped, train = 25–99).
- **CPCV counts**: `n_groups=6, n_test_groups=2` → **15 splits, paths shape (5,6)**,
  every cell filled, each group a test block in exactly 5 splits.
- **Leakage CAUGHT**: a 1-NN-in-time predictor on overlapping labels scores
  **0.80 accuracy unpurged** but **0.57 (≈ chance) under purged CV** — the
  framework structurally destroys the fake edge.
- **DSR** monotonically decreases with `n_trials` (0.99 → 0.38 → 0.03 → 6e-4 → 0
  for N = 1,5,20,100,1000); **Harvey-Liu haircut** Sharpe shrinks 1.20 → 1.01 →
  0.77 → 0.46.
- **PBO** averages ≈ 0.60 on random-noise configs vs ≈ 0.0 on a genuinely
  dominant config (averaged over 12 seeds; single-realisation PBO is noisy by
  construction, hence the seed-averaged assertion).
- **Lockbox** raises `LockboxConsumedError` on the 2nd evaluation (even with the
  same config hash) and the guarantee survives a manifest reopen.

## Existing backtests still import/run

- `import research.cpcv, research.pbo, research.trial_ledger, research.lockbox`
  alongside `backtest.engine`, `research.walk_forward_optimizer`,
  `dl.sequence_filter` → **all OK**.
- `tests/test_backtest_engine.py`, `tests/test_triple_barrier.py`,
  `tests/test_walk_forward_optimizer.py` → **pass** (the last runs a full grid of
  real backtests; it only needs `--basetemp=.pytest_tmp/...` because this
  machine's *global* pytest temp dir is permission-locked — unrelated to this work).

## How `walk_forward_optimizer` switches to `method="cpcv"` next (STEP 4)

The optimizer keeps its public signature; internally, behind a
`method="holdout"|"cpcv"` flag (holdout stays the default during migration):

1. Compute causal signals + `triple_barrier_labels` on full history (as today).
2. `t1 = label_endtimes(labels)`; `w = average_uniqueness(t1, df.index)`.
3. Replace the `train/validation/test = iloc[...]` block with
   `splits, paths = cpcv(t1, n_groups, n_test_groups, embargo_pct)`.
4. Per grid candidate, backtest restricted to each split's test events; reconstruct
   the `paths` OOS equity curves; select params by **median score across paths**.
5. Record every evaluated candidate to the shared `TrialLedger`; feed
   `deflated_sharpe`/`harvey_liu_haircut` the **program-wide** `trial_count`, and
   compute `pbo_cscv` from the per-(config, slice) performance grid.
6. Auto-fail verdict unless `dsr_median > 0.95` AND `pbo < 0.5` AND a single
   lockbox consume — making the honest null the default.

## Remaining for next iterations (STEPS 4–10)

4. `walk_forward_optimizer` CPCV switch (above). 5. ML sizing + `run_meta_labeled_cpcv`
(`proba_to_size`, in-fold calibration). 6. MDA feature importance on the same splits.
7. Nested per-fold regime mapping selection (`regime_selection` + `regime_router_cv`,
fixes the report-(4) trap). 8. Soft regime-feature meta-model vs hard switch on shared
CPCV. 9. DL contest on the same `cpcv` splits with the pre-registered acceptance gate.
10. Runner integration (`experiment_runner`/`model_selection` carry
`dsr_true_trials`, `pbo`, `cpcv_paths`, `lockbox_status`) + single-consume of the
final frozen config; regenerate the `part2_*` reports with the new columns.
