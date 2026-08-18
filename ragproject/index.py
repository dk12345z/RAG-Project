"""In-memory vector index over a list of chunks.

The index intentionally has no automatic refresh mechanism: it is a
snapshot of whatever chunks it was built from at ``build()`` time. This is
deliberate so the lab can demonstrate the "stale index" failure mode
(labs/break_it.py) by mutating the corpus without calling ``build()`` again.
"""
from __future__ import annotations

import time

import numpy as np

from .chunking import Chunk
from .embeddings import Embedder, TfidfEmbedder


class VectorIndex:
    """A snapshot-based vector index over a set of chunks."""

    def __init__(self, embedder: Embedder | None = None) -> None:
        self.embedder: Embedder = embedder or TfidfEmbedder()
        self.chunks: list[Chunk] = []
        self.vectors: np.ndarray | None = None
        self.built_at: float | None = None

    def build(self, chunks: list[Chunk]) -> None:
        """Fit the embedder and embed every chunk. Replaces any prior index."""
        if not chunks:
            raise ValueError("Cannot build an index from an empty chunk list")
        texts = [c.text for c in chunks]
        self.embedder.fit(texts)
        self.vectors = self.embedder.embed(texts)
        self.chunks = list(chunks)
        self.built_at = time.time()

    @property
    def is_built(self) -> bool:
        return self.vectors is not None and len(self.chunks) > 0

    def __len__(self) -> int:
        return len(self.chunks)
