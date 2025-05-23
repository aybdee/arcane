from dataclasses import dataclass
from enum import Enum
from typing import Callable, Optional, Tuple

import numpy as np
from manim import *

from arcane.core.models.constructs import (ArcaneCircle, ArcaneElbow,
                                           ArcaneLine, ArcanePoint,
                                           ArcanePolygon, ArcaneRectangle,
                                           ArcaneRegularPolygon, ArcaneSquare,
                                           SweepCoordinates, SweepObjects,
                                           ThreePoint)
from arcane.graphics.utils.manim import apply_positioning, get_random_color


@apply_positioning
def render_point(point: ArcanePoint, **kwargs):
    return Dot()


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
        vertex = np.array([*elbow.definition.position, 0])
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


@apply_positioning
def render_square(square: ArcaneSquare, **kwargs):
    length = square.definition.length

    # Create square using a Rectangle with equal width and height
    square_mobject = Square(
        side_length=length,
        color=get_random_color(),
    )
    return square_mobject


@apply_positioning
def render_rectangle(rectangle: ArcaneRectangle, **kwargs):
    width = rectangle.definition.width
    height = rectangle.definition.height

    rectangle_mobject = Rectangle(
        width=width,
        height=height,
        color=get_random_color(),
    )

    return rectangle_mobject


@apply_positioning
def render_regular_polygon(polygon: ArcaneRegularPolygon, **kwargs):
    radius = polygon.definition.radius
    num_sides = polygon.definition.num_sides

    polygon_mobject = RegularPolygon(
        n=num_sides,
        radius=radius,
        color=get_random_color(),
    )

    return polygon_mobject


def render_polygon(polygon: ArcanePolygon):
    # Convert points to numpy arrays with z=0
    points = [np.array([*point, 0]) for point in polygon.definition.points]

    polygon_mobject = Polygon(
        *points,
        color=get_random_color(),
    )

    return polygon_mobject


@apply_positioning
def render_circle(circle: ArcaneCircle, **kwargs):
    radius = circle.definition.radius

    circle_mobject = Circle(
        radius=radius,
        color=get_random_color(),
    )

    return circle_mobject
