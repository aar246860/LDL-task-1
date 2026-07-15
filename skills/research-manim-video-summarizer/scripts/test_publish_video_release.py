from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest
import typer
from PIL import Image

from scripts import publish_media_validation, publish_package_validation, publish_video_release
from scripts.release_test_support import make_package, write_nonblank_image

FIXTURES = Path(__file__).parent / "fixtures"


def test_live_publish_requires_explicit_confirmation(tmp_path: Path) -> None:
    with pytest.raises(typer.BadParameter, match="requires --confirm-publish"):
        publish_video_release.main(
            package_dir=tmp_path,
            github_repo="owner/repo",
            release_tag="v1",
            release_title="Release",
            publish="release",
            dry_run=False,
            confirm_publish=False,
        )


def test_dry_run_never_executes_external_command(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    make_package(tmp_path)

    def reject_command(command: list[str], *, check: bool) -> publish_video_release.CommandResult:
        raise AssertionError((command, check))

    monkeypatch.setattr(publish_video_release, "run_command", reject_command)
    publish_video_release.main(
        package_dir=tmp_path,
        github_repo="owner/repo",
        release_tag="v1",
        release_title="Release",
        publish="release",
        dry_run=True,
        confirm_publish=False,
    )


@pytest.mark.parametrize("secret_name", ("secrets.env", "secrets.html", "notes.txt"))
def test_package_rejects_any_unrecognized_file(secret_name: str, tmp_path: Path) -> None:
    make_package(tmp_path)
    (tmp_path / secret_name).write_text("sensitive", encoding="utf-8")

    with pytest.raises(typer.BadParameter, match="non-publishable"):
        publish_video_release.collect_package(tmp_path)


def test_invalid_repository_and_tag_are_rejected(tmp_path: Path) -> None:
    make_package(tmp_path)
    with pytest.raises(typer.BadParameter, match="OWNER/REPO"):
        publish_video_release.main(
            package_dir=tmp_path,
            github_repo="owner/repo/extra",
            release_tag="v1",
            release_title="Release",
            publish="release",
            dry_run=True,
            confirm_publish=False,
        )
    with pytest.raises(typer.BadParameter, match="release tag"):
        publish_video_release.main(
            package_dir=tmp_path,
            github_repo="owner/repo",
            release_tag="../v1",
            release_title="Release",
            publish="release",
            dry_run=True,
            confirm_publish=False,
        )


def test_missing_external_command_has_stable_error(monkeypatch: pytest.MonkeyPatch) -> None:
    def missing_command(command: list[str], *, capture_output: bool, text: bool, timeout: int) -> None:
        _ = (command, capture_output, text, timeout)
        raise FileNotFoundError("missing")

    monkeypatch.setattr(publish_video_release.subprocess, "run", missing_command)
    with pytest.raises(publish_video_release.PublishCommandError, match="required executable"):
        publish_video_release.run_command(["gh", "--version"], check=True)


def test_command_timeout_has_stable_error(monkeypatch: pytest.MonkeyPatch) -> None:
    def timeout_command(command: list[str], *, capture_output: bool, text: bool, timeout: int) -> None:
        _ = (command, capture_output, text, timeout)
        raise publish_video_release.subprocess.TimeoutExpired(command, timeout)

    monkeypatch.setattr(publish_video_release.subprocess, "run", timeout_command)
    with pytest.raises(publish_video_release.PublishCommandError, match="timed out"):
        publish_video_release.run_command(["gh", "--version"], check=True)


def test_package_rejects_empty_visual_qa_manifest(tmp_path: Path) -> None:
    make_package(tmp_path)
    (tmp_path / "summary_visual_qa.json").write_text("{}", encoding="utf-8")

    with pytest.raises(typer.BadParameter, match="named reviewer"):
        publish_video_release.collect_package(tmp_path)


def test_package_rejects_json_recursion(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    make_package(tmp_path)
    monkeypatch.setattr(
        publish_package_validation,
        "json",
        SimpleNamespace(
            JSONDecodeError=json.JSONDecodeError,
            loads=lambda _value: (_ for _ in ()).throw(RecursionError()),
        ),
    )

    with pytest.raises(typer.BadParameter, match="cannot read visual-QA manifest"):
        publish_video_release.collect_package(tmp_path)


def test_package_rejects_unreferenced_frame(tmp_path: Path) -> None:
    make_package(tmp_path)
    write_nonblank_image(tmp_path / "scene11_entry.png")

    with pytest.raises(typer.BadParameter, match="do not match"):
        publish_video_release.collect_package(tmp_path)


def test_package_rejects_blank_frame_evidence(tmp_path: Path) -> None:
    make_package(tmp_path)
    Image.new("RGB", (320, 180), "white").save(tmp_path / "scene1_midpoint.png")

    with pytest.raises(typer.BadParameter, match="blank or nearly uniform"):
        publish_video_release.collect_package(tmp_path)


def test_package_rejects_corrupt_mp4(tmp_path: Path) -> None:
    make_package(tmp_path)
    (tmp_path / "summary.mp4").write_bytes(b"not an mp4")

    with pytest.raises(typer.BadParameter, match="ffprobe rejected the MP4"):
        publish_video_release.collect_package(tmp_path)


def test_package_rejects_video_hash_mismatch(tmp_path: Path) -> None:
    make_package(tmp_path)
    manifest = tmp_path / "summary_visual_qa.json"
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    payload["video_sha256"] = "0" * 64
    manifest.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(typer.BadParameter, match="does not match the package MP4"):
        publish_video_release.collect_package(tmp_path)


def test_package_rejects_source_artifact_hash_mismatch(tmp_path: Path) -> None:
    make_package(tmp_path)
    source = tmp_path / "summary_source.md"
    source.write_text(source.read_text(encoding="utf-8") + "\naltered\n", encoding="utf-8")

    with pytest.raises(typer.BadParameter, match=r"does not match summary_source\.md"):
        publish_video_release.collect_package(tmp_path)


def test_missing_ffprobe_has_stable_error(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    video = tmp_path / "video.mp4"
    video.write_bytes(b"content")

    def missing_probe(*_args, **_kwargs) -> None:
        raise FileNotFoundError("missing")

    monkeypatch.setattr(publish_media_validation.subprocess, "run", missing_probe)
    with pytest.raises(publish_media_validation.MediaValidationError, match="required executable"):
        publish_media_validation.validate_browser_video(video)


def test_package_rejects_symbolic_links(tmp_path: Path) -> None:
    make_package(tmp_path)
    target = tmp_path / "target.bin"
    target.write_bytes(b"outside")
    link = tmp_path / "scene2_entry.png"
    try:
        link.symlink_to(target)
    except OSError:
        pytest.skip("symbolic links are unavailable on this host")

    with pytest.raises(typer.BadParameter, match="symbolic links"):
        publish_video_release.collect_package(tmp_path)
