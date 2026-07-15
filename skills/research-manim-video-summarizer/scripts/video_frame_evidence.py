from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass
from hashlib import sha256
from itertools import pairwise
from pathlib import Path
from typing import Final

from PIL import Image, UnidentifiedImageError

from scripts.json_mapping import as_object_map
from scripts.manim_layout_support import LayoutFinding

HASH_PATTERN: Final = re.compile(r"^[0-9a-f]{64}$")
STATES: Final = ("entry", "midpoint", "settled")
PHASE_WINDOWS: Final = {"entry": (0.10, 0.35), "midpoint": (0.40, 0.65), "settled": (0.70, 0.95)}


@dataclass(frozen=True, slots=True)
class EvidenceFrame:
    scene: int
    state: str
    path: Path
    index: int
    rgb_digest: str
    size: tuple[int, int]


def _local_path(manifest: Path, value: object) -> Path | None:
    if not isinstance(value, str) or not value.strip():
        return None
    candidate = Path(value)
    if candidate.is_absolute():
        return None
    resolved = (manifest.parent / candidate).resolve()
    try:
        resolved.relative_to(manifest.parent.resolve())
    except ValueError:
        return None
    return resolved


def _read_frame(
    manifest: Path,
    record: dict[str, object],
    scene: int,
    state: str,
    invalid: list[str],
) -> EvidenceFrame | None:
    path = _local_path(manifest, record.get(f"{state}_frame"))
    if path is None:
        invalid.append(f"Scene {scene} {state} frame is not a local evidence file")
        return None
    index = record.get(f"{state}_frame_index")
    if not isinstance(index, int) or isinstance(index, bool) or not 0 <= index <= 1_000_000:
        invalid.append(f"Scene {scene} {state} has an invalid frame index")
        return None
    expected_digest = record.get(f"{state}_frame_sha256")
    try:
        content = path.read_bytes()
        with Image.open(path) as image:
            rgb = image.convert("RGB")
            size = rgb.size
            pixels = rgb.tobytes()
    except (OSError, UnidentifiedImageError, Image.DecompressionBombError) as exc:
        invalid.append(f"Scene {scene} {state} frame cannot be read: {exc}")
        return None
    actual_digest = sha256(content).hexdigest()
    if not isinstance(expected_digest, str) or HASH_PATTERN.fullmatch(expected_digest) is None:
        invalid.append(f"Scene {scene} {state} has no valid frame SHA-256")
    elif expected_digest != actual_digest:
        invalid.append(f"Scene {scene} {state} frame SHA-256 does not match")
    return EvidenceFrame(scene, state, path, index, sha256(pixels).hexdigest(), size)


def _decode_selected_frames(video: Path, frames: list[EvidenceFrame]) -> tuple[list[str], str | None]:
    selector = "+".join(f"eq(n\\,{frame.index})" for frame in frames)
    command = [
        "ffmpeg",
        "-v",
        "error",
        "-i",
        str(video),
        "-vf",
        f"select={selector}",
        "-fps_mode",
        "passthrough",
        "-f",
        "rawvideo",
        "-pix_fmt",
        "rgb24",
        "pipe:1",
    ]
    try:
        completed = subprocess.run(command, capture_output=True, timeout=90, check=False)
    except FileNotFoundError:
        return [], "required executable not found: ffmpeg"
    except subprocess.TimeoutExpired:
        return [], "ffmpeg timed out while decoding reviewed frames"
    except OSError as exc:
        return [], f"ffmpeg could not start: {exc}"
    if completed.returncode != 0:
        detail = completed.stderr.decode("utf-8", errors="replace").strip()
        return [], f"ffmpeg rejected reviewed frames: {detail[:240] or completed.returncode}"
    width, height = frames[0].size
    chunk_size = width * height * 3
    if len(completed.stdout) != chunk_size * len(frames):
        return [], "reviewed frame indices or dimensions do not match the MP4"
    digests = [sha256(completed.stdout[offset : offset + chunk_size]).hexdigest() for offset in range(0, len(completed.stdout), chunk_size)]
    return digests, None


def _video_frame_count(video: Path) -> tuple[int | None, str | None]:
    command = [
        "ffprobe",
        "-v",
        "error",
        "-count_frames",
        "-select_streams",
        "v:0",
        "-show_entries",
        "stream=nb_read_frames",
        "-of",
        "json",
        str(video),
    ]
    try:
        completed = subprocess.run(command, capture_output=True, text=True, timeout=30, check=False)
    except FileNotFoundError:
        return None, "required executable not found: ffprobe"
    except subprocess.TimeoutExpired:
        return None, "ffprobe timed out while counting video frames"
    except OSError as exc:
        return None, f"ffprobe could not start: {exc}"
    if completed.returncode != 0:
        return None, "ffprobe could not count video frames"
    try:
        payload_value: object = json.loads(completed.stdout)
        payload = as_object_map(payload_value)
        streams = payload.get("streams") if payload is not None else None
        stream = as_object_map(streams[0]) if isinstance(streams, list) and streams else None
        value = stream.get("nb_read_frames") if stream is not None else None
        count = int(value) if isinstance(value, str) else -1
    except (ValueError, json.JSONDecodeError, RecursionError):
        return None, "ffprobe returned an invalid video frame count"
    return (count, None) if count > 0 else (None, "MP4 has no positive decoded frame count")


def _scene_sort_key(record: dict[str, object]) -> int:
    value = record.get("scene")
    return value if isinstance(value, int) and not isinstance(value, bool) else -1


def inspect_video_frame_evidence(manifest: Path) -> LayoutFinding:
    try:
        payload_value: object = json.loads(manifest.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError, RecursionError) as exc:
        return LayoutFinding(check="video-frame evidence", status="fail", detail=f"cannot read QA manifest: {exc}")
    payload = as_object_map(payload_value)
    scene_values = None if payload is None else payload.get("scenes")
    if payload is None or not isinstance(scene_values, list):
        return LayoutFinding(check="video-frame evidence", status="fail", detail="QA manifest needs scene records")
    video = _local_path(manifest, payload.get("video_file"))
    if video is None or video.suffix.lower() != ".mp4":
        return LayoutFinding(check="video-frame evidence", status="fail", detail="QA manifest needs a local MP4")

    invalid: list[str] = []
    frames: list[EvidenceFrame] = []
    ranges: list[tuple[int, int, int]] = []
    records = [record for value in scene_values if (record := as_object_map(value)) is not None]
    records.sort(key=_scene_sort_key)
    for record in records:
        scene = record.get("scene")
        if not isinstance(scene, int) or isinstance(scene, bool):
            invalid.append("scene record has no integer identifier")
            continue
        start = record.get("scene_start_frame")
        end = record.get("scene_end_frame")
        if not isinstance(start, int) or isinstance(start, bool) or not isinstance(end, int) or isinstance(end, bool) or end <= start:
            invalid.append(f"Scene {scene} has an invalid frame range")
            continue
        ranges.append((scene, start, end))
        for state in STATES:
            frame = _read_frame(manifest, record, scene, state, invalid)
            if frame is not None:
                frames.append(frame)
                position = (frame.index - start) / max(1, end - start - 1)
                lower, upper = PHASE_WINDOWS[state]
                if not lower <= position <= upper:
                    invalid.append(f"Scene {scene} {state} index is outside its temporal phase window")
    if not frames:
        invalid.append("no readable frame evidence")
    elif len({frame.size for frame in frames}) != 1:
        invalid.append("all evidence frames must have the same dimensions")
    indices = [frame.index for frame in frames]
    if indices != sorted(indices) or len(indices) != len(set(indices)):
        invalid.append("frame indices must be globally unique and increase in scene-state order")
    rgb_digests = [frame.rgb_digest for frame in frames]
    if len(rgb_digests) != len(set(rgb_digests)):
        invalid.append("decoded evidence pixels must be globally unique across all scene states")
    if ranges:
        if ranges[0][1] != 0 or any(previous[2] != current[1] for previous, current in pairwise(ranges)):
            invalid.append("scene frame ranges must be contiguous from frame zero")
        frame_count, count_error = _video_frame_count(video)
        if count_error is not None:
            invalid.append(count_error)
        elif ranges[-1][2] != frame_count:
            invalid.append("scene frame ranges do not cover the complete MP4")
    if invalid:
        return LayoutFinding(check="video-frame evidence", status="fail", detail="; ".join(invalid[:8]))

    decoded_digests, decode_error = _decode_selected_frames(video, frames)
    if decode_error is not None:
        return LayoutFinding(check="video-frame evidence", status="fail", detail=decode_error)
    mismatches = [f"Scene {frame.scene} {frame.state}" for frame, decoded in zip(frames, decoded_digests, strict=True) if frame.rgb_digest != decoded]
    if mismatches:
        return LayoutFinding(
            check="video-frame evidence",
            status="fail",
            detail=f"evidence images do not decode from the reviewed MP4: {', '.join(mismatches[:6])}",
        )
    return LayoutFinding(
        check="video-frame evidence",
        status="pass",
        detail=f"{len(frames)} hash-bound images exactly match unique decoded MP4 frames",
    )
