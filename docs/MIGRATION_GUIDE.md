# Migration Guide: Click/Rich → flext-cli

**Migrate from direct Click/Rich usage to flext-cli abstractions**

---

## Why Migrate

### Benefits of flext-cli Abstractions

✅ **ZERO TOLERANCE**: No direct Click/Rich imports needed
✅ **Type Safety**: FlextResult-based error handling
✅ **Unified API**: Single entry point for all CLI functionality
✅ **Future-Proof**: Protected from upstream library changes
✅ **Testability**: Easier mocking and testing
✅ **Consistency**: Standardized patterns across ecosystem

---

## Migration Strategy

### Step 1: Install flext-cli

```bash
pip install flext-cli
# or
poetry add flext-cli
```

### Step 2: Replace Imports

```python
# ❌ BEFORE (Direct Click/Rich)
import click
from rich.console import Console
from rich.table import Table

# ✅ AFTER (flext-cli)
from flext_cli import FlextCli

cli = FlextCli()
# Access: cli.click, cli.formatters, cli.tables, cli.main
```

### Step 3: Migrate Code Patterns

Use the migration patterns below for each scenario.

---

## Click Migration

### Commands

#### Before (Direct Click)

```python
import click

@click.command()
@click.option('--name', default='World', help='Name to greet')
def hello(name):
    """Say hello."""
    print(f'Hello {name}!')

if __name__ == '__main__':
    hello()
```

#### After (flext-cli)

```python
from flext_cli import FlextCli

cli = FlextCli()

@cli.main.command()
def hello(name: str = 'World'):
    """Say hello."""
    print(f'Hello {name}!')

if __name__ == '__main__':
    result = cli.main.execute_cli()
```

**Changes**:

- Replace `@click.command()` with `@cli.main.command()`
- Remove `@click.option()` (handled by function signature)
- Use `cli.main.execute_cli()` instead of calling function

---

### Command Groups

#### Before (Direct Click)

```python
import click

@click.group()
def cli():
    """Main CLI."""
    pass

@cli.command()
def init():
    """Initialize."""
    print('Initializing...')

@cli.command()
def run():
    """Run."""
    print('Running...')

if __name__ == '__main__':
    cli()
```

#### After (flext-cli)

```python
from flext_cli import FlextCli

cli = FlextCli()

@cli.main.group()
def myapp():
    """Main CLI."""
    pass

@myapp.command()
def init():
    """Initialize."""
    print('Initializing...')

@myapp.command()
def run():
    """Run."""
    print('Running...')

if __name__ == '__main__':
    result = cli.main.execute_cli()
```

**Changes**:

- Replace `@click.group()` with `@cli.main.group()`
- Add commands to group with `@group_name.command()`
- Use FlextResult pattern for error handling

---

### Options and Arguments

#### Before (Direct Click)

```python
import click

@click.command()
@click.option('--count', '-c', default=1, help='Number of greetings')
@click.option('--name', prompt='Your name', help='The person to greet')
@click.argument('out', type=click.File('w'), default='-')
def hello(count, name, out):
    """Say hello."""
    for _ in range(count):
        click.echo(f'Hello {name}!', file=out)
```

#### After (flext-cli)

```python
from flext_cli import FlextCli

cli = FlextCli()

# Create option decorators programmatically
count_opt_result = cli.click.create_option_decorator(
    '--count', '-c',
    default=1,
    help='Number of greetings'
)

name_opt_result = cli.click.create_option_decorator(
    '--name',
    prompt='Your name',
    help='The person to greet'
)

# Or use function signature with defaults
@cli.main.command()
def hello(count: int = 1, name: str = "World"):
    """Say hello."""
    for _ in range(count):
        print(f'Hello {name}!')
```

**Changes**:

- Use `cli.click.create_option_decorator()` for options
- Or leverage function signatures with type hints
- Use FlextResult pattern for error handling

---

### Parameter Types

#### Before (Direct Click)

```python
import click

@click.command()
@click.option('--color', type=click.Choice(['red', 'green', 'blue']))
@click.option('--path', type=click.Path(exists=True))
@click.option('--count', type=click.IntRange(1, 100))
def process(color, path, count):
    """Process with types."""
    pass
```

#### After (flext-cli)

```python
from flext_cli import FlextCli

cli = FlextCli()

# Get parameter types from Click wrapper
choice_type = cli.click.get_choice_type(['red', 'green', 'blue'])
path_type = cli.click.get_path_type(exists=True)
int_range_type = cli.click.get_int_range_type(min=1, max=100)

# Create options with types
color_opt = cli.click.create_option_decorator(
    '--color',
    type=choice_type
)

@cli.main.command()
def process(color: str, path: str, count: int):
    """Process with types."""
    pass
```

**Changes**:

- Use `cli.click.get_*_type()` methods
- Pass types to option decorators
- Maintain type safety with FlextResult

---

## Rich Migration

### Console Printing

#### Before (Direct Rich)

```python
from rich.console import Console

console = Console()
console.print("Hello", style="bold red")
console.print("[bold blue]Styled text[/bold blue]")
```

#### After (flext-cli)

```python
from flext_cli import FlextCli

cli = FlextCli()

cli.formatters.print_rich(
    text="Hello",
    style="bold red"
)
cli.formatters.print_rich(
    text="[bold blue]Styled text[/bold blue]"
)
```

**Changes**:

- Replace `console.print()` with `cli.formatters.print_rich()`
- Use FlextResult for error handling
- Same Rich markup syntax works!

---

### Panels

#### Before (Direct Rich)

```python
from rich.console import Console
from rich.panel import Panel

console = Console()
panel = Panel("Content", title="Title", border_style="blue")
console.print(panel)
```

#### After (flext-cli)

```python
from flext_cli import FlextCli

cli = FlextCli()

panel_result = cli.formatters.create_panel(
    content="Content",
    title="Title",
    border_style="blue"
)
if panel_result.is_success:
    cli.formatters.print_rich(renderable=panel_result.unwrap())
```

**Changes**:

- Use `cli.formatters.create_panel()`
- Check `is_success` before using
- Same Rich styling options

---

### Tables

#### Before (Direct Rich)

```python
from rich.console import Console
from rich.table import Table

console = Console()
table = Table(title="Data")
table.add_column("Name")
table.add_column("Age")
table.add_row("Alice", "30")
console.print(table)
```

#### After (flext-cli)

```python
from flext_cli import FlextCli

cli = FlextCli()

# Option 1: Rich table (colored, styled)
table_result = cli.formatters.create_table(title="Data")
if table_result.is_success:
    table = table_result.unwrap()
    cli.formatters.add_table_column(table, "Name")
    cli.formatters.add_table_column(table, "Age")
    cli.formatters.add_table_row(table, "Alice", "30")
    cli.formatters.print_rich(renderable=table)

# Option 2: ASCII table (plain text, fast)
data = [{"Name": "Alice", "Age": 30}]
ascii_result = cli.tables.create_grid_table(data)
if ascii_result.is_success:
    print(ascii_result.unwrap())
```

**Changes**:

- Use `cli.formatters.create_table()` for Rich tables
- Or use `cli.tables.*` for ASCII tables
- FlextResult error handling

---

### Progress Bars

#### Before (Direct Rich)

```python
from rich.progress import Progress

with Progress() as progress:
    task = progress.add_task("Processing...", total=100)
    for i in range(100):
        # Do work
        progress.update(task, advance=1)
```

#### After (flext-cli)

```python
from flext_cli import FlextCli

cli = FlextCli()

progress_result = cli.formatters.create_progress()
if progress_result.is_success:
    progress = progress_result.unwrap()
    with progress:
        task = progress.add_task("Processing...", total=100)
        for i in range(100):
            # Do work
            progress.update(task, advance=1)
```

**Changes**:

- Use `cli.formatters.create_progress()`
- Check FlextResult success
- Same Rich Progress API

---

### Markdown Rendering

#### Before (Direct Rich)

```python
from rich.console import Console
from rich.markdown import Markdown

console = Console()
md = Markdown("# Title\n- Item 1")
console.print(md)
```

#### After (flext-cli)

```python
from flext_cli import FlextCli

cli = FlextCli()

markdown_result = cli.formatters.render_markdown("# Title\n- Item 1")
if markdown_result.is_success:
    cli.formatters.print_rich(renderable=markdown_result.unwrap())
```

**Changes**:

- Use `cli.formatters.render_markdown()`
- FlextResult pattern
- Same markdown syntax

---

### Syntax Highlighting

#### Before (Direct Rich)

```python
from rich.console import Console
from rich.syntax import Syntax

console = Console()
code = 'def hello():\n    print("Hello")'
syntax = Syntax(code, "python", theme="monokai")
console.print(syntax)
```

#### After (flext-cli)

```python
from flext_cli import FlextCli

cli = FlextCli()

code_result = cli.formatters.highlight_code(
    code='def hello():\n    print("Hello")',
    language="python",
    theme="monokai"
)
if code_result.is_success:
    cli.formatters.print_rich(renderable=code_result.unwrap())
```

**Changes**:

- Use `cli.formatters.highlight_code()`
- FlextResult pattern
- Same themes and languages

---

## Common Migration Patterns

### Pattern 1: Error Handling

#### Before

```python
try:
    result = some_operation()
    print(result)
except Exception as e:
    print(f"Error: {e}")
```

#### After

```python
result = some_operation()  # Returns FlextResult
if result.is_success:
    data = result.unwrap()
    print(data)
else:
    print(f"Error: {result.error}")
```

---

### Pattern 2: CLI with Rich Output

#### Before

```python
import click
from rich.console import Console

console = Console()

@click.command()
def hello(name):
    console.print(f"[bold green]Hello {name}![/bold green]")
```

#### After

```python
from flext_cli import FlextCli

cli = FlextCli()

@cli.main.command()
def hello(name: str = "World"):
    cli.formatters.print_rich(
        text=f"Hello {name}!",
        style="bold green"
    )
```

---

### Pattern 3: Testing

#### Before

```python
from click.testing import CliRunner

def test_hello():
    runner = CliRunner()
    result = runner.invoke(hello, ['--name', 'Alice'])
    assert result.exit_code == 0
```

#### After

```python
from flext_cli import FlextCli

def test_hello():
    cli = FlextCli()
    runner_result = cli.click.create_cli_runner()
    if runner_result.is_success:
        runner = runner_result.unwrap()
        # Get command and test...
```

---

## Migration Checklist

### Pre-Migration

- [ ] Audit all direct Click imports
- [ ] Audit all direct Rich imports
- [ ] List all Click parameter types used
- [ ] List all Rich components used
- [ ] Identify command structure (groups, subcommands)

### During Migration

- [ ] Replace Click imports with `FlextCliClick` or `cli.click`
- [ ] Replace Rich imports with `FlextCliFormatters` or `cli.formatters`
- [ ] Update command decorators
- [ ] Convert to FlextResult pattern
- [ ] Update error handling
- [ ] Migrate tests

### Post-Migration

- [ ] Remove all direct Click imports
- [ ] Remove all direct Rich imports
- [ ] Verify ZERO TOLERANCE compliance
- [ ] Run all tests
- [ ] Update documentation

---

## Gradual Migration

You can migrate gradually:

### Phase 1: Add flext-cli alongside existing code

```python
# Old code still works
import click

# New code uses flext-cli
from flext_cli import FlextCli
cli = FlextCli()
```

### Phase 2: Migrate commands one by one

```python
from flext_cli import FlextCli

cli = FlextCli()

# Migrate this command
@cli.main.command()
def new_command():
    pass

# Keep old command temporarily
@click.command()
def old_command():
    pass
```

### Phase 3: Complete migration

```python
from flext_cli import FlextCli

cli = FlextCli()

# All commands through flext-cli
@cli.main.command()
def command1():
    pass

@cli.main.command()
def command2():
    pass
```

---

## Troubleshooting

### Issue: "Can't find Click/Rich features"

**Solution**: Check if feature is wrapped in flext-cli:

- `FlextCliClick`: Check `cli.py` for Click wrappers
- `FlextCliFormatters`: Check `formatters.py` for Rich wrappers
- If missing, feature may be in Phase 2/3 roadmap

### Issue: "FlextResult handling is verbose"

**Solution**: Helper functions can reduce boilerplate:

```python
def unwrap_or_exit(result, error_msg="Operation failed"):
    """Helper to unwrap or exit on failure."""
    if result.is_success:
        return result.unwrap()
    print(f"Error: {error_msg} - {result.error}")
    exit(1)

# Usage
data = unwrap_or_exit(some_operation())
```

### Issue: "Need features not yet wrapped"

**Solutions**:

1. Check if feature is in Phase 2/3 roadmap
2. Use `cli.formatters.get_console()` for direct Rich access (temporary)
3. Request feature addition to flext-cli

---

## Support

- **Documentation**: `docs/` directory
- **Examples**: `examples/phase1_complete_demo.py`
- **Issues**: GitHub issues for feature requests
- **Community**: FLEXT ecosystem support channels

---

**Happy migrating! 🚀**
