from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
from itertools import pairwise
from pathlib import Path

from scripts.json_mapping import as_object_map
from scripts.storyboard_schema import LedgerRow, ParsedStoryboard, parse_storyboard, substantive


@dataclass(frozen=True, slots=True)
class SemanticAuditResult:
    passed: bool
    detail: str


class SourceArtifactError(ValueError):
    pass


def _digest(content: bytes) -> str:
    return sha256(content).hexdigest()


def _review_time_is_valid(value: object) -> bool:
    if not isinstance(value, str):
        return False
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return parsed.tzinfo is not None and parsed.utcoffset() is not None


def _normalized(value: str) -> str:
    return " ".join(value.lower().split())


def _claim_basis(row: LedgerRow) -> str:
    return " ".join(row.cells[1:-1])


def _occurrence_spans(haystack: str, needle: str) -> list[tuple[int, int]]:
    spans: list[tuple[int, int]] = []
    start = haystack.find(needle)
    while start >= 0:
        spans.append((start, start + len(needle)))
        start = haystack.find(needle, start + 1)
    return spans


def _source_text(path: Path, content: bytes) -> str:
    if path.suffix.lower() != ".pdf":
        return content.decode("utf-8")
    try:
        from pypdf import PdfReader
        from pypdf.errors import PdfReadError
    except ImportError as exc:
        raise SourceArtifactError("PDF semantic audit requires pypdf") from exc
    try:
        return "\n".join(page.extract_text() or "" for page in PdfReader(path).pages)
    except (OSError, PdfReadError, ValueError) as exc:
        raise SourceArtifactError(f"cannot extract PDF text: {exc}") from exc


def _record_map(records: object, label: str, issues: list[str]) -> dict[str, dict[str, object]]:
    if not isinstance(records, list):
        issues.append(f"{label} must be a list")
        return {}
    mapped: dict[str, dict[str, object]] = {}
    for value in records:
        record = as_object_map(value)
        if record is None:
            issues.append(f"{label} contains a record without an id")
            continue
        identifier = record.get("id")
        if not isinstance(identifier, str) or not identifier.strip():
            issues.append(f"{label} contains a record without an id")
        elif identifier in mapped:
            issues.append(f"{label} repeats {identifier}")
        else:
            mapped[identifier] = record
    return mapped


def _check_ledger_records(
    records: object,
    rows: tuple[LedgerRow, ...],
    count_field: str,
    source_text: str,
    label: str,
    issues: list[str],
) -> list[tuple[str, int, int]]:
    mapped = _record_map(records, label, issues)
    expected = {row.identifier: row for row in rows}
    if set(mapped) != set(expected):
        issues.append(f"{label} coverage does not match the storyboard ledger")
    excerpts: list[tuple[str, int, int]] = []
    normalized_source = _normalized(source_text)
    for identifier, row in expected.items():
        record = mapped.get(identifier)
        if record is None:
            continue
        excerpt = record.get("source_excerpt")
        if record.get("source_locator") != row.cells[-1]:
            issues.append(f"{identifier} source locator does not match its ledger row")
        if not isinstance(excerpt, str) or not substantive(excerpt, minimum_units=8):
            issues.append(f"{identifier} lacks a substantive source excerpt")
        else:
            normalized_excerpt = _normalized(excerpt)
            spans = _occurrence_spans(normalized_source, normalized_excerpt)
            if not spans:
                issues.append(f"{identifier} excerpt is absent from the source artifact")
            elif len(spans) > 1:
                issues.append(f"{identifier} excerpt is ambiguous within the source artifact")
            else:
                excerpts.append((normalized_excerpt, *spans[0]))
            anchors = record.get("claim_anchor_terms")
            if not isinstance(anchors, list) or len(anchors) < 2 or not all(isinstance(anchor, str) and anchor.strip() for anchor in anchors):
                issues.append(f"{identifier} needs at least two claim anchor terms")
            else:
                claim_basis = _normalized(_claim_basis(row))
                for anchor in anchors:
                    assert isinstance(anchor, str)
                    normalized_anchor = _normalized(anchor)
                    if normalized_anchor not in claim_basis or normalized_anchor not in normalized_excerpt:
                        issues.append(f"{identifier} claim anchor is not shared by the storyboard claim and source excerpt")
        if record.get(count_field) != 1:
            issues.append(f"{identifier} must contain exactly one audited scientific unit")
        if record.get("semantic_match") != "pass":
            issues.append(f"{identifier} semantic comparison is not pass")
    return excerpts


def _check_scene_records(records: object, board: ParsedStoryboard, issues: list[str]) -> None:
    if not isinstance(records, list):
        issues.append("scene_items must be a list")
        return
    mapped: dict[int, dict[str, object]] = {}
    for value in records:
        record = as_object_map(value)
        if record is None:
            issues.append("scene_items contains a record without an integer scene")
            continue
        scene = record.get("scene")
        if not isinstance(scene, int) or isinstance(scene, bool):
            issues.append("scene_items contains a record without an integer scene")
        elif scene in mapped:
            issues.append(f"scene_items repeats Scene {scene}")
        else:
            mapped[scene] = record
    expected_numbers = {scene.number for scene in board.scenes}
    if set(mapped) != expected_numbers:
        issues.append("scene_items coverage does not match the storyboard")
    for scene in board.scenes:
        record = mapped.get(scene.number)
        if record is None:
            continue
        background_count = 0 if scene.fields.token("background beat") == "none" else 1
        method_count = 0 if scene.fields.token("method step") == "none" else 1
        if record.get("background_premise_count") != background_count:
            issues.append(f"Scene {scene.number} background premise count is incorrect")
        if record.get("method_operation_count") != method_count:
            issues.append(f"Scene {scene.number} method operation count is incorrect")
        if record.get("undeclared_scientific_content") != "none":
            issues.append(f"Scene {scene.number} has undeclared scientific content")
        if record.get("source_claims_checked") != "pass":
            issues.append(f"Scene {scene.number} source comparison is not pass")


def inspect_semantic_audit(audit: Path, source: Path, storyboard: Path) -> SemanticAuditResult:
    try:
        audit_bytes = audit.read_bytes()
        source_bytes = source.read_bytes()
        storyboard_bytes = storyboard.read_bytes()
        payload_value: object = json.loads(audit_bytes.decode("utf-8"))
        source_text = _source_text(source, source_bytes)
        board = parse_storyboard(storyboard_bytes.decode("utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError, RecursionError, SourceArtifactError) as exc:
        return SemanticAuditResult(False, f"cannot read semantic audit evidence: {exc}")
    payload = as_object_map(payload_value)
    if payload is None:
        return SemanticAuditResult(False, "semantic audit must be a JSON object")
    issues: list[str] = []
    fixed_fields = {
        "reviewer_role": "independent source auditor",
        "review_method": "source passage comparison",
        "audit_scope": "all background premises, method operations, and scene scientific claims",
        "decision": "pass",
        "source_artifact_sha256": _digest(source_bytes),
        "storyboard_sha256": _digest(storyboard_bytes),
    }
    reviewer = payload.get("reviewer")
    if not isinstance(reviewer, str) or not reviewer.strip():
        issues.append("semantic audit needs a named reviewer")
    if not _review_time_is_valid(payload.get("reviewed_at")):
        issues.append("semantic audit needs a timezone-aware reviewed_at time")
    for field, expected in fixed_fields.items():
        if payload.get(field) != expected:
            issues.append(f"semantic audit has invalid {field}")
    excerpts = _check_ledger_records(
        payload.get("background_items"),
        board.background_rows,
        "independent_premise_count",
        source_text,
        "background_items",
        issues,
    )
    excerpts.extend(
        _check_ledger_records(
            payload.get("method_items"),
            board.method_rows,
            "irreducible_operation_count",
            source_text,
            "method_items",
            issues,
        ),
    )
    if len(excerpts) != len({excerpt for excerpt, _, _ in excerpts}):
        issues.append("each audited ledger item needs a distinct source excerpt")
    ordered_spans = sorted(excerpts, key=lambda item: (item[1], item[2]))
    for previous, current in pairwise(ordered_spans):
        if current[1] < previous[2]:
            issues.append("audited source excerpts must not overlap")
            break
    _check_scene_records(payload.get("scene_items"), board, issues)
    if payload.get("unmapped_source_items") != []:
        issues.append("unmapped_source_items must be an explicitly empty list")
    if board.errors:
        issues.append("storyboard cannot be parsed without structural errors")
    if issues:
        return SemanticAuditResult(False, "; ".join(issues[:10]))
    return SemanticAuditResult(
        True,
        f"independent source audit covers {len(board.background_rows)} premises, {len(board.method_rows)} operations, and {len(board.scenes)} scenes",
    )
