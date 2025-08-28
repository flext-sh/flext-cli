"""CLI Exception Hierarchy - CONSOLIDATED Pattern following FLEXT standards.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Mapping
from enum import Enum

from flext_core import FlextExceptions


class FlextCliExceptions:
    """Single CONSOLIDATED class containing ALL CLI exceptions.

    Consolidates ALL exception definitions into one class following FLEXT patterns.
    Individual exceptions available as nested classes for organization.
    Maintains backward compatibility through properties.
    """

    class ErrorCodes(Enum):
        """Error codes for CLI domain operations."""

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

    # Base CLI exception
    class CliError(FlextExceptions.BaseError):
        """Base exception for all CLI domain errors."""

    class ValidationError(FlextExceptions.BaseError):
        """CLI validation errors."""

    class ConfigurationError(FlextExceptions.BaseError):
        """CLI configuration errors."""

    class CliConnectionError(FlextExceptions.BaseError):
        """CLI connection errors."""

    class ProcessingError(FlextExceptions.BaseError):
        """CLI processing errors."""

    class AuthenticationError(FlextExceptions.BaseError):
        """CLI authentication errors."""

    class CliTimeoutError(FlextExceptions.BaseError):
        """CLI timeout errors."""

    class CommandError(FlextExceptions.BaseError):
        """CLI command execution errors with command context."""

        def __init__(
            self,
            message: str,
            *,
            command: str | None = None,
            exit_code: int | None = None,
            code: str | None = None,  # Will use ErrorCodes.CLI_COMMAND_ERROR
            context: Mapping[str, object] | None = None,
        ) -> None:
            """Initialize with CLI command context."""
            context_dict: dict[str, object] = dict(context) if context else {}
            if command is not None:
                context_dict["command"] = command
            if exit_code is not None:
                context_dict["exit_code"] = exit_code

            super().__init__(
                message,
                code=code,
                context=context_dict,
            )

    class ArgumentError(FlextExceptions.BaseError):
        """CLI argument validation errors with argument context."""

        def __init__(
            self,
            message: str,
            *,
            argument_name: str | None = None,
            argument_value: str | None = None,
            code: str | None = None,  # Will use ErrorCodes.CLI_ARGUMENT_ERROR
            context: Mapping[str, object] | None = None,
        ) -> None:
            """Initialize with CLI argument context."""
            context_dict: dict[str, object] = dict(context) if context else {}
            if argument_name is not None:
                context_dict["argument_name"] = argument_name
            if argument_value is not None:
                context_dict["argument_value"] = argument_value

            super().__init__(
                message,
                code=code,
                context=context_dict,
            )

    class FormatError(FlextExceptions.BaseError):
        """CLI formatting errors with format context."""

        def __init__(
            self,
            message: str,
            *,
            format_type: str | None = None,
            data_type: str | None = None,
            code: str | None = None,  # Will use ErrorCodes.CLI_FORMAT_ERROR
            context: Mapping[str, object] | None = None,
        ) -> None:
            """Initialize with CLI format context."""
            context_dict: dict[str, object] = dict(context) if context else {}
            if format_type is not None:
                context_dict["format_type"] = format_type
            if data_type is not None:
                context_dict["data_type"] = data_type

            super().__init__(
                message,
                code=code,
                context=context_dict,
            )

    class OutputError(FlextExceptions.BaseError):
        """CLI output errors with output context."""

        def __init__(
            self,
            message: str,
            *,
            output_format: str | None = None,
            output_path: str | None = None,
            code: str | None = None,  # Will use ErrorCodes.CLI_OUTPUT_ERROR
            context: Mapping[str, object] | None = None,
        ) -> None:
            """Initialize with CLI output context."""
            context_dict: dict[str, object] = dict(context) if context else {}
            if output_format is not None:
                context_dict["output_format"] = output_format
            if output_path is not None:
                context_dict["output_path"] = output_path

            super().__init__(
                message,
                code=code,
                context=context_dict,
            )

    class ContextError(FlextExceptions.BaseError):
        """CLI context errors with context state information."""

        def __init__(
            self,
            message: str,
            *,
            context_name: str | None = None,
            context_state: str | None = None,
            code: str | None = None,  # Will use ErrorCodes.CLI_CONTEXT_ERROR
            context: Mapping[str, object] | None = None,
        ) -> None:
            """Initialize with CLI context state."""
            context_dict: dict[str, object] = dict(context) if context else {}
            if context_name is not None:
                context_dict["context_name"] = context_name
            if context_state is not None:
                context_dict["context_state"] = context_state

            super().__init__(
                message,
                code=code,
                context=context_dict,
            )


# Direct exports for backward compatibility - all point to nested classes
FlextCliError = FlextCliExceptions.CliError
FlextCliErrorCodes = FlextCliExceptions.ErrorCodes
FlextCliValidationError = FlextCliExceptions.ValidationError
FlextCliConfigurationError = FlextCliExceptions.ConfigurationError
FlextCliConnectionError = FlextCliExceptions.CliConnectionError
FlextCliProcessingError = FlextCliExceptions.ProcessingError
FlextCliAuthenticationError = FlextCliExceptions.AuthenticationError
FlextCliTimeoutError = FlextCliExceptions.CliTimeoutError
FlextCliCommandError = FlextCliExceptions.CommandError
FlextCliArgumentError = FlextCliExceptions.ArgumentError
FlextCliFormatError = FlextCliExceptions.FormatError
FlextCliOutputError = FlextCliExceptions.OutputError
FlextCliContextError = FlextCliExceptions.ContextError


__all__: list[str] = [
    # Legacy compatibility exports (backward compatibility)
    "FlextCliArgumentError",
    "FlextCliAuthenticationError",
    "FlextCliCommandError",
    "FlextCliConfigurationError",
    "FlextCliConnectionError",
    "FlextCliContextError",
    "FlextCliError",
    "FlextCliErrorCodes",
    # CONSOLIDATED main class (new pattern)
    "FlextCliExceptions",
    "FlextCliFormatError",
    "FlextCliOutputError",
    "FlextCliProcessingError",
    "FlextCliTimeoutError",
    "FlextCliValidationError",
]
