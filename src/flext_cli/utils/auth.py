"""Authentication utilities using flext-core patterns.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import TYPE_CHECKING

# Use centralized ServiceResult from flext-core - ELIMINATE DUPLICATION
from flext_core.domain.types import ServiceResult

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


def save_auth_token(token: str) -> ServiceResult[None]:
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

        return ServiceResult.ok(None)
    except Exception as e:
        return ServiceResult.fail(f"Failed to save auth token: {e}")


def save_refresh_token(refresh_token: str) -> ServiceResult[None]:
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

        return ServiceResult.ok(None)
    except Exception as e:
        return ServiceResult.fail(f"Failed to save refresh token: {e}")


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


def clear_auth_tokens() -> ServiceResult[None]:
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

        return ServiceResult.ok(None)
    except Exception as e:
        return ServiceResult.fail(f"Failed to clear auth tokens: {e}")


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
