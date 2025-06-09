import uuid
from pathlib import Path


def get_project_root(marker: str = "pyproject.toml"):
    current_path = Path(__file__).resolve()
    for parent in current_path.parents:
        if (parent / marker).exists():
            return parent
    return current_path  # Fallback if marker isn't found


def group_while(lst, condition):
    groups = []
    current = []
    for item in lst:
        if not current or condition(current[-1], item):
            current.append(item)
        else:
            groups.append(current)
            current = [item]
    if current:
        groups.append(current)
    return groups


def gen_id():
    return str(uuid.uuid4())
