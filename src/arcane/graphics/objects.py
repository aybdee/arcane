from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Literal, Tuple, Protocol, Any, Optional, TypeVar
from abc import ABC, abstractmethod
from arcane.core.models.constructs import VLines
from arcane.graphics.animation import AnimationItem, AnimationPhase
from collections import OrderedDict
from manim import *

PlotContainerType = Literal["PolarPlane"] | Literal["Axis"]


@dataclass
class Plot:
    id: str
    math_function: Callable
    container_type: PlotContainerType
    x_range: Tuple[float, float]
    y_range: Tuple[float, float]
    render: Callable


class PlotContainer:
    def __init__(self, container_type: PlotContainerType):
        self.container_type = container_type
        self.items: List[Plot] = []
        self.x_range = (0, 0)
        self.y_range = (0, 0)
        self.num_ticks = 5

    def add(self, item: Plot):
        if len(self.items) == 0:
            self.x_range = item.x_range
            self.y_range = item.y_range
        else:
            self.x_range = (
                min(self.x_range[0], item.x_range[0]),
                max(self.x_range[1], item.x_range[1]),
            )

            self.y_range = (
                min(self.y_range[0], item.y_range[0]),
                max(self.y_range[1], item.y_range[1]),
            )
        self.items.append(item)

    def render(self):
        x_step = (self.x_range[1] - self.x_range[0]) / self.num_ticks
        y_step = (self.y_range[1] - self.y_range[0]) / self.num_ticks

        x_range = [
            self.x_range[0] * 2,
            self.x_range[1] * 2,
            x_step,
        ]

        y_range = [
            self.y_range[0] * 2,
            self.y_range[1] * 2,
            y_step,
        ]

        if self.container_type == "Axis":
            return Axes(
                x_range=x_range,
                y_range=y_range,
                axis_config={"color": WHITE},
                tips=False,
                x_axis_config={"unit_size": 0.5},
                y_axis_config={"unit_size": 0.5},
            )
        else:
            return PolarPlane()
