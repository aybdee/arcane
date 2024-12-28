from dataclasses import dataclass
from typing import Callable, Tuple
from abc import ABC, abstractmethod
from manim import *


class Frame(ABC):
    @abstractmethod
    def render(self) -> AnimationGroup: ...


@dataclass
class Plot:
    render: Callable
    x_range: Tuple[float, float]
    y_range: Tuple[float, float]


class Axis(Frame):
    def __init__(self):
        self.items: List[Plot] = []
        self.x_range = (0, 0)
        self.y_range = (0, 0)

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
        axes = Axes(
            x_range=[
                self.x_range[0] * 2,
                self.x_range[1] * 2,
                1,
            ],
            y_range=[
                self.y_range[0] * 2,
                self.x_range[1] * 2,
                1,
            ],
            axis_config={"color": GREEN},
            tips=False,
        )

        axes.shift(-axes.coords_to_point(0, 0))  # Move (0, 0) to ORIGIN

        return AnimationGroup(
            *[
                Create(axes),
                *[item.render(axes) for item in self.items],
            ],
            lag_ratio=0.2,
        )
