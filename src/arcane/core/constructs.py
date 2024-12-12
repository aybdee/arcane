from lark import ParseTree
from dataclasses import dataclass
from typing import List, Any, Union,Tuple
from sympy import sympify
from enum import Enum
    

class Transform():
    pass

    
class Animatable():
    pass

@dataclass
class Identifier(Animatable):
    value: str = ""

@dataclass
class MathFunction(Animatable):
    variables: List[Identifier]
    expression: Any


class ArcaneType(Enum):
    MATHFUNCTION = "MATH"

@dataclass
class SweepTransform(Transform):
    sweep_from: float
    sweep_to: float
    
@dataclass 
class MultiSweepTransform(Transform):
    transforms: List[Tuple[Identifier,SweepTransform]]


@dataclass 
class Definition(Animatable):
    type: ArcaneType
    name: Identifier
    value: MathFunction #replace this with a union more types come along
    transform: Transform | None


@dataclass 
class InstanceAnimation(Animatable):
    instance: Identifier | MathFunction
    transform: Transform
    
@dataclass
class Animation():
    value: Animatable
    
@dataclass
class Program():
    statements: List[Definition | Animation]
