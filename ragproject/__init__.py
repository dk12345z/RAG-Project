"""ragproject: a small, dependency-light retrieval layer for the context-engineering lab.

Modules:
    chunking   - split documents into retrievable chunks
    embeddings - turn text into vectors (TF-IDF based, swappable)
    index      - in-memory vector index over chunks
    retriever  - top-k similarity search over an index
    schemas    - structured input/output contracts (pydantic)
    prompts    - versioned prompt loader
"""

from .retriever import Retriever
from .index import VectorIndex
from .chunking import chunk_text, chunk_documents

__all__ = ["Retriever", "VectorIndex", "chunk_text", "chunk_documents", "__version__"]

__version__ = "0.1.0"
