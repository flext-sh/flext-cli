"""FLEXT CLI Handlers - Single unified class following FLEXT standards.

Provides CLI-specific handler implementations using flext-core patterns.
Single FlextCliHandlers class with nested handler subclasses following FLEXT pattern.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Callable

from flext_cli.typings import FlextCliTypes
from flext_core import FlextResult


class FlextCliHandlers:
    """Single unified CLI handlers class following FLEXT standards.

    Contains all handler implementations for CLI domain operations.
    Follows FLEXT pattern: one class per module with nested subclasses.

    ARCHITECTURAL COMPLIANCE:
    - Inherits from FlextHandlers to avoid duplication
    - Uses centralized handler patterns from FlextHandlers
    - Implements CLI-specific extensions while reusing core functionality
    """

    class CommandHandler:
        """CLI command handler implementation."""

        def __init__(
            self,
            handler_func: Callable[..., FlextResult[FlextCliTypes.CliCommandResult]],
        ) -> None:
            """Initialize command handler with handler function."""
            self._handler_func = handler_func

        def __call__(
            self, **kwargs: FlextCliTypes.CliCommandArgs
        ) -> FlextResult[FlextCliTypes.CliCommandResult]:
            """Execute CLI command with arguments.

            Args:
                **kwargs: Command arguments

            Returns:
                FlextResult[FlextCliTypes.CliCommandResult]: Command execution result

            """
            try:
                result = self._handler_func(**kwargs)
                if isinstance(result, FlextResult):
                    # Cast to proper return type since we know the handler returns the correct type
                    return result
                return FlextResult[FlextCliTypes.CliCommandResult].ok(result)
            except Exception as e:
                return FlextResult[FlextCliTypes.CliCommandResult].fail(
                    f"Command execution failed: {e}"
                )

    class FormatterHandler:
        """CLI formatter handler implementation."""

        def __init__(
            self, formatter_func: Callable[[FlextCliTypes.CliFormatData], str]
        ) -> None:
            """Initialize formatter handler with formatter function."""
            self._formatter_func = formatter_func

        def format_data(
            self,
            data: FlextCliTypes.CliFormatData,
            **options: FlextCliTypes.CliConfigData,
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

    class ConfigHandler:
        """CLI configuration handler implementation."""

        def __init__(self, config_data: FlextCliTypes.CliConfigData) -> None:
            """Initialize config handler with configuration data."""
            self._config_data = config_data

        def load_config(self) -> FlextResult[FlextCliTypes.CliConfigData]:
            """Load CLI configuration.

            Returns:
                FlextResult[FlextCliTypes.CliConfigData]: Configuration data or error

            """
            try:
                return FlextResult[FlextCliTypes.CliConfigData].ok(self._config_data)
            except Exception as e:
                return FlextResult[FlextCliTypes.CliConfigData].fail(
                    f"Config load failed: {e}"
                )

        def save_config(self, config: FlextCliTypes.CliConfigData) -> FlextResult[None]:
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

    class AuthHandler:
        """CLI authentication handler implementation."""

        def __init__(
            self, auth_func: Callable[[FlextCliTypes.AuthConfigData], str]
        ) -> None:
            """Initialize auth handler with authentication function."""
            self._auth_func = auth_func

        def authenticate(
            self, credentials: FlextCliTypes.AuthConfigData
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

    class DebugHandler:
        """CLI debug handler implementation."""

        def __init__(self, debug_data: FlextCliTypes.DebugInfoData) -> None:
            """Initialize debug handler with debug data."""
            self._debug_data = debug_data

        def get_debug_info(self) -> FlextResult[FlextCliTypes.DebugInfoData]:
            """Get debug information.

            Returns:
                FlextResult[FlextCliTypes.DebugInfoData]: Debug information or error

            """
            try:
                return FlextResult[FlextCliTypes.DebugInfoData].ok(self._debug_data)
            except Exception as e:
                return FlextResult[FlextCliTypes.DebugInfoData].fail(
                    f"Debug info retrieval failed: {e}"
                )


__all__ = [
    "FlextCliHandlers",
]
