# PRODUCTION_READINESS.md — ThePricingLibrary

> Local hardening validated 2026-11-15. A local PASS is not a deployed PASS.

Historical full release run: `reports/release_readiness_2026-07-25.json`
(2026-07-25 13:02 UTC): 22/22 local gates PASS, zero local artifact blockers,
eight external blockers, and four missing external evidence files. Current audit
evidence is in `reports/2026-11-09_technical-rl_delivery-audit.md` and the
independent `reports/2026-11-09_business-client_delivery-audit.md`; older rows
below retain their historical scope and dates.

Latest consolidated status: `reports/2026-11-10_delivery-audit-status.json`.
Technical and Business local verdicts PASS (Business 92/100); public delivery NO.

Historical targeted generation audit, 2026-11-10: the delivery PASS above did
not certify practical-exercise creation. Actual creation revealed an ignored
dividend, the wrong offline payer PV sign and incomplete question/rubric/render
behavior. That initial FAIL remains in the two exercise-generation audit reports.

Exercise corrections, 2026-11-11: Technical RL PASS locally (335 backend tests,
16 actual HTTP checks,17 browser checks) and independent Business Client Mystère
PASS local (92/100). Explicit dividend/rate units, correct
offline calculations, matched questions/answers/rubric, genuine tables/math,
private account persistence and idempotent recovery are implemented. Runtime
dependency audit is clean; the production artifact guard passes. Evidence:
`reports/2026-11-11_technical-rl_exercise-generation-fixes.md`; independent review:
`reports/2026-11-10_business-client_exercise-generation-fixes.md`. The verified
local mode uses the real RAG and templates; a live external LLM provider and
the deployed public infrastructure are not certified by these local checks.
Consolidated feature status: `reports/2026-11-11_exercise-generation-fixes-status.json`.

Local admin testing access, 2026-11-10 (F-WEB-10): Technical RL PASS and
independent Business Client Mystère PASS (96/100). Loopback development opens
admin with a signed session and server-side Pro test grant against an isolated
activity database. Completed modules restore after reload. The real corpus is
read-only; production bundles contain no local-admin mechanism, and preview's
test bootstrap/API return 404. Evidence: 15 real HTTP checks, 11 browser checks,
10 backend security tests and 9 independent business journeys (including all
12 private scripts). Reports:
`reports/2026-11-10_technical-rl_local-admin.md` and
`reports/2026-11-10_business-client_local-admin.md`. This is an explicit local
testing exception and does not alter the public production verdict below.

## Current verdict

Product hardening, 15 November 2026: the implementation and its bounded
acceptance criteria are recorded in `docs/PRODUCT_HARDENING_ACCEPTANCE.md` and
`reports/product-hardening-2026-11-14/`. This cycle adds the authenticated learner
CLI, true supported tool execution, faithful paper contracts, retained exercise
attempts, fourteen runnable references, server-owned Survival, notebook
execution, useful study exports and reviewed English curricula. English variants
are served only when their raw bytes match the independently accepted index.
The final consolidated `REPORT.md` in that folder supersedes earlier
feature-local verdicts for this changed scope. **Technical RL PASS local;
independent Business PASS local, 91.25/100 expert judgment.** The full backend
run passed 593 tests before the final additive progress patch; 75 focused tests
passed after it. These overlapping counts are not summed. The final production
build, packaged CLI outside the checkout, true bilingual content, retained-work
journeys and mobile budgets pass. Historical reports below remain dated evidence.

Optiquant IA is the intended entity; its complete legal/support configuration
remains unverified. No address from another product has been reused and no
missing field has been invented. Public checkout remains closed. Local technical
or Business PASS does not certify source rights,
real Supabase email, live billing, deployed infrastructure or target-user demand.

English Interview Lab and functional/UX corrections, 2026-11-14: **Technical RL
PASS local; independent Business Client Mystère PASS local, 94.25/100**. Evidence
is in `reports/interview-lab-2026-11-14/technical-review.md` and
`reports/interview-lab-2026-11-14/business-review.md`. Six original English cases,
six conceptual variants, answer/reasoning submission before feedback, immutable
account history, self-review, exact task/correction restoration, private export
and operator-only participation aggregates are implemented. Course position is
separate from completion. The library remains explicitly French; the released
Survival contract is one real Core wave, rather than six unpublished banks.

Validation includes 393 full backend tests before the final focused source/FX
corrections, 85 focused tests after those corrections, 26 Interview Lab browser
checks plus targeted 503/historical-reference rechecks, 22 corrected-journey
checks, 19 generation HTTP checks and 20 generation browser checks. Independent
public-checkout runs validate the code without private corpus/lesson/Product
assets: 334 backend tests plus 23 API checks in a fresh slim Python environment;
frontend build, math, artifact/security checks and 35 API tests in a separately
assembled public workspace. Public GitHub CI is explicitly code/offline scoped.

These are local implementation and usability verdicts. They do not certify a
deployed public sale, email delivery, a payment transaction, commercial source
rights, human review or market demand. The production-sale verdict below remains
closed. No new paid plan or checkout bypass was introduced for the signed pilot.

```text
Technical RL backend gate:     PASS local (593 full, then 75 focused; production guard and installed package)
Frontend build gate:          PASS (local production build, 2026-11-15)
Frontend dependency gate:     PASS runtime (0 alerts); WARN toolchain (11 moderate, no high/critical)
Frontend performance gate:     PASS local (FCP 2244 ms, LCP 3516 ms, CLS 0.01675; median/worst interaction 120/136 ms)
Entitlement/privacy gate:       PASS local (server identity/owner/plan; no external identity attestation)
Paid-course content gate:      PASS-CLOSED (12 FR preserved; 12 reviewed EN hash-accepted privately)
Starter Kit Client Mystere:    PASS-CLOSED (local artifact verified; pilot pending)
Live sale gate:                FAIL-CLOSED (14 local public values missing; public billing configured=false/mode=mock)
Overall production verdict:    NO
```

The codebase is now deployable without exposing the former unauthenticated
generation and billing surfaces. It is deliberately impossible to start a paid
checkout from the frontend until the operator's complete legal notice is present.

## Verified evidence

Courbe signature hero, 2026-11-14 (F-WEB-11): the user-selected proposal is now
implemented in the active home route. Technical RL **PASS** and independent
Business Client Mystère **PASS local** cover the full-contrast seeded curve,
neutral reference, actual final-point quote anchor, preserved authentic
horizontal navbar identity and real free calculator/course actions. The
production UX smoke passes all 12 journeys, with exact quote geometry at eight
widths from 320 to 1440 px, normal/reduced motion and no runtime/asset errors.
Typecheck, visual-shell, build and bundle checks pass; the largest JavaScript
asset remains 437077 bytes. The independent review covers eight browser checks
plus a focused 320 px menu/focus check. A pre-existing P2 remains: menu and
assistant are close at 320 px, with the menu center still operable. Reports and
captures are under `reports/visual-qa-2026-11-14-hero-signature/`. This is local
implementation evidence; no public deployment or commerce change was performed.

Whole-site delivery audit, 2026-11-09 (F-WEB-9): 128 desktop/mobile route/access
combinations and independent business review cover the active site. Corrections
include account confirmation/recovery, complete forum reading/replies, real
exercise export without seeded personal completion, truthful empty/error states,
mobile workspaces, missing-content 404s, Starter Kit unknown readiness, and
23 reviewed editorial correction groups across ten courses. A real CSV check
found and closed a scenario name/sample-count collision; the Lab now uses a
validated CLI engine, independent Python goldens and actual numeric UI/CSV checks.
The nine corrected browser journeys, full frontend aggregate and all 319 backend tests pass locally.
The strict course structure gate remains 12/12; it is not an exhaustive semantic
or real-user satisfaction certification. Final frontend aggregate/performance
and view captures are recorded in the audit report and machine-readable status;
the final view matrix is 128/128 PASS and the brand/navigation shell 12/12 PASS.

Fresh anonymous public checks: the API exists (`/health` 200), while `/ready`
and Starter Kit availability return 404 and `/billing/config` reports mock mode.
The public frontend assets still contain nine unsupported marketing markers.
This does not establish the display of every marker, but the currently published
artifact does not match the locally cleaned release contract. No deployment,
real account password change, real email or purchase was performed by these tests.

Accepted B and source-based navbar identity, 2026-11-09 (F-WEB-8): B is now fixed
on `/`. The actual TPL symbol and three-line lettering come from the original
`Visuels/ThePricingLibrary_logo.png`, traced into a 35,043-byte transparent SVG.
The source SHA and browser-rendered contour masks match the original; navbar
ink/white/vermilion styling follows the existing logo/banner. Twelve UX steps,
build/static/bundle gates pass. A constrained-mobile follow-up passes all budgets;
the first run's 504 ms interaction outlier and the passing 336 ms result are both
retained in the technical report rather than claiming a latency guarantee. See
`reports/2026-11-09_technical-rl_brand-navbar.md`,
`reports/2026-11-09_business-client_brand-navbar.md` and
`reports/visual-qa-2026-11-09-brand-navbar/`. Global launch blockers remain.

Layout proposals and branding correction, 2026-11-09 (F-WEB-7): the invented
mark/wordmark is removed in favor of plain product text. Two local alternatives
present the same illustrative market chart without a split hero or framed card:
editorial (centred copy, full-width graph below) and immersive (graph across the
background). Eleven production-browser steps and static/build checks pass.
The user has been given concrete alternatives to compare, not presumed to have
approved either. See `reports/2026-11-09_technical-rl_hero-layouts.md`,
`reports/2026-11-09_business-client_hero-layouts.md` and
`reports/visual-qa-2026-11-09-hero-layouts/`. This does not alter the global
production verdict or external launch requirements.

User-directed hero correction, 2026-11-09 (F-WEB-6): the approved floating navbar
is retained and the two-path illustrative SPX chart replaces the hero mini-pricer.
The headline and path statistics derive from the displayed red scenario; the
simulation is explicitly distinguished from historical/live quotes. Build,
static contracts and the ten-step production UX smoke pass locally. See
`reports/2026-11-09_technical-rl_hero-market.md`,
`reports/2026-11-09_business-client_hero-market.md` and
`reports/visual-qa-2026-11-09-hero-market/`. Earlier design evidence remains
available; this correction does not alter the overall release verdict.

Hero/navigation update, 2026-11-09: F-WEB-5 builds on the calm layout with a
floating compact navigation, editorial typography and a real interactive
Black-Scholes preview. The existing canonical engine drives its prices, Greeks
and curve; no market feed is implied. Ten local production-browser UX steps,
15 responsive captures and existing journey/build/source/engine gates pass.
Evidence is separate in `reports/visual-qa-2026-11-09-hero-modern/`; see
`reports/2026-11-09_technical-rl_hero-modern.md` and the independent
`reports/2026-11-09_business-client_hero-modern.md`. This remains a local design
iteration, without a deployment or real-user preference/satisfaction claim.

UX update, 2026-11-09: F-WEB-4 replaces the decorative home grid and nested
frames with open spacing, quiet surfaces, a free calculator entry point and
optional scenario details. Course/tool catalogues share the same hierarchy.
The local production build, browser UX matrix and existing entitlement journeys
pass; see `reports/2026-11-09_technical-rl_ux-calm.md` and the independent
`reports/2026-11-09_business-client_ux-calm.md`. This is local design evidence;
the overall production verdict and external release blockers above still apply.

| Area | Verdict | Evidence |
|---|---:|---|
| Backend tests | **PASS** | `python -m pytest -q --basetemp=.pytest_tmp_goal_final_audit_unique`: 319 passed; focused engine compatibility and production checks also pass; `verify_engine_quant.py`: all terminal-condition checks passed. |
| Production security | **PASS** | `python scripts/production_check.py`: JWT/RBAC, fail-closed readiness, rate limit, billing identity and API journey PASS. |
| Credential hygiene | **PASS-CLOSED (local)** | `python scripts/audit_secrets.py` finds no high-confidence OpenAI, Stripe or Supabase service-role material in current text artifacts; historical private notebook material was redacted. Provider-side revocation/rotation is still required. |
| Production observability | **PASS-CLOSED (local)** | Independent Technical RL: **PASS 98/100**; Business Client Mystère: **PASS-CLOSED local 94/100**. Server-generated request IDs and timings, sanitized 5xx logs, operator-only bounded-cardinality Prometheus metrics, and strict RUM ingestion pass API tests and `smoke_observability.py`; the real local HTTP smoke also performs a RUM POST and operator scrape while checking privacy. The production-only browser client sends no credentials/referrer and normalizes routes before transmission; Chromium proves no raw slug, query e-mail or token is emitted. No public scrape, deployed RUM sample, alert or staging rollback drill exists yet. |
| Docker runtime | **PASS (local Docker smoke)** | `python scripts/smoke_docker_runtime.py` builds the pinned-base image, starts a production-guarded non-root/read-only container with an isolated volume, proves `/health` and `/ready`, verifies anonymous denial for protected routes and metrics, verifies operator metrics access/privacy, and waits for the container healthcheck. This remains local evidence, not public staging evidence. |
| Docker deployment contract | **PASS-CLOSED (local)** | The resolved Compose JSON pins the release image by digest, binds port 8000 to loopback, maps subscription/one-shot settings, permits exactly the `api` service plus project-owned `tpl_data`, mounts the verified release read-only, and enforces non-root/read-only/capability controls. Eleven adversarial tests pass. The real registry digest, server values and deployed public health remain unverified. |
| Local HTTP deployment smoke | **PASS-CLOSED (local)** | `python scripts/smoke_local_deployment.py` starts a real ephemeral Uvicorn process in production guard mode with local HS256 fixture identity, seeds only a temporary entitlement, and proves health, readiness, sale availability, anonymous denial, manifest access and entitled ZIP SHA-256 download over HTTP. It intentionally does not prove Docker, Supabase or Stripe. |
| Local rollback smoke | **PASS-CLOSED (local)** | `python scripts/smoke_local_rollback.py` detects deliberate entitlement loss, restores a temporary SQLite backup across real API restarts and re-proves the entitled ZIP SHA-256 download. It does not prove registry digest rollback, proxy rollback or public staging recovery. |
| Authentication | **PASS (code)** | Direct Supabase access-token validation via issuer/audience/JWKS; ES256/RS256 allowlist. |
| Authorization | **PASS (code)** | Public/member/operator split; unknown mutations operator-only; member JWT cannot call operator routes. |
| Paid API entitlements | **PASS (offline)** | JWT subject and active server entitlement enforce Starter/Student/Pro ranks; free/member keys and insufficient plans receive 403 before handlers. Survival requires Student; AG-UI and desk run/state require Pro. |
| Billing identity | **PASS (offline)** | Checkout and entitlement derive `user_id`/email from the signed subject, not browser email. |
| Billing lifecycle | **PASS (offline)** | Signed completion activates; cancellation, refund and chargeback revoke; event replay idempotent. |
| Frontend entitlement | **PASS (code)** | Central plan matrix gates courses, tools, Lab, exercises, Survival, notebooks, API and agent room. |
| Course confidentiality and platform integrity | **PASS (local dual security validation)** | Independent Technical RL **PASS 99/100** with no P0/P1. Paid Markdown, prose, derivations, blueprints and legacy course widgets are absent from the public build; the course shell receives modules/formulas/labs/resources only after the bearer-bound backend entitlement. Progress is atomic and owner-bound, votes are fixed server-side, public DTOs are pseudonymised, admin authority comes from signed `app_metadata`, and unverified Survival scores are excluded. Anonymous/Free/Starter/Student/Pro Chromium journeys, delayed success and HTTP 503 Survival saves, 9 focused backend tests, 21 platform checks and the production-security smoke pass. |
| Paid-course commercial quality | **PASS-CLOSED (local content gate)** | The strict executable audit passes **12/12** private course scripts at threshold **98**, each scoring 100/100 for structure, depth, grounding, practice, UI blocks and both personas. The authenticated browser matrix verifies the 12 unique scripts, references, widgets and tool links. A real buyer pilot and live entitlement journey remain unverified. |
| Frontend quality | **PASS (local technical validation)** | The current `npm run audit:technical` run passes in 274.3 s, including auth-race, deterministic/cross-engine/backend/worker tools, RUM/environment/business contracts, production builds, browser journeys, bundles and performance. The current bundle has 34 JavaScript assets under the 500,000-byte cap (maximum 394,423); the root and course shell remain lazy-loaded. KaTeX remains course-lazy and the Supabase client dynamic. The remaining dependency warning is limited to two upstream moderate React Router advisories; no high/critical advisory is accepted by the release gate. |
| Model calibration | **PASS (local dual validation)** | Independent Technical RL **PASS 99/100** and Business Client Mystère **PASS 96/100**. Black-76, Hagan SABR and Fourier Heston golden cases, deterministic bounded fits, real/fail-closed CSV parsing, worker isolation, residual/model-risk diagnostics and active-route bundle delivery pass. An isolated production Chromium journey reaches the real signed-in Student route with no paid profile metadata, obtains access only through an intercepted bearer-bound backend entitlement, runs all three models, validates/uploads/downloads CSV/JSON, records actual run history and passes mobile/desktop visual QA with zero page, console or critical-request errors. The former random parameters, fake upload, unfinished 3D and legacy quadratic/fake-model paths are absent from production assets. This local contract proof is not a live Supabase/Stripe/staging acceptance test. |
| Yield-curve construction | **PASS (local dual validation)** | Independent Technical RL **PASS 99/100** and Business Client Mystère **PASS 96/100**. A shared JS/Python fixture covers deposits, sequential FRAs, explicitly adjusted STIR futures, sparse swaps and negative rates. Log-DF interpolation constructs every coupon; exact repricing, interval-correct forwards, CSV/JSON contracts and adversarial failures pass. The isolated production Chromium journey proves anonymous locking, bearer-bound Starter access without profile plan metadata, 7/7 repricing with max PV residual `2.05e-15`, stale-result clearing, valid/invalid CSV, export, diagnostics, real session history, 390 px layout and zero page/console/critical-request errors. This educational mono-curve scope declares the absence of calendars, stubs, extrapolation and OIS/projection multi-curve support. Local intercepted auth is not staging/live evidence. |
| Realized-volatility analysis | **PASS (local dual validation)** | Independent Technical RL **PASS 100/100** and Business Client Mystère **PASS 97/100**. One canonical JSON contract governs Python and JavaScript; five OHLC estimators, `1e-13` recursive parity, formatting-invariant SHA-256, byte-identical exports, strict fail-closed parsing, dated quality warnings and local worker isolation pass. Chromium proves anonymous/inactive denial, bearer-bound Starter access, contextual results, actionable alerts, estimator guidance, toggleable five-series comparison, real exports/history, sticky 390/390 px audit table and zero OHLC leakage or browser errors. This remains local intercepted-auth evidence, not a deployed Supabase/Stripe acceptance test. |
| Payoff strategy analysis | **PASS (local dual validation)** | Independent Technical RL **PASS 99/100** and Business Client Mystère **PASS 97/100**, with no P0/P1. One v1.0.1 JSON contract governs Python and JavaScript; eight strategies agree recursively to `1e-12`, analysis IDs and CSV evidence are identical, exact analytical tails/bounds/breakevens replace grid inference, five signed Greeks and premium/multiplier conventions are explicit, and unsupported path-dependent products fail closed. Chromium proves anonymous/inactive denial, bearer-bound Starter access, off-window roots at 195/205, finite/unlimited risk, JSON/two-CSV exports, stale clearing, immutable multi-currency history through Run 10, 390/390 px layout and zero pricing leakage or browser errors. This remains local intercepted-auth evidence, not a deployed Supabase/Stripe acceptance test. |
| Monte Carlo pricing/risk | **PASS (local dual validation)** | Independent Technical RL **PASS 99/100** and Business Client Mystère **PASS 97/100**, with no P0/P1. One v1.0.0 JSON contract governs Python and JavaScript; six P/Q, variance-reduction, Asian and degenerate scenarios agree recursively within `1e-11`, share analysis IDs and emit byte-identical terminal/path CSV evidence. VaR/ES use explicit non-negative loss conventions, pricing exposes uncertainty/convergence and every active backend/course consumer delegates to the canonical seeded engine. Chromium proves anonymous/inactive denial, bearer-bound Starter access, Q pricing, Asian control variate, P loss risk, real exports, stale clearing, history, worker execution, a 44 px CTA at 390/390 px and zero simulation leakage or browser errors. This remains local intercepted-auth evidence, not a deployed Supabase/Stripe acceptance test. |
| Binomial CRR / American options | **PASS (local dual validation)** | Independent Technical RL **PASS 100/100** and Business Client Mystère **PASS 98/100**, with no P0/P1. One v1.0.0 JSON contract governs Python and JavaScript; eight European, American, dividend, degenerate, signed and sensitivity-boundary scenarios agree recursively within `2e-10`, share analysis IDs and emit byte-identical convergence/frontier CSV evidence. Invalid probabilities and schemas fail closed, zero volatility/expiry are explicit, Rho respects the admissible CRR domain, negative-rate American-call diagnostics remain honest, and AG-UI preserves the requested step count. Chromium proves anonymous/inactive denial, bearer-bound Student access, American put and dividend-call frontiers, honest European Black-Scholes convergence, five signed Greeks, retained node decisions, real SHA-bound exports/history, stale clearing, worker execution, a 44 px CTA at 390/390 px and zero calculation leakage or browser errors. This remains local intercepted-auth evidence, not a deployed Supabase/Stripe acceptance test. |
| Fixed-rate Bond pricing and risk | **PASS (local dual validation)** | Independent Technical RL **PASS 99/100** and Business Client Mystère **PASS 98/100**, with no P0/P1. One v1.0.0 JSON contract governs Python and JavaScript; eight date, quote, negative-yield, frequency and end-of-month cases agree recursively within `2e-11`, share SHA-256 analysis IDs and emit byte-identical cash-flow/scenario CSV evidence. ACT/ACT ICMA and normalized 30E/360 accrued interest, clean/dirty identity, bounded YTM inversion, exact DV01, duration, convexity, signed position risk and shocked repricing are explicit; invalid schemas and chronology fail closed. Chromium proves anonymous/inactive denial, bearer-bound Starter access, par and discount quotes, negative yield, risk/cash-flow evidence, real SHA-bound exports/history, stale clearing, worker execution, a 44 px CTA at 390/390 px and zero calculation leakage or browser errors. This remains local intercepted-auth evidence, not a deployed Supabase/Stripe acceptance test. |
| Implied-volatility surface quality | **PASS (local dual validation)** | Independent Technical RL **PASS 99/100** and Business Client Mystère **PASS 98/100**, with no P0/P1. One v1.0.0 JSON contract governs Python and JavaScript; six clean, exact-node, boundary, calendar, butterfly and missing-spread cases agree recursively within `2e-11`, share SHA-256 analysis IDs and emit byte-identical points/diagnostics CSV evidence. The engine uses `k = ln(K/F)` and `w = sigma^2 T`, interpolates only inside the rectangular grid and reports discrete bounds, vertical, butterfly and calendar flags without sorting, filling, clipping or repair. Chromium proves anonymous/inactive denial, bearer-bound Student access, a real local CSV, clean and violation fixtures, slices/ATM term structure/heatmap, real same-SHA exports/history, stale clearing, worker execution, a 44 px CTA at 390/390 px and zero quote leakage or browser errors. This remains local intercepted-auth evidence, not a deployed Supabase/Stripe acceptance test. |
| Black-Scholes pricing and implied volatility | **PASS (local dual validation)** | Independent Technical RL **PASS 99/100** and Business Client Mystère **PASS 98/100**, with no feature-local P0/P1. One canonical v1 input contract governs Python and JavaScript; eight value, dividend, negative-rate, IV, expiry, zero-volatility, declared forward-ATM kink and signed-scale cases agree recursively within `2e-11`, share SHA-256 analysis IDs and emit byte-identical scenario/sensitivity CSV evidence. Strict schemas reject coercion and unknown fields; bounded IV, five unit-labelled Greeks, signed positions, exact shocks, sensitivity bounds and limiting conventions are explicit. Chromium proves anonymous free access, ATM price/parity, a 20% IV round-trip, real same-SHA exports, stale clearing, worker execution, session history, six contextual Free/Starter/Student continuation routes, a 44 px CTA at 390/390 px and zero calculation leakage or browser errors. This feature PASS does not waive the live-sale gate. |
| Frontend dependencies | **WARN** | React Router is pinned to the latest registry-compatible client version **6.30.4**; `npm audit --omit=dev` reports two moderate upstream advisories and no high/critical issue. The application is client-only and does not enable React Router SSR/RSC surfaces, but the dependency should be upgraded when the registry publishes a compatible patched line. |
| Navigation security | **PASS (local contract)** | A global capture boundary blocks malformed backslash/protocol-relative and dangerous-scheme anchor targets before React Router handles them; all application `useNavigate` call sites use the guarded wrapper. Seven unsafe and six safe fixtures pass the runtime smoke, and diagnostics never include target values. The dependency advisory remains until a compatible patched React Router line is available. |
| Retired public surfaces | **PASS (local build gate)** | The historical `public/agent-room-kit` design kit is blocked in dev/preview and removed from `dist` after build; the release gate prevents its old live-market mock copy from becoming a public product surface. |
| Course catalogue contract | **PASS (local)** | `python scripts/audit_course_manifest.py` maps all 12 active catalogue entries to private scripts and exact module counts. The frontend exposes one canonical manifest, while the client sees source excerpt/pedagogical rewrite/verified generation labels. |
| Course objective contract | **PASS (local)** | `python scripts/audit_course_objective.py` confirms 12/12 learner-facing courses have the required desk structure, five answered course-specific quiz questions with no repeated visible stems, and explicit calculator/scenario routing. |
| Tool contract and data transparency | **PASS (local)** | `npm run smoke:product-contract` validates nine tools with explicit engine, inputs, conventions, limits, non-live data status and course/exercise links. Market history API responses expose source, status, as-of date, unit and non-executable-quote limitations. |
| Trust | **PASS (static audit)** | Synthetic community/mentor/admin/challenge claims removed; source internals hidden; deterministic Starter Kit golden case corrected. |
| Legal UX and source rights | **PASS-CLOSED** | Terms, privacy, refund, legal, contact and electronic cancellation pages exist; missing operator fields disable sales. Commercial sale also requires written clearance/attribution for the external source corpus; no such operator evidence is present yet. |
| Starter Kit fulfillment | **PASS-CLOSED (code)** | One-shot payment, JWT-bound product entitlement, signed/idempotent webhook, real-manifest/checksum-gated download and product-only refund/chargeback revocation pass locally. Sale remains closed until final release paths and Stripe price are configured. |
| Starter Kit frontend | **PASS-CLOSED (local)** | Lazy-loaded authenticated workspace, product-specific success/cancel states, public backend availability, seven deliverables and secure bearer download pass the browser journey. Anonymous users receive no checkout control. |
| Starter Kit product | **PASS-CLOSED (local artifact)** | The real Excel dashboard passes its executable contract and golden cases; `release/manifest.json` is `ready:true`, the immutable `starter-kit-v1.0.0.zip` contains **7/7** deliverables, and the checksum bundle verifier passes. Desktop recalculation/visual QA and a five-user target pilot remain external validation gates. The current release report confirms that `staging_evidence.json`, `rollback_evidence.json` and `pilot_evidence.json` are absent; no synthetic replacements were created. |

Independent local re-score after the entitlement, privacy, course and bundle
corrections: Technical RL is **PASS-CLOSED locally** for the implementation and
the reproducible release gates; the Business Client Mystère static checks pass
for clarity/trust/fulfilment, but a real five-user pilot is still absent. Live
sale readiness remains **FAIL-CLOSED** because infrastructure, accountable
operator data and staging evidence are incomplete.

## Required production configuration

### Backend secrets and identity

```text
TPL_ENVIRONMENT=production
TPL_API_KEY=<random secret, >=32 chars>
TPL_OPERATOR_API_KEY=<different random secret, >=32 chars>
TPL_RATE_LIMIT_PER_MINUTE=<positive integer>
TPL_AUTH_ISSUER=https://<project-ref>.supabase.co/auth/v1
TPL_AUTH_JWKS_URL=https://<project-ref>.supabase.co/auth/v1/.well-known/jwks.json
TPL_SOURCE_RIGHTS_CLEARED=true  # only after rights_clearance_evidence.json passes
TPL_AUTH_AUDIENCE=authenticated
TPL_AUTH_ALGORITHMS=ES256,RS256
STRIPE_SECRET_KEY=...
STRIPE_WEBHOOK_SECRET=...
STRIPE_PRICE_STARTER=...
STRIPE_PRICE_STUDENT=...
STRIPE_PRICE_PRO=...
STRIPE_PRICE_STARTER_KIT=...
TPL_STARTER_KIT_BUNDLE_PATH=<absolute path to starter-kit-vX.Y.Z.zip>
TPL_STARTER_KIT_MANIFEST_PATH=<absolute path to release/manifest.json>
TPL_STARTER_KIT_SUCCESS_URL=https://<public-origin>/#/starter-kit/success
TPL_STARTER_KIT_CANCEL_URL=https://<public-origin>/#/starter-kit/cancel
```

For the repository Compose recipe, populate
`Tools/pricinglibrary_rag_backend/.env.production.example` into a server-only
`.env.production`. It additionally requires `TPL_IMAGE_REPOSITORY`,
`TPL_IMAGE_DIGEST`,
`TPL_PUBLIC_ORIGIN`, `TPL_STARTER_KIT_RELEASE_DIR` and
`TPL_STARTER_KIT_BUNDLE_FILENAME`; the release directory is mounted read-only at
`/releases/starter-kit`.

Subscription success/cancel URLs must target `/#/billing/success` and
`/#/billing/cancel`; the one-shot Starter Kit uses the dedicated
`/#/starter-kit/success` and `/#/starter-kit/cancel` routes listed above.
All Stripe secrets remain backend-only.

### Public legal configuration

The keys listed in `WEBSITE/thepricinglab/.env.production.example` must contain
the real operator name/form/capital, address, registration, VAT status, phone,
publication director, host notice, consumer mediator and monitored support email.
The Starter Kit also requires an explicit public one-shot price and the sales
activation flag; the backend availability response must independently be ready.
`npm run check:production-env` must PASS. Placeholder values are forbidden.
`VITE_TPL_RUM_ENABLED=true` and an HTTPS non-local API origin are also mandatory
for the live build; the committed example intentionally remains disabled.

## Open release blockers

The operator-facing gate matrix, with owners, evidence schemas, validator
commands and acceptance criteria, is maintained in
`reports/2026-07-25_external-launch-gate-matrix.md`. The current machine-readable
snapshot is `reports/release_readiness_2026-07-25.json`; missing staging,
rollback and pilot evidence must be produced by real executions and must not be
replaced with synthetic records.

1. **Operator input required:** real legal identity, host, mediator, phone and
   support mailbox have not been supplied. Current gate correctly returns FAIL.
2. **Credential rotation required:** historical notebooks contained private
   provider material; current files are redacted and `audit_secrets.py` passes,
   but any previously exposed OpenAI/Stripe/Supabase credentials must be
   revoked and replaced outside the repository before deployment.
3. **Live infrastructure required:** Stripe live/test products, webhook endpoint,
   Supabase issuer/JWKS and reverse proxy are not configured or exercised here.
4. **Staging acceptance required:** run three consecutive purchases, one
   cancellation and one refund; verify entitlement after refresh without SQL.
5. **Deployment required:** publish the new frontend/backend artifacts and prove
   the public bundle no longer points to localhost or a stale asset. Verify an
   authenticated Prometheus scrape, browser RUM reception, correlation through
   the reverse proxy, an alert and an exercised rollback on that deployment.
   The read-only probe currently finds stale unsupported marketing claims on
   `https://thepricinglibrary.com`; this domain must be redeployed and return
   `PUBLIC DEPLOYMENT PROBE PASS` before public sale.
6. **Legal review required:** an accountable operator should approve CGV,
   privacy/retention, withdrawal/refund and mediation wording for the actual entity.
7. **Scale boundary documented:** v1 is explicitly single-host with SQLite rate
   limiting and one API service/shared volume. Multi-host scale-out remains out
   of scope until Redis or an equivalent shared store is provisioned.
8. **Starter Kit commercial activation required:** configure the one-shot Stripe
   price and both server-only paths, then exercise purchase/refund/chargeback in
   staging against the verified seven-deliverable bundle.
9. **Buyer evidence required:** complete desktop/mobile QA and a five-user pilot
   with at least four satisfied target users and no incorrect number or blocking
   file.
10. **Toolchain dependency follow-up:** the runtime dependency gate is now clean
   after the November audit, including the React Router update. Eleven moderate
   development-tool advisories remain in the full npm audit; none are high or
   critical. Track the upstream minimatch/selector-parser toolchain fixes.

## Release command gates

```text
cd Tools/pricinglibrary_rag_backend
pytest -q --basetemp=.pytest_tmp_release
python scripts/production_check.py
python scripts/audit_course_quality.py --dir pricinglibrary_rag/course_scripts --threshold 98 --json
python scripts/check_deployment_contract.py --env-file .env.production
python scripts/audit_secrets.py
python -m pytest -q tests/test_deployed_acceptance.py --basetemp=.pytest_tmp_acceptance
python scripts/release_readiness_report.py --json-out ../../reports/release_readiness.json

cd WEBSITE/thepricinglab
npm audit
npm run audit:technical
npm run audit:performance
npm run check:production-env
```

The local technical/artifact gates and course-quality command now pass. The
production environment contract and external evidence gates still fail closed
for documented operator, infrastructure and buyer-validation inputs. Therefore
the repository must not be described as already in production or already ready
to sell.
