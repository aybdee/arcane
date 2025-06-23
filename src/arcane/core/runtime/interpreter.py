import copy
from enum import Enum
from pprint import pprint
from typing import Any, Dict, List, Literal, Optional, Tuple, Union, cast

import numpy as np
import sympy

from arcane.core.models.constructs import (Animatable, Animation, ArcaneBrace,
                                           ArcaneCharge, ArcaneClearObject,
                                           ArcaneLine, ArcaneMove,
                                           ArcaneMoveAlong, ArcaneRotate,
                                           ArcaneScale, ArcaneText, AxisBlock,
                                           Definition, DirectAnimatable,
                                           ElectricFieldBlock, Identifier,
                                           MathFunction, ObjectTransform,
                                           ObjectTransformExpression,
                                           ParametricMathFunction, PolarBlock,
                                           PolarMathFunction, Program,
                                           PropagateRays, RegularMathFunction,
                                           SweepDot, SweepObjects,
                                           SweepTransform, VLines)
from arcane.core.runtime.store import Store
from arcane.core.runtime.types import (InterpreterError, InterpreterErrorCode,
                                       InterpreterMessage,
                                       InterpreterMessageType)
from arcane.graphics.builder import SceneBuilder
from arcane.graphics.objects import PlotContainer
from arcane.graphics.scene import construct_scene
from arcane.graphics.utils.math import (avoid_zero, compute_function_range,
                                        generate_math_function)
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

    def evaluate_algebraic_expression(self, expression: sympy.Basic) -> Any:
        """Evaluates all the terms inside an algebraic expression from stored identifiers"""
        variables = list(expression.free_symbols)
        evaluated_expr = expression

        for variable in variables:
            var_name = str(variable)
            stored_value = self.store.get(var_name)
            if isinstance(stored_value, (int, float)):
                evaluated_expr = evaluated_expr.subs({variable: stored_value})

        return evaluated_expr

    def evaluate_expression(self, expression: Any) -> Any:
        """Evaluates all the terms inside an arcane expression"""
        # Handle parametric functions (list of expressions) separately
        if isinstance(expression, List):
            # Create new expressions by substituting stored values
            new_expressions = []
            for expr in expression:
                if isinstance(expr, (sympy.core.add.Add, sympy.core.mul.Mul)):
                    evaluated_expr = self.evaluate_algebraic_expression(expr)
                    variables = list(evaluated_expr.free_symbols)
                    stored_values = {}
                    for variable in variables:
                        var_name = str(variable)
                        stored_value = self.store.get(var_name)
                        if stored_value:
                            stored_values.update({var_name: stored_value})

                    if stored_values:
                        # For parametric functions, all components must be parametric
                        stored_types = list(set(map(type, stored_values.values())))
                        if not all(
                            isinstance(val, ParametricMathFunction)
                            for val in stored_values.values()
                        ):
                            raise InterpreterError(
                                InterpreterErrorCode.UNSUPPORTED_EXPRESSION,
                                expression=str(expression),
                                error="all components must be parametric functions",
                            )

                        # Substitute each component
                        substituted_expr = evaluated_expr
                        for var_name, value in stored_values.items():
                            if len(value.expressions) != len(expression):
                                raise InterpreterError(
                                    InterpreterErrorCode.UNSUPPORTED_EXPRESSION,
                                    expression=str(expression),
                                    error="parametric functions must have same number of components",
                                )
                            idx = len(new_expressions)
                            substituted_expr = substituted_expr.subs(
                                var_name,
                                value.expressions[idx],
                            )
                        new_expressions.append(substituted_expr)
                    else:
                        new_expressions.append(evaluated_expr)
                else:
                    new_expressions.append(expr)

            return ParametricMathFunction(
                id=gen_id(),
                variables=list(map(str, new_expressions[0].free_symbols)),
                expressions=new_expressions,
            )

        # Handle single expressions
        if isinstance(expression, sympy.core.symbol.Symbol):
            return self.store.get_or_throw(str(expression))

        if isinstance(expression, (sympy.core.add.Add, sympy.core.mul.Mul)):
            expression = self.evaluate_algebraic_expression(expression)
            variables = list(expression.free_symbols)
            stored_values = {}
            for variable in variables:
                var_name = str(variable)
                stored_value = self.store.get(var_name)
                if stored_value:
                    stored_values.update({var_name: stored_value})

            if stored_values:
                stored_types = list(set(map(type, stored_values.values())))
                if len(stored_types) != 1:
                    raise InterpreterError(
                        InterpreterErrorCode.UNSUPPORTED_EXPRESSION,
                        expression=str(expression),
                        error=f"cannot combine values of type {stored_types[0].__name__} and {stored_types[1].__name__}",
                    )

                reference_value = list(stored_values.values())[0]
                if isinstance(
                    reference_value, (RegularMathFunction, PolarMathFunction)
                ):
                    for var_name in stored_values.keys():
                        expression = expression.subs(
                            var_name, stored_values[var_name].expression
                        )

                    if isinstance(reference_value, RegularMathFunction):
                        return RegularMathFunction(
                            id=gen_id(),
                            variables=list(map(str, expression.free_symbols)),
                            expression=expression,
                        )
                    else:  # PolarMathFunction
                        return PolarMathFunction(
                            id=gen_id(),
                            variables=list(map(str, expression.free_symbols)),
                            expression=expression,
                        )

        raise InterpreterError(
            InterpreterErrorCode.UNSUPPORTED_EXPRESSION,
            expression=str(expression),
            error=f"cannot evaluate expression {expression}",
        )

    def execute_next(self) -> Optional[InterpreterMessage]:
        """Execute the next statement in the program"""
        # Check if there are any statements left
        if self.instruction_pointer >= len(self.program.statements):
            return None

        # Get the current statement and increment the instruction pointer
        current_statement = self.program.statements[self.instruction_pointer].value
        statement_index = self.program.statements[self.instruction_pointer].index
        self.instruction_pointer += 1

        try:
            if isinstance(current_statement, Definition):
                self.store.add(current_statement.name.value, current_statement.value)
                return InterpreterMessage(InterpreterMessageType.SUCCESS)
            elif isinstance(current_statement, Animation):
                return self.process_animation(current_statement, statement_index)
            elif isinstance(
                current_statement, (AxisBlock, PolarBlock, ElectricFieldBlock)
            ):
                values = self._handle_block(current_statement, statement_index)
                self.instruction_pointer += len(current_statement.statements)
                return values

            elif isinstance(current_statement, ArcaneClearObject):
                # check if the object iss in the scene builder
                if self.scene_builder.get(current_statement.variable.id):
                    self.scene_builder.add_object(
                        id=current_statement.id,
                        value=current_statement,
                        statement_index=statement_index,
                        dependencies=[current_statement.variable.id],
                    )
                    return InterpreterMessage(InterpreterMessageType.SUCCESS)
                else:
                    raise InterpreterError(
                        InterpreterErrorCode.NOT_ANIMATED_CANNOT_CLEAR,
                        variable_name=current_statement.id,
                    )

            else:
                # Handle unsupported statement type
                raise InterpreterError(
                    InterpreterErrorCode.UNSUPPORTED_STATEMENT,
                    statement_type=type(current_statement).__name__,
                )
        except InterpreterError as e:
            raise e
            # raise InterpreterError(InterpreterErrorCode.UNKNOWN, details=str(e)) #TODO:(uncomment)

    def process_animation(
        self, animation: Animation, statement_index: int, id: str = ""
    ) -> InterpreterMessage:
        """Process an instance animation"""
        instance = animation.instance
        transforms = animation.transforms
        id = id if id else gen_id()

        if isinstance(instance, (RegularMathFunction, PolarMathFunction)):
            instance.expression = self.evaluate_algebraic_expression(
                instance.expression
            )
            assert isinstance(transforms[0], SweepTransform)
            instance.x_range = (
                avoid_zero(transforms[0].sweep_from),
                avoid_zero(transforms[0].sweep_to),
            )
            instance.math_function = generate_math_function(instance)
            instance.y_range = compute_function_range(
                instance.math_function, instance.x_range
            )
            return InterpreterMessage(InterpreterMessageType.SUCCESS).with_data(
                (statement_index, instance)
            )

        elif isinstance(instance, ParametricMathFunction):
            instance.expressions = list(
                map(self.evaluate_algebraic_expression, instance.expressions)
            )
            assert isinstance(transforms[0], SweepTransform)
            instance.t_range = (
                avoid_zero(transforms[0].sweep_from),
                avoid_zero(transforms[0].sweep_to),
            )
            instance.math_function = generate_math_function(instance)

            # For parametric functions, we need to compute x and y ranges separately
            x_function = lambda t: instance.expressions[0].subs(
                instance.variables[0], t
            )
            y_function = lambda t: instance.expressions[1].subs(
                instance.variables[0], t
            )
            instance.x_range = compute_function_range(x_function, instance.t_range)
            instance.y_range = compute_function_range(y_function, instance.t_range)

            return InterpreterMessage(InterpreterMessageType.SUCCESS).with_data(
                (statement_index, instance)
            )

        elif isinstance(instance, Identifier):
            # Resolve the identifier and process the result
            resolved_value = self.store.get_or_throw(instance.value)
            return self.process_animation(
                Animation(instance=resolved_value, transforms=transforms),
                statement_index,
                instance.value,
            )

        elif isinstance(instance, ObjectTransformExpression):
            objects = []
            for obj in (instance.object_from, instance.object_to):
                if isinstance(obj, (sympy.Symbol, sympy.Add, sympy.Mul)):
                    evaluate_expr = self.evaluate_expression(obj)
                    objects.append(evaluate_expr)
                elif isinstance(obj, Animatable):
                    objects.append(obj)
                else:
                    raise InterpreterError(
                        InterpreterErrorCode.UNSUPPORTED_STATEMENT,
                        statement_type=type(obj).__name__,
                    )

            object_from, object_to = objects

            # update store with new expression
            if self.store.get(str(instance.object_from)):
                variable_from = str(instance.object_from)
                value_from = copy.deepcopy(self.store.get(variable_from))
                if isinstance(value_from, (PolarMathFunction, RegularMathFunction)):
                    value_from.expression = object_to.expression
                elif isinstance(value_from, ParametricMathFunction):
                    value_from.expressions = object_to.expressions
                else:
                    # just set the objects directly
                    value_from = object_to

                # update the store with new definitions
                self.store.add(variable_from, value_from)

            return self.process_animation(
                Animation(
                    instance=ObjectTransform(
                        id=gen_id(),
                        object_from=object_from,
                        object_to=object_to,
                    ),
                    transforms=transforms,
                ),
                statement_index,
            )

        elif isinstance(instance, (DirectAnimatable, ArcaneCharge)):
            return InterpreterMessage(InterpreterMessageType.SUCCESS).with_data(
                (statement_index, instance)
            )

        else:
            raise InterpreterError(
                InterpreterErrorCode.UNSUPPORTED_STATEMENT,
                statement_type=type(instance).__name__,
            )

    def get_statement_by_index(self, index: int) -> Any:
        """Get a statement by its index"""
        if index < 0 or index >= len(self.program.statements):
            raise IndexError("Statement index out of range")
        for statement in self.program.statements:
            if statement.index == index:
                return statement.value

    def _handle_block(
        self, block: AxisBlock | PolarBlock | ElectricFieldBlock, statement_index: int
    ) -> InterpreterMessage:
        """Handle an AxisBlock or PolarBlock statement"""
        processed_animations = []

        for index in block.statements:
            current_statement = self.program.statements[index].value
            if not isinstance(current_statement, Animation):
                raise InterpreterError(
                    InterpreterErrorCode.ONLY_TYPE_ALLOWED_BLOCK,
                    allowed_type="Animation",
                    gotten_type=type(current_statement).__name__,
                )

            processed_animation = self.process_animation(current_statement, index)
            if processed_animation.data:
                if isinstance(block, (AxisBlock, PolarBlock)):
                    expected_container = None
                    if isinstance(block, AxisBlock):
                        expected_container = "Axis"
                    elif isinstance(block, PolarBlock):
                        expected_container = "PolarPlane"
                    index, container_type = processed_animation.data
                    if container_type != expected_container:
                        InterpreterError(InterpreterErrorCode.UNSUPPORTED_PLOT)

                processed_animations.append(processed_animation.data)

        return InterpreterMessage(InterpreterMessageType.SUCCESS).with_data(
            (statement_index, (block, processed_animations))
        )

    def _add_object(self, obj, statement_index: int, *, default_dep=None):
        """Helper to add an object with optional dependency logic"""
        dep = []
        if isinstance(
            obj, (RegularMathFunction, ParametricMathFunction, PolarMathFunction)
        ):
            dep = [default_dep] if default_dep else []
        elif isinstance(obj, VLines):
            dep = [obj.variable]
        elif isinstance(obj, SweepDot):
            dep = [obj.variable.value]
        elif isinstance(obj, ObjectTransform):
            if not isinstance(
                obj.object_from, MathFunction
            ) and not self.scene_builder.get(obj.object_from.id):
                self.scene_builder.add_object(
                    id=obj.object_from.id,
                    statement_index=statement_index,
                    value=obj.object_from,
                )
                dep.append(obj.object_from.id)
            else:
                dep.append(obj.object_from.id)

            if not isinstance(obj.object_to, MathFunction):
                self.scene_builder.add_object(
                    id=obj.object_to.id,
                    statement_index=statement_index,
                    value=obj.object_to,
                    is_background=True,
                )
                dep.append(obj.object_to.id)

        elif isinstance(obj, ArcaneLine):
            if isinstance(obj.definition, SweepObjects):
                dep = [
                    obj.definition.sweep_from.id,  # type:ignore
                    obj.definition.sweep_to.id,  # type:ignore
                ]  # type:ignore
                for point_id in dep:
                    if not self.scene_builder.get(point_id):
                        point = self.store.get_or_throw(point_id)
                        self.scene_builder.add_object(
                            id=point_id.value,
                            value=point,
                            statement_index=statement_index,
                        )

        elif isinstance(obj, ArcaneMoveAlong):
            dep = [obj.variable_to_move.id, obj.variable_along.id]

        elif isinstance(obj, (ArcaneScale, ArcaneRotate, ArcaneBrace)):
            dep = [obj.variable.id]

        elif isinstance(obj, PropagateRays):
            if not self.scene_builder.get(obj.id):
                ray_definition = self.store.get_or_throw(obj.id)
                self.scene_builder.add_object(
                    id=obj.id, value=ray_definition, statement_index=statement_index
                )

            obj.id = f"propagate-{obj.id}"
            dep = [*map(lambda x: x.id, obj.lenses)]

        self.scene_builder.add_object(
            id=obj.id, value=obj, dependencies=dep, statement_index=statement_index
        )

    def _add_plot_block_to_builder(
        self, statement_index: int, block: AxisBlock | PolarBlock, animations
    ):
        container_type = "Axis" if isinstance(block, AxisBlock) else "PolarPlane"
        self.scene_builder.add_object(
            id=block.id,
            statement_index=statement_index,
            value=PlotContainer(container_type),
        )

        for animation in animations:
            index, value = animation
            self._add_object(value, index, default_dep=block.id)

    def run(self) -> None:
        """Run the entire program"""
        while True:
            try:
                result = self.execute_next()
                if not result:
                    break
                if result.data:
                    index, data = result.data

                    if isinstance(data, MathFunction):
                        container_type = data.container_type
                        global_id = (
                            "global_axis"
                            if container_type == "Axis"
                            else "global_polar"
                        )
                        if not self.scene_builder.get(global_id):
                            self.scene_builder.add_object(
                                id=global_id,
                                statement_index=index,
                                value=PlotContainer(container_type),
                            )
                        self._add_object(data, index, default_dep=global_id)

                    elif isinstance(data, ArcaneCharge):
                        if not self.scene_builder.get("global_electric_field"):
                            self.scene_builder.add_object(
                                id="global_electric_field",
                                statement_index=index,
                                value=ElectricFieldBlock(
                                    id=gen_id(), statements=[], _statements=[]
                                ),
                            )
                        self._add_object(data, index)
                        self.scene_builder.add_dependency(
                            "global_electric_field", data.id
                        )

                    elif isinstance(
                        data,
                        DirectAnimatable,
                    ):
                        self._add_object(data, index)

                    elif isinstance(data, Tuple) and len(data) == 2:
                        block, animations = data
                        dependencies = []
                        if isinstance(block, ElectricFieldBlock):
                            for animation in animations:
                                index, data = animation
                                self._add_object(data, index)
                                dependencies.append(data.id)

                            self.scene_builder.add_object(
                                id=block.id,
                                value=block,
                                statement_index=index,
                                dependencies=dependencies,
                            )
                        else:
                            self._add_plot_block_to_builder(index, block, animations)

            except InterpreterError as e:
                raise e

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
