from __future__ import annotations

import json
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path


class CompanionValidationError(ValueError):
    pass


class _PlayerParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.video_controls = False
        self.poster = ""
        self.sources: list[tuple[str, str]] = []
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "video":
            self.video_controls = "controls" in values
            self.poster = values.get("poster") or ""
        elif tag == "source":
            self.sources.append((values.get("src") or "", values.get("type") or ""))
        elif tag == "a":
            self.links.append(values.get("href") or "")


def _timezone_aware(value: object) -> bool:
    if not isinstance(value, str):
        return False
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return parsed.tzinfo is not None and parsed.utcoffset() is not None


def _validate_html(path: Path, video: Path, contact_sheet: Path) -> None:
    try:
        content = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise CompanionValidationError(f"cannot read HTML player: {exc}") from exc
    parser = _PlayerParser()
    parser.feed(content)
    if not parser.video_controls:
        raise CompanionValidationError("HTML player needs a video element with controls")
    if (video.name, "video/mp4") not in parser.sources:
        raise CompanionValidationError("HTML player does not reference the packaged MP4 source")
    if parser.poster and parser.poster != contact_sheet.name:
        raise CompanionValidationError("HTML player does not use the packaged contact sheet poster")
    if video.name not in parser.links:
        raise CompanionValidationError("HTML player needs a direct packaged MP4 link")


def _validate_metadata(path: Path, video: Path, contact_sheet: Path, html: Path, qa_notes: Path) -> None:
    try:
        payload: object = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError, RecursionError) as exc:
        raise CompanionValidationError(f"cannot read metadata JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise CompanionValidationError("metadata must be a JSON object")
    artifacts = payload.get("artifacts")
    expected = {
        "mp4": video.name,
        "contact_sheet": contact_sheet.name,
        "html": html.name,
        "qa_notes": qa_notes.name,
    }
    if artifacts != expected:
        raise CompanionValidationError("metadata artifact names do not match the package")
    if not _timezone_aware(payload.get("generated_at")):
        raise CompanionValidationError("metadata needs a timezone-aware generated_at value")
    if not isinstance(payload.get("title"), str) or not payload["title"].strip():
        raise CompanionValidationError("metadata needs a nonblank title")
    if not isinstance(payload.get("ffprobe"), str) or len(payload["ffprobe"].strip()) < 20:
        raise CompanionValidationError("metadata needs substantive ffprobe output")


def _validate_qa_notes(path: Path) -> None:
    try:
        text = path.read_text(encoding="utf-8").lower()
    except (OSError, UnicodeError) as exc:
        raise CompanionValidationError(f"cannot read QA notes: {exc}") from exc
    required = (
        "entry, midpoint, and settled",
        "zero-based mp4 frame index",
        "sha-256",
        "overlap-free and within-frame",
        "visual-qa manifest",
    )
    missing = [phrase for phrase in required if phrase not in text]
    if missing:
        raise CompanionValidationError(f"QA notes omit required review rules: {', '.join(missing)}")


def validate_companion_artifacts(
    html: Path,
    metadata: Path,
    qa_notes: Path,
    video: Path,
    contact_sheet: Path,
) -> None:
    _validate_html(html, video, contact_sheet)
    _validate_metadata(metadata, video, contact_sheet, html, qa_notes)
    _validate_qa_notes(qa_notes)
