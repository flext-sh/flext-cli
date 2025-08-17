#!/usr/bin/env python3
"""FLEXT CLI Library Click Integration Example.

This example demonstrates how to use FLEXT CLI library components to build
comprehensive Click-based CLI applications with rich functionality, proper
configuration handling, and enterprise-grade patterns.

Key features demonstrated:
- Click command integration with FLEXT CLI types
- CLI decorators for enhanced functionality
- Configuration-aware commands
- Rich output formatting
- Error handling and validation

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import asyncio
import random
import time
from pathlib import Path

import click
from rich import Console

import flext_cli


# CLI Application with FLEXT CLI integration
@click.group()
@click.option(
    "--config-file",
    type=flext_cli.ExistingFile,
    help="Configuration file path",
)
@click.option(
    "--output-format",
    type=click.Choice(["table", "json", "yaml", "csv", "plain"]),
    default="table",
    help="Output format",
)
@click.option("--debug/--no-debug", default=False, help="Enable debug mode")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
@click.pass_context
def cli(
    ctx: click.Context,
    config_file: Path | None,
    output_format: str,
    *,
    debug: bool,
    verbose: bool,
) -> None:
    """FLEXT CLI Example Application."""
    # Create CLI context with FLEXT CLI library
    cli_context = flext_cli.CLIContext(
      profile="example",
      output_format=output_format,
      debug=debug,
      verbose=verbose,
    )

    # Store context for commands
    ctx.ensure_object(dict)
    ctx.obj["cli_context"] = cli_context
    ctx.obj["config_file"] = config_file


@cli.command()
@click.option(
    "--count",
    type=flext_cli.PositiveInt,
    default=1,
    help="Number of iterations",
)
@click.option(
    "--url",
    type=flext_cli.URL,
    default="https://api.example.com",
    help="API endpoint URL",
)
@click.pass_context
@flext_cli.measure_time(show_in_output=True)
@flext_cli.handle_service_result
def process(ctx: click.Context, count: int, url: str) -> str:
    """Process data with specified parameters."""
    cli_context = ctx.obj["cli_context"]
    console = Console()

    console.print("[bold blue]Processing with FLEXT CLI Library[/bold blue]")
    console.print(f"Profile: {cli_context.profile}")
    console.print(f"Output format: {cli_context.output_format}")
    console.print(f"Debug mode: {cli_context.debug}")
    console.print(f"Count: {count}")
    console.print(f"URL: {url}")

    # Use FLEXT CLI helper for validation
    helper = flext_cli.CLIHelper()
    if not helper.validate_url(url):
      return f"❌ Invalid URL: {url}"

    # Simulate processing
    [f"Processed item {i + 1}" for i in range(count)]

    console.print(f"[green]✅ Processed {count} items successfully[/green]")
    return f"Completed processing {count} items"


@cli.command()
@click.argument("input_file", type=flext_cli.ExistingFile)
@click.argument("output_dir", type=flext_cli.ExistingDir)
@click.option(
    "--new-file",
    type=flext_cli.NewFile,
    help="Optional new file to create",
)
@click.pass_context
@flext_cli.confirm_action("This will process the file. Continue?")
@flext_cli.with_spinner("Processing file...")
@flext_cli.handle_service_result
def transform(
    ctx: click.Context,
    input_file: Path,
    output_dir: Path,
    new_file: Path | None,
) -> str:
    """Transform input file and save to output directory."""
    ctx.obj["cli_context"]
    console = Console()

    console.print("[bold blue]File Transformation[/bold blue]")
    console.print(f"Input file: {input_file}")
    console.print(f"Output directory: {output_dir}")
    if new_file:
      console.print(f"New file: {new_file}")

    # Use FLEXT CLI helper utilities
    helper = flext_cli.CLIHelper()

    # Validate paths
    if not helper.validate_path(str(input_file), must_exist=True):
      return f"❌ Input file does not exist: {input_file}"

    if not helper.validate_path(str(output_dir), must_exist=True):
      return f"❌ Output directory does not exist: {output_dir}"

    # Get file size for display
    file_size = input_file.stat().st_size
    formatted_size = helper.format_size(file_size)
    console.print(f"File size: {formatted_size}")

    # Simulate transformation
    time.sleep(0.5)  # Simulate processing time

    output_file = output_dir / f"transformed_{input_file.name}"
    console.print("[green]✅ File transformed successfully[/green]")
    console.print(f"Output: {output_file}")

    return f"Transformed {input_file.name} -> {output_file.name}"


@cli.command()
@click.option(
    "--email",
    prompt=True,
    help="Email address to validate",
)
@click.option(
    "--phone",
    help="Phone number (optional)",
)
@click.pass_context
@flext_cli.validate_config(["profile", "output_format"])
def validate(ctx: click.Context, email: str, phone: str | None) -> None:
    """Validate user input with FLEXT CLI helpers."""
    cli_context = ctx.obj["cli_context"]
    console = Console()
    helper = flext_cli.CLIHelper()

    console.print("[bold blue]Input Validation[/bold blue]")
    console.print(f"Using profile: {cli_context.profile}")

    # Validate email
    if helper.validate_email(email):
      helper.print_success(f"Valid email: {email}")
    else:
      helper.print_error(f"Invalid email: {email}")

    # Validate phone if provided
    if phone:
      # Simple phone validation (could be enhanced)
      min_phone_length = 10
      if len(phone.replace("-", "").replace(" ", "")) >= min_phone_length:
          helper.print_success(f"Phone number looks valid: {phone}")
      else:
          helper.print_warning(f"Phone number may be invalid: {phone}")

    helper.print_info("Validation completed")


@cli.command()
@click.option(
    "--delay",
    type=float,
    default=1.0,
    help="Delay in seconds",
)
@click.pass_context
@flext_cli.async_command
@flext_cli.handle_service_result
async def async_task(ctx: click.Context, delay: float) -> str:
    """Demonstrate async command with FLEXT CLI."""
    cli_context = ctx.obj["cli_context"]
    console = Console()

    console.print("[bold blue]Async Task Example[/bold blue]")
    console.print(f"Profile: {cli_context.profile}")
    console.print(f"Delay: {delay}s")

    # Simulate async work
    console.print("⏳ Starting async operation...")
    await asyncio.sleep(delay)
    console.print("[green]✅ Async operation completed[/green]")

    return f"Async task completed after {delay}s"


@cli.command()
@click.option(
    "--max-attempts",
    type=flext_cli.PositiveInt,
    default=3,
    help="Maximum retry attempts",
)
@click.pass_context
@flext_cli.retry(max_attempts=3, delay=0.5)
@flext_cli.handle_service_result
def unreliable(ctx: click.Context, max_attempts: int) -> str:
    """Demonstrate retry decorator with potentially failing operation."""
    console = Console()
    # Use context to optionally adjust behavior (e.g., lower failure in debug)
    cli_context = ctx.obj.get("cli_context") if isinstance(ctx.obj, dict) else None
    is_debug = bool(getattr(cli_context, "debug", False))
    console.print("[bold blue]Unreliable Operation with Retry[/bold blue]")
    console.print(f"Maximum retry attempts configured: {max_attempts}")

    # Simulate random failure (less likely in debug to speed up demos)
    failure_probability = 0.5 if is_debug else 0.7
    if random.random() < failure_probability:  # noqa: S311
      msg = "Simulated random failure"
      raise click.ClickException(msg)

    console.print("[green]✅ Operation succeeded![/green]")
    return "Operation completed successfully"


@cli.command()
@click.pass_context
def info(ctx: click.Context) -> None:
    """Show FLEXT CLI library information."""
    console = Console()

    console.print("[bold green]FLEXT CLI Library Information[/bold green]")
    console.print(f"Version: {flext_cli.__version__}")

    # Show configuration
    config = flext_cli.get_config()
    console.print("\n[bold blue]Configuration:[/bold blue]")
    console.print(f"  API URL: {config.api_url}")
    console.print(f"  Timeout: {config.timeout}s")
    console.print(f"  Profile: {config.profile}")

    # Show settings
    settings = flext_cli.get_settings()
    console.print("\n[bold blue]Settings:[/bold blue]")
    console.print(f"  Project: {settings.project_name}")
    console.print(f"  Version: {settings.project_version}")
    console.print(f"  Log Level: {settings.log_level}")

    # Show CLI context
    cli_context = ctx.obj.get("cli_context")
    if cli_context:
      console.print("\n[bold blue]CLI Context:[/bold blue]")
      console.print(f"  Profile: {cli_context.profile}")
      console.print(f"  Output Format: {cli_context.output_format}")
      console.print(f"  Debug: {cli_context.debug}")
      console.print(f"  Verbose: {cli_context.verbose}")


def main() -> None:
    """Run the CLI application."""
    cli()


if __name__ == "__main__":
    main()
