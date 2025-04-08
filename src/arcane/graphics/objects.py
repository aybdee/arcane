from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Literal, Tuple
from abc import ABC, abstractmethod
from arcane.graphics.animation import AnimationItem, AnimationPhase
from manim import *
import numpy as np

PlotContainerType = Literal["PolarPlane"] | Literal["Axis"]


class Frame(ABC):
    @abstractmethod
    def render(self, scene) -> Tuple[VGroup, List[AnimationItem]]: ...


@dataclass
class Plot:
    render: Callable
    container_type: PlotContainerType
    x_range: Tuple[float, float]
    y_range: Tuple[float, float]


@dataclass
class ArcaneDot:
    value: Dot
    tracker: ValueTracker
    end: float


class PlotContainer(Frame):
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

    def render(self, scene):
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
            container = Axes(
                x_range=x_range,
                y_range=y_range,
                axis_config={"color": WHITE},
                tips=False,
                x_axis_config={"unit_size": 0.5},
                y_axis_config={"unit_size": 0.5},
            )
        else:
            container = PolarPlane()

        plots, auxillary = map(
            list, zip(*[item.render(container) for item in self.items])
        )
        animations = []

        plots_group = VGroup(container, *plots)  # Group axes and plots

        animations.append(
            AnimationItem(
                animation=container, phase=AnimationPhase.SETUP, animate=False
            )
        )

        for plot in plots:
            animations.append(
                AnimationItem(animation=Create(plot), phase=AnimationPhase.PRIMARY)
            )

        for aux_group in auxillary:
            for construct in aux_group:
                if isinstance(construct, ArcaneDot):
                    animations.append(
                        AnimationItem(
                            animation=construct.value,
                            phase=AnimationPhase.SECONDARY,
                            animate=False,
                        )
                    )

                    animations.append(
                        AnimationItem(
                            animation=construct.tracker.animate.set_value(
                                construct.end
                            ),
                            phase=AnimationPhase.SECONDARY,
                            config={"rate_func": linear},
                        )
                    )

        return plots_group, animations
