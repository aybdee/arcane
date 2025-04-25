from typing import Any, Dict, List, Literal, Optional, Tuple, Union, cast
from enum import Enum
from pprint import pprint

from arcane.core.constructs import (
    Animation,
    AxisBlock,
    Definition,
    PolarBlock,
    Program,
)
from arcane.graphics.objects import (
    ArcaneText,
    PlotContainer,
    Plot,
    SceneBuilder,
    SweepDot,
    VLines,
)
from arcane.graphics.scene import construct_scene

from arcane.core.interpreter_types import (
    InterpreterMessage,
    InterpreterMessageType,
    InterpreterError,
    InterpreterErrorCode,
)
from arcane.core.store import Store
from arcane.core.animation_processor import AnimationProcessor
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
        self.animation_processor = AnimationProcessor(self.store)
        self.instruction_pointer = 0

        # Results tracking
        self.animation_blocks: List[PlotContainer] = []
        self.global_container: Optional[Dict] = None

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
                return self.animation_processor.process_animation(current_statement)
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

    def _handle_plot_block(self, block: AxisBlock | PolarBlock) -> InterpreterMessage:
        """Handle an AxisBlock or PolarBlock statement"""
        processed_animations = []

        expected_container = None
        if isinstance(block, AxisBlock):
            expected_container = "Axis"
        elif isinstance(block, PolarBlock):
            expected_container = "PolarPlane"

        for animation in block.animations:
            processed_animation = self.animation_processor.process_animation(animation)
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
            dep = [obj.relative_to]

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
