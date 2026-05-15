from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _path_from_env(name: str, default: str) -> Path:
    return Path(os.environ.get(name, default)).expanduser().resolve()


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
    ollama_url: str
    ollama_model: str
    transformers_model_path: str | None
    chunk_target_chars: int
    chunk_overlap_chars: int
    max_context_chunks: int

    @classmethod
    def from_env(cls) -> "Settings":
        _load_env_file()
        data_dir = _path_from_env("TPL_DATA_DIR", "./data")
        db_path = _path_from_env(
            "TPL_DB_PATH",
            str(data_dir / "pricinglibrary_rag.sqlite3"),
        )
        return cls(
            data_dir=data_dir,
            db_path=db_path,
            embedding_backend=os.environ.get("TPL_EMBEDDING_BACKEND", "local-hashing"),
            embedding_dim=int(os.environ.get("TPL_EMBEDDING_DIM", "2048")),
            sentence_transformer_model=os.environ.get("TPL_SENTENCE_TRANSFORMER_MODEL"),
            llm_provider=os.environ.get("TPL_LLM_PROVIDER", "openai"),
            openai_api_key=os.environ.get("TPL_OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY"),
            openai_model=os.environ.get("TPL_OPENAI_MODEL", "gpt-4o-mini"),
            openai_base_url=os.environ.get("TPL_OPENAI_BASE_URL"),
            ollama_url=os.environ.get("TPL_OLLAMA_URL", "http://localhost:11434"),
            ollama_model=os.environ.get("TPL_OLLAMA_MODEL", "llama3.1:8b"),
            transformers_model_path=os.environ.get("TPL_TRANSFORMERS_MODEL_PATH"),
            chunk_target_chars=int(os.environ.get("TPL_CHUNK_TARGET_CHARS", "2600")),
            chunk_overlap_chars=int(os.environ.get("TPL_CHUNK_OVERLAP_CHARS", "350")),
            max_context_chunks=int(os.environ.get("TPL_MAX_CONTEXT_CHUNKS", "8")),
        )

    def ensure_dirs(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
