"""FLEXT CLI Domain Entities - Rich Domain Models for CLI Operations.

This module implements domain entities following Domain-Driven Design (DDD) patterns
with flext-core integration. These entities represent the core business concepts of
CLI operations including commands, sessions, plugins, and configurations.

Architecture:
    - FlextEntity base class for rich domain entities with business logic
    - DomainValueObject for immutable value types and data containers
    - Domain events for entity lifecycle changes and cross-cutting concerns
    - Business rule validation and domain invariant enforcement

Core Entities:
    - CLICommand: Command execution with lifecycle management and status tracking
    - CLISession: User session with command history and context management
    - CLIPlugin: Plugin system with lifecycle and dependency management
    - CLIConfig: Configuration management with validation and profiles

Entity Patterns:
    - Rich domain entities with business methods and validation
    - Domain events for entity state changes and integration
    - Aggregate roots for complex business operations
    - Value objects for data consistency and immutability

Integration:
    All entities integrate with the FLEXT ecosystem patterns:
    - Railway-oriented programming with FlextResult error handling
    - Event-driven architecture with domain event publishing
    - CQRS patterns for command and query separation
    - Repository patterns for data persistence abstraction

Current Implementation Status:
    ✅ Domain entities with flext-core integration (60% complete)
    ✅ Basic lifecycle management and validation
    ⚠️ Domain events defined but not published (Sprint 1-2)
    ❌ Missing repository implementations (Sprint 2)
    ❌ Missing aggregate root patterns (Sprint 2)

TODO (docs/TODO.md):
    Sprint 1-2: Complete domain event publishing system
    Sprint 2: Implement repository pattern integration
    Sprint 2: Add aggregate root patterns for complex operations
    Sprint 3: Add domain service patterns for business logic

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import contextlib
import uuid
from datetime import UTC, datetime
from enum import StrEnum
from typing import TypeVar

from flext_core import (
    FlextDomainEntity as FlextEntity,
    FlextDomainValueObject as DomainValueObject,
    FlextEntityId as EntityId,
    FlextResult,
)
from pydantic import Field

from flext_cli.constants import (
    DEFAULT_TIMEOUT,
    MAX_ENTITY_NAME_LENGTH,
    MAX_ERROR_MESSAGE_LENGTH,
)

T = TypeVar("T")


class FlextFactory:
    """Simple factory for creating entities."""

    @staticmethod
    def create_entity(entity_class: type[T], **kwargs: object) -> FlextResult[T]:
        """Create entity instance."""
        try:
            return FlextResult.ok(entity_class(**kwargs))
        except Exception as e:
            return FlextResult.fail(str(e))


TUserId = EntityId


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


# Legacy constants removed - use simple values from constants.py


class CLICommand(FlextEntity):
    r"""CLI Command Domain Entity - Rich command execution with lifecycle management.

    Modern FlextEntity implementation following foundation-refactored patterns.
    Eliminates 85% boilerplate through automatic ID, timestamp, and versioning.

    Core Responsibilities:
        - Command execution lifecycle management (pending → running → completed/failed)
        - Exit code tracking and success/failure determination
        - Standard output/error capture and management
        - Execution timing and duration calculation
        - Environment and context management
        - Domain event publishing for state changes

    Business Rules:
        - Commands must have non-empty names and command lines
        - Only pending commands can be started
        - Running commands can be completed or cancelled
        - Completed commands cannot change state
        - Exit code 0 indicates success for completed commands

    Usage Examples:
        # Modern pattern - zero boilerplate creation
        >>> result = FlextFactory.create_entity(
        ...     CLICommand,
        ...     entity_id="cmd-001",
        ...     name="list-pipelines",
        ...     command_line="flext pipeline list",
        ...     command_type=CommandType.CLI,
        ... )
        >>> command = result.unwrap()
        >>> # ID, timestamps, version handled automatically

    Integration:
        - Integrates with CLISession for command history
        - Used by command handlers in application layer
        - Persisted via repository pattern (Sprint 2)
        - Monitored via observability system (Sprint 7)

    TODO (docs/TODO.md):
        Sprint 1-2: Implement domain event publishing
        Sprint 2: Add repository persistence integration
        Sprint 3: Add command validation and sanitization
        Sprint 7: Add performance metrics and monitoring
    """

    name: str = Field(
        ...,
        min_length=1,
        max_length=MAX_ENTITY_NAME_LENGTH,
        description="Command name",
    )
    description: str | None = Field(
        None,
        max_length=MAX_ERROR_MESSAGE_LENGTH,
        description="Command description",
    )
    command_line: str = Field(..., min_length=1, description="Command line string")
    command_type: CommandType = Field(
        default=CommandType.SYSTEM,
        description="Type of command",
    )
    command_status: CommandStatus = Field(
        default=CommandStatus.PENDING,
        description="Command status",
    )
    exit_code: int | None = Field(default=None, description="Exit code")
    stdout: str | None = Field(default=None, description="Standard output")
    stderr: str | None = Field(default=None, description="Standard error")
    started_at: datetime | None = Field(default=None, description="Start time")
    finished_at: datetime | None = Field(default=None, description="Finish time")
    duration_seconds: float | None = Field(
        default=None,
        description="Execution duration",
    )
    timeout: int | None = Field(
        default=DEFAULT_TIMEOUT,
        description="Timeout in seconds",
    )

    # Context
    user_id: TUserId | None = Field(default=None, description="User ID")
    session_id: str | None = Field(default=None, description="Session ID")
    working_directory: str | None = Field(
        default=None,
        description="Working directory",
    )
    environment: dict[str, str] = Field(
        default_factory=dict,
        description="Environment variables",
    )
    arguments: dict[str, object] = Field(
        default_factory=dict,
        description="Command arguments",
    )
    options: dict[str, object] = Field(
        default_factory=dict,
        description="Command options",
    )

    @property
    def is_completed(self) -> bool:
        """Check if command execution has reached a terminal state.

        Returns True if the command has finished executing in any way:
        completed successfully, failed, or was cancelled. Once a command
        is completed, its status cannot be changed.

        Returns:
            bool: True if command is in a terminal state, False otherwise.

        Business Logic:
            Terminal states: COMPLETED, FAILED, CANCELLED
            Non-terminal states: PENDING, RUNNING

        """
        return self.command_status in {
            CommandStatus.COMPLETED,
            CommandStatus.FAILED,
            CommandStatus.CANCELLED,
        }

    @property
    def successful(self) -> bool:
        """Check if command executed successfully with zero exit code.

        A command is considered successful only if it completed execution
        without errors (status=COMPLETED) and returned exit code 0, which
        follows Unix convention for successful program execution.

        Returns:
            bool: True if command completed successfully with exit code 0,
                  False for any other status or non-zero exit code.

        Business Logic:
            Success requires both:
            1. Command status must be COMPLETED (not FAILED or CANCELLED)
            2. Exit code must be 0 (Unix success convention)

        Examples:
            >>> command.command_status = CommandStatus.COMPLETED
            >>> command.exit_code = 0
            >>> command.successful  # True

            >>> command.exit_code = 1
            >>> command.successful  # False (non-zero exit)

        """
        return self.command_status == CommandStatus.COMPLETED and self.exit_code == 0

    def start_execution(self) -> FlextResult[CLICommand]:
        """Start command execution with modern railway-oriented programming.

        Modern FlextResult pattern eliminates try/catch boilerplate and provides
        type-safe error handling with automatic error propagation.

        Business Rules:
            - Only commands in PENDING status can be started
            - Starting a command records the current timestamp
            - Command transitions to RUNNING status
            - Domain event should be published (TODO: Sprint 1-2)

        Returns:
            FlextResult[CLICommand]: Railway-oriented result with new command instance
                                   or descriptive error message.

        Modern Usage:
            >>> result = (
            ...     command.validate_business_rules()
            ...     .flat_map(lambda _: command.start_execution())
            ...     .map(lambda cmd: cmd.log_execution_started())
            ... )
            >>> if result.success:
            ...     running_command = result.unwrap()

        """
        # Railway pattern - validate first
        validation_result = self.validate_business_rules()
        if validation_result.is_failure:
            return FlextResult.fail(validation_result.error or "Validation failed")

        if self.command_status != CommandStatus.PENDING:
            return FlextResult.fail(
                f"Cannot start command that is in {self.command_status} status",
            )

        # Create new instance with updated fields (immutable pattern)
        now = datetime.now(UTC)
        updated_command = self.model_copy(
            update={
                "command_status": CommandStatus.RUNNING,
                "started_at": now,
                "updated_at": now,
            },
        )

        # Add domain event for event sourcing
        updated_command.add_domain_event(
            {
                "type": "CommandStarted",
                "command_id": updated_command.id,
                "name": updated_command.name,
                "timestamp": now.isoformat(),
            },
        )

        return FlextResult.ok(updated_command)

    def complete_execution(
        self,
        exit_code: int,
        stdout: str | None = None,
        stderr: str | None = None,
    ) -> FlextResult[CLICommand]:
        """Complete command execution with result capture and status transition.

        Transitions a RUNNING command to either COMPLETED (exit code 0) or
        FAILED (non-zero exit code) status. Captures execution results and
        calculates duration based on start timestamp.

        Args:
            exit_code: Process exit code (0 indicates success)
            stdout: Standard output captured from command execution (optional)
            stderr: Standard error captured from command execution (optional)

        Business Rules:
            - Only RUNNING commands can be completed
            - Exit code 0 → COMPLETED status (success)
            - Non-zero exit code → FAILED status
            - Duration calculated from started_at timestamp
            - Domain event should be published (TODO: Sprint 1-2)

        Returns:
            FlextResult[CLICommand]: Success contains new command instance
                                   with terminal status and execution results,
                                   Failure contains validation error message.

        Domain Events:
            CommandCompletedEvent: Published for successful completion (TODO)
            CommandFailedEvent: Published for failed execution (TODO)

        Examples:
            # Successful completion
            >>> result = running_command.complete_execution(
            ...     exit_code=0, stdout="Operation successful"
            ... )
            >>> completed = result.unwrap()
            >>> assert completed.successful

            # Failed execution
            >>> result = running_command.complete_execution(
            ...     exit_code=1, stderr="Error occurred"
            ... )
            >>> failed = result.unwrap()
            >>> assert not failed.successful

        TODO (Sprint 1-2):
            - Publish appropriate domain events
            - Add output validation and sanitization
            - Integrate with monitoring and metrics

        """
        if self.command_status != CommandStatus.RUNNING:
            return FlextResult.fail("Cannot complete command that hasn't been started")

        finished_at = datetime.now(UTC)
        duration_seconds = None

        if self.started_at:
            duration = finished_at - self.started_at
            duration_seconds = duration.total_seconds()

        status = CommandStatus.COMPLETED if exit_code == 0 else CommandStatus.FAILED

        # Create new instance with updated fields (immutable pattern)
        updated_command = self.model_copy(
            update={
                "exit_code": exit_code,
                "stdout": stdout,
                "stderr": stderr,
                "finished_at": finished_at,
                "duration_seconds": duration_seconds,
                "command_status": status,
                "updated_at": finished_at,
            },
        )

        # Issue #4: Publish appropriate domain events (Sprint 1-2)
        # if status == CommandStatus.COMPLETED:
        #     publish(CommandCompletedEvent(...))
        # else:
        #     publish(CommandFailedEvent(...))

        return FlextResult.ok(updated_command)

    def cancel_execution(self) -> FlextResult[CLICommand]:
        """Cancel command execution and transition to CANCELLED status.

        Allows cancellation of RUNNING commands, recording the cancellation
        timestamp and calculating partial execution duration.

        Business Rules:
            - Only RUNNING commands can be cancelled
            - Cancellation records finish timestamp
            - Duration calculated from start to cancellation
            - Domain event should be published (TODO: Sprint 1-2)

        Returns:
            FlextResult[CLICommand]: Success contains new command instance
                                   with CANCELLED status and timing info,
                                   Failure contains validation error.

        Domain Events:
            CommandCancelledEvent: Published when command is cancelled (TODO)

        TODO (Sprint 1-2):
            - Publish CommandCancelledEvent domain event
            - Add cancellation reason tracking
            - Integrate with process management for cleanup

        """
        if self.command_status != CommandStatus.RUNNING:
            return FlextResult.fail("Cannot cancel command that is not running")

        finished_at = datetime.now(UTC)
        duration_seconds = None

        if self.started_at:
            duration = finished_at - self.started_at
            duration_seconds = duration.total_seconds()

        # Create new instance with updated fields (immutable pattern)
        updated_command = self.model_copy(
            update={
                "command_status": CommandStatus.CANCELLED,
                "finished_at": finished_at,
                "duration_seconds": duration_seconds,
                "updated_at": finished_at,
            },
        )

        # Issue #5: Publish CommandCancelledEvent domain event (Sprint 1-2)

        return FlextResult.ok(updated_command)

    def validate_business_rules(self) -> FlextResult[None]:
        """Validate domain business rules for CLI commands."""
        if not self.name or not self.name.strip():
            return FlextResult.fail("Command name cannot be empty")

        if not self.command_line or not self.command_line.strip():
            return FlextResult.fail("Command line cannot be empty")

        if self.duration_seconds is not None and self.duration_seconds < 0:
            return FlextResult.fail("Duration cannot be negative")

        return FlextResult.ok(None)


class CLISession(FlextEntity):
    """CLI Session Domain Entity - Modern foundation pattern implementation.

    Eliminates 80% boilerplate through FlextEntity automatic features:
    - UUID-based ID generation
    - Timestamp management (created_at, updated_at)
    - Version control for optimistic locking
    - Domain event collection

    Usage:
        # Modern creation pattern
        >>> result = FlextFactory.create_entity(
        ...     CLISession,
        ...     entity_id="session-001",
        ...     session_id="test-session",
        ...     user_id="user123",
        ... )
        >>> session = result.unwrap()
    """

    session_id: str = Field(
        ...,
        min_length=1,
        max_length=MAX_ENTITY_NAME_LENGTH,
        description="Session identifier",
    )
    user_id: TUserId | None = Field(default=None, description="User ID")
    session_status: SessionStatus = Field(
        default=SessionStatus.ACTIVE,
        description="Session status",
    )
    command_history: list[EntityId] = Field(
        default_factory=list,
        description="Command history",
    )
    commands_executed: list[EntityId] = Field(
        default_factory=list,
        description="Executed commands",
    )
    current_command: EntityId | None = Field(
        default=None,
        description="Current command",
    )
    started_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Session start time",
    )
    last_activity: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Last activity",
    )
    ended_at: datetime | None = Field(default=None, description="Session end time")
    active: bool = Field(default=True, description="Session active status")

    # Context
    working_directory: str | None = Field(default=None, description="Working directory")
    environment: dict[str, str] = Field(
        default_factory=dict,
        description="Environment variables",
    )

    def add_command(self, command_id: EntityId) -> FlextResult[CLISession]:
        """Add command to session history with modern railway-oriented programming.

        Modern FlextResult pattern ensures type-safe command addition with
        proper validation and error handling.

        Returns:
            FlextResult[CLISession]: Railway-oriented result with updated session
                                   or validation error message.

        Modern Usage:
            >>> result = (
            ...     session.validate_business_rules()
            ...     .flat_map(lambda _: session.add_command("cmd-001"))
            ...     .map(lambda s: s.log_command_added())
            ... )

        """
        # Railway pattern - validate first
        validation_result = self.validate_business_rules()
        if validation_result.is_failure:
            return FlextResult.fail(validation_result.error or "Validation failed")

        if not command_id or not command_id.strip():
            return FlextResult.fail("Command ID cannot be empty")

        # Create new lists with the command added
        new_history = [*self.command_history, command_id]
        new_executed = [*self.commands_executed, command_id]
        now = datetime.now(UTC)

        # Create new instance with updated fields (immutable pattern)
        updated_session = self.model_copy(
            update={
                "command_history": new_history,
                "commands_executed": new_executed,
                "current_command": command_id,
                "last_activity": now,
                "updated_at": now,
            },
        )

        # Add domain event
        updated_session.add_domain_event(
            {
                "type": "CommandAdded",
                "session_id": updated_session.id,
                "command_id": command_id,
                "timestamp": now.isoformat(),
            },
        )

        return FlextResult.ok(updated_session)

    def end_session(self) -> FlextResult[CLISession]:
        """End CLI session with modern railway-oriented programming.

        Returns:
            FlextResult[CLISession]: Railway-oriented result with ended session.

        """
        validation_result = self.validate_business_rules()
        if validation_result.is_failure:
            return FlextResult.fail(validation_result.error or "Validation failed")

        if not self.active:
            return FlextResult.fail("Session is already ended")

        now = datetime.now(UTC)
        updated_session = self.model_copy(
            update={
                "session_status": SessionStatus.COMPLETED,
                "ended_at": now,
                "active": False,
                "current_command": None,
                "updated_at": now,
            },
        )

        # Add domain event
        updated_session.add_domain_event(
            {
                "type": "SessionEnded",
                "session_id": updated_session.id,
                "commands_executed": len(updated_session.commands_executed),
                "timestamp": now.isoformat(),
            },
        )

        return FlextResult.ok(updated_session)

    def validate_business_rules(self) -> FlextResult[None]:
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
    """CLI Plugin Domain Entity - Modern foundation pattern implementation.

    Eliminates boilerplate through FlextEntity automatic features:
    - Automatic ID, timestamps, versioning
    - Domain event collection for plugin lifecycle
    - Railway-oriented operations with FlextResult

    Modern Usage:
        # Zero-boilerplate creation
        >>> result = FlextFactory.create_entity(
        ...     CLIPlugin,
        ...     entity_id="plugin-001",
        ...     name="test-plugin",
        ...     entry_point="test_plugin.main",
        ... )
        >>> plugin = result.unwrap()
    """

    name: str = Field(
        ...,
        min_length=1,
        max_length=MAX_ENTITY_NAME_LENGTH,
        description="Plugin name",
    )
    plugin_version: str = Field(
        default="0.9.0",
        description="Plugin version string",
    )
    description: str | None = Field(
        None,
        max_length=MAX_ERROR_MESSAGE_LENGTH,
        description="Plugin description",
    )
    entry_point: str = Field(..., min_length=1, description="Plugin entry point")
    commands: list[str] = Field(default_factory=list, description="Plugin commands")
    dependencies: list[str] = Field(
        default_factory=list,
        description="Plugin dependencies",
    )
    plugin_status: PluginStatus = Field(
        default=PluginStatus.INACTIVE,
        description="Plugin status",
    )

    # Status
    enabled: bool = Field(default=True, description="Plugin enabled status")
    installed: bool = Field(default=False, description="Plugin installed status")

    # Metadata
    author: str | None = Field(default=None, description="Plugin author")
    license: str | None = Field(default=None, description="Plugin license")
    repository_url: str | None = Field(default=None, description="Repository URL")

    def activate(self) -> FlextResult[CLIPlugin]:
        """Activate plugin with modern railway-oriented programming.

        Modern FlextResult pattern ensures type-safe activation with
        proper validation and error handling.

        Returns:
            FlextResult[CLIPlugin]: Railway-oriented result with activated plugin
                                  or validation error message.

        Modern Usage:
            >>> result = (
            ...     plugin.validate_business_rules()
            ...     .flat_map(lambda _: plugin.activate())
            ...     .map(lambda p: p.log_activation())
            ... )

        """
        # Railway pattern - validate first
        validation_result = self.validate_business_rules()
        if validation_result.is_failure:
            return FlextResult.fail(validation_result.error or "Validation failed")

        if self.plugin_status == PluginStatus.ACTIVE:
            return FlextResult.fail("Plugin is already active")

        now = datetime.now(UTC)
        updated_plugin = self.model_copy(
            update={
                "plugin_status": PluginStatus.ACTIVE,
                "enabled": True,
                "updated_at": now,
            },
        )

        # Add domain event
        updated_plugin.add_domain_event(
            {
                "type": "PluginActivated",
                "plugin_id": updated_plugin.id,
                "name": updated_plugin.name,
                "timestamp": now.isoformat(),
            },
        )

        return FlextResult.ok(updated_plugin)

    def deactivate(self) -> FlextResult[CLIPlugin]:
        """Deactivate plugin with railway-oriented programming.

        Returns:
            FlextResult[CLIPlugin]: Railway-oriented result with deactivated plugin.

        """
        validation_result = self.validate_business_rules()
        if validation_result.is_failure:
            return FlextResult.fail(validation_result.error or "Validation failed")

        if self.plugin_status == PluginStatus.INACTIVE:
            return FlextResult.fail("Plugin is already inactive")

        now = datetime.now(UTC)
        updated_plugin = self.model_copy(
            update={
                "plugin_status": PluginStatus.INACTIVE,
                "enabled": False,
                "updated_at": now,
            },
        )

        # Add domain event
        updated_plugin.add_domain_event(
            {
                "type": "PluginDeactivated",
                "plugin_id": updated_plugin.id,
                "name": updated_plugin.name,
                "timestamp": now.isoformat(),
            },
        )

        return FlextResult.ok(updated_plugin)

    def enable(self) -> FlextResult[CLIPlugin]:
        """Enable the plugin (modern alias for activate).

        Returns:
            FlextResult[CLIPlugin]: Railway-oriented result with enabled plugin.

        """
        return self.activate()

    def disable(self) -> FlextResult[CLIPlugin]:
        """Disable the plugin with railway-oriented programming.

        Returns:
            FlextResult[CLIPlugin]: Railway-oriented result with disabled plugin.

        """
        return self.deactivate()

    def install(self) -> FlextResult[CLIPlugin]:
        """Install plugin with railway-oriented programming.

        Returns:
            FlextResult[CLIPlugin]: Railway-oriented result with installed plugin.

        """
        validation_result = self.validate_business_rules()
        if validation_result.is_failure:
            return FlextResult.fail(validation_result.error or "Validation failed")

        if self.installed:
            return FlextResult.fail("Plugin is already installed")

        now = datetime.now(UTC)
        updated_plugin = self.model_copy(
            update={
                "installed": True,
                "plugin_status": PluginStatus.ACTIVE,
                "enabled": True,
                "updated_at": now,
            },
        )

        # Add domain event
        updated_plugin.add_domain_event(
            {
                "type": "PluginInstalled",
                "plugin_id": updated_plugin.id,
                "name": updated_plugin.name,
                "timestamp": now.isoformat(),
            },
        )

        return FlextResult.ok(updated_plugin)

    def uninstall(self) -> FlextResult[CLIPlugin]:
        """Uninstall plugin with railway-oriented programming.

        Returns:
            FlextResult[CLIPlugin]: Railway-oriented result with uninstalled plugin.

        """
        validation_result = self.validate_business_rules()
        if validation_result.is_failure:
            return FlextResult.fail(validation_result.error or "Validation failed")

        if not self.installed:
            return FlextResult.fail("Plugin is not installed")

        now = datetime.now(UTC)
        updated_plugin = self.model_copy(
            update={
                "installed": False,
                "enabled": False,
                "plugin_status": PluginStatus.INACTIVE,
                "updated_at": now,
            },
        )

        # Add domain event
        updated_plugin.add_domain_event(
            {
                "type": "PluginUninstalled",
                "plugin_id": updated_plugin.id,
                "name": updated_plugin.name,
                "timestamp": now.isoformat(),
            },
        )

        return FlextResult.ok(updated_plugin)

    def validate_business_rules(self) -> FlextResult[None]:
        """Validate domain business rules for CLI plugins."""
        if not self.name or not self.name.strip():
            return FlextResult.fail("Plugin name cannot be empty")

        if not self.entry_point or not self.entry_point.strip():
            return FlextResult.fail("Plugin entry point cannot be empty")

        # Plugin version must be valid format (basic check)
        if not self.plugin_version or not self.plugin_version.strip():
            return FlextResult.fail("Plugin version cannot be empty")

        return FlextResult.ok(None)


class CLIConfig(DomainValueObject):
    """CLI configuration value object."""

    profile: str = Field(default="default", description="Configuration profile")
    debug: bool = Field(default=False, description="Debug mode")
    output_format: str = Field(default="table", description="Output format")

    def validate_business_rules(self) -> FlextResult[None]:
        """Validate domain business rules for CLI configuration."""
        valid_formats = ["table", "json", "yaml", "csv", "plain"]
        if self.output_format not in valid_formats:
            return FlextResult.fail("Invalid output format")

        return FlextResult.ok(None)


# DRY: CommandStatus and CommandType already defined above - duplicates removed


# Domain Events for CLI operations using flext-core patterns


class CommandStartedEvent(DomainValueObject):
    """Event raised when command starts execution."""

    command_id: EntityId = Field(..., description="Command ID")
    command_name: str | None = Field(None, description="Command name")
    session_id: str | None = Field(None, description="Session ID")


class CommandCompletedEvent(DomainValueObject):
    """Event raised when command completes."""

    command_id: EntityId = Field(..., description="Command ID")
    command_name: str | None = Field(None, description="Command name")
    success: bool = Field(..., description="Success status")


class CommandCancelledEvent(DomainValueObject):
    """Event raised when command is cancelled."""

    command_id: EntityId = Field(..., description="Command ID")
    command_name: str | None = Field(None, description="Command name")


class ConfigUpdatedEvent(DomainValueObject):
    """Event raised when configuration is updated."""

    config_id: EntityId = Field(..., description="Configuration ID")
    config_name: str | None = Field(None, description="Configuration name")


class SessionStartedEvent(DomainValueObject):
    """Event raised when CLI session starts."""

    session_id: EntityId = Field(..., description="Session ID")
    user_id: TUserId | None = Field(None, description="User ID")
    working_directory: str | None = Field(None, description="Working directory")


class SessionEndedEvent(DomainValueObject):
    """Event raised when CLI session ends."""

    session_id: EntityId = Field(..., description="Session ID")
    user_id: TUserId | None = Field(None, description="User ID")
    commands_executed: int = Field(..., description="Number of commands executed")
    duration_seconds: float | None = Field(None, description="Session duration")


class PluginInstalledEvent(DomainValueObject):
    """Event raised when plugin is installed."""

    plugin_id: EntityId = Field(..., description="Plugin ID")
    plugin_name: str | None = Field(None, description="Plugin name")


class PluginUninstalledEvent(DomainValueObject):
    """Event raised when plugin is uninstalled."""

    plugin_id: EntityId = Field(..., description="Plugin ID")
    plugin_name: str | None = Field(None, description="Plugin name")


# =============================================================================
# MODERN FACTORY PATTERNS - Zero-boilerplate entity creation
# =============================================================================


class CLIEntityFactory:
    """Modern CLI entity creation using FlextFactory patterns.

    Eliminates 90% of manual entity creation boilerplate by providing
    factory methods with built-in validation and FlextResult integration.

    Usage:
        # Modern zero-boilerplate command creation
        >>> result = CLIEntityFactory.create_command(
        ...     name="list-pipelines",
        ...     command_line="flext pipeline list",
        ...     command_type=CommandType.CLI,
        ... )
        >>> command = result.unwrap()
    """

    @staticmethod
    def create_command(
        name: str,
        command_line: str,
        command_type: CommandType = CommandType.SYSTEM,
        **kwargs: object,
    ) -> FlextResult[CLICommand]:
        """Create CLI command with automatic ID and timestamp generation."""
        return FlextFactory.create_entity(
            CLICommand,
            entity_id=str(uuid.uuid4()),
            name=name,
            command_line=command_line,
            command_type=command_type,
            **kwargs,
        )

    @staticmethod
    def create_session(
        session_id: str,
        user_id: TUserId | None = None,
        **kwargs: object,
    ) -> FlextResult[CLISession]:
        """Create CLI session with automatic ID and timestamp generation."""
        return FlextFactory.create_entity(
            CLISession,
            entity_id=str(uuid.uuid4()),
            session_id=session_id,
            user_id=user_id,
            **kwargs,
        )

    @staticmethod
    def create_plugin(
        name: str,
        entry_point: str,
        plugin_version: str = "0.9.0",
        **kwargs: object,
    ) -> FlextResult[CLIPlugin]:
        """Create CLI plugin with automatic ID and timestamp generation."""
        return FlextFactory.create_entity(
            CLIPlugin,
            entity_id=str(uuid.uuid4()),
            name=name,
            entry_point=entry_point,
            plugin_version=plugin_version,
            **kwargs,
        )


# Model rebuilding to resolve forward references
with contextlib.suppress(Exception):
    # Non-critical model rebuilding - skip if types not available
    # Ensure all types are available
    globals()["TUserId"] = TUserId
    globals()["EntityId"] = EntityId

    CLICommand.model_rebuild()
    CLISession.model_rebuild()
    CLIPlugin.model_rebuild()
    CLIConfig.model_rebuild()

    # Rebuild event classes too
    CommandStartedEvent.model_rebuild()
    CommandCompletedEvent.model_rebuild()
    CommandCancelledEvent.model_rebuild()
    ConfigUpdatedEvent.model_rebuild()
    SessionStartedEvent.model_rebuild()
    SessionEndedEvent.model_rebuild()
    PluginInstalledEvent.model_rebuild()
    PluginUninstalledEvent.model_rebuild()
