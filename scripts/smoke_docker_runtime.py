"""Run a real, isolated Docker runtime smoke for the backend image.

This is local Technical RL evidence only. It uses generated test credentials,
an ephemeral Docker volume and a loopback port; it never contacts Stripe,
Supabase or a public staging service and never writes release evidence files.
"""

from __future__ import annotations

import json
from http.client import RemoteDisconnected
import shutil
import socket
import subprocess
import time
import uuid
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


BACKEND_ROOT = Path(__file__).resolve().parents[1]
IMAGE_TAG = f"tpl-backend:local-runtime-{uuid.uuid4().hex[:12]}"
CONTAINER_NAME = f"tpl-backend-local-runtime-{uuid.uuid4().hex[:12]}"
VOLUME_NAME = f"tpl-data-local-runtime-{uuid.uuid4().hex[:12]}"
MEMBER_KEY = "local-member-key-for-docker-runtime-smoke-20260725"
OPERATOR_KEY = "local-operator-key-for-docker-runtime-smoke-20260725"
AUTH_SECRET = "local-auth-secret-for-docker-runtime-smoke-20260725"


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _run(command: list[str], *, timeout: int = 180) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=BACKEND_ROOT,
        text=True,
        capture_output=True,
        timeout=timeout,
        check=False,
    )


def _docker(command: list[str], *, timeout: int = 180) -> subprocess.CompletedProcess[str]:
    return _run(["docker", *command], timeout=timeout)


def _http(base_url: str, path: str, headers: dict[str, str] | None = None) -> tuple[int, bytes]:
    request = Request(f"{base_url}{path}", headers=headers or {})
    try:
        with urlopen(request, timeout=5) as response:
            return response.status, response.read()
    except HTTPError as exc:
        return exc.code, exc.read()
    except (OSError, RemoteDisconnected, URLError):
        return 0, b""


def _wait_for(base_url: str, path: str, expected: int, timeout: float = 60.0) -> tuple[int, bytes]:
    deadline = time.monotonic() + timeout
    last: tuple[int, bytes] = (0, b"")
    while time.monotonic() < deadline:
        last = _http(base_url, path)
        if last[0] == expected:
            return last
        time.sleep(0.5)
    return last


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _wait_for_container_health(timeout: float = 60.0) -> str:
    deadline = time.monotonic() + timeout
    status = "unknown"
    while time.monotonic() < deadline:
        inspected = _docker(["inspect", "--format", "{{.State.Health.Status}}", CONTAINER_NAME], timeout=10)
        status = inspected.stdout.strip() if inspected.returncode == 0 else "unknown"
        if status in {"healthy", "unhealthy"}:
            return status
        time.sleep(0.5)
    return status


def main() -> int:
    docker_path = shutil.which("docker")
    if not docker_path:
        print("DOCKER RUNTIME SMOKE FAIL: docker executable unavailable")
        return 1

    port = _free_port()
    base_url = f"http://127.0.0.1:{port}"
    container_started = False
    volume_created = False
    try:
        build = _docker(["build", "--tag", IMAGE_TAG, "."], timeout=240)
        _assert(build.returncode == 0, "Docker image build failed")
        volume = _docker(["volume", "create", VOLUME_NAME], timeout=30)
        _assert(volume.returncode == 0, "Docker volume creation failed")
        volume_created = True

        run = _docker(
            [
                "run",
                "--detach",
                "--name",
                CONTAINER_NAME,
                "--publish",
                f"127.0.0.1:{port}:8000",
                "--read-only",
                "--tmpfs",
                "/tmp:rw,noexec,nosuid,size=64m",
                "--cap-drop",
                "ALL",
                "--security-opt",
                "no-new-privileges",
                "--volume",
                f"{VOLUME_NAME}:/data",
                "--env",
                "TPL_ENVIRONMENT=production",
                "--env",
                f"TPL_API_KEY={MEMBER_KEY}",
                "--env",
                f"TPL_OPERATOR_API_KEY={OPERATOR_KEY}",
                "--env",
                f"TPL_AUTH_TOKEN_SECRET={AUTH_SECRET}",
                "--env",
                "TPL_RATE_LIMIT_PER_MIN=60",
                "--env",
                "TPL_RATE_LIMIT_WINDOW_SECONDS=60",
                "--env",
                "TPL_LLM_PROVIDER=template",
                "--env",
                "GENERATION_MODE=template",
                "--env",
                "RETRIEVAL_MODE=hybrid",
                "--env",
                "EMBEDDING_PROVIDER=local",
                "--env",
                "GENERATION_STRICT_VALIDATION=true",
                IMAGE_TAG,
            ],
            timeout=30,
        )
        _assert(run.returncode == 0, "Docker container failed to start")
        container_started = True

        health_status, health_body = _wait_for(base_url, "/health", 200)
        _assert(health_status == 200, "Docker health endpoint did not return 200")
        health = json.loads(health_body.decode("utf-8"))
        _assert(health.get("security", {}).get("ready") is True, "Docker security readiness is not true")
        _assert(health.get("security", {}).get("rate_limit_backend") == "sqlite", "Docker rate limiter is not active")

        ready_status, _ = _wait_for(base_url, "/ready", 200)
        _assert(ready_status == 200, "Docker readiness endpoint did not return 200")
        _assert(_wait_for_container_health() == "healthy", "Docker healthcheck is not healthy")

        protected_status, _ = _http(base_url, "/courses/vanilla-options-quote/script")
        _assert(protected_status == 401, "anonymous protected course request was not denied")
        anonymous_metrics_status, _ = _http(base_url, "/metrics")
        _assert(anonymous_metrics_status == 401, "anonymous metrics request was not denied")
        operator_metrics_status, metrics_body = _http(base_url, "/metrics", {"X-API-Key": OPERATOR_KEY})
        _assert(operator_metrics_status == 200, "operator metrics scrape did not return 200")
        metrics_text = metrics_body.decode("utf-8", errors="replace")
        _assert(MEMBER_KEY not in metrics_text and OPERATOR_KEY not in metrics_text, "metrics leaked test credentials")

        print(
            "DOCKER RUNTIME SMOKE PASS: image built, production-guarded container healthy, "
            "readiness/health passed, anonymous protected routes denied and operator metrics isolated"
        )
        return 0
    except (OSError, RuntimeError, subprocess.SubprocessError, json.JSONDecodeError) as exc:
        print(f"DOCKER RUNTIME SMOKE FAIL: {type(exc).__name__}: {exc}")
        return 1
    finally:
        if container_started:
            _docker(["rm", "--force", CONTAINER_NAME], timeout=30)
        if volume_created:
            _docker(["volume", "rm", "--force", VOLUME_NAME], timeout=30)
        _docker(["image", "rm", "--force", IMAGE_TAG], timeout=60)


if __name__ == "__main__":
    raise SystemExit(main())
