from dataclasses import dataclass
from manim import *
from typing import List, Callable
from enum import Enum, auto
from arcane.graphics.animation import AnimationItem, AnimationPhase
from arcane.graphics.objects import Frame, SceneBuilder
from arcane.graphics.utils import layout_horizontal


def construct_scene(scene_builder: SceneBuilder):
    class ArcaneScene(Scene):
        def construct(self):
            containers = []
            all_animation_items = []

            scene_builder.build()

            # Collect all containers and animation items
            for container, animation_items in scene_builder.frames:
                containers.append(container)
                all_animation_items.extend(animation_items)

            layout_horizontal(containers)
            container_group = VGroup(*containers)
            if len(containers) > 1:
                container_group.scale(0.7).move_to(ORIGIN)

            # Run animations by phase
            for phase in AnimationPhase:
                items_to_add = [
                    item
                    for item in all_animation_items
                    if item.phase == phase and not item.animate
                ]
                if items_to_add:
                    for item in items_to_add:
                        self.add(item.animation, **item.config)

                # Then play animations for this phase
                items_to_animate = [
                    item
                    for item in all_animation_items
                    if item.phase == phase and item.animate
                ]
                for item in items_to_animate:
                    self.play(item.animation, **item.config)

    return ArcaneScene
