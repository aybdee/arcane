from lark import ParseTree
from dataclasses import dataclass
from typing import Dict, List, Any


from enum import Enum


class SweepDotTransform: ...


class SweepRectangleDotTransform: ...


@dataclass(frozen=True, eq=True)
class Identifier:
    value: str = ""


@dataclass
class RegularMathFunction:
    variables: List[Identifier]
    expression: Any
    pass


@dataclass
class ParametricMathFunction:
    variables: List[Identifier]
    expressions: Any
    pass


MathFunction = RegularMathFunction | ParametricMathFunction


class ArcaneType(Enum):
    MATHFUNCTION = "MATH"
    NUMBER = "NUMBER"


@dataclass
class SweepTransform:
    sweep_from: float
    sweep_to: float


MathTransform = SweepTransform
Transform = MathTransform | SweepDotTransform


@dataclass
class InstanceAnimation:
    instance: Identifier | MathFunction
    transforms: List[Transform]


# union type definitions
Animatable = InstanceAnimation | MathFunction | Identifier


@dataclass
class Definition:
    type: ArcaneType
    name: Identifier
    value: MathFunction | float
    transform: MathTransform | None


@dataclass
class Animation:
    value: Animatable


@dataclass
class AxisBlock:
    name: Identifier
    animations: List[InstanceAnimation]


@dataclass
class Program:
    statements: List[Definition | Animation]
