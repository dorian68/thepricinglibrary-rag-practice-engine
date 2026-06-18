from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import numpy as np

from .embeddings import from_vector_json
from .schemas import DocumentMetadata
from .text_utils import tokenize


@dataclass(frozen=True)
class StoredDocument:
    id: str
    title: str | None
    source: str | None
    path: str | None
    file_sha256: str | None
    metadata: dict[str, Any]
    created_at: str
    status: str


@dataclass(frozen=True)
class StoredChunk:
    id: str
    document_id: str
    chunk_index: int
    content: str
    embedding: np.ndarray
    token_count: int
    section_title: str | None
    metadata: dict[str, Any]
    document_title: str | None = None
    document_source: str | None = None
    content_type: str | None = None
    pedagogical_value: int | None = None
    quality_score: int | None = None
    usable_for_course: bool | None = None


@dataclass(frozen=True)
class StoredGenerationRun:
    id: str
    kind: str
    request: dict[str, Any]
    response: dict[str, Any]
    created_at: str

    @property
    def title(self) -> str:
        return str(self.response.get("title") or self.request.get("topic") or self.id)


class LocalStore:
    def __init__(self, db_path: str | Path) -> None:
        self.db_path = Path(db_path).expanduser().resolve()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode = WAL")
        return conn

    def _init_schema(self) -> None:
        with self.connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS documents (
                    id TEXT PRIMARY KEY,
                    title TEXT,
                    source TEXT,
                    path TEXT,
                    file_sha256 TEXT UNIQUE,
                    metadata_json TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'active',
                    created_at TEXT NOT NULL DEFAULT (datetime('now')),
                    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
                );

                CREATE TABLE IF NOT EXISTS chunks (
                    id TEXT PRIMARY KEY,
                    document_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
                    chunk_index INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    embedding_json TEXT NOT NULL,
                    embedding_blob BLOB,
                    token_count INTEGER NOT NULL DEFAULT 0,
                    section_title TEXT,
                    metadata_json TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT (datetime('now')),
                    UNIQUE(document_id, chunk_index)
                );

                CREATE TABLE IF NOT EXISTS generation_runs (
                    id TEXT PRIMARY KEY,
                    kind TEXT NOT NULL,
                    request_json TEXT NOT NULL,
                    response_json TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT (datetime('now'))
                );

                CREATE TABLE IF NOT EXISTS entitlements (
                    email TEXT PRIMARY KEY,
                    plan TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'active',
                    stripe_customer_id TEXT,
                    stripe_subscription_id TEXT,
                    source TEXT,
                    created_at TEXT NOT NULL DEFAULT (datetime('now')),
                    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
                );

                CREATE TABLE IF NOT EXISTS billing_events (
                    event_id TEXT PRIMARY KEY,
                    type TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT (datetime('now'))
                );

                CREATE INDEX IF NOT EXISTS idx_chunks_document_id
                    ON chunks(document_id);
                CREATE INDEX IF NOT EXISTS idx_documents_status
                    ON documents(status);
                """
            )
            self._ensure_fts(conn)
            self._migrate_schema(conn)

    def _migrate_schema(self, conn: sqlite3.Connection) -> None:
        chunk_cols = {
            row["name"]
            for row in conn.execute("PRAGMA table_info(chunks)").fetchall()
        }
        if "embedding_blob" not in chunk_cols:
            conn.execute("ALTER TABLE chunks ADD COLUMN embedding_blob BLOB")
        # Pedagogical columns (see pedagogy.py). Kept as plain columns so the
        # corpus can be aggregated/filtered without re-scanning JSON metadata.
        pedagogical_columns = {
            "content_type": "TEXT",
            "pedagogical_value": "INTEGER",
            "quality_score": "INTEGER",
            "usable_for_course": "INTEGER",
        }
        for name, sql_type in pedagogical_columns.items():
            if name not in chunk_cols:
                conn.execute(f"ALTER TABLE chunks ADD COLUMN {name} {sql_type}")
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_chunks_content_type ON chunks(content_type)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_chunks_usable ON chunks(usable_for_course)"
        )

    def _ensure_fts(self, conn: sqlite3.Connection) -> None:
        try:
            conn.execute(
                """
                CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts
                USING fts5(chunk_id UNINDEXED, document_id UNINDEXED, content);
                """
            )
        except sqlite3.OperationalError:
            return

    def upsert_document(
        self,
        document_id: str,
        path: str,
        file_sha256: str,
        metadata: DocumentMetadata,
        force: bool = False,
    ) -> tuple[str, bool]:
        payload = metadata.model_dump()
        with self.connect() as conn:
            existing = conn.execute(
                "SELECT id FROM documents WHERE file_sha256 = ?",
                (file_sha256,),
            ).fetchone()
            if existing and not force:
                return str(existing["id"]), False
            if existing and force:
                document_id = str(existing["id"])
                conn.execute("DELETE FROM chunks WHERE document_id = ?", (document_id,))
                self._delete_fts_for_document(conn, document_id)

            conn.execute(
                """
                INSERT INTO documents (
                    id, title, source, path, file_sha256, metadata_json, status, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, 'active', datetime('now'))
                ON CONFLICT(id) DO UPDATE SET
                    title = excluded.title,
                    source = excluded.source,
                    path = excluded.path,
                    file_sha256 = excluded.file_sha256,
                    metadata_json = excluded.metadata_json,
                    status = 'active',
                    updated_at = datetime('now')
                """,
                (
                    document_id,
                    metadata.title,
                    metadata.source,
                    path,
                    file_sha256,
                    json.dumps(payload, ensure_ascii=True),
                ),
            )
            return document_id, True

    def insert_chunks(self, chunks: Iterable[StoredChunk]) -> int:
        rows = list(chunks)
        with self.connect() as conn:
            for chunk in rows:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO chunks (
                        id, document_id, chunk_index, content, embedding_json,
                        embedding_blob, token_count, section_title, metadata_json,
                        content_type, pedagogical_value, quality_score, usable_for_course
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        chunk.id,
                        chunk.document_id,
                        chunk.chunk_index,
                        chunk.content,
                        "[]",
                        chunk.embedding.astype("float32").tobytes(),
                        chunk.token_count,
                        chunk.section_title,
                        json.dumps(chunk.metadata, ensure_ascii=True),
                        chunk.content_type,
                        chunk.pedagogical_value,
                        chunk.quality_score,
                        None if chunk.usable_for_course is None else int(chunk.usable_for_course),
                    ),
                )
                try:
                    conn.execute(
                        """
                        INSERT INTO chunks_fts(chunk_id, document_id, content)
                        VALUES (?, ?, ?)
                        """,
                        (chunk.id, chunk.document_id, chunk.content),
                    )
                except sqlite3.OperationalError:
                    pass
        return len(rows)

    def _delete_fts_for_document(
        self,
        conn: sqlite3.Connection,
        document_id: str,
    ) -> None:
        try:
            conn.execute("DELETE FROM chunks_fts WHERE document_id = ?", (document_id,))
        except sqlite3.OperationalError:
            pass

    def list_documents(self, limit: int = 100, offset: int = 0) -> list[StoredDocument]:
        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT * FROM documents
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
                """,
                (limit, offset),
            ).fetchall()
        return [self._document_from_row(row) for row in rows]

    def document_text_sample(self, document_id: str, max_chunks: int = 4) -> str:
        """Concatenate the first chunks of a document (theme inference input)."""
        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT content FROM chunks
                WHERE document_id = ?
                ORDER BY chunk_index ASC
                LIMIT ?
                """,
                (document_id, max_chunks),
            ).fetchall()
        return "\n".join(str(row["content"]) for row in rows)

    def update_document_metadata(self, document_id: str, metadata: dict[str, Any]) -> None:
        with self.connect() as conn:
            conn.execute(
                """
                UPDATE documents
                SET metadata_json = ?, updated_at = datetime('now')
                WHERE id = ?
                """,
                (json.dumps(metadata, ensure_ascii=True, default=str), document_id),
            )

    def get_document_by_sha(self, file_sha256: str) -> StoredDocument | None:
        with self.connect() as conn:
            row = conn.execute(
                "SELECT * FROM documents WHERE file_sha256 = ?",
                (file_sha256,),
            ).fetchone()
        return self._document_from_row(row) if row else None

    def iter_chunks(
        self,
        *,
        product: str | None = None,
        concept: str | None = None,
        asset_class: str | None = None,
        tags: list[str] | None = None,
        content_type: str | None = None,
        usable_only: bool = False,
        min_pedagogical_value: int | None = None,
        limit: int | None = None,
    ) -> list[StoredChunk]:
        query = """
            SELECT
                c.*,
                d.title AS document_title,
                d.source AS document_source,
                d.metadata_json AS document_metadata_json
            FROM chunks c
            JOIN documents d ON d.id = c.document_id
            WHERE d.status = 'active'
        """
        params: list[Any] = []
        if content_type:
            query += " AND c.content_type = ?"
            params.append(content_type)
        if usable_only:
            query += " AND c.usable_for_course = 1"
        if min_pedagogical_value is not None:
            query += " AND c.pedagogical_value >= ?"
            params.append(min_pedagogical_value)
        if limit:
            query += " LIMIT ?"
            params.append(limit)
        with self.connect() as conn:
            rows = conn.execute(query, params).fetchall()
        chunks = [self._chunk_from_row(row) for row in rows]
        return [
            chunk
            for chunk in chunks
            if self._metadata_matches(chunk, product, concept, asset_class, tags or [])
        ]

    def pedagogy_stats(self) -> dict[str, Any]:
        """Aggregate pedagogical columns across the active corpus."""
        with self.connect() as conn:
            base = """
                FROM chunks c JOIN documents d ON d.id = c.document_id
                WHERE d.status = 'active'
            """
            total = int(conn.execute(f"SELECT count(*) {base}").fetchone()[0])
            classified = int(
                conn.execute(
                    f"SELECT count(*) {base} AND c.content_type IS NOT NULL"
                ).fetchone()[0]
            )
            usable = int(
                conn.execute(
                    f"SELECT count(*) {base} AND c.usable_for_course = 1"
                ).fetchone()[0]
            )
            avg_ped = conn.execute(
                f"SELECT avg(c.pedagogical_value) {base} AND c.pedagogical_value IS NOT NULL"
            ).fetchone()[0]
            avg_qual = conn.execute(
                f"SELECT avg(c.quality_score) {base} AND c.quality_score IS NOT NULL"
            ).fetchone()[0]
            type_rows = conn.execute(
                f"""
                SELECT c.content_type AS ct, count(*) AS n {base}
                AND c.content_type IS NOT NULL
                GROUP BY c.content_type ORDER BY n DESC
                """
            ).fetchall()
            doc_count = int(
                conn.execute("SELECT count(*) FROM documents WHERE status = 'active'").fetchone()[0]
            )
        return {
            "documents": doc_count,
            "chunks": total,
            "classified": classified,
            "unclassified": total - classified,
            "usable_for_course": usable,
            "usable_ratio": round(usable / total, 4) if total else 0.0,
            "average_pedagogical_value": round(float(avg_ped), 2) if avg_ped is not None else 0.0,
            "average_quality_score": round(float(avg_qual), 2) if avg_qual is not None else 0.0,
            "content_type_distribution": {str(r["ct"]): int(r["n"]) for r in type_rows},
        }

    def backfill_pedagogy(
        self,
        classify,
        *,
        batch_size: int = 500,
        limit: int | None = None,
        force: bool = False,
    ) -> int:
        """Classify and persist pedagogy for chunks.

        By default only chunks lacking pedagogy are processed; ``force=True``
        re-classifies the whole corpus (e.g. after the classifier improves).
        ``classify`` is a callable ``(content, section_title) -> ChunkPedagogy``
        (injected to avoid a circular import). Returns the number updated.
        """
        updated = 0
        with self.connect() as conn:
            where = "1 = 1" if force else "content_type IS NULL"
            count_sql = f"SELECT count(*) FROM chunks WHERE {where}"
            remaining = int(conn.execute(count_sql).fetchone()[0])
            target = remaining if limit is None else min(remaining, limit)
            # Keyset pagination on id so re-classified rows (force mode) are not
            # re-read: in NULL mode processed rows leave the set; in force mode
            # the id cursor advances past them.
            last_id = ""
            while updated < target:
                rows = conn.execute(
                    f"""
                    SELECT id, content, section_title, metadata_json
                    FROM chunks WHERE {where} AND id > ?
                    ORDER BY id ASC
                    LIMIT ?
                    """,
                    (last_id, min(batch_size, target - updated)),
                ).fetchall()
                if not rows:
                    break
                last_id = str(rows[-1]["id"])
                for row in rows:
                    pedagogy = classify(str(row["content"]), row["section_title"])
                    metadata = json.loads(row["metadata_json"] or "{}")
                    metadata["pedagogy"] = pedagogy.to_metadata()
                    if pedagogy.keywords:
                        metadata["keywords"] = pedagogy.keywords
                    conn.execute(
                        """
                        UPDATE chunks SET
                            metadata_json = ?,
                            content_type = ?,
                            pedagogical_value = ?,
                            quality_score = ?,
                            usable_for_course = ?
                        WHERE id = ?
                        """,
                        (
                            json.dumps(metadata, ensure_ascii=True),
                            pedagogy.content_type,
                            pedagogy.pedagogical_value,
                            pedagogy.quality_score,
                            int(pedagogy.usable_for_course),
                            str(row["id"]),
                        ),
                    )
                    updated += 1
                conn.commit()
        return updated

    def fts_candidate_ids(self, query: str, limit: int = 80) -> list[str]:
        safe_query = " OR ".join(
            token for token in query.replace('"', " ").split() if len(token) > 2
        )
        if not safe_query:
            return []
        try:
            with self.connect() as conn:
                rows = conn.execute(
                    """
                    SELECT chunk_id
                    FROM chunks_fts
                    WHERE chunks_fts MATCH ?
                    LIMIT ?
                    """,
                    (safe_query, limit),
                ).fetchall()
            return [str(row["chunk_id"]) for row in rows]
        except sqlite3.OperationalError:
            return []

    def save_generation(self, run_id: str, kind: str, request: Any, response: Any) -> None:
        with self.connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO generation_runs(id, kind, request_json, response_json)
                VALUES (?, ?, ?, ?)
                """,
                (
                    run_id,
                    kind,
                    json.dumps(request, ensure_ascii=True, default=str),
                    json.dumps(response, ensure_ascii=True, default=str),
                ),
            )

    # --- billing / entitlements -------------------------------------------
    def upsert_entitlement(
        self,
        email: str,
        plan: str,
        *,
        status: str = "active",
        stripe_customer_id: str | None = None,
        stripe_subscription_id: str | None = None,
        source: str | None = None,
    ) -> dict[str, Any]:
        email = email.strip().lower()
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO entitlements(
                    email, plan, status, stripe_customer_id,
                    stripe_subscription_id, source, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
                ON CONFLICT(email) DO UPDATE SET
                    plan = excluded.plan,
                    status = excluded.status,
                    stripe_customer_id = COALESCE(excluded.stripe_customer_id, entitlements.stripe_customer_id),
                    stripe_subscription_id = COALESCE(excluded.stripe_subscription_id, entitlements.stripe_subscription_id),
                    source = excluded.source,
                    updated_at = datetime('now')
                """,
                (email, plan, status, stripe_customer_id, stripe_subscription_id, source),
            )
        return self.get_entitlement(email) or {}

    def get_entitlement(self, email: str) -> dict[str, Any] | None:
        with self.connect() as conn:
            row = conn.execute(
                "SELECT * FROM entitlements WHERE email = ?", (email.strip().lower(),)
            ).fetchone()
        return dict(row) if row else None

    def list_entitlements(self, *, limit: int = 100) -> list[dict[str, Any]]:
        with self.connect() as conn:
            rows = conn.execute(
                "SELECT * FROM entitlements ORDER BY updated_at DESC LIMIT ?", (limit,)
            ).fetchall()
        return [dict(r) for r in rows]

    def billing_event_seen(self, event_id: str) -> bool:
        with self.connect() as conn:
            row = conn.execute(
                "SELECT 1 FROM billing_events WHERE event_id = ?", (event_id,)
            ).fetchone()
        return row is not None

    def record_billing_event(self, event_id: str, event_type: str, payload: Any) -> None:
        with self.connect() as conn:
            conn.execute(
                """
                INSERT OR IGNORE INTO billing_events(event_id, type, payload_json)
                VALUES (?, ?, ?)
                """,
                (event_id, event_type, json.dumps(payload, ensure_ascii=True, default=str)),
            )

    def list_generation_runs(
        self,
        *,
        kind: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[StoredGenerationRun]:
        query = "SELECT * FROM generation_runs"
        params: list[Any] = []
        if kind:
            query += " WHERE kind = ?"
            params.append(kind)
        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        with self.connect() as conn:
            rows = conn.execute(query, params).fetchall()
        return [self._generation_from_row(row) for row in rows]

    def get_generation_run(self, run_id: str) -> StoredGenerationRun | None:
        with self.connect() as conn:
            row = conn.execute(
                "SELECT * FROM generation_runs WHERE id = ?",
                (run_id,),
            ).fetchone()
        return self._generation_from_row(row) if row else None

    def count_generation_runs(self, *, kind: str | None = None) -> int:
        with self.connect() as conn:
            if kind:
                return int(
                    conn.execute(
                        "SELECT count(*) FROM generation_runs WHERE kind = ?",
                        (kind,),
                    ).fetchone()[0]
                )
            return int(conn.execute("SELECT count(*) FROM generation_runs").fetchone()[0])

    def _document_from_row(self, row: sqlite3.Row) -> StoredDocument:
        return StoredDocument(
            id=str(row["id"]),
            title=row["title"],
            source=row["source"],
            path=row["path"],
            file_sha256=row["file_sha256"],
            metadata=json.loads(row["metadata_json"] or "{}"),
            created_at=row["created_at"],
            status=row["status"],
        )

    def _chunk_from_row(self, row: sqlite3.Row) -> StoredChunk:
        metadata = json.loads(row["metadata_json"] or "{}")
        doc_meta_raw = row["document_metadata_json"] if "document_metadata_json" in row.keys() else None
        if doc_meta_raw:
            metadata.setdefault("document", json.loads(doc_meta_raw or "{}"))
        embedding = None
        if "embedding_blob" in row.keys() and row["embedding_blob"] is not None:
            embedding = np.frombuffer(row["embedding_blob"], dtype=np.float32).copy()
        else:
            embedding = from_vector_json(str(row["embedding_json"]))
        keys = row.keys()
        usable_raw = row["usable_for_course"] if "usable_for_course" in keys else None
        return StoredChunk(
            id=str(row["id"]),
            document_id=str(row["document_id"]),
            chunk_index=int(row["chunk_index"]),
            content=str(row["content"]),
            embedding=embedding,
            token_count=int(row["token_count"]),
            section_title=row["section_title"],
            metadata=metadata,
            document_title=row["document_title"] if "document_title" in keys else None,
            document_source=row["document_source"] if "document_source" in keys else None,
            content_type=row["content_type"] if "content_type" in keys else None,
            pedagogical_value=row["pedagogical_value"] if "pedagogical_value" in keys else None,
            quality_score=row["quality_score"] if "quality_score" in keys else None,
            usable_for_course=None if usable_raw is None else bool(usable_raw),
        )

    def _generation_from_row(self, row: sqlite3.Row) -> StoredGenerationRun:
        return StoredGenerationRun(
            id=str(row["id"]),
            kind=str(row["kind"]),
            request=json.loads(row["request_json"] or "{}"),
            response=json.loads(row["response_json"] or "{}"),
            created_at=str(row["created_at"]),
        )

    def _metadata_matches(
        self,
        chunk: StoredChunk,
        product: str | None,
        concept: str | None,
        asset_class: str | None,
        tags: list[str],
    ) -> bool:
        doc_meta = chunk.metadata.get("document", {})
        merged = {**doc_meta, **chunk.metadata}
        haystack = json.dumps(merged, ensure_ascii=True).lower()

        def contains(value: str | None) -> bool:
            if not value:
                return True
            lowered = value.lower()
            if lowered in haystack:
                return True
            terms = tokenize(lowered)
            return bool(terms) and all(term in haystack for term in terms)

        if not contains(product) or not contains(concept) or not contains(asset_class):
            return False
        return all(tag.lower() in haystack for tag in tags)
