from dataclasses import dataclass, field
from manim import *
from enum import Enum, auto


class AnimationPhase(Enum):
    SETUP = auto()  # Initial setup, no animations here
    PRIMARY = auto()  # First phase animations (e.g., creating axes and graphs)
    SECONDARY = auto()  # Second phase (e.g., adding dots)
    TERTIARY = auto()  # Third phase (e.g., animating dots)
    CLEANUP = auto()


@dataclass
class AnimationItem:
    animation: Animation | Mobject  # Can be an animation or object to add
    phase: AnimationPhase
    config: Dict = field(default_factory=dict)
    animate: bool = True
