# Prompt Versioning: Treat Prompts as Code

A prompt is a dependency of your system's behavior, exactly like a library
version. Changing it changes behavior, sometimes drastically, and that
change deserves the same rigor as a code change:

- **Store prompts in git**, as files, not as inline string literals
  scattered through application code.
- **Version them explicitly** (`answer_v1.md`, `answer_v2.md`, ...) rather
  than overwriting the same file, so a regression can be bisected to an exact
  prompt revision.
- **Keep a changelog** describing *why* each version changed and what
  problem it was meant to fix. "Improved wording" is not a changelog entry;
  "v2: added explicit instruction to cite chunk IDs because v1 fabricated
  sources" is.
- **Pin the prompt version used in production** the same way you'd pin a
  package version, and roll it forward deliberately with evaluation, not
  silently on every deploy.

The payoff is that when behavior regresses, "what changed?" has the same
answer for prompts as it does for code: `git log` and `git diff`.
