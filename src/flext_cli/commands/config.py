"""Configuration management commands for FLEXT CLI."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import click
import yaml
from rich.table import Table

from flext_cli.utils.config import (
    get_config,
    get_config_path,
    get_config_value,
    list_config_values,
    set_config_value,
)

if TYPE_CHECKING:
    from rich.console import Console


@click.group()
def config() -> None:
    """Manage CLI configuration settings."""


@config.command()
@click.argument("key", required=False)
@click.pass_context
def get(ctx: click.Context, key: str | None) -> None:
    """Get configuration value(s)."""
    console: Console = ctx.obj["console"]
    output_format = ctx.obj["output"]

    if key:
        # Get specific value
        value = get_config_value(key)
        if value is None:
            console.print(f"[yellow]Configuration key '{key}' not found[/yellow]")
            ctx.exit(1)

        if output_format == "json":
            console.print(json.dumps({key: value}, indent=2))
        elif output_format == "yaml":
            console.print(yaml.dump({key: value}, default_flow_style=False))
        else:
            console.print(f"{key}: {value}")
    else:
        # Get all values
        config_data = list_config_values()

        if output_format == "json":
            console.print(json.dumps(config_data, indent=2))
        elif output_format == "yaml":
            console.print(yaml.dump(config_data, default_flow_style=False))
        else:
            # Table format
            table = Table(title="FLEXT Configuration")
            table.add_column("Key", style="cyan")
            table.add_column("Value", style="white")

            for k, v in config_data.items():
                table.add_row(k, str(v))

            console.print(table)


@config.command()
@click.argument("key")
@click.argument("value")
@click.pass_context
def set(ctx: click.Context, key: str, value: str) -> None:
    """Set configuration value."""
    console: Console = ctx.obj["console"]

    try:
        # Try to parse value as JSON first
        try:
            parsed_value = json.loads(value)
        except json.JSONDecodeError:
            # If not JSON, treat as string
            parsed_value = value

        set_config_value(key, parsed_value)
        console.print(f"[green]✅ Set {key} = {parsed_value}[/green]")

    except Exception as e:
        console.print(f"[red]❌ Failed to set configuration: {e}[/red]")
        ctx.exit(1)


@config.command()
@click.pass_context
def validate(ctx: click.Context) -> None:
    """Validate configuration."""
    console: Console = ctx.obj["console"]

    try:
        config_data = get_config()

        # Check required fields
        required_fields = ["api_url"]

        missing_fields = [field for field in required_fields if field not in config_data or not config_data[field]]

        if missing_fields:
            console.print("[red]❌ Configuration validation failed[/red]")
            console.print(f"Missing required fields: {', '.join(missing_fields)}")
            ctx.exit(1)
        else:
            console.print("[green]✅ Configuration is valid[/green]")

            # Show configuration location
            config_path = get_config_path()
            console.print(f"Configuration file: {config_path}")

    except Exception as e:
        console.print(f"[red]❌ Configuration validation error: {e}[/red]")
        ctx.exit(1)


@config.command()
@click.pass_context
def path(ctx: click.Context) -> None:
    """Show configuration file path."""
    console: Console = ctx.obj["console"]

    config_path = get_config_path()
    console.print(f"Configuration file: {config_path}")

    if config_path.exists():
        console.print(f"File size: {config_path.stat().st_size} bytes")
        console.print(f"Last modified: {config_path.stat().st_mtime}")
    else:
        console.print("[yellow]Configuration file does not exist yet[/yellow]")


@config.command()
@click.option("--profile", "-p", help="Profile name to edit")
@click.pass_context
def edit(ctx: click.Context, profile: str | None) -> None:  # noqa: ARG001
    """Edit configuration file in editor."""
    console: Console = ctx.obj["console"]

    import os
    import subprocess

    config_path = get_config_path()
    editor = os.environ.get("EDITOR", "vim")

    try:
        if not config_path.exists():
            # Create default config
            default_config = {
                "default": {
                    "api_url": "http://localhost:8000",
                    "output_format": "table",
                },
                "profiles": {},
                "current_profile": "default",
            }
            config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(config_path, "w") as f:
                yaml.dump(default_config, f, default_flow_style=False)

        subprocess.run([editor, str(config_path)], check=True)  # noqa: S603
        console.print("[green]✅ Configuration updated[/green]")

    except subprocess.CalledProcessError:
        console.print("[red]❌ Editor exited with error[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ Failed to edit configuration: {e}[/red]")
        ctx.exit(1)
