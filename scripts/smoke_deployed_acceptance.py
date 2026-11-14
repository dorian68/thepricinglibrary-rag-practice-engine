"""Run the public and entitled Starter Kit acceptance checks against a deployment.

The script is deliberately credential-light: it reads an optional bearer token
from ``TPL_STAGING_ACCESS_TOKEN`` and never prints it. Without a token it still
proves health, readiness, public availability and anonymous denial. With a
token it verifies entitlement, manifest integrity and the private ZIP checksum.
It does not create a Stripe purchase; purchase/refund remains an explicit
staging operator step described in ``docs/DEPLOY_PLAN.md``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from time import monotonic
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


PRODUCT_PREFIX = "/products/market-finance-starter-kit"


@dataclass
class Response:
    status: int
    headers: dict[str, str]
    body: bytes
    error: str | None = None


def http_request(base_url: str, method: str, path: str, token: str | None = None) -> Response:
    headers = {"Accept": "application/json, application/octet-stream"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = Request(f"{base_url.rstrip('/')}{path}", method=method, headers=headers)
    try:
        with urlopen(request, timeout=20) as response:
            return Response(response.status, dict(response.headers.items()), response.read())
    except HTTPError as exc:
        return Response(exc.code, dict(exc.headers.items()), exc.read(), str(exc.reason))
    except (URLError, TimeoutError, OSError) as exc:
        return Response(0, {}, b"", str(exc))


def json_body(response: Response) -> dict:
    try:
        value = json.loads(response.body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", required=True, help="deployed HTTPS API origin")
    parser.add_argument("--json-out", type=Path)
    parser.add_argument(
        "--allow-http-local",
        action="store_true",
        help="allow http://127.0.0.1 or localhost for a local probe",
    )
    parser.add_argument(
        "--require-entitled",
        action="store_true",
        help="fail unless TPL_STAGING_ACCESS_TOKEN proves a real entitled download",
    )
    args = parser.parse_args()
    parsed = urlparse(args.base_url)
    if parsed.scheme not in {"https", "http"} or parsed.username or parsed.password or not parsed.netloc:
        print("DEPLOYED ACCEPTANCE FAIL: base URL must be an origin without credentials")
        return 1
    if parsed.scheme != "https" and not (
        args.allow_http_local and parsed.hostname in {"localhost", "127.0.0.1", "::1"}
    ):
        print("DEPLOYED ACCEPTANCE FAIL: HTTPS is required outside an explicit local probe")
        return 1

    token = os.environ.get("TPL_STAGING_ACCESS_TOKEN", "").strip() or None
    checks: list[dict[str, object]] = []
    manifest: dict = {}

    def check(name: str, method: str, path: str, expected: set[int], auth: str | None = None) -> Response:
        started = monotonic()
        response = http_request(args.base_url, method, path, auth)
        checks.append(
            {
                "name": name,
                "method": method,
                "path": path,
                "expected_status": sorted(expected),
                "actual_status": response.status,
                "pass": response.status in expected,
                "duration_ms": round((monotonic() - started) * 1000, 2),
                "request_id_present": bool(response.headers.get("x-request-id")),
            }
        )
        return response

    health = check("health", "GET", "/health", {200})
    ready = check("readiness", "GET", "/ready", {200})
    availability = check("starter-kit-availability", "GET", f"{PRODUCT_PREFIX}/availability", {200})
    availability_payload = json_body(availability)
    checks.append(
        {
            "name": "availability-sale-ready",
            "pass": availability_payload.get("sale_ready") is True
            and bool(availability_payload.get("version")),
            "sale_ready": availability_payload.get("sale_ready"),
            "version_present": bool(availability_payload.get("version")),
        }
    )
    check("anonymous-manifest-denied", "GET", f"{PRODUCT_PREFIX}/manifest", {401, 403})
    check("anonymous-download-denied", "GET", f"{PRODUCT_PREFIX}/download", {401, 403})
    check("anonymous-checkout-denied", "POST", f"{PRODUCT_PREFIX}/checkout", {401, 403})
    check("anonymous-metrics-denied", "GET", "/metrics", {401, 403})

    if token:
        entitlement = check("entitled-session", "GET", "/billing/entitlement", {200}, token)
        manifest_response = check("entitled-manifest", "GET", f"{PRODUCT_PREFIX}/manifest", {200}, token)
        if manifest_response.status == 200:
            manifest = json_body(manifest_response)
            bundle = manifest.get("bundle", {}) if isinstance(manifest, dict) else {}
            checks.append(
                {
                    "name": "manifest-ready-seven-deliverables",
                    "pass": manifest.get("ready") is True
                    and len(manifest.get("deliverables", [])) == 7
                    and bool(bundle.get("sha256")),
                    "ready": manifest.get("ready"),
                    "deliverable_count": len(manifest.get("deliverables", [])),
                }
            )
            download = check("entitled-download", "GET", f"{PRODUCT_PREFIX}/download", {200}, token)
            if download.status == 200:
                digest = hashlib.sha256(download.body).hexdigest()
                expected_digest = bundle.get("sha256")
                # The release manifest uses the canonical ``size`` field;
                # ``size_bytes`` remains accepted for older test fixtures.
                expected_size = bundle.get("size")
                if expected_size is None:
                    expected_size = bundle.get("size_bytes")
                checks.append(
                    {
                        "name": "download-checksum-and-size",
                        "pass": digest == expected_digest and len(download.body) == expected_size,
                        "sha256_match": digest == expected_digest,
                        "size_match": len(download.body) == expected_size,
                        "cache_control_private": "private" in download.headers.get("cache-control", "").lower(),
                    }
                )
        else:
            # Keep the response body private; only the status is useful for the report.
            _ = entitlement
    elif args.require_entitled:
        checks.append({"name": "entitled-session", "pass": False, "reason": "TPL_STAGING_ACCESS_TOKEN is absent"})
    else:
        checks.append({"name": "entitled-session", "pass": None, "skipped": True, "reason": "token not provided"})

    failed = [item for item in checks if item.get("pass") is False]
    skipped = [item for item in checks if item.get("skipped")]
    report = {
        "base_origin": f"{parsed.scheme}://{parsed.netloc}",
        "token_supplied": bool(token),
        "checks": checks,
        "failed_checks": len(failed),
        "skipped_checks": len(skipped),
        "verdict": "PASS" if not failed else "FAIL",
        "purchase_refund_manual_gate": "REQUIRED",
    }
    encoded = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(encoded, encoding="utf-8")
    print(encoded, end="")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
