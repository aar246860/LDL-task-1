from __future__ import annotations

import ast
from dataclasses import dataclass

from scripts.manim_ast_groups import track_group_add
from scripts.manim_ast_vocabulary import (
    CHILD_NAME_TERMS,
    CONTAINER_NAME_TERMS,
    DATA_CREATORS,
    DATA_NAME_TERMS,
    GROUP_CREATORS,
    KNOWN_ASSIGNMENT_CALLS,
    LABEL_CREATORS,
    LABEL_NAME_TERMS,
    NONVISUAL_CREATORS,
    PLACEMENT_CALLS,
    RENDER_CALLS,
    TRACEABLE_DERIVATION_CALLS,
)


def call_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return ""


def scene_method_name(call: ast.Call) -> str:
    func = call.func
    if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name) and func.value.id == "self":
        return func.attr
    return ""


def calls_in(node: ast.AST) -> tuple[ast.Call, ...]:
    return tuple(item for item in ast.walk(node) if isinstance(item, ast.Call))


def call_names_in(node: ast.AST) -> set[str]:
    return {call_name(call.func) for call in calls_in(node)}


def names_in(node: ast.AST) -> set[str]:
    return {item.id for item in ast.walk(node) if isinstance(item, ast.Name)}


def assignment_name(statement: ast.stmt) -> str | None:
    if isinstance(statement, ast.Assign) and len(statement.targets) == 1 and isinstance(statement.targets[0], ast.Name):
        return statement.targets[0].id
    if isinstance(statement, ast.AnnAssign) and isinstance(statement.target, ast.Name):
        return statement.target.id
    return None


def assignment_value(statement: ast.stmt) -> ast.expr | None:
    if isinstance(statement, (ast.Assign, ast.AnnAssign)):
        return statement.value
    return None


def direct_call(statement: ast.stmt) -> ast.Call | None:
    if isinstance(statement, ast.Expr) and isinstance(statement.value, ast.Call):
        return statement.value
    return None


def executable_statements(body: list[ast.stmt]) -> tuple[ast.stmt, ...]:
    statements: list[ast.stmt] = []
    for statement in body:
        if isinstance(statement, ast.If) and isinstance(statement.test, ast.Constant):
            branch = statement.body if bool(statement.test.value) else statement.orelse
            statements.extend(executable_statements(branch))
            continue
        statements.append(statement)
    return tuple(statements)


def traceable_group_item(item: ast.expr, assignments: dict[str, ast.expr]) -> bool:
    if isinstance(item, ast.Name):
        return item.id in assignments
    if isinstance(item, ast.Call):
        creators = call_names_in(item)
        return bool(creators.intersection(LABEL_CREATORS | DATA_CREATORS | GROUP_CREATORS)) and creators.issubset(
            KNOWN_ASSIGNMENT_CALLS,
        )
    return False


def group_values(value: ast.expr) -> list[ast.expr]:
    if isinstance(value, (ast.List, ast.Tuple, ast.Set)):
        return list(value.elts)
    group_call = next((call for call in calls_in(value) if call_name(call.func) in GROUP_CREATORS), None)
    return [] if group_call is None else list(group_call.args)


@dataclass(frozen=True, slots=True)
class MethodFacts:
    qualified_name: str
    line: int
    assignments: dict[str, ast.expr]
    label_names: frozenset[str]
    data_names: frozenset[str]
    container_names: frozenset[str]
    child_names: frozenset[str]
    group_members: dict[str, frozenset[str]]
    opaque_names: frozenset[str]
    unsupported_render_lines: tuple[int, ...]
    placement_lines: tuple[int, ...]
    direct_calls: tuple[ast.Call, ...]
    all_calls: tuple[ast.Call, ...]

    @property
    def render_calls(self) -> tuple[ast.Call, ...]:
        return tuple(call for call in self.direct_calls if scene_method_name(call) in RENDER_CALLS)

    def visible_at(self, render_call: ast.Call) -> set[str]:
        assigned = set(self.assignments)
        expanded = self.expand_names(names_in(render_call).intersection(assigned))
        return {name for name in expanded if not isinstance(self.assignments.get(name), (ast.List, ast.Tuple, ast.Set))}

    def expand_names(self, names: set[str]) -> set[str]:
        expanded = set(names)
        pending = list(names)
        while pending:
            name = pending.pop()
            for member in self.group_members.get(name, frozenset()):
                if member not in expanded:
                    expanded.add(member)
                    pending.append(member)
        return expanded


def method_facts(class_name: str, method: ast.FunctionDef | ast.AsyncFunctionDef) -> MethodFacts:
    statements = executable_statements(method.body)
    assignments: dict[str, ast.expr] = {}
    label_names: set[str] = set()
    data_names: set[str] = set()
    container_names: set[str] = set()
    child_names: set[str] = set()
    group_members: dict[str, frozenset[str]] = {}
    opaque_names: set[str] = set()
    unsupported_render_lines: list[int] = []
    placement_lines: list[int] = []
    direct_calls: list[ast.Call] = []
    for statement in statements:
        name = assignment_name(statement)
        value = assignment_value(statement)
        if name is not None and value is not None:
            assignments[name] = value
            creators = call_names_in(value)
            lowered_name = name.lower()
            sources = names_in(value).intersection(assignments)
            traceable_derivation = bool(sources) and creators.issubset(TRACEABLE_DERIVATION_CALLS)
            is_label = (
                bool(creators.intersection(LABEL_CREATORS))
                or any(term in lowered_name for term in LABEL_NAME_TERMS)
                or (traceable_derivation and bool(sources.intersection(label_names)))
            )
            is_data = (
                bool(creators.intersection(DATA_CREATORS))
                or any(term in lowered_name for term in DATA_NAME_TERMS)
                or (traceable_derivation and bool(sources.intersection(data_names)))
            )
            if is_label:
                label_names.add(name)
            if is_data:
                data_names.add(name)
            if any(term in lowered_name for term in CONTAINER_NAME_TERMS):
                container_names.add(name)
            if any(term in lowered_name for term in CHILD_NAME_TERMS):
                child_names.add(name)
            is_group = bool(creators.intersection(GROUP_CREATORS)) or isinstance(value, (ast.List, ast.Tuple, ast.Set))
            if is_group:
                group_members[name] = frozenset(names_in(value).intersection(assignments))
            grouped_values = group_values(value)
            unresolved_group = is_group and any(not traceable_group_item(item, assignments) for item in grouped_values)
            if unresolved_group or (
                isinstance(value, ast.Call)
                and (
                    bool(creators - KNOWN_ASSIGNMENT_CALLS) or (not is_label and not is_data and not creators.intersection(GROUP_CREATORS | NONVISUAL_CREATORS))
                )
            ):
                opaque_names.add(name)
            placement_lines.extend(call.lineno for call in calls_in(value) if call_name(call.func) in PLACEMENT_CALLS)
        call = direct_call(statement)
        if call is not None:
            track_group_add(call, assignments, group_members, opaque_names)
            direct_calls.append(call)
            if scene_method_name(call) == "play" and any(isinstance(node, ast.Attribute) and node.attr == "animate" for node in ast.walk(call)):
                unsupported_render_lines.append(call.lineno)
            if call_name(call.func) in PLACEMENT_CALLS:
                placement_lines.append(call.lineno)
        elif any(scene_method_name(nested) in RENDER_CALLS for nested in calls_in(statement)):
            unsupported_render_lines.extend(nested.lineno for nested in calls_in(statement) if scene_method_name(nested) in RENDER_CALLS)
    return MethodFacts(
        qualified_name=f"{class_name}.{method.name}",
        line=method.lineno,
        assignments=assignments,
        label_names=frozenset(label_names),
        data_names=frozenset(data_names),
        container_names=frozenset(container_names),
        child_names=frozenset(child_names),
        group_members=group_members,
        opaque_names=frozenset(opaque_names),
        unsupported_render_lines=tuple(unsupported_render_lines),
        placement_lines=tuple(placement_lines),
        direct_calls=tuple(direct_calls),
        all_calls=calls_in(method),
    )


def scene_methods(tree: ast.AST) -> tuple[MethodFacts, ...]:
    results: list[MethodFacts] = []
    for class_node in (node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)):
        for node in class_node.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                facts = method_facts(class_node.name, node)
                if facts.render_calls or facts.unsupported_render_lines:
                    results.append(facts)
    return tuple(results)


def keyword_names(call: ast.Call, keyword: str, assignments: dict[str, ast.expr]) -> set[str]:
    expression = next((item.value for item in call.keywords if item.arg == keyword), None)
    if expression is None:
        return set()
    if isinstance(expression, ast.Name) and expression.id in assignments:
        expression = assignments[expression.id]
    return names_in(expression).intersection(assignments)


def positional_names(call: ast.Call, index: int, assignments: dict[str, ast.expr]) -> set[str]:
    if len(call.args) <= index:
        return set()
    expression = call.args[index]
    if isinstance(expression, ast.Name) and expression.id in assignments:
        assigned = assignments[expression.id]
        if isinstance(assigned, (ast.List, ast.Tuple, ast.Set)):
            expression = assigned
        else:
            return {expression.id}
    return names_in(expression).intersection(assignments)


def keyword_is_self(call: ast.Call, keyword: str) -> bool:
    expression = next((item.value for item in call.keywords if item.arg == keyword), None)
    return isinstance(expression, ast.Name) and expression.id == "self"
