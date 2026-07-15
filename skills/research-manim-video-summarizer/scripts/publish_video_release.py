# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "pillow>=11.0.0",
#   "rich>=13.7.1",
#   "typer>=0.12.5",
# ]
# ///
from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Final

import typer
from rich.console import Console
from rich.table import Table

SKILL_ROOT = Path(__file__).resolve().parent.parent
if str(SKILL_ROOT) not in sys.path:
    sys.path.insert(0, str(SKILL_ROOT))

from scripts.release_package_collection import ReleasePackage, collect_package  # noqa: E402

CONSOLE: Final = Console()
PUBLISH_MODES: Final = ("release",)
REPOSITORY_PATTERN: Final = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
RELEASE_TAG_PATTERN: Final = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


@dataclass(frozen=True, slots=True)
class CommandResult:
    stdout: str
    stderr: str
    returncode: int


class PublishCommandError(RuntimeError):
    pass


def run_command(command: list[str], *, check: bool) -> CommandResult:
    try:
        completed = subprocess.run(command, capture_output=True, text=True, timeout=120)
    except FileNotFoundError as exc:
        raise PublishCommandError(f"required executable not found: {command[0]}") from exc
    except subprocess.TimeoutExpired as exc:
        raise PublishCommandError(f"command timed out after 120 seconds: {command[0]}") from exc
    except OSError as exc:
        raise PublishCommandError(f"cannot execute {command[0]}: {exc}") from exc
    if check and completed.returncode != 0:
        msg = completed.stderr.strip() or completed.stdout.strip()
        raise PublishCommandError(msg or f"{command[0]} exited with {completed.returncode}")
    return CommandResult(stdout=completed.stdout, stderr=completed.stderr, returncode=completed.returncode)


def default_release_tag(package: ReleasePackage) -> str:
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return f"{package.directory.name}-{stamp}"


def release_url(github_repo: str, release_tag: str) -> str:
    return f"https://github.com/{github_repo}/releases/tag/{release_tag}"


def normalize_publish_mode(publish: str) -> str:
    if publish not in PUBLISH_MODES:
        allowed = ", ".join(PUBLISH_MODES)
        raise typer.BadParameter(f"publish must be one of: {allowed}")
    return publish


def ensure_release(github_repo: str, release_tag: str, release_title: str, notes: str, *, dry_run: bool) -> None:
    view_command = ["gh", "release", "view", release_tag, "-R", github_repo]
    tag_command = ["gh", "api", f"repos/{github_repo}/git/ref/tags/{release_tag}"]
    create_command = ["gh", "release", "create", release_tag, "-R", github_repo, "--title", release_title, "--notes", notes]
    if dry_run:
        CONSOLE.print("[bold]Dry run[/bold]: would check release")
        CONSOLE.print(" ".join(view_command))
        CONSOLE.print("[bold]Dry run[/bold]: would check Git tag")
        CONSOLE.print(" ".join(tag_command))
        CONSOLE.print("[bold]Dry run[/bold]: would create release if missing")
        CONSOLE.print(" ".join(create_command))
        return
    existing = run_command(view_command, check=False)
    if existing.returncode == 0:
        raise PublishCommandError(f"release tag already exists: {release_tag}")
    if not _is_not_found(existing):
        raise PublishCommandError("cannot establish that the GitHub release is absent")
    existing_tag = run_command(tag_command, check=False)
    if existing_tag.returncode == 0:
        raise PublishCommandError(f"Git tag already exists: {release_tag}")
    if not _is_not_found(existing_tag):
        raise PublishCommandError("cannot establish that the Git tag is absent")
    run_command(create_command, check=True)


def _is_not_found(result: CommandResult) -> bool:
    output = f"{result.stdout}\n{result.stderr}".lower()
    return any(
        marker in output
        for marker in (
            "release not found",
            "tag not found",
            "could not find release",
            "could not find tag",
            "http 404",
            "status 404",
        )
    )


def upload_assets(package: ReleasePackage, github_repo: str, release_tag: str, *, dry_run: bool) -> None:
    command = [
        "gh",
        "release",
        "upload",
        release_tag,
        *[str(path) for path in package.assets],
        "-R",
        github_repo,
    ]
    if dry_run:
        CONSOLE.print("[bold]Dry run[/bold]: would upload assets")
        CONSOLE.print(" ".join(command))
        return
    run_command(command, check=True)


def stage_package(package: ReleasePackage, staging_dir: Path) -> ReleasePackage:
    staging_dir.mkdir(parents=True, exist_ok=True)
    for asset in package.assets:
        shutil.copy2(asset, staging_dir / asset.name, follow_symlinks=False)
    return collect_package(staging_dir)


def print_result(package: ReleasePackage, github_repo: str, release_tag: str, *, dry_run: bool) -> None:
    table = Table(title="GitHub Release Video Package")
    table.add_column("Artifact")
    table.add_column("Count")
    table.add_row("MP4", str(len(package.mp4_files)))
    table.add_row("HTML player", str(len(package.html_files)))
    table.add_row("Contact sheet", str(len(package.contact_sheets)))
    table.add_row("Metadata JSON", str(len(package.metadata_files)))
    table.add_row("QA notes", str(len(package.qa_files)))
    table.add_row("Visual-QA manifest", str(len(package.visual_qa_files)))
    table.add_row("Reviewed scene frames", str(len(package.frame_files)))
    table.add_row("Total assets", str(len(package.assets)))
    CONSOLE.print(table)
    CONSOLE.print(f"[bold]Release page[/bold]: {release_url(github_repo, release_tag)}")
    for mp4 in package.mp4_files:
        CONSOLE.print(f"[bold]Phone download[/bold]: open the release page and download asset `{mp4.name}`")
    if dry_run:
        CONSOLE.print("[yellow]Dry run only; no GitHub release or asset was changed.[/yellow]")
    CONSOLE.print("[yellow]Do not share GitHub blob URLs as the only video link; use release assets for downloads.[/yellow]")


def main(
    package_dir: Path = typer.Argument(..., exists=True, file_okay=False, readable=True, help="Exported video package directory."),
    github_repo: str = typer.Option(..., "--github-repo", help="Target private paper repository as OWNER/REPO."),
    release_tag: str | None = typer.Option(None, help="Release tag. Defaults to package name plus timestamp."),
    release_title: str | None = typer.Option(None, help="Release title. Defaults to release tag."),
    publish: str = typer.Option("release", help="Publishing target. Only GitHub Release is automated."),
    dry_run: bool = typer.Option(True, "--dry-run/--live", help="Default to preview-only; --live enables mutation."),
    confirm_publish: bool = typer.Option(False, help="Required together with --live for GitHub mutation."),
) -> None:
    if not dry_run and not confirm_publish:
        raise typer.BadParameter("live GitHub publishing requires --confirm-publish")
    if REPOSITORY_PATTERN.fullmatch(github_repo) is None:
        raise typer.BadParameter("github repository must use OWNER/REPO syntax")
    normalize_publish_mode(publish)
    package = collect_package(package_dir)
    tag = release_tag or default_release_tag(package)
    if RELEASE_TAG_PATTERN.fullmatch(tag) is None:
        raise typer.BadParameter("release tag must use letters, digits, dot, underscore, or hyphen")
    title = release_title or tag
    notes = "Browser-ready Manim research video package with MP4, HTML player, contact sheet, metadata, and QA notes."
    try:
        if dry_run:
            ensure_release(github_repo, tag, title, notes, dry_run=True)
            upload_assets(package, github_repo, tag, dry_run=True)
        else:
            with tempfile.TemporaryDirectory(prefix="video-release-") as staging:
                staged_package = stage_package(package, Path(staging))
                ensure_release(github_repo, tag, title, notes, dry_run=False)
                upload_assets(staged_package, github_repo, tag, dry_run=False)
    except PublishCommandError as exc:
        raise typer.BadParameter(f"GitHub publication failed: {exc}") from None
    print_result(package, github_repo, tag, dry_run=dry_run)


if __name__ == "__main__":
    typer.run(main)
