"""Run the reproducible local release gates and report external blockers.

This command deliberately does not claim that a product is ready to sell. It
separates evidence that can be produced from the repository from gates that
require operator credentials, a deployed environment, legal approval or real
buyers.  It is safe to run in CI because it never prints environment values.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = REPO_ROOT / "Tools" / "pricinglibrary_rag_backend"
FRONTEND_ROOT = REPO_ROOT / "WEBSITE" / "thepricinglab"
STARTER_ROOT = REPO_ROOT / "Products" / "market_finance_starter_kit"


def run_gate(name: str, command: list[str], cwd: Path, timeout: int = 180) -> dict[str, Any]:
    """Run one gate without exposing environment variables or huge logs."""

    try:
        completed = subprocess.run(
            command,
            cwd=cwd,
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return {
            "name": name,
            "status": "FAIL",
            "command": " ".join(command),
            "detail": f"timeout after {timeout}s",
        }

    output = (completed.stdout + "\n" + completed.stderr).strip()
    # Keep the report useful in CI while preventing a noisy or accidental dump.
    if len(output) > 2000:
        output = output[-2000:]
    return {
        "name": name,
        "status": "PASS" if completed.returncode == 0 else "FAIL",
        "command": " ".join(command),
        "returncode": completed.returncode,
        "detail": output,
    }


def evidence_gate(name: str, path: Path, command: list[str], cwd: Path) -> dict[str, Any]:
    """Report a required external evidence file without treating absence as a local failure."""

    if not path.exists():
        return {
            "name": name,
            "status": "MISSING",
            "path": str(path.relative_to(REPO_ROOT)),
            "command": " ".join(command),
            "detail": "required external evidence file is absent; no synthetic evidence was created",
        }
    result = run_gate(name, command, cwd, timeout=60)
    result["path"] = str(path.relative_to(REPO_ROOT))
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json-out", type=Path, help="write the report to this path")
    parser.add_argument(
        "--skip-frontend-build",
        action="store_true",
        help="skip the Vite build when it has already been run by CI",
    )
    args = parser.parse_args()

    py = sys.executable
    npm = "npm.cmd" if sys.platform == "win32" else "npm"
    gates = [
        run_gate(
            "secret-scan",
            [py, "scripts/audit_secrets.py"],
            BACKEND_ROOT,
        ),
        run_gate(
            "deployed-acceptance-harness",
            [
                py,
                "-m",
                "pytest",
                "-q",
                "tests/test_audit_secrets.py",
                "tests/test_deployed_acceptance.py",
                "--basetemp=.pytest_tmp_release_acceptance",
            ],
            BACKEND_ROOT,
        ),
        run_gate(
            "backend-full-test-suite",
            [
                py,
                "-m",
                "pytest",
                "-q",
                "--basetemp=.pytest_tmp_release_full",
            ],
            BACKEND_ROOT,
            timeout=180,
        ),
        run_gate(
            "local-http-deployment-smoke",
            [py, "scripts/smoke_local_deployment.py"],
            BACKEND_ROOT,
            timeout=120,
        ),
        run_gate(
            "local-rollback-smoke",
            [py, "scripts/smoke_local_rollback.py"],
            BACKEND_ROOT,
            timeout=180,
        ),
        run_gate(
            "docker-runtime-smoke",
            [py, "scripts/smoke_docker_runtime.py"],
            BACKEND_ROOT,
            timeout=300,
        ),
        run_gate(
            "starter-kit-excel-contract",
            [py, "scripts/verify_excel_dashboard.py"],
            STARTER_ROOT,
        ),
        run_gate(
            "starter-kit-release-bundle",
            [py, "scripts/verify_bundle.py"],
            STARTER_ROOT,
        ),
        run_gate(
            "course-quality",
            [
                py,
                "scripts/audit_course_quality.py",
                "--dir",
                "pricinglibrary_rag/course_scripts",
                "--threshold",
                "98",
                "--json",
            ],
            BACKEND_ROOT,
        ),
        run_gate(
            "course-manifest-contract",
            [py, "scripts/audit_course_manifest.py"],
            BACKEND_ROOT,
        ),
        run_gate(
            "public-course-projection",
            [py, "scripts/audit_public_course_projection.py"],
            BACKEND_ROOT,
        ),
        run_gate(
            "course-objective-contract",
            [py, "scripts/audit_course_objective.py"],
            BACKEND_ROOT,
        ),
        run_gate(
            "backend-production-smoke",
            [py, "scripts/production_check.py"],
            BACKEND_ROOT,
            timeout=240,
        ),
    ]
    if not args.skip_frontend_build:
        gates.extend(
            [
                run_gate(
                    "frontend-dependency-audit",
                    [npm, "audit", "--audit-level=high"],
                    FRONTEND_ROOT,
                ),
                run_gate("frontend-lint", [npm, "run", "lint"], FRONTEND_ROOT),
                run_gate("frontend-typecheck", [npm, "run", "typecheck"], FRONTEND_ROOT),
                run_gate(
                    "frontend-navigation-security",
                    [npm, "run", "smoke:navigation-security"],
                    FRONTEND_ROOT,
                ),
                run_gate(
                    "frontend-product-contract",
                    [npm, "run", "smoke:product-contract"],
                    FRONTEND_ROOT,
                ),
                run_gate("frontend-business-audit", [npm, "run", "audit:business"], FRONTEND_ROOT),
                run_gate("frontend-build", [npm, "run", "build"], FRONTEND_ROOT),
                run_gate("frontend-trust-artifact", [npm, "run", "audit:frontend-trust"], FRONTEND_ROOT),
                run_gate(
                    "frontend-retired-surface-firewall",
                    [npm, "run", "smoke:retired-surfaces"],
                    FRONTEND_ROOT,
                ),
            ]
        )

    missing_local_inputs = [
        str(path.relative_to(REPO_ROOT))
        for path in (
            STARTER_ROOT / "release" / "manifest.json",
            STARTER_ROOT / "release" / "starter-kit-v1.0.0.zip",
        )
        if not path.exists()
    ]
    external_blockers = [
        "revoke and rotate any credentials that were exposed before repository redaction",
        "real legal identity, operator contact, mediation data and source-rights clearance",
        "production Stripe prices, webhook secret and tested refund/chargeback flow",
        "production Supabase issuer/JWKS and server-only secrets",
        "staging deployment with three purchases, cancellation and refund",
        "public observability, alert and rollback drill",
        "five-user target-customer pilot with recorded outcomes",
        "public domain must serve the current trust-clean frontend bundle; the known domain currently serves stale unsupported marketing claims",
    ]
    external_evidence = [
        evidence_gate(
            "staging-release-evidence",
            REPO_ROOT / "reports" / "staging_evidence.json",
            [py, "scripts/validate_release_evidence.py", "--kind", "staging", "--input", str(REPO_ROOT / "reports" / "staging_evidence.json")],
            BACKEND_ROOT,
        ),
        evidence_gate(
            "rollback-release-evidence",
            REPO_ROOT / "reports" / "rollback_evidence.json",
            [py, "scripts/validate_release_evidence.py", "--kind", "rollback", "--input", str(REPO_ROOT / "reports" / "rollback_evidence.json")],
            BACKEND_ROOT,
        ),
        evidence_gate(
            "pilot-evidence",
            REPO_ROOT / "reports" / "pilot_evidence.json",
            [py, "scripts/validate_pilot_evidence.py", "--input", str(REPO_ROOT / "reports" / "pilot_evidence.json")],
            BACKEND_ROOT,
        ),
        evidence_gate(
            "rights-clearance-evidence",
            REPO_ROOT / "reports" / "rights_clearance_evidence.json",
            [py, "scripts/validate_rights_evidence.py", "--input", str(REPO_ROOT / "reports" / "rights_clearance_evidence.json")],
            BACKEND_ROOT,
        ),
    ]
    missing_external_evidence = [item["name"] for item in external_evidence if item["status"] != "PASS"]
    failed_gates = [gate["name"] for gate in gates if gate["status"] != "PASS"]
    report: dict[str, Any] = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repository": str(REPO_ROOT),
        "local_gates": gates,
        "local_artifact_blockers": missing_local_inputs,
        "external_blockers": external_blockers,
        "external_evidence": external_evidence,
        "missing_external_evidence": missing_external_evidence,
        "ready_to_sell": False,
        "local_gates_pass": not failed_gates and not missing_local_inputs,
        "failed_local_gates": failed_gates,
        "verdict": "NOT_READY_EXTERNAL_GATES_REQUIRED",
    }

    encoded = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(encoded, encoding="utf-8")
    print(encoded, end="")
    # A readiness report is informational; the individual gates carry failure.
    return 0 if not failed_gates and not missing_local_inputs else 1


if __name__ == "__main__":
    raise SystemExit(main())
