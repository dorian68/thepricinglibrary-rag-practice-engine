# Original English courses — authoring and release contract

The English branch of `MaterialGenerator.generate_course` uses the original
curriculum in `course_english_content.py` and deterministic calculations. It
does not translate a private French lesson, call a paid LLM or substitute French
instructional prose when a topic is unsupported. French generation remains on
its existing branch. Book titles and brief genuine source quotations retain
their original language.

## Curriculum and private variants

There are twelve mapped subjects, with the existing catalogue's exact module
counts: vanilla 8; Greeks 9; swaps 9; curve 9; bonds 8; implied volatility 9;
Monte Carlo 10; stochastic calculus 10; barrier 9; CDS 8; autocall 10; VaR 9.
They target master's students and bank-derivatives candidates. The prose and
derivations are original teaching material; no textbook author endorsement,
hiring-outcome prediction or certified mastery is claimed.

The main written lessons contain a contract situation, topic-specific concept,
working method, assumptions, equation and three-step argument, checked numeric
application, task, reasoned correction and decision checkpoint. Shared methods
teach a consistent contract/unit/control workflow. The three written exercises
cover numerical reconstruction, operational criticism and a changed assumption;
they are not presented as three unseen quantitative assessments.

English section names are native: `Written course`, `Lesson`, `Worked numerical
example`, `Corrected exercises`, `Course-specific quiz`, `References`. Five
quiz questions each have five distinct options A–E. Correct positions rotate
across all five positions. `course_english_feedback.py` supplies 240 distinct,
authored explanations mapped to the exact wrong options. There is no lexical
classifier or generic fallback for distractor feedback.

Private documents are staged outside `pricinglibrary_rag/course_scripts` and
served only after accepted promotion into `course_scripts/en`. The entire
private tree remains ignored by Git and excluded from the public wheel. The
existing FR files are not rewritten. Missing EN variants remain unavailable;
the API's separate language contract must not silently return FR.

## Source and numerical evidence

`scripts/generate_english_courses.py` opens the original corpus with SQLite
`mode=ro` plus `PRAGMA query_only=ON`. No constructor, migration, ingestion or
pedagogy backfill is run on that database. Generation history goes to a distinct
staging database. Initial and final source-file size/mtime are compared.

The command obtains pedagogy statistics, retrieves by actual lesson subjects,
and selects contiguous source sentences. It excludes OCR controls, flattened
equations, indexes/bibliography fragments and unrelated snippets. Locators are
deduplicated. At least sixteen readable source chunks are required. Reviewed
public references use the existing slug/anchor/document/chunk allowlist and are
rechecked against the RO corpus; the French bibliography is used only as a
locator/quotation source, never for lesson prose. Public quotations are capped
at 24 words per source document. A private source ledger and raw generation
evidence remain in the ignored staging directory.

The case ticket and every displayed computed result are retained. Three legacy
calculators require technical parser labels in French: a keyword adapter for
bond, FX barrier and autocall preserves every numerical literal while passing
the same economic inputs. It does not fall back to another scenario. Both the
authored English ticket and adapted parser string are recorded in private
metadata. A missing numeric pack is an explicit error. The learner's text and
correction remain English.

Important boundaries are course-specific. Barrier scenarios are conditional
payoffs rather than a generic premium; autocall receipts are not net profit or
fair value; bond duration risk does not reconstruct a schedule; swap/credit
local risks freeze the supplied annuity; VaR uses the declared Gaussian model;
Monte Carlo reports sampling uncertainty based on independent antithetic pairs.
The portable barrier notebook is a separate bounded GBM laboratory. Synthetic
correlation widgets are labelled hypothetical and do not claim market estimates.

## Strict acceptance and review

```powershell
python scripts/generate_english_courses.py --output-dir generated_english_courses
python scripts/audit_course_quality.py --dir generated_english_courses --threshold 98 --json
python -m pytest -q tests/test_english_courses.py
```

The historical gate retains its FR behaviour. Its English extension retains
the 98 threshold, scoring weights and the 8-module, 3000-written-word,
320-average-lesson-word, 16-source and 5-widget requirements. It adds a hard
6500-word minimum on visible instructional prose **excluding widget JSON and
the back-office source ledger**, exact source-locator checks, recomputed numeric
metadata, five-option/varied-position quiz checks and French-instruction checks.
The two persona-oriented automated scores are artifact heuristics; they are
not evidence of actual student satisfaction or willingness to pay.

Passing that gate alone does not publish a variant. Independent Business Client
Mystère review must accept the exact artifact hashes. A review file for promotion
contains `verdict: PASS`, `reviewer_role: business_client_mystere` and a `courses`
list with each `slug` and `sha256`. Then:

```powershell
python scripts/generate_english_courses.py --output-dir generated_english_courses --promote --review-report review.json
```

Promotion refuses missing/failed reviews, changed hashes and sub-threshold
documents. It copies the reviewed raw bytes, verifies their hashes, then commits
`_index.json` using atomic replacement after all copies. The index has
`schema_version: tpl.course.language-index.v1` and a `courses` list containing
`slug`, raw-byte `sha256` and `status: accepted_98_and_independent_review`.
It also records language, real counts, source mode and independent-agent review
metadata without claiming human certification. No source-rights clearance or live authentication/payment
acceptance is implied by local content approval. The paid content's existing
rights and entitlement gates remain applicable.

After promotion, run `python scripts/smoke_published_english_courses.py`. It
requires the real accepted private documents, starts a fresh HTTP server and
invokes actual `tpl` processes for the catalogue and all twelve English reads.
It checks signed non-admin Pro access, Anonymous/Free denial, Student denial on
Pro courses, language/private-cache headers and absence of the private ledger.
Its identities/plans/rights flag are explicit technical fixtures, not claims of
a real Supabase login, purchase or legal clearance. No corpus is ingested or
written by this consumer test.
