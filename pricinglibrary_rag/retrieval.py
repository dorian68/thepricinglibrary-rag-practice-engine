from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass

import numpy as np

from .embeddings import EmbeddingBackend, cosine_similarity
from .schemas import SearchRequest, SearchResponse, SourceRef
from .storage import LocalStore, StoredChunk
from .text_utils import concise_snippet, tokenize


@dataclass(frozen=True)
class RetrievedChunk:
    chunk: StoredChunk
    score: float
    vector_score: float
    lexical_score: float


class LocalRetriever:
    def __init__(
        self,
        store: LocalStore,
        embeddings: EmbeddingBackend,
        vector_weight: float = 0.58,
        lexical_weight: float = 0.42,
    ) -> None:
        self.store = store
        self.embeddings = embeddings
        self.vector_weight = vector_weight
        self.lexical_weight = lexical_weight
        self._cached_chunks: list[StoredChunk] | None = None
        self._cached_matrix: np.ndarray | None = None

    def refresh(self) -> None:
        self._cached_chunks = None
        self._cached_matrix = None

    def search(self, request: SearchRequest) -> SearchResponse:
        results = self.retrieve(
            query=request.query,
            top_k=request.top_k,
            product=request.product,
            concept=request.concept,
            asset_class=request.asset_class,
            tags=request.tags,
        )
        return SearchResponse(
            query=request.query,
            results=[self.to_source_ref(item) for item in results],
        )

    def retrieve(
        self,
        query: str,
        top_k: int = 8,
        *,
        product: str | None = None,
        concept: str | None = None,
        asset_class: str | None = None,
        tags: list[str] | None = None,
    ) -> list[RetrievedChunk]:
        chunks = self._get_chunks(
            product=product,
            concept=concept,
            asset_class=asset_class,
            tags=tags or [],
        )
        if not chunks:
            return []

        query_vector = self.embeddings.embed_one(query)
        matrix = self._get_matrix(chunks, product, concept, asset_class, tags or [])
        vector_scores = cosine_similarity(query_vector, matrix)

        candidate_indices = set(
            int(i)
            for i in np.argsort(-vector_scores)[: max(top_k * 10, 160)]
        )
        id_to_idx = {chunk.id: idx for idx, chunk in enumerate(chunks)}
        fts_ids = set(self.store.fts_candidate_ids(query, limit=max(top_k * 10, 120)))
        candidate_indices.update(
            id_to_idx[chunk_id] for chunk_id in fts_ids if chunk_id in id_to_idx
        )
        if not candidate_indices:
            candidate_indices = set(range(len(chunks)))

        candidate_order = sorted(candidate_indices)
        candidate_chunks = [chunks[idx] for idx in candidate_order]
        candidate_vector_scores = vector_scores[candidate_order]
        lexical_scores = self._bm25_scores(query, candidate_chunks)
        vector_norm = self._normalize_scores(candidate_vector_scores)
        lexical_norm = self._normalize_scores(lexical_scores)

        combined = (
            self.vector_weight * vector_norm
            + self.lexical_weight * lexical_norm
        )
        quality_scores = np.asarray(
            [self._quality_score(chunk.content) for chunk in candidate_chunks],
            dtype=np.float32,
        )
        combined = combined * (0.35 + 0.65 * quality_scores)
        if fts_ids:
            combined = np.asarray(
                [
                    score + (0.06 if candidate_chunks[i].id in fts_ids else 0.0)
                    for i, score in enumerate(combined)
                ],
                dtype=np.float32,
            )

        order = np.argsort(-combined)[: max(top_k, 1)]
        out: list[RetrievedChunk] = []
        for idx in order:
            out.append(
                RetrievedChunk(
                    chunk=candidate_chunks[int(idx)],
                    score=float(combined[int(idx)]),
                    vector_score=float(candidate_vector_scores[int(idx)]),
                    lexical_score=float(lexical_scores[int(idx)]),
                )
            )
        return out

    def to_source_ref(self, item: RetrievedChunk) -> SourceRef:
        chunk = item.chunk
        return SourceRef(
            document_id=chunk.document_id,
            chunk_id=chunk.id,
            title=chunk.document_title,
            source=chunk.document_source,
            chunk_index=chunk.chunk_index,
            score=round(item.score, 6),
            vector_score=round(item.vector_score, 6),
            lexical_score=round(item.lexical_score, 6),
            snippet=concise_snippet(chunk.content),
        )

    def _stack_embeddings(self, chunks: list[StoredChunk]) -> np.ndarray:
        return np.vstack([chunk.embedding for chunk in chunks]).astype(np.float32)

    def _get_chunks(
        self,
        *,
        product: str | None,
        concept: str | None,
        asset_class: str | None,
        tags: list[str],
    ) -> list[StoredChunk]:
        if not product and not concept and not asset_class and not tags:
            if self._cached_chunks is None:
                self._cached_chunks = self.store.iter_chunks()
            return self._cached_chunks
        return self.store.iter_chunks(
            product=product,
            concept=concept,
            asset_class=asset_class,
            tags=tags,
        )

    def _get_matrix(
        self,
        chunks: list[StoredChunk],
        product: str | None,
        concept: str | None,
        asset_class: str | None,
        tags: list[str],
    ) -> np.ndarray:
        if not product and not concept and not asset_class and not tags:
            if self._cached_matrix is None:
                self._cached_matrix = self._stack_embeddings(chunks)
            return self._cached_matrix
        return self._stack_embeddings(chunks)

    def _normalize_scores(self, scores: np.ndarray) -> np.ndarray:
        if len(scores) == 0:
            return scores
        low = float(scores.min())
        high = float(scores.max())
        if math.isclose(low, high):
            return np.ones_like(scores, dtype=np.float32) if high > 0 else np.zeros_like(scores)
        return ((scores - low) / (high - low)).astype(np.float32)

    def _bm25_scores(self, query: str, chunks: list[StoredChunk]) -> np.ndarray:
        query_terms = tokenize(query)
        if not query_terms:
            return np.zeros((len(chunks),), dtype=np.float32)

        docs = [tokenize(chunk.content) for chunk in chunks]
        n_docs = len(docs)
        doc_freq = Counter()
        lengths = []
        for doc in docs:
            lengths.append(len(doc))
            doc_freq.update(set(doc))
        avg_len = sum(lengths) / max(n_docs, 1)
        k1 = 1.5
        b = 0.75

        scores = np.zeros((n_docs,), dtype=np.float32)
        for i, doc in enumerate(docs):
            counts = Counter(doc)
            doc_len = max(lengths[i], 1)
            score = 0.0
            for term in query_terms:
                tf = counts.get(term, 0)
                if tf <= 0:
                    continue
                df = doc_freq.get(term, 0)
                idf = math.log(1 + (n_docs - df + 0.5) / (df + 0.5))
                denom = tf + k1 * (1 - b + b * doc_len / max(avg_len, 1))
                score += idf * (tf * (k1 + 1)) / denom
            scores[i] = score
        return scores

    def _quality_score(self, text: str) -> float:
        stripped = text.strip()
        if not stripped:
            return 0.0
        tokens = tokenize(stripped)
        token_count = len(tokens)
        if token_count < 25:
            return 0.15

        lines = [line.strip() for line in stripped.splitlines() if line.strip()]
        avg_line_len = sum(len(line) for line in lines) / max(len(lines), 1)
        short_line_ratio = (
            sum(1 for line in lines if len(line) < 34) / max(len(lines), 1)
        )
        sentence_like = len(re.findall(r"[.!?]\s+[A-Z0-9]", stripped))
        alpha_ratio = sum(ch.isalpha() for ch in stripped) / max(len(stripped), 1)
        digit_ratio = sum(ch.isdigit() for ch in stripped) / max(len(stripped), 1)
        lower = stripped.lower()

        score = 1.0
        if avg_line_len < 42 and short_line_ratio > 0.45:
            score *= 0.45
        if sentence_like < 2 and token_count < 140:
            score *= 0.55
        if alpha_ratio < 0.45:
            score *= 0.55
        if digit_ratio > 0.22:
            score *= 0.75
        if "index" in lower[:220] or "table of contents" in lower[:300]:
            score *= 0.35
        if "related articles" in lower and short_line_ratio > 0.35:
            score *= 0.55
        return max(0.05, min(score, 1.0))
