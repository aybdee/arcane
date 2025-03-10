from pathlib import Path


def get_project_root(marker: str = "pyproject.toml"):
    current_path = Path(__file__).resolve()
    for parent in current_path.parents:
        if (parent / marker).exists():
            return parent
    return current_path  # Fallback if marker isn't found
