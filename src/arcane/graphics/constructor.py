from manim import *
from arcane.core.constructs import MathFunction, MultiSweepTransform, ParametricMathFunction, RegularMathFunction, SweepTransform
from arcane.core.constructs import Transform as ArcaneTransform
import arcane.graphics.config
import arcane.graphics.utils
from arcane.graphics.utils import get_random_color
import numpy as np


def render_parametric_math_function(function:ParametricMathFunction,transform:ArcaneTransform):
    def parametric_function(t_val):
        # Perform substitution for each expression
        substituted_values = [expr.subs(function.variables[0].value, t_val) for expr in function.expressions]
        return np.array([float(substituted_values[0]), float(substituted_values[1]), 0])

    # for i in range(1,10):
    #     print(parametric_function(i))
    
    def render(axes:Axes):
        graph = None
        if isinstance(transform,SweepTransform):
            start = transform.sweep_from
            end = transform.sweep_to
            if len(function.variables) == 1:
                graph = axes.plot_parametric_curve(lambda t: parametric_function(t),
           t_range =[start,end],
           color=get_random_color(),
           stroke_width=3)
        assert graph is not None
        return AnimationGroup(Create(graph))
    return render


def render_regular_math_function(function:RegularMathFunction, transform:ArcaneTransform):
    def render(axes: Axes):
        if isinstance(transform,MultiSweepTransform):
            x_range = transform.transforms[0][1]
            x_start = x_range.sweep_from
            x_end = x_range.sweep_to

            graph = axes.clip_plot(
                lambda x: function.expression.subs(function.variables[0].value, x),
                x_range=[x_start, x_end,0.1],
                color=get_random_color(),  # Set a pleasing color for the graph
                stroke_width=3,  # Make the graph line slightly bolder
            )

        elif isinstance(transform,SweepTransform):
            x_start = transform.sweep_from
            x_end = transform.sweep_to

            graph = axes.clip_plot(
                lambda x: function.expression.subs(function.variables[0].value, x),
                x_range=[x_start, x_end,0.1],
                color=get_random_color(),  # Set a pleasing color for the graph
                stroke_width=3,  # Make the graph line slightly bolder
            )
            

        else:
            graph = axes.clip_plot(
                lambda x: function.expression.subs(function.variables[0].value, x),
                x_range=[-7, 7,0.1],
                color=get_random_color(),  # Set a pleasing color for the graph
                stroke_width=3,  # Make the graph line slightly bolder
            )
            
    # Create animations
        return AnimationGroup(Create(graph))
    return render
