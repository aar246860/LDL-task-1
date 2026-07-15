from manim import RIGHT, UP, Axes, MathTex, Scene, VGroup

from assets.research_manim_layout import assert_scene_layout, fit_to_width, place_caption


class LayoutGood(Scene):
    def construct(self) -> None:
        axes = Axes(x_range=[0, 10, 2], y_range=[0, 1, 0.2])
        curve = axes.plot(lambda x: 0.1 * x, color="#62c6ff")
        label = MathTex(r"Q_m").next_to(curve, RIGHT)
        equation = VGroup(
            MathTex(r"R"),
            MathTex(r"="),
            MathTex(r"\frac{Q_m}{Q_p}"),
        ).arrange(RIGHT, buff=0.18).to_edge(UP)
        caption = fit_to_width(MathTex(r"\mathrm{uncertainty\ becomes\ width}"), 8.5)
        place_caption(caption)
        assert_scene_layout(
            scene=self,
            pending_items=[axes, curve, label, equation, caption],
            labels=[label, equation, caption],
            blockers=[axes, curve],
            frame_items=[axes, curve, label, equation, caption],
        )
        self.add(axes, curve, label, equation, caption)
