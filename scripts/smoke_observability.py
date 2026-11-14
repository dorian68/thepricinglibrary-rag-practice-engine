"""Offline production observability smoke: request IDs, RUM and metrics RBAC."""

from __future__ import annotations

import re
import sys
import tempfile
from pathlib import Path

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from pricinglibrary_rag.api import create_app
from pricinglibrary_rag.config import Settings
from pricinglibrary_rag.factory import build_services


MEMBER_KEY = "member_" + "m" * 40
OPERATOR_KEY = "operator_" + "o" * 40


def _settings(root: Path) -> Settings:
    return Settings(
        data_dir=root,
        db_path=root / "observability-smoke.sqlite3",
        embedding_backend="local-hashing",
        embedding_dim=64,
        sentence_transformer_model=None,
        llm_provider="template",
        openai_api_key=None,
        openai_model="gpt-4o-mini",
        openai_base_url=None,
        openai_timeout_seconds=10,
        openai_max_retries=0,
        ollama_url="http://localhost:11434",
        ollama_model="dummy",
        transformers_model_path=None,
        chunk_target_chars=700,
        chunk_overlap_chars=80,
        max_context_chunks=4,
        environment="production",
        api_key=MEMBER_KEY,
        operator_api_key=OPERATOR_KEY,
        auth_token_secret="identity_" + "s" * 40,
        rate_limit_per_min=100,
    )


def _step(number: int, label: str, passed: bool, output: str) -> bool:
    print(
        f"[STEP {number}] {label} · [STATUS] {'ok' if passed else 'fail'} · "
        f"[INPUT] sanitized local request · [OUTPUT] {output} · "
        f"[ERROR] {'none' if passed else output} · [NEXT] {'continue' if passed else 'stop'}"
    )
    return passed


def main() -> int:
    checks: list[bool] = []
    with tempfile.TemporaryDirectory(prefix="tpl-observability-") as temporary:
        client = TestClient(create_app(build_services(_settings(Path(temporary)))))
        operator = {"X-API-Key": OPERATOR_KEY}

        health = client.get("/health", headers={"X-Request-ID": "untrusted"})
        request_id = health.headers.get("X-Request-ID", "")
        checks.append(
            _step(
                1,
                "server-generated request correlation",
                health.status_code == 200
                and bool(re.fullmatch(r"[0-9a-f]{32}", request_id))
                and request_id != "untrusted"
                and health.headers.get("Server-Timing", "").startswith("app;dur="),
                f"status={health.status_code}; request_id_generated={request_id != 'untrusted'}",
            )
        )

        anonymous_metrics = client.get("/metrics")
        checks.append(
            _step(
                2,
                "operator-only metrics",
                anonymous_metrics.status_code == 401
                and client.get("/metrics", headers={"X-API-Key": MEMBER_KEY}).status_code == 403,
                f"anonymous={anonymous_metrics.status_code}; member=403",
            )
        )

        rum = client.post(
            "/telemetry/rum",
            json={
                "metric": "LCP",
                "value": 2600,
                "route": "/courses/customer-specific-slug?email=redacted@example.test",
                "navigation_type": "navigate",
            },
        )
        checks.append(
            _step(
                3,
                "privacy-bounded RUM ingestion",
                rum.status_code == 202
                and rum.json().get("route") == "/courses/:slug"
                and rum.json().get("rating") == "needs_improvement",
                f"status={rum.status_code}; route={rum.json().get('route')}; rating={rum.json().get('rating')}",
            )
        )

        invalid = client.post(
            "/telemetry/rum",
            json={"metric": "CUSTOM", "value": 1, "route": "/", "navigation_type": "navigate"},
        )
        checks.append(
            _step(4, "RUM domain rejection", invalid.status_code == 422, f"status={invalid.status_code}")
        )

        metrics = client.get("/metrics", headers=operator)
        no_private_data = all(
            token not in metrics.text
            for token in ("customer-specific-slug", "redacted@example.test", MEMBER_KEY, OPERATOR_KEY)
        )
        checks.append(
            _step(
                5,
                "Prometheus export without private values",
                metrics.status_code == 200
                and "tpl_http_requests_total" in metrics.text
                and 'metric="LCP",route="/courses/:slug"' in metrics.text
                and no_private_data,
                f"status={metrics.status_code}; private_values_absent={no_private_data}",
            )
        )

    passed = all(checks)
    print(
        f"[VERDICT] {'PASS' if passed else 'FAIL'} · request correlation, operator metrics "
        "and privacy-bounded RUM are CLI reproducible"
    )
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
