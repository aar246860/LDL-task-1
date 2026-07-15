from __future__ import annotations

import re
from collections import Counter
from typing import Final

from scripts.storyboard_contract_models import RubricFinding, make_finding
from scripts.storyboard_row_checks import LOCATOR_TERMS, SPINE_REQUIREMENTS, row_issues, scope_count
from scripts.storyboard_schema import ParsedStoryboard, canonical_token, meaningful, substantive

NARRATIVE_BEATS: Final = {
    "hook",
    "context",
    "tension",
    "mechanism",
    "evidence",
    "revelation",
    "return",
    "resolution",
}
STORY_MODES: Final = {"concept", "method", "result", "review-response"}
RENDERING_TARGETS: Final = {"720p", "1080p", "4k"}
AFFILIATION_CLAIM_PATTERN: Final = re.compile(
    r"\b(?:official|affiliated|endorsed|approved|authorized|partnered)\b.{0,48}\b(?:3blue1brown|3b1b|tedx?|ted)\b|"
    r"\b(?:3blue1brown|3b1b|tedx?|ted)\b.{0,48}\b(?:official|affiliated|endorsed|approved|authorized|partnered)\b",
    re.IGNORECASE,
)
GENERIC_SCENE_FIELDS: Final = (
    "source-derived rules",
    "narrative beat",
    "background beat",
    "method step",
    "storyboard trigger",
    "viewer question",
    "visual object",
    "visual antecedent",
    "transformation from previous scene",
    "motion purpose",
    "step detail",
    "why this step is valid",
    "transition bridge",
    "what the viewer learns",
    "minimal on-screen text",
    "evidence locator",
    "frame zones",
    "keep-clear pairs",
    "transition-frame audit",
    "layout guard",
    "formula",
)
METHOD_SCENE_FIELDS: Final = ("input state", "operation", "output state", "validity basis")
NEGATIVE_AUDIT_TERMS: Final = (
    "not inspected",
    "uninspected",
    "without inspection",
    "not checked",
    "unchecked",
    "unreviewed",
    "not reviewed",
    "skip",
    "omitted",
    "never",
)
NEGATIVE_GUARD_TERMS: Final = ("do not", "not call", "never", "skip", "without")
ZONE_TERMS: Final = ("left", "right", "center", "upper", "lower", "lane", "band", "margin", "top", "bottom")
SUBSTANTIVE_SCENE_FIELDS: Final = {
    "storyboard trigger": 5,
    "viewer question": 4,
    "visual object": 3,
    "visual antecedent": 3,
    "motion purpose": 5,
    "step detail": 6,
    "why this step is valid": 6,
    "transition bridge": 5,
    "what the viewer learns": 5,
}


def check_schema_integrity(board: ParsedStoryboard, strict: bool) -> RubricFinding:
    if not strict:
        return make_finding("storyboard schema integrity", 2, "strict-only schema fields not required")
    issues = list(board.errors)
    if AFFILIATION_CLAIM_PATTERN.search(board.raw) is not None:
        issues.append("storyboard contains a prohibited affiliation, endorsement, or official-content claim")
    for field in ("title", "source artifact", "audience", "story mode", "target duration", "rendering target"):
        if not meaningful(board.metadata.one(field)):
            issues.append(f"Metadata missing {field}")
    if board.metadata.token("story mode") not in STORY_MODES:
        issues.append("Metadata has invalid story mode")
    if board.metadata.token("rendering target") not in RENDERING_TARGETS:
        issues.append("Metadata has invalid rendering target")
    for field, minimum_units in SPINE_REQUIREMENTS.items():
        if not substantive(board.spine.one(field), minimum_units=minimum_units):
            issues.append(f"Narrative Spine missing substantive {field}")
    issues.extend(row_issues("Background Ledger", board.background_rows, 6))
    issues.extend(row_issues("Method Decomposition Ledger", board.method_rows, 6))
    background_count = scope_count(board.spine.one("background scope"))
    method_count = scope_count(board.spine.one("method scope"))
    if background_count != len(board.background_rows):
        issues.append("Background scope count does not match the Bxx ledger")
    if method_count != len(board.method_rows):
        issues.append("Method scope count does not match the Mxx ledger")
    if not board.symbol_glossary_present:
        issues.append("missing Symbol Glossary section")
    issues.extend(
        row_issues(
            "Symbol Glossary",
            board.symbol_rows,
            6,
            require_locator=False,
            minimum_semantic_units=None,
        ),
    )
    if any(scene.has_formula() for scene in board.scenes) and not board.symbol_rows:
        issues.append("formula scenes require Symbol Glossary rows")
    scene_numbers = {scene.number for scene in board.scenes}
    for row in board.symbol_rows:
        if len(row.cells) >= 2:
            match = re.fullmatch(r"Scene\s+(\d+)", row.cells[1], re.IGNORECASE)
            if match is None or int(match.group(1)) not in scene_numbers:
                issues.append(f"{row.identifier} has an invalid first-use scene")
    for scene in board.scenes:
        for field in GENERIC_SCENE_FIELDS:
            values = scene.fields.all(field)
            if len(values) != 1 or not meaningful(values[0], allow_none=True):
                issues.append(f"Scene {scene.number} missing one affirmative {field}")
        if scene.fields.token("method step") != "none":
            for field in METHOD_SCENE_FIELDS:
                values = scene.fields.all(field)
                if len(values) != 1 or not meaningful(values[0]):
                    issues.append(f"Scene {scene.number} missing one affirmative {field}")
        for field, minimum_units in SUBSTANTIVE_SCENE_FIELDS.items():
            if not substantive(scene.fields.one(field), minimum_units=minimum_units):
                issues.append(f"Scene {scene.number} has non-substantive {field}")
        background = scene.fields.token("background beat")
        premise_values = scene.fields.all("background premise")
        if background != "none" and (len(premise_values) != 1 or not substantive(premise_values[0], minimum_units=4)):
            issues.append(f"Scene {scene.number} lacks one substantive Background premise")
        if background == "none" and premise_values:
            issues.append(f"Scene {scene.number} declares a Background premise without Bxx ownership")
        locator = scene.fields.one("evidence locator").lower()
        if not substantive(locator, minimum_units=3) or not any(term in locator for term in LOCATOR_TERMS):
            issues.append(f"Scene {scene.number} lacks a specific evidence locator")
        if scene.fields.token("formula") == "none" and "mathtex" in scene.raw.lower():
            issues.append(f"Scene {scene.number} declares Formula none but contains MathTex")
        if scene.has_formula():
            timing = scene.fields.all("antecedent timing")
            if len(timing) != 1 or not meaningful(timing[0]):
                issues.append(f"Scene {scene.number} lacks a unique formula antecedent timing")
    if issues:
        return make_finding("storyboard schema integrity", 0, "; ".join(issues[:8]), fail=True)
    return make_finding("storyboard schema integrity", 2, "unique fields, complete ledgers, source locators, and glossary are present")


def check_public_talk_throughline(board: ParsedStoryboard, strict: bool) -> RubricFinding:
    if not strict:
        return make_finding("public-talk throughline", 2, "strict-only story arc not required")
    if not board.scenes:
        return make_finding("public-talk throughline", 0, "no scenes found", fail=True)
    beats = [scene.fields.token("narrative beat") for scene in board.scenes]
    invalid = [scene.number for scene, beat in zip(board.scenes, beats, strict=True) if beat not in NARRATIVE_BEATS]
    if invalid:
        return make_finding("public-talk throughline", 0, f"invalid narrative beat in scenes {invalid}", fail=True)
    if beats[0] not in {"hook", "tension"}:
        return make_finding("public-talk throughline", 0, "first scene is not a hook or tension beat", fail=True)
    if beats[-1] not in {"return", "resolution"}:
        return make_finding("public-talk throughline", 0, "final scene is not a return or resolution beat", fail=True)
    mechanism_index = next((index for index, beat in enumerate(beats) if beat == "mechanism"), None)
    if mechanism_index is not None and "context" not in beats[:mechanism_index]:
        return make_finding("public-talk throughline", 0, "no context beat precedes the first mechanism", fail=True)
    if board.method_rows and not {"tension", "revelation"}.issubset(beats):
        return make_finding("public-talk throughline", 0, "method story requires tension and revelation beats", fail=True)
    revelations = [scene for scene, beat in zip(board.scenes, beats, strict=True) if beat == "revelation"]
    if revelations and any(not meaningful(scene.fields.one("aha object")) for scene in revelations):
        return make_finding("public-talk throughline", 0, "every revelation scene needs a visible Aha object", fail=True)
    return make_finding("public-talk throughline", 2, "one exact beat per scene forms a complete public-talk arc")


def check_background_beat_coverage(board: ParsedStoryboard, strict: bool) -> RubricFinding:
    if not strict:
        return make_finding("background-beat coverage", 2, "strict-only background ledger not required")
    ledger_ids = [row.identifier for row in board.background_rows]
    ledger_by_id = {row.identifier: row for row in board.background_rows}
    if not ledger_ids:
        return make_finding("background-beat coverage", 0, "strict public-talk mode requires at least one Bxx premise", fail=True)
    scene_ids: list[str] = []
    invalid: list[str] = []
    method_positions: list[int] = []
    background_positions: list[int] = []
    for position, scene in enumerate(board.scenes):
        background = scene.fields.token("background beat")
        method = scene.fields.token("method step")
        beat = scene.fields.token("narrative beat")
        if background != "none" and re.fullmatch(r"b\d{2}", background) is None:
            invalid.append(f"Scene {scene.number} has invalid Background beat")
        elif background != "none":
            scene_ids.append(background.upper())
            background_positions.append(position)
            row = ledger_by_id.get(background.upper())
            premise = scene.fields.one("background premise")
            if row is not None and len(row.cells) >= 2 and canonical_token(premise) != canonical_token(row.cells[1]):
                invalid.append(f"Scene {scene.number} Background premise does not match {background.upper()}")
        if method != "none":
            method_positions.append(position)
        if background != "none" and method != "none":
            invalid.append(f"Scene {scene.number} combines background and method")
        if beat in {"hook", "context", "tension"} and background == "none":
            invalid.append(f"Scene {scene.number} owns a background beat but declares none")
    counts = Counter(scene_ids)
    if scene_ids != ledger_ids:
        invalid.append("background scenes do not map one-to-one in ledger order")
    if any(count > 1 for count in counts.values()):
        invalid.append("a background identifier is reused")
    if method_positions and background_positions and max(background_positions) > min(method_positions):
        invalid.append("a background scene appears after method exposition begins")
    if invalid:
        return make_finding("background-beat coverage", 0, "; ".join(invalid[:6]), fail=True)
    return make_finding("background-beat coverage", 2, f"{len(ledger_ids)} ordered Bxx items map one-to-one to context scenes")


def check_scene_layout_contract(board: ParsedStoryboard, strict: bool) -> RubricFinding:
    if not strict:
        return make_finding("scene layout contract", 2, "strict-only layout fields not required")
    invalid: list[str] = []
    for scene in board.scenes:
        zones = scene.fields.one("frame zones").lower()
        pairs = scene.fields.one("keep-clear pairs").lower()
        audit = scene.fields.one("transition-frame audit").lower()
        guard = scene.fields.one("layout guard").lower()
        has_text = scene.fields.token("minimal on-screen text") != "none"
        is_negated = any(term in guard for term in NEGATIVE_GUARD_TERMS)
        if not meaningful(zones) or sum(term in zones for term in ZONE_TERMS) < 2:
            invalid.append(f"Scene {scene.number} lacks distinct frame zones")
        if not meaningful(pairs) or not any(term in pairs for term in ("versus", " from ", ";", ",")):
            invalid.append(f"Scene {scene.number} lacks explicit keep-clear pairs")
        if not all(term in audit for term in ("entry", "midpoint", "settled")) or any(term in audit for term in NEGATIVE_AUDIT_TERMS):
            invalid.append(f"Scene {scene.number} lacks an affirmative entry/midpoint/settled audit")
        if (has_text or scene.has_formula()) and ("assert_scene_layout" not in guard or is_negated):
            invalid.append(f"Scene {scene.number} text/data state lacks assert_scene_layout")
        if not has_text and not scene.has_formula() and ("assert_within_frame" not in guard or is_negated):
            invalid.append(f"Scene {scene.number} pure-geometry state lacks assert_within_frame")
    if invalid:
        return make_finding("scene layout contract", 0, "; ".join(invalid[:6]), fail=True)
    return make_finding("scene layout contract", 2, f"{len(board.scenes)} scenes declare non-vacuous layout and transition audits")
