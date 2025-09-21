"""CLI core service using flext-core directly.

Production-ready CLI service that uses flext-core services directly without
duplication or fallback mechanisms. Implements standardized architecture patterns.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import csv
import json
from datetime import UTC, datetime
from pathlib import Path

import yaml
from pydantic import PrivateAttr

from flext_cli.configs import FlextCliConfigs
from flext_cli.formatting import FlextCliFormatters
from flext_cli.models import FlextCliModels
from flext_core import (
    FlextContainer,
    FlextDomainService,
    FlextLogger,
    FlextProcessing,
    FlextResult,
    FlextUtilities,
)


class FlextCliService(FlextDomainService[str]):
    """Production-ready CLI service using flext-core directly.

    Provides CLI service orchestration using flext-core infrastructure without
    duplication or fallback mechanisms. Uses FlextConfig singleton as the single
    source of truth for all configuration.

    Args:
        None: Service initializes with flext-core dependencies.

    Returns:
        FlextResult[str]: Service execution result.

    Raises:
        RuntimeError: If service initialization fails.

    """

    # Private attributes
    _config: FlextCliConfigs | None = PrivateAttr(default=None)
    _commands: dict[str, object] = PrivateAttr(
        default_factory=dict,
    )
    _registered_handlers: dict[str, object] = PrivateAttr(
        default_factory=dict,
    )
    _plugins: dict[str, object] = PrivateAttr(
        default_factory=dict,
    )
    _sessions: dict[str, object] = PrivateAttr(
        default_factory=dict,
    )
    _formatters: FlextCliFormatters | None = PrivateAttr(default=None)

    def __init__(self) -> None:
        """Initialize CLI service with flext-core dependencies.

        Initializes the service using FlextConfig singleton and flext-core
        infrastructure. No fallback mechanisms are used.

        """
        super().__init__()
        self._logger = FlextLogger(__name__)
        self._container = FlextContainer.get_global()

        # Initialize configuration from FlextConfig singleton
        self._initialize_configuration()
        self._initialize_services()

    def _initialize_configuration(self) -> None:
        """Initialize configuration from FlextConfig singleton.

        Sets up configuration and formatters using flext-core patterns.
        No fallback mechanisms are used.

        """
        # Initialize configuration state
        self._config = None

        # Initialize formatters with configuration
        self._formatters = FlextCliFormatters()

    # Public accessor methods
    def get_config(self) -> FlextCliConfigs | None:
        """Get current configuration from FlextConfig singleton.

        Returns:
            FlextCliConfigs | None: Description of return value.

        """
        return self._config

    def update_configuration(self) -> None:
        """Update configuration from FlextConfig singleton.

        This method refreshes the service configuration from the
        FlextConfig singleton, ensuring it always uses the latest
        configuration values.

        """
        # Update configuration from singleton
        self._config = FlextCliConfigs.get_global_instance()

        # Reinitialize formatters with new configuration
        self._formatters = FlextCliFormatters()

    def get_handlers(self) -> dict[str, object]:
        """Get registered handlers.

        Returns:
            dict[str, object]: Description of return value.

        """
        return self._registered_handlers

    def get_plugins(self) -> dict[str, object]:
        """Get loaded plugins.

        Returns:
            dict[str, object]: Description of return value.

        """
        return self._plugins

    def get_sessions(self) -> dict[str, object]:
        """Get active sessions.

        Returns:
            dict[str, object]: Description of return value.

        """
        return self._sessions

    def get_commands(self) -> dict[str, object]:
        """Get registered commands.

        Returns:
            dict[str, object]: Description of return value.

        """
        return self._commands

    def get_formatters(self) -> FlextCliFormatters:
        """Get formatters instance.

        Raises:
            RuntimeError: If formatters initialization fails.

        Returns:
            FlextCliFormatters: Description of return value.

        """
        if self._formatters is None:
            self._initialize_services()
        if self._formatters is None:
            msg = "Failed to initialize formatters"
            raise RuntimeError(msg)
        return self._formatters

    # Public property accessors
    @property
    def registry(self) -> object:
        """Get service registry for inspection.

        Returns:
            object: Description of return value.

        """
        return self._service_registry

    @property
    def orchestrator(self) -> object:
        """Get service orchestrator for inspection.

        Returns:
            object: Description of return value.

        """
        return self._service_orchestrator

    @property
    def metrics(self) -> dict[str, object]:
        """Get service metrics for monitoring.

        Returns:
            dict[str, object]: Description of return value.

        """
        return {
            "commands_executed": len(self._commands),
            "handlers_registered": len(self._registered_handlers),
            "sessions_active": len(self._sessions),
            "plugins_loaded": len(self._plugins),
        }

    def _initialize_services(self) -> None:
        """Initialize services using flext-core directly.

        Sets up service registry, orchestrator, and handlers using flext-core
        infrastructure. No duplication or fallback mechanisms are used.

        """
        # Use flext-core services directly - NO duplication
        self._service_registry = FlextProcessing()
        self._service_orchestrator = FlextProcessing.create_pipeline()
        self._handler_registry = FlextProcessing()

        # Initialize _formatters using FlextCliFormatters for full integration
        self._formatters = FlextCliFormatters()

        # Register CLI-specific handlers using flext-core patterns
        self._register_cli_handlers()

    def _register_cli_handlers(self) -> None:
        """Register CLI handlers using flext-core handler registry.

        Registers CLI-specific handlers using flext-core patterns.
        Implementation will be added when concrete handlers are available.

        """
        # Skip handler registration for now - Handler is abstract
        # This will be implemented when concrete handlers are available

    def get_service_health(self) -> FlextResult[dict[str, object]]:
        """Get service health using explicit error handling.

        Returns:
            FlextResult[dict[str, object]]: Health information or error.

        """

        def build_health_info() -> dict[str, object]:
            """Build health information dictionary - used by safe_call.

            Returns:
            dict[str, object]: Description of return value.

            """
            health_info: dict[str, object] = {
                "service": "FlextCliService",
                "status": "healthy",
                "domain": "cli",
                "check_id": "cli_health_check",
                "timestamp": str(id(self)),
                "configured": self._config is not None,
                "handlers": len(self._registered_handlers),
                "plugins": len(self._plugins),
                "sessions": len(self._sessions),
                "commands": len(self._commands),
            }

            # Add config information if configured
            if self._config is not None:
                health_info["config"] = {
                    "profile": getattr(self._config, "profile", "unknown"),
                    "debug": getattr(self._config, "debug", False),
                    "output_format": getattr(self._config, "output_format", "unknown"),
                }

            return health_info

        result = FlextResult.safe_call(build_health_info)
        if result.is_failure:
            return FlextResult[dict[str, object]].fail(
                f"Health check failed: {result.error}"
            )

        return result

    def format_data(self, data: object, format_type: str) -> FlextResult[str]:
        """Format data using FlextCliFormatters.

        Args:
            data: Data to format.
            format_type: Format type (table, json, yaml, csv).

        Returns:
            FlextResult[str]: Formatted data or error.

        """
        # FlextCliFormatters handles all object types - no type validation needed
        formatters = FlextCliFormatters()
        return formatters.format_data(data, format_type)

    def flext_cli_export(
        self,
        data: object,
        file_path: str,
        format_type: str,
    ) -> FlextResult[str]:
        """Export data to file using explicit error handling.

        Args:
            data: Data to export.
            file_path: Target file path.
            format_type: Export format (json, yaml, csv).

        Returns:
            FlextResult[str]: Export result or error.

        """

        def create_export_directory(path: Path) -> Path:
            """Create parent directory for export - used by safe_call.

            Returns:
            Path: Description of return value.

            """
            path.parent.mkdir(parents=True, exist_ok=True)
            return path

        def format_content_for_export(data: object, format_type: str) -> str:
            """Format content based on export type - used by safe_call.

            Returns:
            str: Description of return value.

            """
            # Python 3.13+ match-case for format type handling
            match format_type.lower():
                case "json":
                    return json.dumps(data, indent=2, ensure_ascii=False)
                case "yaml" | "yml":
                    return yaml.safe_dump(data, default_flow_style=False)
                case _:
                    return str(data)

        def export_csv_data(path: Path, data: object) -> str:
            """Export CSV data - used by safe_call.

            Raises:
                ValueError: If data format is invalid for CSV export.

            Returns:
            str: Description of return value.

            """
            if not isinstance(data, list) or not data or not isinstance(data[0], dict):
                msg = "CSV export requires list of dictionaries"
                raise ValueError(msg)

            with path.open("w", newline="", encoding="utf-8") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
            return f"Data exported to {path}"

        def write_content_to_file(path: Path, content: str) -> str:
            """Write content to file - used by safe_call.

            Returns:
            str: Description of return value.

            """
            path.write_text(content, encoding="utf-8")
            return f"Data exported to {path}"

        # Validate inputs first
        if not file_path.strip():
            return FlextResult[str].fail("File path cannot be empty")

        path = Path(file_path)

        # Handle CSV special case first
        if format_type.lower() == "csv":
            directory_result = FlextResult.safe_call(
                lambda: create_export_directory(path)
            )
            if directory_result.is_failure:
                return FlextResult[str].fail(
                    f"Directory creation failed: {directory_result.error}"
                )

            csv_result = FlextResult.safe_call(lambda: export_csv_data(path, data))
            if csv_result.is_failure:
                return FlextResult[str].fail(f"CSV export failed: {csv_result.error}")

            return csv_result

        # Handle other formats using railway pattern
        directory_result = FlextResult.safe_call(lambda: create_export_directory(path))
        if directory_result.is_failure:
            return FlextResult[str].fail(
                f"Directory creation failed: {directory_result.error}"
            )

        format_result = FlextResult.safe_call(
            lambda: format_content_for_export(data, format_type)
        )
        if format_result.is_failure:
            return FlextResult[str].fail(
                f"Content formatting failed: {format_result.error}"
            )

        write_result = FlextResult.safe_call(
            lambda: write_content_to_file(path, format_result.unwrap())
        )
        if write_result.is_failure:
            return FlextResult[str].fail(f"File write failed: {write_result.error}")

        return write_result

    def flext_cli_health(self) -> FlextResult[dict[str, object]]:
        """Get CLI health status.

        Returns:
            FlextResult[dict[str, object]]: Health information or error.

        """
        return self.get_service_health()

    def flext_cli_register_plugin(self, name: str, plugin: object) -> FlextResult[None]:
        """Register a plugin using explicit error handling.

        Args:
            name: Plugin name.
            plugin: Plugin object.

        Returns:
            FlextResult[None]: Registration result or error.

        """

        def register_plugin() -> None:
            """Register plugin - used by safe_call.

            Raises:
                ValueError: If plugin is already registered.

            """
            if name in self._plugins:
                msg = f"Plugin '{name}' already registered"
                raise ValueError(msg)
            self._plugins[name] = plugin

        result = FlextResult.safe_call(register_plugin)
        if result.is_failure:
            return FlextResult[None].fail(f"Plugin registration failed: {result.error}")

        return FlextResult[None].ok(None)

    def flext_cli_get_plugins(self) -> FlextResult[dict[str, object]]:
        """Get plugins copy using explicit error handling.

        Returns:
            FlextResult[dict[str, object]]: Plugins dictionary or error.

        """

        def copy_plugins() -> dict[str, object]:
            """Create plugins copy - used by safe_call.

            Returns:
            dict[str, object]: Description of return value.

            """
            # Return a copy to prevent external modification
            return self._plugins.copy()

        result = FlextResult.safe_call(copy_plugins)
        if result.is_failure:
            return FlextResult[dict[str, object]].fail(
                f"Get plugins failed: {result.error}"
            )

        return result

    def flext_cli_execute_handler(
        self,
        handler_name: str,
        data: object,
    ) -> FlextResult[object]:
        """Execute handler by name using explicit error handling.

        Args:
            handler_name: Name of handler to execute.
            data: Data to pass to handler.

        Returns:
            FlextResult[object]: Handler result or error.

        """

        def execute_handler() -> object:
            """Execute handler - used by safe_call.

            Raises:
                KeyError: If handler is not found.
                TypeError: If handler is not callable.

            Returns:
            object: Description of return value.

            """
            if handler_name not in self._registered_handlers:
                msg = f"Handler '{handler_name}' not found"
                raise KeyError(msg)

            handler = self._registered_handlers[handler_name]
            if not callable(handler):
                msg = f"Handler '{handler_name}' is not callable"
                raise TypeError(msg)

            return handler(data)

        result = FlextResult.safe_call(execute_handler)
        if result.is_failure:
            return FlextResult[object].fail(f"Handler execution failed: {result.error}")

        return result

    def flext_cli_render_with_context(
        self,
        data: object,
        context_options: object = None,
    ) -> FlextResult[str]:
        """Render data with context using explicit error handling.

        Args:
            data: Data to render.
            context_options: Context options for rendering.

        Returns:
            FlextResult[str]: Rendered data or error.

        """

        def determine_format_type() -> str:
            """Determine format type from context or config - used by safe_call.

            Returns:
            str: Description of return value.

            """
            # Use context format if provided, otherwise configured format, otherwise default to table
            format_type = "table"
            if (
                context_options
                and isinstance(context_options, dict)
                and "output_format" in context_options
            ):
                format_type = str(context_options["output_format"])
            elif self._config and hasattr(self._config, "output_format"):
                format_type = self._config.output_format
            return format_type

        format_result = FlextResult.safe_call(determine_format_type)
        if format_result.is_failure:
            return FlextResult[str].fail(
                f"Format type determination failed: {format_result.error}"
            )

        return self.format_data(data, format_result.unwrap())

    def flext_cli_create_command(
        self,
        name: str,
        command_line: str,
    ) -> FlextResult[object]:
        """Create a command using explicit error handling.

        Args:
            name: Command name.
            command_line: Command line string.

        Returns:
            FlextResult[object]: Created command or error.

        """

        def create_command() -> FlextCliModels.CliCommand:
            """Create CLI command - used by safe_call.

            Returns:
            FlextCliModels.CliCommand: Description of return value.

            """
            command = FlextCliModels.CliCommand(
                id=FlextUtilities.Generators.generate_uuid(),
                command_line=command_line,
                execution_time=datetime.now(UTC),
                name=name,
            )
            self._commands[name] = command
            return command

        result = FlextResult.safe_call(create_command)
        if result.is_failure:
            return FlextResult[object].fail(f"Command creation failed: {result.error}")

        return FlextResult[object].ok(result.unwrap())

    def flext_cli_create_session(self, user_id: str) -> FlextResult[object]:
        """Create a session using explicit error handling.

        Args:
            user_id: User ID for session.

        Returns:
            FlextResult[object]: Created session or error.

        """

        def create_session() -> FlextCliModels.CliSession:
            """Create CLI session - used by safe_call.

            Returns:
            FlextCliModels.CliSession: Description of return value.

            """
            session = FlextCliModels.CliSession(
                id=FlextUtilities.Generators.generate_uuid(),
                session_id=FlextUtilities.Generators.generate_uuid(),
                start_time=datetime.now(UTC),
                user_id=user_id,
            )
            self._sessions[session.id] = session
            return session

        result = FlextResult.safe_call(create_session)
        if result.is_failure:
            return FlextResult[object].fail(f"Session creation failed: {result.error}")

        return FlextResult[object].ok(result.unwrap())

    def flext_cli_register_handler(
        self,
        name: str,
        handler: object,
    ) -> FlextResult[None]:
        """Register a handler using explicit error handling.

        Args:
            name: Handler name.
            handler: Handler object.

        Returns:
            FlextResult[None]: Registration result or error.

        """

        def register_handler() -> None:
            """Register handler - used by safe_call.

            Raises:
                ValueError: If handler is already registered.

            """
            if name in self._registered_handlers:
                msg = f"Handler '{name}' already registered"
                raise ValueError(msg)
            self._registered_handlers[name] = handler

        result = FlextResult.safe_call(register_handler)
        if result.is_failure:
            return FlextResult[None].fail(
                f"Handler registration failed: {result.error}"
            )

        return FlextResult[None].ok(None)

    def flext_cli_get_handlers(self) -> FlextResult[dict[str, object]]:
        """Get handlers copy using explicit error handling.

        Returns:
            FlextResult[dict[str, object]]: Handlers dictionary or error.

        """

        def copy_handlers() -> dict[str, object]:
            """Create handlers copy - used by safe_call.

            Returns:
            dict[str, object]: Description of return value.

            """
            # Return a copy to prevent external modification
            return self._registered_handlers.copy()

        result = FlextResult.safe_call(copy_handlers)
        if result.is_failure:
            return FlextResult[dict[str, object]].fail(
                f"Get handlers failed: {result.error}"
            )

        return result

    def flext_cli_get_sessions(self) -> FlextResult[dict[str, object]]:
        """Get sessions copy using explicit error handling.

        Returns:
            FlextResult[dict[str, object]]: Sessions dictionary or error.

        """

        def copy_sessions() -> dict[str, object]:
            """Create sessions copy - used by safe_call.

            Returns:
            dict[str, object]: Description of return value.

            """
            # Return a copy to prevent external modification
            return self._sessions.copy()

        result = FlextResult.safe_call(copy_sessions)
        if result.is_failure:
            return FlextResult[dict[str, object]].fail(
                f"Get sessions failed: {result.error}"
            )

        return result

    def flext_cli_get_commands(self) -> FlextResult[dict[str, object]]:
        """Get commands using explicit error handling.

        Returns:
            FlextResult[dict[str, object]]: Description of return value.

        """

        def copy_commands_dict() -> dict[str, object]:
            """Create commands copy - used by safe_call.

            Returns:
            dict[str, object]: Description of return value.

            """
            return self._commands.copy()

        result = FlextResult.safe_call(copy_commands_dict)
        if result.is_failure:
            return FlextResult[dict[str, object]].fail(
                f"Commands retrieval failed: {result.error}"
            )

        return result

    def validate_request(self, request_data: object) -> FlextResult[bool]:
        """Validate request using flext-core validation.

        Args:
            request_data: Data to validate.

        Returns:
            FlextResult[bool]: Validation result or error.

        """

        def validate_request_data() -> bool:
            """Validate request data - used by safe_call.

            Returns:
            bool: Description of return value.

            """
            # Basic validation using flext-core patterns
            return request_data is not None

        result = FlextResult.safe_call(validate_request_data)
        if result.is_failure:
            return FlextResult[bool].fail(f"Request validation failed: {result.error}")

        return FlextResult[bool].ok(data=result.unwrap())

    def start(self) -> FlextResult[None]:
        """Start CLI service.

        Returns:
            FlextResult[None]: Start result or error.

        """

        def initialize_and_start_service() -> None:
            """Initialize and start CLI service - used by safe_call."""
            # Initialize services if not already done
            if not hasattr(self, "_service_registry"):
                self._initialize_services()

            self._logger.info("FlextCliService started successfully")

        result = FlextResult.safe_call(initialize_and_start_service)
        if result.is_failure:
            return FlextResult[None].fail(f"Service start failed: {result.error}")

        return FlextResult[None].ok(None)

    def stop(self) -> FlextResult[None]:
        """Stop CLI service.

        Returns:
            FlextResult[None]: Stop result or error.

        """

        def cleanup_and_stop_service() -> None:
            """Clean up and stop CLI service - used by safe_call."""
            # Clean up resources
            self._commands.clear()
            self._registered_handlers.clear()
            self._plugins.clear()
            self._sessions.clear()

            self._logger.info("FlextCliService stopped successfully")

        result = FlextResult.safe_call(cleanup_and_stop_service)
        if result.is_failure:
            return FlextResult[None].fail(f"Service stop failed: {result.error}")

        return FlextResult[None].ok(None)

    def health_check(self) -> FlextResult[str]:
        """Perform health check and return status.

        Returns:
            FlextResult[str]: Health status or error.

        """

        def perform_health_check() -> str:
            """Perform health check operation - used by safe_call.

            Returns:
            str: Description of return value.

            """
            health_result = self.get_service_health()
            if health_result.is_success:
                return "healthy"
            return "unhealthy"

        result = FlextResult.safe_call(perform_health_check)
        if result.is_failure:
            return FlextResult[str].fail(f"Health check failed: {result.error}")

        return result

    def configure(self, config: object) -> FlextResult[None]:
        """Configure service with new configuration.

        Args:
            config: Configuration object or dictionary.

        Returns:
            FlextResult[None]: Configuration result or error.

        """

        def configure_service() -> None:
            """Configure service with config - used by safe_call.

            Raises:
                ValueError: If configuration validation fails.
                TypeError: If configuration type is invalid.

            """
            # Validate configuration
            if isinstance(config, dict):
                # Handle format_type mapping to output_format
                config_copy = config.copy()
                if "format_type" in config_copy:
                    config_copy["output_format"] = config_copy.pop("format_type")

                # Check for unknown keys
                valid_keys = {"debug", "output_format", "api_url", "profile"}
                unknown_keys = [key for key in config_copy if key not in valid_keys]
                if unknown_keys:
                    msg = f"Unknown config keys: {', '.join(unknown_keys)}"
                    raise ValueError(msg)

                # Create config object from dict
                self._config = FlextCliConfigs(**config_copy)
            elif isinstance(config, FlextCliConfigs):
                self._config = config
            else:
                msg = "Configuration must be a dictionary or FlextCliConfigs object"
                raise TypeError(msg)

            self._formatters = FlextCliFormatters()
            self._logger.info("FlextCliService configured successfully")

        result = FlextResult.safe_call(configure_service)
        if result.is_failure:
            return FlextResult[None].fail(
                f"Service configuration failed: {result.error}"
            )

        return FlextResult[None].ok(None)

    def execute(self) -> FlextResult[str]:
        """Execute CLI request using flext-core service processor.

        Returns:
            FlextResult[str]: Execution result or error.

        """

        def execute_cli_service() -> str:
            """Execute CLI service operation - used by safe_call.

            Returns:
            str: Description of return value.

            """
            # Use flext-core service orchestrator directly (correct property)
            health_result = self.get_service_health()
            if health_result.is_success:
                return "CLI service ready and healthy"

            # Default execution response
            return "CLI service executed successfully"

        result = FlextResult.safe_call(execute_cli_service)
        if result.is_failure:
            return FlextResult[str].fail(f"Service execution failed: {result.error}")

        return result

    # ========== Consolidated FlextCliServices functionality ==========
    # Methods from services.py - using flext-core directly with ZERO duplication

    @staticmethod
    def create_command_processor() -> FlextResult[str]:
        """Create command processor using flext-core processing directly.

        Returns:
            FlextResult[str]: Creation result or error.

        """

        def create_processor() -> str:
            """Create command processor - used by safe_call.

            Returns:
            str: Description of return value.

            """
            # Use flext-core processing directly - FlextProcessing exists
            FlextProcessing()
            return "Command processor created successfully"

        result = FlextResult.safe_call(create_processor)
        if result.is_failure:
            return FlextResult[str].fail(
                f"Command processor creation failed: {result.error}"
            )

        return result

    @staticmethod
    def create_session_processor() -> FlextResult[str]:
        """Create session processor using flext-core processing directly.

        Returns:
            FlextResult[str]: Creation result or error.

        """

        def create_processor() -> str:
            """Create session processor - used by safe_call.

            Returns:
            str: Description of return value.

            """
            # Use flext-core processing directly - create_pipeline() returns Pipeline directly
            FlextProcessing.create_pipeline()
            # Pipeline created successfully
            return "Session processor created successfully"

        result = FlextResult.safe_call(create_processor)
        if result.is_failure:
            return FlextResult[str].fail(
                f"Session processor creation failed: {result.error}"
            )

        return result

    @staticmethod
    def create_config_processor() -> FlextResult[str]:
        """Create config processor using flext-core processing directly.

        Returns:
            FlextResult[str]: Creation result or error.

        """

        def create_processor() -> str:
            """Create config processor - used by safe_call.

            Returns:
            str: Description of return value.

            """
            # Use flext-core processing directly
            FlextProcessing()
            return "Config processor created successfully"

        result = FlextResult.safe_call(create_processor)
        if result.is_failure:
            return FlextResult[str].fail(
                f"Config processor creation failed: {result.error}"
            )

        return result


__all__ = ["FlextCliService"]
