"""Configuration management commands using flext-core patterns.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import json
import os
import subprocess
from typing import TYPE_CHECKING

import click
import yaml
from flext_cli.utils.config import parse_config_value, set_config_attribute
from rich.table import Table

if TYPE_CHECKING:
    from flext_cli.core.base import CLIContext


@click.group()
def config() -> None:
    """Configuration management commands."""


class ConfigDisplayManager:
    """Handles configuration display with SOLID SRP - focused responsibility."""

    def __init__(self, cli_context: CLIContext) -> None:
        """Initialize with CLI context."""
        self.cli_context = cli_context

    def get_config_value(self, key: str) -> object | None:
        """Get a specific configuration value from config or settings."""
        value = getattr(self.cli_context.config, key, None)
        if value is None:
            value = getattr(self.cli_context.settings, key, None)
        return value

    def format_single_value(self, key: str, value: object) -> None:
        """Format and display a single configuration value."""
        format_type = self.cli_context.config.output_format

        if format_type == "json":
            self.cli_context.console.print(
                json.dumps({key: value}, indent=2, default=str),
            )
        elif format_type == "yaml":
            self.cli_context.console.print(
                yaml.dump({key: value}, default_flow_style=False),
            )
        else:
            self.cli_context.console.print(f"{key}: {value}")

    def get_all_config_data(self) -> dict[str, object]:
        """Get all configuration data merged."""
        return {
            **self.cli_context.config.model_dump(),
            **self.cli_context.settings.model_dump(),
        }

    def format_all_values(self, config_data: dict[str, object]) -> None:
        """Format and display all configuration values."""
        format_type = self.cli_context.config.output_format

        if format_type == "json":
            self.cli_context.console.print(
                json.dumps(config_data, indent=2, default=str)
            )
        elif format_type == "yaml":
            self.cli_context.console.print(
                yaml.dump(config_data, default_flow_style=False)
            )
        else:
            self._display_as_table(config_data)

    def _display_as_table(self, config_data: dict[str, object]) -> None:
        """Display configuration data as a Rich table."""
        table = Table(title="FLEXT Configuration v0.7.0")
        table.add_column("Key", style="cyan")
        table.add_column("Value", style="white")
        table.add_column("Source", style="dim")

        for k, v in config_data.items():
            source = "config" if hasattr(self.cli_context.config, k) else "settings"
            table.add_row(k, str(v), source)

        self.cli_context.console.print(table)


@config.command()
@click.argument("key", required=False)
@click.pass_context
def get(ctx: click.Context, key: str | None) -> None:
    """Get configuration value.

    REFACTORED: Applied SOLID SRP - reduced complexity from 23 to ~3-5 per method.
    """
    cli_context: CLIContext = ctx.obj["cli_context"]
    display_manager = ConfigDisplayManager(cli_context)

    if key:
        try:
            value = display_manager.get_config_value(key)

            if value is None:
                cli_context.print_warning(f"Configuration key '{key}' not found")
                ctx.exit(1)

            display_manager.format_single_value(key, value)
        except (RuntimeError, ValueError, TypeError) as e:
            cli_context.print_error(f"Failed to get configuration: {e}")
            ctx.exit(1)
    else:
        # Get and display all values
        config_data = display_manager.get_all_config_data()
        display_manager.format_all_values(config_data)


@config.command()
@click.argument("key")
@click.argument("value")
@click.pass_context
def set_value(ctx: click.Context, key: str, value: str) -> None:
    cli_context: CLIContext = ctx.obj["cli_context"]

    try:
        # Parse configuration value using utility function
        parse_result = parse_config_value(value)
        if not parse_result.is_success:
            cli_context.print_error(parse_result.error)
            ctx.exit(1)

        parsed_value = parse_result.value

        # Try to set in config first, then settings using utility function
        config_result = set_config_attribute(cli_context.config, key, parsed_value)
        if config_result.is_success:
            cli_context.print_success(config_result.value)
            return

        settings_result = set_config_attribute(cli_context.settings, key, parsed_value)
        if settings_result.is_success:
            cli_context.print_success(settings_result.value)
            return

        cli_context.print_warning(
            f"Configuration key '{key}' not found in config or settings",
        )
        ctx.exit(1)
    except (RuntimeError, ValueError, TypeError) as e:
        cli_context.print_error(f"Failed to set configuration: {e}")
        ctx.exit(1)


@config.command()
@click.pass_context
def validate(ctx: click.Context) -> None:
    cli_context: CLIContext = ctx.obj["cli_context"]

    try:
        if not cli_context.config:
            msg = "Configuration not loaded"
            raise ValueError(msg)

        if cli_context.settings:
            cli_context.print_info(
                f"Config directory: {cli_context.config.config_dir}",
            )
            cli_context.print_info(f"Profile: {cli_context.config.profile}")
            cli_context.print_info(f"API URL: {cli_context.config.api_url}")
            cli_context.print_success("Configuration validation passed")
    except (RuntimeError, ValueError, TypeError) as e:
        cli_context.print_error(f"Configuration validation error: {e}")
        ctx.exit(1)


@config.command()
@click.pass_context
def path(ctx: click.Context) -> None:
    cli_context: CLIContext = ctx.obj["cli_context"]

    # Use flat structure from utils/config.py
    cli_context.print_info(f"Configuration directory: {cli_context.config.config_dir}")
    cli_context.print_info(f"Cache directory: {cli_context.config.cache_dir}")
    cli_context.print_info(f"Log directory: {cli_context.config.log_dir}")
    cli_context.print_info(f"Data directory: {cli_context.config.config_dir / 'data'}")

    # Show auth files
    cli_context.print_info(f"Token file: {cli_context.config.token_file}")
    cli_context.print_info(
        f"Refresh token file: {cli_context.config.refresh_token_file}",
    )

    # Check if directories exist:
    for name, path in [
        ("config", cli_context.config.config_dir),
        ("cache", cli_context.config.cache_dir),
        ("log", cli_context.config.log_dir),
    ]:
        exists = path.exists()
        status = "✓" if exists else "✗"
        color = "green" if exists else "red"
        cli_context.console.print(f"  [{color}]{status}[/{color}] {name}: {path}")

    # Show config files:
    cli_context.print_info("\nConfiguration files:")
    config_files = [
        ("config.yaml", cli_context.config.config_dir / "config.yaml"),
        ("settings.toml", cli_context.config.config_dir / "settings.toml"),
    ]

    for name, path in config_files:
        exists = path.exists()
        status = "✓" if exists else "✗"
        color = "green" if exists else "yellow"
        cli_context.console.print(f"  [{color}]{status}[/{color}] {name}: {path}")


@config.command()
@click.option("--profile", "-p", help="Profile name to edit")
@click.pass_context
def edit(ctx: click.Context, profile: str | None) -> None:
    cli_context: CLIContext = ctx.obj["cli_context"]

    config_dir = cli_context.config.config_dir
    config_file = config_dir / "config.yaml"
    editor = os.environ.get("EDITOR", "vim")

    try:
        # Ensure config directory exists
        config_dir.mkdir(parents=True, exist_ok=True)

        if not config_file.exists():
            # Create default config using flext-core models
            default_config = {
                "config": cli_context.config.model_dump(),
                "settings": cli_context.settings.model_dump(),
            }

            with open(config_file, "w", encoding="utf-8") as f:
                yaml.dump(default_config, f, default_flow_style=False)

            cli_context.print_info(f"Created default configuration at {config_file}")

        subprocess.run([editor, str(config_file)], check=True)
        cli_context.print_success("Configuration updated")
        cli_context.print_info("Restart CLI to apply changes")

    except subprocess.CalledProcessError:
        cli_context.print_error("Editor exited with error")
        ctx.exit(1)
    except (RuntimeError, ValueError, TypeError) as e:
        cli_context.print_error(f"Failed to edit configuration: {e}")
        ctx.exit(1)
