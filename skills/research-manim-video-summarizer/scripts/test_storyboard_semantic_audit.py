from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
import typer

from scripts import storyboard_semantic_audit
from scripts.check_storyboard_contract import main
from scripts.storyboard_semantic_audit import inspect_semantic_audit

FIXTURES = Path(__file__).parent / "fixtures"
AUDIT = FIXTURES / "storyboard_semantic_audit_good.json"
SOURCE = FIXTURES / "storyboard_source_fixture.md"
STORYBOARD = FIXTURES / "storyboard_good_geometry_first.md"


def write_audit(tmp_path: Path, mutate) -> Path:
    payload = json.loads(AUDIT.read_text(encoding="utf-8"))
    mutate(payload)
    path = tmp_path / "audit.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_complete_semantic_audit_passes() -> None:
    assert inspect_semantic_audit(AUDIT, SOURCE, STORYBOARD).passed


def test_storyboard_change_invalidates_bound_audit(tmp_path: Path) -> None:
    altered = tmp_path / "storyboard.md"
    altered.write_text(
        STORYBOARD.read_text(encoding="utf-8").replace(
            "select the measured peak.",
            "select an unrelated fictional threshold.",
            1,
        ),
        encoding="utf-8",
    )
    result = inspect_semantic_audit(AUDIT, SOURCE, altered)
    assert not result.passed
    assert "storyboard_sha256" in result.detail


def test_missing_method_audit_record_fails(tmp_path: Path) -> None:
    audit = write_audit(tmp_path, lambda payload: payload["method_items"].pop())
    assert not inspect_semantic_audit(audit, SOURCE, STORYBOARD).passed


def test_undeclared_scene_science_fails(tmp_path: Path) -> None:
    def mutate(payload: dict[str, Any]) -> None:
        payload["scene_items"][4]["undeclared_scientific_content"] = "secondary calibration"

    result = inspect_semantic_audit(write_audit(tmp_path, mutate), SOURCE, STORYBOARD)
    assert not result.passed
    assert "Scene 5" in result.detail


def test_excerpt_absent_from_source_fails(tmp_path: Path) -> None:
    def mutate(payload: dict[str, Any]) -> None:
        payload["background_items"][0]["source_excerpt"] = "Measured aquifer pressure increases continuously across the eastern boundary during pumping."

    result = inspect_semantic_audit(write_audit(tmp_path, mutate), SOURCE, STORYBOARD)
    assert not result.passed
    assert "absent from the source" in result.detail


def test_different_but_overlapping_source_excerpts_fail(tmp_path: Path) -> None:
    def mutate(payload: dict[str, Any]) -> None:
        payload["background_items"][1]["source_excerpt"] = (
            "identical nominal designs produced visibly different load-displacement responses. This observed mismatch motivates a comparison"
        )

    result = inspect_semantic_audit(write_audit(tmp_path, mutate), SOURCE, STORYBOARD)
    assert not result.passed
    assert "must not overlap" in result.detail


def test_recursive_json_failure_is_stable(monkeypatch: pytest.MonkeyPatch) -> None:
    def recurse(_text: str) -> None:
        raise RecursionError("deep JSON")

    monkeypatch.setattr(storyboard_semantic_audit.json, "loads", recurse)
    result = inspect_semantic_audit(AUDIT, SOURCE, STORYBOARD)
    assert not result.passed
    assert "cannot read semantic audit" in result.detail


def test_strict_cli_requires_semantic_evidence(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(typer.Exit) as caught:
        main(STORYBOARD, strict=True, json_output=True, source_artifact=None, semantic_audit=None)
    payload = json.loads(capsys.readouterr().out)
    assert caught.value.exit_code == 1
    assert payload["structural_passed"] is True
    assert payload["semantic_audit"]["passed"] is False


def test_strict_cli_passes_with_hash_bound_audit(capsys: pytest.CaptureFixture[str]) -> None:
    main(STORYBOARD, strict=True, json_output=True, source_artifact=SOURCE, semantic_audit=AUDIT)
    payload = json.loads(capsys.readouterr().out)
    assert payload["passed"] is True
