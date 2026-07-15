from __future__ import annotations

from pathlib import Path

from scripts.check_manim_layout import evaluate_layout
from scripts.manim_layout_support import LayoutReport


def write_scene(tmp_path: Path, *lines: str) -> Path:
    path = tmp_path / "scene.py"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def status(report: LayoutReport, check: str) -> str:
    return next(finding.status for finding in report.findings if finding.check == check)


def test_decimal_number_requires_text_data_guard(tmp_path: Path) -> None:
    scene = write_scene(
        tmp_path,
        "from manim import Axes, DecimalNumber, Scene",
        "from assets.research_manim_layout import assert_within_frame",
        "class NumericLabel(Scene):",
        "    def construct(self):",
        "        axes = Axes()",
        "        value = DecimalNumber(2.5).next_to(axes)",
        "        assert_within_frame([axes, value], scene=self, pending_items=[axes, value])",
        "        self.add(axes, value)",
    )
    assert status(evaluate_layout(scene), "per-settled-state layout guard") == "fail"


def test_animate_target_is_rejected_as_unverified(tmp_path: Path) -> None:
    scene = write_scene(
        tmp_path,
        "from manim import RIGHT, Axes, MathTex, Scene",
        "from assets.research_manim_layout import assert_scene_layout",
        "class MovingLabel(Scene):",
        "    def construct(self):",
        "        axes = Axes()",
        "        label = MathTex('Q').next_to(axes)",
        "        assert_scene_layout(scene=self, pending_items=[axes, label], labels=[label], blockers=[axes], frame_items=[axes, label])",
        "        self.add(axes, label)",
        "        self.play(label.animate.shift(RIGHT * 100))",
    )
    assert status(evaluate_layout(scene), "control-flow render safety") == "fail"


def test_geometry_mutation_after_guard_requires_a_new_guard(tmp_path: Path) -> None:
    scene = write_scene(
        tmp_path,
        "from manim import Axes, MathTex, Scene, UP",
        "from assets.research_manim_layout import assert_scene_layout",
        "class MovingLabel(Scene):",
        "    def construct(self):",
        "        axes = Axes()",
        "        label = MathTex('Q').next_to(axes)",
        "        assert_scene_layout(scene=self, pending_items=[axes, label], labels=[label], blockers=[axes], frame_items=[axes, label])",
        "        self.add(axes, label)",
        "        label.put_start_and_end_on(UP, UP * 100)",
        "        self.play(label.animate.shift(UP))",
    )
    assert status(evaluate_layout(scene), "per-settled-state layout guard") == "fail"


def test_group_add_is_not_treated_as_scene_render(tmp_path: Path) -> None:
    scene = write_scene(
        tmp_path,
        "from manim import Circle, Scene, VGroup",
        "from assets.research_manim_layout import assert_within_frame",
        "class GroupMutation(Scene):",
        "    def construct(self):",
        "        circle = Circle()",
        "        group = VGroup()",
        "        group.add(circle)",
        "        assert_within_frame([group], scene=self, pending_items=[group])",
        "        self.add(group)",
    )
    assert evaluate_layout(scene).passed


def test_group_add_cannot_hide_text_data_members(tmp_path: Path) -> None:
    scene = write_scene(
        tmp_path,
        "from manim import Axes, MathTex, Scene, VGroup",
        "from assets.research_manim_layout import assert_within_frame",
        "class GroupMutation(Scene):",
        "    def construct(self):",
        "        axes = Axes()",
        "        label = MathTex('Q').next_to(axes)",
        "        group = VGroup()",
        "        group.add(axes, label)",
        "        assert_within_frame([group], scene=self, pending_items=[group])",
        "        self.add(group)",
    )
    assert status(evaluate_layout(scene), "per-settled-state layout guard") == "fail"


def test_positioned_target_copy_can_be_guarded_before_transform(tmp_path: Path) -> None:
    scene = write_scene(
        tmp_path,
        "from manim import LEFT, RIGHT, Axes, Circle, MathTex, Scene, Transform",
        "from assets.research_manim_layout import assert_scene_layout",
        "class GuardedTarget(Scene):",
        "    def construct(self):",
        "        axes = Axes()",
        "        label = MathTex('Q').next_to(axes)",
        "        assert_scene_layout(scene=self, pending_items=[axes, label], labels=[label], blockers=[axes], frame_items=[axes, label])",
        "        self.add(axes, label)",
        "        target = label.copy().shift(RIGHT * 3)",
        "        assert_scene_layout(scene=self, pending_items=[target], labels=[label, target], blockers=[axes], frame_items=[axes, label, target])",
        "        self.play(Transform(label, target))",
        "        circle = Circle().shift(LEFT * 3)",
        "        assert_scene_layout(scene=self, pending_items=[circle], labels=[label], blockers=[axes, circle], frame_items=[axes, label, circle])",
        "        self.add(circle)",
    )
    assert evaluate_layout(scene).passed


def test_faded_label_is_removed_from_later_static_state(tmp_path: Path) -> None:
    scene = write_scene(
        tmp_path,
        "from manim import LEFT, RIGHT, Axes, Circle, FadeOut, MathTex, Scene",
        "from assets.research_manim_layout import assert_scene_layout, assert_within_frame",
        "class FadedLabel(Scene):",
        "    def construct(self):",
        "        axes = Axes()",
        "        label = MathTex('Q').next_to(axes)",
        "        assert_scene_layout(scene=self, pending_items=[axes, label], labels=[label], blockers=[axes], frame_items=[axes, label])",
        "        self.add(axes, label)",
        "        label.shift(RIGHT * 0)",
        "        assert_scene_layout(scene=self, pending_items=[], labels=[label], blockers=[axes], frame_items=[axes, label])",
        "        self.play(FadeOut(label))",
        "        circle = Circle().shift(LEFT * 3)",
        "        assert_within_frame([axes, circle], scene=self, pending_items=[circle])",
        "        self.add(circle)",
    )
    assert evaluate_layout(scene).passed
