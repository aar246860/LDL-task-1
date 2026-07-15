from manim import (
    BLUE, DOWN, GREEN, LEFT, RED, TEAL, UP, YELLOW,
    Axes, BraceBetweenPoints, Create, Dot, FadeIn, FadeOut, GrowFromCenter, Line,
    MathTex, Polygon, Rectangle, Scene, Text, Transform, VGroup,
)

from assets.research_manim_layout import assert_scene_layout, assert_within_frame


class StoryboardMappedScene(Scene):
    def construct(self) -> None:
        self.scene_01_b01_hook()
        self.scene_02_b02_context()
        self.scene_03_b03_tension()
        self.scene_04_m01_select()
        self.scene_05_m02_align()
        self.scene_06_m03_form()
        self.scene_07_m04_aggregate()
        self.scene_08_m05_compare()
        self.scene_09_m06_calibrate()
        self.scene_10_return()

    def scene_01_b01_hook(self) -> None:
        piles = VGroup(
            Rectangle(width=0.45, height=3.0).shift(LEFT * 2.4 + DOWN * 0.5),
            Rectangle(width=0.45, height=3.0).shift(LEFT * 1.7 + DOWN * 0.5),
        ).set_color(TEAL)
        assert_within_frame([piles], scene=self, pending_items=[piles])
        self.play(Create(piles), run_time=0.4)
        self.wait(0.4)
        responses = VGroup(
            Line((-1.2, -1.4, 0), (2.2, 0.5, 0), color=BLUE),
            Line((-1.2, -1.4, 0), (2.2, 1.4, 0), color=YELLOW),
        )
        assert_within_frame(
            [piles, responses], scene=self, pending_items=[responses],
            intentional_overlaps=[(responses[0], responses[1])],
        )
        self.play(Create(responses), run_time=0.4)
        self.wait(0.4)
        caption = Text("same design, different response", font_size=28).to_edge(UP, buff=0.4)
        assert_scene_layout(
            scene=self, pending_items=[caption], labels=[caption], blockers=[piles, responses],
            frame_items=[piles, responses, caption],
            intentional_overlaps=[(responses[0], responses[1])],
        )
        self.play(FadeIn(caption), run_time=0.4)
        self.wait(0.4)
        self.play(FadeOut(piles), FadeOut(responses), FadeOut(caption), run_time=0.2)

    def scene_02_b02_context(self) -> None:
        axes = Axes(x_range=[0, 5], y_range=[0, 5], x_length=6.0, y_length=3.5).shift(DOWN * 0.6)
        assert_within_frame([axes], scene=self, pending_items=[axes])
        self.play(Create(axes), run_time=0.4)
        self.wait(0.4)
        cloud = VGroup(Dot((-2.0, -1.0, 0), color=TEAL), Dot((-0.8, -0.2, 0), color=TEAL), Dot((0.5, 0.1, 0), color=TEAL), Dot((1.8, 1.0, 0), color=TEAL))
        assert_within_frame([axes, cloud], scene=self, pending_items=[cloud], intentional_overlaps=[(axes, cloud)])
        self.play(FadeIn(cloud), run_time=0.4)
        self.wait(0.4)
        caption = Text("tests become comparable points", font_size=28).to_edge(UP, buff=0.4)
        assert_scene_layout(
            scene=self, pending_items=[caption], labels=[caption], blockers=[axes, cloud],
            frame_items=[axes, cloud, caption], intentional_overlaps=[(axes, cloud)],
        )
        self.play(FadeIn(caption), run_time=0.4)
        self.wait(0.4)
        self.play(FadeOut(axes), FadeOut(cloud), FadeOut(caption), run_time=0.2)

    def scene_03_b03_tension(self) -> None:
        axes = Axes(x_range=[0, 5], y_range=[0, 5], x_length=6.0, y_length=3.5).shift(DOWN * 0.6)
        cloud = VGroup(Dot((-1.8, -0.8, 0), color=TEAL), Dot((-0.8, -0.2, 0), color=TEAL), Dot((0.5, 0.2, 0), color=TEAL), Dot((1.7, 0.9, 0), color=TEAL))
        field = VGroup(axes, cloud)
        assert_within_frame([field], scene=self, pending_items=[field], intentional_overlaps=[(axes, cloud)])
        self.play(FadeIn(field), run_time=0.4)
        self.wait(0.4)
        benchmark = Line((-2.4, -1.6, 0), (2.4, 1.6, 0), color=YELLOW)
        assert_within_frame(
            [field, benchmark], scene=self, pending_items=[benchmark],
            intentional_overlaps=[(axes, cloud), (field, benchmark)],
        )
        self.play(Create(benchmark), run_time=0.4)
        self.wait(0.4)
        zones = VGroup(
            Polygon((-3.0, -1.9, 0), (2.4, 1.6, 0), (3.0, 1.9, 0), (-3.0, 1.9, 0), color=BLUE, fill_opacity=0.12),
            Polygon((-3.0, -1.9, 0), (2.4, 1.6, 0), (3.0, -1.9, 0), color=RED, fill_opacity=0.12),
        )
        assert_within_frame(
            [field, benchmark, zones], scene=self, pending_items=[zones],
            intentional_overlaps=[
                (field, benchmark), (field, zones), (benchmark, zones),
                (axes, cloud), (zones[0], zones[1]),
            ],
        )
        self.play(FadeIn(zones), run_time=0.4)
        self.wait(0.4)
        self.play(FadeOut(field), FadeOut(benchmark), FadeOut(zones), run_time=0.2)

    def scene_04_m01_select(self) -> None:
        curve = VGroup(
            Line((-2.5, -1.4, 0), (-0.4, 0.7, 0), color=TEAL),
            Line((-0.4, 0.7, 0), (2.2, -0.3, 0), color=TEAL),
        )
        assert_within_frame([curve], scene=self, pending_items=[curve])
        self.play(Create(curve), run_time=0.4)
        self.wait(0.4)
        peak = Dot((-0.4, 0.7, 0), radius=0.12, color=YELLOW)
        assert_within_frame([curve, peak], scene=self, pending_items=[peak], intentional_overlaps=[(curve, peak)])
        self.play(GrowFromCenter(peak), run_time=0.4)
        self.wait(0.4)
        label = MathTex(r"Q_m\text{ names the measured peak}").to_edge(UP, buff=0.4)
        assert_scene_layout(
            scene=self, pending_items=[label], labels=[label], blockers=[curve, peak],
            frame_items=[curve, peak, label], intentional_overlaps=[(curve, peak)],
        )
        self.play(FadeIn(label), run_time=0.4)
        self.wait(0.4)
        self.play(FadeOut(curve), FadeOut(peak), FadeOut(label), run_time=0.2)

    def scene_05_m02_align(self) -> None:
        measured_curve = VGroup(Line((-2.5, -1.4, 0), (-0.5, 0.7, 0)), Line((-0.5, 0.7, 0), (2.2, -0.2, 0))).set_color(TEAL)
        measured_peak = Dot((-0.5, 0.7, 0), radius=0.12, color=TEAL)
        measured_label = MathTex("Q_m").move_to((-2.1, 1.5, 0)).set_color(TEAL)
        assert_scene_layout(
            scene=self, pending_items=[measured_curve, measured_peak, measured_label], labels=[measured_label],
            blockers=[measured_curve, measured_peak], frame_items=[measured_curve, measured_peak, measured_label],
            intentional_overlaps=[(measured_curve, measured_peak)],
        )
        self.play(Create(measured_curve), GrowFromCenter(measured_peak), FadeIn(measured_label), run_time=0.4)
        self.wait(0.4)
        predicted = VGroup(
            Line((-2.5, -1.4, 0), (0.5, 1.0, 0), color=YELLOW),
            Line((0.5, 1.0, 0), (2.2, 0.0, 0), color=YELLOW),
            Dot((0.5, 1.0, 0), radius=0.12, color=YELLOW),
        )
        assert_scene_layout(
            scene=self, pending_items=[predicted], labels=[measured_label], blockers=[measured_curve, measured_peak, predicted],
            frame_items=[measured_curve, measured_peak, measured_label, predicted],
            intentional_overlaps=[
                (measured_curve, measured_peak), (measured_curve, predicted),
                (measured_peak, predicted), (predicted[0], predicted[2]),
                (predicted[1], predicted[2]),
            ],
        )
        self.play(Create(predicted), run_time=0.4)
        self.wait(0.4)
        label = MathTex(r"Q_p\text{ names the comparable peak}").to_edge(UP, buff=0.4)
        assert_scene_layout(
            scene=self, pending_items=[label], labels=[measured_label, label], blockers=[measured_curve, measured_peak, predicted],
            frame_items=[measured_curve, measured_peak, measured_label, predicted, label],
            intentional_overlaps=[
                (measured_curve, measured_peak), (measured_curve, predicted),
                (measured_peak, predicted), (predicted[0], predicted[2]),
                (predicted[1], predicted[2]),
            ],
        )
        self.play(FadeIn(label), run_time=0.4)
        self.wait(0.4)
        self.play(FadeOut(measured_curve), FadeOut(measured_peak), FadeOut(measured_label), FadeOut(predicted), FadeOut(label), run_time=0.2)

    def scene_06_m03_form(self) -> None:
        measured_point = Dot((-1.8, -0.7, 0), radius=0.15, color=TEAL)
        measured_label = MathTex("Q_m").move_to((-2.5, -0.7, 0))
        predicted_point = Dot((1.8, 0.7, 0), radius=0.15, color=YELLOW)
        predicted_label = MathTex("Q_p").move_to((2.5, 0.7, 0))
        point_items = [measured_point, measured_label, predicted_point, predicted_label]
        brace = BraceBetweenPoints(measured_point.get_center(), predicted_point.get_center(), color=BLUE)
        assert_scene_layout(
            scene=self, pending_items=[*point_items, brace], labels=[measured_label, predicted_label], blockers=[measured_point, predicted_point, brace],
            frame_items=[*point_items, brace], intentional_overlaps=[(measured_point, brace), (predicted_point, brace)],
        )
        self.play(FadeIn(measured_point), FadeIn(measured_label), FadeIn(predicted_point), FadeIn(predicted_label), Create(brace), run_time=0.4)
        self.wait(0.4)
        fraction = MathTex(r"\frac{Q_m}{Q_p}").to_edge(UP, buff=0.4)
        assert_scene_layout(
            scene=self, pending_items=[fraction], labels=[measured_label, predicted_label, fraction], blockers=[measured_point, predicted_point, brace],
            frame_items=[*point_items, brace, fraction], intentional_overlaps=[(measured_point, brace), (predicted_point, brace)],
        )
        self.play(FadeIn(fraction), run_time=0.4)
        self.wait(0.4)
        prefix = VGroup(MathTex("R"), MathTex("=")).arrange().next_to(fraction, LEFT)
        assert_scene_layout(
            scene=self, pending_items=[prefix], labels=[measured_label, predicted_label, fraction, prefix], blockers=[measured_point, predicted_point, brace],
            frame_items=[*point_items, brace, fraction, prefix], intentional_overlaps=[(measured_point, brace), (predicted_point, brace)],
        )
        self.play(FadeIn(prefix), run_time=0.4)
        self.wait(0.4)
        self.play(FadeOut(measured_point), FadeOut(measured_label), FadeOut(predicted_point), FadeOut(predicted_label), FadeOut(brace), FadeOut(fraction), FadeOut(prefix), run_time=0.2)

    def scene_07_m04_aggregate(self) -> None:
        axis = Line((-2.8, -1.3, 0), (2.8, -1.3, 0))
        dots = VGroup(Dot((-2.2, -1.0, 0)), Dot((-1.0, -0.7, 0)), Dot((0.0, -0.9, 0)), Dot((1.1, -0.6, 0)), Dot((2.0, -1.0, 0))).set_color(TEAL)
        samples = VGroup(axis, dots)
        assert_within_frame([samples], scene=self, pending_items=[samples])
        self.play(FadeIn(samples), run_time=0.4)
        self.wait(0.4)
        density = VGroup(Line((-2.2, 0.1, 0), (0.0, 1.3, 0)), Line((0.0, 1.3, 0), (2.2, 0.1, 0))).set_color(BLUE)
        interval = Rectangle(width=3.8, height=0.35, color=TEAL, fill_opacity=0.25).shift(UP * 0.25)
        distribution = VGroup(density, interval)
        assert_within_frame(
            [samples, distribution], scene=self, pending_items=[distribution],
            intentional_overlaps=[(axis, dots), (density, interval)],
        )
        self.play(Create(density), FadeIn(interval), run_time=0.4)
        self.wait(0.4)
        caption = Text("ratios become a distribution", font_size=28).to_edge(UP, buff=0.4)
        assert_scene_layout(
            scene=self, pending_items=[caption], labels=[caption], blockers=[samples, distribution],
            frame_items=[samples, distribution, caption],
            intentional_overlaps=[(axis, dots), (density, interval)],
        )
        self.play(FadeIn(caption), run_time=0.4)
        self.wait(0.4)
        self.play(FadeOut(samples), FadeOut(distribution), FadeOut(caption), run_time=0.2)

    def scene_08_m05_compare(self) -> None:
        lanes = VGroup(
            VGroup(Line((-2.8, 0.2, 0), (-0.8, 1.8, 0)), Line((-0.8, 1.8, 0), (1.2, 0.2, 0))).set_color(BLUE),
            VGroup(Line((-1.2, -1.8, 0), (0.8, -0.2, 0)), Line((0.8, -0.2, 0), (2.8, -1.8, 0))).set_color(YELLOW),
        )
        assert_within_frame([lanes], scene=self, pending_items=[lanes])
        self.play(Create(lanes), run_time=0.4)
        self.wait(0.4)
        aligned = VGroup(
            Line((-3.2, -1.25, 0), (3.2, -1.25, 0)),
            VGroup(Line((-2.8, -1.2, 0), (-0.8, 1.0, 0)), Line((-0.8, 1.0, 0), (1.2, -1.2, 0))).set_color(BLUE),
            VGroup(Line((-1.2, -1.2, 0), (0.8, 0.8, 0)), Line((0.8, 0.8, 0), (2.8, -1.2, 0))).set_color(YELLOW),
        )
        assert_within_frame(
            [lanes, aligned], scene=self, pending_items=[aligned],
            intentional_overlaps=[
                (lanes, aligned), (aligned[0], aligned[1]),
                (aligned[0], aligned[2]), (aligned[1], aligned[2]),
                (aligned[1][0], aligned[1][1]), (aligned[2][0], aligned[2][1]),
            ],
        )
        self.play(Transform(lanes, aligned), run_time=0.4)
        self.wait(0.4)
        overlap = Polygon((-1.2, -1.2, 0), (-0.1, 0.0, 0), (0.8, 0.8, 0), (1.2, -1.2, 0), color=GREEN, fill_opacity=0.3)
        assert_within_frame(
            [lanes, overlap], scene=self, pending_items=[overlap],
            intentional_overlaps=[
                (lanes, overlap), (lanes, lanes),
            ],
        )
        self.play(FadeIn(overlap), run_time=0.4)
        self.wait(0.4)
        self.play(FadeOut(lanes), FadeOut(overlap), run_time=0.2)

    def scene_09_m06_calibrate(self) -> None:
        axis = Line((-3.2, -0.95, 0), (3.2, -0.95, 0))
        interval = Rectangle(width=5.0, height=0.9, color=RED, fill_opacity=0.22).shift(DOWN * 0.5)
        assert_within_frame([axis, interval], scene=self, pending_items=[axis, interval])
        self.play(Create(axis), Create(interval), run_time=0.4)
        self.wait(0.4)
        target = Rectangle(width=3.0, height=0.5, color=GREEN, fill_opacity=0.22).move_to(interval)
        assert_within_frame([axis, interval, target], scene=self, pending_items=[target], intentional_overlaps=[(interval, target)])
        self.play(Transform(interval, target), run_time=0.4)
        self.wait(0.4)
        caption = Text("calibration narrows the interval", font_size=28).to_edge(UP, buff=0.4)
        assert_scene_layout(scene=self, pending_items=[caption], labels=[caption], blockers=[axis, interval], frame_items=[axis, interval, caption])
        self.play(FadeIn(caption), run_time=0.4)
        self.wait(0.4)
        self.play(FadeOut(axis), FadeOut(interval), FadeOut(caption), run_time=0.2)

    def scene_10_return(self) -> None:
        pile = Rectangle(width=0.6, height=3.2, color=TEAL).shift(LEFT * 2 + DOWN * 0.5)
        assert_within_frame([pile], scene=self, pending_items=[pile])
        self.play(Create(pile), run_time=0.4)
        self.wait(0.4)
        interval = VGroup(Line((0.3, -0.4, 0), (2.8, -0.4, 0), color=GREEN), Dot((0.3, -0.4, 0)), Dot((2.8, -0.4, 0)))
        link = Line(pile.get_right(), interval.get_left(), color=BLUE)
        result = VGroup(interval, link)
        assert_within_frame(
            [pile, result], scene=self, pending_items=[result],
            intentional_overlaps=[(result, result)],
        )
        self.play(Create(result), run_time=0.4)
        self.wait(0.4)
        caption = Text("capacity returns to the physical pile", font_size=28).to_edge(UP, buff=0.4)
        assert_scene_layout(
            scene=self, pending_items=[caption], labels=[caption], blockers=[pile, result],
            frame_items=[pile, result, caption], intentional_overlaps=[(result, result)],
        )
        self.play(FadeIn(caption), run_time=0.4)
        self.wait(0.6)
