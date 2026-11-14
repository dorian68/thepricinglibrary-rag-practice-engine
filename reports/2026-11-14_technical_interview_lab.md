# Technical RL — English Interview Lab

Verdict: **PASS, local backend/API scope**. Independent business and browser
integration remain separate gates. No live sale, public deployment, external LLM
call, human review or recruitment-readiness certification is claimed.

## Implemented product

Six original authored English cases, each with a conceptual transfer task:
call → put; dividend parity → zero-dividend carry comparison; short-call hedge →
long-put hedge; short gamma/vol rise → long gamma/vol fall; call carry/rates → put
carry/rates; short-call quote memo → long-put memo. All prices, Greeks,
cash-flow signs and stress results use the canonical European BSM engine. The
automated test oracles use independent `math.erf` closed forms and P&L identities.
The new lab does not ingest or expose the private course corpus.

Task responses omit reference numbers and worked solutions. A numerical answer
and a written method must be submitted before correction, or the learner can
explicitly reveal a reference and lose independent-check eligibility on that
task. First attempts, submitted reasoning, task snapshots, feedback and timestamps
are retained in append-only account events. Retries cannot overwrite them.
"Independent" means no prior attempt/correction exposure recorded on this account;
this practice is not proctored and outside exposure cannot be verified.

Reasoning uses a recorded learner self-review rubric and is not automatically
graded. Numeric pass, transfer pass, activity and self-review counts remain
distinct. Reported foreground active time is capped by elapsed server time and
300 seconds per heartbeat; it does not prove attendance. An exact current task,
role/deadline/session-length onboarding and a private JSON practice report persist
across API re-creation. Anonymous first-case checks work and explicitly do not
save or claim independent mastery. The signed pilot currently adds no paid plan
requirement. Existing private paid-course policy remains unchanged.

## HTTP contract (`tpl.interview-lab.v1`)

- `GET /interview/catalog`: public English case metadata and pilot limitations.
- `GET /interview/cases/{case_id}?variant=primary|transfer`: ticket, instructions,
  numbered question IDs/units/tolerances, hints, assumptions, rubric and exact
  calculator-input link. The first case is public; other cases require signed
  identity. IDs: `call-quote`, `dividend-parity`, `delta-hedge`, `gamma-vega`,
  `time-rates`, `quote-memo`.
- `POST /interview/preview/check`: first case only, `{case_id,variant,answers,
  reasoning,client_request_id}` → `{attempt}` with `persisted:false` and
  `independent:false`. Rate-limited; no account record written.
- `POST /interview/attempts`: same strict body, signed subject → `{attempt}`,
  including immutable originals, task snapshot, feedback/checks and eligibility.
- `POST /interview/reveal`: `{case_id,variant,client_request_id}` → reference
  feedback plus a persisted exposure event.
- `POST /interview/attempts/{attempt_id}/review`: `{criteria:{assumptions,
  decision,limitations},notes,client_request_id}` → `{review}`. Criteria are strict
  booleans. Another account receives 404; a shared API key is not an identity.
- `POST /interview/onboarding`: `{role,deadline,minutes_per_session}` →
  `{onboarding}`. Roles: `sales_trading|structuring|market_risk`; session lengths:
  `15|30|45|60`; deadline ISO date or null. Includes a bounded suggested session.
- `POST /interview/session`: `{case_id,variant,active_seconds,client_request_id}`
  → `{current_task,credited_active_seconds,persisted}`. Strict 0–300 second input.
- `GET /interview/state`: private `{owner_id,onboarding,current_task,attempts,
  exposures,metrics,next_task,limitations}`. Metric aliases used by the UI:
  `cases_attempted`, `numerical_passes` (primary first checks), `transfer_passes`,
  `reasoning_reviews`, `active_seconds`; `certified_mastery` is always false.
- `GET /interview/export`: same private record, timestamp, report limitations and
  JSON attachment headers. All private responses use `private, no-store`.
- `GET /interview/pilot/metrics`: verified operator only (signed operator identity
  or configured trusted operator key). Members receive 403; relaxed local mode
  cannot bypass the handler's explicit operator check. Returns aggregate account
  participation, per-case primary/transfer checks and totals, without identifiers,
  emails, answers or written memos. All counters share one database read snapshot.

Pilot definitions are explicit in the response: profiles opened or saved are
`learners_seen`; a primary attempt marks activation; a return means attempts on
at least two UTC calendar dates, without claiming a D7 retention cohort. A retry
does not inflate first-attempt passes; repeated self-reviews of one attempt count
once. These are account-participation statistics, not unique people, paying
customers, sales conversion or market-fit evidence. The response names the runtime
environment and explicitly identifies local/test activity outside production.

Request IDs are bounded and transactionally unique per owner across mutation
types. Replaying an identical request returns its original result; changing its
payload/type/target returns 409. The owner comes only from a verified signed
token, never a browser-supplied account ID. SQLite `BEGIN IMMEDIATE` serialises
concurrent first submissions and preserves their first-attempt classification.

## Course resume correction (F06)

`PUT /platform/courses/{course_id}/position`, strict `{module_index:int}`, saves
the signed account's position separately from progress/completion. Module indices
are checked against the current course manifest counts. Black-Scholes preview
indices 0/1 are free; other modules follow existing server entitlements.
`GET /platform/progress/{user_id}` includes `course_positions:[{course,module_index,
updated_at}]` and uses private no-store headers. Navigating never awards points or
completes a lesson. Other-account progress remains inaccessible.

For a realistic signed local learner, `Settings.enforce_entitlements` (default
false; `TPL_ENFORCE_ENTITLEMENTS=true`) can enforce exactly the same plan policy
without changing the local environment, corpus or other production guards.
Production continues to enforce entitlements automatically. Verified operators
retain their explicit bypass; a local free learner is denied paid course content
until an actual server grant is present. `/health.security.entitlements_enforced`
reports the effective state. The local-preview launcher opts in explicitly.

## Reproducible validation

```text
python -m pytest -q tests/test_interview_lab.py tests/test_api_security.py tests/test_observability.py --basetemp=.pytest_tmp_interview_pilot_final
51 passed
python scripts/smoke_interview_lab.py --output reports/interview_lab_smoke_2026-11-14.json
23/23 PASS
```

Coverage includes 12 independent mathematical oracles; real anonymous checking;
signed non-admin pilot access; unchanged paid access; private owner separation;
strict malformed/forged input rejection; request collisions and concurrency;
correction exposure; premature transfer and retries; self-review target binding;
actual rate limiting; foreground-time capping; exact state restoration after a new
API instance; immutable original responses; export; and course-position isolation,
entitlement, bounds and zero completion side effects.
Additional checks cover signed/key-based operator metrics, anonymous/member
denial, relaxed-mode denial, zero-data counters, exact aggregate values across
multiple accounts and UTC dates, no private text disclosure, no retry/self-review
inflation, explicit local/test notices, and local free/paid/admin entitlement
behavior with environment parsing.

Storage uses the existing SQLite database and adds only `interview_profiles`,
`interview_events` and `platform_course_positions`. No existing user rows are
deleted and no existing local activity is reset.
