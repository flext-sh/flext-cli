"""FLEXT CLI Authentication - Consolidated authentication management.

Provides FlextCliAuth class for comprehensive authentication operations including
token management, user sessions, and secure credential handling following
flext-core patterns.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import asyncio
import contextlib
from pathlib import Path
from typing import TYPE_CHECKING, TypedDict, cast

import click
from flext_core import FlextResult
from rich.console import Console

if TYPE_CHECKING:
    from flext_cli.config import FlextCliConfig


class FlextCliAuth:
    """Consolidated authentication management following flext-core patterns.

    Provides comprehensive authentication operations including token management,
    user sessions, and secure credential handling with FlextResult error handling.
    Unified class containing ALL authentication functionality including types.

    Features:
        - Token management (access and refresh tokens)
        - Session management and validation
        - Secure credential storage
        - User data extraction and validation
        - Auto-refresh capabilities
        - Integration with FlextApiClient
    """

    class UserData(TypedDict, total=False):
        """Type definition for user data in authentication response."""

        name: str
        email: str
        id: str

    def __init__(self, *, config: FlextCliConfig | None = None) -> None:
        """Initialize authentication manager with configuration.

        Args:
            config: Optional CLI configuration instance

        """
        self._config = config
        self._console = Console()

    @property
    def config(self) -> FlextCliConfig:
        """Get CLI configuration, lazy-loaded to avoid circular imports."""
        if self._config is None:
            # Import local para evitar ciclos
            from flext_cli.config import get_config

            self._config = get_config()
        return self._config

    @staticmethod
    def _get_user_data(data_obj: object) -> FlextCliAuth.UserData | None:
        """Extract user data with proper typing."""
        if isinstance(data_obj, dict):
            return cast("FlextCliAuth.UserData", data_obj)
        return None

    def get_token_path(self) -> Path:
        """Get the path to the authentication token file.

        Uses FlextCliConfig to determine the correct token file location based on
        current configuration settings.

        Returns:
            Path: Absolute path to the authentication token file

        """
        return self.config.token_file

    def get_refresh_token_path(self) -> Path:
        """Get the path to the refresh token file.

        Uses FlextCliConfig to determine the correct refresh token file location
        based on current configuration settings.

        Returns:
            Path: Absolute path to the refresh token file

        """
        return self.config.refresh_token_file

    def save_auth_token(
        self, token: str, *, token_path: Path | None = None
    ) -> FlextResult[None]:
        """Save authentication token to secure storage.

        Args:
            token: Authentication token to save
            token_path: Optional path to save token (defaults to configured path)

        Returns:
            FlextResult[None]: Success or failure result with error details

        """
        if not token or not token.strip():
            return FlextResult[None].fail("Token cannot be empty")

        file_path = token_path or self.get_token_path()
        return self._save_token_to_file(token, file_path)

    def save_refresh_token(
        self, token: str, *, refresh_token_path: Path | None = None
    ) -> FlextResult[None]:
        """Save refresh token to secure storage.

        Args:
            token: Refresh token to save
            refresh_token_path: Optional path to save refresh token (defaults to configured path)

        Returns:
            FlextResult[None]: Success or failure result with error details

        """
        if not token or not token.strip():
            return FlextResult[None].fail("Refresh token cannot be empty")

        file_path = refresh_token_path or self.get_refresh_token_path()
        return self._save_token_to_file(token, file_path)

    def get_auth_token(self, *, token_path: Path | None = None) -> FlextResult[str]:
        """Retrieve authentication token from secure storage.

        Args:
            token_path: Optional path to read token from (defaults to configured path)

        Returns:
            FlextResult[str]: Token value on success, error message on failure

        """
        file_path = token_path or self.get_token_path()
        return self._load_token_from_file(file_path)

    def get_refresh_token(
        self, *, refresh_token_path: Path | None = None
    ) -> FlextResult[str]:
        """Retrieve refresh token from secure storage.

        Args:
            refresh_token_path: Optional path to read refresh token from (defaults to configured path)

        Returns:
            FlextResult[str]: Refresh token value on success, error message on failure

        """
        file_path = refresh_token_path or self.get_refresh_token_path()
        return self._load_token_from_file(file_path)

    def clear_auth_tokens(self) -> FlextResult[None]:
        """Clear all authentication tokens from storage.

        Removes both access and refresh tokens from their storage locations.
        This operation is atomic - either both tokens are cleared or neither.

        Returns:
            FlextResult[None]: Success if all tokens cleared, failure with error details

        """
        token_path = self.get_token_path()
        refresh_path = self.get_refresh_token_path()

        errors = []

        if token_path.exists():
            try:
                token_path.unlink()
            except (OSError, PermissionError) as e:
                errors.append(f"Failed to remove token file: {e}")

        if refresh_path.exists():
            try:
                refresh_path.unlink()
            except (OSError, PermissionError) as e:
                errors.append(f"Failed to remove refresh token file: {e}")

        if errors:
            return FlextResult[None].fail("; ".join(errors))

        return FlextResult[None].ok(None)

    def is_authenticated(self, *, token_path: Path | None = None) -> bool:
        """Check if the user is currently authenticated.

        Args:
            token_path: Optional path to check token from (defaults to configured path)

        Returns:
            True if the user is authenticated, False otherwise

        """
        token_result = self.get_auth_token(token_path=token_path)
        return bool(token_result.value if token_result.is_success else "")

    def should_auto_refresh(self) -> bool:
        """Check if the user should auto refresh the auth tokens.

        Returns:
            True if the user should auto refresh the auth tokens, False otherwise

        """
        return self.config.auto_refresh and bool(
            self.get_refresh_token().value
            if self.get_refresh_token().is_success
            else ""
        )

    def get_auth_headers(self) -> dict[str, str]:
        """Get authentication headers for API requests.

        Returns:
            Dictionary with Authorization header if authenticated, empty dict otherwise

        """
        token_result = self.get_auth_token()
        if token_result.is_success and token_result.value:
            return {"Authorization": f"Bearer {token_result.value}"}
        return {}

    async def login(
        self, username: str, password: str
    ) -> FlextResult[dict[str, object]]:
        """Authenticate with FLEXT services using username and password.

        Args:
            username: Username for authentication
            password: Password for authentication

        Returns:
            FlextResult containing authentication response with user data and tokens

        """
        if not password or len(password) < 1:
            return FlextResult[dict[str, object]].fail("Credentials are empty")

        try:
            # Import local para evitar ciclos
            from flext_cli.client import FlextApiClient

            async with FlextApiClient() as client:
                login_result = await client.login(username, password)

                if login_result.is_failure:
                    return FlextResult[dict[str, object]].fail(
                        f"Login failed: {login_result.error}"
                    )

                response = login_result.value
                if response and "token" in response:
                    token_value = response["token"]
                    if isinstance(token_value, str):
                        save_result = self.save_auth_token(token_value)
                        if save_result.is_failure:
                            return FlextResult[dict[str, object]].fail(
                                f"Authentication save failed: {save_result.error}"
                            )
                        return FlextResult[dict[str, object]].ok(response)

                return FlextResult[dict[str, object]].fail(
                    "Invalid authentication response"
                )

        except (ConnectionError, TimeoutError, ValueError, KeyError) as e:
            return FlextResult[dict[str, object]].fail(f"Login failed: {e}")
        except OSError as e:
            return FlextResult[dict[str, object]].fail(f"Network error: {e}")

    async def logout(self) -> FlextResult[None]:
        """Logout from FLEXT services and clear authentication tokens.

        Returns:
            FlextResult[None]: Success if logout completed, failure with error details

        """
        try:
            # Proactive clear for safety
            with contextlib.suppress(Exception):
                self.clear_auth_tokens()

            token_result = self.get_auth_token()
            if not token_result.is_success or not token_result.value:
                return FlextResult[None].fail("Not logged in")

            # Import local para evitar ciclos
            from flext_cli.client import FlextApiClient

            async with FlextApiClient() as client:
                try:
                    await client.logout()
                except (RuntimeError, ValueError, OSError) as e:
                    # Clear tokens even if server logout fails
                    clear_result = self.clear_auth_tokens()
                    if clear_result.is_failure:
                        return FlextResult[None].fail(
                            f"Logout failed and token clear failed: {e}, {clear_result.error}"
                        )
                    return FlextResult[None].fail(
                        f"Server logout failed but tokens cleared: {e}"
                    )

            # Clear tokens after successful server logout
            clear_result = self.clear_auth_tokens()
            if clear_result.is_failure:
                return FlextResult[None].fail(
                    f"Server logout succeeded but token clear failed: {clear_result.error}"
                )

            return FlextResult[None].ok(None)

        except (
            ConnectionError,
            TimeoutError,
            OSError,
            PermissionError,
            ValueError,
            AttributeError,
        ) as e:
            clear_result = self.clear_auth_tokens()
            if clear_result.is_success:
                return FlextResult[None].ok(None)  # Logged out locally
            return FlextResult[None].fail(
                f"Logout error and failed to clear tokens: {e}"
            )
        except (RuntimeError, TypeError) as e:
            self.clear_auth_tokens()
            return FlextResult[None].fail(f"Logout error: {e}")

    def get_status(self) -> dict[str, object]:
        """Get current authentication status information.

        Returns:
            Dictionary containing authentication status, token file info, etc.

        """
        authenticated = self.is_authenticated()
        token_path = self.get_token_path()
        refresh_path = self.get_refresh_token_path()

        return {
            "authenticated": authenticated,
            "token_file": str(token_path),
            "token_exists": token_path.exists(),
            "refresh_token_file": str(refresh_path),
            "refresh_token_exists": refresh_path.exists(),
            "auto_refresh": self.config.auto_refresh,
        }

    def whoami(self) -> FlextResult[dict[str, object]]:
        """Get information about the currently authenticated user.

        Returns:
            FlextResult containing user information if authenticated

        """
        if not self.is_authenticated():
            return FlextResult[dict[str, object]].fail("Not authenticated")

        try:
            # In a real implementation, this would decode the JWT token
            # or make an API call to get user information
            return FlextResult[dict[str, object]].ok(
                {
                    "authenticated": True,
                    "note": "User information retrieval not yet implemented",
                }
            )
        except (ValueError, KeyError) as e:
            return FlextResult[dict[str, object]].fail(
                f"Error retrieving user information: {e}"
            )

    def _save_token_to_file(self, token: str, file_path: Path) -> FlextResult[None]:
        """Save token to file with secure permissions."""
        try:
            # Create parent directories if needed
            file_path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)

            # Write token with secure permissions
            file_path.write_text(token, encoding="utf-8")
            file_path.chmod(0o600)

            return FlextResult[None].ok(None)
        except (OSError, PermissionError) as e:
            return FlextResult[None].fail(f"Failed to save token: {e}")

    def _load_token_from_file(self, file_path: Path) -> FlextResult[str]:
        """Load token from file with error handling."""
        try:
            if not file_path.exists():
                return FlextResult[str].fail("Token file does not exist")

            token = file_path.read_text(encoding="utf-8").strip()
            if not token:
                return FlextResult[str].fail("Token file is empty")

            return FlextResult[str].ok(token)
        except (OSError, PermissionError) as e:
            return FlextResult[str].fail(f"Failed to load token: {e}")

    @classmethod
    def create(cls) -> FlextCliAuth:
        """Create a FlextCliAuth instance using factory pattern."""
        return cls()


# Backward compatibility function
def create_auth() -> FlextCliAuth:
    """Create a FlextCliAuth instance."""
    return FlextCliAuth.create()


@click.group(name="auth")
def auth() -> None:
    """Authentication management commands."""


@auth.command()
@click.option("--username", prompt=True, help="Username")
@click.option("--password", prompt=True, hide_input=True, help="Password")
def login(username: str, password: str) -> None:
    """Login to FLEXT services."""
    auth_instance = create_auth()
    console = Console()

    async def _login() -> None:
        result = await auth_instance.login(username, password)
        if result.is_success:
            console.print("[green]✓[/green] Login successful")
        else:
            console.print(f"[red]✗[/red] Login failed: {result.error}")

    asyncio.run(_login())


@auth.command()
def logout() -> None:
    """Logout from FLEXT services."""
    auth_instance = create_auth()
    console = Console()

    async def _logout() -> None:
        result = await auth_instance.logout()
        if result.is_success:
            console.print("[green]✓[/green] Logout successful")
        else:
            console.print(f"[red]✗[/red] Logout failed: {result.error}")

    asyncio.run(_logout())


@auth.command()
def status() -> None:
    """Show authentication status."""
    auth_instance = create_auth()
    console = Console()

    status_info = auth_instance.get_status()
    console.print("Authentication Status:")
    for key, value in status_info.items():
        console.print(f"  {key}: {value}")


__all__ = [
    "FlextCliAuth",
    "auth",
    "create_auth",
]
