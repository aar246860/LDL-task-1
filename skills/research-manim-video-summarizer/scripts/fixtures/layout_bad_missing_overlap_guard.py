from manim import UP, Axes, MathTex, Scene


class LayoutBadMissingOverlapGuard(Scene):
    def construct(self) -> None:
        axes = Axes(x_range=[0, 5, 1], y_range=[0, 1, 0.2])
        curve = axes.plot(lambda x: 0.2 * x)
        label = MathTex(r"\text{drawdown curve}").next_to(axes, UP, buff=0.05)
        self.add(axes, curve, label)
