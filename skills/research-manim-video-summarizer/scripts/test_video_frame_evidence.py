from __future__ import annotations

import ast
import json
import shutil
from hashlib import sha256
from pathlib import Path
from typing import Any

from PIL import Image

from scripts.storyboard_schema import parse_storyboard
from scripts.storyboard_source_mapping import inspect_source_scene_mapping
from scripts.storyboard_visual_audit import inspect_storyboard_visual_match
from scripts.video_frame_evidence import inspect_video_frame_evidence

FIXTURES = Path(__file__).parent / "fixtures"
GOLD_MANIFEST = FIXTURES / "visual_qa_good.json"


def copy_gold_evidence(directory: Path) -> Path:
    manifest = directory / "visual_qa_good.json"
    shutil.copy2(GOLD_MANIFEST, manifest)
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    shutil.copy2(FIXTURES / payload["video_file"], directory / payload["video_file"])
    frame_directory = directory / "visual_qa_frames"
    frame_directory.mkdir()
    for record in payload["scenes"]:
        for state in ("entry", "midpoint", "settled"):
            frame = Path(record[f"{state}_frame"])
            shutil.copy2(FIXTURES / frame, directory / frame)
    return manifest


def mutate_manifest(manifest: Path, mutate) -> None:
    payload: dict[str, Any] = json.loads(manifest.read_text(encoding="utf-8"))
    mutate(payload)
    manifest.write_text(json.dumps(payload), encoding="utf-8")


def test_cross_scene_pixel_reuse_fails_globally(tmp_path: Path) -> None:
    manifest = copy_gold_evidence(tmp_path)
    first = tmp_path / "visual_qa_frames/scene1_entry.png"
    reused = tmp_path / "visual_qa_frames/scene2_entry.png"
    shutil.copy2(first, reused)

    def update_hash(payload: dict[str, Any]) -> None:
        payload["scenes"][1]["entry_frame_sha256"] = sha256(reused.read_bytes()).hexdigest()

    mutate_manifest(manifest, update_hash)
    finding = inspect_video_frame_evidence(manifest)
    assert finding.status == "fail"
    assert "globally unique" in finding.detail


def test_frame_mutation_after_manifest_creation_fails(tmp_path: Path) -> None:
    manifest = copy_gold_evidence(tmp_path)
    frame = tmp_path / "visual_qa_frames/scene1_entry.png"
    with Image.open(frame) as image:
        changed = image.convert("RGB")
    changed.putpixel((0, 0), (12, 34, 56))
    changed.save(frame)

    finding = inspect_video_frame_evidence(manifest)
    assert finding.status == "fail"
    assert "SHA-256 does not match" in finding.detail


def test_unrelated_mp4_cannot_support_reviewed_frames(tmp_path: Path) -> None:
    manifest = copy_gold_evidence(tmp_path)
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    video = tmp_path / payload["video_file"]
    shutil.copy2(FIXTURES / "tiny_browser_video.mp4", video)

    finding = inspect_video_frame_evidence(manifest)
    assert finding.status == "fail"
    assert "MP4" in finding.detail or "ffmpeg" in finding.detail


def test_visual_object_and_ownership_must_match_storyboard(tmp_path: Path) -> None:
    manifest = copy_gold_evidence(tmp_path)

    def replace_visual(payload: dict[str, Any]) -> None:
        payload["scenes"][0]["storyboard_visual_object"] = "A generic circle appears without the stated physical pile comparison."
        payload["scenes"][3]["storyboard_ownership"] = "M02"

    mutate_manifest(manifest, replace_visual)
    board = parse_storyboard((FIXTURES / "storyboard_good_geometry_first.md").read_text(encoding="utf-8"))
    finding = inspect_storyboard_visual_match(manifest, board)
    assert finding.status == "fail"
    assert "visual object does not match" in finding.detail
    assert "ownership does not match" in finding.detail


def test_source_helper_suffix_must_match_scene_ownership() -> None:
    source = (FIXTURES / "layout_good_storyboard_mapping.py").read_text(encoding="utf-8")
    tree = ast.parse(source.replace("scene_04_m01_select", "scene_04_m02_select"))
    roles = {1: "b01", 2: "b02", 3: "b03", 4: "m01", 5: "m02", 6: "m03", 7: "m04", 8: "m05", 9: "m06", 10: "return"}
    finding = inspect_source_scene_mapping(tree, roles)
    assert finding.status == "fail"
    assert "ownership" in finding.detail


def test_source_mapping_requires_a_manim_scene_subclass() -> None:
    tree = ast.parse(
        "class Pretender:\n    def construct(self):\n        self.scene_01_b01_hook()\n    def scene_01_b01_hook(self):\n        self.add(object())\n"
    )
    finding = inspect_source_scene_mapping(tree, {1: "b01"})
    assert finding.status == "fail"
    assert "exactly one Scene class" in finding.detail
