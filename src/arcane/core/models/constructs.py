from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Literal, Optional, Tuple, Union

import sympy
from lark import ParseTree

###### Primitives


class RelativePositionPlacement(Enum):
    LEFT = "LEFT"
    RIGHT = "RIGHT"
    ABOVE = "ABOVE"
    BELOW = "BELOW"


class Direction(Enum):
    LEFT = "LEFT"
    RIGHT = "RIGHT"
    UP = "UP"
    DOWN = "DOWN"
    IN = "IN"
    OUT = "OUT"


AbsoluteCoordinatePosition = Tuple[float, float]


@dataclass
class RelativeAnglePosition:
    variable: Identifier
    angle: float


@dataclass
class RelativeDirectionPosition:
    variable: Identifier
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
    variable: Identifier


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
    sweep_from: Identifier
    sweep_to: Identifier


@dataclass
class PropagateRays:
    id: str
    lenses: List[Identifier]


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
class ArcaneClearObject:
    id: str
    variable: Identifier


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
class StyleProperties:
    fill: Optional[str] = None
    stroke_color: Optional[str] = None


@dataclass
class ArcaneSquare:
    id: str
    definition: PositionLength
    style: Optional[StyleProperties] = None


@dataclass
class RectangleDefinition:
    position: Position
    width: float
    height: float


@dataclass
class ArcaneRectangle:
    id: str
    definition: RectangleDefinition
    style: Optional[StyleProperties] = None


@dataclass
class RegularPolygonDefinition:
    position: Position
    radius: float
    num_sides: int


@dataclass
class ArcaneRegularPolygon:
    id: str
    definition: RegularPolygonDefinition
    style: Optional[StyleProperties] = None


@dataclass
class PolygonDefinition:
    points: List[Tuple[float, float]]


@dataclass
class ArcanePolygon:
    id: str
    definition: PolygonDefinition
    style: Optional[StyleProperties] = None


@dataclass
class CircleDefinition:
    position: Position
    radius: float


@dataclass
class ArcaneCircle:
    id: str
    definition: CircleDefinition
    style: Optional[StyleProperties] = None


@dataclass
class ArcaneLens:
    id: str
    focal_length: int
    thickness: int
    position: Position
    style: Optional[StyleProperties] = None


@dataclass
class ArcaneRays:
    id: str
    definition: SweepCoordinates
    count: int
    direction: Direction
    style: Optional[StyleProperties] = None


@dataclass
class ArcaneArrow:
    id: str
    definition: Union[SweepCoordinates, SweepObjects]
    style: Optional[StyleProperties] = None


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
        | ArcaneArrow
        | ArcaneLens
        | ArcaneRays
    )


@dataclass
class AxisBlock:
    id: str
    _statements: List[any]
    statements: List[int] = field(default_factory=list)


@dataclass
class PolarBlock:
    id: str
    _statements: List[any]
    statements: List[int] = field(default_factory=list)


@dataclass
class Program:
    statements: List[Statement]


@dataclass
class Statement:
    index: int
    value: Definition | Animation | AxisBlock | PolarBlock | ArcaneClearObject


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
    | ArcaneArrow
    | ObjectTransform
    | ArcaneLens
    | PropagateRays
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
    ArcaneArrow,
    ArcaneArrow,
    ObjectTransform,
    ArcaneLens,
    PropagateRays,
)

########### end union type definitions
