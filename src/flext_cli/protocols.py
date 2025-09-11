"""FLEXT CLI Protocols - Interface definitions for dependency inversion.

Defines protocols for CLI operations to eliminate circular dependencies
and enforce SOLID principles through proper abstraction.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Protocol

from flext_core import FlextResult, FlextTypes


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

    def validate_credentials(self, username: str, password: str) -> FlextResult[None]:
        """Validate login credentials."""
        ...

    def is_authenticated(self) -> FlextResult[bool]:
        """Check authentication status."""
        ...

    async def authenticate(
        self, username: str, password: str
    ) -> FlextResult[FlextTypes.Core.Dict]:
        """Perform authentication."""
        ...

    async def deauthenticate(self) -> FlextResult[None]:
        """Perform deauthentication."""
        ...
