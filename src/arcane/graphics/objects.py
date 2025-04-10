from __future__ import annotations
import uuid
from dataclasses import dataclass
from typing import Callable, Literal, Tuple, Protocol, Any, Optional
from abc import ABC, abstractmethod
from arcane.graphics.animation import AnimationItem, AnimationPhase
from collections import OrderedDict
from manim import *

PlotContainerType = Literal["PolarPlane"] | Literal["Axis"]


class Frame(ABC):
    @abstractmethod
    def render(self, scene) -> Tuple[VGroup, List[AnimationItem]]: ...


class Renderable(Protocol):
    def render(self) -> Any: ...


@dataclass
class Plot(Renderable):
    id: str
    container_type: PlotContainerType
    x_range: Tuple[float, float]
    y_range: Tuple[float, float]
    render: Callable


@dataclass
class ArcaneDot:
    value: Dot
    tracker: ValueTracker
    end: float


class SceneBuilder:
    def __init__(self):
        self.dependency_tree = OrderedDict()
        self.frames = []
        pass

    def num_objects(self):
        return len(self.dependency_tree.keys())

    def add_object(
        self,
        id: str,
        value: Plot | PlotContainer,
        dependencies: List[str] = [],
    ):
        self.dependency_tree[id] = {
            "value": value,
            "dependencies": dependencies,
        }
        return id

    def add_dependency(self, id: str, dependency: str):
        self.dependency_tree[id].append(dependency)

    def get(self, id: str):
        return self.dependency_tree.get(id)

    def resolve_dependency(self, id):
        dependency = self.get(id)

        dependants = OrderedDict(
            (k, v) for k, v in self.dependency_tree.items() if id in v["dependencies"]
        )
        assert dependency is not None
        if isinstance(dependency["value"], Plot):
            container_id = self.dependency_tree[id]["dependencies"][0]
            container = self.dependency_tree[container_id]
            self.dependency_tree[id]["mobject"] = dependency["value"].render(
                container["mobject"]
            )
        if isinstance(dependency["value"], PlotContainer):
            for dependant_id, dependant in dependants.items():
                dependency["value"].add(dependant["value"])
            self.dependency_tree[id]["mobject"] = dependency["value"].render()

            # resolve children
            for dependant_id in dependants.keys():
                self.resolve_dependency(dependant_id)

            plots, auxillary = map(
                list,
                zip(
                    *[
                        self.dependency_tree[dependant_id]["mobject"]
                        for dependant_id in dependants.keys()
                    ]
                ),
            )
            animations = []

            plots_group = VGroup(
                self.dependency_tree[id]["mobject"], *plots
            )  # Group axes and plots

            animations.append(
                AnimationItem(
                    animation=self.dependency_tree[id]["mobject"],
                    phase=AnimationPhase.SETUP,
                    animate=False,
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

            self.frames.append((plots_group, animations))

    def build(self):
        no_deps = OrderedDict(
            (k, v) for k, v in self.dependency_tree.items() if not v["dependencies"]
        )

        for dependency_id in no_deps.keys():
            self.resolve_dependency(dependency_id)

        return self.frames


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
