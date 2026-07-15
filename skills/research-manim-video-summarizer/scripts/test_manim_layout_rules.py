from __future__ import annotations

from pathlib import Path

import pytest

from scripts.check_manim_layout import evaluate_layout
from scripts.manim_layout_support import LayoutReport

FIXTURES = Path(__file__).parent / "fixtures"
GOOD_SCENE = FIXTURES / "layout_good.py"
GOOD_STORYBOARD = FIXTURES / "storyboard_good_geometry_first.md"
BAD_LAYOUT_CASES = (
    ("layout_bad.py", "math in Text"),
    ("layout_bad_missing_overlap_guard.py", "per-settled-state layout guard"),
    ("layout_bad_missing_boundary_guard.py", "object boundary guard"),
)


def finding_status(report: LayoutReport, check: str) -> str:
    return next(finding.status for finding in report.findings if finding.check == check)


def write_scene(tmp_path: Path, source: str) -> Path:
    path = tmp_path / "scene.py"
    path.write_text(source, encoding="utf-8")
    return path


def scene_source(*lines: str) -> str:
    return "\n".join(lines) + "\n"


def test_good_layout_fixtures_pass() -> None:
    assert evaluate_layout(GOOD_SCENE).passed
    assert evaluate_layout(FIXTURES / "layout_good_boundary_guard.py").passed


@pytest.mark.parametrize(("fixture", "check"), BAD_LAYOUT_CASES)
def test_named_bad_layout_fails_its_target_check(fixture: str, check: str) -> None:
    report = evaluate_layout(FIXTURES / fixture)
    assert not report.passed
    assert finding_status(report, check) == "fail"


def test_unreachable_empty_guard_does_not_count(tmp_path: Path) -> None:
    scene = write_scene(
        tmp_path,
        scene_source(
            "from manim import UP, Axes, MathTex, Scene",
            "from assets.research_manim_layout import assert_scene_layout",
            "class DeadGuard(Scene):",
            "    def construct(self):",
            "        axes = Axes()",
            "        label = MathTex(r'Q').next_to(axes, UP)",
            "        if False:",
            "            assert_scene_layout(labels=[], blockers=[], frame_items=[])",
            "        self.add(axes, label)",
        ),
    )
    report = evaluate_layout(scene)
    assert finding_status(report, "per-settled-state layout guard") == "fail"


def test_reachable_empty_guard_does_not_count(tmp_path: Path) -> None:
    scene = write_scene(
        tmp_path,
        scene_source(
            "from manim import UP, Axes, MathTex, Scene",
            "from assets.research_manim_layout import assert_scene_layout",
            "class EmptyGuard(Scene):",
            "    def construct(self):",
            "        axes = Axes()",
            "        label = MathTex(r'Q').next_to(axes, UP)",
            "        assert_scene_layout(labels=[], blockers=[], frame_items=[])",
            "        self.add(axes, label)",
        ),
    )
    report = evaluate_layout(scene)
    assert finding_status(report, "per-settled-state layout guard") == "fail"


def test_one_scene_guard_cannot_mask_another(tmp_path: Path) -> None:
    scene = write_scene(
        tmp_path,
        scene_source(
            "from manim import UP, Axes, MathTex, Scene",
            "from assets.research_manim_layout import assert_scene_layout",
            "class First(Scene):",
            "    def construct(self):",
            "        axes = Axes()",
            "        label = MathTex(r'Q').next_to(axes, UP)",
            "        assert_scene_layout(labels=[label], blockers=[axes], frame_items=[axes, label])",
            "        self.add(axes, label)",
            "class Second(Scene):",
            "    def construct(self):",
            "        axes = Axes()",
            "        label = MathTex(r'K').next_to(axes, UP)",
            "        self.add(axes, label)",
        ),
    )
    report = evaluate_layout(scene)
    assert finding_status(report, "per-settled-state layout guard") == "fail"


def test_frame_guard_is_not_containment_guard(tmp_path: Path) -> None:
    scene = write_scene(
        tmp_path,
        scene_source(
            "from manim import Circle, Rectangle, Scene",
            "from assets.research_manim_layout import assert_within_frame",
            "class WrongBoundaryGuard(Scene):",
            "    def construct(self):",
            "        aquifer = Rectangle()",
            "        halo = Circle()",
            "        assert_within_frame([aquifer, halo])",
            "        self.add(aquifer, halo)",
        ),
    )
    report = evaluate_layout(scene)
    assert finding_status(report, "object boundary guard") == "fail"


def test_every_rendered_state_needs_a_fresh_guard(tmp_path: Path) -> None:
    scene = write_scene(
        tmp_path,
        scene_source(
            "from manim import UP, Axes, MathTex, Scene",
            "from assets.research_manim_layout import assert_scene_layout",
            "class TwoStates(Scene):",
            "    def construct(self):",
            "        axes = Axes()",
            "        label = MathTex(r'Q').next_to(axes, UP)",
            "        assert_scene_layout(labels=[label], blockers=[axes], frame_items=[axes, label])",
            "        self.add(axes, label)",
            "        self.play(label.animate.shift(UP))",
        ),
    )
    report = evaluate_layout(scene)
    assert finding_status(report, "per-settled-state layout guard") == "fail"


def test_invalid_python_returns_stable_finding(tmp_path: Path) -> None:
    scene = write_scene(tmp_path, "def broken(:\n")
    report = evaluate_layout(scene)
    assert finding_status(report, "input artifact") == "fail"
