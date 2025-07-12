# FLEXT CLI Migration Guide

This guide helps you migrate existing CLI implementations to use the centralized FLEXT CLI framework.

## Overview

The FLEXT CLI framework provides a unified, standardized way to create command-line interfaces across all FLEXT projects. It's built on Click and Rich, providing consistent behavior, styling, and user experience.

## Installation

Add `flext-cli` as a dependency in your project's `pyproject.toml`:

```toml
[project]
dependencies = [
    "flext-cli>=0.6.0",
    # ... other dependencies
]
```

## Core Components

### 1. Base CLI Creation

Replace your current CLI setup with:

```python
from flext_cli.core import create_cli_group

# Instead of manually creating Click groups
cli, cli_instance = create_cli_group(
    name="Your CLI Name",
    version="1.0.0",
    description="Your CLI description",
)
```

### 2. Standard Options

Use the `@standard_options` decorator to add consistent options:

```python
from flext_cli.core import standard_options, handle_errors

@cli.command()
@standard_options  # Adds: --output, --quiet, --verbose, --debug, --no-color
@handle_errors     # Graceful error handling
@click.pass_context
def your_command(ctx, output, quiet, verbose, debug, no_color):
    cli = ctx.obj["cli"]
    # Your command logic
```

### 3. Output Formatting

Replace custom output logic with the formatter system:

```python
from flext_cli.core import FormatterFactory

# Instead of manual formatting
formatter = FormatterFactory.create(output)  # output from @standard_options
formatter.format(data, cli.console)

# Supports: table, json, yaml, csv, plain
```

### 4. Progress and Status Messages

Use built-in methods for consistent messaging:

```python
# Instead of print() or click.echo()
cli.print_success("Operation completed!")
cli.print_error("Something went wrong", exit_code=1)
cli.print_warning("This might cause issues")
cli.print_info("Processing data...")

# Progress bars
with cli.create_progress("Processing...") as progress:
    task = progress.add_task("Working", total=100)
    for i in range(100):
        progress.update(task, advance=1)
```

## Migration Examples

### Example 1: Argparse to FLEXT CLI

**Before (argparse):**

```python
import argparse

def main():
    parser = argparse.ArgumentParser(description="My CLI")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--output", choices=["json", "table"])

    subparsers = parser.add_subparsers(dest="command")

    list_parser = subparsers.add_parser("list")
    list_parser.add_argument("--filter")

    args = parser.parse_args()

    if args.command == "list":
        # List logic
        data = get_data(args.filter)
        if args.output == "json":
            print(json.dumps(data))
        else:
            print_table(data)
```

**After (FLEXT CLI):**

```python
from flext_cli.core import create_cli_group, standard_options, FormatterFactory

cli, cli_instance = create_cli_group("My CLI", "1.0.0", "My CLI description")

@cli.command()
@click.option("--filter", help="Filter results")
@standard_options
@click.pass_context
def list(ctx, filter, output, quiet, verbose, debug, no_color):
    cli = ctx.obj["cli"]

    # List logic
    data = get_data(filter)

    # Automatic formatting based on --output
    formatter = FormatterFactory.create(output)
    formatter.format(data, cli.console)
```

### Example 2: Simple Click to FLEXT CLI

**Before (basic Click):**

```python
import click
from rich.console import Console

console = Console()

@click.group()
@click.version_option("1.0.0")
def cli():
    """My CLI tool."""
    pass

@cli.command()
@click.option("--format", type=click.Choice(["json", "table"]), default="table")
def status(format):
    """Show status."""
    data = {"status": "running", "version": "1.0.0"}

    if format == "json":
        click.echo(json.dumps(data))
    else:
        console.print(data)
```

**After (FLEXT CLI):**

```python
from flext_cli.core import create_cli_group, standard_options, FormatterFactory

cli, cli_instance = create_cli_group("My CLI", "1.0.0", "My CLI tool")

@cli.command()
@standard_options
@click.pass_context
def status(ctx, output, quiet, verbose, debug, no_color):
    """Show status."""
    cli = ctx.obj["cli"]
    data = {"status": "running", "version": "1.0.0"}

    formatter = FormatterFactory.create(output)
    formatter.format(data, cli.console)
```

## Advanced Features

### Async Commands

```python
from flext_cli.core import async_command

@cli.command()
@async_command
async def fetch_data():
    """Async command example."""
    result = await some_async_operation()
    cli_instance.print_success(f"Fetched: {result}")
```

### Authentication Required

```python
from flext_cli.core import require_auth

@cli.command()
@require_auth()  # Checks ~/.flext/auth_token
def protected_command():
    """Command that requires authentication."""
    # Your protected logic
```

### Confirmation Prompts

```python
from flext_cli.core import confirm_action

@cli.command()
@confirm_action("This will delete all data. Continue?")
def dangerous_command():
    """Command with confirmation."""
    # Dangerous operation
```

### Configuration Management

```python
from flext_cli.core import ConfigManager

@cli.command()
def configure():
    """Configure the application."""
    config_mgr = ConfigManager()

    # Set values
    config_mgr.set_value("api.url", "https://api.example.com")
    config_mgr.set_value("api.timeout", 30)

    # Get values
    api_url = config_mgr.get_value("api.url")
```

### Interactive Input

```python
from flext_cli.core import CLIHelper

@cli.command()
def interactive():
    """Interactive command."""
    helper = CLIHelper(cli_instance.console)

    # Get input
    name = helper.prompt("Enter your name", default="User")

    # Select from list
    option = helper.select_from_list(
        ["option1", "option2", "option3"],
        "Choose an option"
    )

    # Confirm
    if helper.confirm("Proceed with these settings?"):
        cli_instance.print_success("Settings saved!")
```

## Custom Types

Use predefined parameter types:

```python
from flext_cli.core import FILE_PATH, DIRECTORY_PATH, POSITIVE_INT, URL

@cli.command()
@click.argument("config", type=FILE_PATH)
@click.option("--port", type=POSITIVE_INT, default=8080)
@click.option("--url", type=URL)
@click.option("--output-dir", type=DIRECTORY_PATH)
def process(config, port, url, output_dir):
    """Process with validated inputs."""
    # All inputs are pre-validated
```

## Testing

The framework is designed to be easily testable:

```python
from click.testing import CliRunner
from your_cli import cli

def test_command():
    runner = CliRunner()
    result = runner.invoke(cli, ["list", "--output", "json"])
    assert result.exit_code == 0
    assert "expected_data" in result.output
```

## Benefits of Migration

1. **Consistency**: All CLIs look and behave the same way
2. **Rich Output**: Beautiful tables, colors, and progress bars
3. **Multiple Formats**: Built-in support for table, JSON, YAML, CSV, plain
4. **Error Handling**: Graceful error messages and exit codes
5. **Standard Options**: Common options work the same everywhere
6. **Less Code**: Remove boilerplate formatting and option handling
7. **Better UX**: Consistent user experience across all tools

## Migration Checklist

- [ ] Add `flext-cli` dependency
- [ ] Replace CLI initialization with `create_cli_group`
- [ ] Add `@standard_options` to commands needing output formatting
- [ ] Replace print/echo with `cli.print_*` methods
- [ ] Replace custom formatting with `FormatterFactory`
- [ ] Add `@handle_errors` for graceful error handling
- [ ] Update tests to use new structure
- [ ] Remove redundant formatting code
- [ ] Test all output formats work correctly
