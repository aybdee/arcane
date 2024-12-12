from manim import *
from typing import List,Callable


def construct_scene(frames:List[Callable]):
    class ArcaneAnimation(Scene):
        def construct(self):
            for frame in frames:
                self.play(frame())

    return ArcaneAnimation
        
            
    
