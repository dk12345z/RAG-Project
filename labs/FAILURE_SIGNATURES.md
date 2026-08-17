# Failure Signatures: Breaking the Retrieval Layer on Purpose

This is the write-up companion to `labs/break_it.py`. Run that script to
reproduce every result below against the sample corpus in `corpus/`.

Each entry follows the same shape: **what we changed**, **what happened**,
**the signature that tells you this is the cause**, and **the fix**.

## 1. Bad chunking

### 1a. Chunks far too small (20 characters, no overlap)

- **What we changed:** `chunk_size=20, chunk_overlap=0` instead of the
  baseline `chunk_size=400, chunk_overlap=50`.
- **What happened:** the top results for "What is a stale index and why is
  it dangerous?" were fragments like `"## Stale indexes"` and
  `"is deterministic."` — headings and half-sentences, not the actual
  explanation of the concept.
- **Signature:** retrieved chunks are grammatically incomplete fragments;
  similarity scores are driven by a single shared word or heading rather than
  topical overlap; the answer a model would generate from these chunks would
  either be a non-answer or a confident guess stitched from noise.
- **Fix:** increase chunk size to at least a paragraph's worth of text (a
  few hundred characters/tokens), and add overlap so a concept split across
  a chunk boundary still appears whole in at least one chunk.

### 1b. Chunks far too large (whole documents, `chunk_size=5000`)

- **What we changed:** each chunk became an entire document.
- **What happened:** the top match for the same stale-index question was
  the *whole* `prompt-versioning.md` document, not the stale-index paragraph
  in `retrieval-and-rag-limits.md` (which did rank, but with a lower score
  than an unrelated document).
- **Signature:** similarity scores compress toward a narrow band (all
  results in the 0.14-0.19 range); the single relevant paragraph is
  outranked by irrelevant documents because it's diluted by everything else
  in its own document; retrieved chunks are too large to fit multiple in a
  context budget, so you effectively get top-1 behavior even at top_k=3.
- **Fix:** cap chunk size to roughly a semantic unit (a section or a few
  paragraphs), not a whole document. If documents are naturally short,
  chunk by heading/section rather than a raw character count.

## 2. Wrong top-k

### 2a. top_k too low (`top_k=1`) for a multi-part question

- **What we changed:** asked a question that spans three sub-topics
  (chunking, top-k, stale indexes) with `top_k=1`.
- **What happened:** only one chunk about top-k came back; the chunking and
  stale-index sub-topics were silently dropped.
- **Signature:** the retrieved set answers only part of a compound
  question; there is no error or warning — the system looks like it worked,
  it just returned an incomplete basis for the answer. This is the most
  dangerous failure signature because nothing looks wrong.
- **Fix:** raise top_k for compound/broad questions, or decompose the query
  into sub-queries and retrieve per sub-query, merging results.

### 2b. top_k too high (`top_k=20`) on a 4-document corpus

- **What we changed:** requested 20 chunks when only ~15 exist in total.
- **What happened:** the result included chunks with a similarity score of
  `0.000` — completely unrelated content (prompt-versioning and
  structured-io chunks) returned alongside genuinely relevant ones for
  "What is chunking?".
- **Signature:** the tail of the returned list has near-zero or zero
  scores; noise chunks about unrelated topics are present; context budget is
  spent on chunks that provide no signal, increasing the chance the
  downstream model anchors on the wrong one.
- **Fix:** set top_k relative to corpus size and always apply a `min_score`
  floor (see `Retriever(min_score=...)`) so garbage below a relevance
  threshold is dropped instead of padded in.

## 3. Stale index

- **What we changed:** built the index over a corpus snapshot, then --
  without rebuilding -- deleted `context-windows.md` and added a new
  `new-policy.md` describing an (fictional) auto-reindexing policy.
- **What happened:** querying "What is the retention policy for rebuilding
  indexes?" returned confident, non-empty, plausible-looking chunks from
  `prompt-versioning.md` and `retrieval-and-rag-limits.md` — no chunk from
  `new-policy.md` was retrieved (it doesn't exist in the index), and no
  error was raised anywhere.
- **Signature:** this is the quietest failure of the three. `index.is_built`
  is `True`, `index.built_at` is a real timestamp, `insufficient_context` is
  `False` — every health signal says the system is fine. The only tell is
  that `index.built_at` predates the last modification time of the corpus
  directory, which nothing in the retriever checks automatically.
- **Fix:** track corpus content hash or last-modified time alongside
  `built_at`, and either (a) refuse to serve queries when the corpus has
  changed since the index was built, or (b) trigger an automatic rebuild on
  a schedule or file-watch hook. Never assume "the index built successfully
  once" implies "the index is still correct."

## Takeaway

None of these three failure modes raise an exception. All three return
well-formed, schema-valid `RetrievalResult` objects. That is the core lesson
of this lab: RAG failures are usually silent and structurally valid — the
JSON schema passing validation tells you nothing about whether the content
is actually right. Catching these requires evaluation against known-answer
queries, not just schema checks.
