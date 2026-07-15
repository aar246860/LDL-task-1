from __future__ import annotations

from pathlib import Path

from scripts.check_manim_layout import evaluate_layout
from scripts.manim_layout_support import LayoutReport


def scene_source(*lines: str) -> str:
    return "\n".join(lines) + "\n"


def write_scene(tmp_path: Path, source: str) -> Path:
    path = tmp_path / "scene.py"
    path.write_text(source, encoding="utf-8")
    return path


def finding_status(report: LayoutReport, check: str) -> str:
    return next(finding.status for finding in report.findings if finding.check == check)


def test_render_inside_nonconstant_control_flow_fails(tmp_path: Path) -> None:
    scene = write_scene(
        tmp_path,
        scene_source(
            "from manim import Axes, Circle, Scene",
            "from assets.research_manim_layout import assert_within_frame",
            "class Conditional(Scene):",
            "    def construct(self):",
            "        axes = Axes()",
            "        assert_within_frame([axes], scene=self, pending_items=[axes])",
            "        self.add(axes)",
            "        if self.camera.frame_width > 0:",
            "            extra = Circle()",
            "            self.add(extra)",
        ),
    )
    report = evaluate_layout(scene)
    assert finding_status(report, "control-flow render safety") == "fail"


def test_vgroup_cannot_hide_text_data_state_behind_frame_guard(tmp_path: Path) -> None:
    scene = write_scene(
        tmp_path,
        scene_source(
            "from manim import UP, Axes, MathTex, Scene, VGroup",
            "from assets.research_manim_layout import assert_within_frame",
            "class Grouped(Scene):",
            "    def construct(self):",
            "        axes = Axes()",
            "        label = MathTex('Q').next_to(axes, UP)",
            "        group = VGroup(axes, label)",
            "        assert_within_frame([group], scene=self, pending_items=[group])",
            "        self.add(group)",
        ),
    )
    report = evaluate_layout(scene)
    assert finding_status(report, "per-settled-state layout guard") == "fail"


def test_helper_returned_label_is_still_classified_as_text(tmp_path: Path) -> None:
    scene = write_scene(
        tmp_path,
        scene_source(
            "from manim import UP, Axes, MathTex, Scene",
            "from assets.research_manim_layout import assert_within_frame",
            "def make_label():",
            "    return MathTex('Q')",
            "class HelperLabel(Scene):",
            "    def construct(self):",
            "        axes = Axes()",
            "        label = make_label().next_to(axes, UP)",
            "        assert_within_frame([axes, label], scene=self, pending_items=[axes, label])",
            "        self.add(axes, label)",
        ),
    )
    report = evaluate_layout(scene)
    assert finding_status(report, "per-settled-state layout guard") == "fail"
    assert finding_status(report, "rendered-object traceability") == "fail"


def test_geometry_mutation_after_guard_invalidates_guard(tmp_path: Path) -> None:
    scene = write_scene(
        tmp_path,
        scene_source(
            "from manim import RIGHT, UP, Axes, MathTex, Scene",
            "from assets.research_manim_layout import assert_scene_layout",
            "class StaleAfterShift(Scene):",
            "    def construct(self):",
            "        axes = Axes()",
            "        label = MathTex('Q').next_to(axes, UP)",
            "        assert_scene_layout(scene=self, pending_items=[axes, label], labels=[label], blockers=[axes], frame_items=[axes, label])",
            "        label.shift(RIGHT * 100)",
            "        self.add(axes, label)",
        ),
    )
    report = evaluate_layout(scene)
    assert finding_status(report, "per-settled-state layout guard") == "fail"


def test_annulus_without_frame_guard_fails(tmp_path: Path) -> None:
    scene = write_scene(
        tmp_path,
        scene_source(
            "from manim import Annulus, Scene",
            "class Ring(Scene):",
            "    def construct(self):",
            "        ring = Annulus()",
            "        self.add(ring)",
        ),
    )
    report = evaluate_layout(scene)
    assert finding_status(report, "frame boundary guard") == "fail"


def test_independent_containment_pairs_pass(tmp_path: Path) -> None:
    scene = write_scene(
        tmp_path,
        scene_source(
            "from manim import Circle, Rectangle, Scene",
            "from assets.research_manim_layout import assert_inside, assert_within_frame",
            "class SeparatePairs(Scene):",
            "    def construct(self):",
            "        left_boundary = Rectangle(width=4, height=3)",
            "        right_boundary = Rectangle(width=4, height=3)",
            "        left_ring = Circle(radius=0.5)",
            "        right_ring = Circle(radius=0.5)",
            "        assert_inside(left_boundary, [left_ring])",
            "        assert_inside(right_boundary, [right_ring])",
            "        items = [left_boundary, right_boundary, left_ring, right_ring]",
            "        assert_within_frame(items, scene=self, pending_items=items)",
            "        self.add(*items)",
        ),
    )
    assert evaluate_layout(scene).passed


def test_removed_label_is_not_required_in_later_state(tmp_path: Path) -> None:
    scene = write_scene(
        tmp_path,
        scene_source(
            "from manim import UP, Axes, Circle, MathTex, Scene",
            "from assets.research_manim_layout import assert_scene_layout, assert_within_frame",
            "class RemoveLabel(Scene):",
            "    def construct(self):",
            "        axes = Axes()",
            "        label = MathTex('Q').next_to(axes, UP)",
            "        assert_scene_layout(scene=self, pending_items=[axes, label], labels=[label], blockers=[axes], frame_items=[axes, label])",
            "        self.add(axes, label)",
            "        self.remove(label)",
            "        circle = Circle()",
            "        assert_within_frame([axes, circle], scene=self, pending_items=[circle])",
            "        self.add(circle)",
        ),
    )
    assert evaluate_layout(scene).passed


def test_opaque_helper_result_is_rejected(tmp_path: Path) -> None:
    scene = write_scene(
        tmp_path,
        scene_source(
            "from manim import Circle, Scene",
            "from assets.research_manim_layout import assert_within_frame",
            "def make_visual():",
            "    return Circle()",
            "class Opaque(Scene):",
            "    def construct(self):",
            "        mystery = make_visual()",
            "        assert_within_frame([mystery], scene=self, pending_items=[mystery])",
            "        self.add(mystery)",
        ),
    )
    report = evaluate_layout(scene)
    assert finding_status(report, "rendered-object traceability") == "fail"


def test_starred_helper_contents_inside_group_are_rejected(tmp_path: Path) -> None:
    scene = write_scene(
        tmp_path,
        scene_source(
            "from manim import Axes, Scene, Text, VGroup",
            "from assets.research_manim_layout import assert_within_frame",
            "def build_contents():",
            "    return [Axes(), Text('hidden label')]",
            "class HiddenGroup(Scene):",
            "    def construct(self):",
            "        group = VGroup(*build_contents())",
            "        assert_within_frame([group], scene=self, pending_items=[group])",
            "        self.add(group)",
        ),
    )
    report = evaluate_layout(scene)
    assert finding_status(report, "rendered-object traceability") == "fail"
