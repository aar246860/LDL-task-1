from __future__ import annotations

import re
from typing import Final

from scripts.storyboard_schema import LedgerRow, canonical_token, meaningful, substantive

LOCATOR_TERMS: Final = (
    "section",
    "sec.",
    "figure",
    "fig.",
    "table",
    "equation",
    "eq.",
    "page",
    "dataset",
    "doi",
    "appendix",
    "supplement",
    "repository",
    "source",
    "fixture",
)
SPINE_REQUIREMENTS: Final = {
    "throughline": 6,
    "audience starting point": 4,
    "stakes": 5,
    "resolution": 5,
    "background scope": 5,
    "method scope": 5,
}


def row_issues(
    label: str,
    rows: tuple[LedgerRow, ...],
    expected_cells: int,
    *,
    require_locator: bool = True,
    minimum_semantic_units: int | None = 3,
) -> list[str]:
    issues: list[str] = []
    identifiers = [row.identifier for row in rows]
    if len(identifiers) != len(set(identifiers)):
        issues.append(f"{label} repeats an identifier")
    semantics = [tuple(canonical_token(cell) for cell in row.cells[1:-1]) for row in rows]
    if len(semantics) != len(set(semantics)):
        issues.append(f"{label} repeats the same semantic row")
    for row in rows:
        if len(row.cells) != expected_cells:
            issues.append(f"{row.identifier} has {len(row.cells)} cells; expected {expected_cells}")
        elif any(not meaningful(cell) for cell in row.cells):
            issues.append(f"{row.identifier} contains a blank or unsupported cell")
        elif minimum_semantic_units is not None and any(not substantive(cell, minimum_units=minimum_semantic_units) for cell in row.cells[1:-1]):
            issues.append(f"{row.identifier} contains non-substantive semantic cells")
        elif require_locator and (not substantive(row.cells[-1], minimum_units=3) or not any(term in row.cells[-1].lower() for term in LOCATOR_TERMS)):
            issues.append(f"{row.identifier} lacks a substantive source locator")
    return issues


def scope_count(value: str) -> int | None:
    match = re.match(r"^\s*(\d+)\b", value)
    return None if match is None else int(match.group(1))
