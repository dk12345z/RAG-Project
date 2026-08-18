"""Command-line entry point for querying the retrieval layer.

Usage:
    python -m ragproject.cli "What is a stale index?" --top-k 3
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .chunking import chunk_documents
from .index import VectorIndex
from .retriever import Retriever
from .schemas import RetrievalQuery

DEFAULT_CORPUS = Path(__file__).resolve().parent.parent / "corpus"


def build_default_retriever(
    corpus_dir: Path = DEFAULT_CORPUS,
    chunk_size: int = 400,
    chunk_overlap: int = 50,
    min_score: float = 0.05,
) -> Retriever:
    chunks = chunk_documents(corpus_dir, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    index = VectorIndex()
    index.build(chunks)
    return Retriever(index, min_score=min_score)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Query the lab's retrieval layer.")
    parser.add_argument("query", help="Natural-language question")
    parser.add_argument("--top-k", type=int, default=3, help="Number of chunks to retrieve")
    parser.add_argument(
        "--corpus", type=Path, default=DEFAULT_CORPUS, help="Directory of .md docs to index"
    )
    parser.add_argument("--chunk-size", type=int, default=400)
    parser.add_argument("--chunk-overlap", type=int, default=50)
    parser.add_argument("--min-score", type=float, default=0.05)
    args = parser.parse_args(argv)

    retriever = build_default_retriever(
        corpus_dir=args.corpus,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
        min_score=args.min_score,
    )
    request = RetrievalQuery(query=args.query, top_k=args.top_k)
    result = retriever.retrieve(request)
    print(json.dumps(result.model_dump(), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
