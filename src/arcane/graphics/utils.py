from manim import *
import sympy as sp
import random


def get_random_color():
    colors = [GREEN, YELLOW, WHITE, RED, BLUE, ORANGE, PURPLE, TEAL]
    return random.choice(colors)


def compute_function_range(func, value_range, num_samples=100):
    x_values = np.linspace(value_range[0], value_range[1], num_samples)
    vfunc = np.vectorize(func)
    y_values = vfunc(x_values)
    y_min, y_max = np.min(y_values), np.max(y_values)
    return [y_min, y_max]


def clip_plot(csystem, plotfun, x_range=[-5, 5, 0.01], **kwargs):
    grp = VGroup()
    dx = x_range[2]
    for xstart in np.arange(*x_range):
        snip = csystem.plot(plotfun, x_range=[xstart, xstart + dx, 0.5 * dx], **kwargs)
        if (snip.get_top()[1] > csystem.get_top()[1]) or (
            snip.get_bottom()[1] < csystem.get_bottom()[1]
        ):
            snip.set_opacity(0)
        grp += snip
    return grp


def layout_horizontal(objects: List[Mobject]):
    current_object = objects[0]
    for object in objects[1:]:
        object.next_to(current_object)
        current_object = object


CoordinateSystem.clip_plot = clip_plot  # type: ignore
