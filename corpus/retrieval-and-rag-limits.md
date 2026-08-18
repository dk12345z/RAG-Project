# Retrieval: Embeddings, Chunking, and the Honest Limits of RAG

Retrieval-augmented generation works by turning a corpus into chunks,
embedding each chunk into a vector space, and retrieving the chunks whose
vectors are closest to a query's vector. That's the whole trick — and it is
also where most of the honest limitations live.

## Chunking

Chunk size is a bias-variance tradeoff. Chunks that are too small lose
surrounding context and get retrieved based on a coincidental keyword match.
Chunks that are too large dilute the embedding with unrelated content and
push the genuinely relevant sentence below the similarity threshold.

## Top-k

Retrieving too few chunks (low top-k) means a correct answer that's split
across two chunks never fully reaches the model. Retrieving too many (high
top-k) reintroduces the context-crowding problem: irrelevant chunks compete
for attention and increase hallucination risk.

## Stale indexes

An index built once from a snapshot of the corpus silently diverges from
reality every time the underlying documents change. RAG systems fail
"quietly" here: retrieval still returns confident-looking results, but they
describe a document that no longer exists in that form. There is no
exception thrown — just wrong answers that look plausible.

## The honest limit

RAG does not give a model "understanding" of your corpus. It gives the model
a lossy, similarity-ranked excerpt of your corpus for a single query. If the
answer requires synthesizing many documents, multi-hop reasoning, or knowing
what is *absent* from the corpus, naive top-k retrieval will not get you
there.
