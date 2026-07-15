from __future__ import annotations

from math import hypot

from manim import Mobject, VMobject

Point2D = tuple[float, float]


def _sample_boundary(item: VMobject, count: int) -> list[Point2D]:
    return [(float(point[0]), float(point[1])) for point in (item.point_from_proportion(index / count) for index in range(count))]


def _segment_distance(point: Point2D, start: Point2D, end: Point2D) -> float:
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    length_squared = dx * dx + dy * dy
    if length_squared == 0:
        return hypot(point[0] - start[0], point[1] - start[1])
    fraction = max(0.0, min(1.0, ((point[0] - start[0]) * dx + (point[1] - start[1]) * dy) / length_squared))
    closest = (start[0] + fraction * dx, start[1] + fraction * dy)
    return hypot(point[0] - closest[0], point[1] - closest[1])


def _inside_polygon(point: Point2D, polygon: list[Point2D]) -> bool:
    inside = False
    previous = polygon[-1]
    for current in polygon:
        crosses = (current[1] > point[1]) != (previous[1] > point[1])
        if crosses:
            x_crossing = (previous[0] - current[0]) * (point[1] - current[1]) / (previous[1] - current[1]) + current[0]
            if point[0] < x_crossing:
                inside = not inside
        previous = current
    return inside


def shape_contains(container: Mobject, item: Mobject, min_gap: float) -> bool:
    if not isinstance(container, VMobject) or not container.has_points() or len(container.get_subpaths()) != 1:
        return False
    start = container.get_start()
    end = container.get_end()
    closure_tolerance = max(float(container.width), float(container.height), 1.0) * 1e-6
    if hypot(float(start[0] - end[0]), float(start[1] - end[1])) > closure_tolerance:
        return False
    polygon = _sample_boundary(container, 128)
    segments = list(zip(polygon, [*polygon[1:], polygon[0]], strict=True))
    item_parts = [member for member in item.get_family() if isinstance(member, VMobject) and member.has_points()]
    if not item_parts:
        return False
    for part in item_parts:
        for point in _sample_boundary(part, 48):
            boundary_distance = min(_segment_distance(point, start, end) for start, end in segments)
            if boundary_distance + 1e-7 < min_gap:
                return False
            if not _inside_polygon(point, polygon) and boundary_distance > 1e-7:
                return False
    return True
