# Structured Input and Output

Free-form prose in and out of a model is easy to write and hard to operate.
Structured input/output — JSON schemas, typed function-calling arguments,
enum-constrained fields — reduces failure in a few concrete ways:

- **Parsing is deterministic.** A downstream system can validate a JSON
  object against a schema and fail fast, instead of regex-scraping prose and
  silently getting it wrong.
- **It narrows the model's decision space.** An enum field with three legal
  values is much harder to get wrong than an open-ended sentence describing
  the same choice.
- **It makes prompt regressions visible.** When output is structured, a
  schema-validation test can catch a prompt change that broke the contract,
  long before a human notices a subtly wrong answer.
- **It composes.** Structured output from one step becomes structured input
  to the next, without a lossy natural-language hop in between.

The failure mode to watch for: schemas that are too rigid punish the model
for edge cases it should be allowed to express (e.g. "I don't know" or
"insufficient context"). Always include an explicit escape hatch field
(`confidence`, `insufficient_context: bool`, etc.) rather than forcing a
guess into a schema shape.
