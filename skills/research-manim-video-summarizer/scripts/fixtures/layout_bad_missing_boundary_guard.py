from manim import Circle, Rectangle, Scene


class LayoutBadMissingBoundaryGuard(Scene):
    def construct(self) -> None:
        aquifer = Rectangle(width=5.8, height=1.2)
        support_volume = Circle(radius=1.0)
        self.add(aquifer, support_volume)
