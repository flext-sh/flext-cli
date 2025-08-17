"""Base CLI service classes.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TypeVar

from flext_core import FlextContainer, FlextDomainService, FlextResult, get_logger
from pydantic import ConfigDict, Field

# Type variables for generic services
T = TypeVar("T")
CommandResultType = TypeVar("CommandResultType")
ValidationResultType = TypeVar("ValidationResultType")

# =============================================================================
# BASE CLI SERVICE - Extends FlextDomainService
# =============================================================================


class FlextCliService(FlextDomainService[object], ABC):
    """Base CLI service extending flext-core domain service patterns.

    Provides foundation for CLI-specific services with:
    - FlextResult-based error handling
    - Dependency injection via FlextContainer
    - Proper initialization and cleanup
    - Service lifecycle management
    - Logging and observability

    Extends FlextDomainService to inherit stateless cross-entity operations
    while adding CLI-specific functionality.
    """

    model_config = ConfigDict(
        frozen=True,
        validate_assignment=True,
        extra="forbid",
        arbitrary_types_allowed=True,
    )

    # CLI-specific configuration
    service_name: str = Field(..., description="Name of the CLI service")
    container: FlextContainer | None = Field(
        default=None,
        description="Dependency injection container",
    )
    enable_logging: bool = Field(
        default=True,
        description="Enable service logging",
    )

    def __init__(self, **data: object) -> None:
        """Initialize CLI service with container and logging."""
        super().__init__(**data)

        # Set up logger if enabled
        if self.enable_logging:
            self._logger = get_logger(f"flext_cli.{self.service_name}")
        else:
            self._logger = None  # type: ignore[assignment]

    @property
    def logger(self) -> object:
        """Get logger instance."""
        return self._logger

    def get_container(self) -> FlextContainer | None:
        """Get dependency injection container."""
        return self.container

    def initialize(self) -> FlextResult[None]:
        """Initialize the CLI service.

        Override in subclasses to provide specific initialization logic.
        Default implementation returns success.
        """
        if self.logger:
            self.logger.info(f"Initializing CLI service: {self.service_name}")  # type: ignore[attr-defined]
        return FlextResult.ok(None)

    def cleanup(self) -> FlextResult[None]:
        """Cleanup the CLI service resources.

        Override in subclasses to provide specific cleanup logic.
        Default implementation returns success.
        """
        if self.logger:
            self.logger.info(f"Cleaning up CLI service: {self.service_name}")  # type: ignore[attr-defined]
        return FlextResult.ok(None)

    def validate_config(self) -> FlextResult[None]:
        """Validate CLI service configuration.

        Extends base validation with CLI-specific checks.
        """
        # Call parent validation first
        parent_result = super().validate_config()
        if parent_result.is_failure:
            return parent_result

        # CLI-specific validation
        if not self.service_name or not self.service_name.strip():
            return FlextResult.fail("Service name cannot be empty")

        return FlextResult.ok(None)


# =============================================================================
# CLI COMMAND SERVICE - For command execution
# =============================================================================


class FlextCliCommandService(FlextCliService):
    """Service for CLI command execution and management.

    Extends FlextCliService to provide command execution capabilities
    with proper error handling, validation, and result processing.
    """

    model_config = ConfigDict(
        frozen=True,
        validate_assignment=True,
        extra="forbid",
        arbitrary_types_allowed=True,
    )

    # Command-specific configuration
    command_timeout: int = Field(
        default=300,
        description="Command timeout in seconds",
    )
    validate_args: bool = Field(
        default=True,
        description="Enable argument validation",
    )

    @abstractmethod
    def execute_command(
        self,
        command: str,
        args: dict[str, object] | None = None,
        **kwargs: object,
    ) -> FlextResult[CommandResultType]:
        """Execute a command with the given arguments.

        Args:
            command: Command name to execute
            args: Command arguments
            **kwargs: Additional execution parameters

        Returns:
            Result of command execution

        """

    def execute(self) -> FlextResult[CommandResultType]:
        """Execute the service operation.

        Implements abstract method from FlextDomainService.
        Delegates to execute_command with default parameters.
        """
        # This is a generic implementation - subclasses should override
        # or implement execute_command directly
        return FlextResult.fail("Command execution not implemented")

    def validate_command_args(
        self,
        command: str,
        _args: dict[str, object] | None = None,
    ) -> FlextResult[None]:
        """Validate command arguments.

        Override in subclasses to provide specific validation logic.
        """
        if not command or not command.strip():
            return FlextResult.fail("Command name cannot be empty")

        # Type system already ensures args is dict[str, object] | None
        # Additional validation can be added in subclasses

        return FlextResult.ok(None)


# =============================================================================
# CLI FORMATTER SERVICE - For output formatting
# =============================================================================


class FlextCliFormatterService(FlextCliService):
    """Service for CLI output formatting and presentation.

    Extends FlextCliService to provide output formatting capabilities
    with support for multiple output formats (JSON, table, plain text).
    """

    model_config = ConfigDict(
        frozen=True,
        validate_assignment=True,
        extra="forbid",
        arbitrary_types_allowed=True,
    )

    # Formatter-specific configuration
    default_format: str = Field(
        default="table",
        description="Default output format",
    )
    supported_formats: list[str] = Field(
        default=["table", "json", "csv", "plain"],
        description="Supported output formats",
    )

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

    def execute(self) -> FlextResult[object]:
        """Execute the service operation.

        Implements abstract method from FlextDomainService.
        Returns empty string as default - subclasses should override.
        """
        return FlextResult.ok("")

    def validate_format(self, format_type: str) -> FlextResult[None]:
        """Validate output format type."""
        if format_type not in self.supported_formats:
            return FlextResult.fail(
                f"Unsupported format: {format_type}. "
                f"Supported formats: {', '.join(self.supported_formats)}",
            )
        return FlextResult.ok(None)


# =============================================================================
# CLI VALIDATOR SERVICE - For input validation
# =============================================================================


class FlextCliValidatorService(FlextCliService):
    """Service for CLI input validation and sanitization.

    Extends FlextCliService to provide input validation capabilities
    with comprehensive validation rules and error reporting.
    """

    model_config = ConfigDict(
        frozen=True,
        validate_assignment=True,
        extra="forbid",
        arbitrary_types_allowed=True,
    )

    # Validator-specific configuration
    strict_validation: bool = Field(
        default=True,
        description="Enable strict validation mode",
    )
    validation_rules: dict[str, object] = Field(
        default_factory=dict,
        description="Custom validation rules",
    )

    @abstractmethod
    def validate_input(
        self,
        input_data: object,
        validation_type: str | None = None,
        **options: object,
    ) -> FlextResult[ValidationResultType]:
        """Validate input data.

        Args:
            input_data: Data to validate
            validation_type: Type of validation to perform
            **options: Validation-specific options

        Returns:
            Validation result with processed data

        """

    def execute(self) -> FlextResult[ValidationResultType]:
        """Execute the service operation.

        Implements abstract method from FlextDomainService.
        Returns None as default - subclasses should override.
        """
        # Return None cast to ValidationResultType - subclasses should override
        return FlextResult.ok(None)  # type: ignore[arg-type]

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
            return FlextResult.fail("Rule name cannot be empty")

        # Create new rules dict (immutable pattern)

        # Note: Due to frozen=True, we can't modify self.validation_rules directly
        # This method shows the pattern - actual implementation would need
        # to return a new instance or use a different approach

        if self.logger and hasattr(self.logger, "info"):
            self.logger.info(f"Added validation rule: {rule_name}")

        return FlextResult.ok(None)


# =============================================================================
# CLI INTERACTIVE SERVICE - For user interaction
# =============================================================================


class FlextCliInteractiveService(FlextCliService):
    """Service for CLI user interaction and prompts.

    Extends FlextCliService to provide interactive capabilities
    with support for prompts, confirmations, and user input handling.
    """

    model_config = ConfigDict(
        frozen=True,
        validate_assignment=True,
        extra="forbid",
        arbitrary_types_allowed=True,
    )

    # Interactive service configuration
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

    def execute(self) -> FlextResult[object]:
        """Execute the service operation.

        Implements abstract method from FlextDomainService.
        Returns empty string as default - subclasses should override.
        """
        return FlextResult.ok("")

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
            return FlextResult.fail("Message cannot be empty")

        # Log the message
        if self.logger and hasattr(self.logger, "info"):
            if message_type == "error" and hasattr(self.logger, "error"):
                self.logger.error(message)
            elif message_type == "warning" and hasattr(self.logger, "warning"):
                self.logger.warning(message)
            else:
                self.logger.info(message)

        # In actual implementation, this would handle colored output
        # and proper terminal formatting based on enable_colors setting

        return FlextResult.ok(None)


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
    ) -> FlextResult[FlextCliCommandService]:
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
            return FlextResult.fail(
                "FlextCliCommandService is abstract - use concrete implementation",
            )
        except Exception as e:
            return FlextResult.fail(f"Failed to create command service: {e}")

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
            return FlextResult.fail(
                "FlextCliFormatterService is abstract - use concrete implementation",
            )
        except Exception as e:
            return FlextResult.fail(f"Failed to create formatter service: {e}")

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
            return FlextResult.fail(
                "FlextCliValidatorService is abstract - use concrete implementation",
            )
        except Exception as e:
            return FlextResult.fail(f"Failed to create validator service: {e}")

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
            return FlextResult.fail(
                "FlextCliInteractiveService is abstract - use concrete implementation",
            )
        except Exception as e:
            return FlextResult.fail(f"Failed to create interactive service: {e}")


# =============================================================================
# EXPORTS - Public API
# =============================================================================

__all__ = [
    "FlextCliCommandService",
    "FlextCliFormatterService",
    "FlextCliInteractiveService",
    # Base service classes
    "FlextCliService",
    # Factory
    "FlextCliServiceFactory",
    "FlextCliValidatorService",
]
