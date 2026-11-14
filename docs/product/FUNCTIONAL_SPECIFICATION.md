# FUNCTIONAL_SPECIFICATION.md — ThePricingLibrary

> Grounded in the real implementation (2026-06-06). Two apps:
> **Backend** `Tools/pricinglibrary_rag_backend` (Python, the engine) and
> **Frontend** `WEBSITE/thepricinglab` (Vite/React, the dashboard; live app is
> `src/claude/ClaudeFrontend.jsx`). Every meaningful feature below carries
> acceptance criteria. A feature without acceptance criteria is not ready.

---

## 1. Product overview

The English interview pilot is specified in `docs/INTERVIEW_LAB_ACCEPTANCE.md`
(2026-11-14). Its explicit attempt/transfer checks supplement the legacy library;
they do not turn course completion or self-reviewed prose into certified mastery.

A practice-first quant-finance learning platform. A local-first Python RAG engine
ingests a finance PDF corpus, qualifies it pedagogically, and generates grounded,
verified courses and exercises. A React frontend renders a deliberately short
static Black-Scholes preview; complete course Markdown is delivered by the
backend only after signed-identity and plan checks. The browser also runs
in-browser tools/calculators and requests practice exercises from the engine.

## 2. Target users

See `PRODUCT_PHILOSOPHY.md`. Students/juniors in market & quantitative finance;
instructors as a secondary audience.

## 3. User roles

| Role | Capabilities | Auth |
|------|--------------|------|
| Anonymous visitor | Browse site, read the Black-Scholes preview, use free tools | none |
| Authenticated learner | Track progress, save exercises, tiered course access and access owned one-shot products | Supabase JWT; server-side entitlement is authoritative |
| Instructor / content owner | Run the backend CLI: ingest corpus, generate courses/exercises, audit quality | local CLI / server operator |
| Operator (deploys) | Run/serve the backend API, configure env, deploy frontend | server / CI |

> Paid access is never inferred from signup/profile metadata. The frontend sends
> the Supabase access token and the backend resolves the active entitlement bound
> to its verified subject.

## 4. Core user journeys

### J1 — Preview or read a grounded course (IMPLEMENTED, entitlement-aware)
Anonymous visitor → Courses → Black-Scholes → reads a short static preview.
Paid learner → opens an entitled course → browser sends the signed session token
→ backend verifies the active plan → complete Markdown is rendered with KaTeX.
- Public data path: only `/course-scripts/vanilla-options-quote.md` (preview).
- Paid data path: `GET /courses/{course_id}/script` with bearer token.
- Locked courses do not load or render prose, formulas, module lists or sources.

### J2 — Generate & solve a practice exercise (LIVE backend or local fallback)
Visitor → Exercises/Practice → picks topic/params → engine returns a grounded
exercise with a verified correction; if backend unreachable, a local fallback
exercise is generated and **labelled as such**.
- Data path: `practiceEngine.js` `POST {VITE_TPL_RAG_API_URL||127.0.0.1:8000}/agent/exercise`;
  health via `GET /health`.

### J3 — Use a tool/calculator (LIVE, client-side)
Visitor → Tools → Black-Scholes pricer / payoff visualizer / Monte Carlo / vol /
bond / curve. Pure in-browser computation.

### J4 — Author content (operator, CLI)
Operator ingests a corpus, generates the course scripts, audits quality, and
packages the full scripts in the backend-private `pricinglibrary_rag/course_scripts/`
directory. Only the public preview is promoted to `public/course-scripts/`.
- Data path: backend CLI + `scripts/generate_course_scripts.py` + `scripts/audit_course_quality.py`.

### J5 — Buy and retrieve the Starter Kit (IMPLEMENTED, sale fail-closed)
Learner → Starter Kit workspace → sign in → public availability check → one-shot
Stripe checkout → signed webhook → product entitlement → manifest → authenticated
bundle download. Product success/cancel routes are distinct from subscriptions.
- Frontend: `/starter-kit`, `/starter-kit/success`, `/starter-kit/cancel`.
- Backend: `/products/market-finance-starter-kit/*`.
- The browser renders no checkout control for anonymous visitors and enables
  purchase only when legal, price, explicit frontend activation, backend checkout
  and the verified 7/7 artifact gate all agree.

## 5. Functional modules

| Module | Backend | Frontend |
|--------|---------|----------|
| Ingestion & corpus | `ingestion.py`, `document_loader.py`, `storage.py` (SQLite+FTS5) | — |
| Pedagogical qualification | `pedagogy.py` (17 content types, scoring, gaps) | — |
| Retrieval | `retrieval.py` (hybrid vector+BM25, `usable_only`, `min_quality`) | — |
| Course generation and delivery | `generation.py`, `course_blocks.py`, entitlement-aware `GET /courses/{course_id}/script` | preview/private renderer in `ClaudeFrontend.jsx` |
| Exercise generation | `generation.py` `/agent/exercise` | `practiceEngine.js` |
| Verified calculators | `calculators.py` (BS, swap DV01, bond, barrier, CDS CS01, VaR, book greeks) | client-side pricers/tools |
| Evaluation | `evaluation.py`, `/evaluation/*` | — |
| Library of generations | `storage.py` `generation_runs`, `/library/*` | — |
| Agent tool registry | `tool_registry.py`, `/agent/tools/*`, CLI `tool-*` | Agent Room / operators |
| Starter Kit commerce | Stripe checkout, product entitlement, availability, manifest and download | Authenticated product workspace and return states |

## 6. Detailed feature list (with IDs)

- **F-ING-1** Ingest PDFs/TXT/MD → chunk → classify → store with pedagogy columns.
- **F-PED-1** Classify each chunk (content_type, pedagogical_value, quality_score, usable_for_course).
- **F-PED-2** Corpus pedagogy stats (`pedagogy-stats`, `/sources/pedagogy-stats`).
- **F-RET-1** Hybrid retrieval filtered to usable, high-quality chunks.
- **F-CRS-1** Generate a course: per-lesson authored prose grounded in `[Sx]`.
- **F-CRS-2** Verified worked example computed by `calculators.py`.
- **F-CRS-3** Corrected exercises + 5-question MCQ quiz + summary.
- **F-CRS-4** Provenance labelling `[extrait]/[reformule]/[genere]` + gap flags.
- **F-CRS-5** Course quality gate (`audit_course_quality.py`, PASS ≥ 70; boilerplate, formula-leak, grounding checks).
- **F-CRS-6** Course-content confidentiality: the production web bundle contains
  only the bounded Black-Scholes preview. Full Fundamentals/Advanced/Complex
  modules, prose, formulas, labs, resources and Markdown are served from a closed
  backend course/file map after Starter,
  Student or Pro entitlement validation and with `private, no-store` caching.
  Direct public paths, public manifests, JavaScript blueprints/widgets and locked
  React views must not expose it; the release smoke scans every emitted JS chunk.
- **F-PLAT-1** Signed platform identity and integrity: production community
  authors, comments, votes, job applications, progress and Survival runs derive
  their user identity from the verified token. Progress is owner-readable only,
  duplicate lesson events and votes are idempotent, leaderboard points use fixed
  server weights, and operational counts are operator-only.
- **F-LAB-1** Trading Lab plan truth: `/lab` lands Student users on the Student
  exercises surface; Backtest is visibly Pro and the Backtest component is not
  mounted for an insufficient plan, preventing any `/strategy/*` request.
- **F-EXO-1** Generate a practice exercise grounded in the corpus (`/agent/exercise`).
- **F-EXO-2** Local fallback exercise when backend is unreachable, labelled as fallback.
- **F-EXO-3** Verified numeric correction (answer key) from calculators.
  Correction acceptance (2026-11-11): explicit continuous dividend yield reaches
  the canonical prices, parity and Greeks; unsupported or malformed numeric
  constraints are rejected without a substituted scenario. Requested question
  count equals question/answer/rubric count, with 100 total points and tasks
  adapted to difficulty/format. The learner sees rendered Markdown/math, no
  authoring instructions, and distinct template/LLM/offline modes. An offline
  reference case identifies its own inputs and never claims to apply the custom
  prompt. Authentication/authorization/validation errors never become fallback
  successes. JSON and Markdown exports retain the same saved case.
- **F-EXO-4** Account exercise library: API-generated cases are stored under the
  verified JWT subject. A new browser can list and reopen them; another subject
  cannot list, read or overwrite them. The browser cache is subject-scoped and
  unowned historical entries are not silently assigned. Retry keys are scoped
  to the owner and prevent duplicate creations; key reuse with changed inputs
  fails explicitly. A local-only offline example is labelled as such.
  The 2026-11-10 re-audit found an ignored dividend and a wrong offline payer
  sign. Those findings are retained historically in the audit reports. The
  2026-11-11 corrections and actual creation/retrieval/error/assessment checks
  are documented in `reports/2026-11-11_technical-rl_exercise-generation-fixes.md`
  and `reports/2026-11-10_business-client_exercise-generation-fixes.md`. Local
  template/RAG evidence is separate from deployed/provider acceptance. Merely
  opening or exporting a predefined exercise never certifies this journey.
- **F-CAL-1** Client-side tools: BS pricer, payoff, Monte Carlo, IV, binomial,
  vol surface, bond and curve.
- **F-CAL-2** Deterministic volatility-model calibration: a shared browser/CLI
  engine validates weighted implied-volatility surfaces, fits Black, Hagan
  lognormal SABR and characteristic-function Heston under explicit forward-measure
  conventions, enforces parameter bounds, supports real fail-closed CSV input and
  exposes residual, convergence and model-risk diagnostics. Random parameters,
  fake uploads, hidden noise and unfinished result placeholders are forbidden.
- **F-CAL-3** Deterministic single-curve construction: a shared browser/CLI
  engine bootstraps spot deposits, sequential FRAs, STIR futures converted with
  an explicit convexity adjustment, and spot-starting par swaps. Sparse swap
  pillars use declared log-linear discount-factor interpolation and a bounded
  deterministic root solve so no coupon is omitted. The result exposes positive
  discount factors, continuous and annual zero rates, interval-correct forwards,
  instrument repricing residuals, shape warnings, conventions, limitations,
  versioned CSV/JSON contracts and source status. Hidden extrapolation, implicit
  stubs/calendars, ambiguous quote units, random data and silent fallback are
  forbidden; this educational v1 must identify itself as mono-curve rather than
  claim production OIS/projection multi-curve support.
- **F-CAL-4** Deterministic realized-volatility and data-quality lab: a shared
  browser/CLI engine consumes a user-supplied, chronological OHLC CSV and
  computes close-to-close, Parkinson, Garman-Klass, Rogers-Satchell and
  Yang-Zhang estimates over identical sessions. Annualization and rolling-window
  conventions are explicit; internal/export values use decimals and UI values
  use percentages. Strict schema, positive-price, OHLC-consistency, date,
  delimiter, size and stale-run gates fail closed. Gaps, possible corporate
  actions, robust outliers, flat bars, repeated closes, missing expected days,
  unknown adjustment basis and estimator divergence remain in the calculation
  but are surfaced as dated warnings; no row is silently sorted, dropped,
  winsorized, resampled, interpolated or imputed. A dedicated worker produces
  deterministic, versioned JSON evidence plus rolling and observation/flag CSV
  exports with SHA-256 provenance. `fixtures/realized_volatility_contract.json`
  is the canonical cross-engine authority for exact CSV column order, limits,
  configuration enums, diagnostic thresholds, canonical-dataset hashing,
  result keys and export headers; hashing the raw upload text is forbidden. The
  active Starter route must accept real
  local upload and one clearly labelled deterministic teaching fixture; asset
  buttons, random walks, fake uploads, hidden market-data claims and volatility
  forecasts/trading signals are forbidden.
- **F-CAL-5** Deterministic vanilla-option strategy and terminal P&L lab: one
  canonical browser/CLI contract values European call/put legs with
  Black-Scholes-Merton, then separates gross intrinsic payoff from net terminal
  P&L including the explicitly selected entry premium. Every leg declares type,
  side, strike, positive integer quantity and premium source (`model` or
  `manual`); the strategy declares spot, volatility, maturity, risk-free rate,
  dividend yield, currency and contract multiplier. Model and manual premiums
  must never be conflated with live market quotes. Signed portfolio Delta,
  Gamma, Vega per volatility point, Theta per calendar day and Rho per rate
  point use the same visible assumptions. Exact piecewise-linear analysis over
  the non-negative terminal-price domain supplies breakevens and finite versus
  unlimited maximum profit/loss; a plotted spot window must never be used to
  infer those bounds. Strict schemas, limits, duplicate IDs and non-finite or
  out-of-domain inputs fail closed. The active Starter route provides bounded
  presets, per-leg audit, scenario decomposition, successful session history
  and versioned JSON/curve/scenario exports. Fake save actions, hidden market
  assumptions, hard-coded Greek scenarios, random prices, silent coercion and
  divergent legacy payoff engines are forbidden.
- **F-CAL-6** Deterministic Monte Carlo pricing and position-risk lab: one
  canonical, versioned Python/JavaScript contract simulates GBM paths with a
  visible Park-Miller seed and Box-Muller transform. Pricing uses the declared
  risk-neutral measure Q, drift `r-q`, discounting and European or arithmetic-
  Asian payoffs; position risk uses the declared physical measure P and reports
  P&L, `Loss = -P&L`, non-negative loss VaR and expected shortfall at 95% or
  99%. The path chart, terminal histogram, pricing/risk statistics and exports
  must all derive from the same observations, seed and step count. Plain,
  antithetic and terminal-spot control-variate methods expose effective sample
  size, standard error, 95% confidence interval, N/4→N convergence and any
  available Black-Scholes benchmark without inventing an Asian closed form.
  ACT/365F, currency, position, quantity, multiplier, model limitations and
  educational/non-market-data status are explicit. Strict schemas, numerical
  domains, path/step limits, method compatibility and finite inputs fail closed.
  The active Starter route runs in a worker, retains successful session history,
  emits SHA-256-bound JSON plus terminal/path CSV evidence, and is usable at
  390 px. Hidden seeds, P/Q conflation, split simulations, signed-P&L quantiles
  mislabeled as VaR, fake sample counts, silent clamping and divergent active
  backend/course engines are forbidden.
- **F-CAL-7** Deterministic European/American option and CRR lattice lab: one
  canonical, versioned Python/JavaScript contract prices call/put contracts
  under the risk-neutral measure Q with `u=exp(σ√dt)`, `d=1/u`, continuous
  dividend yield, ACT/365F and explicit currency, long/short position, quantity
  and contract multiplier. Every non-degenerate run must prove the CRR
  probability is inside `[0,1]`; invalid probabilities, unsafe numerical ranges,
  non-finite values, fractional step/quantity counts and unknown fields fail
  closed without probability clamping or step reduction. Expiry and zero
  volatility use explicit deterministic limits. American valuation retains a
  same-tree European price, non-negative early-exercise premium, node-level
  intrinsic/continuation/decision evidence and a dated optimal-stopping frontier;
  European and same-tree European values expose an honest Black-Scholes
  benchmark. Raw N and N−1 prices, their gap/average and N/8→N convergence are
  diagnostic rather than silently substituted. Delta/Gamma/Theta come from
  retained tree levels when available, while domain-respecting finite
  differences report Vega per volatility point and Rho per rate point; signed
  position Greeks use the declared scale. The active Student route runs in a
  worker, retains successful session history, emits SHA-256-bound JSON plus
  convergence/frontier CSV evidence and is usable at 390 px. Divergent active
  lattice implementations, fake live-data claims, hidden probability repair,
  an American price compared directly with Black-Scholes as if it were a closed
  form, and stale invalid results are forbidden.
- **F-CAL-8** Deterministic fixed-rate bond pricing and risk lab: one canonical,
  versioned Python/JavaScript contract values regular fixed-rate bullet bonds
  per 100 nominal from either an annual nominal yield-to-maturity or a clean
  price. Settlement and maturity are strict ISO dates; a maturity-anchored,
  unadjusted schedule preserves end-of-month dates and accepts only annual,
  semi-annual, quarterly or monthly regular coupons. ACT/ACT ICMA or 30E/360
  determines the elapsed coupon fraction, with the hard identity dirty price =
  clean price + accrued interest. Price-to-yield inversion uses a bounded
  deterministic root solver and exposes iterations and residual.
  Macaulay/modified duration, analytical convexity, exact symmetric ±1 bp DV01,
  signed nominal scaling, exact parallel-shock P&L and duration/convexity
  approximations all reuse the same dated cash flows. Per-cash-flow DV01
  attribution must reconcile to parallel DV01 and must be labelled explicitly
  as an attribution rather than curve-node key-rate duration. Negative yields
  are supported inside the declared positive discount-base domain; strict
  schemas, non-finite/coercible values, invalid dates/frequencies, unsolved
  quotes, singular DV01 bumps and out-of-domain shocks fail closed. The active
  Starter route runs in a worker, retains successful session history, emits
  SHA-256-bound JSON plus cash-flow/scenario CSV evidence and is usable at
  390 px. Calendars, business-day adjustment, settlement lag, irregular stubs,
  optionality, credit, curves, z-spreads, OAS and taxes are explicit v1
  limitations, never silently approximated or claimed.
- **F-CAL-9** Deterministic implied-volatility surface quality and interpolation
  lab, distinct from F-CAL-2 calibration: one canonical Python/JavaScript
  contract consumes a rectangular maturity grid expressed as `k = ln(K/F)`
  with explicit forward, discount factor, mid volatility and optional bid/ask.
  It computes `w(k,T) = sigma^2 T`, ATM term structure, skew, curvature,
  forward-normalized Black call values and strictly in-grid bilinear
  interpolation on total variance. Submitted nodes remain unsorted, unclipped,
  unfilled and unsmoothed; discrete call bounds, vertical monotonicity,
  butterfly convexity and calendar-total-variance violations are reported as
  evidence rather than repaired. Unknown fields, ambiguous units, duplicate or
  incomplete grids, non-finite/domain-invalid values and extrapolation fail
  closed. A local worker emits deterministic SHA-256-bound JSON, points CSV and
  diagnostics CSV. The active Student route supports a labelled fixture and
  real local CSV upload, successful-run-only history, stale-result clearing,
  slices/heatmap/term-structure views and explicit model limits. Live-data,
  continuous arbitrage-free, local-vol and trading claims are forbidden.
- **F-CAL-10** Canonical European Black-Scholes-Merton pricing and implied-
  volatility lab: one versioned Python/JavaScript contract supports call and
  put values with continuous rates/dividend yield, ACT/365F maturity, strict
  volatility-to-price and market-price-to-volatility modes, explicit expiry
  and zero-volatility limits, call-put parity, five Greeks with declared units,
  signed quantity/multiplier scaling and exact spot/volatility/time scenarios.
  The IV solver uses bounded bisection, exposes convergence and residual, and
  rejects quotes outside no-arbitrage or supported-volatility bounds. Unknown,
  coercible, non-finite, mutually inconsistent and out-of-domain payloads fail
  closed without clipping. The free anonymous route runs locally in a worker,
  clears stale output, retains successful runs only, renders three canonical
  21-point sensitivities and emits SHA-256-bound JSON plus scenario/sensitivity
  CSV evidence. The active route, embedded course calculator, AG-UI and practice
  calculators delegate to the same authority; no live quote, early exercise,
  smile, liquidity or trading recommendation is inferred.
- **F-EVAL-1** Product evaluation suite for generated material (`evaluate`, `/evaluation/suite`).
- **F-LIB-1** Persist & retrieve past generations (`/library/generations`).
- **F-AGT-1** Central auditable Tool Registry for Agentic Desk + Quant Pipeline agents.
- **F-AGT-2** Agent artifact contracts: RFQTicket, ProductSpec, MarketSnapshot,
  ModelCard, PricingPack, QuotePack, RiskVerdict, ClientReport,
  PreRegistration, DatasetManifest, FeatureManifest, CVRecord,
  ValidationVerdict, RiskPolicy, AllocationPlan, ExecutionVerdict.
- **F-AGT-3** Tool permissions, input/output schemas, audit/replay and CLI/API
  execution for every registered agent tool.
- **F-AGT-4** Durable ConversationLedger + AgentTaskLedger for agent sessions,
  sanitized history retrieval, artifacts, tool-call links and detached task
  lifecycle.
- **F-AGT-5** MCP-style adapter over the Tool Registry for Codex/OpenClaw/agent
  clients: tool search, describe, call, audit, replay, coverage, conversation
  search and artifact read.
- **F-AGT-6** Agent Interaction Gateway: route an inbound channel/user message
  to the right agent session, append history, run governed tools when requested,
  and persist delivery route metadata.
- **F-AGT-7** Codex/OpenClaw-inspired runtime primitives for agent orchestration:
  durable turns, approvals, lifecycle events, deterministic compaction,
  session fork, context injection and non-destructive rollback markers exposed
  through Python, CLI, HTTP and MCP-style methods. Approved approval records
  can confirm matching sensitive tool payloads without bypassing ToolRegistry
  validation.
- **F-WEB-1** Production bundle budget: stable dependency domains are split into
  cacheable chunks and every minified JavaScript asset must remain at or below
  500,000 bytes. The Starter Kit, assistant and Markdown/KaTeX renderer remain
  lazy-loaded outside the routes that need them.
- **F-WEB-2** Constrained-mobile performance: the production Starter Kit route
  must preserve a stable branded loading viewport and meet the reproducible lab
  budgets FCP <= 2,500 ms, LCP <= 4,000 ms, CLS <= 0.1, median interaction
  latency <= 300 ms and worst interaction latency <= 400 ms under the versioned
  Pixel 5 / 1.6 Mbps / 150 ms RTT / 4x CPU profile.
- **F-WEB-3** Public visual shell: the header, home hero, curriculum, tools,
  community, conversion panel and footer share one synchronously available desk
  token system while preserving the dark/red terminal direction. The shell must
  expose the source-grounded / engine-verified / limits-disclosed trust hierarchy,
  give the hero price scenario a full-width evidence band instead of constraining
  it inside a narrow nested column, keep the secondary terminal evidence balanced,
  and use typographic hierarchy rather than decorative icons in Audience card headers.
  The mobile assistant launcher must reserve its place in the navigation and must
  not cover the reference ticker, hero evidence or primary actions.
  The shell must
  use code-native SVG iconography, remain width-safe at 1440/760/480/390 px,
  retain visible focus and 44 px primary actions, respect reduced motion and add
  no external font or CSS dependency. Snapshot, deterministic-demo, synthetic-demo
  and non-live-market-data disclosures must remain visible and unchanged in meaning.
- **F-WEB-4** Calm workspace UX: preserve the dark/red visual identity while
  using spacing and surface contrast to group content. The home hero, trust
  principles, statistics and illustrative Greeks have no decorative frames or
  background grids. Show one primary free-calculator action and a course action
  before optional newsletter signup; disclose secondary scenario evidence via
  a keyboard-operable details element. Course and tool catalogues offer a clear
  free starting point, accessible search/filters and quiet cards. Keep useful
  table/chart axes, control boundaries, entitlements, demo disclosures and
  visible focus. The mobile menu supports Escape, focus containment/return and
  scroll locking. The unimplemented locale switch must not claim translation.
- **F-WEB-5** Modern navigation and interactive hero: evolve F-WEB-4's home
  into an editorial hero and floating compact navigation without restoring the
  decorative grid. Three main destinations remain directly visible on desktop;
  secondary destinations use an accessible Explore disclosure with outside-click,
  focus-leave and Escape closing. Mobile retains the keyboard-safe drawer.
  Replace the illustrative index/order-book hero with a real anonymous
  Black-Scholes-Merton preview using the existing canonical engine: call/put,
  spot and volatility controls update unit price, delta, three other Greeks and
  a spot-sensitivity curve from identical assumptions. State USD units, declared
  example inputs, constant volatility/model limits and absence of market data.
  The full calculator and course routes remain the two hero actions. Relocate
  the reference snapshot below the hero so it does not compete with navigation.
  This supersedes F-WEB-3's old paired index/order-book evidence composition.
- **F-WEB-6** User-approved navigation with restored market hero: preserve the
  F-WEB-5 navbar and replace its hero calculator with the earlier two-path SPX
  price chart. Show the illustrative index path prominently; derive the headline
  and Open/High/Low from its actual displayed red scenario. No mini-pricer,
  sliders or floating Delta remain in the hero. Disclose reproducible simulated
  data, absence of historical/current quotes and that the comparison is not a
  forecast. F-WEB-6 supersedes F-WEB-5's hero preview only. Local PASS requires
  the production UX smoke to verify stable paths/statistics, provenance disclosure,
  viewport fit and the existing approved navbar/free calculator/course journeys;
  preserve preceding iteration artifacts in separate capture folders.
- **F-WEB-7** Alternative hero presentations and brand correction: remove the
  invented icon/wordmark and render the product name as plain navigation text.
  Present two local layout proposals using the same illustrative market chart:
  editorial (default), with centred copy/actions then a full-width chart; and
  immersive (`?hero=immersive`), with the chart across the background and readable
  foreground copy. Neither uses a two-column hero or chart card/border/shadow.
  Main actions, illustration disclosures and navigation remain usable on mobile.
  Only the allow-listed immersive query selects the alternative; all other values
  fall back to editorial. The normal chart component keeps its default axes and
  aspect-ratio behavior elsewhere. Local PASS requires production browser proof
  of no invented brand mark, stacked/full-width default composition, no chart
  frame/axes, both variants' viewport fit, normal/reduced-motion rendering and
  existing free journeys. These are proposals for the user's choice, not an
  asserted acceptance of an aesthetic direction; F-WEB-7 supersedes the previous
  hero composition and invented brand presentation.
- **F-WEB-8** Accepted immersive hero and authentic navbar identity: B becomes
  the fixed home composition on `/`, without a query flag or alternative
  presentation mode. Restore the actual TPL signature from
  `Visuels/ThePricingLibrary_logo.png`, preserving its three candles, diagonal
  and three-line lettering. A transparent web SVG may trace the existing source
  contours; retain the original unchanged and embed source SHA provenance.
  Navbar color/material derives from the existing ink/white/vermilion identity
  and the ivory editorial banner. Reuse that signature for drawer/footer/auth.
  No new symbol, wordmark/font, pricing engine or hero composition is introduced.
  Local PASS requires matching source hash, >98% symbol/letter mask IoU in the
  actual browser-rendered SVG, asset under 50 kB, readable reserved logo space
  at 390 px, fixed B on `/`, functioning keyboard/menu/CTA journeys and maintained
  production bundle/performance budgets. This supersedes F-WEB-7's provisional
  plain name and open design choice; the user explicitly selected B.
- **F-PROD-1** One-shot Starter Kit fulfillment: Stripe Checkout `mode=payment`
  binds `market-finance-starter-kit` to the authenticated JWT subject; a signed,
  idempotent webhook creates a product entitlement separate from subscriptions.
  Manifest and download require that active entitlement and a server-configured
  immutable bundle whose real release manifest is ready, complete and SHA-256 valid.
- **F-PROD-2** Pricing dashboard artifact: the Starter Kit Excel deliverable must
  be a macro-free, external-link-free `.xlsx` with auditable named inputs,
  formula-driven Black-Scholes prices and Greeks, scenarios, a decision dashboard,
  at least three charts, visible model-risk warnings and recalculated golden cases.
  File presence alone never satisfies the seven-of-seven release gate.
- **F-PROD-3** Immutable commercial deployment: the production Compose contract
  must map every authentication, subscription and one-shot-payment setting,
  require an immutable backend image digest and public callback origin, and expose
  the verified Starter Kit release through a dedicated read-only bind mount.
  Missing operator values may keep commerce unavailable but must never silently
  fall back to localhost, an unversioned image or an in-container mutable bundle.
- **F-PROD-4** Privacy-bounded production observability: every HTTP response gets
  a server-generated correlation id and timing; Prometheus request metrics are
  operator-only and use route templates; browser RUM is production-only,
  explicitly enabled, credential-free, and sends only an allow-listed metric,
  finite value, normalized route and navigation type. The frontend live gate
  rejects disabled sales/RUM, placeholders, localhost, secrets and malformed
  public configuration.
- **F-PROD-5** Editable quant career artifact: the Starter Kit career pack must
  include a real one-page `.docx` CV template with native Word headings and
  lists, explicit placeholders, defensible numerical examples and a visible
  confidentiality checklist. Its build must be deterministic, metadata-scrubbed,
  macro-free, external-link-free, visually rendered and checksum-integrated in
  the immutable release manifest.

- **F-WEB-9** Delivery/content/usability audit of the active site: preserve the
  selected B hero and original branding. Every page has a main landmark,
  meaningful heading and route metadata; forms have stable accessible names,
  private workspaces fit 390 px, and unknown content IDs never substitute a
  different course or exercise. Authentication offers password recovery,
  distinguishes an email-confirmation signup from a signed-in session, and never
  grants paid access from profile metadata. Forum users can publish, reopen,
  read and reply to a persisted discussion; a failed reply retains its draft.
  Exercise export creates a real JSON file rather than claiming a remote save.
  API failure, actual empty data and empty search results remain distinct.
  Starter Kit completion is unknown until a strictly true verified release state
  is returned; checkout remains fail-closed. Lab scenarios use a validated,
  CLI-testable terminal P&L calculation with a numeric `pathCount` separate from
  display names, reproducible seeds, finite statistics and independent golden
  references. Simulation ratios, worst samples and payoff diagrams must not be
  presented as historical Sharpe/drawdown, real trading runs or net P&L.
  Reviewed course corrections align definitions, inputs and confidence-interval
  interpretation with the calculation packs; teacher/persona notes remain
  private. Structural course scores are not mathematical certification or real
  buyer satisfaction. Local checks and current public release blockers are
  recorded separately in the two audit reports.

- **F-WEB-10** Local testing access: loopback Vite development opens a signed
  local admin session by default, with a server-side Pro test grant. The real
  API runs automatically against an isolated `.local-preview` SQLite store;
  progress and forum actions use the signed subject. Existing source material
  may be read through a strictly read-only corpus connection. No real Supabase
  account, provider key, purchase or payment state is modified. The visible test
  toolbar switches between admin, a persistent visitor choice and the real
  authentication flow. Initial API failure has a retry action; private children
  wait for the verified session instead of flashing access locks. Completed
  modules restore from `completed_lessons`; `events` remains a numeric count.
  The exception is disabled on public bind addresses, production mode and
  preview, can be opted out with `TPL_LOCAL_ADMIN=false`, and its client code,
  identity, bootstrap endpoint and test data are absent from production output.
  Local PASS requires real HTTP persistence/security tests, browser journeys and
  an independent Business Client Mystère review. It grants no production access.

- **F-WEB-11** Accepted Courbe signature hero: replace the selected immersive
  presentation with the user's chosen first proposal from
  `reports/design-proposals-2026-11-14-hero/signature-1024.png`. Keep the approved
  navbar, original horizontal artwork, headline and two real starting actions.
  Render the same two deterministic 120-observation paths, with a full-contrast
  vermilion scenario, quiet neutral reference and a price label anchored to the
  displayed final point. The chart has no card, frame, decorative grid or
  global dimming mask. Copy/actions stay clear of the drawing and the quote at
  320/390/480/760/1080/1440 px. Preserve the simulation/non-live/non-forecast
  disclosures; keep Open/High/Low from the same scenario in keyboard-accessible
  chart context. Add no feed, pricing calculation, animation loop or dependency.
  This supersedes F-WEB-8's hero composition only. Local PASS requires the
  updated production UX CLI journey, deterministic data/endpoint and responsive
  quote-placement evidence, working free calculator/course navigation, bundle
  checks and independent Technical RL / Business Client Mystère verdicts.

## 7. Inputs and outputs (key contracts)

- **Course** in: `{topic, product, concepts[], level, duration_minutes, module_count, language}` →
  out: markdown course (front-matter + lessons + verified appendix) + metadata
  `{llm, source_coverage, pedagogical_gaps, library_track}`.
- **Exercise** in: `{topic, product?, concept?, difficulty, exercise_format, number_of_questions, free_prompt?, language}` →
  out: `{title, content (markdown), sources[], metadata{calculation_pack,…}}`.
- **Calculate** in: free-text desk scenario or `--family` → out: `CalculationPack`
  with formula, substitution, result, desk reading.

## 8. State transitions

- Document: `ingested → classified → (enriched theme) → retrievable`.
- Chunk: `stored → classified(pedagogy) → usable_for_course ∈ {0,1}`.
- Generation run: `requested → generated → saved(generation_runs) → retrievable via /library`.
- Course file: `generated_vN → audited(gate) → archived(old) → promoted(public)`.
- Exercise (frontend): `requested → (backend OK ⇒ grounded) | (backend down ⇒ local fallback, labelled)`.

## 9. Data model (SQLite, backend)

- `documents(id, title, path, theme, subtheme, asset_class, …)`
- `chunks(id, document_id, content, section_title, metadata_json, content_type, pedagogical_value, quality_score, usable_for_course, …)` + FTS5 index
- `generation_runs(id, kind, request_json, response_json, created_at)`
- `conversation_sessions`, `conversation_messages`, `conversation_artifacts`,
  `conversation_tool_calls`, `agent_tasks`
- `conversation_turns`, `conversation_summaries`, `agent_approvals`,
  `runtime_events`
- `product_entitlements(user_id, product_id, status, stripe_customer_id,
  stripe_checkout_session_id, stripe_payment_intent_id, source, timestamps)`;
  primary key `(user_id, product_id)`, independent from recurring `entitlements`.

## 10. API contracts (FastAPI, `api.py`)

`GET /health` · `GET /ready` · `GET /metrics` · `POST /telemetry/rum`
· `GET /` · `GET /ui` · `GET /documents` · `GET /sources/pedagogy-stats`
· `POST /documents/ingest` · `POST /rag/search` · `POST /calculate/practice`
· `POST /generate/exercise` · `POST /agent/exercise` · `POST /agent/course`
· `POST /generate/course` · `POST /generate/material-pack`
· `GET /library/generations` · `GET /library/generations/{run_id}`
· `GET /evaluation/cases` · `POST /evaluation/response` · `POST /evaluation/suite`
· `GET /agent/tools` · `GET /agent/tools/coverage`
· `GET /agent/tools/{tool_name}` · `POST /agent/tools/{tool_name}/run`
· `GET /agent/tools/audit/{tool_call_id}` · `POST /agent/tools/replay/{tool_call_id}`
· `GET /agent/tools/search`
· `POST /agent/sessions` · `GET /agent/sessions`
· `GET /agent/sessions/{session_id}` · `POST /agent/sessions/{session_id}/messages`
· `GET /agent/sessions/{session_id}/history`
· `GET/POST /agent/sessions/{session_id}/artifacts`
· `POST /agent/sessions/{session_id}/tools/{tool_name}/run`
· `GET/POST /agent/sessions/{session_id}/turns`
· `POST /agent/turns/{turn_id}/complete`
· `POST /agent/sessions/{session_id}/compact`
· `GET /agent/sessions/{session_id}/summaries`
· `POST /agent/sessions/{session_id}/fork`
· `POST /agent/sessions/{session_id}/inject`
· `POST /agent/sessions/{session_id}/rollback`
· `GET /agent/sessions/{session_id}/events`
· `GET/POST /agent/approvals`
· `POST /agent/approvals/{approval_id}/resolve`
· `GET/POST /agent/tasks` · `POST /agent/tasks/{task_id}/status`
· `POST /agent/mcp/handle` · `POST /agent/gateway/inbound`
· `POST /products/market-finance-starter-kit/checkout`
· `GET /products/market-finance-starter-kit/availability`
· `GET /products/market-finance-starter-kit/manifest`
· `GET /products/market-finance-starter-kit/download`

Contract rule: every generate/agent response includes `sources[]` and a
`metadata.llm` field so the frontend can show grounding + provider.

## 11. Business rules

- Course retrieval uses only `usable_for_course` chunks above `min_quality`.
- No invented numbers: numeric outputs come from `calculators.py` or cited sources.
- Provenance must be labelled; gaps flagged, never fabricated.
- Quality gate: a course must score ≥ 70 and be free of boilerplate repetition
  and formula leaks before promotion to `public/`.
- Starter Kit checkout never accepts a client product id, file path or redirect
  URL. Fulfillment is closed unless the release manifest has non-empty version,
  `ready=true`, exactly seven complete deliverables, no missing files, and a
  `bundle.path/size/sha256` matching the configured server-side bundle.
- Refund and chargeback revoke only the matching product entitlement; a
  recurring plan on the same Stripe customer remains unchanged.
- Public availability exposes only product id, aggregate checkout/artifact
  booleans, `sale_ready` and validated version. It always returns HTTP 200 and
  closes sales on missing or corrupt configuration without exposing paths,
  checksums or provider errors. Product success/cancel URLs come only from
  `TPL_STARTER_KIT_SUCCESS_URL` and `TPL_STARTER_KIT_CANCEL_URL`, never from the client.
- RUM ingestion rejects unknown metrics, non-finite/out-of-domain values,
  oversized strings and every extra field. Raw URLs, query strings, course/tool
  slugs, identity data and credentials are never stored or exported as labels.

## 12. Error states

- Backend unreachable → frontend exercise uses local fallback **with a visible
  "generation locale de secours" notice** (practiceEngine.js).
- LLM provider error/timeout → course generation falls back to deterministic
  per-lesson frames (no crash, still structured).
- Empty/noisy source snippet → withheld and labelled "(extrait non cité: source bruitée)".
- Missing OpenAI key with provider=openai → explicit RuntimeError (no silent mock).
- Starter Kit API/config/artifact unavailable → public availability remains HTTP
  200 with `sale_ready=false`; the frontend displays an honest locked/offline
  state and never simulates checkout or delivery.

## 13. Empty states

- No corpus ingested → retrieval returns empty; course generator must report
  "not_usable / insufficient sources" rather than fabricate. (Acceptance: must
  not invent sources.)
- No course selected → course page shows catalogue.

## 14. Mock/demo mode rules

- `TPL_LLM_PROVIDER=template` is the offline deterministic mode for tests — must
  be clearly an engineering mode, never shipped as "AI-grounded" to a user.
- Frontend local fallback is a *degraded* mode and must be labelled.

## 15. Authentication and permissions

- The live Claude frontend uses Supabase sessions and sends the signed access
  token to protected backend routes.
- The backend validates issuer, audience, JWKS and an ES256/RS256 allowlist, then
  applies public/member/operator route policy and paid tier ranks.
- Stripe subscriptions and one-shot product rights are stored server-side and
  bound to the verified JWT subject; signup/profile metadata grants no paid access.
- Unknown mutations are operator-only. Starter Kit manifest/download require an
  active product entitlement and a ready checksum-valid artifact.
- Other repo services (GitHub OAuth, n8n webhook) belong to the legacy Lovable
  scaffold and are out of scope for the core promise.

## 16. CLI-testability requirements

See `CLI_TESTABILITY_CONTRACT.md`. Every core journey must be reproducible from
the CLI without the UI.

## 17. Acceptance criteria (per critical feature)

- **F-CRS-1/2/3/4** PASS when `scripts/smoke_course_generation.py` shows grounding
  OK, a verified worked example, corrected exercise, quiz, and provenance tags.
- **F-CRS-5** PASS when `audit_course_quality.py` reports gate PASS, 0 boilerplate,
  0 formula leaks for all 12 courses.
- **F-EXO-1** PASS when `POST /agent/exercise` returns a response with non-empty
  `sources[]` and a verified correction, reproducible via a CLI/HTTP smoke.
- **F-EXO-2** PASS when, backend down, the frontend returns a labelled fallback
  (no crash, user can tell it is not grounded).
- **F-CAL-*** PASS when a calculator's output matches the engine/closed form on a
  known case (e.g. BS ATM call = 10.4506).
- **F-CAL-2** PASS when `npm run smoke:calibration` proves Black-76 inversion,
  SABR and Heston golden values, identical repeated calibrations, bounded
  parameters, material fit improvement, valid/adversarial CSV behavior and the
  absence of random/fake/placeholder paths; `npm run smoke:calibration:bundle`
  must prove that the active production route ships the isolated component and
  worker with no legacy/fake model path. `npm run smoke:calibration:browser` must
  exercise an isolated production build of the authenticated `/tools/calib`
  Student route with a server-authoritative entitlement response and no paid
  plan in profile metadata. It must prove the reference and uploaded-CSV paths,
  Black/SABR/Heston runs, objective guidance, invalid-input rejection, JSON and
  sample-CSV downloads, run history, mobile layout, worker execution and zero
  uncaught page/console/critical-request errors. Lint, production build and the
  global bundle/journey gates must also pass. Intercepted local auth/billing
  contracts prove the browser integration, not a live staging deployment.
- **F-CAL-3** PASS when `npm run smoke:curve` proves the deposit, FRA, explicit-
  convexity future and sparse-swap golden cases; exact repricing within `1e-10`;
  flat, shaped, inverted and negative-rate curves; deterministic repeated
  output; correct log-DF interpolation; interval-correct forwards; and explicit
  rejection of non-finite/ambiguous/duplicated/uncovered/non-bracketed inputs,
  implicit stubs, absent future convexity and extrapolation. The JavaScript and
  Python calculator paths must agree on a shared fixture. `npm run
  smoke:curve:bundle` must prove the active route ships a dedicated lazy
  component and the old sparse-node formula/`1y fwd` label is absent. `npm run
  smoke:curve:browser` must exercise anonymous locking and bearer-authorized
  Starter access, reference/CSV inputs, quote modification, diagnostics,
  versioned export and mobile layout in an isolated production preview with zero
  uncaught page/console/critical-request errors. Lint, production build, bundle,
  existing calibration gates and the global journey must remain green.
- **F-CAL-4** PASS when `npm run smoke:realized-vol` and the mirrored Python
  tests prove a shared golden fixture for all five estimators, identical session
  counts, deterministic repeat, 252/365 annualization, rolling windows, zero-vol
  flat data, overnight-only data, strict CSV validation, dated quality warnings
  and versioned JSON/CSV exports. JavaScript/Python variances must agree within
  `1e-14` and annualized volatilities within `1e-12`. `npm run
  smoke:realized-vol:cross-engine` must additionally prove the same recursive
  result contract to `1e-13`, byte-identical versioned CSV exports, a SHA-256
  invariant to comma/semicolon, BOM and CRLF formatting, and identical
  fail-closed/diagnostic behavior on reordered columns, gaps, close jumps,
  intraday ranges, flat bars and repeated closes. `npm run
  smoke:realized-vol:bundle` must prove a dedicated lazy component and worker
  are shipped while the former random walk, asset presets, fake upload and
  legacy calculator are absent. `npm run smoke:realized-vol:browser` must prove
  anonymous locking, bearer-authorized Starter access without paid profile
  metadata, real sample download/upload, five visible estimates, coherent
  window/annualization changes, stale-result invalidation, fail-closed malformed
  CSV, preserved warning rows, three actual exports, session-only successful-run
  history, no OHLC exfiltration, worker execution, desktop and 390 px layout and
  zero uncaught page/console/critical-request errors. Lint, production build,
  bundle budget, calibration, curve and global journey gates must remain green.
- **F-CAL-5** PASS when a shared golden fixture and focused Python/JavaScript
  tests prove call/put parity, signed long/short prices and all five Greeks,
  model/manual premium handling, multiplier and quantity scaling, exact
  piecewise breakevens and finite/unlimited bounds for a long call, naked short
  call, bull call spread, long straddle, butterfly and iron condor. A dedicated
  cross-engine smoke must compare the complete result and versioned exports,
  while adversarial tests reject empty/extra/duplicate/non-finite/out-of-range
  inputs without leaving a stale result. The source and production-bundle gates
  must prove that `/tools/payoff` ships one lazy calculator and that the two old
  grid-bound/hard-coded implementations and fake save path are absent. The
  isolated browser smoke must prove anonymous/inactive denial, bearer-authorized
  Starter access without paid profile metadata, visible market/contract/premium
  conventions, presets and manual legs, exact unlimited labels, off-window
  breakevens, signed Greeks, scenario decomposition, real JSON/CSV downloads,
  successful-run-only history, mobile 390 px usability and zero uncaught page,
  console or critical-request errors. Lint, production build, bundle budget and
  every previously validated calculator/global journey must remain green.
- **F-CAL-6** PASS when `npm run smoke:mc`, `npm run smoke:mc:cross-engine`,
  `npm run smoke:mc:backend` and `npm run smoke:mc:worker` prove deterministic
  P-risk and Q-pricing results, correct loss VaR/ES signs and tails, European and
  arithmetic-Asian payoffs, plain/antithetic/control-variate behavior, degenerate
  zero-volatility handling, convergence/uncertainty fields, strict adversarial
  rejection and worker request/error isolation. Python and JavaScript must agree
  recursively within `1e-11`, share analysis identifiers and emit byte-identical
  LF terminal/path CSV files across six representative cases. The backend AG-UI,
  practice calculator and course calculator must delegate to the canonical
  engine without their former RNGs or input clamping. After `npm run build`,
  `npm run smoke:mc:bundle` must prove one lazy lab and one shared worker, with
  false sample counts and legacy route code absent. `npm run smoke:mc:browser`
  must prove anonymous/inactive denial, bearer-authorized Starter access, visible
  P/Q and numerical conventions, Q price/SE/CI/benchmark/convergence, Asian
  control-variate disclosure, P loss VaR/ES, same-run JSON/two-CSV evidence,
  fail-closed stale clearing, successful history, a visible 44 px CTA and charts
  at 390 px, worker execution and zero uncaught page/console/critical-request or
  simulation-data leakage errors. Lint, production build, bundle budget and all
  earlier calculator/global journey gates must remain green.
- **F-CAL-7** PASS when `npm run smoke:binomial`, `npm run
  smoke:binomial:cross-engine`, `npm run smoke:binomial:backend` and `npm run
  smoke:binomial:worker` prove European convergence and put-call parity,
  American put/high-dividend-call frontiers, the non-dividend-call invariant,
  same-tree European valuation, five position-scaled Greeks, exact zero-volatility
  and expiry limits, hard-domain sensitivities, strict schema/no-arbitrage
  rejection and isolated worker errors. Python and JavaScript must agree
  recursively within `2e-10`, share analysis identifiers and emit byte-identical
  LF convergence/frontier CSV evidence across eight European, American,
  dividend, degenerate, signed-position and sensitivity-boundary cases. The
  AG-UI adapter must preserve requested
  steps and delegate to the canonical backend without probability/step clamping.
  After `npm run build`, `npm run smoke:binomial:bundle` must prove one lazy
  Student lab and one worker with the former inline CRR route absent. `npm run
  smoke:binomial:browser` must prove anonymous/inactive denial, bearer-authorized
  Student access without paid profile metadata, visible Q/day-count/model
  conventions, American put and dividend-call exercise evidence, five Greeks,
  retained node decisions, an honest European Black-Scholes comparison, real
  SHA-bound JSON/two-CSV downloads, fail-closed stale clearing, successful-only
  history, a visible 44 px CTA and frontier at 390/390 px, worker execution and
  zero uncaught page/console/critical-request or calculation-data leakage errors.
  Lint, typecheck, production build, bundle budget and all earlier calculator
  and global journey gates must remain green.
- **F-CAL-8** PASS when npm run smoke:bond, npm run
  smoke:bond:cross-engine, npm run smoke:bond:backend and npm run
  smoke:bond:worker prove the par golden case, off-cycle accrued identity,
  zero-coupon fractional maturity without rounding, YTM/clean-price round trip,
  ACT/ACT ICMA and 30E/360 schedules, end-of-month handling, negative yield,
  duration/convexity, exact central DV01, reconciled cash-flow DV01 attribution,
  signed position values, exact/approximate shocks, strict schemas and isolated
  worker errors. Python and JavaScript must agree recursively within 2e-11,
  share analysis identifiers and emit byte-identical LF cash-flow/scenario CSV
  evidence across at least eight representative quote, convention, frequency
  and position cases. The AG-UI adapter must preserve the canonical payload and
  reject strings, booleans, fractions and unknown fields. After npm run build,
  npm run smoke:bond:bundle must prove one lazy Starter lab and one worker with
  both former divergent calculators absent. npm run smoke:bond:browser must
  prove anonymous/inactive denial, bearer-authorized Starter access without
  paid profile metadata, visible price/yield/settlement conventions, par and
  price-inversion journeys, clean/dirty/accrued reconciliation, dated cash
  flows, exact risk/scenarios, honest negative-yield and model-limit
  disclosures, real SHA-bound JSON/two-CSV downloads, fail-closed stale
  clearing, successful-only history, a visible 44 px CTA and charts at
  390/390 px, worker execution and zero uncaught page/console/critical-request
  or calculation-data leakage errors. Lint, typecheck, production build, bundle
  budget and all earlier calculator/global gates must remain green.
- **F-CAL-9** PASS when `npm run smoke:vol-surface`, `npm run
  smoke:vol-surface:cross-engine`, `npm run smoke:vol-surface:backend` and `npm
  run smoke:vol-surface:worker` prove exact `k = ln(K/F)` and `w = sigma^2 T`,
  ATM/skew/curvature metrics, strictly in-grid total-variance interpolation,
  call bounds, vertical/butterfly/calendar diagnostics, strict rectangular CSV
  and fail-closed schema/grid/extrapolation behavior. Python and JavaScript must
  agree recursively within `2e-11`, share SHA-256 identifiers and emit
  byte-identical LF points/diagnostics CSV evidence across at least six clean,
  boundary, violation and missing-spread cases. AG-UI must delegate without
  coercion, clamp or fallback. After `npm run build`, `npm run
  smoke:vol-surface:bundle` must prove one lazy Student lab and one worker with
  the clamped inline demo and fake 3D page absent. `npm run
  smoke:vol-surface:browser` must prove anonymous/inactive denial,
  bearer-authorized Student access, a real local CSV journey, clean and
  calendar/butterfly cases, slices/ATM term structure/heatmap, same-SHA
  JSON/two-CSV downloads, fail-closed stale clearing, successful history, a
  visible 44 px CTA at 390/390 px, worker execution and zero uncaught
  page/console/critical-request or quote-data leakage errors. Lint, typecheck,
  production build, bundle budget and all earlier gates must remain green.
- **F-CAL-10** PASS when `npm run smoke:black-scholes`, `npm run
  smoke:black-scholes:cross-engine`, `npm run smoke:black-scholes:backend` and
  `npm run smoke:black-scholes:worker` prove ATM/dividend/negative-rate cases,
  exact expiry and discounted zero-volatility limits, five Greeks against
  finite differences, strict IV round-trip/bounds, signed position scaling,
  six exact scenarios, three 21-point sensitivities, strict schemas and worker
  errors. Python and JavaScript must agree recursively within `2e-11`, share
  analysis identifiers and emit byte-identical LF scenario/sensitivity CSV.
  AG-UI, practice and course consumers must delegate without coercion, clamp or
  divergent formula. After `npm run build`, `npm run
  smoke:black-scholes:bundle` must prove one lazy free lab and worker with the
  former inline widget absent. `npm run smoke:black-scholes:browser` must prove
  anonymous access, price and IV journeys, visible Greek units, parity,
  scenarios/sensitivities, same-SHA downloads, fail-closed stale clearing,
  success-only history, a 44 px CTA at 390/390 px and zero browser error or
  calculation-data leakage. Lint, typecheck, the full production build, bundle
  budget and all earlier gates must remain green.
- **F-AGT-1/2/3** PASS when `python scripts/smoke_tool_registry.py`,
  `python scripts/smoke_agent_artifacts.py`, `python scripts/smoke_quant_agent_dag.py`,
  `python scripts/smoke_tool_registry_api.py`, and
  `python scripts/smoke_chief_of_staff_validation.py` pass with Chief of Staff
  satisfaction > 98%.
- **F-AGT-4/5/6/7** PASS when `python scripts/smoke_conversation_ledger.py`,
  `python scripts/smoke_agent_mcp_adapter.py`, `python scripts/smoke_agent_gateway.py`,
  `python scripts/smoke_agent_interaction_api.py`, and
  `python scripts/smoke_agent_runtime_state.py`,
  `python scripts/smoke_agent_runtime_cli.py`,
  `python scripts/smoke_agent_runtime_api.py`, and
  `python scripts/run_codex_agent_audit.py` pass.
- **F-WEB-1** PASS when `npm run smoke:bundle` finds production assets and exits
  zero only if every minified JavaScript chunk is at or below 500,000 bytes;
  `npm run smoke:journey` must still prove lazy assistant/Starter Kit loading and
  report no uncaught browser error.
- **F-WEB-2** PASS when `npm run audit:performance` rebuilds the production bundle,
  enforces its size budget, then observes FCP/LCP/CLS and three isolated
  account-path interactions on the production preview; it must meet every stated
  budget, report the individual interaction samples and exit non-zero on any
  missing metric, budget breach or uncaught browser error.
- **F-WEB-3** PASS when `npm run smoke:visual-shell` proves the semantic shell
  hooks, full-width hero price band, balanced secondary evidence, icon-free
  Audience card headers, safe mobile assistant placement, synchronous/lazy token
  parity, 760/480 px responsive rules,
  reduced-motion support, code-native SVG icon mapping, preserved market-data
  honesty copy and absence of external font/CSS dependencies. A production build
  and runtime probes at 1440/760/480/390 px must additionally show exact viewport
  document width, a visible 2 px focus indicator, 44 px primary CTA, working
  desktop/mobile navigation and zero uncaught runtime error. `npm run
  smoke:bundle` must remain below the 500,000-byte JavaScript asset limit.
- **F-WEB-4** local PASS when `npm run smoke:ux:browser` on a production preview
  proves the free-calculator/course journeys, optional scenario disclosure,
  searchable/filterable catalogues and empty-search recovery; the newsletter
  follows the core experience. At 1440/1080/760/480/390 px the home and catalogues
  fit the viewport, primary actions are at least 44 px high and controls retain
  visible keyboard focus. Mobile navigation supports keyboard entry, Escape,
  contained Tab focus, focus return and working route selection. Capture before/
  after visuals and retain snapshot/demo disclosures, reduced-motion behavior
  and existing entitlement/calculator gates. Technical and independent Business
  Client Mystère verdicts cover this local UX change, not deployed commerce.
- **F-WEB-5** local PASS when `npm run smoke:ux:browser` additionally proves
  canonical ATM call/put prices, correct spot/volatility/delta updates, matching
  plotted marker and controls, keyboard Explore opening/closing/link routing,
  model-assumption disclosure and first-screen activation on mobile. Preserve
  exact viewport fit, focus/44 px main actions, reduced motion, anonymous
  calculator/preview paths, existing commercial gates and the bundle budget.
  Capture this iteration separately from F-WEB-4 so earlier evidence stays
  reviewable; independent technical and business reports are required.
- **F-WEB-11** local PASS when the production UX journey shows the chosen
  Signature composition and unchanged authentic navigation; validates the
  actual price/point coordinates, opaque unmasked scenario and clear quote/
  intro separation at 320/390/480/760/800/960/1080/1440 px; and retains keyboard
  provenance, correct seeded path statistics, real free pricing/course actions,
  reduced motion, 44 px targets and zero runtime errors. Technical and
  independent Business Client Mystère reviews must both pass. This is local
  implementation evidence, not a public deployment or commercial acceptance.
- **Production** PASS only when PRODUCTION_READINESS verdict ≠ NO on P0 items.
- **F-PROD-1** PASS when `python scripts/smoke_starter_kit_fulfillment.py`
  reproduces public fail-closed availability, free-user refusal, one-shot checkout, signed purchase, duplicate
  webhook, manifest/download, incomplete-manifest refusal and refund revocation;
  focused pytest also covers checksum, manifest version/count and chargeback.
- **F-PROD-2** PASS when `python scripts/verify_excel_dashboard.py` validates the
  OOXML structure, exact seven-sheet contract, ten named inputs, formula/control/
  chart minimums, content warnings and four cached golden values; both
  `build_release.py` and `verify_bundle.py` must independently invoke the same
  validation and exit non-zero for a missing or invalid workbook.
- **F-PROD-3** PASS when `python scripts/check_deployment_contract.py --env-file
  .env.production` validates non-placeholder server values, the resolved Compose
  JSON and the locally available digest-pinned image metadata. The backend
  aggregate separately verifies the committed template in explicit PASS-CLOSED
  mode. Live PASS additionally requires the same digest and values on the target
  host plus healthy deployed `/ready` and `starter-kit/availability` responses.
- **F-PROD-4** local PASS requires `python scripts/smoke_observability.py`,
  `npm run smoke:rum`, `npm run smoke:rum:browser` and
  `npm run smoke:production-env-contract` to pass. Live PASS additionally
  requires `npm run check:production-env`, an authenticated `/metrics` scrape,
  verified correlation through the reverse proxy, deployed RUM reception and an
  exercised alert/rollback procedure; local evidence is not a deployed PASS.
- **F-PROD-5** PASS requires `powershell -File scripts/build_career_docx.ps1`
  to produce the same SHA-256 on consecutive builds,
  `powershell -File scripts/render_career_docx.ps1` to render exactly one clean
  page, and the Starter Kit pytest/release gates to prove native numbering,
  substantive content, metadata removal, no macro/external relationship and a
  manifest checksum matching the staged DOCX.

## 18. Production readiness criteria

See `PRODUCTION_READINESS.md`. The implemented commercial matrix is authoritative:

- Free: Black-Scholes course preview and Black-Scholes calculator.
- Starter: Fundamentals, exercise workspace, core payoff/MC/vol/rates tools,
  course scripts, progress and community.
- Student: Advanced courses, calibration/binomial/vol-surface tools, Trading Lab,
  Survival Mode and browser notebook.
- Professional: Complex courses, agentic desk and backtest research workspace.
  The unconfigured private API preview is excluded from the paid-plan promise.

Paid access is granted only by a backend entitlement bound to the authenticated
Supabase JWT subject. Profile or signup metadata never grants a plan. Public sale
remains fail-closed until the complete legal identity and live billing configuration
pass the production gate.
