from __future__ import annotations

from dataclasses import dataclass

from .config import Settings
from .embeddings import EmbeddingBackend, build_embedding_backend
from .generation import MaterialGenerator
from .ingestion import IngestionService
from .llm import LocalLLM, build_llm
from .retrieval import LocalRetriever
from .storage import LocalStore


@dataclass
class Services:
    settings: Settings
    store: LocalStore
    embeddings: EmbeddingBackend
    retriever: LocalRetriever
    ingestion: IngestionService
    generator: MaterialGenerator
    llm: LocalLLM


def build_services(settings: Settings | None = None) -> Services:
    settings = settings or Settings.from_env()
    settings.ensure_dirs()
    store = LocalStore(settings.db_path)
    embeddings = build_embedding_backend(
        backend_name=settings.embedding_backend,
        dim=settings.embedding_dim,
        sentence_transformer_model=settings.sentence_transformer_model,
    )
    retriever = LocalRetriever(store, embeddings)
    ingestion = IngestionService(store, embeddings, settings)
    llm = build_llm(
        settings.llm_provider,
        openai_api_key=settings.openai_api_key,
        openai_model=settings.openai_model,
        openai_base_url=settings.openai_base_url,
        ollama_url=settings.ollama_url,
        ollama_model=settings.ollama_model,
        transformers_model_path=settings.transformers_model_path,
    )
    generator = MaterialGenerator(retriever, llm, store=store)
    return Services(
        settings=settings,
        store=store,
        embeddings=embeddings,
        retriever=retriever,
        ingestion=ingestion,
        generator=generator,
        llm=llm,
    )
