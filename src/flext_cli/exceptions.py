"""FLEXT CLI Exceptions - Single unified class following FLEXT standards.

Provides CLI-specific exception handling using flext-core patterns.
Single FlextCliExceptions class with nested exception subclasses following FLEXT pattern.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import override

from flext_core import FlextExceptions


class FlextCliExceptions(FlextExceptions):
    """Single unified CLI exceptions class following FLEXT standards.

    Contains all exception subclasses for CLI domain operations.
    Follows FLEXT pattern: one class per module with nested subclasses.

    ARCHITECTURAL COMPLIANCE:
    - Inherits from FlextExceptions to avoid duplication
    - Uses centralized exception patterns from FlextExceptions
    - Implements CLI-specific extensions while reusing core functionality
    """

    class BaseError(FlextExceptions.BaseError):
        """Base CLI exception extending FlextExceptions.BaseError.

        Simple exception class for CLI error scenarios with error categorization
        and contextual information support.
        """

        @override
        def __init__(
            self,
            message: str,
            *,
            error_code: str | int = "CLI_ERROR",
            **context: object,
        ) -> None:
            """Initialize CLI exception with message, error code, and context."""
            # Convert int error codes to string for consistency
            if isinstance(error_code, int):
                error_code = str(error_code)
            super().__init__(message, code=error_code, context=context)

        @override
        def __str__(self) -> str:
            """Return string representation of the exception."""
            context_str = ""
            if self.context:
                context_items = [f"{k}={v}" for k, v in self.context.items()]
                context_str = f" ({', '.join(context_items)})"

            return f"[{self.error_code}] {self.message}{context_str}"

        @override
        def __repr__(self) -> str:
            """Return detailed representation for debugging."""
            return (
                f"FlextCliExceptions.BaseError("
                f"message='{self.message}', "
                f"error_code='{self.error_code}', "
                f"context={self.context})"
            )

        def get_context_value(self, key: str, default: object = None) -> object:
            """Get context value by key with optional default."""
            return self.context.get(key, default)

        def is_error_code(self, error_code: str) -> bool:
            """Check if exception matches specific error code."""
            return str(self.error_code) == error_code

    class CliValidationError(BaseError):
        """CLI validation error exception."""

        @override
        def __init__(self, message: str, **context: object) -> None:
            """Initialize validation error with message and context."""
            super().__init__(message, error_code="CLI_VALIDATION_ERROR", **context)

    class CliConfigurationError(BaseError):
        """CLI configuration error exception."""

        @override
        def __init__(self, message: str, **context: object) -> None:
            """Initialize configuration error with message and context."""
            super().__init__(message, error_code="CLI_CONFIGURATION_ERROR", **context)

    class CliConnectionError(BaseError):
        """CLI connection error exception."""

        @override
        def __init__(self, message: str, **context: object) -> None:
            """Initialize connection error with message and context."""
            super().__init__(message, error_code="CLI_CONNECTION_ERROR", **context)

    class CliAuthenticationError(BaseError):
        """CLI authentication error exception."""

        @override
        def __init__(self, message: str, **context: object) -> None:
            """Initialize authentication error with message and context."""
            super().__init__(message, error_code="CLI_AUTHENTICATION_ERROR", **context)

    class CliCommandError(BaseError):
        """CLI command error exception."""

        @override
        def __init__(self, message: str, **context: object) -> None:
            """Initialize command error with message and context."""
            super().__init__(message, error_code="COMMAND_ERROR", **context)

    class CliTimeoutError(BaseError):
        """CLI timeout error exception."""

        @override
        def __init__(self, message: str, **context: object) -> None:
            """Initialize timeout error with message and context."""
            super().__init__(message, error_code="CLI_TIMEOUT_ERROR", **context)

    class CliFormatError(BaseError):
        """CLI format error exception."""

        @override
        def __init__(self, message: str, **context: object) -> None:
            """Initialize format error with message and context."""
            super().__init__(message, error_code="FORMAT_ERROR", **context)


__all__ = [
    "FlextCliExceptions",
]
