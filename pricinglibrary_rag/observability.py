from __future__ import annotations

import math
import re
import threading
import time
from collections import Counter


HTTP_BUCKETS = (0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0)
HTTP_METHODS = {"GET", "HEAD", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "TRACE", "CONNECT"}
RUM_THRESHOLDS = {
    "FCP": (1800.0, 3000.0),
    "LCP": (2500.0, 4000.0),
    "CLS": (0.1, 0.25),
    "TTFB": (800.0, 1800.0),
    "INTERACTION": (200.0, 500.0),
}
NAVIGATION_TYPES = {"navigate", "reload", "back_forward", "prerender", "unknown"}
HTTP_METHODS = {"GET", "HEAD", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"}


def normalize_api_route(route: str | None) -> str:
    value = str(route or "unmatched").strip()
    if not value.startswith("/") or len(value) > 160:
        return "unmatched"
    return value


def normalize_client_route(route: str | None) -> str:
    value = str(route or "/").split("?", 1)[0].split("#", 1)[0].strip()
    if not value.startswith("/") or len(value) > 160:
        return "/other"
    value = re.sub(r"/{2,}", "/", value).rstrip("/") or "/"
    exact = {
        "/", "/pricing", "/starter-kit", "/starter-kit/success",
        "/starter-kit/cancel", "/billing/success", "/billing/cancel",
        "/courses", "/tools", "/account", "/dashboard", "/auth",
    }
    if value in exact:
        return value
    if value.startswith("/courses/"):
        return "/courses/:slug"
    if value.startswith("/tools/"):
        return "/tools/:slug"
    return "/other"


def rum_rating(metric: str, value: float) -> str:
    good, poor = RUM_THRESHOLDS[metric]
    if value <= good:
        return "good"
    if value <= poor:
        return "needs_improvement"
    return "poor"


def validate_rum_measurement(
    *, metric: str, value: float, route: str | None, navigation_type: str | None
) -> tuple[str, float, str, str, str]:
    normalized_metric = str(metric or "").strip().upper()
    if normalized_metric not in RUM_THRESHOLDS:
        raise ValueError("unsupported RUM metric")
    numeric_value = float(value)
    maximum = 10.0 if normalized_metric == "CLS" else 120_000.0
    if not math.isfinite(numeric_value) or numeric_value < 0 or numeric_value > maximum:
        raise ValueError("RUM value is outside the accepted domain")
    normalized_navigation = str(navigation_type or "unknown").strip().lower()
    if normalized_navigation not in NAVIGATION_TYPES:
        normalized_navigation = "unknown"
    normalized_route = normalize_client_route(route)
    return (
        normalized_metric,
        numeric_value,
        normalized_route,
        normalized_navigation,
        rum_rating(normalized_metric, numeric_value),
    )


def _escape_label(value: object) -> str:
    return str(value).replace("\\", "\\\\").replace("\n", "\\n").replace('"', '\\"')


def _labels(**values: object) -> str:
    return "{" + ",".join(f'{key}="{_escape_label(value)}"' for key, value in values.items()) + "}"


class ProductionMetrics:
    """Bounded-cardinality, dependency-free Prometheus metrics registry."""

    def __init__(self) -> None:
        self.started_at = time.monotonic()
        self._lock = threading.Lock()
        self._requests: Counter[tuple[str, str, str]] = Counter()
        self._duration_count: Counter[tuple[str, str]] = Counter()
        self._duration_sum: Counter[tuple[str, str]] = Counter()
        self._duration_buckets: Counter[tuple[str, str, str]] = Counter()
        self._rum_count: Counter[tuple[str, str, str, str]] = Counter()
        self._rum_sum: Counter[tuple[str, str, str, str]] = Counter()

    def record_request(self, *, method: str, route: str, status: int, duration_seconds: float) -> None:
        method_candidate = str(method or "").upper()
        normalized_method = method_candidate if method_candidate in HTTP_METHODS else "OTHER"
        if normalized_method not in HTTP_METHODS:
            normalized_method = "OTHER"
        normalized_route = normalize_api_route(route)
        status_text = str(int(status))
        duration = max(0.0, float(duration_seconds))
        with self._lock:
            self._requests[(normalized_method, normalized_route, status_text)] += 1
            key = (normalized_method, normalized_route)
            self._duration_count[key] += 1
            self._duration_sum[key] += duration
            for bucket in HTTP_BUCKETS:
                if duration <= bucket:
                    self._duration_buckets[(normalized_method, normalized_route, str(bucket))] += 1
            self._duration_buckets[(normalized_method, normalized_route, "+Inf")] += 1

    def record_rum(
        self, *, metric: str, value: float, route: str | None, navigation_type: str | None
    ) -> dict[str, object]:
        metric, value, route, navigation, rating = validate_rum_measurement(
            metric=metric, value=value, route=route, navigation_type=navigation_type
        )
        key = (metric, route, navigation, rating)
        with self._lock:
            self._rum_count[key] += 1
            self._rum_sum[key] += value
        return {"metric": metric, "route": route, "navigation_type": navigation, "rating": rating}

    def render_prometheus(self) -> str:
        with self._lock:
            requests = self._requests.copy()
            duration_count = self._duration_count.copy()
            duration_sum = self._duration_sum.copy()
            duration_buckets = self._duration_buckets.copy()
            rum_count = self._rum_count.copy()
            rum_sum = self._rum_sum.copy()
        lines = [
            "# HELP tpl_process_uptime_seconds Seconds since the API metrics registry started.",
            "# TYPE tpl_process_uptime_seconds gauge",
            f"tpl_process_uptime_seconds {max(0.0, time.monotonic() - self.started_at):.6f}",
            "# HELP tpl_http_requests_total HTTP responses by method, route template and status.",
            "# TYPE tpl_http_requests_total counter",
        ]
        for (method, route, status), count in sorted(requests.items()):
            lines.append(f"tpl_http_requests_total{_labels(method=method, route=route, status=status)} {count}")
        lines.extend(
            [
                "# HELP tpl_http_request_duration_seconds HTTP request latency by route template.",
                "# TYPE tpl_http_request_duration_seconds histogram",
            ]
        )
        for (method, route, boundary), count in sorted(duration_buckets.items()):
            lines.append(
                f"tpl_http_request_duration_seconds_bucket"
                f"{_labels(method=method, route=route, le=boundary)} {count}"
            )
        for (method, route), count in sorted(duration_count.items()):
            label = _labels(method=method, route=route)
            lines.append(f"tpl_http_request_duration_seconds_count{label} {count}")
            lines.append(f"tpl_http_request_duration_seconds_sum{label} {duration_sum[(method, route)]:.9f}")
        lines.extend(
            [
                "# HELP tpl_rum_measurements_total Accepted privacy-bounded browser measurements.",
                "# TYPE tpl_rum_measurements_total counter",
                "# HELP tpl_rum_value_sum Sum of accepted browser measurement values.",
                "# TYPE tpl_rum_value_sum counter",
            ]
        )
        for (metric, route, navigation, rating), count in sorted(rum_count.items()):
            label = _labels(metric=metric, route=route, navigation=navigation, rating=rating)
            lines.append(f"tpl_rum_measurements_total{label} {count}")
            lines.append(f"tpl_rum_value_sum{label} {rum_sum[(metric, route, navigation, rating)]:.9f}")
        return "\n".join(lines) + "\n"
