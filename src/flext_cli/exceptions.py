"""CLI Exception Hierarchy."""

from __future__ import annotations

from flext_core import FlextError


# Base CLI exception hierarchy following flext-core patterns
class FlextCliError(FlextError):
    """Base exception for CLI operations."""

    def __init__(
        self,
        message: str = "CLI error",
        error_code: str | None = "CLI_ERROR",
        context: dict[str, object] | None = None,
    ) -> None:
        """Initialize CLI error with context."""
        super().__init__(
            message=message,
            error_code=error_code,
            context=context,
        )


class FlextCliValidationError(FlextCliError):
    """CLI validation errors."""

    def __init__(
        self,
        message: str = "CLI validation error",
        error_code: str | None = "CLI_VALIDATION_ERROR",
        context: dict[str, object] | None = None,
    ) -> None:
        """Initialize CLI validation error."""
        super().__init__(
            message=message,
            error_code=error_code,
            context=context,
        )


class FlextCliConfigurationError(FlextCliError):
    """CLI configuration errors."""

    def __init__(
        self,
        message: str = "CLI configuration error",
        error_code: str | None = "CLI_CONFIGURATION_ERROR",
        context: dict[str, object] | None = None,
    ) -> None:
        """Initialize CLI configuration error."""
        super().__init__(
            message=message,
            error_code=error_code,
            context=context,
        )


class FlextCliConnectionError(FlextCliError):
    """CLI connection errors."""

    def __init__(
        self,
        message: str = "CLI connection error",
        error_code: str | None = "CLI_CONNECTION_ERROR",
        context: dict[str, object] | None = None,
    ) -> None:
        """Initialize CLI connection error."""
        super().__init__(
            message=message,
            error_code=error_code,
            context=context,
        )


class FlextCliProcessingError(FlextCliError):
    """CLI processing errors."""

    def __init__(
        self,
        message: str = "CLI processing error",
        error_code: str | None = "CLI_PROCESSING_ERROR",
        context: dict[str, object] | None = None,
    ) -> None:
        """Initialize CLI processing error."""
        super().__init__(
            message=message,
            error_code=error_code,
            context=context,
        )


class FlextCliAuthenticationError(FlextCliError):
    """CLI authentication errors."""

    def __init__(
        self,
        message: str = "CLI authentication error",
        error_code: str | None = "CLI_AUTHENTICATION_ERROR",
        context: dict[str, object] | None = None,
    ) -> None:
        """Initialize CLI authentication error."""
        super().__init__(
            message=message,
            error_code=error_code,
            context=context,
        )


class FlextCliTimeoutError(FlextCliError):
    """CLI timeout errors."""

    def __init__(
        self,
        message: str = "CLI timeout error",
        error_code: str | None = "CLI_TIMEOUT_ERROR",
        context: dict[str, object] | None = None,
    ) -> None:
        """Initialize CLI timeout error."""
        super().__init__(
            message=message,
            error_code=error_code,
            context=context,
        )


# Domain-specific exceptions for CLI business logic
# =============================================================================
# REFACTORING: Template Method Pattern - eliminates massive duplication
# =============================================================================


class FlextCliCommandError(FlextCliError):
    """CLI service command errors using DRY foundation."""

    def __init__(
        self,
        message: str = "CLI command error",
        command: str | None = None,
        exit_code: int | None = None,
        error_code: str | None = "CLI_COMMAND_ERROR",
        context: dict[str, object] | None = None,
    ) -> None:
        """Initialize CLI command error with context."""
        context_dict = context or {}
        if command is not None:
            context_dict["command"] = command
        if exit_code is not None:
            context_dict["exit_code"] = exit_code

        super().__init__(
            message=f"CLI command: {message}",
            error_code=error_code,
            context=context_dict,
        )


class FlextCliArgumentError(FlextCliError):
    """CLI service argument errors using DRY foundation."""

    def __init__(
        self,
        message: str = "CLI argument error",
        argument_name: str | None = None,
        argument_value: str | None = None,
        error_code: str | None = "CLI_ARGUMENT_ERROR",
        context: dict[str, object] | None = None,
    ) -> None:
        """Initialize CLI argument error with context."""
        context_dict = context or {}
        if argument_name is not None:
            context_dict["argument_name"] = argument_name
        if argument_value is not None:
            context_dict["argument_value"] = argument_value

        super().__init__(
            message=f"CLI argument: {message}",
            error_code=error_code,
            context=context_dict,
        )


class FlextCliFormatError(FlextCliError):
    """CLI service formatting errors using DRY foundation."""

    def __init__(
        self,
        message: str = "CLI format error",
        format_type: str | None = None,
        data_type: str | None = None,
        error_code: str | None = "CLI_FORMAT_ERROR",
        context: dict[str, object] | None = None,
    ) -> None:
        """Initialize CLI format error with context."""
        context_dict = context or {}
        if format_type is not None:
            context_dict["format_type"] = format_type
        if data_type is not None:
            context_dict["data_type"] = data_type

        super().__init__(
            message=f"CLI format: {message}",
            error_code=error_code,
            context=context_dict,
        )


class FlextCliOutputError(FlextCliError):
    """CLI service output errors using DRY foundation."""

    def __init__(
        self,
        message: str = "CLI output error",
        output_format: str | None = None,
        output_path: str | None = None,
        error_code: str | None = "CLI_OUTPUT_ERROR",
        context: dict[str, object] | None = None,
    ) -> None:
        """Initialize CLI output error with context."""
        context_dict = context or {}
        if output_format is not None:
            context_dict["output_format"] = output_format
        if output_path is not None:
            context_dict["output_path"] = output_path

        super().__init__(
            message=f"CLI output: {message}",
            error_code=error_code,
            context=context_dict,
        )


class FlextCliContextError(FlextCliError):
    """CLI service context errors using DRY foundation."""

    def __init__(
        self,
        message: str = "CLI context error",
        context_name: str | None = None,
        context_state: str | None = None,
        error_code: str | None = "CLI_CONTEXT_ERROR",
        context: dict[str, object] | None = None,
    ) -> None:
        """Initialize CLI context error with context."""
        context_dict = context or {}
        if context_name is not None:
            context_dict["context_name"] = context_name
        if context_state is not None:
            context_dict["context_state"] = context_state

        super().__init__(
            message=f"CLI context: {message}",
            error_code=error_code,
            context=context_dict,
        )


__all__: list[str] = [
    "FlextCliArgumentError",
    "FlextCliAuthenticationError",
    "FlextCliCommandError",
    "FlextCliConfigurationError",
    "FlextCliConnectionError",
    "FlextCliContextError",
    "FlextCliError",
    "FlextCliFormatError",
    "FlextCliOutputError",
    "FlextCliProcessingError",
    "FlextCliTimeoutError",
    "FlextCliValidationError",
]
