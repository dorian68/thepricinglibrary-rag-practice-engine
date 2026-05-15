from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


Difficulty = Literal["beginner", "intermediate", "advanced", "expert"]
ExerciseFormat = Literal[
    "case_study",
    "quantitative_problem",
    "trading_decision",
    "risk_management",
    "mcq",
    "mixed",
]


class DocumentMetadata(BaseModel):
    title: str | None = None
    source: str | None = None
    source_url: str | None = None
    author: str | None = None
    year: int | None = None
    asset_class: str | None = None
    product: str | None = None
    concepts: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    language: str | None = None
    extra: dict[str, Any] = Field(default_factory=dict)


class IngestRequest(BaseModel):
    path: str
    metadata: DocumentMetadata = Field(default_factory=DocumentMetadata)
    recursive: bool = False
    glob: str = "*.pdf"
    force: bool = False


class IngestResult(BaseModel):
    document_id: str
    path: str
    status: str
    chunks_inserted: int = 0
    message: str | None = None


class SearchRequest(BaseModel):
    query: str
    top_k: int = 8
    product: str | None = None
    concept: str | None = None
    asset_class: str | None = None
    tags: list[str] = Field(default_factory=list)
    include_chunks: bool = True


class SourceRef(BaseModel):
    document_id: str
    chunk_id: str
    title: str | None = None
    source: str | None = None
    chunk_index: int
    score: float
    vector_score: float
    lexical_score: float
    snippet: str


class SearchResponse(BaseModel):
    query: str
    results: list[SourceRef]


class ExerciseRequest(BaseModel):
    topic: str | None = None
    product: str | None = None
    concept: str | None = None
    free_prompt: str | None = None
    difficulty: Difficulty = "intermediate"
    exercise_format: ExerciseFormat = "mixed"
    target_audience: str = "market finance learners"
    number_of_questions: int = 5
    require_calculations: bool = True
    top_k: int = 8
    language: Literal["fr", "en"] = "fr"


class CourseRequest(BaseModel):
    topic: str
    product: str | None = None
    concepts: list[str] = Field(default_factory=list)
    level: Difficulty = "intermediate"
    duration_minutes: int = 90
    module_count: int = 4
    target_audience: str = "learners who want to practice market finance"
    top_k: int = 10
    language: Literal["fr", "en"] = "fr"


class MaterialPackRequest(BaseModel):
    topic: str
    product: str | None = None
    concepts: list[str] = Field(default_factory=list)
    level: Difficulty = "intermediate"
    duration_minutes: int = 120
    exercise_count: int = 3
    language: Literal["fr", "en"] = "fr"


class GenerationResponse(BaseModel):
    kind: str
    title: str
    content: str
    sources: list[SourceRef]
    metadata: dict[str, Any] = Field(default_factory=dict)

