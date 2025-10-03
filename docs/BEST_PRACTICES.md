# FLEXT-CLI Best Practices Guide

**Professional patterns for building CLIs with flext-cli**

---

## Core Principles

### 1. ZERO TOLERANCE Enforcement

**Always use flext-cli abstractions - NEVER import Click/Rich directly!**

```python
# ✅ CORRECT
from flext_cli import FlextCli

cli = FlextCli()
cli.click      # For Click functionality
cli.formatters # For Rich functionality
cli.tables     # For Tabulate functionality
cli.main       # For command registration

# ❌ WRONG - FORBIDDEN
import click         # ❌ Use FlextCliClick
from rich import *   # ❌ Use FlextCliFormatters
import tabulate      # ❌ Use FlextCliTables
```

**Why?**

- Maintains consistency across ecosystem
- Provides type safety via FlextResult
- Protects from upstream breaking changes
- Enables easier testing and mocking

---

## FlextResult Pattern

### Always Check Success

```python
# ✅ CORRECT - Check before unwrap
result = cli.formatters.create_panel(content="Test")
if result.is_success:
    panel = result.unwrap()
    cli.formatters.print_rich(renderable=panel)
else:
    print(f"Error: {result.error}")

# ❌ WRONG - Don't unwrap without checking
result = cli.formatters.create_panel(content="Test")
panel = result.unwrap()  # ❌ May fail if result has error!
```

### Early Returns for Failures

```python
# ✅ CORRECT - Early return pattern
def process_data(data: dict) -> FlextResult[str]:
    """Process data with early returns."""
    # Validate
    if not data:
        return FlextResult[str].fail("Data cannot be empty")

    # Process
    table_result = cli.tables.create_table(data)
    if table_result.is_failure:
        return FlextResult[str].fail(f"Table creation failed: {table_result.error}")

    # Success
    return FlextResult[str].ok(table_result.unwrap())
```

### Chaining Operations

```python
# ✅ CORRECT - Chain with checks
def create_styled_output(text: str) -> FlextResult[None]:
    """Create styled panel output."""
    # Create markdown
    markdown_result = cli.formatters.render_markdown(f"**{text}**")
    if markdown_result.is_failure:
        return FlextResult[None].fail(f"Markdown failed: {markdown_result.error}")

    # Create panel
    panel_result = cli.formatters.create_panel(
        content=markdown_result.unwrap(),
        title="Output",
        border_style="green"
    )
    if panel_result.is_failure:
        return FlextResult[None].fail(f"Panel failed: {panel_result.error}")

    # Print
    cli.formatters.print_rich(renderable=panel_result.unwrap())
    return FlextResult[None].ok(None)
```

---

## Command Organization

### Use Unified API

```python
# ✅ CORRECT - Single entry point
from flext_cli import FlextCli

cli = FlextCli()

@cli.main.command()
def command1():
    """First command."""
    pass

@cli.main.group()
def group1():
    """Command group."""
    pass

@group1.command()
def subcommand():
    """Subcommand."""
    pass
```

### Group Related Commands

```python
# ✅ CORRECT - Logical grouping
from flext_cli import FlextCli

cli = FlextCli()

# Data commands
@cli.main.group()
def data():
    """Data management commands."""
    pass

@data.command()
def list_items():
    """List all data items."""
    pass

@data.command()
def export():
    """Export data."""
    pass

# Config commands
@cli.main.group()
def config():
    """Configuration commands."""
    pass

@config.command()
def show():
    """Show configuration."""
    pass

@config.command()
def update():
    """Update configuration."""
    pass
```

### Use Type Hints

```python
# ✅ CORRECT - Full type hints
from flext_cli import FlextCli
from flext_core import FlextResult

cli = FlextCli()

@cli.main.command()
def greet(name: str = "World", count: int = 1) -> FlextResult[None]:
    """Greet someone."""
    for _ in range(count):
        cli.formatters.print_rich(
            text=f"Hello, {name}!",
            style="bold green"
        )
    return FlextResult[None].ok(None)
```

---

## Output Formatting

### Choose the Right Tool

**Use Rich (FlextCliFormatters) for:**

- Interactive terminals
- Colored output
- Visual styling (panels, borders)
- Progress bars
- Live updates

```python
# ✅ Rich for interactive display
cli.formatters.create_panel(
    content="Interactive output",
    border_style="blue"
)
```

**Use Tabulate (FlextCliTables) for:**

- Plain text output
- Log files
- Performance-critical scenarios
- Large datasets
- Markdown/HTML generation

```python
# ✅ Tabulate for plain text
cli.tables.create_grid_table(data, format="grid")
```

### Consistent Styling

```python
# ✅ CORRECT - Define style constants
class OutputStyles:
    """Consistent output styles."""
    SUCCESS = "bold green"
    ERROR = "bold red"
    WARNING = "bold yellow"
    INFO = "bold blue"

# Use throughout application
cli.formatters.print_rich(
    text="Operation successful!",
    style=OutputStyles.SUCCESS
)

cli.formatters.print_rich(
    text="Warning: Check configuration",
    style=OutputStyles.WARNING
)
```

### Table Format Selection

```python
# ✅ CORRECT - Match format to context
class TableFormats:
    """Standard table formats for different contexts."""

    @staticmethod
    def for_terminal(data: list) -> str:
        """Rich colors for terminal."""
        result = cli.formatters.create_rich_table(
            data=data,
            show_header=True
        )
        return result.unwrap() if result.is_success else ""

    @staticmethod
    def for_logs(data: list) -> str:
        """Plain ASCII for logs."""
        result = cli.tables.create_simple_table(data)
        return result.unwrap() if result.is_success else ""

    @staticmethod
    def for_markdown(data: list) -> str:
        """Markdown pipe tables."""
        result = cli.tables.create_markdown_table(data)
        return result.unwrap() if result.is_success else ""
```

---

## Error Handling

### Provide Context

```python
# ✅ CORRECT - Descriptive errors
def load_config(path: str) -> FlextResult[dict]:
    """Load configuration file."""
    if not path:
        return FlextResult[dict].fail(
            "Configuration path cannot be empty. "
            "Please provide a valid file path."
        )

    # More processing...
    return FlextResult[dict].ok(config_data)
```

### Handle Errors Gracefully

```python
# ✅ CORRECT - User-friendly error display
def display_error(error_msg: str) -> None:
    """Display error with styling."""
    panel_result = cli.formatters.create_panel(
        content=f"❌ {error_msg}",
        title="Error",
        border_style="red"
    )
    if panel_result.is_success:
        cli.formatters.print_rich(renderable=panel_result.unwrap())
    else:
        # Fallback
        print(f"Error: {error_msg}")

# Usage
result = some_operation()
if result.is_failure:
    display_error(result.error)
```

### Log Errors

```python
# ✅ CORRECT - Log for debugging
from flext_core import FlextLogger

logger = FlextLogger(__name__)

def process_with_logging() -> FlextResult[None]:
    """Process with logging."""
    result = cli.tables.create_table(data)

    if result.is_failure:
        logger.error(f"Table creation failed: {result.error}")
        return FlextResult[None].fail("Processing failed")

    logger.info("Table created successfully")
    return FlextResult[None].ok(None)
```

---

## Testing

### Test Commands

```python
# ✅ CORRECT - Test CLI commands
def test_hello_command():
    """Test hello command."""
    cli = FlextCli()

    # Create test runner
    runner_result = cli.click.create_cli_runner()
    assert runner_result.is_success

    runner = runner_result.unwrap()

    # Get command
    cmd_result = cli.main.get_command("hello")
    assert cmd_result.is_success

    # Test command
    # result = runner.invoke(cmd_result.unwrap(), ['--name', 'Alice'])
    # assert result.exit_code == 0
```

### Mock FlextResult

```python
# ✅ CORRECT - Mock FlextResult returns
from unittest.mock import Mock, patch
from flext_core import FlextResult

def test_with_mock():
    """Test with mocked FlextResult."""
    mock_result = FlextResult[str].ok("test data")

    with patch.object(cli.tables, 'create_table', return_value=mock_result):
        result = cli.tables.create_table([{"key": "value"}])
        assert result.is_success
        assert result.unwrap() == "test data"
```

### Integration Tests

```python
# ✅ CORRECT - Test full workflows
def test_data_display_workflow():
    """Test complete data display workflow."""
    cli = FlextCli()

    # Prepare data
    data = [{"id": 1, "name": "Test"}]

    # Test table creation
    table_result = cli.tables.create_grid_table(data)
    assert table_result.is_success

    # Test markdown creation
    markdown_result = cli.tables.create_markdown_table(data)
    assert markdown_result.is_success

    # Test Rich table creation
    rich_result = cli.formatters.create_rich_table(data)
    assert rich_result.is_success
```

---

## Performance

### Prefer Tabulate for Large Datasets

```python
# ✅ CORRECT - Tabulate for performance
def display_large_dataset(data: list) -> None:
    """Display large dataset efficiently."""
    if len(data) > 1000:
        # Use Tabulate (faster, no ANSI codes)
        result = cli.tables.create_simple_table(data)
    else:
        # Use Rich (prettier, interactive)
        result = cli.formatters.create_rich_table(data)

    if result.is_success:
        print(result.unwrap())
```

### Lazy Evaluation

```python
# ✅ CORRECT - Lazy table generation
def generate_report(data: list, format: str) -> FlextResult[str]:
    """Generate report in specified format."""
    # Only format if needed
    if format == "markdown":
        return cli.tables.create_markdown_table(data)
    elif format == "html":
        return cli.tables.create_html_table(data)
    else:
        return cli.tables.create_simple_table(data)
```

### Reuse Components

```python
# ✅ CORRECT - Reuse CLI instance
class MyApplication:
    """Application with CLI."""

    def __init__(self):
        # Single CLI instance
        self.cli = FlextCli()

    def display_data(self, data: list):
        """Display data using shared CLI."""
        result = self.cli.tables.create_grid_table(data)
        if result.is_success:
            print(result.unwrap())

    def show_progress(self, total: int):
        """Show progress using shared CLI."""
        progress_result = self.cli.formatters.create_progress()
        if progress_result.is_success:
            progress = progress_result.unwrap()
            # Use progress...
```

---

## Code Organization

### Module Structure

```python
# ✅ CORRECT - Organized module structure
# myapp/
#   __init__.py
#   cli.py          # CLI setup
#   commands/
#     __init__.py
#     data.py       # Data commands
#     config.py     # Config commands
#   formatters/
#     __init__.py
#     output.py     # Output helpers
#     styles.py     # Style constants

# myapp/cli.py
from flext_cli import FlextCli

cli = FlextCli()

# myapp/commands/data.py
from myapp.cli import cli

@cli.main.group()
def data():
    """Data commands."""
    pass

@data.command()
def list_items():
    """List items."""
    pass
```

### Separation of Concerns

```python
# ✅ CORRECT - Separate business logic from CLI
# business.py - Business logic
from flext_core import FlextResult

class DataService:
    """Business logic."""

    def get_items(self) -> FlextResult[list]:
        """Get items."""
        # Business logic here
        return FlextResult[list].ok([{"id": 1}])

# cli.py - CLI interface
from flext_cli import FlextCli
from myapp.business import DataService

cli = FlextCli()
service = DataService()

@cli.main.command()
def list_items():
    """List items command."""
    result = service.get_items()
    if result.is_success:
        table_result = cli.tables.create_grid_table(result.unwrap())
        if table_result.is_success:
            print(table_result.unwrap())
```

---

## Documentation

### Document Commands

```python
# ✅ CORRECT - Comprehensive docstrings
@cli.main.command()
def process(
    input_file: str,
    output_format: str = "json",
    verbose: bool = False
) -> FlextResult[None]:
    """Process input file and generate output.

    Args:
        input_file: Path to input file (required)
        output_format: Output format (json, yaml, csv). Default: json
        verbose: Enable verbose output. Default: False

    Returns:
        FlextResult[None]: Success or error result

    Examples:
        $ myapp process data.csv
        $ myapp process data.csv --output-format yaml
        $ myapp process data.csv --verbose

    """
    # Implementation...
    return FlextResult[None].ok(None)
```

### Use Type Hints

```python
# ✅ CORRECT - Complete type annotations
from flext_cli import FlextCli
from flext_core import FlextResult

def format_output(
    data: list[dict[str, str | int]],
    style: str = "grid"
) -> FlextResult[str]:
    """Format data with type safety.

    Args:
        data: List of dictionaries with string/int values
        style: Table style (grid, simple, fancy_grid)

    Returns:
        FlextResult[str]: Formatted table or error

    """
    cli = FlextCli()
    return cli.tables.create_table(data, format=style)
```

---

## Common Pitfalls

### ❌ Don't: Direct Click/Rich Imports

```python
# ❌ WRONG
import click
from rich import print

# ✅ CORRECT
from flext_cli import FlextCli
cli = FlextCli()
```

### ❌ Don't: Unwrap Without Checking

```python
# ❌ WRONG
result = cli.formatters.create_panel(content="Test")
panel = result.unwrap()  # May crash!

# ✅ CORRECT
result = cli.formatters.create_panel(content="Test")
if result.is_success:
    panel = result.unwrap()
```

### ❌ Don't: Ignore Errors

```python
# ❌ WRONG
result = some_operation()
# Ignore result, continue

# ✅ CORRECT
result = some_operation()
if result.is_failure:
    logger.error(f"Operation failed: {result.error}")
    return FlextResult[None].fail("Processing failed")
```

### ❌ Don't: Mix Direct and Wrapper APIs

```python
# ❌ WRONG
from rich.console import Console
from flext_cli import FlextCli

console = Console()  # Direct Rich
cli = FlextCli()     # Wrapper

# ✅ CORRECT - Use wrapper exclusively
from flext_cli import FlextCli
cli = FlextCli()
```

---

## Summary

### Key Takeaways

1. **ZERO TOLERANCE**: Never import Click/Rich directly
2. **FlextResult**: Always check `is_success` before `unwrap()`
3. **Unified API**: Use `FlextCli()` for all functionality
4. **Right Tool**: Rich for interactive, Tabulate for performance
5. **Type Safety**: Use type hints throughout
6. **Error Handling**: Provide context and log errors
7. **Testing**: Test commands and mock FlextResult
8. **Organization**: Separate concerns and document well

### Quick Reference

```python
from flext_cli import FlextCli

cli = FlextCli()

# Commands
@cli.main.command()
def cmd(): pass

# Click features
cli.click.create_command_decorator()

# Rich features
cli.formatters.print_rich()

# Tables
cli.tables.create_grid_table()

# Always check results
if result.is_success:
    data = result.unwrap()
```

---

**Build professional CLIs with flext-cli! 🚀**
