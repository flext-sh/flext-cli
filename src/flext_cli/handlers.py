"""FLEXT CLI Handlers - Single unified class following FLEXT standards.

Provides CLI-specific handler implementations using flext-core patterns.
Single FlextCliHandlers class with nested handler subclasses following FLEXT pattern.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Callable
from typing import override

from flext_core import FlextCore
from pydantic import BaseModel

from flext_cli.models import FlextCliModels
from flext_cli.protocols import FlextCliProtocols
from flext_cli.typings import FlextCliTypes


class FlextCliHandlers(FlextCore.Handlers):
    """Single unified CLI handlers class following FLEXT standards.

    Contains all handler implementations for CLI domain operations.
    Follows FLEXT pattern: one class per module with nested subclasses.

    ARCHITECTURAL COMPLIANCE:
    - Inherits from FlextCore.Handlers to avoid duplication
    - Uses centralized handler patterns from FlextCore.Handlers
    - Implements CLI-specific extensions while reusing core functionality
    - Provides execute() for CLI handler operations
    """

    def __init__(self, **kwargs: object) -> None:
        """Initialize CLI handlers with optional configuration.

        Args:
            **kwargs: Additional handler initialization data

        """
        # If no config provided, create minimal default config
        config = kwargs.pop("config", None)
        if config is None:
            config = FlextCore.Models.CqrsConfig.Handler(
                handler_id="flext-cli-handlers",
                handler_name="flext-cli-handlers",
                handler_type="command",  # Explicit handler type
            )
        super().__init__(config=config, **kwargs)

    def execute_service(self) -> FlextCore.Result[FlextCore.Types.Dict]:
        """Execute handlers service to return operational status.

        Provides no-arg service status check for CLI handlers.
        Note: Use handle() from FlextCore.Handlers for message processing.

        Returns:
            FlextCore.Result[FlextCore.Types.Dict]: Handler service status

        """
        return self.execute_handlers()

    # ========================================================================
    # MODEL-DRIVEN HANDLER REGISTRATION - Auto-generate handlers from models
    # ========================================================================

    class ModelHandlerFactory:
        """Factory for creating model-driven CLI handlers.

        Automatically generates handlers from Pydantic models with integrated
        validation, reducing boilerplate and ensuring type safety.

        ARCHITECTURAL PATTERN:
        - Introspect Pydantic model to determine handler behavior
        - Generate handler function with automatic validation
        - Register handler with CLI system
        - Provide declarative handler registration via decorators

        USAGE:
            factory = ModelHandlerFactory()
            handler = factory.create_command_handler(ConfigModel, config_logic)
            # Handler now validates input with ConfigModel automatically
        """

        @staticmethod
        def create_model_handler(
            model_class: type[BaseModel],
            handler_func: Callable[[BaseModel], FlextCore.Result[object]],
        ) -> Callable[[dict[str, object]], FlextCore.Result[object]]:
            """Create a handler that validates input with Pydantic model.

            Args:
                model_class: Pydantic model class for validation
                handler_func: Handler function that receives validated model instance

            Returns:
                Handler function with integrated model validation

            """

            def model_validated_handler(
                cli_data: dict[str, object],
            ) -> FlextCore.Result[object]:
                # Validate CLI data with model
                validation_result = (
                    FlextCliModels.CliModelConverter.validate_cli_data_with_model(
                        model_class, cli_data
                    )
                )

                if validation_result.is_failure:
                    return FlextCore.Result[object].fail(
                        f"Input validation failed: {validation_result.error}"
                    )

                validated_model = validation_result.unwrap()

                # Execute handler with validated model
                return handler_func(validated_model)

            return model_validated_handler

        @staticmethod
        def create_command_handler_from_model(
            model_class: type[BaseModel],
            command_logic: Callable[
                [BaseModel], FlextCore.Result[FlextCliTypes.Data.CliCommandResult]
            ],
        ) -> FlextCliHandlers.CommandHandler:
            """Create CommandHandler from Pydantic model and logic function.

            Args:
                model_class: Pydantic model defining command parameters
                command_logic: Function implementing command logic

            Returns:
                CommandHandler instance with model validation

            Example:
                def configure_db(config: DatabaseConfig) -> FlextCore.Result[dict]:
                    # config is validated DatabaseConfig instance
                    return FlextCore.Result[dict].ok({"status": "configured"})

                handler = factory.create_command_handler_from_model(
                    DatabaseConfig, configure_db
                )

            """

            def handler_func(
                **kwargs: object,
            ) -> FlextCore.Result[FlextCliTypes.Data.CliCommandResult]:
                # Validate with model
                validation_result = (
                    FlextCliModels.CliModelConverter.validate_cli_data_with_model(
                        model_class, kwargs
                    )
                )

                if validation_result.is_failure:
                    return FlextCore.Result[FlextCliTypes.Data.CliCommandResult].fail(
                        f"Validation failed: {validation_result.error}"
                    )

                validated_model = validation_result.unwrap()

                # Execute command logic
                return command_logic(validated_model)

            return FlextCliHandlers.CommandHandler(handler_func)

        @staticmethod
        def register_model_handler(
            handler_registry: dict[str, Callable[..., object]],
            command_name: str,
            model_class: type[BaseModel],
            handler_func: Callable[[BaseModel], FlextCore.Result[object]],
        ) -> FlextCore.Result[None]:
            """Register model-driven handler in handler registry.

            Args:
                handler_registry: Dictionary mapping command names to handlers
                command_name: Name for the command
                model_class: Pydantic model for validation
                handler_func: Handler implementation

            Returns:
                FlextCore.Result indicating success or failure

            """
            try:
                # Create model-validated handler
                validated_handler = (
                    FlextCliHandlers.ModelHandlerFactory.create_model_handler(
                        model_class, handler_func
                    )
                )

                # Register in registry
                handler_registry[command_name] = validated_handler

                return FlextCore.Result[None].ok(None)
            except Exception as e:
                return FlextCore.Result[None].fail(f"Handler registration failed: {e}")

    class ModelHandlerDecorators:
        """Decorators for model-driven handler registration.

        Provides declarative syntax for creating handlers from models.

        USAGE:
            @model_command_handler(DatabaseConfig)
            def setup_database(config: DatabaseConfig) -> FlextCore.Result[dict]:
                # config is validated
                return FlextCore.Result[dict].ok({"status": "ok"})
        """

        @staticmethod
        def model_command_handler(
            model_class: type[BaseModel],
        ) -> Callable[
            [Callable[[BaseModel], FlextCore.Result[object]]],
            Callable[[dict[str, object]], FlextCore.Result[object]],
        ]:
            """Decorator to create model-validated command handler.

            Args:
                model_class: Pydantic model for parameter validation

            Returns:
                Decorator that wraps handler with model validation

            """

            def decorator(
                func: Callable[[BaseModel], FlextCore.Result[object]],
            ) -> Callable[[dict[str, object]], FlextCore.Result[object]]:
                return FlextCliHandlers.ModelHandlerFactory.create_model_handler(
                    model_class, func
                )

            return decorator

    class CommandHandler(FlextCliProtocols.Commands.CliCommandHandler):
        """CLI command handler implementation - implements CliCommandHandler protocol."""

        @override
        def __init__(
            self,
            handler_func: Callable[
                ..., FlextCore.Result[FlextCliTypes.Data.CliCommandResult]
            ],
        ) -> None:
            """Initialize command handler with handler function."""
            self._handler_func = handler_func

        def __call__(
            self, **kwargs: FlextCliTypes.Data.CliCommandArgs
        ) -> FlextCore.Result[FlextCliTypes.Data.CliCommandResult]:
            """Execute CLI command with arguments.

            Args:
                **kwargs: Command arguments

            Returns:
                FlextCore.Result[FlextCliTypes.Data.CliCommandResult]: Command execution result

            """
            try:
                result = self._handler_func(**kwargs)
                if isinstance(result, FlextCore.Result):
                    return result
                return FlextCore.Result[FlextCliTypes.Data.CliCommandResult].ok(result)
            except Exception as e:
                return FlextCore.Result[FlextCliTypes.Data.CliCommandResult].fail(
                    f"Command execution failed: {e}"
                )

    class FormatterHandler(FlextCliProtocols.Application.CliFormatter):
        """CLI formatter handler implementation - implements CliFormatter protocol."""

        @override
        def __init__(
            self, formatter_func: Callable[[FlextCliTypes.Data.CliFormatData], str]
        ) -> None:
            """Initialize formatter handler with formatter function."""
            self._formatter_func = formatter_func

        def format_data(
            self,
            data: FlextCliTypes.Data.CliFormatData,
            **options: FlextCliTypes.Data.CliConfigData,
        ) -> FlextCore.Result[str]:
            """Format data for CLI output.

            Args:
                data: Data to format
                **options: Formatting options

            Returns:
                FlextCore.Result[str]: Formatted output or error

            """
            try:
                formatted = self._formatter_func(data, **options)
                return FlextCore.Result[str].ok(formatted)
            except Exception as e:
                return FlextCore.Result[str].fail(f"Formatting failed: {e}")

    class ConfigHandler(FlextCliProtocols.Infrastructure.CliConfigProvider):
        """CLI configuration handler implementation - implements CliConfigProvider protocol."""

        @override
        def __init__(self, config_data: FlextCliTypes.Data.CliConfigData) -> None:
            """Initialize config handler with configuration data."""
            self._config_data = config_data

        def load_config(self) -> FlextCore.Result[FlextCliTypes.Data.CliConfigData]:
            """Load CLI configuration.

            Returns:
                FlextCore.Result[FlextCliTypes.Data.CliConfigData]: Configuration data or error

            """
            try:
                return FlextCore.Result[FlextCliTypes.Data.CliConfigData].ok(
                    self._config_data
                )
            except Exception as e:
                return FlextCore.Result[FlextCliTypes.Data.CliConfigData].fail(
                    f"Config load failed: {e}"
                )

        def save_config(
            self, config: FlextCliTypes.Data.CliConfigData
        ) -> FlextCore.Result[None]:
            """Save CLI configuration.

            Args:
                config: Configuration data to save

            Returns:
                FlextCore.Result[None]: Success or error

            """
            try:
                self._config_data = config
                return FlextCore.Result[None].ok(None)
            except Exception as e:
                return FlextCore.Result[None].fail(f"Config save failed: {e}")

    class AuthHandler(FlextCliProtocols.Infrastructure.CliAuthenticator):
        """CLI authentication handler implementation - implements CliAuthenticator protocol."""

        @override
        def __init__(
            self, auth_func: Callable[[FlextCliTypes.Data.AuthConfigData], str]
        ) -> None:
            """Initialize auth handler with authentication function."""
            self._auth_func = auth_func

        def authenticate(
            self, credentials: FlextCliTypes.Data.AuthConfigData
        ) -> FlextCore.Result[str]:
            """Authenticate and return token.

            Args:
                credentials: Authentication credentials

            Returns:
                FlextCore.Result[str]: Authentication token or error

            """
            try:
                token = self._auth_func(credentials)
                return FlextCore.Result[str].ok(token)
            except Exception as e:
                return FlextCore.Result[str].fail(f"Authentication failed: {e}")

        def validate_token(self, token: str) -> FlextCore.Result[bool]:
            """Validate authentication token.

            Args:
                token: Token to validate

            Returns:
                FlextCore.Result[bool]: Validation result or error

            """
            try:
                # Simple validation - in real implementation would check token validity
                min_token_length = 10
                is_valid = bool(token and len(token) > min_token_length)
                return FlextCore.Result[bool].ok(is_valid)
            except Exception as e:
                return FlextCore.Result[bool].fail(f"Token validation failed: {e}")

    class DebugHandler(FlextCliProtocols.Extensions.CliDebugProvider):
        """CLI debug handler implementation - implements CliDebugProvider protocol."""

        @override
        def __init__(self, debug_data: FlextCliTypes.Data.DebugInfoData) -> None:
            """Initialize debug handler with debug data."""
            self._debug_data: FlextCliTypes.Data.DebugInfoData = debug_data

        def get_debug_info(
            self,
        ) -> FlextCore.Result[FlextCliTypes.Data.DebugInfoData]:
            """Get debug information.

            Returns:
                FlextCore.Result[FlextCliTypes.Data.DebugInfoData]: Debug information or error

            """
            try:
                return FlextCore.Result[FlextCliTypes.Data.DebugInfoData].ok(
                    self._debug_data
                )
            except Exception as e:
                return FlextCore.Result[FlextCliTypes.Data.DebugInfoData].fail(
                    f"Debug info retrieval failed: {e}"
                )

    @override
    def handle(self, message: object) -> FlextCore.Result[object]:
        """Handle message processing - required by FlextCore.Handlers abstract class.

        Args:
            message: Message to handle

        Returns:
            FlextCore.Result[object]: Processing result or error

        """
        try:
            # CLI-specific message handling implementation
            if isinstance(message, dict):
                return FlextCore.Result[object].ok(message)
            return FlextCore.Result[object].ok({"message": str(message)})
        except Exception as e:
            return FlextCore.Result[object].fail(f"Message handling failed: {e}")

    def execute_handlers(self) -> FlextCore.Result[FlextCliTypes.Data.CliCommandResult]:
        """Execute CLI handlers health check operation.

        Provides CLI-specific handler status check.
        Note: Use handle() or execute() from FlextCore.Handlers for message processing.

        Returns:
            FlextCore.Result[FlextCliTypes.Data.CliCommandResult]: Handler status or error

        """
        try:
            # Create a simple command result indicating handlers are operational
            result_data: FlextCliTypes.Data.CliCommandResult = {
                "status": "operational",
                "service": "flext-cli-handlers",
                "timestamp": "2025-01-08T00:00:00Z",
                "handlers_available": [
                    "CommandHandler",
                    "FormatterHandler",
                    "ConfigHandler",
                    "AuthHandler",
                    "DebugHandler",
                ],
            }
            return FlextCore.Result[FlextCliTypes.Data.CliCommandResult].ok(result_data)
        except Exception as e:
            return FlextCore.Result[FlextCliTypes.Data.CliCommandResult].fail(
                f"Handlers execution failed: {e}"
            )


__all__ = [
    "FlextCliHandlers",
]
