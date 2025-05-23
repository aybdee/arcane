from dataclasses import dataclass
from enum import Enum
from typing import Callable, Optional, Tuple

import numpy as np
from manim import *

from arcane.core.models.constructs import ArcaneText, RelativePositionPlacement
from arcane.graphics.utils.manim import apply_positioning


@apply_positioning
def render_text(text: ArcaneText, **kwargs):
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
    return text_mobject
