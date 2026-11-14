"""Fail closed when high-confidence credential material is committed.

The scanner reports only file and line metadata. It never prints a matched
credential. It is intentionally conservative about placeholders such as
``sk-...`` in documentation, while catching real-looking provider tokens in
source, notebooks, fixtures and generated artifacts.
"""

from __future__ import annotations

import argparse
import base64
import json
import re
import sys
from pathlib import Path


DEFAULT_IGNORED_DIRS = {
    ".git",
    ".pytest_cache",
    "__pycache__",
    "node_modules",
    "dist",
    "build",
    "tmp",
    ".vol-surface-browser-dist",
    ".rum-dist",
    "data",
}
TEXT_SUFFIXES = {
    ".c",
    ".cfg",
    ".css",
    ".env",
    ".html",
    ".ini",
    ".ipynb",
    ".js",
    ".json",
    ".jsx",
    ".md",
    ".mjs",
    ".ps1",
    ".py",
    ".sql",
    ".toml",
    ".ts",
    ".tsx",
    ".txt",
    ".yml",
    ".yaml",
}
MAX_SCAN_BYTES = 25 * 1024 * 1024

# These patterns target high-confidence credentials, not generic UUIDs,
# domains, public Supabase anon keys or documentation placeholders.
SECRET_PATTERNS = (
    ("OpenAI key", re.compile(r"\bsk-(?:proj-|live_|test_)[A-Za-z0-9_-]{20,}\b")),
    ("Stripe secret key", re.compile(r"\bsk_(?:live|test)_[A-Za-z0-9]{16,}\b")),
    (
        "FRED API key",
        re.compile(r"(?im)^\s*FRED_API_KEY\s*=\s*(?!$|[\"']?(?:replace|your|sk-\.\.\.))[^\s#]{20,}"),
    ),
    ("GitHub token", re.compile(r"\bgh[ps]_[A-Za-z0-9]{30,}\b")),
    ("AWS access key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("private key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")),
)
JWT_PATTERN = re.compile(r"\beyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\b")


def iter_text_files(root: Path):
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        relative_parts = path.relative_to(root).parts
        if any(part in DEFAULT_IGNORED_DIRS or part.startswith(".pytest_tmp") for part in relative_parts):
            continue
        if not path.name.startswith(".env") and path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            if path.stat().st_size > MAX_SCAN_BYTES:
                continue
        except OSError:
            continue
        yield path


def scan(root: Path) -> list[dict[str, object]]:
    findings: list[dict[str, object]] = []
    for path in iter_text_files(root):
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except OSError:
            continue
        for line_number, line in enumerate(lines, start=1):
            for label, pattern in SECRET_PATTERNS:
                if pattern.search(line):
                    findings.append(
                        {
                            "file": str(path.relative_to(root)),
                            "line": line_number,
                            "type": label,
                        }
                    )
            for token in JWT_PATTERN.findall(line):
                try:
                    payload = token.split(".", 2)[1]
                    payload += "=" * ((4 - len(payload) % 4) % 4)
                    claims = json.loads(base64.urlsafe_b64decode(payload).decode("utf-8"))
                except (ValueError, UnicodeDecodeError, json.JSONDecodeError):
                    continue
                if claims.get("role") == "service_role":
                    findings.append(
                        {
                            "file": str(path.relative_to(root)),
                            "line": line_number,
                            "type": "Supabase service-role JWT",
                        }
                    )
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[3])
    args = parser.parse_args()
    root = args.root.resolve()
    findings = scan(root)
    if findings:
        print(f"SECRET SCAN FAIL: {len(findings)} high-confidence credential occurrence(s)")
        for finding in findings:
            print(f"- {finding['file']}:{finding['line']} ({finding['type']})")
        print("No credential values were printed. Revoke exposed credentials and replace them with environment variables.")
        return 1
    print(f"SECRET SCAN PASS: no high-confidence credentials found under {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
