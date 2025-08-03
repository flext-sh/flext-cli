"""Application Layer Commands - CQRS Command Handlers and Application Services.

This module implements the application layer for FLEXT CLI example, demonstrating
CQRS (Command Query Responsibility Segregation) patterns, application services,
and use case orchestration. Designed as reference implementation for Sprint 2-3
CQRS enhancement.

Architecture:
    - Application layer following Clean Architecture principles
    - CQRS pattern with command and query separation
    - Use case orchestration with domain service coordination
    - Parameter Object pattern to reduce complexity
    - FlextResult error handling throughout

Current Implementation Status:
    ⚠️ BASIC IMPLEMENTATION - Sprint 2-3 Enhancement Target
    - Basic command execution configuration (Parameter Object pattern)
    - Foundation for CQRS implementation
    - Domain service integration patterns
    - Full CQRS handlers pending Sprint 2-3

Target Implementation (Sprint 2-3):
    ✅ Complete CQRS command handlers for all operations
    ✅ Query handlers for read-only operations
    ✅ Event handlers for domain event processing
    ✅ Application service orchestration
    ✅ Cross-cutting concern management (logging, monitoring, caching)

CQRS Pattern Implementation:
    Commands (Write Operations):
        - ExecuteCliCommand: Execute CLI commands with lifecycle tracking
        - CreatePipelineCommand: Create new data pipelines
        - StartPipelineCommand: Start pipeline execution
        - ConfigurePluginCommand: Configure plugin settings

    Queries (Read Operations):
        - ListPipelinesQuery: List pipelines with filtering
        - GetPipelineStatusQuery: Get pipeline execution status
        - ListPluginsQuery: List available plugins
        - GetConfigurationQuery: Get system configuration

    Events (Domain Events):
        - CommandExecutedEvent: CLI command execution completed
        - PipelineStartedEvent: Pipeline execution started
        - PluginInstalledEvent: Plugin installation completed

Application Services:
    - PipelineOrchestrationService: Complex pipeline workflows
    - PluginManagementService: Plugin lifecycle management
    - ConfigurationService: Configuration coordination
    - MonitoringService: Cross-cutting monitoring and metrics

Parameter Object Pattern:
    Applied to reduce method parameter complexity and improve maintainability.
    CommandExecutionConfig encapsulates execution parameters following
    SOLID principles for better extensibility.

Usage Examples:
    Command execution:
    >>> config = CommandExecutionConfig(
    ...     name="deploy",
    ...     command_line="kubectl apply -f app.yaml",
    ...     command_type=CommandType.SYSTEM,
    ... )
    >>> handler = ExecuteCliCommandHandler(service)
    >>> result = await handler.handle(config)

    CQRS implementation (Sprint 2-3 target):
    >>> command = CreatePipelineCommand(name="etl", config=pipeline_config)
    >>> result = await command_bus.execute(command)

Integration Points:
    - Domain Layer: Uses domain entities and services for business logic
    - Infrastructure Layer: Repository and external service access
    - Commands Layer: Receives requests from CLI commands
    - FlextCore: Integration with enterprise patterns and containers

Sprint 2-3 Enhancement Priority:
    This module is the primary target for Sprint 2-3 CQRS implementation.
    Will transform from basic command execution to full CQRS architecture
    with dedicated command/query handlers and event processing.

TODO (Sprint 2-3 Implementation):
    - Implement complete CQRS command handlers
    - Add query handlers for read operations
    - Create event handlers for domain events
    - Add application service orchestration
    - Implement cross-cutting concerns (logging, caching, monitoring)
    - Integrate with FlextContainer dependency injection
    - Add comprehensive error handling and recovery

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_cli.domain.entities import CommandType

if TYPE_CHECKING:
    from uuid import UUID


from dataclasses import dataclass


@dataclass
class CommandExecutionConfig:
    """Configuration for command execution - Parameter Object Pattern.

    REFACTORED: Applied Parameter Object pattern to reduce parameter count from 11 to 3.
    Follows SOLID principles for better maintainability and extensibility.
    """

    # Core parameters
    name: str
    command_line: str
    command_type: CommandType = CommandType.SYSTEM

    # Execution context
    arguments: dict[str, object] | None = None
    options: dict[str, object] | None = None
    user_id: UUID | None = None
    session_id: str | None = None

    # Environment configuration
    working_directory: str | None = None
    environment: dict[str, str] | None = None
    timeout_seconds: float | None = None


class ExecuteCommandCommand:
    """Command to execute a CLI command.

    REFACTORED: Uses Parameter Object pattern to reduce constructor complexity.
    """

    def __init__(self, config: CommandExecutionConfig) -> None:
        """Initialize the command with configuration object.

        Args:
            config: All command execution parameters in a single object

        """
        self.config = config

    # Convenience properties for backward compatibility
    @property
    def name(self) -> str:
        """Get command name."""
        return self.config.name

    @property
    def command_line(self) -> str:
        """Get command line."""
        return self.config.command_line

    @property
    def command_type(self) -> CommandType:
        """Get command type."""
        return self.config.command_type

    @property
    def arguments(self) -> dict[str, object] | None:
        """Get arguments."""
        return self.config.arguments

    @property
    def options(self) -> dict[str, object] | None:
        """Get options."""
        return self.config.options

    @property
    def user_id(self) -> UUID | None:
        """Get user ID."""
        return self.config.user_id

    @property
    def session_id(self) -> str | None:
        """Get session ID."""
        return self.config.session_id

    @property
    def working_directory(self) -> str | None:
        """Get working directory."""
        return self.config.working_directory

    @property
    def environment(self) -> dict[str, str] | None:
        """Get environment variables."""
        return self.config.environment

    @property
    def timeout_seconds(self) -> float | None:
        """Get timeout in seconds."""
        return self.config.timeout_seconds


class CancelCommandCommand:
    """Command to cancel a running CLI command."""

    def __init__(self, command_id: UUID, user_id: UUID | None = None) -> None:
        """Initialize cancel command.

        Args:
            command_id: ID of command to cancel
            user_id: User requesting cancellation

        """
        self.command_id = command_id
        self.user_id = user_id


class CreateConfigCommand:
    """Command to create a CLI configuration."""

    name: str
    description = None
    config_data: dict[str, object]
    config_type: str
    version = "0.9.0"
    user_id: UUID | None = None
    is_global: bool = False


class UpdateConfigCommand:
    """Command to update a CLI configuration."""

    config_id: UUID
    name = None
    description: str | None = None
    config_data: dict[str, object] | None = None
    version: str | None = None
    user_id: UUID | None = None


class DeleteConfigCommand:
    """Command to delete a CLI configuration."""

    config_id: UUID
    user_id = None


class ValidateConfigCommand:
    """Command to validate a CLI configuration."""

    config_id: UUID
    user_id = None


class StartSessionCommand:
    """Command to start a CLI session."""

    session_id: str
    user_id = None
    working_directory: str | None = None
    environment: dict[str, str] | None = None


class EndSessionCommand:
    """Command to end a CLI session."""

    session_id: UUID
    user_id = None


class InstallPluginCommand:
    """Command to install a CLI plugin."""

    name: str
    version = None
    entry_point: str
    commands: list[str] | None = None
    dependencies: list[str] | None = None
    author: str | None = None
    license: str | None = None
    repository_url: str | None = None
    user_id: UUID | None = None


class UninstallPluginCommand:
    """Command to uninstall a CLI plugin."""

    plugin_id: UUID
    user_id = None


class EnablePluginCommand:
    """Command to enable a CLI plugin."""

    plugin_id: UUID
    user_id = None


class DisablePluginCommand:
    """Command to disable a CLI plugin."""

    plugin_id: UUID
    user_id = None


class ListCommandsCommand:
    """Command to list available CLI commands."""

    command_type: CommandType | None = None
    user_id: UUID | None = None
    session_id: str | None = None


class GetCommandHistoryCommand:
    """Command to get command execution history."""

    user_id: UUID | None = None
    session_id: str | None = None
    limit: int = 100
    command_type: CommandType | None = None


class GetCommandStatusCommand:
    """Command to get command execution status."""

    command_id: UUID
    user_id = None


class ListConfigsCommand:
    """Command to list CLI configurations."""

    config_type: str | None = None
    user_id: UUID | None = None
    include_global: bool = True


class ListPluginsCommand:
    """Command to list CLI plugins."""

    enabled_only: bool = False
    installed_only: bool = False
    user_id: UUID | None = None


class GetSessionInfoCommand:
    """Command to get CLI session information."""

    session_id: UUID
    user_id = None
