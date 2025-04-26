from dataclasses import dataclass
from typing import Callable, Tuple
from manim import *
from arcane.core.models.constructs import (
    ArcaneText,
    RelativePositionPlacement,
)
from arcane.graphics.objects import Plot
import numpy as np
from enum import Enum


def render_text(
    text: ArcaneText,
    relative_mobject: Mobject,
):

    if text.is_latex:
        text_mobject = Tex(
            f"${text.value}$",
            font_size=(
                text.options.get("size")
                if text.options.get("size")
                else DEFAULT_FONT_SIZE
            ),  # type:ignore
        )
    else:
        text_mobject = Text(
            text.value,
            font_size=(
                text.options.get("size")
                if text.options.get("size")
                else DEFAULT_FONT_SIZE
            ),  # type:ignore
        )
    if text.position:
        if text.position.placement == RelativePositionPlacement.ABOVE:
            text_mobject = text_mobject.next_to(relative_mobject, UP)

        elif text.position.placement == RelativePositionPlacement.BELOW:
            text_mobject = text_mobject.next_to(relative_mobject, DOWN)

        elif text.position.placement == RelativePositionPlacement.LEFT:
            text_mobject = text_mobject.next_to(relative_mobject, LEFT)

        elif text.position.placement == RelativePositionPlacement.RIGHT:
            text_mobject = text_mobject.next_to(relative_mobject, RIGHT)

    return text_mobject
