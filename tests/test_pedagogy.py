from pathlib import Path

from pricinglibrary_rag.config import Settings
from pricinglibrary_rag.embeddings import LocalHashingEmbedding
from pricinglibrary_rag.ingestion import IngestionService
from pricinglibrary_rag.pedagogy import (
    CONTENT_TYPES,
    classify_chunk,
    detect_pedagogical_gaps,
    infer_document_theme,
    stage_covered,
    summarize_pedagogy,
)
from pricinglibrary_rag.schemas import DocumentMetadata
from pricinglibrary_rag.storage import LocalStore


DEFINITION = (
    "A barrier option is defined as an exotic option whose payoff depends on whether "
    "the underlying asset reaches a predetermined barrier level during the option's "
    "life. We define a knock-out option as a barrier option that ceases to exist if "
    "the barrier is touched, and a knock-in option as one that only becomes active "
    "once the barrier has been touched. By definition the knock-out price is strictly "
    "lower than the equivalent vanilla option, because the contract can disappear "
    "before maturity. This barrier feature is what makes the instrument cheaper and "
    "is the reason desks use barriers to reduce premium for directional clients."
)

FORMULA = (
    "Under Black-Scholes the down-and-out call price satisfies the in-out parity "
    "C = C_out + C_in. The reflection term scales as (H / S)^(2 r / sigma^2 - 1) and "
    "d1 = (log(S / K) + (r + sigma^2 / 2) T) / (sigma sqrt(T)). The delta equals "
    "N(d1) = 0.62 and the value V = 4.21 follows from substitution into the formula."
)

EXERCISE = (
    "Exercise: a trader is short a down-and-out call with the barrier at 1.0000 and "
    "spot at 1.0080. Calculate the delta exposure and show that it becomes unstable "
    "near the barrier. Determine the hedge action and prove that a delta hedge fails "
    "to control gap risk within 20 pips of the barrier."
)

NOISE_TOC = (
    "Table of contents\n1. Introduction 1\n2. Options 4\n2.1 Calls 5\n2.2 Puts 7\n"
    "3. Greeks 12\n4. Barriers 18\n5. References 220\nIndex 230\n"
)


def test_classify_definition():
    p = classify_chunk(DEFINITION)
    assert p.contains_definition is True
    assert p.content_type in CONTENT_TYPES
    assert p.pedagogical_value > 35
    assert p.usable_for_course is True


def test_classify_formula_presence():
    p = classify_chunk(FORMULA)
    assert p.contains_formula is True
    assert p.pedagogical_value > 35


def test_classify_exercise():
    p = classify_chunk(EXERCISE)
    assert p.contains_exercise is True


def test_noise_is_low_quality_and_unusable():
    p = classify_chunk(NOISE_TOC)
    assert p.quality_score < 60
    assert p.usable_for_course is False


def test_summarize_and_gaps():
    items = [classify_chunk(t).to_metadata() for t in (DEFINITION, FORMULA, EXERCISE)]
    summary = summarize_pedagogy(items)
    assert summary["total"] == 3
    assert summary["definitions"] >= 1
    assert summary["formulas"] >= 1
    assert summary["exercises"] >= 1

    gaps = detect_pedagogical_gaps(items)
    # definition + formula + example/exercise present -> core covered enough
    assert "definition" in gaps["present"]
    assert gaps["status"] in {"usable", "partially_usable"}


def test_gaps_flags_missing_core_when_empty():
    gaps = detect_pedagogical_gaps([])
    assert gaps["status"] == "not_usable"
    assert "definition" in gaps["missing"]


def test_stage_covered():
    ped = classify_chunk(DEFINITION).to_metadata()
    assert stage_covered(ped, "definition") is True
    assert stage_covered(ped, "exercise") is False
    assert stage_covered({"content_type": "summary", "content_types": ["summary"]}, "summary")


def test_infer_document_theme():
    rates = infer_document_theme(
        "This book covers interest rate swaps, DV01, the yield curve and "
        "bootstrapping of discount factors for fixed income desks.",
        title="Interest Rate Derivatives Explained",
    )
    assert rates["theme"] == "Rates & Fixed Income"
    assert rates["asset_class"] == "rates"

    vol = infer_document_theme(
        "Implied volatility, the smile, skew and barrier option greeks under "
        "the Black-Scholes model.",
        title="Volatility and Options",
    )
    assert vol["theme"] == "Derivatives & Volatility"


def _settings(tmp_path: Path) -> Settings:
    return Settings(
        data_dir=tmp_path,
        db_path=tmp_path / "rag.sqlite3",
        embedding_backend="local-hashing",
        embedding_dim=256,
        sentence_transformer_model=None,
        llm_provider="template",
        openai_api_key=None,
        openai_model="gpt-4o-mini",
        openai_base_url=None,
        openai_timeout_seconds=90,
        openai_max_retries=1,
        ollama_url="http://localhost:11434",
        ollama_model="dummy",
        transformers_model_path=None,
        chunk_target_chars=700,
        chunk_overlap_chars=80,
        max_context_chunks=6,
    )


def test_ingestion_persists_pedagogy_columns_and_stats(tmp_path: Path):
    source = tmp_path / "barrier.md"
    source.write_text(DEFINITION + "\n\n" + FORMULA, encoding="utf-8")
    settings = _settings(tmp_path)
    store = LocalStore(settings.db_path)
    embeddings = LocalHashingEmbedding(dim=256)
    ingestion = IngestionService(store, embeddings, settings)

    result = ingestion.ingest_file(source, DocumentMetadata(product="option"))
    assert result.status == "ingested"

    chunks = store.iter_chunks()
    assert chunks
    assert all(c.content_type is not None for c in chunks)
    assert all((c.metadata or {}).get("pedagogy") for c in chunks)

    stats = store.pedagogy_stats()
    assert stats["chunks"] == len(chunks)
    assert stats["classified"] == len(chunks)
    assert stats["unclassified"] == 0
    assert 0 <= stats["average_pedagogical_value"] <= 100


def test_backfill_pedagogy_updates_legacy_chunks(tmp_path: Path):
    settings = _settings(tmp_path)
    store = LocalStore(settings.db_path)
    embeddings = LocalHashingEmbedding(dim=256)
    ingestion = IngestionService(store, embeddings, settings)
    source = tmp_path / "note.md"
    source.write_text(DEFINITION, encoding="utf-8")
    ingestion.ingest_file(source, DocumentMetadata(product="option"))

    # Simulate legacy chunks ingested before pedagogical metadata existed.
    with store.connect() as conn:
        conn.execute(
            "UPDATE chunks SET content_type = NULL, pedagogical_value = NULL, "
            "quality_score = NULL, usable_for_course = NULL"
        )
    assert store.pedagogy_stats()["unclassified"] >= 1

    updated = store.backfill_pedagogy(
        lambda content, section_title: classify_chunk(content, section_title=section_title)
    )
    assert updated >= 1
    assert store.pedagogy_stats()["unclassified"] == 0
