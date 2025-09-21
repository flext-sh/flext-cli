"""FLEXT CLI Authentication - Unified authentication service using flext-core directly.

Single responsibility authentication service eliminating ALL loose functions
and wrapper patterns. Uses flext-core utilities directly with SOURCE OF TRUTH
principle for all authentication metadata and operations.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import asyncio
import json
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import ClassVar

from flext_cli.configs import FlextCliConfigs
from flext_cli.models import FlextCliModels
from flext_cli.protocols import FlextCliProtocols
from flext_cli.typings import FlextCliTypes
from flext_core import (
    FlextContainer,
    FlextDomainService,
    FlextLogger,
    FlextResult,
    FlextTypes,
    FlextUtilities,
)


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

    # Use unified types and models from centralized modules - marked as ClassVar for Pydantic
    UserData: ClassVar[type[FlextCliTypes.UserData]] = FlextCliTypes.UserData
    AuthStatus: ClassVar[type[FlextCliTypes.AuthStatus]] = FlextCliTypes.AuthStatus
    LoginCredentials: ClassVar[type[FlextCliTypes.LoginCredentials]] = (
        FlextCliTypes.LoginCredentials
    )
    AuthConfig: ClassVar[type[FlextCliModels.AuthConfig]] = FlextCliModels.AuthConfig
    TokenData: ClassVar[type[FlextCliTypes.TokenData]] = FlextCliTypes.TokenData
    # Instance attributes with proper type annotations
    _config: FlextCliConfigs
    # TokenPaths: ClassVar[type[FlextCliTypes.TokenPaths]] = FlextCliTypes.TokenPaths

    def __init__(
        self,
        *,
        config: FlextCliConfigs | None = None,
        auth_client: FlextCliProtocols.AuthenticationClient | None = None,
        **_data: object,
    ) -> None:
        """Initialize authentication service with flext-core dependencies and SOURCE OF TRUTH."""
        super().__init__()
        self._container = FlextContainer.get_global()
        self._logger = FlextLogger(__name__)

        # Load configuration from FlextConfig singleton as SINGLE SOURCE OF TRUTH
        if config is None:
            self._config = FlextCliConfigs.get_current()
        else:
            self._config = config

        # Dependency injection for authentication client
        self._auth_client = auth_client

    @property
    def config(self) -> FlextCliConfigs:
        """Get current authentication configuration.

        Returns:
            FlextCliConfigs: Current CLI configuration.

        """
        if not isinstance(self._config, FlextCliConfigs):
            # Initialize with FlextCliConfigs if not already set
            self._config = FlextCliConfigs.get_current()
        return self._config

    def _update_from_config(self) -> None:
        """Update authentication configuration from FlextConfig singleton.

        This method allows the authentication service to refresh its configuration
        from the FlextConfig singleton, ensuring it always uses the latest
        configuration values.

        """
        # Update configuration from singleton
        self._config = FlextCliConfigs.get_current()

    def get_token_paths(self) -> FlextResult[FlextCliTypes.TokenPaths]:
        """Get token paths from SOURCE OF TRUTH configuration.

        Returns:
            FlextResult[FlextCliTypes.TokenPaths]: Token paths or error result.

        """
        try:
            # Extract paths from SOURCE OF TRUTH config
            paths: FlextCliTypes.TokenPaths = {
                "token_path": self._config.token_file,
                "refresh_token_path": self._config.refresh_token_file,
            }

            return FlextResult[FlextCliTypes.TokenPaths].ok(paths)

        except (
            AttributeError,
            ValueError,
        ) as e:
            return FlextResult[FlextCliTypes.TokenPaths].fail(
                f"Token paths from SOURCE OF TRUTH failed: {e}",
            )

    def _get_token_path(self) -> Path:
        """Get authentication token file path.

        Returns:
            Path: Authentication token file path.

        """
        return self._config.token_file

    def _get_refresh_token_path(self) -> Path:
        """Get refresh token file path.

        Returns:
            Path: Refresh token file path.

        """
        return self._config.refresh_token_file

    def _save_refresh_token(self, token: str) -> FlextResult[None]:
        """Save refresh token to storage.

        Returns:
            FlextResult[None]: Success or failure result of save operation.

        """
        return self._save_token_to_storage(
            token,
            "refresh",
            self._config.refresh_token_file,
        )

    def _get_refresh_token(self) -> FlextResult[str]:
        """Get refresh token from storage.

        Returns:
            FlextResult[str]: Refresh token string or error result.

        """
        try:
            if not self._config.refresh_token_file.exists():
                return FlextResult[str].fail("Refresh token file not found")

            content = self._config.refresh_token_file.read_text(encoding="utf-8")
            if not content.strip():
                return FlextResult[str].fail("Refresh token file is empty")

            return FlextResult[str].ok(content.strip())
        except (
            AttributeError,
            ValueError,
        ) as e:
            return FlextResult[str].fail(f"Failed to read refresh token: {e}")

    def _should_auto_refresh(self) -> bool:
        """Check if auto refresh is enabled.

        Returns:
            bool: True if auto refresh is enabled, False otherwise.

        """
        return bool(getattr(self._config, "auto_refresh", False))

    def _validate_credentials(
        self,
        credentials: FlextCliTypes.LoginCredentials,
    ) -> FlextResult[None]:
        """Validate login credentials using SOURCE OF TRUTH validation rules.

        Returns:
            FlextResult[None]: Success or failure result of validation.

        """
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
            AttributeError,
            ValueError,
        ) as e:
            return FlextResult[None].fail(
                f"Credential validation using SOURCE OF TRUTH failed: {e}",
            )

    def _save_token_to_storage(
        self,
        token: str,
        token_type: str,
        file_path: Path,
    ) -> FlextResult[None]:
        """Save token to secure storage using SOURCE OF TRUTH security patterns.

        Returns:
            FlextResult[None]: Success or failure result of save operation.

        """
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

    def _load_token_from_storage(
        self,
        file_path: Path,
        token_type: str,
    ) -> FlextResult[str]:
        """Load token from secure storage using SOURCE OF TRUTH patterns.

        Returns:
            FlextResult[str]: Token string or error result.

        """
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

    def _save_auth_token(
        self,
        token: str,
        *,
        token_path: Path | None = None,
    ) -> FlextResult[None]:
        """Save authentication token using SOURCE OF TRUTH storage patterns.

        Returns:
            FlextResult[None]: Success or failure result of save operation.

        """
        try:
            paths_result = self.get_token_paths()
            if paths_result.is_failure:
                return FlextResult[None].fail(
                    f"Token paths from SOURCE OF TRUTH failed: {paths_result.error}",
                )

            paths = paths_result.value
            file_path = token_path or paths["token_path"]

            return self._save_token_to_storage(token, "Authentication token", file_path)

        except (
            AttributeError,
            ValueError,
        ) as e:
            return FlextResult[None].fail(
                f"Auth token save using SOURCE OF TRUTH failed: {e}",
            )

    def _get_auth_token(self, *, token_path: Path | None = None) -> FlextResult[str]:
        """Retrieve authentication token from SOURCE OF TRUTH storage.

        Returns:
            FlextResult[str]: Authentication token string or error result.

        """
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
            AttributeError,
            ValueError,
        ) as e:
            return FlextResult[str].fail(
                f"Auth token retrieval from SOURCE OF TRUTH failed: {e}",
            )

    def _clear_auth_tokens(self) -> FlextResult[None]:
        """Clear all authentication tokens from SOURCE OF TRUTH storage.

        Returns:
            FlextResult[None]: Success or failure result of clear operation.

        """
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
            AttributeError,
            ValueError,
        ) as e:
            return FlextResult[None].fail(
                f"Token clearing from SOURCE OF TRUTH failed: {e}",
            )

    def clear_auth_tokens(self) -> FlextResult[None]:
        """Public interface to clear all authentication tokens.

        Returns:
            FlextResult[None]: Success or failure result of clear operation.

        """
        return self._clear_auth_tokens()

    def load_token_from_storage(
        self, file_path: Path, token_type: str
    ) -> FlextResult[str]:
        """Public interface to load token from storage.

        Returns:
            FlextResult[str]: Token string or error result.

        """
        return self._load_token_from_storage(file_path, token_type)

    def get_auth_token(self, *, token_path: Path | None = None) -> FlextResult[str]:
        """Public interface to retrieve authentication token.

        Returns:
            FlextResult[str]: Authentication token string or error result.

        """
        return self._get_auth_token(token_path=token_path)

    def is_authenticated(self, *, token_path: Path | None = None) -> bool:
        """Public interface to check current authentication status.

        Returns:
            bool: True if authenticated, False otherwise.

        """
        return self._is_authenticated(token_path=token_path)

    def validate_credentials(
        self, credentials: FlextCliTypes.LoginCredentials
    ) -> FlextResult[None]:
        """Public interface to validate login credentials.

        Returns:
            FlextResult[None]: Success or failure result of validation.

        """
        return self._validate_credentials(credentials)

    def save_auth_token(
        self, token: str, *, token_path: Path | None = None
    ) -> FlextResult[None]:
        """Public interface to save authentication token.

        Returns:
            FlextResult[None]: Success or failure result of save operation.

        """
        return self._save_auth_token(token, token_path=token_path)

    def check_authentication_status(
        self, *, token_path: Path | None = None
    ) -> FlextResult[bool]:
        """Public interface to check authentication status.

        Returns:
            FlextResult[bool]: Authentication status or error result.

        """
        return self._check_authentication_status(token_path=token_path)

    def _is_authenticated(self, *, token_path: Path | None = None) -> bool:
        """Check current authentication status.

        Returns:
            bool: True if authenticated, False otherwise.

        """
        try:
            token_result = self.get_auth_token(token_path=token_path)
            return token_result.is_success and bool(token_result.value)
        except (
            ImportError,
            AttributeError,
            ValueError,
        ):
            return False

    def _check_authentication_status(
        self,
        *,
        token_path: Path | None = None,
    ) -> FlextResult[bool]:
        """Check authentication status using SOURCE OF TRUTH.

        Returns:
            FlextResult[bool]: Authentication status or error result.

        """
        try:
            authenticated = self.is_authenticated(token_path=token_path)
            return FlextResult[bool].ok(authenticated)
        except (
            AttributeError,
            ValueError,
        ) as e:
            return FlextResult[bool].fail(f"Authentication check failed: {e}")

    def _get_auth_headers(self) -> FlextResult[FlextTypes.Core.Headers]:
        """Get authentication headers using SOURCE OF TRUTH token.

        Returns:
            FlextResult[FlextTypes.Core.Headers]: Authentication headers or error result.

        """
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
            AttributeError,
            ValueError,
        ) as e:
            return FlextResult[FlextTypes.Core.Headers].fail(
                f"Auth headers from SOURCE OF TRUTH failed: {e}",
            )

    def login(
        self,
        username: str,
        password: str,
    ) -> FlextResult[FlextTypes.Core.Dict]:
        """Perform login using SOURCE OF TRUTH authentication flow.

        Returns:
            FlextResult[FlextTypes.Core.Dict]: Login result data or error result.

        """
        try:
            # Validate credentials using SOURCE OF TRUTH
            credentials: FlextCliTypes.LoginCredentials = {
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
                    "Authentication client not available",
                )

            # Handle async authentication client internally
            async def _perform_login() -> FlextResult[FlextTypes.Core.Dict]:
                try:
                    if self._auth_client is None:
                        return FlextResult[FlextTypes.Core.Dict].fail(
                            "Authentication client not available",
                        )
                    return await self._auth_client.login(username, password)
                except Exception as e:
                    return FlextResult[FlextTypes.Core.Dict].fail(
                        f"Authentication request failed: {e}",
                    )

            # Execute async operation and return FlextResult synchronously
            try:
                response = asyncio.run(_perform_login())
            except Exception as e:
                return FlextResult[FlextTypes.Core.Dict].fail(
                    f"Login execution failed: {e}",
                )

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
            AttributeError,
            ValueError,
        ) as e:
            # Explicit exception handling for caught types
            if isinstance(e, ValueError):
                return FlextResult[FlextTypes.Core.Dict].fail(
                    f"Validation error in SOURCE OF TRUTH: {e}",
                )
            # AttributeError
            return FlextResult[FlextTypes.Core.Dict].fail(
                f"Login validation from SOURCE OF TRUTH failed: {e}",
            )

    def logout(self) -> FlextResult[None]:
        """Perform logout using SOURCE OF TRUTH authentication flow.

        Returns:
            FlextResult[None]: Success or failure result of logout operation.

        """
        # Check authentication status using SOURCE OF TRUTH
        auth_result = self.check_authentication_status()
        if auth_result.is_failure:
            return FlextResult[None].fail(
                f"Authentication check failed: {auth_result.error}",
            )

        if not auth_result.value:
            return FlextResult[None].fail("Not authenticated to SOURCE OF TRUTH")

        # Attempt server logout using injected authentication client
        if self._auth_client is not None:
            # Handle async logout client internally
            async def _perform_logout() -> FlextResult[None]:
                if self._auth_client is not None:
                    await self._auth_client.logout()
                return FlextResult[None].ok(None)

            # Execute async operation internally
            logout_result = asyncio.run(_perform_logout())
            if logout_result.is_failure:
                self._logger.debug(f"Server logout warning: {logout_result.error}")

        # Always clear local tokens from SOURCE OF TRUTH storage
        clear_result = self.clear_auth_tokens()
        if clear_result.is_failure:
            return FlextResult[None].fail(
                f"Token cleanup from SOURCE OF TRUTH failed: {clear_result.error}",
            )

        return FlextResult[None].ok(None)

    def get_status(self) -> FlextResult[FlextCliTypes.AuthStatus]:
        """Get authentication status from SOURCE OF TRUTH.

        Returns:
            FlextResult[FlextCliTypes.AuthStatus]: Authentication status or error result.

        """
        # Get authentication status from SOURCE OF TRUTH
        auth_result = self.check_authentication_status()
        if auth_result.is_failure:
            return FlextResult[FlextCliTypes.AuthStatus].fail(
                f"Authentication check failed: {auth_result.error}",
            )

        authenticated = auth_result.value

        # Get paths from SOURCE OF TRUTH
        paths_result = self.get_token_paths()
        if paths_result.is_failure:
            return FlextResult[FlextCliTypes.AuthStatus].fail(
                f"Token paths from SOURCE OF TRUTH failed: {paths_result.error}",
            )

        paths = paths_result.value

        # Validate config has auto_refresh attribute
        if not hasattr(self._config, "auto_refresh"):
            return FlextResult[FlextCliTypes.AuthStatus].fail(
                "Configuration missing auto_refresh field",
            )

        # Extract username from token if available (placeholder implementation)
        username: str | None = None
        expires_at: str | None = None

        if authenticated:
            # In a real implementation, this would decode JWT token to extract username and expiry
            # For now, we provide None values to satisfy the TypedDict contract
            username = None  # Would extract from JWT token
            expires_at = None  # Would extract from JWT token

        # Build status from SOURCE OF TRUTH data with all required TypedDict fields
        status: FlextCliTypes.AuthStatus = {
            "authenticated": authenticated,
            "username": username,
            "expires_at": expires_at,
            "token_file": str(paths["token_path"]),
            "token_exists": paths["token_path"].exists(),
            "refresh_token_file": str(paths["refresh_token_path"]),
            "refresh_token_exists": paths["refresh_token_path"].exists(),
            "auto_refresh": self._config.auto_refresh,
        }

        return FlextResult[FlextCliTypes.AuthStatus].ok(status)

    def whoami(self) -> FlextResult[FlextTypes.Core.Dict]:
        """Get current user information from SOURCE OF TRUTH.

        Returns:
            FlextResult[FlextTypes.Core.Dict]: User information or error result.

        """
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

    def execute(self) -> FlextResult[str]:
        """Execute authentication service - required by FlextDomainService abstract method.

        Returns:
            FlextResult[str]: Authentication status string or error result.

        """
        # Default execution returns authentication status from SOURCE OF TRUTH
        status_result = self.get_status()
        if status_result.is_failure:
            return FlextResult[str].fail(
                f"Auth status check failed: {status_result.error}",
            )
        return FlextResult[str].ok(
            f"FlextCliAuth service ready: {status_result.value}",
        )

    @classmethod
    def create(cls, *, config: FlextCliConfigs | None = None) -> FlextCliAuth:
        """Create authentication instance using FlextConfig singleton as SINGLE SOURCE OF TRUTH.

        Returns:
            FlextCliAuth: New authentication instance.

        """
        # Use FlextConfig singleton if no config provided
        if config is None:
            config = FlextCliConfigs.get_current()
        return cls(config=config)

    def _validate_user_data(self, user_data: dict[str, object]) -> FlextResult[bool]:
        """Validate user data using flext-core validation.

        Returns:
            FlextResult[bool]: Validation result or error result.

        """
        try:
            # Basic validation
            if "name" not in user_data or "email" not in user_data:
                return FlextResult[bool].fail("Missing required fields: name, email")

            # Check for empty values
            if not user_data.get("name") or not user_data.get("email"):
                return FlextResult[bool].fail("Name and email cannot be empty")

            return FlextResult[bool].ok(True)
        except Exception as e:
            return FlextResult[bool].fail(f"Validation failed: {e}")

    def _authenticate_user(
        self,
        username: str,
        password: str,
    ) -> FlextResult[dict[str, object]]:
        """Authenticate user with credentials.

        Returns:
            FlextResult[dict[str, object]]: Authentication result or error result.

        """
        try:
            if not username or not password:
                return FlextResult[dict[str, object]].fail(
                    "Username and password required",
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

    def _save_auth_config(
        self,
        config_data: dict[str, object],
        file_path: str,
    ) -> FlextResult[str]:
        """Save authentication configuration to file.

        Returns:
            FlextResult[str]: Save result message or error result.

        """
        try:
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)

            content = json.dumps(config_data, indent=2)
            path.write_text(content, encoding="utf-8")

            return FlextResult[str].ok(f"Config saved to {file_path}")
        except Exception as e:
            return FlextResult[str].fail(f"Save failed: {e}")

    def _is_token_expired(self, timestamp: str) -> bool:
        """Check if token is expired.

        Returns:
            bool: True if token is expired, False otherwise.

        """
        if not timestamp:
            return True

        token_time = datetime.fromisoformat(timestamp)
        now = datetime.now(UTC)
        return now > token_time + timedelta(hours=24)

    def _load_auth_config(self, file_path: str) -> FlextResult[dict[str, object]]:
        """Load authentication configuration from file.

        Returns:
            FlextResult[dict[str, object]]: Configuration data or error result.

        """
        try:
            path = Path(file_path)
            if not path.exists():
                return FlextResult[dict[str, object]].fail(
                    f"Config file not found: {file_path}",
                )

            content = path.read_text(encoding="utf-8")
            config_data = json.loads(content)

            return FlextResult[dict[str, object]].ok(config_data)
        except Exception as e:
            return FlextResult[dict[str, object]].fail(f"Load failed: {e}")

    def _validate_auth_config(
        self,
        config_data: dict[str, object],
    ) -> FlextResult[bool]:
        """Validate authentication configuration.

        Returns:
            FlextResult[bool]: Validation result or error result.

        """
        try:
            # Basic validation
            if "api_key" not in config_data or "base_url" not in config_data:
                return FlextResult[bool].fail(
                    "Missing required fields: api_key, base_url",
                )

            # Check for empty values
            if not config_data.get("api_key") or not config_data.get("base_url"):
                return FlextResult[bool].fail("API key and base URL cannot be empty")

            return FlextResult[bool].ok(True)
        except Exception as e:
            return FlextResult[bool].fail(f"Validation failed: {e}")

    class CommandHandler:
        """Unified command handler for authentication operations using SOURCE OF TRUTH."""

        def __init__(self, auth_service: FlextCliAuth) -> None:
            """Initialize with SOURCE OF TRUTH authentication service."""
            self._auth = auth_service
            self._logger = FlextLogger(__name__)

        def handle_login(self, username: str, password: str) -> None:
            """Handle login command using SOURCE OF TRUTH."""
            result = self._auth.login(username, password)
            if result.is_success:
                # Display any user data from response
                response_data = result.value
                if "user" in response_data:
                    user = response_data["user"]
                    self._logger.info("login_successful", user=user)
                else:
                    self._logger.info(
                        "login_successful",
                        details="Login completed successfully",
                    )

        def handle_logout(self) -> None:
            """Handle logout command using SOURCE OF TRUTH."""
            result = self._auth.logout()
            if result.is_success:
                # Handle successful logout - could show confirmation message
                self._logger.info(
                    "logout_successful",
                    details="Logout completed successfully",
                )

        def handle_status(self) -> None:
            """Handle status command using SOURCE OF TRUTH."""
            status_result = self._auth.get_status()
            if status_result.is_failure:
                return

            status_info = status_result.value
            for key, value in status_info.items():
                # Log status information - could be displayed to user
                self._logger.info("auth_status", key=key, value=value)

        def handle_whoami(self) -> None:
            """Handle whoami command using SOURCE OF TRUTH."""
            whoami_result = self._auth.whoami()
            if whoami_result.is_failure:
                return

            user_info = whoami_result.value
            for key, value in user_info.items():
                # Log user information - could be displayed to user
                self._logger.info("user_info", key=key, value=value)


__all__ = ["FlextCliAuth"]
