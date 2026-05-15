from __future__ import annotations

import importlib.util
from abc import ABC, abstractmethod
from typing import Iterable

import numpy as np
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.preprocessing import normalize


class EmbeddingBackend(ABC):
    name: str
    dim: int

    @abstractmethod
    def embed(self, texts: list[str]) -> np.ndarray:
        raise NotImplementedError

    def embed_one(self, text: str) -> np.ndarray:
        return self.embed([text])[0]


class LocalHashingEmbedding(EmbeddingBackend):
    """Local deterministic embedding fallback.

    This is not as semantic as a transformer embedding, but it gives a robust
    zero-network baseline and works well when combined with lexical scoring.
    """

    def __init__(self, dim: int = 2048) -> None:
        self.name = "local-hashing"
        self.dim = dim
        self._vectorizer = HashingVectorizer(
            n_features=dim,
            alternate_sign=False,
            norm=None,
            lowercase=True,
            ngram_range=(1, 2),
        )

    def embed(self, texts: list[str]) -> np.ndarray:
        if not texts:
            return np.zeros((0, self.dim), dtype=np.float32)
        matrix = self._vectorizer.transform(texts)
        matrix = normalize(matrix, norm="l2", axis=1, copy=False)
        return matrix.astype(np.float32).toarray()


class SentenceTransformerEmbedding(EmbeddingBackend):
    def __init__(self, model_name_or_path: str) -> None:
        if importlib.util.find_spec("sentence_transformers") is None:
            raise RuntimeError("sentence-transformers is not installed")
        from sentence_transformers import SentenceTransformer  # type: ignore

        self.name = f"sentence-transformers:{model_name_or_path}"
        self._model = SentenceTransformer(model_name_or_path)
        dim = self._model.get_sentence_embedding_dimension()
        self.dim = int(dim) if dim else 0

    def embed(self, texts: list[str]) -> np.ndarray:
        if not texts:
            return np.zeros((0, self.dim), dtype=np.float32)
        vectors = self._model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        return np.asarray(vectors, dtype=np.float32)


def build_embedding_backend(
    backend_name: str = "local-hashing",
    dim: int = 2048,
    sentence_transformer_model: str | None = None,
) -> EmbeddingBackend:
    if backend_name == "sentence-transformers":
        if not sentence_transformer_model:
            raise RuntimeError(
                "TPL_SENTENCE_TRANSFORMER_MODEL must point to a local model."
            )
        return SentenceTransformerEmbedding(sentence_transformer_model)
    if backend_name == "local-hashing":
        return LocalHashingEmbedding(dim=dim)
    raise ValueError(f"Unknown embedding backend: {backend_name}")


def cosine_similarity(query: np.ndarray, matrix: np.ndarray) -> np.ndarray:
    if matrix.size == 0:
        return np.zeros((0,), dtype=np.float32)
    q = query.astype(np.float32)
    if q.ndim != 1:
        q = q.reshape(-1)
    denom = max(float(np.linalg.norm(q)), 1e-12)
    q = q / denom
    return matrix @ q


def as_vector_json(vector: Iterable[float]) -> str:
    import json

    return json.dumps([float(x) for x in vector], separators=(",", ":"))


def from_vector_json(raw: str) -> np.ndarray:
    import json

    return np.asarray(json.loads(raw), dtype=np.float32)

