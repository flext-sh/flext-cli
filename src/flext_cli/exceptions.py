"""FLEXT CLI exception types for tests, aligned with new patterns."""

from __future__ import annotations

from enum import Enum


class FlextCliErrorCodes(Enum):
    """Canonical CLI error codes for consistent assertions in testes."""

    CLI_ERROR = "CLI_ERROR"
    CLI_VALIDATION_ERROR = "CLI_VALIDATION_ERROR"
    CLI_CONFIGURATION_ERROR = "CLI_CONFIGURATION_ERROR"
    CLI_CONNECTION_ERROR = "CLI_CONNECTION_ERROR"
    CLI_PROCESSING_ERROR = "CLI_PROCESSING_ERROR"
    CLI_AUTHENTICATION_ERROR = "CLI_AUTHENTICATION_ERROR"
    CLI_TIMEOUT_ERROR = "CLI_TIMEOUT_ERROR"
    CLI_COMMAND_ERROR = "CLI_COMMAND_ERROR"
    CLI_ARGUMENT_ERROR = "CLI_ARGUMENT_ERROR"
    CLI_FORMAT_ERROR = "CLI_FORMAT_ERROR"
    CLI_OUTPUT_ERROR = "CLI_OUTPUT_ERROR"
    CLI_CONTEXT_ERROR = "CLI_CONTEXT_ERROR"


class FlextCliError(Exception):
    """Base CLI error carrying optional context details."""

    def __init__(self, message: str, **context: object) -> None:
        super().__init__(message)
        self.context = context


class FlextCliValidationError(FlextCliError):
    """Validation failure for user input or configuration."""


class FlextCliConfigurationError(FlextCliError):
    """Invalid or inconsistent CLI configuration detected."""


class FlextCliConnectionError(FlextCliError):
    """Connectivity failures when reaching remote services."""


class FlextCliProcessingError(FlextCliError):
    """General processing failure in CLI workflows."""


class FlextCliAuthenticationError(FlextCliError):
    """Authentication or authorization related failure."""


class FlextCliTimeoutError(FlextCliError):
    """Operation exceeded configured timeout constraints."""


class FlextCliCommandError(FlextCliError):
    """Error while building or executing a command."""


class FlextCliArgumentError(FlextCliError):
    """Invalid or missing CLI argument detected."""


class FlextCliFormatError(FlextCliError):
    """Formatting or serialization failure for output data."""


class FlextCliOutputError(FlextCliError):
    """Output rendering or console I/O failure."""


class FlextCliContextError(FlextCliError):
    """Invalid application context for command execution."""


__all__ = [
    "FlextCliArgumentError",
    "FlextCliAuthenticationError",
    "FlextCliCommandError",
    "FlextCliConfigurationError",
    "FlextCliConnectionError",
    "FlextCliContextError",
    "FlextCliError",
    "FlextCliErrorCodes",
    "FlextCliFormatError",
    "FlextCliOutputError",
    "FlextCliProcessingError",
    "FlextCliTimeoutError",
    "FlextCliValidationError",
]
