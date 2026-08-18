# RAG-Project

A small, hands-on lab for the "context engineering" week of the curriculum:
context windows as a scarce resource, structured input/output, retrieval
(embeddings + chunking), and prompt versioning.

Most agent failures are context failures, not model failures. This project
builds a minimal retrieval layer over a real corpus of docs, then breaks it
deliberately (bad chunking, wrong top-k, a stale index) so those failure
modes are visible and documented instead of theoretical.

## Layout

- `ragproject/` — the retrieval layer:
  - `chunking.py` — split documents into overlapping chunks
  - `embeddings.py` — TF-IDF embedder (a swappable, dependency-light stand-in
    for a real embedding model/API)
  - `index.py` — in-memory vector index, built as an explicit snapshot
  - `retriever.py` — top-k cosine-similarity search with a `min_score` floor
  - `schemas.py` — structured input/output contracts (pydantic models with
    JSON schema export)
  - `prompts.py` — loads versioned prompt files from `prompts/`
  - `cli.py` — `python -m ragproject.cli "your question" --top-k 3`
- `corpus/` — the sample corpus this lab retrieves over (docs about context
  windows, structured I/O, retrieval limits, and prompt versioning)
- `prompts/` — versioned prompt templates (`answer_v1.md`, `answer_v2.md`)
  plus `CHANGELOG.md` explaining why each version changed
- `labs/break_it.py` — builds a baseline retriever, then deliberately
  reproduces bad chunking, wrong top-k, and a stale index
- `labs/FAILURE_SIGNATURES.md` — the write-up: what broke, the observable
  signature of each failure, and the fix
- `tests/` — pytest suite for chunking, retrieval, schemas, and prompts

## Setup

```bash
pip install -e .
```

## Usage

```bash
# Query the retrieval layer
python -m ragproject.cli "What is a stale index and why is it dangerous?"

# Run the "break it deliberately" lab
python labs/break_it.py

# Run the tests
pytest -q
```
