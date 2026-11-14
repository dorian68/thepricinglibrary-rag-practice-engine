"""Owned loopback API for the website's local admin preview.

Launched by Vite, never imported by the deployed API. Uses the real API and
stores test activity separately; no real account, payment or provider keys.
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import secrets
import sqlite3
import sys
import threading

BACKEND = Path(__file__).resolve().parents[1]
REPOSITORY = BACKEND.parents[1]
PREVIEW_ROOT = REPOSITORY / "WEBSITE" / "thepricinglab" / ".local-preview"
USER_ID = "00000000-0000-4000-8000-000000000001"
USER_EMAIL = "admin@local.tpl.test"


def use_readonly_corpus(services) -> None:
    """Read the existing reference corpus without copying or modifying it.

    Generation history, user activity and entitlements stay in the isolated
    store. This avoids making a first sign-in wait for corpus re-indexing.
    """
    from pricinglibrary_rag.embeddings import LocalHashingEmbedding
    from pricinglibrary_rag.retrieval import build_retriever
    from pricinglibrary_rag.storage import LocalStore
    import json

    source = BACKEND / "data" / "pricinglibrary_rag.sqlite3"
    if not source.is_file():
        print("[local-preview] No local RAG corpus; courses and tools remain available.", flush=True)
        return

    class ReadOnlyCorpus(LocalStore):
        def __init__(self, corpus_path: Path) -> None:
            self.db_path = corpus_path.resolve()

        def connect(self) -> sqlite3.Connection:
            connection = sqlite3.connect(self.db_path.as_uri() + "?mode=ro", uri=True)
            connection.row_factory = sqlite3.Row
            connection.execute("PRAGMA query_only=ON")
            return connection

    corpus = ReadOnlyCorpus(source)
    with corpus.connect() as connection:
        row = connection.execute("SELECT embedding_blob,embedding_json FROM chunks LIMIT 1").fetchone()
        if row is None:
            return
        dimension = len(row["embedding_blob"]) // 4 if row["embedding_blob"] is not None else len(json.loads(row["embedding_json"]))
    services.retriever = build_retriever("lexical", corpus, LocalHashingEmbedding(dim=dimension))
    services.generator.retriever = services.retriever


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, required=True)
    args = parser.parse_args()
    secret = os.environ.get("TPL_LOCAL_PREVIEW_SECRET", "")
    if os.environ.get("TPL_LOCAL_PREVIEW") != "1" or len(secret) < 32:
        parser.error("This launcher requires an owned local-preview process and a temporary signing secret.")
    if not 1024 <= args.port <= 65535:
        parser.error("Invalid loopback port.")

    # Deliberately ignore the developer's real .env and inherited provider keys.
    allowed = {"PATH", "SYSTEMROOT", "WINDIR", "TEMP", "TMP", "USERPROFILE", "LOCALAPPDATA", "APPDATA", "COMSPEC", "PATHEXT", "LANG", "LC_ALL"}
    clean = {key: value for key, value in os.environ.items() if key.upper() in allowed}
    os.environ.clear()
    os.environ.update(clean)
    root = PREVIEW_ROOT.resolve()
    expected = (REPOSITORY / "WEBSITE" / "thepricinglab").resolve()
    if root.parent != expected or root.name != ".local-preview":
        raise RuntimeError("Local preview data must stay in the website's .local-preview directory.")
    data = root / "data"
    data.mkdir(parents=True, exist_ok=True)
    os.environ.update({
        "TPL_ENVIRONMENT": "local",
        "TPL_ENFORCE_ENTITLEMENTS": "true",
        "TPL_DATA_DIR": str(data),
        "TPL_DB_PATH": str(data / "pricinglibrary_rag.sqlite3"),
        "TPL_API_KEY": secrets.token_urlsafe(36),
        "TPL_OPERATOR_API_KEY": secrets.token_urlsafe(36),
        "TPL_AUTH_TOKEN_SECRET": secret,
        "TPL_AUTH_ALGORITHMS": "HS256",
        "GENERATION_MODE": "template",
        "RETRIEVAL_MODE": "lexical",
        "EMBEDDING_PROVIDER": "local",
        "TPL_LLM_PROVIDER": "template",
        "TPL_EMBEDDING_BACKEND": "local-hashing",
        "TPL_COURSE_SCRIPTS_DIR": str(BACKEND / "pricinglibrary_rag" / "course_scripts"),
        "TPL_STARTER_KIT_BUNDLE_PATH": str(REPOSITORY / "Products" / "market_finance_starter_kit" / "release" / "starter-kit-v1.0.0.zip"),
        "TPL_STARTER_KIT_MANIFEST_PATH": str(REPOSITORY / "Products" / "market_finance_starter_kit" / "release" / "manifest.json"),
        "PYTHONIOENCODING": "utf-8",
    })
    sys.path.insert(0, str(BACKEND))
    from pricinglibrary_rag import config

    # Process-local override only: production's configuration loader is intact.
    config._load_env_file = lambda: None
    from pricinglibrary_rag.factory import build_services

    services = build_services()
    use_readonly_corpus(services)
    services.store.upsert_entitlement(USER_EMAIL, "pro", user_id=USER_ID, source="local-preview")
    services.store.upsert_product_entitlement(USER_ID, "market-finance-starter-kit", source="local-preview")
    from pricinglibrary_rag.api import create_app
    import uvicorn

    # Vite keeps stdin open. If its owning process exits, this child exits too.
    def owner_closed() -> None:
        sys.stdin.buffer.read()
        os._exit(0)

    threading.Thread(target=owner_closed, daemon=True).start()
    uvicorn.run(create_app(services), host="127.0.0.1", port=args.port, log_level="warning", access_log=False)


if __name__ == "__main__":
    main()
