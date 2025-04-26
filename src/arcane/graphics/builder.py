from dataclasses import dataclass
from typing import Any, List, Optional, OrderedDict
from arcane.core.models.constructs import SweepDot, VLines, ArcaneText
from manim import *
from arcane.graphics.animation import AnimationItem, AnimationPhase
from arcane.graphics.renderers.graph import (
    render_sweep_dot,
    render_vlines_to_function,
)
from arcane.graphics.renderers.misc import render_text
from arcane.graphics.objects import Plot, PlotContainer
from pprint import pprint


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
            text_mobject = render_text(node.value, parent_object.mobject)

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

            lines = render_vlines_to_function(
                parent_axis,
                parent_graph,
                node.value,
                parent_plot.value.x_range,
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
            parent_axis_id = parent_plot.dependencies[0]
            parent_axis_node = self.dependency_tree[parent_axis_id]
            parent_axis = parent_axis_node.mobject

            assert parent_plot.mobject is not None
            assert parent_axis is not None

            dot, tracker = render_sweep_dot(
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

            plots_group = VGroup(
                node.mobject,
                *descendants,
            )

            self.animations.append(
                AnimationItem(
                    animation=node.mobject,
                    phase=AnimationPhase.SETUP,
                    animate=False,
                )
            )

            self.groups.append(plots_group)

    def build(self) -> None:
        pprint(self.dependency_tree)
        no_deps = OrderedDict(
            (k, v) for k, v in self.dependency_tree.items() if not v.dependencies
        )

        for dependency_id in no_deps.keys():
            self.resolve_dependency(dependency_id)
