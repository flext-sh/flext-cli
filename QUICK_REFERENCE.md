# FLEXT CLI Framework - Quick Reference

## Basic Setup

```python
from flext_cli.core import create_cli_group, standard_options, handle_errors

# Create CLI
cli, cli_instance = create_cli_group("My CLI", "1.0.0", "Description")

# Basic command
@cli.command()
@standard_options
@handle_errors
@click.pass_context
def my_command(ctx, output, quiet, verbose, debug, no_color):
    cli = ctx.obj["cli"]
    # Your code here
```

## Common Imports

```python
from flext_cli.core import (
    # Core
    create_cli_group,
    BaseCLI,
    CLIConfig,

    # Decorators
    standard_options,
    handle_errors,
    async_command,
    require_auth,
    confirm_action,
    measure_time,
    with_spinner,

    # Formatters
    FormatterFactory,

    # Types
    FILE_PATH,
    DIRECTORY_PATH,
    POSITIVE_INT,
    URL,
    PORT,

    # Helpers
    CLIHelper,
    ConfigManager,
    ProgressManager,
)
```

## Standard Options

The `@standard_options` decorator adds:

- `--output/-o`: Output format (table/JSON/YAML/csv/plain)
- `--quiet/-q`: Suppress non-error output
- `--verbose/-v`: Verbose output
- `--debug`: Debug mode
- `--no-color`: Disable colors

## Output Methods

```python
# Status messages
cli.print_success("Operation completed!")
cli.print_error("Error occurred", exit_code=1)
cli.print_warning("Warning message")
cli.print_info("Information")

# Headers
cli.print_header()  # Shows app name and version
```

## Formatting Output

```python
# Auto-format based on --output option
formatter = FormatterFactory.create(output)
formatter.format(data, cli.console)

# Supports any data structure:
# - List of dicts → Table with columns
# - Single dict → Vertical key-value table
# - List → Simple list
# - Any → String representation
```

## Progress Tracking

```python
# Simple progress
with cli.create_progress("Processing...") as progress:
    task = progress.add_task("Working", total=100)
    for i in range(100):
        progress.update(task, advance=1)

# Multi-task progress
with ProgressManager(cli.console) as pm:
    main = pm.add_task("Main task", total=10)
    sub = pm.add_task("Subtask", total=100)

    for i in range(10):
        pm.update(sub, description=f"Item {i}", completed=0)
        for j in range(100):
            pm.update(sub, advance=1)
        pm.update(main, advance=1)
```

## Interactive Input

```python
helper = CLIHelper(cli.console)

# Text input
name = helper.prompt("Enter name", default="User")
password = helper.prompt("Password", password=True)

# Selection
choice = helper.select_from_list(
    ["option1", "option2"],
    "Select option"
)

# Confirmation
if helper.confirm("Continue?", default=False):
    # Proceed
```

## Configuration

```python
config = ConfigManager()

# Set nested values
config.set_value("api.url", "https://api.example.com")
config.set_value("api.token", "secret")

# Get values
url = config.get_value("api.url")
all_config = config.load_config()

# Delete values
config.delete_value("api.token")
```

## Async Commands

```python
@cli.command()
@async_command
async def fetch():
    result = await some_async_operation()
    cli_instance.print_success(f"Result: {result}")
```

## Authentication

```python
# Require auth token
@cli.command()
@require_auth()
def protected():
    ctx = click.get_current_context()
    token = ctx.obj["auth_token"]  # Auto-loaded
```

## Custom Parameter Types

```python
@cli.command()
@click.argument("config", type=FILE_PATH)
@click.option("--port", type=POSITIVE_INT)
@click.option("--api", type=URL)
@click.option("--output", type=DIRECTORY_PATH)
def process(config, port, api, output):
    # All parameters are pre-validated
```

## Error Handling

```python
# Automatic with @handle_errors
@cli.command()
@handle_errors
def risky():
    raise ValueError("Something went wrong")
    # Shows: Error: Something went wrong
    # Exit code: 1

# Manual
try:
    risky_operation()
except Exception as e:
    cli.print_error(str(e), exit_code=1)
```

## Tables and Trees

```python
# Table
table = cli.create_table("Title", [
    ("Column 1", "cyan"),
    ("Column 2", "green"),
])
table.add_row("Value 1", "Value 2")
cli.console.print(table)

# Tree
tree = cli.create_tree("Root")
child = tree.add("Child 1")
child.add("Subchild")
cli.console.print(tree)
```

## Complete Example

```python
from flext_cli.core import (
    create_cli_group,
    standard_options,
    handle_errors,
    FormatterFactory,
    require_auth,
    measure_time,
)

cli, cli_instance = create_cli_group(
    "Example CLI",
    "1.0.0",
    "A complete example"
)

@cli.command()
@standard_options
@handle_errors
@require_auth()
@measure_time()
@click.argument("name")
@click.option("--count", type=POSITIVE_INT, default=1)
@click.pass_context
def process(ctx, name, count, output, quiet, verbose, debug, no_color):
    """Process items with authentication."""
    cli = ctx.obj["cli"]

    # Progress
    with cli.create_progress(f"Processing {name}...") as progress:
        task = progress.add_task("Items", total=count)

        results = []
        for i in range(count):
            # Process item
            result = {"id": i, "name": f"{name}_{i}", "status": "ok"}
            results.append(result)
            progress.update(task, advance=1)

    # Output results
    formatter = FormatterFactory.create(output)
    formatter.format(results, cli.console)

    cli.print_success(f"Processed {count} items!")

if __name__ == "__main__":
    cli()
```
