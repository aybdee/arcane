from dataclasses import dataclass
from typing import Callable, Tuple
from abc import ABC, abstractmethod
from manim import *


class Frame(ABC):
    @abstractmethod
    def render(self) -> Tuple[VGroup, List]: ...


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
        axes = Axes(
            x_range=[
                self.x_range[0] * 2,
                self.x_range[1] * 2,
                x_step,
            ],
            y_range=[
                self.y_range[0] * 2,
                self.x_range[1] * 2,
                y_step,
            ],
            axis_config={"color": GREEN},
            tips=False,
            x_axis_config={"unit_size": 0.5},
            y_axis_config={"unit_size": 0.5},
        )

        plots = [item.render(axes) for item in self.items]
        plots_group = VGroup(axes, *plots)  # Group axes and plots

        return (
            plots_group,
            [Create(axes), *[Create(plot) for plot in plots]],
        )  # Return the grouped animation
