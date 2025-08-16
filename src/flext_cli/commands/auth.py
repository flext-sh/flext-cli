"""Auth commands."""

from __future__ import annotations

import contextlib

import click

from flext_cli.cli_auth import (
    auth,
    clear_auth_tokens,
    get_auth_token,
    get_refresh_token,
    get_refresh_token_path,
    get_token_path,
    login as _cli_login,
    logout as _cli_logout,
    save_auth_token,
    save_refresh_token,
    status as _cli_status,
    whoami as _cli_whoami,
)
from flext_cli.flext_api_integration import FlextCLIApiClient as FlextApiClient

__all__ = [
    "FlextApiClient",
    "auth",
    "clear_auth_tokens",
    "get_auth_token",
    "get_refresh_token",
    "get_refresh_token_path",
    "get_token_path",
    "login",
    "logout",
    "save_auth_token",
    "save_refresh_token",
    "status",
    "whoami",
]

# Expose original Click commands directly
login = _cli_login
status = _cli_status
whoami = _cli_whoami

# Wrap logout callback to ensure clear_auth_tokens (patchable here) is invoked first
_original_logout_callback = getattr(_cli_logout, "callback", None)


@click.pass_context
def _logout_shim(ctx: click.Context) -> None:  # pragma: no cover - thin wrapper
    """Logout shim function.

    Args:
        ctx (click.Context): Description.

    """
    with contextlib.suppress(Exception):
        clear_auth_tokens()
    if callable(_original_logout_callback):
        _original_logout_callback(ctx)


_cli_logout.callback = _logout_shim
logout = _cli_logout
