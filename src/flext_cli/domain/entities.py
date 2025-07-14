"""Domain entities for FLEXT-CLI.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

Uses flext-core mixins, types, StrEnum, and constants.
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING
from typing import Any

from pydantic import Field

from flext_core.domain.pydantic_base import DomainEntity
from flext_core.domain.pydantic_base import DomainEvent

if TYPE_CHECKING:
    from flext_core.domain.types import EntityId
    from flext_core.domain.types import UserId


# Simple constants for compatibility
class FlextConstants:
    """Constants for FLEXT CLI domain."""

    MAX_ENTITY_NAME_LENGTH = 255
    MAX_ERROR_MESSAGE_LENGTH = 1000
    DEFAULT_TIMEOUT = 30
    FRAMEWORK_VERSION = "0.7.0"


# Simple version type
Version = str

# Types are now imported directly above


class CommandStatus(StrEnum):
    """Command execution status using StrEnum for type safety."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class CommandType(StrEnum):
    """Command types using StrEnum for type safety."""

    SYSTEM = "system"
    PIPELINE = "pipeline"
    PLUGIN = "plugin"
    DATA = "data"
    CONFIG = "config"
    AUTH = "auth"
    MONITORING = "monitoring"


class CLICommand(DomainEntity):
    """CLI command domain entity using flext-core foundation."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=FlextConstants.MAX_ENTITY_NAME_LENGTH,
    )
    description: str | None = Field(
        None,
        max_length=FlextConstants.MAX_ERROR_MESSAGE_LENGTH,
    )
    command_type: CommandType = Field(default=CommandType.SYSTEM)

    # Command structure
    command_line: str = Field(..., min_length=1)
    arguments: dict[str, Any] = Field(default_factory=dict)
    options: dict[str, Any] = Field(default_factory=dict)

    # Execution details - inherits from StatusMixin in EntityMixin
    command_status: CommandStatus = Field(default=CommandStatus.PENDING)
    exit_code: int | None = None

    # Timing - inherits from TimestampMixin in EntityMixin
    started_at: datetime | None = None
    completed_at: datetime | None = None
    duration_seconds: float | None = None

    # Output
    stdout: str | None = None
    stderr: str | None = None

    # Context - inherits from MetadataMixin in EntityMixin
    user_id: UserId | None = None
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

    def start_execution(self) -> None:
        """Start command execution.

        Sets status to running and records start time.
        """
        self.command_status = CommandStatus.RUNNING
        self.started_at = datetime.now()

    def complete_execution(
        self,
        exit_code: int,
        stdout: str | None = None,
        stderr: str | None = None,
    ) -> None:
        """Complete command execution.

        Args:
            exit_code: Command exit code.
            stdout: Standard output from command.
            stderr: Standard error from command.

        """
        self.command_status = (
            CommandStatus.COMPLETED if exit_code == 0 else CommandStatus.FAILED
        )
        self.exit_code = exit_code
        self.completed_at = datetime.now()
        self.stdout = stdout
        self.stderr = stderr

        if self.started_at:
            duration = self.completed_at - self.started_at
            self.duration_seconds = duration.total_seconds()

    def cancel_execution(self) -> None:
        """Cancel command execution.

        Sets status to cancelled and records completion time.
        """
        self.command_status = CommandStatus.CANCELLED
        self.completed_at = datetime.now()

        if self.started_at:
            duration = self.completed_at - self.started_at
            self.duration_seconds = duration.total_seconds()


class CLIConfig(DomainEntity):
    """CLI configuration domain entity using flext-core foundation."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=FlextConstants.MAX_ENTITY_NAME_LENGTH,
    )
    description: str | None = Field(
        None,
        max_length=FlextConstants.MAX_ERROR_MESSAGE_LENGTH,
    )

    # Configuration data - inherits from MetadataMixin in EntityMixin
    config_data: dict[str, Any] = Field(default_factory=dict)

    # Metadata
    config_type: str = Field(
        ...,
        min_length=1,
        max_length=FlextConstants.MAX_ENTITY_NAME_LENGTH,
    )
    version: Version = Field(
        FlextConstants.FRAMEWORK_VERSION,
        description="Configuration version",
    )

    # Validation - inherits from StatusMixin in EntityMixin
    is_valid: bool = Field(default=True)
    validation_errors: list[str] = Field(default_factory=list)

    # Context
    user_id: UserId | None = None
    is_global: bool = Field(default=False)

    def validate_config(self) -> None:
        """Validate configuration data.

        Checks configuration data and updates validation errors.
        """
        self.validation_errors = []

        # Basic validation
        if not self.config_data:
            self.validation_errors.append("Configuration data is empty")

        # Set validation status
        self.is_valid = len(self.validation_errors) == 0


class CLISession(DomainEntity):
    """CLI session domain entity using flext-core foundation."""

    session_id: str = Field(
        ...,
        min_length=1,
        max_length=FlextConstants.MAX_ENTITY_NAME_LENGTH,
    )
    user_id: UserId | None = None

    # Session details - inherits from TimestampMixin in EntityMixin
    started_at: datetime = Field(default_factory=datetime.now)
    last_activity: datetime = Field(default_factory=datetime.now)

    # Context - inherits from MetadataMixin in EntityMixin
    working_directory: str | None = None
    environment: dict[str, str] = Field(default_factory=dict)

    # Commands
    commands_executed: list[EntityId] = Field(default_factory=list)
    current_command: EntityId | None = None

    # Status - inherits from StatusMixin in EntityMixin
    active: bool = Field(default=True)

    def add_command(self, command_id: EntityId) -> None:
        """Add a command to the session.

        Args:
            command_id: ID of the command to add.

        """
        self.commands_executed.append(command_id)
        self.current_command = command_id
        self.last_activity = datetime.now()

    def end_session(self) -> None:
        """End the CLI session.

        Sets session as inactive and clears current command.
        """
        self.active = False
        self.current_command = None
        self.last_activity = datetime.now()


class CLIPlugin(DomainEntity):
    """CLI plugin domain entity using flext-core foundation."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=FlextConstants.MAX_ENTITY_NAME_LENGTH,
    )
    version: Version = Field(
        FlextConstants.FRAMEWORK_VERSION,
        description="Plugin version",
    )
    description: str | None = Field(
        None,
        max_length=FlextConstants.MAX_ERROR_MESSAGE_LENGTH,
    )

    # Plugin details
    entry_point: str = Field(..., min_length=1)
    commands: list[str] = Field(default_factory=list)

    # Status - inherits from StatusMixin in EntityMixin
    enabled: bool = Field(default=True)
    installed: bool = Field(default=False)

    # Dependencies
    dependencies: list[str] = Field(default_factory=list)

    # Metadata - inherits from MetadataMixin in EntityMixin
    author: str | None = None
    license: str | None = None
    repository_url: str | None = None

    def enable(self) -> None:
        """Enable the plugin."""
        self.enabled = True

    def disable(self) -> None:
        """Disable the plugin."""
        self.enabled = False

    def install(self) -> None:
        """Install the plugin."""
        self.installed = True

    def uninstall(self) -> None:
        """Uninstall the plugin and disable it."""
        self.installed = False
        self.enabled = False


# Domain Events - Using typed IDs for consistency
class CommandStartedEvent(DomainEvent):
    """Event raised when command starts execution."""

    command_id: EntityId = Field(..., description="Command ID")
    command_name: str | None = Field(None, description="Command name")
    session_id: str | None = Field(None, description="Session ID")


class CommandCompletedEvent(DomainEvent):
    """Event raised when command completes."""

    command_id: EntityId = Field(..., description="Command ID")
    command_name: str | None = Field(None, description="Command name")
    success: bool = Field(..., description="Success status")


class CommandCancelledEvent(DomainEvent):
    """Event raised when command is cancelled."""

    command_id: EntityId = Field(..., description="Command ID")
    command_name: str | None = Field(None, description="Command name")


class ConfigUpdatedEvent(DomainEvent):
    """Event raised when configuration is updated."""

    config_id: EntityId = Field(..., description="Configuration ID")
    config_name: str | None = Field(None, description="Configuration name")


class SessionStartedEvent(DomainEvent):
    """Event raised when CLI session starts."""

    session_id: EntityId = Field(..., description="Session ID")
    user_id: UserId | None = Field(None, description="User ID")
    working_directory: str | None = Field(None, description="Working directory")


class SessionEndedEvent(DomainEvent):
    """Event raised when CLI session ends."""

    session_id: EntityId = Field(..., description="Session ID")
    user_id: UserId | None = Field(None, description="User ID")
    commands_executed: int = Field(..., description="Number of commands executed")
    duration_seconds: float | None = Field(None, description="Session duration")


class PluginInstalledEvent(DomainEvent):
    """Event raised when plugin is installed."""

    plugin_id: EntityId = Field(..., description="Plugin ID")
    plugin_name: str | None = Field(None, description="Plugin name")


class PluginUninstalledEvent(DomainEvent):
    """Event raised when plugin is uninstalled."""

    plugin_id: EntityId = Field(..., description="Plugin ID")
    plugin_name: str | None = Field(None, description="Plugin name")
