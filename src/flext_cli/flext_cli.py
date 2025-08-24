"""FLEXT CLI Public Interface.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from pathlib import Path

from flext_core import get_logger

from flext_cli.api import (
    FlextCliApi,
    FlextCliContext,
    SessionSummary,
)
from flext_cli.cli_types import (
    FlextCliDataType,
    FlextCliOutputFormat,
)

# Global API instance
_api = FlextCliApi()


def flext_cli_export(
    data: FlextCliDataType,
    path: str | Path,
    format_type: FlextCliOutputFormat = FlextCliOutputFormat.JSON,
) -> bool:
    """Export data to file in specified format.

    Args:
      data: Data to export
      path: File path to write to
      format_type: Output format (json, yaml, csv, table, plain)

    Returns:
      True if export successful, False otherwise

    """
    return _api.flext_cli_export(data, path, format_type)


def flext_cli_format(
    data: FlextCliDataType,
    format_type: FlextCliOutputFormat = FlextCliOutputFormat.JSON,
) -> str:
    """Format data for display.

    Args:
      data: Data to format
      format_type: Output format (json, yaml, csv, table, plain)

    Returns:
      Formatted string representation

    """
    return _api.flext_cli_format(data, format_type)


def flext_cli_configure(config: dict[str, object]) -> bool:
    """Configure CLI service.

    Args:
      config: Configuration dictionary

    Returns:
      True if configuration successful, False otherwise

    """
    return _api.flext_cli_configure(config)


def flext_cli_health() -> dict[str, object]:
    """Get service health status.

    Returns:
      Health status dictionary

    """
    return _api.flext_cli_health()


def flext_cli_create_context(
    config: dict[str, object] | None = None,
) -> FlextCliContext:
    """Create CLI execution context.

    Args:
      config: Optional configuration dictionary

    Returns:
      CLI context object

    """
    result = _api.flext_cli_create_context(config)
    # Cast to expected type since API returns object
    if isinstance(result, FlextCliContext):
        return result

    # If not the expected type, this indicates a serious API issue
    logger = get_logger(__name__)
    result_type = type(result)
    logger.error(
        f"API returned unexpected type: {result_type}, expected FlextCliContext"
    )
    error_msg = (
        f"CLI context creation failed: got {result_type}, expected FlextCliContext"
    )
    raise TypeError(error_msg)


# Additional flext-cli functionality


def flext_cli_create_command(name: str, command_line: str, **options: object) -> bool:
    """Create command using shared API.

    Args:
      name: Command name
      command_line: Command line string
      **options: Additional command options

    Returns:
      True if command created successfully, False otherwise

    """
    # Use FlextResult's is_success for cleaner boolean conversion
    return _api.flext_cli_create_command(name, command_line, **options).is_success


def flext_cli_create_session(user_id: str | None = None) -> str:
    """Create session with auto-generated ID.

    Args:
      user_id: Optional user ID

    Returns:
      Session creation result message

    """
    result = _api.flext_cli_create_session(user_id)
    return result.unwrap_or("")


def flext_cli_register_handler(name: str, handler: object) -> bool:
    """Register handler using unified method.

    Args:
      name: Handler name
      handler: Handler function or callable

    Returns:
      True if handler registered successfully, False otherwise

    """
    # Use FlextResult's is_success for cleaner boolean conversion
    return _api.flext_cli_register_handler(name, handler).is_success


def flext_cli_register_plugin(name: str, plugin: object) -> bool:
    """Register plugin using unified method.

    Args:
      name: Plugin name
      plugin: Plugin instance

    Returns:
      True if plugin registered successfully, False otherwise

    """
    # Use FlextResult's is_success for cleaner boolean conversion
    return _api.flext_cli_register_plugin(name, plugin).is_success


def flext_cli_execute_handler(name: str, *args: object, **kwargs: object) -> object:
    """Execute handler using shared API.

    Args:
      name: Handler name
      *args: Positional arguments
      **kwargs: Keyword arguments

    Returns:
      Handler execution result or error dict

    """
    result = _api.flext_cli_execute_handler(name, *args, **kwargs)
    return result.unwrap_or({})


def flext_cli_render_with_context(
    data: FlextCliDataType,
    context: dict[str, object] | None = None,
) -> str:
    """Render with context.

    Args:
      data: Data to render
      context: Optional context dictionary

    Returns:
      Formatted string representation

    """
    result = _api.flext_cli_render_with_context(data, context)
    return result.unwrap_or("")


def flext_cli_get_commands() -> dict[str, object]:
    """Get all commands.

    Returns:
      Dictionary of all registered commands

    """
    return _api.flext_cli_get_commands()


def flext_cli_get_sessions() -> dict[str, SessionSummary]:
    """Get all sessions.

    Returns:
      Dictionary of all active sessions

    """
    return _api.flext_cli_get_sessions()


def flext_cli_get_plugins() -> dict[str, object]:
    """Get all plugins.

    Returns:
      Dictionary of all registered plugins

    """
    return _api.flext_cli_get_plugins()


def flext_cli_get_handlers() -> dict[str, object]:
    """Get all handlers.

    Returns:
      Dictionary of all registered handlers

    """
    return _api.flext_cli_get_handlers()
