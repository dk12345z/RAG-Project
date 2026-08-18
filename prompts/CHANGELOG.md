# Prompt Changelog

All prompt changes are recorded here, same as a code changelog. Prompts are
files under this directory, never inline strings — see
`ragproject/prompts.py` for the loader.

## answer

### v2 — 2026-08-17
- Added an explicit instruction to cite `chunk_id`s used in the answer.
  v1 produced answers with no traceable link back to the retrieved chunk,
  which made it impossible to tell whether a wrong answer was a retrieval
  failure or a generation failure.
- Added an explicit "Insufficient context to answer." escape hatch. v1 had
  no such instruction and would confidently answer from world knowledge
  when retrieval returned weak or irrelevant chunks (a hallucination risk
  masquerading as a correct-looking answer).

### v1 — 2026-08-17
- Initial version: context + question, free-form one-to-two sentence
  answer. No citation requirement, no explicit fallback for missing
  context.
