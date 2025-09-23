"""CLI core service using flext-core directly.

Production-ready CLI service that uses flext-core services directly without
duplication or fallback mechanisms. Implements standardized architecture patterns.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import csv
import json
from collections.abc import Callable
from datetime import UTC, datetime
from io import StringIO
from pathlib import Path
from uuid import uuid4

import yaml

from flext_cli.models import FlextCliModels
from flext_core import (
    FlextContainer,
    FlextLogger,
    FlextResult,
    FlextService,
    FlextTypes,
)

# Type aliases for cleaner code
type HandlerData = (
    dict[str, str | int | float | bool]
    | list[dict[str, str | int | float | bool]]
    | str
    | int
    | float
    | bool
)
type HandlerFunction = Callable[[HandlerData], HandlerData]


class FlextCliService(FlextService[FlextTypes.Core.Dict]):
    """Essential CLI service using flext-core directly.

    Provides CLI configuration management using flext-core patterns.
    No over-engineered abstractions or unused functionality.
    """

    def __init__(self) -> None:
        """Initialize CLI service with flext-core dependencies."""
        super().__init__()
        self._logger = FlextLogger(__name__)
        self._container = FlextContainer.get_global()
        self._cli_config = FlextCliModels.FlextCliConfig.create_default()
        self._handlers: dict[str, HandlerFunction] = {}
        self._plugins: dict[str, FlextCliModels.CliCommand] = {}
        self._sessions: dict[str, FlextCliModels.CliSession] = {}
        self._commands: dict[str, FlextCliModels.CliCommand] = {}
        self._formatters = FlextCliModels.CliFormatters()

    def execute(self) -> FlextResult[FlextTypes.Core.Dict]:
        """Execute CLI service - required by FlextService."""
        self._logger.info("CLI service operational")
        return FlextResult[FlextTypes.Core.Dict].ok({
            "status": "operational",
            "service": "FlextCliService",
        })

    def start(self) -> FlextResult[None]:
        """Start the CLI service."""
        self._logger.info("Starting FlextCliService")
        return FlextResult[None].ok(None)

    def stop(self) -> FlextResult[None]:
        """Stop the CLI service."""
        self._logger.info("Stopping FlextCliService")
        return FlextResult[None].ok(None)

    def health_check(self) -> FlextResult[str]:
        """Check service health."""
        return FlextResult[str].ok("healthy")

    def get_config(self) -> FlextCliModels.FlextCliConfig | None:
        """Get current CLI configuration."""
        return self._cli_config

    def configure(
        self,
        config: FlextCliModels.FlextCliConfig | dict[str, str | int | float | bool],
    ) -> FlextResult[None]:
        """Configure the service."""
        if isinstance(config, dict):
            # Convert dict to FlextCliConfig
            try:
                # Extract and validate values for FlextCliConfig
                profile_value = config.get("profile", "default")
                output_format_value = config.get("output_format", "table")
                debug_mode_value = config.get("debug_mode", False)

                # Ensure proper types
                if not isinstance(profile_value, str):
                    profile_value = str(profile_value)
                if not isinstance(output_format_value, str):
                    output_format_value = str(output_format_value)
                if not isinstance(debug_mode_value, bool):
                    debug_mode_value = bool(debug_mode_value)

                self._cli_config = FlextCliModels.FlextCliConfig(
                    profile=profile_value,
                    output_format=output_format_value,
                    debug_mode=debug_mode_value,
                )
            except Exception as e:
                return FlextResult[None].fail(f"Invalid configuration: {e}")
        else:
            self._cli_config = config
        return FlextResult[None].ok(None)

    def get_handlers(self) -> dict[str, HandlerFunction]:
        """Get registered handlers."""
        return self._handlers.copy()

    def get_plugins(self) -> dict[str, FlextCliModels.CliCommand]:
        """Get registered plugins."""
        return self._plugins.copy()

    def get_sessions(self) -> dict[str, FlextCliModels.CliSession]:
        """Get active sessions."""
        return self._sessions.copy()

    def get_commands(self) -> dict[str, FlextCliModels.CliCommand]:
        """Get registered commands."""
        return self._commands.copy()

    def get_formatters(self) -> FlextCliModels.CliFormatters:
        """Get formatters instance."""
        return self._formatters

    def format_data(self, data: HandlerData, format_type: str) -> FlextResult[str]:
        """Format data using specified format type."""
        try:
            if format_type == "json":
                formatted = json.dumps(data, indent=2, default=str)
            elif format_type == "yaml":
                formatted = yaml.dump(data, default_flow_style=False)
            elif format_type == "csv":
                # Type narrowing: data must be list[dict] for CSV format
                if not isinstance(data, list):
                    return FlextResult[str].fail(
                        "CSV format requires list of dictionaries"
                    )
                csv_data = (
                    data  # data is already list[dict[str, str | int | float | bool]]
                )
                if not csv_data:
                    return FlextResult[str].fail("No valid dictionary data found")
                output = StringIO()
                fieldnames = list(csv_data[0].keys())
                writer = csv.DictWriter(output, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(csv_data)
                formatted = output.getvalue()
            elif format_type == "table":
                if isinstance(data, dict):
                    formatted = "\n".join(f"{k}: {v}" for k, v in data.items())
                elif isinstance(data, list):
                    formatted = "\n".join(str(item) for item in data)
                else:
                    formatted = str(data)
            elif format_type == "plain":
                formatted = str(data)
            else:
                return FlextResult[str].fail(f"Unsupported format: {format_type}")

            return FlextResult[str].ok(formatted)
        except Exception as e:
            return FlextResult[str].fail(f"Formatting failed: {e}")

    def flext_cli_export(
        self, data: HandlerData, file_path: str, format_type: str
    ) -> FlextResult[None]:
        """Export data to file."""
        try:
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)

            if format_type == "json":
                with path.open("w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, default=str)
            elif format_type == "yaml":
                with path.open("w", encoding="utf-8") as f:
                    yaml.dump(data, f, default_flow_style=False)
            elif format_type == "csv":
                if not isinstance(data, list):
                    return FlextResult[None].fail(
                        "CSV format requires list of dictionaries"
                    )
                # Type narrowing: at this point we know data is list[dict]
                csv_data = (
                    data  # data is already list[dict[str, str | int | float | bool]]
                )
                if not csv_data:
                    return FlextResult[None].fail("No valid dictionary data found")
                with path.open("w", encoding="utf-8", newline="") as f:
                    fieldnames = list(csv_data[0].keys())
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(csv_data)
            else:
                return FlextResult[None].fail(
                    f"Unsupported export format: {format_type}"
                )

            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(f"Export failed: {e}")

    def flext_cli_health(self) -> FlextResult[dict[str, str | int | bool]]:
        """Get service health information."""
        health_data: dict[str, str | int | bool] = {
            "service": "FlextCliService",
            "status": "healthy",
            "timestamp": datetime.now(UTC).isoformat(),
            "configured": True,
            "handlers": len(self._handlers),
            "plugins": len(self._plugins),
            "sessions": len(self._sessions),
            "commands": len(self._commands),
        }
        return FlextResult[dict[str, str | int | bool]].ok(health_data)

    def create_command(
        self, command_line: str
    ) -> FlextResult[FlextCliModels.CliCommand]:
        """Create a new CLI command."""
        try:
            command = FlextCliModels.CliCommand(command_line=command_line)
            self._commands[command.id] = command
            return FlextResult[FlextCliModels.CliCommand].ok(command)
        except Exception as e:
            return FlextResult[FlextCliModels.CliCommand].fail(
                f"Command creation failed: {e}"
            )

    def create_session(
        self, user_id: str | None = None
    ) -> FlextResult[FlextCliModels.CliSession]:
        """Create a new CLI session."""
        try:
            if user_id is None:
                user_id = f"user_{uuid4().hex[:8]}"
            session = FlextCliModels.CliSession(user_id=user_id)
            self._sessions[session.id] = session
            return FlextResult[FlextCliModels.CliSession].ok(session)
        except Exception as e:
            return FlextResult[FlextCliModels.CliSession].fail(
                f"Session creation failed: {e}"
            )

    def flext_cli_register_handler(
        self, name: str, handler: HandlerFunction
    ) -> FlextResult[None]:
        """Register a command handler."""
        if name in self._handlers:
            return FlextResult[None].fail(f"Handler '{name}' already registered")
        self._handlers[name] = handler
        return FlextResult[None].ok(None)

    def flext_cli_execute_handler(
        self, name: str, *, data: HandlerData
    ) -> FlextResult[HandlerData]:
        """Execute a registered handler."""
        if name not in self._handlers:
            return FlextResult[HandlerData].fail(f"Handler '{name}' not found")
        try:
            result = self._handlers[name](data)
            return FlextResult[HandlerData].ok(result)
        except Exception as e:
            return FlextResult[HandlerData].fail(f"Handler execution failed: {e}")

    def flext_cli_register_plugin(
        self, name: str, plugin: FlextCliModels.CliCommand
    ) -> FlextResult[None]:
        """Register a plugin."""
        if name in self._plugins:
            return FlextResult[None].fail(f"Plugin '{name}' already registered")
        self._plugins[name] = plugin
        return FlextResult[None].ok(None)

    def flext_cli_get_plugins(
        self,
    ) -> FlextResult[dict[str, FlextCliModels.CliCommand]]:
        """Get all registered plugins."""
        return FlextResult[dict[str, FlextCliModels.CliCommand]].ok(
            self._plugins.copy()
        )

    def flext_cli_render_with_context(
        self,
        *,
        data: HandlerData,
        context: dict[str, str | int | float | bool] | None = None,
    ) -> FlextResult[str]:
        """Render data with context."""
        try:
            format_type = "table"
            if context and "output_format" in context:
                format_type = str(context["output_format"])
            elif self._cli_config:
                format_type = self._cli_config.output_format

            return self.format_data(data, format_type)
        except Exception as e:
            return FlextResult[str].fail(f"Rendering failed: {e}")

    def flext_cli_create_command(
        self, name: str, command_line: str
    ) -> FlextResult[FlextCliModels.CliCommand]:
        """Create a command with specific name."""
        try:
            command = FlextCliModels.CliCommand(command_line=command_line)
            command.id = name
            self._commands[name] = command
            return FlextResult[FlextCliModels.CliCommand].ok(command)
        except Exception as e:
            return FlextResult[FlextCliModels.CliCommand].fail(
                f"Command creation failed: {e}"
            )

    def flext_cli_create_session(
        self, user_id: str
    ) -> FlextResult[FlextCliModels.CliSession]:
        """Create a session with specific user ID."""
        try:
            session = FlextCliModels.CliSession(user_id=user_id)
            self._sessions[session.id] = session
            return FlextResult[FlextCliModels.CliSession].ok(session)
        except Exception as e:
            return FlextResult[FlextCliModels.CliSession].fail(
                f"Session creation failed: {e}"
            )

    def flext_cli_get_commands(
        self,
    ) -> FlextResult[dict[str, FlextCliModels.CliCommand]]:
        """Get all registered commands."""
        return FlextResult[dict[str, FlextCliModels.CliCommand]].ok(
            self._commands.copy()
        )

    def flext_cli_get_sessions(
        self,
    ) -> FlextResult[dict[str, FlextCliModels.CliSession]]:
        """Get all active sessions."""
        return FlextResult[dict[str, FlextCliModels.CliSession]].ok(
            self._sessions.copy()
        )

    def flext_cli_get_handlers(self) -> FlextResult[dict[str, HandlerFunction]]:
        """Get all registered handlers."""
        return FlextResult[dict[str, HandlerFunction]].ok(self._handlers.copy())

    def get_service_health(self) -> FlextResult[dict[str, str | int | bool]]:
        """Get detailed service health information."""
        return self.flext_cli_health()

    def update_configuration(self) -> None:
        """Update service configuration."""

    @property
    def registry(self) -> FlextContainer:
        """Get service registry."""
        return self._container

    @property
    def orchestrator(self) -> FlextContainer:
        """Get service orchestrator."""
        return self._container

    @property
    def metrics(self) -> dict[str, int]:
        """Get service metrics."""
        return {
            "handlers": len(self._handlers),
            "plugins": len(self._plugins),
            "sessions": len(self._sessions),
            "commands": len(self._commands),
        }


__all__ = ["FlextCliService"]
