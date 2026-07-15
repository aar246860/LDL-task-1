from __future__ import annotations

import re
import stat
from dataclasses import dataclass
from pathlib import Path
from typing import Final

import typer

from scripts.publish_media_validation import MediaValidationError, validate_browser_video
from scripts.publish_package_validation import ReleaseManifestError, validate_release_manifest

FRAME_PATTERN: Final = re.compile(r"^scene\d+_(entry|midpoint|settled)\.(png|jpe?g)$", re.IGNORECASE)


@dataclass(frozen=True, slots=True)
class ReleasePackage:
    directory: Path
    assets: list[Path]
    mp4_files: list[Path]
    html_files: list[Path]
    contact_sheets: list[Path]
    metadata_files: list[Path]
    qa_files: list[Path]
    visual_qa_files: list[Path]
    frame_files: list[Path]


def _is_link_like(path: Path) -> bool:
    try:
        attributes = getattr(path.lstat(), "st_file_attributes", 0)
    except OSError:
        return True
    reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    return path.is_symlink() or bool(attributes & reparse_flag)


def _publishable_names(slug: str) -> set[str]:
    return {
        f"{slug}.mp4",
        f"{slug}.html",
        f"{slug}_contact_sheet.png",
        f"{slug}_contact_sheet.jpg",
        f"{slug}_contact_sheet.jpeg",
        f"{slug}_metadata.json",
        f"{slug}_qa.md",
        f"{slug}_visual_qa.json",
        f"{slug}_scene.py",
        f"{slug}_storyboard.md",
        f"{slug}_semantic_audit.json",
        f"{slug}_source.md",
        f"{slug}_source.pdf",
        f"{slug}_source.txt",
    }


def _role_files(files: list[Path], slug: str) -> dict[str, list[Path]]:
    return {
        "scene source": [path for path in files if path.name == f"{slug}_scene.py"],
        "storyboard": [path for path in files if path.name == f"{slug}_storyboard.md"],
        "source artifact": [path for path in files if re.fullmatch(rf"{re.escape(slug)}_source\.(md|pdf|txt)", path.name)],
        "semantic audit": [path for path in files if path.name == f"{slug}_semantic_audit.json"],
    }


def collect_package(package_dir: Path) -> ReleasePackage:
    if _is_link_like(package_dir):
        raise typer.BadParameter("package directory cannot be a symbolic link or reparse point")
    entries = list(package_dir.iterdir())
    linked = [path.name for path in entries if _is_link_like(path)]
    if linked:
        raise typer.BadParameter(f"package contains symbolic links or reparse points: {', '.join(linked[:8])}")
    directories = [path.name for path in entries if path.is_dir()]
    if directories:
        raise typer.BadParameter(f"package must be flat; nested directories are not publishable: {', '.join(directories[:8])}")
    files = sorted(path for path in entries if path.is_file())
    videos = [path for path in files if path.suffix.lower() == ".mp4"]
    if len(videos) != 1:
        raise typer.BadParameter("package must contain exactly one browser-ready MP4")
    slug = videos[0].stem
    allowed = _publishable_names(slug)
    unexpected = [path.name for path in files if path.name not in allowed and FRAME_PATTERN.fullmatch(path.name) is None]
    if unexpected:
        raise typer.BadParameter(f"package contains non-publishable files: {', '.join(unexpected[:8])}")
    roles = _role_files(files, slug)
    invalid_roles = [role for role, matches in roles.items() if len(matches) != 1]
    if invalid_roles:
        raise typer.BadParameter(f"package needs exactly one file for each provenance role: {', '.join(invalid_roles)}")
    groups = {
        "HTML player": [path for path in files if path.name == f"{slug}.html"],
        "contact sheet": [path for path in files if path.name.startswith(f"{slug}_contact_sheet.")],
        "metadata JSON": [path for path in files if path.name == f"{slug}_metadata.json"],
        "QA notes": [path for path in files if path.name == f"{slug}_qa.md"],
        "visual-QA manifest": [path for path in files if path.name == f"{slug}_visual_qa.json"],
        "entry/midpoint/settled frames": [path for path in files if FRAME_PATTERN.fullmatch(path.name)],
    }
    frame_label = "entry/midpoint/settled frames"
    invalid_groups = [label for label, matches in groups.items() if label != frame_label and len(matches) != 1]
    if invalid_groups:
        raise typer.BadParameter(f"package must contain exactly one {invalid_groups[0]}")
    if not groups[frame_label]:
        raise typer.BadParameter(f"package must contain {frame_label}")
    try:
        validate_browser_video(videos[0])
        validate_release_manifest(
            groups["visual-QA manifest"][0],
            groups["entry/midpoint/settled frames"],
            groups["contact sheet"][0],
            videos[0],
            files,
        )
    except (MediaValidationError, ReleaseManifestError) as exc:
        raise typer.BadParameter(f"package evidence is invalid: {exc}") from None
    return ReleasePackage(
        package_dir,
        files,
        videos,
        groups["HTML player"],
        groups["contact sheet"],
        groups["metadata JSON"],
        groups["QA notes"],
        groups["visual-QA manifest"],
        groups["entry/midpoint/settled frames"],
    )
