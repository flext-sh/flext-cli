"""FLEXT CLI Protocols - Single unified class following FLEXT standards.

Provides CLI-specific protocol definitions using flext-core patterns.
Single FlextCliProtocols class with nested protocol subclasses following FLEXT pattern.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from flext_cli.typings import FlextCliTypes
from flext_core import FlextProtocols, FlextResult


class FlextCliProtocols:
    """Single unified CLI protocols class following FLEXT standards.

    Contains all protocol definitions for CLI domain operations.
    Follows FLEXT pattern: one class per module with nested subclasses.
    """

    # =========================================================================
    # RE-EXPORT FOUNDATION PROTOCOLS - Use FlextProtocols from flext-core
    # =========================================================================

    Foundation = FlextProtocols.Foundation
    Domain = FlextProtocols.Domain
    Application = FlextProtocols.Application
    Infrastructure = FlextProtocols.Infrastructure
    Extensions = FlextProtocols.Extensions
    Commands = FlextProtocols.Commands

    # =========================================================================
    # CLI-SPECIFIC PROTOCOLS - Domain extension for CLI operations
    # =========================================================================

    class Cli:
        """CLI domain-specific protocols."""

        @runtime_checkable
        class CliCommandHandler(Protocol):
            """Protocol for CLI command handlers."""

            def __call__(
                self, **kwargs: FlextCliTypes.Data.CliCommandArgs
            ) -> FlextResult[FlextCliTypes.Data.CliCommandResult]:
                """Execute CLI command with arguments.

                Args:
                    **kwargs: Command arguments

                Returns:
                    FlextResult[FlextCliTypes.Data.CliCommandResult]: Command execution result

                """
                ...

        @runtime_checkable
        class CliFormatter(Protocol):
            """Protocol for CLI output formatters."""

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
                ...

        @runtime_checkable
        class CliConfigProvider(Protocol):
            """Protocol for CLI configuration providers."""

            def load_config(
                self: object,
            ) -> FlextResult[FlextCliTypes.Data.CliConfigData]:
                """Load CLI configuration.

                Returns:
                    FlextResult[FlextCliTypes.Data.CliConfigData]: Configuration data or error

                """
                ...

            def save_config(
                self, config: FlextCliTypes.Data.CliConfigData
            ) -> FlextResult[None]:
                """Save CLI configuration.

                Args:
                    config: Configuration data to save

                Returns:
                    FlextResult[None]: Success or error

                """
                ...

        @runtime_checkable
        class CliAuthenticator(Protocol):
            """Protocol for CLI authentication providers."""

            def authenticate(
                self, credentials: FlextCliTypes.Data.AuthConfigData
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

        @runtime_checkable
        class CliDebugProvider(Protocol):
            """Protocol for CLI debug information providers."""

            def get_debug_info(
                self: object,
            ) -> FlextResult[FlextCliTypes.Data.DebugInfoData]:
                """Get debug information.

                Returns:
                    FlextResult[FlextCliTypes.Data.DebugInfoData]: Debug information or error

                """
                ...


__all__ = [
    "FlextCliProtocols",
]
