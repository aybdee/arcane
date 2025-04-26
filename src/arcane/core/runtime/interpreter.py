from typing import Any, Dict, List, Literal, Optional, Tuple, Union, cast
from enum import Enum
from pprint import pprint


from arcane.core.models.constructs import (
    Animation,
    Identifier,
    ParametricMathFunction,
    PolarMathFunction,
    RegularMathFunction,
    SweepTransform,
    ArcaneText,
    SweepDot,
    VLines,
)


from arcane.graphics.builder import SceneBuilder
from arcane.graphics.renderers.graph import (
    render_parametric_math_function,
    render_polar_math_function,
    render_regular_math_function,
)

from arcane.core.models.constructs import (
    Animation,
    AxisBlock,
    Definition,
    PolarBlock,
    Program,
)
from arcane.graphics.objects import (
    PlotContainer,
    Plot,
)

from arcane.graphics.scene import construct_scene

from arcane.core.runtime.types import (
    InterpreterMessage,
    InterpreterMessageType,
    InterpreterError,
    InterpreterErrorCode,
)
from arcane.core.runtime.store import Store
from arcane.utils import gen_id


class ArcaneInterpreter:
    """
    Interpreter for Arcane language programs

    This interpreter executes statements in an Arcane program one by one,
    maintaining a store of variables and processing animations and axis blocks.
    """

    def __init__(self, program: Program):
        self.program = program
        self.store = Store()
        self.scene_builder = SceneBuilder()
        self.instruction_pointer = 0

        # Results tracking
        self.animation_blocks: List[PlotContainer] = []
        self.global_container: Optional[Dict] = None

    def process_expression(self, expression: Any) -> Any:
        """Evaluates all the terms inside an expression that have stored identifiers"""
        variables = list(expression.free_symbols)
        evaluated_expr = expression

        for variable in variables:
            var_name = str(variable)
            stored_value = self.store.get(var_name)
            if isinstance(stored_value, (int, float)):
                evaluated_expr = evaluated_expr.subs({variable: stored_value})

        return evaluated_expr

    def execute_next(self) -> InterpreterMessage:
        """Execute the next statement in the program"""
        # Check if there are any statements left
        if self.instruction_pointer >= len(self.program.statements):
            raise InterpreterError(InterpreterErrorCode.NO_STATEMENTS_AVAILABLE)

        # Get the current statement and increment the instruction pointer
        current_statement = self.program.statements[self.instruction_pointer]
        self.instruction_pointer += 1

        try:
            if isinstance(current_statement, Definition):
                self.store.add(current_statement.name.value, current_statement.value)
                return InterpreterMessage(InterpreterMessageType.SUCCESS)
            elif isinstance(current_statement, Animation):
                return self.process_animation(current_statement)
            elif isinstance(current_statement, AxisBlock) or isinstance(
                current_statement, PolarBlock
            ):
                return self._handle_plot_block(current_statement)
            else:
                # Handle unsupported statement type
                raise InterpreterError(
                    InterpreterErrorCode.UNSUPPORTED_STATEMENT,
                    statement_type=type(current_statement).__name__,
                )
        except InterpreterError:
            raise
        except Exception as e:
            raise e
            # raise InterpreterError(InterpreterErrorCode.UNKNOWN, details=str(e)) #TODO:(uncomment)

    def process_animation(
        self, animation: Animation, id: str = ""
    ) -> InterpreterMessage:
        """Process an instance animation"""
        instance = animation.instance
        transforms = animation.transforms
        id = id if id else gen_id()

        if isinstance(instance, RegularMathFunction):
            instance.expression = self.process_expression(instance.expression)
            plot = render_regular_math_function(id, instance, transforms)
            return InterpreterMessage(InterpreterMessageType.SUCCESS).with_data(plot)

        if isinstance(instance, PolarMathFunction):
            instance.expression = self.process_expression(instance.expression)
            plot = render_polar_math_function(id, instance, transforms)
            return InterpreterMessage(InterpreterMessageType.SUCCESS).with_data(plot)

        elif isinstance(instance, ParametricMathFunction):
            instance.expressions = list(
                map(self.process_expression, instance.expressions)
            )
            plot = render_parametric_math_function(id, instance, transforms)
            return InterpreterMessage(InterpreterMessageType.SUCCESS).with_data(plot)

        elif isinstance(instance, Identifier):
            # Resolve the identifier and process the result
            resolved_value = self.store.get_or_throw(instance.value)
            return self.process_animation(
                Animation(instance=resolved_value, transforms=transforms),
                instance.value,
            )

        elif isinstance(instance, (VLines, SweepDot, ArcaneText)):
            return InterpreterMessage(InterpreterMessageType.SUCCESS).with_data(
                instance
            )

        else:
            raise InterpreterError(
                InterpreterErrorCode.UNSUPPORTED_STATEMENT,
                statement_type=type(instance).__name__,
            )

    def _handle_plot_block(self, block: AxisBlock | PolarBlock) -> InterpreterMessage:
        """Handle an AxisBlock or PolarBlock statement"""
        processed_animations = []

        expected_container = None
        if isinstance(block, AxisBlock):
            expected_container = "Axis"
        elif isinstance(block, PolarBlock):
            expected_container = "PolarPlane"

        for animation in block.animations:
            processed_animation = self.process_animation(animation)
            if processed_animation.data:
                if isinstance(processed_animation.data, Plot):
                    if processed_animation.data.container_type != expected_container:
                        InterpreterError(InterpreterErrorCode.UNSUPPORTED_PLOT)
                processed_animations.append(processed_animation.data)

        return InterpreterMessage(InterpreterMessageType.SUCCESS).with_data(
            (block, processed_animations)
        )

    def _add_object(self, obj, *, default_dep=None):
        """Helper to add an object with optional dependency logic"""
        dep = []
        if isinstance(obj, Plot):
            dep = [default_dep] if default_dep else []
        elif isinstance(obj, VLines):
            dep = [obj.variable]
        elif isinstance(obj, SweepDot):
            dep = [obj.variable]
        elif isinstance(obj, ArcaneText):
            if obj.position:
                dep = [obj.position.variable]

        self.scene_builder.add_object(id=obj.id, value=obj, dependencies=dep)

    def _add_plot_block_to_builder(self, block: AxisBlock | PolarBlock, animations):
        container_type = "Axis" if isinstance(block, AxisBlock) else "PolarPlane"
        self.scene_builder.add_object(id=block.id, value=PlotContainer(container_type))

        for animation in animations:
            self._add_object(animation, default_dep=block.id)

    def run(self) -> None:
        """Run the entire program"""
        for _ in range(len(self.program.statements)):
            try:
                result = self.execute_next()
                data = result.data

                if isinstance(data, Plot):
                    container_type = data.container_type
                    global_id = (
                        "global_axis" if container_type == "Axis" else "global_polar"
                    )
                    if not self.scene_builder.get(global_id):
                        self.scene_builder.add_object(
                            id=global_id,
                            value=PlotContainer(container_type),
                        )
                    self._add_object(data, default_dep=global_id)

                elif isinstance(data, (VLines, SweepDot, ArcaneText)):
                    self._add_object(data)

                elif isinstance(data, Tuple) and len(data) == 2:
                    block, animations = data
                    self._add_plot_block_to_builder(block, animations)

            except InterpreterError as e:
                print(f"Error: {e}")
                break

        # Render the final scene if there are any animation blocks
        if self.scene_builder.num_objects() != 0:
            arcane_animation = construct_scene(self.scene_builder)()
            arcane_animation.render()
        else:
            print("No animations to render")

    def __str__(self) -> str:
        """Return a string representation of the interpreter state"""
        return f"""
        Interpreter State:
        - Instruction pointer: {self.instruction_pointer}
        - Variables: {str(self.store)}
        - Total statements: {len(self.program.statements)}
        - Statements executed: {self.instruction_pointer}
        """
