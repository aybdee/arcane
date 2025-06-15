from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any

from manim import *


class AnimationPhase(Enum):
    SETUP = auto()  # Initial setup, no animations here
    PRIMARY = auto()  # First phase animations (e.g., creating axes and graphs)
    SECONDARY = auto()  # Second phase (e.g., adding dots)
    TERTIARY = auto()  # Third phase (e.g., animating dots)
    CLEANUP = auto()


@dataclass
class AnimationItem:
    index: float  # use fractions so i can easily insert animations
    animation: Any  # Can be an animation or object to add
    phase: AnimationPhase
    config: Dict = field(default_factory=dict)
    animate: bool = True
