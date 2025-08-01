"""Clean API implementation using service composition.

Single API class with all functionality, no duplication.
"""

from typing import Any

from flext_cli.core import FlextCliService
from flext_cli.types import (
    FlextCliConfig,
    FlextCliContext,
    FlextCliPlugin,
    TCliData,
    TCliFormat,
    TCliPath,
)
from flext_core.loggings import get_logger


class FlextCliApi:
    """Main API interface for FLEXT CLI operations."""

    def __init__(self) -> None:
        self.logger = get_logger(__name__)
        self._service = FlextCliService()
        self.logger.info("FlextCliApi initialized")

    def flext_cli_configure(self, config: dict) -> bool:
        """Configure the CLI service."""
        result = self._service.configure(config)
        if result.is_success:
            self.logger.info("CLI configured successfully")
            return True
        self.logger.error(f"Configuration failed: {result.error}")
        return False

    def flext_cli_export(
        self,
        data: TCliData,
        path: TCliPath,
        format_type: TCliFormat = "json",
    ) -> bool:
        """Export data to file."""
        result = self._service.flext_cli_export(data, path, format_type)
        return result.is_success

    def flext_cli_format(self, data: TCliData, format_type: TCliFormat = "json") -> str:
        """Format data for display."""
        result = self._service.flext_cli_format(data, format_type)
        if result.is_success:
            return result.unwrap()
        self.logger.error(f"Formatting failed: {result.error}")
        return str(data)

    def flext_cli_health(self) -> dict:
        """Get service health status."""
        result = self._service.flext_cli_health()
        if result.is_success:
            return result.unwrap()
        return {"status": "unhealthy", "error": result.error}

    def flext_cli_create_context(self, config: dict | None = None) -> FlextCliContext:
        """Create CLI execution context."""
        cli_config = FlextCliConfig(config or {})
        return FlextCliContext(cli_config)

    # RESTORED FROM BACKUP - All additional functionality

    def flext_cli_create_command(
        self,
        name: str,
        command_line: str,
        **options: dict[str, object],
    ) -> bool:
        """Create command using shared service."""
        result = self._service.flext_cli_create_command(name, command_line, **options)
        return result.is_success

    def flext_cli_create_session(self, user_id: str | None = None) -> str:
        """Create session with auto-generated ID."""
        result = self._service.flext_cli_create_session(user_id)
        return result.unwrap() if result.is_success else f"Error: {result.error}"

    def flext_cli_register_handler(self, name: str, handler) -> bool:
        """Register handler using unified method."""
        result = self._service.flext_cli_register_handler(name, handler)
        return result.is_success

    def flext_cli_register_plugin(self, name: str, plugin: FlextCliPlugin) -> bool:
        """Register plugin using unified method."""
        result = self._service.flext_cli_register_plugin(name, plugin)
        return result.is_success

    def flext_cli_execute_handler(
        self,
        name: str,
        *args: Any,
        **kwargs: Any,
    ) -> dict[str, object]:
        """Execute handler using shared service."""
        result = self._service.flext_cli_execute_handler(name, *args, **kwargs)
        return result.unwrap() if result.is_success else {"error": result.error}

    def flext_cli_render_with_context(
        self,
        data: Any,
        context: dict[str, object] | None = None,
    ) -> str:
        """Render with context."""
        result = self._service.flext_cli_render_with_context(data, context)
        return result.unwrap() if result.is_success else f"Error: {result.error}"

    def flext_cli_get_commands(self) -> dict:
        """Get all commands."""
        result = self._service.flext_cli_get_commands()
        return result.unwrap() if result.is_success else {}

    def flext_cli_get_sessions(self) -> dict:
        """Get all sessions."""
        result = self._service.flext_cli_get_sessions()
        return result.unwrap() if result.is_success else {}

    def flext_cli_get_plugins(self) -> dict:
        """Get all plugins."""
        result = self._service.flext_cli_get_plugins()
        return result.unwrap() if result.is_success else {}

    def flext_cli_get_handlers(self) -> dict:
        """Get all handlers."""
        result = self._service.flext_cli_get_handlers()
        return result.unwrap() if result.is_success else {}
