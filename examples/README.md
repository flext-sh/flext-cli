# FLEXT-CLI Examples - Library Usage Guide

**IMPORTANT**: flext-cli is a **LIBRARY**, not a CLI application. Import `FlextCli` and use it in your Python applications.

## 📚 Overview

This directory contains comprehensive examples demonstrating all flext-cli capabilities. Each example focuses on specific modules and features, showing how to use them through the `FlextCli` API.

## 🎯 What is flext-cli

flext-cli is a production-ready Python library that provides:

- **Click abstraction** - No direct Click imports needed
- **Rich terminal output** - Beautiful formatted output
- **Table formatting** - 22+ table formats via Tabulate
- **Interactive prompts** - User input with validation
- **File operations** - Type-safe file handling
- **Authentication** - Token management
- **Plugin system** - Extensible architecture
- **Performance utilities** - Caching and optimization

## 📖 Examples

### Getting Started

1. **[01_getting_started.py](01_getting_started.py)** - Start here!
   - Basic FlextCli initialization
   - Accessing domain services
   - FlextCore.Result railway pattern
   - Core operations

2. **[02_output_formatting.py](02_output_formatting.py)** - Rich output
   - Styled messages (success, error, warning, info)
   - Table display (Rich and Tabulate)
   - Data formatting (JSON, YAML)
   - Progress bars and spinners

3. **[03_interactive_prompts.py](03_interactive_prompts.py)** - User interaction
   - Confirmation prompts
   - Text input
   - Choice selection
   - Password input
   - Input validation

### Core Features

4. **[04_file_operations.py](04_file_operations.py)** - File handling
   - File reading/writing
   - Path validation
   - Directory operations
   - JSON/YAML file handling

5. **[05_authentication.py](05_authentication.py)** - Auth patterns
   - Token management
   - Authorization headers
   - Session management
   - Protected operations

6. **[06_configuration.py](06_configuration.py)** - Config management
   - FlextCliConfig usage
   - Environment variables
   - Pydantic validation
   - Multiple profiles

### Advanced Features

7. **[07_plugin_system.py](07_plugin_system.py)** - Plugins
   - Plugin loading
   - Custom plugin development
   - Plugin lifecycle

8. **[08_shell_interaction.py](08_shell_interaction.py)** - Interactive shell
   - REPL functionality
   - Command history
   - Custom commands

9. **[09_performance_optimization.py](09_performance_optimization.py)** - Performance
   - Caching strategies
   - Lazy loading
   - Performance measurement

10. **[10_testing_utilities.py](10_testing_utilities.py)** - Testing
    - Mock scenarios
    - Output capture
    - Test utilities

### Integration

11. **[11_complete_integration.py](11_complete_integration.py)** - Everything together
    - Complete workflow example
    - Module integration
    - Best practices

## 🚀 Quick Start

```python
# Install flext-cli
pip install flext-cli

# Import and use
from flext_cli import FlextCli

# Initialize
cli = FlextCli()

# Use features
cli.output.success("Hello, World!")

# Display data
data = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]
cli.tables.display_rich_table(data, title="Users")

# Interactive prompt
name = cli.prompts.prompt("Enter your name:")
cli.output.info(f"Hello, {name}!")
```

## 📦 Available Modules

Access all modules through the `FlextCli` facade:

```python
cli = FlextCli()

# Domain services (accessed via properties)
cli.core           # FlextCliCore - Core functionality
cli.output         # FlextCliOutput - Styled messages
cli.formatters     # FlextCliFormatters - Data formatting
cli.tables         # FlextCliTables - Table display
cli.prompts        # FlextCliPrompts - User input
cli.file_tools     # FlextCliFileTools - File operations
cli.auth           # FlextCliAuth - Authentication
cli.plugins        # FlextCliPlugins - Plugin system
cli.shell          # FlextCliShell - Interactive shell
cli.performance    # FlextCliPerformance - Optimization
cli.processors     # FlextCliProcessors - Data processing
```

Or import modules directly:

```python
from flext_cli import (
    FlextCli,
    FlextCliConfig,
    FlextCliOutput,
    FlextCliFormatters,
    FlextCliTables,
    # ... etc
)
```

## 🏗️ Architecture

flext-cli follows the FLEXT ecosystem architecture:

- **FlextCli** - Main facade providing unified access
- **Domain Services** - Specialized modules (Output, Formatters, Tables, etc.)
- **FlextCore.Result** - Railway-oriented error handling (from flext-core)
- **FlextCore.Config** - Pydantic-based configuration
- **Type Safety** - Complete type hints throughout

## 💡 Usage Patterns

### Pattern 1: Direct FlextCli Usage

```python
from flext_cli import FlextCli

cli = FlextCli()
cli.output.success("Operation successful")
```

### Pattern 2: Service-Specific Import

```python
from flext_cli import FlextCliOutput

output = FlextCliOutput()
output.error("Something went wrong")
```

### Pattern 3: With FlextCore.Result

```python
from flext_cli import FlextCli
from flext_core import FlextCore

def process_data(data: dict) -> FlextCore.Result[dict]:
    cli = FlextCli()

    if not data:
        return FlextCore.Result[dict].fail("Data is empty")

    cli.output.info("Processing...")
    # ... processing logic ...

    return FlextCore.Result[dict].ok(processed_data)
```

### Pattern 4: With Configuration

```python
from flext_cli import FlextCli, FlextCliConfig

config = FlextCliConfig(
    debug=True,
    log_level="DEBUG",
)

cli = FlextCli()
cli.output.info(f"Debug mode: {config.debug}")
```

## 🎓 Learning Path

**Beginner** (Start here):

1. 01_getting_started.py
2. 02_output_formatting.py
3. 03_interactive_prompts.py

**Intermediate**: 4. 04_file_operations.py 5. 05_authentication.py 6. 06_configuration.py

**Advanced**: 7. 07_plugin_system.py 8. 08_shell_interaction.py 9. 09_performance_optimization.py 10. 10_testing_utilities.py

**Integration**: 11. 11_complete_integration.py

## 📝 Key Concepts

### 1. FlextCore.Result Railway Pattern

All operations return `FlextCore.Result` for type-safe error handling:

```python
result = cli.file_tools.read_json("config.json")

if result.is_success:
    data = result.value
else:
    error = result.error
```

### 2. Property-Based Service Access

Access domain services through properties:

```python
cli = FlextCli()
cli.output.success("Message")    # Not: cli.get_output().success()
cli.tables.display_rich_table()  # Not: cli.get_tables().display()
```

### 3. Configuration Management

Use FlextCliConfig for settings:

```python
config = FlextCliConfig(
    debug=True,
    environment="development",
)
```

### 4. Type Safety

Complete type hints for IDE support:

```python
from flext_cli import FlextCli
from flext_core import FlextCore

def typed_operation(data: dict) -> FlextCore.Result[dict]:
    cli = FlextCli()
    return cli.file_tools.write_json("output.json", data)
```

## 🔧 Common Use Cases

### CLI Application Development

```python
from flext_cli import FlextCli

def main():
    cli = FlextCli()

    # Get user input
    name = cli.prompts.prompt("Enter project name:")

    # Process
    cli.output.info(f"Creating project: {name}")

    # Show results
    cli.output.success("Project created!")

if __name__ == "__main__":
    main()
```

### Data Processing Pipeline

```python
from flext_cli import FlextCli
from flext_core import FlextCore

def process_pipeline(input_file: str) -> FlextCore.Result[dict]:
    cli = FlextCli()

    # Read input
    data_result = cli.file_tools.read_json(input_file)
    if data_result.is_failure:
        return FlextCore.Result[dict].fail(f"Read failed: {data_result.error}")

    # Process
    cli.output.info("Processing data...")
    processed = transform_data(data_result.value)

    # Write output
    write_result = cli.file_tools.write_json("output.json", processed)
    if write_result.is_failure:
        return FlextCore.Result[dict].fail(f"Write failed: {write_result.error}")

    cli.output.success("Pipeline complete!")
    return FlextCore.Result[dict].ok(processed)
```

### Interactive Tool

```python
from flext_cli import FlextCli

def interactive_tool():
    cli = FlextCli()

    while True:
        action = cli.prompts.select(
            "Choose action:",
            choices=["Process", "View", "Exit"]
        )

        if action == "Exit":
            break

        if action == "Process":
            cli.output.info("Processing...")
            # ... processing logic ...
            cli.output.success("Done!")
```

## 📚 Additional Resources

- **Source Code**: [../src/flext_cli/](../src/flext_cli/)
- **Tests**: [../tests/](../tests/)
- **Main Documentation**: [../README.md](../README.md)
- **Development Guide**: [../CLAUDE.md](../CLAUDE.md)

## 🆘 Getting Help

1. Review the examples in order (01-11)
2. Check the inline code documentation
3. Refer to [../README.md](../README.md) for API reference
4. See [../CLAUDE.md](../CLAUDE.md) for development guidelines

## ✅ Best Practices

1. **Use FlextCore.Result** for all operations
2. **Initialize FlextCli once** and reuse
3. **Access services via properties** (cli.output, cli.tables)
4. **Handle errors explicitly** with FlextCore.Result patterns
5. **Use type hints** for better IDE support
6. **Configure via FlextCliConfig** for environment-specific settings
7. **Combine modules** for complete functionality

---

**Remember**: flext-cli is a **LIBRARY** - import and use it in your applications!

Copyright (c) 2025 FLEXT Team. All rights reserved.
