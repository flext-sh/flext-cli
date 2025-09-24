"""FLEXT CLI Protocols - Single unified class following FLEXT standards.

Provides CLI-specific protocol definitions using flext-core patterns.
Single FlextCliProtocols class with nested protocol subclasses following FLEXT pattern.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Protocol

from flext_cli.typings import FlextCliTypings
from flext_core import FlextProtocols, FlextResult


class FlextCliProtocols(FlextProtocols):
    """Single unified CLI protocols class following FLEXT standards.

    Contains all protocol definitions for CLI domain operations.
    Follows FLEXT pattern: one class per module with nested subclasses.
    """

    class CliCommandHandler(Protocol):
        """Protocol for CLI command handlers."""

        def __call__(
            self, **kwargs: object
        ) -> FlextResult[FlextCliTypings.CliCommandResult]:
            """Execute CLI command with arguments.

            Args:
                **kwargs: Command arguments

            Returns:
                FlextResult[FlextCliTypings.CliCommandResult]: Command execution result

            """
            ...

    class CliFormatter(Protocol):
        """Protocol for CLI output formatters."""

        def format_data(
            self, data: FlextCliTypings.CliFormatData, **options: object
        ) -> FlextResult[str]:
            """Format data for CLI output.

            Args:
                data: Data to format
                **options: Formatting options

            Returns:
                FlextResult[str]: Formatted output or error

            """
            ...

    class CliConfigProvider(Protocol):
        """Protocol for CLI configuration providers."""

        def load_config(self) -> FlextResult[FlextCliTypings.CliConfigData]:
            """Load CLI configuration.

            Returns:
                FlextResult[FlextCliTypings.CliConfigData]: Configuration data or error

            """
            ...

        def save_config(
            self, config: FlextCliTypings.CliConfigData
        ) -> FlextResult[None]:
            """Save CLI configuration.

            Args:
                config: Configuration data to save

            Returns:
                FlextResult[None]: Success or error

            """
            ...

    class CliAuthenticator(Protocol):
        """Protocol for CLI authentication providers."""

        def authenticate(
            self, credentials: FlextCliTypings.CliConfigData
        ) -> FlextResult[str]:
            """Authenticate and return token.

            Args:
                credentials: Authentication credentials

            Returns:
                FlextResult[str]: Authentication token or error

            """
            ...

        def validate_token(self, token: str) -> FlextResult[bool]:
            """Validate authentication token.

            Args:
                token: Token to validate

            Returns:
                FlextResult[bool]: Validation result or error

            """
            ...

    class CliDebugProvider(Protocol):
        """Protocol for CLI debug information providers."""

        def get_debug_info(self) -> FlextResult[FlextCliTypings.CliConfigData]:
            """Get debug information.

            Returns:
                FlextResult[FlextCliTypings.CliConfigData]: Debug information or error

            """
            ...


__all__ = [
    "FlextCliProtocols",
]
