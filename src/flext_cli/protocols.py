"""FLEXT CLI Protocols - Interface definitions for dependency inversion.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from flext_core import FlextResult, FlextTypes


class FlextCliProtocols:
    """Unified CLI protocols container following single class pattern.

    Contains all CLI protocol definitions to eliminate circular dependencies
    and enforce SOLID principles through proper abstraction.
    """

    class AuthenticationClient(Protocol):
        """Protocol for authentication client operations."""

        async def login(
            self,
            username: str,
            password: str,
        ) -> FlextResult[FlextTypes.Core.Dict]:
            """Login with username and password."""
            ...

        async def logout(self) -> FlextResult[None]:
            """Logout the current user."""
            ...

    class TokenStorage(Protocol):
        """Protocol for token storage operations."""

        def save_token(self, token: str, token_type: str) -> FlextResult[None]:
            """Save token to storage."""
            ...

        def load_token(self, token_type: str) -> FlextResult[str]:
            """Load token from storage."""
            ...

        def clear_tokens(self) -> FlextResult[None]:
            """Clear all tokens from storage."""
            ...

    class AuthenticationService(Protocol):
        """Protocol for authentication service operations."""

        def validate_credentials(
            self,
            username: str,
            password: str,
        ) -> FlextResult[None]:
            """Validate login credentials."""
            ...

        def is_authenticated(self) -> FlextResult[bool]:
            """Check authentication status."""
            ...

        async def authenticate(
            self,
            username: str,
            password: str,
        ) -> FlextResult[FlextTypes.Core.Dict]:
            """Perform authentication."""
            ...

        async def deauthenticate(self) -> FlextResult[None]:
            """Perform deauthentication."""
            ...

    # ==========================================================================
    # CLI PROCESSING PROTOCOLS - Moved from typings.py for unification
    # ==========================================================================

    class CliProcessor(Protocol):
        """Protocol for CLI processors."""

        def process(
            self,
            request: str | dict[str, object],
        ) -> FlextResult[object]:
            """Process CLI request."""
            ...

        def build(
            self,
            domain: object,
            *,
            correlation_id: str,
        ) -> str | dict[str, object]:
            """Build CLI response."""
            ...

    class CliValidator(Protocol):
        """Protocol for CLI validators."""

        def validate(
            self,
            data: dict[str, object] | str | float,
        ) -> FlextResult[None]:
            """Validate CLI data."""
            ...

    class CliFormatter(Protocol):
        """Protocol for CLI formatters."""

        def format(
            self,
            data: dict[str, object] | list[object] | str,
            format_type: str,
        ) -> FlextResult[str]:
            """Format CLI data with specified type."""
            ...

    class CliAuthenticator(Protocol):
        """Protocol for CLI authenticators."""

        def authenticate(
            self,
            credentials: dict[str, str],
        ) -> FlextResult[FlextTypes.Core.Dict]:
            """Authenticate CLI user."""
            ...

        def is_authenticated(self) -> bool:
            """Check authentication status."""
            ...

    @runtime_checkable
    class OutputFormatter(Protocol):
        """Protocol for formatter classes used by the CLI."""

        def format(self, data: object, console: object) -> None:
            """Format data using console output."""
            ...


__all__ = [
    "FlextCliProtocols",
]
