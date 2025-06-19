from manim import *


class DopplerEffect(Scene):
    def construct(self):
        # Title
        title = Text("Doppler Effect", font_size=48, color=BLUE)
        title.to_edge(UP)
        self.play(Write(title))
        self.wait(0.5)

        # Create source (ambulance/siren)
        source = Circle(radius=0.3, color=RED, fill_opacity=0.8)
        source_label = Text("Source", font_size=20, color=WHITE)
        source_label.move_to(source.get_center())
        source_group = VGroup(source, source_label)
        source_group.move_to(LEFT * 4)

        # Create observer
        observer = Square(side_length=0.6, color=GREEN, fill_opacity=0.8)
        observer_label = Text("Observer", font_size=16, color=WHITE)
        observer_label.move_to(observer.get_center())
        observer_group = VGroup(observer, observer_label)
        observer_group.move_to(RIGHT * 4)

        self.play(Create(source_group), Create(observer_group))
        self.wait(0.5)

        # Stationary case
        stationary_text = Text("Stationary Source", font_size=24, color=YELLOW)
        stationary_text.move_to(DOWN * 2.5)
        self.play(Write(stationary_text))

        # Generate concentric wave circles (stationary)
        waves = []
        for i in range(5):
            wave = Circle(radius=0.5, color=BLUE, stroke_width=2)
            wave.move_to(source.get_center())
            waves.append(wave)

        # Animate stationary waves
        animations = []
        for i, wave in enumerate(waves):
            animations.append(
                wave.animate.scale(6).set_stroke(opacity=0.3).set_stroke_width(1)
            )

        self.play(*animations, run_time=3)
        self.wait(0.5)

        # Clear waves
        self.play(*[FadeOut(wave) for wave in waves])
        self.play(FadeOut(stationary_text))

        # Moving source case
        moving_text = Text("Moving Source", font_size=24, color=YELLOW)
        moving_text.move_to(DOWN * 2.5)
        self.play(Write(moving_text))

        # Reset source position
        source_group.move_to(LEFT * 4)

        # Arrow showing direction
        arrow = Arrow(LEFT * 2, RIGHT * 2, color=ORANGE, stroke_width=6)
        arrow.move_to(DOWN * 1.5)
        self.play(Create(arrow))

        # Moving source with compressed waves
        def create_moving_waves():
            # Move source while creating waves
            source_positions = []
            wave_groups = []

            # Create multiple wave positions
            for t in range(8):
                pos_x = -4 + t * 0.8  # Source moves right
                source_pos = np.array([pos_x, 0, 0])
                source_positions.append(source_pos)

                # Create waves from this position
                wave_set = []
                for r in range(1, 4):
                    wave = Circle(
                        radius=r * 0.8, color=BLUE, stroke_width=2, stroke_opacity=0.7
                    )
                    wave.move_to(source_pos)
                    wave_set.append(wave)
                wave_groups.append(wave_set)

            return source_positions, wave_groups

        # Animate moving source with waves
        source_positions, wave_groups = create_moving_waves()

        # Show compressed waves (higher frequency) on the right
        # and stretched waves (lower frequency) on the left
        all_waves = []
        for i, (pos, waves) in enumerate(zip(source_positions, wave_groups)):
            for j, wave in enumerate(waves):
                # Waves in front are compressed
                if wave.get_center()[0] > pos[0]:
                    scale_factor = 3 + j * 0.8
                else:  # Waves behind are stretched
                    scale_factor = 4 + j * 1.2

                all_waves.append(
                    wave.animate.scale(scale_factor).set_stroke(opacity=0.3)
                )

        # Move source across screen
        self.play(source_group.animate.move_to(RIGHT * 2), *all_waves, run_time=4)

        # Add frequency labels
        high_freq = Text("Higher\nFrequency", font_size=20, color=RED)
        high_freq.move_to(RIGHT * 3 + UP * 1.5)

        low_freq = Text("Lower\nFrequency", font_size=20, color=BLUE)
        low_freq.move_to(LEFT * 3 + UP * 1.5)

        self.play(Write(high_freq), Write(low_freq))

        # Clear all waves
        for wave_set in wave_groups:
            self.remove(*wave_set)

        self.wait(2)

        # Fade out everything
        self.play(*[FadeOut(mob) for mob in self.mobjects])
