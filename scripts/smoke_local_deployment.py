"""Run the deployed acceptance probe against a real ephemeral local API process.

This is stronger than a mocked HTTP harness but deliberately not a production
or Stripe/Supabase acceptance test. It starts Uvicorn with a temporary SQLite
database, the verified Starter Kit artifact and a non-networked fake Stripe
configuration only to make the public availability contract observable.
"""

from __future__ import annotations

import json
import gc
import os
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

BACKEND_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = BACKEND_ROOT.parents[1]
STARTER_ROOT = REPO_ROOT / "Products" / "market_finance_starter_kit"
PROBE = BACKEND_ROOT / "scripts" / "smoke_deployed_acceptance.py"
LOCAL_AUTH_SECRET = "local-hs256-session-secret-for-http-smoke-000000000000"
LOCAL_USER_ID = "local-http-entitled-user"

sys.path.insert(0, str(BACKEND_ROOT))
from pricinglibrary_rag.security import mint_session_token  # noqa: E402
from pricinglibrary_rag.storage import LocalStore  # noqa: E402


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _wait_for_health(base_url: str, process: subprocess.Popen[bytes], timeout: float = 35.0) -> None:
    deadline = time.monotonic() + timeout
    last_error = "not started"
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError(f"local API exited before health check (code {process.returncode})")
        try:
            with urlopen(f"{base_url}/health", timeout=2) as response:
                if response.status == 200:
                    return
                last_error = f"HTTP {response.status}"
        except (OSError, URLError) as exc:
            last_error = type(exc).__name__
        time.sleep(0.25)
    raise RuntimeError(f"local API health timeout ({last_error})")


def local_fixture_environment(data_dir: str | Path, bundle: Path, manifest: Path) -> dict[str, str]:
    """Return isolated production-guarded fixture settings for local HTTP probes."""

    env = os.environ.copy()
    env.update(
        {
            "TPL_ENVIRONMENT": "production",
            # Local fixture assertion: this smoke represents an operator-approved
            # commercial deployment. Real production must obtain this from the
            # reviewed rights evidence file; the Settings default remains false.
            "TPL_SOURCE_RIGHTS_CLEARED": "true",
            "TPL_DATA_DIR": str(data_dir),
            "TPL_DB_PATH": str(Path(data_dir) / "pricinglibrary_rag.sqlite3"),
            "TPL_EMBEDDING_BACKEND": "local-hashing",
            "TPL_EMBEDDING_DIM": "2048",
            "GENERATION_MODE": "template",
            "RETRIEVAL_MODE": "hybrid",
            "EMBEDDING_PROVIDER": "local",
            "GENERATION_STRICT_VALIDATION": "true",
            "TPL_API_KEY": "local-member-key-for-http-smoke-000000000000",
            "TPL_OPERATOR_API_KEY": "local-operator-key-for-http-smoke-000",
            "TPL_AUTH_TOKEN_SECRET": LOCAL_AUTH_SECRET,
            "TPL_AUTH_ALGORITHMS": "HS256",
            "TPL_RATE_LIMIT_PER_MIN": "60",
            "TPL_RATE_LIMIT_WINDOW_SECONDS": "60",
            "TPL_CORS_ORIGINS": "https://staging.example.invalid",
            "STRIPE_SECRET_KEY": "sk_test_local_acceptance_fixture",
            "STRIPE_PRICE_STARTER_KIT": "price_local_acceptance_fixture",
            "TPL_BILLING_SUCCESS_URL": "https://staging.example.invalid/#/billing/success?session_id={CHECKOUT_SESSION_ID}",
            "TPL_BILLING_CANCEL_URL": "https://staging.example.invalid/#/billing/cancel",
            "TPL_STARTER_KIT_BUNDLE_PATH": str(bundle),
            "TPL_STARTER_KIT_MANIFEST_PATH": str(manifest),
            "TPL_STARTER_KIT_SUCCESS_URL": "https://staging.example.invalid/#/starter-kit/success",
            "TPL_STARTER_KIT_CANCEL_URL": "https://staging.example.invalid/#/starter-kit/cancel",
        }
    )
    env.pop("TPL_STAGING_ACCESS_TOKEN", None)
    return env


def _local_http_request(
    base_url: str,
    path: str,
    *,
    method: str = "GET",
    headers: dict[str, str] | None = None,
    body: bytes | None = None,
) -> tuple[int, bytes]:
    request = Request(
        f"{base_url}{path}",
        method=method,
        headers=headers or {},
        data=body,
    )
    try:
        with urlopen(request, timeout=10) as response:
            return response.status, response.read()
    except HTTPError as exc:
        return exc.code, exc.read()


def main() -> int:
    bundle = STARTER_ROOT / "release" / "starter-kit-v1.0.0.zip"
    manifest = STARTER_ROOT / "release" / "manifest.json"
    if not bundle.is_file() or not manifest.is_file():
        print("LOCAL DEPLOYMENT SMOKE FAIL: verified Starter Kit artifact is missing")
        return 1

    port = _free_port()
    base_url = f"http://127.0.0.1:{port}"
    with tempfile.TemporaryDirectory(prefix="tpl-local-deployment-") as data_dir:
        env = local_fixture_environment(data_dir, bundle, manifest)
        process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "pricinglibrary_rag.api:app", "--host", "127.0.0.1", "--port", str(port)],
            cwd=BACKEND_ROOT,
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        try:
            _wait_for_health(base_url, process)
            local_store = LocalStore(Path(data_dir) / "pricinglibrary_rag.sqlite3")
            local_store.upsert_product_entitlement(
                LOCAL_USER_ID,
                "market-finance-starter-kit",
                status="active",
                source="local-http-smoke",
            )
            del local_store
            gc.collect()
            env["TPL_STAGING_ACCESS_TOKEN"] = mint_session_token(
                LOCAL_AUTH_SECRET,
                user_id=LOCAL_USER_ID,
                email="local-http-entitled@example.invalid",
                expires_at=int(time.time()) + 300,
            )
            report_path = Path(data_dir) / "deployed_acceptance.json"
            probe = subprocess.run(
                [
                    sys.executable,
                    str(PROBE),
                    "--base-url",
                    base_url,
                    "--allow-http-local",
                    "--require-entitled",
                    "--json-out",
                    str(report_path),
                ],
                cwd=BACKEND_ROOT,
                env=env,
                text=True,
                capture_output=True,
                timeout=60,
                check=False,
            )
            if probe.returncode != 0:
                failed_names: list[str] = []
                try:
                    failed_report = json.loads(report_path.read_text(encoding="utf-8"))
                    failed_names = [
                        str(item.get("name"))
                        for item in failed_report.get("checks", [])
                        if item.get("pass") is False
                    ]
                except (OSError, json.JSONDecodeError):
                    pass
                suffix = f": {', '.join(failed_names)}" if failed_names else ""
                print(f"LOCAL DEPLOYMENT SMOKE FAIL: deployed acceptance probe failed{suffix}")
                return 1
            report = json.loads(report_path.read_text(encoding="utf-8"))
            if report.get("verdict") != "PASS" or report.get("failed_checks") != 0:
                print("LOCAL DEPLOYMENT SMOKE FAIL: acceptance report was not PASS")
                return 1
            rum_payload = json.dumps(
                {
                    "metric": "LCP",
                    "value": 2600,
                    "route": "/courses/local-http-observability-slug?email=private@example.invalid",
                    "navigation_type": "navigate",
                }
            ).encode("utf-8")
            rum_status, rum_body = _local_http_request(
                base_url,
                "/telemetry/rum",
                method="POST",
                headers={"Content-Type": "application/json"},
                body=rum_payload,
            )
            metrics_status, metrics_body = _local_http_request(
                base_url,
                "/metrics",
                headers={"X-API-Key": env["TPL_OPERATOR_API_KEY"]},
            )
            metrics_text = metrics_body.decode("utf-8", errors="replace")
            rum_response = json.loads(rum_body.decode("utf-8")) if rum_body else {}
            private_values_absent = all(
                value not in metrics_text
                for value in (
                    "local-http-observability-slug",
                    "private@example.invalid",
                    env["TPL_API_KEY"],
                    env["TPL_OPERATOR_API_KEY"],
                )
            )
            if not (
                rum_status == 202
                and rum_response.get("route") == "/courses/:slug"
                and metrics_status == 200
                and 'metric="LCP",route="/courses/:slug"' in metrics_text
                and private_values_absent
            ):
                print("LOCAL DEPLOYMENT SMOKE FAIL: HTTP observability privacy contract failed")
                return 1
            print(
                "LOCAL DEPLOYMENT SMOKE PASS: real local API process, verified artifact, "
                "public readiness/availability, anonymous denial, entitled SHA-256 download "
                "and operator RUM/Prometheus privacy"
            )
            return 0
        except (OSError, RuntimeError, subprocess.SubprocessError, json.JSONDecodeError) as exc:
            print(f"LOCAL DEPLOYMENT SMOKE FAIL: {type(exc).__name__}")
            return 1
        finally:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=10)
            gc.collect()


if __name__ == "__main__":
    raise SystemExit(main())
