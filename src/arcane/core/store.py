from typing import Any, Dict, List, Optional
from arcane.core.interpreter_types import (
    InterpreterError,
    InterpreterMessage,
    InterpreterErrorCode,
)


class Store:
    """Variable storage for the interpreter"""

    def __init__(self):
        self._store: Dict[str, Any] = {}

    def add(self, key: str, value: Any) -> None:
        """Add or update a variable in the store"""
        self._store[key] = value

    def get(self, key: str) -> Optional[Any]:
        """Get a variable from the store, returning None if not found"""
        return self._store.get(key)

    def get_or_throw(self, key: str) -> Any:
        """Get a variable from the store, raising an error if not found"""
        value = self.get(key)
        if value is not None:
            return value

        raise InterpreterError(
            InterpreterErrorCode.UNDEFINED_VARIABLE, variable_name=key
        )

    def has(self, key: str) -> bool:
        """Check if a variable exists in the store"""
        return key in self._store

    def keys(self) -> List[str]:
        """Get all variable names in the store"""
        return list(self._store.keys())

    def __str__(self) -> str:
        return str(self.keys())
