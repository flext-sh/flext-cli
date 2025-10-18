"""FLEXT CLI Authentication Service - Security-focused auth handling.

Consolidates all authentication operations from api.py into a dedicated security service.
Implements FlextCliProtocols.CliAuthProvider through structural subtyping.

Key operations:
- Token-based authentication
- Credential-based authentication with validation
- Token persistence (save/load/clear)
- Session authentication state tracking

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import secrets
from typing import cast

from flext_core import FlextResult, FlextTypes

from flext_cli.config import FlextCliConfig
from flext_cli.constants import FlextCliConstants
from flext_cli.file_tools import FlextCliFileTools
from flext_cli.typings import FlextCliTypes


class FlextCliAuthService:
    """Security-focused authentication service.

    Consolidates authentication operations with proper token lifecycle management,
    credential validation, and secure session tracking.

    Implements FlextCliProtocols.CliAuthProvider through structural subtyping:
    - authenticate() → FlextResult[str]
    - validate_token() → FlextResult[bool]
    - get_auth_token() → FlextResult[str]
    - is_authenticated() → bool
    - clear_auth_tokens() → FlextResult[None]
    """

    def __init__(
        self,
        config: FlextCliConfig,
        file_tools: FlextCliFileTools,
    ) -> None:
        """Initialize auth service with dependencies.

        Args:
            config: CLI configuration for token file paths
            file_tools: File operations for token persistence

        """
        self.config = config
        self.file_tools = file_tools
        self._valid_tokens: set[str] = set()

    def authenticate(
        self, credentials: FlextCliTypes.Auth.CredentialsData
    ) -> FlextResult[str]:
        """Authenticate user with provided credentials.

        Supports two authentication methods:
        1. Token-based: {token: "..."}
        2. Credentials-based: {username: "...", password: "..."}

        Args:
            credentials: Authentication data dict

        Returns:
            FlextResult[str]: Generated/provided token or error

        """
        if FlextCliConstants.DictKeys.TOKEN in credentials:
            return self._authenticate_with_token(credentials)
        if (
            FlextCliConstants.DictKeys.USERNAME in credentials
            and FlextCliConstants.DictKeys.PASSWORD in credentials
        ):
            return self._authenticate_with_credentials(credentials)
        return FlextResult[str].fail(
            FlextCliConstants.ErrorMessages.INVALID_CREDENTIALS
        )

    def _authenticate_with_token(
        self, credentials: FlextCliTypes.Auth.CredentialsData
    ) -> FlextResult[str]:
        """Authenticate using provided token.

        Args:
            credentials: Must contain 'token' key

        Returns:
            FlextResult[str]: Token or error

        """
        token = str(credentials[FlextCliConstants.DictKeys.TOKEN])
        if not token.strip():
            return FlextResult[str].fail(FlextCliConstants.ErrorMessages.TOKEN_EMPTY)
        save_result = self.save_auth_token(token)
        if save_result.is_failure:
            return FlextResult[str].fail(
                FlextCliConstants.ErrorMessages.TOKEN_SAVE_FAILED.format(
                    error=save_result.error
                )
            )
        return FlextResult[str].ok(token)

    def _authenticate_with_credentials(
        self, credentials: FlextCliTypes.Auth.CredentialsData
    ) -> FlextResult[str]:
        """Authenticate using username/password.

        Args:
            credentials: Must contain 'username' and 'password' keys

        Returns:
            FlextResult[str]: Generated token or error

        """
        username = str(credentials[FlextCliConstants.DictKeys.USERNAME])
        password = str(credentials[FlextCliConstants.DictKeys.PASSWORD])

        # Validate credentials
        validation = self.validate_credentials(username, password)
        if validation.is_failure:
            return FlextResult[str].fail(validation.error)

        # Generate token
        token = secrets.token_urlsafe(
            FlextCliConstants.APIDefaults.TOKEN_GENERATION_BYTES
        )
        self._valid_tokens.add(token)

        return FlextResult[str].ok(token)

    def validate_credentials(self, username: str, password: str) -> FlextResult[None]:
        """Validate username and password meet security requirements.

        Args:
            username: Username to validate
            password: Password to validate

        Returns:
            FlextResult[None]: Success or validation error

        """
        if not username or not password:
            return FlextResult[None].fail(
                FlextCliConstants.ErrorMessages.USERNAME_PASSWORD_REQUIRED
            )

        if len(username) < FlextCliConstants.Auth.MIN_USERNAME_LENGTH:
            return FlextResult[None].fail(
                FlextCliConstants.ErrorMessages.USERNAME_TOO_SHORT
            )

        if len(password) < FlextCliConstants.Auth.MIN_PASSWORD_LENGTH:
            return FlextResult[None].fail(
                FlextCliConstants.ErrorMessages.PASSWORD_TOO_SHORT
            )

        return FlextResult[None].ok(None)

    def save_auth_token(self, token: str) -> FlextResult[None]:
        """Save authentication token to file.

        Args:
            token: Token to persist

        Returns:
            FlextResult[None]: Success or error

        """
        if not token.strip():
            return FlextResult[None].fail(FlextCliConstants.ErrorMessages.TOKEN_EMPTY)

        token_path = self.config.token_file
        token_data: FlextCliTypes.Auth.CredentialsData = {
            FlextCliConstants.DictKeys.TOKEN: token
        }

        # Use file tools for JSON persistence
        json_data: FlextTypes.JsonValue = cast("FlextTypes.JsonValue", token_data)
        write_result = self.file_tools.write_json_file(str(token_path), json_data)
        if write_result.is_failure:
            return FlextResult[None].fail(
                FlextCliConstants.ErrorMessages.TOKEN_SAVE_FAILED.format(
                    error=write_result.error
                )
            )

        self._valid_tokens.add(token)
        return FlextResult[None].ok(None)

    def get_auth_token(self) -> FlextResult[str]:
        """Retrieve authentication token from file.

        Returns:
            FlextResult[str]: Token or error

        """
        token_path = self.config.token_file

        # Use file tools for JSON retrieval
        read_result = self.file_tools.read_json_file(str(token_path))
        if read_result.is_failure:
            if (
                FlextCliConstants.APIDefaults.FILE_ERROR_INDICATOR
                in str(read_result.error).lower()
            ):
                return FlextResult[str].fail(
                    FlextCliConstants.ErrorMessages.TOKEN_FILE_NOT_FOUND
                )
            return FlextResult[str].fail(
                FlextCliConstants.ErrorMessages.TOKEN_LOAD_FAILED.format(
                    error=read_result.error
                )
            )

        # Type guard: validate data structure
        data = read_result.unwrap()
        if not isinstance(data, dict):
            return FlextResult[str].fail(
                FlextCliConstants.APIDefaults.TOKEN_DATA_TYPE_ERROR
            )

        token = data.get(FlextCliConstants.DictKeys.TOKEN)
        if not token:
            return FlextResult[str].fail(
                FlextCliConstants.ErrorMessages.TOKEN_FILE_EMPTY
            )

        if not isinstance(token, str):
            return FlextResult[str].fail(
                FlextCliConstants.APIDefaults.TOKEN_VALUE_TYPE_ERROR
            )

        return FlextResult[str].ok(token)

    def validate_token(self, token: str) -> FlextResult[bool]:
        """Validate if token is valid and authentic.

        Args:
            token: Token to validate

        Returns:
            FlextResult[bool]: True if valid, False otherwise or error

        """
        if not token.strip():
            return FlextResult[bool].ok(False)

        # Check against valid tokens set
        is_valid = token in self._valid_tokens
        return FlextResult[bool].ok(is_valid)

    def is_authenticated(self) -> bool:
        """Check if user is currently authenticated.

        Returns:
            bool: True if authenticated (token exists and valid)

        """
        token_result = self.get_auth_token()
        return token_result.is_success

    def clear_auth_tokens(self) -> FlextResult[None]:
        """Clear all authentication tokens and session data.

        Returns:
            FlextResult[None]: Success or error

        """
        token_path = self.config.token_file
        refresh_token_path = self.config.refresh_token_file

        # Use file tools for file deletion
        delete_token_result = self.file_tools.delete_file(str(token_path))
        delete_refresh_result = self.file_tools.delete_file(str(refresh_token_path))

        # Check if either deletion failed (but don't fail if file doesn't exist)
        if (
            delete_token_result.is_failure
            and FlextCliConstants.APIDefaults.FILE_ERROR_INDICATOR
            not in str(delete_token_result.error).lower()
        ):
            return FlextResult[None].fail(
                FlextCliConstants.ErrorMessages.FAILED_CLEAR_CREDENTIALS.format(
                    error=delete_token_result.error
                )
            )

        if (
            delete_refresh_result.is_failure
            and FlextCliConstants.APIDefaults.FILE_ERROR_INDICATOR
            not in str(delete_refresh_result.error).lower()
        ):
            return FlextResult[None].fail(
                FlextCliConstants.ErrorMessages.FAILED_CLEAR_CREDENTIALS.format(
                    error=delete_refresh_result.error
                )
            )

        self._valid_tokens.clear()
        return FlextResult[None].ok(None)


__all__ = [
    "FlextCliAuthService",
]
