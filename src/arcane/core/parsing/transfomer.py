from typing import Dict, List

from lark import Transformer
from manim.constants import PI
from sympy import sympify
from sympy.core.numbers import E, Float

from arcane.core.models.constructs import (Animatable, Animation, ArcaneArrow,
                                           ArcaneBrace, ArcaneCharge,
                                           ArcaneCircle, ArcaneClearObject,
                                           ArcaneElbow, ArcaneLens, ArcaneLine,
                                           ArcaneMove, ArcaneMoveAlong,
                                           ArcanePoint, ArcanePolygon,
                                           ArcaneRays, ArcaneRectangle,
                                           ArcaneRegularPolygon, ArcaneRotate,
                                           ArcaneScale, ArcaneSquare,
                                           ArcaneText, AxisBlock,
                                           CircleDefinition,
                                           CoordinateAngleLength, Definition,
                                           Direction, ElectricFieldBlock,
                                           Identifier, MathFunction,
                                           ObjectTransformExpression,
                                           ParametricMathFunction, PolarBlock,
                                           PolarMathFunction,
                                           PolygonDefinition, PositionLength,
                                           Program, PropagateRays,
                                           RectangleDefinition,
                                           RegularMathFunction,
                                           RegularPolygonDefinition,
                                           RelativeAnglePosition,
                                           RelativeDirectionPosition,
                                           RelativePositionPlacement,
                                           Statement, StyleProperties,
                                           SweepCoordinates, SweepDot,
                                           SweepObjects, SweepTransform,
                                           ThreePoint, VLines)
from arcane.utils import gen_id


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
    @filter_none
    def program(self, items):
        statement_pieces = list(flatten(items))
        statements = []
        statement_index = 0
        for current_statement in statement_pieces:
            if isinstance(
                current_statement, (AxisBlock, PolarBlock, ElectricFieldBlock)
            ):
                statement_indices = []
                block_index = statement_index
                for statement in current_statement._statements:
                    statement_index += 1
                    statements.append(Statement(index=statement_index, value=statement))
                    statement_indices.append(statement_index)
                current_statement.statements = statement_indices
                current_statement._statements = []
                statements.append(Statement(index=block_index, value=current_statement))

            else:
                statements.append(
                    Statement(index=statement_index, value=current_statement)
                )

            statement_index += 1
        statements.sort(key=lambda x: x.index)
        return Program(
            statements=statements,
        )

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
                    ArcaneCircle,
                    ArcaneArrow,
                    ArcaneLens,
                    ArcaneRays,
                    ArcaneCharge,
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

    def clear_declaration(self, items):
        return ArcaneClearObject(id=gen_id(), variable=items[0])

    def animate_declaration(self, items):
        items = items[0]  # unwrap from animatable
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

            if isinstance(item, SweepDot) and not item.variable.value:
                item.variable = Identifier(animations[0][0].id)

        return list(
            map(lambda x: Animation(instance=x[0], transforms=x[1]), animations)
        )

    def sweep_dot(self, _):
        return SweepDot(id=gen_id(), variable=Identifier())

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
            position=items[1],
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
    def electric_field_declaration(self, items):
        identifier = None
        animations = []
        for item in items:
            if isinstance(item, Identifier):
                identifier = item
            else:
                animations.append(item)
        assert identifier is not None

        return ElectricFieldBlock(id=gen_id(), _statements=list(flatten(animations)))

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
        return PolarBlock(id=identifier.id, _statements=list(flatten(animations)))

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
        return AxisBlock(id=identifier.id, _statements=list(flatten(animations)))

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
        items = list(flatten(items))
        return ObjectTransformExpression(object_from=items[0], object_to=items[1])

    def ident_sweep(self, items):
        return SweepObjects(sweep_from=items[0], sweep_to=items[1])

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

    def parametric_expression(self, items):
        return list(items)

    def algebraic_expression(self, items):
        return f'({" ".join(items)})'

    def algebraic_factor(self, items):
        return " ".join(items)

    def algebraic_term(self, items):
        return " ".join(items)

    def arrow_declaration(self, items):
        style = next(
            (item for item in items if isinstance(item, StyleProperties)), None
        )
        return ArcaneArrow(id=gen_id(), definition=items[0], style=style)

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
        return ArcanePoint(id=gen_id(), position=items[0])

    def three_point_angle(self, items):
        return ThreePoint(
            position=items[0],
            point1=(items[1], items[2]),
            point2=(items[3], items[4]),
        )

    def angle_declaration(self, items):
        return ArcaneElbow(id=gen_id(), definition=items[0])

    def coordinate_angle_length(self, items):
        return CoordinateAngleLength(
            sweep_from=(items[0], items[1]), angle=items[2], length=items[3]
        )

    def absolute_coordinate_position(self, items):
        return tuple(items)

    def expression(self, items):
        if isinstance(
            items[0], str
        ):  # check if it's just a literal value(not function)
            return sympify(items[0])
        elif isinstance(items[0], List):
            return list(map(sympify, items[0]))
        else:
            return items[0]

    def COMMENT(self, items):
        pass

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

    def ATAN(self, _):
        return "atan"

    def PI(self, _):
        return PI

    def E(self, _):
        return float(E)

    # process non terminal nodes

    @filter_none
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

    def RELATIVE_POSITION_DIRECTION(self, items):
        value = str(items)
        if value == "below":
            return RelativePositionPlacement.BELOW
        elif value == "above":
            return RelativePositionPlacement.ABOVE
        elif value == "left of":
            return RelativePositionPlacement.LEFT
        elif value == "center of":
            return RelativePositionPlacement.CENTER
        else:
            return RelativePositionPlacement.RIGHT

    def NEWLINE(self, _):
        pass

    def position_length(self, items):
        return PositionLength(position=items[1], length=items[0])

    def square_declaration(self, items):
        style = next(
            (item for item in items if isinstance(item, StyleProperties)), None
        )
        return ArcaneSquare(id=gen_id(), definition=items[0], style=style)

    def rectangle_declaration(self, items):
        style = next(
            (item for item in items if isinstance(item, StyleProperties)), None
        )
        return ArcaneRectangle(
            id=gen_id(),
            definition=RectangleDefinition(
                width=float(items[0]),
                height=float(items[1]),
                position=items[2],
            ),
            style=style,
        )

    def regular_polygon_declaration(self, items):
        style = next(
            (item for item in items if isinstance(item, StyleProperties)), None
        )
        return ArcaneRegularPolygon(
            id=gen_id(),
            definition=RegularPolygonDefinition(
                radius=float(items[0]), num_sides=int(items[1]), position=items[2]
            ),
            style=style,
        )

    def position(self, items):
        return items[0]

    def relative_direction_position(self, items):
        return RelativeDirectionPosition(placement=items[0], variable=items[1])

    def point_list(self, items):
        points = []
        for i in range(0, len(items), 2):
            points.append((float(items[i]), float(items[i + 1])))
        return points

    def polygon_declaration(self, items):
        style = next(
            (item for item in items if isinstance(item, StyleProperties)), None
        )
        return ArcanePolygon(
            id=gen_id(),
            definition=PolygonDefinition(points=items[0]),
            style=style,
        )

    def relative_angle_position(self, items):
        return RelativeAnglePosition(variable=items[0], angle=float(items[1]))

    def lens_declaration(self, items):
        style = next(
            (item for item in items if isinstance(item, StyleProperties)), None
        )
        return ArcaneLens(
            id=gen_id(),
            focal_length=int(items[0]),
            thickness=int(items[1]),
            position=items[2],
            style=style,
        )

    def DIRECTION(self, items):
        return Direction(items)

    def propagate_rays(self, items):
        return PropagateRays(id=items[0].value, lenses=items[1:])

    def ray_declaration(self, items):
        return ArcaneRays(
            id=gen_id(),
            definition=items[0],
            direction=items[1],
            count=int(items[2]),
            style=next(
                (item for item in items if isinstance(item, StyleProperties)), None
            ),
        )

    def circle_declaration(self, items):
        style = next(
            (item for item in items if isinstance(item, StyleProperties)), None
        )
        return ArcaneCircle(
            id=gen_id(),
            definition=CircleDefinition(radius=float(items[0]), position=items[1]),
            style=style,
        )

    def animatable(self, items):
        return items

    def charge_declaration(self, items):
        return ArcaneCharge(id=gen_id(), position=items[1], magnitude=items[0])

    def move_declaration(self, items):
        return ArcaneMove(id=gen_id(), variable=items[0], position_to=items[1])

    def brace_label_declaration(self, items):
        is_latex = items[1].startswith("latex")
        return ArcaneBrace(
            id=gen_id(), variable=items[0], text=items[1], is_latex=is_latex
        )

    def move_along_declaration(self, items):
        return ArcaneMoveAlong(
            id=gen_id(),
            variable_to_move=items[0],
            variable_along=items[1],
        )

    def rotate_declaration(self, items):
        return ArcaneRotate(id=gen_id(), variable=items[0], angle=items[1])

    def scale_declaration(self, items):
        return ArcaneScale(id=gen_id(), variable=items[0], factor=items[1])

    @filter_none
    def style_block(self, items):
        style_dict = {}
        for item in items:
            style_dict.update(item)
        return StyleProperties(**style_dict)

    def style_property(self, items):
        key = str(items[0])
        value = str(items[1])
        return {key: value}

    def STYLE_PROPERTY_KEY(self, items):
        return str(items)
