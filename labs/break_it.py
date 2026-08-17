"""Lab: build a retrieval layer over a real corpus, then break it deliberately.

Run:
    python labs/break_it.py

This script builds a baseline retriever over ``corpus/`` and then reproduces
three failure modes on purpose:

1. Bad chunking (too small / too large chunk sizes)
2. Wrong top-k (too low / too high)
3. Stale index (corpus mutated after the index was built)

Each experiment prints its result and the observed failure signature. See
labs/FAILURE_SIGNATURES.md for the write-up.
"""
from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from ragproject.chunking import chunk_documents
from ragproject.index import VectorIndex
from ragproject.retriever import Retriever
from ragproject.schemas import RetrievalQuery

CORPUS_DIR = Path(__file__).resolve().parent.parent / "corpus"


def section(title: str) -> None:
    print("\n" + "=" * 72)
    print(title)
    print("=" * 72)


def run_query(retriever: Retriever, query: str, top_k: int = 3) -> None:
    result = retriever.retrieve(RetrievalQuery(query=query, top_k=top_k))
    print(f"query: {query!r}  top_k={top_k}")
    if result.insufficient_context:
        print("  -> insufficient_context = True (no chunk cleared min_score)")
    for c in result.chunks:
        preview = c.text[:90].replace("\n", " ")
        print(f"  [{c.score:.3f}] {c.chunk_id}: {preview!r}")


def baseline() -> None:
    section("BASELINE: reasonable chunk size, reasonable top_k")
    chunks = chunk_documents(CORPUS_DIR, chunk_size=400, chunk_overlap=50)
    index = VectorIndex()
    index.build(chunks)
    retriever = Retriever(index, min_score=0.05)
    run_query(retriever, "What is a stale index and why is it dangerous?")


def bad_chunking_too_small() -> None:
    section("FAILURE 1a: chunk size far too small (20 chars, no overlap)")
    chunks = chunk_documents(CORPUS_DIR, chunk_size=20, chunk_overlap=0)
    index = VectorIndex()
    index.build(chunks)
    retriever = Retriever(index, min_score=0.05)
    run_query(retriever, "What is a stale index and why is it dangerous?")
    print(
        "Signature: chunks are sentence fragments; the concept 'stale index' is split "
        "across many tiny chunks so no single chunk scores highly, and matches are "
        "driven by coincidental keyword overlap rather than the actual explanation."
    )


def bad_chunking_too_large() -> None:
    section("FAILURE 1b: chunk size far too large (whole-document chunks)")
    chunks = chunk_documents(CORPUS_DIR, chunk_size=5000, chunk_overlap=0)
    index = VectorIndex()
    index.build(chunks)
    retriever = Retriever(index, min_score=0.05)
    run_query(retriever, "What is a stale index and why is it dangerous?")
    print(
        "Signature: each chunk is an entire document, so the one relevant paragraph is "
        "diluted by every other topic in that document. Similarity scores compress "
        "toward the mean and the top match is often the whole retrieval-and-rag-limits "
        "doc rather than the specific stale-index paragraph, wasting context budget."
    )


def wrong_top_k_too_low() -> None:
    section("FAILURE 2a: top_k too low (top_k=1) for a multi-part answer")
    chunks = chunk_documents(CORPUS_DIR, chunk_size=250, chunk_overlap=0)
    index = VectorIndex()
    index.build(chunks)
    retriever = Retriever(index, min_score=0.0)
    run_query(
        retriever,
        "Compare chunking, top-k, and stale indexes as RAG failure modes",
        top_k=1,
    )
    print(
        "Signature: the query spans three sub-topics (chunking, top-k, stale indexes) "
        "that live in different chunks; top_k=1 returns only the single best-matching "
        "chunk and silently drops the other two, so the generated answer will look "
        "confident but be incomplete with no error surfaced."
    )


def wrong_top_k_too_high() -> None:
    section("FAILURE 2b: top_k too high (top_k=20) floods context with noise")
    chunks = chunk_documents(CORPUS_DIR, chunk_size=250, chunk_overlap=0)
    index = VectorIndex()
    index.build(chunks)
    retriever = Retriever(index, min_score=0.0)
    run_query(retriever, "What is chunking?", top_k=20)
    print(
        "Signature: with only a handful of documents, top_k=20 returns every chunk in "
        "the corpus regardless of relevance (scores trail off near 0), including chunks "
        "about prompt versioning and structured output that have nothing to do with the "
        "question. Downstream generation now has to sort signal from noise itself."
    )


def stale_index() -> None:
    section("FAILURE 3: stale index after the corpus changes")
    with tempfile.TemporaryDirectory() as tmp:
        tmp_corpus = Path(tmp)
        shutil.copytree(CORPUS_DIR, tmp_corpus, dirs_exist_ok=True)

        chunks = chunk_documents(tmp_corpus, chunk_size=400, chunk_overlap=50)
        index = VectorIndex()
        index.build(chunks)
        retriever = Retriever(index, min_score=0.05)
        print(f"Index built at {index.built_at} over {len(index)} chunks.")

        # Mutate the corpus AFTER the index was built, without rebuilding.
        new_doc = tmp_corpus / "new-policy.md"
        new_doc.write_text(
            "# Retention Policy Update\n\nAs of this revision, retrieval indexes must be "
            "rebuilt automatically whenever the corpus directory changes, via a file-watch "
            "hook or a scheduled reindex job.",
            encoding="utf-8",
        )
        (tmp_corpus / "context-windows.md").unlink()

        run_query(retriever, "What is the retention policy for rebuilding indexes?")
        print(
            "Signature: the corpus on disk changed (a doc was added, another removed) but "
            "index.built_at and index.chunks were never refreshed. The retriever returns "
            "confident-looking, non-empty results from the *old* snapshot -- it has no "
            "way to know the new-policy.md content exists, and no error is raised because "
            "nothing in the index/retriever is actually broken. This is why 'insufficient_"
            "context' alone is not a safety net: the index can be wrong while looking healthy."
        )


if __name__ == "__main__":
    baseline()
    bad_chunking_too_small()
    bad_chunking_too_large()
    wrong_top_k_too_low()
    wrong_top_k_too_high()
    stale_index()
