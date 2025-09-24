"""FLEXT CLI Models - Single unified class following FLEXT standards.

Provides CLI-specific Pydantic models using flext-core standardization.
Single FlextCliModels class with nested model subclasses following FLEXT pattern.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel, Field

from flext_cli.constants import FlextCliConstants
from flext_cli.mixins import FlextCliMixins
from flext_core import FlextModels, FlextResult


class FlextCliModels(FlextModels):
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

    # Base classes for common functionality
    class _BaseEntity(BaseModel, FlextCliMixins.ValidationMixin):
        """Base entity with common fields for entities with id, timestamps, and status."""

        id: str = Field(
            default_factory=lambda: f"entity_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S_%f')}"
        )
        created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
        updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
        status: str = Field(default=FlextCliConstants.CommandStatus.PENDING.value)

        def update_timestamp(self) -> None:
            """Update the updated_at timestamp."""
            self.updated_at = datetime.now(UTC)

    class _BaseValidatedModel(BaseModel, FlextCliMixins.ValidationMixin):
        """Base model with common validation patterns."""

    class _BaseConfig(_BaseValidatedModel):
        """Base configuration model with common config validation patterns."""

    class CliCommand(_BaseEntity, FlextCliMixins.BusinessRulesMixin):
        """CLI command model extending _BaseEntity."""

        command: str = Field(min_length=1)
        args: list[str] = Field(default_factory=list)
        exit_code: int | None = None
        output: str = Field(default="")
        error_output: str = Field(default="")
        name: str = Field(default="")
        entry_point: str = Field(default="")
        plugin_version: str = Field(default="1.0.0")

        def __init__(
            self,
            command_line: str | None = None,
            execution_time: datetime | None = None,
            name: str | None = None,
            entry_point: str | None = None,
            plugin_version: str | None = None,
            **data: object,
        ) -> None:
            """Initialize with compatibility for command_line and execution_time parameters."""
            if command_line is not None:
                data["command"] = command_line
            if execution_time is not None:
                data["created_at"] = execution_time
            if name is not None:
                data["name"] = name
            if entry_point is not None:
                data["entry_point"] = entry_point
            if plugin_version is not None:
                data["plugin_version"] = plugin_version
            super().__init__(**data)  # type: ignore[arg-type]

        @property
        def command_line(self) -> str:
            """Compatibility property for command_line access."""
            return self.command

        @property
        def execution_time(self) -> datetime:
            """Compatibility property for execution_time access."""
            return self.created_at

        def validate_business_rules(self) -> FlextResult[None]:
            """Validate command business rules."""
            # Use mixin validation methods
            command_result = FlextCliMixins.ValidationMixin.validate_not_empty(
                "Command line", self.command
            )
            if command_result.is_failure:
                return command_result

            status_result = FlextCliMixins.ValidationMixin.validate_status(self.status)
            if status_result.is_failure:
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
            if state_result.is_failure:
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
            if state_result.is_failure:
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

        def validate_business_rules(self) -> FlextResult[None]:
            """Validate debug info business rules."""
            # Use mixin validation methods
            service_result = FlextCliMixins.ValidationMixin.validate_not_empty(
                "Service name", self.service
            )
            if service_result.is_failure:
                return service_result

            return FlextResult[None].ok(None)

    class FormatOptions(BaseModel):
        """Format options for CLI output extending BaseModel."""

        title: str | None = None
        headers: list[str] | None = None
        show_lines: bool = True
        max_width: int | None = None

    class CliSession(
        _BaseValidatedModel,
        FlextCliMixins.BusinessRulesMixin,
    ):
        """CLI session model extending _BaseValidatedModel."""

        id: str = Field(
            default_factory=lambda: f"session_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}"
        )
        session_id: str = Field(
            default_factory=lambda: f"session_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}"
        )
        start_time: datetime = Field(default_factory=lambda: datetime.now(UTC))
        end_time: datetime | None = None
        last_activity: datetime = Field(default_factory=lambda: datetime.now(UTC))
        duration_seconds: float = Field(default=0.0)
        commands_executed: int = Field(default=0)
        commands: list[FlextCliModels.CliCommand] = Field(default_factory=list)
        status: str = Field(default="active")
        user_id: str | None = None

        def __init__(
            self,
            session_id: str | None = None,
            user_id: str | None = None,
            start_time: datetime | None = None,
            **data: object,
        ) -> None:
            """Initialize with compatibility for session_id, user_id, and start_time parameters."""
            if session_id is not None:
                data["id"] = session_id
                data["session_id"] = session_id
            if start_time is not None:
                data["start_time"] = start_time
            if user_id is not None:
                data["user_id"] = user_id
            super().__init__(**data)

        def validate_business_rules(self) -> FlextResult[None]:
            """Validate session business rules."""
            # Use mixin validation methods
            id_result = FlextCliMixins.ValidationMixin.validate_not_empty(
                "Session ID", self.id
            )
            if id_result.is_failure:
                return id_result

            valid_statuses = ["active", "completed", "terminated"]
            status_result = FlextCliMixins.ValidationMixin.validate_enum_value(
                "status", self.status, valid_statuses
            )
            if status_result.is_failure:
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

    class CliFormatters(BaseModel):
        """CLI formatters model extending BaseModel."""

        def list_formats(self) -> list[str]:
            """List available output formats."""
            return ["json", "yaml", "csv", "table", "plain"]

    class CliPipeline(_BaseEntity, FlextCliMixins.BusinessRulesMixin):
        """CLI Pipeline model extending _BaseEntity."""

        name: str = Field(min_length=1)
        description: str = Field(default="")
        steps: list[dict[str, object]] = Field(default_factory=list)
        config: dict[str, object] = Field(default_factory=dict)

        def validate_business_rules(self) -> FlextResult[None]:
            """Validate pipeline business rules."""
            # Use mixin validation methods
            name_result = FlextCliMixins.ValidationMixin.validate_not_empty(
                "Pipeline name", self.name
            )
            if name_result.is_failure:
                return name_result

            status_result = FlextCliMixins.ValidationMixin.validate_status(self.status)
            if status_result.is_failure:
                return status_result

            return FlextResult[None].ok(None)

        def add_step(self, step: dict[str, object]) -> FlextResult[None]:
            """Add a step to the pipeline."""
            step_result = FlextCliMixins.BusinessRulesMixin.validate_pipeline_step(step)
            if step_result.is_failure:
                return step_result

            self.steps.append(step)
            self.update_timestamp()  # Use inherited method
            return FlextResult[None].ok(None)

        def update_status(self, new_status: str) -> FlextResult[None]:
            """Update pipeline status."""
            status_result = FlextCliMixins.ValidationMixin.validate_status(new_status)
            if status_result.is_failure:
                return status_result

            self.status = new_status
            self.update_timestamp()  # Use inherited method
            return FlextResult[None].ok(None)

    class PipelineConfig(
        _BaseValidatedModel,
        FlextCliMixins.BusinessRulesMixin,
    ):
        """Pipeline configuration model extending _BaseValidatedModel."""

        name: str = Field(min_length=1)
        description: str = Field(default="")
        steps: list[dict[str, object]] = Field(default_factory=list)
        config: dict[str, object] = Field(default_factory=dict)
        enabled: bool = Field(default=True)
        timeout_seconds: int = Field(default=300)
        retry_count: int = Field(default=3)

        def validate_business_rules(self) -> FlextResult[None]:
            """Validate pipeline configuration business rules."""
            # Use mixin validation methods
            name_result = FlextCliMixins.ValidationMixin.validate_not_empty(
                "Pipeline name", self.name
            )
            if name_result.is_failure:
                return name_result

            timeout_result = FlextCliMixins.ValidationMixin.validate_positive_number(
                "Timeout", self.timeout_seconds
            )
            if timeout_result.is_failure:
                return timeout_result

            retry_result = FlextCliMixins.ValidationMixin.validate_non_negative_number(
                "Retry count", self.retry_count
            )
            if retry_result.is_failure:
                return retry_result

            return FlextResult[None].ok(None)

        def add_step(self, step: dict[str, object]) -> FlextResult[None]:
            """Add a step to the pipeline configuration."""
            step_result = FlextCliMixins.BusinessRulesMixin.validate_pipeline_step(step)
            if step_result.is_failure:
                return step_result

            self.steps.append(step)
            return FlextResult[None].ok(None)

    # =========================================================================
    # CENTRALIZED VALIDATION ARCHITECTURE
    # =========================================================================


__all__ = [
    "FlextCliModels",
]
