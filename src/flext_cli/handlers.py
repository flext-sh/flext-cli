"""FLEXT CLI Handlers - Single unified class following FLEXT standards.

Provides CLI-specific handler implementations using flext-core patterns.
Single FlextCliHandlers class with nested handler subclasses following FLEXT pattern.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Callable
from typing import override

from flext_cli.protocols import FlextCliProtocols
from flext_cli.typings import FlextCliTypes
from flext_core import FlextHandlers, FlextModels, FlextResult


class FlextCliHandlers(FlextHandlers):
    """Single unified CLI handlers class following FLEXT standards.

    Contains all handler implementations for CLI domain operations.
    Follows FLEXT pattern: one class per module with nested subclasses.

    ARCHITECTURAL COMPLIANCE:
    - Inherits from FlextHandlers to avoid duplication
    - Uses centralized handler patterns from FlextHandlers
    - Implements CLI-specific extensions while reusing core functionality
    - Provides execute() for CLI handler operations
    """

    def __init__(self, **kwargs: object) -> None:
        """Initialize CLI handlers with optional configuration.

        Args:
            **kwargs: Additional handler initialization data

        """
        # If no config provided, create minimal default config
        if "config" not in kwargs:
            kwargs["config"] = FlextModels.CqrsConfig.Handler(
                handler_id="flext-cli-handlers",
                handler_name="flext-cli-handlers",
            )
        super().__init__(**kwargs)

    def execute_service(self) -> FlextResult[dict]:
        """Execute handlers service to return operational status.

        Provides no-arg service status check for CLI handlers.
        Note: Use handle() from FlextHandlers for message processing.

        Returns:
            FlextResult[dict]: Handler service status

        """
        return self.execute_handlers()

    class CommandHandler(FlextCliProtocols.CliCommandHandler):
        """CLI command handler implementation - implements CliCommandHandler protocol."""

        @override
        def __init__(
            self,
            handler_func: Callable[
                ..., FlextResult[FlextCliTypes.Data.CliCommandResult]
            ],
        ) -> None:
            """Initialize command handler with handler function."""
            self._handler_func = handler_func

        def __call__(
            self, **kwargs: FlextCliTypes.Data.CliCommandArgs
        ) -> FlextResult[FlextCliTypes.Data.CliCommandResult]:
            """Execute CLI command with arguments.

            Args:
                **kwargs: Command arguments

            Returns:
                FlextResult[FlextCliTypes.Data.CliCommandResult]: Command execution result

            """
            try:
                result = self._handler_func(**kwargs)
                if isinstance(result, FlextResult):
                    return result
                return FlextResult[FlextCliTypes.Data.CliCommandResult].ok(result)
            except Exception as e:
                return FlextResult[FlextCliTypes.Data.CliCommandResult].fail(
                    f"Command execution failed: {e}"
                )

    class FormatterHandler(FlextCliProtocols.CliFormatter):
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
        ) -> FlextResult[str]:
            """Format data for CLI output.

            Args:
                data: Data to format
                **options: Formatting options

            Returns:
                FlextResult[str]: Formatted output or error

            """
            try:
                formatted = self._formatter_func(data, **options)
                return FlextResult[str].ok(formatted)
            except Exception as e:
                return FlextResult[str].fail(f"Formatting failed: {e}")

    class ConfigHandler(FlextCliProtocols.CliConfigProvider):
        """CLI configuration handler implementation - implements CliConfigProvider protocol."""

        @override
        def __init__(self, config_data: FlextCliTypes.Data.CliConfigData) -> None:
            """Initialize config handler with configuration data."""
            self._config_data = config_data

        def load_config(self) -> FlextResult[FlextCliTypes.Data.CliConfigData]:
            """Load CLI configuration.

            Returns:
                FlextResult[FlextCliTypes.Data.CliConfigData]: Configuration data or error

            """
            try:
                return FlextResult[FlextCliTypes.Data.CliConfigData].ok(
                    self._config_data
                )
            except Exception as e:
                return FlextResult[FlextCliTypes.Data.CliConfigData].fail(
                    f"Config load failed: {e}"
                )

        def save_config(
            self, config: FlextCliTypes.Data.CliConfigData
        ) -> FlextResult[None]:
            """Save CLI configuration.

            Args:
                config: Configuration data to save

            Returns:
                FlextResult[None]: Success or error

            """
            try:
                self._config_data = config
                return FlextResult[None].ok(None)
            except Exception as e:
                return FlextResult[None].fail(f"Config save failed: {e}")

    class AuthHandler(FlextCliProtocols.CliAuthenticator):
        """CLI authentication handler implementation - implements CliAuthenticator protocol."""

        @override
        def __init__(
            self, auth_func: Callable[[FlextCliTypes.Data.AuthConfigData], str]
        ) -> None:
            """Initialize auth handler with authentication function."""
            self._auth_func = auth_func

        def authenticate(
            self, credentials: FlextCliTypes.Data.AuthConfigData
        ) -> FlextResult[str]:
            """Authenticate and return token.

            Args:
                credentials: Authentication credentials

            Returns:
                FlextResult[str]: Authentication token or error

            """
            try:
                token = self._auth_func(credentials)
                return FlextResult[str].ok(token)
            except Exception as e:
                return FlextResult[str].fail(f"Authentication failed: {e}")

        def validate_token(self, token: str) -> FlextResult[bool]:
            """Validate authentication token.

            Args:
                token: Token to validate

            Returns:
                FlextResult[bool]: Validation result or error

            """
            try:
                # Simple validation - in real implementation would check token validity
                min_token_length = 10
                is_valid = bool(token and len(token) > min_token_length)
                return FlextResult[bool].ok(is_valid)
            except Exception as e:
                return FlextResult[bool].fail(f"Token validation failed: {e}")

    class DebugHandler(FlextCliProtocols.CliDebugProvider):
        """CLI debug handler implementation - implements CliDebugProvider protocol."""

        @override
        def __init__(self, debug_data: FlextCliTypes.Data.DebugInfoData) -> None:
            """Initialize debug handler with debug data."""
            self._debug_data: FlextCliTypes.Data.DebugInfoData = debug_data

        def get_debug_info(
            self,
        ) -> FlextResult[FlextCliTypes.Data.DebugInfoData]:
            """Get debug information.

            Returns:
                FlextResult[FlextCliTypes.Data.DebugInfoData]: Debug information or error

            """
            try:
                return FlextResult[FlextCliTypes.Data.DebugInfoData].ok(
                    self._debug_data
                )
            except Exception as e:
                return FlextResult[FlextCliTypes.Data.DebugInfoData].fail(
                    f"Debug info retrieval failed: {e}"
                )

    @override
    def handle(self, message: object) -> FlextResult[object]:
        """Handle message processing - required by FlextHandlers abstract class.

        Args:
            message: Message to handle

        Returns:
            FlextResult[object]: Processing result or error

        """
        try:
            # CLI-specific message handling implementation
            if isinstance(message, dict):
                return FlextResult[object].ok(message)
            return FlextResult[object].ok({"message": str(message)})
        except Exception as e:
            return FlextResult[object].fail(f"Message handling failed: {e}")

    def execute_handlers(self) -> FlextResult[FlextCliTypes.Data.CliCommandResult]:
        """Execute CLI handlers health check operation.

        Provides CLI-specific handler status check.
        Note: Use handle() or execute() from FlextHandlers for message processing.

        Returns:
            FlextResult[FlextCliTypes.Data.CliCommandResult]: Handler status or error

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
            return FlextResult[FlextCliTypes.Data.CliCommandResult].ok(result_data)
        except Exception as e:
            return FlextResult[FlextCliTypes.Data.CliCommandResult].fail(
                f"Handlers execution failed: {e}"
            )


__all__ = [
    "FlextCliHandlers",
]
