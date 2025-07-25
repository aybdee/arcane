from dataclasses import dataclass
from enum import Enum, auto
from pprint import pprint
from typing import Callable, List

from manim import *
from manim_physics import SpaceScene

import arcane.graphics.config
from arcane.graphics.animation import AnimationItem, AnimationPhase
from arcane.graphics.builder import SceneBuilder
from arcane.graphics.layout import (layout_grid, layout_horizontal,
                                    scale_to_fit_screen)
from arcane.utils import group_while


def construct_scene(scene_builder: SceneBuilder):
    class ArcaneScene(SpaceScene):
        def construct(self):

            scene_container = scene_builder.build()

            if len(scene_builder.groups) < 3:
                layout_horizontal(scene_builder.groups)
            else:
                layout_grid(scene_builder.groups, 3, 3)
            container_group = VGroup(*scene_builder.groups)
            scale_to_fit_screen(scene_container)

            # Run animations by phase
            for phase in AnimationPhase:
                items_to_add = [
                    item
                    for item in scene_builder.animations
                    if item.phase == phase and not item.animate
                ]
                if items_to_add:
                    for item in items_to_add:
                        if not item.defer:
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
                        *[
                            item.animation() if item.defer else item.animation
                            for item in item_group
                        ],
                        **{k: v for item in item_group for k, v in item.config.items()},
                    )

                for item in items_to_add:
                    if item.defer:
                        self.add(item.animation, **item.config)

            self.wait(0.5)

    return ArcaneScene
