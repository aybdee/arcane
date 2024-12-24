from lark import ParseTree
from dataclasses import dataclass
from typing import Dict, List, Any, Union,Tuple


from enum import Enum
    

class Transform():
    pass
    
class Animatable():
    pass


class MathFunction(Animatable):
    pass

@dataclass(frozen=True, eq=True)
class Identifier(Animatable):
    value: str = ""

@dataclass
class RegularMathFunction(MathFunction):
    variables: List[Identifier]
    expression: Any
    pass

@dataclass
class ParametricMathFunction(MathFunction):
    variables: List[Identifier]
    expressions: Any
    pass

class ArcaneType(Enum):
    MATHFUNCTION = "MATH"
    NUMBER = "NUMBER"

@dataclass
class SweepTransform(Transform):
    sweep_from: float
    sweep_to: float
    
@dataclass 
class MultiSweepTransform(Transform):
    transforms: List[Tuple[Identifier,SweepTransform]]


@dataclass 
class Definition():
    type: ArcaneType
    name: Identifier
    value: MathFunction | float
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
