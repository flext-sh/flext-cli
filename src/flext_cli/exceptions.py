"""FLEXT CLI Exceptions.

Error codes and context, replacing multiple specialized exception classes.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from enum import StrEnum


class FlextCliError(Exception):
    """Consolidated CLI exception following flext-core patterns.

    Single comprehensive exception class that handles all CLI error scenarios
    through error codes and contextual information, eliminating the need for
    multiple specialized exception classes.

    Features:
        - Error code categorization via ErrorCode enum
        - Contextual information via keyword arguments
        - User-friendly error messages
        - Stack trace preservation
        - Integration with FlextResult error handling
    """

    class ErrorCode(StrEnum):
        """Error code enumeration for CLI exception categorization."""

        # General errors
        CLI_ERROR = "CLI_ERROR"

        # Input/validation errors
        VALIDATION_ERROR = "CLI_VALIDATION_ERROR"
        ARGUMENT_ERROR = "CLI_ARGUMENT_ERROR"

        # Configuration errors
        CONFIGURATION_ERROR = "CLI_CONFIGURATION_ERROR"
        CONTEXT_ERROR = "CLI_CONTEXT_ERROR"

        # Network/connectivity errors
        CONNECTION_ERROR = "CLI_CONNECTION_ERROR"
        AUTHENTICATION_ERROR = "CLI_AUTHENTICATION_ERROR"
        TIMEOUT_ERROR = "CLI_TIMEOUT_ERROR"

        # Processing errors
        PROCESSING_ERROR = "CLI_PROCESSING_ERROR"
        COMMAND_ERROR = "CLI_COMMAND_ERROR"

        # Output/formatting errors
        FORMAT_ERROR = "CLI_FORMAT_ERROR"
        OUTPUT_ERROR = "CLI_OUTPUT_ERROR"

    def __init__(
        self,
        message: str,
        *,
        error_code: ErrorCode = ErrorCode.CLI_ERROR,
        **context: object,
    ) -> None:
        """Initialize CLI exception with message, error code, and context.

        Args:
            message: Human-readable error description
            error_code: Categorized error code for programmatic handling
            **context: Additional contextual information about the error

        """
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
        """Create validation error exception.

        Args:
            message: Validation error description
            **context: Additional validation context

        Returns:
            FlextCliError with validation error code

        """
        return cls(message, error_code=cls.ErrorCode.VALIDATION_ERROR, **context)

    @classmethod
    def configuration_error(cls, message: str, **context: object) -> FlextCliError:
        """Create configuration error exception.

        Args:
            message: Configuration error description
            **context: Additional configuration context

        Returns:
            FlextCliError with configuration error code

        """
        return cls(message, error_code=cls.ErrorCode.CONFIGURATION_ERROR, **context)

    @classmethod
    def connection_error(cls, message: str, **context: object) -> FlextCliError:
        """Create connection error exception.

        Args:
            message: Connection error description
            **context: Additional connection context

        Returns:
            FlextCliError with connection error code

        """
        return cls(message, error_code=cls.ErrorCode.CONNECTION_ERROR, **context)

    @classmethod
    def authentication_error(cls, message: str, **context: object) -> FlextCliError:
        """Create authentication error exception.

        Args:
            message: Authentication error description
            **context: Additional authentication context

        Returns:
            FlextCliError with authentication error code

        """
        return cls(message, error_code=cls.ErrorCode.AUTHENTICATION_ERROR, **context)

    @classmethod
    def command_error(cls, message: str, **context: object) -> FlextCliError:
        """Create command error exception.

        Args:
            message: Command error description
            **context: Additional command context

        Returns:
            FlextCliError with command error code

        """
        return cls(message, error_code=cls.ErrorCode.COMMAND_ERROR, **context)

    @classmethod
    def timeout_error(cls, message: str, **context: object) -> FlextCliError:
        """Create timeout error exception.

        Args:
            message: Timeout error description
            **context: Additional timeout context

        Returns:
            FlextCliError with timeout error code

        """
        return cls(message, error_code=cls.ErrorCode.TIMEOUT_ERROR, **context)

    @classmethod
    def format_error(cls, message: str, **context: object) -> FlextCliError:
        """Create format error exception.

        Args:
            message: Format error description
            **context: Additional format context

        Returns:
            FlextCliError with format error code

        """
        return cls(message, error_code=cls.ErrorCode.FORMAT_ERROR, **context)

    def is_error_code(self, error_code: ErrorCode) -> bool:
        """Check if exception matches specific error code.

        Args:
            error_code: Error code to check against

        Returns:
            True if error codes match, False otherwise

        """
        return self.error_code == error_code

    def get_context_value(self, key: str, default: object = None) -> object:
        """Get context value by key with optional default.

        Args:
            key: Context key to retrieve
            default: Default value if key not found

        Returns:
            Context value or default

        """
        return self.context.get(key, default)


# Backward compatibility aliases for existing code
FlextCliException = FlextCliError  # Backward compatibility
FlextCliValidationError = FlextCliError
FlextCliConfigurationError = FlextCliError
FlextCliConnectionError = FlextCliError
FlextCliProcessingError = FlextCliError
FlextCliAuthenticationError = FlextCliError
FlextCliTimeoutError = FlextCliError
FlextCliCommandError = FlextCliError
FlextCliArgumentError = FlextCliError
FlextCliFormatError = FlextCliError
FlextCliOutputError = FlextCliError
FlextCliContextError = FlextCliError


__all__ = [
    "FlextCliArgumentError",
    "FlextCliAuthenticationError",
    "FlextCliCommandError",
    "FlextCliConfigurationError",
    "FlextCliConnectionError",
    "FlextCliContextError",
    # Backward compatibility exports
    "FlextCliError",
    "FlextCliException",
    "FlextCliFormatError",
    "FlextCliOutputError",
    "FlextCliProcessingError",
    "FlextCliTimeoutError",
    "FlextCliValidationError",
]
