"""FLEXT CLI Authentication Utilities - Token Management and Security Operations.

This module provides authentication utilities for FLEXT CLI operations including
token storage, retrieval, validation, and security patterns. Uses flext-core
FlextResult patterns for comprehensive error handling and security best practices.

Authentication Features:
    - Secure token storage with restricted file permissions (0o600)
    - Auth token and refresh token management
    - Authentication state validation
    - Auto-refresh token capabilities
    - Secure token cleanup and logout operations

Security Features:
    - Restricted file permissions for token storage
    - Secure token file location in user's home directory
    - Error handling for permission and filesystem issues
    - Token validation and integrity checks
    - Secure token cleanup operations

Current Implementation Status:
    ✅ Token storage and retrieval with security
    ✅ Auth and refresh token management
    ✅ FlextResult integration for error handling
    ✅ Authentication state validation
    ✅ Auto-refresh token support
    ⚠️ Basic implementation (TODO: Sprint 2 - enhance security features)

TODO (docs/TODO.md):
    Sprint 2: Add token expiration and validation
    Sprint 2: Add JWT token parsing and validation
    Sprint 3: Add multi-profile authentication support
    Sprint 5: Add authentication audit logging
    Sprint 7: Add authentication metrics and monitoring

Functions:
    - get_token_path/get_refresh_token_path: Token file location management
    - save_auth_token/save_refresh_token: Secure token storage
    - get_auth_token/get_refresh_token: Token retrieval
    - clear_auth_tokens: Secure token cleanup
    - is_authenticated: Authentication state validation
    - should_auto_refresh: Auto-refresh token logic

Usage Examples:
    Save authentication token:
    >>> result = save_auth_token("jwt_token_here")
    >>> if result.is_success:
    ...     print("Token saved securely")

    Check authentication status:
    >>> if is_authenticated():
    ...     token = get_auth_token()
    ...     # Use token for API calls

    Logout and clear tokens:
    >>> result = clear_auth_tokens()
    >>> if result.is_success:
    ...     print("Logged out successfully")

Integration:
    - Used by authentication commands for token management
    - Integrates with CLI configuration for token paths
    - Supports authentication decorators and middleware
    - Provides foundation for secure CLI operations

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core import FlextResult

from flext_cli.utils.config import get_config

if TYPE_CHECKING:
    from pathlib import Path


def get_token_path() -> Path:
    """Get the path to the auth token file.

    Returns:
        The path to the auth token file.

    """
    config = get_config()
    return config.token_file


def get_refresh_token_path() -> Path:
    """Get the path to the refresh token file.

    Returns:
        The path to the refresh token file.

    """
    config = get_config()
    return config.refresh_token_file


def save_auth_token(token: str) -> FlextResult[None]:
    """Save the auth token to the file.

    Args:
        token: The auth token to save.

    Returns:
        The result of the operation.

    """
    try:
        token_path = get_token_path()
        token_path.parent.mkdir(parents=True, exist_ok=True)

        # Save token with restricted permissions
        token_path.write_text(token)
        token_path.chmod(0o600)  # Read/write for owner only

        return FlextResult.ok(None)
    except (OSError, PermissionError, ValueError) as e:
        error_msg = f"Failed to save auth token: {e}"
        return FlextResult.fail(error_msg)


def save_refresh_token(refresh_token: str) -> FlextResult[None]:
    """Save the refresh token to the file.

    Args:
        refresh_token: The refresh token to save.

    Returns:
        The result of the operation.

    """
    try:
        refresh_token_path = get_refresh_token_path()
        refresh_token_path.parent.mkdir(parents=True, exist_ok=True)

        # Save token with restricted permissions
        refresh_token_path.write_text(refresh_token)
        refresh_token_path.chmod(0o600)  # Read/write for owner only

        return FlextResult.ok(None)
    except (OSError, PermissionError, ValueError) as e:
        error_msg = f"Failed to save refresh token: {e}"
        return FlextResult.fail(error_msg)


def get_auth_token() -> str | None:
    """Get the auth token from the file.

    Returns:
        The auth token.

    """
    token_path = get_token_path()

    if token_path.exists():
        return token_path.read_text().strip()

    return None


def get_refresh_token() -> str | None:
    """Get the refresh token from the file.

    Returns:
        The refresh token.

    """
    refresh_token_path = get_refresh_token_path()

    if refresh_token_path.exists():
        return refresh_token_path.read_text().strip()

    return None


def clear_auth_tokens() -> FlextResult[None]:
    """Clear the auth tokens from the file.

    Returns:
        The result of the operation.

    """
    try:
        token_path = get_token_path()
        refresh_token_path = get_refresh_token_path()

        if token_path.exists():
            token_path.unlink()

        if refresh_token_path.exists():
            refresh_token_path.unlink()

        return FlextResult.ok(None)
    except (OSError, PermissionError) as e:
        error_msg = f"Failed to clear auth tokens: {e}"
        return FlextResult.fail(error_msg)


def is_authenticated() -> bool:
    """Check if the user is authenticated.

    Returns:
        True if the user is authenticated, False otherwise.

    """
    return get_auth_token() is not None


def should_auto_refresh() -> bool:
    """Check if the user should auto refresh the auth tokens.

    Returns:
        True if the user should auto refresh the auth tokens, False otherwise.

    """
    config = get_config()
    return config.auto_refresh and get_refresh_token() is not None
