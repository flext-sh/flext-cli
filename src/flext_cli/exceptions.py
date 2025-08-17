"""CLI Exception Hierarchy - Modern Pydantic v2 Patterns.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Mapping
from enum import Enum

from flext_core import FlextError


class FlextCliErrorCodes(Enum):
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


# Base CLI exception hierarchy following flext-core FlextError pattern
class FlextCliError(FlextError):
    """Base exception for all CLI domain errors."""


class FlextCliValidationError(FlextCliError):
    """CLI validation errors."""


class FlextCliConfigurationError(FlextCliError):
    """CLI configuration errors."""


class FlextCliConnectionError(FlextCliError):
    """CLI connection errors."""


class FlextCliProcessingError(FlextCliError):
    """CLI processing errors."""


class FlextCliAuthenticationError(FlextCliError):
    """CLI authentication errors."""


class FlextCliTimeoutError(FlextCliError):
    """CLI timeout errors."""


# Domain-specific exceptions for CLI business logic
# Using modern FlextError pattern with context support


class FlextCliCommandError(FlextCliError):
    """CLI command execution errors with command context."""

    def __init__(
      self,
      message: str,
      *,
      command: str | None = None,
      exit_code: int | None = None,
      code: FlextCliErrorCodes | None = FlextCliErrorCodes.CLI_COMMAND_ERROR,
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


class FlextCliArgumentError(FlextCliError):
    """CLI argument validation errors with argument context."""

    def __init__(
      self,
      message: str,
      *,
      argument_name: str | None = None,
      argument_value: str | None = None,
      code: FlextCliErrorCodes | None = FlextCliErrorCodes.CLI_ARGUMENT_ERROR,
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


class FlextCliFormatError(FlextCliError):
    """CLI formatting errors with format context."""

    def __init__(
      self,
      message: str,
      *,
      format_type: str | None = None,
      data_type: str | None = None,
      code: FlextCliErrorCodes | None = FlextCliErrorCodes.CLI_FORMAT_ERROR,
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


class FlextCliOutputError(FlextCliError):
    """CLI output errors with output context."""

    def __init__(
      self,
      message: str,
      *,
      output_format: str | None = None,
      output_path: str | None = None,
      code: FlextCliErrorCodes | None = FlextCliErrorCodes.CLI_OUTPUT_ERROR,
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


class FlextCliContextError(FlextCliError):
    """CLI context errors with context state information."""

    def __init__(
      self,
      message: str,
      *,
      context_name: str | None = None,
      context_state: str | None = None,
      code: FlextCliErrorCodes | None = FlextCliErrorCodes.CLI_CONTEXT_ERROR,
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


__all__: list[str] = [
    # Base exceptions (alphabetical)
    "FlextCliArgumentError",
    "FlextCliAuthenticationError",
    "FlextCliCommandError",
    "FlextCliConfigurationError",
    "FlextCliConnectionError",
    "FlextCliContextError",
    "FlextCliError",
    # Error codes enum
    "FlextCliErrorCodes",
    "FlextCliFormatError",
    "FlextCliOutputError",
    "FlextCliProcessingError",
    "FlextCliTimeoutError",
    "FlextCliValidationError",
]
