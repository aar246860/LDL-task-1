from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest
import typer

from scripts import publish_video_release
from scripts.release_test_support import file_digest, make_package


def _manifest(directory: Path) -> Path:
    return directory / "summary_visual_qa.json"


def _refresh_hash(directory: Path, role: str) -> None:
    manifest = _manifest(directory)
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    artifact = directory / payload[f"{role}_file"]
    payload[f"{role}_sha256"] = file_digest(artifact)
    manifest.write_text(json.dumps(payload), encoding="utf-8")


def test_revalidation_rejects_scene_without_layout_guards(tmp_path: Path) -> None:
    make_package(tmp_path)
    scene = tmp_path / "summary_scene.py"
    scene.write_text(scene.read_text(encoding="utf-8").replace("assert_scene_layout(", "assert_within_frame("), encoding="utf-8")
    _refresh_hash(tmp_path, "scene_source")

    with pytest.raises(typer.BadParameter, match="release revalidation failed"):
        publish_video_release.collect_package(tmp_path)


def test_revalidation_rejects_failed_semantic_audit(tmp_path: Path) -> None:
    make_package(tmp_path)
    audit = tmp_path / "summary_semantic_audit.json"
    payload = json.loads(audit.read_text(encoding="utf-8"))
    payload["decision"] = "fail"
    audit.write_text(json.dumps(payload), encoding="utf-8")
    _refresh_hash(tmp_path, "semantic_audit")

    with pytest.raises(typer.BadParameter, match="release revalidation failed"):
        publish_video_release.collect_package(tmp_path)


def test_swapped_provenance_roles_are_rejected_after_rehash(tmp_path: Path) -> None:
    make_package(tmp_path)
    scene = tmp_path / "summary_scene.py"
    storyboard = tmp_path / "summary_storyboard.md"
    scene_bytes, storyboard_bytes = scene.read_bytes(), storyboard.read_bytes()
    scene.write_bytes(storyboard_bytes)
    storyboard.write_bytes(scene_bytes)
    _refresh_hash(tmp_path, "scene_source")
    _refresh_hash(tmp_path, "storyboard")

    with pytest.raises(typer.BadParameter, match="release revalidation failed"):
        publish_video_release.collect_package(tmp_path)


@pytest.mark.parametrize(
    "case",
    (
        ("summary.html", "html", "<video controls></video>", "HTML player"),
        ("summary_metadata.json", "metadata", "{}", "metadata"),
        ("summary_qa.md", "qa_notes", "thin review", "QA notes"),
    ),
)
def test_companion_content_is_revalidated_after_rehash(tmp_path: Path, case: tuple[str, str, str, str]) -> None:
    name, role, content, message = case
    make_package(tmp_path)
    (tmp_path / name).write_text(content, encoding="utf-8")
    _refresh_hash(tmp_path, role)

    with pytest.raises(typer.BadParameter, match=message):
        publish_video_release.collect_package(tmp_path)


def test_duplicate_source_role_is_rejected(tmp_path: Path) -> None:
    make_package(tmp_path)
    shutil.copy2(tmp_path / "summary_source.md", tmp_path / "summary_source.txt")

    with pytest.raises(typer.BadParameter, match="exactly one file for each provenance role"):
        publish_video_release.collect_package(tmp_path)


def test_nested_package_content_is_rejected(tmp_path: Path) -> None:
    make_package(tmp_path)
    (tmp_path / "nested").mkdir()

    with pytest.raises(typer.BadParameter, match="must be flat"):
        publish_video_release.collect_package(tmp_path)


def test_non_faststart_mp4_is_rejected_after_rehash(tmp_path: Path) -> None:
    make_package(tmp_path)
    video = tmp_path / "summary.mp4"
    remuxed = tmp_path / "remuxed.mp4"
    try:
        completed = subprocess.run(
            ["ffmpeg", "-y", "-v", "error", "-i", str(video), "-c", "copy", str(remuxed)],
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
    except FileNotFoundError:
        pytest.skip("ffmpeg is unavailable")
    assert completed.returncode == 0, completed.stderr
    remuxed.replace(video)
    manifest = _manifest(tmp_path)
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    payload["video_sha256"] = file_digest(video)
    manifest.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(typer.BadParameter, match="not faststart"):
        publish_video_release.collect_package(tmp_path)


def test_existing_release_tag_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_run(command: list[str], *, check: bool) -> publish_video_release.CommandResult:
        assert check is False
        return publish_video_release.CommandResult(stdout="existing", stderr="", returncode=0)

    monkeypatch.setattr(publish_video_release, "run_command", fake_run)

    with pytest.raises(publish_video_release.PublishCommandError, match="already exists"):
        publish_video_release.ensure_release("owner/repo", "v1", "title", "notes", dry_run=False)


def test_existing_git_tag_without_release_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    commands: list[list[str]] = []

    def fake_run(command: list[str], *, check: bool) -> publish_video_release.CommandResult:
        commands.append(command)
        return publish_video_release.CommandResult(
            stdout="tag" if "api" in command else "",
            stderr="release not found" if "api" not in command else "",
            returncode=0 if "api" in command else 1,
        )

    monkeypatch.setattr(publish_video_release, "run_command", fake_run)

    with pytest.raises(publish_video_release.PublishCommandError, match="already exists"):
        publish_video_release.ensure_release("owner/repo", "v1", "title", "notes", dry_run=False)
    assert any(command[:2] == ["gh", "api"] for command in commands)


def test_repository_lookup_failure_is_fail_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    commands: list[list[str]] = []

    def fake_run(command: list[str], *, check: bool) -> publish_video_release.CommandResult:
        commands.append(command)
        return publish_video_release.CommandResult(stdout="", stderr="repository not found", returncode=1)

    monkeypatch.setattr(publish_video_release, "run_command", fake_run)

    with pytest.raises(publish_video_release.PublishCommandError, match="cannot establish"):
        publish_video_release.ensure_release("owner/repo", "v1", "title", "notes", dry_run=False)
    assert not any(command[2:4] == ["release", "create"] for command in commands)


def test_upload_command_cannot_clobber_remote_assets(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    make_package(tmp_path)
    package = publish_video_release.collect_package(tmp_path)
    captured: list[str] = []

    def fake_run(command: list[str], *, check: bool) -> publish_video_release.CommandResult:
        captured.extend(command)
        return publish_video_release.CommandResult(stdout="", stderr="", returncode=0)

    monkeypatch.setattr(publish_video_release, "run_command", fake_run)
    publish_video_release.upload_assets(package, "owner/repo", "v1", dry_run=False)

    assert "--clobber" not in captured


def test_stage_package_revalidates_an_immutable_copy(tmp_path: Path) -> None:
    make_package(tmp_path)
    package = publish_video_release.collect_package(tmp_path)
    staged = publish_video_release.stage_package(package, tmp_path / "staged")

    assert [path.name for path in staged.assets] == [path.name for path in package.assets]
