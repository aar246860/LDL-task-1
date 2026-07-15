from __future__ import annotations

from typing import Final

from scripts.storyboard_contract_models import RubricFinding, contains_any, make_finding, normalize
from scripts.storyboard_schema import ParsedStoryboard, meaningful

ACADEMIC_FIELDS: Final = ("step detail", "why this step is valid", "transition bridge")
FORMULA_FIELDS: Final = ("symbol handoff", "formula split plan", "formula derivation steps")
REASON_TERMS: Final = ("because", "therefore", "so that", "depends on", "assumes", "valid", "evidence", "defines")
BRIDGE_TERMS: Final = ("from", "to", "after", "before", "previous", "becomes", "turns into", "returns")
SKIP_PATTERNS: Final = (
    "skip the derivation",
    "details omitted",
    "jump straight",
    "black box",
    "handwave",
    "obvious to experts",
)
UNCERTAINTY_TERMS: Final = ("uncertainty", "probability", "confidence", "error", "residual", "variance")
HOOK_RULES: Final = {"H01", "H02", "H06"}
BACKGROUND_RULES: Final = {"H06", "H19", "H20", "H21"}
METHOD_RULES: Final = {"H07", "H08", "H12", "H13", "H20"}
FORMULA_RULES: Final = {"H05", "H15", "H16", "H18"}
CONTINUITY_RULES: Final = {"H12", "H13", "H18"}
UNCERTAINTY_RULES: Final = {"H03", "H04", "H17"}
RETURN_RULES: Final = {"H01", "H06", "H08", "H21"}


def check_academic_step_detail(board: ParsedStoryboard, strict: bool) -> RubricFinding:
    if not strict:
        return make_finding("academic step detail", 2, "strict-only step-detail fields not required")
    invalid: list[str] = []
    for scene in board.scenes:
        text = normalize(scene.raw)
        if contains_any(text, SKIP_PATTERNS):
            invalid.append(f"Scene {scene.number} admits skipped reasoning")
        missing = [field for field in ACADEMIC_FIELDS if not meaningful(scene.fields.one(field))]
        if missing:
            invalid.append(f"Scene {scene.number} missing {', '.join(missing)}")
            continue
        reason = normalize(scene.fields.one("why this step is valid"))
        bridge = normalize(scene.fields.one("transition bridge"))
        if not contains_any(reason, REASON_TERMS):
            invalid.append(f"Scene {scene.number} lacks an explicit reason relation")
        if not contains_any(bridge, BRIDGE_TERMS):
            invalid.append(f"Scene {scene.number} lacks a visible handoff bridge")
        if scene.has_formula():
            formula_missing = [field for field in FORMULA_FIELDS if not meaningful(scene.fields.one(field))]
            if formula_missing:
                invalid.append(f"Scene {scene.number} missing {', '.join(formula_missing)}")
    if invalid:
        return make_finding("academic step detail", 0, "; ".join(invalid[:7]), fail=True)
    return make_finding("academic step detail", 2, f"{len(board.scenes)} scenes include explicit steps, reasons, and visual handoffs")


def check_source_trigger_coverage(board: ParsedStoryboard, strict: bool) -> RubricFinding:
    if not strict:
        return make_finding("source-derived trigger coverage", 2, "strict-only evidence-map fields not required")
    invalid: list[str] = []
    all_rules: set[str] = set()
    for index, scene in enumerate(board.scenes):
        rules = scene.rule_ids()
        all_rules.update(rules)
        if not rules:
            invalid.append(f"Scene {scene.number} has no valid Hxx rule")
            continue
        beat = scene.fields.token("narrative beat")
        background = scene.fields.token("background beat")
        method = scene.fields.token("method step")
        if index == 0 and not rules.intersection(HOOK_RULES):
            invalid.append(f"Scene {scene.number} lacks an opening-hook rule")
        if background != "none" and not rules.intersection(BACKGROUND_RULES):
            invalid.append(f"Scene {scene.number} lacks a background-story rule")
        if method != "none" and not rules.intersection(METHOD_RULES):
            invalid.append(f"Scene {scene.number} lacks an atomic-method rule")
        if scene.has_formula() and not rules.intersection(FORMULA_RULES):
            invalid.append(f"Scene {scene.number} lacks a formula/symbol rule")
        if "assert_scene_layout" in scene.fields.one("layout guard").lower() and "H17" not in rules:
            invalid.append(f"Scene {scene.number} layout guard lacks H17")
        if contains_any(normalize(scene.raw), UNCERTAINTY_TERMS):
            if not meaningful(scene.fields.one("uncertainty shape")):
                invalid.append(f"Scene {scene.number} lacks an uncertainty shape")
            if not rules.intersection(UNCERTAINTY_RULES):
                invalid.append(f"Scene {scene.number} lacks an uncertainty rule")
        if beat == "revelation" and "H10" not in rules:
            invalid.append(f"Scene {scene.number} revelation lacks H10")
        if beat in {"return", "resolution"} and not rules.intersection(RETURN_RULES):
            invalid.append(f"Scene {scene.number} lacks a return rule")
    if not all_rules.intersection(CONTINUITY_RULES):
        invalid.append("storyboard lacks H12/H13/H18 continuity coverage")
    if "H19" not in all_rules or not ({"H20", "H21"} & all_rules):
        invalid.append("storyboard lacks H19 and H20/H21 public-talk coverage")
    if len(all_rules) < 7:
        invalid.append(f"only {len(all_rules)} distinct Hxx rules are cited")
    if invalid:
        return make_finding("source-derived trigger coverage", 0, "; ".join(invalid[:8]), fail=True)
    return make_finding("source-derived trigger coverage", 2, f"{len(all_rules)} distinct Hxx rules satisfy scene-specific trigger families")
