from __future__ import annotations

from dataclasses import dataclass

from .billing import BillingService
from .config import Settings
from .embeddings import EmbeddingBackend, build_embedding_backend
from .evaluation import ProductEvaluator
from .generation import MaterialGenerator
from .ingestion import IngestionService
from .llm import LocalLLM, build_llm
from .retrieval import BaseRetriever, build_retriever
from .storage import LocalStore


@dataclass
class Services:
    settings: Settings
    store: LocalStore
    embeddings: EmbeddingBackend
    retriever: BaseRetriever
    ingestion: IngestionService
    generator: MaterialGenerator
    llm: LocalLLM
    evaluator: ProductEvaluator
    billing: BillingService


def build_services(settings: Settings | None = None) -> Services:
    settings = settings or Settings.from_env()
    settings.ensure_dirs()
    store = LocalStore(settings.db_path)
    embeddings = build_embedding_backend(
        backend_name=settings.embedding_backend,
        dim=settings.embedding_dim,
        sentence_transformer_model=settings.sentence_transformer_model,
        openai_api_key=settings.openai_api_key,
    )
    retriever = build_retriever(settings.retrieval_mode, store, embeddings)
    ingestion = IngestionService(store, embeddings, settings)
    llm = build_llm(
        settings.llm_provider,
        openai_api_key=settings.openai_api_key,
        openai_model=settings.openai_model,
        openai_base_url=settings.openai_base_url,
        openai_timeout_seconds=settings.openai_timeout_seconds,
        openai_max_retries=settings.openai_max_retries,
        ollama_url=settings.ollama_url,
        ollama_model=settings.ollama_model,
        transformers_model_path=settings.transformers_model_path,
    )
    generator = MaterialGenerator(
        retriever, llm, store=store, strict_validation=settings.strict_validation
    )
    evaluator = ProductEvaluator()
    billing = BillingService(settings, store)
    return Services(
        settings=settings,
        store=store,
        embeddings=embeddings,
        retriever=retriever,
        ingestion=ingestion,
        generator=generator,
        llm=llm,
        evaluator=evaluator,
        billing=billing,
    )
