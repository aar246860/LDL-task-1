from __future__ import annotations

import ast
import re
from typing import Final

from scripts.manim_ast_vocabulary import RENDER_CALLS
from scripts.manim_layout_support import LayoutFinding

SCENE_HELPER_PATTERN: Final = re.compile(r"^scene_(\d{2})_([a-z0-9_]+)$")
RENDER_METHODS: Final = RENDER_CALLS


def _self_call_name(statement: ast.stmt) -> str | None:
    if not isinstance(statement, ast.Expr) or not isinstance(statement.value, ast.Call):
        return None
    function = statement.value.func
    if not isinstance(function, ast.Attribute) or not isinstance(function.value, ast.Name):
        return None
    return function.attr if function.value.id == "self" else None


def _has_direct_render(method: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    return any(
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id == "self"
        and node.func.attr in RENDER_METHODS
        for node in ast.walk(method)
    )


def _inherits_scene(class_node: ast.ClassDef) -> bool:
    return any((isinstance(base, ast.Name) and base.id == "Scene") or (isinstance(base, ast.Attribute) and base.attr == "Scene") for base in class_node.bases)


def inspect_source_scene_mapping(tree: ast.AST, expected_roles: dict[int, str]) -> LayoutFinding:
    candidates: list[tuple[list[int], dict[int, tuple[str, ast.FunctionDef | ast.AsyncFunctionDef]]]] = []
    for class_node in (node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)):
        if not _inherits_scene(class_node):
            continue
        methods = {node.name: node for node in class_node.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}
        construct = methods.get("construct")
        if construct is None:
            continue
        sequence: list[int] = []
        helpers: dict[int, tuple[str, ast.FunctionDef | ast.AsyncFunctionDef]] = {}
        for name, method in methods.items():
            match = SCENE_HELPER_PATTERN.fullmatch(name)
            if match is not None:
                helpers[int(match.group(1))] = (match.group(2), method)
        for statement in construct.body:
            name = _self_call_name(statement)
            match = None if name is None else SCENE_HELPER_PATTERN.fullmatch(name)
            if match is not None:
                sequence.append(int(match.group(1)))
        if sequence or helpers:
            candidates.append((sequence, helpers))
    expected = sorted(expected_roles)
    if len(candidates) != 1:
        return LayoutFinding(
            check="source scene mapping",
            status="fail",
            detail="source needs exactly one Scene class with numbered scene helpers",
        )
    sequence, helpers = candidates[0]
    invalid: list[str] = []
    methods: dict[str, ast.FunctionDef | ast.AsyncFunctionDef] = {}
    for class_node in (node for node in ast.walk(tree) if isinstance(node, ast.ClassDef) and _inherits_scene(node)):
        methods = {node.name: node for node in class_node.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}
        if "construct" in methods:
            break
    construct = methods.get("construct")
    if construct is None:
        return LayoutFinding(check="source scene mapping", status="fail", detail="Scene class has no construct method")
    extra_construct_calls = [
        call.lineno
        for call in (node for node in ast.walk(construct) if isinstance(node, ast.Call))
        if (
            isinstance(call.func, ast.Attribute)
            and isinstance(call.func.value, ast.Name)
            and call.func.value.id == "self"
            and SCENE_HELPER_PATTERN.fullmatch(call.func.attr) is None
        )
    ]
    unlisted_render_methods = [
        name for name, method in methods.items() if name != "construct" and SCENE_HELPER_PATTERN.fullmatch(name) is None and _has_direct_render(method)
    ]
    if extra_construct_calls:
        invalid.append(f"construct has unowned self calls at lines {extra_construct_calls[:6]}")
    if unlisted_render_methods:
        invalid.append(f"unlisted helpers contain direct render calls: {sorted(unlisted_render_methods)}")
    if sequence != expected:
        invalid.append(f"construct calls scene helpers in order {sequence}; expected {expected}")
    if sorted(helpers) != expected:
        invalid.append(f"source helper coverage is {sorted(helpers)}; expected {expected}")
    wrong_roles = [
        number for number, (suffix, _) in helpers.items() if suffix != expected_roles.get(number) and not suffix.startswith(f"{expected_roles.get(number)}_")
    ]
    if wrong_roles:
        invalid.append(f"scene helper ownership does not match storyboard roles: {sorted(wrong_roles)}")
    unrendered = [number for number, (_, helper) in helpers.items() if not _has_direct_render(helper)]
    if unrendered:
        invalid.append(f"scene helpers without direct add/play calls: {sorted(unrendered)}")
    return LayoutFinding(
        check="source scene mapping",
        status="fail" if invalid else "pass",
        detail="; ".join(invalid) if invalid else f"{len(expected)} numbered helpers map one-to-one to storyboard scenes",
    )
