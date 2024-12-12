from manim import *
from arcane.core.constructs import MathFunction
from arcane.core.constructs import Transform as ArcaneTransform
import arcane.graphics.config
import arcane.graphics.utils
import numpy as np

def animate_math_function(function:MathFunction, transform:ArcaneTransform):
    def animate():
        axes = Axes(
            x_range=[-7, 7, 1],  # Extended x-range for more visual balance
            y_range=[-3.0, 3.0, 1],  # Adjusted y-range for typical functions
            
            x_length=12,
            y_length=6,
            axis_config={"color": GREEN},
            tips=False, 
        )

        # Smoother graph plotting
        graph = axes.clip_plot(
            lambda x: function.expression.subs(function.variables[0].value, x),
            x_range=[-7, 7,0.1],
            color=BLUE,  # Set a pleasing color for the graph
            stroke_width=3,  # Make the graph line slightly bolder
        )

        # Add labels for clarity
        labels = axes.get_axis_labels(x_label="x", y_label="f(x)")

    # Create animations
        return AnimationGroup(Create(axes), Create(graph), Write(labels), lag_ratio=0.2)
    return animate



