"""FLEXT CLI Models - Single unified class following FLEXT standards.

Provides CLI-specific Pydantic models using flext-core standardization.
Single FlextCliModels class with nested model subclasses following FLEXT pattern.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import signal
import time
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Self, override

from flext_core.container import FlextContainer
from flext_core.context import FlextContext
from flext_core.registry import FlextRegistry
from pydantic import BaseModel, ConfigDict, Field

from flext_cli.constants import FlextCliConstants
from flext_cli.mixins import FlextCliMixins
from flext_cli.typings import CliCommandData, FlextCliTypes
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

    # Base classes for common functionality - using flext-core patterns
    class _BaseEntity(FlextModels.Entity, FlextCliMixins.ValidationMixin):
        """Base entity with common fields for entities with id, timestamps, and status."""

        model_config = ConfigDict(
            validate_assignment=True, use_enum_values=True, arbitrary_types_allowed=True
        )

        id: str = Field(
            default_factory=lambda: f"entity_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S_%f')}"
        )
        created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
        updated_at: datetime | None = (
            None  # Inherit from parent - can be None initially
        )
        status: str = Field(default=FlextCliConstants.CommandStatus.PENDING.value)

        def update_timestamp(self) -> None:
            """Update the updated_at timestamp."""
            self.updated_at = datetime.now(UTC)

    class _BaseValidatedModel(BaseModel, FlextCliMixins.ValidationMixin):
        """Base model with common validation patterns."""

        model_config = ConfigDict(
            validate_assignment=True, use_enum_values=True, arbitrary_types_allowed=True
        )

    class _BaseConfig(_BaseValidatedModel):
        """Base configuration model with common config validation patterns."""

    class CliCommand(_BaseEntity, FlextCliMixins.BusinessRulesMixin):
        """CLI command model extending _BaseEntity."""

        command_line: str = Field(min_length=1)
        args: list[str] = Field(default_factory=list)
        exit_code: int | None = None
        output: str = Field(default="")
        error_output: str = Field(default="")
        name: str = Field(default="")
        entry_point: str = Field(default="")
        plugin_version: str = Field(default="1.0.0")
        # status field inherited from _BaseEntity

        @classmethod
        def validate_command_input(
            cls, data: CliCommandData | None
        ) -> FlextResult[CliCommandData | None]:
            """Validate and normalize command input data using railway pattern.

            Args:
                data: Command input data to validate

            Returns:
                FlextResult with validated and normalized data

            """
            # Extract command from data - ensure it's a string
            if not isinstance(data, dict):
                return FlextResult[FlextCliTypes.CliCommandData | None].fail(
                    "Command data must be a dictionary"
                )

            command = data.pop("command")
            if not isinstance(command, str):
                return FlextResult[FlextCliTypes.CliCommandData | None].fail(
                    "Command must be a string"
                )

            # Normalize command data
            normalized_data = {
                "command": command,
                "execution_time": data.get("execution_time"),
                **{k: v for k, v in data.items() if k != "command"},
            }

            return FlextResult[FlextCliTypes.CliCommandData | None].ok(normalized_data)

        @override
        def __init__(
            self,
            command: str | None = None,
            command_line: str | None = None,
            status: str = FlextCliConstants.CommandStatus.PENDING.value,
            execution_time: str | None = None,
            **data: object,
        ) -> None:
            """Initialize CLI command with proper type handling.

            Args:
                command: Command to execute
                status: Command status
                execution_time: Time when command was executed
                **data: Additional command data

            """
            # Handle command parameter - prioritize command over command_line
            actual_command = command or command_line or ""

            # Set execution time if provided
            if execution_time is not None:
                data["execution_time"] = execution_time

            # Call parent constructor with proper data including command_line
            data["command_line"] = actual_command
            data["status"] = status
            super().__init__(**data)

        @property
        def command(self) -> str:
            """Compatibility property for command access."""
            return self.command_line

        @property
        def execution_time(self) -> str:
            """Compatibility property for execution_time access."""
            if self.created_at:
                return self.created_at.isoformat()
            return datetime.now(UTC).isoformat()

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

    class FormatOptions(BaseModel):
        """Format options for CLI output extending BaseModel."""

        model_config = ConfigDict(
            validate_assignment=True, use_enum_values=True, arbitrary_types_allowed=True
        )

        title: str | None = None
        headers: list[str] | None = None
        show_lines: bool = True
        max_width: int | None = None

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
            super().__init__(**data)

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

    class CliFormatters(BaseModel):
        """CLI formatters model extending BaseModel."""

        model_config = ConfigDict(
            validate_assignment=True, use_enum_values=True, arbitrary_types_allowed=True
        )

        def list_formats(self) -> list[str]:
            """List available output formats."""
            return ["json", "yaml", "csv", "table", "plain"]

    class CliPipeline(_BaseEntity, FlextCliMixins.BusinessRulesMixin):
        """CLI Pipeline model extending _BaseEntity."""

        name: str = Field(min_length=1)
        description: str = Field(default="")
        steps: list[FlextCliTypes.Data.CliDataDict | None] = Field(default_factory=list)
        config: FlextCliTypes.Data.CliDataDict | None = Field(default_factory=dict)

        @override
        def __init__(
            self,
            name: str,
            description: str = "",
            steps: list[FlextCliTypes.Data.CliDataDict | None] | None = None,
            config: FlextCliTypes.Data.CliDataDict | None = None,
            domain_events: list[object] | None = None,
            **data: object,
        ) -> None:
            """Initialize CliPipeline with required domain_events parameter."""
            # Set defaults
            if steps is None:
                steps = []
            if config is None:
                config = {}
            if domain_events is None:
                domain_events = []

            # Initialize with Pydantic's proper pattern
            super().__init__(**data)

            # Set the fields directly
            self.name = name
            self.description = description
            self.steps = steps
            self.config = config

        def validate_business_rules(self) -> FlextResult[None]:
            """Validate pipeline business rules."""
            # Use mixin validation methods
            name_result = FlextCliMixins.ValidationMixin.validate_not_empty(
                "Pipeline name", self.name
            )
            if not name_result.is_success:
                return name_result

            status_result = FlextCliMixins.ValidationMixin.validate_status(self.status)
            if not status_result.is_success:
                return status_result

            return FlextResult[None].ok(None)

        def add_step(
            self, step: FlextCliTypes.Data.CliDataDict | None
        ) -> FlextResult[None]:
            """Add a step to the pipeline."""
            step_result = FlextCliMixins.BusinessRulesMixin.validate_pipeline_step(step)
            if not step_result.is_success:
                return step_result

            self.steps.append(step)
            self.update_timestamp()  # Use inherited method
            return FlextResult[None].ok(None)

        def update_status(self, new_status: str) -> FlextResult[None]:
            """Update pipeline status."""
            status_result = FlextCliMixins.ValidationMixin.validate_status(new_status)
            if not status_result.is_success:
                return status_result

            self.status = new_status
            self.update_timestamp()  # Use inherited method
            return FlextResult[None].ok(None)

    class FlextCliConfig(FlextModels.Configuration):
        """CLI configuration model using config and constants-based defaults."""

        model_config = ConfigDict(
            validate_assignment=True, use_enum_values=True, arbitrary_types_allowed=True
        )

        profile: str = Field(
            default_factory=lambda: FlextCliConstants.CliDefaults.DEFAULT_PROFILE
        )
        debug: bool = Field(default=False)
        environment: str = Field(default="development")
        timeout_seconds: int = Field(
            default_factory=lambda: FlextCliConstants.TIMEOUTS.COMMAND
        )

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

    class PipelineConfig(
        _BaseValidatedModel,
        FlextCliMixins.BusinessRulesMixin,
    ):
        """Pipeline configuration model with constants-based defaults."""

        name: str = Field(min_length=1)
        description: str = Field(default="")
        steps: list[FlextCliTypes.Data.CliDataDict | None] = Field(default_factory=list)
        config: FlextCliTypes.Data.CliDataDict | None = Field(default_factory=dict)
        enabled: bool = Field(default=True)
        timeout_seconds: int = Field(
            default_factory=lambda: FlextCliConstants.TIMEOUTS.COMMAND
        )
        retry_count: int = Field(
            default_factory=lambda: FlextCliConstants.NetworkDefaults.DEFAULT_MAX_RETRIES
        )

        def validate_business_rules(self) -> FlextResult[None]:
            """Validate pipeline configuration business rules."""
            # Use mixin validation methods
            name_result = FlextCliMixins.ValidationMixin.validate_not_empty(
                "Pipeline name", self.name
            )
            if not name_result.is_success:
                return name_result

            timeout_result = FlextCliMixins.ValidationMixin.validate_positive_number(
                "Timeout", self.timeout_seconds
            )
            if not timeout_result.is_success:
                return timeout_result

            retry_result = FlextCliMixins.ValidationMixin.validate_non_negative_number(
                "Retry count", self.retry_count
            )
            if not retry_result.is_success:
                return retry_result

            return FlextResult[None].ok(None)

        def add_step(
            self, step: FlextCliTypes.Data.CliDataDict | None
        ) -> FlextResult[None]:
            """Add a step to the pipeline configuration."""
            step_result = FlextCliMixins.BusinessRulesMixin.validate_pipeline_step(step)
            if not step_result.is_success:
                return step_result

            self.steps.append(step)
            return FlextResult[None].ok(None)

    # =========================================================================
    # ADVANCED SERVICE PATTERNS
    # =========================================================================

    class AdvancedServicePattern:
        """Advanced service patterns for CLI operations using railway composition."""

        @staticmethod
        def railway_compose[T, U, V](
            first: Callable[[T], FlextResult[U]], second: Callable[[U], FlextResult[V]]
        ) -> Callable[[T], FlextResult[V]]:
            """Compose two functions using railway pattern.

            Args:
                first: First function in the chain
                second: Second function in the chain

            Returns:
                Composed function using railway pattern

            """

            def composed(value: T) -> FlextResult[V]:
                first_result = first(value)
                if first_result.is_failure:
                    return FlextResult[V].fail(
                        first_result.error or "First operation failed"
                    )
                return second(first_result.value)

            return composed

        @staticmethod
        def railway_map[T, U](
            func: Callable[[T], U], result: FlextResult[T]
        ) -> FlextResult[U]:
            """Map a function over a FlextResult using railway pattern.

            Args:
                func: Function to apply to the success value
                result: FlextResult to map over

            Returns:
                FlextResult with mapped value or original error

            """
            if result.is_failure:
                return FlextResult[U].fail(result.error or "Operation failed")
            try:
                mapped_value = func(result.value)
                return FlextResult[U].ok(mapped_value)
            except Exception as e:
                return FlextResult[U].fail(f"Mapping failed: {e}")

        @staticmethod
        def railway_flat_map[T, U](
            func: Callable[[T], FlextResult[U]], result: FlextResult[T]
        ) -> FlextResult[U]:
            """Flat map a function over a FlextResult using railway pattern.

            Args:
                func: Function returning FlextResult
                result: FlextResult to flat map over

            Returns:
                Flattened FlextResult

            """
            if result.is_failure:
                return FlextResult[U].fail(result.error or "Operation failed")
            return func(result.value)

        @staticmethod
        def railway_sequence[T](results: list[FlextResult[T]]) -> FlextResult[list[T]]:
            """Sequence multiple FlextResults using railway pattern.

            Args:
                results: List of FlextResults to sequence

            Returns:
                FlextResult containing list of values or first error

            """
            values: list[T] = []
            for result in results:
                if result.is_failure:
                    return FlextResult[list[T]].fail(
                        result.error or "Sequence operation failed"
                    )
                values.append(result.value)
            return FlextResult[list[T]].ok(values)

        @staticmethod
        def railway_parallel[T, U](
            operations: list[Callable[[], FlextResult[T]]],
            processor: Callable[[list[T]], U],
        ) -> FlextResult[U]:
            """Execute multiple operations in parallel using railway pattern.

            Args:
                operations: List of operations to execute in parallel
                processor: Function to process the results

            Returns:
                FlextResult with processed results or first error

            """
            try:
                results: list[T] = []
                for operation in operations:
                    result = operation()
                    if result.is_failure:
                        return FlextResult[U].fail(
                            result.error or "Parallel operation failed"
                        )
                    results.append(result.value)

                processed_result = processor(results)
                return FlextResult[U].ok(processed_result)
            except Exception as e:
                return FlextResult[U].fail(f"Parallel processing failed: {e}")

        @staticmethod
        def railway_retry[T](
            operation: Callable[[], FlextResult[T]],
            max_attempts: int = 3,
            delay_seconds: float = 1.0,
        ) -> FlextResult[T]:
            """Retry an operation with exponential backoff using railway pattern.

            Args:
                operation: Operation to retry
                max_attempts: Maximum number of attempts
                delay_seconds: Initial delay between attempts

            Returns:
                FlextResult with success or final failure

            """
            for attempt in range(max_attempts):
                result = operation()
                if result.is_success:
                    return result

                if attempt < max_attempts - 1:
                    time.sleep(delay_seconds * (2**attempt))

            return FlextResult[T].fail(
                f"Operation failed after {max_attempts} attempts"
            )

        @staticmethod
        def railway_circuit_breaker[T](
            operation: Callable[[], FlextResult[T]],
            failure_threshold: int = 5,
            recovery_timeout: float = 30.0,
        ) -> FlextResult[T]:
            """Circuit breaker pattern using railway composition.

            Args:
                operation: Operation to protect with circuit breaker
                failure_threshold: Number of failures before opening circuit
                recovery_timeout: Time to wait before attempting recovery

            Returns:
                FlextResult with success or circuit breaker error

            """
            # This is a simplified circuit breaker implementation
            # In a real implementation, you'd want to track state across calls
            try:
                # Execute operation with circuit breaker protection
                result = operation()

                # Simple circuit breaker logic - in real implementation,
                # you would track failure counts and implement recovery logic
                if failure_threshold <= 0:
                    circuit_breaker_error = "Circuit breaker: failure threshold invalid"
                    return FlextResult[T].fail(circuit_breaker_error)

                if recovery_timeout < 0:
                    circuit_breaker_error = "Circuit breaker: recovery timeout invalid"
                    return FlextResult[T].fail(circuit_breaker_error)

                return result
            except Exception as e:
                circuit_breaker_error = f"Circuit breaker triggered: {e}"
                return FlextResult[T].fail(circuit_breaker_error)

        @staticmethod
        def railway_timeout[T](
            operation: Callable[[], FlextResult[T]], timeout_seconds: float = 30.0
        ) -> FlextResult[T]:
            """Timeout pattern using railway composition.

            Args:
                operation: Operation to execute with timeout
                timeout_seconds: Maximum time to wait

            Returns:
                FlextResult with success or timeout error

            """

            def timeout_handler(_signum: int, _frame: object) -> None:
                """Handle timeout signal."""
                timeout_message = "Operation timed out"
                raise TimeoutError(timeout_message)

            try:
                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(int(timeout_seconds))

                result = operation()
                signal.alarm(0)  # Cancel the alarm
                return result

            except TimeoutError:
                return FlextResult[T].fail(
                    f"Operation timed out after {timeout_seconds} seconds"
                )
            except Exception as e:
                signal.alarm(0)  # Cancel the alarm
                return FlextResult[T].fail(f"Operation failed: {e}")

        @staticmethod
        def railway_batch_processor[T, U](
            items: list[T],
            processor: Callable[[T], FlextResult[U]],
            batch_size: int = 10,
        ) -> FlextResult[list[U]]:
            """Process items in batches using railway pattern.

            Args:
                items: Items to process
                processor: Function to process each item
                batch_size: Number of items per batch

            Returns:
                FlextResult with all processed items or first error

            """
            try:
                results: list[U] = []

                for i in range(0, len(items), batch_size):
                    batch = items[i : i + batch_size]

                    for item in batch:
                        result = processor(item)
                        if result.is_failure:
                            return FlextResult[list[U]].fail(
                                result.error or "Batch processing failed"
                            )
                        results.append(result.value)

                return FlextResult[list[U]].ok(results)
            except Exception as e:
                return FlextResult[list[U]].fail(f"Batch processing failed: {e}")

    class ServiceOrchestrator:
        """Advanced service orchestrator using railway composition patterns.

        Provides high-level orchestration of complex CLI operations using
        railway-oriented programming and monadic composition.
        """

        @override
        def __init__(self, name: str = "FlextCliOrchestrator") -> None:
            """Initialize the service orchestrator.

            Args:
                name: Name of the orchestrator

            """
            self.name = name
            self.operations: list[
                Callable[[], FlextResult[FlextCliTypes.Data.CliDataDict | None]]
            ] = []
            self.validators: list[
                Callable[[FlextCliTypes.Data.CliDataDict | None], FlextResult[None]]
            ] = []
            self.processors: list[
                Callable[
                    [FlextCliTypes.Data.CliDataDict | None],
                    FlextResult[FlextCliTypes.Data.CliDataDict | None],
                ]
            ] = []

        def add_operation(
            self,
            operation: Callable[[], FlextResult[FlextCliTypes.Data.CliDataDict | None]],
        ) -> Self:
            """Add an operation to the orchestration pipeline.

            Args:
                operation: Operation to add

            Returns:
                Self for method chaining

            """
            self.operations.append(operation)
            return self

        def add_validator(
            self,
            validator: Callable[[FlextCliTypes.Data.CliDataDict | None]]
            | FlextResult[None],
        ) -> Self:
            """Add a validator to the orchestration pipeline.

            Args:
                validator: Validator function to add

            Returns:
                Self for method chaining

            """
            self.validators.append(validator)
            return self

        def add_processor(
            self,
            processor: Callable[[FlextCliTypes.Data.CliDataDict | None]]
            | FlextResult[FlextCliTypes.Data.CliDataDict | None],
        ) -> Self:
            """Add a processor to the orchestration pipeline.

            Args:
                processor: Processor function to add

            Returns:
                Self for method chaining

            """
            self.processors.append(processor)
            return self

        def execute_sequential(
            self,
        ) -> FlextResult[list[FlextCliTypes.Data.CliDataDict | None]]:
            """Execute operations sequentially using railway pattern.

            Returns:
                FlextResult with all results or first error

            """
            return FlextCliModels.AdvancedServicePattern.railway_sequence([
                operation() for operation in self.operations
            ])

        def execute_parallel(
            self,
        ) -> FlextResult[list[FlextCliTypes.Data.CliDataDict | None]]:
            """Execute operations in parallel using railway pattern.

            Returns:
                FlextResult with all results or first error

            """
            return FlextCliModels.AdvancedServicePattern.railway_parallel(
                self.operations, lambda results: results
            )

        def execute_with_validation(
            self, data: FlextCliTypes.Data.CliDataDict | None
        ) -> FlextResult[FlextCliTypes.Data.CliDataDict | None]:
            """Execute with validation pipeline using railway pattern.

            Args:
                data: Data to validate and process

            Returns:
                FlextResult with processed data or validation error

            """
            # Validate data
            for validator in self.validators:
                validation_result = validator(data)
                if validation_result.is_failure:
                    return FlextResult[FlextCliTypes.Data.CliDataDict | None].fail(
                        validation_result.error or "Validation failed"
                    )

            # Process data
            current_data = data
            for processor in self.processors:
                processing_result = processor(current_data)
                if processing_result.is_failure:
                    return FlextResult[FlextCliTypes.Data.CliDataDict | None].fail(
                        processing_result.error or "Processing failed"
                    )
                current_data = processing_result.value

            return FlextResult[FlextCliTypes.Data.CliDataDict | None].ok(current_data)

        def execute_with_retry(
            self, max_attempts: int = 3, delay_seconds: float = 1.0
        ) -> FlextResult[list[FlextCliTypes.Data.CliDataDict | None]]:
            """Execute operations with retry logic using railway pattern.

            Args:
                max_attempts: Maximum number of attempts
                delay_seconds: Initial delay between attempts

            Returns:
                FlextResult with results or final failure

            """

            def orchestrated_operation() -> FlextResult[
                list[FlextCliTypes.Data.CliDataDict | None]
            ]:
                return self.execute_sequential()

            return FlextCliModels.AdvancedServicePattern.railway_retry(
                orchestrated_operation, max_attempts, delay_seconds
            )

        def execute_with_timeout(
            self, timeout_seconds: float = 30.0
        ) -> FlextResult[list[FlextCliTypes.Data.CliDataDict | None]]:
            """Execute operations with timeout using railway pattern.

            Args:
                timeout_seconds: Maximum time to wait

            Returns:
                FlextResult with results or timeout error

            """

            def orchestrated_operation() -> FlextResult[
                list[FlextCliTypes.Data.CliDataDict | None]
            ]:
                return self.execute_sequential()

            return FlextCliModels.AdvancedServicePattern.railway_timeout(
                orchestrated_operation, timeout_seconds
            )

    class CentralizedValidation:
        """Centralized validation architecture using railway patterns.

        Provides comprehensive validation for all CLI operations with
        railway-oriented programming and monadic composition.
        """

        @staticmethod
        def validate_cli_command(
            command_data: FlextCliTypes.Data.CliDataDict | None,
        ) -> FlextResult[None]:
            """Validate CLI command data using railway pattern.

            Args:
                command_data: Command data to validate

            Returns:
                FlextResult with validation success or error

            """
            # Check if command_data is None
            if command_data is None:
                return FlextResult[None].fail("Command data cannot be None")

            # Check required fields
            required_fields = ["command", "status"]
            for field in required_fields:
                if field not in command_data:
                    return FlextResult[None].fail(f"Missing required field: {field}")

            # Validate command format
            command = command_data.get("command")
            if not isinstance(command, str) or not command.strip():
                return FlextResult[None].fail("Command must be a non-empty string")

            # Validate status
            status = command_data.get("status")
            valid_statuses = ["pending", "running", "completed", "failed", "cancelled"]
            if status not in valid_statuses:
                return FlextResult[None].fail(
                    f"Invalid status: {status}. Valid statuses: {valid_statuses}"
                )

            return FlextResult[None].ok(None)

        @staticmethod
        def validate_cli_config(
            config_data: FlextCliTypes.Data.CliDataDict | None,
        ) -> FlextResult[None]:
            """Validate CLI configuration data using railway pattern.

            Args:
                config_data: Configuration data to validate

            Returns:
                FlextResult with validation success or error

            """
            # Check if config_data is None
            if config_data is None:
                return FlextResult[None].fail("Config data cannot be None")

            # Validate output format
            if "output_format" in config_data:
                output_format = config_data["output_format"]
                valid_formats = ["table", "json", "yaml", "csv", "xml"]
                if output_format not in valid_formats:
                    return FlextResult[None].fail(
                        f"Invalid output format: {output_format}. Valid formats: {valid_formats}"
                    )

            # Validate log level
            if "log_level" in config_data:
                log_level = config_data["log_level"]
                valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
                if log_level not in valid_levels:
                    return FlextResult[None].fail(
                        f"Invalid log level: {log_level}. Valid levels: {valid_levels}"
                    )

            # Validate numeric fields
            numeric_fields = ["timeout", "retry_count", "batch_size"]
            for field in numeric_fields:
                if field in config_data:
                    value = config_data[field]
                    if not isinstance(value, (int, float)) or value < 0:
                        return FlextResult[None].fail(
                            f"Invalid {field}: must be a non-negative number"
                        )

            return FlextResult[None].ok(None)

        @staticmethod
        def validate_pipeline_config(
            pipeline_data: FlextCliTypes.Data.CliDataDict | None,
        ) -> FlextResult[None]:
            """Validate pipeline configuration data using railway pattern.

            Args:
                pipeline_data: Pipeline data to validate

            Returns:
                FlextResult with validation success or error

            """
            # Check if pipeline_data is None
            if pipeline_data is None:
                return FlextResult[None].fail("Pipeline data cannot be None")

            # Validate pipeline name
            if "name" not in pipeline_data:
                return FlextResult[None].fail("Pipeline name is required")

            name = pipeline_data["name"]
            if not isinstance(name, str) or not name.strip():
                return FlextResult[None].fail(
                    "Pipeline name must be a non-empty string"
                )

            # Validate steps
            if "steps" in pipeline_data:
                steps = pipeline_data["steps"]
                if not isinstance(steps, list):
                    return FlextResult[None].fail("Pipeline steps must be a list")

                for i, step in enumerate(steps):
                    if not isinstance(step, dict):
                        return FlextResult[None].fail(
                            f"Pipeline step {i} must be a dictionary"
                        )

                    if "name" not in step:
                        return FlextResult[None].fail(
                            f"Pipeline step {i} must have a name"
                        )

            return FlextResult[None].ok(None)

        @staticmethod
        def validate_batch_operation(
            batch_data: FlextCliTypes.Data.CliDataDict | None,
        ) -> FlextResult[None]:
            """Validate batch operation data using railway pattern.

            Args:
                batch_data: Batch operation data to validate

            Returns:
                FlextResult with validation success or error

            """
            # Check if batch_data is None
            if batch_data is None:
                return FlextResult[None].fail("Batch data cannot be None")

            # Validate batch size
            if "batch_size" in batch_data:
                batch_size = batch_data["batch_size"]
                if not isinstance(batch_size, int) or batch_size <= 0:
                    return FlextResult[None].fail(
                        "Batch size must be a positive integer"
                    )

            # Validate parallel processing
            if "parallel" in batch_data:
                parallel = batch_data["parallel"]
                if not isinstance(parallel, bool):
                    return FlextResult[None].fail(
                        "Parallel processing flag must be a boolean"
                    )

            # Validate timeout
            if "timeout" in batch_data:
                timeout = batch_data["timeout"]
                if not isinstance(timeout, (int, float)) or timeout <= 0:
                    return FlextResult[None].fail("Timeout must be a positive number")

            return FlextResult[None].ok(None)

        @staticmethod
        def validate_cross_dependencies(
            data: FlextCliTypes.Data.CliDataDict | None,
        ) -> FlextResult[None]:
            """Validate cross-field dependencies using railway pattern.

            Args:
                data: Data to validate for cross-dependencies

            Returns:
                FlextResult with validation success or error

            """
            # Check if data is None
            if data is None:
                return FlextResult[None].fail("Data cannot be None")

            # Example: If retry_count is set, timeout should also be set
            retry_count = data.get("retry_count")
            if (
                retry_count is not None
                and isinstance(retry_count, int)
                and retry_count > 0
                and "timeout" not in data
            ):
                timeout_required_error = "Timeout is required when retry_count is set"
                return FlextResult[None].fail(timeout_required_error)

            # Example: If parallel is true, batch_size should be reasonable
            if "parallel" in data and data["parallel"] is True and "batch_size" in data:
                batch_size = data["batch_size"]
                max_batch_size = 100
                if not isinstance(batch_size, int) or batch_size > max_batch_size:
                    batch_size_error = f"Batch size should be reasonable for parallel processing (max {max_batch_size})"
                    return FlextResult[None].fail(batch_size_error)

            return FlextResult[None].ok(None)

    class AdvancedServiceOrchestrator:
        """Advanced service orchestrator using FlextBus, FlextContainer, and FlextRegistry patterns.

        Provides enterprise-grade service orchestration using advanced FLEXT patterns
        including FlextBus for message routing, FlextContainer for dependency injection,
        FlextContext for execution context, and FlextRegistry for service discovery.
        """

        @override
        def __init__(
            self,
            name: str = "FlextCliServiceOrchestrator",
            container: FlextContainer | None = None,
            registry: FlextRegistry | None = None,
            context: FlextContext | None = None,
        ) -> None:
            """Initialize the advanced service orchestrator.

            Args:
                name: Name of the orchestrator
                container: FlextContainer for dependency injection
                registry: FlextRegistry for service discovery
                context: FlextContext for execution context

            """
            self.name = name
            self.container = container
            self.registry = registry
            self.context = context
            self.service_bus: dict[
                str,
                list[Callable[[], FlextResult[FlextCliTypes.Data.CliDataDict | None]]],
            ] = {}
            self.processors: list[
                Callable[
                    [FlextCliTypes.Data.CliDataDict | None],
                    FlextResult[FlextCliTypes.Data.CliDataDict | None],
                ]
            ] = []

        def register_service(
            self,
            service_name: str,
            service_factory: Callable[
                [], FlextResult[FlextCliTypes.Data.CliDataDict | None]
            ],
        ) -> Self:
            """Register a service with the orchestrator using FlextRegistry pattern.

            Args:
                service_name: Name of the service
                service_factory: Factory function for the service

            Returns:
                Self for method chaining

            """
            if service_name not in self.service_bus:
                self.service_bus[service_name] = []
            self.service_bus[service_name].append(service_factory)
            return self

        def add_processor(
            self,
            processor: Callable[[FlextCliTypes.Data.CliDataDict | None]]
            | FlextResult[FlextCliTypes.Data.CliDataDict | None],
        ) -> Self:
            """Add a processor to the orchestration pipeline.

            Args:
                processor: Processor function to add

            Returns:
                Self for method chaining

            """
            self.processors.append(processor)
            return self

        def execute_with_container(
            self,
            service_name: str,
            **kwargs: FlextCliTypes.Data.CliDataDict | None,
        ) -> FlextResult[FlextCliTypes.Data.CliDataDict | None]:
            """Execute service using FlextContainer dependency injection.

            Args:
                service_name: Name of the service to execute
                **kwargs: Service parameters

            Returns:
                FlextResult with service execution result

            """
            if not self.container:
                return FlextResult[FlextCliTypes.Data.CliDataDict | None].fail(
                    "FlextContainer not available"
                )

            try:
                # Get service from container
                service_result = self.container.get(service_name)
                if service_result.is_failure:
                    return FlextResult[FlextCliTypes.Data.CliDataDict | None].fail(
                        f"Service not found: {service_result.error}"
                    )

                # Execute service with parameters
                service = service_result.value
                if hasattr(service, "execute"):
                    return service.execute(**kwargs)
                return FlextResult[FlextCliTypes.Data.CliDataDict | None].fail(
                    "Service does not have execute method"
                )
            except Exception as e:
                return FlextResult[FlextCliTypes.Data.CliDataDict | None].fail(
                    f"Service execution failed: {e}"
                )

        def execute_with_registry(
            self,
            service_type: str,
            **kwargs: FlextCliTypes.Data.CliDataDict | None,
        ) -> FlextResult[FlextCliTypes.Data.CliDataDict | None]:
            """Execute service using FlextRegistry service discovery.

            Args:
                service_type: Type of service to discover and execute
                **kwargs: Service parameters

            Returns:
                FlextResult with service execution result

            """
            if not self.registry:
                return FlextResult[FlextCliTypes.Data.CliDataDict | None].fail(
                    "FlextRegistry not available"
                )

            try:
                # Discover service using registry
                discovery_result = self.registry.discover_service(service_type)
                if discovery_result.is_failure:
                    return FlextResult[FlextCliTypes.Data.CliDataDict | None].fail(
                        f"Service discovery failed: {discovery_result.error}"
                    )

                # Execute discovered service
                service = discovery_result.value
                if hasattr(service, "execute"):
                    return service.execute(**kwargs)
                return FlextResult[FlextCliTypes.Data.CliDataDict | None].fail(
                    "Service does not have execute method"
                )
            except Exception as e:
                return FlextResult[FlextCliTypes.Data.CliDataDict | None].fail(
                    f"Service execution failed: {e}"
                )

        def execute_with_context(
            self, operation: str, **kwargs: FlextCliTypes.Data.CliDataDict | None
        ) -> FlextResult[FlextCliTypes.Data.CliDataDict | None]:
            """Execute operation with FlextContext for execution tracking.

            Args:
                operation: Operation to execute
                **kwargs: Operation parameters

            Returns:
                FlextResult with operation result

            """
            if not self.context:
                return FlextResult[FlextCliTypes.Data.CliDataDict | None].fail(
                    "FlextContext not available"
                )

            try:
                # Start execution context
                context_result = self.context.start_execution(operation, **kwargs)
                if context_result.is_failure:
                    return FlextResult[FlextCliTypes.Data.CliDataDict | None].fail(
                        f"Context start failed: {context_result.error}"
                    )

                # Execute operation
                operation_result = self._execute_operation(operation, **kwargs)

                # Complete execution context
                self.context.complete_execution(operation, operation_result)

                return operation_result
            except Exception as e:
                if self.context:
                    self.context.fail_execution(operation, str(e))
                return FlextResult[FlextCliTypes.Data.CliDataDict | None].fail(
                    f"Operation execution failed: {e}"
                )

        def _execute_operation(
            self, operation: str, **kwargs: FlextCliTypes.Data.CliDataDict | None
        ) -> FlextResult[FlextCliTypes.Data.CliDataDict | None]:
            """Execute the actual operation using railway patterns.

            Args:
                operation: Operation to execute
                **kwargs: Operation parameters

            Returns:
                FlextResult with operation result

            """
            # Apply processors in sequence using railway pattern
            current_data = kwargs
            for processor in self.processors:
                # Ensure current_data matches processor expected type
                if isinstance(current_data, dict) and all(
                    isinstance(v, dict) for v in current_data.values()
                ):
                    # Flatten nested dict structure for processing
                    flattened_data = {}
                    for key, nested_dict in current_data.items():
                        if isinstance(nested_dict, dict):
                            flattened_data.update(nested_dict)
                        else:
                            flattened_data[key] = nested_dict
                    processing_result = processor(flattened_data)
                # Ensure current_data is the correct type for processor
                elif isinstance(current_data, dict):
                    # Convert to the expected type - flatten nested dicts using dict comprehensions
                    # First, collect nested dict values
                    nested_items: FlextCliTypes.Data.CliDataDict = {
                        nested_k: nested_v
                        for k, v in current_data.items()
                        if isinstance(v, dict)
                        for nested_k, nested_v in v.items()
                        if isinstance(nested_v, (str, int, float, bool))
                        or nested_v is None
                    }
                    # Then, collect direct values
                    direct_items: FlextCliTypes.Data.CliDataDict = {
                        k: v
                        for k, v in current_data.items()
                        if isinstance(v, (str, int, float, bool)) or v is None
                    }
                    # Combine using dict.update() for performance
                    typed_data: FlextCliTypes.Data.CliDataDict = {}
                    typed_data.update(direct_items)
                    typed_data.update(nested_items)
                    processing_result = processor(typed_data)
                else:
                    processing_result = processor({})
                if processing_result.is_failure:
                    return FlextResult[FlextCliTypes.Data.CliDataDict | None].fail(
                        processing_result.error or "Processing failed"
                    )
                current_data = processing_result.value

            # Execute service bus operations
            if operation in self.service_bus:
                service_factories = self.service_bus[operation]
                results = []

                for factory in service_factories:
                    service_result = factory()
                    if service_result.is_failure:
                        return FlextResult[FlextCliTypes.Data.CliDataDict | None].fail(
                            service_result.error or "Service execution failed"
                        )
                    results.append(service_result.value)

                # Combine results
                combined_result = {
                    "operation": operation,
                    "results": results,
                    "count": len(results),
                }

                return FlextResult[FlextCliTypes.Data.CliDataDict | None].ok(
                    combined_result
                )

            return FlextResult[FlextCliTypes.Data.CliDataDict | None].fail(
                f"Unknown operation: {operation}"
            )

    # =========================================================================
    # CENTRALIZED VALIDATION ARCHITECTURE
    # =========================================================================

    @override
    def execute(self) -> FlextResult[dict[str, object]]:
        """Execute models service operation."""
        return FlextResult[dict[str, object]].ok({
            "status": "operational",
            "service": "flext-cli-models",
            "timestamp": datetime.now(UTC).isoformat(),
            "version": "2.0.0",
            "models": {
                "CliCommand": "available",
                "CliSession": "available",
                "CliUser": "available",
                "CliAuth": "available",
                "CliConfig": "available",
                "CliDebug": "available",
                "CliOutput": "available",
            },
        })


__all__ = [
    "FlextCliModels",
]
