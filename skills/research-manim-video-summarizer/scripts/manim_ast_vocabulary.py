from __future__ import annotations

from typing import Final

LABEL_CREATORS: Final = {"Text", "Tex", "MathTex", "DecimalNumber"}
DATA_CREATORS: Final = {
    "Axes",
    "NumberPlane",
    "plot",
    "plot_line_graph",
    "Dot",
    "Line",
    "Arrow",
    "Polygon",
    "Circle",
    "Annulus",
    "Arc",
    "Rectangle",
    "RoundedRectangle",
    "Surface",
    "ParametricFunction",
    "VMobject",
    "ImageMobject",
    "BarChart",
    "NumberLine",
    "DashedLine",
    "BraceBetweenPoints",
}
GROUP_CREATORS: Final = {"Group", "VGroup"}
NONVISUAL_CREATORS: Final = {"ValueTracker", "Camera", "Color"}
LABEL_NAME_TERMS: Final = ("label", "caption", "title", "formula", "equation", "text", "legend")
DATA_NAME_TERMS: Final = ("axes", "axis", "curve", "line", "band", "field", "map", "cloud", "point", "surface")
CONTAINER_NAME_TERMS: Final = ("container", "boundary", "aquifer", "specimen", "domain")
CHILD_NAME_TERMS: Final = ("halo", "ring", "support_volume", "interval", "inner_band")
PLACEMENT_CALLS: Final = {
    "next_to",
    "arrange",
    "align_to",
    "to_edge",
    "to_corner",
    "move_to",
    "place_caption",
    "place_formula_lane",
    "margin_label",
    "fit_to_width",
    "place_label_clear",
    "shift",
    "scale",
    "stretch",
    "rotate",
    "set_width",
    "set_height",
    "put_start_and_end_on",
    "match_width",
    "match_height",
    "stretch_to_fit_width",
    "stretch_to_fit_height",
    "center",
    "become",
}
TRACEABLE_DERIVATION_CALLS: Final = PLACEMENT_CALLS | {
    "copy",
    "set_color",
    "set_fill",
    "set_opacity",
    "set_stroke",
    "set_z_index",
}
GEOMETRY_ACCESSORS: Final = {"get_center", "get_left", "get_right", "get_top", "get_bottom"}
KNOWN_ASSIGNMENT_CALLS: Final = LABEL_CREATORS | DATA_CREATORS | GROUP_CREATORS | NONVISUAL_CREATORS | TRACEABLE_DERIVATION_CALLS | GEOMETRY_ACCESSORS
VISIBLE_ADD_CALLS: Final = {
    "add",
    "play",
    "add_fixed_in_frame_mobjects",
    "add_fixed_orientation_mobjects",
    "add_foreground_mobject",
    "add_foreground_mobjects",
}
VISIBLE_REMOVE_CALLS: Final = {
    "remove",
    "remove_fixed_in_frame_mobjects",
    "remove_fixed_orientation_mobjects",
    "remove_foreground_mobjects",
}
RENDER_CALLS: Final = VISIBLE_ADD_CALLS | VISIBLE_REMOVE_CALLS | {"clear"}
