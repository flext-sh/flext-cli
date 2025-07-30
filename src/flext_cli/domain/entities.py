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

    name: str = Field(..., description="Command name")
    command_line: str = Field(..., description="Command line string")
    command_type: CommandType = Field(..., description="Type of command")
    command_status: CommandStatus = Field(default=CommandStatus.PENDING, description="Command status")
    exit_code: int | None = Field(default=None, description="Exit code")
    stdout: str | None = Field(default=None, description="Standard output")
    stderr: str | None = Field(default=None, description="Standard error")
    started_at: datetime | None = Field(default=None, description="Start time")
    finished_at: datetime | None = Field(default=None, description="Finish time")

    def start_execution(self) -> None:
        """Start command execution."""
        if self.command_status != CommandStatus.PENDING:
            msg = f"Cannot start command that is in {self.command_status} status"
            raise ValueError(msg)
        
        object.__setattr__(self, 'command_status', CommandStatus.RUNNING)
        object.__setattr__(self, 'started_at', datetime.now(UTC))

    def complete_execution(
        self, 
        exit_code: int, 
        stdout: str | None = None, 
        stderr: str | None = None
    ) -> None:
        """Complete command execution."""
        if self.command_status != CommandStatus.RUNNING:
            msg = "Cannot complete command that hasn't been started"
            raise ValueError(msg)
        
        object.__setattr__(self, 'exit_code', exit_code)
        object.__setattr__(self, 'stdout', stdout)
        object.__setattr__(self, 'stderr', stderr)
        object.__setattr__(self, 'finished_at', datetime.now(UTC))
        
        if exit_code == 0:
            object.__setattr__(self, 'command_status', CommandStatus.COMPLETED)
        else:
            object.__setattr__(self, 'command_status', CommandStatus.FAILED)

    @property
    def is_successful(self) -> bool:
        """Check if command was successful."""
        return self.command_status == CommandStatus.COMPLETED and self.exit_code == 0

    def validate_domain_rules(self) -> FlextResult[None]:
        """Validate domain business rules for CLI commands."""
        if not self.name or not self.name.strip():
            return FlextResult.failure("Command name cannot be empty")
        
        if not self.command_line or not self.command_line.strip():
            return FlextResult.failure("Command line cannot be empty")
        
        return FlextResult.ok(None)


class CLISession(FlextEntity):
    """CLI session entity for tracking command execution sessions."""

    session_id: str = Field(..., description="Session identifier")
    session_status: SessionStatus = Field(default=SessionStatus.ACTIVE, description="Session status")
    command_history: list[TEntityId] = Field(default_factory=list, description="Command history")
    started_at: datetime = Field(default_factory=lambda: datetime.now(UTC), description="Session start time")
    ended_at: datetime | None = Field(default=None, description="Session end time")

    def add_command(self, command_id: TEntityId) -> None:
        """Add command to session history."""
        self.command_history.append(command_id)

    def end_session(self) -> None:
        """End the CLI session."""
        object.__setattr__(self, 'session_status', SessionStatus.COMPLETED)
        object.__setattr__(self, 'ended_at', datetime.now(UTC))

    def validate_domain_rules(self) -> FlextResult[None]:
        """Validate domain business rules for CLI sessions."""
        if not self.session_id or not self.session_id.strip():
            return FlextResult.failure("Session ID cannot be empty")
        
        return FlextResult.ok(None)


class CLIPlugin(FlextEntity):
    """CLI plugin entity for managing plugin lifecycle."""

    name: str = Field(..., description="Plugin name")
    entry_point: str = Field(..., description="Plugin entry point")
    commands: list[str] = Field(default_factory=list, description="Plugin commands")
    dependencies: list[str] = Field(default_factory=list, description="Plugin dependencies")
    plugin_status: PluginStatus = Field(default=PluginStatus.INACTIVE, description="Plugin status")

    def activate(self) -> None:
        """Activate the plugin."""
        object.__setattr__(self, 'plugin_status', PluginStatus.ACTIVE)

    def deactivate(self) -> None:
        """Deactivate the plugin."""
        object.__setattr__(self, 'plugin_status', PluginStatus.INACTIVE)

    def validate_domain_rules(self) -> FlextResult[None]:
        """Validate domain business rules for CLI plugins."""
        if not self.name or not self.name.strip():
            return FlextResult.failure("Plugin name cannot be empty")
        
        if not self.entry_point or not self.entry_point.strip():
            return FlextResult.failure("Entry point cannot be empty")
        
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
            return FlextResult.failure("Invalid output format")
        
        return FlextResult.ok(None)


# DRY: CommandStatus and CommandType already defined above - removing duplicates


class CLICommand(FlextEntity):
    """CLI command domain entity with execution lifecycle management."""

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
    )
    description: str | None = Field(
        None,
        max_length=CLIConstants.MAX_ERROR_MESSAGE_LENGTH,
    )
    command_type: CommandType = Field(default=CommandType.SYSTEM)

    # Command structure
    command_line: str = Field(..., min_length=1)
    arguments: dict[str, object] = Field(default_factory=dict)
    options: dict[str, object] = Field(default_factory=dict)

    # Execution details - inherits from StatusMixin in EntityMixin
    command_status: CommandStatus = Field(default=CommandStatus.PENDING)
    exit_code: int | None = None

    # Timing - inherits from TimestampMixin in EntityMixin
    started_at: datetime | None = None
    completed_at: datetime | None = None
    duration_seconds: float | None = None
    timeout: int | None = Field(default=CLIConstants.DEFAULT_TIMEOUT)

    # Output
    stdout: str | None = None
    stderr: str | None = None

    # Context - inherits from MetadataMixin in EntityMixin
    user_id: TUserId | None = None
    session_id: str | None = None
    working_directory: str | None = None
    environment: dict[str, str] = Field(default_factory=dict)

    @property
    def is_completed(self) -> bool:
        """Check if command execution is completed.

        Returns:
            True if command is completed, failed, or cancelled.

        """
        return self.command_status in {
            CommandStatus.COMPLETED,
            CommandStatus.FAILED,
            CommandStatus.CANCELLED,
        }

    @property
    def is_successful(self) -> bool:
        """Check if command execution was successful.

        Returns:
            True if command completed successfully with exit code 0.

        """
        return self.command_status == CommandStatus.COMPLETED and self.exit_code == 0

    def start_execution(self) -> CLICommand:
        """Start command execution.

        Sets status to running and records start time.

        Returns:
            New command instance with updated status and start time.

        """
        # Create new instance with updates (immutable pattern)
        current_dict = self.model_dump()
        current_dict.update(
            {
                "command_status": CommandStatus.RUNNING,
                "started_at": datetime.now(UTC),
            },
        )
        return CLICommand.model_validate(current_dict)

    def complete_execution(
        self,
        exit_code: int,
        stdout: str | None = None,
        stderr: str | None = None,
    ) -> CLICommand:
        """Complete command execution.

        Args:
            exit_code: Command exit code.
            stdout: Standard output from command.
            stderr: Standard error from command.

        Returns:
            New command instance with execution completed.

        """
        completed_at = datetime.now(UTC)
        duration_seconds = None

        if self.started_at:
            duration = completed_at - self.started_at
            duration_seconds = duration.total_seconds()

        updates = {
            "command_status": (
                CommandStatus.COMPLETED if exit_code == 0 else CommandStatus.FAILED
            ),
            "exit_code": exit_code,
            "completed_at": completed_at,
            "stdout": stdout,
            "stderr": stderr,
            "duration_seconds": duration_seconds,
        }

        # Create new instance with updates (immutable pattern)
        current_dict = self.model_dump()
        current_dict.update(updates)
        return CLICommand.model_validate(current_dict)

    def cancel_execution(self) -> CLICommand:
        """Cancel command execution.

        Sets status to cancelled and records completion time.

        Returns:
            New command instance with cancelled status.

        """
        completed_at = datetime.now(UTC)
        duration_seconds = None

        if self.started_at:
            duration = completed_at - self.started_at
            duration_seconds = duration.total_seconds()

        updates = {
            "command_status": CommandStatus.CANCELLED,
            "completed_at": completed_at,
            "duration_seconds": duration_seconds,
        }

        # Create new instance with updates (immutable pattern)
        current_dict = self.model_dump()
        current_dict.update(updates)
        return CLICommand.model_validate(current_dict)

    def validate_domain_rules(self) -> FlextResult[None]:
        """Validate domain business rules for CLI commands.

        Returns:
            FlextResult indicating success or failure with validation errors.

        """
        # Command name cannot be empty
        if not self.name or not self.name.strip():
            return FlextResult.fail("Command name cannot be empty")

        # Command line cannot be empty
        if not self.command_line or not self.command_line.strip():
            return FlextResult.fail("Command line cannot be empty")

        # Duration must be positive when set
        if self.duration_seconds is not None and self.duration_seconds < 0:
            return FlextResult.fail("Duration cannot be negative")

        return FlextResult.ok(None)


class CLISession(FlextEntity):
    """CLI session domain entity with command tracking."""

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
    )
    user_id: TUserId | None = None

    # Session details - inherits from TimestampMixin in EntityMixin
    started_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    last_activity: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # Context - inherits from MetadataMixin in EntityMixin
    working_directory: str | None = None
    environment: dict[str, str] = Field(default_factory=dict)

    # Commands
    commands_executed: list[TEntityId] = Field(default_factory=list)
    current_command: TEntityId | None = None

    # Status - inherits from StatusMixin in EntityMixin
    active: bool = Field(default=True)
    session_status: SessionStatus = Field(default=SessionStatus.ACTIVE)

    @property
    def command_history(self) -> list[TEntityId]:
        """Get command history (alias for commands_executed for backward compatibility).
        
        Returns:
            List of executed command IDs.
        """
        return self.commands_executed

    def add_command(self, command_id: TEntityId) -> CLISession:
        """Add a command to the session.

        Args:
            command_id: ID of the command to add.

        Returns:
            New session instance with command added.

        """
        # Create new list with the command added
        new_commands = list(self.commands_executed)
        new_commands.append(command_id)

        updates = {
            "commands_executed": new_commands,
            "current_command": command_id,
            "last_activity": datetime.now(UTC),
            "session_status": SessionStatus.ACTIVE,
        }

        # Create new instance with updates (immutable pattern)
        current_dict = self.model_dump()
        current_dict.update(updates)
        return CLISession.model_validate(current_dict)

    def end_session(self) -> CLISession:
        """End the CLI session.

        Sets session as inactive and clears current command.

        Returns:
            New session instance with session ended.

        """
        updates = {
            "active": False,
            "current_command": None,
            "last_activity": datetime.now(UTC),
            "session_status": SessionStatus.COMPLETED,
        }

        # Create new instance with updates (immutable pattern)
        current_dict = self.model_dump()
        current_dict.update(updates)
        return CLISession.model_validate(current_dict)

    def validate_domain_rules(self) -> FlextResult[None]:
        """Validate domain business rules for CLI sessions.

        Returns:
            FlextResult indicating success or failure with validation errors.

        """
        # Session ID cannot be empty
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
    """CLI plugin domain entity with lifecycle management."""

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
    )
    plugin_version: str = Field(
        default="0.8.0",
        description="Plugin version string",
    )
    description: str | None = Field(
        None,
        max_length=CLIConstants.MAX_ERROR_MESSAGE_LENGTH,
    )

    # Plugin details
    entry_point: str = Field(..., min_length=1)
    commands: list[str] = Field(default_factory=list)

    # Status - inherits from StatusMixin in EntityMixin
    enabled: bool = Field(default=True)
    installed: bool = Field(default=False)
    plugin_status: PluginStatus = Field(default=PluginStatus.INACTIVE)

    # Dependencies
    dependencies: list[str] = Field(default_factory=list)

    # Metadata - inherits from MetadataMixin in EntityMixin
    author: str | None = None
    license: str | None = None
    repository_url: str | None = None

    def enable(self) -> CLIPlugin:
        """Enable the plugin.

        Returns:
            New plugin instance with enabled status.

        """
        current_dict = self.model_dump()
        current_dict["enabled"] = True
        current_dict["plugin_status"] = PluginStatus.ACTIVE
        return CLIPlugin.model_validate(current_dict)

    def activate(self) -> CLIPlugin:
        """Activate the plugin (alias for enable for backward compatibility).

        Returns:
            New plugin instance with activated status.

        """
        return self.enable()

    def disable(self) -> CLIPlugin:
        """Disable the plugin.

        Returns:
            New plugin instance with disabled status.

        """
        current_dict = self.model_dump()
        current_dict["enabled"] = False
        current_dict["plugin_status"] = PluginStatus.INACTIVE
        return CLIPlugin.model_validate(current_dict)

    def deactivate(self) -> CLIPlugin:
        """Deactivate the plugin (alias for disable for backward compatibility).

        Returns:
            New plugin instance with deactivated status.

        """
        return self.disable()

    def install(self) -> CLIPlugin:
        """Install the plugin.

        Returns:
            New plugin instance with installed status.

        """
        current_dict = self.model_dump()
        current_dict["installed"] = True
        current_dict["plugin_status"] = PluginStatus.ACTIVE
        return CLIPlugin.model_validate(current_dict)

    def uninstall(self) -> CLIPlugin:
        """Uninstall the plugin and disable it.

        Returns:
            New plugin instance with uninstalled and disabled status.

        """
        updates = {
            "installed": False, 
            "enabled": False,
            "plugin_status": PluginStatus.INACTIVE
        }
        current_dict = self.model_dump()
        current_dict.update(updates)
        return CLIPlugin.model_validate(current_dict)

    def validate_domain_rules(self) -> FlextResult[None]:
        """Validate domain business rules for CLI plugins.

        Returns:
            FlextResult indicating success or failure with validation errors.

        """
        # Plugin name cannot be empty
        if not self.name or not self.name.strip():
            return FlextResult.fail("Plugin name cannot be empty")

        # Entry point cannot be empty
        if not self.entry_point or not self.entry_point.strip():
            return FlextResult.fail("Plugin entry point cannot be empty")

        # Plugin version must be valid format (basic check)
        if not self.plugin_version or not self.plugin_version.strip():
            return FlextResult.fail("Plugin version cannot be empty")

        return FlextResult.ok(None)


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
