"""Generate an HTML completion report for this repository."""
from __future__ import annotations

import argparse
import html
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


REQUIRED_PATHS = [
    "ragproject/chunking.py",
    "ragproject/embeddings.py",
    "ragproject/index.py",
    "ragproject/retriever.py",
    "ragproject/schemas.py",
    "ragproject/prompts.py",
    "ragproject/cli.py",
    "corpus/context-windows.md",
    "corpus/prompt-versioning.md",
    "corpus/retrieval-and-rag-limits.md",
    "corpus/structured-io.md",
    "prompts/answer_v1.md",
    "prompts/answer_v2.md",
    "prompts/CHANGELOG.md",
    "labs/break_it.py",
    "labs/FAILURE_SIGNATURES.md",
    "tests/test_chunking.py",
    "tests/test_prompts.py",
    "tests/test_retriever.py",
    "tests/test_schemas.py",
]


@dataclass
class TestSummary:
    passed: int = 0
    failed: int = 0
    errors: int = 0
    skipped: int = 0
    total: int = 0
    output: str = ""
    ran: bool = False


@dataclass
class CompletionReport:
    completed_items: int
    total_items: int
    completion_percent: float
    existing_paths: list[str]
    missing_paths: list[str]
    tests: TestSummary
    generated_at: str


def _parse_count(output: str, marker: str) -> int:
    match = re.search(rf"(\d+)\s+{re.escape(marker)}\b", output)
    return int(match.group(1)) if match else 0


def run_tests(project_root: Path) -> TestSummary:
    cmd = [sys.executable, "-m", "pytest", "-q"]
    proc = subprocess.run(cmd, cwd=project_root, capture_output=True, text=True)
    output = (proc.stdout + "\n" + proc.stderr).strip()

    if "No module named pytest" in output:
        return TestSummary(output=output, ran=False)

    passed = _parse_count(output, "passed")
    failed = _parse_count(output, "failed")
    errors = _parse_count(output, "error") + _parse_count(output, "errors")
    skipped = _parse_count(output, "skipped")
    total = passed + failed + errors + skipped

    return TestSummary(
        passed=passed,
        failed=failed,
        errors=errors,
        skipped=skipped,
        total=total,
        output=output,
        ran=True,
    )


def build_report(project_root: Path, run_test_suite: bool = True) -> CompletionReport:
    existing_paths: list[str] = []
    missing_paths: list[str] = []

    for relative_path in REQUIRED_PATHS:
        if (project_root / relative_path).exists():
            existing_paths.append(relative_path)
        else:
            missing_paths.append(relative_path)

    tests = run_tests(project_root) if run_test_suite else TestSummary(ran=False)

    completed = len(existing_paths)
    total = len(REQUIRED_PATHS)

    if tests.ran and tests.total > 0:
        completed += tests.passed
        total += tests.total

    percent = (completed / total * 100) if total else 0.0

    return CompletionReport(
        completed_items=completed,
        total_items=total,
        completion_percent=percent,
        existing_paths=existing_paths,
        missing_paths=missing_paths,
        tests=tests,
        generated_at=datetime.now(timezone.utc).isoformat(),
    )


def render_html(report: CompletionReport, output_path: Path) -> None:
    def li(items: list[str]) -> str:
        if not items:
            return "<li>None</li>"
        return "".join(f"<li>{html.escape(item)}</li>" for item in items)

    tests = report.tests
    test_block = (
        f"<p><strong>Tests:</strong> {tests.passed} passed, {tests.failed} failed, "
        f"{tests.errors} errors, {tests.skipped} skipped</p>"
        if tests.ran
        else "<p><strong>Tests:</strong> Not run (pytest unavailable or disabled).</p>"
    )

    html_doc = f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>RAG-Project Completion Report</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 2rem; line-height: 1.5; }}
    .percent {{ font-size: 2rem; font-weight: bold; color: #0b6bcb; }}
    .ok {{ color: #116611; }}
    .warn {{ color: #9b1c1c; }}
    pre {{ background: #f6f8fa; padding: 1rem; border-radius: 6px; overflow-x: auto; }}
  </style>
</head>
<body>
  <h1>RAG-Project Completion Report</h1>
  <p>Generated at: {html.escape(report.generated_at)}</p>
  <p class=\"percent\">{report.completion_percent:.2f}% complete</p>
  <p>Completed checks: {report.completed_items}/{report.total_items}</p>
  {test_block}

  <h2>Required project files found ({len(report.existing_paths)})</h2>
  <ul class=\"ok\">{li(report.existing_paths)}</ul>

  <h2>Missing required files ({len(report.missing_paths)})</h2>
  <ul class=\"warn\">{li(report.missing_paths)}</ul>

  <h2>Raw test output</h2>
  <pre>{html.escape(report.tests.output or 'No test output available.')}</pre>
</body>
</html>
"""
    output_path.write_text(html_doc, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate an HTML completion report.")
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
        help="Repository root path",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("project_completion_report.html"),
        help="Output HTML path",
    )
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="Skip running pytest while computing completion",
    )
    args = parser.parse_args(argv)

    project_root = args.project_root.resolve()
    output_path = args.output if args.output.is_absolute() else project_root / args.output

    report = build_report(project_root, run_test_suite=not args.skip_tests)
    render_html(report, output_path)
    print(
        f"Generated {output_path} ({report.completion_percent:.2f}% complete: "
        f"{report.completed_items}/{report.total_items})."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
