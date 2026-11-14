"""Explicit CLI identity flows. Passwords/codes are never command arguments.

Provider exchanges are HTTPS (HTTP only for loopback test providers), without
redirects or automatic POST retries. Dev sessions require an explicit command
and the existing loopback-only Vite development gateway, never token minting.
"""
from __future__ import annotations

import getpass
import csv
import io
import json
import os
from pathlib import Path
import re
import socket
import subprocess
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit, urlencode
from urllib.request import Request, HTTPRedirectHandler, build_opener
import uuid


class AuthFailure(Exception):
    def __init__(self, message, exit_code=2, status=None):
        self.message, self.exit_code, self.status = message, exit_code, status
        super().__init__(message)


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *_args, **_kwargs):
        return None


def default_session_file():
    return Path.home() / ".thepricinglibrary" / "session.private.json"


def session_path(args=None):
    return Path(getattr(args, "session_file", None) or getattr(args, "token_file", None)
                or os.environ.get("TPL_TOKEN_FILE") or default_session_file()).expanduser()


def read_session(path):
    try:
        if path.stat().st_size > 65536:
            raise ValueError()
        value = json.loads(path.read_text(encoding="utf-8-sig"))
        if not isinstance(value, dict) or not isinstance(value.get("access_token"), str):
            raise ValueError()
        return value
    except (OSError, ValueError, TypeError):
        raise AuthFailure("A readable private JSON session file is required; no credential was printed.") from None


def stored_api_url(path=None):
    path = Path(path or os.environ.get("TPL_TOKEN_FILE") or default_session_file())
    if not path.is_file():
        return None
    try:
        return read_session(path).get("api_url")
    except AuthFailure:
        return None  # A plain token file is still valid for the main CLI client.


def safe_origin(value, *, loopback_only=False):
    try:
        parsed = urlsplit(value)
        local = parsed.hostname in {"localhost", "127.0.0.1", "::1"}
        if (not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment
                or parsed.path not in {"", "/"} or parsed.scheme not in {"https", "http"}
                or (parsed.scheme == "http" and not local) or (loopback_only and not local)):
            raise ValueError()
        parsed.port  # Also validate malformed/overflowing ports.
        return value.rstrip("/")
    except (TypeError, ValueError):
        raise AuthFailure("Identity URL must be an HTTPS origin, or a loopback HTTP test origin, without credentials/path/query.") from None


def _public_key(args):
    try:
        value = (Path(args.public_key_file).read_text(encoding="utf-8-sig").strip()
                 if args.public_key_file else os.environ.get("TPL_SUPABASE_ANON_KEY", "").strip())
        if not value or len(value) > 16384 or re.search(r"\s", value) or value.startswith("sb_secret_"):
            raise ValueError()
        if value.count(".") == 2:
            import base64
            payload = value.split(".")[1]
            claims = json.loads(base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4)))
            if claims.get("role") != "anon":
                raise ValueError()
        elif not value.startswith("sb_publishable_"):
            raise ValueError()
        return value
    except (OSError, ValueError, TypeError, AttributeError):
        raise AuthFailure("Supply the provider's public anon/publishable key via TPL_SUPABASE_ANON_KEY or --public-key-file; service-role/secret keys are refused.") from None


def _secret(args, name="password"):
    from_stdin = (args.code_stdin or args.token_hash_stdin) if name == "code" else args.password_stdin
    try:
        if from_stdin:
            value = sys.stdin.readline(4098).rstrip("\r\n")
        elif sys.stdin.isatty():
            value = getpass.getpass("Verification code: " if name == "code" else "Password: ")
        else:
            raise AuthFailure("Use a terminal prompt or the explicit --password-stdin/--code-stdin option; never pass secrets as arguments.")
        if not value or len(value) > 4096 or any(ord(c) < 32 for c in value):
            raise AuthFailure("The secret input is empty or invalid; its value was not printed.")
        return value
    except (EOFError, KeyboardInterrupt):
        raise AuthFailure("Identity input was cancelled; no session was changed.") from None


def _http(origin, route, *, body=None, token=None, public_key=None, timeout=30, method="POST", query=None):
    headers = {"Accept": "application/json", "User-Agent": "ThePricingLibrary-CLI/1"}
    if public_key:
        headers["apikey"] = public_key
    if token:
        headers["Authorization"] = "Bearer " + token
    data = None
    if body is not None:
        data = json.dumps(body, allow_nan=False).encode("utf-8")
        headers["Content-Type"] = "application/json"
    url = origin + route + ("?" + urlencode(query) if query else "")
    try:
        with build_opener(NoRedirect()).open(Request(url, data=data, headers=headers, method=method), timeout=timeout) as response:
            raw = response.read(131073)
            if len(raw) > 131072:
                raise AuthFailure("Identity response exceeds its size budget.", 8)
            if not raw:
                return {}
            value = json.loads(raw)
            if not isinstance(value, dict):
                raise ValueError()
            return value
    except HTTPError as exc:
        # Never echo a provider body: even an erroneous/malicious response must
        # not reflect a password, refresh token, public key or verification code.
        status = exc.code
        exc.close()
        raise AuthFailure(f"Identity request was rejected (HTTP {status}); no credential value was printed.",
                          {401: 3, 403: 4, 409: 6, 429: 8}.get(status, 8 if status >= 500 else 7), status) from None
    except (URLError, socket.timeout, TimeoutError, ConnectionError):
        raise AuthFailure("Identity service is unreachable; no session was changed.", 8) from None
    except (ValueError, UnicodeError):
        raise AuthFailure("Identity service returned an invalid response; no session was changed.", 8) from None


def _store(path, value, *, replace=False):
    if path.is_symlink() or (path.exists() and not replace):
        raise AuthFailure("Session file already exists or is a symlink; use --replace for an intentional session replacement.", 6)
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    temporary = path.with_name(path.name + "." + uuid.uuid4().hex + ".tmp")
    try:
        descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as file:
            json.dump(value, file, ensure_ascii=False, indent=2, allow_nan=False)
            file.write("\n")
        if os.name == "nt":
            # chmod(0600) does not restrict a Windows DACL. Use the current
            # security identifier, with argument arrays and no visible console.
            options = {"capture_output": True, "text": True, "timeout": 10,
                       "creationflags": subprocess.CREATE_NO_WINDOW}
            who = subprocess.run(["whoami", "/user", "/fo", "csv", "/nh"], **options)
            row = next(csv.reader(io.StringIO(who.stdout)), [])
            sid = row[1] if len(row) > 1 else ""
            if who.returncode or not re.fullmatch(r"S-1-[0-9-]+", sid):
                raise OSError("Current account SID unavailable.")
            acl = subprocess.run(["icacls", str(temporary), "/inheritance:r", "/grant:r", "*" + sid + ":(F)"], **options)
            if acl.returncode:
                raise OSError("Private session DACL could not be applied.")
        if replace:
            os.replace(temporary, path)
        else:
            # Hard-link creation is exclusive, preventing an intervening writer
            # from being silently overwritten by a first login.
            os.link(temporary, path)
            temporary.unlink()
    except (OSError, subprocess.SubprocessError):
        temporary.unlink(missing_ok=True)
        raise AuthFailure("The private session file could not be written; no token value was printed.", 8) from None


def _save_response(response, args, origin, *, api_url=None, replace=False, development=False):
    session = response.get("session", response)
    if not isinstance(session, dict) or not session.get("access_token"):
        pending_user = response.get("user") or response
        if args.action != "signup" or not isinstance(pending_user, dict) or not pending_user.get("id"):
            raise AuthFailure("The identity provider has not issued the required session contract.", 8)
        return {"signed_in": False, "confirmation_required": True, "delivery_verified": False,
                "notice": "The identity provider has accepted signup without issuing a session. Complete email confirmation before signing in."}
    token = session.get("access_token")
    refresh = session.get("refresh_token", "")
    if not isinstance(token, str) or not token or len(token) > 16384 or re.search(r"\s", token) or not isinstance(refresh, str):
        raise AuthFailure("The provider did not return a valid session contract.", 8)
    user = session.get("user") or response.get("user") or {}
    value = {"access_token": token, "refresh_token": refresh, "auth_url": origin,
             "expires_at": session.get("expires_at") or int(time.time()) + int(session.get("expires_in", 3600)),
             "user": {"id": user.get("id"), "email": user.get("email")},
             "development_fixture": development}
    if api_url:
        value["api_url"] = api_url
    path = session_path(args)
    _store(path, value, replace=replace)
    return {"signed_in": True, "session_file": str(path.resolve()), "expires_at": value["expires_at"],
            "user": value["user"], "development_fixture": development,
            "api_url": api_url, "notice": "Session saved privately. Paid access remains a server-side decision."}


def add_parsers(leaf):
    for action in ("login", "signup", "recover", "verify", "refresh", "logout", "password"):
        parser = leaf("auth", action)
        parser.add_argument("--auth-url", default=os.environ.get("TPL_SUPABASE_URL"))
        parser.add_argument("--public-key-file")
        parser.add_argument("--session-file")
        if action in {"login", "signup", "recover", "verify"}:
            parser.add_argument("--email", required=True)
        if action in {"login", "signup", "password"}:
            parser.add_argument("--password-stdin", action="store_true")
        if action in {"login", "signup", "verify"}:
            parser.add_argument("--replace", action="store_true")
        if action == "verify":
            parser.add_argument("--kind", choices=("email", "signup", "recovery"), default="email",
                                help="email verifies signup; signup is retained as a compatibility alias.")
            codes = parser.add_mutually_exclusive_group()
            codes.add_argument("--code-stdin", action="store_true")
            codes.add_argument("--token-hash-stdin", action="store_true", help="Read the provider email-link hash via stdin.")
        if action == "logout":
            parser.add_argument("--local-only", action="store_true")
    parser = leaf("auth", "dev-session")
    parser.add_argument("--preview-url", default="http://127.0.0.1:5173")
    parser.add_argument("--role", choices=("learner", "admin"), default="learner")
    parser.add_argument("--session-file")
    parser.add_argument("--replace", action="store_true")


def dispatch_auth(args):
    path = session_path(args)
    if args.action in {"login", "signup", "verify", "dev-session"} and (path.is_symlink() or (path.exists() and not args.replace)):
        raise AuthFailure("An existing session will not be replaced implicitly; use --replace or another --session-file.", 6)
    if args.action == "dev-session":
        origin = safe_origin(args.preview_url, loopback_only=True)
        response = _http(origin, "/__dev/session", method="GET", query={"role": args.role}, timeout=args.timeout)
        if not isinstance(response.get("session"), dict) or response.get("profile", {}).get("email", "").endswith("@local.tpl.test") is not True:
            raise AuthFailure("This origin did not return the existing local-development session contract.", 8)
        return _save_response(response, args, origin, api_url=origin + "/__dev/api",
                              replace=args.replace, development=True)
    previous = read_session(path) if args.action in {"refresh", "logout", "password"} else None
    if args.action == "logout" and args.local_only:
        path.unlink()
        return {"signed_in": False, "local_session_removed": True, "provider_revocation_verified": False}
    origin = safe_origin(args.auth_url or (previous or {}).get("auth_url"))
    if previous and previous.get("development_fixture"):
        raise AuthFailure("A dev session cannot use provider refresh/password/logout. Request a new dev-session or use logout --local-only.")
    public_key = _public_key(args)
    if args.action in {"login", "signup", "recover", "verify"}:
        if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", args.email) or len(args.email) > 320:
            raise AuthFailure("A valid email address is required.")
    if args.action in {"login", "signup"}:
        password = _secret(args)
        route = "/auth/v1/token" if args.action == "login" else "/auth/v1/signup"
        response = _http(origin, route, body={"email": args.email, "password": password}, public_key=public_key,
                         query={"grant_type": "password"} if args.action == "login" else None, timeout=args.timeout)
        return _save_response(response, args, origin, replace=args.replace)
    if args.action == "recover":
        _http(origin, "/auth/v1/recover", body={"email": args.email}, public_key=public_key, timeout=args.timeout)
        return {"request_accepted": True, "delivery_verified": False,
                "notice": "If eligible, the provider will send recovery instructions. Acceptance does not verify email delivery."}
    if args.action == "verify":
        verification = {"email": args.email, "type": "email" if args.kind == "signup" else args.kind,
                        "token_hash" if args.token_hash_stdin else "token": _secret(args, "code")}
        response = _http(origin, "/auth/v1/verify", body=verification,
                         public_key=public_key, timeout=args.timeout)
        return _save_response(response, args, origin, replace=args.replace)
    if args.action == "refresh":
        if not previous.get("refresh_token"):
            raise AuthFailure("This session has no provider refresh token.")
        response = _http(origin, "/auth/v1/token", body={"refresh_token": previous["refresh_token"]}, query={"grant_type": "refresh_token"},
                         public_key=public_key, timeout=args.timeout)
        return _save_response(response, args, origin, api_url=previous.get("api_url"), replace=True)
    if args.action == "password":
        response = _http(origin, "/auth/v1/user", body={"password": _secret(args)}, method="PUT",
                         public_key=public_key, token=previous["access_token"], timeout=args.timeout)
        return {"password_updated": True, "user_id": response.get("id"), "notice": "The provider accepted the update; the password is never included in this receipt."}
    _http(origin, "/auth/v1/logout", query={"scope": "local"}, public_key=public_key,
          token=previous["access_token"], timeout=args.timeout)
    path.unlink()
    return {"signed_in": False, "local_session_removed": True, "provider_revocation_verified": True}
