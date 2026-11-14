# Pricing and Greeks Interview Lab — implementation contract (2026-11-14)

Owner: Technical RL; independent validation: Business Client Mystère.
Target: English-speaking master's students preparing bank derivatives interviews.
This is a learning pilot, not a recruitment certification or a live market feed.

## Acceptance

1. Six authored English cases form a progressive path: call quote, put-call
   parity/dividends, delta hedge/sign, gamma/vega shock, time/rate assumptions,
   and a final quote-and-risk memo. Each has a different conceptual transfer
   variant, explicit units, assumptions, useful hints and a worked explanation.
2. A short onboarding records role, deadline and available minutes. It gives a
   bounded first session and a suggested next task; no hiring outcome is promised.
3. A public first case is genuinely usable. Authenticated verified learners can
   save attempts; the remaining cases follow an explicit server-owned access
   policy. Existing paid-course access rules remain in force. Anonymous preview
   activity must be clearly labelled as unsaved, never invented persisted mastery.
4. The task response omits the answer key. Numerical answer plus substantive
   reasoning must be submitted before correction. Revealing a correction first
   disqualifies that attempt as an independent check. A new conceptual variant
   checks transfer; retry history must never overwrite the first attempt.
5. Numerical assessment uses the canonical deterministic engine with specified
   tolerances. Written reasoning uses an explicit self-review rubric, recorded
   separately. Neither word counts nor self-report can produce a certified pass.
6. Signed account identity owns progress, attempts and onboarding. Another account
   cannot read or overwrite them. Reload and a fresh browser restore the actual
   task/variant, not the first lesson. Double submission is idempotent.
7. Dashboard distinguishes cases attempted, numerical checks passed, transfer
   checks passed, reasoning self-reviewed and time spent (observed active use,
   capped/explicit; no fabricated daily study). Export is a private learner report
   with original responses, feedback, timestamp, limitations and next steps.
   Operator-only pilot aggregates count actual participation, primary/transfer
   attempts and distinct UTC days, without identities or written answers. These
   are not customer, sales conversion, retention guarantees or market-fit counts.
8. No raw corpus excerpts, operator-only metadata, hidden answers or paid prose
   enter public bundles, task DTOs, URLs or public Git additions. Original authored
   English lab content is distinct from older private French library material.
9. Existing audit findings F01–F16 are each fixed and rechecked, or an unavoidable
   external dependency is named precisely. In particular: correct Survival
   question/feedback timing and wave contract; course/generator and payoff context;
   true resume/completion; no Markdown comment leak; usable source references;
   mobile calculation first; simpler lesson hierarchy; finite service states and
   useful next actions from unavailable adjacent services; outcome-based packaging.
10. No payment, live LLM call, human review, market demand, licensed source right
    or public deployment is claimed without actual evidence. Existing sale gates
    remain fail-closed. New lab output does not depend on an external LLM API.

## API and CLI expectations

Use a versioned `/interview` namespace and strict bounded request models. Public
catalogue/task data must not include reference answers. Signed account state,
attempt and review endpoints use the current identity/entitlement middleware,
SQLite persistence, transactional writes and bounded idempotency keys. The
implementation documents its exact endpoint DTOs in its API/CLI smoke report.
Tests must exercise actual API handlers and deterministic numerical oracles,
cross-account access, validation, duplicate submit, correction-before-attempt,
variant transfer and restored state. Anonymous first-case checking may return
an explicitly unsaved result, without writing an invented account record.

Course reading position uses signed `PUT /platform/courses/{course_id}/position`
and `course_positions` in the existing private progress response. Navigation
cannot create lesson completions or points. Pilot aggregates use operator-only
`GET /interview/pilot/metrics`, including an explicit environment/scope notice.

## Delivery

Baseline checkpoints already pushed on `codex/2026-11-14-interview-lab`:
frontend `fd948a5`; backend `b88cd06`. Implementation is committed in reviewable
increments after tests, pushed without force, and independently reviewed against
this contract. A local PASS is not proof of a real purchase or market fit.
