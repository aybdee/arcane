import os
from manim import config
from arcane.utils import get_project_root


root_dir = get_project_root()

config.media_dir = os.path.join(root_dir, "media")
# config.renderer = "opengl"
config.preview = True
# config.verbosity = "DEBUG"
# config.log_to_file = True
