from __future__ import annotations

import json
import re
from datetime import datetime
from hashlib import sha256
from pathlib import Path
from typing import Final

from scripts.check_manim_layout import evaluate_layout
from scripts.manim_layout_support import LAYOUT_REVIEW_PASS
from scripts.publish_companion_validation import CompanionValidationError, validate_companion_artifacts

FRAME_PATTERN: Final = re.compile(r"^scene(\d+)_(entry|midpoint|settled)\.(png|jpe?g)$", re.IGNORECASE)
HASH_PATTERN: Final = re.compile(r"^[0-9a-f]{64}$")


class ReleaseManifestError(ValueError):
    pass


def _valid_review_time(value: object) -> bool:
    if not isinstance(value, str):
        return False
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return parsed.tzinfo is not None and parsed.utcoffset() is not None


def _file_digest(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _artifact(
    payload: dict[object, object],
    package: dict[str, Path],
    file_field: str,
    hash_field: str,
    expected_name: re.Pattern[str],
) -> Path:
    name = payload.get(file_field)
    digest = payload.get(hash_field)
    if not isinstance(name, str) or Path(name).name != name or expected_name.fullmatch(name) is None:
        raise ReleaseManifestError(f"visual-QA manifest has an invalid {file_field}")
    path = package.get(name)
    if path is None:
        raise ReleaseManifestError(f"visual-QA manifest needs a packaged {file_field}")
    if not isinstance(digest, str) or HASH_PATTERN.fullmatch(digest) is None or digest != _file_digest(path):
        raise ReleaseManifestError(f"visual-QA manifest does not match {name}")
    return path


def _required_artifacts(
    payload: dict[object, object],
    package: dict[str, Path],
    slug: str,
) -> dict[str, Path]:
    escaped = re.escape(slug)
    specs = {
        "scene": ("scene_source_file", "scene_source_sha256", rf"{escaped}_scene\.py"),
        "storyboard": ("storyboard_file", "storyboard_sha256", rf"{escaped}_storyboard\.md"),
        "source": ("source_artifact_file", "source_artifact_sha256", rf"{escaped}_source\.(md|pdf|txt)"),
        "audit": ("semantic_audit_file", "semantic_audit_sha256", rf"{escaped}_semantic_audit\.json"),
        "contact": ("contact_sheet_file", "contact_sheet_sha256", rf"{escaped}_contact_sheet\.(png|jpe?g)"),
        "html": ("html_file", "html_sha256", rf"{escaped}\.html"),
        "metadata": ("metadata_file", "metadata_sha256", rf"{escaped}_metadata\.json"),
        "qa": ("qa_notes_file", "qa_notes_sha256", rf"{escaped}_qa\.md"),
    }
    artifacts = {
        role: _artifact(payload, package, file_field, hash_field, re.compile(pattern, re.IGNORECASE))
        for role, (file_field, hash_field, pattern) in specs.items()
    }
    if len({path.name for path in artifacts.values()}) != len(artifacts):
        raise ReleaseManifestError("each manifest artifact role must reference a distinct packaged file")
    return artifacts


def _validate_scene_records(payload: dict[object, object], frame_files: list[Path]) -> None:
    records = payload.get("scenes")
    if not isinstance(records, list) or not records:
        raise ReleaseManifestError("visual-QA manifest needs nonempty scene records")
    available = {path.name for path in frame_files}
    referenced: list[str] = []
    seen: list[int] = []
    for value in records:
        if not isinstance(value, dict):
            raise ReleaseManifestError("visual-QA scene record must be an object")
        scene = value.get("scene")
        if not isinstance(scene, int) or isinstance(scene, bool):
            raise ReleaseManifestError("visual-QA scene identifier must be an integer")
        seen.append(scene)
        for state in ("entry", "midpoint", "settled"):
            if value.get(state) != LAYOUT_REVIEW_PASS:
                raise ReleaseManifestError(f"Scene {scene} {state} is not overlap-free and within-frame")
            frame_name = value.get(f"{state}_frame")
            if not isinstance(frame_name, str) or Path(frame_name).name != frame_name:
                raise ReleaseManifestError(f"Scene {scene} {state} frame must be a package-root file name")
            match = FRAME_PATTERN.fullmatch(frame_name)
            if match is None or int(match.group(1)) != scene or match.group(2).lower() != state:
                raise ReleaseManifestError(f"Scene {scene} {state} frame name does not match its record")
            referenced.append(frame_name)
    if len(seen) != len(set(seen)) or len(referenced) != len(set(referenced)):
        raise ReleaseManifestError("visual-QA scene or frame records are duplicated")
    if set(referenced) != available:
        raise ReleaseManifestError("visual-QA frame references do not match package frame files")


def validate_release_manifest(
    manifest: Path,
    frame_files: list[Path],
    contact_sheet: Path,
    video: Path,
    package_files: list[Path],
) -> None:
    try:
        payload: object = json.loads(manifest.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError, RecursionError) as exc:
        raise ReleaseManifestError(f"cannot read visual-QA manifest: {exc}") from exc
    if not isinstance(payload, dict):
        raise ReleaseManifestError("visual-QA manifest must be a JSON object")
    if not isinstance(payload.get("reviewer"), str) or not payload["reviewer"].strip():
        raise ReleaseManifestError("visual-QA manifest needs a named reviewer")
    if not _valid_review_time(payload.get("reviewed_at")) or payload.get("review_method") != "visual inspection":
        raise ReleaseManifestError("visual-QA manifest needs a valid independent review record")
    if payload.get("browser_playback") != "pass: finite duration, positive dimensions, no media error":
        raise ReleaseManifestError("visual-QA manifest needs a passing browser playback review")
    if payload.get("video_file") != video.name or payload.get("video_sha256") != _file_digest(video):
        raise ReleaseManifestError("visual-QA manifest does not match the package MP4")
    package = {path.name: path for path in package_files}
    artifacts = _required_artifacts(payload, package, video.stem)
    if artifacts["contact"] != contact_sheet:
        raise ReleaseManifestError("visual-QA manifest does not match the selected contact sheet")
    _validate_scene_records(payload, frame_files)
    try:
        validate_companion_artifacts(
            artifacts["html"],
            artifacts["metadata"],
            artifacts["qa"],
            video,
            contact_sheet,
        )
    except CompanionValidationError as exc:
        raise ReleaseManifestError(str(exc)) from exc
    report = evaluate_layout(
        artifacts["scene"],
        contact_sheet,
        manifest,
        artifacts["storyboard"],
        artifacts["source"],
        artifacts["audit"],
    )
    failures = [finding.detail for finding in report.findings if finding.status == "fail"]
    if failures:
        raise ReleaseManifestError("release revalidation failed: " + "; ".join(failures[:8]))
