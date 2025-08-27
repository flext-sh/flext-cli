#!/usr/bin/env python3
"""02 - CLI Commands and Click Integration.

This example demonstrates Click framework integration with flext-cli patterns:

Key Patterns Demonstrated:
- Click commands using FlextResult for error handling
- CLI decorators (@cli_enhanced, @cli_measure_time, @cli_confirm)
- Type-safe CLI options using flext-cli types (URL, PositiveInt, ExistingFile)
- CLI mixins for reusable functionality
- Service integration with Click commands

Architecture Layers:
- Application: Click commands with flext-cli decorators
- Service: CLI service integration for command execution
- Infrastructure: Output formatting and validation

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import time
from pathlib import Path

import click
from flext_core import FlextResult
from rich.console import Console
from rich.panel import Panel

from flext_cli import (
    CLIHelper,
    FlextCliCommand,
    get_cli_config,
    setup_cli,
)


# CLI Mixins for reusable functionality
class DemoCommandMixin:
    """Mixin providing demo command functionality."""

    def __init__(self) -> None:
        self.console = Console()
        self.helper = CLIHelper()

    def log_operation(self, operation: str) -> None:
        """Log operation using Rich console."""
        self.console.print(f"[green]→[/green] {operation}")

    def show_result[T](self, result: FlextResult[T]) -> None:
        """Display operation result."""
        if result.is_success:
            self.console.print(f"[green]✅ Success:[/green] {result.value}")
        else:
            self.console.print(f"[red]❌ Error:[/red] {result.error}")


# Click integration with flext-cli patterns
@click.group()
@click.option(
    "--config-file",
    type=click.Path(exists=True, path_type=Path),
    help="Configuration file path",
)
@click.option("--debug/--no-debug", default=False, help="Enable debug mode")
@click.pass_context
def demo_cli(
    ctx: click.Context, config_file: Path | None, *, debug: bool = False
) -> None:
    """FLEXT-CLI Click Integration Demo."""
    # Setup CLI using flext-cli patterns
    setup_result = setup_cli()
    if setup_result.is_failure:
        click.echo(f"Setup failed: {setup_result.error}", err=True)
        ctx.exit(1)

    # Store configuration in Click context
    config = get_cli_config()
    if debug:
        config = config.model_copy(update={"debug": debug})

    # Note: config_file parameter available but not used in this demo
    _ = config_file  # Acknowledge parameter

    ctx.ensure_object(dict)
    ctx.obj["config"] = config
    ctx.obj["console"] = Console()


@demo_cli.command()
@click.option("--url", type=str, required=True, help="Service URL to connect to")
@click.option("--timeout", type=int, default=30, help="Connection timeout")
@click.option("--retries", type=int, default=3, help="Number of retries")
@click.pass_context
def connect(ctx: click.Context, url: str, timeout: int, retries: int) -> None:
    """Test connection to a service with flext-cli integration."""
    # Manual confirmation (instead of @cli_confirm decorator)
    if not click.confirm("This will test the connection. Continue?"):
        return

    # Manual timing start (instead of @cli_measure_time decorator)
    start_time = time.time()

    console = ctx.obj["console"]

    # Create command entity using flext-cli patterns
    command_result = create_connection_command(url, timeout, retries)
    if command_result.is_failure:
        console.print(f"[red]Failed to create command: {command_result.error}[/red]")
        return

    command = command_result.value
    console.print(
        Panel(
            f"Testing connection to: {url}\nTimeout: {timeout}s\nRetries: {retries}",
            title="Connection Test",
        )
    )

    # Execute connection test using FlextResult pattern
    result = execute_connection_test(command)

    mixin = DemoCommandMixin()
    mixin.show_result(result)

    # Manual timing end (instead of @cli_measure_time decorator)
    elapsed = time.time() - start_time
    console.print(f"[dim]Operation completed in {elapsed:.2f}s[/dim]")


@demo_cli.command()
@click.option(
    "--input-file",
    type=click.Path(exists=True, path_type=Path),
    required=True,
    help="Input file to process",
)
@click.option(
    "--output-format", type=click.Choice(["json", "yaml", "csv"]), default="json"
)
@click.option("--batch-size", type=int, default=100, help="Processing batch size")
@click.pass_context
def process_file(
    ctx: click.Context, input_file: Path, output_format: str, batch_size: int
) -> None:
    """Process file with flext-cli patterns."""
    # Manual timing start (instead of @cli_measure_time decorator)
    start_time = time.time()

    console = ctx.obj["console"]

    console.print(
        Panel(
            f"Processing file: {input_file}\n"
            f"Output format: {output_format}\n"
            f"Batch size: {batch_size}",
            title="File Processing",
        )
    )

    # Simulate file processing with FlextResult
    result = simulate_file_processing(input_file, output_format, batch_size)

    mixin = DemoCommandMixin()
    mixin.show_result(result)

    # Manual timing end (instead of @cli_measure_time decorator)
    elapsed = time.time() - start_time
    console.print(f"[dim]Operation completed in {elapsed:.2f}s[/dim]")


@demo_cli.command()
@click.option(
    "--workspace", type=click.Path(path_type=Path), help="Workspace directory"
)
@click.pass_context
def status(ctx: click.Context, workspace: Path | None) -> None:
    """Show CLI status with flext-cli integration."""
    console = ctx.obj["console"]
    config = ctx.obj["config"]

    # Display configuration using flext-cli patterns
    console.print(
        Panel(
            f"Profile: {config.profile}\n"
            f"Debug: {config.debug}\n"
            f"Output Format: {config.output.format}\n"
            f"Workspace: {workspace or Path.cwd()}",
            title="CLI Status",
        )
    )


def create_connection_command(
    url: str, timeout: int, retries: int
) -> FlextResult[FlextCliCommand]:
    """Create connection command using flext-cli domain patterns."""
    try:
        command = FlextCliCommand(
            name="connection-test",
            command_line=f"curl --connect-timeout {timeout} --retry {retries} {url}",
            description=f"Test connection to {url}",
            working_directory=Path.cwd(),  # type: ignore[call-arg]
        )

        return FlextResult[FlextCliCommand].ok(command)

    except Exception as e:
        return FlextResult[FlextCliCommand].fail(
            f"Failed to create connection command: {e}"
        )


def execute_connection_test(command: FlextCliCommand) -> FlextResult[str]:
    """Execute connection test with FlextResult pattern."""
    try:
        # Simulate connection test
        time.sleep(1)  # Simulate network delay

        # Validate command before execution
        validation_result = command.validate_business_rules()
        if validation_result.is_failure:
            return FlextResult[str].fail(
                f"Command validation failed: {validation_result.error}"
            )

        # Start command execution
        command.start_execution()

        # Simulate execution result
        if "localhost" in command.command_line:
            return FlextResult[str].ok("Connection successful to localhost")
        return FlextResult[str].ok("Connection test completed")

    except Exception as e:
        return FlextResult[str].fail(f"Connection test failed: {e}")


def simulate_file_processing(
    file_path: Path, output_format: str, batch_size: int
) -> FlextResult[str]:
    """Simulate file processing with FlextResult pattern."""
    try:
        # Validate file exists
        if not file_path.exists():
            return FlextResult[str].fail(f"File not found: {file_path}")

        # Simulate processing
        time.sleep(0.5)

        lines_processed = 150  # Simulate
        batches = (lines_processed + batch_size - 1) // batch_size

        return FlextResult[str].ok(
            f"Processed {lines_processed} lines in {batches} batches. "
            f"Output format: {output_format}"
        )

    except Exception as e:
        return FlextResult[str].fail(f"File processing failed: {e}")


def main() -> None:
    """Main CLI entry point."""
    try:
        demo_cli()
    except Exception as e:
        console = Console()
        console.print(f"[bold red]CLI error: {e}[/bold red]")


if __name__ == "__main__":
    main()
