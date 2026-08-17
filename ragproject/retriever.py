"""Top-k similarity search over a VectorIndex."""
from __future__ import annotations

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from .index import VectorIndex
from .schemas import RetrievalQuery, RetrievalResult, RetrievedChunk


class Retriever:
    """Retrieves the top-k most similar chunks for a query against an index."""

    def __init__(self, index: VectorIndex, min_score: float = 0.0) -> None:
        """
        Args:
            index: a built VectorIndex to search.
            min_score: minimum cosine similarity a chunk must clear to be
                returned. If no chunk clears the bar, the result is marked
                ``insufficient_context`` instead of returning weak matches.
        """
        self.index = index
        self.min_score = min_score

    def retrieve(self, request: RetrievalQuery) -> RetrievalResult:
        if not self.index.is_built:
            raise RuntimeError("Index has not been built yet; call VectorIndex.build() first")

        query_vector = self.index.embedder.embed([request.query])
        similarities = cosine_similarity(query_vector, self.index.vectors)[0]

        order = np.argsort(similarities)[::-1][: request.top_k]
        candidates = [
            RetrievedChunk(
                doc_id=self.index.chunks[i].doc_id,
                chunk_id=self.index.chunks[i].chunk_id,
                text=self.index.chunks[i].text,
                score=float(similarities[i]),
            )
            for i in order
        ]

        passing = [c for c in candidates if c.score >= self.min_score]
        # A chunk with a score of ~0 carries no real signal even if it
        # technically clears a min_score of 0.0 (the default). Treat an
        # all-noise result the same as an empty one so callers get an
        # honest `insufficient_context` signal instead of a false "OK".
        has_signal = any(c.score > 1e-9 for c in passing)

        return RetrievalResult(
            query=request.query,
            chunks=passing,
            insufficient_context=not has_signal,
            index_built_at=self.index.built_at,
        )
