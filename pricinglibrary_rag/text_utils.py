from __future__ import annotations

import hashlib
import math
import re
from collections import Counter
from dataclasses import dataclass
from typing import Iterable


TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z0-9_+\-./]{1,}|[0-9]+(?:\.[0-9]+)?%?")
SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")

STOPWORDS = {
    "about",
    "above",
    "after",
    "again",
    "against",
    "also",
    "and",
    "are",
    "because",
    "been",
    "before",
    "between",
    "both",
    "but",
    "can",
    "could",
    "does",
    "down",
    "during",
    "each",
    "from",
    "have",
    "into",
    "more",
    "most",
    "not",
    "only",
    "other",
    "over",
    "same",
    "should",
    "some",
    "such",
    "than",
    "that",
    "the",
    "their",
    "then",
    "there",
    "these",
    "they",
    "this",
    "through",
    "under",
    "very",
    "was",
    "were",
    "what",
    "when",
    "where",
    "which",
    "while",
    "with",
    "would",
    "you",
    "your",
    "dans",
    "des",
    "donc",
    "elle",
    "est",
    "etre",
    "ils",
    "les",
    "leur",
    "mais",
    "nous",
    "par",
    "pas",
    "plus",
    "pour",
    "que",
    "qui",
    "sur",
    "une",
    "vous",
}


def stable_id(*parts: str, size: int = 16) -> str:
    joined = "::".join(parts).encode("utf-8", errors="ignore")
    return hashlib.sha256(joined).hexdigest()[:size]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def normalize_text(text: str) -> str:
    text = text.replace("\x00", " ")
    text = re.sub(r"[\t\r\f\v]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ ]{2,}", " ", text)
    return text.strip()


def tokenize(text: str) -> list[str]:
    return [
        tok.lower()
        for tok in TOKEN_RE.findall(text)
        if len(tok) > 1 and tok.lower() not in STOPWORDS
    ]


def split_sentences(text: str) -> list[str]:
    parts: list[str] = []
    for block in re.split(r"\n{2,}", normalize_text(text)):
        parts.extend(SENTENCE_RE.split(block))
    return [p.strip() for p in parts if p.strip()]


def estimate_language(text: str) -> str:
    sample = text[:4000].lower()
    french_hits = sum(
        sample.count(word)
        for word in (" le ", " la ", " des ", " une ", " pour ", " dans ", " avec ")
    )
    english_hits = sum(
        sample.count(word)
        for word in (" the ", " and ", " of ", " for ", " with ", " from ", " risk ")
    )
    if french_hits > english_hits * 1.2:
        return "fr"
    if english_hits > 0:
        return "en"
    return "unknown"


def keyword_scores(texts: Iterable[str], top_k: int = 16) -> list[tuple[str, float]]:
    docs = [tokenize(t) for t in texts]
    if not docs:
        return []
    n_docs = len(docs)
    tf = Counter()
    df = Counter()
    for doc in docs:
        tf.update(doc)
        df.update(set(doc))
    scored: list[tuple[str, float]] = []
    for term, count in tf.items():
        idf = math.log((1 + n_docs) / (1 + df[term])) + 1
        scored.append((term, count * idf))
    scored.sort(key=lambda item: item[1], reverse=True)
    return scored[:top_k]


@dataclass(frozen=True)
class TextChunk:
    content: str
    section_title: str | None
    start_char: int
    end_char: int
    token_count: int


def _nearest_boundary(text: str, start: int, target_end: int, min_end: int) -> int:
    boundaries = ["\n\n", ". ", "? ", "! ", "; ", "\n"]
    best = -1
    for boundary in boundaries:
        idx = text.rfind(boundary, min_end, target_end)
        if idx > best:
            best = idx + len(boundary)
    return best if best > start else target_end


def chunk_text(
    text: str,
    target_chars: int = 2600,
    overlap_chars: int = 350,
) -> list[TextChunk]:
    """Chunk text with overlap and soft section awareness."""

    text = normalize_text(text)
    if not text:
        return []
    if len(text) <= target_chars:
        return [
            TextChunk(
                content=text,
                section_title=infer_section_title(text),
                start_char=0,
                end_char=len(text),
                token_count=len(tokenize(text)),
            )
        ]

    chunks: list[TextChunk] = []
    start = 0
    n = len(text)
    while start < n:
        hard_end = min(n, start + target_chars)
        min_end = min(n, start + int(target_chars * 0.65))
        end = _nearest_boundary(text, start, hard_end, min_end)
        content = text[start:end].strip()
        if content:
            chunks.append(
                TextChunk(
                    content=content,
                    section_title=infer_section_title(content),
                    start_char=start,
                    end_char=end,
                    token_count=len(tokenize(content)),
                )
            )
        if end >= n:
            break
        start = max(0, end - overlap_chars)
    return chunks


def infer_section_title(text: str) -> str | None:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    for line in lines[:8]:
        clean = re.sub(r"\s+", " ", line)
        if 4 <= len(clean) <= 120:
            alpha_ratio = sum(ch.isalpha() for ch in clean) / max(len(clean), 1)
            if alpha_ratio > 0.55 and not clean.endswith("."):
                return clean
    return None


def concise_snippet(text: str, max_chars: int = 420) -> str:
    text = normalize_text(text)
    if len(text) <= max_chars:
        return text
    sentences = split_sentences(text)
    out = ""
    for sentence in sentences:
        if len(out) + len(sentence) + 1 > max_chars:
            break
        out = f"{out} {sentence}".strip()
    if out:
        return out
    return text[: max_chars - 3].rstrip() + "..."

