from __future__ import annotations

from pathlib import Path

from scripts.check_manim_layout import evaluate_layout
from scripts.manim_layout_support import LayoutReport


def _scene(tmp_path: Path, *lines: str) -> Path:
    path = tmp_path / "scene.py"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def _status(report: LayoutReport, check: str) -> str:
    return next(finding.status for finding in report.findings if finding.check == check)


def test_shadowed_noop_guard_is_rejected(tmp_path: Path) -> None:
    path = _scene(
        tmp_path,
        "from manim import Axes, MathTex, Scene",
        "def assert_scene_layout(**kwargs): pass",
        "class Shadowed(Scene):",
        "    def construct(self):",
        "        axes = Axes()",
        "        label = MathTex('Q').next_to(axes)",
        "        assert_scene_layout(scene=self, pending_items=[axes, label], labels=[label], blockers=[axes], frame_items=[axes, label])",
        "        self.add(axes, label)",
    )
    assert _status(evaluate_layout(path), "per-settled-state layout guard") == "fail"


def test_fixed_in_frame_render_api_requires_a_guard(tmp_path: Path) -> None:
    path = _scene(
        tmp_path,
        "from manim import MathTex, Scene",
        "class Fixed(Scene):",
        "    def construct(self):",
        "        label = MathTex('Q')",
        "        self.add_fixed_in_frame_mobjects(label)",
    )
    assert _status(evaluate_layout(path), "frame boundary guard") == "fail"


def test_construct_cannot_render_outside_numbered_helpers(tmp_path: Path) -> None:
    path = _scene(
        tmp_path,
        "from manim import Circle, Scene",
        "from assets.research_manim_layout import assert_within_frame",
        "class Mapped(Scene):",
        "    def construct(self):",
        "        extra = Circle()",
        "        assert_within_frame([extra], scene=self, pending_items=[extra])",
        "        self.add(extra)",
        "        self.scene_01_b01()",
        "    def scene_01_b01(self):",
        "        item = Circle()",
        "        assert_within_frame([item], scene=self, pending_items=[item])",
        "        self.add(item)",
    )
    from ast import parse

    from scripts.storyboard_source_mapping import inspect_source_scene_mapping

    finding = inspect_source_scene_mapping(parse(path.read_text(encoding="utf-8")), {1: "b01"})
    assert finding.status == "fail"


def test_unlisted_render_helper_is_rejected(tmp_path: Path) -> None:
    path = _scene(
        tmp_path,
        "from manim import Circle, Scene",
        "class Mapped(Scene):",
        "    def construct(self):",
        "        self.scene_01_b01()",
        "    def scene_01_b01(self):",
        "        self.add(Circle())",
        "    def helper(self):",
        "        self.add(Circle())",
    )
    from ast import parse

    from scripts.storyboard_source_mapping import inspect_source_scene_mapping

    finding = inspect_source_scene_mapping(parse(path.read_text(encoding="utf-8")), {1: "b01"})
    assert finding.status == "fail"
