from manim import *


def layout_horizontal(objects: List[Mobject]):
    if objects:
        current_object = objects[0]
        for object in objects[1:]:
            object.next_to(current_object)
            current_object = object


def layout_grid(objects: List[Mobject], rows: int, cols: int, spacing=0.5):
    """Layout objects in a grid with proper spacing based on their dimensions."""
    if not objects:
        return

    # Calculate the maximum width and height needed for each cell
    max_width = max(obj.get_width() for obj in objects) if objects else 0
    max_height = max(obj.get_height() for obj in objects) if objects else 0

    # Add spacing to cell dimensions
    cell_width = max_width + spacing
    cell_height = max_height + spacing

    for i in range(rows):
        for j in range(cols):
            index = i * cols + j
            if index < len(objects):
                obj = objects[index]
                # Calculate position: start from top-left, move right by j cells, down by i cells
                x_pos = j * cell_width
                y_pos = -i * cell_height  # Negative because Y increases upward in Manim

                # Center the object within its cell
                obj.move_to(RIGHT * x_pos + UP * y_pos)


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
