"""Authentication commands for FLEXT CLI.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

import click

from flext_cli.client import FlextApiClient
from flext_cli.utils.auth import clear_auth_tokens
from flext_cli.utils.auth import get_auth_token
from flext_cli.utils.auth import save_auth_token

if TYPE_CHECKING:
    from rich.console import Console


@click.group()
def auth() -> None:
    """Authentication commands."""


@auth.command()
@click.option("--username", "-u", prompt=True, help="Username")
@click.option("--password", "-p", prompt=True, hide_input=True, help="Password")
@click.pass_context
def login(ctx: click.Context, username: str, password: str) -> None:
    """Login to FLEXT with username and password."""
    console: Console = ctx.obj["console"]

    async def _login() -> None:
        try:
            async with FlextApiClient() as client:
                console.print(f"[yellow]Logging in as {username}...[/yellow]")
                response = await client.login(username, password)

                if "token" in response:
                    save_auth_token(response["token"])
                    console.print("[green]✅ Login successful![/green]")

                    if "user" in response:
                        user = response["user"]
                        console.print(f"Welcome, {user.get('name', username)}!")
                else:
                    console.print("[red]❌ Login failed: Invalid response[/red]")

        except Exception as e:
            console.print(f"[red]❌ Login failed: {e}[/red]")
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

            async with FlextApiClient() as client:
                console.print("[yellow]Logging out...[/yellow]")
                await client.logout()
                clear_auth_tokens()
                console.print("[green]✅ Logged out successfully[/green]")

        except Exception as e:
            # Clear token even if API call fails:
            clear_auth_tokens()
            console.print(f"[yellow]⚠️  Logged out locally ({e})[/yellow]")

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

            async with FlextApiClient() as client:
                console.print("[yellow]Checking authentication...[/yellow]")
                user = await client.get_current_user()

                console.print("[green]✅ Authenticated[/green]")
                console.print(f"User: {user.get('username', 'Unknown')}")
                console.print(f"Email: {user.get('email', 'Unknown')}")
                console.print(f"Role: {user.get('role', 'Unknown')}")

        except Exception as e:
            console.print(f"[red]❌ Authentication check failed: {e}[/red]")
            console.print("Run 'flext auth login' to re-authenticate")
            ctx.exit(1)

    asyncio.run(_status())
