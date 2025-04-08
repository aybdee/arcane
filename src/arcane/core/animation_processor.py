from typing import Any, List, Union

from arcane.core.constructs import (
    Animation,
    Identifier,
    InstanceAnimation,
    ParametricMathFunction,
    PolarMathFunction,
    RegularMathFunction,
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
)
from arcane.graphics.objects import Plot

from arcane.core.store import Store


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
        self, function: PolarMathFunction, transforms: List[Any]
    ) -> Plot:
        """Process a regular math function and return a rendered plot"""
        # Process the expressions with any stored variables
        function.expression = self.process_expression(function.expression)
        # Render the function
        return render_polar_math_function(function, transforms)

    def handle_regular_math_function(
        self, function: RegularMathFunction, transforms: List[Any]
    ) -> Plot:
        """Process a regular math function and return a rendered plot"""
        # Process the expressions with any stored variables
        function.expression = self.process_expression(function.expression)
        # Render the function
        return render_regular_math_function(function, transforms)

    def handle_parametric_math_function(
        self, function: ParametricMathFunction, transforms: List[Any]
    ) -> Plot:
        """Process a parametric math function and return a rendered plot"""
        # Process all expressions with any stored variables
        function.expressions = list(map(self.process_expression, function.expressions))
        # Render the function
        return render_parametric_math_function(function, transforms)

    def process_animation(self, animation: Animation) -> InterpreterMessage:
        """Process an animation and return the result"""
        try:
            if isinstance(animation.value, InstanceAnimation):
                return self._process_instance_animation(animation.value)
            elif isinstance(animation.value, Identifier):
                return self._process_identifier_animation(animation.value)
            else:
                raise InterpreterError(
                    InterpreterErrorCode.UNSUPPORTED_STATEMENT,
                    statement_type=type(animation.value).__name__,
                )
        except InterpreterError:
            # Re-raise interpreter errors without wrapping
            raise
        except Exception as e:
            # Wrap other exceptions in an interpreter error
            raise InterpreterError(InterpreterErrorCode.ANIMATION_ERROR, details=str(e))

    def _process_identifier_animation(
        self, identifier: Identifier
    ) -> InterpreterMessage:
        """Process an animation referenced by identifier"""
        value = self.store.get_or_throw(identifier.value)
        return self.process_animation(Animation(value=value))

    def _process_instance_animation(
        self, instance_animation: InstanceAnimation
    ) -> InterpreterMessage:
        """Process an instance animation"""
        instance = instance_animation.instance
        transforms = instance_animation.transforms

        if isinstance(instance, RegularMathFunction):
            plot = self.handle_regular_math_function(instance, transforms)
            return InterpreterMessage(InterpreterMessageType.SUCCESS).with_data(plot)

        if isinstance(instance, PolarMathFunction):
            plot = self.handle_polar_math_function(instance, transforms)
            return InterpreterMessage(InterpreterMessageType.SUCCESS).with_data(plot)

        elif isinstance(instance, ParametricMathFunction):
            plot = self.handle_parametric_math_function(instance, transforms)
            return InterpreterMessage(InterpreterMessageType.SUCCESS).with_data(plot)

        elif isinstance(instance, Identifier):
            # Resolve the identifier and process the result
            resolved_value = self.store.get_or_throw(instance.value)
            return self.process_animation(
                Animation(
                    value=InstanceAnimation(
                        instance=resolved_value, transforms=transforms
                    )
                )
            )

        else:
            raise InterpreterError(
                InterpreterErrorCode.UNSUPPORTED_STATEMENT,
                statement_type=type(instance).__name__,
            )
