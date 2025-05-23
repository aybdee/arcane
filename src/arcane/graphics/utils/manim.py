import random
from functools import wraps
from typing import Any, Concatenate, Optional, ParamSpec

from manim import *

from arcane.core.models.constructs import (Position, RelativeDirectionPosition,
                                           RelativePositionPlacement)


def get_random_color():
    colors = [GREEN, YELLOW, WHITE, RED, BLUE, ORANGE, PURPLE, TEAL]
    return random.choice(colors)


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
