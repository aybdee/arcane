from enum import Enum
from typing import Any


class InterpreterErrorCode(Enum):
    NO_STATEMENTS_AVAILABLE = "No statements left to evaluate"
    UNDEFINED_VARIABLE = "Undefined variable: {variable_name}"
    UNKNOWN = "Program crashed unexpectedly: {details}"
    UNSUPPORTED_STATEMENT = "Unsupported statement type: {statement_type}"
    UNSUPPORTED_PLOT = "Unsupported plot on axis"
    ANIMATION_ERROR = "Error during animation: {details}"
    UNSUPPORTED_EXPRESSION = "Error evaluating expression {expression}: {error}"
    UNEXPECTED_TYPE = "Expected value of type {expected} got {gotten}"


class InterpreterError(Exception):
    """Custom exception for interpreter-specific errors"""

    def __init__(self, error_code: InterpreterErrorCode, **kwargs):
        self.error_code = error_code
        self.message = error_code.value.format(**kwargs)
        super().__init__(self.message)

    def __str__(self):
        return self.message


class InterpreterMessageType(Enum):
    SUCCESS = "statement evaluated"
    WARNING = "warning"
    INFO = "info"


class InterpreterMessage:
    """Message returned by the interpreter after statement execution"""

    def __init__(
        self, message_type: InterpreterMessageType, message: str = "", data: Any = None
    ):
        self.type = message_type
        self.message = message or message_type.value
        self.data = data

    def with_data(self, data: Any) -> "InterpreterMessage":
        """Returns a new message with the same type and message but different data"""
        return InterpreterMessage(self.type, self.message, data)

    def __str__(self):
        return f"{self.type.name}: {self.message}"
