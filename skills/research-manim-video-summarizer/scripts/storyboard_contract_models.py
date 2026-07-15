from __future__ import annotations

from dataclasses import dataclass
from typing import Final

FORMULA_TERMS: Final = ("mathtex", "\\frac", "\\sum", "\\int", "`q_", "`r`", "`r =", "$")


@dataclass(frozen=True, slots=True)
class RubricFinding:
    check: str
    score: int
    maximum: int
    status: str
    detail: str


@dataclass(frozen=True, slots=True)
class StoryboardReport:
    score: int
    maximum: int
    threshold: int
    passed: bool
    findings: list[RubricFinding]


def normalize(text: str) -> str:
    return " ".join(text.lower().split())


def contains_any(text: str, terms: tuple[str, ...]) -> bool:
    return any(term in text for term in terms)


def count_matches(text: str, terms: tuple[str, ...]) -> int:
    return sum(1 for term in terms if term in text)


def first_position(text: str, terms: tuple[str, ...]) -> int:
    positions = [text.find(term) for term in terms if term in text]
    return -1 if not positions else min(positions)


def make_finding(check: str, score: int, detail: str, *, fail: bool = False) -> RubricFinding:
    status = "fail" if fail or score == 0 else "pass" if score == 2 else "revise"
    return RubricFinding(check=check, score=score, maximum=2, status=status, detail=detail)
