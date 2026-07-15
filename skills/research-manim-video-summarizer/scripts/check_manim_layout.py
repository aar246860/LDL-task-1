# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "pillow>=10.4.0",
#   "pypdf>=5.0.0",
#   "rich>=13.7.1",
#   "typer>=0.12.5",
# ]
# ///
from __future__ import annotations

import ast
import sys
from pathlib import Path
from typing import Final

import typer
from rich.console import Console
from rich.table import Table

SKILL_ROOT = Path(__file__).resolve().parent.parent
if str(SKILL_ROOT) not in sys.path:
    sys.path.insert(0, str(SKILL_ROOT))

from scripts.manim_layout_rules import evaluate_tree  # noqa: E402
from scripts.manim_layout_support import (  # noqa: E402
    LayoutFinding,
    LayoutReport,
    inspect_contact_sheet,
    inspect_qa_manifest,
    inspect_qa_provenance,
)
from scripts.storyboard_contract_rules import evaluate_storyboard  # noqa: E402
from scripts.storyboard_schema import parse_storyboard  # noqa: E402
from scripts.storyboard_semantic_audit import inspect_semantic_audit  # noqa: E402
from scripts.storyboard_source_mapping import inspect_source_scene_mapping  # noqa: E402
from scripts.storyboard_visual_audit import inspect_storyboard_visual_match  # noqa: E402
from scripts.video_frame_evidence import inspect_video_frame_evidence  # noqa: E402

CONSOLE: Final = Console()


def _input_failure(detail: str) -> LayoutReport:
    return LayoutReport(
        passed=False,
        findings=[LayoutFinding(check="input artifact", status="fail", detail=detail)],
    )


def evaluate_layout(
    scene_file: Path,
    contact_sheet: Path | None = None,
    qa_manifest: Path | None = None,
    storyboard: Path | None = None,
    source_artifact: Path | None = None,
    semantic_audit: Path | None = None,
) -> LayoutReport:
    try:
        source = scene_file.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(scene_file))
    except (OSError, UnicodeError, SyntaxError) as exc:
        return _input_failure(f"cannot parse scene file: {exc}")
    findings = evaluate_tree(tree)
    evidence_items = (contact_sheet, qa_manifest, storyboard, source_artifact, semantic_audit)
    if any(item is not None for item in evidence_items) and not all(item is not None for item in evidence_items):
        findings.append(
            LayoutFinding(
                check="post-render evidence set",
                status="fail",
                detail="contact sheet, QA manifest, storyboard, source artifact, and semantic audit must be supplied together",
            ),
        )
    elif all(item is not None for item in evidence_items):
        assert contact_sheet is not None and qa_manifest is not None and storyboard is not None
        assert source_artifact is not None and semantic_audit is not None
        findings.extend(inspect_contact_sheet(contact_sheet))
        semantic = inspect_semantic_audit(semantic_audit, source_artifact, storyboard)
        findings.append(
            LayoutFinding(
                check="semantic source audit",
                status="pass" if semantic.passed else "fail",
                detail=semantic.detail,
            ),
        )
        try:
            parsed_storyboard = parse_storyboard(storyboard.read_text(encoding="utf-8"))
        except (OSError, UnicodeError) as exc:
            findings.append(
                LayoutFinding(check="visual QA manifest", status="fail", detail=f"cannot read storyboard: {exc}"),
            )
        else:
            storyboard_report = evaluate_storyboard(parsed_storyboard.raw, strict=True)
            if not storyboard_report.passed:
                failed = [finding.check for finding in storyboard_report.findings if finding.status == "fail"]
                findings.append(
                    LayoutFinding(
                        check="storyboard contract",
                        status="fail",
                        detail=f"storyboard must pass strict review before visual QA: {', '.join(failed[:6])}",
                    ),
                )
            else:
                expected_scenes = {scene.number for scene in parsed_storyboard.scenes}
                expected_roles: dict[int, str] = {}
                for scene in parsed_storyboard.scenes:
                    background = scene.fields.token("background beat")
                    method = scene.fields.token("method step")
                    expected_roles[scene.number] = background if background != "none" else method if method != "none" else scene.fields.token("narrative beat")
                findings.append(inspect_source_scene_mapping(tree, expected_roles))
                findings.extend(inspect_qa_manifest(qa_manifest, expected_scenes))
                findings.append(inspect_storyboard_visual_match(qa_manifest, parsed_storyboard))
                findings.append(inspect_video_frame_evidence(qa_manifest))
                findings.extend(
                    inspect_qa_provenance(
                        qa_manifest,
                        scene_file,
                        storyboard,
                        contact_sheet,
                        source_artifact,
                        semantic_audit,
                    ),
                )
    passed = bool(findings) and all(finding.status == "pass" for finding in findings)
    return LayoutReport(passed=passed, findings=findings)


def print_report(report: LayoutReport) -> None:
    table = Table(title="Manim Layout Risk Check")
    table.add_column("Check")
    table.add_column("Status")
    table.add_column("Line")
    table.add_column("Detail")
    for finding in report.findings:
        table.add_row(finding.check, finding.status, "" if finding.line is None else str(finding.line), finding.detail)
    CONSOLE.print(table)
    CONSOLE.print(f"[bold]Result[/bold]: {'PASS' if report.passed else 'REVISE'}")


def main(
    scene_file: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        help="Generated Manim Python file.",
    ),
    contact_sheet: Path | None = typer.Option(
        None,
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        help="Rendered overview image; requires --qa-manifest and --storyboard.",
    ),
    qa_manifest: Path | None = typer.Option(
        None,
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        help="Entry/midpoint/settled review record; requires contact sheet and storyboard.",
    ),
    storyboard: Path | None = typer.Option(
        None,
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        help="Storyboard used to verify QA-manifest scene coverage.",
    ),
    source_artifact: Path | None = typer.Option(
        None,
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        help="Research source used by the independent semantic audit.",
    ),
    semantic_audit: Path | None = typer.Option(
        None,
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        help="Hash-bound independent source-passage audit JSON.",
    ),
) -> None:
    report = evaluate_layout(scene_file, contact_sheet, qa_manifest, storyboard, source_artifact, semantic_audit)
    print_report(report)
    if not report.passed:
        raise typer.Exit(code=1)


if __name__ == "__main__":
    typer.run(main)
