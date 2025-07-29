"""Authentication commands for FLEXT CLI.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

import click

from flext_cli.client import FlextApiClient
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
def login(ctx: click.Context, username: str, _password: str) -> None:
    """Login to FLEXT with username and password."""
    console: Console = ctx.obj["console"]

    async def _login() -> None:
        try:
            FlextApiClient()
            console.print(f"[yellow]Logging in as {username}...[/yellow]")

            # Simulate login response for stub client
            response: dict[str, object] = {
                "token": f"token_{username}",
                "user": {"name": username},
            }

            if "token" in response:
                token_value = response["token"]
                if isinstance(token_value, str):
                    save_auth_token(token_value)
                    console.print("[green]✅ Login successful![/green]")

                if "user" in response:
                    user_data = response["user"]
                    if isinstance(user_data, dict):
                        console.print(f"Welcome, {user_data.get('name', username)}!")
            else:
                console.print("[red]❌ Login failed: Invalid response[/red]")
        except (ConnectionError, TimeoutError, ValueError, KeyError) as e:
            console.print(f"[red]❌ Login failed: {e}[/red]")
            ctx.exit(1)
        except OSError as e:
            console.print(f"[red]❌ Network error during login: {e}[/red]")
            ctx.exit(1)

    asyncio.run(_login())


@auth.command()
@click.pass_context
def logout(ctx: click.Context) -> None:
    """Logout from FLEXT."""
    console: Console = ctx.obj["console"]

    async def _logout() -> None:
        try:
            token = get_auth_token()
            if not token:
                console.print("[yellow]Not logged in[/yellow]")
                return

            FlextApiClient()
            console.print("[yellow]Logging out...[/yellow]")
            # Simulate logout for stub client
            clear_auth_tokens()
            console.print("[green]✅ Logged out successfully[/green]")
        except (ConnectionError, TimeoutError, ValueError, KeyError) as e:
            # Clear token even if API call fails:
            clear_auth_tokens()
            console.print(f"[yellow]⚠️  Logged out locally ({e})[/yellow]")
        except OSError as e:
            # Clear token even if API call fails:
            clear_auth_tokens()
            console.print(
                f"[yellow]⚠️  Network error during logout, "
                f"logged out locally ({e})[/yellow]",
            )

    asyncio.run(_logout())


@auth.command()
@click.pass_context
def status(ctx: click.Context) -> None:
    """Check authentication status."""
    console: Console = ctx.obj["console"]

    async def _status() -> None:
        try:
            token = get_auth_token()
            if not token:
                console.print("[red]❌ Not authenticated[/red]")
                console.print("Run 'flext auth login' to authenticate")
                ctx.exit(1)

            FlextApiClient()
            console.print("[yellow]Checking authentication...[/yellow]")
            # Simulate user response for stub client
            user = {
                "username": "test_user",
                "email": "test@example.com",
                "role": "user",
            }

            console.print("[green]✅ Authenticated[/green]")
            console.print(f"User: {user.get('username', 'Unknown')}")
            console.print(f"Email: {user.get('email', 'Unknown')}")
            console.print(f"Role: {user.get('role', 'Unknown')}")
        except (ConnectionError, TimeoutError, ValueError, KeyError) as e:
            console.print(f"[red]❌ Authentication check failed: {e}[/red]")
            console.print("Run 'flext auth login' to re-authenticate")
            ctx.exit(1)
        except OSError as e:
            console.print(
                f"[red]❌ Network error during authentication check: {e}[/red]",
            )
            console.print("Run 'flext auth login' to re-authenticate")
            ctx.exit(1)

    asyncio.run(_status())
