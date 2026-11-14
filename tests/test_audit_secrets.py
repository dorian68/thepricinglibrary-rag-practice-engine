import base64
import importlib.util
import json
from pathlib import Path


_SCRIPT = Path(__file__).parents[1] / "scripts" / "audit_secrets.py"
_SPEC = importlib.util.spec_from_file_location("audit_secrets", _SCRIPT)
audit_secrets = importlib.util.module_from_spec(_SPEC)
assert _SPEC.loader is not None
_SPEC.loader.exec_module(audit_secrets)


def _jwt(role: str) -> str:
    encode = lambda value: base64.urlsafe_b64encode(value).decode().rstrip("=")
    return ".".join(
        [
            encode(b'{"alg":"HS256","typ":"JWT"}'),
            encode(json.dumps({"role": role}).encode()),
            encode(b"signature-material-long-enough-for-test"),
        ]
    )


def test_scanner_allows_public_anon_jwt_but_flags_service_role(tmp_path):
    (tmp_path / "safe.txt").write_text(_jwt("anon"), encoding="utf-8")
    assert audit_secrets.scan(tmp_path) == []

    (tmp_path / "private.txt").write_text(_jwt("service_role"), encoding="utf-8")
    findings = audit_secrets.scan(tmp_path)
    assert [finding["type"] for finding in findings] == ["Supabase service-role JWT"]


def test_scanner_flags_provider_secret_without_printing_value(tmp_path):
    (tmp_path / ".env").write_text(
        "sk-proj-" + "A" * 32 + "\nsk_live_" + "B" * 32,
        encoding="utf-8",
    )
    findings = audit_secrets.scan(tmp_path)
    assert {finding["type"] for finding in findings} == {"OpenAI key", "Stripe secret key"}


def test_scanner_flags_named_fred_key(tmp_path):
    (tmp_path / ".env").write_text("FRED_API_KEY=" + "F" * 32, encoding="utf-8")
    findings = audit_secrets.scan(tmp_path)
    assert [finding["type"] for finding in findings] == ["FRED API key"]
