from __future__ import annotations

import json
from pathlib import Path

import pytest
import typer

from scripts.check_storyboard_contract import main


def test_missing_path_returns_machine_readable_json(capsys: pytest.CaptureFixture[str], tmp_path: Path) -> None:
    with pytest.raises(typer.Exit) as caught:
        main(tmp_path / "missing.md", strict=True, json_output=True)

    payload = json.loads(capsys.readouterr().out)
    assert caught.value.exit_code == 2
    assert payload["passed"] is False
    assert "expected a readable file" in payload["error"]


def test_directory_returns_machine_readable_json(capsys: pytest.CaptureFixture[str], tmp_path: Path) -> None:
    with pytest.raises(typer.Exit) as caught:
        main(tmp_path, strict=True, json_output=True)

    payload = json.loads(capsys.readouterr().out)
    assert caught.value.exit_code == 2
    assert payload["passed"] is False
