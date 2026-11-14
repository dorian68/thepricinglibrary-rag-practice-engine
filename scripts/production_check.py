"""Aggregate, offline P0 production gate for the backend.

This does not contact live services or deploy anything. It validates the
security policy through HTTP, the existing API journey, focused pytest coverage,
and the slim Docker runtime manifest/import contract.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _run(step: int, label: str, command: list[str]) -> bool:
    print(f"[STEP {step}] {label}")
    print("  [REQUEST] " + " ".join(command))
    result = subprocess.run(command, cwd=ROOT, check=False)
    status = "ok" if result.returncode == 0 else "fail"
    print(f"  [STATUS] {status}")
    print(f"  [OUTPUT] exit_code={result.returncode}")
    return result.returncode == 0


def _docker_manifest_check() -> bool:
    required = {
        "fastapi",
        "uvicorn",
        "pydantic",
        "numpy",
        "pandas",
        "requests",
        "pyjwt",
        "scikit-learn",
        "openai",
        "stripe",
    }
    manifest = (ROOT / "requirements-docker.txt").read_text(encoding="utf-8")
    packages = {
        line.strip().split("[", 1)[0].split(">", 1)[0].split("=", 1)[0].lower()
        for line in manifest.splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }
    missing = sorted(required - packages)
    print("[STEP 6] slim Docker runtime manifest + API import")
    print("  [REQUEST] requirements-docker.txt and import pricinglibrary_rag.api")
    if missing:
        print("  [STATUS] fail")
        print(f"  [ERROR] missing runtime packages: {missing}")
        return False
    result = subprocess.run(
        [sys.executable, "-c", "from pricinglibrary_rag.api import app; assert len(app.routes) > 0"],
        cwd=ROOT,
        check=False,
    )
    ok = result.returncode == 0
    print(f"  [STATUS] {'ok' if ok else 'fail'}")
    print(f"  [OUTPUT] manifest complete; api_import_exit={result.returncode}")
    return ok


def main() -> int:
    checks = [
        _run(
            1,
            "focused security tests",
            [
                sys.executable,
                "-m",
                "pytest",
                "-q",
                "tests/test_api_security.py",
                "tests/test_starter_kit_fulfillment.py",
                "--basetemp=.pytest_tmp_production",
            ],
        ),
        _run(8, "production observability and RUM smoke", [sys.executable, "scripts/smoke_observability.py"]),
        _run(2, "production auth/RBAC smoke", [sys.executable, "scripts/smoke_production_security.py"]),
        _run(3, "billing lifecycle and revocation smoke", [sys.executable, "scripts/smoke_billing.py"]),
        _run(4, "starter kit one-shot fulfillment smoke", [sys.executable, "scripts/smoke_starter_kit_fulfillment.py"]),
        _run(5, "existing API journey smoke", [sys.executable, "scripts/smoke_api.py"]),
        _docker_manifest_check(),
        _run(
            7,
            "Docker Compose deployment template contract",
            [
                sys.executable,
                "scripts/check_deployment_contract.py",
                "--env-file",
                ".env.production.example",
                "--allow-placeholders",
            ],
        ),
    ]
    print(f"[VERDICT] {'PASS' if all(checks) else 'FAIL'}")
    return 0 if all(checks) else 1


if __name__ == "__main__":
    raise SystemExit(main())
