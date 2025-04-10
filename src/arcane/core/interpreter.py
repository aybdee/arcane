from typing import Any, Dict, List, Literal, Optional, Tuple, Union, cast
from enum import Enum
from pprint import pprint

from arcane.core.constructs import (
    Animation,
    AxisBlock,
    Definition,
    PolarBlock,
    Program,
    MathFunction,
    InstanceAnimation,
)
from arcane.graphics.objects import PlotContainer, Plot, SceneBuilder
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
            # Handle different statement types
            if isinstance(current_statement, Definition):
                return self._handle_definition(current_statement)
            elif isinstance(current_statement, Animation):
                return self._handle_animation(current_statement)
            elif isinstance(current_statement, AxisBlock):
                return self._handle_axis_block(current_statement)
            elif isinstance(current_statement, PolarBlock):
                return self._handle_polar_block(current_statement)
            else:
                # Handle unsupported statement type
                raise InterpreterError(
                    InterpreterErrorCode.UNSUPPORTED_STATEMENT,
                    statement_type=type(current_statement).__name__,
                )
        except InterpreterError:
            # Re-raise interpreter errors
            raise
        except Exception as e:
            # Wrap other exceptions in an interpreter error
            raise e
            # raise InterpreterError(InterpreterErrorCode.UNKNOWN, details=str(e))

    def _handle_definition(self, definition: Definition) -> InterpreterMessage:
        """Handle a definition statement"""
        if definition.transform and isinstance(definition.value, MathFunction):
            # Store a function with its transform
            self.store.add(
                definition.name.value,
                InstanceAnimation(
                    instance=definition.value, transforms=[definition.transform]
                ),
            )
        else:
            # Store a regular value
            self.store.add(definition.name.value, definition.value)

        return InterpreterMessage(InterpreterMessageType.SUCCESS)

    def _handle_animation(self, animation: Animation) -> InterpreterMessage:
        """Handle an animation statement"""
        # Delegate to the animation processor
        return self.animation_processor.process_animation(animation)

    def _handle_axis_block(self, axis_block: AxisBlock) -> InterpreterMessage:
        """Handle an axis block statement"""
        processed_animations = []

        # Process each animation in the axis block
        for animation in axis_block.animations:
            processed_animation = self._handle_animation(animation)  # type: ignore
            if processed_animation.data:
                if processed_animation.data.container_type != "Axis":
                    InterpreterError(InterpreterErrorCode.UNSUPPORTED_PLOT)
                processed_animations.append(processed_animation.data)

        # Return the axis block with its processed animations
        return InterpreterMessage(InterpreterMessageType.SUCCESS).with_data(
            (axis_block, processed_animations)
        )

    def _handle_polar_block(self, polar_block: PolarBlock) -> InterpreterMessage:
        """Handle an polar block statement"""
        processed_animations = []

        # Process each animation in the axis block
        for animation in polar_block.animations:
            processed_animation = self._handle_animation(animation)  # type: ignore
            if processed_animation.data:
                if processed_animation.data.container_type != "PolarPlane":
                    InterpreterError(InterpreterErrorCode.UNSUPPORTED_PLOT)
                processed_animations.append(processed_animation.data)

        # Return the axis block with its processed animations
        return InterpreterMessage(InterpreterMessageType.SUCCESS).with_data(
            (polar_block, processed_animations)
        )

    def run(self) -> None:
        """Run the entire program"""
        scene_builder = SceneBuilder()

        # Execute all statements in the program
        for _ in range(len(self.program.statements)):
            try:
                result = self.execute_next()
                # Handle the result
                if isinstance(result.data, Plot):
                    # Add plots to the global axis
                    if result.data.container_type == "Axis":
                        if not scene_builder.get("global_axis"):
                            scene_builder.add_object(
                                id="global_axis",
                                value=PlotContainer("Axis"),
                            )
                        scene_builder.add_object(
                            id=result.data.id,
                            value=result.data,
                            dependencies=["global_axis"],
                        )

                    elif result.data.container_type == "PolarPlane":
                        if not scene_builder.get("global_polar"):
                            scene_builder.add_object(
                                id="global_axis",
                                value=PlotContainer("PolarPlane"),
                            )

                        scene_builder.add_object(
                            id=result.data.id,
                            value=result.data,
                            dependencies=["global_polar"],
                        )

                elif isinstance(result.data, Tuple) and len(result.data) == 2:
                    # Create a new axis for an axis block
                    block, animations = result.data
                    if isinstance(block, AxisBlock):
                        axis_id = gen_id()
                        scene_builder.add_object(
                            id=axis_id, value=PlotContainer("Axis")
                        )
                        for animation in animations:
                            scene_builder.add_object(
                                id=animation.id, value=animation, dependencies=[axis_id]
                            )
                    elif isinstance(block, PolarBlock):
                        polar_id = gen_id()
                        scene_builder.add_object(
                            id=polar_id, value=PlotContainer("PolarPlane")
                        )
                        for animation in animations:
                            scene_builder.add_object(
                                id=animation.id,
                                value=animation,
                                dependencies=[polar_id],
                            )

            except InterpreterError as e:
                print(f"Error: {e}")
                # Optionally break execution or continue based on error severity
                break

        # Render the final scene if there are any animation blocks
        if scene_builder.num_objects() != 0:
            arcane_animation = construct_scene(scene_builder)()
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
