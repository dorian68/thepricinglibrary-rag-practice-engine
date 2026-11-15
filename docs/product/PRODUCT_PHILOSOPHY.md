# PRODUCT_PHILOSOPHY.md — ThePricingLibrary

> Source of truth for *why* this product exists. Both the Technical RL Agent and
> the Business Client Mystère Agent must serve this file. Grounded in the real
> codebase as of 2026-06-06 — not aspirational marketing.

---

## Product name

**ThePricingLibrary** (TPL).

## Target users

Launch focus (2026-11-14): English-speaking master's students preparing bank
derivatives, sales/trading, structuring and market-risk interviews. This is not
a claim to cover proprietary-trading recruitment or to predict hiring outcomes.

Primary:
- Students (L3/M1/M2) in quantitative / market finance preparing for desk roles.
- Junior front-office profiles (trading, structuring, market risk) who must turn
  textbook theory into desk-usable calculations.
- Self-taught quants and dev-front-office building pricing/risk intuition.

Secondary:
- Instructors who need reusable, sourced teaching material (courses, exercises,
  quizzes) rather than building it from scratch.

## Problem solved

Quant-finance learning material is either (a) abstract academic theory with no
desk application, or (b) opaque desk lore with no rigorous grounding. Learners
cannot easily go from a formula to *"what do I actually do on a desk, with which
numbers, and why"*. Generic LLM chatbots hallucinate numbers and cite nothing.

## Pain point

- "I understand Black-Scholes on paper but I can't price and hedge a real ticket."
- "Course content online is generic, ungrounded, and I can't trust the numbers."
- "I want practice problems with *verified* corrections, not a chatbot guess."

## Product promise

> **Practice-first quant finance, grounded in a real source library and verified
> by a deterministic pricing engine.** The source-backed library uses an
> ingested corpus of finance books; numbers are computed by controlled
> calculators (not invented by an LLM), and provenance is explicit
> (`[extrait]` / `[reformule]` / `[genere]`).

The original English **Pricing & Greeks Interview Lab** supplements that
corpus-backed library. Its six authored cases and six conceptual variants use
the deterministic engine directly, without a textbook corpus or an LLM call.
Its trust claim is a reproducible calculation and retained learner response;
it does not claim retrieved sources, expert grading or certified mastery.

## Core value proposition

1. **Grounded** — content is retrieved from a real ingested PDF corpus (~123
   documents, ~47k chunks). The retrieved excerpts are injected into the LLM
   prompt (input-side `[Sx]` labels) so generation stays anchored. The learner
   sees a **clean references layer** (book titles + a readable excerpt), never
   the machinery (no `[Sx]` codes, chunk ids, scores, or family slugs).
2. **Verified** — every important number (BS price/greeks, swap DV01, bond
   duration, VaR, CS01…) is produced by `calculators.py`, so corrections are
   correct, not plausible.
3. **Honest** — grounding and provenance are tracked, but the distinction
   between extracted / reformulated / generated lives in **back-office**
   (`response.metadata`: family, calculation_pack, coherence, validation, raw
   sources). Nothing is fabricated, and pedagogical gaps are never invented —
   but the paying persona is shown a finished product, not the plumbing.
4. **Practice-first** — courses lead with intuition → mechanism → worked example
   → corrected exercise → quiz → decision, in desk language.

## Why the product should exist

Because the combination *grounded + verified + honest about provenance* is exactly
what a generic AI tutor cannot offer, and exactly what a learner heading for a
desk needs to build trustworthy intuition.

## Main value-producing workflow

The launch path is: select a bounded interview session → attempt a ticket and
write the reasoning → compare the deterministic correction → self-review the
argument → test a changed assumption → resume or export the actual record.
Anonymous first-case results are unsaved. Signed pilot access currently adds no
paid-plan requirement. The library retains its twelve French curricula and now
has twelve separately reviewed English curricula. English delivery requires the
exact accepted file hash in the private language index; a draft does not become
a published variant merely by existing. The existing French Starter Kit retains
its separate access and public-sale requirements.

The practical learning loop also retains written exercise attempts before
correction, a clearly labelled self-review and reproducible Python/Jupyter
references. Reports, CSV, revision cards and a voluntary calendar move the
student's work into their existing study tools. These formats do not certify
attendance, independent reasoning or hiring readiness.

The library-authoring workflow remains:

```text
Ingest finance corpus (PDF) ─▶ qualify each chunk pedagogically
        ─▶ retrieve usable, high-quality chunks for a topic
        ─▶ generate a course (per-lesson authored prose, grounded in [Sx])
           + verified worked example + corrected exercises + quiz
        ─▶ learner reads the course / solves a generated practice exercise
        ─▶ learner checks their answer against an engine-verified correction
```

The activation moment is: **the learner sees a correct, sourced worked example
they can reproduce by hand and get the same number.**

## What must be observable in the product

**Persona-facing (the client must see — clean, no machinery):**
- Verified numbers with their formula, substitution and result (the worked
  corrigé, with LaTeX demonstrations).
- A clean **References (bibliothèque)** list: real book titles + a readable
  excerpt — the trust signal that this comes from real sources.
- The honest fallback notice when content is locally generated (backend down).

**Back-office only (QA / trust audit / the engine — never shown to the persona):**
- Source machinery: `[Sx]` markers, chunk ids, retrieval scores, family slugs.
- Provenance/coherence/validation metadata (extracted vs reformulated vs
  generated, calculation_pack, coherence, validation) — kept in
  `response.metadata`, used internally, not surfaced to a paying user.

> Rule of thumb: when you would not say it to a client across a desk, it belongs
> in back-office, not in the rendered exercise.

## What must never be faked

- **Numbers.** A displayed price/greek/risk figure must come from a calculator
  or a cited source, never invented by the LLM.
- **Sources.** Every reference shown to the learner must map to a real ingested
  chunk; noisy/OCR excerpts are withheld (filtered out), never shown as a clean
  quote. The `[Sx]`/chunk/score mapping is retained in back-office, not displayed.
- **Grounding status.** If the backend is not reachable and content is locally
  generated, that must be disclosed, not presented as grounded.
- **Provenance.** Generated content must not be presented as extracted. The
  learner now sees a client-safe distinction between source excerpt,
  pedagogical rewrite and verified generation; raw chunk IDs, retrieval scores
  and internal metadata remain back-office only.

## What would make the product worth paying for

- Trustworthy, sourced, verified material that saves hours vs assembling it from
  textbooks — and that a generic chatbot demonstrably cannot match on trust.
- A coherent path from course → exercise → verified correction → progress.
- Tools (pricers, payoff, Monte Carlo, curve builder) that turn reading into
  doing.

## Anti-goals

- Not a generic AI chatbot.
- Not an ungrounded content mill.
- Not a pretty dashboard that computes nothing real.
