"""FLEXT CLI Models - CLI domain models with Python 3.13 cutting-edge patterns.

Advanced Pydantic v2 implementation with discriminated unions, computed properties,
and type-safe state transitions following Domain-Driven Design principles.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Annotated, ClassVar, Self
from uuid import uuid4

from flext_core import FlextModels, FlextResult
from pydantic import (
    Discriminator,
    Field,
    computed_field,
    field_validator,
    model_validator,
)

from flext_cli.constants import FlextCliConstants
from flext_cli.typings import FlextCliTypes


class FlextCliModels:
    """CLI-specific models extending flext_core FlextModels."""

    Core: ClassVar[type[FlextModels]] = FlextModels

    class CliCommand(FlextModels.Entity):
        """Advanced CLI command model with discriminated union state management.

        Features:
            - Type-safe state transitions using Python 3.13 pattern matching
            - Discriminated unions for command states
            - Advanced computed properties with caching
            - Comprehensive validation with business rules
        """

        id: str = Field(default_factory=lambda: str(uuid4()))
        command_line: str | None = Field(None, description="Command to execute")
        execution_time: datetime = Field(default_factory=lambda: datetime.now(UTC))

        # Advanced discriminated union state management
        state: Annotated[
            FlextCliTypes.Commands.CommandState,
            Discriminator("status"),
        ] = Field(
            default_factory=FlextCliTypes.Commands.PendingState,
            description="Type-safe command state with discriminated union",
        )

        # Backward compatibility fields
        exit_code: int | None = None
        output: str = ""
        error_output: str = ""
        name: str | None = None  # Plugin compatibility
        entry_point: str | None = None  # Plugin compatibility
        plugin_version: str | None = None  # Plugin compatibility

        @property
        def status(self) -> str:
            """Get current status from discriminated union state."""
            return self.state.status

        @computed_field
        def is_successful(self) -> bool:
            """Advanced success determination with pattern matching."""
            match self.state:
                case FlextCliTypes.Commands.CompletedState(exit_code=0):
                    return True
                case FlextCliTypes.Commands.CompletedState():
                    return False
                case _:
                    return False

        # STATUS VALIDATION REMOVED: 'status' is a @property, not a field
        # Field validators can only validate actual fields, not computed properties
        # The status validation is handled by the discriminated union state system

        @field_validator("command_line")
        @classmethod
        def validate_command_line(cls, v: str | None) -> str | None:
            """Advanced command line validation with security checks."""
            if v is None:
                return None  # Allow None for plugin-type objects

            if not v.strip():
                msg = "Command line cannot be empty"
                raise ValueError(msg)

            # Security: Basic check for potentially dangerous commands
            dangerous_patterns = ["rm -rf", "format", "del /", "sudo rm"]
            command_lower = v.lower()
            if any(pattern in command_lower for pattern in dangerous_patterns):
                msg = "Potentially dangerous command detected"
                raise ValueError(msg)

            return v.strip()

        @model_validator(mode="after")
        def validate_command_state_consistency(self) -> FlextCliModels.CliCommand:
            """Advanced model validation ensuring state consistency across fields."""
            # Validate completed/failed commands have exit codes
            if (
                self.status
                in {FlextCliConstants.STATUS_COMPLETED, FlextCliConstants.STATUS_FAILED}
                and self.exit_code is None
            ):
                msg = f"Commands with status {self.status} must have an exit code"
                raise ValueError(msg)

            # Validate successful completion
            if (
                self.status == FlextCliConstants.STATUS_COMPLETED
                and self.exit_code != 0
            ):
                msg = "Completed commands should have exit code 0"
                raise ValueError(msg)

            # Validate failed commands have error output when exit code > 0
            if self.status == FlextCliConstants.STATUS_FAILED and self.exit_code == 0:
                msg = "Failed commands should have non-zero exit code"
                raise ValueError(msg)

            return self

        def start_execution(self) -> FlextResult[Self]:
            """Start execution with type-safe state transition using pattern matching."""
            match self.state:
                case FlextCliTypes.Commands.PendingState():
                    self.state = FlextCliTypes.Commands.RunningState(
                        started_at=datetime.now(UTC)
                    )
                    self.execution_time = datetime.now(UTC)
                    return FlextResult[Self].ok(self)
                case current_state:
                    return FlextResult[Self].fail(
                        f"Cannot start execution from state {current_state.status}. "
                        "Command must be in PENDING state."
                    )

        def complete_execution(
            self, exit_code: int, output: str = "", error_output: str = ""
        ) -> FlextResult[Self]:
            """Complete execution with advanced state transition and pattern matching."""
            match self.state:
                case FlextCliTypes.Commands.RunningState():
                    # Set backward compatibility fields first
                    self.exit_code = exit_code
                    self.output = output
                    self.error_output = error_output

                    # Type-safe state transition based on exit code
                    if exit_code == 0:
                        self.state = FlextCliTypes.Commands.CompletedState(
                            completed_at=datetime.now(UTC),
                            exit_code=exit_code,
                            output=output,
                        )
                    else:
                        self.state = FlextCliTypes.Commands.FailedState(
                            failed_at=datetime.now(UTC),
                            exit_code=exit_code,
                            error_output=error_output,
                        )
                    return FlextResult[Self].ok(self)
                case current_state:
                    return FlextResult[Self].fail(
                        f"Cannot complete execution from state {current_state.status}. "
                        "Command must be in RUNNING state."
                    )

        def validate_business_rules(self) -> FlextResult[None]:
            """Advanced business rule validation using Python 3.13 pattern matching."""
            # Basic validation
            if self.command_line and not self.command_line.strip():
                return FlextResult[None].fail("Command line cannot be empty")

            # Simplified state validation to avoid unreachable code issues
            # Basic validation based on state type names

            state_name = type(self.state).__name__

            # Check for basic state validation rules
            if "Pending" in state_name and self.exit_code is not None:
                return FlextResult[None].fail(
                    "Pending commands should not have exit codes"
                )
            if "Running" in state_name and self.exit_code is not None:
                return FlextResult[None].fail(
                    "Running commands should not have exit codes until completion"
                )

            # Check exit code requirements for completed/failed states
            if hasattr(self.state, "exit_code"):
                exit_code = getattr(self.state, "exit_code", None)
                if "Completed" in state_name and exit_code is None:
                    return FlextResult[None].fail(
                        "Completed commands must have exit codes"
                    )
                if "Failed" in state_name and (exit_code is None or exit_code == 0):
                    return FlextResult[None].fail(
                        "Failed commands must have non-zero exit codes"
                    )

            # If we reach here, validation passed
            return FlextResult[None].ok(None)

    class CliSession(FlextModels.Entity):
        """CLI session model."""

        id: str = Field(default_factory=lambda: str(uuid4()))
        session_id: str = Field(default_factory=lambda: str(uuid4()))
        start_time: datetime = Field(default_factory=lambda: datetime.now(UTC))
        end_time: datetime | None = None
        commands: list[FlextCliModels.CliCommand] = Field(default_factory=list)
        user_id: str | None = None

        @computed_field
        def duration_seconds(self) -> float | None:
            if self.end_time is None:
                return None
            return (self.end_time - self.start_time).total_seconds()

        def add_command(self, command: FlextCliModels.CliCommand) -> FlextResult[None]:
            """Add a command to the session."""
            self.commands.append(command)
            return FlextResult[None].ok(None)

        def end_session(self) -> FlextResult[None]:
            """End the session."""
            self.end_time = datetime.now(UTC)
            return FlextResult[None].ok(None)

        def validate_business_rules(self) -> FlextResult[None]:
            if self.end_time is not None and self.end_time < self.start_time:
                return FlextResult[None].fail("End time cannot be before start time")
            if len(self.commands) > FlextCliConstants.LIMITS.max_commands_per_session:
                return FlextResult[None].fail(
                    f"Session has too many commands (limit: {FlextCliConstants.LIMITS.max_commands_per_session})"
                )
            for cmd in self.commands:
                validation_result = cmd.validate_business_rules()
                if validation_result.is_failure:
                    return FlextResult[None].fail(
                        f"Invalid command in session: {validation_result.error}"
                    )
            return FlextResult[None].ok(None)

    class CliConfig(FlextModels.Entity):
        """CLI configuration model."""

        id: str = Field(default_factory=lambda: str(uuid4()))
        profile: str = Field(default=FlextCliConstants.ProfileName.DEFAULT)
        output_format: str = Field(
            default=FlextCliConstants.OUTPUT.default_output_format
        )
        debug_mode: bool = Field(default=False)
        timeout_seconds: int = Field(
            default=FlextCliConstants.TIMEOUTS.default_command_timeout
        )

        @field_validator("output_format")
        @classmethod
        def validate_output_format(cls, v: str) -> str:
            if v not in FlextCliConstants.VALID_OUTPUT_FORMATS:
                msg = f"Output format must be one of: {FlextCliConstants.VALID_OUTPUT_FORMATS}"
                raise ValueError(msg)
            return v

        @field_validator("timeout_seconds")
        @classmethod
        def validate_timeout(cls, v: int) -> int:
            if v <= 0 or v > FlextCliConstants.LIMITS.max_timeout_seconds:
                msg = f"Timeout must be between 1 and {FlextCliConstants.LIMITS.max_timeout_seconds} seconds"
                raise ValueError(msg)
            return v

        def validate_business_rules(self) -> FlextResult[None]:
            """Validate business rules for configuration."""
            try:
                # All validation is done through Pydantic validators
                return FlextResult[None].ok(None)
            except Exception as e:
                return FlextResult[None].fail(f"Configuration validation failed: {e}")

    class CliPlugin(FlextModels.Entity):
        """CLI plugin model."""

        id: str = Field(default_factory=lambda: str(uuid4()))
        name: str = Field(...)
        entry_point: str = Field(...)
        plugin_version: str = Field(default="1.0.0")
        description: str | None = None

        @field_validator("name")
        @classmethod
        def validate_name(cls, v: str) -> str:
            if not v or not v.strip():
                msg = "Plugin name cannot be empty"
                raise ValueError(msg)
            return v.strip()

        @field_validator("entry_point")
        @classmethod
        def validate_entry_point(cls, v: str) -> str:
            if not v or not v.strip():
                msg = "Plugin entry point cannot be empty"
                raise ValueError(msg)
            # Basic validation for entry point format (module:function)
            if ":" not in v:
                msg = "Entry point must be in format 'module:function'"
                raise ValueError(msg)
            return v.strip()

        def validate_business_rules(self) -> FlextResult[None]:
            """Validate plugin business rules."""
            if not self.name.strip():
                return FlextResult[None].fail("Plugin name cannot be empty")
            if not self.entry_point.strip():
                return FlextResult[None].fail("Plugin entry point cannot be empty")
            return FlextResult[None].ok(None)


__all__ = ["FlextCliModels"]
