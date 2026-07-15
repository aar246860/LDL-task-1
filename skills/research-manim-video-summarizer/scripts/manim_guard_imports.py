from __future__ import annotations

import ast
from typing import Final

GUARD_MODULE: Final = "assets.research_manim_layout"
GUARD_NAMES: Final = {"assert_inside", "assert_scene_layout", "assert_within_frame"}


def _assigned_names(node: ast.AST) -> set[str]:
    names: set[str] = set()
    for item in ast.walk(node):
        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(item.name)
        elif isinstance(item, (ast.Assign, ast.AnnAssign, ast.NamedExpr)):
            targets = item.targets if isinstance(item, ast.Assign) else [item.target]
            names.update(target.id for target in targets if isinstance(target, ast.Name))
    return names


def approved_guard_calls(tree: ast.AST) -> dict[str, frozenset[int]]:
    direct: dict[str, str] = {}
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module == GUARD_MODULE:
            for alias in node.names:
                if alias.name in GUARD_NAMES:
                    direct[alias.asname or alias.name] = alias.name
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == GUARD_MODULE:
                    modules.add(alias.asname or alias.name)
    shadowed = _assigned_names(tree) - {node.name for node in ast.walk(tree) if isinstance(node, ast.alias)}
    direct = {local: canonical for local, canonical in direct.items() if local not in shadowed}
    approved: dict[str, set[int]] = {name: set() for name in GUARD_NAMES}
    for call in (node for node in ast.walk(tree) if isinstance(node, ast.Call)):
        if isinstance(call.func, ast.Name) and call.func.id in direct:
            approved[direct[call.func.id]].add(id(call))
        elif isinstance(call.func, ast.Attribute) and call.func.attr in GUARD_NAMES and isinstance(call.func.value, ast.Name) and call.func.value.id in modules:
            approved[call.func.attr].add(id(call))
    return {name: frozenset(calls) for name, calls in approved.items()}
