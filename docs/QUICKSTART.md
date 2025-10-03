# FLEXT-CLI Quick Start Guide

**Get started with flext-cli Phase 1 in 5 minutes!**

---

## Installation

```bash
pip install flext-cli
# or with poetry
poetry add flext-cli
```

---

## Basic Usage

### Option 1: Unified API (Recommended)

Single import for everything:

```python
from flext_cli import FlextCli

# Create CLI instance
cli = FlextCli()

# Access all functionality through unified API
cli.click      # Click abstraction
cli.formatters # Rich abstraction
cli.tables     # Tabulate integration
cli.main       # Command registration
```

### Option 2: Direct Component Access

Import specific components:

```python
from flext_cli import (
    FlextCliClick,      # Click abstraction
    FlextCliFormatters, # Rich abstraction
    FlextCliTables,     # Tabulate integration
    FlextCliMain,       # Command registration
)
```

---

## Quick Examples

### 1. Create Commands (NO Click imports!)

```python
from flext_cli import FlextCli

cli = FlextCli()

# Register a command
@cli.main.command()
def hello(name: str = "World"):
    """Say hello to someone."""
    print(f"Hello, {name}!")

# Register a command group
@cli.main.group()
def config():
    """Configuration commands."""
    pass

@config.command()
def show():
    """Show configuration."""
    print("Current config...")
```

**ZERO TOLERANCE**: No need to `import click` - everything through flext-cli!

### 2. Rich Output (NO Rich imports!)

```python
from flext_cli import FlextCli

cli = FlextCli()

# Create a beautiful panel
panel_result = cli.formatters.create_panel(
    content="Important message!",
    title="Alert",
    border_style="red"
)
if panel_result.is_success:
    cli.formatters.print_rich(renderable=panel_result.unwrap())

# Print styled text
cli.formatters.print_rich(
    text="Success!",
    style="bold green"
)

# Create a progress bar
progress_result = cli.formatters.create_progress()
if progress_result.is_success:
    progress = progress_result.unwrap()
    # Use progress...
```

**ZERO TOLERANCE**: No need to `import rich` - everything through flext-cli!

### 3. Tables (Multiple Formats!)

```python
from flext_cli import FlextCli

cli = FlextCli()

data = [
    {"Name": "Alice", "Age": 30, "City": "NYC"},
    {"Name": "Bob", "Age": 25, "City": "LA"},
]

# ASCII table (fast, plain text)
table_result = cli.tables.create_grid_table(data, fancy=True)
if table_result.is_success:
    print(table_result.unwrap())

# Markdown table
markdown_result = cli.tables.create_markdown_table(data)
if markdown_result.is_success:
    print(markdown_result.unwrap())

# HTML table
html_result = cli.tables.create_html_table(data)
if html_result.is_success:
    print(html_result.unwrap())

# 22+ formats available!
print(f"Available: {cli.tables.list_formats()}")
```

### 4. Complete CLI Application

```python
from flext_cli import FlextCli

cli = FlextCli()

@cli.main.command()
def greet(name: str = "World"):
    """Greet someone with styled output."""
    # Create panel
    panel_result = cli.formatters.create_panel(
        content=f"Hello, {name}!",
        title="Greeting",
        border_style="green"
    )
    if panel_result.is_success:
        cli.formatters.print_rich(renderable=panel_result.unwrap())

@cli.main.group()
def data():
    """Data commands."""
    pass

@data.command()
def list_items():
    """List data items."""
    items = [
        {"ID": 1, "Name": "Item 1"},
        {"ID": 2, "Name": "Item 2"},
    ]

    # Display as table
    table_result = cli.tables.create_grid_table(items)
    if table_result.is_success:
        print(table_result.unwrap())

# Execute CLI
if __name__ == "__main__":
    result = cli.main.execute_cli()
```

---

## FlextResult Pattern

All operations return `FlextResult` for type-safe error handling:

```python
from flext_cli import FlextCli

cli = FlextCli()

# Create something
result = cli.formatters.create_panel(content="Test")

# Check success
if result.is_success:
    panel = result.unwrap()  # Safe to unwrap
    cli.formatters.print_rich(renderable=panel)
else:
    print(f"Error: {result.error}")  # Handle error

# Or check failure
if result.is_failure:
    print(f"Failed: {result.error}")
```

**Benefits**:

- Type-safe error handling
- No exceptions to catch
- Explicit success/failure checking
- Railway-oriented programming

---

## Common Patterns

### Pattern 1: Click Command with Options

```python
from flext_cli import FlextCliClick

click = FlextCliClick()

# Create command decorator
cmd_result = click.create_command_decorator(name="process")
if cmd_result.is_success:
    command = cmd_result.unwrap()

# Create option decorator
opt_result = click.create_option_decorator(
    "--input", "-i",
    type=str,
    required=True,
    help="Input file"
)
if opt_result.is_success:
    option = opt_result.unwrap()
```

### Pattern 2: Rich Panel with Markdown

```python
from flext_cli import FlextCliFormatters

formatters = FlextCliFormatters()

# Render markdown
markdown_result = formatters.render_markdown("""
# Title
- Item 1
- Item 2
""")

# Put in panel
if markdown_result.is_success:
    panel_result = formatters.create_panel(
        content=markdown_result.unwrap(),
        title="Documentation",
        border_style="blue"
    )
    if panel_result.is_success:
        formatters.print_rich(renderable=panel_result.unwrap())
```

### Pattern 3: Multiple Table Formats

```python
from flext_cli import FlextCliTables

tables = FlextCliTables()

data = [{"col1": "val1", "col2": "val2"}]

# Try different formats
for format_type in ["simple", "grid", "fancy_grid", "pipe"]:
    result = tables.create_table(data, format=format_type)
    if result.is_success:
        print(f"\n{format_type.upper()}:")
        print(result.unwrap())
```

---

## Best Practices

### ✅ DO

```python
# Use unified API
from flext_cli import FlextCli
cli = FlextCli()

# Use FlextResult pattern
result = cli.formatters.create_panel(content="Test")
if result.is_success:
    panel = result.unwrap()

# Use appropriate table format
# - Rich tables: Interactive, colored
# - Tabulate: Plain text, performance
```

### ❌ DON'T

```python
# Don't import Click directly
import click  # ❌ FORBIDDEN - use FlextCliClick

# Don't import Rich directly
from rich import print  # ❌ FORBIDDEN - use FlextCliFormatters

# Don't ignore FlextResult
result = cli.formatters.create_panel(content="Test")
panel = result.unwrap()  # ❌ Check is_success first!
```

---

## Next Steps

1. **Run the demo**: `python examples/phase1_complete_demo.py`
2. **Read the docs**: Check `docs/` for detailed patterns
3. **Explore examples**: See `examples/` for more use cases
4. **Check API reference**: See component docstrings

---

## Getting Help

- **Documentation**: `docs/TRANSFORMATION_PLAN.md`
- **Examples**: `examples/phase1_complete_demo.py`
- **Source**: Browse `src/flext_cli/` for implementation
- **Issues**: Report at GitHub

---

## Key Concepts

### ZERO TOLERANCE

**flext-cli enforces ZERO TOLERANCE for direct Click/Rich imports:**

- ✅ Click functionality: Use `FlextCliClick` or `cli.click`
- ✅ Rich functionality: Use `FlextCliFormatters` or `cli.formatters`
- ✅ Tables: Use `FlextCliTables` or `cli.tables`
- ✅ Commands: Use `FlextCliMain` or `cli.main`

**Benefits**:

- Consistent API across ecosystem
- Type-safe abstractions
- Easier testing and mocking
- Future-proof against library changes

### Component Architecture

```
FlextCli (Unified Facade)
├── click: FlextCliClick (Click abstraction)
├── formatters: FlextCliFormatters (Rich abstraction)
├── tables: FlextCliTables (Tabulate integration)
└── main: FlextCliMain (Command registration)
```

All components use `FlextResult` for consistent error handling.

---

**Ready to build amazing CLIs with flext-cli! 🚀**
