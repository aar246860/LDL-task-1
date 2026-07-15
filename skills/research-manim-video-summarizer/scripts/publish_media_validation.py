from __future__ import annotations

import json
import subprocess
from math import isfinite
from pathlib import Path


class MediaValidationError(ValueError):
    pass


def _positive_duration(value: str | int | float | None) -> bool:
    if value is None or isinstance(value, bool):
        return False
    try:
        duration = float(value)
        return isfinite(duration) and duration > 0
    except (TypeError, ValueError):
        return False


def _has_faststart(video: Path) -> bool:
    try:
        file_size = video.stat().st_size
        with video.open("rb") as stream:
            offset = 0
            boxes: dict[bytes, int] = {}
            while offset + 8 <= file_size:
                header = stream.read(8)
                if len(header) != 8:
                    return False
                size = int.from_bytes(header[:4], "big")
                box_type = header[4:8]
                header_size = 8
                if size == 1:
                    extended = stream.read(8)
                    if len(extended) != 8:
                        return False
                    size = int.from_bytes(extended, "big")
                    header_size = 16
                elif size == 0:
                    size = file_size - offset
                if size < header_size or offset + size > file_size:
                    return False
                boxes.setdefault(box_type, offset)
                stream.seek(size - header_size, 1)
                offset += size
            return b"moov" in boxes and b"mdat" in boxes and boxes[b"moov"] < boxes[b"mdat"]
    except OSError as exc:
        raise MediaValidationError(f"cannot read MP4 boxes: {exc}") from exc


def validate_browser_video(video: Path) -> None:
    command = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "stream=codec_type,codec_name,profile,pix_fmt,width,height:format=duration,format_name",
        "-of",
        "json",
        str(video),
    ]
    try:
        completed = subprocess.run(command, capture_output=True, text=True, timeout=20, check=False)
    except FileNotFoundError as exc:
        raise MediaValidationError("required executable not found: ffprobe") from exc
    except subprocess.TimeoutExpired as exc:
        raise MediaValidationError("ffprobe timed out while reading the MP4") from exc
    except OSError as exc:
        raise MediaValidationError(f"ffprobe could not start: {exc}") from exc
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip() or f"exit code {completed.returncode}"
        raise MediaValidationError(f"ffprobe rejected the MP4: {detail}")
    try:
        payload = json.loads(completed.stdout)
    except (json.JSONDecodeError, RecursionError) as exc:
        raise MediaValidationError(f"ffprobe returned invalid JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise MediaValidationError("ffprobe did not return a media object")
    streams = payload.get("streams")
    media_format = payload.get("format")
    if not isinstance(streams, list):
        raise MediaValidationError("MP4 must contain exactly one readable video stream")
    video_streams = [stream for stream in streams if isinstance(stream, dict) and stream.get("codec_type") == "video"]
    if len(video_streams) != 1:
        raise MediaValidationError("MP4 must contain exactly one readable video stream")
    if not isinstance(media_format, dict):
        raise MediaValidationError("MP4 has no readable format metadata")
    stream = video_streams[0]
    if stream.get("codec_name") != "h264" or stream.get("pix_fmt") != "yuv420p":
        raise MediaValidationError("MP4 must use H.264 video with yuv420p pixels")
    if not isinstance(stream.get("profile"), str) or not stream["profile"].strip():
        raise MediaValidationError("MP4 has no readable H.264 profile")
    width = stream.get("width")
    height = stream.get("height")
    if not isinstance(width, int) or isinstance(width, bool) or width <= 0:
        raise MediaValidationError("MP4 has no positive video width")
    if not isinstance(height, int) or isinstance(height, bool) or height <= 0:
        raise MediaValidationError("MP4 has no positive video height")
    format_name = media_format.get("format_name")
    if not isinstance(format_name, str) or "mp4" not in format_name.split(","):
        raise MediaValidationError("video container is not MP4")
    if not _positive_duration(media_format.get("duration")):
        raise MediaValidationError("MP4 has no positive finite duration")
    if not _has_faststart(video):
        raise MediaValidationError("MP4 is not faststart; the moov box must precede media data")
