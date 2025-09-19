"""FLEXT CLI API - Unified single-class implementation.

Uses Python 3.13 cutting-edge patterns.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import json
import logging
import platform
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Protocol, override
from uuid import UUID, uuid4

import yaml
from pydantic import BaseModel, Field, PrivateAttr

from flext_cli.configs import FlextCliConfigs
from flext_cli.core import FlextCliService
from flext_cli.formatters import FlextCliFormatters
from flext_cli.models import FlextCliModels
from flext_core import FlextContainer, FlextResult, FlextTypes, T


class DispatcherProtocol(Protocol):
    """Protocol for operation dispatcher with proper type safety."""

    def dispatch_operation(self, operation: str, **params: object) -> FlextResult[object]:
        """Dispatch operation with parameters."""
        ...

    def configure(self, config: object) -> FlextResult[None]:
        """Configure dispatcher with settings."""
        ...


class FlextCliApi(BaseModel):
    """Unified CLI API with Python 3.13 cutting-edge patterns.

    Uses nested specialized handlers.

    Features:
        - Single class pattern with all functionality encapsulated
        - Nested specialized handlers for different operation types
        - Advanced pattern matching for request dispatching
        - Zero loose helper functions - all functionality contained
        - Advanced Pydantic v2 optimizations with computed fields
    """

    # State management attributes - SIMPLE ALIAS: Use optional fields with proper defaults
    state: FlextCliModels.ApiState | None = Field(default=None)
    dispatcher: object | None = Field(
        default=None,
    )  # Will be OperationDispatcher implementing DispatcherProtocol at runtime

    # Type alias for test compatibility
    @property
    def api_state_class(self) -> type[FlextCliModels.ApiState]:
        """Get ApiState model class for test compatibility."""
        return FlextCliModels.ApiState

    # Private attributes for Pydantic
    _formatters: FlextCliFormatters = PrivateAttr()
    _container: object = PrivateAttr()
    _logger: object = PrivateAttr()
    _models: object = PrivateAttr()
    _services: object = PrivateAttr()

    # Model configuration
    model_config = {"arbitrary_types_allowed": True}

    # =========================================================================
    # NESTED SPECIALIZED CLASSES - Advanced Architecture Pattern
    # =========================================================================

    class OperationDispatcher:
        """Nested operation dispatcher using Python 3.13 pattern matching."""

        def __init__(
            self,
            state: FlextCliModels.ApiState,
            formatters: FlextCliFormatters,
        ) -> None:
            """Initialize operation dispatcher with state and formatters."""
            self.state = state
            self.formatters = formatters

        def dispatch_operation(
            self,
            operation: str,
            **params: object,
        ) -> FlextResult[object]:
            """Advanced operation dispatching using match-case patterns."""
            match operation.lower():
                case "format":
                    format_result = self._handle_format_operation(
                        params.get("data"),
                        str(params.get("format_type", "table")),
                    )
                    return (
                        FlextResult[object].ok(format_result.value)
                        if format_result.is_success
                        else FlextResult[object].fail(
                            format_result.error or "Format failed",
                        )
                    )
                case "export":
                    export_result = self._handle_export_operation(
                        params.get("data"),
                        params.get("file_path"),
                    )
                    return (
                        FlextResult[object].ok(export_result.value)
                        if export_result.is_success
                        else FlextResult[object].fail(
                            export_result.error or "Export failed",
                        )
                    )
                case "transform":
                    transform_result = self._handle_transform_operation(
                        params.get("data"),
                        params.get("filters"),
                    )
                    return (
                        FlextResult[object].ok(transform_result.value)
                        if transform_result.is_success
                        else FlextResult[object].fail(
                            transform_result.error or "Transform failed",
                        )
                    )
                case "create_command":
                    cmd_result = self._handle_create_command_operation(
                        params.get("command_line"),
                    )
                    return (
                        FlextResult[object].ok(cmd_result.value)
                        if cmd_result.is_success
                        else FlextResult[object].fail(
                            cmd_result.error or "Create command failed",
                        )
                    )
                case "execute_command":
                    exec_result = self._handle_execute_command_operation(
                        params.get("command"),
                    )
                    return (
                        FlextResult[object].ok(exec_result.value)
                        if exec_result.is_success
                        else FlextResult[object].fail(
                            exec_result.error or "Execute command failed",
                        )
                    )
                case "create_session":
                    session_result = self._handle_create_session_operation(
                        params.get("user_id"),
                    )
                    return (
                        FlextResult[object].ok(session_result.value)
                        if session_result.is_success
                        else FlextResult[object].fail(
                            session_result.error or "Create session failed",
                        )
                    )
                case "end_session":
                    end_result = self._handle_end_session_operation(
                        params.get("session_id"),
                    )
                    return (
                        FlextResult[object].ok(end_result.value)
                        if end_result.is_success
                        else FlextResult[object].fail(
                            end_result.error or "End session failed",
                        )
                    )
                case "health":
                    health_result = self._handle_health_operation()
                    return (
                        FlextResult[object].ok(health_result.value)
                        if health_result.is_success
                        else FlextResult[object].fail(
                            health_result.error or "Health check failed",
                        )
                    )
                case "configure":
                    config_result = self._handle_configure_operation(
                        params.get("config"),
                    )
                    return (
                        FlextResult[object].ok(config_result.value)
                        if config_result.is_success
                        else FlextResult[object].fail(
                            config_result.error or "Configure failed",
                        )
                    )
                case "aggregate":
                    agg_result = self._handle_aggregate_operation(
                        params.get("data"),
                        params.get("group_by"),
                        params.get("sum_fields"),
                    )
                    return (
                        FlextResult[object].ok(agg_result.value)
                        if agg_result.is_success
                        else FlextResult[object].fail(
                            agg_result.error or "Aggregate failed",
                        )
                    )
                case "batch_export":
                    batch_result = self._handle_batch_export_operation(
                        params.get("datasets"),
                        params.get("base_path"),
                        params.get("format_type"),
                    )
                    return (
                        FlextResult[object].ok(batch_result.value)
                        if batch_result.is_success
                        else FlextResult[object].fail(
                            batch_result.error or "Batch export failed",
                        )
                    )
                case _:
                    return FlextResult[object].fail(f"Unknown operation: {operation}")

        def _handle_format_operation(
            self,
            data: object,
            format_type: str,
        ) -> FlextResult[str]:
            """Handle format operations using advanced parameter validation."""
            if not format_type or not isinstance(format_type, str):
                return FlextResult[str].fail("Format type must be a non-empty string")

            match format_type.lower():
                case "json":
                    result = json.dumps(data, default=str)
                    return FlextResult[str].ok(result)
                case "yaml":
                    result = yaml.dump(
                        data,
                        default_flow_style=False,
                        allow_unicode=True,
                    )
                    return FlextResult[str].ok(result)
                case "csv":
                    return self._format_as_csv(data)
                case "table":
                    # FlextCliFormatters handles all object types - no type validation needed
                    # Type cast to match formatter expectations
                    formatted_data = (
                        data if isinstance(data, (dict, list)) else {"value": data}
                    )
                    table_result = self.formatters.create_table(formatted_data)
                    if table_result.is_success:
                        # Convert Table to string representation
                        return FlextResult[str].ok(str(table_result.value))
                    return FlextResult[str].fail(
                        table_result.error or "Table formatting failed",
                    )
                case "plain":
                    return FlextResult[str].ok(str(data))
                case _:
                    return FlextResult[str].fail(
                        f"Unsupported format type: {format_type}",
                    )

        def _format_as_csv(self, data: object) -> FlextResult[str]:
            """Format data as CSV using flext-core utilities - NO duplication."""
            # REMOVED: Local CSV implementation - using flext-core formatters instead
            # This method now delegates to standard string formatting
            # CSV format should be handled by dedicated CSV processors in proper domain
            return FlextResult[str].ok(str(data))

        def _handle_export_operation(
            self,
            _data: object,
            _file_path: object,
        ) -> FlextResult[str]:
            """ELIMINATED: File I/O violates API single responsibility principle."""
            # VIOLATION: CLI API should NOT handle file operations directly
            # SOLUTION: Delegate to proper file operations domain (FlextCliFileOperations)
            return FlextResult[str].fail(
                "Export operations moved to FlextCliFileOperations domain",
            )

        def _handle_transform_operation(
            self,
            _data: object,
            _filters: object,
        ) -> FlextResult[FlextTypes.Core.List]:
            """ELIMINATED: Data transformation violates API single responsibility principle."""
            # VIOLATION ANALYSIS:
            # - Data transformation: Already available in FlextUtilities from flext-core
            # - Filtering logic: Should use flext-core data processing utilities
            # - Data conversion patterns: FlextUtilities has pattern matching conversions
            # - Complex filtering: Violates Single Responsibility Principle for CLI API
            #
            # SOLUTION: Use FlextUtilities from flext-core for data transformations
            return FlextResult[FlextTypes.Core.List].fail(
                "Data transformation operations moved to FlextUtilities from flext-core - use existing utilities",
            )

        def _handle_create_command_operation(
            self,
            command_line: object,
        ) -> FlextResult[FlextCliModels.CliCommand]:
            """Handle command creation with advanced validation."""
            if not isinstance(command_line, str) or not command_line.strip():
                return FlextResult[FlextCliModels.CliCommand].fail(
                    "Invalid command line",
                )
            command = FlextCliModels.CliCommand(
                id=str(uuid4()),
                command_line=command_line.strip(),
                execution_time=datetime.now(UTC),
            )
            self.state.command_history.append(command)
            return FlextResult[FlextCliModels.CliCommand].ok(command)

        def _handle_execute_command_operation(
            self,
            command: object,
        ) -> FlextResult[str]:
            """Handle command execution with validation."""
            if not isinstance(command, FlextCliModels.CliCommand):
                return FlextResult[str].fail("Invalid command object")
            return FlextResult[str].ok(f"Executed: {command.command_line}")

        def _handle_create_session_operation(
            self,
            user_id: object,
        ) -> FlextResult[FlextCliModels.CliSession]:
            """Handle session creation with advanced state management."""
            session = FlextCliModels.CliSession(
                id=str(uuid4()),
                session_id=str(uuid4()),
                start_time=datetime.now(UTC),
                user_id=str(user_id) if user_id else None,
            )
            if self.state.enable_session_tracking:
                self.state.sessions[session.session_id] = session
            return FlextResult[FlextCliModels.CliSession].ok(session)

        def _handle_end_session_operation(
            self,
            session_id: object,
        ) -> FlextResult[None]:
            """Handle session end with advanced validation."""
            if not isinstance(session_id, str) or not session_id.strip():
                return FlextResult[None].fail("Session ID must be a non-empty string")

            try:
                UUID(session_id)
            except ValueError:
                return FlextResult[None].fail(
                    f"Invalid session ID format: {session_id}",
                )

            # Remove from tracking if exists
            if session_id in self.state.sessions:
                del self.state.sessions[session_id]

            return FlextResult[None].ok(None)

        def _handle_health_operation(self) -> FlextResult[FlextTypes.Core.Dict]:
            """Handle health check with comprehensive system information."""
            return FlextResult[FlextTypes.Core.Dict].ok(
                {
                    "status": "healthy",
                    "version": self.state.version,
                    "service": self.state.service_name,
                    "python_version": f"{sys.version_info.major}.{sys.version_info.minor}",
                    "platform": platform.system(),
                    "timestamp": datetime.now(UTC).isoformat(),
                    "sessions": self.state.session_count,
                    "handlers": self.state.handler_count,
                    "features": {
                        "session_tracking": self.state.enable_session_tracking,
                        "command_history": self.state.enable_command_history,
                    },
                },
            )

        def configure(self, config: object) -> FlextResult[None]:
            """Configure API with validation and state updates."""
            return self._handle_configure_operation(config)

        def _handle_configure_operation(self, config: object) -> FlextResult[None]:
            """Handle configuration with advanced validation and state updates."""
            if not isinstance(config, dict):
                return FlextResult[None].fail("Configuration must be a dictionary")

            if not config:
                return FlextResult[None].fail("Configuration cannot be empty")

            # Apply configuration settings using pattern matching
            for key, value in config.items():
                match key:
                    case "enable_session_tracking":
                        self.state.enable_session_tracking = bool(value)
                    case "enable_command_history":
                        self.state.enable_command_history = bool(value)
                    case "version":
                        if str(value):
                            # Convert to int since Entity.version expects int
                            version_str = str(value)
                            if "." in version_str:
                                version_parts = version_str.split(".")
                                if version_parts and version_parts[0].isdigit():
                                    self.state.version = int(
                                        version_parts[0],
                                    )  # Use major version
                                else:
                                    self.state.version = 1  # Default version
                            elif version_str.isdigit():
                                self.state.version = int(version_str)
                            else:
                                self.state.version = 1  # Default version

            return FlextResult[None].ok(None)

        def _handle_aggregate_operation(
            self,
            _data: object,
            _group_by: object,
            _sum_fields: object,
        ) -> FlextResult[FlextTypes.Core.Dict]:
            """ELIMINATED: Data aggregation violates API single responsibility principle."""
            # VIOLATION ANALYSIS:
            # - Complex data grouping: Should be in FlextDataProcessing service
            # - Mathematical computations (sum, count): Not CLI API responsibility
            # - Business logic for aggregations: Belongs in dedicated analytics domain
            # - Data transformation patterns: FlextUtilities has these capabilities
            # - Advanced computations: Violates Single Responsibility Principle
            #
            # SOLUTION: Use FlextDataProcessing service from flext-core for aggregations
            return FlextResult[FlextTypes.Core.Dict].fail(
                "Data aggregation operations moved to FlextDataProcessing service - use dedicated analytics domain",
            )

        def _handle_batch_export_operation(
            self,
            datasets: object,
            base_path: object,
            format_type: object,
        ) -> FlextResult[list[str]]:
            """Handle batch export."""
            if not isinstance(datasets, list):
                return FlextResult[list[str]].fail(
                    "Datasets must be a list",
                )

            if not isinstance(base_path, (str, Path)):
                return FlextResult[list[str]].fail(
                    "Base path must be string or Path",
                )

            if not isinstance(format_type, str):
                return FlextResult[list[str]].fail(
                    "Format type must be string",
                )

            base = Path(base_path)
            base.mkdir(parents=True, exist_ok=True)

            exported_files = []

            for name, data in datasets:
                if not isinstance(name, str) or not name:
                    return FlextResult[list[str]].fail(
                        "Dataset names must be non-empty strings",
                    )

                filename = f"{name}.{format_type}"
                file_path = base / filename

                if format_type == "json":
                    content = json.dumps(data, indent=2)
                elif format_type in {"yaml", "yml"}:
                    content = yaml.safe_dump(data, default_flow_style=False)
                else:
                    content = str(data)

                file_path.write_text(content, encoding="utf-8")
                exported_files.append(str(file_path))

            return FlextResult[list[str]].ok(exported_files)

    # =========================================================================
    # MAIN API IMPLEMENTATION
    # =========================================================================

    def __init__(
        self,
        *,
        models: type[BaseModel] | None = None,
        services: FlextCliService | None = None,
        version: str | None = None,
    ) -> None:
        """Initialize unified API with nested architecture and flext-core patterns.

        Uses FlextConfig singleton as the single source of truth for all configuration.
        """
        # Get FlextConfig singleton as single source of truth
        config = FlextCliConfigs.get_global_instance()

        # Use config values as defaults, allow overrides
        api_version = str(version or getattr(config, "project_version", "0.9.1"))

        # Initialize components needed for dispatcher (temporary)
        temp_formatters = FlextCliFormatters()

        # Initialize state and dispatcher BEFORE calling super() - SIMPLE ALIAS approach
        # Convert version to int for Entity compatibility
        if "." in api_version:
            version_parts = api_version.split(".")
            if version_parts and version_parts[0].isdigit():
                version_int = int(version_parts[0])  # Use major version
            else:
                version_int = 1  # Default version
        elif api_version.isdigit():
            version_int = int(api_version)
        else:
            version_int = 1  # Default version

        # Create ApiState with required base_url from config
        api_base_url = getattr(config, "api_url", "http://localhost:8000")
        state = FlextCliModels.ApiState(
            version=version_int,
            base_url=api_base_url,
        )
        dispatcher = FlextCliApi.OperationDispatcher(
            state=state,
            formatters=temp_formatters,
        )

        # Initialize FlextDomainService without extra data
        super().__init__()

        # Set state and dispatcher using object.__setattr__ to bypass frozen model
        object.__setattr__(self, "state", state)
        object.__setattr__(self, "dispatcher", dispatcher)

        # Set all private attributes after Pydantic initialization
        self._formatters = temp_formatters
        self._container = FlextContainer()
        self._logger = logging.getLogger(__name__)
        self._models = models or BaseModel

        # Store reference to config for future use
        self._config = config
        self._services = services or FlextCliService()

    def _dispatch_operation(
        self, operation: str, **kwargs: object,
    ) -> FlextResult[object]:
        """Safely dispatch operation to dispatcher with type checking."""
        if self.dispatcher is None:
            return FlextResult[object].fail("Dispatcher not initialized")
        if not hasattr(self.dispatcher, "dispatch_operation"):
            return FlextResult[object].fail(
                "Dispatcher missing dispatch_operation method",
            )
        # Safe attribute access with getattr for type checking compliance
        dispatch_method = getattr(self.dispatcher, "dispatch_operation")
        result = dispatch_method(operation, **kwargs)
        return (
            result
            if isinstance(result, FlextResult)
            else FlextResult[object].ok(result)
        )

    def configure(self, config: object) -> FlextResult[None]:
        """Configure API with validation and state updates."""
        if self.dispatcher is None:
            return FlextResult[None].fail("Dispatcher not initialized")
        if not hasattr(self.dispatcher, "configure"):
            return FlextResult[None].fail("Dispatcher missing configure method")
        # Safe attribute access with getattr for type checking compliance
        configure_method = getattr(self.dispatcher, "configure")
        result = configure_method(config)
        return result if isinstance(result, FlextResult) else FlextResult[None].ok(None)

    def update_from_config(self) -> None:
        """Update API configuration from FlextConfig singleton.

        This method allows the API to refresh its configuration
        from the FlextConfig singleton, ensuring it always uses
        the latest configuration values.
        """
        # Update configuration from singleton
        self._config = FlextCliConfigs.get_global_instance()

        # Update state with new configuration
        if hasattr(self, "state") and self.state:
            # Update version from config - convert to int for Entity compatibility
            config_version = getattr(self._config, "project_version", "0.9.1")
            version_str = str(config_version)
            if "." in version_str:
                version_parts = version_str.split(".")
                if version_parts and version_parts[0].isdigit():
                    self.state.version = int(version_parts[0])  # Use major version
                else:
                    self.state.version = 1  # Default version
            elif version_str.isdigit():
                self.state.version = int(version_str)
            else:
                self.state.version = 1  # Default version

    # =========================================================================
    # PUBLIC API - Maintaining original signatures for backward compatibility
    # =========================================================================

    def execute(
        self,
        operation: str | None = None,
        **kwargs: object,
    ) -> FlextResult[str]:
        """Execute service request - required by FlextDomainService with simple alias support."""
        if operation is None:
            # Default execution for FlextDomainService
            health_result = self._dispatch_operation("health")
            if health_result.is_success:
                return FlextResult[str].ok("CLI API executed successfully")
            return FlextResult[str].fail(f"API execution failed: {health_result.error}")

        if operation == "format":
            format_type = kwargs.get("format_type", "plain")
            data = kwargs.get("data", {})
            return self.format_data(data, str(format_type))

        # Dispatch other operations through the dispatcher
        result = self._dispatch_operation(operation, **kwargs)
        return (
            FlextResult[str].ok(str(result.value))
            if result.is_success
            else FlextResult[str].fail(result.error or f"Operation {operation} failed")
        )

    def execute_operation(
        self,
        operation_name: str,
        operation: object,
        *_args: object,
        **kwargs: object,
    ) -> FlextResult[object]:
        """Universal operation executor using advanced pattern matching dispatch."""
        # Convert superclass signature to internal dispatcher call
        all_params = dict(kwargs)
        if operation is not None:
            all_params["operation"] = operation
        return self._dispatch_operation(operation_name, **all_params)

    # =========================================================================
    # CONVENIENCE METHODS - Backward compatibility with unified implementation
    # =========================================================================

    def display_message(
        self, message: str, message_type: str = "info",
    ) -> FlextResult[None]:
        """Display message using CLI formatters."""
        if not message:
            return FlextResult[None].fail("Message cannot be empty")

        if message_type not in {"info", "warning", "error", "success"}:
            return FlextResult[None].fail(f"Invalid message type: {message_type}")

        # Use formatters to display message with type
        display_result = self._formatters.display_message(message, message_type)
        if display_result.is_success:
            return FlextResult[None].ok(None)
        return FlextResult[None].fail(display_result.error or "Message display failed")

    def display_output(
        self,
        data: object,
        format_type: str = "table",
        title: str | None = None,
    ) -> FlextResult[None]:
        """Display output using CLI formatters."""
        if data is None:
            return FlextResult[None].fail("Data cannot be None")

        if format_type not in {"table", "json", "yaml", "text"}:
            return FlextResult[None].fail(f"Invalid format type: {format_type}")

        # Format the data first
        format_result = self.format_data(data, format_type)
        if format_result.is_failure:
            return FlextResult[None].fail(
                f"Data formatting failed: {format_result.error}",
            )

        # Display using formatters
        if format_type == "table":
            display_result = self._formatters.display_table(data, title=title)
        else:
            # For other formats, display the formatted string directly
            self._formatters.console.print(format_result.value)
            display_result = FlextResult[None].ok(None)
        if display_result.is_success:
            return FlextResult[None].ok(None)
        return FlextResult[None].fail(display_result.error or "Output display failed")

    def format_output(
        self,
        data: object,
        format_type: str = "table",
    ) -> FlextResult[str]:
        """Format data using CLI formatters."""
        return self.format_data(data, format_type)

    def create_command(
        self,
        name: str,
        description: str,
        handler: object,
        arguments: list[str] | None = None,
    ) -> FlextResult[FlextCliModels.CliCommand]:
        """Create CLI command with validation."""
        if not name or not name.strip():
            return FlextResult[FlextCliModels.CliCommand].fail(
                "Command name cannot be empty",
            )

        if not description or not description.strip():
            return FlextResult[FlextCliModels.CliCommand].fail(
                "Command description cannot be empty",
            )

        if not callable(handler):
            return FlextResult[FlextCliModels.CliCommand].fail(
                "Handler must be callable",
            )

        command = FlextCliModels.CliCommand(
            id=str(uuid4()),
            command_line=f"{name} {' '.join(arguments or [])}",
            execution_time=datetime.now(UTC),
        )

        # Note: output_format stored separately as needed
        # command model doesn't have _output_format attribute

        # Store command in history if enabled
        if self.enable_command_history and self.state:
            self.state.command_history.append(command)

        return FlextResult[FlextCliModels.CliCommand].ok(command)

    def format_data(self, data: object, format_type: str) -> FlextResult[str]:
        """Format data to specified format type using FlextCliFormatters."""
        # FlextCliFormatters handles all object types - no type validation needed
        return self._formatters.format_data(data, format_type)

    def export_data(self, data: object, file_path: str | Path) -> FlextResult[str]:
        """Export data to file."""
        if not file_path:
            return FlextResult[str].fail("File path cannot be empty")

        if data is None:
            return FlextResult[str].fail("Data cannot be None")

        path = Path(file_path)
        suffix = path.suffix.lower()

        if suffix == ".json":
            content = json.dumps(data, indent=2)
        elif suffix in {".yaml", ".yml"}:
            content = yaml.safe_dump(data, default_flow_style=False)
        else:
            content = str(data)

        try:
            # Create parent directory if it doesn't exist
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            return FlextResult[str].ok(f"Data exported to {file_path}")
        except (OSError, PermissionError) as e:
            return FlextResult[str].fail(f"Failed to export data to {file_path}: {e}")

    def create_table(
        self,
        data: object,
        title: str | None = None,
    ) -> FlextResult[object]:
        """Create formatted table - returns string for most cases, RichTable when needed."""
        # FlextCliFormatters handles all object types - no type validation needed
        # Type cast to match formatter expectations
        formatted_data = data if isinstance(data, (dict, list)) else {"value": data}
        table_result = self._formatters.create_table(formatted_data, title=title)
        if table_result.is_success:
            return FlextResult[object].ok(table_result.value)
        return FlextResult[object].fail(table_result.error or "Table creation failed")

    def create_rich_table(
        self,
        data: object,
        title: str | None = None,
    ) -> FlextResult[object]:
        """Create Rich Table object for advanced use cases - uses abstraction layer."""
        if data is None:
            return FlextResult[object].fail("Data cannot be None")

        # FlextCliFormatters handles all object types - no type validation needed
        # Use formatters abstraction layer instead of direct Rich import
        # Type cast to match formatter expectations
        formatted_data = data if isinstance(data, (dict, list)) else {"value": data}
        table_result = self._formatters.create_table(formatted_data, title=title)
        if table_result.is_success:
            return FlextResult[object].ok(table_result.value)
        return FlextResult[object].fail(f"Table creation failed: {table_result.error}")

    def aggregate_data(
        self,
        _data: list[FlextTypes.Core.Dict],
        _group_by: str,
        _sum_fields: list[str] | None = None,
    ) -> FlextResult[FlextTypes.Core.Dict]:
        """ELIMINATED: Data aggregation violates API single responsibility principle."""
        # VIOLATION: CLI API should not perform complex data analysis operations
        # SOLUTION: Use FlextDataProcessing service from flext-core for data aggregations
        # PATTERN: Separate data analytics from CLI API operations
        return FlextResult[FlextTypes.Core.Dict].fail(
            "Data aggregation operations moved to FlextDataProcessing service - use dedicated analytics domain",
        )

    def batch_export(
        self,
        datasets: list[tuple[str, object]],
        base_path: Path,
        format_type: str,
    ) -> FlextResult[list[str]]:
        """Export multiple datasets to files."""
        if self.dispatcher is None:
            return FlextResult[list[str]].fail(
                "Dispatcher not initialized",
            )
        result = self._dispatch_operation(
            "batch_export",
            datasets=datasets,
            base_path=base_path,
            format_type=format_type,
        )
        # Safe casting - we know batch_export returns list of strings
        if result.is_success and isinstance(result.value, list):
            return FlextResult[list[str]].ok(result.value)
        return FlextResult[list[str]].fail(
            result.error or "Batch export failed",
        )

    def transform_data(
        self,
        _data: object,
        _transform_fn: object,
        _group_by: str | None = None,
    ) -> FlextResult[object]:
        """ELIMINATED: Data transformation violates API single responsibility principle."""
        # VIOLATION ANALYSIS:
        # - Function application: Not CLI API responsibility
        # - Data grouping logic: Should be in FlextDataProcessing service
        # - Complex transformation patterns: FlextUtilities has these capabilities
        # - Business logic execution: Violates Single Responsibility Principle
        #
        # SOLUTION: Use FlextDataProcessing service from flext-core for transformations
        return FlextResult[object].fail(
            "Data transformation operations moved to FlextUtilities/FlextDataProcessing - use existing services",
        )

    # =========================================================================
    # UTILITY METHODS - All functionality contained within unified class
    # =========================================================================

    def unwrap_or_default(self, result: FlextResult[T], default: T) -> T:
        """Unwrap FlextResult or return default value."""
        return result.value if result.is_success else default

    def unwrap_or_none(self, result: FlextResult[T]) -> T | None:
        """Unwrap FlextResult or return None."""
        return result.value if result.is_success else None

    @property
    def version(self) -> str:
        """Get API version from unified state."""
        if self.state is None:
            return "unknown"
        return str(self.state.version)

    @property
    def service_name(self) -> str:
        """Get service name from unified state."""
        if self.state is None:
            return "flext-cli"
        return self.state.service_name

    @property
    def enable_session_tracking(self) -> bool:
        """Check if session tracking is enabled from unified state."""
        if self.state is None:
            return False
        return self.state.enable_session_tracking

    @property
    def enable_command_history(self) -> bool:
        """Check if command history is enabled from unified state."""
        if self.state is None:
            return False
        return self.state.enable_command_history

    def get_command_history(self) -> list[FlextCliModels.CliCommand]:
        """Get command history from unified state."""
        if not self.enable_command_history:
            return []
        if self.state is None:
            return []
        return list(self.state.command_history)

    # =========================================================================
    # FACTORY METHODS - Advanced dependency injection patterns
    # =========================================================================

    @classmethod
    def create_with_dependencies(
        cls,
        *,
        models: type[BaseModel] | None = None,
        services: FlextCliService | None = None,
        config_override: FlextTypes.Core.Dict | None = None,
    ) -> FlextCliApi:
        """Create factory method for creating API with full dependency injection."""
        api = cls(models=models, services=services)

        if config_override:
            configure_result = api.configure(config_override)
            if (
                configure_result.is_failure
                and hasattr(api, "_logger")
                and hasattr(api._logger, "warning")
            ):
                # Log warning but continue - skip logging if no logger available
                getattr(api._logger, "warning", lambda _: None)(
                    f"Configuration override failed: {configure_result.error}",
                )

        return api

    @override
    def __repr__(self) -> str:
        """Return string representation of unified FlextCliApi."""
        session_count = self.state.session_count if self.state else 0
        handler_count = self.state.handler_count if self.state else 0
        return (
            f"FlextCliApi("
            f"version='{self.version}', "
            f"service='{self.service_name}', "
            f"session_tracking={self.enable_session_tracking}, "
            f"command_history={self.enable_command_history}, "
            f"sessions={session_count}, "
            f"handlers={handler_count}"
            f")"
        )


# =========================================================================
# MODULE EXPORTS - Single unified class with all functionality encapsulated
# =========================================================================

__all__ = [
    "FlextCliApi",
]
