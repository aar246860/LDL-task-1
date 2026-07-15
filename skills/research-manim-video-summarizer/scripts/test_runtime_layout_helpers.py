from __future__ import annotations

import pytest
from manim import DOWN, LEFT, RIGHT, UP, Circle, Rectangle, Scene, VGroup, VMobject

from assets.research_manim_layout import (
    LayoutContractError,
    assert_inside,
    assert_scene_layout,
    assert_within_frame,
)


def test_clear_runtime_layout_passes() -> None:
    scene = Scene()
    left = Rectangle(width=1.0, height=0.5).shift(LEFT * 2)
    right = Rectangle(width=1.0, height=0.5).shift(RIGHT * 2)
    blocker = Rectangle(width=2.0, height=0.5).shift(DOWN * 2)
    pending = [left, right, blocker]
    assert_scene_layout(
        scene=scene,
        pending_items=pending,
        labels=[left, right],
        blockers=[blocker],
        frame_items=pending,
    )


def test_overlapping_labels_raise() -> None:
    scene = Scene()
    label = Rectangle(width=1.0, height=0.5)
    second_label = label.copy()
    blocker = Rectangle(width=1.0, height=0.5).shift(DOWN * 2)
    with pytest.raises(LayoutContractError):
        assert_scene_layout(
            scene=scene,
            pending_items=[label, second_label, blocker],
            labels=[label, second_label],
            blockers=[blocker],
            frame_items=[label, second_label, blocker],
        )


def test_empty_runtime_guard_raises() -> None:
    with pytest.raises(LayoutContractError):
        assert_scene_layout(scene=Scene(), pending_items=[], labels=[], blockers=[], frame_items=[])


def test_off_frame_object_raises() -> None:
    outside = Rectangle(width=1.0, height=0.5).shift(RIGHT * 8)
    with pytest.raises(LayoutContractError):
        assert_within_frame([outside])


def test_unacknowledged_geometry_overlap_raises() -> None:
    first = Circle(radius=1.0)
    second = Circle(radius=1.0).shift(RIGHT * 0.5)
    with pytest.raises(LayoutContractError, match="intentional_overlaps"):
        assert_within_frame([first, second])


def test_declared_geometry_overlap_passes() -> None:
    first = Circle(radius=1.0)
    second = Circle(radius=1.0).shift(RIGHT * 0.5)
    assert_within_frame([first, second], intentional_overlaps=[(first, second)])


def test_group_children_cannot_hide_geometry_overlap() -> None:
    group = VGroup(Circle(radius=1.0), Circle(radius=1.0).shift(RIGHT * 0.5))
    with pytest.raises(LayoutContractError):
        assert_within_frame([group])


def test_invalid_overlap_declaration_raises() -> None:
    first = Circle(radius=1.0)
    second = Circle(radius=1.0)
    detached = Circle(radius=0.5)
    with pytest.raises(LayoutContractError, match="distinct guarded"):
        assert_within_frame([first, second], intentional_overlaps=[(first, detached)])


def test_containment_overflow_raises() -> None:
    container = Rectangle(width=2.0, height=1.0)
    child = Circle(radius=1.0)
    with pytest.raises(LayoutContractError):
        assert_inside(container, [child], min_gap=0.05)


def test_circular_container_rejects_bbox_only_false_positive() -> None:
    container = Circle(radius=1.0)
    child = Circle(radius=0.1).shift(RIGHT * 0.75 + UP * 0.75)
    with pytest.raises(LayoutContractError):
        assert_inside(container, [child])


def test_shape_containment_accepts_a_clear_interior_child() -> None:
    assert_inside(Circle(radius=1.0), [Circle(radius=0.2)], min_gap=0.1)


def test_open_path_cannot_claim_a_closed_container() -> None:
    container = VMobject().set_points_as_corners([LEFT + DOWN, RIGHT + DOWN, UP])
    with pytest.raises(LayoutContractError):
        assert_inside(container, [Circle(radius=0.1)])


def test_scene_object_omitted_from_frame_items_raises() -> None:
    scene = Scene()
    outside = Rectangle(width=1.0, height=0.5).shift(RIGHT * 8)
    label = Rectangle(width=1.0, height=0.5).shift(LEFT * 2)
    blocker = Rectangle(width=1.0, height=0.5).shift(RIGHT * 2)
    scene.add(outside)
    with pytest.raises(LayoutContractError, match="omit"):
        assert_scene_layout(
            scene=scene,
            pending_items=[label, blocker],
            labels=[label],
            blockers=[blocker],
            frame_items=[label, blocker],
        )


def test_off_frame_label_omitted_from_guarded_state_raises() -> None:
    scene = Scene()
    label = Rectangle(width=1.0, height=0.5).shift(RIGHT * 8)
    blocker = Rectangle(width=1.0, height=0.5).shift(LEFT * 2)
    with pytest.raises(LayoutContractError, match="absent"):
        assert_scene_layout(
            scene=scene,
            pending_items=[blocker],
            labels=[label],
            blockers=[blocker],
            frame_items=[blocker],
        )


@pytest.mark.parametrize("gap", (-0.01, -1.0))
def test_negative_layout_thresholds_raise(gap: float) -> None:
    first = Rectangle(width=1.0, height=0.5).shift(LEFT * 2)
    second = Rectangle(width=1.0, height=0.5).shift(RIGHT * 2)
    with pytest.raises(LayoutContractError):
        assert_scene_layout(
            scene=Scene(),
            pending_items=[first, second],
            labels=[first],
            blockers=[second],
            frame_items=[first, second],
            min_gap=gap,
        )
    with pytest.raises(LayoutContractError):
        assert_within_frame([first], margin=gap)
    with pytest.raises(LayoutContractError):
        assert_inside(second, [first], min_gap=gap)
