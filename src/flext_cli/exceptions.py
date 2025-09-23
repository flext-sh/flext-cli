"""FLEXT CLI Exceptions - Simple exception classes extending flext-core patterns.

Provides essential exception handling using flext-core patterns.
Follows single-responsibility principle with simple, focused exceptions.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations


class FlextCliError(Exception):
    """Base CLI exception extending standard Exception.

    Simple exception class for CLI error scenarios with error categorization
    and contextual information support.
    """

    def __init__(
        self,
        message: str,
        *,
        error_code: str = "CLI_ERROR",
        **context: object,
    ) -> None:
        """Initialize CLI exception with message, error code, and context."""
        super().__init__(message)
        self.error_code = error_code
        self.context = context
        self.message = message

    def __str__(self) -> str:
        """Return string representation of the exception."""
        context_str = ""
        if self.context:
            context_items = [f"{k}={v}" for k, v in self.context.items()]
            context_str = f" ({', '.join(context_items)})"

        return f"[{self.error_code}] {self.message}{context_str}"

    def __repr__(self) -> str:
        """Return detailed representation for debugging."""
        return (
            f"FlextCliError("
            f"message='{self.message}', "
            f"error_code='{self.error_code}', "
            f"context={self.context})"
        )

    @classmethod
    def validation_error(cls, message: str, **context: object) -> FlextCliError:
        """Create validation error exception."""
        return cls(message, error_code="VALIDATION_ERROR", **context)

    @classmethod
    def configuration_error(cls, message: str, **context: object) -> FlextCliError:
        """Create configuration error exception."""
        return cls(message, error_code="CONFIGURATION_ERROR", **context)

    @classmethod
    def connection_error(cls, message: str, **context: object) -> FlextCliError:
        """Create connection error exception."""
        return cls(message, error_code="CONNECTION_ERROR", **context)

    @classmethod
    def authentication_error(cls, message: str, **context: object) -> FlextCliError:
        """Create authentication error exception."""
        return cls(message, error_code="AUTHENTICATION_ERROR", **context)

    @classmethod
    def command_error(cls, message: str, **context: object) -> FlextCliError:
        """Create command error exception."""
        return cls(message, error_code="COMMAND_ERROR", **context)

    @classmethod
    def timeout_error(cls, message: str, **context: object) -> FlextCliError:
        """Create timeout error exception."""
        return cls(message, error_code="TIMEOUT_ERROR", **context)

    @classmethod
    def format_error(cls, message: str, **context: object) -> FlextCliError:
        """Create format error exception."""
        return cls(message, error_code="FORMAT_ERROR", **context)

    def is_error_code(self, error_code: str) -> bool:
        """Check if exception matches specific error code."""
        return self.error_code == error_code

    def get_context_value(self, key: str, default: object = None) -> object:
        """Get context value by key with optional default."""
        return self.context.get(key, default)


__all__ = [
    "FlextCliError",
]
