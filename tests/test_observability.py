from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import re

from fastapi.testclient import TestClient

from pricinglibrary_rag.api import create_app
from pricinglibrary_rag.config import Settings
from pricinglibrary_rag.factory import build_services
from pricinglibrary_rag.observability import (
    ProductionMetrics,
    normalize_client_route,
    rum_rating,
    validate_rum_measurement,
)
from pricinglibrary_rag.security import ApiSecurity


MEMBER_KEY = "member_" + "m" * 40
OPERATOR_KEY = "operator_" + "o" * 40
AUTH_SECRET = "identity_" + "s" * 40


def _settings(tmp_path: Path, **overrides) -> Settings:
    base = Settings(
        data_dir=tmp_path,
        db_path=tmp_path / "observability.sqlite3",
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
        auth_token_secret=AUTH_SECRET,
        rate_limit_per_min=100,
    )
    return replace(base, **overrides)


def test_rum_contract_bounds_cardinality_and_computes_rating() -> None:
    assert normalize_client_route("/courses/black-scholes?email=private@example.test") == "/courses/:slug"
    assert normalize_client_route("/unexpected/customer/123") == "/other"
    assert rum_rating("LCP", 2500) == "good"
    assert rum_rating("LCP", 2501) == "needs_improvement"
    assert rum_rating("LCP", 4001) == "poor"
    assert validate_rum_measurement(
        metric="cls", value=0.12, route="/starter-kit", navigation_type="reload"
    ) == ("CLS", 0.12, "/starter-kit", "reload", "needs_improvement")


def test_rum_contract_rejects_invalid_metric_and_value() -> None:
    for metric, value in (("EMAIL", 1), ("LCP", -1), ("LCP", 120_001), ("CLS", 11)):
        try:
            validate_rum_measurement(
                metric=metric, value=value, route="/", navigation_type="navigate"
            )
        except ValueError:
            pass
        else:
            raise AssertionError(f"invalid RUM measurement accepted: {metric}={value}")


def test_metrics_registry_uses_route_templates_and_prometheus_histograms() -> None:
    metrics = ProductionMetrics()
    metrics.record_request(method="get", route="/documents/{document_id}", status=200, duration_seconds=0.02)
    metrics.record_request(method="attacker-cardinality", route="x" * 200, status=418, duration_seconds=0.01)
    metrics.record_rum(metric="LCP", value=2600, route="/courses/private-course", navigation_type="navigate")
    output = metrics.render_prometheus()
    assert 'route="/documents/{document_id}"' in output
    assert 'method="OTHER",route="unmatched",status="418"' in output
    assert "attacker-cardinality" not in output
    assert 'le="0.025"' in output
    assert 'metric="LCP",route="/courses/:slug",navigation="navigate",rating="needs_improvement"' in output
    assert "private-course" not in output


def test_metrics_registry_collapses_unexpected_http_methods() -> None:
    metrics = ProductionMetrics()
    for index in range(100):
        metrics.record_request(
            method=f"X-CARDINALITY-{index}",
            route="unmatched",
            status=401,
            duration_seconds=0.001,
        )
    output = metrics.render_prometheus()
    assert 'method="OTHER"' in output
    assert "X-CARDINALITY" not in output


def test_api_request_ids_rum_and_operator_metrics_are_fail_closed(tmp_path: Path) -> None:
    client = TestClient(create_app(build_services(_settings(tmp_path))))
    member = {"X-API-Key": MEMBER_KEY}
    operator = {"X-API-Key": OPERATOR_KEY}

    health = client.get("/health", headers={"X-Request-ID": "attacker-controlled"})
    assert health.status_code == 200
    assert re.fullmatch(r"[0-9a-f]{32}", health.headers["X-Request-ID"])
    assert health.headers["X-Request-ID"] != "attacker-controlled"
    assert health.headers["Server-Timing"].startswith("app;dur=")

    assert client.get("/metrics").status_code == 401
    assert client.get("/metrics", headers=member).status_code == 403

    accepted = client.post(
        "/telemetry/rum",
        json={
            "metric": "LCP",
            "value": 2600,
            "route": "/courses/never-store-this-slug?email=private@example.test",
            "navigation_type": "navigate",
        },
    )
    assert accepted.status_code == 202
    assert accepted.json() == {
        "accepted": True,
        "metric": "LCP",
        "route": "/courses/:slug",
        "navigation_type": "navigate",
        "rating": "needs_improvement",
    }
    assert client.post(
        "/telemetry/rum",
        json={"metric": "CUSTOM", "value": 1, "route": "/", "navigation_type": "navigate"},
    ).status_code == 422
    assert client.post(
        "/telemetry/rum",
        json={
            "metric": "FCP",
            "value": 900,
            "route": "/",
            "navigation_type": "navigate",
            "email": "must-not-be-accepted@example.test",
        },
    ).status_code == 422
    assert client.post(
        "/telemetry/rum",
        json={"metric": "FCP", "value": 900, "route": "/" + "x" * 200},
    ).status_code == 422

    response = client.get("/metrics", headers=operator)
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/plain")
    assert "tpl_http_requests_total" in response.text
    assert 'metric="LCP",route="/courses/:slug"' in response.text
    assert "never-store-this-slug" not in response.text
    assert "private@example.test" not in response.text


def test_observability_security_policy_is_explicit() -> None:
    assert ApiSecurity.access_for("GET", "/metrics") == "operator"
    assert ApiSecurity.access_for("POST", "/telemetry/rum") == "public_rate_limited"
