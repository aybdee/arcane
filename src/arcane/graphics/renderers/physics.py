from manim import *

from arcane.core.models.constructs import (ArcaneLens, ArcaneRays, Direction,
                                           PropagateRays)
from arcane.graphics.custom_mobjects.lens import Lens
from arcane.graphics.custom_mobjects.rays import Ray
from arcane.graphics.utils.manim import (apply_positioning, get_random_color,
                                         map_color_string, map_direction)


@apply_positioning
def render_lens(lens: ArcaneLens, **kwargs):
    lens_style = {"fill_opacity": 0.3, "color": BLUE_B, "stroke_width": 2}
    if lens.style and lens.style.fill:
        lens_style["color"] = map_color_string(lens.style.fill)
    return Lens(f=lens.focal_length, d=lens.thickness, **lens_style)


def render_rays(rays: ArcaneRays):
    start_x, start_y = rays.definition.sweep_from
    end_x, end_y = rays.definition.sweep_to
    count = rays.count
    dir_vec = map_direction(rays.direction)

    # Generate evenly spaced points between start and end
    if rays.direction == Direction.RIGHT or rays.direction == Direction.LEFT:
        t_vals = np.linspace(start_y, end_y, count)
        start_val = start_x if rays.direction == Direction.RIGHT else end_x
        start_point = np.array([start_val, 0, 0])
    else:
        t_vals = np.linspace(start_x, end_x, count)
        start_val = start_y if rays.direction == Direction.RIGHT else end_y
        start_point = np.array([0, start_val, 0])

    ray_color = get_random_color()
    rays_mobject = [
        Ray(
            start=start_point + UP * t,
            direction=dir_vec,
            init_length=3,
            color=(
                ray_color
                if not rays.style or not rays.style.fill
                else map_color_string(rays.style.fill)
            ),
        )
        for t in t_vals
    ]

    return VGroup(*rays_mobject)
