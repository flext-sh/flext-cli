"""Authentication utilities for FLX CLI."""

from __future__ import annotations

from pathlib import Path


def get_token_path() -> Path:
    """Get path to token file."""
    return Path.home() / ".flx" / ".token"


def save_auth_token(token: str) -> None:
    """Save authentication token to file."""
    token_path = get_token_path()
    token_path.parent.mkdir(parents=True, exist_ok=True)

    # Save token with restricted permissions
    token_path.write_text(token)
    token_path.chmod(0o600)  # Read/write for owner only


def get_auth_token() -> str | None:
    """Get saved authentication token."""
    token_path = get_token_path()

    if token_path.exists():
        return token_path.read_text().strip()

    return None


def clear_auth_token() -> None:
    """Clear saved authentication token."""
    token_path = get_token_path()

    if token_path.exists():
        token_path.unlink()


def is_authenticated() -> bool:
    """Check if user is authenticated."""
    return get_auth_token() is not None
