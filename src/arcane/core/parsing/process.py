import re
from dataclasses import fields, is_dataclass
from typing import Any, Set

from arcane.core.models.constructs import (Animation, ArcaneArrow, ArcaneText,
                                           Definition, Identifier,
                                           MathFunction, ObjectTransform,
                                           Program, RelativeAnglePosition,
                                           RelativeDirectionPosition,
                                           SweepObjects, VLines)


def _is_generated_id(id_str: str) -> bool:
    """Check if a string looks like a generated UUID"""
    # TODO: come up with better way off handling this, this approach could technically cause overlap if the user decides to name a variable
    return bool(
        re.match(
            r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", id_str
        )
    )


def _get_defined_variables(ast: Program) -> set[str]:
    """Extract all defined variable names from the AST"""
    defined_vars = set()
    for statement in ast.statements:
        if isinstance(statement, Definition):
            defined_vars.add(statement.name.value)
    return defined_vars


def _search_for_identifiers(obj: Any, deps: Set[str]) -> None:
    """Recursively search through an object and its fields for Identifier instances"""
    # Skip None objects
    if obj is None:
        return

    # Handle lists, tuples, and sets
    if isinstance(obj, (list, tuple, set)):
        for item in obj:
            _search_for_identifiers(item, deps)
        return

    # Handle dictionaries
    if isinstance(obj, dict):
        for value in obj.values():
            _search_for_identifiers(value, deps)
        return

    # If it's an Identifier and not in a field named 'id', add its value
    if isinstance(obj, Identifier):
        deps.add(obj.value)
        return

    # For dataclasses, recursively check all fields
    if is_dataclass(obj):
        for field in fields(obj):
            if field.name != "id" and field.name != "name":
                field_value = getattr(obj, field.name)
                _search_for_identifiers(field_value, deps)


def _get_dependencies(node) -> set[str]:
    """Extract dependencies from a node by finding all Identifier instances"""
    deps = set()
    _search_for_identifiers(node, deps)
    # Filter out empty strings and generated IDs
    return {dep for dep in deps if dep and not _is_generated_id(dep)}


def resolve_dependencies(ast: Program) -> Program:
    """Resolve dependencies between objects in the AST"""
    defined_vars = _get_defined_variables(ast)
    animated_vars = set()
    new_statements = []

    # First pass: collect all variables that are already animated
    for statement in ast.statements:
        if isinstance(statement, Animation):
            if isinstance(statement.instance, Identifier):
                animated_vars.add(statement.instance.value)
            elif hasattr(statement.instance, "id"):
                animated_vars.add(statement.instance.id)

    # Second pass: process statements and inject animations where needed
    for statement in ast.statements:
        deps = _get_dependencies(statement)
        print(deps)
        # For each dependency that hasn't been animated yet
        for dep in deps:
            if dep not in defined_vars:
                raise ValueError(f"Undefined variable '{dep}' referenced")

            # If dependency hasn't been animated, inject an animation
            if dep not in animated_vars:
                new_statements.append(
                    Animation(instance=Identifier(value=dep), transforms=[])
                )
                animated_vars.add(dep)

        new_statements.append(statement)

    # Update the AST with the new statements
    ast.statements = new_statements
    return ast
