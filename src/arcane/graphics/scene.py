from manim import *
from typing import List,Callable

from arcane.graphics.objects import Frame


def construct_scene(frames:List[Frame]):
    class ArcaneAnimation(Scene):
        def construct(self):
            for frame in frames:
                self.play(frame.render())

    return ArcaneAnimation
        
            
    
