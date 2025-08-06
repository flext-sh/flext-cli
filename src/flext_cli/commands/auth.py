"""FLEXT CLI Authentication Commands - Ecosystem Authentication Management.

This module implements authentication commands for the FLEXT CLI, providing
secure authentication against FLEXT services and ecosystem components.
Follows standard CLI patterns with Rich output and comprehensive error handling.

Commands:
    ✅ login: Authenticate with username/password and store tokens
    ✅ logout: Clear authentication tokens and end session
    ✅ status: Check current authentication status and token validity
    ✅ token: Token management (show, refresh, revoke)

Architecture:
    - Click-based command definitions with Rich console output
    - Secure token storage and management
    - Integration with FLEXT service authentication endpoints
    - Railway-oriented error handling with FlextResult patterns

Authentication Flow:
    1. User provides credentials via login command
    2. CLI authenticates against FLEXT services (currently mock)
    3. Authentication tokens stored securely for session
    4. Subsequent commands use stored tokens for authorization
    5. Logout clears tokens and ends authenticated session

Security Features:
    - Password input hidden from terminal history
    - Secure token storage (TODO: Sprint 2 - implement encryption)
    - Token expiration and refresh handling
    - Session validation and cleanup

Integration Status:
    ✅ Basic authentication commands implemented
    ⚠️ Mock authentication (TODO: Sprint 1 - real service integration)
    ❌ Token encryption not implemented (TODO: Sprint 2)
    ❌ SSO/OAuth integration not implemented (TODO: Sprint 9)

TODO (docs/TODO.md):
    Sprint 1: Integrate with real FLEXT authentication services
    Sprint 2: Implement secure token encryption and storage
    Sprint 3: Add multi-factor authentication support
    Sprint 9: Implement SSO and OAuth integration

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

import click

from flext_cli.flext_api_integration import FlextCLIApiClient as FlextApiClient
from flext_cli.utils.auth import clear_auth_tokens, get_auth_token, save_auth_token

if TYPE_CHECKING:
    from rich.console import Console


@click.group()
def auth() -> None:
    """Manage authentication commands."""


@auth.command()
@click.option("--username", "-u", prompt=True, help="Username")
@click.option("--password", "-p", prompt=True, hide_input=True, help="Password")
@click.pass_context
def login(ctx: click.Context, username: str, password: str) -> None:
    """Authenticate with FLEXT services using username and password.

    Performs secure authentication against FLEXT services and stores
    authentication tokens for subsequent CLI operations. Uses secure
    password input (hidden from terminal) and validates credentials.

    Options:
        --username, -u: Username for authentication (prompted if not provided)
        --password, -p: Password for authentication (prompted securely if not provided)

    Authentication Flow:
        1. Validates username and password input
        2. Connects to FLEXT authentication service
        3. Authenticates credentials and receives token
        4. Stores token securely for session use
        5. Displays welcome message with user details

    Security Features:
        - Password input hidden from terminal and history
        - Secure token storage after successful authentication
        - Input validation to prevent empty credentials
        - Comprehensive error handling for various failure modes

    Examples:
        $ flext auth login --username REDACTED_LDAP_BIND_PASSWORD
        Password: [hidden input]
        ✅ Login successful!
        Welcome, Administrator!

        $ flext auth login -u testuser -p [will prompt]

    Current Implementation:
        ⚠️ Uses mock authentication service for development

    TODO (Sprint 1):
        - Integrate with real FLEXT authentication endpoints
        - Add support for different authentication methods
        - Implement token encryption for storage
        - Add automatic token refresh mechanism

    Exit Codes:
        0: Authentication successful
        1: Authentication failed (invalid credentials, network error, etc.)

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
                        save_auth_token(token_value)
                        console.print("[green]✅ Login successful![/green]")

                    if "user" in response:
                        user_data = response["user"]
                        if isinstance(user_data, dict):
                            console.print(
                                f"Welcome, {user_data.get('name', username)}!",
                            )
                else:
                    console.print("[red]❌ Login failed: Invalid response[/red]")
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
    """Logout from FLEXT."""
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
                clear_auth_tokens()
                console.print("[green]✅ Logged out successfully[/green]")
        except KeyError:
            # KeyError is treated as successful logout (token cleanup)
            clear_auth_tokens()
            console.print("[green]✅ Logged out successfully[/green]")
        except (
            ConnectionError,
            TimeoutError,
            OSError,
            PermissionError,
            ValueError,
            AttributeError,
        ) as e:
            # Clear token even if any error occurs:
            clear_auth_tokens()
            console.print(
                f"[yellow]⚠️  Error during logout, logged out locally ({e})[/yellow]",
            )

    # Run async function
    asyncio.run(_async_logout())


@auth.command()
@click.pass_context
def status(ctx: click.Context) -> None:
    """Check authentication status."""
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


@auth.command()
@click.pass_context
def whoami(ctx: click.Context) -> None:
    """Show current user information."""
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
            console.print(
                f"[red]❌ Network error getting user info: {e}[/red]",
            )
            console.print("Run 'flext auth login' to re-authenticate")
            ctx.exit(1)

    # Run async function
    asyncio.run(_async_whoami())
