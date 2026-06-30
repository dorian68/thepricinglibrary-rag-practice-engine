"""Tests for the optional-LLM pipeline + numeric guardrails.

Covered:
- template mode works with no API key (pass-through, no validation metadata);
- a real LLM writer is only invoked when configured;
- lexical fallback and hybrid retrieval both keep the pipeline working;
- the calculation_pack numbers survive a faithful rewrite;
- a tampering/empty LLM output falls back to the template (strict) or is flagged
  (lenient);
- sources/citations are never lost in LLM mode.
"""

from pathlib import Path

from pricinglibrary_rag.embeddings import LocalHashingEmbedding
from pricinglibrary_rag.generation import MaterialGenerator
from pricinglibrary_rag.ingestion import IngestionService
from pricinglibrary_rag.config import Settings
from pricinglibrary_rag.llm import BaseLLM, LocalLLM, TemplateLLM
from pricinglibrary_rag.retrieval import build_retriever
from pricinglibrary_rag.schemas import DocumentMetadata, ExerciseRequest
from pricinglibrary_rag.storage import LocalStore


MARKER = "[TEMPLATE_OUTPUT]"


def _draft_of(prompt: str) -> str:
    return prompt.split(MARKER, 1)[1].strip() if MARKER in prompt else prompt


class FaithfulLLM(LocalLLM):
    """A 'real' writer that preserves the draft verbatim (numbers intact)."""

    name = "fake:faithful"

    def generate(self, prompt: str, *, max_tokens: int = 2200) -> str:
        return "Reformulation pedagogique.\n\n" + _draft_of(prompt)


class TamperLLM(LocalLLM):
    """A writer that drops every number (simulates an LLM changing results)."""

    name = "fake:tamper"

    def generate(self, prompt: str, *, max_tokens: int = 2200) -> str:
        return "Un exercice reformule sans aucune donnee chiffree precise."


class EmptyLLM(LocalLLM):
    name = "fake:empty"

    def generate(self, prompt: str, *, max_tokens: int = 2200) -> str:
        return ""


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


def _ingest(tmp_path: Path):
    source = tmp_path / "options_note.txt"
    source.write_text(
        """
        Vanilla European options are priced with Black-Scholes. Traders watch
        spot, strike, volatility, time to maturity and rates. Delta and vega
        drive the hedge. A call's price rises with volatility and time value.
        """,
        encoding="utf-8",
    )
    settings = _settings(tmp_path)
    store = LocalStore(settings.db_path)
    embeddings = LocalHashingEmbedding(dim=512)
    ingestion = IngestionService(store, embeddings, settings)
    ingestion.ingest_file(
        source, DocumentMetadata(product="option", concepts=["vanilla", "hedging"])
    )
    return store, embeddings


def _request() -> ExerciseRequest:
    return ExerciseRequest(
        free_prompt="Call europeen S=100 K=100 sigma=20% T=1 taux 2%",
        product="option",
        concept="vanilla option",
        require_calculations=True,
    )


def test_base_llm_alias_points_to_abstract_base() -> None:
    assert BaseLLM is LocalLLM
    assert issubclass(TemplateLLM, BaseLLM)


def test_template_mode_works_without_api_key(tmp_path: Path) -> None:
    store, embeddings = _ingest(tmp_path)
    gen = MaterialGenerator(
        build_retriever("hybrid", store, embeddings), TemplateLLM(), store=store
    )
    resp = gen.generate_exercise(_request())
    assert resp.content.strip()
    assert resp.sources  # citations preserved
    # Pass-through template is trusted: no validation step runs.
    assert "validation" not in resp.metadata
    assert resp.metadata["llm"] == "template"


def test_lexical_and_hybrid_retrieval_both_return_hits(tmp_path: Path) -> None:
    store, embeddings = _ingest(tmp_path)
    for mode in ("lexical", "hybrid", "semantic"):
        retr = build_retriever(mode, store, embeddings)
        hits = retr.retrieve("vanilla option delta vega hedge", top_k=3)
        assert hits, f"{mode} retrieval returned no hits"


def test_faithful_llm_output_is_kept_and_numbers_validate(tmp_path: Path) -> None:
    store, embeddings = _ingest(tmp_path)
    gen = MaterialGenerator(
        build_retriever("hybrid", store, embeddings), FaithfulLLM(), store=store
    )
    resp = gen.generate_exercise(_request())
    assert resp.metadata["llm"] == "fake:faithful"
    assert resp.content.startswith("Reformulation pedagogique")
    assert resp.metadata["validation"]["ok"] is True
    assert resp.metadata.get("validation_fallback") is None
    assert resp.sources


def test_tampering_llm_falls_back_to_template_in_strict_mode(tmp_path: Path) -> None:
    store, embeddings = _ingest(tmp_path)
    gen = MaterialGenerator(
        build_retriever("hybrid", store, embeddings),
        TamperLLM(),
        store=store,
        strict_validation=True,
    )
    resp = gen.generate_exercise(_request())
    assert resp.metadata["validation"]["ok"] is False
    assert resp.metadata["validation_fallback"] is True
    # Fallback content is the deterministic draft, NOT the numberless tamper text.
    assert "sans aucune donnee chiffree" not in resp.content
    pack = resp.metadata["calculation_pack"]
    assert pack["steps"], "expected a calculation pack with steps"
    assert resp.sources


def test_tampering_llm_is_only_flagged_in_lenient_mode(tmp_path: Path) -> None:
    store, embeddings = _ingest(tmp_path)
    gen = MaterialGenerator(
        build_retriever("hybrid", store, embeddings),
        TamperLLM(),
        store=store,
        strict_validation=False,
    )
    resp = gen.generate_exercise(_request())
    assert resp.metadata["validation"]["ok"] is False
    assert resp.metadata.get("validation_fallback") is None
    # Lenient: the (flagged) LLM text is kept as-is.
    assert "sans aucune donnee chiffree" in resp.content


def test_empty_llm_output_falls_back(tmp_path: Path) -> None:
    store, embeddings = _ingest(tmp_path)
    gen = MaterialGenerator(
        build_retriever("hybrid", store, embeddings),
        EmptyLLM(),
        store=store,
        strict_validation=True,
    )
    resp = gen.generate_exercise(_request())
    assert resp.metadata["validation"]["ok"] is False
    assert resp.metadata["validation_fallback"] is True
    assert resp.content.strip()  # not empty — restored from template
