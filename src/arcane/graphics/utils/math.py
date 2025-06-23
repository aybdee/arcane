import copy
from typing import Any, Callable, Tuple, Union

import numpy as np
import sympy
from sympy.core import Add, Mul, Symbol

from arcane.core.models.constructs import (MathFunction,
                                           ParametricMathFunction,
                                           PolarMathFunction,
                                           RegularMathFunction)


def substitute_sympy_expressions(obj: Any, variable: str, value: Any) -> Any:
    """
    Recursively walk through an object or list and substitute sympy expressions.

    Args:
        obj: The object to walk through (can be any type)
        variable: The variable name to substitute (string)
        value: The value to substitute for the variable

    Returns:
        The object with all sympy expressions substituted
    """
    if obj is None:
        return obj

    # Handle sympy expressions
    if isinstance(obj, (Add, Mul, Symbol)):
        try:
            return obj.subs(variable, value)
        except:
            return obj

    # Handle lists and tuples
    if isinstance(obj, (list, tuple)):
        return type(obj)(
            substitute_sympy_expressions(item, variable, value) for item in obj
        )

    # Handle dictionaries
    if isinstance(obj, dict):
        return {
            key: substitute_sympy_expressions(val, variable, value)
            for key, val in obj.items()
        }

    # Handle objects with attributes (dataclasses, custom objects, etc.)
    if hasattr(obj, "__dict__"):
        # Use deep copy to preserve object structure and handle complex initialization
        try:
            result = copy.deepcopy(obj)
            # Recursively substitute in all attributes
            for attr_name, attr_value in result.__dict__.items():
                setattr(
                    result,
                    attr_name,
                    substitute_sympy_expressions(attr_value, variable, value),
                )
            return result
        except (TypeError, ValueError):
            # If deep copy fails, try shallow copy and modify in place
            result = copy.copy(obj)
            for attr_name, attr_value in result.__dict__.items():
                setattr(
                    result,
                    attr_name,
                    substitute_sympy_expressions(attr_value, variable, value),
                )
            return result

    # Handle objects with slots (like some dataclasses)
    if hasattr(obj, "__slots__"):
        try:
            result = copy.deepcopy(obj)
            for slot_name in obj.__slots__:
                if hasattr(result, slot_name):
                    slot_value = getattr(result, slot_name)
                    setattr(
                        result,
                        slot_name,
                        substitute_sympy_expressions(slot_value, variable, value),
                    )
            return result
        except (TypeError, ValueError):
            # If deep copy fails, try shallow copy
            result = copy.copy(obj)
            for slot_name in obj.__slots__:
                if hasattr(result, slot_name):
                    slot_value = getattr(result, slot_name)
                    setattr(
                        result,
                        slot_name,
                        substitute_sympy_expressions(slot_value, variable, value),
                    )
            return result

    # For any other type, return as is
    return obj


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
