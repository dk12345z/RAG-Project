"""Load versioned prompt templates from prompts/.

Prompts are stored as plain files in the repository (in ``prompts/``) so
that changing a prompt is a normal, reviewable git diff, and a specific
version can be pinned by name rather than by mutating a single file.
"""
from __future__ import annotations

from pathlib import Path

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"


def load_prompt(name: str, version: str) -> str:
    """Load a versioned prompt file, e.g. ``load_prompt("answer", "v2")``.

    Looks for ``prompts/{name}_{version}.md``.
    """
    path = PROMPTS_DIR / f"{name}_{version}.md"
    if not path.exists():
        available = sorted(p.name for p in PROMPTS_DIR.glob(f"{name}_*.md"))
        raise FileNotFoundError(
            f"No prompt file at {path}. Available versions for '{name}': {available}"
        )
    return path.read_text(encoding="utf-8")


def latest_version(name: str) -> str:
    """Return the highest version string available for a prompt ``name``.

    Versions are expected to be of the form ``v1``, ``v2``, ... and are
    compared numerically.
    """
    candidates = list(PROMPTS_DIR.glob(f"{name}_v*.md"))
    if not candidates:
        raise FileNotFoundError(f"No prompt files found for '{name}' in {PROMPTS_DIR}")

    def version_num(path: Path) -> int:
        stem = path.stem  # e.g. "answer_v2"
        version_part = stem.split("_")[-1]  # "v2"
        return int(version_part.lstrip("v"))

    best = max(candidates, key=version_num)
    return best.stem.split("_")[-1]
