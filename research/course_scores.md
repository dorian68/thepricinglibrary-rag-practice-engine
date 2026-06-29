# Course evaluation scorecard — two-persona panel (P1 / P2)

Panel: **P1** Polytechnique-grade finance student (rigour, derivations, prose density, conceptual depth) · **P2** young GS/MS/JPM front-office pro (desk realism, number correctness, UIBLOCK fitness, zero hand-waving).
Bar: a course PASSES only when **BOTH P1 ≥ 98 AND P2 ≥ 98**. Scored brutally; no participation trophies.

Evaluation depth: all 12 `.md` read in full by the panel. Numbers independently re-verified with the deterministic engine / by hand for 8 courses (vanilla BS, rates swap, CDS triangle, VaR/ES, autocall, Monte-Carlo CI, implied-vol SVI slice, barrier reflection+BGK, bond duration/convexity, yield-curve bootstrap). **Every checked number reproduced exactly** — the author's engine-grounding claim holds.

## Scorecard

| course | P1 | P2 | min | PASS? |
|---|---|---|---|---|
| structured-products-autocall | 94 | 92 | 92 | ❌ |
| fixed-income-bonds-duration | 95 | 93 | 93 | ❌ |
| yield-curve-bootstrapping | 95 | 93 | 93 | ❌ |
| market-risk-var-stress | 95 | 94 | 94 | ❌ |
| vanilla-options-quote | 95 | 95 | 95 | ❌ |
| options-book-greeks-pnl | 95 | 95 | 95 | ❌ |
| rates-swaps-dv01 | 96 | 95 | 95 | ❌ |
| credit-derivatives-cds | 96 | 95 | 95 | ❌ |
| monte-carlo-pricing | 96 | 95 | 95 | ❌ |
| implied-volatility-smile | 97 | 96 | 96 | ❌ |
| barrier-options-gap-risk | 96 | 96 | 96 | ❌ |
| stochastic-calculus-for-hedging | 97 | 96 | 96 | ❌ |

**Ranking weakest → strongest:** autocall < bonds ≈ yield-curve < var < vanilla ≈ options-book ≈ rates ≈ cds ≈ monte-carlo < implied-vol ≈ barrier ≈ stoch-calc.

**Verdict: ITERATING.** No course clears the 98/98 bar, but the whole set sits in a tight 92–97 band — one more focused pass on UIBLOCKs + the per-course gaps below should push most courses to ≥98.

## #1 cross-cutting blocker (fix once, lifts 5 courses)

The `scenario_table` block type only renders a **Black-Scholes spot×vol option grid** (`params: {spot,strike,vol,T,kind}`). That is correct in option courses, but in non-option courses it is shoe-horned in and **mislabeled**, rendering an option grid where the prose computes something else:
- **yield-curve-bootstrapping §5** — block titled "Stress de courbe … receiver" but params `{spot:100,strike:100,vol:0.20,T:2,kind:"call"}` → renders a BS call grid, not a curve/PV01 shock table.
- **fixed-income-bonds-duration §3.3** — block used as a "convexity sandbox"; the course *admits in the description* it draws a vanilla grid as a proxy for bond convexity. A P2 reads that as decorative.
- **market-risk-var-stress §3** — "Stress overlay – chocs historiques rejoués sur le book 10 M$" with `{spot,vol,kind:"call"}` → BS option grid instead of the −22.9%/−12.8%/−8% spot-shock table the narrative already cites.
- **rates-swaps-dv01 §3.4** — generic BS grid reframed as a "payer-swaption surface"; defensible but the params are a plain BS call, not a swaption-vol surface.

Build a `rate_shock_table` / `pnl_grid` block (rows = factor shock, cols = second factor) fed by the engine, and point each non-option course at it. This single change is the highest-leverage lift in the set.

## Per-course fixes to reach 98 (every course < 98)

**structured-products-autocall (94/92) — weakest.**
1. Exercise 1(b) ships an **unedited stream-of-consciousness self-contradiction** ("le DIP fait mal côté book… non - côté book elle est *longue* le DIP, donc elle *gagne*…"). Rewrite cleanly: bank short the note / long the DIP hedge; on a crash DIP MtM rises but realised-corr→1 and the barrier gap break the delta-hedge.
2. **Dividend-sign clash with the source:** course asserts the autocall seller is "short dividendes" while quoted [S8] literally says the seller is "long dividends," patched only by a vague parenthetical. Derive the forward/DIP dividend sensitivity for *this* structure instead of leaning on a barrier quote that states the opposite sign.
3. Only q₁ is hand-derived (=N(−0.15)=0.4404, verified). Add the **bivariate-normal q₂** (a 2-date Gaussian probability) so ≥2 autocall probabilities are analytically checkable, not just one anchoring an all-MC table.

**fixed-income-bonds-duration (95/93).**
1. Replace the §3.3 BS-grid `scenario_table` with a real **yield-shock P&L grid** (the markdown table at §3.3 already has the right numbers: −7.7496% at +100bp, +200bp residual 1.46%).
2. Print an actual **key-rate / partial-DV01 vector** (2Y/5Y/10Y/30Y) — §4.5 only describes KRD in prose; a P2 wants the bucketed numbers on the hook's 50m line.
3. Minor: give the **dirty/clean + accrued** a worked number (carry vs price-return split is asserted, never computed).

**yield-curve-bootstrapping (95/93).**
1. Fix the §5 `scenario_table` (BS call grid mislabeled "receiver stress") → a curve-shock PV table on the stated receiver.
2. The convexity-adjustment for STIR futures is named (§2.2/§4.5) but **never quantified** — add one engine number (e.g. bp adjustment on a 2Y future) so the front-end calibration is concrete.
3. Show the **forward curve plotted vs the zero curve** (the course argues forwards amplify DF noise — demonstrate it with the §3.2 forwards rather than asserting it).

**market-risk-var-stress (95/94).**
1. Replace the §3 BS-option `scenario_table` with the real **1987/2020/Lehman spot-shock stress table** the narrative already cites (−2.29M / −1.28M P&L on the 10M book).
2. The §2.4 `monte_carlo` block is thin (`paths/horizon/confidence`) and not tied to the ^GSPC return sample — feed it the real returns so the empirical fat-tail quantile shown is the one in §3.3.
3. Only **3 exercises**; add a 4th on **Kupiec POF** (given N exceptions in n days, compute LR_POF and accept/reject) — the one quantitative backtest tool is never exercised.

**vanilla-options-quote (95/95).**
1. The BS closed form is **asserted** ("en intégrant le payoff … on obtient"); add the log-normal integral sketch (or the N(d₁)/N(d₂) split derivation) so P1 sees the step, not just the result.
2. Bid-offer levels (10.35/10.58) are stated, not constructed — tie the spread width to a sourced rule (size/offset time) numerically.

**options-book-greeks-pnl (95/95).**
1. The aggregate book Greeks (Δ250k/Γ−80k/ν120k/Θ−15k) are **operational round numbers**, not tied to an engine-priced book — build them from `bs_full` on a stated multi-option position so the attribution chain is fully engine-grounded like §3.1.
2. Vanna/volga appear in the Taylor block but are never given a number; add a small worked second-order-vol term on a wing-heavy sub-book.

**rates-swaps-dv01 (96/95).**
1. Swap the §3.4 generic-BS `scenario_table` for a genuine swaption-vol surface, or relabel honestly as illustrative.
2. KRD01 is discussed (§4.2) but the **bucket vector is never printed** — show the 5Y payer's KRD01 distribution (concentrated at 5Y) as a table so "parallel vs curve risk" is concrete.

**credit-derivatives-cds (96/95).**
1. Annuity is loose across the worked example (desk-rounded **4.2** in §3.2 vs bootstrap **4.3149** annual vs **4.397** quarterly). Pick one consistent A for the hook ticket so CS01 (21,000 vs 21,985) doesn't read as two answers.
2. The hazard curve is bootstrapped flat; add the **term-structure bootstrap** (1Y/3Y/5Y piecewise-flat λ) the limits section promises — currently only a single flat λ is shown.

**monte-carlo-pricing (96/95).**
1. §3.5 asserts the Kemna-Vorst geometric-Asian closed form (5.6374) but never shows the **adjusted vol σ/√3 / adjusted drift** derivation — add it in prose; a P1 wants the KV step.
2. §4.6 names QMC/Sobol as "often the real gain" but shows **no convergence evidence** — add one Sobol row to the §3.2 table so the O(N⁻¹) claim is demonstrated.
3. The BTC `price_chart` is semi-decorative (vol computed but BTC never feeds the Asian example) — tie it in or use the actual underlying being priced.

**implied-volatility-smile (97/96).**
1. The Durrleman/Gatheral g(k) ≥ 0 butterfly condition is **stated but never evaluated** on the §3.4 SVI slice — compute min g(k) and confirm > 0 so "a beautiful fit isn't a valid fit" is demonstrated, not asserted.
2. The sticky-strike vs sticky-delta delta difference (§4.4) is qualitative — give the numerical delta gap (ν·∂σ/∂S term) on one strike.

**barrier-options-gap-risk (96/96) — closest to the bar.**
1. Reverse-KO **vega sign-flip** (§4.5) is asserted; produce the engine number showing negative vega near the barrier, so the "barrier vega ≠ vanilla vega" claim is quantified.
2. The static-hedge replication (§5, [S11]) is described but never instantiated — show a 2–3 vanilla portfolio that is zero on the barrier.

**stochastic-calculus-for-hedging (97/96) — strongest.**
1. §2.6 `greeks_scenario` hardcodes **invented round Greeks** (gamma −80000, vega 120000, theta −15000) untied to any engine book — populate from `vanilla_option_black_scholes` on a stated notional, or it's the one un-verified table in a course that brags every number is engine-computed.
2. §3.5 ^GSPC `price_chart` is **decorative** (asserts the carry sign, computes no number) — compute the realised-21d vs VIX spread on the cache series or cut it.
3. Add the explicit **Leland transaction-cost optimum** (§4.4 only describes it) as a closed form so the hedge-frequency tradeoff is quantitative.

## Notes for the next iteration
- Sourcing is genuinely strong everywhere: 10–20 real `[Sx]` per course, correctly labelled [extrait]/[reformulé]/[généré], with a populated source map. Not decorative. Keep it.
- The 9-section §2 structure is complete in all 12. Prose is Hull-density, not scaffold.
- The dominant gap is **interactive-block fitness**, not content: fix the block types/params so every UIBLOCK renders the engine/cache number the surrounding prose computes, and the non-option courses jump ~2–3 points on P2.
- Quiz counts: most have 5 MCQ with distractor analysis (good); VaR has only 3 exercises (add a 4th).
