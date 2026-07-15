from __future__ import annotations

import json
from pathlib import Path

import pytest
import typer
from PIL import Image

from scripts import publish_media_validation, publish_video_release
from scripts.export_package_content import player_html
from scripts.release_test_support import file_digest, make_package, write_nonblank_image

FIXTURES = Path(__file__).parent / "fixtures"


def test_package_rejects_multiple_contact_sheets(tmp_path: Path) -> None:
    make_package(tmp_path)
    write_nonblank_image(tmp_path / "summary_contact_sheet.jpg")
    with pytest.raises(typer.BadParameter, match="exactly one contact sheet"):
        publish_video_release.collect_package(tmp_path)


def test_jpeg_contact_sheet_is_accepted(tmp_path: Path) -> None:
    make_package(tmp_path)
    png = tmp_path / "summary_contact_sheet.png"
    jpeg = tmp_path / "summary_contact_sheet.jpeg"
    with Image.open(png) as image:
        image.convert("RGB").save(jpeg, format="JPEG")
    png.unlink()
    manifest = tmp_path / "summary_visual_qa.json"
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    html = tmp_path / "summary.html"
    html.write_text(
        player_html(
            title="Atomic research story fixture",
            description="Release validation fixture with ten independently reviewed scenes.",
            mp4_name="summary.mp4",
            contact_sheet_name=jpeg.name,
        ),
        encoding="utf-8",
    )
    metadata = tmp_path / "summary_metadata.json"
    metadata_payload = json.loads(metadata.read_text(encoding="utf-8"))
    metadata_payload["artifacts"]["contact_sheet"] = jpeg.name
    metadata.write_text(json.dumps(metadata_payload), encoding="utf-8")
    payload["contact_sheet_file"] = jpeg.name
    payload["contact_sheet_sha256"] = file_digest(jpeg)
    payload["html_sha256"] = file_digest(html)
    payload["metadata_sha256"] = file_digest(metadata)
    manifest.write_text(json.dumps(payload), encoding="utf-8")
    assert publish_video_release.collect_package(tmp_path).contact_sheets == [jpeg]


def test_two_video_streams_are_rejected() -> None:
    video = FIXTURES / "tiny_two_stream_video.mp4"
    with pytest.raises(publish_media_validation.MediaValidationError, match="exactly one"):
        publish_media_validation.validate_browser_video(video)


def test_permission_error_has_stable_publish_error(monkeypatch: pytest.MonkeyPatch) -> None:
    def deny(*_args, **_kwargs) -> None:
        raise PermissionError("blocked")

    monkeypatch.setattr(publish_video_release.subprocess, "run", deny)
    with pytest.raises(publish_video_release.PublishCommandError, match="cannot execute gh"):
        publish_video_release.run_command(["gh", "--version"], check=True)
