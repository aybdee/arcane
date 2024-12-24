from dataclasses import dataclass
from typing import Callable, List
from abc import ABC, abstractmethod
from manim import *

class Frame(ABC):
    @abstractmethod
    def render(self) -> AnimationGroup:
        ...
    
class Axis(Frame):
    def __init__(self):
        self.items : List[Callable] = []

    def add(self,item:Callable):
        self.items.append(item)
    
    def render(self):
        axes = Axes(
            x_range=[-7, 7, 1],  # Extended x-range for more visual balance
            y_range=[-3.0, 3.0, 1],  # Adjusted y-range for typical functions
            
            x_length=12,
            y_length=6,
            axis_config={"color": GREEN},
            tips=False, 
        )

        return AnimationGroup(*[
            Create(axes),
            *[item(axes) for item in self.items],
        ],lag_ratio=0.2)
