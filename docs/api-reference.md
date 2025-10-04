# API Reference - flext-cli

**Complete API documentation for the FLEXT CLI foundation library.**

**Last Updated**: October 1, 2025 | **Version**: 2.2.0 (96% Functional)

---

## Core Classes

### FlextCli

Main CLI API interface with comprehensive functionality.

```python
from flext_cli import FlextCli

class FlextCli(FlextService[str]):
    """Unified CLI API with Python 3.13 patterns."""

    def process_command(self, command: str) -> FlextResult[str]:
        """Process CLI command with error handling."""

    def format_output(self, data: dict, format_type: str) -> FlextResult[str]:
        """Format output data using Rich abstraction."""

    def validate_config(self, config_data: dict) -> FlextResult[FlextTypes.Dict]:
        """Validate CLI configuration data."""
```

### FlextCliConfig

Configuration management with Pydantic validation.

```python
from Flext_cli import FlextCliConfig

class FlextCliConfig:
    """CLI configuration management."""

    def load_project_config(self) -> FlextResult[FlextCliConfig]:
        """Load configuration from project settings."""

    def save_config(self, config: dict) -> FlextResult[None]:
        """Save configuration with validation."""

    def get_output_format(self) -> str:
        """Get configured output format."""
```

### FlextCliAuth

Authentication service integration.

```python
from flext_cli import FlextCliAuth

class FlextCliAuth:
    """Authentication command integration."""

    def login(self, credentials: dict) -> FlextResult[str]:
        """Authenticate user with credentials."""

    def logout(self) -> FlextResult[None]:
        """Logout current user."""

    def get_status(self) -> FlextResult[FlextTypes.Dict]:
        """Get authentication status."""
```

---

## Command Interface

### Available Commands

```bash
flext --help                # Main help
flext auth login           # User authentication
flext auth status          # Authentication status
flext config show          # Show configuration
flext debug info          # System information
```

### Command Registration

```python
from flext_cli import FlextCliCommands

cli = FlextCliCommands(name="my-cli")
cli.register_command_group(
    name="data",
    commands=data_commands,
    description="Data management commands"
)
```

---

## Formatters

### Output Formatting

```python
from flext_cli import FlextCliOutput

formatters = FlextCliOutput()

# Table formatting
table_result = formatters.format_as_table(
    data={"name": "value"},
    title="Data Table"
)

# JSON formatting
json_result = formatters.format_as_json(data)

# YAML formatting
yaml_result = formatters.format_as_yaml(data)
```

---

## Exception Hierarchy

### CLI Exceptions

```python
from flext_cli import FlextCliExceptions.FlextCliError

# Unified exception with error codes and factory methods
error = FlextCliExceptions.FlextCliError("Base error")
validation_error = FlextCliExceptions.FlextCliError.validation_error("Invalid input")
auth_error = FlextCliExceptions.FlextCliError.authentication_error("Authentication failed")
config_error = FlextCliExceptions.FlextCliError.configuration_error("Config invalid")
connection_error = FlextCliExceptions.FlextCliError.connection_error("Connection failed")
command_error = FlextCliExceptions.FlextCliError.command_error("Command failed")
timeout_error = FlextCliExceptions.FlextCliError.timeout_error("Operation timed out")
format_error = FlextCliExceptions.FlextCliError.format_error("Format error")

# Error codes available
FlextCliExceptions.FlextCliError.ErrorCode.CLI_ERROR
FlextCliExceptions.FlextCliError.ErrorCode.VALIDATION_ERROR
FlextCliExceptions.FlextCliError.ErrorCode.AUTHENTICATION_ERROR
FlextCliExceptions.FlextCliError.ErrorCode.CONFIGURATION_ERROR
FlextCliExceptions.FlextCliError.ErrorCode.CONNECTION_ERROR
FlextCliExceptions.FlextCliError.ErrorCode.COMMAND_ERROR
FlextCliExceptions.FlextCliError.ErrorCode.TIMEOUT_ERROR
FlextCliExceptions.FlextCliError.ErrorCode.FORMAT_ERROR
```

---

## Type Definitions

### Core Types

```python
from flext_cli import T, U, V, P, R, E, F

# Generic type variables for CLI operations
T = TypeVar('T')  # General type variable
U = TypeVar('U')  # Secondary type variable
P = TypeVar('P')  # Parameter type variable
R = TypeVar('R')  # Return type variable
```

---

## Integration Patterns

### CLI Integration

```python
from flext_cli import FlextCli, FlextCliService

# CLI operations
api = FlextCli()
api.process_command("example")

# CLI service usage
service = FlextCliService()
```

---

## Extension Examples

### Custom Command Handler

```python
from flext_cli import FlextCli

class CustomCommandHandler:
    """Custom command implementation."""

    def __init__(self):
        self._cli_api = FlextCli()

    def handle_custom_command(self, args: dict):
        """Handle custom CLI command."""
        # Implementation logic
        return "Command executed"
```

### Custom Formatter

```python
from flext_cli import FlextCliOutput

class CustomFormatters(FlextCliOutput):
    """Extended formatters with custom output."""

    def format_as_custom(self, data: dict):
        """Custom formatting implementation."""
        # Custom formatting logic
        return "formatted_output"
```

---

For usage examples, see [examples/](examples/).
For development patterns, see [development.md](development.md).
