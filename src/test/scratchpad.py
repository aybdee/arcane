from manim import *
from manim_physics import *


class SideBySideGraphs(Scene):
    def construct(self):
        concave_lens = Lens(f=-3, d=1)
        self.play(Create(concave_lens))
