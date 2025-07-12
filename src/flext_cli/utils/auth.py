"""Authentication utilities using flext-core patterns.

Version 0.7.0 - Refactored to use flext-core configuration.
No legacy token handling - all through CLIConfig.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_cli.utils.config import get_config

# Use centralized ServiceResult from flext-core - ELIMINATE DUPLICATION
from flext_core.domain.types import ServiceResult

if TYPE_CHECKING:
            from pathlib import Path


def get_token_path() -> Path:
    config = get_config()
    return config.token_file


def get_refresh_token_path() -> Path:
    config = get_config()
    return config.refresh_token_file


def save_auth_token(token: str) -> ServiceResult[None]:
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
    token_path = get_token_path()

    if token_path.exists():
        return token_path.read_text().strip()

    return None


def get_refresh_token() -> str | None:
    refresh_token_path = get_refresh_token_path()

    if refresh_token_path.exists():
        return refresh_token_path.read_text().strip()

    return None


def clear_auth_tokens() -> ServiceResult[None]:
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
    return get_auth_token() is not None


def should_auto_refresh() -> bool:
    config = get_config()
    return config.auto_refresh and get_refresh_token() is not None
