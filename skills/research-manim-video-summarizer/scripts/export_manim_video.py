# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "rich>=13.7.1",
#   "typer>=0.12.5",
# ]
# ///
from __future__ import annotations

import json
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Final

import typer
from rich.console import Console
from rich.table import Table

SKILL_ROOT = Path(__file__).resolve().parent.parent
if str(SKILL_ROOT) not in sys.path:
    sys.path.insert(0, str(SKILL_ROOT))

from scripts.export_package_content import ExportContentError, player_html, qa_notes_text  # noqa: E402

CONSOLE: Final = Console()
DEFAULT_DESCRIPTION: Final = "Independent geometry-first research animation generated with Manim Community."
SLUG_PATTERN: Final = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


@dataclass(frozen=True, slots=True)
class VideoPackage:
    mp4: Path
    contact_sheet: Path
    html: Path
    metadata: Path
    qa_notes: Path


@dataclass(frozen=True, slots=True)
class CommandResult:
    stdout: str
    stderr: str


@dataclass(frozen=True, slots=True)
class ExportArtifactMissingError(Exception):
    artifact: Path

    def __str__(self) -> str:
        return f"expected export artifact was not created: {self.artifact}"


class ExportCommandError(RuntimeError):
    pass


def run_command(command: list[str]) -> CommandResult:
    try:
        completed = subprocess.run(command, check=True, capture_output=True, text=True)
    except FileNotFoundError as exc:
        raise ExportCommandError(f"required executable not found: {command[0]}") from exc
    except subprocess.CalledProcessError as exc:
        detail = exc.stderr.strip() or exc.stdout.strip() or f"exit code {exc.returncode}"
        raise ExportCommandError(f"{command[0]} failed: {detail}") from exc
    return CommandResult(stdout=completed.stdout, stderr=completed.stderr)


def validated_slug(slug: str) -> str:
    if SLUG_PATTERN.fullmatch(slug) is None or slug in {".", ".."}:
        raise typer.BadParameter("slug must be one local file-name token using letters, digits, dot, underscore, or hyphen")
    return slug


def ensure_output_dir(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)


def require_artifact(path: Path) -> None:
    if not path.exists() or path.stat().st_size <= 0:
        raise ExportArtifactMissingError(path)


def reencode_mp4(input_mp4: Path, output_mp4: Path) -> None:
    run_command(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(input_mp4),
            "-c:v",
            "libx264",
            "-profile:v",
            "baseline",
            "-level",
            "3.1",
            "-pix_fmt",
            "yuv420p",
            "-preset",
            "medium",
            "-crf",
            "23",
            "-movflags",
            "+faststart",
            "-an",
            str(output_mp4),
        ],
    )
    require_artifact(output_mp4)


def extract_contact_sheet(input_mp4: Path, contact_sheet: Path) -> None:
    run_command(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(input_mp4),
            "-vf",
            "fps=1/5,scale=320:-1,tile=4x3",
            "-frames:v",
            "1",
            str(contact_sheet),
        ],
    )
    if contact_sheet.exists() and contact_sheet.stat().st_size > 0:
        return
    run_command(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(input_mp4),
            "-vf",
            "scale=320:-1",
            "-frames:v",
            "1",
            str(contact_sheet),
        ],
    )
    require_artifact(contact_sheet)


def write_player_page(package: VideoPackage, title: str, description: str) -> None:
    html = player_html(
        title=title,
        description=description,
        mp4_name=package.mp4.name,
        contact_sheet_name=package.contact_sheet.name,
    )
    package.html.write_text(html, encoding="utf-8")


def inspect_video(mp4: Path) -> str:
    result = run_command(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=codec_name,profile,level,pix_fmt,width,height,duration,nb_frames",
            "-show_entries",
            "format=duration,size,format_name",
            "-of",
            "default=noprint_wrappers=1",
            str(mp4),
        ],
    )
    return result.stdout


def write_metadata(package: VideoPackage, title: str, description: str, metadata: str) -> None:
    payload = {
        "title": title,
        "description": description,
        "generated_at": datetime.now(UTC).isoformat(),
        "artifacts": {
            "mp4": package.mp4.name,
            "contact_sheet": package.contact_sheet.name,
            "html": package.html.name,
            "qa_notes": package.qa_notes.name,
        },
        "ffprobe": metadata,
    }
    package.metadata.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_qa_notes(package: VideoPackage, metadata: str) -> None:
    notes = qa_notes_text(
        mp4_name=package.mp4.name,
        html_name=package.html.name,
        contact_sheet_name=package.contact_sheet.name,
        metadata_name=package.metadata.name,
        metadata=metadata,
    )
    package.qa_notes.write_text(notes, encoding="utf-8")


def print_package(package: VideoPackage, metadata: str) -> None:
    table = Table(title="Research Video Export")
    table.add_column("Artifact")
    table.add_column("Path")
    table.add_row("MP4", str(package.mp4))
    table.add_row("Contact sheet", str(package.contact_sheet))
    table.add_row("HTML player", str(package.html))
    table.add_row("Metadata JSON", str(package.metadata))
    table.add_row("QA notes", str(package.qa_notes))
    CONSOLE.print(table)
    CONSOLE.print("[bold]Video metadata[/bold]")
    CONSOLE.print(metadata)


def main(
    input_mp4: Path = typer.Argument(..., exists=True, file_okay=True, dir_okay=False, readable=True, help="Rendered Manim MP4."),
    output_dir: Path = typer.Argument(..., help="Directory for browser-ready output package."),
    title: str = typer.Option("Research video summary", help="HTML player title."),
    description: str = typer.Option(DEFAULT_DESCRIPTION, help="HTML player description."),
    slug: str = typer.Option("research_video", help="Output file slug."),
) -> None:
    safe_slug = validated_slug(slug)
    try:
        ensure_output_dir(output_dir)
    except OSError as exc:
        raise typer.BadParameter(f"cannot create output directory: {exc}") from None
    package = VideoPackage(
        mp4=output_dir / f"{safe_slug}.mp4",
        contact_sheet=output_dir / f"{safe_slug}_contact_sheet.png",
        html=output_dir / f"{safe_slug}.html",
        metadata=output_dir / f"{safe_slug}_metadata.json",
        qa_notes=output_dir / f"{safe_slug}_qa.md",
    )
    try:
        reencode_mp4(input_mp4, package.mp4)
        extract_contact_sheet(package.mp4, package.contact_sheet)
        write_player_page(package, title=title, description=description)
        metadata = inspect_video(package.mp4)
        write_metadata(package, title=title, description=description, metadata=metadata)
        write_qa_notes(package, metadata)
    except (ExportArtifactMissingError, ExportCommandError, ExportContentError, OSError) as exc:
        raise typer.BadParameter(f"video export failed: {exc}") from None
    print_package(package, metadata)


if __name__ == "__main__":
    typer.run(main)
