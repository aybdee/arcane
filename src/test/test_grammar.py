import os

import pytest

from arcane.core.parsing.parser import parse
from arcane.core.parsing.transfomer import ArcaneTransfomer


def get_test_scripts():
    """Helper function to get all test scripts"""
    test_dir = os.path.join(os.path.dirname(__file__), "test_scripts")
    return [
        os.path.join(test_dir, f) for f in os.listdir(test_dir) if f.endswith(".arc")
    ]


@pytest.mark.parametrize("script_path", get_test_scripts())
def test_script_grammar(script_path):
    """Test if each script can be parsed and transformed successfully"""
    with open(script_path, "r") as f:
        content = f.read()
        # If any step fails, pytest will show the specific error and mark the test as failed
        tree = parse(content)
        program = ArcaneTransfomer().transform(tree)
        # The test passes if no exception is raised
