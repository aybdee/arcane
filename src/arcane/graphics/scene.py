from dataclasses import dataclass
from enum import Enum, auto
from typing import Callable, List

from manim import *

import arcane.graphics.config
from arcane.graphics.animation import AnimationItem, AnimationPhase
from arcane.graphics.builder import SceneBuilder
from arcane.graphics.layout import layout_horizontal, scale_to_fit_screen
from arcane.utils import group_while


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

                items_to_animate = group_while(
                    sorted(items_to_animate, key=lambda item: item.index),
                    lambda a, b: a.index == b.index,
                )
                for item_group in items_to_animate:
                    self.play(
                        *[item.animation for item in item_group],
                        **{k: v for item in item_group for k, v in item.config.items()},
                    )

    return ArcaneScene
