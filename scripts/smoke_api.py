"""HTTP-contract smoke test for the live API surface (J2 enabler).

Backend-first, fully offline and free:
- throwaway SQLite DB + template LLM (no OpenAI call, no network port);
- ingests a small mock corpus so retrieval has real content;
- drives the FastAPI app in-process via Starlette TestClient;
- asserts the response CONTRACT the frontend depends on:
    /health           -> 200
    /agent/exercise   -> 200, sources[] non-empty, [Sx] grounding,
                          metadata.llm present, verified calculation_pack
    /agent/course     -> 200, sources[], lessons, metadata.llm

Structured logs follow backend_first_debugging_paradigm.md. Exits non-zero on
the first contract breach.

Usage:
    python scripts/smoke_api.py
"""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

# Offline, deterministic config BEFORE importing the package.
_TMP = Path(tempfile.mkdtemp(prefix="tpl_smoke_api_"))
os.environ["TPL_DATA_DIR"] = str(_TMP)
os.environ["TPL_DB_PATH"] = str(_TMP / "smoke_api.sqlite3")
os.environ["TPL_LLM_PROVIDER"] = "template"
os.environ["TPL_EMBEDDING_BACKEND"] = "local-hashing"
os.environ["TPL_EMBEDDING_DIM"] = "512"

from starlette.testclient import TestClient  # noqa: E402

from pricinglibrary_rag.api import create_app  # noqa: E402
from pricinglibrary_rag.factory import build_services  # noqa: E402
from pricinglibrary_rag.schemas import DocumentMetadata  # noqa: E402

# Reuse the same rich mock corpus as the course smoke.
from smoke_course_generation import MOCK_SOURCES  # noqa: E402

_failures: list[str] = []
_step = 0


def log(status: str, request: str, output: str = "", error: str = "", nxt: str = "") -> None:
    global _step
    _step += 1
    print(f"[STEP {_step}] {request}")
    print(f"  [STATUS] {status}")
    if output:
        print(f"  [OUTPUT] {output}")
    if error:
        print(f"  [ERROR]  {error}")
    if nxt:
        print(f"  [NEXT]   {nxt}")


def check(cond: bool, label: str, *, output: str = "", error: str = "") -> bool:
    if cond:
        log("ok", label, output=output)
    else:
        _failures.append(label)
        log("fail", label, error=error or "assertion failed")
    return cond


def _seed(services) -> int:
    src_dir = _TMP / "mock_sources"
    src_dir.mkdir(parents=True, exist_ok=True)
    for name, body in MOCK_SOURCES.items():
        (src_dir / name).write_text(body.strip() + "\n", encoding="utf-8")
    results = services.ingestion.ingest_directory(
        src_dir,
        metadata=DocumentMetadata(
            product="FX barrier option",
            asset_class="fx",
            concepts=["barrier", "gap risk", "monitoring"],
            tags=["mock", "smoke"],
        ),
        glob="*.md",
        recursive=False,
    )
    services.retriever.refresh()
    return sum(1 for r in results if r.status == "ingested")


def main() -> int:
    print("=" * 64)
    print("  SMOKE TEST - live API contract (/health, /agent/*)")
    print("=" * 64)

    services = build_services()
    ingested = _seed(services)
    check(ingested > 0, "corpus seeded for retrieval", output=f"{ingested} docs ingested")

    client = TestClient(create_app(services))

    # --- /health ----------------------------------------------------------
    r = client.get("/health")
    check(r.status_code == 200, "GET /health -> 200",
          output=str(r.json())[:120], error=f"status {r.status_code}")

    # --- /agent/exercise --------------------------------------------------
    payload = {
        "topic": "Barrier options and gap risk",
        "product": "FX barrier option",
        "concept": "down-and-out call",
        "difficulty": "advanced",
        "exercise_format": "quantitative_problem",
        "number_of_questions": 4,
        "require_calculations": True,
        "language": "fr",
    }
    r = client.post("/agent/exercise", json=payload)
    if check(r.status_code == 200, "POST /agent/exercise -> 200",
             error=f"status {r.status_code}: {r.text[:200]}"):
        data = r.json()
        content = data.get("content", "")
        sources = data.get("sources", []) or []
        meta = data.get("metadata", {}) or {}
        check(len(sources) > 0, "exercise: sources[] non-empty",
              output=f"{len(sources)} sources")
        check("[S" in content, "exercise: [Sx] grounding markers in content")
        check(bool(meta.get("llm")), "exercise: metadata.llm present",
              output=str(meta.get("llm")))
        pack = meta.get("calculation_pack")
        check(isinstance(pack, dict) and bool(pack),
              "exercise: verified calculation_pack present",
              output=f"keys={list(pack)[:6] if isinstance(pack, dict) else pack}")
        # J2 VALUE assertions (F-EXO-3): the answer key must be a REAL computed
        # result from a recognized calculator family, not a generic placeholder.
        if isinstance(pack, dict):
            family = str(pack.get("family", ""))
            steps = pack.get("steps") or []
            numeric_result = any(
                any(ch.isdigit() for ch in str(s.get("result", "")))
                for s in steps if isinstance(s, dict)
            )
            check(bool(family) and family != "generic",
                  "exercise: recognized calculator family (not generic)",
                  output=family or "(empty)")
            check(numeric_result,
                  "exercise: at least one step has a numeric result",
                  output=f"{len(steps)} steps")
        check(bool(__import__("re").search(r"(?i)corrig|correction|solution", content)),
              "exercise: correction/solution section present")

    # --- /agent/course ----------------------------------------------------
    course_payload = {
        "topic": "Barrier options and gap risk",
        "product": "FX barrier option",
        "concepts": ["down-and-out", "knock-out", "gap risk"],
        "level": "advanced",
        "duration_minutes": 120,
        "module_count": 4,
        "language": "fr",
    }
    r = client.post("/agent/course", json=course_payload)
    if check(r.status_code == 200, "POST /agent/course -> 200",
             error=f"status {r.status_code}: {r.text[:200]}"):
        data = r.json()
        content = data.get("content", "")
        sources = data.get("sources", []) or []
        meta = data.get("metadata", {}) or {}
        check(len(sources) > 0, "course: sources[] non-empty",
              output=f"{len(sources)} sources")
        check("### Lecon" in content, "course: written lessons present")
        check(bool(meta.get("llm")), "course: metadata.llm present",
              output=str(meta.get("llm")))

    # --- /billing ---------------------------------------------------------
    r = client.get("/billing/config")
    if check(r.status_code == 200, "GET /billing/config -> 200"):
        cfg = r.json()
        check("mode" in cfg and "plans" in cfg, "billing: config has mode + plans",
              output=str(cfg))
    r = client.post("/billing/checkout", json={"plan": "starter", "email": "smoke@desk.com"})
    if check(r.status_code == 200, "POST /billing/checkout -> 200",
             error=f"status {r.status_code}: {r.text[:160]}"):
        s = r.json()
        check(bool(s.get("id")) and bool(s.get("url")) and s.get("mode") in ("mock", "live"),
              "billing: checkout returns id + url + mode", output=str(s))
    r = client.post("/billing/checkout", json={"plan": "enterprise"})
    check(r.status_code == 400, "billing: unknown plan rejected (400)",
          error=f"status {r.status_code}")

    # --- teardown ---------------------------------------------------------
    import shutil
    shutil.rmtree(_TMP, ignore_errors=True)

    print("=" * 64)
    if _failures:
        print("SMOKE: FAIL")
        for f in _failures:
            print(f"  - {f}")
        return 1
    print("SMOKE: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
