from __future__ import annotations

import math
import re
from typing import Final

from scripts.storyboard_contract_models import (
    RubricFinding,
    contains_any,
    count_matches,
    make_finding,
    normalize,
)
from scripts.storyboard_contract_models import (
    StoryboardReport as StoryboardReport,
)
from scripts.storyboard_evidence_checks import check_academic_step_detail, check_source_trigger_coverage
from scripts.storyboard_method_checks import check_atomic_method_coverage
from scripts.storyboard_schema import ParsedScene, ParsedStoryboard, canonical_token, meaningful, parse_storyboard
from scripts.storyboard_structure_checks import (
    check_background_beat_coverage,
    check_public_talk_throughline,
    check_scene_layout_contract,
    check_schema_integrity,
)

HOOK_TERMS: Final = ("hook", "why", "what if", "question", "mismatch", "puzzle", "tension", "unknown")
ANCHOR_TERMS: Final = (
    "pile",
    "aquifer",
    "specimen",
    "curve",
    "axis",
    "point cloud",
    "distribution",
    "interval",
    "surface",
    "field",
    "map",
    "geometry",
    "silhouette",
)
MOTION_PURPOSE_TERMS: Final = (
    "because",
    "reveals",
    "creates",
    "constructs",
    "compares",
    "shows",
    "makes",
    "changes",
    "turns",
    "becomes",
    "gives",
    "defines",
)
UNCERTAINTY_TERMS: Final = ("uncertainty", "probability", "confidence", "error", "residual", "variance")
UNCERTAINTY_SHAPES: Final = (
    "distribution",
    "density",
    "interval",
    "cloud",
    "sample cloud",
    "shaded band",
    "band",
    "histogram",
    "number line",
    "width",
    "spread",
    "distance",
)
BANNED_PATTERNS: Final = (
    "spreadsheet",
    "software pipeline",
    "flowchart only",
    "bullet-heavy",
    "formula first",
    "github blob only",
    "static screenshots",
)
NEGATIVE_MOTION_PATTERNS: Final = (
    "no visual change",
    "purposeful motion: none",
    "motion purpose: none",
    "decorative motion",
    "motion: none",
    "hard cut",
    "unrelated new slide",
)
TEXT_ONLY_UNCERTAINTY: Final = (
    "probability is described only in prose",
    "described only in prose",
    "only in prose",
    "text-only",
    "text only",
    "without drawing a distribution",
)
SCIENTIFIC_OBJECT_TERMS: Final = (
    "pile",
    "aquifer",
    "specimen",
    "soil",
    "field",
    "map",
    "curve",
    "physical object",
    "scientific object",
    "original",
)
DEFAULT_MIN_SCORE: Final = 12
SAME_SCENE_ANTECEDENT: Final = "earlier in this scene before formula"


def _antecedent_precedes_formula(scene: ParsedScene) -> bool:
    timing = canonical_token(scene.fields.one("antecedent timing"))
    if timing == SAME_SCENE_ANTECEDENT:
        return True
    match = re.fullmatch(r"prior scene\s+(\d+)", timing)
    return match is not None and 0 < int(match.group(1)) < scene.number


def check_narrative_hook(board: ParsedStoryboard) -> RubricFinding:
    if not board.scenes:
        return make_finding("narrative hook", 0, "no first scene", fail=True)
    first = board.scenes[0]
    text = normalize(first.raw)
    has_hook = contains_any(text, HOOK_TERMS) or "?" in first.raw
    if has_hook and not first.has_formula():
        return make_finding("narrative hook", 2, "first scene opens with a concrete question or tension")
    return make_finding("narrative hook", 0, "first scene is formula-led or lacks a concrete question", fail=True)


def check_visual_anchor(board: ParsedStoryboard) -> RubricFinding:
    if not board.scenes:
        return make_finding("concrete visual anchor", 0, "no first scene", fail=True)
    first = board.scenes[0]
    text = normalize(first.fields.one("visual object"))
    found = [term for term in ANCHOR_TERMS if term in text]
    if found:
        return make_finding("concrete visual anchor", 2, f"found: {', '.join(found[:5])}")
    return make_finding("concrete visual anchor", 0, "first scene has no concrete scientific or geometric object", fail=True)


def check_geometry_before_formula(board: ParsedStoryboard) -> RubricFinding:
    formula_scenes = [scene for scene in board.scenes if scene.has_formula()]
    if not formula_scenes:
        return make_finding("geometry before formula", 2, "no formula scene triggers the chronology rule")
    invalid = [
        scene.number
        for scene in formula_scenes
        if scene.number == 1 or not meaningful(scene.fields.one("visual antecedent")) or not _antecedent_precedes_formula(scene)
    ]
    if invalid:
        return make_finding("geometry before formula", 0, f"formula precedes geometry in scenes {invalid}", fail=True)
    return make_finding("geometry before formula", 2, "every formula follows an explicitly earlier visible antecedent")


def check_one_idea_per_scene(board: ParsedStoryboard) -> RubricFinding:
    invalid: list[int] = []
    for scene in board.scenes:
        background = scene.fields.token("background beat")
        method = scene.fields.token("method step")
        if (background != "none" and method != "none") or not meaningful(scene.fields.one("what the viewer learns")):
            invalid.append(scene.number)
    if contains_any(normalize(board.raw), BANNED_PATTERNS):
        return make_finding("one idea per scene", 0, "a banned slide or workflow pattern dominates", fail=True)
    if invalid:
        return make_finding("one idea per scene", 0, f"ambiguous scene ownership or learning purpose in {invalid}", fail=True)
    return make_finding("one idea per scene", 2, f"{len(board.scenes)} scenes each declare one learning purpose")


def check_morph_continuity(board: ParsedStoryboard) -> RubricFinding:
    required = math.ceil(len(board.scenes) / 2)
    continuous: list[int] = []
    for scene in board.scenes[1:]:
        value = normalize(scene.fields.one("transformation from previous scene"))
        if meaningful(value) and not contains_any(value, NEGATIVE_MOTION_PATTERNS):
            continuous.append(scene.number)
    if len(continuous) < required:
        return make_finding(
            "morph continuity",
            0,
            f"only {len(continuous)} scenes preserve prior objects; at least {required} are required",
            fail=True,
        )
    return make_finding("morph continuity", 2, f"{len(continuous)} scenes preserve and transform prior objects")


def check_purposeful_motion(board: ParsedStoryboard) -> RubricFinding:
    invalid: list[int] = []
    for scene in board.scenes:
        purpose = normalize(scene.fields.one("motion purpose"))
        if not meaningful(purpose) or contains_any(purpose, NEGATIVE_MOTION_PATTERNS) or count_matches(purpose, MOTION_PURPOSE_TERMS) == 0:
            invalid.append(scene.number)
    if invalid:
        return make_finding("purposeful motion", 0, f"motion lacks an explanatory consequence in scenes {invalid}", fail=True)
    return make_finding("purposeful motion", 2, "every scene states what becomes visible because of motion")


def check_uncertainty_shape(board: ParsedStoryboard) -> RubricFinding:
    triggered = [scene for scene in board.scenes if contains_any(normalize(scene.raw), UNCERTAINTY_TERMS)]
    if not triggered:
        return make_finding("uncertainty as shape", 2, "no uncertainty claim triggers this rule")
    invalid: list[int] = []
    for scene in triggered:
        text = normalize(scene.raw)
        shape = normalize(scene.fields.one("uncertainty shape"))
        if contains_any(text, TEXT_ONLY_UNCERTAINTY) or not meaningful(shape) or not contains_any(shape, UNCERTAINTY_SHAPES):
            invalid.append(scene.number)
    if invalid:
        return make_finding("uncertainty as shape", 0, f"uncertainty is not a visible shape in scenes {invalid}", fail=True)
    return make_finding("uncertainty as shape", 2, f"{len(triggered)} uncertainty scenes use explicit visual shapes")


def check_final_return(board: ParsedStoryboard) -> RubricFinding:
    if not board.scenes:
        return make_finding("return to scientific object", 0, "no scenes found", fail=True)
    last = board.scenes[-1]
    text = normalize(last.raw)
    if last.fields.token("narrative beat") in {"return", "resolution"} and count_matches(text, SCIENTIFIC_OBJECT_TERMS) >= 1:
        return make_finding("return to scientific object", 2, "final scene returns to the research object")
    return make_finding("return to scientific object", 0, "final scene ends away from the scientific object", fail=True)


def evaluate_storyboard(markdown: str, *, strict: bool) -> StoryboardReport:
    board = parse_storyboard(markdown)
    findings = [
        check_schema_integrity(board, strict),
        check_narrative_hook(board),
        check_visual_anchor(board),
        check_geometry_before_formula(board),
        check_one_idea_per_scene(board),
        check_academic_step_detail(board, strict),
        check_morph_continuity(board),
        check_purposeful_motion(board),
        check_uncertainty_shape(board),
        check_final_return(board),
        check_source_trigger_coverage(board, strict),
        check_public_talk_throughline(board, strict),
        check_background_beat_coverage(board, strict),
        check_atomic_method_coverage(board, strict),
        check_scene_layout_contract(board, strict),
    ]
    score = sum(finding.score for finding in findings)
    maximum = sum(finding.maximum for finding in findings)
    threshold = maximum if strict else DEFAULT_MIN_SCORE
    has_failure = any(finding.status == "fail" for finding in findings)
    return StoryboardReport(score, maximum, threshold, score >= threshold and not has_failure, findings)
