from manim import Circle, Rectangle, Scene

from assets.research_manim_layout import assert_inside, assert_within_frame


class LayoutGoodBoundaryGuard(Scene):
    def construct(self) -> None:
        aquifer = Rectangle(width=5.8, height=1.2)
        support_volume = Circle(radius=0.4)
        assert_inside(aquifer, [support_volume], min_gap=0.05)
        assert_within_frame(
            [aquifer, support_volume],
            scene=self,
            pending_items=[aquifer, support_volume],
            intentional_overlaps=[(aquifer, support_volume)],
        )
        self.add(aquifer, support_volume)
