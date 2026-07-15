from __future__ import annotations

import re
from pathlib import Path

import pytest

from scripts.storyboard_contract_rules import StoryboardReport, evaluate_storyboard
from scripts.storyboard_method_checks import operation_issue

GOOD_STORYBOARD = Path(__file__).parent / "fixtures" / "storyboard_good_geometry_first.md"


def good_storyboard() -> str:
    return GOOD_STORYBOARD.read_text(encoding="utf-8")


def finding_status(report: StoryboardReport, check: str) -> str:
    return next(finding.status for finding in report.findings if finding.check == check)


def replace_scene_field(markdown: str, scene_number: int, field: str, value: str) -> str:
    scene_pattern = re.compile(rf"(?ms)(^### Scene {scene_number}:.*?)(?=^### Scene \d+:|\Z)")

    def replace_in_scene(match: re.Match[str]) -> str:
        field_pattern = re.compile(rf"(?m)^- {re.escape(field)}:.*$")
        updated, count = field_pattern.subn(f"- {field}: {value}", match.group(1), count=1)
        assert count == 1
        return updated

    updated, count = scene_pattern.subn(replace_in_scene, markdown, count=1)
    assert count == 1
    return updated


def assert_fails(markdown: str, check: str) -> None:
    report = evaluate_storyboard(markdown, strict=True)
    assert not report.passed
    assert finding_status(report, check) == "fail"


def test_invalid_story_mode_fails_schema() -> None:
    markdown = good_storyboard().replace("- Story mode: `method`", "- Story mode: bananas", 1)
    assert_fails(markdown, "storyboard schema integrity")


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("Storyboard trigger", "show."),
        ("Storyboard trigger", "show show show show show."),
        ("Visual object", "no visual object was shown."),
        ("Why this step is valid", "because source."),
        ("What the viewer learns", "idea."),
    ),
)
def test_non_substantive_scene_fields_fail(field: str, value: str) -> None:
    assert_fails(replace_scene_field(good_storyboard(), 4, field, value), "storyboard schema integrity")


def test_unreviewed_evidence_locator_fails_schema() -> None:
    markdown = replace_scene_field(good_storyboard(), 4, "Evidence locator", "source section was not reviewed.")
    assert_fails(markdown, "storyboard schema integrity")


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("Evidence locator", "fixture source section was never inspected."),
        ("Visual antecedent", "the required visible object is deliberately omitted."),
        ("Storyboard trigger", "the source event is deliberately omitted from this scene."),
        ("Transition-frame audit", "avoid inspecting entry, midpoint, and settled frames."),
        ("Layout guard", "avoid calling assert_scene_layout for this scene."),
    ),
)
def test_negated_required_evidence_fails(field: str, value: str) -> None:
    assert_fails(replace_scene_field(good_storyboard(), 4, field, value), "storyboard schema integrity")


def test_required_field_inside_code_fence_is_ignored() -> None:
    markdown = good_storyboard().replace(
        "- Operation: select the measured peak.",
        "```text\n- Operation: select the measured peak.\n```",
        1,
    )
    assert_fails(markdown, "storyboard schema integrity")


@pytest.mark.parametrize(
    "operation",
    (
        "select the measured peak and select the predicted peak.",
        "select the measured peak and archive the result.",
        "select the measured peak while archive the result.",
        "select the measured peak. Archive the result.",
        "select the measured peak: archive the result.",
        "select the measured peak to archive the result.",
    ),
)
def test_repeated_or_unknown_second_action_fails(operation: str) -> None:
    assert_fails(replace_scene_field(good_storyboard(), 4, "Operation", operation), "atomic method coverage")


def test_scene_operation_must_match_ledger_semantics() -> None:
    markdown = replace_scene_field(good_storyboard(), 4, "Operation", "compute the final ratio.")
    assert_fails(markdown, "atomic method coverage")


def test_decimal_parameter_does_not_create_a_false_second_action() -> None:
    assert operation_issue("multiply the threshold by 0.5.") is None


def test_duplicate_background_semantics_fail_schema() -> None:
    duplicate = (
        "| `B03` | individual tests can be represented on common axes | curves collapsing into points | "
        "makes comparison geometric | each point retains its measured and predicted coordinates | "
        "fixture source, Methods Sec. 2 |"
    )
    markdown = re.sub(r"(?m)^\| `B03` \|.*$", duplicate, good_storyboard(), count=1)
    markdown = replace_scene_field(
        markdown,
        3,
        "Background premise",
        "individual tests can be represented on common axes.",
    )
    assert_fails(markdown, "storyboard schema integrity")


def test_background_premise_must_match_ledger() -> None:
    markdown = replace_scene_field(good_storyboard(), 3, "Background premise", "a different premise entirely.")
    assert_fails(markdown, "background-beat coverage")


def test_ledger_semantic_filler_fails_schema() -> None:
    filler = "| `B01` | x1 | x2 | x3 | x4 | fixture source, Background Sec. 1 |"
    markdown = re.sub(r"(?m)^\| `B01` \|.*$", filler, good_storyboard(), count=1)
    markdown = replace_scene_field(markdown, 1, "Background premise", "x1")
    assert_fails(markdown, "storyboard schema integrity")


def test_h19_alone_does_not_satisfy_opening_rule() -> None:
    markdown = replace_scene_field(good_storyboard(), 1, "Source-derived rules", "`H17`, `H19`.")
    assert_fails(markdown, "source-derived trigger coverage")


def test_formula_rule_alone_does_not_satisfy_method_rule() -> None:
    markdown = replace_scene_field(good_storyboard(), 4, "Source-derived rules", "`H05`, `H17`.")
    assert_fails(markdown, "source-derived trigger coverage")


def test_h17_is_required_when_scene_layout_guard_is_used() -> None:
    markdown = replace_scene_field(good_storyboard(), 5, "Source-derived rules", "`H05`, `H13`, `H15`.")
    assert_fails(markdown, "source-derived trigger coverage")


def test_extreme_scene_number_returns_a_schema_failure() -> None:
    huge_number = "9" * 5000
    markdown = good_storyboard().replace("### Scene 10:", f"### Scene {huge_number}:", 1)
    assert_fails(markdown, "storyboard schema integrity")


def test_duplicate_scene_table_cannot_hide_an_extra_scene() -> None:
    markdown = good_storyboard() + "\n## Scene Table\n\n### Scene 11: undeclared extra\n"
    assert_fails(markdown, "storyboard schema integrity")


def test_affiliation_or_endorsement_claim_fails() -> None:
    markdown = replace_scene_field(
        good_storyboard(),
        1,
        "What the viewer learns",
        "This is official 3Blue1Brown content endorsed by TED and TEDx.",
    )
    assert_fails(markdown, "storyboard schema integrity")


def test_unlisted_domain_verb_after_infinitive_fails() -> None:
    operation = "select the measured peak to krige the residual field."
    assert_fails(replace_scene_field(good_storyboard(), 4, "Operation", operation), "atomic method coverage")
