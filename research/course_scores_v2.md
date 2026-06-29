# Independent panel re-score (round 2) — precise remaining fixes per course

Bar: PASS only if BOTH P1 ≥ 98 AND P2 ≥ 98. Current: 0/12 pass (numbers verified correct; gaps are derivation completeness, mislabeled UIBLOCKs, precision/labeling).

| course | P1 | P2 | remaining fixes |
|---|---|---|---|
| vanilla-options-quote | 97 | 98 | Show Δ=∂C/∂S and one more Greek by explicit differentiation (currently boxed "en dérivant…" without a shown derivation). Make the AAPL 20.1% realized-vol reproducible (state window/estimator). |
| options-book-greeks-pnl | 95 | 97 | BS PDE + all five Greeks are asserted; the gamma-theta thesis hangs on the PDE. Add a short replicating-portfolio/Itô derivation of the BS PDE + at least one explicit Greek differentiation. |
| implied-volatility-smile | 92 | 93 | g(k) no-arb is evaluated, not DERIVED — derive via Breeden-Litzenberger (C convex → density) → Durrleman/Gatheral g(k) by differentiating w(k) twice. §3.4 mislabeled "calibration de la même slice": it's a hand-set 31%-vol synthetic with NO fit — either least-squares fit the real ~17.8% SPX slice or rename "illustrative". Fix Ex.3 slip 0.0098→0.0977; infimum 0.254→0.249. |
| rates-swaps-dv01 | 95 | 96 | §4.2 mislabels the 248 EUR/bp KRD-vs-DV01 gap as "convexité de §3.3" — it is the first-order off-par cross-term N·(s−K)·A'·1bp (~+261); true 2nd order ≈13. Correct the narrative; add the analytic per-pillar KRD01 formula. |
| yield-curve-bootstrapping | 96 | 96 | partial-DV01 scenario_table doesn't reconcile: 2Y-only +50bp shows −168.8k vs true re-bootstrap ≈−159k, and 1Y/2Y partials don't sum to the parallel cell. Recompute off-diagonal cells; fix the description (2Y move is the leveraged float forward, not the fixed annuity). |
| barrier-options-gap-risk | 95 | 96 | Reflection principle is asserted/cited (Haug), not derived — derive the running-min law + Girsanov for λ=1. Answer the hook's own question with a euro gap-loss number. |
| credit-derivatives-cds | 95 | 95 | The load-bearing quarterly annuity 4.397 and the piecewise λ₂/λ₃ solves are stated as engine output, not shown — add the geometric-sum / bootstrap table that root-solves them. Flag the omitted accrued-on-default term. |
| fixed-income-bonds-duration | 97 | 98 | D_Mac=8.3061 and C=78.184 are engine-asserted — add the cash-flow-map UIBLOCK (PV_t, w_t, t·w_t) summing to price and to D_Mac. |
| market-risk-var-stress | 95 | 91 | WORST. (1) Stress P&L uses log-return×notional — Black Monday booked −2.29M vs true simple-return −2.05M; relabel or use (e^r−1)·V. (2) The promised real-returns covariance/correlation-matrix UIBLOCK + portfolio VaR is ABSENT (course is single-factor) — add it (renderer now has a corr_matrix block). (3) Derive the ES truncated-normal integral it promises but skips. |
| monte-carlo-pricing | 97 | 97 | Sobol table inconsistent: last RMSE cell 0.00003 should be 0.000034 (gain ~815), and 95→94. Show the control-variate β* minimisation (one line). |
| structured-products-autocall | 97 | 97 | MC error band overstated: q₁ at ~1.6σ, not ±0.0008 — widen to ±0.0016. Drop false-precision "PV=99.998" → "≈100.0 ± ~0.1". |
| stochastic-calculus-for-hedging | 95 | 98 | P1 only. Self-financing is the frozen-Δ heuristic — carry the S·dΔ term or state it explicitly. Girsanov is cited, not derived — give the RN density + Q-martingale check. |

A `corr_matrix` UIBLOCK is available: `params: { labels: [...], matrix: [[...]] }` (heatmap; values in [-1,1]).
