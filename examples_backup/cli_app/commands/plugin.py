"""Plugin Management Commands - Extensible Plugin System for FLEXT CLI.

This module implements plugin management commands for FLEXT CLI, providing
comprehensive plugin discovery, installation, configuration, and lifecycle
management.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import asyncio
import json

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from flext_cli import FlextApiClient, format_plugin_list


@click.group()
def plugin() -> None:
    """Plugin management commands."""


@plugin.command(name="list")
@click.option(
    "--type",
    "plugin_type",
    help="Filter by plugin type (tap/target/transform)",
)
@click.option("--installed", is_flag=True, help="Show only installed plugins")
@click.pass_context
def list_plugins(ctx: click.Context, plugin_type: str | None, **kwargs: bool) -> None:
    """List available plugins."""
    console: Console = ctx.obj["console"]
    output_format = ctx.obj["output"]
    installed = kwargs.get("installed", False)

    async def _list() -> None:
        try:
            async with FlextApiClient() as client:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console,
                    transient=True,
                ) as progress:
                    progress.add_task("Loading plugins...")
                    plugins = await client.list_plugins(
                        plugin_type,
                        installed_only=installed,
                    )

                if output_format == "json":
                    console.print(json.dumps(plugins, indent=2))
                else:
                    format_plugin_list(console, plugins, output_format)
        except (RuntimeError, ValueError, TypeError) as e:
            console.print(f"[red]❌ Failed to list plugins: {e}[/red]")
            ctx.exit(1)

    asyncio.run(_list())


@plugin.command()
@click.argument("plugin_id")
@click.pass_context
def show(ctx: click.Context, plugin_id: str) -> None:
    """Show plugin details."""
    console: Console = ctx.obj["console"]
    output_format = ctx.obj["output"]

    async def _show() -> None:
        try:
            async with FlextApiClient() as client:
                plugin = await client.get_plugin(plugin_id)

                if output_format == "json":
                    console.print(json.dumps(plugin, indent=2))
                else:
                    # Display plugin details
                    console.print(f"\n[bold cyan]{plugin['name']}[/bold cyan]")
                    console.print(f"ID: {plugin['id']}")
                    console.print(f"Type: {plugin['type']}")
                    console.print(f"Version: {plugin.get('version', 'Unknown')}")
                    console.print(f"Status: {plugin.get('status', 'Unknown')}")

                    if "description" in plugin:
                        console.print(f"\nDescription:\n{plugin['description']}")

                    if "settings" in plugin:
                        console.print("\nSettings:")
                        settings = plugin["settings"]
                        if isinstance(settings, dict):
                            for key, value in settings.items():
                                console.print(f"  {key}: {value}")
                        else:
                            console.print(f"  {settings}")
        except (RuntimeError, ValueError, TypeError) as e:
            console.print(f"[red]❌ Failed to get plugin details: {e}[/red]")
            ctx.exit(1)

    asyncio.run(_show())


@plugin.command()
@click.argument("plugin_id")
@click.option("--version", help="Specific version to install")
@click.pass_context
def install(ctx: click.Context, plugin_id: str, version: str | None) -> None:
    """Install a plugin."""
    console: Console = ctx.obj["console"]

    async def _install() -> None:
        try:
            async with FlextApiClient() as client:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console,
                    transient=True,
                ) as progress:
                    progress.add_task(f"Installing {plugin_id}...")
                    result = await client.install_plugin(plugin_id, version)

                console.print(
                    f"[green]✅ Plugin '{plugin_id}' installed successfully![/green]",
                )

                if "version" in result:
                    console.print(f"Version: {result['version']}")
        except (RuntimeError, ValueError, TypeError) as e:
            console.print(f"[red]❌ Failed to install plugin: {e}[/red]")
            ctx.exit(1)

    asyncio.run(_install())


@plugin.command()
@click.argument("plugin_id")
@click.option("--version", help="Specific version to update to")
@click.pass_context
def update(ctx: click.Context, plugin_id: str, version: str | None) -> None:
    """Update a plugin."""
    console: Console = ctx.obj["console"]

    async def _update() -> None:
        try:
            async with FlextApiClient() as client:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console,
                    transient=True,
                ) as progress:
                    progress.add_task(f"Updating {plugin_id}...")
                    result = await client.update_plugin(plugin_id, version)

                console.print(
                    f"[green]✅ Plugin '{plugin_id}' updated successfully![/green]",
                )

                if "old_version" in result and "new_version" in result:
                    old_ver = result["old_version"]
                    new_ver = result["new_version"]
                    version_msg: str = f"Updated from {old_ver} to {new_ver}"
                    console.print(version_msg)
        except (RuntimeError, ValueError, TypeError) as e:
            console.print(f"[red]❌ Failed to update plugin: {e}[/red]")
            ctx.exit(1)

    asyncio.run(_update())


@plugin.command()
@click.argument("plugin_id")
@click.option("--force", is_flag=True, help="Force removal without confirmation")
@click.pass_context
def remove(ctx: click.Context, plugin_id: str, **kwargs: bool) -> None:
    """Remove a plugin."""
    console: Console = ctx.obj["console"]
    force = kwargs.get("force", False)

    async def _remove() -> None:
        try:
            async with FlextApiClient() as client:
                # Get plugin details first
                plugin = await client.get_plugin(plugin_id)

                if not force:
                    confirm = click.confirm(
                        f"Are you sure you want to remove plugin '{plugin['name']}'?",
                    )
                    if not confirm:
                        console.print("[yellow]Removal cancelled[/yellow]")
                        return

                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console,
                    transient=True,
                ) as progress:
                    progress.add_task(f"Removing {plugin_id}...")
                    await client.uninstall_plugin(plugin_id)

                console.print(
                    f"[green]✅ Plugin '{plugin['name']}' removed successfully[/green]",
                )
        except (RuntimeError, ValueError, TypeError) as e:
            console.print(f"[red]❌ Failed to remove plugin: {e}[/red]")
            ctx.exit(1)

    asyncio.run(_remove())


@plugin.command()
@click.argument("query")
@click.pass_context
def search(ctx: click.Context, query: str) -> None:
    """Search for plugins."""
    console: Console = ctx.obj["console"]

    console.print("[yellow]Plugin search not yet implemented[/yellow]")
    console.print(f"Would search for: {query}")


@plugin.command()
@click.option("--name", prompt=True, help="Plugin name")
@click.option(
    "--type",
    "plugin_type",
    prompt=True,
    type=click.Choice(["tap", "target", "transform"]),
    help="Plugin type",
)
@click.option("--template", help="Template to use")
@click.pass_context
def create(
    ctx: click.Context,
    name: str,
    plugin_type: str,
    template: str | None,
) -> None:
    """Create a new plugin."""
    console: Console = ctx.obj["console"]

    console.print("[yellow]Plugin creation not yet implemented[/yellow]")
    console.print(f"Would create {plugin_type} plugin: {name}")
    if template:
        console.print(f"Using template: {template}")


@plugin.command()
@click.option("--watch", is_flag=True, help="Watch for changes and hot reload")
@click.pass_context
def test(ctx: click.Context, **kwargs: bool) -> None:
    """Test plugins."""
    console: Console = ctx.obj["console"]
    watch = kwargs.get("watch", False)

    console.print("[yellow]Plugin testing not yet implemented[/yellow]")
    if watch:
        console.print("[blue]Watch mode would be enabled[/blue]")
    if watch:
        console.print("Would enable hot reload...")
