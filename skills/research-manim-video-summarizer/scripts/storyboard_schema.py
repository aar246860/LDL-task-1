from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Final

FIELD_PATTERN: Final = re.compile(r"^\s*-\s*([^:]+):\s*(.*)$")
SCENE_PATTERN: Final = re.compile(r"^#{2,4}\s*Scene\s+(\d+)\s*:\s*(.+)$", re.IGNORECASE)
SECTION_PATTERN: Final = re.compile(r"^##(?!#)\s+(.+?)\s*$")
TABLE_SEPARATOR: Final = re.compile(r"^:?-{3,}:?$")
BACKGROUND_ID: Final = re.compile(r"B\d{2}", re.IGNORECASE)
METHOD_ID: Final = re.compile(r"M\d{2}", re.IGNORECASE)
RULE_ID: Final = re.compile(r"H(?:0[1-9]|1[0-9]|2[0-1])", re.IGNORECASE)
EMPTY_VALUES: Final = {"", "none", "n/a", "na", "tbd", "todo", "unknown", "placeholder"}
UNSUPPORTED_TERMS: Final = ("unsupported", "invented claim", "fabricated", "not verified", "not checked")
NEGATED_EVIDENCE_TERMS: Final = (
    "not reviewed",
    "unreviewed",
    "not shown",
    "no visual object",
    "do not show",
    "never shown",
)
NEGATED_DECLARATION_PATTERN: Final = re.compile(
    r"\b(?:avoid(?:ed|ing)?|omit(?:ted|ting)?|skip(?:ped|ping)?|absent|missing)\b|"
    r"\b(?:no|not|never|without)\b.{0,48}\b(?:inspect(?:ed|ing)?|review(?:ed|ing)?|"
    r"check(?:ed|ing)?|verif(?:y|ied|ying)|show(?:n|ing)?|call(?:ed|ing)?|use(?:d|ing)?|"
    r"include(?:d|ing)?|provide(?:d|ing)?|appear(?:ed|ing)?)\b",
    re.IGNORECASE,
)
CONTENT_UNIT_PATTERN: Final = re.compile(r"[A-Za-z0-9]+|[\u3400-\u9fff]")


def normalize_key(value: str) -> str:
    return " ".join(value.lower().strip().split())


def canonical_token(value: str) -> str:
    return value.strip().rstrip(".").strip().strip("`").lower()


def meaningful(value: str, *, allow_none: bool = False) -> bool:
    token = canonical_token(value)
    if not token or (not allow_none and token in EMPTY_VALUES):
        return False
    return not any(term in token for term in (*UNSUPPORTED_TERMS, *NEGATED_EVIDENCE_TERMS)) and (NEGATED_DECLARATION_PATTERN.search(token) is None)


def substantive(value: str, *, minimum_units: int) -> bool:
    units = [unit.lower() for unit in CONTENT_UNIT_PATTERN.findall(value)]
    minimum_unique = min(3, minimum_units)
    return meaningful(value) and len(units) >= minimum_units and len(set(units)) >= minimum_unique


@dataclass(frozen=True, slots=True)
class FieldMap:
    values: dict[str, tuple[str, ...]]

    def all(self, key: str) -> tuple[str, ...]:
        return self.values.get(normalize_key(key), ())

    def one(self, key: str) -> str:
        values = self.all(key)
        return values[0].strip() if len(values) == 1 else ""

    def token(self, key: str) -> str:
        return canonical_token(self.one(key))

    def duplicate_keys(self) -> list[str]:
        return [key for key, values in self.values.items() if len(values) > 1]


@dataclass(frozen=True, slots=True)
class LedgerRow:
    identifier: str
    cells: tuple[str, ...]
    line: int


@dataclass(frozen=True, slots=True)
class ParsedScene:
    number: int
    title: str
    line: int
    fields: FieldMap
    raw: str

    def rule_ids(self) -> set[str]:
        return {match.upper() for match in RULE_ID.findall(self.fields.one("source-derived rules"))}

    def has_formula(self) -> bool:
        formula = self.fields.token("formula")
        return (bool(formula) and formula != "none") or "mathtex" in self.raw.lower()


@dataclass(frozen=True, slots=True)
class ParsedStoryboard:
    raw: str
    metadata: FieldMap
    spine: FieldMap
    background_rows: tuple[LedgerRow, ...]
    method_rows: tuple[LedgerRow, ...]
    symbol_rows: tuple[LedgerRow, ...]
    scenes: tuple[ParsedScene, ...]
    symbol_glossary_present: bool
    errors: tuple[str, ...]


def _fields(lines: list[tuple[int, str]]) -> FieldMap:
    values: dict[str, list[str]] = {}
    fenced = False
    for _, line in lines:
        if line.lstrip().startswith("```"):
            fenced = not fenced
            continue
        if fenced:
            continue
        match = FIELD_PATTERN.match(line)
        if match is None:
            continue
        key = normalize_key(match.group(1))
        values.setdefault(key, []).append(match.group(2).strip())
    return FieldMap({key: tuple(items) for key, items in values.items()})


def _section(lines: list[str], heading: str) -> tuple[list[tuple[int, str]], bool]:
    start: int | None = None
    for index, line in enumerate(lines):
        match = SECTION_PATTERN.match(line)
        if match is not None and normalize_key(match.group(1)) == normalize_key(heading):
            start = index + 1
            break
    if start is None:
        return [], False
    end = len(lines)
    for index in range(start, len(lines)):
        if SECTION_PATTERN.match(lines[index]) is not None:
            end = index
            break
    return [(index + 1, lines[index]) for index in range(start, end)], True


def _split_table(line: str) -> tuple[str, ...]:
    return tuple(cell.strip() for cell in line.strip().strip("|").split("|"))


def _ledger_rows(
    lines: list[tuple[int, str]],
    id_pattern: re.Pattern[str] | None,
) -> tuple[tuple[LedgerRow, ...], list[str]]:
    rows: list[LedgerRow] = []
    errors: list[str] = []
    for line_number, line in lines:
        if not line.strip().startswith("|"):
            continue
        cells = _split_table(line)
        if not cells or all(TABLE_SEPARATOR.fullmatch(cell) for cell in cells):
            continue
        first = canonical_token(cells[0])
        if first in {"id", "symbol"}:
            continue
        if id_pattern is not None and id_pattern.fullmatch(first) is None:
            errors.append(f"line {line_number} has invalid ledger identifier '{cells[0]}'")
            continue
        if not first:
            errors.append(f"line {line_number} has a blank table identifier")
            continue
        rows.append(LedgerRow(first.upper(), cells, line_number))
    return tuple(rows), errors


def _scene_blocks(lines: list[tuple[int, str]]) -> tuple[tuple[ParsedScene, ...], list[str]]:
    headings: list[tuple[int, int, re.Match[str]]] = []
    fenced = False
    for position, (line_number, line) in enumerate(lines):
        if line.lstrip().startswith("```"):
            fenced = not fenced
            continue
        match = None if fenced else SCENE_PATTERN.match(line)
        if match is not None:
            headings.append((position, line_number, match))
    scenes: list[ParsedScene] = []
    errors: list[str] = []
    for index, (position, line_number, match) in enumerate(headings):
        end = headings[index + 1][0] if index + 1 < len(headings) else len(lines)
        block_lines = lines[position:end]
        fields = _fields(block_lines)
        try:
            number = int(match.group(1))
        except ValueError:
            errors.append(f"line {line_number} has an invalid scene number")
            continue
        raw = "\n".join(line for _, line in block_lines)
        scenes.append(ParsedScene(number, match.group(2).strip(), line_number, fields, raw))
        for key in fields.duplicate_keys():
            errors.append(f"Scene {number} repeats field '{key}'")
    numbers = [scene.number for scene in scenes]
    if numbers and numbers != list(range(1, len(numbers) + 1)):
        errors.append("scene numbers must be unique and sequential from 1")
    if not scenes:
        errors.append("Scene Table has no scene headings")
    return tuple(scenes), errors


def parse_storyboard(markdown: str) -> ParsedStoryboard:
    lines = markdown.splitlines()
    section_names = [normalize_key(match.group(1)) for line in lines if (match := SECTION_PATTERN.match(line))]
    metadata_lines, _ = _section(lines, "Metadata")
    spine_lines, _ = _section(lines, "Narrative Spine")
    background_lines, _ = _section(lines, "Background Ledger")
    method_lines, _ = _section(lines, "Method Decomposition Ledger")
    symbol_lines, symbol_present = _section(lines, "Symbol Glossary")
    scene_lines, scene_present = _section(lines, "Scene Table")
    background_rows, background_errors = _ledger_rows(background_lines, BACKGROUND_ID)
    method_rows, method_errors = _ledger_rows(method_lines, METHOD_ID)
    symbol_rows, symbol_errors = _ledger_rows(symbol_lines, None)
    scenes, scene_errors = _scene_blocks(scene_lines)
    metadata = _fields(metadata_lines)
    spine = _fields(spine_lines)
    errors = [*background_errors, *method_errors, *symbol_errors, *scene_errors]
    for section_name in (
        "metadata",
        "narrative spine",
        "background ledger",
        "method decomposition ledger",
        "symbol glossary",
        "scene table",
    ):
        if section_names.count(section_name) > 1:
            errors.append(f"section '{section_name}' appears more than once")
    for section_name, fields in (("Metadata", metadata), ("Narrative Spine", spine)):
        for key in fields.duplicate_keys():
            errors.append(f"{section_name} repeats field '{key}'")
    if not scene_present:
        errors.append("missing Scene Table section")
    return ParsedStoryboard(
        raw=markdown,
        metadata=metadata,
        spine=spine,
        background_rows=background_rows,
        method_rows=method_rows,
        symbol_rows=symbol_rows,
        scenes=scenes,
        symbol_glossary_present=symbol_present,
        errors=tuple(errors),
    )
