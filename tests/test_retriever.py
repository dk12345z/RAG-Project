import pytest

from ragproject.chunking import chunk_text
from ragproject.index import VectorIndex
from ragproject.retriever import Retriever
from ragproject.schemas import RetrievalQuery


CHUNKS = (
    chunk_text("Cats are small domesticated carnivorous mammals.", doc_id="cats", chunk_size=200)
    + chunk_text("Rockets use combustion to generate thrust for spaceflight.", doc_id="rockets", chunk_size=200)
    + chunk_text("Kittens are baby cats and are also small mammals.", doc_id="kittens", chunk_size=200)
)


def build_retriever(min_score: float = 0.0) -> Retriever:
    index = VectorIndex()
    index.build(list(CHUNKS))
    return Retriever(index, min_score=min_score)


def test_retriever_returns_top_k_ordered_by_score():
    retriever = build_retriever()
    result = retriever.retrieve(RetrievalQuery(query="small mammals", top_k=2))
    assert len(result.chunks) == 2
    scores = [c.score for c in result.chunks]
    assert scores == sorted(scores, reverse=True)


def test_retriever_relevant_chunk_ranks_above_unrelated():
    retriever = build_retriever()
    result = retriever.retrieve(RetrievalQuery(query="domesticated cats", top_k=3))
    doc_ids = [c.doc_id for c in result.chunks]
    assert doc_ids[0] in {"cats", "kittens"}


def test_retriever_marks_insufficient_context_when_min_score_not_met():
    retriever = build_retriever(min_score=0.99)
    result = retriever.retrieve(RetrievalQuery(query="small mammals", top_k=3))
    assert result.insufficient_context is True
    assert result.chunks == []


def test_retriever_raises_if_index_not_built():
    index = VectorIndex()
    retriever = Retriever(index)
    with pytest.raises(RuntimeError):
        retriever.retrieve(RetrievalQuery(query="anything"))


def test_retriever_result_includes_index_built_at():
    retriever = build_retriever()
    result = retriever.retrieve(RetrievalQuery(query="rockets", top_k=1))
    assert result.index_built_at is not None
    assert result.index_built_at == retriever.index.built_at
