from __future__ import annotations

import re
from html import escape
from pathlib import Path
from typing import Final

PLAYER_TEMPLATE: Final = Path(__file__).resolve().parent.parent / "assets" / "research_video_player.html"
TEMPLATE_TOKEN: Final = re.compile(r"\{\{(TITLE|DESCRIPTION|MP4|CONTACT_SHEET)\}\}")


class ExportContentError(ValueError):
    pass


def _asset_name(value: str) -> str:
    if not value or Path(value).name != value or value in {".", ".."} or ":" in value or "\\" in value:
        raise ExportContentError(f"asset must be a local file name: {value!r}")
    return escape(value, quote=True)


def player_html(
    *,
    title: str,
    description: str,
    mp4_name: str,
    contact_sheet_name: str,
) -> str:
    replacements = {
        "TITLE": escape(title),
        "DESCRIPTION": escape(description),
        "MP4": _asset_name(mp4_name),
        "CONTACT_SHEET": _asset_name(contact_sheet_name),
    }
    content = PLAYER_TEMPLATE.read_text(encoding="utf-8")
    return TEMPLATE_TOKEN.sub(lambda match: replacements[match.group(1)], content)


def qa_notes_text(
    *,
    mp4_name: str,
    html_name: str,
    contact_sheet_name: str,
    metadata_name: str,
    metadata: str,
) -> str:
    lines = [
        "# Research Video QA Notes",
        "",
        "## Exported Artifacts",
        "",
        f"- MP4: `{mp4_name}`",
        f"- HTML player: `{html_name}`",
        f"- Contact sheet: `{contact_sheet_name}`",
        f"- Metadata: `{metadata_name}`",
        "",
        "## ffprobe Metadata",
        "",
        "```text",
        metadata.strip(),
        "```",
        "",
        "## Required Manual Review",
        "",
        "- Open the HTML player in a browser.",
        "- Confirm the video has finite duration, positive width and height, and no media error.",
        "- Treat the contact sheet as navigation only; review per-scene entry, midpoint, and settled frames separately.",
        "- Mark a scene state pass only when visual inspection confirms it is overlap-free and within-frame; a generic pass label is invalid.",
        "- Extract three nonblank frames per scene: entry, midpoint, and settled. Record each zero-based MP4 frame index, relative image path, and image SHA-256; all indices and decoded RGB images must be globally unique.",
        "- Decode the declared MP4 indices with FFmpeg and require exact RGB-pixel equality with the reviewed images. Renamed, repeated, or unrelated images do not count as evidence.",
        "- Record a named reviewer, timezone-aware ISO reviewed_at time, review_method set to visual inspection, pass decisions, and a substantive visual-content summary for every scene state in the visual-QA manifest.",
        "- Bind the visual-QA manifest to the Manim source, storyboard, research source, semantic audit, contact sheet, and MP4 with verified file names and SHA-256 values; regenerate it after any artifact changes.",
        "- Publish only after the user explicitly authorizes a live GitHub Release.",
        "",
    ]
    return "\n".join(lines)
