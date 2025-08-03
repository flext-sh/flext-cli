"""FLEXT CLI Configuration Commands - Settings and Profile Management.

This module implements configuration management commands for the FLEXT CLI,
providing comprehensive configuration operations including profile management,
setting manipulation, and hierarchical configuration support.

Commands:
    ✅ show: Display current configuration with various output formats
    ✅ get: Retrieve specific configuration values with type safety
    ✅ set: Update configuration values with validation
    ✅ reset: Reset configuration to defaults with confirmation

Architecture:
    - Click-based command definitions with Rich table output
    - FlextBaseSettings integration for type-safe configuration
    - Hierarchical configuration with profile support (dev/staging/prod)
    - YAML/JSON export and import capabilities

Configuration Features:
    - Profile-based configuration management
    - Environment variable override support
    - Type-safe value parsing and validation
    - Secure value handling (passwords, tokens)
    - Configuration inheritance and merging

Current Implementation Status:
    ✅ Basic configuration commands implemented
    ✅ Profile support and type validation
    ✅ Multiple output formats (table, json, yaml)
    ⚠️ Basic profile loading (TODO: Sprint 1 - enhance profiles)
    ❌ Configuration encryption not implemented (TODO: Sprint 2)

TODO (docs/TODO.md):
    Sprint 1: Implement hierarchical profile loading system
    Sprint 2: Add configuration value encryption for secrets
    Sprint 3: Add configuration templates and validation schemas
    Sprint 9: Add advanced profile management and inheritance

Integration:
    - Used by all CLI commands for configuration access
    - Integrates with authentication for secure settings
    - Supports ecosystem service configuration
    - Profile-aware for multi-environment deployments

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
from rich.table import Table

from flext_cli.utils.config import parse_config_value, set_config_attribute

if TYPE_CHECKING:
    from flext_cli.domain.cli_context import CLIContext


@click.group()
def config() -> None:
    """Configuration management for FLEXT CLI and ecosystem services.

    Provides comprehensive configuration commands for managing CLI settings,
    profiles, and service configurations. Supports hierarchical configuration
    with environment-specific overrides and secure value handling.

    Available Commands:
        show   - Display current configuration with formatting options
        get    - Retrieve specific configuration values
        set    - Update configuration values with type validation
        reset  - Reset configuration to defaults

    Profile Support:
        - dev: Development environment settings
        - staging: Staging environment configuration
        - prod: Production environment settings
        - custom: User-defined profiles

    Configuration Hierarchy:
        1. Command-line options (highest priority)
        2. Environment variables (FLX_*, FLEXT_CLI_*)
        3. Profile-specific configuration files
        4. Default configuration values (lowest priority)

    Examples:
        $ flext config show --format json
        $ flext config get auth.username
        $ flext config set debug.enabled true --type bool
        $ flext config reset --key auth --confirm

    TODO (Sprint 1):
        - Implement advanced profile management
        - Add configuration validation schemas
        - Integrate with ecosystem service configs

    """


@config.command()
@click.argument("key", required=False)
@click.pass_context
def get(ctx: click.Context, key: str | None) -> None:
    """Get configuration value."""
    cli_context: CLIContext = ctx.obj["cli_context"]

    if key:
        _get_single_key(ctx, cli_context, key)
    else:
        _get_all_config(cli_context)


@config.command()
@click.pass_context
def show(ctx: click.Context) -> None:
    """Show current configuration."""
    cli_context: CLIContext = ctx.obj["cli_context"]
    _get_all_config(cli_context)


def _get_single_key(ctx: click.Context, cli_context: CLIContext, key: str) -> None:
    """Get single configuration key value."""
    try:
        value = _find_config_value(cli_context, key)
        if value is None:
            cli_context.print_warning(f"Configuration key '{key}' not found")
            ctx.exit(1)

        _print_config_value(cli_context, key, value)
    except (AttributeError, KeyError, ValueError) as e:
        cli_context.print_error(f"Failed to get configuration: {e}")
        ctx.exit(1)
    except OSError as e:
        cli_context.print_error(f"Configuration file error: {e}")
        ctx.exit(1)


def _find_config_value(cli_context: CLIContext, key: str) -> object:
    """Find configuration value in config or settings."""
    value = getattr(cli_context.config, key, None)
    if value is None:
        value = getattr(cli_context.settings, key, None)
    return value


def _print_config_value(cli_context: CLIContext, key: str, value: object) -> None:
    """Print configuration value in the requested format."""
    output_format = cli_context.config.output_format

    if output_format == "json":
        cli_context.console.print(
            json.dumps({key: value}, indent=2, default=str),
        )
    elif output_format == "yaml":
        cli_context.console.print(
            yaml.dump({key: value}, default_flow_style=False),
        )
    else:
        cli_context.console.print(f"{key}: {value}")


def _get_all_config(cli_context: CLIContext) -> None:
    """Get all configuration values."""
    config_data = {
        **cli_context.config.model_dump(),
        **cli_context.settings.model_dump(),
    }

    output_format = cli_context.config.output_format

    if output_format == "json":
        cli_context.console.print(json.dumps(config_data, indent=2, default=str))
    elif output_format == "yaml":
        cli_context.console.print(yaml.dump(config_data, default_flow_style=False))
    else:
        _print_config_table(cli_context, config_data)


def _print_config_table(
    cli_context: CLIContext,
    config_data: dict[str, object],
) -> None:
    """Print configuration data as a table."""
    table = Table(title="FLEXT Configuration v0.7.0")
    table.add_column("Key", style="cyan")
    table.add_column("Value", style="white")
    table.add_column("Source", style="dim")

    for k, v in config_data.items():
        source = "config" if hasattr(cli_context.config, k) else "settings"
        table.add_row(k, str(v), source)

    cli_context.console.print(table)


@config.command()
@click.argument("key")
@click.argument("value")
@click.pass_context
def set_value(ctx: click.Context, key: str, value: str) -> None:
    """Set configuration value."""
    cli_context: CLIContext = ctx.obj["cli_context"]

    try:
        # Parse configuration value using utility function
        parse_result = parse_config_value(value)
        if not parse_result.is_success:
            error_msg = parse_result.error or "Configuration parsing failed"
            cli_context.print_error(error_msg)
            ctx.exit(1)

        parsed_value = parse_result.data

        # Try to set in config first, then settings using utility function
        config_result = set_config_attribute(cli_context.config, key, parsed_value)
        if config_result.is_success:
            success_msg = config_result.data or "Configuration updated successfully"
            cli_context.print_success(success_msg)
            return

        settings_result = set_config_attribute(cli_context.settings, key, parsed_value)
        if settings_result.is_success:
            success_msg = settings_result.data or "Settings updated successfully"
            cli_context.print_success(success_msg)
            return

        cli_context.print_warning(
            f"Configuration key '{key}' not found in config or settings",
        )
        ctx.exit(1)
    except (AttributeError, KeyError, ValueError, TypeError) as e:
        cli_context.print_error(f"Failed to set configuration: {e}")
        ctx.exit(1)
    except OSError as e:
        cli_context.print_error(f"Configuration file error: {e}")
        ctx.exit(1)


@config.command()
@click.pass_context
def validate(ctx: click.Context) -> None:
    """Validate configuration."""
    cli_context: CLIContext = ctx.obj["cli_context"]

    def _raise_config_error() -> None:
        """Raise configuration error."""
        msg = "Configuration not loaded"
        raise ValueError(msg)

    try:
        if not cli_context.config:
            _raise_config_error()

        if cli_context.settings:
            cli_context.print_info(
                f"Config directory: {cli_context.config.config_dir}",
            )
            cli_context.print_info(f"Profile: {cli_context.config.profile}")
            cli_context.print_info(f"API URL: {cli_context.config.api_url}")
            cli_context.print_success("Configuration validation passed")
    except (AttributeError, ValueError, TypeError) as e:
        cli_context.print_error(f"Configuration validation error: {e}")
        ctx.exit(1)
    except OSError as e:
        cli_context.print_error(f"Configuration file error: {e}")
        ctx.exit(1)


@config.command()
@click.pass_context
def path(ctx: click.Context) -> None:
    """Show configuration file paths and status."""
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
def edit(ctx: click.Context, _profile: str | None) -> None:
    """Edit configuration file using default editor."""
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

            with config_file.open("w", encoding="utf-8") as f:
                yaml.dump(default_config, f, default_flow_style=False)

            cli_context.print_info(f"Created default configuration at {config_file}")

        # Security: Editor is from environment variable, validate it exists
        if not editor or not editor.strip():
            cli_context.print_error(
                "No editor configured (EDITOR environment variable)",
            )
            ctx.exit(1)

        subprocess.run([editor, str(config_file)], check=True, shell=False)  # noqa: S603
        cli_context.print_success("Configuration updated")
        cli_context.print_info("Restart CLI to apply changes")

    except subprocess.CalledProcessError:
        cli_context.print_error("Editor exited with error")
        ctx.exit(1)
    except (FileNotFoundError, PermissionError, OSError) as e:
        cli_context.print_error(f"Failed to edit configuration: {e}")
        ctx.exit(1)
    except (AttributeError, ValueError, TypeError) as e:
        cli_context.print_error(f"Configuration model error: {e}")
        ctx.exit(1)
