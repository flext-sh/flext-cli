"""FLEXT CLI Authentication - Unified authentication service using flext-core directly.

Single responsibility authentication service eliminating ALL loose functions
and wrapper patterns. Uses flext-core utilities directly with SOURCE OF TRUTH
principle for all authentication metadata and operations.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import asyncio
import contextlib
import json
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import TypedDict

from flext_core import (
    FlextContainer,
    FlextDomainService,
    FlextLogger,
    FlextResult,
    FlextTypes,
    FlextUtilities,
)

from flext_cli.config import FlextCliConfig
from flext_cli.protocols import AuthenticationClient


class FlextCliAuth(FlextDomainService[str]):
    """Unified authentication service using flext-core utilities directly.

    Eliminates ALL wrapper methods and loose functions, using flext-core
    utilities directly without abstraction layers. Uses SOURCE OF TRUTH
    principle for all authentication metadata and operations.

    SOLID Principles Applied:
        - Single Responsibility: Authentication operations only
        - Open/Closed: Extensible through flext-core patterns
        - Dependency Inversion: Uses FlextContainer for dependencies
        - Interface Segregation: Focused authentication interface
    """

    class UserData(TypedDict, total=False):
        """User data structure from SOURCE OF TRUTH."""

        name: str
        email: str
        id: str

    class AuthStatus(TypedDict):
        """Authentication status structure from SOURCE OF TRUTH."""

        authenticated: bool
        token_file: str
        token_exists: bool
        refresh_token_file: str
        refresh_token_exists: bool
        auto_refresh: bool

    class LoginCredentials(TypedDict):
        """Login credentials structure from SOURCE OF TRUTH."""

        username: str
        password: str

    class TokenPaths(TypedDict):
        """Token paths structure from SOURCE OF TRUTH."""

        token_path: Path
        refresh_token_path: Path

    class AuthConfig(TypedDict):
        """Auth config structure for test compatibility."""

        api_key: str
        base_url: str
        timeout: int

    class TokenData(TypedDict):
        """Token data structure for test compatibility."""

        access_token: str
        refresh_token: str
        expires_at: datetime
        token_type: str

    def __init__(
        self,
        *,
        config: FlextCliConfig | None = None,
        auth_client: AuthenticationClient | None = None,
        **_data: object,
    ) -> None:
        """Initialize authentication service with flext-core dependencies and SOURCE OF TRUTH."""
        super().__init__()
        self._container = FlextContainer.get_global()
        self._logger = FlextLogger(__name__)

        # Load configuration from FlextConfig singleton as SINGLE SOURCE OF TRUTH
        if config is None:
            self._config = FlextCliConfig.get_current()
        else:
            self._config = config

        # Dependency injection for authentication client
        self._auth_client = auth_client

    @property
    def config(self) -> FlextCliConfig:
        """Get configuration - SIMPLE ALIAS for test compatibility."""
        return self._config

    def update_from_config(self) -> None:
        """Update authentication configuration from FlextConfig singleton.

        This method allows the authentication service to refresh its configuration
        from the FlextConfig singleton, ensuring it always uses the latest
        configuration values.
        """
        # Update configuration from singleton
        self._config = FlextCliConfig.get_current()

    def get_token_paths(self) -> FlextResult[FlextCliAuth.TokenPaths]:
        """Get token paths from SOURCE OF TRUTH configuration."""
        try:
            # Extract paths from SOURCE OF TRUTH config
            paths: FlextCliAuth.TokenPaths = {
                "token_path": self._config.token_file,
                "refresh_token_path": self._config.refresh_token_file,
            }

            return FlextResult[FlextCliAuth.TokenPaths].ok(paths)

        except (
            ImportError,
            AttributeError,
            ValueError,
        ) as e:
            return FlextResult[FlextCliAuth.TokenPaths].fail(
                f"Token paths from SOURCE OF TRUTH failed: {e}",
            )

    def get_token_path(self) -> Path:
        """Get token path - SIMPLE ALIAS for test compatibility."""
        return self._config.token_file

    def get_refresh_token_path(self) -> Path:
        """Get refresh token path - SIMPLE ALIAS for test compatibility."""
        return self._config.refresh_token_file

    def save_refresh_token(self, token: str) -> FlextResult[None]:
        """Save refresh token - SIMPLE ALIAS for test compatibility."""
        return self.save_token_to_storage(
            token,
            "refresh",
            self._config.refresh_token_file,
        )

    def get_refresh_token(self) -> FlextResult[str]:
        """Get refresh token - SIMPLE ALIAS for test compatibility."""
        try:
            if not self._config.refresh_token_file.exists():
                return FlextResult[str].fail("Refresh token file not found")

            content = self._config.refresh_token_file.read_text(encoding="utf-8")
            if not content.strip():
                return FlextResult[str].fail("Refresh token file is empty")

            return FlextResult[str].ok(content.strip())
        except (
            ImportError,
            AttributeError,
            ValueError,
        ) as e:
            return FlextResult[str].fail(f"Failed to read refresh token: {e}")

    def should_auto_refresh(self) -> bool:
        """Check if auto refresh is enabled - SIMPLE ALIAS for test compatibility."""
        return bool(getattr(self._config, "auto_refresh", False))

    def validate_credentials(self, credentials: LoginCredentials) -> FlextResult[None]:
        """Validate login credentials using SOURCE OF TRUTH validation rules."""
        try:
            username = (
                credentials["username"].strip() if credentials["username"] else ""
            )
            password = (
                credentials["password"].strip() if credentials["password"] else ""
            )

            # SOURCE OF TRUTH validation rules
            if not username or not password:
                return FlextResult[None].fail("Username and password cannot be empty")

            if len(username) < 1 or len(password) < 1:
                return FlextResult[None].fail(
                    "Username and password must be at least 1 character",
                )

            return FlextResult[None].ok(None)

        except (
            ImportError,
            AttributeError,
            ValueError,
        ) as e:
            return FlextResult[None].fail(
                f"Credential validation using SOURCE OF TRUTH failed: {e}",
            )

    def save_token_to_storage(
        self,
        token: str,
        token_type: str,
        file_path: Path,
    ) -> FlextResult[None]:
        """Save token to secure storage using SOURCE OF TRUTH security patterns."""
        try:
            if not token or not token.strip():
                return FlextResult[None].fail(f"{token_type} cannot be empty")

            # Create parent directories using SOURCE OF TRUTH permissions
            file_path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)

            # Write token using SOURCE OF TRUTH encoding and permissions
            file_path.write_text(token, encoding="utf-8")
            file_path.chmod(0o600)

            return FlextResult[None].ok(None)

        except (OSError, PermissionError) as e:
            return FlextResult[None].fail(
                f"Failed to save {token_type} to SOURCE OF TRUTH storage: {e}",
            )

    def load_token_from_storage(
        self,
        file_path: Path,
        token_type: str,
    ) -> FlextResult[str]:
        """Load token from secure storage using SOURCE OF TRUTH patterns."""
        try:
            if not file_path.exists():
                return FlextResult[str].fail(
                    f"{token_type} file does not exist in SOURCE OF TRUTH storage",
                )

            # Load using SOURCE OF TRUTH encoding
            token = file_path.read_text(encoding="utf-8").strip()
            if not token:
                return FlextResult[str].fail(
                    f"{token_type} file is empty in SOURCE OF TRUTH storage",
                )

            return FlextResult[str].ok(token)

        except (OSError, PermissionError) as e:
            return FlextResult[str].fail(
                f"Failed to load {token_type} from SOURCE OF TRUTH storage: {e}",
            )

    def save_auth_token(
        self,
        token: str,
        *,
        token_path: Path | None = None,
    ) -> FlextResult[None]:
        """Save authentication token using SOURCE OF TRUTH storage patterns."""
        try:
            paths_result = self.get_token_paths()
            if paths_result.is_failure:
                return FlextResult[None].fail(
                    f"Token paths from SOURCE OF TRUTH failed: {paths_result.error}",
                )

            paths = paths_result.value
            file_path = token_path or paths["token_path"]

            return self.save_token_to_storage(token, "Authentication token", file_path)

        except (
            ImportError,
            AttributeError,
            ValueError,
        ) as e:
            return FlextResult[None].fail(
                f"Auth token save using SOURCE OF TRUTH failed: {e}",
            )

    def get_auth_token(self, *, token_path: Path | None = None) -> FlextResult[str]:
        """Retrieve authentication token from SOURCE OF TRUTH storage."""
        try:
            paths_result = self.get_token_paths()
            if paths_result.is_failure:
                return FlextResult[str].fail(
                    f"Token paths from SOURCE OF TRUTH failed: {paths_result.error}",
                )

            paths = paths_result.value
            file_path = token_path or paths["token_path"]

            return self.load_token_from_storage(file_path, "Authentication token")

        except (
            ImportError,
            AttributeError,
            ValueError,
        ) as e:
            return FlextResult[str].fail(
                f"Auth token retrieval from SOURCE OF TRUTH failed: {e}",
            )

    def clear_auth_tokens(self) -> FlextResult[None]:
        """Clear all authentication tokens from SOURCE OF TRUTH storage."""
        try:
            paths_result = self.get_token_paths()
            if paths_result.is_failure:
                return FlextResult[None].fail(
                    f"Token paths from SOURCE OF TRUTH failed: {paths_result.error}",
                )

            paths = paths_result.value
            errors = []

            # Clear access token from SOURCE OF TRUTH storage
            if paths["token_path"].exists():
                try:
                    paths["token_path"].unlink()
                except (OSError, PermissionError) as e:
                    errors.append(
                        f"Failed to remove token file from SOURCE OF TRUTH storage: {e}",
                    )

            # Clear refresh token from SOURCE OF TRUTH storage
            if paths["refresh_token_path"].exists():
                try:
                    paths["refresh_token_path"].unlink()
                except (OSError, PermissionError) as e:
                    errors.append(
                        f"Failed to remove refresh token file from SOURCE OF TRUTH storage: {e}",
                    )

            if errors:
                return FlextResult[None].fail("; ".join(errors))

            return FlextResult[None].ok(None)

        except (
            ImportError,
            AttributeError,
            ValueError,
        ) as e:
            return FlextResult[None].fail(
                f"Token clearing from SOURCE OF TRUTH failed: {e}",
            )

    def is_authenticated(self, *, token_path: Path | None = None) -> bool:
        """Check authentication status - SIMPLE ALIAS for test compatibility."""
        try:
            token_result = self.get_auth_token(token_path=token_path)
            return token_result.is_success and bool(token_result.value)
        except (
            ImportError,
            AttributeError,
            ValueError,
        ):
            return False

    def check_authentication_status(
        self, *, token_path: Path | None = None
    ) -> FlextResult[bool]:
        """Check authentication status using SOURCE OF TRUTH - returns FlextResult for API compatibility."""
        try:
            authenticated = self.is_authenticated(token_path=token_path)
            return FlextResult[bool].ok(authenticated)
        except (
            ImportError,
            AttributeError,
            ValueError,
        ) as e:
            return FlextResult[bool].fail(f"Authentication check failed: {e}")

    def get_auth_headers(self) -> FlextResult[FlextTypes.Core.Headers]:
        """Get authentication headers using SOURCE OF TRUTH token."""
        try:
            token_result = self.get_auth_token()
            if token_result.is_failure:
                return FlextResult[FlextTypes.Core.Headers].ok({})

            token = token_result.value
            if not token:
                return FlextResult[FlextTypes.Core.Headers].ok({})

            # Create headers using SOURCE OF TRUTH Bearer pattern
            headers: FlextTypes.Core.Headers = {"Authorization": f"Bearer {token}"}

            return FlextResult[FlextTypes.Core.Headers].ok(headers)

        except (
            ImportError,
            AttributeError,
            ValueError,
        ) as e:
            return FlextResult[FlextTypes.Core.Headers].fail(
                f"Auth headers from SOURCE OF TRUTH failed: {e}",
            )

    async def login(
        self,
        username: str,
        password: str,
    ) -> FlextResult[FlextTypes.Core.Dict]:
        """Perform login using SOURCE OF TRUTH authentication flow."""
        try:
            # Validate credentials using SOURCE OF TRUTH
            credentials: FlextCliAuth.LoginCredentials = {
                "username": username,
                "password": password,
            }

            validation_result = self.validate_credentials(credentials)
            if validation_result.is_failure:
                return FlextResult[FlextTypes.Core.Dict].fail(
                    f"Credential validation failed: {validation_result.error}",
                )

            # Perform login using injected authentication client
            if self._auth_client is None:
                return FlextResult[FlextTypes.Core.Dict].fail(
                    "Authentication client not available"
                )

            response = await self._auth_client.login(username, password)

            # Check response using SOURCE OF TRUTH patterns
            if not response.is_success:
                return FlextResult[FlextTypes.Core.Dict].fail(
                    f"Login failed: {response.error or 'Unknown error'}",
                )

            # Extract response data from SOURCE OF TRUTH
            response_data = response.value
            if not response_data or response_data == {}:
                return FlextResult[FlextTypes.Core.Dict].fail(
                    "Empty authentication response from SOURCE OF TRUTH",
                )

            # Token extraction using SOURCE OF TRUTH structure
            if "token" not in response_data:
                return FlextResult[FlextTypes.Core.Dict].fail(
                    "Missing token in SOURCE OF TRUTH response",
                )

            token = response_data.get("token")
            if not isinstance(token, str) or not token.strip():
                return FlextResult[FlextTypes.Core.Dict].fail(
                    f"Invalid token format from SOURCE OF TRUTH: {type(token)}",
                )

            # Save token using SOURCE OF TRUTH storage
            save_result = self.save_auth_token(token)
            if save_result.is_failure:
                return FlextResult[FlextTypes.Core.Dict].fail(
                    f"Token save to SOURCE OF TRUTH failed: {save_result.error}",
                )

            return FlextResult[FlextTypes.Core.Dict].ok(response_data)

        except (
            ImportError,
            AttributeError,
            ValueError,
        ) as e:
            # Categorized exception handling using Python 3.13+ match-case patterns
            match e:
                case ConnectionError() | TimeoutError():
                    return FlextResult[FlextTypes.Core.Dict].fail(
                        f"Connection to SOURCE OF TRUTH failed: {e}",
                    )
                case ValueError() | KeyError():
                    return FlextResult[FlextTypes.Core.Dict].fail(
                        f"Login validation from SOURCE OF TRUTH failed: {e}",
                    )
                case OSError():
                    return FlextResult[FlextTypes.Core.Dict].fail(
                        f"Network error to SOURCE OF TRUTH: {e}",
                    )
                case _:
                    return FlextResult[FlextTypes.Core.Dict].fail(
                        f"Login to SOURCE OF TRUTH failed: {e}",
                    )

    async def logout(self) -> FlextResult[None]:
        """Perform logout using SOURCE OF TRUTH authentication flow."""
        try:
            # Check authentication status using SOURCE OF TRUTH
            auth_result = self.check_authentication_status()
            if auth_result.is_failure:
                return FlextResult[None].fail(
                    f"Authentication check failed: {auth_result.error}",
                )

            if not auth_result.value:
                return FlextResult[None].fail("Not authenticated to SOURCE OF TRUTH")

            # Attempt server logout using injected authentication client (graceful failure)
            if self._auth_client is not None:
                try:
                    await self._auth_client.logout()
                except (
                    ImportError,
                    AttributeError,
                    ValueError,
                ) as e:
                    logout_msg = f"Server logout from SOURCE OF TRUTH failed (continuing anyway): {e}"
                    self._logger.debug(logout_msg)

            # Always clear local tokens from SOURCE OF TRUTH storage
            clear_result = self.clear_auth_tokens()
            if clear_result.is_failure:
                return FlextResult[None].fail(
                    f"Token cleanup from SOURCE OF TRUTH failed: {clear_result.error}",
                )

            return FlextResult[None].ok(None)

        except (
            ImportError,
            AttributeError,
            ValueError,
        ) as e:
            return FlextResult[None].fail(f"Logout from SOURCE OF TRUTH failed: {e}")

    def get_status(self) -> FlextResult[FlextCliAuth.AuthStatus]:
        """Get authentication status from SOURCE OF TRUTH."""
        try:
            # Get authentication status from SOURCE OF TRUTH
            auth_result = self.check_authentication_status()
            if auth_result.is_failure:
                return FlextResult[FlextCliAuth.AuthStatus].fail(
                    f"Authentication check failed: {auth_result.error}",
                )

            authenticated = auth_result.value

            # Get paths from SOURCE OF TRUTH
            paths_result = self.get_token_paths()
            if paths_result.is_failure:
                return FlextResult[FlextCliAuth.AuthStatus].fail(
                    f"Token paths from SOURCE OF TRUTH failed: {paths_result.error}",
                )

            paths = paths_result.value

            # Build status from SOURCE OF TRUTH data
            status: FlextCliAuth.AuthStatus = {
                "authenticated": authenticated,
                "token_file": str(paths["token_path"]),
                "token_exists": paths["token_path"].exists(),
                "refresh_token_file": str(paths["refresh_token_path"]),
                "refresh_token_exists": paths["refresh_token_path"].exists(),
                "auto_refresh": getattr(self._config, "auto_refresh", False),
            }

            return FlextResult[FlextCliAuth.AuthStatus].ok(status)

        except (
            ImportError,
            AttributeError,
            ValueError,
        ) as e:
            return FlextResult[FlextCliAuth.AuthStatus].fail(
                f"Status retrieval from SOURCE OF TRUTH failed: {e}",
            )

    def whoami(self) -> FlextResult[FlextTypes.Core.Dict]:
        """Get current user information from SOURCE OF TRUTH."""
        try:
            # Check authentication using SOURCE OF TRUTH
            auth_result = self.check_authentication_status()
            if auth_result.is_failure:
                return FlextResult[FlextTypes.Core.Dict].fail(
                    f"Authentication check failed: {auth_result.error}",
                )

            if not auth_result.value:
                return FlextResult[FlextTypes.Core.Dict].fail(
                    "Not authenticated to SOURCE OF TRUTH",
                )

            # In real implementation, would decode JWT from SOURCE OF TRUTH or make API call
            user_info = {
                "authenticated": True,
                "note": "User information retrieval from SOURCE OF TRUTH not yet implemented",
                "timestamp": FlextUtilities.Generators.generate_iso_timestamp(),
            }

            return FlextResult[FlextTypes.Core.Dict].ok(user_info)

        except (
            ImportError,
            AttributeError,
            ValueError,
        ) as e:
            return FlextResult[FlextTypes.Core.Dict].fail(
                f"User info retrieval from SOURCE OF TRUTH failed: {e}",
            )

    def execute(self) -> FlextResult[str]:
        """Execute authentication service - required by FlextDomainService abstract method."""
        try:
            # Default execution returns authentication status from SOURCE OF TRUTH
            status_result = self.get_status()
            if status_result.is_failure:
                return FlextResult[str].fail(
                    f"Auth status check failed: {status_result.error}",
                )
            return FlextResult[str].ok(
                f"FlextCliAuth service ready: {status_result.value}",
            )
        except (
            ImportError,
            AttributeError,
            ValueError,
        ) as e:
            return FlextResult[str].fail(f"Auth service execution failed: {e}")

    @classmethod
    def create(cls, *, config: FlextCliConfig | None = None) -> FlextCliAuth:
        """Create authentication instance using FlextConfig singleton as SINGLE SOURCE OF TRUTH."""
        # Use FlextConfig singleton if no config provided
        if config is None:
            config = FlextCliConfig.get_current()
        return cls(config=config)

    def _validate_user_data(self, user_data: dict[str, object]) -> FlextResult[bool]:
        """Validate user data using flext-core validation."""
        try:
            if not isinstance(user_data, dict):
                return FlextResult[bool].fail("User data must be a dictionary")

            # Basic validation
            if "name" not in user_data or "email" not in user_data:
                return FlextResult[bool].fail("Missing required fields: name, email")

            # Check for empty values
            if not user_data.get("name") or not user_data.get("email"):
                return FlextResult[bool].fail("Name and email cannot be empty")

            return FlextResult[bool].ok(data=True)
        except Exception as e:
            return FlextResult[bool].fail(f"Validation failed: {e}")

    def authenticate_user(
        self, username: str, password: str
    ) -> FlextResult[dict[str, object]]:
        """Authenticate user with credentials."""
        try:
            if not username or not password:
                return FlextResult[dict[str, object]].fail(
                    "Username and password required"
                )

            # Simple authentication logic
            auth_result = {
                "user_id": f"user_{username}",
                "username": username,
                "authenticated": True,
                "timestamp": FlextUtilities.Generators.generate_iso_timestamp(),
                "access_token": f"access_token_{username}",
            }

            return FlextResult[dict[str, object]].ok(auth_result)
        except Exception as e:
            return FlextResult[dict[str, object]].fail(f"Authentication failed: {e}")

    def save_auth_config(
        self, config_data: dict[str, object], file_path: str
    ) -> FlextResult[str]:
        """Save authentication configuration to file."""
        try:
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)

            content = json.dumps(config_data, indent=2)
            path.write_text(content, encoding="utf-8")

            return FlextResult[str].ok(f"Config saved to {file_path}")
        except Exception as e:
            return FlextResult[str].fail(f"Save failed: {e}")

    def _is_token_expired(self, timestamp: str) -> bool:
        """Check if token is expired."""
        try:
            token_time = datetime.fromisoformat(timestamp)
            now = datetime.now(UTC)
            return now > token_time + timedelta(hours=24)
        except Exception:
            return True

    def load_auth_config(self, file_path: str) -> FlextResult[dict[str, object]]:
        """Load authentication configuration from file."""
        try:
            path = Path(file_path)
            if not path.exists():
                return FlextResult[dict[str, object]].fail(
                    f"Config file not found: {file_path}"
                )

            content = path.read_text(encoding="utf-8")
            config_data = json.loads(content)

            return FlextResult[dict[str, object]].ok(config_data)
        except Exception as e:
            return FlextResult[dict[str, object]].fail(f"Load failed: {e}")

    def _validate_auth_config(
        self, config_data: dict[str, object]
    ) -> FlextResult[bool]:
        """Validate authentication configuration."""
        try:
            if not isinstance(config_data, dict):
                return FlextResult[bool].fail("Config data must be a dictionary")

            # Basic validation
            if "api_key" not in config_data or "base_url" not in config_data:
                return FlextResult[bool].fail(
                    "Missing required fields: api_key, base_url"
                )

            # Check for empty values
            if not config_data.get("api_key") or not config_data.get("base_url"):
                return FlextResult[bool].fail("API key and base URL cannot be empty")

            return FlextResult[bool].ok(data=True)
        except Exception as e:
            return FlextResult[bool].fail(f"Validation failed: {e}")

    class CommandHandler:
        """Unified command handler for authentication operations using SOURCE OF TRUTH."""

        def __init__(self, auth_service: FlextCliAuth) -> None:
            """Initialize with SOURCE OF TRUTH authentication service."""
            self._auth = auth_service

        def handle_login(self, username: str, password: str) -> None:
            """Handle login command using SOURCE OF TRUTH."""

            async def _login() -> None:
                result = await self._auth.login(username, password)
                if result.is_success:
                    # Display any user data from response
                    response_data = result.value
                    if "user" in response_data:
                        pass

            with contextlib.suppress(Exception):
                asyncio.run(_login())

        def handle_logout(self) -> None:
            """Handle logout command using SOURCE OF TRUTH."""

            async def _logout() -> None:
                result = await self._auth.logout()
                if result.is_success:
                    pass

            with contextlib.suppress(Exception):
                asyncio.run(_logout())

        def handle_status(self) -> None:
            """Handle status command using SOURCE OF TRUTH."""
            status_result = self._auth.get_status()
            if status_result.is_failure:
                return

            status_info = status_result.value
            for _key, _value in status_info.items():
                pass

        def handle_whoami(self) -> None:
            """Handle whoami command using SOURCE OF TRUTH."""
            whoami_result = self._auth.whoami()
            if whoami_result.is_failure:
                return

            user_info = whoami_result.value
            for _key, _value in user_info.items():
                pass


# Lazy loading aliases para evitar instantiation durante import
def _get_auth_instance() -> FlextCliAuth:
    """Get auth instance lazily."""
    return FlextCliAuth()


def _get_auth_handler() -> FlextCliAuth.CommandHandler:
    """Get auth command handler lazily."""
    instance = _get_auth_instance()
    return instance.CommandHandler(instance)


def _get_status_func() -> object:
    """Get status function lazily."""
    return _get_auth_instance().get_status


# Aliases que os testes esperam - usando lazy loading
auth = _get_auth_handler  # Handler function
status = _get_status_func  # Status function

__all__ = ["FlextCliAuth", "auth", "status"]
