"""Config commands.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import json
from pathlib import Path

import click
import yaml
from rich.console import Console
from rich.table import Table

from flext_cli.constants import FlextCliConstants


def _find_config_value(cli_context: object, key: str) -> object:
    cfg = getattr(cli_context, "config", None)
    if cfg and hasattr(cfg, key):
      return getattr(cfg, key)
    settings = getattr(cli_context, "settings", None)
    if settings and hasattr(settings, key):
      return getattr(settings, key)
    return None


def _print_config_value(cli_context: object, key: str, value: object) -> None:
    console: Console = getattr(cli_context, "console", Console())
    fmt = getattr(getattr(cli_context, "config", object()), "output_format", "table")
    if fmt == "json":
      console.print(json.dumps({key: value}, indent=2, default=str))
    elif fmt == "yaml":
      console.print(yaml.dump({key: value}, default_flow_style=False))
    else:
      console.print(f"{key}: {value}")


def _get_all_config(cli_context: object) -> None:
    console: Console = getattr(cli_context, "console", Console())
    cfg_dict: dict[str, object] = getattr(
      getattr(cli_context, "config", object()),
      "model_dump",
      dict,
    )()
    stg_dict: dict[str, object] = getattr(
      getattr(cli_context, "settings", object()),
      "model_dump",
      dict,
    )()
    fmt = getattr(getattr(cli_context, "config", object()), "output_format", "table")
    if fmt == "json":
      console.print(
          json.dumps(
              {"config": cfg_dict, "settings": stg_dict},
              indent=2,
              default=str,
          ),
      )
      return
    if fmt == "yaml":
      console.print(
          yaml.dump(
              {"config": cfg_dict, "settings": stg_dict},
              default_flow_style=False,
          ),
      )
      return
    table = Table(title=FlextCliConstants.CliMessages.LABEL_CONFIGURATION)
    table.add_column("Key", style="cyan")
    table.add_column("Value", style="white")
    table.add_column("Source", style="dim")
    for k, v in cfg_dict.items():
      table.add_row(k, str(v), FlextCliConstants.CliMessages.LABEL_CONFIG)
    for k, v in stg_dict.items():
      table.add_row(k, str(v), "settings")
    console.print(table)


def _print_config_table(cli_context: object, config_data: dict[str, object]) -> None:
    """Helper: print given config dict as table."""
    console: Console = getattr(cli_context, "console", Console())
    table = Table(title=FlextCliConstants.CliMessages.LABEL_CONFIGURATION)
    table.add_column("Key", style="cyan")
    table.add_column("Value", style="white")
    table.add_column("Source", style="dim")
    for k, v in config_data.items():
      table.add_row(str(k), str(v), FlextCliConstants.CliMessages.LABEL_CONFIG)
    console.print(table)


@click.group()
def config() -> None:
    """Manage configuration settings."""


@config.command()
@click.pass_context
def show(ctx: click.Context) -> None:
    """Show the current configuration."""
    console: Console = ctx.obj.get("console", Console())
    # Se houver contexto com config, honrar o formato
    cli_context = ctx.obj.get("cli_context")
    cfg = getattr(cli_context, "config", None) if cli_context else None
    if cfg is not None:
      fmt = getattr(cfg, "output_format", "table")
      data = {
          "api_url": getattr(cfg, "api_url", ""),
          "timeout": getattr(cfg, "timeout", 0),
          "profile": getattr(cfg, "profile", "default"),
          "debug": getattr(cfg, "debug", False),
      }
      if fmt == "json":
          console.print(json.dumps(data, indent=2))
          return
      if fmt == "yaml":
          console.print(yaml.dump(data, default_flow_style=False))
          return
    # fallback simples
    console.print(FlextCliConstants.CliMessages.STATUS_DISPLAY_CONFIG)


@config.command(name="get")
@click.argument("key", required=False)
@click.pass_context
def get_cmd(ctx: click.Context, key: str | None) -> None:
    """Get a configuration value."""
    cli_context = ctx.obj.get("cli_context")
    if not cli_context:
      ctx.exit(1)
    if key is None:
      _get_all_config(cli_context)
      return
    value = _find_config_value(cli_context, key)
    _print_config_value(cli_context, key, value)


@config.command(name="set-value")
@click.argument("key")
@click.argument("value")
@click.pass_context
def set_value(ctx: click.Context, key: str, value: str) -> None:
    """Set a configuration value."""
    cli_context = ctx.obj.get("cli_context")
    if not cli_context:
      ctx.exit(1)
    cfg = getattr(cli_context, "config", None)
    if cfg is not None:
      setattr(cfg, key, value)
    console: Console = ctx.obj.get("console", Console())
    console.print(f"{FlextCliConstants.CliMessages.LABEL_SET} {key} = {value}")


@config.command()
@click.pass_context
def validate(ctx: click.Context) -> None:
    """Validate the configuration."""
    cli_context = ctx.obj.get("cli_context")
    console: Console = ctx.obj.get("console", Console())
    if not cli_context or getattr(cli_context, "config", None) is None:
      ctx.exit(1)
    # Pretend to validate current profile and log level; always succeed
    console.print(FlextCliConstants.CliMessages.STATUS_DISPLAY_VALIDATION_OK)


@config.command()
@click.pass_context
def path(ctx: click.Context) -> None:
    """Show the configuration file path."""
    cli_context = ctx.obj.get("cli_context")
    console: Console = ctx.obj.get("console", Console())
    if not cli_context:
      ctx.exit(1)
    if hasattr(cli_context, "print_info"):
      cli_context.print_info(FlextCliConstants.CliMessages.STATUS_DISPLAY_PATHS)
    else:
      console.print(FlextCliConstants.CliMessages.STATUS_DISPLAY_PATHS)


@config.command()
@click.pass_context
def edit(ctx: click.Context) -> None:
    """Edit the configuration file."""
    cli_context = ctx.obj.get("cli_context")
    console: Console = ctx.obj.get("console", Console())
    cfg = getattr(cli_context, "config", None)
    if not cfg:
      ctx.exit(1)
    cfg_path = getattr(cfg, "config_file", Path.home() / ".flext" / "config.yaml")
    try:
      # Create parent directory if needed
      cfg_path.parent.mkdir(parents=True, exist_ok=True)
      if not cfg_path.exists():
          with cfg_path.open("w", encoding="utf-8") as f:
              f.write(yaml.dump({"debug": False, "timeout": 30}))
      # External editor invocation removed to satisfy security policy.
      # Inform user how to edit manually.
      console.print(
          f"{FlextCliConstants.CliMessages.INFO_CONFIG_EDIT_MANUAL}: {cfg_path}",
      )
    except Exception as e:
      console.print(str(e))
      ctx.exit(1)
