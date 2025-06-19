from manim import *
import numpy as np

class FullWaveRectification(Scene):
    def construct(self):
        # Title
        title = Text("Full Wave Rectification", font_size=36, color=BLUE)
        title.to_edge(UP)
        self.play(Write(title))
        self.wait(0.5)
        
        # Create axes for input sine wave
        input_axes = Axes(
            x_range=[0, 4*PI, PI/2],
            y_range=[-2, 2, 1],
            x_length=6,
            y_length=2,
            axis_config={"color": WHITE, "stroke_width": 2}
        ).shift(UP*2)
        
        input_label = Text("AC Input", font_size=20, color=GREEN).next_to(input_axes, LEFT)
        
        # Create axes for output rectified wave
        output_axes = Axes(
            x_range=[0, 4*PI, PI/2],
            y_range=[0, 2, 1],
            x_length=6,
            y_length=2,
            axis_config={"color": WHITE, "stroke_width": 2}
        ).shift(DOWN*1.5)
        
        output_label = Text("Rectified Output", font_size=20, color=RED).next_to(output_axes, LEFT)
        
        self.play(Create(input_axes), Create(output_axes))
        self.play(Write(input_label), Write(output_label))
        
        # Circuit diagram in the middle
        circuit_group = VGroup()
        
        # AC source
        ac_source = Circle(radius=0.3, color=YELLOW).shift(LEFT*3)
        sine_symbol = Text("~", font_size=20, color=YELLOW).move_to(ac_source)
        
        # Transformer
        primary_coil = Arc(radius=0.2, angle=PI, color=BLUE).shift(LEFT*1.5 + UP*0.3)
        secondary_coil1 = Arc(radius=0.2, angle=PI, color=BLUE).shift(LEFT*0.5 + UP*0.3)
        secondary_coil2 = Arc(radius=0.2, angle=-PI, color=BLUE).shift(LEFT*0.5 + DOWN*0.3)
        center_tap = Dot(LEFT*0.5, color=WHITE)
        
        # Diodes
        diode1 = Polygon(
            [0.2, 0.1, 0], [0.2, -0.1, 0], [0.4, 0, 0],
            color=PURPLE, fill_opacity=1
        ).shift(RIGHT*0.5 + UP*0.5)
        
        diode2 = Polygon(
            [0.2, 0.1, 0], [0.2, -0.1, 0], [0.4, 0, 0],
            color=PURPLE, fill_opacity=1
        ).shift(RIGHT*0.5 + DOWN*0.5)
        
        # Load resistor
        resistor = Rectangle(width=0.6, height=0.2, color=ORANGE).shift(RIGHT*2.5)
        resistor_label = Text("R", font_size=16, color=ORANGE).move_to(resistor)
        
        # Connecting wires
        wire1 = Line(ac_source.get_right(), primary_coil.get_left(), color=WHITE)
        wire2 = Line(secondary_coil1.get_right(), diode1.get_left(), color=WHITE)
        wire3 = Line(secondary_coil2.get_right(), diode2.get_left(), color=WHITE)
        wire4 = Line(diode1.get_right(), resistor.get_top(), color=WHITE)
        wire5 = Line(diode2.get_right(), resistor.get_top(), color=WHITE)
        wire6 = Line(center_tap.get_center(), resistor.get_bottom(), color=WHITE)
        
        circuit_group.add(
            ac_source, sine_symbol, primary_coil, secondary_coil1, secondary_coil2, center_tap,
            diode1, diode2, resistor, resistor_label,
            wire1, wire2, wire3, wire4, wire5, wire6
        )
        
        self.play(Create(circuit_group))
        self.wait(1)
        
        # Animation of sine wave and rectification
        t_tracker = ValueTracker(0)
        
        def get_input_sine():
            t = t_tracker.get_value()
            return input_axes.plot(
                lambda x: np.sin(x), 
                x_range=[0, t], 
                color=GREEN, 
                stroke_width=3
            )
        
        def get_rectified_wave():
            t = t_tracker.get_value()
            return output_axes.plot(
                lambda x: abs(np.sin(x)), 
                x_range=[0, t], 
                color=RED, 
                stroke_width=3
            )
        
        input_sine = always_redraw(get_input_sine)
        rectified_wave = always_redraw(get_rectified_wave)
        
        self.add(input_sine, rectified_wave)
        
        # Animate current flow through diodes
        def update_diode_colors(mob, dt):
            t = t_tracker.get_value()
            sine_val = np.sin(t)
            
            if sine_val > 0:
                diode1.set_fill(color=YELLOW, opacity=0.8)
                diode2.set_fill(color=PURPLE, opacity=0.3)
            else:
                diode1.set_fill(color=PURPLE, opacity=0.3)
                diode2.set_fill(color=YELLOW, opacity=0.8)
        
        diode1.add_updater(update_diode_colors)
        
        # Phase indicators
        positive_phase = Text("Positive Half", font_size=16, color=YELLOW)
        negative_phase = Text("Negative Half", font_size=16, color=YELLOW)
        phase_text = VGroup(positive_phase, negative_phase).arrange(RIGHT, buff=2).shift(DOWN*3)
        
        def update_phase_indicator(mob):
            t = t_tracker.get_value()
            sine_val = np.sin(t)
            
            if sine_val > 0:
                positive_phase.set_opacity(1)
                negative_phase.set_opacity(0.3)
            else:
                positive_phase.set_opacity(0.3)
                negative_phase.set_opacity(1)
        
        phase_text.add_updater(update_phase_indicator)
        self.add(phase_text)
        
        # Animate the waves
        self.play(t_tracker.animate.set_value(4*PI), run_time=8, rate_func=linear)
        
        # Highlight the key concept
        highlight_box = SurroundingRectangle(rectified_wave, color=YELLOW, buff=0.1)
        concept_text = Text("Both halves rectified!", font_size=20, color=YELLOW)
        concept_text.next_to(output_axes, DOWN)
        
        self.play(Create(highlight_box))
        self.play(Write(concept_text))
        self.wait(2)
        
        # Clean up updaters
        diode1.clear_updaters()
        phase_text.clear_updaters()
        
        self.wait(1)