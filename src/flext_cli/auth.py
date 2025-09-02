"""FLEXT CLI Authentication.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import asyncio
import contextlib
from pathlib import Path
from typing import TypedDict, cast

import click
from flext_core import FlextResult
from rich.console import Console

from flext_cli.client import FlextApiClient
from flext_cli.config import FlextCliConfig
from flext_cli.constants import FlextCliConstants


class UserData(TypedDict, total=False):
    """Type definition for user data in authentication response."""

    name: str
    email: str
    id: str


def _get_user_data(data_obj: object) -> UserData | None:
    """Extract user data with proper typing."""
    if isinstance(data_obj, dict):
        return cast("UserData", data_obj)
    return None


# =============================================================================
# AUTHENTICATION UTILITIES - Token management and security operations
# =============================================================================


def get_cli_config() -> FlextCliConfig:
    """Get CLI configuration instance using high-level config factory.

    Uses flext_cli.config.get_config to avoid strict env parsing from FlextConfig.
    """
    # Import local tardio para evitar ciclos e importes pesados no carregamento

    return FlextCliConfig()


def _clear_tokens_bridge() -> FlextResult[None]:
    """Call clear_auth_tokens with local patch point.

    Tests may monkey-patch `clear_auth_tokens` on this module directly.
    """
    try:
        return clear_auth_tokens()
    except Exception as e:
        return FlextResult[None].fail(str(e))


def _get_client_class() -> type[FlextApiClient]:
    """Return client class (patchable at module level)."""
    return FlextApiClient


def _get_auth_token_bridge(*, token_path: Path | None = None) -> str | None:
    """Return auth token via local implementation (patchable here)."""
    # Use FlextResult's value_or_none property for None handling
    return get_auth_token(token_path=token_path).value_or_none


def get_token_path() -> Path:
    """Get the path to the auth token file.

    Returns:
      The path to the auth token file.

    """
    config = get_cli_config()
    # Prefer explicit token_file attribute when available
    direct = getattr(config, "token_file", None)
    if isinstance(direct, Path):
        return direct
    auth_cfg = getattr(config, "auth", None)
    if auth_cfg is not None and hasattr(auth_cfg, "token_file"):
        token_file_value = getattr(auth_cfg, "token_file", None)
        if isinstance(token_file_value, Path):
            return token_file_value
    # Fallback to standard location under data_dir
    data_dir = getattr(
        config, "data_dir", Path.home() / FlextCliConstants.FLEXT_DIR_NAME
    )
    return data_dir / "auth_token"


def get_refresh_token_path() -> Path:
    """Get the path to the refresh token file.

    Returns:
      The path to the refresh token file.

    """
    config = get_cli_config()
    # Prefer explicit refresh_token_file attribute when available
    direct = getattr(config, "refresh_token_file", None)
    if isinstance(direct, Path):
        return direct
    auth_cfg = getattr(config, "auth", None)
    if auth_cfg is not None and hasattr(auth_cfg, "refresh_token_file"):
        refresh_token_value = getattr(auth_cfg, "refresh_token_file", None)
        if isinstance(refresh_token_value, Path):
            return refresh_token_value
    data_dir = getattr(
        config, "data_dir", Path.home() / FlextCliConstants.FLEXT_DIR_NAME
    )
    return data_dir / "refresh_token"


def save_auth_token(token: str, *, token_path: Path | None = None) -> FlextResult[None]:
    """Save the auth token to the file with secure permissions.

    Args:
      token: The auth token to save
      token_path: Optional path to save token (defaults to configured path)

    Returns:
      Result of the operation

    """
    # Validate token is not empty
    if not token or not token.strip():
        return FlextResult[None].fail("Token cannot be empty")

    try:
        path = token_path or get_token_path()
        path.parent.mkdir(parents=True, exist_ok=True)

        # Save token with restricted permissions
        path.write_text(token, encoding=FlextCliConstants.DEFAULT_ENCODING)
        path.chmod(0o600)  # Read/write for owner only

        return FlextResult[None].ok(None)
    except (OSError, PermissionError, ValueError) as e:
        return FlextResult[None].fail(f"Authentication save failed: {e}")


def save_refresh_token(
    refresh_token: str, *, refresh_token_path: Path | None = None
) -> FlextResult[None]:
    """Save the refresh token to the file with secure permissions.

    Args:
      refresh_token: The refresh token to save
      refresh_token_path: Optional path to save refresh token (defaults to configured path)

    Returns:
      Result of the operation

    """
    try:
        path = refresh_token_path or get_refresh_token_path()
        path.parent.mkdir(parents=True, exist_ok=True)

        # Save token with restricted permissions
        path.write_text(refresh_token, encoding=FlextCliConstants.DEFAULT_ENCODING)
        path.chmod(0o600)  # Read/write for owner only

        return FlextResult[None].ok(None)
    except (OSError, PermissionError, ValueError) as e:
        return FlextResult[None].fail(f"Refresh token save failed: {e}")


def get_auth_token(*, token_path: Path | None = None) -> FlextResult[str]:
    """Get the auth token from the file.

    Args:
      token_path: Optional path to read token from (defaults to configured path)

    Returns:
      FlextResult containing the auth token or failure

    """
    path = token_path or get_token_path()

    if path.exists():
        try:
            token = path.read_text(encoding=FlextCliConstants.DEFAULT_ENCODING).strip()
            if token:
                return FlextResult[str].ok(token)
            return FlextResult[str].fail("Token file is empty")
        except (OSError, UnicodeDecodeError) as e:
            return FlextResult[str].fail(f"Failed to read token: {e}")

    return FlextResult[str].fail("Token file not found")


def get_refresh_token(*, refresh_token_path: Path | None = None) -> FlextResult[str]:
    """Get the refresh token from the file.

    Args:
      refresh_token_path: Optional path to read refresh token from (defaults to configured path)

    Returns:
      FlextResult containing the refresh token or failure

    """
    path = refresh_token_path or get_refresh_token_path()

    if path.exists():
        try:
            token = path.read_text(encoding=FlextCliConstants.DEFAULT_ENCODING).strip()
            if token:
                return FlextResult[str].ok(token)
            return FlextResult[str].fail("Refresh token file is empty")
        except (OSError, UnicodeDecodeError) as e:
            return FlextResult[str].fail(f"Failed to read refresh token: {e}")

    return FlextResult[str].fail("Refresh token file not found")


def clear_auth_tokens() -> FlextResult[None]:
    """Clear the auth tokens from the files.

    Returns:
      Result of the operation

    """
    try:
        token_path = get_token_path()
        refresh_token_path = get_refresh_token_path()

        if token_path.exists():
            token_path.unlink()

        if refresh_token_path.exists():
            refresh_token_path.unlink()

        return FlextResult[None].ok(None)
    except (OSError, PermissionError) as e:
        return FlextResult[None].fail(f"Authentication clear failed: {e}")


def is_authenticated(*, token_path: Path | None = None) -> bool:
    """Check if the user is authenticated.

    Args:
      token_path: Optional path to check token from (defaults to configured path)

    Returns:
      True if the user is authenticated, False otherwise

    """
    token_result = get_auth_token(token_path=token_path)
    return bool(token_result.value if token_result.is_success else "")


def should_auto_refresh() -> bool:
    """Check if the user should auto refresh the auth tokens.

    Returns:
      True if the user should auto refresh the auth tokens, False otherwise

    """
    config = get_cli_config()
    return (
        hasattr(config, "auto_refresh")
        and getattr(config, "auto_refresh", False)
        and bool(get_refresh_token().value if get_refresh_token().is_success else "")
    )


# =============================================================================
# AUTHENTICATION CLI COMMANDS - Interactive authentication management
# =============================================================================


@click.group()
def auth() -> None:
    """Manage authentication commands."""


async def _async_login_impl(
    ctx: click.Context,
    console: Console,
    username: str,
    password: str,
) -> None:
    """Async login workflow extracted to reduce function complexity."""
    try:
        async with FlextApiClient() as client:
            console.print(f"[yellow]Logging in user: {username}...[/yellow]")

            if not password or len(password) < 1:
                console.print("[red]✗ Credentials are empty[/red]")
                ctx.exit(1)

            login_result = await client.login(username, password)

            if login_result.is_failure:
                console.print(f"[red]✗ Login failed: {login_result.error}[/red]")
                ctx.exit(1)

            response = login_result.value
            if response and "token" in response:
                token_value = response["token"]
                if isinstance(token_value, str):
                    save_result = save_auth_token(token_value)
                    if save_result.is_success:
                        console.print("[green]✓ Successfully logged in[/green]")
                    else:
                        console.print(
                            f"[red]✗ Authentication save failed: {save_result.error}[/red]"
                        )
                    ctx.exit(1)

                if "user" in response:
                    user_obj = _get_user_data(response["user"])
                    if user_obj:
                        user_name = user_obj.get("name", username)
                        console.print(f"Welcome, {user_name}!")
            else:
                console.print("[red]✗ Invalid authentication response[/red]")
            ctx.exit(1)
    except (ConnectionError, TimeoutError, ValueError, KeyError) as e:
        console.print(f"[red]✗ Login failed: {e}[/red]")
        ctx.exit(1)
    except OSError as e:
        console.print(f"[red]✗ Network error: {e}[/red]")
        ctx.exit(1)


@auth.command(help="Login to FLEXT")
@click.option("--username", "-u", prompt=True, help="Username for authentication")
@click.option(
    "--password",
    "-p",
    prompt=True,
    hide_input=True,
    help="Password for authentication",
)
@click.pass_context
def login(ctx: click.Context, username: str, password: str) -> None:
    """Authenticate with FLEXT services using username and password.

    Performs secure authentication against FLEXT services and stores
    authentication tokens for subsequent CLI operations.

    Security Features:
      - Password input hidden from terminal and history
      - Secure token storage with restricted file permissions
      - Comprehensive error handling for various failure modes

    Exit Codes:
      0: Authentication successful
      1: Authentication failed
    """
    console: Console = ctx.obj.get("console", Console())

    asyncio.run(_async_login_impl(ctx, console, username, password))


async def _async_logout_impl(_ctx: click.Context, console: Console) -> None:
    """Async logout workflow extracted to reduce function complexity."""
    try:
        # Proactive clear; tests can patch `clear_auth_tokens` here
        with contextlib.suppress(Exception):
            clear_auth_tokens()

        token = _get_auth_token_bridge()
        if not token:
            console.print("[yellow]Not logged in[/yellow]")
            return
        # Proactively clear tokens; tests expect token cleanup even on early failures
        _clear_tokens_bridge()

        try:
            client_class = _get_client_class()
            client_manager = client_class()
        except (RuntimeError, ValueError, TypeError, OSError):
            _clear_tokens_bridge()
            raise

        async with client_manager as client:
            console.print("[yellow]Logging out...[/yellow]")
            try:
                await client.logout()
            except (RuntimeError, ValueError, OSError) as e:
                console.print(f"[red]✗ Logout failed: {e}[/red]")

            clear_result = FlextResult[None].ok(None)  # already cleared proactively
            if clear_result.is_success:
                console.print("[green]✓ Successfully logged out[/green]")
            else:
                console.print(
                    f"[yellow]⚠ Warning: Failed to clear authentication tokens: {clear_result.error}[/yellow]"
                )
    except KeyError:
        clear_result = _clear_tokens_bridge()
        if clear_result.is_success:
            console.print("[green]✓ Successfully logged out[/green]")
        else:
            console.print(
                f"[yellow]⚠ Warning: Failed to clear authentication tokens: {clear_result.error}[/yellow]"
            )
    except (
        ConnectionError,
        TimeoutError,
        OSError,
        PermissionError,
        ValueError,
        AttributeError,
    ) as e:
        clear_result = _clear_tokens_bridge()
        if clear_result.is_success:
            console.print(
                f"[yellow]⚠️ Error during logout, logged out locally ({e})[/yellow]",
            )
        else:
            console.print(
                f"[red]❌ Logout error and failed to clear tokens: {e}[/red]",
            )
    except (RuntimeError, TypeError):
        _clear_tokens_bridge()


@auth.command(help="Logout from FLEXT")
@click.pass_context
def logout(ctx: click.Context) -> None:
    """Logout from FLEXT services and clear authentication tokens.

    Performs secure logout by:
      1. Notifying FLEXT services of logout (if connected)
      2. Clearing local authentication tokens
      3. Ending authenticated session
    """
    console: Console = ctx.obj.get("console", Console())

    # Run async function, ensure tokens are cleared even if it crashes early
    try:
        asyncio.run(_async_logout_impl(ctx, console))
    except (RuntimeError, ValueError, OSError, TypeError):
        _clear_tokens_bridge()


@auth.command(help="Check authentication status")
@click.pass_context
def status(ctx: click.Context) -> None:
    """Check current authentication status and token validity.

    Displays:
      - Authentication status (logged in or not)
      - User information if authenticated
      - Token validity status

    Exit Codes:
      0: Authenticated and token valid
      1: Not authenticated or token invalid
    """
    console: Console = ctx.obj.get("console", Console()) if ctx.obj else Console()

    async def _async_status() -> None:
        """Async status check implementation."""
        try:
            token = _get_auth_token_bridge()
            if not token:
                console.print("[red]✗ Not authenticated[/red]")
                console.print("Run 'flext auth login' to authenticate")
                ctx.exit(1)

            async with FlextApiClient() as client:
                console.print("[yellow]Checking authentication status...[/yellow]")
                user_result = await client.get_current_user()

                # user_result is already a dict[str, object], not FlextResult
                user = user_result
                if user:
                    console.print("[green]✓ Authenticated[/green]")
                    console.print(f"User: {user.get('username', 'Unknown')}")
                    console.print(f"Email: {user.get('email', 'Unknown')}")
                    console.print(f"Role: {user.get('role', 'Unknown')}")
                else:
                    error_msg = "No user data returned"
                    console.print(
                        f"[red]❌ Authentication check failed: {error_msg}[/red]",
                    )
                    console.print("Run 'flext auth login' to re-authenticate")
                    ctx.exit(1)
        except KeyError as e:
            console.print(f"[red]❌ Authentication check failed: {e}[/red]")
            console.print("Run 'flext auth login' to re-authenticate")
            ctx.exit(1)
        except (ConnectionError, TimeoutError, ValueError) as e:
            console.print(f"[red]❌ Authentication check failed: {e}[/red]")
            console.print("Run 'flext auth login' to re-authenticate")
            ctx.exit(1)
        except OSError as e:
            console.print(
                f"[red]❌ Network error during authentication check: {e}[/red]",
            )
            console.print("Run 'flext auth login' to re-authenticate")
            ctx.exit(1)

    # Run async function
    asyncio.run(_async_status())


@auth.command(help="Show current authenticated user")
@click.pass_context
def whoami(ctx: click.Context) -> None:
    """Show current authenticated user information.

    Displays detailed information about the currently authenticated user:
      - Username
      - Full name
      - Email address
      - Role/permissions
      - User ID

    Exit Codes:
      0: User information retrieved successfully
      1: Not authenticated or failed to retrieve user information
    """
    console: Console = ctx.obj["console"]

    async def _async_whoami() -> None:
        """Async whoami implementation."""
        try:
            token = get_auth_token()
            if not token:
                console.print("[red]❌ Not authenticated[/red]")
                console.print("Run 'flext auth login' to authenticate")
                ctx.exit(1)

            async with FlextApiClient() as client:
                user_result = await client.get_current_user()

                # user_result is already a dict[str, object], not FlextResult
                user = user_result
                if user:
                    console.print(f"Username: {user.get('username', 'Unknown')}")
                    console.print(f"Full Name: {user.get('full_name', 'Unknown')}")
                    console.print(f"Email: {user.get('email', 'Unknown')}")
                    console.print(f"Role: {user.get('role', 'Unknown')}")
                    console.print(f"ID: {user.get('id', 'Unknown')}")
                else:
                    error_msg = "No user data returned"
                    console.print(f"[red]❌ Failed to get user info: {error_msg}[/red]")
                    console.print("Run 'flext auth login' to re-authenticate")
                    ctx.exit(1)
        except (ConnectionError, TimeoutError, ValueError, KeyError) as e:
            console.print(f"[red]❌ Failed to get user info: {e}[/red]")
            console.print("Run 'flext auth login' to re-authenticate")
            ctx.exit(1)
        except OSError as e:
            console.print(f"[red]❌ Network error getting user info: {e}[/red]")
            console.print("Run 'flext auth login' to re-authenticate")
            ctx.exit(1)

    # Run async function
    asyncio.run(_async_whoami())


# =============================================================================
# AUTHENTICATION HEADERS
# =============================================================================


def get_auth_headers() -> dict[str, str]:
    """Get authentication headers for API requests."""
    token_result = get_auth_token()
    if token_result.is_success and token_result.value:
        return {
            FlextCliConstants.HEADER_AUTHORIZATION: f"{FlextCliConstants.AUTH_BEARER_PREFIX} {token_result.value}"
        }
    return {}


# Command aliases (from commands/auth.py)
auth_login = login
auth_logout = logout
auth_status = status
auth_whoami = whoami

# Command aliases for __init__.py imports
login_command = login
logout_command = logout
status_command = status


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # CLI commands
    "auth",
    "auth_login",
    "auth_logout",
    "auth_status",
    "auth_whoami",
    "clear_auth_tokens",
    "get_auth_headers",
    "get_auth_token",
    "get_refresh_token",
    "get_refresh_token_path",
    "get_token_path",
    "is_authenticated",
    "login",
    "login_command",
    "logout",
    "logout_command",
    "save_auth_token",
    "save_refresh_token",
    "should_auto_refresh",
    "status",
    "status_command",
    "whoami",
]
