"""FLEXT CLI Models - Single unified class following FLEXT standards.

Provides CLI-specific Pydantic models using flext-core standardization.
Single FlextCliModels class with nested model subclasses following FLEXT pattern.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import override

try:
    from typing import Self
except ImportError:
    from typing import Self

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    computed_field,
    field_serializer,
    model_validator,
)

from flext_cli.constants import FlextCliConstants
from flext_cli.mixins import FlextCliMixins
from flext_cli.typings import FlextCliTypes
from flext_core import (
    FlextModels,
    FlextResult,
)


class FlextCliModels(BaseModel, FlextModels):
    """Single unified CLI models class following FLEXT standards.

    Contains all Pydantic model subclasses for CLI domain operations.
    Follows FLEXT pattern: one class per module with nested subclasses.

    ARCHITECTURAL COMPLIANCE:
    - Inherits from FlextModels to avoid duplication
    - Uses centralized validation via FlextModels.Validation
    - Implements CLI-specific extensions while reusing core functionality

    CRITICAL ARCHITECTURE: ALL model validation is centralized in FlextModels.
    NO inline validation is allowed in service methods.
    """

    # For test instantiation
    name: str = Field(default="FlextCliModels")

    # Advanced Pydantic 2.11 configuration for comprehensive model behavior
    model_config = ConfigDict(
        validate_assignment=True,
        use_enum_values=True,
        arbitrary_types_allowed=True,
        extra="forbid",
        frozen=False,
        validate_return=True,
        ser_json_timedelta="iso8601",
        ser_json_bytes="base64",
        hide_input_in_errors=True,
        json_schema_extra={
            "title": "FlextCliModels",
            "description": "Comprehensive CLI domain models with advanced Pydantic 2.11 features",
            "examples": [
                {
                    "cli_command": {
                        "command_line": "flext validate",
                        "status": "pending",
                        "args": ["validate"],
                    }
                }
            ],
        },
    )

    @computed_field
    def active_models_count(self) -> int:
        """Computed field returning the number of active CLI model types."""
        # Count all nested model classes
        # Note: FormatOptions and CliPipeline removed - delegated to specialized services
        model_classes = [
            "CliCommand",
            "DebugInfo",
            "CliSession",
            "CliFormatters",
            "LoggingConfig",
            "PipelineConfig",
        ]
        return len(model_classes)

    @computed_field
    def model_summary(self) -> dict[str, str]:
        """Computed field returning a summary of all available models."""
        # Note: FormatOptions and CliPipeline removed - delegated to specialized services
        return {
            "CliCommand": "Command execution model with status tracking",
            "DebugInfo": "Debug information model with system details",
            "CliSession": "User session tracking model",
            "CliFormatters": "Available output formatters",
            "LoggingConfig": "Logging configuration model",
            "PipelineConfig": "Pipeline configuration model",
        }

    @model_validator(mode="after")
    def validate_cli_models_consistency(self) -> Self:
        """Cross-model validation ensuring CLI models consistency."""
        # Ensure all required nested classes are properly defined
        # Note: FormatOptions and CliPipeline removed - delegated to specialized services
        required_nested_classes = [
            "_BaseEntity",
            "_BaseValidatedModel",
            "_BaseConfig",
            "CliCommand",
            "DebugInfo",
            "CliSession",
        ]

        for class_name in required_nested_classes:
            if not hasattr(self.__class__, class_name):
                error_message = f"Required nested class {class_name} not found"
                raise ValueError(error_message)

        return self

    @field_serializer("model_summary")
    def serialize_model_summary(
        self, value: dict[str, str], _info: object
    ) -> dict[str, str | dict[str, str | int]]:
        """Serialize model summary with additional metadata."""
        return {
            **value,
            "_metadata": {
                "generated_at": datetime.now(UTC).isoformat(),
                "total_models": len(value),
                "serialization_version": "2.11",
            },
        }

    # Base classes for common functionality - using flext-core patterns
    class _BaseEntity(FlextModels.Entity, FlextCliMixins.ValidationMixin):
        """Base entity with common fields for entities with id, timestamps, and status."""

        model_config = ConfigDict(
            validate_assignment=True,
            use_enum_values=True,
            arbitrary_types_allowed=True,
            extra="forbid",
            validate_return=True,
        )

        id: str = Field(
            default_factory=lambda: f"entity_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S_%f')}"
        )
        created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
        updated_at: datetime | None = (
            None  # Inherit from parent - can be None initially
        )
        status: str = Field(default=FlextCliConstants.CommandStatus.PENDING.value)

        @computed_field
        def entity_age_seconds(self) -> float:
            """Computed field for entity age in seconds."""
            return (datetime.now(UTC) - self.created_at).total_seconds()

        @model_validator(mode="after")
        def validate_timestamps(self) -> Self:
            """Validate timestamp consistency."""
            if self.updated_at and self.updated_at < self.created_at:
                timestamp_error = "updated_at cannot be before created_at"
                raise ValueError(timestamp_error)
            return self

        def update_timestamp(self) -> None:
            """Update the updated_at timestamp."""
            self.updated_at = datetime.now(UTC)

    class _BaseValidatedModel(BaseModel, FlextCliMixins.ValidationMixin):
        """Base model with common validation patterns."""

        model_config = ConfigDict(
            validate_assignment=True,
            use_enum_values=True,
            arbitrary_types_allowed=True,
            extra="forbid",
            validate_return=True,
        )

        @computed_field
        def model_type(self) -> str:
            """Computed field returning the model type name."""
            return self.__class__.__name__

    class _BaseConfig(_BaseValidatedModel):
        """Base configuration model with common config validation patterns."""

        @model_validator(mode="after")
        def validate_config_consistency(self) -> Self:
            """Validate configuration consistency."""
            # Base validation for all config models
            return self

    class CliCommand(_BaseEntity, FlextCliMixins.BusinessRulesMixin):
        """CLI command model extending _BaseEntity."""

        command_line: str = Field(min_length=1)
        args: list[str] = Field(default_factory=list)
        exit_code: int | None = None
        output: str = Field(default="")
        error_output: str = Field(default="")
        name: str = Field(default="")
        description: str = Field(default="")
        usage: str = Field(default="")
        entry_point: str = Field(default="")
        plugin_version: str = Field(
            default_factory=lambda: FlextCliConstants.CliDefaults.DEFAULT_PROFILE
        )
        # status field inherited from _BaseEntity

        @computed_field
        def command_summary(self) -> dict[str, object]:
            """Computed field for command execution summary."""
            return {
                "command": self.command_line,
                "args_count": len(self.args),
                "has_output": bool(self.output),
                "has_errors": bool(self.error_output),
                "is_completed": self.exit_code is not None,
                "execution_time": self.entity_age_seconds,
            }

        @computed_field
        def is_successful(self) -> bool:
            """Computed field indicating if command executed successfully."""
            return self.exit_code == 0 if self.exit_code is not None else False

        @model_validator(mode="after")
        def validate_command_consistency(self) -> Self:
            """Cross-field validation for command consistency."""
            # If exit_code is set, status should be completed
            if (
                self.exit_code is not None
                and self.status == FlextCliConstants.CommandStatus.PENDING.value
            ):
                exit_code_error = "Command with exit_code cannot have pending status"
                raise ValueError(exit_code_error)

            # If command has output, it should have been executed
            if (
                self.output
                and self.status == FlextCliConstants.CommandStatus.PENDING.value
            ):
                output_error = "Command with output cannot have pending status"
                raise ValueError(output_error)

            return self

        @field_serializer("command_line")
        def serialize_command_line(self, value: str, _info: object) -> str:
            """Serialize command line with safety checks for sensitive commands."""
            # Mask potentially sensitive command parts
            sensitive_patterns = ["password", "token", "secret", "key"]
            for pattern in sensitive_patterns:
                if pattern in value.lower():
                    return value.replace(pattern, "*" * len(pattern))
            return value

        @classmethod
        def validate_command_input(
            cls, data: FlextCliTypes.Data.CliCommandData | None
        ) -> FlextResult[FlextCliTypes.Data.CliCommandData | None]:
            """Validate and normalize command input data using railway pattern.

            Args:
                data: Command input data to validate

            Returns:
                FlextResult with validated and normalized data

            """
            # Extract command from data - ensure it's a string
            if not isinstance(data, dict):
                return FlextResult[FlextCliTypes.Data.CliCommandData | None].fail(
                    "Command data must be a dictionary"
                )

            command = data.pop("command")
            if not isinstance(command, str):
                return FlextResult[FlextCliTypes.Data.CliCommandData | None].fail(
                    "Command must be a string"
                )

            # Normalize command data
            normalized_data = {
                "command": command,
                "execution_time": data.get("execution_time"),
                **{k: v for k, v in data.items() if k != "command"},
            }

            return FlextResult[FlextCliTypes.Data.CliCommandData | None].ok(
                normalized_data
            )

        @override
        def __init__(self, **data: object) -> None:
            """Initialize CLI command with Pydantic validation.

            Args:
                **data: Command data including command_line, status, etc.

            """
            # Call parent Pydantic __init__ which handles all field validation
            # Pydantic will automatically convert types as needed
            super().__init__(**data)

        def validate_business_rules(self) -> FlextResult[None]:
            """Validate command business rules."""
            # Use mixin validation methods
            command_result = FlextCliMixins.ValidationMixin.validate_not_empty(
                "Command line", self.command_line
            )
            if not command_result.is_success:
                return command_result

            status_result = FlextCliMixins.ValidationMixin.validate_status(self.status)
            if not status_result.is_success:
                return status_result

            return FlextResult[None].ok(None)

        def start_execution(self) -> FlextResult[None]:
            """Start command execution."""
            state_result = (
                FlextCliMixins.BusinessRulesMixin.validate_command_execution_state(
                    self.status,
                    FlextCliConstants.CommandStatus.PENDING.value,
                    "start execution",
                )
            )
            if not state_result.is_success:
                return state_result

            self.status = FlextCliConstants.CommandStatus.RUNNING.value
            return FlextResult[None].ok(None)

        def complete_execution(
            self, exit_code: int, output: str = ""
        ) -> FlextResult[None]:
            """Complete command execution."""
            state_result = (
                FlextCliMixins.BusinessRulesMixin.validate_command_execution_state(
                    self.status,
                    FlextCliConstants.CommandStatus.RUNNING.value,
                    "complete execution",
                )
            )
            if not state_result.is_success:
                return state_result

            self.exit_code = exit_code
            self.output = output
            self.status = FlextCliConstants.CommandStatus.COMPLETED.value
            return FlextResult[None].ok(None)

    class DebugInfo(_BaseValidatedModel):
        """Debug information model extending _BaseValidatedModel."""

        service: str = Field(default="FlextCliDebug")
        status: str = Field(default="operational")
        timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
        system_info: dict[str, str] = Field(default_factory=dict)
        config_info: dict[str, str] = Field(default_factory=dict)
        level: str = Field(default="info")
        message: str = Field(default="")

        @computed_field
        def debug_summary(self) -> dict[str, object]:
            """Computed field for debug information summary."""
            return {
                "service": self.service,
                "level": self.level,
                "has_system_info": bool(self.system_info),
                "has_config_info": bool(self.config_info),
                "message_length": len(self.message),
                "age_seconds": (datetime.now(UTC) - self.timestamp).total_seconds(),
            }

        @model_validator(mode="after")
        def validate_debug_consistency(self) -> Self:
            """Validate debug info consistency."""
            valid_levels = {"debug", "info", "warning", "error", "critical"}
            if self.level not in valid_levels:
                msg = f"Invalid debug level: {self.level}"
                raise ValueError(msg)
            return self

        @field_serializer("system_info", "config_info")
        def serialize_sensitive_info(
            self, value: dict[str, str], _info: object
        ) -> dict[str, str]:
            """Serialize system/config info masking sensitive values."""
            sensitive_keys = {"password", "token", "secret", "key", "auth"}
            return {
                k: (
                    "***MASKED***"
                    if any(sens in k.lower() for sens in sensitive_keys)
                    else v
                )
                for k, v in value.items()
            }

        def validate_business_rules(self) -> FlextResult[None]:
            """Validate debug info business rules."""
            # Use mixin validation methods
            service_result = FlextCliMixins.ValidationMixin.validate_not_empty(
                "Service name", self.service
            )
            if not service_result.is_success:
                return service_result

            # Validate level
            valid_levels = ["debug", "info", "warning", "error", "critical"]
            level_result = FlextCliMixins.ValidationMixin.validate_enum_value(
                "level", self.level, valid_levels
            )
            if not level_result.is_success:
                return level_result

            return FlextResult[None].ok(None)

    class CliSession(
        FlextModels.Entity,
        FlextCliMixins.BusinessRulesMixin,
    ):
        """CLI session model extending FlextModels.Entity."""

        # id field inherited from FlextModels.Entity
        session_id: str = Field(
            default_factory=lambda: f"session_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S_%f')}"
        )
        start_time: str | None = Field(default=None)
        end_time: str | None = None
        last_activity: str | None = Field(default=None)
        duration_seconds: float = Field(default=0.0)
        commands_executed: int = Field(default=0)
        commands: list[FlextCliModels.CliCommand] = Field(default_factory=list)
        status: str = Field(default="active")
        user_id: str | None = None

        @computed_field
        def session_summary(self) -> dict[str, object]:
            """Computed field for session activity summary."""
            return {
                "session_id": self.session_id,
                "is_active": self.status == "active",
                "commands_count": len(self.commands),
                "duration_minutes": round(self.duration_seconds / 60, 2),
                "has_user": self.user_id is not None,
                "last_activity_age": self._calculate_activity_age(),
            }

        @computed_field
        def commands_by_status(self) -> dict[str, int]:
            """Computed field grouping commands by status."""
            status_counts: dict[str, int] = {}
            for command in self.commands:
                status = command.status
                status_counts[status] = status_counts.get(status, 0) + 1
            return status_counts

        @model_validator(mode="after")
        def validate_session_consistency(self) -> Self:
            """Cross-field validation for session consistency."""
            # Commands count should match actual commands list
            if self.commands_executed != len(self.commands):
                self.commands_executed = len(self.commands)

            # Duration should be non-negative
            if self.duration_seconds < 0:
                msg = "duration_seconds cannot be negative"
                raise ValueError(msg)

            return self

        @field_serializer("commands")
        def serialize_commands(
            self, value: list[FlextCliModels.CliCommand], _info: object
        ) -> list[dict[str, object]]:
            """Serialize commands with summary information."""
            return [
                {
                    "id": cmd.id,
                    "command_line": cmd.command_line,
                    "status": cmd.status,
                    "exit_code": cmd.exit_code,
                    "created_at": cmd.created_at.isoformat(),
                }
                for cmd in value
            ]

        def _calculate_activity_age(self) -> float | None:
            """Calculate time since last activity in seconds."""
            if not self.last_activity:
                return None
            try:
                last_time = datetime.fromisoformat(self.last_activity)
                return (datetime.now(UTC) - last_time).total_seconds()
            except (ValueError, AttributeError):
                return None

        @override
        def __init__(
            self,
            session_id: str | None = None,
            user_id: str | None = None,
            start_time: str | datetime | None = None,
            **data: object,
        ) -> None:
            """Initialize CLI session with proper type handling.

            Args:
                session_id: Unique session identifier (optional, auto-generated if None)
                user_id: User identifier
                start_time: Session start time
                **data: Additional session data

            """
            # Set session-specific fields
            if user_id is not None:
                data["user_id"] = user_id
            if start_time is not None:
                # Convert datetime to string if needed
                if isinstance(start_time, datetime):
                    data["start_time"] = start_time.isoformat()
                else:
                    data["start_time"] = start_time

            # Call parent constructor with proper data
            # Ensure required fields have correct types for parent class
            if "id" not in data:
                data["id"] = str(uuid.uuid4())
            if "version" not in data:
                data["version"] = 1
            if "created_at" not in data:
                data["created_at"] = datetime.now(UTC)
            if "updated_at" not in data:
                data["updated_at"] = None
            if "domain_events" not in data:
                data["domain_events"] = []

            # Create parent class with explicit parameters
            version_obj = data.get("version", 1)
            version_value: int = version_obj if isinstance(version_obj, int) else 1

            created_at_obj = data.get("created_at", datetime.now(UTC))
            created_at_value: datetime = (
                created_at_obj
                if isinstance(created_at_obj, datetime)
                else datetime.now(UTC)
            )

            updated_at_obj = data.get("updated_at")
            updated_at_value: datetime | None = (
                updated_at_obj if isinstance(updated_at_obj, datetime) else None
            )

            domain_events_obj = data.get("domain_events", [])
            domain_events_value: list[object] = (
                domain_events_obj if isinstance(domain_events_obj, list) else []
            )

            super().__init__(
                id=str(data.get("id", str(uuid.uuid4()))),
                version=version_value,
                created_at=created_at_value,
                updated_at=updated_at_value,
                domain_events=domain_events_value,
            )

            # Set session identifier (auto-generate if not provided)
            if session_id is not None:
                self.session_id = session_id

        def validate_business_rules(self) -> FlextResult[None]:
            """Validate session business rules."""
            # Use mixin validation methods
            session_id_result = FlextCliMixins.ValidationMixin.validate_not_empty(
                "Session ID", self.session_id
            )
            if not session_id_result.is_success:
                return session_id_result

            # Validate user_id if provided
            if self.user_id is not None and not self.user_id.strip():
                return FlextResult[None].fail("User ID cannot be empty")

            valid_statuses = ["active", "completed", "terminated"]
            status_result = FlextCliMixins.ValidationMixin.validate_enum_value(
                "status", self.status, valid_statuses
            )
            if not status_result.is_success:
                return status_result

            return FlextResult[None].ok(None)

        def add_command(self, command: FlextCliModels.CliCommand) -> FlextResult[None]:
            """Add a command to the session.

            Args:
                command: Command to add to the session

            Returns:
                FlextResult[None]: Success if command added, failure otherwise

            """
            try:
                # Add command to the commands list
                self.commands.append(command)

                # Update commands executed count
                self.commands_executed = len(self.commands)

                return FlextResult[None].ok(None)
            except Exception as e:
                return FlextResult[None].fail(f"Failed to add command to session: {e}")

    # REMOVED: Unused models CliFormatters and CliPipeline
    # These models were not used anywhere in the codebase

    # REMOVED: FlextCliConfig moved to config.py following FLEXT standards
    # Use: from flext_cli.config import FlextCliConfig

    class LoggingConfig(FlextModels.Configuration):
        """Logging configuration model - consolidated from scattered definition.

        This model extends FlextModels.Configuration for logging-specific settings
        while maintaining the consolidated [Project]Models pattern.
        """

        log_level: str = Field(default="INFO", description="Logging level")
        log_format: str = Field(
            default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            description="Log format string",
        )
        console_output: bool = Field(default=True, description="Enable console output")
        log_file: str | None = Field(default=None, description="Log file path")
        log_level_source: str = Field(
            default="default", description="Source of log level"
        )

        @computed_field
        def logging_summary(self) -> dict[str, object]:
            """Computed field for logging configuration summary."""
            return {
                "level": self.log_level,
                "console_enabled": self.console_output,
                "file_logging": self.log_file is not None,
                "format_length": len(self.log_format),
                "source": self.log_level_source,
            }

        @model_validator(mode="after")
        def validate_logging_config(self) -> Self:
            """Validate logging configuration consistency."""
            valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
            if self.log_level not in valid_levels:
                msg = f"Invalid log level: {self.log_level}"
                raise ValueError(msg)
            return self

        @field_serializer("log_file")
        def serialize_log_file(self, value: str | None, _info: object) -> str | None:
            """Serialize log file path with safety checks."""
            if value and "secret" in value.lower():
                return "***SENSITIVE_PATH***"
            return value

    # REMOVED: PipelineConfig, AdvancedServicePattern, ServiceOrchestrator,
    # CentralizedValidation, and AdvancedServiceOrchestrator classes.
    # These were over-engineered patterns not used anywhere in the codebase.
    # Total removed: ~1,016 lines of unused code


__all__ = [
    "FlextCliModels",
]
