from manim import *


def layout_horizontal(objects: List[Mobject]):
    if objects:
        current_object = objects[0]
        for object in objects[1:]:
            object.next_to(current_object)
            current_object = object


def scale_to_fit_screen(container_group, padding=0.5):
    left = container_group.get_left()[0]
    right = container_group.get_right()[0]
    top = container_group.get_top()[1]
    bottom = container_group.get_bottom()[1]

    group_width = right - left
    group_height = top - bottom

    available_width = config.frame_width - (2 * padding)
    available_height = config.frame_height - (2 * padding)

    width_scale = available_width / group_width if group_width > available_width else 1
    height_scale = (
        available_height / group_height if group_height > available_height else 1
    )

    scale_factor = min(width_scale, height_scale)

    if scale_factor < 1:
        container_group.scale(scale_factor)

    container_group.move_to(ORIGIN)
    return container_group
