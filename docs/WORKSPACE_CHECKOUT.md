# Reproduce the public code checks

The backend and frontend live in two public repositories. Some numerical tests
compare the Python engine with the JavaScript engine and resolve shared fixtures
relative to the original workspace. A flat backend checkout does not provide
those sibling files automatically.

Use this layout (the workspace directory can have any name):

```text
workspace/
  fixtures/                         # restored from the backend snapshot below
  Tools/pricinglibrary_rag_backend/  # this repository
  WEBSITE/thepricinglab/            # public frontend repository
```

From a new workspace directory:

```bash
git clone --branch codex/2026-11-14-interview-lab https://github.com/dorian68/thepricinglibrary-rag-practice-engine.git Tools/pricinglibrary_rag_backend
git clone --branch codex/2026-11-14-interview-lab https://github.com/dorian68/thepricinglab.git WEBSITE/thepricinglab
```

Create a Python 3.11 environment, activate it and install the slim dependencies
from the backend directory. Node.js 22 must also be available; no npm packages
are required for the engine cross-checks.

```bash
cd Tools/pricinglibrary_rag_backend
python -m pip install -r requirements-docker.txt pytest httpx PyMuPDF
```

Restore the eleven original synthetic numerical contracts/golden fixtures.
The versioned `fixtures/` snapshots in both repositories must match byte-for-byte;
the CI workflow compares SHA-256 before copying anything to the workspace root.
The fixture directory pins JSON line endings to LF so Windows Git settings do
not change those bytes on checkout.
Run this Python code from the backend directory:

```python
from pathlib import Path
import hashlib
import shutil

backend = Path.cwd()
workspace = backend.parents[1]
target = workspace / "fixtures"
target.mkdir(exist_ok=True)
files = sorted((backend / "fixtures").glob("*.json"))
assert len(files) == 11
for fixture in files:
    sibling = workspace / "WEBSITE/thepricinglab/fixtures" / fixture.name
    assert hashlib.sha256(fixture.read_bytes()).digest() == hashlib.sha256(sibling.read_bytes()).digest()
    destination = target / fixture.name
    if destination.exists():
        assert destination.read_bytes() == fixture.read_bytes(), "Existing shared fixture differs; review before replacing it"
    else:
        shutil.copyfile(fixture, destination)
```

Run the same scoped tests used in the public CI:

```bash
python -m pytest -q --basetemp=.pytest_tmp_ci tests/test_interview_lab.py tests/test_english_generation.py tests/test_exercise_generation.py tests/test_generation_controls.py tests/test_generation_llm_guardrails.py tests/test_api_security.py tests/test_observability.py tests/test_black_scholes.py tests/test_binomial.py tests/test_bond.py tests/test_monte_carlo.py tests/test_monte_carlo_compat.py tests/test_payoff_strategy.py tests/test_realized_volatility.py tests/test_vol_surface.py tests/test_yield_curve.py
python scripts/smoke_interview_lab.py --output reports/interview_lab_ci_smoke.json
```

These tests use original synthetic ingestion text, isolated temporary SQLite
databases, test identities and the local template generator. They need no real
LLM key, Stripe account, Docker daemon, paid course scripts or textbook corpus.
The workflow also builds an API image on the CI runner without publishing it;
that build is separate from the commands above.

## What this gate establishes

The gate checks the public Python/JavaScript numerical contracts, signed learner
isolation, deterministic English generation, interview attempts/transfer,
resume/exports, explicit self-review, operator-only pilot aggregates and honest
local entitlement testing. Fixture snapshots contain only synthetic numerical
inputs, original expected values and engine contracts. They contain no learner
records, production credentials or licensed source material.

It does not certify a public deployment, a payment, licensed source rights,
complete paid-course delivery or demand from customers. The operator release
command remains `python scripts/production_check.py`; its wider checks require
the private reviewed course directory, genuine product release artifacts and the
documented deployment/evidence files. Do not publish those private assets to make
the public workflow appear to pass.

The CI frontend reference is currently
`dorian68/thepricinglab@codex/2026-11-14-interview-lab`. Publish the coordinated
frontend fixture/engine revision before triggering this backend workflow. Update
that explicit reference when promoting a later compatible pair; for a release,
record both exact commit SHAs to preserve the tested combination.
