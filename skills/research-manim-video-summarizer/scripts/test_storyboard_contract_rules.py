from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from scripts.check_storyboard_contract import serialize_report
from scripts.storyboard_contract_rules import StoryboardReport, evaluate_storyboard

FIXTURES = Path(__file__).parent / "fixtures"
GOOD_STORYBOARD = FIXTURES / "storyboard_good_geometry_first.md"
BAD_CASES = (
    ("storyboard_bad_formula_first.md", "geometry before formula"),
    ("storyboard_bad_missing_evidence_map.md", "source-derived trigger coverage"),
    ("storyboard_bad_probability_text_only.md", "uncertainty as shape"),
    ("storyboard_bad_skips_academic_steps.md", "academic step detail"),
)


def good_storyboard() -> str:
    return GOOD_STORYBOARD.read_text(encoding="utf-8")


def finding_status(report: StoryboardReport, check: str) -> str:
    return next(finding.status for finding in report.findings if finding.check == check)


def replace_scene_field(markdown: str, scene_number: int, field: str, value: str) -> str:
    scene_pattern = re.compile(
        rf"(?ms)(^### Scene {scene_number}:.*?)(?=^### Scene \d+:|\Z)",
    )

    def replace_in_scene(match: re.Match[str]) -> str:
        field_pattern = re.compile(rf"(?m)^- {re.escape(field)}:.*$")
        updated, count = field_pattern.subn(f"- {field}: {value}", match.group(1), count=1)
        assert count == 1
        return updated

    updated, count = scene_pattern.subn(replace_in_scene, markdown, count=1)
    assert count == 1
    return updated


def assert_check_fails(markdown: str, check: str) -> None:
    report = evaluate_storyboard(markdown, strict=True)
    assert not report.passed
    assert finding_status(report, check) == "fail"


def test_strict_storyboard_passes_all_checks() -> None:
    report = evaluate_storyboard(good_storyboard(), strict=True)
    assert report.passed
    assert report.score == report.maximum == report.threshold == 30


@pytest.mark.parametrize(("fixture", "check"), BAD_CASES)
def test_named_bad_fixture_fails_its_target_check(fixture: str, check: str) -> None:
    markdown = (FIXTURES / fixture).read_text(encoding="utf-8")
    assert_check_fails(markdown, check)


def test_combined_method_steps_fail() -> None:
    markdown = replace_scene_field(good_storyboard(), 5, "Method step", "`M01`, `M02`.")
    assert_check_fails(markdown, "atomic method coverage")


def test_combined_background_beats_fail() -> None:
    markdown = replace_scene_field(good_storyboard(), 2, "Background beat", "`B01`, `B02`.")
    assert_check_fails(markdown, "background-beat coverage")


def test_missing_layout_field_fails() -> None:
    markdown = re.sub(r"(?m)^- Frame zones:.*\n", "", good_storyboard(), count=1)
    assert_check_fails(markdown, "scene layout contract")


def test_missing_throughline_fails() -> None:
    markdown = re.sub(r"(?m)^- Throughline:.*\n", "", good_storyboard(), count=1)
    assert_check_fails(markdown, "storyboard schema integrity")


def test_background_ledger_order_is_enforced() -> None:
    prefix, scenes = good_storyboard().split("## Scene Table", maxsplit=1)
    scenes = scenes.replace("`B01`", "`B99`", 1).replace("`B02`", "`B01`", 1).replace("`B99`", "`B02`", 1)
    assert_check_fails(prefix + "## Scene Table" + scenes, "background-beat coverage")


def test_method_ledger_order_is_enforced() -> None:
    prefix, scenes = good_storyboard().split("## Scene Table", maxsplit=1)
    scenes = scenes.replace("`M01`", "`M99`", 1).replace("`M02`", "`M01`", 1).replace("`M99`", "`M02`", 1)
    assert_check_fails(prefix + "## Scene Table" + scenes, "atomic method coverage")


def test_duplicate_scene_field_fails_schema() -> None:
    markdown = good_storyboard().replace("- Background beat: `B02`.", "- Background beat: `B02`.\n- Background beat: none.", 1)
    assert_check_fails(markdown, "storyboard schema integrity")


def test_blank_required_field_fails_schema() -> None:
    markdown = replace_scene_field(good_storyboard(), 2, "Storyboard trigger", "")
    assert_check_fails(markdown, "storyboard schema integrity")


def test_invalid_narrative_enum_fails() -> None:
    markdown = replace_scene_field(good_storyboard(), 2, "Narrative beat", "not context.")
    assert_check_fails(markdown, "public-talk throughline")


def test_negated_layout_guard_fails() -> None:
    markdown = replace_scene_field(good_storyboard(), 2, "Layout guard", "do not call `assert_scene_layout`.")
    assert_check_fails(markdown, "scene layout contract")


def test_text_scene_cannot_use_frame_only_guard() -> None:
    markdown = replace_scene_field(good_storyboard(), 2, "Layout guard", "`assert_within_frame` for all objects.")
    assert_check_fails(markdown, "scene layout contract")


def test_pure_geometry_scene_uses_frame_guard() -> None:
    markdown = replace_scene_field(good_storyboard(), 2, "Minimal on-screen text", "none.")
    markdown = replace_scene_field(markdown, 2, "Layout guard", "`assert_within_frame` for all visible geometry.")
    report = evaluate_storyboard(markdown, strict=True)
    assert finding_status(report, "scene layout contract") == "pass"


def test_plain_conjunction_between_operations_fails() -> None:
    markdown = replace_scene_field(good_storyboard(), 4, "Operation", "select the peak and compute its ratio.")
    assert_check_fails(markdown, "atomic method coverage")


def test_unlisted_second_action_after_infinitive_fails() -> None:
    markdown = replace_scene_field(good_storyboard(), 4, "Operation", "select the peak to overwrite its reference value.")
    assert_check_fails(markdown, "atomic method coverage")


def test_formula_none_cannot_hide_mathtex() -> None:
    markdown = replace_scene_field(good_storyboard(), 4, "Formula", "none.")
    assert_check_fails(markdown, "storyboard schema integrity")


def test_formula_antecedent_must_precede_formula() -> None:
    markdown = replace_scene_field(good_storyboard(), 4, "Antecedent timing", "prior Scene 5.")
    assert_check_fails(markdown, "geometry before formula")


def test_formula_antecedent_timing_is_required() -> None:
    markdown = re.sub(r"(?m)^- Antecedent timing:.*\n", "", good_storyboard(), count=1)
    assert_check_fails(markdown, "storyboard schema integrity")


def test_unrelated_h_rule_set_fails_scene_specific_families() -> None:
    markdown = re.sub(
        r"(?m)^- Source-derived rules:.*$",
        "- Source-derived rules: `H01`, `H02`, `H03`, `H04`, `H06`, `H19`, `H20`, `H21`.",
        good_storyboard(),
    )
    assert_check_fails(markdown, "source-derived trigger coverage")


def test_duplicate_scene_number_fails_schema() -> None:
    markdown = good_storyboard().replace("### Scene 10:", "### Scene 9:", 1)
    assert_check_fails(markdown, "storyboard schema integrity")


def test_blank_ledger_semantics_fail_schema() -> None:
    markdown = re.sub(r"(?m)^\| `B01` \|.*$", "| `B01` |  |  |  |  |  |", good_storyboard(), count=1)
    assert_check_fails(markdown, "storyboard schema integrity")


def test_undeclared_method_fields_fail_atomicity() -> None:
    markdown = replace_scene_field(good_storyboard(), 9, "Method step", "none.")
    assert_check_fails(markdown, "atomic method coverage")


def test_missing_symbol_glossary_fails_schema() -> None:
    markdown = re.sub(r"(?ms)^## Symbol Glossary\n.*?(?=^## Scene Table)", "", good_storyboard(), count=1)
    assert_check_fails(markdown, "storyboard schema integrity")


def test_insufficient_object_continuity_fails() -> None:
    markdown = good_storyboard()
    for scene_number in range(2, 10):
        markdown = replace_scene_field(markdown, scene_number, "Transformation from previous scene", "hard cut to unrelated new slide.")
    assert_check_fails(markdown, "morph continuity")


def test_revelation_without_aha_object_fails() -> None:
    markdown = re.sub(r"(?m)^- Aha object:.*\n", "", good_storyboard(), count=1)
    assert_check_fails(markdown, "public-talk throughline")


def test_unsupported_scientific_basis_fails_schema() -> None:
    markdown = replace_scene_field(
        good_storyboard(),
        4,
        "Validity basis",
        "unsupported invented claim.",
    )
    assert_check_fails(markdown, "atomic method coverage")


def test_negative_transition_audit_fails() -> None:
    markdown = replace_scene_field(
        good_storyboard(),
        2,
        "Transition-frame audit",
        "entry, midpoint, and settled frames were not inspected.",
    )
    assert_check_fails(markdown, "scene layout contract")


def test_uninspected_transition_audit_fails() -> None:
    markdown = replace_scene_field(
        good_storyboard(),
        2,
        "Transition-frame audit",
        "entry, midpoint, and settled frames remain uninspected.",
    )
    assert_check_fails(markdown, "scene layout contract")


def test_removed_method_row_cannot_hide_existing_operation() -> None:
    markdown = re.sub(r"(?m)^\| `M06` \|.*\n", "", good_storyboard(), count=1)
    markdown = replace_scene_field(markdown, 9, "Method step", "none.")
    assert_check_fails(markdown, "atomic method coverage")


def test_removed_background_row_cannot_hide_tension_context() -> None:
    markdown = re.sub(r"(?m)^\| `B03` \|.*\n", "", good_storyboard(), count=1)
    markdown = replace_scene_field(markdown, 3, "Background beat", "none.")
    assert_check_fails(markdown, "background-beat coverage")


def test_strict_mode_rejects_an_empty_background_ledger() -> None:
    markdown = re.sub(r"(?m)^\| `B\d{2}` \|.*\n", "", good_storyboard())
    markdown = re.sub(
        r"(?m)^- Background scope:.*$",
        "- Background scope: none required because the audience knows the field.",
        markdown,
        count=1,
    )
    for scene_number in range(1, 4):
        markdown = replace_scene_field(markdown, scene_number, "Background beat", "none.")
    assert_check_fails(markdown, "background-beat coverage")


def test_json_serializer_is_machine_parseable() -> None:
    report = evaluate_storyboard(good_storyboard(), strict=True)
    payload = json.loads(serialize_report(report))
    assert payload["passed"] is True
    assert payload["score"] == 30
