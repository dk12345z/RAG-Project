import pytest

from ragproject.chunking import chunk_text, chunk_documents


def test_chunk_text_covers_full_text():
    text = "a" * 1000
    chunks = chunk_text(text, doc_id="doc", chunk_size=100, chunk_overlap=20)
    assert chunks[0].text.startswith("a")
    assert chunks[-1].metadata["end"] == 1000
    # every position in [0, 1000) must be covered by at least one chunk
    covered = set()
    for c in chunks:
        covered.update(range(c.metadata["start"], c.metadata["end"]))
    assert covered == set(range(1000))


def test_chunk_text_empty_string_returns_no_chunks():
    assert chunk_text("   ", doc_id="doc") == []


def test_chunk_text_rejects_invalid_chunk_size():
    with pytest.raises(ValueError):
        chunk_text("hello world", doc_id="doc", chunk_size=0)


def test_chunk_text_rejects_overlap_gte_chunk_size():
    with pytest.raises(ValueError):
        chunk_text("hello world", doc_id="doc", chunk_size=10, chunk_overlap=10)


def test_chunk_text_ids_are_unique_and_sequential():
    text = "word " * 200
    chunks = chunk_text(text, doc_id="d", chunk_size=50, chunk_overlap=10)
    ids = [c.chunk_id for c in chunks]
    assert len(ids) == len(set(ids))
    assert ids == [f"d::{i}" for i in range(len(ids))]


def test_chunk_documents_reads_markdown_corpus(tmp_path):
    (tmp_path / "one.md").write_text("Hello world. " * 50, encoding="utf-8")
    (tmp_path / "two.md").write_text("Another document. " * 50, encoding="utf-8")
    (tmp_path / "ignored.txt").write_text("should not be picked up", encoding="utf-8")

    chunks = chunk_documents(tmp_path, chunk_size=100, chunk_overlap=10)
    doc_ids = {c.doc_id for c in chunks}
    assert doc_ids == {"one", "two"}
