"""Chunking strategies for splitting documents into retrievable pieces.

Chunking is deliberately kept simple and parameterized so the lab can
demonstrate how chunk size and overlap change retrieval quality (see
labs/break_it.py).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Chunk:
    """A single retrievable unit of text."""

    doc_id: str
    chunk_id: str
    text: str
    metadata: dict = field(default_factory=dict)


def chunk_text(
    text: str,
    doc_id: str,
    chunk_size: int = 400,
    chunk_overlap: int = 50,
) -> list[Chunk]:
    """Split ``text`` into overlapping fixed-size chunks (measured in characters).

    Args:
        text: the raw document text.
        doc_id: an identifier for the source document.
        chunk_size: target number of characters per chunk. Must be > 0.
        chunk_overlap: number of characters shared between consecutive
            chunks. Must be >= 0 and < chunk_size.

    Returns:
        A list of Chunk objects covering the full text.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be a positive integer")
    if chunk_overlap < 0 or chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must satisfy 0 <= chunk_overlap < chunk_size")

    text = text.strip()
    if not text:
        return []

    chunks: list[Chunk] = []
    step = chunk_size - chunk_overlap
    start = 0
    index = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        raw = text[start:end]
        piece = raw.strip()
        if piece:
            # Report the bounds of the stripped text within the original
            # string, not the raw pre-strip slice, so metadata["start"] and
            # metadata["end"] always describe exactly what's in `text`.
            leading_ws = len(raw) - len(raw.lstrip())
            piece_start = start + leading_ws
            piece_end = piece_start + len(piece)
            chunks.append(
                Chunk(
                    doc_id=doc_id,
                    chunk_id=f"{doc_id}::{index}",
                    text=piece,
                    metadata={"start": piece_start, "end": piece_end},
                )
            )
            index += 1
        if end == len(text):
            break
        start += step
    return chunks


def chunk_documents(
    corpus_dir: str | Path,
    chunk_size: int = 400,
    chunk_overlap: int = 50,
    glob: str = "*.md",
) -> list[Chunk]:
    """Load every file matching ``glob`` under ``corpus_dir`` and chunk it.

    This is the entry point the retriever/index use to build a corpus from a
    real directory of docs (team wiki export, paper set, codebase, etc.).
    """
    corpus_dir = Path(corpus_dir)
    all_chunks: list[Chunk] = []
    for path in sorted(corpus_dir.glob(glob)):
        text = path.read_text(encoding="utf-8")
        doc_id = path.stem
        all_chunks.extend(
            chunk_text(text, doc_id=doc_id, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        )
    return all_chunks
