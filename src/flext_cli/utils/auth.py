"""Auth utilities re-export to match legacy imports in tests."""

from __future__ import annotations

from pathlib import Path

from flext_core import FlextResult

from flext_cli.config import get_config  # used in tests for paths

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
        return bool(cfg.auto_refresh and (get_refresh_token() is not None))
    # Otherwise look into nested auth config
    auth_cfg = getattr(cfg, "auth", None)
    return bool(
        bool(getattr(auth_cfg, "auto_refresh", False))
        and (get_refresh_token() is not None),
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


def save_auth_token(token: str) -> FlextResult[None]:
    """Save auth token to disk with secure permissions.

    Creates parent directories, writes token, and chmod 600.
    Returns failure on filesystem or permission errors.
    """
    try:
        token_path = get_token_path()
        token_path.parent.mkdir(parents=True, exist_ok=True)
        token_path.write_text(token, encoding="utf-8")
        try:
            token_path.chmod(0o600)
        except Exception as e:  # chmod may fail on some platforms
            return FlextResult.fail(f"Failed to save auth token: {e}")
        return FlextResult.ok(None)
    except (OSError, PermissionError, ValueError) as e:
        return FlextResult.fail(f"Failed to save auth token: {e}")


def save_refresh_token(refresh_token: str) -> FlextResult[None]:
    """Save refresh token to disk with secure permissions."""
    try:
        path = get_refresh_token_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(refresh_token, encoding="utf-8")
        try:
            path.chmod(0o600)
        except Exception as e:
            return FlextResult.fail(f"Failed to save refresh token: {e}")
        return FlextResult.ok(None)
    except (OSError, PermissionError, ValueError) as e:
        return FlextResult.fail(f"Failed to save refresh token: {e}")


def get_auth_token() -> str | None:
    """Load auth token contents if file exists; returns None if missing."""
    path = get_token_path()
    if not path.exists():
        return None
    try:
        return path.read_text(encoding="utf-8").strip()
    except (OSError, UnicodeDecodeError):
        return None


def get_refresh_token() -> str | None:
    """Load refresh token contents if file exists; returns None if missing."""
    path = get_refresh_token_path()
    if not path.exists():
        return None
    try:
        return path.read_text(encoding="utf-8").strip()
    except (OSError, UnicodeDecodeError):
        return None


def clear_auth_tokens() -> FlextResult[None]:
    """Delete both token files if present; report errors when unlink fails."""
    try:
        token_path = get_token_path()
        refresh_path = get_refresh_token_path()
        if token_path.exists():
            token_path.unlink()
        if refresh_path.exists():
            refresh_path.unlink()
        return FlextResult.ok(None)
    except (OSError, PermissionError) as e:
        return FlextResult.fail(f"Failed to clear auth tokens: {e}")


def is_authenticated() -> bool:
    """Return True if token file is present (even if empty)."""
    return get_auth_token() is not None
