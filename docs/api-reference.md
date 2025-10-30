# FLEXT CLI API Reference

**Complete reference for FLEXT CLI command-line interface patterns**

**Last Updated**: 2025-01-24 | **Version**: 0.10.0

---

## 📌 Quick Navigation

- [v0.10.0 API (Current)](#v0100-api-current) ← **Start Here**
- [v0.9.0 API (Historical Reference)](#v090-api-historical-reference)

---

## v0.10.0 API (Current)

**Status**: 📝 Planned | **Release**: Q1 2025 | **Breaking Changes**: Yes

### Overview

FLEXT-CLI v0.10.0 introduces a **direct access API pattern**, removing all wrapper methods from the main `FlextCli` facade. This provides clearer ownership of functionality and eliminates API duplication.

**Key Changes**:

- **Direct Access**: All operations accessed via property paths (e.g., `cli.formatters.print()`)
- **No Wrappers**: Removed ~15 wrapper methods from `FlextCli`
- **Clear Ownership**: Explicit which service handles each operation
- **Context as Value Object**: `FlextCliContext` is now immutable data

### Essential Imports (v0.10.0)

```python
# Main API facade
from flext_cli import FlextCli

# Core services and utilities
from flext_cli import (
    FlextCliCore,          # Core service (stateful)
    FlextCliCmd,           # Command execution
    FlextCliConfig,        # Configuration singleton
    FlextCliContext,       # Execution context (NOW VALUE OBJECT)
)

# Simple utility classes
from flext_cli import (
    FlextCliFileTools,     # File I/O (JSON/YAML/CSV)
    FlextCliFormatters,    # Rich formatting
    FlextCliTables,        # Table generation
    FlextCliOutput,        # Output management
    FlextCliPrompts,       # Interactive prompts
    FlextCliDebug,         # Debug utilities
)

# Data models and types
from flext_cli import (
    FlextCliModels,        # ALL Pydantic models
    FlextCliTypes,         # Type definitions
    FlextCliConstants,     # System constants
    FlextCliExceptions,    # Exception hierarchy
)

# Railway pattern from flext-core
from flext_core import FlextResult
```

---

### 🏗️ FlextCli - Main API Facade (v0.10.0)

The main entry point provides access to all CLI functionality via properties.

#### Basic Initialization

```python
from flext_cli import FlextCli

# Create instance (singleton pattern)
cli = FlextCli()

# Access services via direct properties
cli.formatters    # FlextCliFormatters - Rich formatting
cli.file_tools    # FlextCliFileTools - File operations
cli.prompts       # FlextCliPrompts - User input
cli.output        # FlextCliOutput - Output management
cli.config        # FlextCliConfig - Configuration
cli.core          # FlextCliCore - Core service
```

---

### 🎨 Output Formatting (v0.10.0)

#### Print and Formatting

```python
from flext_cli import FlextCli

cli = FlextCli()

# Direct access to formatters
cli.formatters.print("Hello World!", style="green")
cli.formatters.print("[bold red]Error![/bold red]")
cli.formatters.print("Info", style="blue bold")

# Create styled text
styled = cli.formatters.style_text("Warning", style="yellow")
```

#### Table Display

```python
from flext_cli import FlextCli

cli = FlextCli()

# Create table data
users = [
    {"name": "Alice", "age": 30, "role": "Admin"},
    {"name": "Bob", "age": 25, "role": "User"},
]

# Format as table (direct access to output service)
table_result = cli.output.format_data(
    data={"users": users},
    format_type="table"
)

# Display the table
if table_result.is_success:
    cli.formatters.print(table_result.unwrap())
```

#### Progress Indicators

```python
from flext_cli import FlextCli

cli = FlextCli()

# Create progress bar
progress_result = cli.formatters.create_progress_bar(
    total=100,
    description="Processing items..."
)

if progress_result.is_success:
    progress = progress_result.unwrap()

    for i in range(100):
        progress.update(1)
        # Do work...

    progress.stop()
```

---

### 📁 File Operations (v0.10.0)

#### JSON Operations

```python
from flext_cli import FlextCli
from pathlib import Path

cli = FlextCli()

# Read JSON file (direct access to file_tools)
config_result = cli.file_tools.read_json_file("config.json")

if config_result.is_success:
    config = config_result.unwrap()
    print(f"Loaded config: {config}")
else:
    cli.formatters.print(f"Error: {config_result.error}", style="red")

# Write JSON file
data = {"setting": "value", "enabled": True}
write_result = cli.file_tools.write_json_file("output.json", data)

if write_result.is_success:
    cli.formatters.print("File saved!", style="green")
```

#### YAML Operations

```python
from flext_cli import FlextCli

cli = FlextCli()

# Read YAML
yaml_result = cli.file_tools.read_yaml_file("config.yaml")

if yaml_result.is_success:
    config = yaml_result.unwrap()

# Write YAML
data = {"database": {"host": "localhost", "port": 5432}}
cli.file_tools.write_yaml_file("config.yaml", data)
```

#### CSV Operations

```python
from flext_cli import FlextCli

cli = FlextCli()

# Read CSV
csv_result = cli.file_tools.read_csv_file("data.csv")

if csv_result.is_success:
    rows = csv_result.unwrap()
    cli.formatters.print(f"Loaded {len(rows)} rows")

# Write CSV
data = [
    ["Name", "Age", "Role"],
    ["Alice", "30", "Admin"],
    ["Bob", "25", "User"],
]
cli.file_tools.write_csv_file("output.csv", data)
```

---

### 💬 Interactive Prompts (v0.10.0)

#### Confirmation Dialogs

```python
from flext_cli import FlextCli

cli = FlextCli()

# Ask for confirmation (direct access to prompts)
confirm_result = cli.prompts.confirm(
    "Continue with operation?",
    default=True
)

if confirm_result.is_success and confirm_result.unwrap():
    cli.formatters.print("Proceeding...", style="green")
else:
    cli.formatters.print("Cancelled", style="yellow")
```

#### Text Input

```python
from flext_cli import FlextCli

cli = FlextCli()

# Get text input
name_result = cli.prompts.prompt(
    "Enter your name:",
    default="Guest"
)

if name_result.is_success:
    name = name_result.unwrap()
    cli.formatters.print(f"Hello, {name}!", style="cyan")
```

#### Selection Prompts

```python
from flext_cli import FlextCli

cli = FlextCli()

# Select from choices
choice_result = cli.prompts.select(
    message="Choose environment:",
    choices=["development", "staging", "production"]
)

if choice_result.is_success:
    env = choice_result.unwrap()
    cli.formatters.print(f"Selected: {env}", style="green")
```

---

### 📦 Context as Value Object (v0.10.0)

**Important Change**: `FlextCliContext` is now an immutable value object (not a service).

```python
from flext_cli import FlextCliContext

# Create immutable context
context = FlextCliContext(
    command="deploy",
    arguments=["production", "--force"],
    environment_variables={"ENV": "prod"},
    working_directory="/app"
)

# Access data (no methods, just properties)
print(f"Command: {context.command}")
print(f"Args: {context.arguments}")
print(f"Working dir: {context.working_directory}")

# Immutable - create new instance for changes
updated_context = context.model_copy(
    update={"working_directory": "/app/new"}
)

# ❌ OLD (v0.9.0) - No longer available:
# context.activate()   # REMOVED
# context.deactivate() # REMOVED
# context.is_active = True  # REMOVED (now immutable)
```

---

### ⚙️ Configuration Management (v0.10.0)

```python
from flext_cli import FlextCliConfig

# Get singleton instance
config = FlextCliConfig.get_global_instance()

# Read-only properties (env var support)
debug = config.debug                    # FLEXT_DEBUG
output_format = config.output_format    # FLEXT_OUTPUT_FORMAT
timeout = config.timeout                # FLEXT_TIMEOUT
token_file = config.token_file          # ~/.flext/auth/token.json

# Access via CLI facade
from flext_cli import FlextCli
cli = FlextCli()
debug_mode = cli.config.debug
```

---

### 🧪 Railway-Oriented Error Handling (v0.10.0)

All operations return `FlextResult[T]` for composable error handling.

```python
from flext_cli import FlextCli
from flext_core import FlextResult

cli = FlextCli()

# Chain operations
result = (
    cli.file_tools.read_json_file("config.json")
    .flat_map(lambda config: validate_config(config))
    .map(lambda config: apply_defaults(config))
    .map(lambda config: cli.formatters.print(f"Config loaded: {config}"))
)

# Handle success or failure
if result.is_success:
    cli.formatters.print("Operation completed!", style="green")
else:
    cli.formatters.print(f"Error: {result.error}", style="red")

# Safe unwrap with default
config = result.unwrap_or(default_config)
```

---

### 🔧 Utility Operations (v0.10.0)

#### Debug Utilities

```python
from flext_cli import FlextCli

cli = FlextCli()

# Access debug utilities
debug_info = cli.debug.get_system_info()
cli.debug.dump_state()
cli.debug.trace_execution()
```

#### Table Formatting

```python
from flext_cli import FlextCli

cli = FlextCli()

# Create table with specific format
data = [["Name", "Age"], ["Alice", 30], ["Bob", 25]]

table_result = cli.tables.create_table(
    data=data,
    format="fancy_grid",  # 22+ formats available
    title="Users"
)

if table_result.is_success:
    cli.formatters.print(table_result.unwrap())
```

---

### 📊 Complete Example: Application Workflow (v0.10.0)

```python
from flext_cli import FlextCli, FlextCliContext
from flext_core import FlextResult

def main() -> FlextResult[None]:
    """Complete application using v0.10.0 API patterns."""
    cli = FlextCli()

    # 1. Load configuration (direct access)
    config_result = cli.file_tools.read_json_file("config.json")
    if not config_result.is_success:
        cli.formatters.print(f"Config error: {config_result.error}", style="red")
        return FlextResult[None].fail(config_result.error)

    config = config_result.unwrap()

    # 2. Create immutable context (value object)
    context = FlextCliContext(
        command="process",
        arguments=["--verbose"],
        environment_variables={"MODE": "production"},
        working_directory=config.get("work_dir", "/tmp")
    )

    # 3. Confirm with user (direct access to prompts)
    confirm_result = cli.prompts.confirm(
        f"Process in {context.environment_variables['MODE']} mode?"
    )

    if not confirm_result.is_success or not confirm_result.unwrap():
        cli.formatters.print("Operation cancelled", style="yellow")
        return FlextResult[None].ok(None)

    # 4. Process data with progress
    cli.formatters.print("Processing data...", style="cyan")

    # 5. Save results (direct access to file_tools)
    results = {"status": "completed", "processed": 100}
    save_result = cli.file_tools.write_json_file("results.json", results)

    if save_result.is_success:
        cli.formatters.print("✓ Processing complete!", style="green bold")

        # 6. Display results as table
        table_data = [
            ["Metric", "Value"],
            ["Status", results["status"]],
            ["Processed", results["processed"]],
        ]
        table_result = cli.tables.create_table(data=table_data, format="simple")

        if table_result.is_success:
            cli.formatters.print(table_result.unwrap())

    return FlextResult[None].ok(None)

if __name__ == "__main__":
    result = main()
    if not result.is_success:
        print(f"Error: {result.error}")
```

---

### 🔀 Migration from v0.9.0 to v0.10.0

**Common Pattern Changes**:

| v0.9.0 (Old)               | v0.10.0 (New)                                      | Category |
| -------------------------- | -------------------------------------------------- | -------- |
| `cli.print(...)`           | `cli.formatters.print(...)`                        | Output   |
| `cli.create_table(...)`    | `cli.output.format_data(..., format_type="table")` | Tables   |
| `cli.read_json_file(...)`  | `cli.file_tools.read_json_file(...)`               | Files    |
| `cli.write_json_file(...)` | `cli.file_tools.write_json_file(...)`              | Files    |
| `cli.confirm(...)`         | `cli.prompts.confirm(...)`                         | Input    |
| `cli.prompt_text(...)`     | `cli.prompts.prompt(...)`                          | Input    |
| `context.activate()`       | ❌ Removed (context is now immutable)              | Context  |
| `context.deactivate()`     | ❌ Removed (context is now immutable)              | Context  |

**See Full Guide**: [MIGRATION_GUIDE_V0.9_TO_V0.10.md](refactoring/MIGRATION_GUIDE_V0.9_TO_V0.10.md)

---

## v0.9.0 API (Historical Reference)

**Note**: The following documentation describes the v0.9.0 API with wrapper methods. This is kept for historical reference during the migration period.

## 🎯 Essential Imports

All imports should use the unified flext_cli package:

```python
# Main consolidated API (recommended entry point)
from flext_cli import FlextCli

# Core components (19 exports available)
from flext_cli import (
    FlextCliCli,           # Click abstraction (NOT FlextCliClick)
    FlextCliCmd,           # Command execution
    FlextCliCommands,      # Command management
    FlextCliCommonParams,  # Reusable CLI parameters
    FlextCliConfig,        # Configuration singleton
    FlextCliConstants,     # System constants
    FlextCliContext,       # Execution context
    FlextCliCore,          # Core service
    FlextCliDebug,         # Debug utilities
    FlextCliExceptions,    # Exception hierarchy
    FlextCliFileTools,     # File operations (JSON/YAML/CSV)
    FlextCliFormatters,    # Rich abstraction
    FlextCliMixins,        # Reusable mixins
    FlextCliModels,        # ALL Pydantic models
    FlextCliOutput,        # Output service
    FlextCliPrompts,       # Interactive prompts
    FlextCliProtocols,     # Structural typing
    FlextCliTables,        # Table formatting (NOT FlextCliTable)
    FlextCliTypes,         # Type definitions
)

# Import from flext-core for patterns
from flext_core import FlextBus
from flext_core import FlextConfig
from flext_core import FlextConstants
from flext_core import FlextContainer
from flext_core import FlextContext
from flext_core import FlextDecorators
from flext_core import FlextDispatcher
from flext_core import FlextExceptions
from flext_core import FlextHandlers
from flext_core import FlextLogger
from flext_core import FlextMixins
from flext_core import FlextModels
from flext_core import FlextProcessors
from flext_core import FlextProtocols
from flext_core import FlextRegistry
from flext_core import FlextResult
from flext_core import FlextRuntime
from flext_core import FlextService
from flext_core import FlextTypes
from flext_core import FlextUtilities
```

**Note**: `FlextCliAuth` and `FlextCliMain` mentioned in older documentation are not part of current exports. Use `FlextCli` as the main API entry point.

## 🏗️ FlextCli - Main Consolidated API

The `FlextCli` class is the primary entry point providing a unified facade over all CLI functionality.

### Basic Usage

```python
from flext_cli import FlextCli
from flext_core import FlextBus
from flext_core import FlextConfig
from flext_core import FlextConstants
from flext_core import FlextContainer
from flext_core import FlextContext
from flext_core import FlextDecorators
from flext_core import FlextDispatcher
from flext_core import FlextExceptions
from flext_core import FlextHandlers
from flext_core import FlextLogger
from flext_core import FlextMixins
from flext_core import FlextModels
from flext_core import FlextProcessors
from flext_core import FlextProtocols
from flext_core import FlextRegistry
from flext_core import FlextResult
from flext_core import FlextRuntime
from flext_core import FlextService
from flext_core import FlextTypes
from flext_core import FlextUtilities

# Create CLI instance (consolidated API)
cli = FlextCli()

# Configuration access (singleton pattern)
config = cli.config
debug_mode = config.debug
output_format = config.output_format

# Output operations
cli.print("Success!", style="green")
cli.print("[bold red]Error message[/bold red]")

# Table display
users = [
    {"name": "Alice", "age": 30, "role": "Admin"},
    {"name": "Bob", "age": 25, "role": "User"},
]
table_result = cli.create_table(
    data={"users": users},
    headers=["Name", "Age", "Role"],
    title="Active Users"
)
```

### File Operations

```python
from pathlib import Path

# Read/write text files
content_result = cli.read_text_file(Path("config.txt"))
if content_result.is_success:
    content = content_result.unwrap()

write_result = cli.write_text_file(Path("output.txt"), "Hello World")

# JSON operations (via file_tools)
json_result = cli.file_tools.read_json_file("config.json")
if json_result.is_success:
    config_data = json_result.unwrap()

write_json_result = cli.file_tools.write_json_file(
    "data.json",
    {"key": "value"}
)
```

### Interactive Prompts

```python
# Confirmation dialogs
if cli.confirm("Continue with operation?", default=True):
    # User confirmed
    name = cli.prompt_text("Enter your name:", default="Guest")
    cli.success(f"Hello, {name}!")

# Various prompt types via prompts
choice_result = cli.prompts.select(
    "Choose option:",
    choices=["option1", "option2", "option3"]
)
```

## 🎨 FlextCliOutput - Rich Output Formatting

Beautiful CLI output using Rich library through flext-cli domain.

### Table Display

```python
from flext_cli.output import FlextCliOutput

output = FlextCliOutput()

# Display data as table
users = [
    {"id": 1, "name": "John", "email": "john@example.com"},
    {"id": 2, "name": "Jane", "email": "jane@example.com"},
]

result = output.display_table(
    data=users,
    title="Active Users",
    columns=["id", "name", "email"]
)
```

### Progress Bars

```python
# Show progress during long operations
result = output.create_progress_bar(
    total=100,
    description="Processing items..."
)

if result.is_success:
    progress = result.unwrap()

    for i in range(100):
        # Update progress
        progress.update(1)

        # Do work...
        time.sleep(0.1)

    progress.stop()
```

### Interactive Prompts

```python
from flext_cli.prompts import FlextCliPrompts

prompts = FlextCliPrompts()

# Text input
name_result = prompts.text_input("Enter your name")
if name_result.is_success:
    name = name_result.unwrap()

# Confirmation
confirm_result = prompts.confirm("Continue with operation?")
if confirm_result.is_success:
    confirmed = confirm_result.unwrap()

# Selection
choice_result = prompts.select(
    "Choose option",
    choices=["option1", "option2", "option3"]
)
```

## ⚙️ FlextCliConfig - Configuration Management

Singleton configuration with environment variable support.

```python
from flext_cli import FlextCliConfig

# Get singleton instance (creates if needed)
config = FlextCliConfig.get_global_instance()

# Configuration is read-only properties
debug = config.debug                    # FLEXT_DEBUG env var
output_format = config.output_format    # FLEXT_OUTPUT_FORMAT env var
no_color = config.no_color             # FLEXT_NO_COLOR env var
profile = config.profile               # FLEXT_PROFILE env var
timeout = config.timeout               # FLEXT_TIMEOUT env var
token_file = config.token_file         # ~/.flext/auth/token.json

# Access via FlextCli
from flext_cli import FlextCli
cli = FlextCli()
config = cli.config  # Same singleton instance
```

**Environment Variables:**

- `FLEXT_DEBUG` - Enable debug mode (true/false)
- `FLEXT_OUTPUT_FORMAT` - Output format (JSON/table/YAML)
- `FLEXT_NO_COLOR` - Disable colors (true/false)
- `FLEXT_PROFILE` - Configuration profile name
- `FLEXT_TIMEOUT` - Default timeout in seconds
- `FLEXT_RETRIES` - Max retry attempts

## 🔧 FlextCliContext - Context Management

Context management for CLI operations with correlation IDs.

```python
from flext_cli.context import FlextCliContext

# Create context for operation
context = FlextCliContext(operation_id="user_sync_001")

with context:
    # All operations in this block share the context
    logger.info("Starting user sync", extra=context.to_dict())
```

## 🧪 Testing Patterns

### Testing CLI Components

```python
import pytest
from flext_cli import FlextCli, FlextCliFileTools
from flext_core import FlextBus
from flext_core import FlextConfig
from flext_core import FlextConstants
from flext_core import FlextContainer
from flext_core import FlextContext
from flext_core import FlextDecorators
from flext_core import FlextDispatcher
from flext_core import FlextExceptions
from flext_core import FlextHandlers
from flext_core import FlextLogger
from flext_core import FlextMixins
from flext_core import FlextModels
from flext_core import FlextProcessors
from flext_core import FlextProtocols
from flext_core import FlextRegistry
from flext_core import FlextResult
from flext_core import FlextRuntime
from flext_core import FlextService
from flext_core import FlextTypes
from flext_core import FlextUtilities
from pathlib import Path

def test_cli_output(flext_cli_api: FlextCli):
    """Test CLI output operations using fixture."""
    result = flext_cli_api.print("Test message", style="green")
    assert result is None  # Print operations return None

def test_file_operations(flext_cli_file_tools: FlextCliFileTools, temp_dir: Path):
    """Test file operations."""
    test_file = temp_dir / "test.txt"
    content = "Hello, World!"

    # Write file
    write_result = flext_cli_file_tools.write_text_file(test_file, content)
    assert write_result.is_success

    # Read file
    read_result = flext_cli_file_tools.read_text_file(test_file)
    assert read_result.is_success
    assert read_result.unwrap() == content

def test_json_operations(flext_cli_api: FlextCli, temp_json_file: Path):
    """Test JSON file operations."""
    json_result = flext_cli_api.file_tools.read_json_file(str(temp_json_file))
    assert json_result.is_success
    data = json_result.unwrap()
    assert "key" in data
```

**Available Test Fixtures** (from `tests/conftest.py`):

- `flext_cli_api` - FlextCli instance
- `flext_cli_file_tools` - FlextCliFileTools instance
- `temp_dir` - Temporary directory
- `temp_file`, `temp_json_file`, `temp_yaml_file` - Temporary files
- `sample_config_data` - Sample configuration dict
- `mock_env_vars` - Mock environment variables

## 📋 CLI Usage Patterns

### Using FlextCli Facade

The recommended approach is to use `FlextCli` as the unified API:

```python
from flext_cli import FlextCli
from flext_core import FlextBus
from flext_core import FlextConfig
from flext_core import FlextConstants
from flext_core import FlextContainer
from flext_core import FlextContext
from flext_core import FlextDecorators
from flext_core import FlextDispatcher
from flext_core import FlextExceptions
from flext_core import FlextHandlers
from flext_core import FlextLogger
from flext_core import FlextMixins
from flext_core import FlextModels
from flext_core import FlextProcessors
from flext_core import FlextProtocols
from flext_core import FlextRegistry
from flext_core import FlextResult
from flext_core import FlextRuntime
from flext_core import FlextService
from flext_core import FlextTypes
from flext_core import FlextUtilities
from pathlib import Path

def process_command(input_file: str, output_file: str = "output.txt") -> FlextResult[str]:
    """Process input file and save to output."""
    cli = FlextCli()

    # Read input file
    read_result = cli.read_text_file(Path(input_file))
    if read_result.is_failure:
        return FlextResult[str].fail(f"Failed to read input: {read_result.error}")

    # Process content
    content = read_result.unwrap()
    processed = content.upper()  # Example processing

    # Write output file
    write_result = cli.write_text_file(Path(output_file), processed)
    if write_result.is_failure:
        return FlextResult[str].fail(f"Failed to write output: {write_result.error}")

    cli.success(f"Processed {input_file} -> {output_file}")
    return FlextResult[str].ok("Processing complete")
```

### Railway-Oriented Error Handling

Always use `FlextResult[T]` for operations that can fail:

```python
from flext_cli import FlextCli, FlextCliFileTools
from flext_core import FlextBus
from flext_core import FlextConfig
from flext_core import FlextConstants
from flext_core import FlextContainer
from flext_core import FlextContext
from flext_core import FlextDecorators
from flext_core import FlextDispatcher
from flext_core import FlextExceptions
from flext_core import FlextHandlers
from flext_core import FlextLogger
from flext_core import FlextMixins
from flext_core import FlextModels
from flext_core import FlextProcessors
from flext_core import FlextProtocols
from flext_core import FlextRegistry
from flext_core import FlextResult
from flext_core import FlextRuntime
from flext_core import FlextService
from flext_core import FlextTypes
from flext_core import FlextUtilities

def risky_operation(file_path: str) -> FlextResult[dict]:
    """Operation with proper error handling."""
    file_tools = FlextCliFileTools()

    # Chain operations with railway pattern
    return (
        file_tools.read_json_file(file_path)
        .flat_map(lambda data: validate_data(data))
        .map(lambda data: transform_data(data))
        .map_error(lambda err: f"Operation failed: {err}")
    )

def validate_data(data: dict) -> FlextResult[dict]:
    """Validation step."""
    if "required_field" not in data:
        return FlextResult[dict].fail("Missing required field")
    return FlextResult[dict].ok(data)

def transform_data(data: dict) -> dict[str, object]:
    """Transformation step (can't fail)."""
    return {**data, "processed": True}
```

## 🛠️ CLI Utilities

### File Operations

```python
from flext_cli.file_tools import FlextCliFileTools

file_tools = FlextCliFileTools()

# Read file with error handling
content_result = file_tools.read_file("config.json")
if content_result.is_success:
    content = content_result.unwrap()

# Write file safely
write_result = file_tools.write_file("output.txt", "Hello, World!")
```

### Command Execution

```python
from flext_cli import FlextCliCmd

cmd = FlextCliCmd()

# Execute system command safely
result = cmd.execute_command("ls -la")
if result.is_success:
    output = result.unwrap()
    print(f"Command output: {output}")
```

## 🎯 Best Practices

### Command Design

1. **Use FlextResult for all operations**
2. **Provide clear help text and descriptions**
3. **Validate inputs early**
4. **Use consistent naming conventions**
5. **Handle errors gracefully**

### Output Formatting

1. **Use Rich tables for data display**
2. **Show progress for long operations**
3. **Provide clear error messages**
4. **Use consistent color schemes**
5. **Support both human-readable and machine-readable output**

### Configuration

1. **Use environment variables for sensitive data**
2. **Provide sensible defaults**
3. **Validate configuration early**
4. **Support multiple configuration sources**
5. **Document all configuration options**

## 🔗 Integration with FLEXT Ecosystem

### Using flext-cli with flext-core Patterns

```python
from flext_cli import FlextCli
from flext_core import FlextBus
from flext_core import FlextConfig
from flext_core import FlextConstants
from flext_core import FlextContainer
from flext_core import FlextContext
from flext_core import FlextDecorators
from flext_core import FlextDispatcher
from flext_core import FlextExceptions
from flext_core import FlextHandlers
from flext_core import FlextLogger
from flext_core import FlextMixins
from flext_core import FlextModels
from flext_core import FlextProcessors
from flext_core import FlextProtocols
from flext_core import FlextRegistry
from flext_core import FlextResult
from flext_core import FlextRuntime
from flext_core import FlextService
from flext_core import FlextTypes
from flext_core import FlextUtilities

# All operations return FlextResult[T]
def process_with_cli(data: dict) -> FlextResult[str]:
    """Example integration with flext-core patterns."""
    cli = FlextCli()

    # Use FlextResult railway pattern
    return (
        validate_input(data)
        .map(lambda d: process_data(d))
        .map(lambda result: format_output(result, cli))
    )

def validate_input(data: dict) -> FlextResult[dict]:
    """Validate with FlextResult."""
    if not data:
        return FlextResult[dict].fail("Data cannot be empty")
    return FlextResult[dict].ok(data)

def process_data(data: dict) -> dict[str, object]:
    """Process data."""
    return {**data, "processed": True}

def format_output(data: dict, cli: FlextCli) -> str:
    """Format and display output."""
    cli.success("Processing complete!")
    cli.print(f"Result: {data}")
    return "done"
```

### Custom Output Formats

```python
from flext_cli import FlextCli, FlextCliFormatters

def format_user_data(users: list[dict]) -> str:
    """Custom formatting for user data."""
    output = []
    for user in users:
        output.append(f"👤 {user['name']} ({user['id']})")
    return "\n".join(output)

def display_users() -> None:
    """Display users with custom formatting."""
    cli = FlextCli()
    users = [
        {"name": "Alice", "id": 1},
        {"name": "Bob", "id": 2}
    ]

    # Format and display
    formatted = format_user_data(users)
    cli.print(formatted)

    # Or use Rich directly via formatters
    cli.formatters.print_text(formatted, style="bold blue")
```

---

**Last Updated**: 2025-10-10 | **Version**: 0.9.0

_This API reference reflects the actual current implementation in flext-cli 0.9.0. All examples use the 19 exported classes from `src/flext_cli/__init__.py`._
