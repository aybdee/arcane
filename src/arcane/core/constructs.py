from __future__ import annotations
from lark import ParseTree
from dataclasses import dataclass
from typing import Dict, List, Any
from enum import Enum


###### Primitives
class ArcaneType(Enum):
    MATHFUNCTION = "MATH"
    NUMBER = "NUMBER"


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
class InstanceAnimation:
    instance: Identifier | MathFunction
    transforms: List[Transform]


@dataclass
class Animation:
    value: Animatable


####### end animation primitives


######### blocks
@dataclass
class Definition:
    type: ArcaneType
    name: Identifier
    value: MathFunction | float
    transform: MathTransform | None


@dataclass
class AxisBlock:
    name: Identifier
    animations: List[InstanceAnimation]


@dataclass
class Program:
    statements: List[Definition | Animation]


######### end blocks

########### union type definitions
MathFunction = RegularMathFunction | ParametricMathFunction | PolarMathFunction
Animatable = InstanceAnimation | MathFunction | Identifier
MathTransform = SweepTransform
Transform = MathTransform | SweepDotTransform
########### end union type definitions
