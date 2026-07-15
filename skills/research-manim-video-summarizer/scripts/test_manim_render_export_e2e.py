from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from scripts.publish_companion_validation import validate_companion_artifacts
from scripts.publish_media_validation import validate_browser_video

SKILL_ROOT = Path(__file__).resolve().parent.parent
SCENE_SOURCE = SKILL_ROOT / "scripts" / "fixtures" / "layout_good_storyboard_mapping.py"


def test_real_manim_render_exports_browser_ready_package(tmp_path: Path) -> None:
    media = tmp_path / "media"
    environment = dict(os.environ)
    environment["PYTHONPATH"] = os.pathsep.join(filter(None, (str(SKILL_ROOT), environment.get("PYTHONPATH"))))
    render = subprocess.run(
        [
            sys.executable,
            "-m",
            "manim",
            "-ql",
            "--disable_caching",
            "--progress_bar",
            "none",
            "--fps",
            "15",
            "-r",
            "426,240",
            "--media_dir",
            str(media),
            str(SCENE_SOURCE),
            "StoryboardMappedScene",
        ],
        cwd=SKILL_ROOT,
        env=environment,
        capture_output=True,
        text=True,
        timeout=180,
        check=False,
    )
    assert render.returncode == 0, render.stderr or render.stdout
    rendered = next(media.rglob("StoryboardMappedScene.mp4"))
    output = tmp_path / "output"
    export = subprocess.run(
        [
            sys.executable,
            str(SKILL_ROOT / "scripts" / "export_manim_video.py"),
            str(rendered),
            str(output),
            "--slug",
            "e2e",
            "--title",
            "E2E research animation",
        ],
        cwd=SKILL_ROOT,
        env=environment,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    assert export.returncode == 0, export.stderr or export.stdout
    video = output / "e2e.mp4"
    contact = output / "e2e_contact_sheet.png"
    html = output / "e2e.html"
    metadata = output / "e2e_metadata.json"
    qa_notes = output / "e2e_qa.md"
    validate_browser_video(video)
    validate_companion_artifacts(html, metadata, qa_notes, video, contact)
