from dataclasses import dataclass
from manim import *
from arcane.core.constructs import (
    MathFunction,
    ParametricMathFunction,
    PolarMathFunction,
    RegularMathFunction,
    SweepDotTransform,
    SweepTransform,
)
from arcane.core.constructs import Transform as ArcaneTransform
import arcane.graphics.config
import arcane.graphics.utils
from arcane.graphics.utils import avoid_zero, get_random_color, compute_function_range
from arcane.graphics.objects import Plot, ArcaneDot
import numpy as np
from enum import Enum


def render_parametric_math_function(
    function: ParametricMathFunction, transforms: List[ArcaneTransform]
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

    x_function = lambda t: function.expressions[0].subs(function.variables[0].value, t)
    y_function = lambda t: function.expressions[1].subs(function.variables[0].value, t)
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
        assert graph is not None

        auxillary = []
        # Add sweep dot handling
        for transform in auxillary_transforms:
            if isinstance(transform, SweepDotTransform):
                t = ValueTracker(int(start))  # Start at the beginning of the curve
                dot = Dot(
                    point=axes.coords_to_point(*parametric_function(start)),
                    color=WHITE,
                )

                dot.add_updater(
                    lambda x: x.move_to(
                        axes.coords_to_point(*parametric_function(t.get_value()))
                    )
                )
                auxillary.append(ArcaneDot(value=dot, tracker=t, end=end))

        return (graph, auxillary)

    return Plot(
        render,
        "Axis",
        x_range=(x_range[0], x_range[1]),
        y_range=(y_range[0], y_range[1]),
    )


def render_polar_math_function(
    function: PolarMathFunction, transforms: List[ArcaneTransform]
) -> Plot:
    x_start = 0
    x_end = 0

    primary_transform = transforms[0]
    auxillary_transforms = transforms[1:]

    if isinstance(primary_transform, SweepTransform):
        x_start = avoid_zero(primary_transform.sweep_from)
        x_end = avoid_zero(primary_transform.sweep_to)

    else:
        raise (Exception("unhandled transformation encountered"))

    math_function = lambda x: function.expression.subs(function.variables[0].value, x)
    y_range = compute_function_range(math_function, [x_start, x_end])

    def render(plane: PolarPlane):
        graph = plane.plot_polar_graph(
            math_function, [x_start, x_end], color=get_random_color()
        )

        auxillary = []

        for transform in auxillary_transforms:
            if isinstance(transform, SweepDotTransform):
                t = ValueTracker(int(x_start))
                dot = Dot(
                    point=plane.coords_to_point(
                        t.get_value(), math_function(t.get_value())
                    ),
                    color=WHITE,
                )

                dot.add_updater(
                    lambda x: x.move_to(
                        plane.c2p(t.get_value(), math_function(t.get_value()))
                    )
                )
                auxillary.append(ArcaneDot(value=dot, tracker=t, end=x_end))

        # Create animations
        return (graph, auxillary)

    return Plot(
        render, "PolarPlane", x_range=(x_start, x_end), y_range=(y_range[0], y_range[1])
    )


def render_regular_math_function(
    function: RegularMathFunction, transforms: List[ArcaneTransform]
) -> Plot:

    x_start = 0
    x_end = 0

    primary_transform = transforms[0]
    auxillary_transforms = transforms[1:]

    if isinstance(primary_transform, SweepTransform):
        x_start = avoid_zero(primary_transform.sweep_from)
        x_end = avoid_zero(primary_transform.sweep_to)

    else:
        raise (Exception("unhandled transformation encountered"))

    math_function = lambda x: function.expression.subs(function.variables[0].value, x)

    y_range = compute_function_range(math_function, [x_start, x_end])

    def render(axes: Axes):
        graph = axes.plot(
            math_function,
            x_range=[x_start, x_end, 0.1],
            color=get_random_color(),
            stroke_width=3,
        )
        auxillary = []

        for transform in auxillary_transforms:
            if isinstance(transform, SweepDotTransform):
                t = ValueTracker(int(x_start))
                dot = Dot(
                    point=axes.coords_to_point(
                        t.get_value(), math_function(t.get_value())
                    ),
                    color=WHITE,
                )

                dot.add_updater(
                    lambda x: x.move_to(
                        axes.c2p(t.get_value(), math_function(t.get_value()))
                    )
                )
                auxillary.append(ArcaneDot(value=dot, tracker=t, end=x_end))

        # Create animations
        return (graph, auxillary)

    return Plot(
        render, "Axis", x_range=(x_start, x_end), y_range=(y_range[0], y_range[1])
    )
