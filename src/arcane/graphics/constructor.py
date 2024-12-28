from manim import *
from arcane.core.constructs import (
    MathFunction,
    ParametricMathFunction,
    RegularMathFunction,
    SweepTransform,
)
from arcane.core.constructs import Transform as ArcaneTransform
import arcane.graphics.config
import arcane.graphics.utils
from arcane.graphics.utils import get_random_color, compute_function_range
from arcane.graphics.objects import Plot
import numpy as np


def render_parametric_math_function(
    function: ParametricMathFunction, transform: ArcaneTransform
) -> Plot:

    start = 0
    end = 0
    if isinstance(transform, SweepTransform):
        start = transform.sweep_from
        end = transform.sweep_to

    else:
        raise (Exception("unhandled transformation encountered"))

    x_function = lambda t: function.expressions[0].subs(function.variables[0].value, t)
    y_function = lambda t: function.expressions[1].subs(function.variables[0].value, t)
    x_range = compute_function_range(x_function, (start, end))
    y_range = compute_function_range(y_function, (start, end))

    def parametric_function(t_val):
        # Perform substitution for each expression
        return np.array([float(x_function(t_val)), float(y_function(t_val))])

    def render(axes: Axes):
        graph = None
        if isinstance(transform, SweepTransform):
            start = transform.sweep_from
            end = transform.sweep_to
            if len(function.variables) == 1:
                graph = axes.plot_parametric_curve(
                    lambda t: parametric_function(t),
                    t_range=[start, end],
                    color=get_random_color(),
                    stroke_width=3,
                )
        assert graph is not None
        return AnimationGroup(Create(graph))

    return Plot(
        render, x_range=(x_range[0], x_range[1]), y_range=(y_range[0], y_range[1])
    )


def render_regular_math_function(
    function: RegularMathFunction, transform: ArcaneTransform
) -> Plot:

    x_start = 0
    x_end = 0
    if isinstance(transform, SweepTransform):
        x_start = transform.sweep_from
        x_end = transform.sweep_to

    else:
        raise (Exception("unhandled transformation encountered"))

    math_function = lambda x: function.expression.subs(function.variables[0].value, x)

    y_range = compute_function_range(math_function, [x_start, x_end])

    def render(axes: Axes):
        graph = axes.clip_plot(
            math_function,
            x_range=[x_start, x_end, 0.1],
            color=get_random_color(),  # Set a pleasing color for the graph
            stroke_width=3,  # Make the graph line slightly bolder
        )

        # Create animations
        return AnimationGroup(Create(graph))

    return Plot(render, x_range=(x_start, x_end), y_range=(y_range[0], y_range[1]))
