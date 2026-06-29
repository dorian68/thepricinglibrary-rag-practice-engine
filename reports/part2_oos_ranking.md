# Part 2 — Honest Out-of-Sample (OOS) Strategy Ranking

**Engine:** `C:\Users\Labry\documents\TRADING\trading_engine` (event-driven backtester; costs = spread, slippage, commission, swap, gap-aware fills).
**Method:** `src/research/walk_forward_optimizer.py` — chronological split **train 50% / validation 25% / test 25%**. Params are picked on the **validation** window; **every number in the ranking is from the untouched TEST window** (true OOS). The **Deflated Sharpe Ratio (dSR)** corrects for the number of grid trials (Bailey–López de Prado): it is a probability in [0,1] that the true Sharpe beats the best Sharpe luck alone would produce across N trials. It is the anti-overfit guard and the primary ranking key.
**Grid:** `max_grid = 8` candidates per (strategy × instrument), random-sampled from the full grid with fixed seed.
**Risk profile:** `capital_ladder` (as specified). **Data:** native 15-min CSVs, ~54k bars FX/Gold (~2 yr), ~71k bars crypto. Test window ≈ last ~13.5k–17.8k bars (~6 months).
**Run date:** 2026-06-29. All 18 combos completed; none timed out.

## 1. Engine verification (working command)

From the backend env (`Tools/pricinglibrary_rag_backend`), the wrapped engine runs:

```bash
cd Tools/pricinglibrary_rag_backend && python scripts/smoke_integrations.py   # includes a strategylab EURUSD backtest
```

Direct engine backtest (confirmed metrics + trades + equity returned):

```bash
cd TRADING/trading_engine
PYTHONPATH="src" python tpl_runner.py '{"action":"backtest","instrument":"EURUSD","source":"native","max_bars":20000,"capital":5000}'
# -> keys: metrics, equity (223 pts), trades, n_trades=21, rejected  ✓
```

OOS walk-forward per combo (the path actually used for this report):

```bash
cd TRADING/trading_engine
PYTHONPATH="src" python src/main.py walk-forward --symbol XAUUSD --strategy trend --risk-profile capital_ladder --max-grid 8
# prints decision/reason/selected_params; full TEST metrics written to reports/walk_forward/<SYM>_<strat>_walk_forward.csv
```

(For this report a driver called `optimize_walk_forward` directly for all 18 combos and re-ran the **selected** params on the TEST split to recover the full OOS metric set incl. raw Sharpe.)

## 2. Honest OOS ranking (sorted by Deflated Sharpe)

| # | Strategy | Instrument | OOS ret % | OOS Sharpe | **dSR** | Max DD % | PF | Trades | Train % | Val % | Verdict |
|---|----------|-----------|----------:|-----------:|--------:|---------:|----:|-------:|--------:|------:|---------|
| 1 | trend_following | **XAUUSD** | **+4.74** | 2.46 | **0.68** | 1.42 | 2.31 | 17 | +0.55 | **−6.70** | EDGE? (only dSR>0.5; but losing val + thin sample) |
| 2 | volatility_breakout | GBPUSD | +0.59 | 0.81 | 0.46 | 0.82 | 2.08 | 3 | −1.35 | +0.58 | INSUFFICIENT (3 trades) |
| 3 | volatility_breakout | EURUSD | +0.13 | 0.18 | 0.31 | 0.62 | 1.21 | 2 | +1.04 | +0.71 | INSUFFICIENT (2 trades) |
| 4 | mean_reversion | EURUSD | +0.80 | 0.53 | 0.21 | 1.36 | 1.33 | 8 | +1.15 | −0.46 | NEGATIVE (dSR<0.5) |
| 5 | mean_reversion | GBPUSD | −0.52 | −0.22 | 0.18 | 2.65 | 0.92 | 19 | −1.97 | −3.91 | NEGATIVE |
| 6 | trend_following | EURUSD | +2.88 | 0.78 | 0.09 | 3.78 | 1.16 | 59 | −17.70 | +0.48 | OVERFIT/weak (dSR fails; train −17.7%) |
| 7 | trend_following | BTCUSD | −0.50 | −1.17 | 0.06 | 0.67 | 0.00 | 1 | −1.59 | +1.49 | NO CONCLUSION (1 trade) |
| 8 | trend_following | GBPUSD | −1.13 | −0.45 | 0.01 | 4.93 | 0.91 | 39 | −7.98 | +2.47 | NEGATIVE |
| 9 | mean_reversion | ETHUSD | −0.52 | −1.17 | 0.01 | 0.55 | 0.00 | 1 | +0.56 | −0.52 | NO CONCLUSION (1 trade) |
| 10 | trend_following | ETHUSD | −0.52 | −1.17 | 0.00 | 0.52 | 0.00 | 1 | −0.57 | +0.53 | NO CONCLUSION (1 trade) |
| 11 | mean_reversion | BTCUSD | −0.54 | −1.17 | 0.00 | 0.54 | 0.00 | 1 | −0.43 | +0.61 | NO CONCLUSION (1 trade) |
| 12 | volatility_breakout | XAUUSD | −1.29 | −2.52 | 0.00 | 1.29 | 0.00 | 3 | −1.19 | +0.63 | NEGATIVE |
| 13 | mean_reversion | XAUUSD | −1.30 | −1.66 | 0.00 | 1.30 | 0.00 | 3 | −0.05 | −0.33 | NEGATIVE |
| 14 | volatility_breakout | BTCUSD | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0 | 0.00 | +0.57 | NO TRADES |
| 15 | volatility_breakout | ETHUSD | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0 | +0.58 | 0.00 | NO TRADES |
| 16 | trend_following | USDJPY | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0 | 0.00 | 0.00 | NO TRADES (margin reject) |
| 17 | volatility_breakout | USDJPY | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0 | 0.00 | 0.00 | NO TRADES (margin reject) |
| 18 | mean_reversion | USDJPY | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0 | 0.00 | 0.00 | NO TRADES (margin reject) |

Verdict rule used: **GENUINE EDGE** = dSR > ~0.5 AND positive OOS return AND enough trades; **OVERFIT** = good in-sample/train but poor OOS or failing dSR; **NEGATIVE** = negative OOS; **NO CONCLUSION / NO TRADES** = sample too small to judge.

## 3. Single best OOS config

**trend_following on XAUUSD (Gold), 15-min, capital_ladder**
Params: `fast_ema=10, slow_ema=100, atr_stop_mult=3.0, trailing_stop=True`
Real TEST-set metrics: **return +4.74%, Sharpe 2.46, Sortino ≈ 2.5, Deflated Sharpe 0.68, max DD 1.42%, profit factor 2.31, 17 trades, expectancy positive.** Decision flag from engine: `needs_more_data`.

It is the **only** config whose deflated Sharpe clears ~0.5, and it is positive net of all modelled costs. **But it does not qualify as deployable**, for two honest reasons:
1. Its **validation window lost −6.70%** while train was ~flat (+0.55%) — the params were *not* validated; the good OOS number followed a bad validation, which is more consistent with luck/regime than with stable edge.
2. **17 trades over ~6 months** is far too thin a sample to trust a Sharpe of 2.46; the engine itself tags it `needs_more_data`.

## 4. STRETCH — did ML (meta-labeling / LSTM) help?

**Not evaluated as OOS — and that is the honest answer.** The `--use-meta-labeling` / `--use-lstm` flags exist on the CLI but are **wired into the in-sample research suite** (`research/model_selection.py` → `run_research_suite`, which runs each variant as a single full-history `BacktestEngine` pass), **not into `optimize_walk_forward`** (the train/val/test + deflated-Sharpe path). Running the ML variants there would produce **in-sample, look-ahead-prone numbers** that are not comparable to the OOS test figures above, and the meta-classifier would train on data overlapping the evaluation window. Reporting those as "OOS" would violate the integrity mandate, so they are deliberately omitted. A proper answer requires wiring the meta/LSTM filter into the walk-forward split (fit on train+val, score on test) — a code change, not a run.

## 5. Honest caveats

- **USDJPY = engine artifact, not a strategy result.** All 3 USDJPY combos and several crypto combos produced 0–1 trades. A full-history diagnostic on USDJPY generated **26,652 orders but filled 0** — rejections dominated by `insufficient_margin` (7,547) under the small `capital_ladder` capital at JPY's ~152 price scale (plus `reward_risk_too_low`). So USDJPY/low-trade crypto rows reflect **position-sizing/margin config under capital_ladder**, not strategy edge. Re-running with a larger-capital profile (e.g. `institutional`/`balanced`) is needed before any USDJPY/crypto conclusion.
- **Small samples everywhere.** Most non-trend configs fire 0–19 OOS trades; volatility_breakout/mean_reversion essentially have no statistical mass on the test window. Sharpe/PF on <10 trades are noise.
- **Costs are included** (spread, slippage, commission, swap, gap fills) — the positive numbers are net, which is the right way to read them. They are still tiny.
- **Data depth ~2 years of 15-min bars** (more than the feared 6–12 mo), but one ~6-month OOS window per instrument is a single regime draw; no cross-validation across multiple OOS folds was done.
- **Grid is modest (8 trials).** A wider grid would raise the deflation benchmark and likely lower dSR further — i.e. results would get *more* skeptical, not less.

## 6. Bottom line / deployable edge?

**No strategy shows a robust, deployable OOS edge on this data.** Out of 18 (strategy × instrument) tests, exactly one — **trend_following on Gold** — beat the deflated-Sharpe overfit guard with a positive net OOS return, and even that rests on **17 trades and a losing validation window**, so it is a *lead to investigate*, not a signal to trade. Everything else is either negative, statistically empty (≤3 trades), or a margin-rejection artifact (USDJPY). Trend-following on trending instruments (Gold, and EURUSD which was +2.88% OOS but failed dSR with a −17.7% train) is the only theme worth more research — with more data, multi-fold OOS, larger capital sizing, and ML properly wired into the walk-forward split. Honest call: **would not survive live in current form.**
