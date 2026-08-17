"""Structured input/output contracts for the retrieval layer.

Using pydantic models (which export a JSON schema via ``model_json_schema``)
instead of loose dicts means malformed queries/results fail validation
immediately and explicitly, instead of propagating as silent bugs downstream.
"""
from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class RetrievalQuery(BaseModel):
    """Structured request into the retrieval layer."""

    query: str = Field(..., min_length=1, description="The user's natural-language question")
    top_k: int = Field(default=3, ge=1, le=50, description="Number of chunks to retrieve")

    @field_validator("query")
    @classmethod
    def query_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("query must not be blank")
        return value


class RetrievedChunk(BaseModel):
    """A single scored chunk returned by the retriever."""

    doc_id: str
    chunk_id: str
    text: str
    score: float = Field(..., ge=-1.0, le=1.0)


class RetrievalResult(BaseModel):
    """Structured response from the retrieval layer.

    ``insufficient_context`` is the explicit escape hatch: if no chunk clears
    a minimum relevance bar, the retriever sets this to True instead of
    forcing low-quality chunks into the response.
    """

    query: str
    chunks: list[RetrievedChunk] = Field(default_factory=list)
    insufficient_context: bool = False
    index_built_at: float | None = None
