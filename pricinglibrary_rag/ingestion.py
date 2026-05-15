from __future__ import annotations

from pathlib import Path

from .config import Settings
from .document_loader import DocumentLoadError, load_document
from .embeddings import EmbeddingBackend
from .schemas import DocumentMetadata, IngestResult
from .storage import LocalStore, StoredChunk
from .text_utils import chunk_text, keyword_scores, stable_id


class IngestionService:
    def __init__(
        self,
        store: LocalStore,
        embeddings: EmbeddingBackend,
        settings: Settings,
    ) -> None:
        self.store = store
        self.embeddings = embeddings
        self.settings = settings

    def ingest_file(
        self,
        path: str | Path,
        metadata: DocumentMetadata | None = None,
        force: bool = False,
    ) -> IngestResult:
        try:
            loaded = load_document(path, metadata)
        except DocumentLoadError as exc:
            return IngestResult(
                document_id="",
                path=str(path),
                status="failed",
                message=str(exc),
            )

        document_id = stable_id(str(loaded.path), loaded.file_sha256, size=24)
        document_id, should_insert = self.store.upsert_document(
            document_id=document_id,
            path=str(loaded.path),
            file_sha256=loaded.file_sha256,
            metadata=loaded.metadata,
            force=force,
        )
        if not should_insert:
            return IngestResult(
                document_id=document_id,
                path=str(loaded.path),
                status="skipped",
                message="Document already ingested. Use force=True to reingest.",
            )

        text_chunks = chunk_text(
            loaded.content,
            target_chars=self.settings.chunk_target_chars,
            overlap_chars=self.settings.chunk_overlap_chars,
        )
        if not text_chunks:
            return IngestResult(
                document_id=document_id,
                path=str(loaded.path),
                status="failed",
                message="No chunks generated.",
            )

        vectors = self.embeddings.embed([chunk.content for chunk in text_chunks])
        top_terms = [term for term, _ in keyword_scores([loaded.content], top_k=20)]
        stored_chunks: list[StoredChunk] = []
        for idx, chunk in enumerate(text_chunks):
            chunk_terms = [term for term, _ in keyword_scores([chunk.content], top_k=12)]
            chunk_id = stable_id(document_id, str(idx), chunk.content[:100], size=24)
            stored_chunks.append(
                StoredChunk(
                    id=chunk_id,
                    document_id=document_id,
                    chunk_index=idx,
                    content=chunk.content,
                    embedding=vectors[idx],
                    token_count=chunk.token_count,
                    section_title=chunk.section_title,
                    metadata={
                        "start_char": chunk.start_char,
                        "end_char": chunk.end_char,
                        "keywords": chunk_terms,
                        "document_keywords": top_terms,
                        "embedding_backend": self.embeddings.name,
                        "embedding_dim": self.embeddings.dim,
                    },
                )
            )
        inserted = self.store.insert_chunks(stored_chunks)
        return IngestResult(
            document_id=document_id,
            path=str(loaded.path),
            status="ingested",
            chunks_inserted=inserted,
        )

    def ingest_directory(
        self,
        path: str | Path,
        metadata: DocumentMetadata | None = None,
        glob: str = "*.pdf",
        recursive: bool = True,
        force: bool = False,
    ) -> list[IngestResult]:
        root = Path(path).expanduser().resolve()
        if not root.exists() or not root.is_dir():
            return [
                IngestResult(
                    document_id="",
                    path=str(root),
                    status="failed",
                    message="Directory does not exist.",
                )
            ]
        iterator = root.rglob(glob) if recursive else root.glob(glob)
        results = []
        for file_path in sorted(iterator):
            results.append(self.ingest_file(file_path, metadata, force=force))
        return results

