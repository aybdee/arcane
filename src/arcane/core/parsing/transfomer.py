from typing import Dict
from lark import Transformer
from manim.constants import PI
from sympy import sympify
from sympy.core.numbers import E, Float
from arcane.utils import gen_id


from arcane.core.models.constructs import (
    Animatable,
    Animation,
    ArcanePoint,
    CoordinateAngleLength,
    Definition,
    Identifier,
    ArcaneLine,
    MathFunction,
    ObjectTransformExpression,
    ParametricMathFunction,
    PolarBlock,
    PolarMathFunction,
    SweepCoordinates,
    SweepDot,
    Program,
    RegularMathFunction,
    RelativePosition,
    RelativePositionPlacement,
    SweepObjects,
    SweepTransform,
    AxisBlock,
    ArcaneText,
    VLines,
    ThreePoint,
    ArcaneElbow,
    PointLength,
    ArcaneSquare,
    ArcaneRectangle,
    RectangleDefinition,
    RegularPolygonDefinition,
    ArcaneRegularPolygon,
    PolygonDefinition,
    ArcanePolygon,
)


def filter_none(func):
    def wrapper(self, items, *args, **kwargs):
        # Filter out None values
        filtered_items = [item for item in items if item is not None]
        return func(self, filtered_items, *args, **kwargs)

    return wrapper


def flatten(lst):
    for item in lst:
        if isinstance(item, list):
            yield from flatten(item)
        else:
            yield item


def safe_get(lst, index, default=None):
    return lst[index] if 0 <= index < len(lst) else default


class ArcaneTransfomer(Transformer):
    def program(self, items):
        statements = list(flatten(items))
        return Program(statements)

    def definition(self, items):
        name = None
        value = None
        for item in items:
            if isinstance(item, Identifier):
                name = item
            elif isinstance(item, MathFunction):
                assert name is not None
                # replace generated ID with variable name
                item.id = name.value
                value = item
            elif isinstance(
                item,
                (
                    ArcaneLine,
                    ArcanePoint,
                    ArcaneElbow,
                    ArcaneSquare,
                    ArcaneRectangle,
                    ArcaneRegularPolygon,
                    ArcanePolygon,
                ),
            ):
                assert name is not None
                # replace generated ID with variable name
                item.id = name.value
                value = item

            elif isinstance(item, Float):
                value = float(item)
            else:
                pass

        assert name is not None
        assert value is not None
        return Definition(name, value)

    def animate_declaration(self, items):
        items = list(filter(lambda x: x != None, items))
        animations = []
        instance_index = 0
        for index, item in enumerate(items):
            if isinstance(item, Animatable) and index != 0:
                animations.append(
                    (items[instance_index], items[instance_index + 1 : index])
                )
                instance_index = index

            if index == len(items) - 1:
                animations.append((items[instance_index], items[instance_index + 1 :]))

            if isinstance(item, SweepDot) and not item.variable:
                item.variable = animations[0][0].id

        return list(
            map(lambda x: Animation(instance=x[0], transforms=x[1]), animations)
        )

    def sweep_dot(self, _):
        return SweepDot(id=gen_id(), variable="")

    def vertical_line_declaration(self, items):
        return VLines(gen_id(), variable=items[1].id, num_lines=items[0])

    def line_declaration(self, items):
        return ArcaneLine(id=gen_id(), definition=items[0])

    def write_declaration(self, items):
        # TODO:(dont use positions to extract items)
        position = list(
            filter(lambda x: isinstance(x, RelativePositionPlacement), items)
        )
        is_latex = items[0].startswith("latex")
        return ArcaneText(
            id=gen_id(),
            value=items[0] if not is_latex else items[0].replace("latex", ""),
            position=(
                RelativePosition(variable=items[2].id, placement=position[0])
                if position
                else None
            ),
            options=items[-1] if isinstance(items[-1], Dict) else {},
            is_latex=is_latex,
        )

    def font_option(self, items):
        options = {}
        for i in range(0, len(items), 2):
            options.update({items[i]: items[i + 1]})
        return options

    def show_declaration(self, items):
        return items[0]

    @filter_none
    def polar_declaration(self, items):
        identifier = None
        animations = []
        for item in items:
            if isinstance(item, Identifier):
                identifier = item
            else:
                animations.append(item)
        assert identifier is not None
        return PolarBlock(id=identifier.id, animations=list(flatten(animations)))

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
        return AxisBlock(id=identifier.id, animations=list(flatten(animations)))

    def regular_math_function(self, items):
        variables = []
        expression = ""
        for item in items:
            if isinstance(item, Identifier):
                variables.append(item.value)
            else:
                expression = sympify(item)
        return RegularMathFunction(gen_id(), variables, expression)

    def parametric_math_function(self, items):
        variables = []
        expressions = []
        for item in items:
            if isinstance(item, Identifier):
                variables.append(item.value)
            else:
                expressions.append(sympify(item))
        return ParametricMathFunction(gen_id(), variables, expressions)

    def polar_math_function(self, items):
        variables = []
        expression = ""
        for item in items:
            if isinstance(item, Identifier):
                variables.append(item.value)
            else:
                expression = sympify(item)
        return PolarMathFunction(gen_id(), variables, expression)

    def sweep(self, items):
        return SweepTransform(items[0], items[1])

    def sweep_coordinates(self, items):
        return SweepCoordinates(
            sweep_from=(items[0], items[1]), sweep_to=(items[2], items[3])
        )

    def transform_declaration(self, items):
        return ObjectTransformExpression(object_from=items[0], object_to=items[1])

    def ident_sweep(self, items):
        return SweepObjects(sweep_from=items[0].id, sweep_to=items[1].id)

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

    def point_declaration(self, items):
        return ArcanePoint(id=gen_id(), position=(items[0], items[1]))

    def three_point_angle(self, items):
        return ThreePoint(
            vertex=(items[0], items[1]),
            point1=(items[2], items[3]),
            point2=(items[4], items[5]),
        )

    def angle_declaration(self, items):
        return ArcaneElbow(id=gen_id(), definition=items[0])

    def coordinate_angle_length(self, items):
        return CoordinateAngleLength(
            sweep_from=(items[0], items[1]), angle=items[2], length=items[3]
        )

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
        return float(E)

    # process non terminal nodes

    def statement(self, items):
        return items[0]

    def start(self, items):
        return items[0]

    def math_transform(self, items):
        return items[0]

    def math_function(self, items):
        return items[0]

    @filter_none
    def constant(self, items):
        return float("".join(map(str, items)))

    def font_option_value(self, items):
        return items[0]

    def write_value(self, items):
        return items[0]

    def latex(self, items):
        return "latex" + items[0]

    def FONT_OPTION_KEY(self, items):
        return str(items)

    def STRING(self, items):
        return str(items)[1:-1]

    def RELATIVE_POSITION(self, items):
        value = str(items)
        if value == "below":
            return RelativePositionPlacement.BELOW
        elif value == "above":
            return RelativePositionPlacement.ABOVE
        elif value == "left of":
            return RelativePositionPlacement.LEFT
        else:
            return RelativePositionPlacement.RIGHT

    def NEWLINE(self, _):
        pass

    def point_length(self, items):
        return PointLength(point=(items[0], items[1]), length=items[2])

    def square_declaration(self, items):
        return ArcaneSquare(id=gen_id(), definition=items[0])

    def rectangle_declaration(self, items):
        return ArcaneRectangle(
            id=gen_id(),
            definition=RectangleDefinition(
                width=float(items[0]),
                height=float(items[1]),
                point=(float(items[2]), float(items[3])),
            ),
        )

    def regular_polygon_declaration(self, items):
        return ArcaneRegularPolygon(
            id=gen_id(),
            definition=RegularPolygonDefinition(
                radius=float(items[0]),
                num_sides=int(items[1]),
                point=(float(items[2]), float(items[3])),
            ),
        )

    def point_list(self, items):
        points = []
        for i in range(0, len(items), 2):
            points.append((float(items[i]), float(items[i + 1])))
        return points

    def polygon_declaration(self, items):
        return ArcanePolygon(id=gen_id(), definition=PolygonDefinition(points=items[0]))
