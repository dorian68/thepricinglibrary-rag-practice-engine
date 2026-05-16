from pathlib import Path

from pricinglibrary_rag.config import Settings
from pricinglibrary_rag.embeddings import LocalHashingEmbedding
from pricinglibrary_rag.generation import MaterialGenerator
from pricinglibrary_rag.ingestion import IngestionService
from pricinglibrary_rag.llm import TemplateLLM
from pricinglibrary_rag.retrieval import LocalRetriever
from pricinglibrary_rag.schemas import CourseRequest, DocumentMetadata, ExerciseRequest
from pricinglibrary_rag.storage import LocalStore


def _settings(tmp_path: Path) -> Settings:
    return Settings(
        data_dir=tmp_path,
        db_path=tmp_path / "rag.sqlite3",
        embedding_backend="local-hashing",
        embedding_dim=512,
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


def test_ingest_search_and_generate(tmp_path: Path) -> None:
    source = tmp_path / "options_note.txt"
    source.write_text(
        """
        Barrier options are path-dependent derivatives. A knock-out option ceases
        to exist if the underlying touches a predefined barrier. Traders focus on
        spot, volatility, time to maturity, rates and barrier distance. Practical
        hedging requires monitoring gamma and gap risk near the barrier.
        """,
        encoding="utf-8",
    )
    settings = _settings(tmp_path)
    store = LocalStore(settings.db_path)
    embeddings = LocalHashingEmbedding(dim=512)
    ingestion = IngestionService(store, embeddings, settings)
    result = ingestion.ingest_file(
        source,
        DocumentMetadata(product="option", concepts=["barrier", "hedging"]),
    )
    assert result.status == "ingested"
    assert result.chunks_inserted >= 1

    retriever = LocalRetriever(store, embeddings)
    hits = retriever.retrieve("barrier option hedging gamma", top_k=3)
    assert hits
    assert "Barrier options" in hits[0].chunk.content

    generator = MaterialGenerator(retriever, TemplateLLM(), store=store)
    exercise = generator.generate_exercise(
        ExerciseRequest(product="option", concept="barrier option")
    )
    assert "Cas pratique" in exercise.content
    assert exercise.sources

    course = generator.generate_course(CourseRequest(topic="Barrier options"))
    assert "Module pratique" in course.content
    assert course.sources
