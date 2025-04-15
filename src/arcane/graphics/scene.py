from dataclasses import dataclass
from manim import *
from typing import List, Callable
from enum import Enum, auto
from arcane.graphics.animation import AnimationItem, AnimationPhase
from arcane.graphics.layout import layout_horizontal, scale_to_fit_screen
from arcane.graphics.objects import Frame, SceneBuilder


def construct_scene(scene_builder: SceneBuilder):
    class ArcaneScene(Scene):
        def construct(self):

            scene_builder.build()

            layout_horizontal(scene_builder.groups)
            container_group = VGroup(*scene_builder.groups)
            scale_to_fit_screen(container_group)

            # Run animations by phase
            for phase in AnimationPhase:
                items_to_add = [
                    item
                    for item in scene_builder.animations
                    if item.phase == phase and not item.animate
                ]
                if items_to_add:
                    for item in items_to_add:
                        self.add(item.animation, **item.config)

                # Then play animations for this phase
                items_to_animate = [
                    item
                    for item in scene_builder.animations
                    if item.phase == phase and item.animate
                ]
                for item in items_to_animate:
                    self.play(item.animation, **item.config)

    return ArcaneScene
