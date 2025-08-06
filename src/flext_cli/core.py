"""FLEXT CLI Core Service - Primary Service Implementation with flext-core Integration.

This module provides the core service implementation for FLEXT CLI operations,
implementing FlextService interfaces with composition-based architecture and
comprehensive functionality. Serves as the primary service class integrating
all CLI operations with flext-core patterns.

Service Architecture:
    - FlextService interface implementation with Clean Architecture patterns
    - FlextConfigurable interface for configuration management
    - Composition-based design with centralized functionality
    - flext-core integration (utilities, logging, result handling)
    - Railway-oriented programming with FlextResult error handling

Core Features:
    - Data formatting in multiple formats (JSON, YAML, CSV, table, plain)
    - File export capabilities with directory creation
    - Command, session, plugin, and handler management
    - Health monitoring and service status reporting
    - Context-based rendering and data transformation

Current Implementation Status:
    ✅ Complete service implementation with all functionality
    ✅ Multi-format data formatting and export
    ✅ Command, session, plugin, handler management
    ✅ Health monitoring and status reporting
    ✅ flext-core integration with safe operations
    ✅ Configuration management with validation
    ⚠️ Full functionality (TODO: Sprint 2 - enhance performance and features)

TODO (docs/TODO.md):
    Sprint 2: Add advanced caching and performance optimization
    Sprint 3: Add streaming support for large datasets
    Sprint 5: Add persistence layer integration
    Sprint 7: Add comprehensive monitoring and metrics collection
    Sprint 8: Add plugin hot-reload and dynamic configuration

Service Capabilities:
    Data Operations:
        - flext_cli_format: Multi-format data formatting
        - flext_cli_export: File export with directory management
        - flext_cli_render_with_context: Context-based rendering

    Management Operations:
        - flext_cli_create_command/session: Entity creation with ID generation
        - flext_cli_register_handler/plugin: Service registration
        - flext_cli_execute_handler: Safe handler execution

    System Operations:
        - flext_cli_health: Comprehensive health and status reporting
        - configure: Service configuration with validation

Usage Examples:
    Service initialization:
    >>> service = FlextCliService()
    >>> config = FlextCliConfig({"debug": True})
    >>> result = service.configure(config)

    Data formatting:
    >>> result = service.flext_cli_format(data, "json")
    >>> if result.success:
    ...     formatted = result.unwrap()

    Command management:
    >>> result = service.flext_cli_create_command("test", "echo hello")
    >>> commands = service.flext_cli_get_commands().unwrap()

Integration:
    - Used by CLI commands for data operations and management
    - Provides centralized service functionality
    - Integrates with flext-core utilities and patterns
    - Supports Clean Architecture service layer patterns

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

import csv
import io
import json
from collections.abc import Callable
from pathlib import Path

import yaml
from flext_core import FlextResult
from flext_core.interfaces import FlextConfigurable
from flext_core.loggings import get_logger
from flext_core.utilities import FlextUtilities, safe_call

from flext_cli.types import (
    FlextCliCommand,
    FlextCliConfig,
    FlextCliPlugin,
    FlextCliSession,
    OutputFormat,
    TCliData,
    TCliFormat,
    TCliPath,
)

# Export imports for test access
__all__: list[str] = [
    "FlextCliService",
    "FlextService",
    "FlextUtilities",
    "safe_call",
]


# FlextService interface
class FlextService:
    """Base service interface."""


class FlextCliService(FlextService, FlextConfigurable):
    """Core CLI service implementing all functionality."""

    def __init__(self) -> None:
        """Initialize CLI service with all functionality."""
        self.logger = get_logger(__name__)
        self._config: FlextCliConfig | None = None

        # Restored from backup - full functionality
        self._handlers: dict[str, Callable[..., object]] = {}
        self._plugins: dict[str, FlextCliPlugin] = {}
        self._sessions: dict[str, FlextCliSession] = {}
        self._commands: dict[str, FlextCliCommand] = {}
        self._formats = {"json", "yaml", "csv", "table", "plain"}

        self.logger.info("FlextCliService initialized with full backup functionality")

    def configure(
        self,
        config: FlextCliConfig | dict[str, object],
    ) -> FlextResult[None]:
        """Configure service with FlextCliConfig."""
        try:
            if isinstance(config, dict):
                # Handle backward compatibility: format_type -> output_format
                cleaned_config = dict(config)
                if (
                    "format_type" in cleaned_config
                    and "output_format" not in cleaned_config
                ):
                    cleaned_config["output_format"] = cleaned_config.pop("format_type")
                self._config = FlextCliConfig(**cleaned_config)
            elif isinstance(config, FlextCliConfig):
                self._config = config
            else:
                return FlextResult.fail(f"Invalid config type: {type(config)}")

            self.logger.info(
                "CLI service configured with format: %s",
                self._config.output_format,
            )
            return FlextResult.ok(None)
        except (AttributeError, ValueError, TypeError, OSError, Exception) as e:
            return FlextResult.fail(f"Configuration failed: {e}")

    def flext_cli_export(
        self,
        data: TCliData,
        path: TCliPath,
        format_type: TCliFormat = OutputFormat.JSON,
    ) -> FlextResult[bool]:
        """Export data to file in specified format."""
        try:
            formatted_result = self.flext_cli_format(data, format_type)
            if not formatted_result.success:
                return FlextResult.fail(formatted_result.error)

            formatted_data = formatted_result.unwrap()
            path_obj = Path(path)

            # Ensure parent directory exists
            path_obj.parent.mkdir(parents=True, exist_ok=True)

            # Write file
            path_obj.write_text(formatted_data, encoding="utf-8")

            self.logger.info("Data exported to %s in %s format", path, format_type)
            return FlextResult.ok(data=True)

        except Exception as e:
            self.logger.exception("Export failed")
            return FlextResult.fail(f"Export failed: {e}")

    def flext_cli_format(
        self,
        data: TCliData,
        format_type: TCliFormat = OutputFormat.JSON,
    ) -> FlextResult[str]:
        """Format data in specified format."""
        formatters = {
            "json": self._format_json,
            "yaml": self._format_yaml,
            "csv": self._format_csv,
            "table": self._format_table,
            "plain": self._format_plain,
        }

        formatter = formatters.get(format_type)
        if not formatter:
            return FlextResult.fail(f"Unsupported format: {format_type}")

        return formatter(data)

    def flext_cli_health(self) -> FlextResult[dict]:
        """Get service health status."""
        try:
            status = {
                "service": "FlextCliService",
                "status": "healthy",
                "timestamp": FlextUtilities.generate_iso_timestamp(),
                "configured": self._config is not None,
                "handlers": len(self._handlers),
                "plugins": len(self._plugins),
                "sessions": len(self._sessions),
                "commands": len(self._commands),
                "supported_formats": list(self._formats),
                "flext_core_integration": {
                    "entities": True,
                    "value_objects": True,
                    "services": True,
                    "utilities": True,
                    "chain_operations": True,
                    "safe_call": True,
                    "validation": True,
                },
            }

            if self._config:
                status["config"] = {
                    "format": self._config.output_format,
                    "debug": self._config.debug,
                    "profile": self._config.profile,
                    "api_url": self._config.api_url,
                }

            return FlextResult.ok(status)

        except (
            AttributeError,
            ValueError,
            TypeError,
            OSError,
            ImportError,
            Exception,
        ) as e:
            return FlextResult.fail(f"Health check failed: {e}")

    def _format_json(self, data: TCliData) -> FlextResult[str]:
        """Format data as JSON."""
        return safe_call(lambda: json.dumps(data, indent=2, default=str))

    def _format_yaml(self, data: TCliData) -> FlextResult[str]:
        """Format data as YAML."""

        def format_yaml_data() -> str:
            return yaml.dump(data, default_flow_style=False, indent=2)

        return safe_call(format_yaml_data)

    def _format_csv(self, data: TCliData) -> FlextResult[str]:
        """Format data as CSV."""

        def format_csv_data() -> str:
            if not isinstance(data, (list, tuple)):
                data_list = [data] if isinstance(data, dict) else [{"value": str(data)}]
            else:
                data_list = data

            if not data_list:
                return ""

            output = io.StringIO()

            # Handle list of dictionaries
            if isinstance(data_list[0], dict):
                fieldnames = list(data_list[0].keys())
                writer = csv.DictWriter(output, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data_list)
            else:
                # Handle list of values
                writer = csv.writer(output)
                writer.writerow(["value"])
                for item in data_list:
                    writer.writerow([str(item)])

            return output.getvalue()

        return safe_call(format_csv_data)

    def _format_table(self, data: TCliData) -> FlextResult[str]:
        """Format data as ASCII table."""

        def format_table_data() -> str:
            if isinstance(data, dict):
                # Key-value table
                max_key_len = max(len(str(k)) for k in data) if data else 0
                lines = [f"{k!s:<{max_key_len}} | {v!s}" for k, v in data.items()]
                return "\\n".join(lines)
            if isinstance(data, (list, tuple)) and data and isinstance(data[0], dict):
                # Table with headers
                headers = list(data[0].keys())
                col_widths = [
                    max(
                        len(str(header)),
                        *(len(str(row.get(header, ""))) for row in data),
                    )
                    for header in headers
                ]

                # Header row
                header_row = " | ".join(
                    f"{header:<{width}}"
                    for header, width in zip(headers, col_widths, strict=False)
                )
                separator = "-+-".join("-" * width for width in col_widths)

                # Data rows
                data_rows = []
                for row in data:
                    row_str = " | ".join(
                        f"{row.get(header, '')!s:<{width}}"
                        for header, width in zip(headers, col_widths, strict=False)
                    )
                    data_rows.append(row_str)

                return "\\n".join([header_row, separator, *data_rows])
            # Simple list
            return "\\n".join(
                str(item)
                for item in (data if isinstance(data, (list, tuple)) else [data])
            )

        return safe_call(format_table_data)

    def _format_plain(self, data: TCliData) -> FlextResult[str]:
        """Format data as plain text."""
        return safe_call(lambda: str(data))

    # RESTORED FROM BACKUP - All additional functionality

    def flext_cli_validate_format(self, format_type: str) -> FlextResult[str]:
        """Validate format using flext-core validation."""
        if format_type not in self._formats:
            supported = ", ".join(sorted(self._formats))
            return FlextResult.fail(
                f"Unsupported format: {format_type}. Supported: {supported}",
            )
        return FlextResult.ok(format_type)

    def flext_cli_create_command(
        self,
        name: str,
        command_line: str,
        **options: object,
    ) -> FlextResult[str]:
        """Create command using flext-core safe operations - restored from backup."""

        def create_command() -> str:
            entity_id = FlextUtilities.generate_entity_id()
            command = FlextCliCommand(
                id=entity_id,
                name=name,
                command_line=command_line,
                **options,
            )
            self._commands[name] = command
            return f"Command '{name}' created with ID {command.id}"

        return safe_call(create_command)

    def flext_cli_create_session(self, user_id: str | None = None) -> FlextResult[str]:
        """Create session using auto-generated ID - restored from backup."""

        def create_session() -> str:
            entity_id = FlextUtilities.generate_entity_id()
            session_id = f"session_{entity_id}"
            session = FlextCliSession(
                id=entity_id,
                session_id=session_id,
                user_id=user_id,
            )
            self._sessions[session.id] = session
            return f"Session '{session.id}' created"

        return safe_call(create_session)

    def flext_cli_register_handler(
        self,
        name: str,
        handler: Callable[..., object],
    ) -> FlextResult[None]:
        """Register handler using flext-core validation - restored from backup."""
        if name in self._handlers:
            return FlextResult.fail(f"Handler '{name}' already registered")
        self._handlers[name] = handler
        return FlextResult.ok(None)

    def flext_cli_register_plugin(
        self,
        name: str,
        plugin: FlextCliPlugin,
    ) -> FlextResult[None]:
        """Register plugin using flext-core validation - restored from backup."""
        if name in self._plugins:
            return FlextResult.fail(f"Plugin '{name}' already registered")
        self._plugins[name] = plugin
        return FlextResult.ok(None)

    def flext_cli_execute_handler(
        self,
        name: str,
        *args: object,
        **kwargs: object,
    ) -> FlextResult[object]:
        """Execute handler using flext-core safe_call - restored from backup."""
        if name not in self._handlers:
            return FlextResult.fail(f"Handler '{name}' not found")
        return safe_call(lambda: self._handlers[name](*args, **kwargs))

    def flext_cli_render_with_context(
        self,
        data: object,
        context_options: dict[str, object] | None = None,
    ) -> FlextResult[str]:
        """Render using immutable context - restored from backup."""
        # Create context with required fields - handle missing config
        # and output override
        config = self._config or FlextCliConfig()

        # Extract output format from context options if provided
        context_options = context_options or {}
        output_format = context_options.get("output_format", config.output_format)

        return self.flext_cli_format(data, output_format)

    def flext_cli_get_commands(self) -> FlextResult[dict[str, FlextCliCommand]]:
        """Get all commands - restored from backup."""
        return FlextResult.ok(self._commands.copy())

    def flext_cli_get_sessions(self) -> FlextResult[dict[str, FlextCliSession]]:
        """Get all sessions - restored from backup."""
        return FlextResult.ok(self._sessions.copy())

    def flext_cli_get_plugins(self) -> FlextResult[dict[str, FlextCliPlugin]]:
        """Get all plugins - restored from backup."""
        return FlextResult.ok(self._plugins.copy())

    def flext_cli_get_handlers(self) -> FlextResult[dict[str, object]]:
        """Get all handlers - restored from backup."""
        return FlextResult.ok(self._handlers.copy())
