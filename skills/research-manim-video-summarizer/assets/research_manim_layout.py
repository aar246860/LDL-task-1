from __future__ import annotations

from collections.abc import Sequence
from typing import Final

from manim import DOWN, LEFT, RIGHT, UP, Mobject, Rectangle, Scene, VGroup, VMobject

from assets.research_manim_geometry import shape_contains

FRAME_WIDTH: Final = 14.222
FRAME_HEIGHT: Final = 8.0
DEFAULT_MARGIN: Final = 0.45
CAPTION_BAND_HEIGHT: Final = 1.1


class LayoutContractError(RuntimeError):
    pass


def _require_nonempty(items: Sequence[Mobject], name: str) -> None:
    if not items:
        raise LayoutContractError(f"layout contract risk: {name} cannot be empty")


def _require_nonnegative(value: float, name: str) -> None:
    if value < 0:
        raise LayoutContractError(f"layout contract risk: {name} cannot be negative")


def _family_ids(items: Sequence[Mobject]) -> set[int]:
    return {id(member) for item in items for member in item.get_family() if member.has_points()}


def _family_object_ids(items: Sequence[Mobject]) -> set[int]:
    return {id(member) for item in items for member in item.get_family()}


def _require_scene_coverage(
    scene: Scene,
    pending_items: Sequence[Mobject],
    frame_items: Sequence[Mobject],
) -> None:
    expected = [*scene.mobjects, *pending_items]
    _require_nonempty(expected, "scene and pending items")
    if not _family_ids(expected).issubset(_family_ids(frame_items)):
        raise LayoutContractError("layout contract risk: frame items omit a scene or pending mobject")


def _require_role_coverage(
    scene: Scene,
    pending_items: Sequence[Mobject],
    frame_items: Sequence[Mobject],
    role_items: Sequence[Mobject],
) -> None:
    role_ids = _family_ids(role_items)
    expected_ids = _family_ids([*scene.mobjects, *pending_items])
    if not role_ids.issubset(expected_ids) or not role_ids.issubset(_family_ids(frame_items)):
        raise LayoutContractError("layout contract risk: a label or blocker is absent from the guarded state")


def fit_to_width(mobject: Mobject, max_width: float) -> Mobject:
    if mobject.width > max_width:
        _ = mobject.scale(max_width / mobject.width)
    return mobject


def caption_band(*, top: bool = False) -> Rectangle:
    band = Rectangle(
        width=FRAME_WIDTH - 2 * DEFAULT_MARGIN,
        height=CAPTION_BAND_HEIGHT,
        stroke_opacity=0,
        fill_opacity=0,
    )
    _ = band.to_edge(UP if top else DOWN, buff=DEFAULT_MARGIN)
    return band


def place_caption(caption: Mobject, *, top: bool = False, max_width: float = 12.2) -> Mobject:
    fit_to_width(caption, max_width)
    _ = caption.move_to(caption_band(top=top).get_center())
    return caption


def place_formula_lane(formula: Mobject, *, top: bool = True, max_width: float = 10.8) -> Mobject:
    fit_to_width(formula, max_width)
    _ = formula.to_edge(UP if top else DOWN, buff=DEFAULT_MARGIN)
    return formula


def margin_label(label: Mobject, target: Mobject, *, side: str = "right", buff: float = 0.2) -> Mobject:
    direction = RIGHT if side == "right" else LEFT
    _ = label.next_to(target, direction, buff=buff)
    _ = label.shift(UP * 0.05)
    return label


def arrange_equation_terms(*terms: VMobject, buff: float = 0.18) -> VGroup:
    group = VGroup(*terms)
    _ = group.arrange(RIGHT, buff=buff)
    return group


def bbox_gap(first: Mobject, second: Mobject) -> float:
    horizontal_gap = max(
        float(second.get_left()[0]) - float(first.get_right()[0]),
        float(first.get_left()[0]) - float(second.get_right()[0]),
    )
    vertical_gap = max(
        float(second.get_bottom()[1]) - float(first.get_top()[1]),
        float(first.get_bottom()[1]) - float(second.get_top()[1]),
    )
    return float(max(horizontal_gap, vertical_gap))


def _overlap_leaves(items: Sequence[Mobject]) -> list[Mobject]:
    leaves: list[Mobject] = []
    for item in items:
        if item.__class__.__name__ in {"Group", "VGroup"} and item.submobjects:
            leaves.extend(_overlap_leaves(item.submobjects))
        else:
            leaves.append(item)
    return leaves


def assert_no_overlap(labels: Sequence[Mobject], blockers: Sequence[Mobject], *, min_gap: float = 0.08) -> None:
    _require_nonnegative(min_gap, "minimum overlap gap")
    _require_nonempty(labels, "labels")
    _require_nonempty(blockers, "blockers")
    for label in _overlap_leaves(labels):
        for blocker in _overlap_leaves(blockers):
            if bbox_gap(label, blocker) < min_gap:
                message = f"layout overlap risk: label {label.__class__.__name__} is too close to {blocker.__class__.__name__}"
                raise LayoutContractError(message)


def assert_mutually_clear(items: Sequence[Mobject], *, min_gap: float = 0.08) -> None:
    _require_nonnegative(min_gap, "minimum mutual gap")
    _require_nonempty(items, "items")
    leaves = _overlap_leaves(items)
    for index, first in enumerate(leaves):
        for second in leaves[index + 1 :]:
            if bbox_gap(first, second) < min_gap:
                message = f"layout overlap risk: {first.__class__.__name__} is too close to {second.__class__.__name__}"
                raise LayoutContractError(message)


def assert_no_unintended_overlap(
    items: Sequence[Mobject],
    *,
    intentional_overlaps: Sequence[tuple[Mobject, Mobject]] = (),
    min_gap: float = 0.0,
) -> None:
    _require_nonnegative(min_gap, "minimum geometry gap")
    _require_nonempty(items, "geometry items")
    leaves = _overlap_leaves(items)
    item_ids = {id(item) for item in items} | _family_object_ids(items)
    allowed: set[frozenset[int]] = set()
    for first, second in intentional_overlaps:
        first_leaves = _overlap_leaves([first])
        second_leaves = _overlap_leaves([second])
        if first is second:
            if first.__class__.__name__ not in {"Group", "VGroup"} or id(first) not in item_ids or not first_leaves:
                raise LayoutContractError("layout contract risk: intentional overlap pair is not a distinct guarded item pair")
            allowed.update(frozenset((id(left), id(right))) for index, left in enumerate(first_leaves) for right in first_leaves[index + 1 :])
            continue
        if id(first) not in item_ids or id(second) not in item_ids or not first_leaves or not second_leaves:
            raise LayoutContractError("layout contract risk: intentional overlap pair is not a distinct guarded item pair")
        allowed.update(frozenset((id(left), id(right))) for left in first_leaves for right in second_leaves)
    for index, first in enumerate(leaves):
        for second in leaves[index + 1 :]:
            pair = frozenset((id(first), id(second)))
            if bbox_gap(first, second) < min_gap and pair not in allowed:
                raise LayoutContractError(
                    "layout overlap risk: geometry overlaps without an intentional_overlaps "
                    f"declaration ({first.__class__.__name__} vs {second.__class__.__name__})",
                )


def assert_within_frame(
    items: Sequence[Mobject],
    *,
    margin: float = 0.12,
    scene: Scene | None = None,
    pending_items: Sequence[Mobject] = (),
    intentional_overlaps: Sequence[tuple[Mobject, Mobject]] = (),
    geometry_min_gap: float = 0.0,
) -> None:
    _require_nonempty(items, "frame items")
    _require_nonnegative(margin, "frame margin")
    if margin >= min(FRAME_WIDTH, FRAME_HEIGHT) / 2:
        raise LayoutContractError("layout contract risk: frame margin consumes the visible frame")
    if scene is not None:
        _require_scene_coverage(scene, pending_items, items)
    assert_no_unintended_overlap(
        items,
        intentional_overlaps=intentional_overlaps,
        min_gap=geometry_min_gap,
    )
    left = -FRAME_WIDTH / 2 + margin
    right = FRAME_WIDTH / 2 - margin
    bottom = -FRAME_HEIGHT / 2 + margin
    top = FRAME_HEIGHT / 2 - margin
    for item in _overlap_leaves(items):
        outside_bounds = item.get_left()[0] < left or item.get_right()[0] > right or item.get_bottom()[1] < bottom or item.get_top()[1] > top
        if outside_bounds:
            message = f"layout frame risk: {item.__class__.__name__} extends outside the safe frame"
            raise LayoutContractError(message)


def assert_inside(container: Mobject, items: Sequence[Mobject], *, min_gap: float = 0.0) -> None:
    _require_nonempty(items, "contained items")
    _require_nonnegative(min_gap, "containment gap")
    left = float(container.get_left()[0]) + min_gap
    right = float(container.get_right()[0]) - min_gap
    bottom = float(container.get_bottom()[1]) + min_gap
    top = float(container.get_top()[1]) - min_gap
    for item in items:
        outside = item.get_left()[0] < left or item.get_right()[0] > right or item.get_bottom()[1] < bottom or item.get_top()[1] > top
        if outside or not shape_contains(container, item, min_gap):
            message = f"layout boundary risk: {item.__class__.__name__} extends outside {container.__class__.__name__}"
            raise LayoutContractError(message)


def assert_scene_layout(
    *,
    scene: Scene,
    pending_items: Sequence[Mobject],
    labels: Sequence[Mobject],
    blockers: Sequence[Mobject],
    frame_items: Sequence[Mobject],
    min_gap: float = 0.08,
    frame_margin: float = 0.12,
    intentional_overlaps: Sequence[tuple[Mobject, Mobject]] = (),
) -> None:
    _require_nonempty(labels, "labels")
    _require_nonempty(blockers, "blockers")
    _require_scene_coverage(scene, pending_items, frame_items)
    _require_role_coverage(scene, pending_items, frame_items, [*labels, *blockers])
    assert_mutually_clear(labels, min_gap=min_gap)
    assert_no_overlap(labels, blockers, min_gap=min_gap)
    assert_within_frame(
        frame_items,
        margin=frame_margin,
        intentional_overlaps=intentional_overlaps,
    )


def place_label_clear(label: Mobject, target: Mobject, blockers: Sequence[Mobject]) -> Mobject:
    for direction in (UP, DOWN, RIGHT, LEFT):
        _ = label.next_to(target, direction, buff=0.16)
        if all(bbox_gap(label, blocker) >= 0.08 for blocker in blockers):
            return label
    raise LayoutContractError("layout overlap risk: no clear label placement found")
