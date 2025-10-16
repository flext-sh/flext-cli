"""FLEXT CLI Protocols - Single unified class following FLEXT standards.

Provides CLI-specific protocol definitions using flext-core patterns.
Single FlextCliProtocols class with nested protocol subclasses following FLEXT pattern.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from flext_core import FlextProtocols, FlextResult, FlextTypes

from flext_cli.typings import FlextCliTypes


class FlextCliProtocols(FlextProtocols):
    """Single unified CLI protocols class following FLEXT standards.

    Extends FlextProtocols with CLI-specific protocol definitions.
    All foundation protocols (Service, Repository, Handler, etc.) are inherited
    from FlextProtocols and available directly.
    """

    # =========================================================================
    # CLI-SPECIFIC PROTOCOLS - Domain extension for CLI operations
    # =========================================================================

    class Cli:
        """CLI domain-specific protocols."""

        @runtime_checkable
        class CliFormatter(Protocol):
            """Protocol for CLI output formatters."""

            def format_data(
                self,
                data: FlextCliTypes.Data.CliFormatData,
                **options: FlextCliTypes.Data.CliConfigData,
            ) -> FlextResult[str]:
                """Format data for CLI output."""
                ...

        @runtime_checkable
        class CliConfigProvider(Protocol):
            """Protocol for CLI configuration providers."""

            def load_config(
                self,
            ) -> FlextResult[FlextCliTypes.Data.CliConfigData]:
                """Load CLI configuration."""
                ...

            def save_config(
                self,
                config: FlextCliTypes.Data.CliConfigData,
            ) -> FlextResult[None]:
                """Save CLI configuration."""
                ...

        @runtime_checkable
        class CliAuthenticator(Protocol):
            """Protocol for CLI authentication providers."""

            def authenticate(
                self,
                credentials: FlextCliTypes.Data.AuthConfigData,
            ) -> FlextResult[str]:
                """Authenticate and return token."""
                ...

            def validate_token(self, token: str) -> FlextResult[bool]:
                """Validate authentication token."""
                ...

        @runtime_checkable
        class CliDebugProvider(Protocol):
            """Protocol for CLI debug information providers."""

            def get_debug_info(
                self,
            ) -> FlextResult[FlextCliTypes.Data.DebugInfoData]:
                """Get debug information."""
                ...

        @runtime_checkable
        class CliPlugin(Protocol):
            """Protocol for CLI plugins."""

            name: str
            version: str

            def initialize(self, cli_main: FlextTypes.JsonValue) -> FlextResult[None]:
                """Initialize plugin with CLI context."""
                ...

            def register_commands(
                self, cli_main: FlextTypes.JsonValue
            ) -> FlextResult[None]:
                """Register plugin commands with CLI."""
                ...

        @runtime_checkable
        class CliCommandHandler(Protocol):
            """Protocol for CLI command handlers."""

            def __call__(
                self,
                **kwargs: FlextCliTypes.Data.CliCommandArgs,
            ) -> FlextResult[FlextCliTypes.Data.CliCommandResult]:
                """Execute CLI command with arguments."""
                ...


__all__ = [
    "FlextCliProtocols",
]
