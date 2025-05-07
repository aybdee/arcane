from dataclasses import dataclass
from typing import Callable, Optional, Tuple
from manim import *
from arcane.graphics.utils.manim import get_random_color
from arcane.graphics.utils.math import avoid_zero, compute_function_range
from arcane.graphics.objects import Plot
from arcane.core.models.constructs import (
    ArcaneLine,
    ArcanePoint,
    CoordinateAngleLength,
    SweepCoordinates,
    SweepObjects,
)
import numpy as np
from enum import Enum


def render_point(point: ArcanePoint):
    return Dot(np.array([*point.position, 0]))


def render_line(
    line: ArcaneLine,
    from_object: Optional[Mobject] = None,
    to_object: Optional[Mobject] = None,
):
    if isinstance(line.definition, SweepCoordinates):
        return Line(
            start=np.array([*line.definition.sweep_from, 0]),
            end=np.array([*line.definition.sweep_to, 0]),
        )

    elif isinstance(line.definition, SweepObjects):
        assert from_object is not None
        assert to_object is not None

        return Line(start=from_object.get_center(), end=to_object.get_center())
    else:
        direction = np.array(
            [np.cos(line.definition.angle), np.sin(line.definition.angle), 0]
        )

        sweep_from = np.array([*line.definition.sweep_from, 0])
        sweep_to = sweep_from + (line.definition.length * direction)

        return Line(
            start=sweep_from,
            end=np.array(sweep_to),
        )
