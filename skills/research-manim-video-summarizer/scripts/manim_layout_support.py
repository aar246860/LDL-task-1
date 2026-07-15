from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
from pathlib import Path

from scripts.image_evidence import image_fingerprint, image_issue
from scripts.publish_media_validation import MediaValidationError, validate_browser_video
from scripts.storyboard_schema import substantive

LAYOUT_REVIEW_PASS = "pass: overlap-free and within-frame"


@dataclass(frozen=True, slots=True)
class LayoutFinding:
    check: str
    status: str
    detail: str
    line: int | None = None


@dataclass(frozen=True, slots=True)
class LayoutReport:
    passed: bool
    findings: list[LayoutFinding]


def inspect_contact_sheet(contact_sheet: Path) -> list[LayoutFinding]:
    issue = image_issue(contact_sheet, minimum_width=320, minimum_height=180)
    if issue is not None:
        return [
            LayoutFinding(
                check="contact-sheet integrity",
                status="fail",
                detail=issue,
            ),
        ]
    return [
        LayoutFinding(
            check="contact-sheet integrity",
            status="pass",
            detail="image is readable and nonblank; this technical check does not prove collision freedom",
        ),
    ]


def _valid_review_time(value: str) -> bool:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return parsed.tzinfo is not None and parsed.utcoffset() is not None


def _frame_path(manifest: Path, value: str) -> Path | None:
    candidate = Path(value)
    if candidate.is_absolute():
        return None
    resolved = (manifest.parent / candidate).resolve()
    try:
        resolved.relative_to(manifest.parent.resolve())
    except ValueError:
        return None
    return resolved


def _file_digest(path: Path) -> str | None:
    try:
        return sha256(path.read_bytes()).hexdigest()
    except OSError:
        return None


def inspect_qa_provenance(
    manifest: Path,
    scene_source: Path,
    storyboard: Path,
    contact_sheet: Path,
    source_artifact: Path,
    semantic_audit: Path,
) -> list[LayoutFinding]:
    try:
        payload = json.loads(manifest.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError, RecursionError) as exc:
        return [LayoutFinding(check="render provenance", status="fail", detail=f"cannot read QA manifest: {exc}")]
    if not isinstance(payload, dict):
        return [LayoutFinding(check="render provenance", status="fail", detail="QA manifest must be a JSON object")]
    expected = {
        "scene_source_file": scene_source.name,
        "scene_source_sha256": _file_digest(scene_source),
        "storyboard_file": storyboard.name,
        "storyboard_sha256": _file_digest(storyboard),
        "contact_sheet_file": contact_sheet.name,
        "contact_sheet_sha256": _file_digest(contact_sheet),
        "source_artifact_file": source_artifact.name,
        "source_artifact_sha256": _file_digest(source_artifact),
        "semantic_audit_file": semantic_audit.name,
        "semantic_audit_sha256": _file_digest(semantic_audit),
    }
    invalid = [field for field, digest in expected.items() if payload.get(field) != digest or digest is None]
    video_value = payload.get("video_file")
    video = _frame_path(manifest, video_value) if isinstance(video_value, str) else None
    video_digest = None if video is None else _file_digest(video)
    if video is None or video.suffix.lower() != ".mp4":
        invalid.append("video_file")
    elif payload.get("video_sha256") != video_digest or video_digest is None:
        invalid.append("video_sha256")
    else:
        try:
            validate_browser_video(video)
        except MediaValidationError as exc:
            invalid.append(f"video validation: {exc}")
    for file_field, hash_field in (
        ("html_file", "html_sha256"),
        ("metadata_file", "metadata_sha256"),
        ("qa_notes_file", "qa_notes_sha256"),
    ):
        value = payload.get(file_field)
        artifact = _frame_path(manifest, value) if isinstance(value, str) else None
        digest = None if artifact is None else _file_digest(artifact)
        if artifact is None or payload.get(hash_field) != digest or digest is None:
            invalid.append(file_field)
    if invalid:
        return [
            LayoutFinding(
                check="render provenance",
                status="fail",
                detail=f"manifest does not match reviewed artifacts: {', '.join(invalid[:6])}",
            ),
        ]
    return [
        LayoutFinding(
            check="render provenance",
            status="pass",
            detail="manifest hashes match source code, storyboard, research source, semantic audit, contact sheet, and MP4",
        ),
    ]


def inspect_qa_manifest(manifest: Path, expected_scenes: set[int]) -> list[LayoutFinding]:
    if not expected_scenes:
        return [LayoutFinding(check="visual QA manifest", status="fail", detail="expected scene set is empty")]
    try:
        payload = json.loads(manifest.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError, RecursionError) as exc:
        return [LayoutFinding(check="visual QA manifest", status="fail", detail=f"cannot read QA manifest: {exc}")]
    if not isinstance(payload, dict) or not isinstance(payload.get("reviewer"), str) or not payload["reviewer"].strip():
        return [LayoutFinding(check="visual QA manifest", status="fail", detail="manifest needs a named reviewer")]
    reviewed_at = payload.get("reviewed_at")
    if not isinstance(reviewed_at, str) or not _valid_review_time(reviewed_at):
        return [LayoutFinding(check="visual QA manifest", status="fail", detail="manifest needs an ISO reviewed_at time")]
    if payload.get("review_method") != "visual inspection":
        return [LayoutFinding(check="visual QA manifest", status="fail", detail="review_method must be visual inspection")]
    if payload.get("browser_playback") != "pass: finite duration, positive dimensions, no media error":
        return [LayoutFinding(check="visual QA manifest", status="fail", detail="browser playback review is incomplete")]
    records = payload.get("scenes")
    if not isinstance(records, list):
        return [LayoutFinding(check="visual QA manifest", status="fail", detail="manifest needs a scenes list")]
    seen: list[int] = []
    frame_paths: list[Path] = []
    invalid: list[str] = []
    for record in records:
        scene_value = record.get("scene") if isinstance(record, dict) else None
        if not isinstance(scene_value, int) or isinstance(scene_value, bool):
            invalid.append("record without integer scene")
            continue
        scene_number = scene_value
        seen.append(scene_number)
        scene_fingerprints: list[str] = []
        start = record.get("scene_start_frame")
        end = record.get("scene_end_frame")
        if not isinstance(start, int) or isinstance(start, bool) or not isinstance(end, int) or isinstance(end, bool) or end <= start:
            invalid.append(f"Scene {scene_number} has no valid frame range")
        for state in ("entry", "midpoint", "settled"):
            if record.get(state) != LAYOUT_REVIEW_PASS:
                invalid.append(f"Scene {scene_number} {state} is not overlap-free and within-frame")
            summary = record.get(f"{state}_content_summary")
            if not isinstance(summary, str) or not substantive(summary, minimum_units=6):
                invalid.append(f"Scene {scene_number} {state} lacks a substantive visual summary")
            frame_value = record.get(f"{state}_frame")
            if not isinstance(frame_value, str) or not frame_value.strip():
                invalid.append(f"Scene {scene_number} {state} has no frame evidence")
                continue
            frame = _frame_path(manifest, frame_value)
            if frame is None:
                invalid.append(f"Scene {scene_number} {state} frame escapes the evidence directory")
                continue
            frame_paths.append(frame)
            issue = image_issue(frame, minimum_width=320, minimum_height=180)
            if issue is not None:
                invalid.append(f"Scene {scene_number} {state} {issue}")
                continue
            fingerprint = image_fingerprint(frame)
            if fingerprint is None:
                invalid.append(f"Scene {scene_number} {state} cannot fingerprint frame evidence")
            else:
                scene_fingerprints.append(fingerprint)
        if len(scene_fingerprints) == 3 and len(set(scene_fingerprints)) != 3:
            invalid.append(
                f"Scene {scene_number} entry, midpoint, and settled images lack distinct decoded pixel content",
            )
    if len(seen) != len(set(seen)):
        invalid.append("scene records are duplicated")
    if set(seen) != expected_scenes:
        invalid.append(f"scene coverage is {sorted(set(seen))}; expected {sorted(expected_scenes)}")
    if len(frame_paths) != len(set(frame_paths)):
        invalid.append("each entry, midpoint, and settled state needs a distinct frame file")
    if invalid:
        return [LayoutFinding(check="visual QA manifest", status="fail", detail="; ".join(invalid[:8]))]
    return [
        LayoutFinding(
            check="visual QA manifest",
            status="pass",
            detail=f"{len(seen)} scenes record entry, midpoint, and settled visual review with distinct frame evidence",
        ),
    ]
