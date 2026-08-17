# Context Windows Are the Scarcest Resource

Large language models don't fail because they are "not smart enough." Most
production agent failures trace back to *context* problems: the wrong
information was in the prompt, the right information was missing, or too much
irrelevant material crowded out what mattered.

Treat the context window like RAM on a memory-constrained device, not like an
infinite scratchpad. Every token you put in context has a cost: it competes
for the model's attention, it costs money, and it increases the chance that
the model latches onto the wrong detail.

Three questions to ask before adding anything to a prompt:

1. Does the model need this to answer the *current* step, or could it fetch
   it on demand via a tool call?
2. Is this information stable for the life of the conversation, or will it go
   stale within a few turns?
3. If I removed this, would the model's answer actually get worse?

When in doubt, leave it out and add a retrieval or tool-call path instead.
