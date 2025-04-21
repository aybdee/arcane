from typing import Any, List, Union

from arcane.core.constructs import (
    Animation,
    Identifier,
    ParametricMathFunction,
    PolarMathFunction,
    RegularMathFunction,
    RelativePosition,
    SweepTransform,
    TextAnimation,
    SweepDot as SweepDotConstruct,
    VLines as VLinesConstruct,
)

from arcane.core.interpreter_types import (
    InterpreterError,
    InterpreterMessage,
    InterpreterMessageType,
    InterpreterErrorCode,
)
from arcane.graphics.constructor import (
    render_parametric_math_function,
    render_polar_math_function,
    render_regular_math_function,
    render_relative_text,
    render_sweep_dot,
    render_vlines_to_function,
)
from arcane.graphics.objects import ArcaneText, Plot, SweepDot, VLines

from arcane.core.store import Store
from arcane.utils import gen_id


class AnimationProcessor:
    """Handles processing of animation statements"""

    def __init__(self, store: Store):
        self.store = store

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

    def handle_polar_math_function(
        self, id: str, function: PolarMathFunction, transforms: List[Any]
    ) -> Plot:
        """Process a regular math function and return a rendered plot"""
        function.expression = self.process_expression(function.expression)
        return render_polar_math_function(id, function, transforms)

    def handle_regular_math_function(
        self, id: str, function: RegularMathFunction, transforms: List[Any]
    ) -> Plot:
        """Process a regular math function and return a rendered plot"""
        function.expression = self.process_expression(function.expression)
        return render_regular_math_function(id, function, transforms)

    def handle_parametric_math_function(
        self, id: str, function: ParametricMathFunction, transforms: List[Any]
    ) -> Plot:
        """Process a parametric math function and return a rendered plot"""
        function.expressions = list(map(self.process_expression, function.expressions))
        return render_parametric_math_function(id, function, transforms)

    def process_animation(
        self, animation: Animation, id: str = ""
    ) -> InterpreterMessage:
        """Process an instance animation"""
        instance = animation.instance
        transforms = animation.transforms
        id = id if id else gen_id()

        if isinstance(instance, RegularMathFunction):
            plot = self.handle_regular_math_function(id, instance, transforms)
            return InterpreterMessage(InterpreterMessageType.SUCCESS).with_data(plot)

        if isinstance(instance, PolarMathFunction):
            plot = self.handle_polar_math_function(id, instance, transforms)
            return InterpreterMessage(InterpreterMessageType.SUCCESS).with_data(plot)

        elif isinstance(instance, ParametricMathFunction):
            plot = self.handle_parametric_math_function(id, instance, transforms)
            return InterpreterMessage(InterpreterMessageType.SUCCESS).with_data(plot)

        elif isinstance(instance, Identifier):
            # Resolve the identifier and process the result
            resolved_value = self.store.get_or_throw(instance.value)
            return self.process_animation(
                Animation(instance=resolved_value, transforms=transforms),
                instance.value,
            )

        elif isinstance(instance, VLinesConstruct):
            assert isinstance(transforms[0], SweepTransform)
            return InterpreterMessage(InterpreterMessageType.SUCCESS).with_data(
                VLines(
                    id=id,
                    variable=instance.variable,
                    x_range=[transforms[0].sweep_from, transforms[0].sweep_to],
                    num_lines=instance.num_lines,
                    render=render_vlines_to_function,
                )
            )

        elif isinstance(instance, SweepDotConstruct):
            return InterpreterMessage(InterpreterMessageType.SUCCESS).with_data(
                SweepDot(
                    id=instance.id, variable=instance.variable, render=render_sweep_dot
                )
            )

        elif isinstance(instance, TextAnimation):
            assert instance.position
            return InterpreterMessage(InterpreterMessageType.SUCCESS).with_data(
                ArcaneText(
                    id=id,
                    relative_to=instance.position.variable.value,
                    relative_placement=instance.position.placement,
                    text=instance.value,
                    render=render_relative_text,
                )
            )

        else:
            raise InterpreterError(
                InterpreterErrorCode.UNSUPPORTED_STATEMENT,
                statement_type=type(instance).__name__,
            )
