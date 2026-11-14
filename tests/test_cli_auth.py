"""Identity protocol fixtures, not a claim of live Supabase/email acceptance."""
from __future__ import annotations

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
from urllib.parse import urlsplit, parse_qs

import pytest

from pricinglibrary_rag.cli_auth import AuthFailure, safe_origin

PASSWORD = "fixture-password-never-print-812"
ACCESS = "fixture-access-private-958"
REFRESH = "fixture-refresh-private-816"


@pytest.fixture
def provider():
    evidence = []
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass
        def handle_request(self):
            route = urlsplit(self.path)
            length = int(self.headers.get("Content-Length", "0"))
            body = json.loads(self.rfile.read(length)) if length else {}
            evidence.append({"path": route.path, "query": parse_qs(route.query), "method": self.command,
                             "body": body, "had_bearer": bool(self.headers.get("Authorization"))})
            status, data = 200, {}
            if body.get("email") == "reject@fixture.test":
                status, data = 400, {"message": PASSWORD + " " + ACCESS + " " + REFRESH}
            elif route.path == "/auth/v1/signup":
                data = {"id": "pending-learner", "email": body["email"]}
            elif route.path == "/auth/v1/token" or route.path == "/auth/v1/verify":
                refreshed = "refresh_token" in body
                data = {"access_token": ACCESS + ("-renewed" if refreshed else ""), "refresh_token": REFRESH,
                        "expires_in": 3600, "user": {"id": "identity-fixture", "email": "learner@fixture.test"}}
            elif route.path == "/auth/v1/user":
                data = {"id": "identity-fixture"}
            elif route.path == "/auth/v1/logout":
                status = 204
            elif route.path == "/__dev/session":
                data = {"session": {"access_token": ACCESS, "refresh_token": "", "expires_in": 3600,
                                    "user": {"id": "dev-fixture", "email": "learner@local.tpl.test"}},
                        "profile": {"email": "learner@local.tpl.test"}}
            elif route.path == "/auth/v1/recover":
                data = {}
            else:
                status = 404
            payload = json.dumps(data).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            if status != 204:
                self.wfile.write(payload)
        do_GET = do_POST = do_PUT = handle_request
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}", evidence
    finally:
        server.shutdown(); server.server_close(); thread.join(timeout=3)


def invoke(provider, tmp_path, action, *options, secret=None):
    origin, _ = provider
    env = {**os.environ, "TPL_SUPABASE_URL": origin,
           "TPL_SUPABASE_ANON_KEY": "sb_publishable_identity_contract_fixture"}
    for key in ("TPL_ACCESS_TOKEN", "TPL_TOKEN_FILE", "TPL_API_URL", "TPL_BASE_URL"):
        env.pop(key, None)
    command = [sys.executable, "-m", "pricinglibrary_rag.learner_cli", "auth", action,
               "--session-file", str(tmp_path / "session.private.json"), *options]
    result = subprocess.run(command, input=secret, text=True, encoding="utf-8", capture_output=True, env=env, timeout=20)
    assert all(value not in result.stdout + result.stderr for value in (PASSWORD, ACCESS, REFRESH))
    return result, json.loads(result.stdout)


def test_real_cli_login_refresh_password_and_logout_protocol(provider, tmp_path):
    result, receipt = invoke(provider, tmp_path, "login", "--email", "learner@fixture.test", "--password-stdin", secret=PASSWORD + "\n")
    assert result.returncode == 0 and receipt["data"]["signed_in"]
    path = tmp_path / "session.private.json"
    assert json.loads(path.read_text())["access_token"] == ACCESS
    assert provider[1][0]["body"]["password"] == PASSWORD
    assert provider[1][0]["query"] == {"grant_type": ["password"]}
    result, receipt = invoke(provider, tmp_path, "refresh")
    assert result.returncode == 0 and receipt["data"]["signed_in"]
    assert json.loads(path.read_text())["access_token"] == ACCESS + "-renewed"
    result, receipt = invoke(provider, tmp_path, "password", "--password-stdin", secret=PASSWORD + "\n")
    assert result.returncode == 0 and receipt["data"]["password_updated"]
    assert provider[1][-1]["had_bearer"] and provider[1][-1]["method"] == "PUT"
    result, receipt = invoke(provider, tmp_path, "logout")
    assert result.returncode == 0 and not path.exists() and receipt["data"]["provider_revocation_verified"]


def test_signup_without_session_requires_confirmation_and_does_not_fake_delivery(provider, tmp_path):
    result, receipt = invoke(provider, tmp_path, "signup", "--email", "learner@fixture.test", "--password-stdin", secret=PASSWORD + "\n")
    assert result.returncode == 0 and receipt["data"]["confirmation_required"]
    assert not receipt["data"]["signed_in"] and not receipt["data"]["delivery_verified"]
    assert not (tmp_path / "session.private.json").exists()
    result, receipt = invoke(provider, tmp_path, "verify", "--email", "learner@fixture.test", "--code-stdin", secret="123456\n")
    assert result.returncode == 0 and receipt["data"]["signed_in"]
    assert provider[1][-1]["body"]["token"] == "123456"
    assert provider[1][-1]["body"]["type"] == "email"


def test_recovery_token_hash_is_read_from_stdin_without_echo(provider, tmp_path):
    result, receipt = invoke(provider, tmp_path, "verify", "--email", "learner@fixture.test", "--kind", "recovery", "--token-hash-stdin", secret="fixture-hash-never-log\n")
    assert result.returncode == 0 and receipt["data"]["signed_in"]
    body = provider[1][-1]["body"]
    assert body["type"] == "recovery" and body["token_hash"] == "fixture-hash-never-log" and "token" not in body
    assert "fixture-hash-never-log" not in result.stdout + result.stderr


def test_recovery_acceptance_is_distinct_from_email_delivery(provider, tmp_path):
    result, receipt = invoke(provider, tmp_path, "recover", "--email", "learner@fixture.test")
    assert result.returncode == 0 and receipt["data"]["request_accepted"]
    assert not receipt["data"]["delivery_verified"] and not (tmp_path / "session.private.json").exists()


def test_provider_error_does_not_echo_secrets_retry_post_or_change_previous_session(provider, tmp_path):
    target = tmp_path / "session.private.json"
    target.write_text(json.dumps({"access_token": "previous-session"}), encoding="utf-8")
    before = target.read_bytes()
    result, _ = invoke(provider, tmp_path, "login", "--email", "reject@fixture.test", "--password-stdin", "--replace", secret=PASSWORD + "\n")
    assert result.returncode == 7 and target.read_bytes() == before
    assert len(provider[1]) == 1


def test_existing_session_not_replaced_before_network_exchange(provider, tmp_path):
    target = tmp_path / "session.private.json"
    target.write_text(json.dumps({"access_token": "previous-session"}), encoding="utf-8")
    result, _ = invoke(provider, tmp_path, "login", "--email", "learner@fixture.test", "--password-stdin", secret=PASSWORD + "\n")
    assert result.returncode == 6 and not provider[1]
    assert json.loads(target.read_text())["access_token"] == "previous-session"


def test_dev_gateway_is_explicit_loopback_and_can_only_clear_locally(provider, tmp_path):
    result, receipt = invoke(provider, tmp_path, "dev-session", "--preview-url", provider[0], "--role", "learner")
    assert result.returncode == 0 and receipt["data"]["development_fixture"]
    assert receipt["data"]["api_url"] == provider[0] + "/__dev/api"
    assert provider[1][-1]["query"] == {"role": ["learner"]}
    result, _ = invoke(provider, tmp_path, "refresh")
    assert result.returncode == 2
    result, receipt = invoke(provider, tmp_path, "logout", "--local-only")
    assert result.returncode == 0 and not receipt["data"]["provider_revocation_verified"]
    assert not (tmp_path / "session.private.json").exists()


@pytest.mark.parametrize("origin", ["http://supabase.com", "https://user:secret@supabase.com", "https://supabase.com/path", "https://supabase.com?q=x", "file:///tmp/config"])
def test_identity_credentials_never_go_to_unsafe_origin(origin):
    with pytest.raises(AuthFailure):
        safe_origin(origin)


def test_remote_dev_session_and_password_argument_are_rejected_without_echo(provider, tmp_path):
    result, _ = invoke(provider, tmp_path, "dev-session", "--preview-url", "https://example.com")
    assert result.returncode == 2 and not provider[1]
    result, _ = invoke(provider, tmp_path, "login", "--email", "learner@fixture.test", "--password", PASSWORD)
    assert result.returncode == 2 and not provider[1]
