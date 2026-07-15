from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path

import pytest
from PIL import Image, ImageDraw

from scripts import manim_layout_support
from scripts.check_manim_layout import evaluate_layout
from scripts.manim_layout_support import LAYOUT_REVIEW_PASS, LayoutReport, inspect_qa_manifest

FIXTURES = Path(__file__).parent / "fixtures"
GOOD_SCENE = FIXTURES / "layout_good_storyboard_mapping.py"
ONE_SCENE_SOURCE = FIXTURES / "layout_good.py"
GOOD_STORYBOARD = FIXTURES / "storyboard_good_geometry_first.md"
GOOD_VIDEO = FIXTURES / "tiny_browser_video.mp4"
GOOD_SOURCE = FIXTURES / "storyboard_source_fixture.md"
GOOD_AUDIT = FIXTURES / "storyboard_semantic_audit_good.json"


def finding_status(report: LayoutReport, check: str) -> str:
    return next(finding.status for finding in report.findings if finding.check == check)


def make_nonblank_image(path: Path, *, offset: int = 0, size: tuple[int, int] = (640, 360)) -> None:
    image = Image.new("RGB", size, "white")
    draw = ImageDraw.Draw(image)
    left = 30 + offset % 120
    draw.rectangle((left, 40, left + 180, 260), fill=(20, 90, 160), outline=(0, 0, 0), width=4)
    draw.line((20, 320 - offset % 40, 610, 80 + offset % 60), fill=(180, 40, 50), width=8)
    image.save(path)


def file_digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def write_manifest(
    directory: Path,
    scene_numbers: range | tuple[int, ...],
    *,
    contact_sheet: Path | None = None,
    scene_source: Path = GOOD_SCENE,
    storyboard: Path = GOOD_STORYBOARD,
) -> Path:
    records: list[dict[str, int | str]] = []
    for scene_number in scene_numbers:
        start = (scene_number - 1) * 36
        record: dict[str, int | str] = {
            "scene": scene_number,
            "scene_start_frame": start,
            "scene_end_frame": start + 36,
            "notes": "inspected at native resolution",
        }
        for index, state in enumerate(("entry", "midpoint", "settled")):
            frame_name = f"scene{scene_number}_{state}.png"
            make_nonblank_image(directory / frame_name, offset=scene_number * 11 + index * 17)
            record[state] = LAYOUT_REVIEW_PASS
            record[f"{state}_frame"] = frame_name
            record[f"{state}_content_summary"] = f"Scene {scene_number} {state} displays distinct reviewed geometry for this temporal state."
        records.append(record)
    manifest = directory / "qa.json"
    video = directory / "reviewed_video.mp4"
    video.write_bytes(GOOD_VIDEO.read_bytes())
    payload = {
        "reviewer": "independent QA",
        "reviewed_at": "2026-07-13T12:00:00+08:00",
        "review_method": "visual inspection",
        "browser_playback": "pass: finite duration, positive dimensions, no media error",
        "video_file": video.name,
        "video_sha256": file_digest(video),
        "scene_source_sha256": file_digest(scene_source),
        "storyboard_sha256": file_digest(storyboard),
        "source_artifact_sha256": file_digest(GOOD_SOURCE),
        "semantic_audit_sha256": file_digest(GOOD_AUDIT),
        "contact_sheet_sha256": "0" * 64 if contact_sheet is None else file_digest(contact_sheet),
        "scenes": records,
    }
    manifest.write_text(json.dumps(payload), encoding="utf-8")
    return manifest


def test_invalid_image_returns_stable_finding(tmp_path: Path) -> None:
    image = tmp_path / "not-an-image.png"
    image.write_text("not an image", encoding="utf-8")
    manifest = write_manifest(tmp_path, range(1, 11))
    report = evaluate_layout(GOOD_SCENE, image, manifest, GOOD_STORYBOARD, GOOD_SOURCE, GOOD_AUDIT)
    assert finding_status(report, "contact-sheet integrity") == "fail"


def test_blank_or_tiny_contact_sheet_fails(tmp_path: Path) -> None:
    image = tmp_path / "contact.png"
    Image.new("RGB", (64, 64), "white").save(image)
    manifest = write_manifest(tmp_path, range(1, 11))
    report = evaluate_layout(GOOD_SCENE, image, manifest, GOOD_STORYBOARD, GOOD_SOURCE, GOOD_AUDIT)
    assert finding_status(report, "contact-sheet integrity") == "fail"


def test_complete_post_render_evidence_passes() -> None:
    image = FIXTURES / "storyboard_reviewed_video_contact_sheet.png"
    manifest = FIXTURES / "visual_qa_good.json"
    assert evaluate_layout(GOOD_SCENE, image, manifest, GOOD_STORYBOARD, GOOD_SOURCE, GOOD_AUDIT).passed


def test_source_scene_count_must_match_storyboard(tmp_path: Path) -> None:
    image = tmp_path / "contact.png"
    make_nonblank_image(image)
    manifest = write_manifest(tmp_path, range(1, 11), contact_sheet=image, scene_source=ONE_SCENE_SOURCE)
    report = evaluate_layout(ONE_SCENE_SOURCE, image, manifest, GOOD_STORYBOARD, GOOD_SOURCE, GOOD_AUDIT)
    assert finding_status(report, "source scene mapping") == "fail"


def test_manifest_hashes_must_match_reviewed_artifacts(tmp_path: Path) -> None:
    image = tmp_path / "contact.png"
    make_nonblank_image(image)
    source = tmp_path / "scene.py"
    source.write_bytes(GOOD_SCENE.read_bytes())
    manifest = write_manifest(tmp_path, range(1, 11), contact_sheet=image, scene_source=source)
    source.write_text(source.read_text(encoding="utf-8") + "\n", encoding="utf-8")

    report = evaluate_layout(source, image, manifest, GOOD_STORYBOARD, GOOD_SOURCE, GOOD_AUDIT)
    assert finding_status(report, "render provenance") == "fail"


def test_checked_in_visual_qa_fixture_is_self_consistent() -> None:
    manifest = FIXTURES / "visual_qa_good.json"
    assert inspect_qa_manifest(manifest, set(range(1, 11)))[0].status == "pass"


def test_partial_post_render_evidence_fails(tmp_path: Path) -> None:
    image = tmp_path / "contact.png"
    make_nonblank_image(image)
    report = evaluate_layout(GOOD_SCENE, contact_sheet=image)
    assert finding_status(report, "post-render evidence set") == "fail"


def test_invalid_storyboard_cannot_be_certified(tmp_path: Path) -> None:
    image = tmp_path / "contact.png"
    make_nonblank_image(image)
    manifest = write_manifest(tmp_path, (1,))
    storyboard = tmp_path / "storyboard.md"
    storyboard.write_text("# no scene table\n", encoding="utf-8")
    report = evaluate_layout(GOOD_SCENE, image, manifest, storyboard, GOOD_SOURCE, GOOD_AUDIT)
    assert finding_status(report, "storyboard contract") == "fail"


def test_boolean_scene_identifier_is_rejected(tmp_path: Path) -> None:
    manifest = write_manifest(tmp_path, (1,))
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    payload["scenes"][0]["scene"] = True
    manifest.write_text(json.dumps(payload), encoding="utf-8")
    assert inspect_qa_manifest(manifest, {1})[0].status == "fail"


def test_naive_review_timestamp_is_rejected(tmp_path: Path) -> None:
    manifest = write_manifest(tmp_path, (1,))
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    payload["reviewed_at"] = "2026-07-13T12:00:00"
    manifest.write_text(json.dumps(payload), encoding="utf-8")
    assert inspect_qa_manifest(manifest, {1})[0].status == "fail"


def test_frame_evidence_must_be_distinct_and_local(tmp_path: Path) -> None:
    manifest = write_manifest(tmp_path, (1,))
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    payload["scenes"][0]["midpoint_frame"] = payload["scenes"][0]["entry_frame"]
    manifest.write_text(json.dumps(payload), encoding="utf-8")
    assert inspect_qa_manifest(manifest, {1})[0].status == "fail"

    payload["scenes"][0]["midpoint_frame"] = "../outside.png"
    manifest.write_text(json.dumps(payload), encoding="utf-8")
    assert inspect_qa_manifest(manifest, {1})[0].status == "fail"


def test_different_frame_names_cannot_reuse_identical_pixels(tmp_path: Path) -> None:
    manifest = write_manifest(tmp_path, (1,))
    entry = tmp_path / "scene1_entry.png"
    (tmp_path / "scene1_midpoint.png").write_bytes(entry.read_bytes())
    (tmp_path / "scene1_settled.png").write_bytes(entry.read_bytes())

    finding = inspect_qa_manifest(manifest, {1})[0]
    assert finding.status == "fail"
    assert "distinct decoded pixel content" in finding.detail


def test_json_recursion_returns_stable_failure(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    manifest = tmp_path / "qa.json"
    manifest.write_text("{}", encoding="utf-8")
    monkeypatch.setattr(manim_layout_support.json, "loads", lambda _value: (_ for _ in ()).throw(RecursionError()))

    finding = inspect_qa_manifest(manifest, {1})[0]
    assert finding.status == "fail"
    assert "cannot read QA manifest" in finding.detail
