"""Auth utilities.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from pathlib import Path

from flext_core import FlextResult

from flext_cli.config import get_config

__all__ = [
    "clear_auth_tokens",
    "get_auth_token",
    "get_refresh_token",
    "get_refresh_token_path",
    "get_token_path",
    "is_authenticated",
    "save_auth_token",
    "save_refresh_token",
    "should_auto_refresh",
]


def should_auto_refresh() -> bool:
    """Return True if token auto-refresh should be performed."""
    """Return whether refresh tokens should be auto-refreshed based on config."""
    cfg = get_config()
    # If explicit auto_refresh exists at root, honor it first
    if hasattr(cfg, "auto_refresh"):
        return bool(cfg.auto_refresh and get_refresh_token().is_success)
    # Otherwise look into nested auth config
    auth_cfg = getattr(cfg, "auth", None)
    return bool(
        bool(getattr(auth_cfg, "auto_refresh", False))
        and get_refresh_token().is_success,
    )


def get_token_path() -> Path:
    """Return token path, honoring tests that patch get_config()."""
    cfg = get_config()
    direct = getattr(cfg, "token_file", None)
    if isinstance(direct, Path):
        return direct
    auth_cfg = getattr(cfg, "auth", None)
    token_path = getattr(auth_cfg, "token_file", None) if auth_cfg is not None else None
    if isinstance(token_path, Path):
        return token_path
    return Path.home() / ".flext" / "auth" / "token"


def get_refresh_token_path() -> Path:
    """Return refresh token path, honoring tests that patch get_config()."""
    cfg = get_config()
    direct = getattr(cfg, "refresh_token_file", None)
    if isinstance(direct, Path):
        return direct
    auth_cfg = getattr(cfg, "auth", None)
    refresh_path = (
        getattr(auth_cfg, "refresh_token_file", None) if auth_cfg is not None else None
    )
    if isinstance(refresh_path, Path):
        return refresh_path
    return Path.home() / ".flext" / "auth" / "refresh_token"


def save_auth_token(token: str, *, token_path: Path | None = None) -> FlextResult[None]:
    """Save auth token to disk with secure permissions.

    Args:
        token: The auth token to save
        token_path: Optional path to save token (defaults to configured path)

    Creates parent directories, writes token, and chmod 600.
    Returns failure on filesystem or permission errors.

    """
    # Validate token is not empty
    if not token or not token.strip():
        return FlextResult[None].fail("Token cannot be empty")

    try:
        path = token_path or get_token_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(token, encoding="utf-8")
        try:
            path.chmod(0o600)
        except Exception as e:  # chmod may fail on some platforms
            return FlextResult[None].fail(f"Failed to save auth token: {e}")
        return FlextResult[None].ok(None)
    except (OSError, PermissionError, ValueError) as e:
        return FlextResult[None].fail(f"Failed to save auth token: {e}")


def save_refresh_token(refresh_token: str, *, token_path: Path | None = None) -> FlextResult[None]:
    """Save refresh token to disk with secure permissions.

    Args:
        refresh_token: The refresh token to save
        token_path: Optional path to save token (defaults to configured path)

    """
    try:
        path = token_path or get_refresh_token_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(refresh_token, encoding="utf-8")
        try:
            path.chmod(0o600)
        except Exception as e:
            return FlextResult[None].fail(f"Failed to save refresh token: {e}")
        return FlextResult[None].ok(None)
    except (OSError, PermissionError, ValueError) as e:
        return FlextResult[None].fail(f"Failed to save refresh token: {e}")


def get_auth_token(*, token_path: Path | None = None) -> FlextResult[str]:
    """Load auth token contents if file exists; returns FlextResult.

    Args:
        token_path: Optional path to read token from (defaults to configured path)

    """
    path = token_path or get_token_path()
    if not path.exists():
        return FlextResult[str].fail("Token file not found")
    try:
        token = path.read_text(encoding="utf-8").strip()
        if token:
            return FlextResult[str].ok(token)
        return FlextResult[str].fail("Token file is empty")
    except (OSError, UnicodeDecodeError) as e:
        return FlextResult[str].fail(f"Failed to read token: {e}")


def get_refresh_token(*, token_path: Path | None = None) -> FlextResult[str]:
    """Load refresh token contents if file exists; returns FlextResult.

    Args:
        token_path: Optional path to read token from (defaults to configured path)

    """
    path = token_path or get_refresh_token_path()
    if not path.exists():
        return FlextResult[str].fail("Refresh token file not found")
    try:
        token = path.read_text(encoding="utf-8").strip()
        if token:
            return FlextResult[str].ok(token)
        return FlextResult[str].fail("Refresh token file is empty")
    except (OSError, UnicodeDecodeError) as e:
        return FlextResult[str].fail(f"Failed to read refresh token: {e}")


def clear_auth_tokens() -> FlextResult[None]:
    """Delete both token files if present; report errors when unlink fails."""
    try:
        token_path = get_token_path()
        refresh_path = get_refresh_token_path()
        if token_path.exists():
            token_path.unlink()
        if refresh_path.exists():
            refresh_path.unlink()
        return FlextResult[None].ok(None)
    except (OSError, PermissionError) as e:
        return FlextResult[None].fail(f"Failed to clear auth tokens: {e}")


def is_authenticated(*, token_path: Path | None = None) -> bool:
    """Return True if token file is present and contains valid token.

    Args:
        token_path: Optional path to check for token (defaults to configured path)

    """
    return get_auth_token(token_path=token_path).is_success
