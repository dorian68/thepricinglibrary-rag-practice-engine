import hashlib
import importlib.util
import json
import sys
from pathlib import Path

_SCRIPT = Path(__file__).parents[1] / "scripts" / "smoke_deployed_acceptance.py"
_SPEC = importlib.util.spec_from_file_location("smoke_deployed_acceptance", _SCRIPT)
acceptance = importlib.util.module_from_spec(_SPEC)
assert _SPEC.loader is not None
sys.modules[_SPEC.name] = acceptance
_SPEC.loader.exec_module(acceptance)


def test_anonymous_deployed_acceptance_is_fail_closed(monkeypatch, capsys):
    def fake_request(_base, method, path, _token=None):
        if path == "/health" or path == "/ready":
            return acceptance.Response(200, {"x-request-id": "test"}, b"{}")
        if path.endswith("/availability"):
            return acceptance.Response(200, {}, b'{"sale_ready":true,"version":"1.0.0"}')
        if path == "/metrics" or path.endswith("/manifest") or path.endswith("/download"):
            return acceptance.Response(401, {}, b"{}");
        if method == "POST" and path.endswith("/checkout"):
            return acceptance.Response(401, {}, b"{}")
        raise AssertionError(path)

    monkeypatch.setattr(acceptance, "http_request", fake_request)
    monkeypatch.delenv("TPL_STAGING_ACCESS_TOKEN", raising=False)
    monkeypatch.setattr(sys, "argv", ["smoke_deployed_acceptance.py", "--base-url", "https://staging.example"])
    assert acceptance.main() == 0
    assert '"verdict": "PASS"' in capsys.readouterr().out


def test_entitled_download_matches_manifest(monkeypatch, capsys):
    payload = b"verified starter kit"
    manifest = {
        "ready": True,
        "version": "1.0.0",
        "deliverables": [{"path": str(index)} for index in range(7)],
        "bundle": {"sha256": hashlib.sha256(payload).hexdigest(), "size_bytes": len(payload)},
    }

    def fake_request(_base, method, path, token=None):
        assert token in {None, "staging-token"}
        if path == "/health" or path == "/ready":
            return acceptance.Response(200, {}, b"{}")
        if path.endswith("/availability"):
            return acceptance.Response(200, {}, b'{"sale_ready":true,"version":"1.0.0"}')
        if path == "/metrics" or (path.endswith("/manifest") or path.endswith("/download")) and not token:
            return acceptance.Response(401, {}, b"{}")
        if method == "POST" and path.endswith("/checkout"):
            return acceptance.Response(401, {}, b"{}")
        if path == "/billing/entitlement":
            return acceptance.Response(200, {}, b'{"active":true,"plan":"starter"}')
        if path.endswith("/manifest"):
            return acceptance.Response(200, {"x-request-id": "test"}, json.dumps(manifest).encode())
        if path.endswith("/download"):
            return acceptance.Response(200, {"cache-control": "private, no-store"}, payload)
        raise AssertionError(path)

    monkeypatch.setattr(acceptance, "http_request", fake_request)
    monkeypatch.setenv("TPL_STAGING_ACCESS_TOKEN", "staging-token")
    monkeypatch.setattr(
        sys,
        "argv",
        ["smoke_deployed_acceptance.py", "--base-url", "https://staging.example", "--require-entitled"],
    )
    assert acceptance.main() == 0
    assert '"download-checksum-and-size"' in capsys.readouterr().out


def test_entitled_download_accepts_canonical_manifest_size(monkeypatch, capsys):
    payload = b"canonical-size-bundle"
    manifest = {
        "ready": True,
        "version": "1.0.0",
        "deliverables": [{"path": str(index)} for index in range(7)],
        "bundle": {"sha256": hashlib.sha256(payload).hexdigest(), "size": len(payload)},
    }

    def fake_request(_base, method, path, token=None):
        if path in {"/health", "/ready"}:
            return acceptance.Response(200, {}, b"{}")
        if path.endswith("/availability"):
            return acceptance.Response(200, {}, b'{"sale_ready":true,"version":"1.0.0"}')
        if path == "/metrics" or (path.endswith(("/manifest", "/download")) and not token):
            return acceptance.Response(401, {}, b"{}")
        if method == "POST" and path.endswith("/checkout"):
            return acceptance.Response(401, {}, b"{}")
        if path == "/billing/entitlement":
            return acceptance.Response(200, {}, b'{"active":true}')
        if path.endswith("/manifest"):
            return acceptance.Response(200, {}, json.dumps(manifest).encode())
        if path.endswith("/download"):
            return acceptance.Response(200, {"cache-control": "private, no-store"}, payload)
        raise AssertionError(path)

    monkeypatch.setattr(acceptance, "http_request", fake_request)
    monkeypatch.setenv("TPL_STAGING_ACCESS_TOKEN", "staging-token")
    monkeypatch.setattr(
        sys,
        "argv",
        ["smoke_deployed_acceptance.py", "--base-url", "https://staging.example", "--require-entitled"],
    )
    assert acceptance.main() == 0
    assert '"sha256_match": true' in capsys.readouterr().out
