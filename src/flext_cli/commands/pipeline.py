"""Pipeline management commands for FLEXT CLI.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import TYPE_CHECKING

import click

if TYPE_CHECKING:
    from rich.console import Console


@click.group()
def pipeline() -> None:
    """Pipeline management commands."""


@pipeline.command(name="list")
@click.option("--page", "-p", default=1, help="Page number")
@click.option("--page-size", "-s", default=20, help="Page size")
@click.option("--status", help="Filter by status")
@click.pass_context
def list_pipelines(
    ctx: click.Context,
    page: int,
    page_size: int,
    status: str | None,
) -> None:
    """List pipelines."""
    console: Console = ctx.obj.get("console")
    if console:
        console.print(f"Listing pipelines (page {page}, size {page_size})")
        if status:
            console.print(f"Filtered by status: {status}")
        console.print("[yellow]Pipeline listing not yet implemented[/yellow]")


@pipeline.command()
@click.argument("name")
@click.pass_context
def show(ctx: click.Context, name: str) -> None:
    """Show pipeline details."""
    console: Console = ctx.obj.get("console")
    if console:
        console.print(f"Pipeline details for: {name}")
        console.print("[yellow]Pipeline details not yet implemented[/yellow]")


@pipeline.command()
@click.argument("name")
@click.pass_context
def run(ctx: click.Context, name: str) -> None:
    """Run a pipeline."""
    console: Console = ctx.obj.get("console")
    if console:
        console.print(f"Running pipeline: {name}")
        console.print("[yellow]Pipeline execution not yet implemented[/yellow]")


@pipeline.command()
@click.argument("name")
@click.pass_context
def stop(ctx: click.Context, name: str) -> None:
    """Stop a pipeline."""
    console: Console = ctx.obj.get("console")
    if console:
        console.print(f"Stopping pipeline: {name}")
        console.print("[yellow]Pipeline stopping not yet implemented[/yellow]")
