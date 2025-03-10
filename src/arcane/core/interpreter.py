from typing import Any, Tuple
from pprint import pprint
from arcane.core.constructs import (
    Animation,
    AxisBlock,
    Definition,
    Identifier,
    InstanceAnimation,
    MathFunction,
    ParametricMathFunction,
    Program,
    RegularMathFunction,
)
from enum import Enum

from arcane.graphics.constructor import (
    render_parametric_math_function,
    render_regular_math_function,
)
from arcane.graphics.objects import Axis, Plot

from arcane.graphics.scene import construct_scene


class InterpreterErrorCode(Enum):
    NO_STATEMENTS_AVAILABLE = "No statements left to evaluate"
    UNDEFINED_VARIABLE = "Undefined variable: {variable_name}"
    UNKOWN = "Program crashed unexpectedly"


class InterpreterError(Exception):
    def __init__(self, error_code: InterpreterErrorCode, **kwargs):
        self.error_code = error_code
        self.message = error_code.value.format(**kwargs)
        super().__init__(self.message)

    def __str__(self):
        return self.message


class InterpreterMessage(Enum):
    SUCCESS = ("statement evaulated", None)

    def __new__(cls, label, data):
        obj = object.__new__(cls)
        obj._value_ = label
        obj.data = data
        return obj

    def with_data(self, data):
        self.data = data
        return self


class Store:
    def __init__(self):
        self.store = {}

    def add(self, key, value):
        self.store.update({key: value})

    def get(self, key):
        return self.store.get(key)

    def get_or_throw(self, key):
        value = self.get(key)
        if value:
            return value
        else:
            raise InterpreterError(
                InterpreterErrorCode.UNDEFINED_VARIABLE, variable_name=key
            )

    def __str__(self):
        return str(list(self.store.keys()))


class ArcaneInterpreter:
    def __init__(self, program: Program):
        self.program = program
        self.store = Store()
        self.current_axis = 0
        self.instruction_pointer = 0

    def execute_next(self) -> InterpreterMessage:
        if len(self.program.statements) - 1 < self.instruction_pointer:
            raise InterpreterError(InterpreterErrorCode.NO_STATEMENTS_AVAILABLE)

        current_statement = self.program.statements[self.instruction_pointer]
        self.instruction_pointer += 1
        if isinstance(current_statement, Definition):
            return self.handle_definition(current_statement)

        elif isinstance(current_statement, Animation):
            return self.handle_animation(current_statement)

        elif isinstance(current_statement, AxisBlock):
            return self.handle_axis_block(current_statement)

        raise InterpreterError(InterpreterErrorCode(InterpreterErrorCode.UNKOWN))

    def handle_axis_block(self, axis_block: AxisBlock):
        processed_animations = []
        for animation in axis_block.animations:
            processed_animation = self.handle_animation(animation)  # type: ignore
            processed_animations.append(processed_animation.data)

        # self.blocks.append((axis_block, processed_animations))
        # return InterpreterMessage.SUCCESS

        return InterpreterMessage.SUCCESS.with_data((axis_block, processed_animations))

    def handle_definition(self, definition: Definition):
        if definition.transform and isinstance(definition.value, MathFunction):
            self.store.add(
                definition.name.value,
                InstanceAnimation(
                    instance=definition.value, transforms=[definition.transform]
                ),
            )
        else:
            self.store.add(definition.name.value, definition.value)
        return InterpreterMessage.SUCCESS

    def animate_variable(self, id: str):
        return self.handle_animation(Animation(value=self.store.get_or_throw(id)))

    def process_expression(self, expression: Any) -> Any:
        # evalutes all the terms inside an expression that have stored identifiers
        variables = list(expression.free_symbols)
        evaluated_expr = expression
        for variable in variables:
            stored_value = self.store.get(str(variable))
            if isinstance(stored_value, float):
                evaluated_expr = evaluated_expr.subs({variable: stored_value})
        return evaluated_expr

    def handle_animation(self, animation: Animation):
        if isinstance(animation.value, InstanceAnimation):
            if isinstance(animation.value.instance, MathFunction):
                if isinstance(animation.value.instance, RegularMathFunction):
                    animation.value.instance.expression = self.process_expression(
                        animation.value.instance.expression
                    )
                    return InterpreterMessage.SUCCESS.with_data(
                        render_regular_math_function(
                            animation.value.instance, animation.value.transforms
                        )
                    )

                elif isinstance(animation.value.instance, ParametricMathFunction):
                    animation.value.instance.expressions = list(
                        map(
                            self.process_expression,
                            animation.value.instance.expressions,
                        )
                    )
                    return InterpreterMessage.SUCCESS.with_data(
                        render_parametric_math_function(
                            animation.value.instance, animation.value.transforms
                        )
                    )
            else:
                value = self.store.get_or_throw(animation.value.instance.value)
                return self.handle_animation(
                    Animation(
                        value=InstanceAnimation(
                            instance=value, transforms=animation.value.transforms
                        )
                    )
                )
        elif isinstance(animation.value, Identifier):
            return self.animate_variable(animation.value.value)
        return InterpreterMessage.SUCCESS

    def run(self):
        animation_blocks = []
        global_axis = None
        objects = []
        for _ in range(len(self.program.statements)):
            result = self.execute_next()
            if isinstance(result, InterpreterMessage):
                if isinstance(result.data, Plot):
                    if not global_axis:
                        global_axis = Axis()

                    global_axis.add(result.data)
                elif isinstance(result.data, Tuple):
                    axis = Axis()
                    for animation in result.data[1]:
                        axis.add(animation)
                    animation_blocks.append(axis)

            else:
                raise Exception("an exception occured")

        if global_axis:
            animation_blocks.append(global_axis)

        arcane_animation = construct_scene(animation_blocks)()
        arcane_animation.render()

    def __str__(self):
        return f"""
        instruction_pointer: {self.instruction_pointer}
        variables: {str(self.store)}
        """
