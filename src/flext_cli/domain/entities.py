"""Domain entities for FLEXT-CLI.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

Domain entities using flext-core foundation patterns.
"""

from __future__ import annotations

import contextlib
from datetime import UTC, datetime
from enum import StrEnum

# DRY: Use REAL flext-core imports from main API - NO DUPLICATION
from flext_core import FlextEntity, FlextResult, FlextValueObject, TEntityId
from pydantic import Field

# DRY: Use real type alias - NO DUPLICATION
TUserId = TEntityId


class PluginStatus(StrEnum):
    """Plugin status enumeration using StrEnum for type safety."""

    INACTIVE = "inactive"
    ACTIVE = "active"
    ERROR = "error"
    LOADING = "loading"
    DISABLED = "disabled"


class SessionStatus(StrEnum):
    """Session status enumeration using StrEnum for type safety."""

    ACTIVE = "active"
    COMPLETED = "completed"
    ENDED = "ended"
    INACTIVE = "inactive"


class CommandStatus(StrEnum):
    """Command status enumeration using StrEnum for type safety."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class CommandType(StrEnum):
    """Command type enumeration using StrEnum for type safety."""

    CLI = "cli"
    SYSTEM = "system"
    SCRIPT = "script"
    SQL = "sql"
    # Additional command types consolidated from duplicated definition (DRY principle)
    PIPELINE = "pipeline"
    PLUGIN = "plugin"
    DATA = "data"
    CONFIG = "config"
    AUTH = "auth"
    MONITORING = "monitoring"


# Constants for domain entities
class CLIConstants:
    """Constants for FLEXT CLI domain."""

    MAX_ENTITY_NAME_LENGTH = 255
    MAX_ERROR_MESSAGE_LENGTH = 1000
    DEFAULT_TIMEOUT = 30


class CLICommand(FlextEntity):
    """CLI command entity with execution tracking."""

    # Entity ID is inherited from FlextEntity but we need to provide a default factory
    id: str = Field(
        default_factory=lambda: (
            f"cmd_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S_%f')[:23]}"
        ),
    )

    name: str = Field(
        ...,
        min_length=1,
        max_length=CLIConstants.MAX_ENTITY_NAME_LENGTH,
        description="Command name",
    )
    description: str | None = Field(
        None,
        max_length=CLIConstants.MAX_ERROR_MESSAGE_LENGTH,
        description="Command description",
    )
    command_line: str = Field(..., min_length=1, description="Command line string")
    command_type: CommandType = Field(
        default=CommandType.SYSTEM, description="Type of command",
    )
    command_status: CommandStatus = Field(
        default=CommandStatus.PENDING, description="Command status",
    )
    exit_code: int | None = Field(default=None, description="Exit code")
    stdout: str | None = Field(default=None, description="Standard output")
    stderr: str | None = Field(default=None, description="Standard error")
    started_at: datetime | None = Field(default=None, description="Start time")
    finished_at: datetime | None = Field(default=None, description="Finish time")
    duration_seconds: float | None = Field(
        default=None, description="Execution duration",
    )
    timeout: int | None = Field(
        default=CLIConstants.DEFAULT_TIMEOUT, description="Timeout in seconds",
    )

    # Context
    user_id: TUserId | None = Field(default=None, description="User ID")
    session_id: str | None = Field(default=None, description="Session ID")
    working_directory: str | None = Field(
        default=None, description="Working directory",
    )
    environment: dict[str, str] = Field(
        default_factory=dict, description="Environment variables",
    )
    arguments: dict[str, object] = Field(
        default_factory=dict, description="Command arguments",
    )
    options: dict[str, object] = Field(
        default_factory=dict, description="Command options",
    )

    @property
    def is_completed(self) -> bool:
        """Check if command execution is completed."""
        return self.command_status in {
            CommandStatus.COMPLETED,
            CommandStatus.FAILED,
            CommandStatus.CANCELLED,
        }

    @property
    def is_successful(self) -> bool:
        """Check if command was successful."""
        return self.command_status == CommandStatus.COMPLETED and self.exit_code == 0

    def start_execution(self) -> CLICommand:
        """Start command execution.

        Returns:
            New command instance with updated status.

        """
        if self.command_status != CommandStatus.PENDING:
            msg = f"Cannot start command that is in {self.command_status} status"
            raise ValueError(msg)

        # Create new instance with updated fields (immutable pattern)
        return self.model_copy(update={
            "command_status": CommandStatus.RUNNING,
            "started_at": datetime.now(UTC),
        })

    def complete_execution(
        self,
        exit_code: int,
        stdout: str | None = None,
        stderr: str | None = None,
    ) -> CLICommand:
        """Complete command execution.

        Returns:
            New command instance with execution completed.

        """
        if self.command_status != CommandStatus.RUNNING:
            msg = "Cannot complete command that hasn't been started"
            raise ValueError(msg)

        finished_at = datetime.now(UTC)
        duration_seconds = None

        if self.started_at:
            duration = finished_at - self.started_at
            duration_seconds = duration.total_seconds()

        status = CommandStatus.COMPLETED if exit_code == 0 else CommandStatus.FAILED

        # Create new instance with updated fields (immutable pattern)
        return self.model_copy(update={
            "exit_code": exit_code,
            "stdout": stdout,
            "stderr": stderr,
            "finished_at": finished_at,
            "duration_seconds": duration_seconds,
            "command_status": status,
        })

    def cancel_execution(self) -> CLICommand:
        """Cancel command execution.

        Returns:
            New command instance with cancelled status.

        """
        finished_at = datetime.now(UTC)
        duration_seconds = None

        if self.started_at:
            duration = finished_at - self.started_at
            duration_seconds = duration.total_seconds()

        # Create new instance with updated fields (immutable pattern)
        return self.model_copy(update={
            "command_status": CommandStatus.CANCELLED,
            "finished_at": finished_at,
            "duration_seconds": duration_seconds,
        })

    def validate_domain_rules(self) -> FlextResult[None]:
        """Validate domain business rules for CLI commands."""
        if not self.name or not self.name.strip():
            return FlextResult.fail("Command name cannot be empty")

        if not self.command_line or not self.command_line.strip():
            return FlextResult.fail("Command line cannot be empty")

        if self.duration_seconds is not None and self.duration_seconds < 0:
            return FlextResult.fail("Duration cannot be negative")

        return FlextResult.ok(None)


class CLISession(FlextEntity):
    """CLI session entity for tracking command execution sessions."""

    # Entity ID is inherited from FlextEntity but we need to provide a default factory
    id: str = Field(
        default_factory=lambda: (
            f"session_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S_%f')[:26]}"
        ),
    )

    session_id: str = Field(
        ...,
        min_length=1,
        max_length=CLIConstants.MAX_ENTITY_NAME_LENGTH,
        description="Session identifier",
    )
    user_id: TUserId | None = Field(default=None, description="User ID")
    session_status: SessionStatus = Field(
        default=SessionStatus.ACTIVE, description="Session status",
    )
    command_history: list[TEntityId] = Field(
        default_factory=list, description="Command history",
    )
    commands_executed: list[TEntityId] = Field(
        default_factory=list, description="Executed commands",
    )
    current_command: TEntityId | None = Field(
        default=None, description="Current command",
    )
    started_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Session start time",
    )
    last_activity: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Last activity",
    )
    ended_at: datetime | None = Field(default=None, description="Session end time")
    active: bool = Field(default=True, description="Session active status")

    # Context
    working_directory: str | None = Field(default=None, description="Working directory")
    environment: dict[str, str] = Field(
        default_factory=dict, description="Environment variables",
    )

    def add_command(self, command_id: TEntityId) -> CLISession:
        """Add command to session history.

        Returns:
            New session instance with command added.

        """
        # Create new lists with the command added
        new_history = [*self.command_history, command_id]
        new_executed = [*self.commands_executed, command_id]

        # Create new instance with updated fields (immutable pattern)
        return self.model_copy(update={
            "command_history": new_history,
            "commands_executed": new_executed,
            "current_command": command_id,
            "last_activity": datetime.now(UTC),
        })

    def end_session(self) -> CLISession:
        """End the CLI session.

        Returns:
            New session instance with session ended.

        """
        # Create new instance with updated fields (immutable pattern)
        return self.model_copy(update={
            "session_status": SessionStatus.COMPLETED,
            "ended_at": datetime.now(UTC),
            "active": False,
            "current_command": None,
        })

    def validate_domain_rules(self) -> FlextResult[None]:
        """Validate domain business rules for CLI sessions."""
        if not self.session_id or not self.session_id.strip():
            return FlextResult.fail("Session ID cannot be empty")

        # Last activity cannot be before started_at
        if self.last_activity < self.started_at:
            return FlextResult.fail("Last activity cannot be before session start")

        # Current command must be in commands_executed if set
        if (
            self.current_command is not None
            and self.current_command not in self.commands_executed
        ):
            return FlextResult.fail("Current command must be in executed commands list")

        return FlextResult.ok(None)


class CLIPlugin(FlextEntity):
    """CLI plugin entity for managing plugin lifecycle."""

    # Entity ID is inherited from FlextEntity but we need to provide a default factory
    id: str = Field(
        default_factory=lambda: (
            f"plugin_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S_%f')[:27]}"
        ),
    )

    name: str = Field(
        ...,
        min_length=1,
        max_length=CLIConstants.MAX_ENTITY_NAME_LENGTH,
        description="Plugin name",
    )
    plugin_version: str = Field(
        default="0.8.0",
        description="Plugin version string",
    )
    description: str | None = Field(
        None,
        max_length=CLIConstants.MAX_ERROR_MESSAGE_LENGTH,
        description="Plugin description",
    )
    entry_point: str = Field(..., min_length=1, description="Plugin entry point")
    commands: list[str] = Field(default_factory=list, description="Plugin commands")
    dependencies: list[str] = Field(
        default_factory=list, description="Plugin dependencies",
    )
    plugin_status: PluginStatus = Field(
        default=PluginStatus.INACTIVE, description="Plugin status",
    )

    # Status
    enabled: bool = Field(default=True, description="Plugin enabled status")
    installed: bool = Field(default=False, description="Plugin installed status")

    # Metadata
    author: str | None = Field(default=None, description="Plugin author")
    license: str | None = Field(default=None, description="Plugin license")
    repository_url: str | None = Field(default=None, description="Repository URL")

    def activate(self) -> CLIPlugin:
        """Activate the plugin.

        Returns:
            New plugin instance with activated status.

        """
        return self.model_copy(update={
            "plugin_status": PluginStatus.ACTIVE,
            "enabled": True,
        })

    def deactivate(self) -> CLIPlugin:
        """Deactivate the plugin.

        Returns:
            New plugin instance with deactivated status.

        """
        return self.model_copy(update={
            "plugin_status": PluginStatus.INACTIVE,
            "enabled": False,
        })

    def enable(self) -> CLIPlugin:
        """Enable the plugin (alias for activate).

        Returns:
            New plugin instance with enabled status.

        """
        return self.activate()

    def disable(self) -> CLIPlugin:
        """Disable the plugin (alias for deactivate).

        Returns:
            New plugin instance with disabled status.

        """
        return self.deactivate()

    def install(self) -> CLIPlugin:
        """Install the plugin.

        Returns:
            New plugin instance with installed status.

        """
        return self.model_copy(update={
            "installed": True,
            "plugin_status": PluginStatus.ACTIVE,
        })

    def uninstall(self) -> CLIPlugin:
        """Uninstall the plugin and disable it.

        Returns:
            New plugin instance with uninstalled status.

        """
        return self.model_copy(update={
            "installed": False,
            "enabled": False,
            "plugin_status": PluginStatus.INACTIVE,
        })

    def validate_domain_rules(self) -> FlextResult[None]:
        """Validate domain business rules for CLI plugins."""
        if not self.name or not self.name.strip():
            return FlextResult.fail("Plugin name cannot be empty")

        if not self.entry_point or not self.entry_point.strip():
            return FlextResult.fail("Plugin entry point cannot be empty")

        # Plugin version must be valid format (basic check)
        if not self.plugin_version or not self.plugin_version.strip():
            return FlextResult.fail("Plugin version cannot be empty")

        return FlextResult.ok(None)


class CLIConfig(FlextValueObject):
    """CLI configuration value object."""

    profile: str = Field(default="default", description="Configuration profile")
    debug: bool = Field(default=False, description="Debug mode")
    output_format: str = Field(default="table", description="Output format")

    def validate_domain_rules(self) -> FlextResult[None]:
        """Validate domain business rules for CLI configuration."""
        valid_formats = ["table", "json", "yaml", "csv", "plain"]
        if self.output_format not in valid_formats:
            return FlextResult.fail("Invalid output format")

        return FlextResult.ok(None)


# DRY: CommandStatus and CommandType already defined above - duplicates removed


# Domain Events for CLI operations using flext-core patterns


class CommandStartedEvent(FlextValueObject):
    """Event raised when command starts execution."""

    command_id: TEntityId = Field(..., description="Command ID")
    command_name: str | None = Field(None, description="Command name")
    session_id: str | None = Field(None, description="Session ID")


class CommandCompletedEvent(FlextValueObject):
    """Event raised when command completes."""

    command_id: TEntityId = Field(..., description="Command ID")
    command_name: str | None = Field(None, description="Command name")
    success: bool = Field(..., description="Success status")


class CommandCancelledEvent(FlextValueObject):
    """Event raised when command is cancelled."""

    command_id: TEntityId = Field(..., description="Command ID")
    command_name: str | None = Field(None, description="Command name")


class ConfigUpdatedEvent(FlextValueObject):
    """Event raised when configuration is updated."""

    config_id: TEntityId = Field(..., description="Configuration ID")
    config_name: str | None = Field(None, description="Configuration name")


class SessionStartedEvent(FlextValueObject):
    """Event raised when CLI session starts."""

    session_id: TEntityId = Field(..., description="Session ID")
    user_id: TUserId | None = Field(None, description="User ID")
    working_directory: str | None = Field(None, description="Working directory")


class SessionEndedEvent(FlextValueObject):
    """Event raised when CLI session ends."""

    session_id: TEntityId = Field(..., description="Session ID")
    user_id: TUserId | None = Field(None, description="User ID")
    commands_executed: int = Field(..., description="Number of commands executed")
    duration_seconds: float | None = Field(None, description="Session duration")


class PluginInstalledEvent(FlextValueObject):
    """Event raised when plugin is installed."""

    plugin_id: TEntityId = Field(..., description="Plugin ID")
    plugin_name: str | None = Field(None, description="Plugin name")


class PluginUninstalledEvent(FlextValueObject):
    """Event raised when plugin is uninstalled."""

    plugin_id: TEntityId = Field(..., description="Plugin ID")
    plugin_name: str | None = Field(None, description="Plugin name")


# Model rebuilding to resolve forward references
with contextlib.suppress(Exception):
    # Non-critical model rebuilding - skip if types not available
    # Ensure all types are available
    globals()["TUserId"] = TUserId
    globals()["TEntityId"] = TEntityId

    CLICommand.model_rebuild()
    CLISession.model_rebuild()
    CLIPlugin.model_rebuild()

    # Rebuild event classes too
    CommandStartedEvent.model_rebuild()
    CommandCompletedEvent.model_rebuild()
    CommandCancelledEvent.model_rebuild()
    ConfigUpdatedEvent.model_rebuild()
    SessionStartedEvent.model_rebuild()
    SessionEndedEvent.model_rebuild()
    PluginInstalledEvent.model_rebuild()
    PluginUninstalledEvent.model_rebuild()
