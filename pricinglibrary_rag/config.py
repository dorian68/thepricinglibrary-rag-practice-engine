from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


def _path_from_env(name: str, default: str) -> Path:
    return Path(os.environ.get(name, default)).expanduser().resolve()


def _env_bool(name: str, default: bool) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in ("1", "true", "yes", "on")


def _load_env_file() -> None:
    env_path = os.environ.get("TPL_ENV_PATH")
    candidates = []
    if env_path:
        candidates.append(Path(env_path).expanduser())
    candidates.extend([Path.cwd() / ".env", Path(__file__).resolve().parents[1] / ".env"])
    for path in candidates:
        if not path.exists() or not path.is_file():
            continue
        for raw_line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value


@dataclass(frozen=True)
class Settings:
    """Runtime configuration.

    Defaults are local-only and do not call any external service.
    """

    data_dir: Path
    db_path: Path
    embedding_backend: str
    embedding_dim: int
    sentence_transformer_model: str | None
    llm_provider: str
    openai_api_key: str | None
    openai_model: str
    openai_base_url: str | None
    openai_timeout_seconds: float
    openai_max_retries: int
    ollama_url: str
    ollama_model: str
    transformers_model_path: str | None
    chunk_target_chars: int
    chunk_overlap_chars: int
    max_context_chunks: int
    # --- public-deployment guards (defaulted so local callers keep working) --
    cors_origins: tuple[str, ...] = ()
    api_key: str | None = None
    rate_limit_per_min: int = 0
    # --- generation / retrieval pipeline modes (safe defaults) ------------
    # generation_mode: "template" (deterministic, zero API) | "llm" (LLM writer).
    # retrieval_mode:  "lexical" | "semantic" | "hybrid".
    # embedding_provider: "local" | "openai" | "none" (only affects the vector
    #   side; switching it requires re-ingesting the corpus, see docs).
    # strict_validation: when an LLM rewrites an exercise, fall back to the
    #   deterministic template if it alters any calculated number.
    generation_mode: str = "template"
    retrieval_mode: str = "hybrid"
    embedding_provider: str = "local"
    strict_validation: bool = True
    # --- billing (Stripe) — defaulted so existing callers keep working ----
    stripe_secret_key: str | None = None
    stripe_webhook_secret: str | None = None
    stripe_prices: dict[str, str] = field(default_factory=dict)
    billing_checkout_mode: str = "subscription"
    billing_success_url: str = "http://localhost:5173/billing/success?session_id={CHECKOUT_SESSION_ID}"
    billing_cancel_url: str = "http://localhost:5173/pricing"

    @property
    def billing_configured(self) -> bool:
        """True when real Stripe checkout can be created (secret key + at least
        one price). When False the service runs in offline 'mock' mode and never
        touches real money."""
        return bool(self.stripe_secret_key) and bool(self.stripe_prices)

    @classmethod
    def from_env(cls) -> "Settings":
        _load_env_file()
        data_dir = _path_from_env("TPL_DATA_DIR", "./data")
        db_path = _path_from_env(
            "TPL_DB_PATH",
            str(data_dir / "pricinglibrary_rag.sqlite3"),
        )

        # --- high-level pipeline modes (new env names, with safe defaults) --
        generation_mode = os.environ.get("GENERATION_MODE", "template").strip().lower()
        retrieval_mode = os.environ.get("RETRIEVAL_MODE", "hybrid").strip().lower()
        embedding_provider = os.environ.get("EMBEDDING_PROVIDER", "local").strip().lower()
        strict_validation = _env_bool("GENERATION_STRICT_VALIDATION", True)

        # LLM provider: prefer the new LLM_PROVIDER, fall back to legacy
        # TPL_LLM_PROVIDER. "none" means "no LLM" -> deterministic template.
        # When generation_mode is "template" the LLM writer is OFF regardless,
        # so the effective provider stays "template" (zero API, safe default).
        llm_provider_raw = (
            os.environ.get("LLM_PROVIDER")
            or os.environ.get("TPL_LLM_PROVIDER")
            or "template"
        ).strip().lower()
        if llm_provider_raw in ("none", ""):
            llm_provider_raw = "template"
        effective_llm_provider = (
            llm_provider_raw if generation_mode == "llm" else "template"
        )

        # Embedding backend: legacy TPL_EMBEDDING_BACKEND wins if set, else it is
        # derived from EMBEDDING_PROVIDER. "none"/"local" -> the offline hashing
        # backend; "openai" -> OpenAI embeddings (requires re-ingestion).
        embedding_backend = os.environ.get("TPL_EMBEDDING_BACKEND")
        if not embedding_backend:
            embedding_backend = {
                "local": "local-hashing",
                "none": "local-hashing",
                "openai": "openai",
            }.get(embedding_provider, "local-hashing")

        return cls(
            data_dir=data_dir,
            db_path=db_path,
            embedding_backend=embedding_backend,
            embedding_dim=int(os.environ.get("TPL_EMBEDDING_DIM", "2048")),
            sentence_transformer_model=os.environ.get("TPL_SENTENCE_TRANSFORMER_MODEL"),
            llm_provider=effective_llm_provider,
            openai_api_key=os.environ.get("TPL_OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY"),
            openai_model=os.environ.get("TPL_OPENAI_MODEL", "gpt-4o-mini"),
            openai_base_url=os.environ.get("TPL_OPENAI_BASE_URL"),
            openai_timeout_seconds=float(os.environ.get("TPL_OPENAI_TIMEOUT_SECONDS", "90")),
            openai_max_retries=int(os.environ.get("TPL_OPENAI_MAX_RETRIES", "1")),
            ollama_url=os.environ.get("TPL_OLLAMA_URL", "http://localhost:11434"),
            ollama_model=os.environ.get("TPL_OLLAMA_MODEL", "llama3.1:8b"),
            transformers_model_path=os.environ.get("TPL_TRANSFORMERS_MODEL_PATH"),
            chunk_target_chars=int(os.environ.get("TPL_CHUNK_TARGET_CHARS", "2600")),
            chunk_overlap_chars=int(os.environ.get("TPL_CHUNK_OVERLAP_CHARS", "350")),
            max_context_chunks=int(os.environ.get("TPL_MAX_CONTEXT_CHUNKS", "8")),
            cors_origins=tuple(
                o.strip()
                for o in os.environ.get("TPL_CORS_ORIGINS", "").split(",")
                if o.strip()
            ),
            api_key=os.environ.get("TPL_API_KEY") or None,
            rate_limit_per_min=int(os.environ.get("TPL_RATE_LIMIT_PER_MIN", "0")),
            generation_mode=generation_mode,
            retrieval_mode=retrieval_mode,
            embedding_provider=embedding_provider,
            strict_validation=strict_validation,
            stripe_secret_key=os.environ.get("STRIPE_SECRET_KEY") or os.environ.get("TPL_STRIPE_SECRET_KEY"),
            stripe_webhook_secret=os.environ.get("STRIPE_WEBHOOK_SECRET") or os.environ.get("TPL_STRIPE_WEBHOOK_SECRET"),
            stripe_prices={
                plan: price
                for plan, env_name in (
                    ("starter", "STRIPE_PRICE_STARTER"),
                    ("student", "STRIPE_PRICE_STUDENT"),
                    ("pro", "STRIPE_PRICE_PRO"),
                )
                if (price := os.environ.get(env_name))
            },
            billing_checkout_mode=os.environ.get("TPL_BILLING_CHECKOUT_MODE", "subscription"),
            billing_success_url=os.environ.get(
                "TPL_BILLING_SUCCESS_URL",
                "http://localhost:5173/billing/success?session_id={CHECKOUT_SESSION_ID}",
            ),
            billing_cancel_url=os.environ.get(
                "TPL_BILLING_CANCEL_URL", "http://localhost:5173/pricing"
            ),
        )

    def ensure_dirs(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
