from manim import Axes, Scene, Text


class LayoutBad(Scene):
    def construct(self) -> None:
        axes = Axes(x_range=[0, 10, 2], y_range=[0, 1, 0.2])
        curve = axes.plot(lambda x: 0.1 * x)
        label = Text("Q_m = measured capacity / predicted capacity")
        paragraph = Text(
            "Probability is high enough, therefore the uncertainty is acceptable without drawing a distribution.",
        )
        self.add(axes, curve, label, paragraph)
