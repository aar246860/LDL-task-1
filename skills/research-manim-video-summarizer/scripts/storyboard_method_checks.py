from __future__ import annotations

import re
from collections import Counter
from typing import Final

from scripts.storyboard_contract_models import RubricFinding, make_finding
from scripts.storyboard_schema import ParsedStoryboard, canonical_token, meaningful

METHOD_FIELDS: Final = ("input state", "operation", "output state", "validity basis")
METHOD_VERB_PATTERN: Final = re.compile(
    r"\b(select|compute|calculate|transform|align|aggregate|fit|estimate|apply|calibrate|normalize|"
    r"interpolate|compare|derive|convert|classify|sample|map|solve|integrate|differentiate|filter|"
    r"rescale|project|update|simulate|evaluate|mark|overlay|plot|form|divide|multiply|add|"
    r"subtract|identify|extract|combine|separate|assign|construct|propagate|archive|store|save|"
    r"write|remove|display|summarize|validate|inspect|overwrite|replace|copy|move|label|draw|shade|"
    r"reveal|shrink|expand)(?:s|d|ed|ing)?\b",
    re.IGNORECASE,
)
ATOMIC_BREAK_PATTERN: Final = re.compile(
    r"\b(and|then|also|followed by|while|after|before|plus|simultaneously)\b|(?<!\d)\.(?!\d)|[;,:&/]",
    re.IGNORECASE,
)
INFINITIVE_ACTION_PATTERN: Final = re.compile(r"\bto\s+[a-z][a-z0-9_-]*\s+(?:the|a|an)\b", re.IGNORECASE)


def operation_verbs(operation: str) -> tuple[str, ...]:
    return tuple(match.lower() for match in METHOD_VERB_PATTERN.findall(operation))


def operation_issue(operation: str) -> str | None:
    text = " ".join(operation.lower().split())
    body = text.rstrip(".")
    verbs = operation_verbs(body)
    if not meaningful(text):
        return "operation is blank or unsupported"
    if not verbs:
        return "operation has no recognized atomic verb; rephrase it as one explicit action"
    if len(verbs) > 1 or ATOMIC_BREAK_PATTERN.search(body) is not None or INFINITIVE_ACTION_PATTERN.search(body):
        return f"operation contains multiple actions: {', '.join(dict.fromkeys(verbs))}"
    return None


def check_atomic_method_coverage(board: ParsedStoryboard, strict: bool) -> RubricFinding:
    if not strict:
        return make_finding("atomic method coverage", 2, "strict-only method ledger not required")
    ledger_ids = [row.identifier for row in board.method_rows]
    method_mode = board.metadata.token("story mode") == "method"
    if method_mode and not ledger_ids:
        return make_finding("atomic method coverage", 0, "method storyboard has no Mxx ledger rows", fail=True)
    invalid: list[str] = []
    ledger_by_id = {row.identifier: row for row in board.method_rows}
    for row in board.method_rows:
        if len(row.cells) >= 3:
            issue = operation_issue(row.cells[2])
            if issue is not None:
                invalid.append(f"{row.identifier} ledger {issue}")
    scene_ids: list[str] = []
    for scene in board.scenes:
        method = scene.fields.token("method step")
        background = scene.fields.token("background beat")
        beat = scene.fields.token("narrative beat")
        present_method_fields = [field for field in METHOD_FIELDS if scene.fields.all(field)]
        if method == "none":
            if present_method_fields:
                invalid.append(f"Scene {scene.number} has undeclared method fields")
            if beat == "mechanism":
                invalid.append(f"Scene {scene.number} is a mechanism without Mxx ownership")
            continue
        if re.fullmatch(r"m\d{2}", method) is None:
            invalid.append(f"Scene {scene.number} has invalid Method step")
            continue
        if background != "none":
            invalid.append(f"Scene {scene.number} combines method and background")
        scene_ids.append(method.upper())
        missing = [field for field in METHOD_FIELDS if not meaningful(scene.fields.one(field))]
        if missing:
            invalid.append(f"Scene {scene.number} missing {', '.join(missing)}")
        issue = operation_issue(scene.fields.one("operation"))
        if issue is not None:
            invalid.append(f"Scene {scene.number} {issue}")
        ledger_row = ledger_by_id.get(method.upper())
        if ledger_row is not None and len(ledger_row.cells) >= 5:
            for field, ledger_value in zip(METHOD_FIELDS, ledger_row.cells[1:5], strict=True):
                if canonical_token(scene.fields.one(field)) != canonical_token(ledger_value):
                    invalid.append(f"Scene {scene.number} {field} does not match {method.upper()} ledger semantics")
    counts = Counter(scene_ids)
    if scene_ids != ledger_ids:
        invalid.append("method scenes do not map one-to-one in ledger order")
    if any(count > 1 for count in counts.values()):
        invalid.append("a method identifier is reused")
    minimum_scene_count = len(board.background_rows) + len(board.method_rows) + 1
    if len(board.scenes) < minimum_scene_count:
        invalid.append(f"{len(board.scenes)} scenes are fewer than the derived minimum {minimum_scene_count}")
    if invalid:
        return make_finding("atomic method coverage", 0, "; ".join(invalid[:7]), fail=True)
    if not ledger_ids:
        return make_finding("atomic method coverage", 2, "non-method storyboard explicitly declares no method steps")
    return make_finding("atomic method coverage", 2, f"{len(ledger_ids)} ordered Mxx operations map one-to-one to atomic scenes")
