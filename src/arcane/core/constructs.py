from __future__ import annotations
from lark import ParseTree
from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from enum import Enum


###### Primitives
class ArcaneType(Enum):
    MATHFUNCTION = "MATH"
    NUMBER = "NUMBER"


class RelativePositionPlacement(Enum):
    LEFT = "LEFT"
    RIGHT = "RIGHT"
    ABOVE = "ABOVE"
    BELOW = "BELOW"


@dataclass
class RelativePosition:
    variable: Identifier
    placement: RelativePositionPlacement


@dataclass(frozen=True, eq=True)
class Identifier:
    value: str = ""


###### end Primitives


##### Transforms
class SweepDotTransform: ...


@dataclass
class SweepTransform:
    sweep_from: float
    sweep_to: float


##### end Transforms


######### math functions
@dataclass
class RegularMathFunction:
    variables: List[Identifier]
    expression: Any


@dataclass
class ParametricMathFunction:
    variables: List[Identifier]
    expressions: Any


@dataclass
class PolarMathFunction:
    variables: List[Identifier]
    expression: Any


######### end math functions


####### animation primitives
@dataclass
class Animation:
    instance: Identifier | MathFunction | VLines | TextAnimation | SweepDotTransform
    transforms: List[Transform]


@dataclass
class TextAnimation:
    value: str
    position: Optional[RelativePosition]


####### end animation primitives


######### blocks
@dataclass
class Definition:
    type: ArcaneType
    name: Identifier
    value: MathFunction | float


@dataclass
class AxisBlock:
    name: Identifier
    animations: List[Animation]


@dataclass
class PolarBlock:
    name: Identifier
    animations: List[Animation]


@dataclass
class Program:
    statements: List[Definition | Animation]


@dataclass
class VLines:
    variable: Identifier
    num_lines: float


######### end blocks

########### union type definitions
MathFunction = RegularMathFunction | ParametricMathFunction | PolarMathFunction
MathTransform = SweepTransform
Transform = MathTransform | SweepDotTransform
########### end union type definitions
