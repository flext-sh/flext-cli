"""Public interface for FLEXT CLI library.

Clean, simple functions for external use.
"""

from typing import Any

from flext_cli.api import FlextCliApi
from flext_cli.types import TCliData, TCliFormat, TCliPath

# Global API instance
_api = FlextCliApi()


def flext_cli_export(
    data: TCliData,
    path: TCliPath,
    format_type: TCliFormat = "json",
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


def flext_cli_format(data: TCliData, format_type: TCliFormat = "json") -> str:
    """Format data for display.

    Args:
        data: Data to format
        format_type: Output format (json, yaml, csv, table, plain)

    Returns:
        Formatted string representation

    """
    return _api.flext_cli_format(data, format_type)


def flext_cli_configure(config: dict) -> bool:
    """Configure CLI service.

    Args:
        config: Configuration dictionary

    Returns:
        True if configuration successful, False otherwise

    """
    return _api.flext_cli_configure(config)


def flext_cli_health() -> dict:
    """Get service health status.

    Returns:
        Health status dictionary

    """
    return _api.flext_cli_health()


def flext_cli_create_context(config: dict | None = None) -> Any:
    """Create CLI execution context.

    Args:
        config: Optional configuration dictionary

    Returns:
        CLI context object

    """
    return _api.flext_cli_create_context(config)


# RESTORED FROM BACKUP - All additional functionality


def flext_cli_create_command(name: str, command_line: str, **options: Any) -> bool:
    """Create command using shared API.

    Args:
        name: Command name
        command_line: Command line string
        **options: Additional command options

    Returns:
        True if command created successfully, False otherwise

    """
    return _api.flext_cli_create_command(name, command_line, **options)


def flext_cli_create_session(user_id: str | None = None) -> str:
    """Create session with auto-generated ID.

    Args:
        user_id: Optional user ID

    Returns:
        Session creation result message

    """
    return _api.flext_cli_create_session(user_id)


def flext_cli_register_handler(name: str, handler: Any) -> bool:
    """Register handler using unified method.

    Args:
        name: Handler name
        handler: Handler function or callable

    Returns:
        True if handler registered successfully, False otherwise

    """
    return _api.flext_cli_register_handler(name, handler)


def flext_cli_register_plugin(name: str, plugin: FlextCliPlugin) -> bool:
    """Register plugin using unified method.

    Args:
        name: Plugin name
        plugin: Plugin instance

    Returns:
        True if plugin registered successfully, False otherwise

    """
    return _api.flext_cli_register_plugin(name, plugin)


def flext_cli_execute_handler(name: str, *args: Any, **kwargs: Any) -> Any:
    """Execute handler using shared API.

    Args:
        name: Handler name
        *args: Positional arguments
        **kwargs: Keyword arguments

    Returns:
        Handler execution result or error dict

    """
    return _api.flext_cli_execute_handler(name, *args, **kwargs)


def flext_cli_render_with_context(
    data: Any,
    context: dict[str, Any] | None = None,
) -> str:
    """Render with context.

    Args:
        data: Data to render
        context: Optional context dictionary

    Returns:
        Formatted string representation

    """
    return _api.flext_cli_render_with_context(data, context)


def flext_cli_get_commands() -> dict[str, Any]:
    """Get all commands.

    Returns:
        Dictionary of all registered commands

    """
    return _api.flext_cli_get_commands()


def flext_cli_get_sessions() -> dict[str, Any]:
    """Get all sessions.

    Returns:
        Dictionary of all active sessions

    """
    return _api.flext_cli_get_sessions()


def flext_cli_get_plugins() -> dict[str, Any]:
    """Get all plugins.

    Returns:
        Dictionary of all registered plugins

    """
    return _api.flext_cli_get_plugins()


def flext_cli_get_handlers() -> dict[str, Any]:
    """Get all handlers.

    Returns:
        Dictionary of all registered handlers

    """
    return _api.flext_cli_get_handlers()
