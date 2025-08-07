"""FLEXT CLI Public Interface - Legacy Compatibility and Simple Function API.

This module provides a simplified public interface for FLEXT CLI library,
offering clean, simple functions for external use and backward compatibility.
Acts as a facade over the main FlextCliApi implementation for easy integration.

Interface Categories:
    - Data Operations: Export, formatting, and rendering functions
    - Configuration: Service configuration and health monitoring
    - Context Management: CLI execution context creation and management
    - Command Management: Command, session, plugin, handler registration
    - System Operations: Health checks and service status

Architecture:
    - Facade pattern over FlextCliApi for simplified access
    - Backward compatibility for legacy integrations
    - Error handling with graceful degradation
    - Type safety with proper error propagation
    - Global API instance for stateful operations

Current Implementation Status:
    ✅ Complete public interface with all operations
    ✅ FlextCliApi integration with error handling
    ✅ Context creation and management functions
    ✅ Command, session, plugin, handler registration
    ✅ Data export, formatting, and rendering
    ✅ Health monitoring and service status
    ⚠️ Legacy compatibility layer (TODO: Sprint 3 - modernize interface)

TODO (docs/TODO.md):
    Sprint 3: Modernize interface with async support
    Sprint 3: Add type safety improvements and validation
    Sprint 5: Add comprehensive error recovery and fallbacks
    Sprint 7: Add performance monitoring and metrics integration
    Sprint 8: Add interactive features and user guidance

Public Functions:
    Data Operations:
        - flext_cli_export: Export data to files in multiple formats
        - flext_cli_format: Format data for display and output
        - flext_cli_render_with_context: Context-based rendering

    System Operations:
        - flext_cli_configure: Service configuration
        - flext_cli_health: Health status and monitoring
        - flext_cli_create_context: CLI execution context creation

    Management Operations:
        - flext_cli_create_command/session: Entity creation
        - flext_cli_register_handler/plugin: Service registration
        - flext_cli_get_commands/sessions/plugins/handlers: Registry access

Usage Examples:
    Basic data operations:
    >>> flext_cli_configure({"debug": True})
    >>> formatted = flext_cli_format(data, "json")
    >>> flext_cli_export(data, "output.json", "json")

    Context management:
    >>> context = flext_cli_create_context({"output_format": "table"})
    >>> health = flext_cli_health()

    Registration operations:
    >>> flext_cli_register_handler("my_handler", handler_func)
    >>> commands = flext_cli_get_commands()

Integration:
    - Used by external applications for FLEXT CLI integration
    - Provides backward compatibility for existing code
    - Acts as facade over complex FlextCliApi implementation
    - Supports simple function-based interface patterns

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core import get_logger
from rich.console import Console

from flext_cli.api import FlextCliApi
from flext_cli.types import (
    FlextCliConfig,
    FlextCliContext,
    OutputFormat,
)

if TYPE_CHECKING:
    from flext_cli.types import (
        FlextCliPlugin,
        TCliData,
        TCliFormat,
        TCliPath,
    )

# Global API instance
_api = FlextCliApi()


def flext_cli_export(
    data: TCliData,
    path: TCliPath,
    format_type: TCliFormat = OutputFormat.JSON,
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
    data: TCliData, format_type: TCliFormat = OutputFormat.JSON,
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
    try:
        if isinstance(result, FlextCliContext):
            return result
    except TypeError as e:
        # Handle cases where isinstance fails due to import issues
        logger = get_logger(__name__)
        logger.warning(f"Type checking failed for FlextCliContext: {e}")
    # Create fallback context if cast fails
    cli_config = FlextCliConfig()
    if config:
        cli_config = cli_config.model_copy(update=config)
    return FlextCliContext(config=cli_config, console=Console())


# RESTORED FROM BACKUP - All additional functionality


def flext_cli_create_command(name: str, command_line: str, **options: object) -> bool:
    """Create command using shared API.

    Args:
        name: Command name
        command_line: Command line string
        **options: Additional command options

    Returns:
        True if command created successfully, False otherwise

    """
    result = _api.flext_cli_create_command(name, command_line, **options)
    return result.success if hasattr(result, "success") else False


def flext_cli_create_session(user_id: str | None = None) -> str:
    """Create session with auto-generated ID.

    Args:
        user_id: Optional user ID

    Returns:
        Session creation result message

    """
    result = _api.flext_cli_create_session(user_id)
    return result.unwrap() if hasattr(result, "unwrap") and result.success else ""


def flext_cli_register_handler(name: str, handler: object) -> bool:
    """Register handler using unified method.

    Args:
        name: Handler name
        handler: Handler function or callable

    Returns:
        True if handler registered successfully, False otherwise

    """
    result = _api.flext_cli_register_handler(name, handler)
    return result.success if hasattr(result, "success") else False


def flext_cli_register_plugin(name: str, plugin: FlextCliPlugin) -> bool:
    """Register plugin using unified method.

    Args:
        name: Plugin name
        plugin: Plugin instance

    Returns:
        True if plugin registered successfully, False otherwise

    """
    result = _api.flext_cli_register_plugin(name, plugin)
    return result.success if hasattr(result, "success") else False


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
    return result.unwrap() if hasattr(result, "unwrap") and result.success else {}


def flext_cli_render_with_context(
    data: object,
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
    return result.unwrap() if hasattr(result, "unwrap") and result.success else ""


def flext_cli_get_commands() -> dict[str, object]:
    """Get all commands.

    Returns:
        Dictionary of all registered commands

    """
    return _api.flext_cli_get_commands()


def flext_cli_get_sessions() -> dict[str, object]:
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
