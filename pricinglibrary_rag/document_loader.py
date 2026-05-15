from __future__ import annotations

import mimetypes
from pathlib import Path

from .schemas import DocumentMetadata
from .text_utils import estimate_language, normalize_text, sha256_bytes


class DocumentLoadError(RuntimeError):
    pass


class LoadedDocument:
    def __init__(
        self,
        path: Path,
        content: str,
        file_sha256: str,
        metadata: DocumentMetadata,
    ) -> None:
        self.path = path
        self.content = content
        self.file_sha256 = file_sha256
        self.metadata = metadata


def load_document(path: str | Path, metadata: DocumentMetadata | None = None) -> LoadedDocument:
    path = Path(path).expanduser().resolve()
    if not path.exists():
        raise DocumentLoadError(f"File does not exist: {path}")
    if not path.is_file():
        raise DocumentLoadError(f"Path is not a file: {path}")

    raw = path.read_bytes()
    file_sha = sha256_bytes(raw)
    metadata = metadata or DocumentMetadata()
    ext = path.suffix.lower()
    if ext == ".pdf":
        content = _extract_pdf_text(path)
    elif ext in {".txt", ".md", ".rst", ".csv"}:
        content = raw.decode("utf-8", errors="ignore")
    else:
        guessed, _ = mimetypes.guess_type(str(path))
        if guessed and guessed.startswith("text/"):
            content = raw.decode("utf-8", errors="ignore")
        else:
            raise DocumentLoadError(
                f"Unsupported file type for {path.name}. "
                "Install PyMuPDF for PDFs or provide .txt/.md files."
            )

    content = normalize_text(content)
    if not content:
        raise DocumentLoadError(f"No extractable text found in {path}")

    merged = metadata.model_copy()
    if not merged.title:
        merged.title = path.stem.replace("_", " ").replace("-", " ").strip()
    if not merged.source:
        merged.source = path.name
    if not merged.language:
        merged.language = estimate_language(content)
    return LoadedDocument(path, content, file_sha, merged)


def _extract_pdf_text(path: Path) -> str:
    try:
        import fitz  # type: ignore
    except Exception:
        fitz = None

    if fitz is not None:
        parts: list[str] = []
        with fitz.open(path) as doc:
            for page_number, page in enumerate(doc, start=1):
                text = page.get_text("text")
                if text.strip():
                    parts.append(f"\n\n[Page {page_number}]\n{text}")
        return normalize_text("\n".join(parts))

    try:
        from PyPDF2 import PdfReader  # type: ignore
    except Exception:
        PdfReader = None

    if PdfReader is not None:
        reader = PdfReader(str(path))
        parts = []
        for page_number, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            if text.strip():
                parts.append(f"\n\n[Page {page_number}]\n{text}")
        return normalize_text("\n".join(parts))

    raise DocumentLoadError(
        "PDF ingestion needs a local PDF parser. Install PyMuPDF with "
        "`pip install PyMuPDF`, then retry."
    )

