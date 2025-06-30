"""Pipeline management commands for FLEXT CLI."""

from __future__ import annotations

import asyncio
import json
from typing import TYPE_CHECKING

import click
import yaml
from rich.progress import Progress, SpinnerColumn, TextColumn

from flext_cli.client import FlextApiClient, PipelineConfig
from flext_cli.utils.output import format_pipeline, format_pipeline_list

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
    ctx: click.Context, page: int, page_size: int, status: str | None
) -> None:
    """List all pipelines."""
    console: Console = ctx.obj["console"]
    output_format = ctx.obj["output"]

    async def _list() -> None:
        try:
            async with FlextApiClient() as client:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console,
                    transient=True,
                ) as progress:
                    progress.add_task("Loading pipelines...")
                    pipeline_list = await client.list_pipelines(page, page_size, status)

                if output_format == "json":
                    console.print(json.dumps(pipeline_list.model_dump(), indent=2))
                elif output_format == "yaml":
                    console.print(
                        yaml.dump(pipeline_list.model_dump(), default_flow_style=False)
                    )
                else:
                    format_pipeline_list(console, pipeline_list)

        except Exception as e:
            console.print(f"[red]❌ Failed to list pipelines: {e}[/red]")
            ctx.exit(1)

    asyncio.run(_list())


@pipeline.command()
@click.argument("pipeline_id")
@click.pass_context
def get(ctx: click.Context, pipeline_id: str) -> None:
    """Get pipeline details."""
    console: Console = ctx.obj["console"]
    output_format = ctx.obj["output"]

    async def _get() -> None:
        try:
            async with FlextApiClient() as client:
                pipeline = await client.get_pipeline(pipeline_id)

                if output_format == "json":
                    console.print(json.dumps(pipeline.model_dump(), indent=2))
                elif output_format == "yaml":
                    console.print(
                        yaml.dump(pipeline.model_dump(), default_flow_style=False)
                    )
                else:
                    format_pipeline(console, pipeline)

        except Exception as e:
            console.print(f"[red]❌ Failed to get pipeline: {e}[/red]")
            ctx.exit(1)

    asyncio.run(_get())


@pipeline.command()
@click.option("--name", prompt=True, help="Pipeline name")
@click.option("--tap", prompt=True, help="Source tap plugin")
@click.option("--target", prompt=True, help="Target plugin")
@click.option("--transform", help="Transform plugin")
@click.option("--schedule", help="Cron schedule")
@click.option("--config-file", type=click.Path(exists=True), help="Configuration file")
@click.pass_context
def create(
    ctx: click.Context,
    name: str,
    tap: str,
    target: str,
    transform: str | None,
    schedule: str | None,
    config_file: str | None,
) -> None:
    """Create new pipeline."""
    console: Console = ctx.obj["console"]

    async def _create() -> None:
        try:
            # Load additional config from file if provided
            additional_config = {}
            if config_file:
                with open(config_file) as f:
                    if config_file.endswith((".yaml", ".yml")):
                        additional_config = yaml.safe_load(f)
                    else:
                        additional_config = json.load(f)

            config = PipelineConfig(
                name=name,
                tap=tap,
                target=target,
                transform=transform,
                schedule=schedule,
                config=additional_config,
            )

            async with FlextApiClient() as client:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console,
                    transient=True,
                ) as progress:
                    progress.add_task("Creating pipeline...")
                    pipeline = await client.create_pipeline(config)

                success_msg = f"[green]✅ Pipeline '{pipeline.name}' created![/green]"
                console.print(success_msg)
                console.print(f"Pipeline ID: {pipeline.id}")

        except Exception as e:
            console.print(f"[red]❌ Failed to create pipeline: {e}[/red]")
            ctx.exit(1)

    asyncio.run(_create())


@pipeline.command()
@click.argument("pipeline_id")
@click.option("--full-refresh", is_flag=True, help="Run full refresh")
@click.option("--follow", "-f", is_flag=True, help="Follow execution logs")
@click.pass_context
def run(ctx: click.Context, pipeline_id: str, full_refresh: bool, follow: bool) -> None:
    """Run pipeline execution."""
    console: Console = ctx.obj["console"]

    async def _run() -> None:
        try:
            async with FlextApiClient() as client:
                # Start execution
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console,
                    transient=True,
                ) as progress:
                    progress.add_task("Starting pipeline execution...")
                    execution = await client.run_pipeline(pipeline_id, full_refresh)

                console.print("[green]✅ Pipeline execution started[/green]")
                console.print(
                    f"Execution ID: {execution.get('execution_id', 'Unknown')}"
                )

                if follow:
                    console.print("\n[yellow]Following execution logs...[/yellow]")
                    # TODO: Implement log streaming
                    console.print("[yellow]Log streaming not yet implemented[/yellow]")

        except Exception as e:
            console.print(f"[red]❌ Failed to run pipeline: {e}[/red]")
            ctx.exit(1)

    asyncio.run(_run())


@pipeline.command()
@click.argument("pipeline_id")
@click.pass_context
def status(ctx: click.Context, pipeline_id: str) -> None:
    """Check pipeline execution status."""
    console: Console = ctx.obj["console"]

    async def _status() -> None:
        try:
            async with FlextApiClient() as client:
                status_info = await client.get_pipeline_status(pipeline_id)

                console.print(f"Pipeline: {status_info.get('name', pipeline_id)}")
                console.print(f"Status: {status_info.get('status', 'Unknown')}")

                if "last_execution" in status_info:
                    last_exec = status_info["last_execution"]
                    console.print("\nLast Execution:")
                    console.print(
                        f"  Started: {last_exec.get('started_at', 'Unknown')}"
                    )
                    console.print(
                        f"  Completed: {last_exec.get('completed_at', 'Not completed')}"
                    )
                    console.print(f"  Duration: {last_exec.get('duration', 'Unknown')}")
                    console.print(f"  Records: {last_exec.get('records_processed', 0)}")

        except Exception as e:
            console.print(f"[red]❌ Failed to get pipeline status: {e}[/red]")
            ctx.exit(1)

    asyncio.run(_status())


@pipeline.command()
@click.argument("pipeline_id")
@click.option("--tail", "-n", default=100, help="Number of lines to show")
@click.option("--execution-id", help="Specific execution ID")
@click.option("--follow", "-f", is_flag=True, help="Follow log output")
@click.pass_context
def logs(
    ctx: click.Context,
    pipeline_id: str,
    tail: int,
    execution_id: str | None,
    follow: bool,
) -> None:
    """View pipeline execution logs."""
    console: Console = ctx.obj["console"]

    async def _logs() -> None:
        try:
            async with FlextApiClient() as client:
                log_lines = await client.get_pipeline_logs(
                    pipeline_id, execution_id, tail
                )

                for line in log_lines:
                    console.print(line)

                if follow:
                    console.print(
                        "\n[yellow]Following logs not yet implemented[/yellow]"
                    )

        except Exception as e:
            console.print(f"[red]❌ Failed to get logs: {e}[/red]")
            ctx.exit(1)

    asyncio.run(_logs())


@pipeline.command()
@click.argument("pipeline_id")
@click.option("--force", is_flag=True, help="Force deletion without confirmation")
@click.pass_context
def delete(ctx: click.Context, pipeline_id: str, force: bool) -> None:
    """Delete pipeline."""
    console: Console = ctx.obj["console"]

    async def _delete() -> None:
        try:
            # Get pipeline details first
            async with FlextApiClient() as client:
                pipeline = await client.get_pipeline(pipeline_id)

                if not force:
                    confirm = click.confirm(
                        f"Are you sure you want to delete pipeline '{pipeline.name}'?"
                    )
                    if not confirm:
                        console.print("[yellow]Deletion cancelled[/yellow]")
                        return

                await client.delete_pipeline(pipeline_id)
                console.print(
                    f"[green]✅ Pipeline '{pipeline.name}' deleted successfully[/green]"
                )

        except Exception as e:
            console.print(f"[red]❌ Failed to delete pipeline: {e}[/red]")
            ctx.exit(1)

    asyncio.run(_delete())
