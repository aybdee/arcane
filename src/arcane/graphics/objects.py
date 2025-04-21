from __future__ import annotations
import uuid
from dataclasses import dataclass
from typing import Callable, Generic, Literal, Tuple, Protocol, Any, Optional, TypeVar
from abc import ABC, abstractmethod
from arcane.core.constructs import RelativePosition, RelativePositionPlacement
from arcane.graphics.animation import AnimationItem, AnimationPhase
from collections import OrderedDict
from pprint import pprint
from manim import *
from arcane.core.constructs import (
    VLines as VLinesConstruct,
    SweepDot as SweepDotConstruct,
)

PlotContainerType = Literal["PolarPlane"] | Literal["Axis"]


class Frame(ABC):
    @abstractmethod
    def render(self, scene) -> Tuple[VGroup, List[AnimationItem]]: ...


class Renderable(Protocol):
    def render(self) -> Mobject: ...


@dataclass
class Plot(Renderable):
    id: str
    math_function: Callable
    container_type: PlotContainerType
    x_range: Tuple[float, float]
    y_range: Tuple[float, float]
    render: Callable


@dataclass
class SweepDot(SweepDotConstruct):
    render: Callable


@dataclass
class VLines(VLinesConstruct):
    id: str
    x_range: List[float]
    render: Callable


# @dataclass
# class ArcaneDot:
#     value: Dot
#     tracker: ValueTracker
#     end: float


@dataclass
class ArcaneText:
    id: str
    text: str
    relative_to: str
    relative_placement: RelativePositionPlacement
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


SceneObject = Plot | PlotContainer | VLines | ArcaneText | SweepDot


@dataclass
class DependencyNode:
    """A node in the dependency tree."""

    value: SceneObject
    dependencies: List[str]
    mobject: Optional[Any] = None


class SceneBuilder:
    def __init__(self):
        self.dependency_tree: OrderedDict[str, DependencyNode] = OrderedDict()
        self.groups: List[Any] = []
        self.animations: List[AnimationItem] = []

    def num_objects(self) -> int:
        return len(self.dependency_tree.keys())

    def add_object(
        self,
        id: str,
        value: SceneObject,
        dependencies: List[str] = [],
    ) -> str:
        self.dependency_tree[id] = DependencyNode(
            value=value,
            dependencies=dependencies,
        )
        return id

    def add_dependency(self, id: str, dependency: str) -> None:
        if id in self.dependency_tree:
            self.dependency_tree[id].dependencies.append(dependency)

    def get(self, id: str) -> Optional[DependencyNode]:
        return self.dependency_tree.get(id)

    def collect_all_descendant_mobjects(self, current_id: str) -> List[Any]:
        collected: List[Any] = []
        direct_dependants = OrderedDict(
            (k, v)
            for k, v in self.dependency_tree.items()
            if current_id in v.dependencies
        )
        for child_id in direct_dependants:
            node = self.dependency_tree[child_id]
            if node.mobject is None:
                self.resolve_dependency(child_id)

            mobj = node.mobject
            if mobj is not None:
                collected.extend(mobj if isinstance(mobj, (list, tuple)) else [mobj])

            # Recurse
            collected.extend(self.collect_all_descendant_mobjects(child_id))
        return collected

    def resolve_dependency(self, id: str) -> None:
        node = self.get(id)
        if node is None:
            raise ValueError(f"Dependency with ID {id} not found")
        if node.mobject:
            return

        dependants = OrderedDict(
            (k, v) for k, v in self.dependency_tree.items() if id in v.dependencies
        )

        if isinstance(node.value, Plot):
            container_id = node.dependencies[0]
            container = self.dependency_tree[container_id]
            if container.mobject is None:
                raise ValueError(
                    f"Container mobject for {container_id} is not resolved"
                )
            plot = node.value.render(container.mobject)
            node.mobject = plot
            for dependant_id in dependants.keys():
                self.resolve_dependency(dependant_id)

            self.animations.append(
                AnimationItem(animation=Create(plot), phase=AnimationPhase.PRIMARY)
            )

        elif isinstance(node.value, ArcaneText):
            parent_object_id = node.dependencies[0]
            parent_object = self.dependency_tree[parent_object_id]

            assert parent_object.mobject is not None
            text_mobject = node.value.render(
                node.value.text,
                parent_object.mobject,
                node.value.relative_placement,
            )

            self.animations.append(
                AnimationItem(
                    animation=Write(text_mobject),
                    phase=AnimationPhase.PRIMARY,
                    animate=True,
                )
            )

            node.mobject = text_mobject

        elif isinstance(node.value, VLines):
            parent_plot_id = node.dependencies[0]
            parent_plot = self.dependency_tree[parent_plot_id]

            if not isinstance(parent_plot.value, Plot):
                raise ValueError(
                    f"Expected Plot for {parent_plot_id}, got {type(parent_plot.value)}"
                )
            assert parent_plot.mobject is not None
            parent_graph = parent_plot.mobject
            parent_axis_id = parent_plot.dependencies[0]
            parent_axis_node = self.dependency_tree[parent_axis_id]

            if parent_axis_node.mobject is None:
                raise ValueError(
                    f"Parent axis mobject for {parent_axis_id} is not resolved"
                )

            parent_axis = parent_axis_node.mobject

            lines = node.value.render(
                parent_axis,
                parent_graph,
                node.value.x_range,
                node.value.num_lines,
            )
            node.mobject = lines
            self.animations.append(
                AnimationItem(
                    animation=Create(lines),
                    phase=AnimationPhase.SECONDARY,
                    animate=True,
                )
            )

        elif isinstance(node.value, SweepDot):
            parent_plot_id = node.dependencies[0]
            parent_plot = self.dependency_tree[parent_plot_id]

            if not isinstance(parent_plot.value, Plot):
                raise ValueError(
                    f"Expected Plot for {parent_plot_id}, got {type(parent_plot.value)}"
                )
            assert parent_plot.mobject is not None
            parent_axis_id = parent_plot.dependencies[0]
            parent_axis_node = self.dependency_tree[parent_axis_id]
            parent_axis = parent_axis_node.mobject

            dot, tracker = node.value.render(
                parent_axis, parent_plot.value.math_function, parent_plot.value.x_range
            )

            node.mobject = dot

            self.animations.append(
                AnimationItem(
                    animation=dot,
                    phase=AnimationPhase.SECONDARY,
                    animate=False,
                )
            )

            self.animations.append(
                AnimationItem(
                    animation=tracker.animate.set_value(parent_plot.value.x_range[1]),
                    phase=AnimationPhase.SECONDARY,
                    config={"rate_func": linear},
                )
            )

        elif isinstance(node.value, PlotContainer):
            for dependant_id in dependants.keys():
                dependant = self.dependency_tree[dependant_id]
                if isinstance(dependant.value, Plot):
                    node.value.add(dependant.value)

            node.mobject = node.value.render()

            descendants: List[Any] = []
            # resolve children
            for dependant_id in dependants.keys():
                self.resolve_dependency(dependant_id)
            descendants.extend(self.collect_all_descendant_mobjects(id))

            # plots = [
            #     dependant_id
            #     for dependant_id in dependants.keys()
            #     if self.dependency_tree[dependant_id].mobject is not None
            #     and isinstance(self.dependency_tree[dependant_id].value, Plot)
            # ]

            # if not plots_and_aux:
            #     plots = []
            #     auxillary = []
            # else:
            #     plots, auxillary = map(list, zip(*plots_and_aux))
            #
            # auxillary_mobjects: List[Any] = []
            # for aux in auxillary:
            #     if isinstance(aux, ArcaneDot):
            #         auxillary_mobjects.append(aux.value)

            plots_group = VGroup(
                node.mobject,
                *descendants,
            )  # Group axes and plots

            self.animations.append(
                AnimationItem(
                    animation=node.mobject,
                    phase=AnimationPhase.SETUP,
                    animate=False,
                )
            )

            # for plot in plots:
            #     self.animations.append(
            #         AnimationItem(animation=Create(plot), phase=AnimationPhase.PRIMARY)
            #     )

            # for aux_group in auxillary:
            #     for construct in aux_group:
            #         if isinstance(construct, ArcaneDot):
            #             self.animations.append(
            #                 AnimationItem(
            #                     animation=construct.value,
            #                     phase=AnimationPhase.SECONDARY,
            #                     animate=False,
            #                 )
            #             )
            #
            #             self.animations.append(
            #                 AnimationItem(
            #                     animation=construct.tracker.animate.set_value(
            #                         construct.end
            #                     ),
            #                     phase=AnimationPhase.SECONDARY,
            #                     config={"rate_func": linear},
            #                 )
            #             )

            self.groups.append(plots_group)

    def build(self) -> None:
        pprint(self.dependency_tree)
        no_deps = OrderedDict(
            (k, v) for k, v in self.dependency_tree.items() if not v.dependencies
        )

        for dependency_id in no_deps.keys():
            self.resolve_dependency(dependency_id)
