from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Literal, Optional, Tuple

import sympy
from lark import ParseTree

###### Primitives


class RelativePositionPlacement(Enum):
    LEFT = "LEFT"
    RIGHT = "RIGHT"
    ABOVE = "ABOVE"
    BELOW = "BELOW"


AbsoluteCoordinatePosition = Tuple[float, float]


@dataclass
class RelativeAnglePosition:
    variable: str
    angle: float


@dataclass
class RelativeDirectionPosition:
    variable: str
    placement: RelativePositionPlacement


Position = (
    AbsoluteCoordinatePosition | RelativeDirectionPosition | RelativeAnglePosition
)


@dataclass(eq=True)
class Identifier:
    id: str = field(init=False, compare=False)
    value: str = ""

    def __post_init__(self):
        self.id = self.value


###### end Primitives


##### Transforms
@dataclass
class SweepDot:
    id: str
    variable: str


@dataclass
class SweepTransform:
    sweep_from: float
    sweep_to: float


@dataclass
class SweepCoordinates:
    sweep_from: Tuple[float, float]
    sweep_to: Tuple[float, float]


@dataclass
class SweepObjects:
    sweep_from: str
    sweep_to: str


@dataclass
class CoordinateAngleLength:
    sweep_from: Tuple[float, float]
    angle: float
    length: float


@dataclass
class ObjectTransformExpression:
    object_from: sympy.Basic
    object_to: sympy.Basic | List[sympy.Basic]


@dataclass
class ObjectTransform:
    id: str
    object_from: RegularMathFunction | ParametricMathFunction | PolarMathFunction
    object_to: RegularMathFunction | ParametricMathFunction | PolarMathFunction


##### end Transforms


######### math functions


@dataclass
class RegularMathFunction:
    id: str
    variables: List[str]
    expression: Any
    math_function: Callable = lambda x: ...
    x_range: Tuple[float, float] = (0, 0)
    y_range: Tuple[float, float] = (0, 0)
    container_type: Literal["Axis"] = "Axis"  # TODO:(remove this in refactor)


@dataclass
class ParametricMathFunction:
    id: str
    variables: List[str]
    expressions: Any
    math_function: Callable = lambda x: ...
    t_range: Tuple[float, float] = (0, 0)
    x_range: Tuple[float, float] = (0, 0)
    y_range: Tuple[float, float] = (0, 0)
    container_type: Literal["Axis"] = "Axis"


@dataclass
class PolarMathFunction:
    id: str
    variables: List[str]
    expression: Any
    math_function: Callable = lambda x: ...
    x_range: Tuple[float, float] = (0, 0)
    y_range: Tuple[float, float] = (0, 0)
    container_type: Literal["PolarPlane"] = "PolarPlane"


######### end math functions


####### animation primitives
@dataclass
class Animation:
    instance: Animatable
    transforms: List[Transform]


@dataclass
class ArcaneText:
    id: str
    value: str
    position: Optional[Position]
    options: Dict = field(default_factory=dict)
    is_latex: bool = False


@dataclass
class ThreePoint:
    position: Position
    point1: Tuple[float, float]
    point2: Tuple[float, float]


@dataclass
class ArcaneElbow:
    id: str
    definition: ThreePoint | CoordinateAngleLength


@dataclass
class ArcanePoint:
    id: str
    position: Position


@dataclass
class ArcaneLine:
    id: str
    definition: SweepCoordinates | CoordinateAngleLength


@dataclass
class PositionLength:
    position: Position
    length: float


@dataclass
class ArcaneSquare:
    id: str
    definition: PositionLength


@dataclass
class RectangleDefinition:
    position: Position
    width: float
    height: float


@dataclass
class ArcaneRectangle:
    id: str
    definition: RectangleDefinition


@dataclass
class RegularPolygonDefinition:
    position: Position
    radius: float
    num_sides: int


@dataclass
class ArcaneRegularPolygon:
    id: str
    definition: RegularPolygonDefinition


@dataclass
class PolygonDefinition:
    points: List[Tuple[float, float]]


@dataclass
class ArcanePolygon:
    id: str
    definition: PolygonDefinition


@dataclass
class CircleDefinition:
    position: Position
    radius: float


@dataclass
class ArcaneCircle:
    id: str
    definition: CircleDefinition


####### end animation primitives


######### blocks
@dataclass
class Definition:
    name: Identifier
    value: (
        MathFunction
        | ArcaneLine
        | ArcanePoint
        | float
        | ArcaneElbow
        | ArcaneSquare
        | ArcaneRectangle
        | ArcaneRegularPolygon
        | ArcanePolygon
        | ArcaneCircle
    )


@dataclass
class AxisBlock:
    id: str
    animations: List[Animation]


@dataclass
class PolarBlock:
    id: str
    animations: List[Animation]


@dataclass
class Program:
    statements: List[Definition | Animation]


@dataclass
class VLines:
    id: str
    variable: str
    num_lines: float


######### end blocks

########### union type definitions
MathFunction = RegularMathFunction | ParametricMathFunction | PolarMathFunction
MathTransform = SweepTransform
Transform = MathTransform | SweepDot
Animatable = (
    Identifier
    | MathFunction
    | VLines
    | ArcaneText
    | SweepDot
    | ArcaneLine
    | ArcanePoint
    | ArcaneElbow
    | ArcaneSquare
    | ArcaneRectangle
    | ArcaneRegularPolygon
    | ArcanePolygon
    | ArcaneCircle
    | ObjectTransform
)
DirectAnimatable = (
    VLines,
    ArcaneText,
    SweepDot,
    ArcaneLine,
    ArcanePoint,
    ArcaneElbow,
    ArcaneSquare,
    ArcaneRectangle,
    ArcaneRegularPolygon,
    ArcanePolygon,
    ArcaneCircle,
    ObjectTransform,
)


########### end union type definitions
