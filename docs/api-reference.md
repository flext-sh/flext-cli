# FLEXT CLI API Reference

**Complete reference for FLEXT CLI command-line interface patterns**

This document provides comprehensive API documentation for FLEXT CLI components based on the actual implementation in `src/flext_cli/`.

## 🎯 Essential Imports

```python
# Core CLI components (from main flext package)
from flext.cli import FlextCliCommands

# Or import directly from flext_cli module
from flext_cli.main import FlextCliMain
from flext_cli.cli import FlextCliClick
from flext_cli.commands import FlextCliCommands
from flext_cli.config import FlextCliConfig
from flext_cli.output import FlextCliOutput
from flext_cli.context import FlextCliContext

# CLI utilities
from flext_cli.tables import FlextCliTable
from flext_cli.formatters import FlextCliFormatters
from flext_cli.prompts import FlextCliPrompts
from flext_cli.shell import FlextCliShell

# CLI patterns
from flext_cli.core import FlextCliCore
from flext_cli.api import FlextCli
from flext_cli.auth import FlextCliAuth
```

## 🏗️ FlextCliMain - Command Registration System

Central hub for CLI command registration, discovery, and execution.

### Basic Usage

```python
from flext_cli.main import FlextCliMain
from flext_core import FlextResult

# Create CLI application
main = FlextCliMain(
    name="myapp",
    version="1.0.0",
    description="My awesome CLI application"
)

# Register a simple command
@main.command()
def hello(name: str):
    """Say hello to someone."""
    print(f"Hello {name}!")

# Register a command group
@main.group()
def config():
    """Configuration commands."""
    pass

# Register subcommand
@config.command()
def show():
    """Show configuration."""
    print("Configuration...")

# Execute CLI
result = main.execute_cli()
```

### Advanced Features

```python
# Register command programmatically
def custom_command(value: str):
    """Custom command with validation."""
    print(f"Processing: {value}")

result = main.register_command(
    custom_command,
    name="custom",
    help="Process a value"
)

# Load plugin commands
plugin_result = main.load_plugin_commands("myapp.plugins")
if plugin_result.is_success:
    loaded_commands = plugin_result.unwrap()

# List available commands
commands_result = main.list_commands()
if commands_result.is_success:
    commands = commands_result.unwrap()
    print(f"Available commands: {commands}")
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

Environment-aware configuration for CLI applications.

```python
from flext_cli.config import FlextCliConfig
from flext_core import FlextConfig

class MyCliConfig(FlextCliConfig):
    api_url: str = "https://api.example.com"
    timeout: int = 30
    debug: bool = False

    model_config = {"env_prefix": "MYCLI_"}

# Usage
config = MyCliConfig()
print(f"API URL: {config.api_url}")
print(f"Timeout: {config.timeout}")
```

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

### Testing CLI Commands

```python
import pytest
from flext_cli.main import FlextCliMain
from flext_core import FlextResult

def test_hello_command():
    """Test hello command functionality."""
    main = FlextCliMain()

    @main.command()
    def hello(name: str) -> str:
        return f"Hello {name}!"

    # Test command execution
    result = main.execute_cli(["hello", "World"])
    assert result.is_success

def test_command_registration():
    """Test command registration."""
    main = FlextCliMain()

    def test_cmd(value: str) -> str:
        return f"Processed: {value}"

    result = main.register_command(test_cmd, name="test")
    assert result.is_success

    # Verify command is registered
    commands_result = main.list_commands()
    assert "test" in commands_result.unwrap()
```

## 📋 CLI Command Patterns

### Standard Command Structure

```python
from flext_cli.main import FlextCliMain
from flext_core import FlextResult

class MyCliApp(FlextCliMain):
    def __init__(self):
        super().__init__(
            name="myapp",
            version="1.0.0"
        )

    @FlextCliMain.command()
    def process(
        self,
        input_file: str,
        output_file: str = "output.txt",
        verbose: bool = False
    ) -> None:
        """Process input file and save to output."""
        # Command implementation
        pass

    @FlextCliMain.group()
    def config(self):
        """Configuration management."""
        pass

    @config.command()
    def show(self):
        """Show current configuration."""
        # Subcommand implementation
        pass
```

### Error Handling in Commands

```python
@FlextCliMain.command()
def risky_operation(file_path: str) -> None:
    """Perform operation that might fail."""
    try:
        # Operation that might fail
        result = process_file(file_path)

        if result.is_failure:
            # Use flext-core error handling
            raise click.ClickException(result.error)

    except Exception as e:
        # Convert to FlextResult pattern
        error_result = FlextResult[None].fail(str(e))
        raise click.ClickException(error_result.error)
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

### Shell Integration

```python
from flext_cli.shell import FlextCliShell

shell = FlextCliShell()

# Execute shell command
result = shell.execute("ls -la")
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

## 🔗 Integration Examples

### With Other FLEXT Domains

```python
# Use flext-api for HTTP operations
from flext_api import FlextApiClient
from flext_cli.main import FlextCliMain

class ApiCliApp(FlextCliMain):
    def __init__(self):
        super().__init__(name="api-cli")
        self._api = FlextApiClient()

    @FlextCliMain.command()
    def get_user(self, user_id: int) -> None:
        """Get user information from API."""
        result = self._api.get(f"/users/{user_id}")

        if result.is_success:
            user_data = result.unwrap()
            self._output.display_json(user_data)
        else:
            raise click.ClickException(result.error)
```

### Custom Output Formats

```python
from flext_cli.output import FlextCliOutput

class CustomFormatter(FlextCliOutput):
    def format_user_data(self, users: list) -> str:
        """Custom formatting for user data."""
        output = []
        for user in users:
            output.append(f"👤 {user['name']} ({user['id']})")

        return "\n".join(output)

# Use in command
@main.command()
def list_users():
    """List users with custom formatting."""
    users = get_users_from_api()
    formatter = CustomFormatter()
    formatted = formatter.format_user_data(users)
    print(formatted)
```

---

_This API reference is based on actual implementation analysis and provides working examples for all documented patterns._
