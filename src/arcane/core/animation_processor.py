from typing import Any, List, Union

from arcane.core.constructs import (
    Animation,
    Identifier,
    InstanceAnimation,
    ParametricMathFunction,
    PolarMathFunction,
    RegularMathFunction,
    SweepTransform,
    VLines as VLinesToken,
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
    render_vlines_to_function,
)
from arcane.graphics.objects import Plot, VLines

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
        # Process the expressions with any stored variables
        function.expression = self.process_expression(function.expression)
        # Render the function
        return render_polar_math_function(id, function, transforms)

    def handle_regular_math_function(
        self, id: str, function: RegularMathFunction, transforms: List[Any]
    ) -> Plot:
        """Process a regular math function and return a rendered plot"""
        # Process the expressions with any stored variables
        function.expression = self.process_expression(function.expression)
        # Render the function
        return render_regular_math_function(id, function, transforms)

    def handle_parametric_math_function(
        self, id: str, function: ParametricMathFunction, transforms: List[Any]
    ) -> Plot:
        """Process a parametric math function and return a rendered plot"""
        # Process all expressions with any stored variables
        function.expressions = list(map(self.process_expression, function.expressions))
        # Render the function
        return render_parametric_math_function(id, function, transforms)

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
            raise e
            # TODO: change-back
            # raise InterpreterError(InterpreterErrorCode.ANIMATION_ERROR, details=str(e))

    def _process_identifier_animation(
        self, identifier: Identifier
    ) -> InterpreterMessage:
        """Process an animation referenced by identifier"""
        value = self.store.get_or_throw(identifier.value)
        return self.process_animation(Animation(value=value))

    def _process_instance_animation(
        self, instance_animation: InstanceAnimation, id: str = ""
    ) -> InterpreterMessage:
        """Process an instance animation"""
        instance = instance_animation.instance
        transforms = instance_animation.transforms
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
            return self._process_instance_animation(
                InstanceAnimation(instance=resolved_value, transforms=transforms),
                instance.value,
            )

        elif isinstance(instance, VLinesToken):
            assert isinstance(transforms[0], SweepTransform)
            return InterpreterMessage(InterpreterMessageType.SUCCESS).with_data(
                VLines(
                    id=id,
                    variable=instance.variable.value,
                    x_range=[transforms[0].sweep_from, transforms[0].sweep_to],
                    render=render_vlines_to_function,
                )
            )

        else:
            raise InterpreterError(
                InterpreterErrorCode.UNSUPPORTED_STATEMENT,
                statement_type=type(instance).__name__,
            )
