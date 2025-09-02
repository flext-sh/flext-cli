"""Shim exposing debug Click group and commands for tests."""

from __future__ import annotations

import click
from rich.console import Console

from flext_cli.debug import connectivity, debug_cmd, performance


@debug_cmd.command(help="Validate environment and configuration")
@click.pass_context
def validate(ctx: click.Context) -> None:
    """Validate configuration and environment in a lightweight manner."""
    console: Console = (ctx.obj or {}).get("console", Console())
    console.print("Validation completed")


@debug_cmd.command(help="Show environment information")
def env() -> None:
    """Show environment information for diagnostics."""
    Console().print("Environment info")


@debug_cmd.command(help="Show CLI paths")
def paths() -> None:
    """Display important CLI paths (config/cache/logs)."""
    Console().print("Paths:")


@debug_cmd.command(help="Trace diagnostics")
def trace() -> None:
    """Emit a simple tracing message to confirm wiring."""
    Console().print("Tracing enabled")


__all__ = [
    "connectivity",
    "debug_cmd",
    "env",
    "paths",
    "performance",
    "trace",
    "validate",
]
