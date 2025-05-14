from dataclasses import dataclass
from typing import Any, List, Optional, OrderedDict
from arcane.core.models.constructs import (
    ArcanePoint,
    MathFunction,
    ObjectTransform,
    ParametricMathFunction,
    PolarMathFunction,
    RegularMathFunction,
    SweepDot,
    SweepObjects,
    VLines,
    ArcaneText,
    ArcaneLine,
    ArcaneElbow,
    ArcaneSquare,
    ArcaneRectangle,
    ArcaneRegularPolygon,
    ArcanePolygon,
)
from manim import *
from arcane.graphics.animation import AnimationItem, AnimationPhase
from arcane.graphics.renderers.geometry import (
    render_line,
    render_point,
    render_elbow,
    render_square,
    render_rectangle,
    render_regular_polygon,
    render_polygon,
)
from arcane.graphics.renderers.graph import (
    render_math_function,
    render_sweep_dot,
    render_vlines_to_function,
)
from arcane.graphics.renderers.misc import render_text
from arcane.graphics.objects import PlotContainer
from pprint import pprint
import arcane.graphics.config
from arcane.graphics.utils.math import generate_math_function


SceneObject = (
    PlotContainer
    | VLines
    | ArcaneText
    | SweepDot
    | ArcaneLine
    | ArcanePoint
    | ArcaneElbow
    | ArcaneSquare
    | ArcaneRectangle
    | ArcaneRegularPolygon
    | ArcanePolygon
    | ObjectTransform
    | MathFunction
)


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

        if isinstance(node.value, MathFunction):
            container_id = node.dependencies[0]
            container = self.dependency_tree[container_id]
            if container.mobject is None:
                raise ValueError(
                    f"Container mobject for {container_id} is not resolved"
                )

            plot = render_math_function(node.value, container.mobject)

            node.mobject = plot

            self.animations.append(
                AnimationItem(animation=Create(plot), phase=AnimationPhase.PRIMARY)
            )

        elif isinstance(node.value, ArcanePoint):
            mobject = render_point(node.value)
            node.mobject = mobject
            self.dependency_tree[id].mobject = mobject
            for dependant_id in dependants.keys():
                try:
                    # TODO:(figure out better way to do this)
                    self.resolve_dependency(dependant_id)
                except Exception as e:
                    pass

            self.animations.append(
                AnimationItem(
                    animation=Create(mobject),
                    phase=AnimationPhase.PRIMARY,
                )
            )

        elif isinstance(node.value, ArcaneLine):
            if isinstance(node.value.definition, SweepObjects):
                from_node = self.dependency_tree[
                    node.value.definition.sweep_from
                ]  # type:ignore
                to_node = self.dependency_tree[
                    node.value.definition.sweep_to
                ]  # type:ignore

                assert from_node.mobject is not None

                assert to_node.mobject is not None

                self.animations.append(
                    AnimationItem(
                        animation=Create(
                            render_line(node.value, from_node.mobject, to_node.mobject)
                        ),
                        phase=AnimationPhase.PRIMARY,
                    )
                )
            else:
                self.animations.append(
                    AnimationItem(
                        animation=Create(render_line(node.value)),
                        phase=AnimationPhase.PRIMARY,
                    )
                )

        elif isinstance(node.value, ObjectTransform):
            from_object_id = node.value.object_from.id
            to_object = node.value.object_to
            from_object = self.dependency_tree[from_object_id]
            container_id = from_object.dependencies[0]
            container = self.dependency_tree[container_id]
            if container.mobject is None:
                raise ValueError(
                    f"Container mobject for {container_id} is not resolved"
                )

            assert from_object.mobject is not None

            if isinstance(from_object.value, MathFunction):
                to_object.x_range = from_object.value.x_range
                to_object.y_range = from_object.value.y_range
                if isinstance(from_object.value, ParametricMathFunction):
                    assert isinstance(to_object, ParametricMathFunction)
                    to_object.t_range = from_object.value.t_range

            # come up with cleaner way to do this
            to_object.math_function = generate_math_function(to_object)
            to_mobject = render_math_function(
                to_object, container.mobject, from_object.mobject.color
            )
            assert isinstance(from_object.mobject, Mobject)
            self.animations.append(
                AnimationItem(
                    animation=ReplacementTransform(from_object.mobject, to_mobject),
                    phase=AnimationPhase.PRIMARY,
                )
            )
            from_object.mobject = to_mobject

            node.mobject = to_mobject

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

            if not isinstance(parent_plot.value, MathFunction):
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

            if not isinstance(parent_plot.value, MathFunction):
                raise ValueError(
                    f"Expected Plot for {parent_plot_id}, got {type(parent_plot.value)}"
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

            if not isinstance(parent_plot.value, MathFunction):
                raise ValueError(
                    f"Expected Plot for {parent_plot_id}, got {type(parent_plot.value)}"
                )
            parent_axis_id = parent_plot.dependencies[0]
            parent_axis_node = self.dependency_tree[parent_axis_id]
            parent_axis = parent_axis_node.mobject

            assert parent_plot.mobject is not None
            assert parent_axis is not None

            dot, tracker = render_sweep_dot(
                parent_axis,
                parent_plot.value.math_function,
                parent_plot.value.x_range,
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
                if isinstance(dependant.value, MathFunction):
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

        elif isinstance(node.value, ArcaneElbow):
            angle_mobject = render_elbow(node.value)
            node.mobject = angle_mobject
            self.animations.append(
                AnimationItem(
                    animation=Create(angle_mobject),
                    phase=AnimationPhase.PRIMARY,
                )
            )

        elif isinstance(node.value, ArcaneSquare):
            square_mobject = render_square(node.value)
            node.mobject = square_mobject
            self.animations.append(
                AnimationItem(
                    animation=Create(square_mobject),
                    phase=AnimationPhase.PRIMARY,
                )
            )

        elif isinstance(node.value, ArcaneRectangle):
            rectangle_mobject = render_rectangle(node.value)
            node.mobject = rectangle_mobject
            self.animations.append(
                AnimationItem(
                    animation=Create(rectangle_mobject),
                    phase=AnimationPhase.PRIMARY,
                )
            )

        elif isinstance(node.value, ArcaneRegularPolygon):
            polygon_mobject = render_regular_polygon(node.value)
            node.mobject = polygon_mobject
            self.animations.append(
                AnimationItem(
                    animation=Create(polygon_mobject),
                    phase=AnimationPhase.PRIMARY,
                )
            )

        elif isinstance(node.value, ArcanePolygon):
            polygon_mobject = render_polygon(node.value)
            node.mobject = polygon_mobject
            self.animations.append(
                AnimationItem(
                    animation=Create(polygon_mobject),
                    phase=AnimationPhase.PRIMARY,
                )
            )

    def build(self) -> None:

        def get_pending_animations() -> OrderedDict[str, DependencyNode]:
            pending = OrderedDict()

            # Check items without dependencies first
            for id, node in self.dependency_tree.items():
                if not node.dependencies and node.mobject is None:
                    pending[id] = node

            # Check items with dependencies
            for id, node in self.dependency_tree.items():
                if node.mobject is None and node.dependencies:
                    # Check if all dependencies are resolved
                    all_deps_resolved = all(
                        self.dependency_tree[dep].mobject is not None
                        for dep in node.dependencies
                    )
                    if all_deps_resolved:
                        pending[id] = node

            return pending

        previous_pending = None
        iteration_count = 0

        while True:
            pending = get_pending_animations()

            # No more pending animations, we're done
            if not pending:
                break

            # Check if we're stuck in a loop
            if pending == previous_pending:
                iteration_count += 1
                if iteration_count >= 2:
                    unresolved = [
                        id
                        for id, node in self.dependency_tree.items()
                        if node.mobject is None
                    ]
                    raise ValueError(
                        f"Unable to resolve dependencies after multiple iterations. Unresolved nodes: {unresolved}"
                    )
            else:
                iteration_count = 0

            # Process pending animations
            for dependency_id in pending.keys():
                self.resolve_dependency(dependency_id)

            previous_pending = pending
