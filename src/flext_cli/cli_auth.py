"""FLEXT CLI Authentication - Complete authentication system consolidating utilities and commands.

This module consolidates all CLI authentication functionality from multiple scattered files
into a single, well-organized module following PEP8 naming conventions.

Consolidated from:
    - utils/auth.py (authentication utilities)
    - commands/auth.py (authentication CLI commands)
    - Various authentication definitions across modules

Design Principles:
    - PEP8 naming: cli_auth.py (not auth.py for clarity)
    - Single source of truth for all CLI authentication
    - Secure token management with restricted permissions
    - Rich terminal UI with comprehensive error handling
    - Type safety with comprehensive annotations

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

import click
from flext_core import FlextResult

from flext_cli.cli_config import CLIConfig
from flext_cli.flext_api_integration import FlextCLIApiClient as FlextApiClient

if TYPE_CHECKING:
    from pathlib import Path

    from rich.console import Console


# =============================================================================
# AUTHENTICATION UTILITIES - Token management and security operations
# =============================================================================


def get_cli_config() -> CLIConfig:
    """Get CLI configuration instance."""
    return CLIConfig()


def get_token_path() -> Path:
    """Get the path to the auth token file.
    
    Returns:
        The path to the auth token file.

    """
    config = get_cli_config()
    return config.data_dir / "auth_token"


def get_refresh_token_path() -> Path:
    """Get the path to the refresh token file.
    
    Returns:
        The path to the refresh token file.

    """
    config = get_cli_config()
    return config.data_dir / "refresh_token"


def save_auth_token(token: str) -> FlextResult[None]:
    """Save the auth token to the file with secure permissions.
    
    Args:
        token: The auth token to save
        
    Returns:
        Result of the operation

    """
    try:
        token_path = get_token_path()
        token_path.parent.mkdir(parents=True, exist_ok=True)

        # Save token with restricted permissions
        token_path.write_text(token, encoding="utf-8")
        token_path.chmod(0o600)  # Read/write for owner only

        return FlextResult.ok(None)
    except (OSError, PermissionError, ValueError) as e:
        return FlextResult.fail(f"Failed to save auth token: {e}")


def save_refresh_token(refresh_token: str) -> FlextResult[None]:
    """Save the refresh token to the file with secure permissions.
    
    Args:
        refresh_token: The refresh token to save
        
    Returns:
        Result of the operation

    """
    try:
        refresh_token_path = get_refresh_token_path()
        refresh_token_path.parent.mkdir(parents=True, exist_ok=True)

        # Save token with restricted permissions
        refresh_token_path.write_text(refresh_token, encoding="utf-8")
        refresh_token_path.chmod(0o600)  # Read/write for owner only

        return FlextResult.ok(None)
    except (OSError, PermissionError, ValueError) as e:
        return FlextResult.fail(f"Failed to save refresh token: {e}")


def get_auth_token() -> str | None:
    """Get the auth token from the file.
    
    Returns:
        The auth token or None if not found

    """
    token_path = get_token_path()

    if token_path.exists():
        try:
            return token_path.read_text(encoding="utf-8").strip()
        except (OSError, UnicodeDecodeError):
            return None

    return None


def get_refresh_token() -> str | None:
    """Get the refresh token from the file.
    
    Returns:
        The refresh token or None if not found

    """
    refresh_token_path = get_refresh_token_path()

    if refresh_token_path.exists():
        try:
            return refresh_token_path.read_text(encoding="utf-8").strip()
        except (OSError, UnicodeDecodeError):
            return None

    return None


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

        return FlextResult.ok(None)
    except (OSError, PermissionError) as e:
        return FlextResult.fail(f"Failed to clear auth tokens: {e}")


def is_authenticated() -> bool:
    """Check if the user is authenticated.
    
    Returns:
        True if the user is authenticated, False otherwise

    """
    return get_auth_token() is not None


def should_auto_refresh() -> bool:
    """Check if the user should auto refresh the auth tokens.
    
    Returns:
        True if the user should auto refresh the auth tokens, False otherwise

    """
    config = get_cli_config()
    return hasattr(config, "auto_refresh") and getattr(config, "auto_refresh", False) and get_refresh_token() is not None


# =============================================================================
# AUTHENTICATION CLI COMMANDS - Interactive authentication management
# =============================================================================


@click.group()
def auth() -> None:
    """Manage authentication commands."""


@auth.command()
@click.option("--username", "-u", prompt=True, help="Username for authentication")
@click.option("--password", "-p", prompt=True, hide_input=True, help="Password for authentication")
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
    console: Console = ctx.obj["console"]

    async def _async_login() -> None:
        """Async login implementation."""
        try:
            async with FlextApiClient() as client:
                console.print(f"[yellow]Logging in as {username}...[/yellow]")

                # Validate password before authentication
                if not password or len(password) < 1:
                    console.print("[red]❌ Password cannot be empty[/red]")
                    ctx.exit(1)

                # Real authentication via API client
                login_result = await client.login(username, password)

                if login_result.is_failure:
                    console.print(f"[red]❌ Login failed: {login_result.error}[/red]")
                    ctx.exit(1)

                response = login_result.data
                if response and "token" in response:
                    token_value = response["token"]
                    if isinstance(token_value, str):
                        save_result = save_auth_token(token_value)
                        if save_result.is_success:
                            console.print("[green]✅ Login successful![/green]")
                        else:
                            console.print(f"[red]❌ Failed to save token: {save_result.error}[/red]")
                            ctx.exit(1)

                    if "user" in response:
                        user_data = response["user"]
                        if isinstance(user_data, dict):
                            console.print(f"Welcome, {user_data.get('name', username)}!")
                else:
                    console.print("[red]❌ Login failed: Invalid response[/red]")
                    ctx.exit(1)
        except (ConnectionError, TimeoutError, ValueError, KeyError) as e:
            console.print(f"[red]❌ Login failed: {e}[/red]")
            ctx.exit(1)
        except OSError as e:
            console.print(f"[red]❌ Network error during login: {e}[/red]")
            ctx.exit(1)

    # Run async function
    asyncio.run(_async_login())


@auth.command()
@click.pass_context
def logout(ctx: click.Context) -> None:
    """Logout from FLEXT services and clear authentication tokens.
    
    Performs secure logout by:
        1. Notifying FLEXT services of logout (if connected)
        2. Clearing local authentication tokens
        3. Ending authenticated session
    """
    console: Console = ctx.obj["console"]

    async def _async_logout() -> None:
        """Async logout implementation."""
        try:
            token = get_auth_token()
            if not token:
                console.print("[yellow]Not logged in[/yellow]")
                return

            async with FlextApiClient() as client:
                console.print("[yellow]Logging out...[/yellow]")
                logout_result = await client.logout()

                if logout_result.is_failure:
                    console.print(f"[red]❌ Logout failed: {logout_result.error}[/red]")
                    # Continue with token cleanup anyway

                clear_result = clear_auth_tokens()
                if clear_result.is_success:
                    console.print("[green]✅ Logged out successfully[/green]")
                else:
                    console.print(f"[yellow]⚠️ Logged out, but failed to clear tokens: {clear_result.error}[/yellow]")
        except KeyError:
            # KeyError is treated as successful logout (token cleanup)
            clear_result = clear_auth_tokens()
            if clear_result.is_success:
                console.print("[green]✅ Logged out successfully[/green]")
            else:
                console.print(f"[yellow]⚠️ Logged out, but failed to clear tokens: {clear_result.error}[/yellow]")
        except (ConnectionError, TimeoutError, OSError, PermissionError, ValueError, AttributeError) as e:
            # Clear token even if any error occurs
            clear_result = clear_auth_tokens()
            if clear_result.is_success:
                console.print(f"[yellow]⚠️ Error during logout, logged out locally ({e})[/yellow]")
            else:
                console.print(f"[red]❌ Logout error and failed to clear tokens: {e}[/red]")

    # Run async function
    asyncio.run(_async_logout())


@auth.command()
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
    console: Console = ctx.obj["console"]

    async def _async_status() -> None:
        """Async status check implementation."""
        try:
            token = get_auth_token()
            if not token:
                console.print("[red]❌ Not authenticated[/red]")
                console.print("Run 'flext auth login' to authenticate")
                ctx.exit(1)

            async with FlextApiClient() as client:
                console.print("[yellow]Checking authentication...[/yellow]")
                user_result = await client.get_current_user()

                if user_result.success and user_result.data:
                    user = user_result.data
                    console.print("[green]✅ Authenticated[/green]")
                    console.print(f"User: {user.get('username', 'Unknown')}")
                    console.print(f"Email: {user.get('email', 'Unknown')}")
                    console.print(f"Role: {user.get('role', 'Unknown')}")
                else:
                    error_msg = user_result.error or "Unknown error"
                    console.print(f"[red]❌ Authentication check failed: {error_msg}[/red]")
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
            console.print(f"[red]❌ Network error during authentication check: {e}[/red]")
            console.print("Run 'flext auth login' to re-authenticate")
            ctx.exit(1)

    # Run async function
    asyncio.run(_async_status())


@auth.command()
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

                if user_result.success and user_result.data:
                    user = user_result.data
                    console.print(f"Username: {user.get('username', 'Unknown')}")
                    console.print(f"Full Name: {user.get('full_name', 'Unknown')}")
                    console.print(f"Email: {user.get('email', 'Unknown')}")
                    console.print(f"Role: {user.get('role', 'Unknown')}")
                    console.print(f"ID: {user.get('id', 'Unknown')}")
                else:
                    error_msg = user_result.error or "Unknown error"
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
# LEGACY COMPATIBILITY - Backward compatibility aliases
# =============================================================================

# Legacy aliases for utilities (from utils/auth.py)
get_token_file_path = get_token_path
get_refresh_token_file_path = get_refresh_token_path
clear_tokens = clear_auth_tokens
is_user_authenticated = is_authenticated

# Legacy aliases for commands (from commands/auth.py)
auth_login = login
auth_logout = logout
auth_status = status
auth_whoami = whoami


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Authentication utilities
    "get_token_path",
    "get_refresh_token_path",
    "save_auth_token",
    "save_refresh_token",
    "get_auth_token",
    "get_refresh_token",
    "clear_auth_tokens",
    "is_authenticated",
    "should_auto_refresh",
    # CLI commands
    "auth",
    "login",
    "logout",
    "status",
    "whoami",
    # Legacy aliases
    "get_token_file_path",
    "get_refresh_token_file_path",
    "clear_tokens",
    "is_user_authenticated",
    "auth_login",
    "auth_logout",
    "auth_status",
    "auth_whoami",
]
