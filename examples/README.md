# FLEXT CLI Library Examples

This directory contains practical examples demonstrating how to use the FLEXT CLI library to build powerful command-line interfaces with enterprise-grade patterns.

## Overview

The FLEXT CLI library provides a comprehensive toolkit for building CLI applications using:

- **flext-core foundation patterns** for robust, type-safe development
- **Click integration** with enhanced parameter types and decorators
- **Rich output formatting** for beautiful terminal interfaces
- **Domain-driven design** with CLI-specific entities and business rules
- **Configuration management** with environment variable support
- **Helper utilities** for common CLI operations

## Examples

### 1. Basic CLI Usage (`01_basic_cli_usage.py`)

**Purpose**: Introduction to core FLEXT CLI library functionality

**Features demonstrated**:
- Configuration management with `CLIConfig` and `CLISettings`
- CLI context creation and management
- Helper utilities for validation and formatting
- Click parameter types integration
- Service result handling patterns
- CLI setup and initialization

**Run**: 
```bash
python examples/01_basic_cli_usage.py
```

**Key concepts**:
- `flext_cli.get_config()` - Load CLI configuration
- `flext_cli.CLIContext()` - Create execution context
- `flext_cli.CLIHelper()` - Access utility functions
- `@flext_cli.handle_service_result` - Handle service results

### 2. Click Integration (`02_click_integration.py`)

**Purpose**: Complete Click-based CLI application using FLEXT CLI library

**Features demonstrated**:
- Full Click command group with FLEXT CLI types
- Enhanced decorators for time measurement, confirmation, spinners
- Async command support
- Retry mechanisms for unreliable operations
- Path validation with custom Click types
- Configuration-aware command execution

**Run**:
```bash
python examples/02_click_integration.py --help
python examples/02_click_integration.py process --count 5 --url https://api.example.com
python examples/02_click_integration.py validate --email user@example.com
python examples/02_click_integration.py info
```

**Key concepts**:
- `flext_cli.PositiveInt`, `flext_cli.URL`, `flext_cli.ExistingFile` - Custom Click types
- `@flext_cli.measure_time()` - Time execution measurement
- `@flext_cli.confirm_action()` - User confirmation prompts
- `@flext_cli.with_spinner()` - Progress indication
- `@flext_cli.async_command` - Async command support
- `@flext_cli.retry()` - Automatic retry with backoff

### 3. Domain Entities (`03_domain_entities.py`)

**Purpose**: Demonstrate CLI domain modeling with FLEXT CLI entities

**Features demonstrated**:
- CLI command lifecycle management
- CLI session tracking with command history
- CLI plugin management with dependencies
- Domain events for CLI operations
- Business rule validation
- Practical usage patterns

**Run**:
```bash
python examples/03_domain_entities.py
```

**Key concepts**:
- `flext_cli.CLICommand` - Command execution modeling
- `flext_cli.CLISession` - Session management
- `flext_cli.CLIPlugin` - Plugin system support
- `flext_cli.CommandStatus`, `flext_cli.CommandType` - Domain enums
- Domain events for integration patterns
- Business rule validation with `validate_domain_rules()`

## Library Components

### Configuration Management
```python
# Get configuration
config = flext_cli.get_config()
settings = flext_cli.get_settings()

# Create CLI context
context = flext_cli.CLIContext(
    profile="production",
    output_format="json",
    debug=False
)
```

### Click Parameter Types
```python
@click.option("--count", type=flext_cli.PositiveInt)
@click.option("--url", type=flext_cli.URL) 
@click.option("--input-file", type=flext_cli.ExistingFile)
@click.option("--output-dir", type=flext_cli.ExistingDir)
@click.option("--new-file", type=flext_cli.NewFile)
```

### CLI Decorators
```python
@flext_cli.measure_time(show_in_output=True)
@flext_cli.confirm_action("Are you sure?")
@flext_cli.with_spinner("Processing...")
@flext_cli.retry(max_attempts=3, delay=1.0)
@flext_cli.async_command
@flext_cli.handle_service_result
```

### Helper Utilities
```python
helper = flext_cli.CLIHelper()

# Validation
helper.validate_url("https://api.example.com")
helper.validate_email("user@example.com")
helper.validate_path("/path/to/file")

# Formatting
helper.format_size(1024 * 1024)  # "1.0 MB"
helper.truncate_text("Long text...", max_length=20)
helper.sanitize_filename("unsafe/filename")

# User interaction
helper.confirm("Continue?")
helper.prompt("Enter value:")

# Output
helper.print_success("Operation completed")
helper.print_error("Something went wrong")
helper.print_warning("Be careful")
helper.print_info("FYI")
```

### Domain Entities
```python
# Command modeling
command = flext_cli.CLICommand(
    name="deploy",
    command_line="kubectl apply -f app.yaml",
    command_type=flext_cli.CommandType.SYSTEM
)

# Session tracking
session = flext_cli.CLISession(session_id="session-123")
session.add_command(command.id)

# Plugin management
plugin = flext_cli.CLIPlugin(
    name="k8s-plugin",
    entry_point="k8s.main",
    commands=["deploy", "scale"]
)
```

## Getting Started

1. **Install the FLEXT CLI library** (when published):
   ```bash
   pip install flext-cli
   ```

2. **Start with basic usage**:
   ```python
   import flext_cli
   
   # Get configuration
   config = flext_cli.get_config()
   
   # Create helper
   helper = flext_cli.CLIHelper()
   
   # Use in your CLI
   @flext_cli.handle_service_result
   def my_command():
       return "Success!"
   ```

3. **Build Click commands**:
   ```python
   import click
   import flext_cli
   
   @click.command()
   @click.option("--count", type=flext_cli.PositiveInt)
   @flext_cli.measure_time()
   def process(count):
       # Your command logic
       pass
   ```

4. **Use domain entities** for complex CLI applications:
   ```python
   # Model your CLI operations
   command = flext_cli.CLICommand(name="task", command_line="python script.py")
   command.start_execution()
   # ... execute ...
   command.complete_execution(exit_code=0)
   ```

## Best Practices

1. **Configuration Management**:
   - Use environment variables with `FLEXT_CLI_` prefix
   - Leverage `CLIConfig` and `CLISettings` for structured configuration
   - Create contexts for different execution environments

2. **Error Handling**:
   - Use `@handle_service_result` for consistent error handling
   - Leverage `FlextResult` patterns from flext-core
   - Implement proper validation with business rules

3. **User Experience**:
   - Use Rich for beautiful output formatting
   - Implement progress indicators with spinners
   - Provide clear confirmation prompts for destructive operations

4. **Domain Modeling**:
   - Model CLI operations as domain entities
   - Use domain events for integration and audit trails
   - Implement business rules for data integrity

5. **Testing**:
   - The library provides comprehensive test coverage
   - Use Click's testing utilities for CLI testing
   - Mock external dependencies appropriately

## Library Architecture

The FLEXT CLI library follows Clean Architecture principles:

- **Domain Layer**: Entities, value objects, and business rules
- **Application Layer**: Use cases and application services  
- **Infrastructure Layer**: External integrations and frameworks
- **Interface Layer**: CLI commands, decorators, and user interface

This provides:
- ✅ **Type Safety**: Complete type coverage with MyPy
- ✅ **Domain-Driven Design**: Rich domain entities and business rules
- ✅ **Clean Architecture**: Clear separation of concerns
- ✅ **Enterprise Patterns**: Configuration, validation, error handling
- ✅ **Developer Experience**: Rich CLI development toolkit

## Contributing

When adding new examples:

1. Follow the naming convention: `##_descriptive_name.py`
2. Include comprehensive docstrings
3. Demonstrate specific library features
4. Provide clear run instructions
5. Update this README with the new example

## Support

For questions about the FLEXT CLI library:

- Check the main project documentation
- Review the test suites for additional usage examples
- Examine the source code for implementation details

The library is designed to be intuitive and self-documenting, with comprehensive type hints and docstrings throughout.