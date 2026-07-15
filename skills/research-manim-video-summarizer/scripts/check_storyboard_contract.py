# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "pypdf>=5.0.0",
#   "rich>=13.7.1",
#   "typer>=0.12.5",
# ]
# ///
from __future__ import annotations

import json
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Final

import typer
from rich.console import Console
from rich.table import Table

SKILL_ROOT = Path(__file__).resolve().parent.parent
if str(SKILL_ROOT) not in sys.path:
    sys.path.insert(0, str(SKILL_ROOT))

from scripts.storyboard_contract_rules import StoryboardReport, evaluate_storyboard  # noqa: E402
from scripts.storyboard_semantic_audit import SemanticAuditResult, inspect_semantic_audit  # noqa: E402

CONSOLE: Final = Console()


def serialize_report(report: StoryboardReport) -> str:
    return json.dumps(asdict(report), ensure_ascii=False, indent=2)


def print_report(report: StoryboardReport) -> None:
    table = Table(title="3B1B Storyboard Rubric")
    table.add_column("Check")
    table.add_column("Score")
    table.add_column("Status")
    table.add_column("Detail")
    for finding in report.findings:
        table.add_row(finding.check, f"{finding.score}/{finding.maximum}", finding.status, finding.detail)
    CONSOLE.print(table)
    CONSOLE.print(
        f"[bold]Total[/bold]: {report.score}/{report.maximum} (threshold {report.threshold}) - {'PASS' if report.passed else 'REVISE'}",
    )


def serialize_complete_report(report: StoryboardReport, semantic: SemanticAuditResult) -> str:
    payload = asdict(report)
    payload["structural_passed"] = report.passed
    payload["semantic_audit"] = asdict(semantic)
    payload["passed"] = report.passed and semantic.passed
    return json.dumps(payload, ensure_ascii=False, indent=2)


def main(
    storyboard: Path = typer.Argument(
        ...,
        help="Storyboard Markdown file.",
    ),
    strict: bool = typer.Option(False, help="Require stronger 3B1B-style evidence."),
    json_output: bool = typer.Option(False, "--json", help="Print JSON instead of a table."),
    source_artifact: Path | None = typer.Option(None, help="Source artifact used for independent semantic review."),
    semantic_audit: Path | None = typer.Option(None, help="Hash-bound source-passage audit JSON."),
) -> None:
    if not storyboard.is_file():
        message = f"cannot read storyboard: expected a readable file at {storyboard}"
        if json_output:
            typer.echo(json.dumps({"passed": False, "error": message}, ensure_ascii=False))
        else:
            CONSOLE.print(f"[red]{message}[/red]")
        raise typer.Exit(code=2)
    try:
        markdown = storyboard.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        message = f"cannot read storyboard: {exc}"
        if json_output:
            typer.echo(json.dumps({"passed": False, "error": message}, ensure_ascii=False))
        else:
            CONSOLE.print(f"[red]{message}[/red]")
        raise typer.Exit(code=2) from exc
    report = evaluate_storyboard(markdown, strict=strict)
    semantic = SemanticAuditResult(True, "semantic source audit is not required outside strict mode")
    if strict:
        if not isinstance(source_artifact, Path) or not isinstance(semantic_audit, Path):
            semantic = SemanticAuditResult(False, "strict mode requires --source-artifact and --semantic-audit")
        else:
            semantic = inspect_semantic_audit(semantic_audit, source_artifact, storyboard)
    if json_output:
        typer.echo(serialize_complete_report(report, semantic))
    else:
        print_report(report)
        CONSOLE.print(f"[bold]Semantic source audit[/bold]: {'PASS' if semantic.passed else 'REVISE'} - {semantic.detail}")
    if not report.passed or not semantic.passed:
        raise typer.Exit(code=1)


if __name__ == "__main__":
    typer.run(main)
