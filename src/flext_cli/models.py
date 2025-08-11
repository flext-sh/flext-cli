"""CLI-Specific Domain Models extending FLEXT-Core patterns.

This module provides CLI-specific domain models that extend flext-core's foundational
patterns without duplication. All models delegate to flext-core for base functionality
while adding CLI-specific business logic and validation.

Architecture:
    - FlextEntity: Identity-based entities with lifecycle management
    - FlextValueObject: Immutable value objects with attribute-based equality  
    - FlextAggregateRoot: DDD aggregate roots with transactional boundaries
    - FlextResult: Railway-oriented programming for error handling

CLI Models:
    - FlextCliCommand: Command execution entity with lifecycle management
    - FlextCliSession: CLI session tracking with command history
    - FlextCliContext: Execution context value object
    - FlextCliOutput: Command output value object
    - FlextCliPlugin: Plugin management entity
    - FlextCliConfiguration: Configuration value object

Design Principles:
    - NO DUPLICATION: All base functionality delegated to flext-core
    - EXTENSION ONLY: CLI-specific behavior and validation
    - CLEAN IMPORTS: Only from flext_core root module
    - TYPE SAFETY: Comprehensive type hints with Python 3.13 features
    - RAILWAY PATTERN: FlextResult for all business operations

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from typing import Any, ClassVar

# Import ONLY from flext_core root - never from submodules
from flext_core import (
    FlextAggregateRoot,
    FlextEntity,
    FlextEntityId,
    FlextResult,
    FlextValueObject,
)
from pydantic import Field, field_validator

# =============================================================================
# CLI-SPECIFIC ENUMERATIONS
# =============================================================================


class FlextCliCommandStatus(StrEnum):
    """CLI command execution status enumeration."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class FlextCliSessionState(StrEnum):
    """CLI session state enumeration."""

    ACTIVE = "active"
    IDLE = "idle"
    SUSPENDED = "suspended"
    TERMINATED = "terminated"
    ERROR = "error"


class FlextCliPluginState(StrEnum):
    """CLI plugin state enumeration."""

    UNLOADED = "unloaded"
    LOADING = "loading"
    LOADED = "loaded"
    ACTIVE = "active"
    DISABLED = "disabled"
    ERROR = "error"


class FlextCliOutputFormat(StrEnum):
    """CLI output format enumeration."""

    TEXT = "text"
    JSON = "json"
    XML = "xml"
    CSV = "csv"
    YAML = "yaml"
    TABLE = "table"


# =============================================================================
# CLI VALUE OBJECTS - Immutable data containers
# =============================================================================


class FlextCliContext(FlextValueObject):
    """CLI execution context value object.
    
    Immutable context containing execution environment, user information,
    and configuration settings for CLI command execution.
    
    Business Rules:
        - Working directory must exist if specified
        - Environment variables must be valid strings
        - User ID must be non-empty if provided
    """

    working_directory: Path | None = Field(
        default=None,
        description="Working directory for command execution"
    )
    environment_variables: dict[str, str] = Field(
        default_factory=dict,
        description="Environment variables for execution context"
    )
    user_id: str | None = Field(
        default=None,
        description="User identifier for the context"
    )
    session_id: str | None = Field(
        default=None,
        description="CLI session identifier"
    )
    configuration: dict[str, Any] = Field(
        default_factory=dict,
        description="Context-specific configuration"
    )
    timeout_seconds: int = Field(
        default=300,
        ge=1,
        description="Default timeout for operations in this context"
    )

    @field_validator("working_directory")
    @classmethod
    def validate_working_directory(cls, v: Path | None) -> Path | None:
        """Validate working directory exists if specified."""
        if v is not None and not v.exists():
            msg = f"Working directory does not exist: {v}"
            raise ValueError(msg)
        return v

    @field_validator("user_id")
    @classmethod
    def validate_user_id(cls, v: str | None) -> str | None:
        """Validate user ID is not empty if provided."""
        if v is not None and not v.strip():
            msg = "User ID cannot be empty string"
            raise ValueError(msg)
        return v.strip() if v else None

    def validate_business_rules(self) -> FlextResult[None]:
        """Validate CLI context business rules."""
        # Environment variables must be strings
        for key, value in self.environment_variables.items():
            if not isinstance(key, str) or not isinstance(value, str):
                return FlextResult.fail(
                    f"Environment variable '{key}' must be string key-value pair"
                )

        # Timeout must be reasonable
        if self.timeout_seconds > 86400:  # 24 hours
            return FlextResult.fail("Timeout cannot exceed 24 hours")

        return FlextResult.ok(None)

    def with_environment(self, **env_vars: str) -> FlextCliContext:
        """Create new context with additional environment variables."""
        new_env = {**self.environment_variables, **env_vars}
        return self.model_copy(update={"environment_variables": new_env})

    def with_working_directory(self, directory: Path) -> FlextCliContext:
        """Create new context with different working directory."""
        return self.model_copy(update={"working_directory": directory})


class FlextCliOutput(FlextValueObject):
    """CLI command output value object.
    
    Immutable container for command execution results including stdout,
    stderr, exit code, and timing information.
    
    Business Rules:
        - Exit code determines success (0 = success)
        - Duration must be non-negative
        - Output streams can be empty but not None after execution
    """

    stdout: str = Field(
        default="",
        description="Standard output from command execution"
    )
    stderr: str = Field(
        default="",
        description="Standard error from command execution"
    )
    exit_code: int | None = Field(
        default=None,
        description="Process exit code (None if not executed)"
    )
    execution_time_seconds: float | None = Field(
        default=None,
        ge=0,
        description="Command execution duration in seconds"
    )
    output_format: FlextCliOutputFormat = Field(
        default=FlextCliOutputFormat.TEXT,
        description="Format of the output content"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional output metadata"
    )
    captured_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Timestamp when output was captured"
    )

    @property
    def is_success(self) -> bool:
        """Check if command execution was successful (exit code 0)."""
        return self.exit_code == 0

    @property
    def is_error(self) -> bool:
        """Check if command execution had errors (non-zero exit code)."""
        return self.exit_code is not None and self.exit_code != 0

    @property
    def has_output(self) -> bool:
        """Check if command produced any output."""
        return bool(self.stdout.strip() or self.stderr.strip())

    def validate_business_rules(self) -> FlextResult[None]:
        """Validate CLI output business rules."""
        # Exit code range validation
        if self.exit_code is not None and (self.exit_code < 0 or self.exit_code > 255):
            return FlextResult.fail("Exit code must be between 0 and 255")

        # Execution time validation
        if self.execution_time_seconds is not None and self.execution_time_seconds < 0:
            return FlextResult.fail("Execution time cannot be negative")

        return FlextResult.ok(None)

    def format_output(self) -> str:
        """Format output for display based on output format."""
        if self.output_format == FlextCliOutputFormat.JSON:
            import json
            return json.dumps({
                "stdout": self.stdout,
                "stderr": self.stderr,
                "exit_code": self.exit_code,
                "execution_time": self.execution_time_seconds
            }, indent=2)

        # Default text format
        result = []
        if self.stdout.strip():
            result.append(f"STDOUT:\n{self.stdout}")
        if self.stderr.strip():
            result.append(f"STDERR:\n{self.stderr}")
        if self.exit_code is not None:
            result.append(f"EXIT CODE: {self.exit_code}")
        return "\n\n".join(result)


class FlextCliConfiguration(FlextValueObject):
    """CLI configuration value object.
    
    Immutable configuration container for CLI application settings,
    preferences, and operational parameters.
    
    Business Rules:
        - Profile name must be valid identifier
        - Log level must be recognized level
        - Paths must be accessible if specified
    """

    profile_name: str = Field(
        default="default",
        min_length=1,
        description="Configuration profile name"
    )
    log_level: str = Field(
        default="INFO",
        description="Logging level for CLI operations"
    )
    default_timeout: int = Field(
        default=300,
        ge=1,
        description="Default timeout for CLI operations in seconds"
    )
    output_format: FlextCliOutputFormat = Field(
        default=FlextCliOutputFormat.TEXT,
        description="Default output format"
    )
    config_file_path: Path | None = Field(
        default=None,
        description="Path to configuration file"
    )
    cache_directory: Path | None = Field(
        default=None,
        description="Directory for caching CLI data"
    )
    plugin_directories: list[Path] = Field(
        default_factory=list,
        description="Directories to search for plugins"
    )
    environment_overrides: dict[str, str] = Field(
        default_factory=dict,
        description="Environment variable overrides"
    )
    features_enabled: list[str] = Field(
        default_factory=list,
        description="List of enabled feature flags"
    )

    VALID_LOG_LEVELS: ClassVar[set[str]] = {
        "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"
    }

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level is recognized."""
        if v.upper() not in cls.VALID_LOG_LEVELS:
            msg = f"Log level must be one of: {', '.join(cls.VALID_LOG_LEVELS)}"
            raise ValueError(msg)
        return v.upper()

    @field_validator("profile_name")
    @classmethod
    def validate_profile_name(cls, v: str) -> str:
        """Validate profile name is valid identifier."""
        if not v.replace("_", "a").replace("-", "a").isalnum():
            msg = "Profile name must contain only alphanumeric, underscore, and dash characters"
            raise ValueError(msg)
        return v

    def validate_business_rules(self) -> FlextResult[None]:
        """Validate CLI configuration business rules."""
        # Validate paths if specified
        if self.config_file_path and not self.config_file_path.parent.exists():
            return FlextResult.fail(
                f"Config file directory does not exist: {self.config_file_path.parent}"
            )

        if self.cache_directory and not self.cache_directory.parent.exists():
            return FlextResult.fail(
                f"Cache directory parent does not exist: {self.cache_directory.parent}"
            )

        # Validate plugin directories exist
        for plugin_dir in self.plugin_directories:
            if not plugin_dir.exists():
                return FlextResult.fail(f"Plugin directory does not exist: {plugin_dir}")

        return FlextResult.ok(None)

    def is_feature_enabled(self, feature_name: str) -> bool:
        """Check if a feature is enabled."""
        return feature_name in self.features_enabled

    def with_feature(self, feature_name: str) -> FlextCliConfiguration:
        """Create new configuration with additional feature enabled."""
        features = [*self.features_enabled, feature_name]
        return self.model_copy(update={"features_enabled": list(set(features))})


# =============================================================================
# CLI ENTITIES - Identity-based domain objects
# =============================================================================


class FlextCliCommand(FlextEntity):
    """CLI command execution entity.
    
    Represents a CLI command with full execution lifecycle management,
    extending FlextEntity with CLI-specific business logic.
    
    Business Rules:
        - Command line must not be empty
        - Only pending commands can be started
        - Running commands can be completed or cancelled
        - Completed commands cannot change state
    """

    command_line: str = Field(
        ...,
        min_length=1,
        description="Command line string to execute"
    )
    arguments: list[str] = Field(
        default_factory=list,
        description="Command line arguments"
    )
    status: FlextCliCommandStatus = Field(
        default=FlextCliCommandStatus.PENDING,
        description="Current command execution status"
    )
    context: FlextCliContext = Field(
        default_factory=FlextCliContext,
        description="Execution context for the command"
    )
    output: FlextCliOutput | None = Field(
        default=None,
        description="Command execution output"
    )
    started_at: datetime | None = Field(
        default=None,
        description="Timestamp when command execution started"
    )
    completed_at: datetime | None = Field(
        default=None,
        description="Timestamp when command execution completed"
    )
    process_id: int | None = Field(
        default=None,
        description="Operating system process ID"
    )

    @property
    def is_terminal_state(self) -> bool:
        """Check if command is in a terminal state (cannot transition further)."""
        return self.status in {
            FlextCliCommandStatus.COMPLETED,
            FlextCliCommandStatus.FAILED,
            FlextCliCommandStatus.CANCELLED,
            FlextCliCommandStatus.TIMEOUT
        }

    @property
    def execution_duration(self) -> float | None:
        """Get command execution duration in seconds."""
        if self.started_at and self.completed_at:
            delta = self.completed_at - self.started_at
            return delta.total_seconds()
        return None

    def validate_business_rules(self) -> FlextResult[None]:
        """Validate CLI command business rules."""
        if not self.command_line.strip():
            return FlextResult.fail("Command line cannot be empty")

        # Validate timestamps are in correct order
        if self.started_at and self.completed_at:
            if self.completed_at < self.started_at:
                return FlextResult.fail("Completion time cannot be before start time")

        # Validate status transitions
        if self.status == FlextCliCommandStatus.RUNNING and not self.started_at:
            return FlextResult.fail("Running command must have started_at timestamp")

        if self.is_terminal_state and not self.completed_at:
            return FlextResult.fail("Terminal state commands must have completed_at timestamp")

        return FlextResult.ok(None)

    def start_execution(self) -> FlextResult[FlextCliCommand]:
        """Start command execution with validation."""
        if self.status != FlextCliCommandStatus.PENDING:
            return FlextResult.fail(f"Cannot start command in {self.status} status")

        # Validate context before starting
        context_validation = self.context.validate_business_rules()
        if context_validation.is_failure:
            return FlextResult.fail(f"Invalid context: {context_validation.error}")

        now = datetime.now(UTC)
        updated_command = self.copy_with(
            status=FlextCliCommandStatus.RUNNING,
            started_at=now
        )

        result = updated_command.unwrap()

        # Add domain event
        event_result = result.add_domain_event(
            "CommandStarted",
            {
                "command_id": result.id,
                "command_line": result.command_line,
                "started_at": now.isoformat()
            }
        )

        if event_result.is_failure:
            return FlextResult.fail(f"Failed to add domain event: {event_result.error}")

        return FlextResult.ok(result)

    def complete_execution(
        self,
        exit_code: int,
        stdout: str = "",
        stderr: str = ""
    ) -> FlextResult[FlextCliCommand]:
        """Complete command execution with output capture."""
        if self.status != FlextCliCommandStatus.RUNNING:
            return FlextResult.fail("Can only complete running commands")

        now = datetime.now(UTC)
        execution_time = None
        if self.started_at:
            execution_time = (now - self.started_at).total_seconds()

        # Create output value object
        output = FlextCliOutput(
            stdout=stdout,
            stderr=stderr,
            exit_code=exit_code,
            execution_time_seconds=execution_time,
            captured_at=now
        )

        # Determine final status based on exit code
        final_status = (
            FlextCliCommandStatus.COMPLETED if exit_code == 0
            else FlextCliCommandStatus.FAILED
        )

        updated_command = self.copy_with(
            status=final_status,
            output=output,
            completed_at=now,
            process_id=None  # Clear process ID
        )

        result = updated_command.unwrap()

        # Add domain event
        event_result = result.add_domain_event(
            "CommandCompleted",
            {
                "command_id": result.id,
                "exit_code": exit_code,
                "status": final_status.value,
                "execution_time": execution_time,
                "completed_at": now.isoformat()
            }
        )

        if event_result.is_failure:
            return FlextResult.fail(f"Failed to add domain event: {event_result.error}")

        return FlextResult.ok(result)

    def cancel_execution(self) -> FlextResult[FlextCliCommand]:
        """Cancel running command execution."""
        if self.status != FlextCliCommandStatus.RUNNING:
            return FlextResult.fail("Can only cancel running commands")

        now = datetime.now(UTC)
        updated_command = self.copy_with(
            status=FlextCliCommandStatus.CANCELLED,
            completed_at=now,
            process_id=None
        )

        result = updated_command.unwrap()

        # Add domain event
        event_result = result.add_domain_event(
            "CommandCancelled",
            {
                "command_id": result.id,
                "cancelled_at": now.isoformat()
            }
        )

        if event_result.is_failure:
            return FlextResult.fail(f"Failed to add domain event: {event_result.error}")

        return FlextResult.ok(result)


class FlextCliSession(FlextEntity):
    """CLI session tracking entity.
    
    Manages CLI session state with command history, user context,
    and session lifecycle operations.
    
    Business Rules:
        - Session must have valid user context
        - Commands can only be added to active sessions
        - Session termination clears active state
    """

    user_id: str = Field(
        ...,
        min_length=1,
        description="User identifier for this session"
    )
    state: FlextCliSessionState = Field(
        default=FlextCliSessionState.ACTIVE,
        description="Current session state"
    )
    context: FlextCliContext = Field(
        default_factory=FlextCliContext,
        description="Session execution context"
    )
    configuration: FlextCliConfiguration = Field(
        default_factory=FlextCliConfiguration,
        description="Session configuration"
    )
    command_history: list[FlextEntityId] = Field(
        default_factory=list,
        description="History of command IDs executed in this session"
    )
    current_command_id: FlextEntityId | None = Field(
        default=None,
        description="ID of currently executing command"
    )
    session_data: dict[str, Any] = Field(
        default_factory=dict,
        description="Session-specific data storage"
    )
    started_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Session start timestamp"
    )
    last_activity_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Last activity timestamp"
    )
    ended_at: datetime | None = Field(
        default=None,
        description="Session end timestamp"
    )

    @property
    def is_active(self) -> bool:
        """Check if session is active."""
        return self.state == FlextCliSessionState.ACTIVE

    @property
    def commands_executed_count(self) -> int:
        """Get count of commands executed in this session."""
        return len(self.command_history)

    @property
    def session_duration(self) -> float | None:
        """Get session duration in seconds."""
        end_time = self.ended_at or datetime.now(UTC)
        delta = end_time - self.started_at
        return delta.total_seconds()

    def validate_business_rules(self) -> FlextResult[None]:
        """Validate CLI session business rules."""
        if not self.user_id.strip():
            return FlextResult.fail("User ID cannot be empty")

        # Validate timestamps
        if self.ended_at and self.ended_at < self.started_at:
            return FlextResult.fail("End time cannot be before start time")

        if self.last_activity_at < self.started_at:
            return FlextResult.fail("Last activity cannot be before start time")

        # Current command must be in history if set
        if (self.current_command_id and
            self.current_command_id not in self.command_history):
            return FlextResult.fail("Current command must be in command history")

        return FlextResult.ok(None)

    def add_command(self, command_id: FlextEntityId) -> FlextResult[FlextCliSession]:
        """Add command to session history."""
        if not self.is_active:
            return FlextResult.fail("Cannot add commands to inactive session")

        now = datetime.now(UTC)
        new_history = [*self.command_history, command_id]

        updated_session = self.copy_with(
            command_history=new_history,
            current_command_id=command_id,
            last_activity_at=now
        )

        result = updated_session.unwrap()

        # Add domain event
        event_result = result.add_domain_event(
            "CommandAddedToSession",
            {
                "session_id": result.id,
                "command_id": command_id,
                "command_count": len(new_history),
                "added_at": now.isoformat()
            }
        )

        if event_result.is_failure:
            return FlextResult.fail(f"Failed to add domain event: {event_result.error}")

        return FlextResult.ok(result)

    def suspend_session(self) -> FlextResult[FlextCliSession]:
        """Suspend the session."""
        if not self.is_active:
            return FlextResult.fail("Can only suspend active sessions")

        now = datetime.now(UTC)
        updated_session = self.copy_with(
            state=FlextCliSessionState.SUSPENDED,
            current_command_id=None,
            last_activity_at=now
        )

        result = updated_session.unwrap()

        # Add domain event
        event_result = result.add_domain_event(
            "SessionSuspended",
            {
                "session_id": result.id,
                "suspended_at": now.isoformat()
            }
        )

        if event_result.is_failure:
            return FlextResult.fail(f"Failed to add domain event: {event_result.error}")

        return FlextResult.ok(result)

    def resume_session(self) -> FlextResult[FlextCliSession]:
        """Resume suspended session."""
        if self.state != FlextCliSessionState.SUSPENDED:
            return FlextResult.fail("Can only resume suspended sessions")

        now = datetime.now(UTC)
        updated_session = self.copy_with(
            state=FlextCliSessionState.ACTIVE,
            last_activity_at=now
        )

        result = updated_session.unwrap()

        # Add domain event
        event_result = result.add_domain_event(
            "SessionResumed",
            {
                "session_id": result.id,
                "resumed_at": now.isoformat()
            }
        )

        if event_result.is_failure:
            return FlextResult.fail(f"Failed to add domain event: {event_result.error}")

        return FlextResult.ok(result)

    def terminate_session(self) -> FlextResult[FlextCliSession]:
        """Terminate the session."""
        if self.state == FlextCliSessionState.TERMINATED:
            return FlextResult.fail("Session is already terminated")

        now = datetime.now(UTC)
        updated_session = self.copy_with(
            state=FlextCliSessionState.TERMINATED,
            current_command_id=None,
            ended_at=now,
            last_activity_at=now
        )

        result = updated_session.unwrap()

        # Add domain event
        event_result = result.add_domain_event(
            "SessionTerminated",
            {
                "session_id": result.id,
                "commands_executed": len(self.command_history),
                "duration_seconds": self.session_duration,
                "terminated_at": now.isoformat()
            }
        )

        if event_result.is_failure:
            return FlextResult.fail(f"Failed to add domain event: {event_result.error}")

        return FlextResult.ok(result)


class FlextCliPlugin(FlextEntity):
    """CLI plugin management entity.
    
    Manages plugin lifecycle, metadata, and integration with the CLI system.
    
    Business Rules:
        - Plugin name must be unique
        - Entry point must be valid Python module path
        - Plugin must be loaded before activation
    """

    name: str = Field(
        ...,
        min_length=1,
        description="Unique plugin name"
    )
    description: str | None = Field(
        default=None,
        description="Plugin description"
    )
    version: str = Field(
        default="0.1.0",
        description="Plugin version string"
    )
    entry_point: str = Field(
        ...,
        min_length=1,
        description="Python module entry point (e.g., 'package.module:function')"
    )
    state: FlextCliPluginState = Field(
        default=FlextCliPluginState.UNLOADED,
        description="Current plugin state"
    )
    author: str | None = Field(
        default=None,
        description="Plugin author"
    )
    license: str | None = Field(
        default=None,
        description="Plugin license"
    )
    dependencies: list[str] = Field(
        default_factory=list,
        description="List of required dependencies"
    )
    commands: list[str] = Field(
        default_factory=list,
        description="Commands provided by this plugin"
    )
    configuration: dict[str, Any] = Field(
        default_factory=dict,
        description="Plugin-specific configuration"
    )
    plugin_directory: Path | None = Field(
        default=None,
        description="Directory containing plugin files"
    )
    loaded_at: datetime | None = Field(
        default=None,
        description="Timestamp when plugin was loaded"
    )
    last_error: str | None = Field(
        default=None,
        description="Last error message if plugin failed"
    )

    @property
    def is_loaded(self) -> bool:
        """Check if plugin is loaded."""
        return self.state in {
            FlextCliPluginState.LOADED,
            FlextCliPluginState.ACTIVE
        }

    @property
    def is_active(self) -> bool:
        """Check if plugin is active."""
        return self.state == FlextCliPluginState.ACTIVE

    @field_validator("entry_point")
    @classmethod
    def validate_entry_point(cls, v: str) -> str:
        """Validate entry point format."""
        if ":" in v:
            module_path, function_name = v.split(":", 1)
            if not module_path or not function_name:
                msg = "Entry point must be in format 'module.path:function_name'"
                raise ValueError(msg)
        elif "." not in v:
            msg = "Entry point must contain module path"
            raise ValueError(msg)
        return v

    def validate_business_rules(self) -> FlextResult[None]:
        """Validate CLI plugin business rules."""
        if not self.name.strip():
            return FlextResult.fail("Plugin name cannot be empty")

        if not self.entry_point.strip():
            return FlextResult.fail("Entry point cannot be empty")

        # Validate plugin directory exists if specified
        if self.plugin_directory and not self.plugin_directory.exists():
            return FlextResult.fail(f"Plugin directory does not exist: {self.plugin_directory}")

        # Validate state transitions
        if self.state == FlextCliPluginState.ACTIVE and not self.loaded_at:
            return FlextResult.fail("Active plugin must have loaded_at timestamp")

        return FlextResult.ok(None)

    def load_plugin(self) -> FlextResult[FlextCliPlugin]:
        """Load the plugin."""
        if self.state != FlextCliPluginState.UNLOADED:
            return FlextResult.fail(f"Cannot load plugin in {self.state} state")

        # Set loading state first
        loading_result = self.copy_with(state=FlextCliPluginState.LOADING)
        if loading_result.is_failure:
            return loading_result

        try:
            # Plugin loading logic would go here
            # For now, simulate successful loading
            now = datetime.now(UTC)
            loaded_plugin = loading_result.unwrap().copy_with(
                state=FlextCliPluginState.LOADED,
                loaded_at=now,
                last_error=None
            )

            result = loaded_plugin.unwrap()

            # Add domain event
            event_result = result.add_domain_event(
                "PluginLoaded",
                {
                    "plugin_id": result.id,
                    "plugin_name": result.name,
                    "loaded_at": now.isoformat()
                }
            )

            if event_result.is_failure:
                return FlextResult.fail(f"Failed to add domain event: {event_result.error}")

            return FlextResult.ok(result)

        except Exception as e:
            # Handle loading error
            error_result = loading_result.unwrap().copy_with(
                state=FlextCliPluginState.ERROR,
                last_error=str(e)
            )
            return error_result

    def activate_plugin(self) -> FlextResult[FlextCliPlugin]:
        """Activate the loaded plugin."""
        if self.state != FlextCliPluginState.LOADED:
            return FlextResult.fail(f"Cannot activate plugin in {self.state} state")

        updated_plugin = self.copy_with(state=FlextCliPluginState.ACTIVE)
        result = updated_plugin.unwrap()

        # Add domain event
        event_result = result.add_domain_event(
            "PluginActivated",
            {
                "plugin_id": result.id,
                "plugin_name": result.name,
                "commands": result.commands,
                "activated_at": datetime.now(UTC).isoformat()
            }
        )

        if event_result.is_failure:
            return FlextResult.fail(f"Failed to add domain event: {event_result.error}")

        return FlextResult.ok(result)

    def deactivate_plugin(self) -> FlextResult[FlextCliPlugin]:
        """Deactivate the plugin."""
        if self.state != FlextCliPluginState.ACTIVE:
            return FlextResult.fail(f"Cannot deactivate plugin in {self.state} state")

        updated_plugin = self.copy_with(state=FlextCliPluginState.LOADED)
        result = updated_plugin.unwrap()

        # Add domain event
        event_result = result.add_domain_event(
            "PluginDeactivated",
            {
                "plugin_id": result.id,
                "plugin_name": result.name,
                "deactivated_at": datetime.now(UTC).isoformat()
            }
        )

        if event_result.is_failure:
            return FlextResult.fail(f"Failed to add domain event: {event_result.error}")

        return FlextResult.ok(result)

    def unload_plugin(self) -> FlextResult[FlextCliPlugin]:
        """Unload the plugin."""
        if self.state == FlextCliPluginState.UNLOADED:
            return FlextResult.fail("Plugin is already unloaded")

        # Deactivate first if active
        if self.state == FlextCliPluginState.ACTIVE:
            deactivate_result = self.deactivate_plugin()
            if deactivate_result.is_failure:
                return deactivate_result
            current_plugin = deactivate_result.unwrap()
        else:
            current_plugin = self

        updated_plugin = current_plugin.copy_with(
            state=FlextCliPluginState.UNLOADED,
            loaded_at=None
        )

        result = updated_plugin.unwrap()

        # Add domain event
        event_result = result.add_domain_event(
            "PluginUnloaded",
            {
                "plugin_id": result.id,
                "plugin_name": result.name,
                "unloaded_at": datetime.now(UTC).isoformat()
            }
        )

        if event_result.is_failure:
            return FlextResult.fail(f"Failed to add domain event: {event_result.error}")

        return FlextResult.ok(result)


# =============================================================================
# CLI AGGREGATE ROOT - Complex business operations
# =============================================================================


class FlextCliWorkspace(FlextAggregateRoot):
    """CLI workspace aggregate root.
    
    Manages complex CLI operations involving multiple entities and
    cross-cutting concerns with transactional boundaries.
    
    Business Rules:
        - Workspace must have unique name
        - Sessions belong to workspace
        - Plugins are shared across sessions in workspace
    """

    name: str = Field(
        ...,
        min_length=1,
        description="Workspace name"
    )
    description: str | None = Field(
        default=None,
        description="Workspace description"
    )
    configuration: FlextCliConfiguration = Field(
        default_factory=FlextCliConfiguration,
        description="Workspace configuration"
    )
    session_ids: list[FlextEntityId] = Field(
        default_factory=list,
        description="Active session IDs in this workspace"
    )
    plugin_ids: list[FlextEntityId] = Field(
        default_factory=list,
        description="Installed plugin IDs"
    )
    workspace_data: dict[str, Any] = Field(
        default_factory=dict,
        description="Workspace-specific data storage"
    )

    def validate_business_rules(self) -> FlextResult[None]:
        """Validate CLI workspace business rules."""
        if not self.name.strip():
            return FlextResult.fail("Workspace name cannot be empty")

        return FlextResult.ok(None)

    def add_session(self, session_id: FlextEntityId) -> FlextResult[FlextCliWorkspace]:
        """Add session to workspace."""
        validation_result = self.validate_business_rules()
        if validation_result.is_failure:
            return FlextResult.fail(validation_result.error or "Validation failed")

        if session_id in self.session_ids:
            return FlextResult.fail("Session already exists in workspace")

        new_session_ids = [*self.session_ids, session_id]
        updated_workspace = self.copy_with(session_ids=new_session_ids)

        result = updated_workspace.unwrap()

        # Add domain event
        event_result = result.add_domain_event(
            "SessionAddedToWorkspace",
            {
                "workspace_id": result.id,
                "session_id": session_id,
                "session_count": len(new_session_ids),
                "added_at": datetime.now(UTC).isoformat()
            }
        )

        if event_result.is_failure:
            return FlextResult.fail(f"Failed to add domain event: {event_result.error}")

        return FlextResult.ok(result)

    def remove_session(self, session_id: FlextEntityId) -> FlextResult[FlextCliWorkspace]:
        """Remove session from workspace."""
        if session_id not in self.session_ids:
            return FlextResult.fail("Session not found in workspace")

        new_session_ids = [sid for sid in self.session_ids if sid != session_id]
        updated_workspace = self.copy_with(session_ids=new_session_ids)

        result = updated_workspace.unwrap()

        # Add domain event
        event_result = result.add_domain_event(
            "SessionRemovedFromWorkspace",
            {
                "workspace_id": result.id,
                "session_id": session_id,
                "remaining_sessions": len(new_session_ids),
                "removed_at": datetime.now(UTC).isoformat()
            }
        )

        if event_result.is_failure:
            return FlextResult.fail(f"Failed to add domain event: {event_result.error}")

        return FlextResult.ok(result)

    def install_plugin(self, plugin_id: FlextEntityId) -> FlextResult[FlextCliWorkspace]:
        """Install plugin in workspace."""
        if plugin_id in self.plugin_ids:
            return FlextResult.fail("Plugin already installed in workspace")

        new_plugin_ids = [*self.plugin_ids, plugin_id]
        updated_workspace = self.copy_with(plugin_ids=new_plugin_ids)

        result = updated_workspace.unwrap()

        # Add domain event
        event_result = result.add_domain_event(
            "PluginInstalledInWorkspace",
            {
                "workspace_id": result.id,
                "plugin_id": plugin_id,
                "plugin_count": len(new_plugin_ids),
                "installed_at": datetime.now(UTC).isoformat()
            }
        )

        if event_result.is_failure:
            return FlextResult.fail(f"Failed to add domain event: {event_result.error}")

        return FlextResult.ok(result)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Enumerations
    "FlextCliCommandStatus",
    "FlextCliSessionState",
    "FlextCliPluginState",
    "FlextCliOutputFormat",
    # Value Objects
    "FlextCliContext",
    "FlextCliOutput",
    "FlextCliConfiguration",
    # Entities
    "FlextCliCommand",
    "FlextCliSession",
    "FlextCliPlugin",
    # Aggregate Root
    "FlextCliWorkspace",
]
