"""FLEXT CLI Authentication - Consolidated authentication management.

Provides FlextCliAuth class for comprehensive authentication operations including
token management, user sessions, and secure credential handling following
flext-core patterns.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from pathlib import Path
from typing import TypedDict, cast

import click
from flext_core import FlextLogger, FlextResult
from rich.console import Console

from flext_cli.client import FlextApiClient
from flext_cli.config import FlextCliConfig

logger = FlextLogger(__name__)


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
            # Avoid circular import - lazy load

            self._config = FlextCliConfig.get_current()
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

    def _save_token_generic(
        self,
        token: str,
        default_path_func: Callable[[], Path],
        custom_path: Path | None,
        token_type: str,
    ) -> FlextResult[None]:
        """Generic token saving functionality to eliminate code duplication.

        Args:
            token: Token to save
            default_path_func: Function to get default path
            custom_path: Optional custom path
            token_type: Type of token for error messages

        Returns:
            FlextResult[None]: Success or failure result

        """
        if not token or not token.strip():
            return FlextResult[None].fail(f"{token_type} cannot be empty")

        file_path = custom_path or default_path_func()
        return self._save_token_to_file(token, file_path)

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
        return self._save_token_generic(token, self.get_token_path, token_path, "Token")

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
        return self._save_token_generic(
            token, self.get_refresh_token_path, refresh_token_path, "Refresh token"
        )

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
        """Ultra-simplified login using Python 3.13+ match-case patterns."""
        # Single-expression validation using match-case
        match (
            username.strip() if username else "",
            password.strip() if password else "",
        ):
            case ("", _) | (_, ""):
                credential_status = "empty_credentials"
            case (user, pwd) if len(user) < 1 or len(pwd) < 1:
                credential_status = "invalid_credentials"
            case _:
                credential_status = "valid"

        if credential_status != "valid":
            return FlextResult[dict[str, object]].fail(
                f"Credential validation failed: {credential_status}"
            )

        # Single try-catch with match-case error handling
        try:
            async with FlextApiClient() as client:
                response = await client.login(username, password)

                # Check if login was successful
                if not response.is_success:
                    return response  # Return the error result directly

                # Extract the response data
                response_data = response.data
                if response_data is None or response_data == {}:
                    return FlextResult[dict[str, object]].fail(
                        "Empty authentication response"
                    )

                # Token extraction and validation
                if "token" in response_data:
                    token = response_data.get("token")
                    if isinstance(token, str) and token.strip():
                        return self._handle_token_save(token, response_data)
                    return FlextResult[dict[str, object]].fail(
                        f"Invalid token format: {type(token)}"
                    )

                return FlextResult[dict[str, object]].fail("Missing token in response")

        except Exception as e:
            # Exception handling
            if isinstance(e, (ConnectionError, TimeoutError)):
                return FlextResult[dict[str, object]].fail(f"Connection failed: {e}")
            if isinstance(e, (ValueError, KeyError)):
                return FlextResult[dict[str, object]].fail(
                    f"Login validation failed: {e}"
                )
            if isinstance(e, OSError):
                return FlextResult[dict[str, object]].fail(f"Network error: {e}")
            return FlextResult[dict[str, object]].fail(f"Login failed: {e}")

    def _handle_token_save(
        self, token: str, response: dict[str, object]
    ) -> FlextResult[dict[str, object]]:
        """Handle token saving with error recovery."""
        save_result = self.save_auth_token(token)
        match save_result.is_success:
            case True:
                return FlextResult[dict[str, object]].ok(response)
            case False:
                return FlextResult[dict[str, object]].fail(
                    f"Token save failed: {save_result.error}"
                )

    async def logout(self) -> FlextResult[None]:
        """Ultra-simplified logout using match-case and error recovery."""
        # Single match-case authentication check
        token_result = self.get_auth_token()
        if token_result.is_success and token_result.value.strip():
            auth_status = "authenticated"
        else:
            auth_status = "not_authenticated"

        if auth_status != "authenticated":
            return FlextResult[None].fail("Not logged in")

        # Attempt server logout with graceful error handling
        try:
            async with FlextApiClient() as client:
                await client.logout()
        except Exception as e:
            logger.debug(f"Server logout failed (continuing anyway): {e}")

        # Always clear local tokens - proper result handling
        result = self.clear_auth_tokens()
        if result.is_success:
            return FlextResult[None].ok(None)
        return FlextResult[None].fail(f"Token cleanup failed: {result.error}")

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
        """Get current user information using match-case authentication check.

        Returns:
            FlextResult containing user information if authenticated

        """
        match self.is_authenticated():
            case False:
                return FlextResult[dict[str, object]].fail("Not authenticated")
            case True:
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


@click.group(name="auth")
def auth() -> None:
    """Authentication management commands."""


@auth.command()
@click.option("--username", prompt=True, help="Username")
@click.option("--password", prompt=True, hide_input=True, help="Password")
def login(username: str, password: str) -> None:
    """Login to FLEXT services."""
    auth_instance = FlextCliAuth.create()
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
    auth_instance = FlextCliAuth.create()
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
    auth_instance = FlextCliAuth.create()
    console = Console()

    status_info = auth_instance.get_status()
    console.print("Authentication Status:")
    for key, value in status_info.items():
        console.print(f"  {key}: {value}")


__all__ = [
    "FlextCliAuth",
    "auth",
]
