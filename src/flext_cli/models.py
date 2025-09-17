"""FLEXT CLI Models - CLI domain models with Python 3.13 cutting-edge patterns.

Advanced Pydantic v2 implementation with discriminated unions, computed properties,
and type-safe state transitions following Domain-Driven Design principles.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Annotated, ClassVar, Literal

from pydantic import (
    Discriminator,
    Field,
    computed_field,
    field_validator,
    model_validator,
)

from flext_cli.constants import FlextCliConstants
from flext_cli.utils import FlextCliUtilities
from flext_core import FlextModels, FlextResult


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

        model_config = FlextCliUtilities.get_base_config_dict()

        id: str = Field(default_factory=FlextCliUtilities.generate_uuid)
        command_line: str | None = Field(default=None, description="Command to execute")
        execution_time: datetime = Field(default_factory=lambda: datetime.now(UTC))

        # Advanced discriminated union state management using unified models
        state: Annotated[
            FlextCliModels.PendingState
            | FlextCliModels.RunningState
            | FlextCliModels.CompletedState
            | FlextCliModels.FailedState,
            Discriminator("status"),
        ] = Field(
            default_factory=lambda: FlextCliModels.PendingState(
                queued_at=datetime.now(UTC)
            ),
            description="Type-safe command state with discriminated union",
        )

        # Command execution result fields
        exit_code: int | None = None
        output: str = ""
        error_output: str = ""
        name: str | None = None  # Plugin name field
        entry_point: str | None = None  # Plugin entry point
        plugin_version: str | None = None  # Plugin version

        @property
        def status(self) -> str:
            """Get current status from discriminated union state."""
            return self.state.status

        @computed_field
        def is_successful(self) -> bool:
            """Advanced success determination with pattern matching."""
            match self.state:
                case FlextCliModels.CompletedState(exit_code=0):
                    return True
                case FlextCliModels.CompletedState():
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
                in {
                    FlextCliConstants.CommandStatus.COMPLETED,
                    FlextCliConstants.CommandStatus.FAILED,
                }
                and self.exit_code is None
            ):
                msg = f"Commands with status {self.status} must have an exit code"
                raise ValueError(msg)

            # Validate successful completion
            if (
                self.status == FlextCliConstants.CommandStatus.COMPLETED
                and self.exit_code != 0
            ):
                msg = "Completed commands should have exit code 0"
                raise ValueError(msg)

            # Validate failed commands have error output when exit code > 0
            if (
                self.status == FlextCliConstants.CommandStatus.FAILED
                and self.exit_code == 0
            ):
                msg = "Failed commands should have non-zero exit code"
                raise ValueError(msg)

            return self

        def start_execution(self) -> FlextResult[None]:
            """Start execution with type-safe state transition using pattern matching."""
            match self.state:
                case FlextCliModels.PendingState():
                    self.state = FlextCliModels.RunningState(
                        started_at=datetime.now(UTC),
                    )
                    self.execution_time = datetime.now(UTC)
                    return FlextResult[None].ok(None)
                case current_state:
                    return FlextResult[None].fail(
                        f"Cannot start execution from state {current_state.status}. "
                        "Command must be in PENDING state.",
                    )

        def complete_execution(
            self,
            exit_code: int,
            output: str = "",
            error_output: str = "",
        ) -> FlextResult[None]:
            """Complete execution with advanced state transition and pattern matching."""
            match self.state:
                case FlextCliModels.RunningState():
                    # Set command execution result fields
                    self.exit_code = exit_code
                    self.output = output
                    self.error_output = error_output

                    if exit_code == 0:
                        self.state = FlextCliModels.CompletedState(
                            completed_at=datetime.now(UTC),
                            exit_code=exit_code,
                            output=output,
                        )
                    else:
                        self.state = FlextCliModels.FailedState(
                            failed_at=datetime.now(UTC),
                            exit_code=exit_code,
                            error_output=error_output,
                        )
                    return FlextResult[None].ok(None)
                case current_state:
                    return FlextResult[None].fail(
                        f"Cannot complete execution from state {current_state.status}. "
                        "Command must be in RUNNING state.",
                    )

        def validate_business_rules(self) -> FlextResult[None]:
            """Advanced business rule validation using Python 3.13 pattern matching."""
            # Basic validation
            if self.command_line and not self.command_line.strip():
                return FlextResult[None].fail("Command line cannot be empty")

            # Advanced pattern matching validation with Python 3.13+ syntax
            match self.state:
                case FlextCliModels.PendingState() if self.exit_code is not None:
                    return FlextResult[None].fail(
                        "Pending commands should not have exit codes"
                    )
                case FlextCliModels.RunningState() if self.exit_code is not None:
                    return FlextResult[None].fail(
                        "Running commands should not have exit codes until completion"
                    )
                case FlextCliModels.FailedState(exit_code=exit_code) if (
                    exit_code is None or exit_code == 0
                ):
                    return FlextResult[None].fail(
                        "Failed commands must have non-zero exit codes"
                    )
                case _:
                    # All validation rules passed
                    pass

            return FlextResult[None].ok(None)

    class CliSession(FlextModels.Entity):
        """CLI session model."""

        id: str = Field(default_factory=FlextCliUtilities.generate_uuid)
        session_id: str = Field(default_factory=FlextCliUtilities.generate_uuid)
        start_time: datetime = Field(default_factory=lambda: datetime.now(UTC))
        end_time: datetime | None = None
        commands: list[FlextCliModels.CliCommand] = Field(default_factory=list)
        user_id: str | None = None

        @computed_field
        def duration_seconds(self) -> float | None:
            """Calculate session duration in seconds."""
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
            """Validate session business rules."""
            if self.end_time is not None and self.end_time < self.start_time:
                return FlextResult[None].fail("End time cannot be before start time")
            if len(self.commands) > FlextCliConstants.LIMITS.max_commands_per_session:
                return FlextResult[None].fail(
                    f"Session has too many commands (limit: {FlextCliConstants.LIMITS.max_commands_per_session})",
                )
            for cmd in self.commands:
                validation_result = cmd.validate_business_rules()
                if validation_result.is_failure:
                    return FlextResult[None].fail(
                        f"Invalid command in session: {validation_result.error}",
                    )
            return FlextResult[None].ok(None)

    class CliConfig(FlextModels.Entity):
        """CLI configuration model."""

        id: str = Field(default_factory=FlextCliUtilities.generate_uuid)
        profile: str = Field(default=FlextCliConstants.ProfileName.DEFAULT)
        output_format: str = Field(
            default=FlextCliConstants.OUTPUT.default_output_format, frozen=True
        )
        debug_mode: bool = Field(default=False)
        timeout_seconds: int = Field(
            default=FlextCliConstants.TIMEOUTS.default_command_timeout, ge=1
        )

        @field_validator("output_format")
        @classmethod
        def validate_output_format(cls, v: str) -> str:
            """Validate output format is supported."""
            if v not in FlextCliConstants.VALID_OUTPUT_FORMATS:
                msg = f"Output format must be one of: {FlextCliConstants.VALID_OUTPUT_FORMATS}"
                raise ValueError(msg)
            return v

        @field_validator("timeout_seconds")
        @classmethod
        def validate_timeout(cls, v: int) -> int:
            """Validate timeout is within limits."""
            if v <= 0 or v > FlextCliConstants.LIMITS.max_timeout_seconds:
                msg = f"Timeout must be between 1 and {FlextCliConstants.LIMITS.max_timeout_seconds} seconds"
                raise ValueError(msg)
            return v

        def validate_business_rules(self) -> FlextResult[None]:
            """Validate business rules for configuration."""
            try:
                # All validation is done through Pydantic validators
                return FlextResult[None].ok(None)
            except (ImportError, AttributeError, ValueError) as e:
                return FlextResult[None].fail(f"Configuration validation failed: {e}")

    class CliPlugin(FlextModels.Entity):
        """CLI plugin model."""

        id: str = Field(default_factory=FlextCliUtilities.generate_uuid)
        name: str = Field(min_length=1)
        plugin_version: str = Field(default="0.1.0")
        entry_point: str = Field(min_length=1)
        enabled: bool = Field(default=True)
        config: dict[str, object] = Field(default_factory=FlextCliUtilities.empty_dict)
        metadata: dict[str, object] = Field(
            default_factory=FlextCliUtilities.empty_dict
        )

        @field_validator("name")
        @classmethod
        def validate_name(cls, v: str) -> str:
            """Validate plugin name."""
            if not v.strip():
                msg = "Plugin name cannot be empty"
                raise ValueError(msg)
            return v.strip()

        def validate_business_rules(self) -> FlextResult[None]:
            """Validate plugin business rules."""
            if not self.name or not self.name.strip():
                return FlextResult[None].fail("Plugin must have a name")
            if not self.entry_point or not self.entry_point.strip():
                return FlextResult[None].fail("Plugin must have an entry point")
            return FlextResult[None].ok(None)

    # Discriminated union state models for type-safe command states
    class PendingState(FlextModels.Entity):
        """Pending command state."""

        status: Literal["PENDING"] = Field(default="PENDING", frozen=True)
        queued_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    class RunningState(FlextModels.Entity):
        """Running command state."""

        status: Literal["RUNNING"] = Field(default="RUNNING", frozen=True)
        started_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    class CompletedState(FlextModels.Entity):
        """Completed command state."""

        status: Literal["COMPLETED"] = Field(default="COMPLETED", frozen=True)
        completed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
        exit_code: int = Field(default=0)
        output: str = Field(default="")

    class FailedState(FlextModels.Entity):
        """Failed command state."""

        status: Literal["FAILED"] = Field(default="FAILED", frozen=True)
        failed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
        exit_code: int = Field(gt=0)
        error_output: str = Field(default="")

    # Pipeline model for complex command orchestration
    class Pipeline(FlextModels.Entity):
        """Pipeline model for CLI operations with proper Entity inheritance."""

        name: str = Field(..., description="Pipeline name")
        description: str = Field(default="", description="Pipeline description")
        status: str = Field(default="inactive", description="Pipeline status")
        config: dict[str, object] = Field(default_factory=dict, description="Pipeline configuration")

        # Entity fields are inherited: id, created_at, updated_at (all required datetime)

    # Pipeline state models
    class PipelinePendingState(FlextModels.Entity):
        """Pending pipeline state."""

        status: Literal["PENDING"] = Field(default="PENDING", frozen=True)
        created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    class PipelineRunningState(FlextModels.Entity):
        """Running pipeline state."""

        status: Literal["RUNNING"] = Field(default="RUNNING", frozen=True)
        started_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
        current_command_index: int = Field(default=0, ge=0)

    class PipelineCompletedState(FlextModels.Entity):
        """Completed pipeline state."""

        status: Literal["COMPLETED"] = Field(default="COMPLETED", frozen=True)
        completed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
        success_rate: float = Field(default=0.0, ge=0.0, le=100.0)

    class PipelineFailedState(FlextModels.Entity):
        """Failed pipeline state."""

        status: Literal["FAILED"] = Field(default="FAILED", frozen=True)
        failed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
        failure_reason: str = Field(default="Unknown failure")
        failed_command_index: int | None = Field(default=None, ge=0)

    # Additional API models for CLI operations
    class ApiState(FlextModels.Entity):
        """API connection and authentication state model with session tracking."""

        model_config = FlextCliUtilities.get_base_config_dict()

        id: str = Field(default_factory=FlextCliUtilities.generate_uuid)
        base_url: str = Field(default="http://localhost:8000", min_length=1)
        authenticated: bool = Field(default=False)
        token: str | None = Field(default=None)
        refresh_token: str | None = Field(default=None)
        expires_at: datetime | None = None
        last_request_at: datetime | None = None
        request_count: int = Field(default=0, ge=0)
        error_count: int = Field(default=0, ge=0)

        # Additional fields required by api.py and tests
        service_name: str = Field(
            default="flext-cli", description="Service name for API state"
        )
        enable_session_tracking: bool = Field(
            default=True, description="Enable session tracking"
        )
        enable_command_history: bool = Field(
            default=True, description="Enable command history"
        )
        command_history: list[FlextCliModels.CliCommand] = Field(default_factory=list)
        sessions: dict[str, FlextCliModels.CliSession] = Field(default_factory=dict)

        # Fields required by tests
        handlers: dict[str, object] = Field(
            default_factory=dict, description="Registered command handlers"
        )
        plugins: dict[str, object] = Field(
            default_factory=dict, description="Registered plugins"
        )

        @field_validator("base_url")
        @classmethod
        def validate_base_url(cls, v: str) -> str:
            """Validate API base URL."""
            if not v.strip():
                msg = "Base URL cannot be empty"
                raise ValueError(msg)

            # Basic URL validation
            if not (v.startswith(("http://", "https://"))):
                msg = "Base URL must start with http:// or https://"
                raise ValueError(msg)

            return v.strip()

        @computed_field
        def session_count(self) -> int:
            """Number of active sessions."""
            return len(self.sessions)

        @computed_field
        def handler_count(self) -> int:
            """Number of registered handlers."""
            return len(self.handlers)

        @computed_field
        def is_token_expired(self) -> bool:
            """Check if token is expired."""
            if self.expires_at is None:
                return False
            return datetime.now(UTC) > self.expires_at

        @computed_field
        def error_rate(self) -> float:
            """Calculate error rate as percentage."""
            if self.request_count == 0:
                return 0.0
            return (self.error_count / self.request_count) * 100

        def record_request(self, *, success: bool = True) -> FlextResult[None]:
            """Record API request for metrics."""
            self.last_request_at = datetime.now(UTC)
            self.request_count += 1
            if not success:
                self.error_count += 1
            return FlextResult[None].ok(None)

        def authenticate(
            self,
            token: str,
            refresh_token: str | None = None,
            expires_in: int | None = None,
        ) -> FlextResult[None]:
            """Set authentication state."""
            self.token = token
            self.refresh_token = refresh_token
            self.authenticated = True

            if expires_in:
                self.expires_at = datetime.now(UTC) + timedelta(seconds=expires_in)

            return FlextResult[None].ok(None)

        def clear_authentication(self) -> FlextResult[None]:
            """Clear authentication state."""
            self.token = None
            self.refresh_token = None
            self.authenticated = False
            self.expires_at = None
            return FlextResult[None].ok(None)

        def validate_business_rules(self) -> FlextResult[None]:
            """Validate API state business rules."""
            if not self.base_url:
                return FlextResult[None].fail("API state must have a base URL")

            if self.authenticated and not self.token:
                return FlextResult[None].fail("Authenticated state must have a token")

            # Calculate error rate manually to avoid computed field issues
            if self.request_count == 0:
                calculated_error_rate = 0.0
            else:
                calculated_error_rate = (self.error_count / self.request_count) * 100

            if calculated_error_rate > FlextCliConstants.LIMITS.max_error_rate_percent:
                return FlextResult[None].fail(
                    f"Error rate too high: {calculated_error_rate:.1f}%"
                )

            return FlextResult[None].ok(None)

    # Additional models for API operations
    class PipelineList(FlextModels.Entity):
        """List of pipelines with pagination support."""

        model_config = FlextCliUtilities.get_base_config_dict()

        pipelines: list[FlextCliModels.Pipeline] = Field(default_factory=list)
        total: int = Field(default=0, ge=0, description="Total number of pipelines")
        page: int = Field(default=1, ge=1, description="Current page number")
        page_size: int = Field(default=10, ge=1, le=100, description="Number of items per page")
        has_next: bool = Field(default=False)
        has_previous: bool = Field(default=False)

        @computed_field
        def total_pages(self) -> int:
            """Calculate total number of pages."""
            if self.page_size == 0:
                return 0
            return (self.total + self.page_size - 1) // self.page_size

        def validate_business_rules(self) -> FlextResult[None]:
            """Validate pipeline list business rules."""
            if self.page_size <= 0:
                return FlextResult[None].fail("page_size must be positive")

            if self.page <= 0:
                return FlextResult[None].fail("page must be positive")

            if len(self.pipelines) > self.page_size:
                return FlextResult[None].fail("Too many pipelines for page size")

            return FlextResult[None].ok(None)

    class PipelineConfig(FlextModels.Entity):
        """Configuration for pipeline execution."""

        model_config = FlextCliUtilities.get_base_config_dict()

        id: str = Field(default_factory=FlextCliUtilities.generate_uuid)
        name: str = Field(min_length=1)
        description: str = Field(default="")
        timeout_seconds: int = Field(
            default=FlextCliConstants.TIMEOUTS.default_command_timeout, ge=1
        )
        max_retries: int = Field(default=3, ge=0, le=10)
        parallel_execution: bool = Field(default=False)
        fail_fast: bool = Field(default=True)
        environment: dict[str, str] = Field(default_factory=dict)
        tags: list[str] = Field(default_factory=list)

        # Additional fields required by tests for Meltano pipeline compatibility
        tap: str | None = Field(default=None, description="Tap (extractor) name")
        target: str | None = Field(default=None, description="Target (loader) name")
        schedule: str | None = Field(default=None, description="Schedule expression")
        transform: str | None = Field(default=None, description="Transform name")
        state: str | None = Field(default=None, description="State backend")
        config: dict[str, object] | None = Field(default=None, description="Additional configuration")

        @field_validator("timeout_seconds")
        @classmethod
        def validate_timeout(cls, v: int) -> int:
            """Validate timeout is within limits."""
            if v <= 0 or v > FlextCliConstants.LIMITS.max_timeout_seconds:
                msg = f"Timeout must be between 1 and {FlextCliConstants.LIMITS.max_timeout_seconds} seconds"
                raise ValueError(msg)
            return v

        def validate_business_rules(self) -> FlextResult[None]:
            """Validate pipeline config business rules."""
            if not self.name or not self.name.strip():
                return FlextResult[None].fail("Pipeline config must have a name")

            if self.max_retries < 0:
                return FlextResult[None].fail("max_retries cannot be negative")

            return FlextResult[None].ok(None)

    # API Response models for centralizing validation
    class ApiJsonResponse(FlextModels.Entity):
        """Generic API JSON response model with automatic validation."""

        model_config = FlextCliUtilities.get_base_config_dict()

        data: dict[str, object] = Field(default_factory=dict)
        status: str = Field(default="success")
        message: str = Field(default="")

        def validate_business_rules(self) -> FlextResult[None]:
            """Validate API response business rules."""
            # Type validation handled by Pydantic - data is guaranteed to be dict
            return FlextResult[None].ok(None)

    class ApiListResponse(FlextModels.Entity):
        """Generic API list response model with automatic validation."""

        model_config = FlextCliUtilities.get_base_config_dict()

        data: list[dict[str, object]] = Field(default_factory=list)
        status: str = Field(default="success")
        message: str = Field(default="")

        def validate_business_rules(self) -> FlextResult[None]:
            """Validate API list response business rules."""
            # Type validation handled by Pydantic - data is guaranteed to be list[dict[str, object]]
            return FlextResult[None].ok(None)

    class StringListResponse(FlextModels.Entity):
        """String list response model with automatic validation."""

        model_config = FlextCliUtilities.get_base_config_dict()

        logs: list[str] = Field(default_factory=list)

        @field_validator("logs")
        @classmethod
        def validate_logs_are_strings(cls, v: list[str]) -> list[str]:
            """Validate all items are strings."""
            # Type validation handled by Pydantic type system - v is guaranteed to be list[str]
            return v

        def validate_business_rules(self) -> FlextResult[None]:
            """Validate string list response business rules."""
            return FlextResult[None].ok(None)

    class PluginListResponse(FlextModels.Entity):
        """Plugin list response model with automatic validation."""

        model_config = FlextCliUtilities.get_base_config_dict()

        plugins: list[dict[str, object]] = Field(default_factory=list)

        @field_validator("plugins")
        @classmethod
        def validate_plugins_are_dicts(
            cls, v: list[dict[str, object]]
        ) -> list[dict[str, object]]:
            """Validate all items are dictionaries."""
            # Type validation handled by Pydantic type system - v is guaranteed to be list[dict[str, object]]
            return v

        def validate_business_rules(self) -> FlextResult[None]:
            """Validate plugin list response business rules."""
            return FlextResult[None].ok(None)

    # Data validation models for formatter operations
    class FormatterDataInput(FlextModels.Entity):
        """Centralized data validation for formatter operations."""

        model_config = FlextCliUtilities.get_base_config_dict()

        data: dict[str, object] | list[dict[str, object]] | list[object] | object = (
            Field(description="Data to be formatted - supports various types")
        )

        @field_validator("data")
        @classmethod
        def validate_data_structure(cls, v: object) -> object:
            """Validate data structure is suitable for formatting."""
            # Allow any data type but ensure it's not None
            if v is None:
                msg = "Data cannot be None for formatting operations"
                raise ValueError(msg)
            return v

        def validate_business_rules(self) -> FlextResult[None]:
            """Validate data formatting business rules."""
            if self.data is None:
                return FlextResult[None].fail("Data cannot be None")
            return FlextResult[None].ok(None)

    class TableFormatterData(FlextModels.Entity):
        """Specific validation for table formatting data."""

        model_config = FlextCliUtilities.get_base_config_dict()

        data: dict[str, object] | list[dict[str, object]] = Field(
            description="Data suitable for table formatting"
        )

        @field_validator("data")
        @classmethod
        def validate_table_data(
            cls, v: dict[str, object] | list[dict[str, object]]
        ) -> dict[str, object] | list[dict[str, object]]:
            """Validate data is suitable for table formatting."""
            # Type validation handled by Pydantic - v is guaranteed to match the union type
            return v

        def validate_business_rules(self) -> FlextResult[None]:
            """Validate table data business rules."""
            if isinstance(self.data, list) and self.data:
                # Validate all items are dicts with consistent keys
                first_keys = (
                    set(self.data[0].keys())
                    if isinstance(self.data[0], dict)
                    else set()
                )
                for item in self.data[1:]:
                    if isinstance(item, dict) and set(item.keys()) != first_keys:
                        return FlextResult[None].fail(
                            "Inconsistent dictionary keys in list data"
                        )
            return FlextResult[None].ok(None)

    class CsvFormatterData(FlextModels.Entity):
        """Specific validation for CSV formatting data."""

        model_config = FlextCliUtilities.get_base_config_dict()

        data: dict[str, object] | list[dict[str, object]] = Field(
            description="Data suitable for CSV formatting"
        )

        @field_validator("data")
        @classmethod
        def validate_csv_data(
            cls, v: dict[str, object] | list[dict[str, object]]
        ) -> dict[str, object] | list[dict[str, object]]:
            """Validate data is suitable for CSV formatting."""
            # Validate consistent fieldnames for CSV if it's a list
            if isinstance(v, list) and v:
                first_keys = set(v[0].keys())
                for item in v[1:]:
                    if set(item.keys()) != first_keys:
                        msg = "CSV data contains inconsistent field names"
                        raise ValueError(msg)
            return v

        def validate_business_rules(self) -> FlextResult[None]:
            """Validate CSV data business rules."""
            return FlextResult[None].ok(None)

    # Field validation models for utils.py
    class FieldValidationSpec(FlextModels.Entity):
        """Specification for field validation rules."""

        model_config = FlextCliUtilities.get_base_config_dict()

        field_name: str = Field(min_length=1, description="Name of field to validate")
        field_type: str = Field(
            min_length=1, description="Expected type name for field"
        )
        required: bool = Field(default=True, description="Whether field is required")

        def validate_business_rules(self) -> FlextResult[None]:
            """Validate field validation spec business rules."""
            if not self.field_name.strip():
                return FlextResult[None].fail("Field name cannot be empty")
            return FlextResult[None].ok(None)

    class ValidationTarget(FlextModels.Entity):
        """Target data for validation operations."""

        model_config = FlextCliUtilities.get_base_config_dict()

        data: dict[str, object] = Field(description="Data to validate")
        validation_specs: list[FlextCliModels.FieldValidationSpec] = Field(
            default_factory=list, description="Field validation specifications"
        )

        @field_validator("data")
        @classmethod
        def validate_data_is_dict(cls, v: dict[str, object]) -> dict[str, object]:
            """Validate data is a dictionary."""
            # Type validation handled by Pydantic - v is guaranteed to be dict[str, object]
            return v

        def validate_business_rules(self) -> FlextResult[None]:
            """Validate target data against field specifications."""
            for spec in self.validation_specs:
                if spec.required and spec.field_name not in self.data:
                    return FlextResult[None].fail(
                        f"Missing required field: {spec.field_name}"
                    )

                if spec.field_name in self.data:
                    # Type validation would be done here based on spec.field_type
                    # For now, we trust the Pydantic model structure
                    pass

            return FlextResult[None].ok(None)


__all__ = ["FlextCliModels"]
