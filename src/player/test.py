from manim import *


class DopplerEffect(Scene):
    def construct(self):
        # Title
        title = Text("Doppler Effect", font_size=48, color=BLUE)
        title.to_edge(UP)
        self.play(Write(title))
        self.wait(0.5)

        # Create source (ambulance) and observer
        source = Rectangle(width=1, height=0.6, fill_color=RED, fill_opacity=1)
        source_label = Text("Source", font_size=20).next_to(source, DOWN, buff=0.1)
        source_group = VGroup(source, source_label)

        observer = Circle(radius=0.3, fill_color=GREEN, fill_opacity=1)
        observer_label = Text("Observer", font_size=20).next_to(
            observer, DOWN, buff=0.1
        )
        observer_group = VGroup(observer, observer_label)

        # Position elements
        source_group.move_to(LEFT * 4)
        observer_group.move_to(RIGHT * 4)

        self.play(FadeIn(source_group), FadeIn(observer_group))
        self.wait(1)

        # Stationary source demonstration
        stationary_text = Text("Stationary Source", font_size=24, color=WHITE)
        stationary_text.to_edge(DOWN)
        self.play(Write(stationary_text))

        # Create wave circles for stationary source
        wave_circles = []
        for i in range(4):
            circle = Circle(radius=0.1, color=YELLOW, stroke_width=3)
            circle.move_to(source.get_center())
            wave_circles.append(circle)

        # Animate concentric waves from stationary source
        for i, circle in enumerate(wave_circles):
            self.play(
                circle.animate.scale(20).set_stroke(opacity=0.3),
                run_time=1.5,
                rate_func=linear,
            )
            if i < len(wave_circles) - 1:
                self.wait(0.3)

        self.wait(1)
        self.play(FadeOut(*wave_circles), FadeOut(stationary_text))

        # Moving source demonstration
        moving_text = Text("Moving Source", font_size=24, color=WHITE)
        moving_text.to_edge(DOWN)
        self.play(Write(moving_text))

        # Create velocity arrow
        velocity_arrow = Arrow(LEFT * 3, LEFT * 2, color=ORANGE, buff=0)
        velocity_label = Text("v", font_size=20, color=ORANGE).next_to(
            velocity_arrow, UP
        )
        self.play(Create(velocity_arrow), Write(velocity_label))

        # Animate moving source with compressed waves
        wave_positions = []
        wave_circles_moving = []

        # Create multiple wave fronts
        for i in range(6):
            circle = Circle(radius=0.1, color=YELLOW, stroke_width=3)
            wave_circles_moving.append(circle)

        # Animate source movement and wave emission
        source_path = Line(LEFT * 4, RIGHT * 1, color=BLUE)

        def create_wave_at_position(pos, delay=0):
            circle = Circle(radius=0.1, color=YELLOW, stroke_width=3)
            circle.move_to(pos)
            return circle

        # Move source and emit waves
        wave_animations = []
        source_start = source_group.get_center()

        for i in range(5):
            # Source position at time of wave emission
            progress = i / 4
            source_pos = source_start + RIGHT * 5 * progress

            # Create wave at current source position
            wave = Circle(radius=0.1, color=YELLOW, stroke_width=3)
            wave.move_to(source_pos)

            # Add wave expansion animation
            wave_animations.append(
                AnimationGroup(
                    wave.animate.scale(25).set_stroke(opacity=0.2),
                    run_time=3,
                    rate_func=linear,
                )
            )

            # Move source
            if i == 0:
                self.play(
                    source_group.animate.move_to(source_pos), Create(wave), run_time=0.3
                )
            else:
                self.play(
                    source_group.animate.move_to(source_pos), Create(wave), run_time=0.6
                )

            # Start wave expansion
            self.add(wave)
            self.play(wave_animations[-1])

        # Show frequency labels
        high_freq = Text("Higher\nFrequency", font_size=18, color=RED)
        high_freq.move_to(RIGHT * 2 + UP * 1.5)

        low_freq = Text("Lower\nFrequency", font_size=18, color=BLUE)
        low_freq.move_to(LEFT * 3 + UP * 1.5)

        # Arrows pointing to compressed and stretched regions
        high_arrow = Arrow(high_freq.get_bottom(), RIGHT * 3, color=RED)
        low_arrow = Arrow(low_freq.get_bottom(), LEFT * 2, color=BLUE)

        self.play(
            Write(high_freq), Write(low_freq), Create(high_arrow), Create(low_arrow)
        )

        self.wait(2)

        # Clean up and show formula
        self.play(FadeOut(*[mob for mob in self.mobjects if mob != title]))

        # Doppler formula
        formula_text = Text("Observed Frequency:", font_size=24)
        formula = MathTex(r"f' = f \frac{v \pm v_o}{v \pm v_s}")

        legend = VGroup(
            Text("f' = observed frequency", font_size=18),
            Text("f = source frequency", font_size=18),
            Text("v = wave speed", font_size=18),
            Text("v₀ = observer speed", font_size=18),
            Text("vₛ = source speed", font_size=18),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2)

        formula_group = VGroup(formula_text, formula, legend)
        formula_group.arrange(DOWN, buff=0.5)
        formula_group.move_to(ORIGIN)

        self.play(Write(formula_text))
        self.play(Write(formula))
        self.play(Write(legend))

        self.wait(3)
