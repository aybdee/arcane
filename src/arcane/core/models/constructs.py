from __future__ import annotations
from lark import ParseTree
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum


###### Primitives


class RelativePositionPlacement(Enum):
    LEFT = "LEFT"
    RIGHT = "RIGHT"
    ABOVE = "ABOVE"
    BELOW = "BELOW"


@dataclass
class RelativePosition:
    variable: str
    placement: RelativePositionPlacement


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


##### end Transforms


######### math functions
@dataclass
class RegularMathFunction:
    id: str
    variables: List[str]
    expression: Any


@dataclass
class ParametricMathFunction:
    id: str
    variables: List[str]
    expressions: Any


@dataclass
class PolarMathFunction:
    id: str
    variables: List[str]
    expression: Any


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
    position: Optional[RelativePosition]
    options: Dict = field(default_factory=dict)
    is_latex: bool = False


@dataclass
class ThreePoint:
    vertex: Tuple[float, float]
    point1: Tuple[float, float]
    point2: Tuple[float, float]


@dataclass
class ArcaneElbow:
    id: str
    definition: ThreePoint | CoordinateAngleLength


@dataclass
class ArcanePoint:
    id: str
    position: Tuple[float, float]


@dataclass
class ArcaneLine:
    id: str
    definition: SweepCoordinates | CoordinateAngleLength


####### end animation primitives


######### blocks
@dataclass
class Definition:
    name: Identifier
    value: MathFunction | ArcaneLine | ArcanePoint | float


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
)


########### end union type definitions
