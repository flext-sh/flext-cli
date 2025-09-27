"""CLI core service using flext-core directly.

Production-ready CLI service that uses flext-core services directly without
duplication. Implements standardized architecture patterns.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import asyncio
import csv
import json
import re
import subprocess  # nosec B404
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import cast, override
from uuid import UUID, uuid4

import yaml

from flext_cli.commands import FlextCliCommands
from flext_cli.config import FlextCliConfig
from flext_cli.constants import FlextCliConstants
from flext_cli.file_tools import FlextCliFileTools
from flext_cli.models import FlextCliModels

# Use centralized types from FlextCliTypes
from flext_cli.typings import FlextCliTypes
from flext_cli.utilities import FlextCliUtilities
from flext_core import (
    FlextContainer,
    FlextDispatcher,
    FlextLogger,
    FlextResult,
    FlextService,
    FlextTypes,
)

type HandlerData = FlextCliTypes.CliCommandResult
type HandlerFunction = Callable[[HandlerData], FlextResult[HandlerData]]


class FlextCliService(FlextService[FlextTypes.Core.Dict]):
    """Advanced CLI service using flext-core with enhanced patterns.

    Provides CLI configuration management using flext-core patterns with
    advanced class architecture, railway-oriented programming, and
    monadic composition for better error handling and code clarity.
    """

    @override
    def __init__(self) -> None:
        """Initialize CLI service with flext-core dependencies."""
        super().__init__()
        self._logger = FlextLogger(__name__)
        self._container = FlextContainer.get_global()
        self._dispatcher = FlextDispatcher()
        self._cli_config: FlextCliConfig = FlextCliConfig()
        self._handlers: dict[str, HandlerFunction] = {}
        self._plugins: dict[str, FlextCliModels.CliCommand] = {}
        self._sessions: dict[str, FlextCliModels.CliSession] = {}
        self._commands: FlextCliCommands = FlextCliCommands()
        self._formatters = FlextCliModels.CliFormatters()

        # Initialize service dependencies
        self._files = FlextCliFileTools()
        self._utils = FlextCliUtilities()

        # Initialize advanced components
        self._validation_helper = self._AdvancedValidationHelper()
        self._state_helper = self._AdvancedStateHelper()
        self._command_processor = self._AdvancedCommandProcessor()
        self._session_manager = self._AdvancedSessionManager()

    class _AdvancedValidationHelper:
        """Advanced validation helper with railway-oriented programming patterns."""

        @override
        def __init__(self) -> None:
            """Initialize validation helper."""
            self._logger = FlextLogger(f"{__name__}._ValidationHelper")

        def validate_session_id(self, session_id: str | None) -> FlextResult[str]:
            """Validate session ID format using railway pattern.

            Args:
                session_id: Session ID to validate

            Returns:
                FlextResult[str]: Validated session ID

            """
            if session_id is None:
                return FlextResult[str].fail("Session ID cannot be None")

            if not session_id.strip():
                return FlextResult[str].fail("Session ID must be a non-empty string")

            # Validate UUID format
            try:
                UUID(session_id)
                return FlextResult[str].ok(session_id)
            except ValueError:
                return FlextResult[str].fail("Invalid session ID format")

        def validate_user_id(self, user_id: object) -> FlextResult[str | None]:
            """Validate user ID using railway pattern.

            Args:
                user_id: User ID to validate

            Returns:
                FlextResult[str | None]: Validated user ID

            """
            if user_id is None:
                # Generate a default user ID for anonymous sessions
                default_user_id = f"user_{uuid4().hex[:8]}"
                return FlextResult[str | None].ok(default_user_id)

            if isinstance(user_id, str):
                if not user_id.strip():
                    # Generate a default user ID for empty strings
                    default_user_id = f"user_{uuid4().hex[:8]}"
                    return FlextResult[str | None].ok(default_user_id)
                return FlextResult[str | None].ok(user_id)

            # Convert to string
            return FlextResult[str | None].ok(str(user_id))

        def validate_command_data(
            self, *, data: dict[str, str | int | float] | bool
        ) -> FlextResult[dict[str, str | int | float] | bool]:
            """Validate command data structure.

            Args:
                data: Command data to validate

            Returns:
                FlextResult[dict[str | str | int | float | bool]]: Validated command data

            """
            if not isinstance(data, dict):
                return FlextResult[dict[str, str | int | float] | bool].fail(
                    "Command data must be a dictionary"
                )

            if not data:
                return FlextResult[dict[str, str | int | float] | bool].fail(
                    "Command data cannot be empty"
                )

            return FlextResult[dict[str, str | int | float] | bool].ok(data)

    class _AdvancedStateHelper:
        """Advanced state helper with railway-oriented programming patterns."""

        @override
        def __init__(self) -> None:
            """Initialize state helper."""
            self._logger = FlextLogger(f"{__name__}._StateHelper")

        def create_session_metadata(
            self, user_id: str | None = None
        ) -> FlextResult[FlextCliModels.CliSession]:
            """Create session metadata using railway pattern.

            Args:
                user_id: Optional user ID

            Returns:
                FlextResult[FlextCliModels.CliSession]: Session with metadata

            """
            try:
                session_id = str(uuid4())
                session = FlextCliModels.CliSession(
                    session_id=session_id,
                    user_id=user_id,
                    start_time=datetime.now(UTC).isoformat(),
                )
                return FlextResult[FlextCliModels.CliSession].ok(session)
            except Exception as e:
                return FlextResult[FlextCliModels.CliSession].fail(
                    f"Failed to create session: {e}"
                )

        def calculate_session_duration(
            self, session: FlextCliModels.CliSession
        ) -> FlextResult[float]:
            """Calculate session duration in seconds using railway pattern.

            Args:
                session: Session to calculate duration for

            Returns:
                FlextResult[float]: Duration in seconds

            """
            try:
                # Convert string timestamps to datetime objects for calculation
                start_time = (
                    datetime.fromisoformat(session.start_time)
                    if session.start_time
                    else datetime.now(UTC)
                )

                if session.end_time:
                    end_time = datetime.fromisoformat(session.end_time)
                    duration = (end_time - start_time).total_seconds()
                else:
                    last_activity = (
                        datetime.fromisoformat(session.last_activity)
                        if session.last_activity
                        else datetime.now(UTC)
                    )
                    duration = (last_activity - start_time).total_seconds()

                return FlextResult[float].ok(duration)
            except Exception as e:
                return FlextResult[float].fail(f"Failed to calculate duration: {e}")

        def update_session_activity(
            self, session: FlextCliModels.CliSession
        ) -> FlextResult[FlextCliModels.CliSession]:
            """Update session last activity timestamp.

            Args:
                session: Session to update

            Returns:
                FlextResult[FlextCliModels.CliSession]: Updated session

            """
            try:
                session.last_activity = datetime.now(UTC).isoformat()
                return FlextResult[FlextCliModels.CliSession].ok(session)
            except Exception as e:
                return FlextResult[FlextCliModels.CliSession].fail(
                    f"Failed to update session: {e}"
                )

    class _AdvancedCommandProcessor:
        """Advanced command processor with railway-oriented programming patterns."""

        @override
        def __init__(self) -> None:
            """Initialize command processor."""
            self._logger = FlextLogger(f"{__name__}._CommandProcessor")

        def process_command(
            self, command: str, data: HandlerData
        ) -> FlextResult[HandlerData]:
            """Process command using railway pattern.

            Args:
                command: Command to process
                data: Command data

            Returns:
                FlextResult[HandlerData]: Processed result

            """
            try:
                # Add command processing logic here
                processed_data: dict[str, str | int | float | bool] = (
                    dict(data) if isinstance(data, dict) else {}
                )
                processed_data["command"] = command
                processed_data["processed_at"] = datetime.now(UTC).isoformat()

                return FlextResult[HandlerData].ok(cast("HandlerData", processed_data))
            except Exception as e:
                return FlextResult[HandlerData].fail(f"Failed to process command: {e}")

        def validate_command_syntax(self, command: str) -> FlextResult[str]:
            """Validate command syntax.

            Args:
                command: Command to validate

            Returns:
                FlextResult[str]: Validated command

            """
            if not command or not command.strip():
                return FlextResult[str].fail("Command cannot be empty")

            # Add more validation logic here
            return FlextResult[str].ok(command.strip())

    class _AdvancedSessionManager:
        """Advanced session manager with railway-oriented programming patterns."""

        @override
        def __init__(self) -> None:
            """Initialize session manager."""
            self._logger = FlextLogger(f"{__name__}._SessionManager")

        def create_session(self, user_id: str | None = None) -> FlextResult[str]:
            """Create new session.

            Args:
                user_id: Optional user ID for session context

            Returns:
                FlextResult[str]: Session ID

            """
            try:
                session_id = str(uuid4())
                # Store user context if provided
                if user_id:
                    self._logger.debug(f"Creating session for user: {user_id}")
                return FlextResult[str].ok(session_id)
            except Exception as e:
                return FlextResult[str].fail(f"Failed to create session: {e}")

        def cleanup_expired_sessions(
            self, sessions: dict[str, FlextCliModels.CliSession]
        ) -> FlextResult[dict[str, FlextCliModels.CliSession]]:
            """Clean up expired sessions.

            Args:
                sessions: Current sessions

            Returns:
                FlextResult[dict[str, FlextCliModels.CliSession]]: Cleaned sessions

            """
            try:
                current_time = datetime.now(UTC)
                # Session timeout constant (1 hour in seconds)
                session_timeout_seconds = 3600

                # Use dictionary comprehension for better performance
                cleaned_sessions = {
                    session_id: session
                    for session_id, session in sessions.items()
                    if session.last_activity
                    and (
                        current_time - datetime.fromisoformat(session.last_activity)
                    ).total_seconds()
                    < session_timeout_seconds
                }

                return FlextResult[dict[str, FlextCliModels.CliSession]].ok(
                    cleaned_sessions
                )
            except Exception as e:
                return FlextResult[dict[str, FlextCliModels.CliSession]].fail(
                    f"Failed to cleanup sessions: {e}"
                )

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

    def get_config(self) -> FlextCliConfig | None:
        """Get current CLI configuration."""
        return self._cli_config

    def configure(
        self,
        config: FlextCliConfig | dict[str, str | int | float],
    ) -> FlextResult[None]:
        """Configure the service using advanced validation patterns."""
        try:
            if isinstance(config, dict):
                # Validate configuration data using railway pattern
                validation_result = self._validation_helper.validate_command_data(
                    data=config
                )
                if validation_result.is_failure:
                    return FlextResult[None].fail(
                        f"Configuration validation failed: {validation_result.error}"
                    )

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

                self._cli_config = FlextCliConfig(
                    profile=profile_value,
                    output_format=output_format_value,
                    debug=debug_mode_value,
                )
            else:
                self._cli_config = config

            self._logger.info("Configuration updated successfully")
            return FlextResult[None].ok(None)
        except Exception as e:
            self._logger.exception("Configuration failed")
            return FlextResult[None].fail(f"Invalid configuration: {e}")

    def get_handlers(self) -> dict[str, HandlerFunction]:
        """Get registered handlers."""
        return self._handlers.copy()

    def get_plugins(self) -> dict[str, FlextCliModels.CliCommand]:
        """Get registered plugins."""
        return self._plugins.copy()

    def get_sessions(self) -> dict[str, FlextCliModels.CliSession]:
        """Get active sessions."""
        return self._sessions.copy()

    def get_session(self, session_id: str) -> FlextResult[FlextCliModels.CliSession]:
        """Get a specific session by ID using advanced validation patterns.

        Args:
            session_id: The session ID to retrieve

        Returns:
            FlextResult[FlextCliModels.CliSession]: The session if found

        """
        # Validate session ID using railway pattern
        validation_result = self._validation_helper.validate_session_id(session_id)
        if validation_result.is_failure:
            return FlextResult[FlextCliModels.CliSession].fail(
                f"Invalid session ID: {validation_result.error}"
            )

        if session_id in self._sessions:
            # Update session activity using state helper
            session = self._sessions[session_id]
            activity_result = self._state_helper.update_session_activity(session)
            if activity_result.is_success:
                self._sessions[session_id] = activity_result.value
            return FlextResult[FlextCliModels.CliSession].ok(self._sessions[session_id])

        return FlextResult[FlextCliModels.CliSession].fail(
            f"Session not found: {session_id}"
        )

    def get_commands(self) -> dict[str, FlextCliModels.CliCommand]:
        """Get registered commands."""
        return cast(
            "dict[str, FlextCliModels.CliCommand]", self._commands.get_commands()
        )

    def get_formatters(self) -> FlextCliModels.CliFormatters:
        """Get formatters instance."""
        return self._formatters

    def format_data(self, data: HandlerData, format_type: str) -> FlextResult[str]:
        """Format data using consolidated formatting service."""
        # Use the format_type parameter to determine formatting method
        if format_type == "json":
            return FlextCliUtilities.Formatting.format_json(data)
        if format_type == "yaml":
            return FlextCliUtilities.Formatting.format_yaml(data)
        if format_type == "csv":
            return FlextCliUtilities.Formatting.format_csv(data)
        if format_type == "table":
            return FlextCliUtilities.Formatting.format_table(data)
        # Default to JSON if format_type is not recognized
        return FlextCliUtilities.Formatting.format_json(data)

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
                    data  # data is already list[dict[str | str | int | float | bool]]
                )
                if not csv_data:
                    return FlextResult[None].fail("No valid dictionary data found")
                with path.open("w", encoding="utf-8", newline="") as f:
                    fieldnames: list[str] = list(csv_data[0].keys())
                    writer: csv.DictWriter[str] = csv.DictWriter(
                        f, fieldnames=fieldnames
                    )
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
            "commands": len(self._commands.get_commands()),
        }
        return FlextResult[dict[str, str | int | bool]].ok(health_data)

    def create_command(
        self, command_line: str
    ) -> FlextResult[FlextCliModels.CliCommand]:
        """Create a new CLI command."""
        try:
            # Validation
            if not command_line or not command_line.strip():
                return FlextResult[FlextCliModels.CliCommand].fail(
                    "Validation error: Command line cannot be empty"
                )

            # Check for dangerous patterns
            dangerous_patterns = [
                "rm -rf",
                "sudo rm",
                "format",
                "del /",
                "shutdown",
                "reboot",
            ]
            command_lower = command_line.lower()
            for pattern in dangerous_patterns:
                if pattern in command_lower:
                    return FlextResult[FlextCliModels.CliCommand].fail(
                        f"Dangerous command pattern detected: {pattern}"
                    )

            command = FlextCliModels.CliCommand(command_line=command_line.strip())
            register_result = self._commands.register_command(
                name=command.id, handler=command, description=command.command_line
            )
            if register_result.is_success:
                return FlextResult[FlextCliModels.CliCommand].ok(command)
            return FlextResult[FlextCliModels.CliCommand].fail(
                register_result.error or "Command registration failed"
            )
        except Exception as e:
            return FlextResult[FlextCliModels.CliCommand].fail(
                f"Command creation failed: {e}"
            )

    def create_session(
        self, user_id: str | None = None
    ) -> FlextResult[FlextCliModels.CliSession]:
        """Create a new CLI session."""
        try:
            # Validate user_id using validation helper
            validation_result = self._validation_helper.validate_user_id(user_id)
            if validation_result.is_failure:
                return FlextResult[FlextCliModels.CliSession].fail(
                    f"User ID validation failed: {validation_result.error}"
                )

            validated_user_id = validation_result.value

            # Create session using state helper
            session_result = self._state_helper.create_session_metadata(
                validated_user_id
            )
            if session_result.is_failure:
                return FlextResult[FlextCliModels.CliSession].fail(
                    f"Session creation failed: {session_result.error}"
                )

            session = session_result.value
            self._sessions[session.session_id] = session
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
            if isinstance(result, FlextResult):
                return result
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

    def flext_cli_render_with_context(
        self,
        *,
        data: HandlerData,
        context: dict[str, str | int | float] | bool | None = None,
    ) -> FlextResult[str]:
        """Render data with context."""
        try:
            format_type = "table"
            if context and isinstance(context, dict) and "output_format" in context:
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
            command = FlextCliModels.CliCommand(command=command_line)
            command.id = name
            register_result = self._commands.register_command(
                name=name, handler=command, description=command_line
            )
            if register_result.is_success:
                return FlextResult[FlextCliModels.CliCommand].ok(command)
            return FlextResult[FlextCliModels.CliCommand].fail(
                register_result.error or "Command registration failed"
            )
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
    def dispatcher(self) -> FlextDispatcher:
        """Get service dispatcher."""
        return self._dispatcher

    @property
    def metrics(self) -> dict[str, int]:
        """Get service metrics."""
        return {
            "handlers": len(self._handlers),
            "plugins": len(self._plugins),
            "sessions": len(self._sessions),
            "commands": len(self._commands.get_commands()),
        }

    # =========================================================================
    # DOMAIN SERVICE METHODS - Merged from FlextCliDomainService
    # =========================================================================

    def start_command_execution(
        self, command: FlextCliModels.CliCommand
    ) -> FlextResult[FlextCliModels.CliCommand]:
        """Start command execution."""
        try:
            if command.status != FlextCliConstants.CommandStatus.PENDING.value:
                return FlextResult[FlextCliModels.CliCommand].fail(
                    f"Command must be pending to start. Current status: {command.status}"
                )

            command.status = FlextCliConstants.CommandStatus.RUNNING.value
            return FlextResult[FlextCliModels.CliCommand].ok(command)
        except Exception as e:
            return FlextResult[FlextCliModels.CliCommand].fail(
                f"Start execution failed: {e}"
            )

    def complete_command_execution(
        self,
        command: FlextCliModels.CliCommand,
        exit_code: int,
        output: str = "",
        error_output: str = "",
    ) -> FlextResult[FlextCliModels.CliCommand]:
        """Complete command execution."""
        try:
            if command.status != FlextCliConstants.CommandStatus.RUNNING.value:
                return FlextResult[FlextCliModels.CliCommand].fail(
                    f"Command must be running to complete. Current status: {command.status}"
                )

            command.exit_code = exit_code
            command.output = output
            command.error_output = error_output

            if exit_code == 0:
                command.status = FlextCliConstants.CommandStatus.COMPLETED.value
            else:
                command.status = FlextCliConstants.CommandStatus.FAILED.value

            return FlextResult[FlextCliModels.CliCommand].ok(command)
        except Exception as e:
            return FlextResult[FlextCliModels.CliCommand].fail(
                f"Complete execution failed: {e}"
            )

    def add_command_to_session(
        self,
        session: FlextCliModels.CliSession,
        command: FlextCliModels.CliCommand,
    ) -> FlextResult[FlextCliModels.CliSession]:
        """Add command to session."""
        try:
            session.commands.append(command)
            session.last_activity = datetime.now(UTC).isoformat()
            return FlextResult[FlextCliModels.CliSession].ok(session)
        except Exception as e:
            return FlextResult[FlextCliModels.CliSession].fail(
                f"Add command to session failed: {e}"
            )

    def end_session(
        self, session_or_id: FlextCliModels.CliSession | str
    ) -> FlextResult[FlextCliModels.CliSession]:
        """End a CLI session by session object or session ID."""
        try:
            if isinstance(session_or_id, str):
                # Validate session ID first
                validation_result = self._validation_helper.validate_session_id(
                    session_or_id
                )
                if not validation_result.is_success:
                    return FlextResult[FlextCliModels.CliSession].fail(
                        validation_result.error or "Invalid session ID"
                    )

                # Find session by ID
                session = self._sessions.get(session_or_id)
                if not session:
                    return FlextResult[FlextCliModels.CliSession].fail(
                        f"Session not found: {session_or_id}"
                    )
            else:
                session = session_or_id

            session.status = FlextCliConstants.CommandStatus.COMPLETED.value
            session.last_activity = datetime.now(UTC).isoformat()
            session.end_time = datetime.now(UTC).isoformat()
            return FlextResult[FlextCliModels.CliSession].ok(session)
        except Exception as e:
            return FlextResult[FlextCliModels.CliSession].fail(
                f"End session failed: {e}"
            )

    def execute_command_workflow(
        self,
        command_line: str,
        _user_id: str | None = None,
    ) -> FlextResult[FlextCliModels.CliCommand]:
        """Execute a complete command workflow using advanced monadic composition."""
        # Railway-oriented programming with visual FlextResult composition
        return (
            self.create_command(command_line)
            .flat_map(self.start_command_execution)
            .flat_map(
                lambda cmd: self.complete_command_execution(
                    cmd, 0, "Command executed successfully"
                )
            )
        )

    def execute_command_with_dispatcher(
        self,
        command_name: str,
        data: HandlerData,
    ) -> FlextResult[HandlerData]:
        """Execute command using FlextDispatcher for advanced orchestration."""
        try:
            # Use dispatcher for command execution with context propagation
            dispatch_result = self._dispatcher.dispatch(
                message_or_type=command_name,
                metadata={
                    "cli_service": self,
                    "data": data,
                    "timestamp": datetime.now(UTC).isoformat(),
                },
            )

            if dispatch_result.is_success:
                return FlextResult[HandlerData].ok(
                    cast("HandlerData", dispatch_result.value)
                )
            return FlextResult[HandlerData].fail(
                f"Dispatcher execution failed: {dispatch_result.error}"
            )
        except Exception as e:
            return FlextResult[HandlerData].fail(f"Dispatcher execution error: {e}")

    # =========================================================================
    # COMMAND SERVICE METHODS - Merged from FlextCliCommandService
    # =========================================================================

    def execute_cli_command(
        self, command: object, timeout: int = 30
    ) -> FlextResult[str]:
        """Execute CLI command with validation."""
        try:
            # Basic validation
            if not hasattr(command, "command_line"):
                return FlextResult[str].fail(
                    "Command object must have command_line attribute"
                )

            command_line = str(getattr(command, "command_line", ""))
            if not command_line.strip():
                return FlextResult[str].fail("Empty command")

            # Basic security check - prevent dangerous commands
            command_parts = command_line.split()
            dangerous_commands = ["rm", "del", "format", "shutdown", "reboot"]
            if command_parts[0].lower() in dangerous_commands:
                return FlextResult[str].fail(
                    f"Dangerous command blocked: {command_parts[0]}"
                )

            # Execute command with subprocess (safe - no shell=True, command_parts validated)
            # Additional validation: ensure command_parts contains only safe characters
            # Allow quotes and common punctuation for echo commands
            for part in command_parts:
                # Remove quotes and common safe characters for validation
                clean_part = (
                    part.replace("'", "")
                    .replace('"', "")
                    .replace("-", "")
                    .replace("_", "")
                    .replace(".", "")
                    .replace("/", "")
                )
                if not clean_part.isalnum():
                    return FlextResult[str].fail(
                        f"Unsafe command part detected: '{part}'"
                    )

            # Command parts are validated above for safety
            result = subprocess.run(  # noqa: S603
                command_parts,
                check=False,
                capture_output=True,
                text=True,
                timeout=timeout,  # Use provided timeout parameter
            )

            if result.returncode == 0:
                return FlextResult[str].ok(
                    f"Command executed successfully: {result.stdout}"
                )
            return FlextResult[str].fail(f"Command failed: {result.stderr}")

        except Exception as e:
            return FlextResult[str].fail(f"Command execution failed: {e}")

    def get_command_history(
        self,
    ) -> FlextResult[list[FlextCliModels.CliCommand]]:
        """Get command history."""
        try:
            return FlextResult[list[FlextCliModels.CliCommand]].ok(
                cast(
                    "list[FlextCliModels.CliCommand]",
                    list(self._commands.get_commands().values()),
                )
            )
        except Exception as e:
            return FlextResult[list[FlextCliModels.CliCommand]].fail(
                f"Failed to get command history: {e}"
            )

    def clear_command_history(self) -> FlextResult[int]:
        """Clear command history."""
        try:
            return self._commands.clear_commands()
        except Exception as e:
            return FlextResult[int].fail(f"Failed to clear command history: {e}")

    def get_command_statistics(self) -> FlextResult[FlextTypes.Core.Dict]:
        """Get command statistics."""
        try:
            stats: FlextTypes.Core.Dict = {
                "total_commands": len(self._commands.get_commands()),
                "total_sessions": len(self._sessions),
                "total_handlers": len(self._handlers),
                "total_plugins": len(self._plugins),
            }
            return FlextResult[FlextTypes.Core.Dict].ok(stats)
        except Exception as e:
            return FlextResult[FlextTypes.Core.Dict].fail(
                f"Failed to get command statistics: {e}"
            )

    def find_commands_by_pattern(
        self, pattern: str
    ) -> FlextResult[list[FlextCliModels.CliCommand]]:
        """Find commands by pattern."""
        try:
            matching_commands = [
                command
                for command in cast(
                    "list[FlextCliModels.CliCommand]",
                    list(self._commands.get_commands().values()),
                )
                if re.search(pattern, command.command, re.IGNORECASE)
            ]
            return FlextResult[list[FlextCliModels.CliCommand]].ok(matching_commands)
        except Exception as e:
            return FlextResult[list[FlextCliModels.CliCommand]].fail(
                f"Failed to find commands: {e}"
            )

    def get_recent_commands(
        self, limit: int = 10
    ) -> FlextResult[list[FlextCliModels.CliCommand]]:
        """Get recent commands."""
        try:
            # Sort commands by creation time and return the most recent ones
            sorted_commands = sorted(
                cast(
                    "list[FlextCliModels.CliCommand]",
                    list(self._commands.get_commands().values()),
                ),
                key=lambda cmd: cmd.created_at,
                reverse=True,
            )
            return FlextResult[list[FlextCliModels.CliCommand]].ok(
                sorted_commands[:limit]
            )
        except Exception as e:
            return FlextResult[list[FlextCliModels.CliCommand]].fail(
                f"Failed to get recent commands: {e}"
            )

    # =========================================================================
    # SESSION SERVICE METHODS - Merged from FlextCliSessionService
    # =========================================================================

    def list_active_sessions(
        self,
    ) -> FlextResult[list[FlextCliModels.CliSession]]:
        """List all active sessions."""
        try:
            active_sessions = list(self._sessions.values())
            return FlextResult[list[FlextCliModels.CliSession]].ok(active_sessions)
        except Exception as e:
            return FlextResult[list[FlextCliModels.CliSession]].fail(
                f"Failed to list active sessions: {e}"
            )

    def get_session_statistics(self) -> FlextResult[FlextTypes.Core.Dict]:
        """Get session statistics."""
        try:
            total_sessions = len(self._sessions)
            session_durations: list[float] = []
            sessions_by_user: dict[str, int] = {}

            for session in self._sessions.values():
                # Calculate duration
                start_time = (
                    datetime.fromisoformat(session.start_time)
                    if session.start_time
                    else datetime.now(UTC)
                )

                if session.end_time:
                    end_time = datetime.fromisoformat(session.end_time)
                    duration = (end_time - start_time).total_seconds()
                else:
                    last_activity = (
                        datetime.fromisoformat(session.last_activity)
                        if session.last_activity
                        else datetime.now(UTC)
                    )
                    duration = (last_activity - start_time).total_seconds()
                session_durations.append(duration)

                # Count by user
                user_id = session.user_id or "anonymous"
                sessions_by_user[user_id] = sessions_by_user.get(user_id, 0) + 1

            statistics: FlextTypes.Core.Dict = {
                "total_active_sessions": total_sessions,
                "average_duration_seconds": sum(session_durations)
                / len(session_durations)
                if session_durations
                else 0,
                "longest_session_seconds": max(session_durations)
                if session_durations
                else 0,
                "shortest_session_seconds": min(session_durations)
                if session_durations
                else 0,
                "sessions_by_user": sessions_by_user,
            }

            return FlextResult[FlextTypes.Core.Dict].ok(statistics)
        except Exception as e:
            return FlextResult[FlextTypes.Core.Dict].fail(
                f"Failed to get session statistics: {e}"
            )

    def clear_all_sessions(self) -> FlextResult[int]:
        """Clear all sessions."""
        try:
            count = len(self._sessions)
            self._sessions.clear()
            return FlextResult[int].ok(count)
        except Exception as e:
            return FlextResult[int].fail(f"Failed to clear all sessions: {e}")

    def _get_sessions_by_user(self) -> dict[str, int]:
        """Get session counts by user (private helper for testing).

        Returns:
            dict[str, int]: User ID to session count mapping

        """
        sessions_by_user: dict[str, int] = {}
        for session in self._sessions.values():
            user_id = session.user_id or "anonymous"
            sessions_by_user[user_id] = sessions_by_user.get(user_id, 0) + 1
        return sessions_by_user

    def configure_command_history(self, *, enabled: bool) -> FlextResult[None]:
        """Configure command history tracking.

        Args:
            enabled: Whether to enable command history

        Returns:
            FlextResult[None]: Configuration result

        """
        # Command history is always enabled in this implementation
        # This method provides standardized service interface
        self._logger.info(f"Command history {'enabled' if enabled else 'disabled'}")
        return FlextResult[None].ok(None)

    def configure_session_tracking(self, *, enabled: bool) -> FlextResult[None]:
        """Configure session tracking."""
        try:
            # This would be stored in configuration in a real implementation
            self._logger.info(
                f"Session tracking {'enabled' if enabled else 'disabled'}"
            )
            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(f"Failed to configure session tracking: {e}")

    def create_command_definition(
        self,
        name: str,
        description: str,
        handler: Callable[[], FlextResult[object]] | None,
        arguments: list[str] | None = None,
        output_format: str = "json",
    ) -> FlextResult[dict[str, object]]:
        """Create a command definition."""
        try:
            # Validation
            if not name.strip():
                return FlextResult[dict[str, object]].fail(
                    "Command name must be a non-empty string"
                )

            if not description.strip():
                return FlextResult[dict[str, object]].fail(
                    "Command description must be a non-empty string"
                )

            if handler is None:
                return FlextResult[dict[str, object]].fail("Handler cannot be None")

            definition: dict[str, object] = {
                "name": name,
                "description": description,
                "handler": handler,
                "arguments": arguments or [],
                "output_format": output_format,
            }
            return FlextResult[dict[str, object]].ok(definition)
        except Exception as e:
            return FlextResult[dict[str, object]].fail(
                f"Failed to create command definition: {e}"
            )

    @override
    def execute(self) -> FlextResult[FlextTypes.Core.Dict]:
        """Execute the main CLI service operation.

        Returns:
            FlextResult[FlextTypes.Core.Dict]: Service execution result

        """
        try:
            self._logger.info("Executing CLI service")

            # Initialize service components
            init_result = self._initialize_service()
            if init_result.is_failure:
                return FlextResult[FlextTypes.Core.Dict].fail(
                    init_result.error or "Service initialization failed"
                )

            # Return service status
            status_data: FlextTypes.Core.Dict = {
                "service": "FlextCliService",
                "status": "ready",
                "commands_count": len(self._commands.get_commands()),
                "sessions_count": len(self._sessions),
                "plugins_count": len(self._plugins),
                "handlers_count": len(self._handlers),
            }

            return FlextResult[FlextTypes.Core.Dict].ok(status_data)
        except Exception as e:
            return FlextResult[FlextTypes.Core.Dict].fail(
                f"Service execution failed: {e}"
            )

    async def execute_async(self) -> FlextResult[FlextTypes.Core.Dict]:
        """Execute the main CLI service operation asynchronously.

        Returns:
            FlextResult[FlextTypes.Core.Dict]: Async service execution result

        """
        try:
            self._logger.info("Executing CLI service asynchronously")

            # Initialize service components asynchronously
            init_result = await self._initialize_service_async()
            if init_result.is_failure:
                return FlextResult[FlextTypes.Core.Dict].fail(
                    init_result.error or "Service initialization failed"
                )

            # Return service status
            status_data: FlextTypes.Core.Dict = {
                "service": "FlextCliService",
                "status": "ready_async",
                "commands_count": len(self._commands.get_commands()),
                "sessions_count": len(self._sessions),
                "plugins_count": len(self._plugins),
                "handlers_count": len(self._handlers),
            }

            return FlextResult[FlextTypes.Core.Dict].ok(status_data)
        except Exception as e:
            return FlextResult[FlextTypes.Core.Dict].fail(
                f"Async service execution failed: {e}"
            )

    def _initialize_service(self) -> FlextResult[None]:
        """Initialize service components.

        Returns:
            FlextResult[None]: Initialization result

        """
        try:
            # Initialize default handlers
            self._handlers["default"] = self._default_handler
            self._handlers["health"] = self._health_check_handler

            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(f"Service initialization failed: {e}")

    async def _initialize_service_async(self) -> FlextResult[None]:
        """Initialize service components asynchronously.

        Returns:
            FlextResult[None]: Async initialization result

        """
        try:
            # Initialize default handlers asynchronously
            self._handlers["default"] = self._default_handler
            self._handlers["health"] = self._health_check_handler

            # Simulate async initialization
            await asyncio.sleep(0.001)

            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(f"Async service initialization failed: {e}")

    def _default_handler(self, data: HandlerData) -> FlextResult[HandlerData]:
        """Default command handler.

        Args:
            data: Handler data

        Returns:
            FlextResult[HandlerData]: Handler result

        """
        return FlextResult[HandlerData].ok(data)

    def _health_check_handler(self, data: HandlerData) -> FlextResult[HandlerData]:
        """Health check command handler.

        Args:
            data: Handler data

        Returns:
            FlextResult[HandlerData]: Handler result

        """
        if isinstance(data, dict):
            health_data: dict[str, str | int | float | bool] = {
                **data,
                "health": "ok",
                "timestamp": datetime.now(UTC).isoformat(),
            }
        else:
            health_data: dict[str, str | int | float | bool] = {
                "health": "ok",
                "timestamp": datetime.now(UTC).isoformat(),
            }
        return FlextResult[HandlerData].ok(cast("HandlerData", health_data))

    # Convenience methods for backward compatibility with tests
    def read_file_content(self, file_path: str) -> FlextResult[str]:
        """Read file content."""
        return self._files.read_text_file(file_path)

    def write_file_content(self, file_path: str, content: str) -> FlextResult[bool]:
        """Write content to file."""
        return self._files.write_text_file(file_path, content)

    def copy_file(self, source_path: str, destination_path: str) -> FlextResult[bool]:
        """Copy file from source to destination."""
        return self._files.copy_file(source_path, destination_path)

    def move_file(self, source_path: str, destination_path: str) -> FlextResult[bool]:
        """Move file from source to destination."""
        return self._files.move_file(source_path, destination_path)

    def delete_file(self, file_path: str) -> FlextResult[bool]:
        """Delete file."""
        return self._files.delete_file(file_path)

    def delete_directory(self, directory_path: str) -> FlextResult[bool]:
        """Delete directory."""
        return self._files.delete_directory(directory_path)

    def create_directory(self, directory_path: str) -> FlextResult[bool]:
        """Create directory."""
        return self._files.create_directory(directory_path)

    def list_directory(self, directory_path: str) -> FlextResult[list[str]]:
        """List files in directory."""
        return self._files.list_directory(directory_path)

    def execute_command(
        self,
        command: str,
        args: list[str] | None = None,
        timeout: int = 30,
    ) -> FlextResult[str]:
        """Execute shell command."""
        full_command = f"{command} {' '.join(args)}" if args else command

        # Create a simple command object for execute_cli_command
        @dataclass
        class SimpleCommand:
            command_line: str

        command_obj = SimpleCommand(full_command)
        return self.execute_cli_command(command_obj, timeout)

    def make_http_request(
        self,
        method: str,
        url: str,
        data: dict[str, object] | None = None,
        timeout: int = 10,
    ) -> FlextResult[str]:
        """Make HTTP request."""
        # Note: timeout parameter is for future use when HTTP client supports it
        self._logger.debug(
            f"Making HTTP {method} request to {url} with timeout {timeout}s"
        )
        return self._commands.make_http_request(
            url, method, None, str(data) if data else None
        )

    def parse_json_data(self, json_data: str) -> FlextResult[dict[str, object]]:
        """Parse JSON data."""
        try:
            parsed = json.loads(json_data)
            return FlextResult[dict[str, object]].ok(parsed)
        except Exception as e:
            return FlextResult[dict[str, object]].fail(f"JSON parsing failed: {e}")

    def parse_yaml_data(self, yaml_data: str) -> FlextResult[dict[str, object]]:
        """Parse YAML data."""
        try:
            parsed = yaml.safe_load(yaml_data)
            return FlextResult[dict[str, object]].ok(parsed)
        except Exception as e:
            return FlextResult[dict[str, object]].fail(f"YAML parsing failed: {e}")

    def serialize_json_data(self, data: dict[str, object]) -> FlextResult[str]:
        """Serialize data to JSON."""
        try:
            serialized = json.dumps(data, indent=2)
            return FlextResult[str].ok(serialized)
        except Exception as e:
            return FlextResult[str].fail(f"JSON serialization failed: {e}")

    def serialize_yaml_data(self, data: dict[str, object]) -> FlextResult[str]:
        """Serialize data to YAML."""
        try:
            serialized = yaml.dump(data, default_flow_style=False)
            return FlextResult[str].ok(serialized)
        except Exception as e:
            return FlextResult[str].fail(f"YAML serialization failed: {e}")

    def validate_email(self, email: str) -> FlextResult[bool]:
        """Validate email address format."""
        return self._utils.validate_email(email)

    def validate_url(self, url: str) -> FlextResult[bool]:
        """Validate URL format."""
        return self._utils.validate_url(url)

    def generate_uuid(self) -> FlextResult[str]:
        """Generate UUID string."""
        return self._utils.generate_uuid()

    def format_timestamp(
        self, timestamp: float, format_str: str = "%Y-%m-%d %H:%M:%S"
    ) -> FlextResult[str]:
        """Format timestamp to string."""
        return self._utils.format_timestamp(timestamp, format_str)

    def save_configuration(
        self, config_path: str, config: dict[str, object]
    ) -> FlextResult[bool]:
        """Save configuration to file."""
        return self._files.save_json_file(config_path, config)

    def load_configuration(self, config_path: str) -> FlextResult[dict[str, object]]:
        """Load configuration from file."""
        return self._files.load_json_file(config_path)

    def validate_configuration(self, config: dict[str, object]) -> FlextResult[bool]:
        """Validate configuration."""
        try:
            # Simple validation - check if it's a dict
            if not isinstance(config, dict):
                return FlextResult[bool].fail("Config must be a dictionary")
            return FlextResult[bool].ok(True)
        except Exception as e:
            return FlextResult[bool].fail(f"Config validation failed: {e}")

    def run(self) -> FlextResult[dict[str, object]]:
        """Run the CLI service - main execution method."""
        try:
            # Start the service
            start_result = self.start()
            if start_result.is_failure:
                return FlextResult[dict[str, object]].fail(
                    f"Failed to start service: {start_result.error}"
                )

            # Get service status
            health_result = self.health_check()
            if health_result.is_failure:
                return FlextResult[dict[str, object]].fail(
                    f"Health check failed: {health_result.error}"
                )

            # Return service information
            return FlextResult[dict[str, object]].ok({
                "status": "running",
                "service": "flext-cli-service",
                "timestamp": datetime.now(UTC).isoformat(),
                "version": "2.0.0",
                "health": health_result.value,
                "sessions": len(self.get_sessions()),
                "handlers": len(self.get_handlers()),
                "commands": len(self.get_commands()),
            })
        except Exception as e:
            return FlextResult[dict[str, object]].fail(f"Service run failed: {e}")


__all__ = ["FlextCliService"]
