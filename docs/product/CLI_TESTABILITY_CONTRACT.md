# CLI_TESTABILITY_CONTRACT.md — ThePricingLibrary

> Every core journey must be reproducible from the CLI, without the UI. This
> contract lists what EXISTS today (grounded in the repo, 2026-06-06) and what is
> MISSING. The Technical RL Agent owns closing the gaps. Status evidence below
> is current through 2026-07-25.

---

## Principle

> The backend is the engine; the UI is the dashboard. If a journey cannot be
> validated from the CLI, it is not validated. No feature is "done" on UI
> inspection alone.

All commands below run from `Tools/pricinglibrary_rag_backend` unless noted.
Offline/no-cost prefix: `TPL_LLM_PROVIDER=template`. On this Windows box pytest
requires `--basetemp=.pytest_tmp` (default temp throws WinError 5).

---

## A. Backend — EXISTING and required commands

English interview pilot (2026-11-14): backend `python scripts/smoke_interview_lab.py`
exercises signed non-admin access, numerical attempts, immutable/idempotent
history, correction exposure, conceptual transfer, private export, exact resume,
operator-only anonymous aggregates and the opt-in local entitlement policy.
Focused pytest: `python -m pytest -q tests/test_interview_lab.py
tests/test_english_generation.py tests/test_api_security.py
--basetemp=.pytest_tmp_interview`. No provider key, corpus or purchase is required
for these original authored cases. `TPL_ENFORCE_ENTITLEMENTS=true` makes signed
local learner testing enforce paid-course rules while retaining the explicit
operator test account. This flag does not relax production security.

Frontend: `npm run smoke:interview:browser` covers real public preview, signed
free-learner attempts, self-review, conceptual put transfer, cross-browser resume,
private export, 503 retry and all six cases at 1440/390/320 px. The existing
course/Survival corrections use `npm run smoke:journey-fixes`. Generator checks
remain `smoke:exercise-generation` and `smoke:exercise-generation:browser`, with
English default, explicit French, preserved mathematics, curated references,
private history and failure recovery. `smoke:interview-context` checks exact tool
inputs, strategy presets and allowlisted authentication return URLs.

Public checkout CI has an explicit code-only scope. Full licensed-content,
Starter Kit artifact, deployment, payment and public pilot gates remain separate;
passing public CI cannot substitute for their real external evidence.

Accepted Courbe signature hero (F-WEB-11, 2026-11-14): from
`WEBSITE/thepricinglab`, `npm run build && npm run smoke:ux:browser` exercises
the real anonymous production build. The journey validates seeded paths and
their exact Open/High/Low values, the final-point price anchor at eight widths
(320 through 1440 px), the original horizontal logo, unframed full-contrast
chart, keyboard provenance disclosure, free pricing calculation and course
navigation. `signature-geometry.json` records actual SVG-to-screen coordinates
and quote/copy bounds; normal/reduced-motion and mobile-menu behavior remain
covered. Use `TPL_UX_EVIDENCE_DIR` to keep this iteration separate. Typecheck,
visual-shell and bundle-budget checks also remain required. No backend,
provider or authentication contract changes are part of this visual evolution.

Exercise corrections (F-EXO-1/2/3/4, 2026-11-11): from the frontend directory,
`npm run smoke:exercise-generation` validates actual signed HTTP generation,
calculation inputs, private library, pagination, retries and offline reference
calculations. `npm run smoke:exercise-generation:browser` additionally validates
fresh-browser retrieval, exact exports, rendered math/rubric, preserved inputs,
access/validation errors and503 recovery. They use the real local API and
corpus; HTTP fixtures are confined to explicit browser error cases. Backend
`tests/test_exercise_generation.py` covers independent math oracles, constraints,
question/answer/rubric mapping, bounded lexical retrieval and member A/B library
isolation/idempotency. Public read contracts: verified-user-only
`GET /platform/exercises?limit=30&offset=0` and
`GET /platform/exercises/{id}`. The old operator-only generation history is not
used as a cross-user library. No provider API key is needed in template mode.

Local admin preview (F-WEB-10, 2026-11-10): run `npm run dev` from
`WEBSITE/thepricinglab`, then `npm run smoke:local-admin` for actual signed API
access, server-owned progress/forum persistence, visitor rejection and
cross-origin rejection. `npm run smoke:local-admin:browser` covers fresh admin,
reload, completed-module restoration, paid calculation/export, exercises,
visitor/admin switching and startup retry, with no Supabase/online API calls.
After `npm run build`, `npm run smoke:local-admin:production` proves the built
artifact contains no local-admin mechanism and preview bootstrap/API return 404.
These commands require the existing Python backend dependencies; they need no
Supabase, Stripe or LLM credentials. Test activity lives only in the ignored
`WEBSITE/thepricinglab/.local-preview/data` directory. This is a local testing
exception, never a production entitlement source.

| Capability | Command | Status |
|------------|---------|--------|
| Unit/integration tests | `python -m pytest -q --basetemp=.pytest_tmp_fcal10_final` | ✅ 301 pass |
| Init DB | `python -m pricinglibrary_rag.cli init-db` | ✅ |
| Ingest corpus | `python -m pricinglibrary_rag.cli ingest <path> --recursive --glob "*.pdf"` | ✅ |
| Search corpus | `python -m pricinglibrary_rag.cli search "<query>" --top-k 8` | ✅ |
| Verified calc | `python -m pricinglibrary_rag.cli calculate "<scenario>"` | ✅ |
| Generate exercise | `python -m pricinglibrary_rag.cli exercise --product option --concept "barrier"` | ✅ |
| Generate course | `python -m pricinglibrary_rag.cli course "<topic>" --concept ...` | ✅ |
| Pedagogy stats | `python -m pricinglibrary_rag.cli pedagogy-stats` | ✅ |
| Backfill pedagogy | `python -m pricinglibrary_rag.cli backfill-pedagogy [--force]` | ✅ |
| Product evaluation | `python -m pricinglibrary_rag.cli evaluate --limit 3` | ✅ |
| Serve API | `python -m pricinglibrary_rag.cli serve --host 127.0.0.1 --port 8000` | ✅ |
| Corpus pedagogical audit | `python scripts/debug_sources.py [--sample N]` | ✅ |
| Course gen smoke (e2e, offline) | `python scripts/smoke_course_generation.py` | ✅ |
| Course quality gate | `python scripts/audit_course_quality.py --dir <dir>` | ✅ |
| Billing state machine (offline, no charge) | `python scripts/smoke_billing.py` | ✅ checkout (mock) + signed webhook → entitlement + idempotency + bad-sig reject |
| Starter Kit one-shot fulfillment | `python scripts/smoke_starter_kit_fulfillment.py` | ✅ 8 steps: public availability + JWT-bound payment checkout + signed/idempotent webhook + real manifest/checksum gate + download + refund isolation |
| Starter Kit Excel contract | `python scripts/verify_excel_dashboard.py` (from `Products/market_finance_starter_kit`) | ✅ real workbook passes the OOXML graph, exact formulas/inputs/charts, independent cached values and active-content rejection gates. |
| Starter Kit immutable release | `python scripts/build_release.py && python scripts/verify_bundle.py` (from product directory) | ✅ executable seven-of-seven/checksum/ZIP gate; `ready:true` manifest and immutable v1.0.0 ZIP verified. |
| Starter Kit editable quant CV | `powershell -File scripts/build_career_docx.ps1 && powershell -File scripts/render_career_docx.ps1` (from product directory) | ✅ deterministic metadata-scrubbed DOCX, native Word lists/headings, one-page Word/PNG render and manifest checksum; 21/21 product tests pass |
| Production Compose contract | `python scripts/check_deployment_contract.py --env-file .env.production` | ✅ fail-closed resolved-JSON gate: image digest and metadata, public callbacks, exact auth/Stripe values, loopback port, non-root/read-only runtime and mount whitelist. The aggregate runs the committed template in explicit PASS-CLOSED mode. |
| Production observability | `python scripts/smoke_observability.py` | ✅ request correlation, operator-only Prometheus metrics, bounded-cardinality route labels, validated privacy-bounded RUM |
| Credential scan | `python scripts/audit_secrets.py` | ✅ high-confidence OpenAI/Stripe/service-role material absent from current text artifacts; public Supabase anon keys are not treated as secrets |
| Deployed Starter Kit acceptance harness | `python scripts/smoke_deployed_acceptance.py --base-url https://<staging-api-origin> --require-entitled` | ✅ public denial, readiness, availability, entitlement, manifest and ZIP checksum checks; real token is read only from `TPL_STAGING_ACCESS_TOKEN` |
| Local HTTP deployment smoke | `python scripts/smoke_local_deployment.py` | ✅ starts a real ephemeral Uvicorn process, serves the verified artifact, checks health/readiness/availability and anonymous denial; deliberately does not claim Stripe/Supabase or Docker evidence |
| Local rollback smoke | `python scripts/smoke_local_rollback.py` | ✅ temporary SQLite backup/restore across real API restarts, deliberate entitlement-loss detection and restored entitled SHA-256 download; does not claim Docker digest or public rollback evidence |
| Buyer pilot evidence gate | `python scripts/validate_pilot_evidence.py --input ../../reports/pilot_evidence.json` | ✅ anonymised five-user schema, SHA-256 delivery evidence, workbook recalculation, satisfaction and blocking-issue thresholds; intentionally remains FAIL-CLOSED until real pilot evidence exists |
| Staging evidence gate | `python scripts/validate_release_evidence.py --kind staging --input ../../reports/staging_evidence.json` | ✅ exactly three purchases, anonymous denial, entitlement persistence, SHA-256, webhook idempotence, cancellation/refund/chargeback and stale-asset checks; remains FAIL-CLOSED until a deployed staging run exists |
| Rollback evidence gate | `python scripts/validate_release_evidence.py --kind rollback --input ../../reports/rollback_evidence.json` | ✅ immutable digest transition/restoration, verified backup, readiness/availability, entitled-download checksum and integrity checks; remains FAIL-CLOSED until a timed staging drill exists |
| Course entitlement and platform identity | `python -m pytest -q tests/test_api_security.py --basetemp=.pytest_tmp/course-security` | ✅ 9 focused tests: anonymous/insufficient-plan denial, Starter/Student delivery, private caching, unknown-course 404, signed authorship, cross-account progress denial, atomic concurrent progress, fixed `+1` vote, public DTO privacy, unverified Survival exclusion and signed operator claims |
| Billing CLI | `python -m pricinglibrary_rag.cli billing-config\|billing-checkout\|billing-entitlement <email>` | ✅ |
| Regenerate 12 courses | `python scripts/generate_course_scripts.py --output-dir <dir> --llm-provider <p>` | ✅ |
| Course catalogue/script contract | `python scripts/audit_course_manifest.py` | ✅ 12/12 active courses map to private scripts with matching module counts |
| Course objective contract | `python scripts/audit_course_objective.py` | ✅ 12/12 visible course-specific quizzes, complete desk structure and explicit calculator/scenario routing |
| Market provenance contract | `python -m pytest -q tests/test_market_provenance.py --basetemp=.pytest_tmp_manifest` | ✅ source, status, date, unit and non-executable-quote limitation asserted |

## B. Backend — status update (2026-07-25)

| Capability | Command | Status |
|------------|---------|--------|
| API + J2 contract smoke (HTTP, in-process) | `python scripts/smoke_api.py` | ✅ DONE — proves `/health`, `/agent/exercise` (grounded `sources[]`, verified `calculation_pack` with a numeric result, `metadata.llm`), `/agent/course`. Also covers the J2 *value* path (F-EXO-3), so a separate `smoke_exercise_journey.py` is intentionally not created. |
| Calculators golden values | `python -m pytest -q tests/test_generation_controls.py tests/test_yield_curve.py` | ✅ 22 focused tests; shared JS/Python curve fixture, sparse-swap repricing and invalid-input paths included |
| Quant terminal-condition audit | `python scripts/verify_engine_quant.py` | ✅ 321 checks; canonical Bond, Vol Surface and Black-Scholes values/limits/forward-ATM kink identities, curve construction plus all five realized-volatility estimators, independent formulas, rolling and adversarial quality cases included |
| Full backend regression suite | `python -m pytest -q --basetemp=.pytest_tmp_fcal10_final` | ✅ 301 tests on 2026-07-19 |
| Production technical aggregate | `python scripts/production_check.py` | ✅ configuration gate plus security, billing, API and Starter Kit smokes |

## C. Frontend — EXISTING / MISSING

The November 2026 delivery audit adds these reproducible checks from
`WEBSITE/thepricinglab` (build first). They start and stop their own production
preview; browser identities and service failures are explicitly local fixtures.

- `npm run audit:site:browser`: 128 active-route/view combinations at 1440/390 px,
  anonymous and Pro fixture; headings, main landmark, labels, images, overflow,
  runtime errors and captures. No live billing or Supabase acceptance claim.
- `npm run smoke:delivery:browser`: signup confirmation, recovery request and
  password update, blog outage/search/404, product readiness, signed forum
  publication/reopen/reply/failure draft, actual exercise JSON, actual simulation
  CSV/finite numbers/UI parity and payoff geometry.
- `npm run smoke:teaching-scenarios`: eleven named fixed-seed cases, zero-volatility
  boundary, invalid inputs, analytical expectation and independent Python goldens
  in `fixtures/teaching_scenarios_reference.json`. Display names cannot shadow
  sample count. This runs independently of React and the browser.
- Backend: `python scripts/smoke_platform.py` proves real temporary SQLite
  persistence; `python scripts/audit_public_course_projection.py` and
  `tests/test_api_security.py` also exclude teacher/persona production notes.

Evidence: `reports/2026-11-09_technical-rl_delivery-audit.md` and
`reports/2026-11-09_business-client_delivery-audit.md`. An actual production
configuration and real deployed acceptance remain separate release gates.

| Capability | Command | Status |
|------------|---------|--------|
| Source-line parser smoke | `node scripts/smoke_parse_sources.mjs` | ✅ exists |
| Build | `npm run build` | ✅ |
| Navigation security | `npm run smoke:navigation-security` | ✅ global click-capture boundary blocks backslashes, protocol-relative targets and dangerous schemes; guarded `useNavigate` covers programmatic SPA navigation without logging target values |
| Public visual shell | `npm run smoke:visual-shell` | ✅ shared synchronous/lazy tokens, semantic home/hero hooks, a full-width price evidence band, paired secondary terminal evidence, typographic icon-free Audience card headers, safe mobile assistant placement, SVG action-icon mapping, 760/480 px responsive rules, reduced-motion behavior, trust disclosures and self-contained visual assets are enforced from the CLI; runtime QA separately proves exact width at 1440/760/480/390 px |
| Calm workspace UX (F-WEB-4, 2026-11-09) | `npm run build` then `npm run smoke:ux:browser` | Initial eight-step production Chromium evidence is retained in `reports/visual-qa-2026-11-09/`. The current runner extends it with F-WEB-5 below; anonymous calculator/course journeys, catalogue filters, 15 layouts, 44 px actions and keyboard-safe mobile navigation remain covered. |
| Modern hero/navigation (F-WEB-5, 2026-11-09) | Historical run of `npm run smoke:ux:browser` | Ten-step evidence is retained in `reports/visual-qa-2026-11-09-hero-modern/`. The user approved its navbar and requested the earlier market chart instead of its mini-pricer; the current runner follows F-WEB-6 below. |
| Restored market hero (F-WEB-6, 2026-11-09) | Historical production UX run | Ten-step evidence remains in `reports/visual-qa-2026-11-09-hero-market/`; the user subsequently rejected the framed two-column composition and invented branding, leading to F-WEB-7 below. |
| Hero layout proposals / brand correction (F-WEB-7, 2026-11-09) | Historical production UX run | Eleven-step proposal evidence remains in `reports/visual-qa-2026-11-09-hero-layouts/`. The user explicitly selected B; current behavior and branding follow F-WEB-8 below. |
| Selected B + original brand identity (F-WEB-8, 2026-11-09) | `python scripts/build_brand_svg.py`, `npm run build`, `npm run smoke:ux:browser` | Twelve production steps verify the source logo SHA, SVG under 50 kB, browser symbol/letter contour IoU >98%, original signature at 390 px, B fixed on `/`, existing calculator/course/menu journeys and responsive/motion behavior. Current evidence: `reports/visual-qa-YYYY-MM-DD-brand-navbar/`. Browser runtime needs no Python/OpenCV; they are authoring dependencies only. |
| Product/tool contract | `npm run smoke:product-contract` | ✅ nine active tools expose engine, inputs, conventions, limits, data status and course/exercise links; twelve-course manifest is present |
| Deterministic model calibration | `npm run smoke:calibration` | ✅ Black-76 price/inversion, Hagan SABR and Fourier Heston golden cases; repeated fits, parameter bounds, fit improvement, CSV validation and browser-source trust contract |
| Active calibration production bundle | `npm run smoke:calibration:bundle` (after `npm run build`) | ✅ dedicated lazy component + Web Worker shipped by the active route; legacy quadratic and fake contributive-model strings absent |
| Authenticated calibration browser journey | `npm run smoke:calibration:browser` | ✅ isolated production build/preview; real `/tools/calib` route unlocked only by a bearer-bound backend entitlement contract; Black/SABR/Heston, valid/adversarial CSV, downloads, history, mobile layout and zero browser errors proved |
| Deterministic yield-curve construction | `npm run smoke:curve` | ✅ shared five-case fixture; deposit/FRA/explicit-convexity future/sparse swaps/negative rates; exact repricing, CSV/export and adversarial failures |
| Active curve production bundle | `npm run smoke:curve:bundle` (after `npm run build`) | ✅ dedicated lazy component; conventions/repricing present; legacy sparse bootstrap and misleading `1y fwd` path absent |
| Authorized curve browser journey | `npm run smoke:curve:browser` | ✅ anonymous lock plus bearer-bound Starter access; reference/edit/valid and invalid CSV paths, JSON export, diagnostics, actual history, 390 px layout and zero browser errors proved |
| Deterministic realized volatility | `npm run smoke:realized-vol` | ✅ five OHLC estimators, shared sessions, 252/365 scaling, rolling, strict parser, dated warnings, deterministic exports and pure worker protocol |
| Python/JavaScript realized-volatility parity | `npm run smoke:realized-vol:cross-engine` | ✅ one canonical contract; recursive results agree to `1e-13`, CSV exports are byte-identical, formatting-invariant SHA-256 and adversarial parser/diagnostic parity pass |
| Active realized-volatility bundle | `npm run smoke:realized-vol:bundle` (after `npm run build`) | ✅ dedicated 26,201-byte component and 18,548-byte worker; legacy synthetic walk absent |
| Authorized realized-volatility browser journey | `npm run smoke:realized-vol:browser` | ✅ anonymous/inactive lock, bearer-bound Starter access, local worker, five rendered/toggleable series, actionable warnings, estimator guidance, contextual result header, evidence exports, fail-closed CSV, history, sticky 390 px audit table and zero browser/network leakage errors |
| Deterministic payoff strategy analysis | `npm run smoke:payoff` | ✅ canonical v1.0.1 engine; exact analytical tails/bounds/breakevens, signed Greeks, 7 golden strategies, deterministic JSON/two-CSV evidence and 14 fail-closed adversaries |
| Python/JavaScript payoff parity | `npm run smoke:payoff:cross-engine` | ✅ 8 strategies agree recursively to `1e-12`, share analysis IDs and produce byte-identical CSV; 6 invalid cases fail closed in both runtimes |
| Historical payoff-consumer compatibility | `npm run smoke:payoff:compat && npm run smoke:legacy-options` | ✅ active vanilla consumers delegate to the canonical engine; grid-derived bounds, fake VaR/sine data and invalid short Greeks are absent; unsupported barriers fail closed |
| Active payoff production bundle | `npm run smoke:payoff:bundle` (after `npm run build`) | ✅ dedicated 22,629-byte component plus 12.54 kB shared exact engine; duplicate/grid-bound calculator and fake save path absent |
| Authorized payoff browser journey | `npm run smoke:payoff:browser` | ✅ anonymous/inactive lock, bearer-bound Starter access, exact unlimited/finite tails, off-window roots, signed Greeks, real JSON/two-CSV exports, fail-closed stale clearing, history, 390 px layout and zero errors/data leakage |
| Deterministic Monte Carlo pricing/risk | `npm run smoke:mc` | ✅ canonical v1.0.0 engine; explicit P/Q measures, loss VaR/ES, European/Asian pricing, plain/antithetic/control methods, uncertainty/convergence, same-run paths/distribution, versioned evidence and 12 fail-closed adversaries |
| Python/JavaScript Monte Carlo parity | `npm run smoke:mc:cross-engine` | ✅ six P/Q, variance-reduction, Asian and degenerate cases agree recursively within `1e-11`, share analysis IDs and emit byte-identical LF terminal/path CSV files |
| Monte Carlo backend compatibility | `npm run smoke:mc:backend` | ✅ 52 Python cases; canonical engine plus AG-UI/practice adapters, strict limits, rejected overflow/string/fraction coercion, surfaced domain errors and absence of former RNG/clamping paths |
| Monte Carlo worker protocol | `npm run smoke:mc:worker` | ✅ canonical import, request-id isolation, deterministic result and scoped fail-closed errors without DOM/network/ambient randomness |
| Active Monte Carlo production bundle | `npm run smoke:mc:bundle` (after `npm run build`) | ✅ dedicated 31,126-byte lazy component and one 12,480-byte worker shared with course content; false counts and split-seed/static legacy route absent |
| Authorized Monte Carlo browser journey | `npm run smoke:mc:browser` | ✅ anonymous/inactive lock, bearer-bound Starter access, Q pricing/uncertainty/Asian control variate, P loss risk, real JSON/two-CSV evidence, stale clearing, history, worker, visible 44 px mobile CTA and zero errors/data leakage |
| Deterministic CRR lattice analysis | `npm run smoke:binomial` | ✅ canonical v1.0.0 European/American engine; parity, same-tree benchmark, exercise frontier, five Greeks, degenerate/hard-bound handling, deterministic evidence and 13 fail-closed adversaries |
| Python/JavaScript CRR parity | `npm run smoke:binomial:cross-engine` | ✅ eight European, American, dividend, zero-volatility, expiry/short, probability-boundary-Rho and negative-rate-call cases agree recursively within `2e-10`, share analysis IDs and emit byte-identical LF convergence/frontier CSV files |
| Binomial backend compatibility | `npm run smoke:binomial:backend` | ✅ 29 cases; canonical backend and AG-UI adapter preserve strict types, requested steps, dividend yield, no-arbitrage failures and full analysis metadata without legacy clamping |
| Binomial worker protocol | `npm run smoke:binomial:worker` | ✅ canonical import, request-id isolation, deterministic result and scoped fail-closed error without DOM/network state |
| Active Binomial production bundle | `npm run smoke:binomial:bundle` (after `npm run build`) | ✅ dedicated lazy Student component and worker; former inline CRR calculator, step cap and probability repair absent |
| Authorized Binomial browser journey | `npm run smoke:binomial:browser` | ✅ anonymous/inactive lock, bearer-bound Student access, American put/dividend-call frontiers, honest European benchmark, Greeks/nodes, real JSON/two-CSV evidence, stale clearing/history, worker, 44 px CTA at 390/390 px and zero errors/data leakage |
| Deterministic fixed-rate bond analysis | `npm run smoke:bond` | ✅ canonical v1.0.0 engine; par/accrued identities, price↔YTM inversion, dated schedules, negative yields, duration/convexity, central and cash-flow-attributed DV01, signed shocks, deterministic evidence and strict adversaries |
| Python/JavaScript bond parity | `npm run smoke:bond:cross-engine` | ✅ eight yield/clean-price, ACT/ACT and 30E/360 February→August EOM, zero-coupon, negative-yield, short-position and monthly-EOM cases agree recursively within 2e-11, share SHA IDs and emit byte-identical LF cash-flow/scenario CSV files |
| Bond backend compatibility | `npm run smoke:bond:backend` | ✅ 31 Python cases; canonical backend plus strict AG-UI adapter, February/EOM day-count normalization, schedules, quote inversion, risk, evidence and rejected coercion/unknown fields |
| Bond worker protocol | `npm run smoke:bond:worker` | ✅ canonical import, request-id isolation, deterministic result and scoped fail-closed error without DOM/network/ambient randomness |
| Active Bond production bundle | `npm run smoke:bond:bundle` (after `npm run build`) | ✅ dedicated lazy Starter component and worker; inline rounded-maturity engine and unused divergent component absent |
| Authorized Bond browser journey | `npm run smoke:bond:browser` | ✅ 9/9 anonymous/inactive lock, bearer-bound Starter access, par and clean-price inversion, clean/dirty/accrued, risk/cash-flow evidence, negative yield, stale clearing/history, worker, 44 px CTA at 390/390 px and zero errors/data leakage |
| Deterministic volatility-surface quality | `npm run smoke:vol-surface` | ✅ canonical v1.0.0 `k`/total-variance engine; ATM/skew/curvature, bilinear `w` interpolation, clean/calendar/butterfly diagnostics, deterministic evidence, strict CSV and 15 fail-closed adversaries |
| Python/JavaScript surface parity | `npm run smoke:vol-surface:cross-engine` | ✅ six clean/interior/node/boundary/calendar/butterfly/no-spread cases agree recursively within `2e-11`, share SHA IDs and emit byte-identical LF points/diagnostics CSV files |
| Vol Surface backend compatibility | `npm run smoke:vol-surface:backend` | ✅ 27 Python cases; canonical backend plus closed AG-UI adapter, golden metrics, violations, exports and rejected coercion/unknown fields |
| Vol Surface worker protocol | `npm run smoke:vol-surface:worker` | ✅ canonical import, request-id isolation, deterministic result and scoped fail-closed error without DOM/network/ambient randomness |
| Active Vol Surface production bundle | `npm run smoke:vol-surface:bundle` (after `npm run build`) | ✅ dedicated lazy Student component (29,480 bytes) and worker (12,369 bytes); clamped inline demo and fake 3D page absent |
| Authorized Vol Surface browser journey | `npm run smoke:vol-surface:browser` | ✅ 9/9 anonymous/inactive lock, bearer-bound Student access, real CSV, clean/calendar/butterfly cases, slices/term structure/heatmap, same-SHA JSON/two-CSV evidence, stale clearing/history, 44 px CTA at 390/390 px and zero errors/data leakage |
| Deterministic Black-Scholes pricing and IV | `npm run smoke:black-scholes` | ✅ canonical European BSM with dividends/negative rates, strict bounded IV, expiry and zero-volatility limits including declared forward-ATM kink, five unit-labelled Greeks, signed portfolio, exact shocks, 21-point sensitivities and deterministic SHA-bound evidence |
| Python/JavaScript Black-Scholes parity | `npm run smoke:black-scholes:cross-engine` | ✅ eight value/IV/expiry/zero-volatility/kink/signed-scale cases agree recursively within `2e-11`, share SHA IDs and emit byte-identical LF scenario/sensitivity CSV files; invalid schemas fail closed in both runtimes |
| Black-Scholes backend compatibility | `npm run smoke:black-scholes:backend` | ✅ 22 Python cases; canonical backend plus closed AG-UI adapter, strict types, value/IV/limit/Greek/evidence contracts and rejected coercion/unknown fields |
| Black-Scholes worker protocol | `npm run smoke:black-scholes:worker` | ✅ canonical import, request-id isolation, deterministic success and scoped fail-closed error without DOM/network/clock/ambient randomness |
| Active Black-Scholes production bundle | `npm run smoke:black-scholes:bundle` (after `npm run build`) | ✅ 35-asset build with dedicated anonymous/free lazy component (~23.94 kB) and worker (11,304 bytes); shell, course and Agent Room BSM/IV consumers delegate to the canonical engine without silent clamps; six post-result Free/Starter/Student continuation routes are bundle-checked |
| Anonymous Black-Scholes browser journey | `npm run smoke:black-scholes:browser` | ✅ 8/8 free access, ATM price/parity, Greek units, six signed scenarios, six contextual Free/Starter/Student continuation links, 20% IV round-trip, same-SHA JSON/two-CSV evidence, fail-closed stale clearing, three 21-point grids/history, worker, 44 px CTA at 390/390 px and zero errors/data leakage |
| Tools catalogue truth contract | `npm run smoke:tools-catalog` | ✅ 9 declared tools resolve through 4 known tiers; Starter route badges match access; unknown tiers fail safe; global unproved `stable` copy is forbidden and synthetic/validated states are explicit |
| Course/Lab entitlement bundle contract | `npm run build && npm run smoke:entitlements` | ✅ production bundle contains only the bounded Black-Scholes preview; all emitted JS is scanned against paid prose/derivation markers and contains no `lessonProse`/`derivations` chunk; paid scripts use the bearer API; admin authority is signed; completion waits for the server; `/lab` defaults Student and Backtest is Pro-gated |
| Full browser entitlement matrix | `npm run smoke:entitlements:browser` | ✅ isolated production build proves Anonymous/Free/Starter/Student/Pro access, paid-script non-fetch while locked, server-confirmed course completion after refresh, Pro Backtest non-mounting for Student, and Survival delayed success plus explicit HTTP 503 failure (`Not saved`) |
| Production bundle budget | `npm run smoke:bundle` | ✅ 35 JS assets; largest 394,423 bytes; hard limit 500,000; Supabase is a dynamic 212.51 kB client chunk absent from anonymous HTML preloads |
| Browser RUM source contract | `npm run smoke:rum` | ✅ production-only, explicit opt-in, HTTPS API and privacy field/route rules |
| Browser RUM runtime | `npm run smoke:rum:browser` | ✅ isolated production build in Chromium; TTFB/FCP/flush payloads contain no raw slug, query email or token |
| Live frontend environment contract | `npm run smoke:production-env-contract` | ✅ adversarial validator tests; real `npm run check:production-env` remains fail-closed until operator values exist |
| Auth freshness / account-switch races | `npm run smoke:auth-freshness` | ✅ delayed getSession/profile/entitlement A cannot overwrite logout or account B; same-token SIGNED_IN invalidates and refetches entitlement; rejected dynamic imports remain retryable |
| Constrained mobile performance | `npm run smoke:performance` | ✅ four post-remediation samples plus the final aggregate pass every hard budget; observed envelope FCP 1,604–1,704 ms, LCP 2,900–3,228 ms, CLS 0, median interaction 104–120 ms and worst 264–296 ms vs 2,500/4,000/0.1/300/400 budgets |
| Lint | `npm run lint` | ✅ |
| Backend-connectivity smoke | `npm run smoke:api` | ✅ DONE — pings `${VITE_TPL_RAG_API_URL}/health` + one `/agent/exercise` round-trip; SKIPs (exit 0) when backend down (hybride-local), PASS with grounded contract when up |
| TypeScript contract | `npm run typecheck` | ✅ `tsc --noEmit`; included before all runtime smokes in the technical aggregate |
| Technical audit | `npm run audit:technical` | ✅ fresh aggregate PASS in 330.2 s: lint, TypeScript, source/catalogue/auth-freshness, every deterministic/cross-engine/backend/worker tool gate, RUM/environment/business contracts, full production build, all browser journeys, bundle budget and constrained-mobile performance |
| Business journey smoke | `npm run smoke:journey` | ✅ catalogue tiers/statuses, course rendering, lazy Markdown/KaTeX and assistant, fail-closed Starter Kit workspace, calibration, curve, realized-volatility, payoff, Monte Carlo, Binomial, Bond, Vol Surface and Black-Scholes production-browser journeys |

### Current npm script contract (authoritative source: `package.json`)

```jsonc
{
  "smoke:sources": "node scripts/smoke_parse_sources.mjs",
  "smoke:api":     "node scripts/smoke_api.mjs",        // pings backend health + exercise
  "smoke:calibration": "node scripts/smoke_model_calibration.mjs",
  "smoke:curve": "node scripts/smoke_yield_curve.mjs",
  "smoke:realized-vol": "node scripts/smoke_realized_volatility.mjs",
  "smoke:realized-vol:cross-engine": "node scripts/smoke_realized_volatility_cross_engine.mjs",
  "smoke:payoff": "node scripts/smoke_payoff_strategy.mjs",
  "smoke:payoff:cross-engine": "node scripts/smoke_payoff_strategy_cross_engine.mjs",
  "smoke:payoff:compat": "node scripts/smoke_payoff_strategy_compat.mjs",
  "smoke:mc": "node scripts/smoke_monte_carlo.mjs",
  "smoke:mc:cross-engine": "node scripts/smoke_monte_carlo_cross_engine.mjs",
  "smoke:mc:backend": "node scripts/smoke_monte_carlo_backend.mjs",
  "smoke:mc:worker": "node scripts/smoke_monte_carlo_worker.mjs",
  "smoke:mc:bundle": "node scripts/smoke_monte_carlo_bundle.mjs",
  "smoke:mc:browser": "node scripts/smoke_monte_carlo_browser.mjs",
  "smoke:binomial": "node scripts/smoke_binomial.mjs",
  "smoke:binomial:cross-engine": "node scripts/smoke_binomial_cross_engine.mjs",
  "smoke:binomial:backend": "node scripts/smoke_binomial_backend.mjs",
  "smoke:binomial:worker": "node scripts/smoke_binomial_worker.mjs",
  "smoke:binomial:bundle": "node scripts/smoke_binomial_bundle.mjs",
  "smoke:binomial:browser": "node scripts/smoke_binomial_browser.mjs",
  "smoke:bond": "node scripts/smoke_bond.mjs",
  "smoke:bond:cross-engine": "node scripts/smoke_bond_cross_engine.mjs",
  "smoke:bond:backend": "node scripts/smoke_bond_backend.mjs",
  "smoke:bond:worker": "node scripts/smoke_bond_worker.mjs",
  "smoke:bond:bundle": "node scripts/smoke_bond_bundle.mjs",
  "smoke:bond:browser": "node scripts/smoke_bond_browser.mjs",
  "smoke:black-scholes": "node scripts/smoke_black_scholes.mjs",
  "smoke:black-scholes:cross-engine": "node scripts/smoke_black_scholes_cross_engine.mjs",
  "smoke:black-scholes:backend": "node scripts/smoke_black_scholes_backend.mjs",
  "smoke:black-scholes:worker": "node scripts/smoke_black_scholes_worker.mjs",
  "smoke:black-scholes:bundle": "node scripts/smoke_black_scholes_bundle.mjs",
  "smoke:black-scholes:browser": "node scripts/smoke_black_scholes_browser.mjs",
  "smoke:legacy-options": "node scripts/smoke_legacy_black_scholes.mjs",
  "smoke:auth-freshness": "node scripts/smoke_auth_freshness.mjs",
  "smoke:navigation-security": "node scripts/smoke_navigation_security.mjs",
  "smoke:visual-shell": "node scripts/smoke_visual_shell.mjs",
  "smoke:tools-catalog": "node scripts/smoke_tools_catalog.mjs",
  "smoke:journey": "npm run build && ...browser/bundle gates...",
  "audit:technical": "npm run lint && ...all deterministic and browser gates..."
}
```

## D. Agent tooling registry — implemented 2026-06-30

| Capability | Command | Status |
|------------|---------|--------|
| Tool registry contracts + audit/replay | `python scripts/smoke_tool_registry.py` | ✅ DONE — 16 agents, 874 registered tools, schemas, permissions, artifacts, audit/replay |
| Agent artifact contracts | `python scripts/smoke_agent_artifacts.py` | ✅ DONE — desk agents and quant DAG agents emit expected artifacts |
| RFQ-to-report journey | `python scripts/smoke_rfq_to_report.py` | ✅ DONE — Sales→Report chain with deterministic price, quote, risk, disclaimer |
| Compliance/suitability guards | `python scripts/smoke_compliance_suitability.py` | ✅ DONE — client/product/advice-boundary checks executable and audited |
| Quant agent DAG | `python scripts/smoke_quant_agent_dag.py` | ✅ DONE — G0/G1/G3/G4/G6/gating tools present and executable |
| Preregistration contract | `python scripts/smoke_preregistration.py` | ✅ DONE |
| Dataset manifest contract | `python scripts/smoke_dataset_manifest.py` | ✅ DONE |
| Capacity/net-of-cost contract | `python scripts/smoke_capacity_curve.py` | ✅ DONE |
| Tool registry HTTP API | `python scripts/smoke_tool_registry_api.py` | ✅ DONE |
| Chief of Staff validation | `python scripts/smoke_chief_of_staff_validation.py` | ✅ DONE — satisfaction 100% (>98% bar) |
| ConversationLedger + task ledger | `python scripts/smoke_conversation_ledger.py` | ✅ DONE — sessions, sanitized history, artifacts, detached tasks |
| MCP adapter for agent tools | `python scripts/smoke_agent_mcp_adapter.py` | ✅ DONE — search/list/describe/call/audit/replay/conversation search |
| Agent Interaction Gateway | `python scripts/smoke_agent_gateway.py` | ✅ DONE — inbound channel route, session reuse, tool artifact |
| Sessions/tasks/MCP/gateway HTTP API | `python scripts/smoke_agent_interaction_api.py` | ✅ DONE |
| Runtime turns/approvals/thread transforms | `python scripts/smoke_agent_runtime_state.py` | ✅ DONE — turns, approvals, compact, fork, inject, rollback, lifecycle events |
| Runtime CLI commands | `python scripts/smoke_agent_runtime_cli.py` | ✅ DONE — `session-*`, `turn-*`, and `approval-*` commands |
| Runtime HTTP API | `python scripts/smoke_agent_runtime_api.py` | ✅ DONE — routes for turns, approvals, summaries, events and session transforms |
| Codex/CI agent audit runner | `python scripts/run_codex_agent_audit.py` | ✅ DONE — orchestrates registry + ledger + MCP + gateway + runtime + Chief of Staff smokes and writes reports |

## E. Structured-log requirement

Every smoke script must emit the structured step format from
`backend_first_debugging_paradigm.md`:

```text
[STEP n] what · [STATUS] ok/fail/skip · [REQUEST] endpoint · [INPUT] sanitized · [OUTPUT] summary · [ERROR] raw · [NEXT] implication
```

Secrets are never printed in full (presence + first4/last4 + length only).

## F. Definition of CLI-testable

A journey is CLI-testable when:
1. a single command reproduces it without the UI;
2. it exits non-zero on failure;
3. it prints a structured PASS/FAIL summary;
4. it runs offline where possible (`TPL_LLM_PROVIDER=template`) or documents the
   credential it needs.

## G. Current coverage verdict (updated 2026-06-30)

- Course authoring + quality (J4, J1 content): **CLI-testable ✅**.
- Verified calculators: **CLI-testable ✅** (via pytest/controls).
- Live API surface + exercise journey (J2): **CLI-testable ✅** (`scripts/smoke_api.py`, incl. F-EXO-3 value).
- Frontend↔backend connectivity: **CLI-testable ✅** (`npm run smoke:api`).
- Agentic Desk tools and Quant Pipeline tools: **CLI-testable ✅** (`scripts/smoke_tool_registry.py` + Chief of Staff validation).
- Conversation/session recall, task ledger, MCP adapter and interaction gateway:
  **CLI-testable ✅** (`scripts/smoke_conversation_ledger.py`,
  `scripts/smoke_agent_mcp_adapter.py`, `scripts/smoke_agent_gateway.py`,
  `scripts/smoke_agent_interaction_api.py`, `scripts/run_codex_agent_audit.py`).
- Codex/OpenClaw-style runtime primitives: **CLI-testable ✅**
  (`session-compact`, `session-fork`, `session-inject`, `session-rollback`,
  `session-events`, `turn-*`, `approval-*`, plus
  `scripts/smoke_agent_runtime_state.py`, `scripts/smoke_agent_runtime_cli.py`,
  and `scripts/smoke_agent_runtime_api.py`).
- Remaining: real legal/operator configuration, credential rotation after historical exposure,
  live/staging authentication and Stripe acceptance against deployed infrastructure,
  public observability/rollback evidence and the target-user pilot.
