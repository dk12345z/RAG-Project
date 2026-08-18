import pytest
from pydantic import ValidationError

from ragproject.schemas import RetrievalQuery, RetrievalResult, RetrievedChunk


def test_retrieval_query_rejects_blank_query():
    with pytest.raises(ValidationError):
        RetrievalQuery(query="   ")


def test_retrieval_query_rejects_top_k_out_of_range():
    with pytest.raises(ValidationError):
        RetrievalQuery(query="hi", top_k=0)
    with pytest.raises(ValidationError):
        RetrievalQuery(query="hi", top_k=51)


def test_retrieval_query_defaults():
    q = RetrievalQuery(query="hi")
    assert q.top_k == 3


def test_retrieved_chunk_rejects_score_out_of_range():
    with pytest.raises(ValidationError):
        RetrievedChunk(doc_id="d", chunk_id="d::0", text="x", score=1.5)


def test_retrieval_result_defaults_to_empty_chunks_and_not_insufficient():
    result = RetrievalResult(query="hi")
    assert result.chunks == []
    assert result.insufficient_context is False


def test_retrieval_result_json_schema_has_expected_fields():
    schema = RetrievalResult.model_json_schema()
    assert set(schema["properties"]) >= {
        "query",
        "chunks",
        "insufficient_context",
        "index_built_at",
    }
