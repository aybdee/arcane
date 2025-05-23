from typing import Callable, Tuple

import numpy as np

from arcane.core.models.constructs import (MathFunction,
                                           ParametricMathFunction,
                                           PolarMathFunction,
                                           RegularMathFunction)


def avoid_zero(num):
    if num == 0:
        return 0.001
    else:
        return num


def compute_point_on_circle(
    center: tuple[float, float], radius: float, angle_rad: float
) -> tuple[float, float]:
    """
    Calculate a point on a circle given the center, radius, and angle in degrees.

    Args:
        center: The center of the circle (x, y).
        radius: The radius of the circle.
        angle_rad: The angle in radians.

    Returns:
        A tuple representing the point on the circle (x, y).
    """
    x = center[0] + radius * np.cos(angle_rad)
    y = center[1] + radius * np.sin(angle_rad)
    return (x, y)


def compute_function_range(func, value_range, num_samples=100):
    x_values = np.linspace(value_range[0], value_range[1], num_samples)
    vfunc = np.vectorize(func)
    y_values = vfunc(x_values)
    y_min, y_max = np.min(y_values), np.max(y_values)
    return (y_min, y_max)


def generate_math_function(math_function: MathFunction) -> Callable:
    """
    Generates the callable math function for different types of math functions.

    Args:
        math_function: The math function object to generate the callable for

    Returns:
        Callable: The generated math function
    """
    if isinstance(math_function, (RegularMathFunction, PolarMathFunction)):
        return lambda x: math_function.expression.subs(math_function.variables[0], x)

    elif isinstance(math_function, ParametricMathFunction):
        x_function = lambda t: math_function.expressions[0].subs(
            math_function.variables[0], t
        )
        y_function = lambda t: math_function.expressions[1].subs(
            math_function.variables[0], t
        )

        def parametric_function(t_val):
            return np.array([float(x_function(t_val)), float(y_function(t_val))])

        return parametric_function

    raise ValueError(f"Unsupported math function type: {type(math_function)}")
