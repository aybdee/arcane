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
    ThreePoint,
    ArcaneElbow,
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


def render_elbow(elbow: ArcaneElbow):
    if isinstance(elbow.definition, ThreePoint):
        vertex = np.array([*elbow.definition.vertex, 0])
        point1 = np.array([*elbow.definition.point1, 0])
        point2 = np.array([*elbow.definition.point2, 0])

        line1 = Line(vertex, point1)
        line2 = Line(vertex, point2)

        angle_arc = Angle(line1, line2, radius=0.4, other_angle=False, color=WHITE)

        return VGroup(line1, line2, angle_arc)

    else:
        start = np.array([*elbow.definition.sweep_from, 0])
        # Calculate end point using angle and length
        end = np.array(
            [
                start[0] + elbow.definition.length * np.cos(elbow.definition.angle),
                start[1] + elbow.definition.length * np.sin(elbow.definition.angle),
                0,
            ]
        )

        # Create reference line (horizontal from start point)
        ref_end = np.array([start[0] + elbow.definition.length, start[1], 0])
        ref_line = Line(start, ref_end)

        actual_line = Line(start, end)

        angle_arc = Angle(
            ref_line, actual_line, radius=0.4, other_angle=False, color=WHITE
        )

        return VGroup(actual_line, ref_line, angle_arc)
