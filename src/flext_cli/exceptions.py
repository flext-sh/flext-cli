"""FLEXT CLI Exception Hierarchy - Domain-Specific Exceptions with flext-core.

This module provides a comprehensive exception hierarchy for FLEXT CLI operations,
inheriting from flext-core base exceptions with domain-specific context and
error handling patterns. Designed for precise error classification and
comprehensive error reporting.

Exception Categories:
    - FlextCliError: Base CLI exception with command context
    - FlextCliValidationError: Input validation and argument errors
    - FlextCliAuthenticationError: Authentication and authorization errors
    - FlextCliConfigurationError: Configuration and setup errors
    - FlextCliConnectionError: Service and network connection errors
    - FlextCliProcessingError: Command execution and processing errors
    - FlextCliTimeoutError: Operation timeout and cancellation errors
    - Specialized exceptions: Command, argument, format, output, context errors

Architecture:
    - Inherits from flext-core exception hierarchy
    - Domain-specific context information for debugging
    - Consistent error message formatting and structure
    - Integration with FlextResult error handling patterns
    - Rich error context for monitoring and diagnostics

Current Implementation Status:
    ✅ Complete exception hierarchy with flext-core inheritance
    ✅ Domain-specific exceptions with rich context
    ✅ Consistent error message formatting
    ✅ Context information for debugging and monitoring
    ✅ Integration with CLI command and argument handling
    ⚠️ Full functionality (TODO: Sprint 2 - enhance error recovery)

TODO (docs/TODO.md):
    Sprint 2: Add error recovery suggestions and help text
    Sprint 3: Add localization support for error messages
    Sprint 5: Add error analytics and reporting
    Sprint 7: Add error monitoring and alerting integration
    Sprint 8: Add interactive error handling and user guidance

Exception Features:
    - Rich context information (command, arguments, values)
    - Consistent error code assignment and categorization
    - Integration with logging and monitoring systems
    - User-friendly error messages with actionable information
    - Support for error recovery and retry mechanisms

Usage Examples:
    Validation error:
    >>> raise FlextCliValidationError(
    ...     "Invalid output format",
    ...     field="format",
    ...     value="invalid",
    ...     argument_name="--output"
    ... )

    Command error:
    >>> raise FlextCliCommandError(
    ...     "Command execution failed",
    ...     command="flext auth login",
    ...     exit_code=1
    ... )

    Configuration error:
    >>> raise FlextCliConfigurationError(
    ...     "Missing API URL",
    ...     config_key="api_url",
    ...     config_file="~/.flext/config.yaml"
    ... )

Integration:
    - Used throughout FLEXT CLI for consistent error handling
    - Integrates with FlextResult patterns for error propagation
    - Provides foundation for error monitoring and reporting
    - Supports CLI help systems and user guidance

Copyright (c) 2025 FLEXT Contributors
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core.exceptions import (
    FlextAuthenticationError,
    FlextConfigurationError,
    FlextConnectionError,
    FlextError,
    FlextProcessingError,
    FlextTimeoutError,
    FlextValidationError,
)


class FlextCliError(FlextError):
    """Base exception for CLI service operations."""

    def __init__(
        self,
        message: str = "CLI service error",
        command: str | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize CLI service error with context."""
        context = kwargs.copy()
        if command is not None:
            context["command"] = command

        super().__init__(message, error_code="CLI_SERVICE_ERROR", context=context)


class FlextCliValidationError(FlextValidationError):
    """CLI service validation errors."""

    def __init__(
        self,
        message: str = "CLI validation failed",
        field: str | None = None,
        value: object = None,
        argument_name: str | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize CLI validation error with context."""
        validation_details = {}
        if field is not None:
            validation_details["field"] = field
        if value is not None:
            validation_details["value"] = str(value)[:100]  # Truncate long values

        context = kwargs.copy()
        if argument_name is not None:
            context["argument_name"] = argument_name

        super().__init__(
            f"CLI validation: {message}",
            validation_details=(
                validation_details
                if validation_details is None
                else dict(validation_details)
            ),
            context=context,
        )


class FlextCliAuthenticationError(FlextAuthenticationError):
    """CLI service authentication errors."""

    def __init__(
        self,
        message: str = "CLI authentication failed",
        auth_method: str | None = None,
        username: str | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize CLI authentication error with context."""
        context = kwargs.copy()
        if auth_method is not None:
            context["auth_method"] = auth_method
        if username is not None:
            context["username"] = username

        super().__init__(f"CLI auth: {message}", **context)


class FlextCliConfigurationError(FlextConfigurationError):
    """CLI service configuration errors."""

    def __init__(
        self,
        message: str = "CLI configuration error",
        config_key: str | None = None,
        config_file: str | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize CLI configuration error with context."""
        context = kwargs.copy()
        if config_key is not None:
            context["config_key"] = config_key
        if config_file is not None:
            context["config_file"] = config_file

        super().__init__(f"CLI config: {message}", **context)


class FlextCliConnectionError(FlextConnectionError):
    """CLI service connection errors."""

    def __init__(
        self,
        message: str = "CLI connection failed",
        service_name: str | None = None,
        endpoint: str | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize CLI connection error with context."""
        context = kwargs.copy()
        if service_name is not None:
            context["service_name"] = service_name
        if endpoint is not None:
            context["endpoint"] = endpoint

        super().__init__(f"CLI connection: {message}", **context)


class FlextCliProcessingError(FlextProcessingError):
    """CLI service processing errors."""

    def __init__(
        self,
        message: str = "CLI processing failed",
        command: str | None = None,
        stage: str | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize CLI processing error with context."""
        context = kwargs.copy()
        if command is not None:
            context["command"] = command
        if stage is not None:
            context["stage"] = stage

        super().__init__(f"CLI processing: {message}", **context)


class FlextCliTimeoutError(FlextTimeoutError):
    """CLI service timeout errors."""

    def __init__(
        self,
        message: str = "CLI operation timed out",
        command: str | None = None,
        timeout_seconds: float | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize CLI timeout error with context."""
        context = kwargs.copy()
        if command is not None:
            context["command"] = command
        if timeout_seconds is not None:
            context["timeout_seconds"] = timeout_seconds

        super().__init__(f"CLI timeout: {message}", **context)


class FlextCliCommandError(FlextCliError):
    """CLI service command errors."""

    def __init__(
        self,
        message: str = "CLI command error",
        command: str | None = None,
        exit_code: int | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize CLI command error with context."""
        context = kwargs.copy()
        if exit_code is not None:
            context["exit_code"] = exit_code

        super().__init__(f"CLI command: {message}", command=command, **context)


class FlextCliArgumentError(FlextCliError):
    """CLI service argument errors."""

    def __init__(
        self,
        message: str = "CLI argument error",
        argument_name: str | None = None,
        argument_value: str | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize CLI argument error with context."""
        context = kwargs.copy()
        if argument_name is not None:
            context["argument_name"] = argument_name
        if argument_value is not None:
            context["argument_value"] = argument_value

        command = context.get("command")
        filtered_context = {k: v for k, v in context.items() if k != "command"}
        super().__init__(
            f"CLI argument: {message}",
            command=command if isinstance(command, str) else None,
            **filtered_context,
        )


class FlextCliFormatError(FlextCliError):
    """CLI service formatting errors."""

    def __init__(
        self,
        message: str = "CLI format error",
        format_type: str | None = None,
        data_type: str | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize CLI format error with context."""
        context = kwargs.copy()
        if format_type is not None:
            context["format_type"] = format_type
        if data_type is not None:
            context["data_type"] = data_type

        command = context.get("command")
        filtered_context = {k: v for k, v in context.items() if k != "command"}
        super().__init__(
            f"CLI format: {message}",
            command=command if isinstance(command, str) else None,
            **filtered_context,
        )


class FlextCliOutputError(FlextCliError):
    """CLI service output errors."""

    def __init__(
        self,
        message: str = "CLI output error",
        output_format: str | None = None,
        output_path: str | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize CLI output error with context."""
        context = kwargs.copy()
        if output_format is not None:
            context["output_format"] = output_format
        if output_path is not None:
            context["output_path"] = output_path

        command = context.get("command")
        filtered_context = {k: v for k, v in context.items() if k != "command"}
        super().__init__(
            f"CLI output: {message}",
            command=command if isinstance(command, str) else None,
            **filtered_context,
        )


class FlextCliContextError(FlextCliError):
    """CLI service context errors."""

    def __init__(
        self,
        message: str = "CLI context error",
        context_name: str | None = None,
        context_state: str | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize CLI context error with context."""
        context_dict = kwargs.copy()
        if context_name is not None:
            context_dict["context_name"] = context_name
        if context_state is not None:
            context_dict["context_state"] = context_state

        command = context_dict.get("command")
        filtered_context = {k: v for k, v in context_dict.items() if k != "command"}
        super().__init__(
            f"CLI context: {message}",
            command=command if isinstance(command, str) else None,
            **filtered_context,
        )


__all__ = [
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
