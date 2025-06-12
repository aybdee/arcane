from dataclasses import dataclass
from pprint import pprint
from typing import Any, List, Optional, OrderedDict, Tuple

from manim import *

import arcane.graphics.config
from arcane.core.models.constructs import (
    ArcaneArrow,
    ArcaneCircle,
    ArcaneClearObject,
    ArcaneElbow,
    ArcaneLine,
    ArcanePoint,
    ArcanePolygon,
    ArcaneRectangle,
    ArcaneRegularPolygon,
    ArcaneSquare,
    ArcaneText,
    MathFunction,
    ObjectTransform,
    ParametricMathFunction,
    PolarMathFunction,
    Position,
    RegularMathFunction,
    RelativeAnglePosition,
    RelativeDirectionPosition,
    SweepDot,
    SweepObjects,
    VLines,
)
from arcane.core.runtime.types import InterpreterError, InterpreterErrorCode
from arcane.graphics.animation import AnimationItem, AnimationPhase
from arcane.graphics.objects import PlotContainer
from arcane.graphics.renderers.geometry import (
    render_arrow,
    render_circle,
    render_elbow,
    render_line,
    render_point,
    render_polygon,
    render_rectangle,
    render_regular_polygon,
    render_square,
)
from arcane.graphics.renderers.graph import (
    render_math_function,
    render_sweep_dot,
    render_vlines_to_function,
)
from arcane.graphics.renderers.misc import render_text
from arcane.graphics.utils.math import compute_point_on_circle, generate_math_function

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
    | ArcaneCircle
    | ArcaneArrow
    | ArcaneClearObject
)


@dataclass
class DependencyNode:
    """A node in the dependency tree."""

    statement_index: int
    value: SceneObject
    dependencies: List[str]
    mobject: Optional[Any] = None
    relative_mobject: Optional[Mobject] = None


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
        statement_index: int,
        value: SceneObject,
        dependencies: List[str] = [],
    ) -> str:

        definition = getattr(value, "definition", None)
        position: Optional[Position] = None
        if definition:
            position = getattr(definition, "position", None)
        else:
            position = getattr(value, "position", None)

        if isinstance(position, (RelativeDirectionPosition, RelativeAnglePosition)):
            dependencies.append(position.variable.value)

        self.dependency_tree[id] = DependencyNode(
            value=value,
            statement_index=statement_index,
            dependencies=dependencies,
        )
        return id

    def resolve_position(self, id: str):
        node = self.dependency_tree[id]
        # check if object uses definition
        definition = getattr(node.value, "definition", None)
        position: Optional[Position] = None
        if definition:
            position = getattr(definition, "position", None)
        else:
            position = getattr(node.value, "position", None)
        if position is None:
            return

        if isinstance(position, Tuple):
            return
        elif isinstance(position, RelativeAnglePosition):
            relative_object_id = position.variable
            relative_object = self.dependency_tree[relative_object_id.value]
            if isinstance(relative_object.value, ArcaneCircle):
                circle_center = relative_object.mobject.get_center()
                point_on_circle = compute_point_on_circle(
                    (
                        circle_center[0],
                        circle_center[1],
                    ),
                    relative_object.value.definition.radius,
                    position.angle,
                )
                if definition:
                    self.dependency_tree[
                        id
                    ].value.definition.position = (  # type:ignore
                        point_on_circle
                    )
                else:
                    self.dependency_tree[id].value.position = (  # type:ignore
                        point_on_circle
                    )
            else:
                raise InterpreterError(
                    error_code=InterpreterErrorCode.UNEXPECTED_TYPE,
                    expected="ArcaneCircle",
                    gotten=type(relative_object.value).__name__,
                )

        elif isinstance(position, RelativeDirectionPosition):
            relative_object_id = position.variable
            relative_object = self.dependency_tree[relative_object_id.value]
            self.dependency_tree[id].relative_mobject = relative_object.mobject

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
        self.resolve_position(id)
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
                AnimationItem(
                    node.statement_index,
                    animation=Create(plot),
                    phase=AnimationPhase.PRIMARY,
                )
            )

        elif isinstance(node.value, ArcanePoint):
            mobject = render_point(node.value, relative_mobject=node.relative_mobject)
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
                    node.statement_index,
                    animation=Create(mobject),
                    phase=AnimationPhase.PRIMARY,
                )
            )

        elif isinstance(node.value, ArcaneClearObject):
            obj_to_clear_id = node.dependencies[0]
            obj_to_clear = self.dependency_tree[obj_to_clear_id]
            assert obj_to_clear.mobject is not None
            self.animations.append(
                AnimationItem(
                    node.statement_index,
                    animation=FadeOut(obj_to_clear.mobject),
                    phase=AnimationPhase.PRIMARY,
                )
            )
            node.mobject = True

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

                line = render_line(node.value, from_node.mobject, to_node.mobject)
                self.dependency_tree[id].mobject = line

                self.animations.append(
                    AnimationItem(
                        node.statement_index,
                        animation=Create(line),
                        phase=AnimationPhase.PRIMARY,
                    )
                )
            else:
                line = render_line(node.value)
                self.dependency_tree[id].mobject = line
                self.animations.append(
                    AnimationItem(
                        node.statement_index,
                        animation=Create(line),
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
                    node.statement_index,
                    animation=ReplacementTransform(from_object.mobject, to_mobject),
                    phase=AnimationPhase.PRIMARY,
                )
            )
            from_object.mobject = to_mobject

            node.mobject = to_mobject

        elif isinstance(node.value, ArcaneText):
            text_mobject = render_text(
                node.value, relative_mobject=node.relative_mobject
            )

            self.animations.append(
                AnimationItem(
                    node.statement_index,
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
                    node.statement_index,
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
                    node.statement_index,
                    animation=dot,
                    phase=AnimationPhase.SECONDARY,
                    animate=False,
                )
            )

            self.animations.append(
                AnimationItem(
                    node.statement_index,
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
                    node.statement_index,
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
                    node.statement_index,
                    animation=Create(angle_mobject),
                    phase=AnimationPhase.PRIMARY,
                )
            )

        elif isinstance(node.value, ArcaneSquare):
            square_mobject = render_square(
                node.value, relative_mobject=node.relative_mobject
            )
            node.mobject = square_mobject
            self.animations.append(
                AnimationItem(
                    node.statement_index,
                    animation=Create(square_mobject),
                    phase=AnimationPhase.PRIMARY,
                )
            )

        elif isinstance(node.value, ArcaneRectangle):
            rectangle_mobject = render_rectangle(
                node.value, relative_mobject=node.relative_mobject
            )
            node.mobject = rectangle_mobject
            self.animations.append(
                AnimationItem(
                    node.statement_index,
                    animation=Create(rectangle_mobject),
                    phase=AnimationPhase.PRIMARY,
                )
            )

        elif isinstance(node.value, ArcaneRegularPolygon):
            polygon_mobject = render_regular_polygon(
                node.value, relative_mobject=node.relative_mobject
            )
            node.mobject = polygon_mobject
            self.animations.append(
                AnimationItem(
                    node.statement_index,
                    animation=Create(polygon_mobject),
                    phase=AnimationPhase.PRIMARY,
                )
            )

        elif isinstance(node.value, ArcanePolygon):
            polygon_mobject = render_polygon(node.value)
            node.mobject = polygon_mobject
            self.animations.append(
                AnimationItem(
                    node.statement_index,
                    animation=Create(polygon_mobject),
                    phase=AnimationPhase.PRIMARY,
                )
            )

        elif isinstance(node.value, ArcaneCircle):
            circle_mobject = render_circle(
                node.value, relative_mobject=node.relative_mobject
            )
            node.mobject = circle_mobject
            self.animations.append(
                AnimationItem(
                    node.statement_index,
                    animation=Create(circle_mobject),
                    phase=AnimationPhase.PRIMARY,
                )
            )

        elif isinstance(node.value, ArcaneArrow):
            if isinstance(node.value.definition, SweepObjects):
                from_node = self.dependency_tree[
                    node.value.definition.sweep_from.value
                ]  # type:ignore
                to_node = self.dependency_tree[
                    node.value.definition.sweep_to.value
                ]  # type:ignore

                assert from_node.mobject is not None

                assert to_node.mobject is not None

                line = render_arrow(node.value, from_node.mobject, to_node.mobject)
                self.dependency_tree[id].mobject = line

                self.animations.append(
                    AnimationItem(
                        node.statement_index,
                        animation=Create(line),
                        phase=AnimationPhase.PRIMARY,
                    )
                )
            else:
                arrow_mobject = render_arrow(node.value)
                node.mobject = arrow_mobject
                self.animations.append(
                    AnimationItem(
                        node.statement_index,
                        animation=Create(arrow_mobject),
                        phase=AnimationPhase.PRIMARY,
                    )
                )

    def build(self) -> None:
        # pprint(self.dependency_tree)

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
            for id in pending.keys():
                self.resolve_dependency(id)

            previous_pending = pending
