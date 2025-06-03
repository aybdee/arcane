from dataclasses import dataclass
from typing import Callable, Tuple

from manim import *

import arcane.graphics.config
import arcane.graphics.utils
from arcane.core.models.constructs import (MathFunction,
                                           ParametricMathFunction,
                                           PolarMathFunction,
                                           RegularMathFunction, SweepTransform)
from arcane.core.models.constructs import Transform as ArcaneTransform
from arcane.core.models.constructs import VLines
from arcane.core.runtime.types import InterpreterError, InterpreterErrorCode
from arcane.graphics.utils.manim import get_random_color


def render_vlines_to_function(
    axes: Axes,
    math_function: ParametricFunction,
    vlines: VLines,
    x_range: Tuple[float, float],
):
    lines = axes.get_vertical_lines_to_graph(
        math_function,
        x_range=x_range,
        num_lines=int(vlines.num_lines),
        color=get_random_color(),
    )
    return lines


def render_parametric_math_function(
    function: ParametricMathFunction, axes: Axes, color: ManimColor = get_random_color()
) -> ParametricFunction:

    start = function.t_range[0]
    end = function.t_range[1]

    graph = axes.plot_parametric_curve(
        lambda t: function.math_function(t),
        t_range=[start, end],
        color=color,
        stroke_width=3,
    )

    return graph


def render_polar_math_function(
    function: PolarMathFunction,
    plane: PolarPlane,
    color: ManimColor = get_random_color(),
) -> ParametricFunction:

    x_start = function.x_range[0]
    x_end = function.x_range[1]

    graph = plane.plot_polar_graph(
        function.math_function, [x_start, x_end], color=color
    )

    return graph


def render_regular_math_function(
    function: RegularMathFunction,
    axes: Axes,
    color: ManimColor = get_random_color(),
) -> ParametricFunction:

    x_start = function.x_range[0]
    x_end = function.x_range[1]

    graph = axes.plot(
        function.math_function,
        x_range=[x_start, x_end, 0.1],
        color=color,
        stroke_width=3,
    )

    return graph


def render_sweep_dot(axes: Axes, math_function: Callable, range: Tuple[float, float]):
    t = ValueTracker(int(range[0]))
    dot = Dot(
        point=axes.coords_to_point(t.get_value(), math_function(t.get_value())),
        color=WHITE,
    )

    dot.add_updater(
        lambda x: x.move_to(axes.c2p(t.get_value(), math_function(t.get_value())))
    )
    return (dot, t)


def render_math_function(
    math_function: MathFunction,
    container: Axes | PolarPlane,
    color: ManimColor = get_random_color(),
) -> ParametricFunction:
    """
    Renders a math function based on the container and function type.

    Args:
        container: Either an Axes or PolarPlane object
        math_function: The callable math function to render
        x_range: The range over which to plot the function
    """

    if isinstance(math_function, RegularMathFunction):
        return render_regular_math_function(math_function, container, color)

    elif isinstance(math_function, ParametricMathFunction):
        return render_parametric_math_function(math_function, container, color)

    else:
        if isinstance(container, PolarPlane):
            return render_polar_math_function(math_function, container, color)
        else:
            raise InterpreterError(
                InterpreterErrorCode.UNEXPECTED_TYPE,
                expected="Polar Container",
                gotten="Axis Container",
            )
