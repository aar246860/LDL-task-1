from __future__ import annotations

import ast
from typing import Final

from scripts.manim_ast_model import MethodFacts, call_name, calls_in, names_in

SOURCE_MUTATING_TRANSFORMS: Final = {"Transform"}
SOURCE_REPLACING_TRANSFORMS: Final = {
    "ReplacementTransform",
    "TransformMatchingShapes",
    "TransformMatchingTex",
    "FadeTransform",
}
REMOVAL_ANIMATIONS: Final = {"FadeOut", "Uncreate", "Unwrite", "RemoveTextLetterByLetter"}


def _argument_names(facts: MethodFacts, call: ast.Call, index: int) -> set[str]:
    if len(call.args) <= index:
        return set()
    return facts.expand_names(names_in(call.args[index]).intersection(facts.assignments))


def animation_state_changes(facts: MethodFacts, render: ast.Call) -> tuple[set[str], set[str], set[str]]:
    touched = facts.visible_at(render)
    persistent = set(touched)
    removed: set[str] = set()
    for animation in calls_in(render):
        name = call_name(animation.func)
        if name in SOURCE_MUTATING_TRANSFORMS:
            persistent.difference_update(_argument_names(facts, animation, 1))
        elif name in SOURCE_REPLACING_TRANSFORMS or name in REMOVAL_ANIMATIONS:
            removed.update(_argument_names(facts, animation, 0))
    return touched, persistent, removed
