from manim import *
from typing import List, Callable

from arcane.graphics.objects import Frame
from arcane.graphics.utils import layout_horizontal


def construct_scene(frames: List[Frame]):
    class ArcaneAnimation(Scene):
        def construct(self):
            partial_frames: List[List[Animation]] = []
            containers = []
            for frame in frames:
                container, animations = frame.render()
                partial_frames.append(animations)
                containers.append(container)

            layout_horizontal(containers)

            VGroup(*containers).scale(0.7).move_to(ORIGIN)

            for frame in partial_frames:
                self.play(frame)

    return ArcaneAnimation
