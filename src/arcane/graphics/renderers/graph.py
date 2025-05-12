from dataclasses import dataclass
from typing import Callable, Tuple
from manim import *
from arcane.core.models.constructs import (
    ParametricMathFunction,
    PolarMathFunction,
    RegularMathFunction,
    SweepTransform,
    VLines,
    Transform as ArcaneTransform,
)
import arcane.graphics.config
import arcane.graphics.utils
from arcane.graphics.utils.manim import get_random_color
from arcane.graphics.utils.math import avoid_zero, compute_function_range
from arcane.graphics.objects import Plot
import numpy as np
from enum import Enum


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
    id: str, function: ParametricMathFunction, transforms: List[ArcaneTransform]
) -> Plot:
    primary_transform = transforms[0]
    auxillary_transforms = transforms[1:]

    start = 0
    end = 0
    if isinstance(primary_transform, SweepTransform):
        start = avoid_zero(primary_transform.sweep_from)
        end = avoid_zero(primary_transform.sweep_to)
    else:
        raise (Exception("unhandled transformation encountered"))

    x_function = lambda t: function.expressions[0].subs(function.variables[0], t)
    y_function = lambda t: function.expressions[1].subs(function.variables[0], t)
    x_range = compute_function_range(x_function, (start, end))
    y_range = compute_function_range(y_function, (start, end))

    def parametric_function(t_val):
        return np.array([float(x_function(t_val)), float(y_function(t_val))])

    def render(axes: Axes):
        graph = None
        if isinstance(primary_transform, SweepTransform):
            graph = axes.plot_parametric_curve(
                lambda t: parametric_function(t),
                t_range=[start, end],
                color=get_random_color(),
                stroke_width=3,
            )

        return graph

    return Plot(
        id,
        container_type="Axis",
        math_function=parametric_function,
        x_range=(x_range[0], x_range[1]),
        y_range=(y_range[0], y_range[1]),
        render=render,
    )


def render_polar_math_function(
    id: str, function: PolarMathFunction, transforms: List[ArcaneTransform]
) -> Plot:
    x_start = 0
    x_end = 0

    primary_transform = transforms[0]

    if isinstance(primary_transform, SweepTransform):
        x_start = avoid_zero(primary_transform.sweep_from)
        x_end = avoid_zero(primary_transform.sweep_to)

    else:
        raise (Exception("unhandled transformation encountered"))

    math_function = lambda x: function.expression.subs(function.variables[0], x)
    y_range = compute_function_range(math_function, [x_start, x_end])

    def render(plane: PolarPlane):
        graph = plane.plot_polar_graph(
            math_function, [x_start, x_end], color=get_random_color()
        )
        return graph

    return Plot(
        id,
        container_type="PolarPlane",
        math_function=math_function,
        x_range=(x_start, x_end),
        y_range=(y_range[0], y_range[1]),
        render=render,
    )


def render_regular_math_function(
    id: str, function: RegularMathFunction, transforms: List[ArcaneTransform]
) -> Plot:

    x_start = 0
    x_end = 0

    primary_transform = transforms[0]

    if isinstance(primary_transform, SweepTransform):
        x_start = avoid_zero(primary_transform.sweep_from)
        x_end = avoid_zero(primary_transform.sweep_to)

    else:
        raise (Exception("unhandled transformation encountered"))

    math_function = lambda x: function.expression.subs(function.variables[0], x)

    y_range = compute_function_range(math_function, [x_start, x_end])

    def render(axes: Axes):
        graph = axes.plot(
            math_function,
            x_range=[x_start, x_end, 0.1],
            color=get_random_color(),
            stroke_width=3,
        )

        # Create animations
        return graph

    return Plot(
        id,
        container_type="Axis",
        math_function=math_function,
        x_range=(x_start, x_end),
        y_range=(y_range[0], y_range[1]),
        render=render,
    )


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
