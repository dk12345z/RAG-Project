"""Embedding backends.

The lab uses a TF-IDF vectorizer as a lightweight, dependency-light stand-in
for a real embedding model (e.g. sentence-transformers or an API-based
embedding endpoint). It has the same interface (`fit`, `embed`) a real
embedding client would have, so it is a drop-in swap: replace
``TfidfEmbedder`` with a client that calls an embeddings API and everything
downstream (index, retriever) keeps working unchanged.

Using TF-IDF here is itself an honest limitation worth calling out: TF-IDF
captures lexical overlap, not semantic similarity. A real embedding model
would retrieve paraphrases that share no words; TF-IDF will not. That gap is
intentionally left visible rather than hidden behind a heavier dependency.
"""
from __future__ import annotations

from typing import Protocol

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer


class Embedder(Protocol):
    """Interface every embedding backend must satisfy."""

    def fit(self, texts: list[str]) -> None: ...

    def embed(self, texts: list[str]) -> np.ndarray: ...


class TfidfEmbedder:
    """TF-IDF based embedder used as the default backend for the lab."""

    def __init__(self, **vectorizer_kwargs) -> None:
        self._vectorizer = TfidfVectorizer(**vectorizer_kwargs)
        self._fitted = False

    def fit(self, texts: list[str]) -> None:
        if not texts:
            raise ValueError("Cannot fit an embedder on an empty corpus")
        self._vectorizer.fit(texts)
        self._fitted = True

    def embed(self, texts: list[str]) -> np.ndarray:
        if not self._fitted:
            raise RuntimeError("Embedder must be fit() before calling embed()")
        matrix = self._vectorizer.transform(texts)
        return matrix.toarray()
