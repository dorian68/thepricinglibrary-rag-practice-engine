# The Correct Multi-Agent Quant Strategy-Development Pipeline

**Status:** architecture / methodology blueprint (drives implementation).
**Grounding:** López de Prado, *Advances in Financial Machine Learning* (AFML, 2018); Bailey & López de Prado, *The Deflated Sharpe Ratio* (2014) and *The Probability of Backtest Overfitting* (PBO, 2015); Harvey, Liu & Zhu, *…and the Cross-Section of Expected Returns* + Harvey & Liu, *Backtesting* (2015, the haircut / multiple-testing framework).
**Why this document exists:** four prior ad-hoc attempts failed *honestly* and their failure modes are the design constraints here. This pipeline exists to make those failure modes **structurally impossible**, not merely discouraged.

---

## 0. The failures this pipeline must structurally prevent

From the prior reports in this folder (read for grounding):

| # | Report | Methodological flaw demonstrated | Pipeline countermeasure (owner) |
|---|--------|----------------------------------|----------------------------------|
| 1 | `part2_oos_broad.md` | **Multiple comparisons across instruments** — 33 instruments × 3 strategies tested, the single best (trend/GOLD, DSR 0.959) reported; 0 survive Benjamini-Hochberg / Bonferroni. | Trial Registry + family-wise correction; *breadth* gate, not best-of (Validator). |
| 2 | `part2_portfolio_oos.md` | **ML applied as raw OOS overlay**, not as a meta-filter on a pre-justified primary signal; portfolio assembled from legs that individually lacked edge. | ML restricted to meta-labeling/sizing (ML Dev); combine only *independently-validated* uncorrelated edges (PM). |
| 3 | `part2_regime_switching_oos.md` | **Regime→strategy mapping fit on TRAIN and applied** — the mapping itself was never validated OOS; "train-fitted mapping" Sharpe 0.18 < SPX 0.49. | Regime mapping validated by **nested CV**; the map is a model, not a lookup (ML Dev + Validator). |
| 4 | `part2_momentum_research.md` | **Survivorship-biased universe** (current-constituent cache, delistings absent) inflating every momentum number; edge entirely pre-2000. | Point-in-time, delisting-inclusive universe is a hard gate (Data Engineer). |
| all | every report | **No held-out lockbox tested once** — the same TEST window (50/25/25) was reused across iterations 3 and 4; "OOS" decayed into a second validation set. | Single-use LOCKBOX, sealed, opened exactly once per strategy (Validator). |

The recurring honest verdict — *"nothing beats passive SPX risk-adjusted OOS after costs, robustly"* — is the **correct** result of honest testing. This pipeline is designed so that the **null result is the cheap default** and a positive result is expensive, pre-committed, and hard to fake.

---

## 1. THE AGENT ROLES

Each agent has **one** responsibility, typed **inputs/outputs**, and **one anti-p-hacking guard it owns and can VETO on**. Agents are stages in a DAG (§1.9); a VETO returns the artifact to the upstream agent or kills the idea. No agent may perform another agent's gate (separation of duties — the Validator never sees the data the Researcher fits on; the Researcher never touches the lockbox).

### 1.1 Quant Researcher — *the economic prior*
- **Single responsibility:** produce a falsifiable hypothesis with an **economic rationale** (a structural reason the edge should exist: risk premium, behavioral bias, market-microstructure friction, institutional constraint) and **pre-register the test** before any data is touched.
- **Inputs:** literature/RAG corpus, market intuition.
- **Outputs:** a signed **Pre-Registration Record** (`pre_reg.yaml`) — hypothesis statement, economic mechanism, the *exact* instrument universe, the *exact* signal definition, parameter ranges to be searched (with cardinality `N_trials`), the primary metric, the decision thresholds (copied from §2), and the predicted sign/magnitude of the effect.
- **Anti-p-hacking guard it OWNS — the Economic-Prior Gate:** *No backtest may run without an a-priori mechanism and a pre-registered spec.* "Try everything and see what sticks" is rejected at this gate. The universe and parameter grid are frozen here; widening them later is a new pre-registration (a new trial family).
- **VETO power:** can kill any downstream result whose realized test deviates from the registered spec (spec drift = p-hacking).

### 1.2 Data Engineer — *point-in-time integrity*
- **Single responsibility:** deliver a **point-in-time (PIT), survivorship-free, corporate-action-adjusted** dataset with a documented look-ahead audit.
- **Inputs:** raw vendor feeds; the registered universe.
- **Outputs:** an immutable, versioned dataset snapshot (hash-pinned) with: as-of timestamps on every field, **delisting returns included**, point-in-time index membership (no using today's S&P 500 to backtest 2005), corporate actions (splits/dividends) applied as-of, and a **look-ahead audit report** (no `center=True` rolling, no negative `.shift(-n)`, no future-resampled bars, no fields populated after their as-of time).
- **Anti-p-hacking guard it OWNS — the Data-Integrity Gate:** survivorship bias and look-ahead are *structural* false-positive generators (flaw #4). Universe membership must be reconstructed as-of; delisted/bankrupt names must be present with their terminal returns.
- **VETO power:** blocks any strategy built on a non-PIT or survivorship-biased universe (this would have killed `part2_momentum_research.md` at the gate).

### 1.3 Feature Engineer — *causal, stationary, leak-free features*
- **Single responsibility:** transform PIT data into **causal** features that are **stationary enough to be learnable** without destroying memory, and prove no leakage.
- **Inputs:** PIT dataset.
- **Outputs:** feature matrix where (a) every feature at time *t* uses only data ≤ *t* (trailing windows only); (b) price-like series are made stationary via **fractional differentiation** (AFML ch. 5 — minimum differencing order `d*` that passes ADF stationarity while retaining maximum memory; integer differencing of returns throws away predictive memory); (c) a leakage unit test asserting feature(*t*) is invariant to any data after *t*.
- **Anti-p-hacking guard it OWNS — the Leakage/Stationarity Gate:** features that are non-stationary produce spurious in-sample fit; features that peek produce fake OOS. Both are blocked here.
- **VETO power:** rejects any feature that fails the shift-invariance leakage test.

### 1.4 ML / Quant Dev — *meta-labeling, not signal-from-noise*
- **Single responsibility:** build the model **correctly** — ML sits **on top of** the Researcher's economically-motivated **primary signal** as a **meta-label** (trade / don't-trade + size), never as the primary alpha invented from features (flaw #2).
- **Inputs:** primary signal (from Researcher), causal features (from Feature Engineer), PIT labels.
- **Outputs:** a trained meta-model with: **triple-barrier labels** (AFML ch. 3); **purged k-fold or Combinatorial Purged CV (CPCV)** with an **embargo** (AFML ch. 7 — remove training observations whose label horizons overlap the test fold, plus an embargo band after each test fold); **sample-uniqueness weights** (AFML ch. 4 — down-weight overlapping/concurrent labels, sequential-bootstrap if bagging); **MDA feature importance** (mean-decrease-accuracy under the purged scheme, not impurity importance) with a feature-shuffling significance check; and the meta-model's **OOS hit-rate / precision** on held-back folds.
- **Anti-p-hacking guard it OWNS — the Validation-Scheme Gate:** standard k-fold leaks in finance (overlapping labels + serial correlation). The model is only valid if trained under purge+embargo+uniqueness weighting. Feature importance must be MDA under that scheme.
- **VETO power:** rejects any model trained with leaky CV or ML used as a primary signal.

### 1.5 Validator / Skeptic — *the adversary who owns the lockbox*
- **Single responsibility:** try to **kill** the strategy with the strongest available statistics, and guard the **single-use LOCKBOX**.
- **Inputs:** the candidate's full TRAIN+CV record, the Trial Registry (total trials across the whole program), the sealed lockbox.
- **Outputs:** a verdict with: **Deflated Sharpe Ratio** (DSR — PSR against the *expected maximum* Sharpe of `N_trials`, Bailey-LdP); **PBO** (probability of backtest overfitting via combinatorially-symmetric CV — the rank-degradation probability that the IS-best config is below-median OOS); **multiple-testing correction** across the *entire research program* (Harvey-Liu haircut Sharpe / family-wise `N_trials` from the Registry, not just the local grid); and **one** lockbox read.
- **Anti-p-hacking guard it OWNS — the Lockbox + Deflation Gate:** the lockbox is opened **exactly once** per strategy, after all other gates pass. A second peek voids the strategy permanently (a re-tested lockbox is just another validation set — flaw #5). DSR/PBO use the program-wide trial count.
- **VETO power:** absolute. The Validator is the only agent that can promote a strategy past research, and the only one allowed to touch the lockbox.

### 1.6 Risk Manager — *survivability, regime-aware sizing*
- **Single responsibility:** convert a validated edge into a **survivable** position-sizing policy: volatility targeting, drawdown limits, regime-aware leverage, kill-switch.
- **Inputs:** validated strategy returns, regime state.
- **Outputs:** a sizing policy — target portfolio vol (e.g. 10% ann.), per-trade equity-risk cap, max-drawdown circuit-breaker, regime leverage multipliers (0 in crisis → 1 in trend), VaR/CVaR limits.
- **Anti-p-hacking guard it OWNS — the Survivability Gate:** sizing parameters are *risk* parameters, not *alpha* parameters; they must **not** be tuned to maximize backtest Sharpe (that re-introduces overfitting through the back door). Sizing is set by risk policy, fit on TRAIN only, never on the lockbox.
- **VETO power:** rejects any strategy whose drawdown/tail profile breaches risk policy regardless of Sharpe.

### 1.7 Portfolio Manager / Allocator — *combine UNCORRELATED edges*
- **Single responsibility:** allocate capital across **independently-validated, low-correlation** edges.
- **Inputs:** the set of strategies that each independently passed §1.5, their return streams.
- **Outputs:** allocation weights (risk-parity / edge-weighted), with a hard **max pairwise correlation** constraint and crisis-correlation stress (trend bets cluster in crises — the CTA caveat noted in `part2_portfolio_oos.md`).
- **Anti-p-hacking guard it OWNS — the Independence Gate:** stacking many *correlated* mediocre edges is not diversification and inflates aggregate Sharpe spuriously. Only edges that each cleared the lockbox individually and are <0.7 correlated may be combined.
- **VETO power:** rejects correlated or individually-unvalidated legs.

### 1.8 Execution / Cost Analyst — *capacity and turnover reality*
- **Single responsibility:** confirm the edge survives **realistic** transaction costs, slippage, market impact, and **capacity** at intended size.
- **Inputs:** strategy trade list, turnover, intended capital.
- **Outputs:** net-of-cost metrics with vol-scaled slippage, spread, commission, financing/swap, and a **capacity curve** (Sharpe vs deployed capital) and turnover budget.
- **Anti-p-hacking guard it OWNS — the Net-of-Cost / Capacity Gate:** gross edges that evaporate after realistic costs, or that only exist at sub-scale capital, are not deployable. (Note: `part2_momentum_research.md` showed costs were *not* the binding constraint there — decay was — so this gate must report *which* constraint binds.)
- **VETO power:** rejects strategies whose net edge or capacity is below deployment threshold.

### 1.9 The handoff DAG and veto topology

```
                       ┌─────────────────────────── Trial Registry (append-only) ───────────────────────────┐
                       │                                                                                      │
 (1) Quant Researcher ─► (2) Data Engineer ─► (3) Feature Engineer ─► (4) ML/Quant Dev ─► (5) Validator/Skeptic
   economic prior +        PIT, surv-free,       causal + frac-diff     meta-label +          DSR + PBO + Harvey-Liu
   pre-registration        no look-ahead         no leakage             purged CV/embargo     + LOCKBOX (once)
        │ VETO                  │ VETO                 │ VETO                 │ VETO                   │ VETO (absolute)
        ▼                                                                                              ▼
   [kill / revise] ◄───────────────────────── (return upstream on any veto) ──────────────────────  PASS
                                                                                                       │
                                            (6) Risk Manager ─► (7) Portfolio Manager ─► (8) Execution/Cost
                                              survivability        uncorrelated combine     net + capacity
                                                   │ VETO                │ VETO                  │ VETO
                                                                                                 ▼
                                                                                          PAPER → DEPLOY
```

- The DAG is **strictly ordered**: stage *k* cannot start until *k−1* signs off. No backtest before §1.1; no model before §1.2/§1.3; no statistics before §1.4; no sizing before §1.5 passes.
- **Two agents have absolute veto:** the **Data Engineer** (a non-PIT universe poisons everything downstream) and the **Validator** (the only promoter, the only lockbox key-holder).
- The **Trial Registry** is a side-channel every agent writes to and the Validator reads from — see §5.

---

## 2. THE STAGE-GATED WORKFLOW (idea → deployment)

Ordered gates, each with a **pass/fail criterion that kills weak ideas as early and cheaply as possible**. Default outcome at every gate is **FAIL** (the null is cheap). Thresholds below are starting values; they are themselves pre-registered per strategy and never relaxed after seeing results.

| # | Gate | Owner | Data it may touch | PASS criterion | On FAIL |
|---|------|-------|-------------------|----------------|---------|
| G0 | **Economic-rationale** | Researcher | none (literature) | Written mechanism + pre-registered spec (universe, signal, grid `N_trials`, thresholds) signed before data access. | Kill. No backtest. |
| G1 | **Data-integrity** | Data Engineer | raw → PIT snapshot | PIT membership reconstructed; delisting returns present; corporate actions as-of; look-ahead audit clean (no `center=True`, no `shift(-n)`). | Kill or fix data; cannot proceed. |
| G2 | **In-sample fit (TRAIN only)** | ML Dev | **TRAIN** slice only | Signal shows hypothesized sign with economically plausible magnitude on TRAIN. (Sanity, not success — a strong IS fit is *expected*, not evidence.) | Kill (mechanism not present even in-sample). |
| G3 | **Purged + embargoed CV** | ML Dev | TRAIN via purged k-fold/CPCV | CV Sharpe stable across folds (low dispersion); meta-model OOS precision > base rate; MDA importances significant for the economically-motivated features. | Kill (overfit / leakage / features uninformative). |
| G4 | **Deflated-Sharpe & PBO** | Validator | CV record + Registry | **DSR > 0.95** (against expected-max Sharpe of the **program-wide** `N_trials`); **PBO < 0.5** (LdP threshold; aim < 0.2); Harvey-Liu haircut Sharpe still > 0. | Kill (indistinguishable from luck given the search). |
| G5 | **Breadth / robustness** | Validator | CV record | If a universe strategy: edge survives **Benjamini-Hochberg FDR (q=0.05)** across instruments (not best-of-N); ≥ a pre-set fraction of the universe positive. If single-instrument: parameter-neighborhood robustness (no knife-edge), **≥ 30–50 trades**, best-trade concentration < 40%. | Kill (a lone survivor of multiple comparisons — exactly flaw #1). |
| G6 | **SINGLE-USE LOCKBOX** | Validator | **LOCKBOX (read once)** | OOS lockbox Sharpe **within ~0.5σ** (or a pre-registered tolerance, e.g. ≥ 70% of CV Sharpe retained); sign and magnitude match the registered prediction; net of costs. | Kill **permanently**. Lockbox is now burned for this strategy. |
| G7 | **Paper / forward test** | Risk + Execution | live forward data only | N months of *live forward* (never-seen) data: realized Sharpe consistent with lockbox; slippage matches model; no behavior breach. | Kill or recycle to research with a *new* lockbox. |
| G8 | **Size & deploy** | Risk + PM + Execution | live | Risk policy attached (vol target, DD kill-switch, regime sizing); correlation < 0.7 to existing book; capacity adequate at size; net edge > cost+financing. | Hold at paper. |

**Key numeric thresholds (pre-registered, fixed):**
- DSR > 0.95; PBO < 0.5 (target < 0.2); Harvey-Liu haircut Sharpe > 0 at program-wide `N_trials`.
- BH-FDR q = 0.05 across the universe; OR Bonferroni for the strict claim.
- OOS-vs-CV retention ≥ 70% of CV Sharpe (degradation > 30% ⇒ overfit).
- Min trades ≥ 30 (≥ 50 preferred); best-trade concentration < 40%; max-DD within risk policy.
- Max pairwise correlation to book < 0.7; portfolio vol target ~10% ann.
- Paper-test minimum: pre-registered window (e.g. 3–6 months) before any capital.

**Why this ordering kills cheaply:** G0–G3 cost almost nothing and reject most ideas on mechanism, data, or in-sample sanity. The expensive, *irreversible* gates (G4–G6, especially the lockbox) are reached only by ideas that already survived everything else. The lockbox is the last thing touched, exactly once.

---

## 3. HOW REGIME-SWITCHING FITS CORRECTLY

The trap in `part2_regime_switching_oos.md`: the regime→strategy map was **fit on TRAIN and applied**, and the "best meta variant" used a mapping that was effectively a lookup table optimized in-sample (it also silently added a 1-of-8 selection per regime — an *uncorrected* extra multiple-comparison, as the report's own caveat admits).

**Correct design:**
1. **Regime as a causal meta-state.** Keep the existing causal classifier: regime(*t*) from trailing trend-strength, vol-percentile, return z-score, EMA slope — all windows ≤ *t*, acted on at *t+1*. The report already verified this is leak-free; *keep that property*. Regime is a feature, not a label of the future.
2. **Per-regime sub-models trained with nested CV.** Each regime gets its own sub-model trained on the **TRAIN** data *within that regime*, validated with purged k-fold **inside** TRAIN. No regime sub-model ever sees CV/lockbox data.
3. **The regime→action mapping is itself a model that must be validated OOS.** This is the crux. The mapping {regime → strategy/leverage} is **not** a lookup chosen by TRAIN PnL and then applied — it is fit on an **inner** training fold and its performance is measured on the **outer** held-out fold (nested CV). The map's parameters (which strategy per regime, leverage per regime) are inner-fold choices; the outer fold judges the *whole routing policy*, never the components.
4. **Count the regime selection in `N_trials`.** Selecting 1-of-8 strategies in each of 5 regimes is `8^5` (or at minimum 8×5) implicit trials — these enter the Trial Registry and the DSR/Harvey-Liu deflation. The prior report's failure to do this is precisely why a 0.18-Sharpe map looked interesting.
5. **Economic-prior fallback, pre-registered.** Where a regime has too few train trades, fall back to the *economically*-motivated action (e.g. crisis → flat), declared in G0 — not to whatever maximized in-sample PnL.

Result: regime routing reshapes the *risk* profile (lower DD, fewer trades) and may pass only if the **routing policy itself** survives the lockbox after deflation — not because some in-sample lookup happened to fit.

---

## 4. HOW ML / DL FITS CORRECTLY

**Core rule (AFML): ML is a META-LABEL, not the primary alpha.** The Researcher's economically-justified primary signal decides *direction*; ML decides *whether to act and how big* (precision filter + sizing). Using ML to mine a signal from features is signal-from-noise (flaw #2) and is forbidden at the Validation-Scheme Gate.

**The correct ML recipe (all mandatory):**
1. **Primary signal first** — economically motivated, from G0. ML never replaces it.
2. **Triple-barrier labels** — label each primary-signal event by which barrier (profit/stop/time) it hits, volatility-scaled (AFML ch. 3).
3. **Meta-labeling** — a classifier predicts P(the primary signal's trade is correct); trade only when P > threshold; size ∝ P (AFML ch. 3.6).
4. **Purged k-fold / CPCV + embargo** — overlapping label horizons are purged from training folds; an embargo band follows each test fold (AFML ch. 7). No vanilla k-fold, ever.
5. **Sample-uniqueness weights** — concurrent/overlapping labels are down-weighted; sequential bootstrap if bagging (AFML ch. 4). Prevents the model from over-counting redundant samples.
6. **MDA feature importance** — mean-decrease-accuracy under the purged scheme; the economically-motivated features should rank as important and survive a shuffling significance test. If only exotic, unexplainable features matter, treat as overfit.

**When DL is justified vs overkill:**
- **Default to simple models** (logistic regression, random forest for the meta-label). They are interpretable, MDA-friendly, and rarely beaten on tabular financial data with few effective samples.
- **DL (LSTM/Transformer) is justified only when** (a) there is a genuine **sequential / path-dependent** structure the meta-features can't capture (microstructure order-flow, intrabar paths), AND (b) the **effective sample size** (uniqueness-weighted, not raw rows) is large enough to fit the parameter count without memorizing, AND (c) DL beats the simple model **on the purged CV folds**, not in-sample.
- **DL is overkill / forbidden when** the dataset is daily bars over a few thousand low-uniqueness samples (most of this codebase's universe) — there the parameter count dwarfs effective samples and DL just overfits with extra steps. DL must clear the *same* G4–G6 gates as everything else, with `N_trials` charged for the architecture search.

---

## 5. THE ANTI-P-HACKING CHARTER

Binding rules. Violating any one voids the strategy.

1. **Economic prior before any backtest.** No data is touched without a written mechanism and a signed pre-registration (G0). "Search and see" is banned.
2. **Pre-registration freezes the spec.** Universe, signal, parameter grid (`N_trials`), primary metric, and thresholds are fixed before results are seen. Any change is a *new* pre-registration and a *new* trial family.
3. **Track EVERY trial in an append-only Trial Registry.** Every parameter combination, every instrument, every regime selection, every architecture tried — across the *entire research program*, not just one run — is logged. The program-wide `N_trials` feeds the Deflated Sharpe and the Harvey-Liu haircut. (The prior reports deflated only within a single grid; cross-experiment trials went uncounted — this is the single biggest leak.)
4. **The lockbox is opened exactly once.** One strategy, one read, at G6. A second read permanently burns that lockbox; the strategy must be re-derived against a *fresh* held-out period. Reusing the test set across iterations (as iterations 3–4 did) is forbidden.
5. **No peeking / no leakage.** No `center=True` rolling, no `.shift(-n)`, no future-resampled bars, no fitting sizing/risk on the lockbox. Features are shift-invariant by unit test.
6. **Report all negatives.** Every strategy, including the dead ones, is published with full distribution (losers included), as the prior reports did. A folder of honest nulls is the expected output; survivorship in *reporting* is itself p-hacking.
7. **Separation of duties.** The agent that fits never validates; the Validator who holds the lockbox never fits. Risk/sizing parameters are never tuned for Sharpe.
8. **Breadth over best-of.** A claim requires surviving family-wise/FDR correction across the tested universe (G5), never "the best of 33."

---

## 6. MAPPING TO THIS CODEBASE (what exists, what's missing)

Legend: ✅ exists and usable · 🟡 partial / needs adaptation · ❌ missing (build it).

### 6.1 By role / gate

| Pipeline element | Existing code | Status |
|---|---|---|
| **Researcher / pre-registration** | — (the reports are written *post hoc*) | ❌ No `pre_reg.yaml` mechanism, no economic-prior gate. Build a pre-registration artifact + a runner that refuses to backtest without one. |
| **Trial Registry (program-wide)** | `research/experiment_runner.py` (`run_quant_search`) logs a single run's grid; `walk_forward_optimizer` feeds local grid `N_trials` to DSR | 🟡 Per-run trial counting exists; **no append-only cross-experiment registry**. Build one; have DSR/Harvey-Liu read the *cumulative* count. |
| **Data Engineer / PIT + survivorship** | `marketdata/{base,catalog,providers,aspirate}.py`, `marketdata.cache` (CSV/parquet); `data/data_quality.py` | 🟡/❌ 80+ symbol catalog, OHLCV normalization, multi-provider aspirate exist. **But the cache is NOT point-in-time and has NO survivorship/delisting handling** (aspirate overwrites with current history; `part2_momentum_research.md` confirms current-constituent bias). Build: as-of index membership, delisting returns, immutable hash-pinned snapshots, look-ahead audit script. |
| **Feature Engineer / causal features** | `data/feature_engineering.py::add_features` (trailing EMA/ATR/RSI/MACD/Donchian/BB/z-scores/vol-percentile) | ✅ causal features. ❌ **No fractional differentiation** — add `frac_diff` (fixed-width window, ADF-tuned `d*`) per AFML ch. 5. ❌ no automated shift-invariance leakage unit test (the audit in report #3 was manual). |
| **ML Dev / labels** | `ml/triple_barrier.py` (vol-scaled barriers, `touched_at` for embargo) | ✅ triple-barrier labeling present and embargo-aware. |
| **ML Dev / meta-labeling** | `ml/meta_labeling.py` (`MetaLabelConfig` w/ embargo_bars, `apply_probability_filter`), `research/meta_label_oos.py` (`run_meta_labeled_oos`: train-only fit, embargo gap, raw-vs-filtered comparison) | ✅ meta-labeling done correctly as a *filter on a primary signal* with an embargo. 🟡 Logistic/RF only. |
| **ML Dev / purged CV + uniqueness weights + MDA** | `ml/walk_forward.py` (`rolling_walk_forward_splits`), `walk_forward_optimizer.py` | 🟡/❌ Walk-forward rolling splits exist and `meta_label_oos` does an embargo gap, but there is **no purged k-fold / CPCV**, **no sample-uniqueness weighting / sequential bootstrap**, and **no MDA feature importance**. Build all three (AFML ch. 4 & 7). |
| **Validator / DSR + PSR** | `backtest/statistics.py` (`deflated_sharpe_ratio`, `probabilistic_sharpe_ratio`, `expected_max_sharpe`) | ✅ Bailey-LdP DSR/PSR implemented and already used in the reports. |
| **Validator / PBO** | — (reports approximate with BH/Bonferroni across instruments) | ❌ **No PBO (combinatorially-symmetric CV) function.** Build `pbo()` per Bailey et al. 2015. |
| **Validator / multiple-testing correction** | reports apply BH-FDR & Bonferroni manually in scratchpad | 🟡 Logic demonstrated but **not a reusable module** and **not program-wide** (only within one run's universe). Build a Harvey-Liu haircut + family-wise module reading the Trial Registry. |
| **Validator / LOCKBOX** | `walk_forward_optimizer.py` does 50/25/25 train/val/test | ❌ **No sealed single-use lockbox.** The TEST split was reused across report iterations (flaw #5). Build a lockbox abstraction: a sealed, hash-pinned date range, access-logged, single-read, that voids on second access. |
| **Risk Manager** | `risk/{position_sizing,drawdown_control,kill_switch,var_cvar,exposure,tradability,capital_ladder}.py` | ✅ Comprehensive: vol+regime-multiplied sizing, DD curve + behavior breach, kill-switch, VaR/CVaR, exposure book, tradability vs account size, capital ladder. Add explicit **vol-targeting** wrapper if not already (reports did it in scratchpad). |
| **Portfolio Manager / uncorrelated combine** | `portfolio/{correlation_filter,asset_selector,capital_allocator}.py` (max_corr 0.75, edge-score ranking, risk-budget allocation w/ 2% cap) | ✅ correlation gate + edge-weighted allocation exist. Tighten max_corr to <0.7 and add crisis-correlation stress. |
| **Execution / Cost** | `execution/slippage.py` (vol-scaled, adverse), `broker/broker_specs.py`, `broker/simulator.py` | ✅ spread/slippage/commission/swap modeled. ❌ **No capacity curve** (Sharpe-vs-capital) — build it. |
| **Robustness / diagnostics** | `research/{robustness_score,edge_diagnostics,ablation_study,no_trade_diagnostics,failure_analysis,model_selection}.py` | ✅ Rich G5-style robustness scoring, edge enrichment (CVaR, cost-drag, best-trade concentration), ablation, failure decisions, variant selection. Wire `robust_score`/`failure_analysis` thresholds to the G5 pass/fail. |
| **Paper / forward test** | `live/paper_runner.py`, `live/forward_shadow_runner.py` (`run` on top-N from research CSV, future window) | ✅ forward-shadow on held-out future data + paper signal generator exist → G7. |
| **DL (justified-only)** | `dl/models.py` (`LSTMTradeFilter`, `TransformerTradeFilter`), `model_selection.py` `DL_VARIANTS` | ✅ DL *as a trade filter* (the correct meta-label role) with variant comparison. Enforce the §4 "DL-justified" checklist + charge architecture search to the Registry. |
| **Regime (correct form)** | `strategies/regime_switching.py` (causal classifier, leverage by regime), `strategies/regime_router.py` (causal routing), `research/strategy_regime_analysis.py` | 🟡 Causal regime + router exist and are leak-free. ❌ **The regime→action mapping is config/train-fit, NOT validated by nested CV**, and the per-regime selection is **not charged to `N_trials`** (flaw #3). Build nested-CV validation of the routing policy + register the selection count. |
| **Agent infrastructure** | `pricinglibrary_rag/desk_agents.py` (`Agent` ABC + roles), `agui.py` (orchestration loop, step/token guardrails) | 🟡 A real agent framework exists, but the roles are **pricing-desk** roles (Sales/Structurer/Quant/Pricing/Trader/Risk/Report), not the **research-pipeline** roles of §1. Reuse the `Agent`/`Desk` abstraction and `agui` orchestration to instantiate the 8 pipeline agents + the DAG/veto topology. |

### 6.2 The gaps that block the full pipeline (build list, priority order)

1. **Point-in-time, survivorship-free dataset** (G1) — the single highest-leverage gap; without it every result is optimistically biased (proven in report #4). Add as-of membership, delisting returns, immutable snapshots.
2. **Single-use LOCKBOX** (G6) — the gap that turned prior "OOS" into a reused validation set. A sealed, access-logged, void-on-second-read held-out period.
3. **Program-wide Trial Registry + Harvey-Liu / family-wise correction** (§5, G4) — currently trials are counted per-run only; cross-experiment selection (instruments, regimes, architectures) is uncounted, which is the dominant hidden multiple-comparison.
4. **Purged k-fold / CPCV + sample-uniqueness weights + MDA** (G3) — present validation is rolling-WF + an embargo gap; the AFML purge/uniqueness/MDA machinery is missing.
5. **PBO function** (G4) — DSR exists, PBO does not.
6. **Nested-CV validation of the regime→action policy** (§3) — and charging regime selection to `N_trials`.
7. **Fractional differentiation** in feature engineering (G2/§4).
8. **Pre-registration artifact + economic-prior gate** (G0) and **capacity curve** (G8) — process/tooling glue.
9. **Instantiate the 8 research agents + DAG/veto** on the existing `desk_agents`/`agui` infra.

---

## 7. One-paragraph summary

Build the strategy as a **strictly-ordered DAG of eight single-responsibility agents** — Researcher (economic prior + pre-registration), Data Engineer (PIT + survivorship-free, absolute veto), Feature Engineer (causal + fractional differentiation, no leakage), ML/Quant Dev (meta-labeling on a primary signal, purged CV + embargo + uniqueness weights + MDA), Validator/Skeptic (DSR > 0.95, PBO < 0.5, program-wide Harvey-Liu correction, the single-use lockbox, absolute veto), Risk Manager (vol-target + DD kill-switch + regime sizing), Portfolio Manager (combine only <0.7-correlated independently-validated edges), and Execution/Cost (net-of-cost + capacity). Ideas flow through **nine gates** (G0 economic-rationale → G1 data-integrity → G2 train-only fit → G3 purged CV → G4 DSR+PBO → G5 breadth/FDR → G6 single-use lockbox → G7 paper → G8 size+deploy), each defaulting to FAIL so the null is cheap and a positive result is pre-committed and expensive to fake. Regime-switching is admitted only as a **nested-CV-validated routing policy** (not a train-fit lookup) with its selection charged to the trial count; DL is admitted only as a **meta-label filter** when sequential structure and effective sample size justify it. The trading_engine already supplies DSR, triple-barrier, embargoed meta-labeling, regime classification/routing, the full risk stack, correlation-filtered allocation, cost modeling, robustness scoring, and forward-shadow testing; the **missing pieces that block the pipeline are: a point-in-time survivorship-free dataset, a single-use lockbox, a program-wide trial registry with family-wise correction, purged-CV/uniqueness/MDA, a PBO function, nested-CV regime validation, fractional differentiation, and the pre-registration gate.**
```
```
