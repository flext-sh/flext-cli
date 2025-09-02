"""Class-based bridge for authentication operations (no free helpers)."""

from __future__ import annotations

from pathlib import Path

from flext_core import FlextResult

from flext_cli.auth import (
    get_auth_token,
    get_refresh_token,
    get_refresh_token_path,
    get_token_path,
    is_authenticated,
    save_auth_token,
    save_refresh_token,
)
from flext_cli.constants import FlextCliConstants


class FlextCliAuthBridge:
    """Class-based bridge exposing auth operations as static methods."""

    @staticmethod
    def get_auth_data_path() -> Path:
        return (
            Path.home()
            / FlextCliConstants.FLEXT_DIR_NAME
            / FlextCliConstants.AUTH_DIR_NAME
        )

    @staticmethod
    def get_token_path() -> Path:
        return get_token_path()

    @staticmethod
    def get_refresh_token_path() -> Path:
        return get_refresh_token_path()

    @staticmethod
    def save_auth_token(
        token: str, *, token_path: Path | None = None
    ) -> FlextResult[None]:
        return save_auth_token(token, token_path=token_path)

    @staticmethod
    def save_refresh_token(
        token: str, *, token_path: Path | None = None
    ) -> FlextResult[None]:
        # Map legacy kw to new kw
        return save_refresh_token(token, refresh_token_path=token_path)

    @staticmethod
    def get_auth_token(*, token_path: Path | None = None) -> FlextResult[str]:
        return get_auth_token(token_path=token_path)

    @staticmethod
    def get_refresh_token(*, token_path: Path | None = None) -> FlextResult[str]:
        return get_refresh_token(refresh_token_path=token_path)

    @staticmethod
    def is_authenticated(*, token_path: Path | None = None) -> bool:
        return is_authenticated(token_path=token_path)


__all__ = [
    "FlextCliAuthBridge",
]
