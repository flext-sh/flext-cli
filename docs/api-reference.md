# FLEXT CLI API Reference

**Complete reference for FLEXT CLI command-line interface patterns**

This document provides comprehensive API documentation for FLEXT CLI components based on the actual implementation in `src/flext_cli/`.

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
from flext_core import FlextCore, FlextCore
```

**Note**: `FlextCliAuth` and `FlextCliMain` mentioned in older documentation are not part of current exports. Use `FlextCli` as the main API entry point.

## 🏗️ FlextCli - Main Consolidated API

The `FlextCli` class is the primary entry point providing a unified facade over all CLI functionality.

### Basic Usage

```python
from flext_cli import FlextCli
from flext_core import FlextCore

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
from flext_core import FlextCore
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
from flext_core import FlextCore
from pathlib import Path

def process_command(input_file: str, output_file: str = "output.txt") -> FlextCore.Result[str]:
    """Process input file and save to output."""
    cli = FlextCli()

    # Read input file
    read_result = cli.read_text_file(Path(input_file))
    if read_result.is_failure:
        return FlextCore.Result[str].fail(f"Failed to read input: {read_result.error}")

    # Process content
    content = read_result.unwrap()
    processed = content.upper()  # Example processing

    # Write output file
    write_result = cli.write_text_file(Path(output_file), processed)
    if write_result.is_failure:
        return FlextCore.Result[str].fail(f"Failed to write output: {write_result.error}")

    cli.success(f"Processed {input_file} -> {output_file}")
    return FlextCore.Result[str].ok("Processing complete")
```

### Railway-Oriented Error Handling

Always use `FlextCore.Result[T]` for operations that can fail:

```python
from flext_cli import FlextCli, FlextCliFileTools
from flext_core import FlextCore

def risky_operation(file_path: str) -> FlextCore.Result[dict]:
    """Operation with proper error handling."""
    file_tools = FlextCliFileTools()

    # Chain operations with railway pattern
    return (
        file_tools.read_json_file(file_path)
        .flat_map(lambda data: validate_data(data))
        .map(lambda data: transform_data(data))
        .map_error(lambda err: f"Operation failed: {err}")
    )

def validate_data(data: dict) -> FlextCore.Result[dict]:
    """Validation step."""
    if "required_field" not in data:
        return FlextCore.Result[dict].fail("Missing required field")
    return FlextCore.Result[dict].ok(data)

def transform_data(data: dict) -> dict:
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

1. **Use FlextCore.Result for all operations**
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
from flext_core import FlextCore, FlextCore

# All operations return FlextCore.Result[T]
def process_with_cli(data: dict) -> FlextCore.Result[str]:
    """Example integration with flext-core patterns."""
    cli = FlextCli()

    # Use FlextCore.Result railway pattern
    return (
        validate_input(data)
        .map(lambda d: process_data(d))
        .map(lambda result: format_output(result, cli))
    )

def validate_input(data: dict) -> FlextCore.Result[dict]:
    """Validate with FlextCore.Result."""
    if not data:
        return FlextCore.Result[dict].fail("Data cannot be empty")
    return FlextCore.Result[dict].ok(data)

def process_data(data: dict) -> dict:
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
