from __future__ import annotations

import ast


def track_group_add(
    call: ast.Call,
    assignments: dict[str, ast.expr],
    group_members: dict[str, frozenset[str]],
    opaque_names: set[str],
) -> None:
    function = call.func
    if not (isinstance(function, ast.Attribute) and function.attr == "add" and isinstance(function.value, ast.Name) and function.value.id in group_members):
        return
    group_name = function.value.id
    added_names = {argument.id for argument in call.args if isinstance(argument, ast.Name) and argument.id in assignments}
    if len(added_names) == len(call.args):
        group_members[group_name] = frozenset({*group_members[group_name], *added_names})
    else:
        opaque_names.add(group_name)
