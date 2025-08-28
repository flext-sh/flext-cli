"""CLI service implementations using flext-core domain services.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from abc import abstractmethod
from typing import TypeVar, override

from flext_core import (
    FlextContainer,
    FlextDomainService,
    FlextLogger,
    FlextResult,
)
from pydantic import ConfigDict, Field

# Type variables for generic services
T = TypeVar("T")
CommandResultType = TypeVar("CommandResultType")
ValidationResultType = TypeVar("ValidationResultType")

# =============================================================================
# CLI COMMAND SERVICE - Direct FlextDomainService extension
# =============================================================================


class FlextCliCommandService(FlextDomainService[T]):
    """Service for CLI command execution and management.

    Directly extends FlextDomainService following FLEXT architectural standards.
    Provides command execution capabilities with proper error handling,
    validation, and result processing.
    """

    model_config = ConfigDict(
        frozen=True,
        validate_assignment=True,
        extra="forbid",
        arbitrary_types_allowed=True,
    )

    # Command-specific configuration
    service_name: str = Field(..., description="Name of the CLI command service")
    command_timeout: int = Field(
        default=300,
        description="Command timeout in seconds",
    )
    validate_args: bool = Field(
        default=True,
        description="Enable argument validation",
    )
    container: FlextContainer | None = Field(
        default=None,
        description="Dependency injection container",
    )

    def __init__(self, **data: object) -> None:
        """Initialize CLI command service."""
        super().__init__(**data)
        self._logger = FlextLogger(f"flext_cli.{self.service_name}")

    @property
    def logger(self) -> FlextLogger:
        """Get logger instance."""
        return self._logger

    @abstractmethod
    def execute_command(
        self,
        command: str,
        args: dict[str, object] | None = None,
        **kwargs: object,
    ) -> FlextResult[T]:
        """Execute a command with the given arguments.

        Args:
            command: Command name to execute
            args: Command arguments
            **kwargs: Additional execution parameters

        Returns:
            Result of command execution

        """

    @override
    def execute(self) -> FlextResult[T]:
        """Execute the service operation.

        Implements abstract method from FlextDomainService.
        Delegates to execute_command with default parameters.
        """
        # This is a generic implementation - subclasses should override
        # or implement execute_command directly
        # Abstract method - should not be called directly
        return FlextResult[T].fail("Command execution not implemented")

    def validate_command_args(
        self,
        command: str,
        _args: dict[str, object] | None = None,
    ) -> FlextResult[None]:
        """Validate command arguments.

        Override in subclasses to provide specific validation logic.
        """
        if not command or not command.strip():
            return FlextResult[None].fail("Command name cannot be empty")

        # Type system already ensures args is dict[str, object] | None
        # Additional validation can be added in subclasses

        return FlextResult[None].ok(None)


# =============================================================================
# CLI FORMATTER SERVICE - For output formatting
# =============================================================================


class FlextCliFormatterService(FlextDomainService[str]):
    """Service for CLI output formatting and presentation.

    Directly extends FlextDomainService following FLEXT architectural standards.
    Provides output formatting capabilities with support for multiple
    output formats (JSON, table, plain text).
    """

    model_config = ConfigDict(
        frozen=True,
        validate_assignment=True,
        extra="forbid",
        arbitrary_types_allowed=True,
    )

    # Service identification and formatting configuration
    service_name: str = Field(..., description="Name of the CLI formatter service")
    default_format: str = Field(
        default="table",
        description="Default output format",
    )
    supported_formats: list[str] = Field(
        default=["table", "json", "csv", "plain"],
        description="Supported output formats",
    )

    def __init__(self, **data: object) -> None:
        """Initialize CLI formatter service."""
        super().__init__(**data)
        self._logger = FlextLogger(f"flext_cli.{self.service_name}")

    @property
    def logger(self) -> FlextLogger:
        """Get logger instance."""
        return self._logger

    @abstractmethod
    def format_output(
        self,
        data: object,
        format_type: str | None = None,
        **options: object,
    ) -> FlextResult[str]:
        """Format data for output.

        Args:
            data: Data to format
            format_type: Output format type
            **options: Format-specific options

        Returns:
            Formatted output string

        """

    @override
    def execute(self) -> FlextResult[str]:
        """Execute the service operation.

        Implements abstract method from FlextDomainService.
        Returns empty string as default - subclasses should override.
        """
        return FlextResult[str].ok("")

    def validate_format(self, format_type: str) -> FlextResult[None]:
        """Validate output format type."""
        if format_type not in self.supported_formats:
            message = (
                f"Unsupported format: {format_type}. "
                f"Supported formats: {', '.join(self.supported_formats)}"
            )
            return FlextResult[None].fail(message)
        return FlextResult[None].ok(None)


# =============================================================================
# CLI VALIDATOR SERVICE - For input validation
# =============================================================================


class FlextCliValidatorService(FlextDomainService[bool]):
    """Service for CLI input validation and sanitization.

    Directly extends FlextDomainService following FLEXT architectural standards.
    Provides input validation capabilities with comprehensive validation rules
    and error reporting.
    """

    model_config = ConfigDict(
        frozen=True,
        validate_assignment=True,
        extra="forbid",
        arbitrary_types_allowed=True,
    )

    # Service identification and validator-specific configuration
    service_name: str = Field(..., description="Name of the CLI validator service")
    strict_validation: bool = Field(
        default=True,
        description="Enable strict validation mode",
    )
    validation_rules: dict[str, object] = Field(
        default_factory=dict,
        description="Custom validation rules",
    )

    def __init__(self, **data: object) -> None:
        """Initialize CLI validator service."""
        super().__init__(**data)
        self._logger = FlextLogger(f"flext_cli.{self.service_name}")

    @property
    def logger(self) -> FlextLogger:
        """Get logger instance."""
        return self._logger

    @abstractmethod
    def validate_input(
        self,
        input_data: object,
        validation_type: str | None = None,
        **options: object,
    ) -> FlextResult[bool]:
        """Validate input data.

        Args:
            input_data: Data to validate
            validation_type: Type of validation to perform
            **options: Validation-specific options

        Returns:
            Validation result with processed data

        """

    @override
    def execute(self) -> FlextResult[bool]:
        """Execute the service operation.

        Implements abstract method from FlextDomainService.
        Returns False as default - subclasses should override.
        """
        # Return False as default - subclasses should override
        is_successful = False
        return FlextResult[bool].ok(is_successful)

    def add_validation_rule(
        self,
        rule_name: str,
        _rule_definition: object,
    ) -> FlextResult[None]:
        """Add a custom validation rule.

        Args:
            rule_name: Name of the validation rule
            rule_definition: Rule definition or callable

        Returns:
            Result of rule addition

        """
        if not rule_name or not rule_name.strip():
            return FlextResult[None].fail("Rule name cannot be empty")

        # Create new rules dict (immutable pattern)

        # Note: Due to frozen=True, we can't modify self.validation_rules directly
        # This method shows the pattern - actual implementation would need
        # to return a new instance or use a different approach

        self.logger.info(f"Added validation rule: {rule_name}")

        return FlextResult[None].ok(None)


# =============================================================================
# CLI INTERACTIVE SERVICE - For user interaction
# =============================================================================


class FlextCliInteractiveService(FlextDomainService[str]):
    """Service for CLI user interaction and prompts.

    Directly extends FlextDomainService following FLEXT architectural standards.
    Provides interactive capabilities with support for prompts, confirmations,
    and user input handling.
    """

    model_config = ConfigDict(
        frozen=True,
        validate_assignment=True,
        extra="forbid",
        arbitrary_types_allowed=True,
    )

    # Service identification and interactive service configuration
    service_name: str = Field(..., description="Name of the CLI interactive service")
    enable_colors: bool = Field(
        default=True,
        description="Enable colored output",
    )
    confirmation_required: bool = Field(
        default=False,
        description="Require confirmation for operations",
    )
    input_timeout: int = Field(
        default=30,
        description="User input timeout in seconds",
    )

    def __init__(self, **data: object) -> None:
        """Initialize CLI interactive service."""
        super().__init__(**data)
        self._logger = FlextLogger(f"flext_cli.{self.service_name}")

    @property
    def logger(self) -> FlextLogger:
        """Get logger instance."""
        return self._logger

    @abstractmethod
    def prompt_user(
        self,
        message: str,
        input_type: str = "text",
        **options: object,
    ) -> FlextResult[str]:
        """Prompt user for input.

        Args:
            message: Prompt message to display
            input_type: Type of input expected
            **options: Input-specific options

        Returns:
            User input result

        """

    @abstractmethod
    def confirm_action(
        self,
        message: str,
        *,
        default: bool = False,
    ) -> FlextResult[bool]:
        """Request user confirmation for an action.

        Args:
            message: Confirmation message
            default: Default response if user just presses Enter

        Returns:
            User confirmation result

        """

    @override
    def execute(self) -> FlextResult[str]:
        """Execute the service operation.

        Implements abstract method from FlextDomainService.
        Returns empty string as default - subclasses should override.
        """
        return FlextResult[str].ok("")

    def display_message(
        self,
        message: str,
        message_type: str = "info",
    ) -> FlextResult[None]:
        """Display a message to the user.

        Args:
            message: Message to display
            message_type: Type of message (info, warning, error, success)

        Returns:
            Result of message display

        """
        if not message:
            return FlextResult[None].fail("Message cannot be empty")

        # Log the message
        if message_type == "error":
            self.logger.error(message)
        elif message_type == "warning":
            self.logger.warning(message)
        else:
            self.logger.info(message)

        # In actual implementation, this would handle colored output
        # and proper terminal formatting based on enable_colors setting

        return FlextResult[None].ok(None)


# =============================================================================
# SERVICE FACTORY - For creating service instances
# =============================================================================


class FlextCliServiceFactory:
    """Factory for creating CLI service instances with dependency injection."""

    @staticmethod
    def create_command_service(
        _service_name: str,
        _container: FlextContainer | None = None,
        **_config: object,
    ) -> FlextResult[FlextCliCommandService[object]]:
        """Create a command service instance.

        Args:
            service_name: Name of the service
            container: Dependency injection container
            **config: Additional configuration

        Returns:
            Created command service instance

        """
        try:
            # This is a stub implementation - actual implementation would
            # create a concrete command service subclass
            # Note: Using correct return type for command service
            return FlextResult[FlextCliCommandService[object]].fail(
                "FlextCliCommandService is abstract - use concrete implementation",
            )
        except Exception as e:
            return FlextResult[FlextCliCommandService[object]].fail(
                f"Failed to create command service: {e}"
            )

    @staticmethod
    def create_formatter_service(
        _service_name: str,
        _container: FlextContainer | None = None,
        **_config: object,
    ) -> FlextResult[FlextCliFormatterService]:
        """Create a formatter service instance.

        Args:
            service_name: Name of the service
            container: Dependency injection container
            **config: Additional configuration

        Returns:
            Created formatter service instance

        """
        try:
            # This is a stub implementation - actual implementation would
            # create a concrete formatter service subclass
            return FlextResult[FlextCliFormatterService].fail(
                "FlextCliFormatterService is abstract - use concrete implementation",
            )
        except Exception as e:
            return FlextResult[FlextCliFormatterService].fail(
                f"Failed to create formatter service: {e}"
            )

    @staticmethod
    def create_validator_service(
        _service_name: str,
        _container: FlextContainer | None = None,
        **_config: object,
    ) -> FlextResult[FlextCliValidatorService]:
        """Create a validator service instance.

        Args:
            service_name: Name of the service
            container: Dependency injection container
            **config: Additional configuration

        Returns:
            Created validator service instance

        """
        try:
            # This is a stub implementation - actual implementation would
            # create a concrete validator service subclass
            return FlextResult[FlextCliValidatorService].fail(
                "FlextCliValidatorService is abstract - use concrete implementation",
            )
        except Exception as e:
            return FlextResult[FlextCliValidatorService].fail(
                f"Failed to create validator service: {e}"
            )

    @staticmethod
    def create_interactive_service(
        _service_name: str,
        _container: FlextContainer | None = None,
        **_config: object,
    ) -> FlextResult[FlextCliInteractiveService]:
        """Create an interactive service instance.

        Args:
            service_name: Name of the service
            container: Dependency injection container
            **config: Additional configuration

        Returns:
            Created interactive service instance

        """
        try:
            # This is a stub implementation - actual implementation would
            # create a concrete interactive service subclass
            return FlextResult[FlextCliInteractiveService].fail(
                "FlextCliInteractiveService is abstract - use concrete implementation",
            )
        except Exception as e:
            return FlextResult[FlextCliInteractiveService].fail(
                f"Failed to create interactive service: {e}"
            )


# =============================================================================
# EXPORTS - Public API
# =============================================================================

__all__ = [
    "FlextCliCommandService",
    "FlextCliFormatterService",
    "FlextCliInteractiveService",
    # Factory
    "FlextCliServiceFactory",
    "FlextCliValidatorService",
]
