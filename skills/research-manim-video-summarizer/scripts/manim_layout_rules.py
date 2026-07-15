from __future__ import annotations

import ast
from typing import Final

from scripts.manim_animation_state import animation_state_changes
from scripts.manim_ast_model import (
    MethodFacts,
    call_name,
    calls_in,
    keyword_is_self,
    keyword_names,
    positional_names,
    scene_method_name,
    scene_methods,
)
from scripts.manim_ast_vocabulary import VISIBLE_ADD_CALLS, VISIBLE_REMOVE_CALLS
from scripts.manim_guard_imports import approved_guard_calls
from scripts.manim_layout_support import LayoutFinding

MATH_SIGNAL_CHARS: Final = ("=", "\\", "_", "^", "∑", "∫", "α", "β", "γ", "μ", "σ", "θ")
LONG_TEXT_LIMIT: Final = 72
LONG_FORMULA_LIMIT: Final = 96


def first_string_argument(node: ast.Call) -> str:
    if not node.args:
        return ""
    first = node.args[0]
    if isinstance(first, ast.Constant) and isinstance(first.value, str):
        return first.value
    return ""


def _finding(check: str, passed: bool, detail: str, line: int | None = None) -> LayoutFinding:
    return LayoutFinding(check=check, status="pass" if passed else "fail", detail=detail, line=line)


def check_text_and_formula_calls(tree: ast.AST) -> list[LayoutFinding]:
    calls = calls_in(tree)
    math_in_text: list[int] = []
    dense_text: list[int] = []
    long_formula: list[int] = []
    for call in calls:
        name = call_name(call.func)
        content = first_string_argument(call)
        if name == "Text" and any(signal in content for signal in MATH_SIGNAL_CHARS):
            math_in_text.append(call.lineno)
        if name == "Text" and (len(content) > LONG_TEXT_LIMIT or len(content.split()) > 12):
            dense_text.append(call.lineno)
        if name == "MathTex" and (len(content) > LONG_FORMULA_LIMIT or content.count("=") > 1):
            long_formula.append(call.lineno)
    return [
        _finding("math in Text", not math_in_text, f"formula-like Text calls at lines {math_in_text}" if math_in_text else "no formula-like Text calls"),
        _finding("dense Text", not dense_text, f"dense prose at lines {dense_text}" if dense_text else "no oversized prose labels"),
        _finding("split formulas", not long_formula, f"oversized MathTex at lines {long_formula}" if long_formula else "no oversized MathTex calls"),
    ]


def _calls_between(
    facts: MethodFacts,
    name: str,
    lower: int,
    upper: int,
    approved: dict[str, frozenset[int]],
) -> tuple[ast.Call, ...]:
    return tuple(call for call in facts.direct_calls if id(call) in approved.get(name, frozenset()) and lower < call.lineno < upper)


def _valid_scene_guard(
    facts: MethodFacts,
    guard: ast.Call,
    labels: set[str],
    blockers: set[str],
    visible: set[str],
    newly_visible: set[str],
) -> bool:
    supplied_labels = facts.expand_names(keyword_names(guard, "labels", facts.assignments))
    supplied_blockers = facts.expand_names(keyword_names(guard, "blockers", facts.assignments))
    supplied_frame = facts.expand_names(keyword_names(guard, "frame_items", facts.assignments))
    supplied_pending = facts.expand_names(keyword_names(guard, "pending_items", facts.assignments))
    return (
        keyword_is_self(guard, "scene")
        and bool(supplied_labels)
        and bool(supplied_blockers)
        and bool(supplied_frame)
        and labels.issubset(supplied_labels)
        and blockers.issubset(supplied_blockers)
        and visible.issubset(supplied_frame)
        and newly_visible.issubset(supplied_pending)
    )


def _valid_frame_guard(
    facts: MethodFacts,
    guard: ast.Call,
    visible: set[str],
    newly_visible: set[str],
) -> bool:
    supplied = facts.expand_names(positional_names(guard, 0, facts.assignments))
    pending = facts.expand_names(keyword_names(guard, "pending_items", facts.assignments))
    return keyword_is_self(guard, "scene") and bool(supplied) and visible.issubset(supplied) and newly_visible.issubset(pending)


def _covered_inside_children(
    facts: MethodFacts,
    guard: ast.Call,
    containers: set[str],
    children: set[str],
) -> set[str]:
    supplied_containers = facts.expand_names(positional_names(guard, 0, facts.assignments))
    supplied_children = facts.expand_names(positional_names(guard, 1, facts.assignments))
    if not supplied_containers.intersection(containers):
        return set()
    return supplied_children.intersection(children)


def check_method_layout_coverage(tree: ast.AST) -> list[LayoutFinding]:
    methods = scene_methods(tree)
    approved = approved_guard_calls(tree)
    if not methods:
        return [_finding("scene-method coverage", False, "no rendering scene method was found")]
    layout_failures: list[str] = []
    frame_failures: list[str] = []
    boundary_failures: list[str] = []
    placement_failures: list[str] = []
    control_flow_failures: list[str] = []
    traceability_failures: list[str] = []
    guarded_states = 0
    for facts in methods:
        if facts.unsupported_render_lines:
            lines = ", ".join(str(line) for line in facts.unsupported_render_lines[:6])
            control_flow_failures.append(f"{facts.qualified_name} has nested or unverified rendering at lines {lines}")
        visible: set[str] = set()
        previous_render = facts.line
        for render in facts.direct_calls:
            render_name = scene_method_name(render)
            if render_name in VISIBLE_REMOVE_CALLS:
                visible.difference_update(facts.visible_at(render))
                continue
            if render_name == "clear":
                visible.clear()
                continue
            if render_name not in VISIBLE_ADD_CALLS:
                continue
            previous_visible = set(visible)
            touched, persistent, removed = animation_state_changes(facts, render)
            if touched and persistent.issubset(removed):
                visible.difference_update(removed)
                previous_render = render.lineno
                continue
            guarded_visible = previous_visible | touched
            newly_visible = guarded_visible - previous_visible
            opaque = guarded_visible.intersection(facts.opaque_names)
            if not touched:
                traceability_failures.append(f"{facts.qualified_name} line {render.lineno} renders no assigned mobject")
            if opaque:
                traceability_failures.append(
                    f"{facts.qualified_name} line {render.lineno} has opaque helper results {sorted(opaque)}",
                )
            labels = guarded_visible.intersection(facts.label_names)
            blockers = guarded_visible.intersection(facts.data_names)
            containers = guarded_visible.intersection(facts.container_names)
            children = guarded_visible.intersection(facts.child_names)
            latest_placement = max(
                (line for line in facts.placement_lines if previous_render < line < render.lineno),
                default=previous_render,
            )
            if labels and blockers:
                guards = _calls_between(facts, "assert_scene_layout", latest_placement - 1, render.lineno, approved)
                if not any(_valid_scene_guard(facts, guard, labels, blockers, guarded_visible, newly_visible) for guard in guards):
                    layout_failures.append(f"{facts.qualified_name} before line {render.lineno}")
                else:
                    guarded_states += 1
                new_labels = newly_visible.intersection(facts.label_names)
                if new_labels and not any(previous_render < line < render.lineno for line in facts.placement_lines):
                    placement_failures.append(f"{facts.qualified_name} before line {render.lineno}")
            elif guarded_visible:
                guards = _calls_between(facts, "assert_within_frame", previous_render, render.lineno, approved)
                if not any(_valid_frame_guard(facts, guard, guarded_visible, newly_visible) for guard in guards):
                    frame_failures.append(f"{facts.qualified_name} before line {render.lineno}")
            if containers and children:
                guards = _calls_between(facts, "assert_inside", previous_render, render.lineno, approved)
                covered = (
                    set().union(
                        *(_covered_inside_children(facts, guard, containers, children) for guard in guards),
                    )
                    if guards
                    else set()
                )
                if not children.issubset(covered):
                    boundary_failures.append(f"{facts.qualified_name} before line {render.lineno}")
            visible.update(persistent)
            visible.difference_update(removed)
            previous_render = render.lineno
    return [
        _finding(
            "per-settled-state layout guard",
            not layout_failures,
            "; ".join(layout_failures[:6]) if layout_failures else f"{guarded_states} text/data settled states have complete guards",
        ),
        _finding(
            "safe placement",
            not placement_failures,
            "; ".join(placement_failures[:6]) if placement_failures else "every guarded text/data state has a prior placement operation",
        ),
        _finding(
            "frame boundary guard",
            not frame_failures,
            "; ".join(frame_failures[:6]) if frame_failures else "non-text/data states have scene-local frame guards",
        ),
        _finding(
            "object boundary guard",
            not boundary_failures,
            "; ".join(boundary_failures[:6]) if boundary_failures else "contained objects have scene-local assert_inside guards",
        ),
        _finding(
            "control-flow render safety",
            not control_flow_failures,
            "; ".join(control_flow_failures[:6]) if control_flow_failures else "render calls are in statically ordered scene statements",
        ),
        _finding(
            "rendered-object traceability",
            not traceability_failures,
            "; ".join(traceability_failures[:6]) if traceability_failures else "rendered mobjects have statically traceable assignments",
        ),
    ]


def evaluate_tree(tree: ast.AST) -> list[LayoutFinding]:
    findings = [*check_text_and_formula_calls(tree), *check_method_layout_coverage(tree)]
    has_mathtex = any(call_name(call.func) == "MathTex" for call in calls_in(tree))
    has_formula_text = any(
        call_name(call.func) == "Text" and any(signal in first_string_argument(call) for signal in MATH_SIGNAL_CHARS) for call in calls_in(tree)
    )
    findings.append(
        _finding(
            "MathTex usage",
            not has_formula_text or has_mathtex,
            "MathTex is present or no formula-like Text call exists",
        ),
    )
    return findings
