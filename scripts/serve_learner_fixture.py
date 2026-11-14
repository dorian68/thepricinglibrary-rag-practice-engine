"""Serve an explicit loopback-only learner QA cohort from a clean checkout.

No personal .env, provider, textbook corpus, purchase or real learner is used.
Existing fixture activity is preserved. Temporary keys are written to a private
file; stdout contains only its path and the API address.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import secrets
import socket
import sys
import time

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=0)
    parser.add_argument("--data-dir", type=Path, default=BACKEND / ".learner-fixtures" / "default")
    args = parser.parse_args()
    if not 0 <= args.port <= 65535:
        parser.error("Use a valid local port or 0 for an ephemeral port.")
    folder = args.data_dir.expanduser().resolve()
    marker = folder / ".tpl-learner-fixture"
    if folder.exists() and any(folder.iterdir()) and not marker.is_file():
        parser.error("Choose an empty directory or an existing marked TPL fixture; existing user stores are never reused.")
    folder.mkdir(parents=True, exist_ok=True)
    marker.write_text("Isolated learner QA fixture; never a production or customer store.\n", encoding="utf-8")
    allowed = {"PATH", "SYSTEMROOT", "WINDIR", "TEMP", "TMP", "USERPROFILE", "LOCALAPPDATA", "APPDATA", "COMSPEC", "PATHEXT", "LANG", "LC_ALL"}
    environment = {key: value for key, value in os.environ.items() if key.upper() in allowed}
    secret = secrets.token_urlsafe(48)
    environment.update({"PYTHONIOENCODING": "utf-8", "TPL_ENVIRONMENT": "production",
                        "TPL_DATA_DIR": str(folder), "TPL_DB_PATH": str(folder / "platform.sqlite3"),
                        "TPL_API_KEY": "fixture-member-" + secrets.token_hex(32),
                        "TPL_OPERATOR_API_KEY": "fixture-operator-" + secrets.token_hex(32),
                        "TPL_AUTH_TOKEN_SECRET": secret, "TPL_RATE_LIMIT_PER_MIN": "10000",
                        "TPL_LLM_PROVIDER": "template", "GENERATION_MODE": "template",
                        "TPL_EMBEDDING_BACKEND": "local-hashing", "TPL_EMBEDDING_DIM": "64", "RETRIEVAL_MODE": "lexical",
                        "TPL_COURSE_SCRIPTS_DIR": str(folder / "private-course-fixtures"),
                        "TPL_SOURCE_RIGHTS_CLEARED": "false", "TPL_ENFORCE_ENTITLEMENTS": "true"})
    os.environ.clear(); os.environ.update(environment)
    from pricinglibrary_rag import config
    config._load_env_file = lambda: None
    from pricinglibrary_rag.config import Settings
    from pricinglibrary_rag.factory import build_services
    from pricinglibrary_rag.security import mint_session_token
    from pricinglibrary_rag.api import create_app
    from pricinglibrary_rag.cli_auth import _store
    import uvicorn
    services = build_services(Settings.from_env())
    identities = {}
    for actor, plan, role in [("free", "free", "member"), ("starter", "starter", "member"),
                              ("student", "student", "member"), ("pro", "pro", "member"),
                              ("other", "pro", "member"), ("operator", "pro", "operator")]:
        user_id, email = f"fixture-{actor}", f"{actor}@local.tpl.test"
        if plan != "free":
            services.store.upsert_entitlement(email, plan, user_id=user_id, status="active", source="explicit-learner-QA-fixture")
        identities[actor] = {"id": user_id, "email": email, "role": role, "plan": plan,
                             "access_token": mint_session_token(secret, user_id=user_id, email=email, role=role,
                                                                 expires_at=int(time.time()) + 14400)}
    application = create_app(services)
    # Fail closed on accidental provider calls in the API process. This is a QA
    # fixture, not a network proxy or a way to activate external subscriptions.
    original_connect = socket.socket.connect
    def loopback_connect(sock, address):
        if isinstance(address, tuple) and address[0] not in {"127.0.0.1", "localhost", "::1"}:
            raise OSError("External providers are disabled in the learner QA fixture.")
        return original_connect(sock, address)
    socket.socket.connect = loopback_connect
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.bind(("127.0.0.1", args.port))
    base_url = f"http://127.0.0.1:{listener.getsockname()[1]}"
    credentials = folder / "session-credentials.private.json"
    _store(credentials, {"access_token": identities["pro"]["access_token"], "base_url": base_url,
                         "api_url": base_url, "identities": identities, "fixture": True}, replace=True)
    print(json.dumps({"base_url": base_url, "credentials_file": str(credentials), "fixture": True,
                      "notice": "Signed QA actors only; no real signup, purchase, provider or private corpus."}), flush=True)
    uvicorn.Server(uvicorn.Config(application, host="127.0.0.1", port=listener.getsockname()[1],
                                  log_level="warning", access_log=False)).run(sockets=[listener])


if __name__ == "__main__":
    main()
