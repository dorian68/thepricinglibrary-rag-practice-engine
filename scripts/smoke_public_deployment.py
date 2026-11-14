"""Read-only trust/freshness probe for a deployed ThePricingLibrary frontend.

This is an external deployment check, not a substitute for staging purchase,
rollback, legal or pilot evidence. It fetches the public HTML and same-origin
JavaScript assets, reports only status/marker names, and never writes evidence
or prints response bodies.
"""

from __future__ import annotations

import argparse
import re
import sys
from html import unescape
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen


FORBIDDEN_MARKERS = (
    "TRADING TERMINAL ACTIVATED",
    "What Our Users Say",
    "Curriculum designed in partnership with quantitative analysts from top investment banks",
    "Monthly live workshops",
    "Course completion certificates",
    "1-on-1 expert sessions",
    "Join thousands of professionals",
    "LinkedIn Integration",
    "Performance Reports",
    "Live Market Snapshot",
    "real backtests",
    "live market context",
)


def fetch(url: str, timeout: float) -> tuple[int, str, str]:
    request = Request(url, headers={"User-Agent": "ThePricingLibrary-release-probe/1.0"})
    with urlopen(request, timeout=timeout) as response:  # noqa: S310 - operator-supplied HTTPS URL
        body = response.read(8 * 1024 * 1024 + 1)
        if len(body) > 8 * 1024 * 1024:
            raise RuntimeError(f"response too large: {url}")
        return int(response.status), response.headers.get_content_type(), body.decode("utf-8", errors="replace")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="https://thepricinglibrary.com", help="public frontend origin")
    parser.add_argument("--timeout", type=float, default=20.0)
    args = parser.parse_args()

    parsed = urlparse(args.url)
    if parsed.scheme not in {"https", "http"} or not parsed.netloc:
        print("PUBLIC DEPLOYMENT PROBE FAIL: URL must be an absolute HTTP(S) origin")
        return 1

    origin = f"{parsed.scheme}://{parsed.netloc}"
    try:
        status, content_type, html = fetch(args.url, args.timeout)
        if status != 200 or "html" not in content_type:
            print(f"PUBLIC DEPLOYMENT PROBE FAIL: root status={status} content_type={content_type}")
            return 1

        scripts = []
        for match in re.finditer(r"<(?:script|link)[^>]+(?:src|href)=['\"]([^'\"]+\.(?:js|mjs)(?:\?[^'\"]*)?)['\"]", html, re.I):
            asset = unescape(match.group(1))
            script_url = urljoin(args.url, asset)
            if urlparse(script_url).netloc == parsed.netloc:
                scripts.append(script_url)
        scripts = list(dict.fromkeys(scripts))
        if not scripts:
            print("PUBLIC DEPLOYMENT PROBE FAIL: no same-origin JavaScript asset found")
            return 1

        markers = set()
        for script_url in scripts:
            script_status, _, script = fetch(script_url, args.timeout)
            if script_status != 200:
                print(f"PUBLIC DEPLOYMENT PROBE FAIL: asset status={script_status} asset={script_url}")
                return 1
            markers.update(marker for marker in FORBIDDEN_MARKERS if marker in script)

        if markers:
            print(f"PUBLIC DEPLOYMENT PROBE FAIL: stale/unsupported markers={sorted(markers)} assets={len(scripts)}")
            return 1

        print(f"PUBLIC DEPLOYMENT PROBE PASS: root=200 assets={len(scripts)} trust markers=0 origin={origin}")
        return 0
    except Exception as exc:  # pragma: no cover - network failure is environment-dependent
        print(f"PUBLIC DEPLOYMENT PROBE ERROR: {type(exc).__name__}: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
