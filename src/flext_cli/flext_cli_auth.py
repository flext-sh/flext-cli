"""FLEXT CLI Authentication - Unified authentication service using flext-core directly.

Single responsibility authentication service eliminating ALL loose functions
and wrapper patterns. Uses flext-core utilities directly with SOURCE OF TRUTH
principle for all authentication metadata and operations.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from pathlib import Path

from flext_cli.models import FlextCliModels
from flext_core import (
    FlextContainer,
    FlextLogger,
    FlextResult,
    FlextService,
    FlextUtilities,
)


class FlextCliAuth(FlextService[str]):
    """Authentication service extending FlextService from flext-core.

    Provides essential authentication functionality using flext-core patterns.
    Follows single-responsibility principle with nested helpers.
    """

    def __init__(
        self, *, config: FlextCliModels.FlextCliConfig | None = None, **_data: object
    ) -> None:
        """Initialize authentication service with flext-core integration."""
        super().__init__()
        self._logger = FlextLogger(__name__)
        self._container = FlextContainer.get_global()

        # Use models module
        if config is None:
            from flext_cli.models import FlextCliModels

            self._config = FlextCliModels.FlextCliConfig()
        else:
            self._config = config

    class _AuthHelper:
        """Nested helper for authentication operations."""

        @staticmethod
        def validate_credentials(username: str, password: str) -> FlextResult[None]:
            """Validate login credentials."""
            if not username or not username.strip():
                return FlextResult[None].fail("Username cannot be empty")

            if not password or not password.strip():
                return FlextResult[None].fail("Password cannot be empty")

            if len(username.strip()) < 1 or len(password.strip()) < 1:
                return FlextResult[None].fail(
                    "Username and password must be at least 1 character"
                )

            return FlextResult[None].ok(None)

        @staticmethod
        def get_token_paths(config: object) -> FlextResult[dict[str, Path]]:
            """Get token file paths from configuration."""
            try:
                # Use basic config attributes or defaults
                token_path = getattr(
                    config, "token_file", Path.home() / ".flext" / "token"
                )
                refresh_path = getattr(
                    config,
                    "refresh_token_file",
                    Path.home() / ".flext" / "refresh_token",
                )

                paths = {"token_path": token_path, "refresh_token_path": refresh_path}

                return FlextResult[dict[str, Path]].ok(paths)
            except Exception as e:
                return FlextResult[dict[str, Path]].fail(
                    f"Failed to get token paths: {e}"
                )

        @staticmethod
        def save_token_to_file(token: str, file_path: Path) -> FlextResult[None]:
            """Save token to secure file storage."""
            try:
                if not token or not token.strip():
                    return FlextResult[None].fail("Token cannot be empty")

                # Create parent directories with secure permissions
                file_path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)

                # Write token with secure permissions
                file_path.write_text(token.strip(), encoding="utf-8")
                file_path.chmod(0o600)

                return FlextResult[None].ok(None)
            except (OSError, PermissionError) as e:
                return FlextResult[None].fail(f"Failed to save token: {e}")

        @staticmethod
        def load_token_from_file(file_path: Path) -> FlextResult[str]:
            """Load token from secure file storage."""
            try:
                if not file_path.exists():
                    return FlextResult[str].fail("Token file does not exist")

                token = file_path.read_text(encoding="utf-8").strip()
                if not token:
                    return FlextResult[str].fail("Token file is empty")

                return FlextResult[str].ok(token)
            except (OSError, PermissionError) as e:
                return FlextResult[str].fail(f"Failed to load token: {e}")

    def execute(self) -> FlextResult[str]:
        """Execute authentication service - required by FlextService."""
        status_result = self.get_auth_status()
        if status_result.is_failure:
            return FlextResult[str].fail(
                f"Auth status check failed: {status_result.error}"
            )

        return FlextResult[str].ok("FlextCliAuth service operational")

    def validate_credentials(self, username: str, password: str) -> FlextResult[None]:
        """Validate login credentials."""
        return self._AuthHelper.validate_credentials(username, password)

    def save_auth_token(self, token: str) -> FlextResult[None]:
        """Save authentication token to secure storage."""
        paths_result = self._AuthHelper.get_token_paths(self._config)
        if paths_result.is_failure:
            return FlextResult[None].fail(f"Token paths failed: {paths_result.error}")

        paths = paths_result.value
        return self._AuthHelper.save_token_to_file(token, paths["token_path"])

    def get_auth_token(self) -> FlextResult[str]:
        """Retrieve authentication token from storage."""
        paths_result = self._AuthHelper.get_token_paths(self._config)
        if paths_result.is_failure:
            return FlextResult[str].fail(f"Token paths failed: {paths_result.error}")

        paths = paths_result.value
        return self._AuthHelper.load_token_from_file(paths["token_path"])

    def is_authenticated(self) -> bool:
        """Check if user is currently authenticated."""
        token_result = self.get_auth_token()
        return token_result.is_success and bool(token_result.value)

    def clear_auth_tokens(self) -> FlextResult[None]:
        """Clear all authentication tokens from storage."""
        paths_result = self._AuthHelper.get_token_paths(self._config)
        if paths_result.is_failure:
            return FlextResult[None].fail(f"Token paths failed: {paths_result.error}")

        paths = paths_result.value
        errors = []

        # Clear access token
        if paths["token_path"].exists():
            try:
                paths["token_path"].unlink()
            except (OSError, PermissionError) as e:
                errors.append(f"Failed to remove token file: {e}")

        # Clear refresh token
        if paths["refresh_token_path"].exists():
            try:
                paths["refresh_token_path"].unlink()
            except (OSError, PermissionError) as e:
                errors.append(f"Failed to remove refresh token file: {e}")

        if errors:
            return FlextResult[None].fail("; ".join(errors))

        return FlextResult[None].ok(None)

    def get_auth_status(self) -> FlextResult[dict[str, object]]:
        """Get current authentication status information."""
        paths_result = self._AuthHelper.get_token_paths(self._config)
        if paths_result.is_failure:
            return FlextResult[dict[str, object]].fail(
                f"Token paths failed: {paths_result.error}"
            )

        paths = paths_result.value
        authenticated = self.is_authenticated()

        status = {
            "authenticated": authenticated,
            "token_file": str(paths["token_path"]),
            "token_exists": paths["token_path"].exists(),
            "refresh_token_file": str(paths["refresh_token_path"]),
            "refresh_token_exists": paths["refresh_token_path"].exists(),
            "timestamp": FlextUtilities.Generators.generate_iso_timestamp(),
        }

        return FlextResult[dict[str, object]].ok(status)

    def authenticate(self, credentials: dict[str, object]) -> FlextResult[str]:
        """Authenticate user with provided credentials.

        Args:
            credentials: Authentication credentials (username, password, token, etc.)

        Returns:
            FlextResult[str]: Authentication token or error message

        """
        try:
            # Handle token-based authentication
            if "token" in credentials:
                token = str(credentials["token"])
                if not token.strip():
                    return FlextResult[str].fail("Token cannot be empty")

                # Save the token
                save_result = self.save_auth_token(token)
                if save_result.is_failure:
                    return FlextResult[str].fail(
                        f"Failed to save token: {save_result.error}"
                    )

                return FlextResult[str].ok(token)

            # Handle username/password authentication (basic implementation)
            if "username" in credentials and "password" in credentials:
                username = str(credentials["username"])
                password = str(credentials["password"])

                if not username.strip() or not password.strip():
                    return FlextResult[str].fail(
                        "Username and password cannot be empty"
                    )

                # For now, this is a placeholder - in real implementation,
                # this would authenticate against an API endpoint
                mock_token = f"auth_token_{username}_{len(password)}"
                save_result = self.save_auth_token(mock_token)
                if save_result.is_failure:
                    return FlextResult[str].fail(
                        f"Failed to save token: {save_result.error}"
                    )

                return FlextResult[str].ok(mock_token)

            return FlextResult[str].fail(
                "Invalid credentials: missing token or username/password"
            )

        except Exception as e:
            return FlextResult[str].fail(f"Authentication failed: {e}")


__all__ = ["FlextCliAuth"]
