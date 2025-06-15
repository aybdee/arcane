import random
from functools import wraps
from typing import Any, Concatenate, Optional, ParamSpec

from manim import *
from manim.typing import Point3D, Vector3D

from arcane.core.models.constructs import (Direction, Position,
                                           RelativeDirectionPosition,
                                           RelativePositionPlacement)


def get_random_color():
    colors = [GREEN, YELLOW, WHITE, RED, BLUE, ORANGE, PURPLE, TEAL]
    return random.choice(colors)


def get_relative_position(
    mobject_or_point: Mobject | Point3D,
    direction: Vector3D = RIGHT,
    aligned_edge: Vector3D = ORIGIN,
    index_of_submobject_to_align: int | None = None,
):
    if isinstance(mobject_or_point, Mobject):
        mob = mobject_or_point
        if index_of_submobject_to_align is not None:
            target_aligner = mob[index_of_submobject_to_align]
        else:
            target_aligner = mob
        target_point = target_aligner.get_critical_point(aligned_edge + direction)
    else:
        target_point = mobject_or_point
    return target_point


def map_direction(direction: Direction) -> np.ndarray:
    """Maps a Direction enum to a numpy array representing the direction vector."""
    direction_map = {
        Direction.UP: UP,
        Direction.DOWN: DOWN,
        Direction.LEFT: LEFT,
        Direction.RIGHT: RIGHT,
        Direction.IN: IN,
        Direction.OUT: OUT,
    }
    return direction_map.get(direction, np.array([0, 0, 0]))


def clip_plot(csystem, plotfun, x_range=[-5, 5, 0.01], **kwargs):
    grp = VGroup()
    dx = x_range[2]
    for xstart in np.arange(*x_range):
        snip = csystem.plot(plotfun, x_range=[xstart, xstart + dx, 0.5 * dx], **kwargs)
        if (snip.get_top()[1] > csystem.get_top()[1]) or (
            snip.get_bottom()[1] < csystem.get_bottom()[1]
        ):
            snip.set_opacity(0)
        grp += snip
    return grp


def apply_positioning(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        value = args[0]
        relative_mobject: Optional[Mobject] = kwargs.get("relative_mobject", None)
        mobject: Mobject = func(*args, **kwargs)
        definition = getattr(value, "definition", None)
        position: Optional[Position] = None
        if definition:
            position = definition.position
        else:
            position = value.position

        if position:
            if isinstance(position, RelativeDirectionPosition):
                placement = position.placement

                direction_map = {
                    RelativePositionPlacement.ABOVE: UP,
                    RelativePositionPlacement.BELOW: DOWN,
                    RelativePositionPlacement.LEFT: LEFT,
                    RelativePositionPlacement.RIGHT: RIGHT,
                }

                assert relative_mobject is not None

                if placement in direction_map:
                    mobject = mobject.next_to(
                        relative_mobject, direction_map[placement]
                    )
            elif isinstance(position, tuple):
                mobject.move_to(np.array([*position, 0]))

        return mobject

    return wrapper


CoordinateSystem.clip_plot = clip_plot  # type: ignore


def map_color_string(color_str: str) -> ManimColor:
    """Maps string color names to Manim color constants"""
    COLOR_MAP = {
        # Basic colors
        "white": WHITE,
        "black": BLACK,
        "red": RED,
        "green": GREEN,
        "blue": BLUE,
        "yellow": YELLOW,
        "orange": ORANGE,
        "purple": PURPLE,
        "pink": PINK,
        # Light variants
        "light_gray": LIGHT_GRAY,
        "light_brown": "#CD853F",
        # Dark variants
        "dark_gray": DARK_GRAY,
        "dark_blue": DARK_BLUE,
        "dark_brown": "#8B4513",
        # Special colors
        "teal": TEAL,
        "maroon": "#800000",
        "gold": GOLD,
        "gray": GRAY,
    }

    color_str = color_str.lower()
    if color_str not in COLOR_MAP:
        raise ValueError(
            f"Unsupported color: {color_str}. Available colors: {', '.join(COLOR_MAP.keys())}"
        )

    return COLOR_MAP[color_str]
