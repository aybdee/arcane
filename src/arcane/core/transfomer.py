from lark import Transformer
from manim.constants import PI
from sympy import sympify
from sympy.core.numbers import E, Float


from arcane.core.constructs import (
    Animation,
    Definition,
    Identifier,
    InstanceAnimation,
    MathFunction,
    ArcaneType,
    ParametricMathFunction,
    Program,
    RegularMathFunction,
    SweepTransform,
    Transform,
    AxisBlock,
)


def filter_none(func):
    def wrapper(self, items, *args, **kwargs):
        # Filter out None values
        filtered_items = [item for item in items if item is not None]
        return func(self, filtered_items, *args, **kwargs)

    return wrapper


class ArcaneTransfomer(Transformer):
    def program(self, items):
        statements = []
        for item in items:
            statements.append(item)
        return Program(statements)

    def definition(self, items):
        name = None
        value = None
        arctype = None
        transform = None
        for item in items:
            if isinstance(item, Identifier):
                name = item
            elif isinstance(item, MathFunction):
                arctype = ArcaneType.MATHFUNCTION
                value = item

            elif isinstance(item, Transform):
                transform = item

            elif isinstance(item, Float):
                value = float(item)
                arctype = ArcaneType.NUMBER
            else:
                pass

        assert name is not None
        assert value is not None
        assert arctype is not None
        return Definition(arctype, name, value, transform)

    def animate_declaration(self, items):
        items = list(filter(lambda x: x != None, items))
        if len(items) == 1:
            return Animation(value=items[0])
        else:
            return Animation(
                value=InstanceAnimation(instance=items[0], transform=items[1])
            )

    @filter_none
    def axis_declaration(self, items):
        identifier = None
        animations = []
        for item in items:
            if isinstance(item, Identifier):
                identifier = item
            else:
                animations.append(item)
        assert identifier is not None
        return AxisBlock(name=identifier, animations=animations)

    def regular_math_function(self, items):
        variables = []
        expression = ""
        for item in items:
            if isinstance(item, Identifier):
                variables.append(item)
            else:
                expression = sympify(item)
        return RegularMathFunction(variables, expression)

    def parametric_math_function(self, items):
        variables = []
        expressions = []
        for item in items:
            if isinstance(item, Identifier):
                variables.append(item)
            else:
                expressions.append(sympify(item))
        return ParametricMathFunction(variables, expressions)

    def sweep(self, items):
        return SweepTransform(items[0], items[1])

    def numerical_expression(self, items):
        return float(sympify(" ".join(items)))

    def numerical_factor(self, items):
        return " ".join(items)

    def numerical_term(self, items):
        return " ".join(items)

    def numerical_base(self, items):
        repr_string = ""
        for item in items:
            if isinstance(item, Identifier):
                repr_string += f"{item.value}"
            else:
                repr_string += f"{item}"
        return repr_string

    def algebraic_expression(self, items):
        return f'({" ".join(items)})'

    def algebraic_factor(self, items):
        return " ".join(items)

    def algebraic_term(self, items):
        return " ".join(items)

    @filter_none
    def algebraic_base(self, items):
        repr_string = ""
        for item in items:
            if isinstance(item, Identifier):
                repr_string += f"{item.value}"
            else:
                repr_string += f"{item}"
        return repr_string

    def trigonometric_function(self, items):
        return f"{items[0]}({items[1]})"

    def expression(self, items):
        if isinstance(
            items[0], str
        ):  # check if it's just a literal value(not function)
            return sympify(items[0])
        else:
            return items[0]

    def NUMBER(self, n):
        return float(n)

    def IDENT(self, n):
        return Identifier(str(n))

    def MUL(self, _):
        return "*"

    def DIV(self, _):
        return "/"

    def ADD(self, _):
        return "+"

    def SUB(self, _):
        return "-"

    def MOD(self, _):
        return "%"

    def EXP(self, _):
        return "^"

    def SIN(self, _):
        return "sin"

    def COS(self, _):
        return "cos"

    def TAN(self, _):
        return "tan"

    def PI(self, _):
        return PI

    def E(self, _):
        return E

    # process non terminal nodes

    def statement(self, items):
        return items[0]

    def start(self, items):
        return items[0]

    def math_transform(self, items):
        return items[0]

    def math_function(self, items):
        return items[0]

    def constant(self, items):
        return items[0]

    def NEWLINE(self, _):
        pass
