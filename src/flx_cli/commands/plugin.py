"""Plugin management commands for FLX CLI."""

from __future__ import annotations

import asyncio
import json
from typing import TYPE_CHECKING

import click
from rich.progress import Progress, SpinnerColumn, TextColumn

from flx_cli.client import FlxApiClient
from flx_cli.utils.output import format_plugin_list

if TYPE_CHECKING:
    from rich.console import Console


@click.group()
def plugin() -> None:
    """Plugin management commands."""


@plugin.command(name="list")
@click.option(
    "--type", "plugin_type", help="Filter by plugin type (tap/target/transform)"
)
@click.option("--installed", is_flag=True, help="Show only installed plugins")
@click.pass_context
def list_plugins(ctx: click.Context, plugin_type: str | None, installed: bool) -> None:
    """List available plugins."""
    console: Console = ctx.obj["console"]
    output_format = ctx.obj["output"]

    async def _list() -> None:
        try:
            async with FlxApiClient() as client:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console,
                    transient=True,
                ) as progress:
                    progress.add_task("Loading plugins...")
                    plugins = await client.list_plugins(plugin_type, installed)

                if output_format == "json":
                    console.print(json.dumps(plugins, indent=2))
                else:
                    format_plugin_list(console, plugins, output_format)

        except Exception as e:
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
            async with FlxApiClient() as client:
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
                        for key, value in plugin["settings"].items():
                            console.print(f"  {key}: {value}")

        except Exception as e:
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
            async with FlxApiClient() as client:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console,
                    transient=True,
                ) as progress:
                    progress.add_task(f"Installing {plugin_id}...")
                    result = await client.install_plugin(plugin_id, version)

                console.print(
                    f"[green]✅ Plugin '{plugin_id}' installed successfully![/green]"
                )

                if "version" in result:
                    console.print(f"Version: {result['version']}")

        except Exception as e:
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
            async with FlxApiClient() as client:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console,
                    transient=True,
                ) as progress:
                    progress.add_task(f"Updating {plugin_id}...")
                    result = await client.update_plugin(plugin_id, version)

                console.print(
                    f"[green]✅ Plugin '{plugin_id}' updated successfully![/green]"
                )

                if "old_version" in result and "new_version" in result:
                    console.print(
                        f"Updated from {result['old_version']} to {result['new_version']}"
                    )

        except Exception as e:
            console.print(f"[red]❌ Failed to update plugin: {e}[/red]")
            ctx.exit(1)

    asyncio.run(_update())


@plugin.command()
@click.argument("plugin_id")
@click.option("--force", is_flag=True, help="Force removal without confirmation")
@click.pass_context
def remove(ctx: click.Context, plugin_id: str, force: bool) -> None:
    """Remove a plugin."""
    console: Console = ctx.obj["console"]

    async def _remove() -> None:
        try:
            async with FlxApiClient() as client:
                # Get plugin details first
                plugin = await client.get_plugin(plugin_id)

                if not force:
                    confirm = click.confirm(
                        f"Are you sure you want to remove plugin '{plugin['name']}'?"
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
                    f"[green]✅ Plugin '{plugin['name']}' removed successfully[/green]"
                )

        except Exception as e:
            console.print(f"[red]❌ Failed to remove plugin: {e}[/red]")
            ctx.exit(1)

    asyncio.run(_remove())


@plugin.command()
@click.argument("query")
@click.pass_context
def search(ctx: click.Context, query: str) -> None:
    """Search for plugins in the registry."""
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
    ctx: click.Context, name: str, plugin_type: str, template: str | None
) -> None:
    """Create a new plugin from template."""
    console: Console = ctx.obj["console"]

    console.print("[yellow]Plugin creation not yet implemented[/yellow]")
    console.print(f"Would create {plugin_type} plugin: {name}")
    if template:
        console.print(f"Using template: {template}")


@plugin.command()
@click.option("--watch", is_flag=True, help="Watch for changes and hot reload")
@click.pass_context
def test(ctx: click.Context, watch: bool) -> None:
    """Test plugin in development mode."""
    console: Console = ctx.obj["console"]

    console.print("[yellow]Plugin testing not yet implemented[/yellow]")
    if watch:
        console.print("Would enable hot reload...")
