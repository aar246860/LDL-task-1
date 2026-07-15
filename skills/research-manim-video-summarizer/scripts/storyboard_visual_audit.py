from __future__ import annotations

import json
from pathlib import Path

from scripts.manim_layout_support import LayoutFinding
from scripts.storyboard_schema import ParsedStoryboard, canonical_token, substantive


def _canonical(value: str) -> str:
    return " ".join(canonical_token(value).split())


def _expected_ownership(board: ParsedStoryboard) -> dict[int, str]:
    ownership: dict[int, str] = {}
    for scene in board.scenes:
        background = scene.fields.token("background beat")
        method = scene.fields.token("method step")
        ownership[scene.number] = background if background != "none" else method if method != "none" else scene.fields.token("narrative beat")
    return ownership


def inspect_storyboard_visual_match(manifest: Path, board: ParsedStoryboard | None = None) -> LayoutFinding:
    try:
        payload = json.loads(manifest.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError, RecursionError) as exc:
        return LayoutFinding(check="storyboard visual match", status="fail", detail=f"cannot read QA manifest: {exc}")
    records = payload.get("scenes") if isinstance(payload, dict) else None
    if not isinstance(records, list):
        return LayoutFinding(check="storyboard visual match", status="fail", detail="QA manifest needs scene records")

    expected_scenes = {} if board is None else {scene.number: scene for scene in board.scenes}
    expected_ownership = {} if board is None else _expected_ownership(board)
    seen: list[int] = []
    summaries: list[str] = []
    invalid: list[str] = []
    for record in records:
        scene_number = record.get("scene") if isinstance(record, dict) else None
        if not isinstance(scene_number, int) or isinstance(scene_number, bool):
            invalid.append("record without integer scene")
            continue
        seen.append(scene_number)
        visual_object = record.get("storyboard_visual_object")
        ownership = record.get("storyboard_ownership")
        if record.get("visual_semantic_match") != "pass":
            invalid.append(f"Scene {scene_number} visual semantic comparison is not pass")
        if not isinstance(visual_object, str) or not substantive(visual_object, minimum_units=6):
            invalid.append(f"Scene {scene_number} lacks a substantive storyboard visual object")
        if not isinstance(ownership, str) or not ownership.strip():
            invalid.append(f"Scene {scene_number} lacks storyboard ownership")
        for state in ("entry", "midpoint", "settled"):
            summary = record.get(f"{state}_content_summary")
            if not isinstance(summary, str) or not substantive(summary, minimum_units=6):
                invalid.append(f"Scene {scene_number} {state} lacks a substantive frame-content summary")
            else:
                summaries.append(_canonical(summary))
        expected_scene = expected_scenes.get(scene_number)
        if (
            expected_scene is not None
            and isinstance(visual_object, str)
            and _canonical(visual_object) != _canonical(expected_scene.fields.one("visual object"))
        ):
            invalid.append(f"Scene {scene_number} visual object does not match the storyboard")
        expected_role = expected_ownership.get(scene_number)
        if expected_role is not None and isinstance(ownership, str) and _canonical(ownership) != expected_role:
            invalid.append(f"Scene {scene_number} ownership does not match {expected_role}")
    if len(seen) != len(set(seen)):
        invalid.append("scene records are duplicated")
    if board is not None and set(seen) != set(expected_scenes):
        invalid.append("visual semantic scene coverage does not match the storyboard")
    if len(summaries) != len(set(summaries)):
        invalid.append("each reviewed scene state needs a distinct frame-content summary")
    if invalid:
        return LayoutFinding(check="storyboard visual match", status="fail", detail="; ".join(invalid[:8]))
    scope = "against exact storyboard objects and roles" if board is not None else "for release-record completeness"
    return LayoutFinding(
        check="storyboard visual match",
        status="pass",
        detail=f"named visual review covers {len(seen)} scenes {scope}",
    )
