# FLEXT-CLI Examples - Library Usage Guide

<!-- TOC START -->

- [📚 Overview](#-overview)
- [🎯 What is flext-cli](#-what-is-flext-cli)
- [📖 Examples](#-examples)
  - [Getting Started](#getting-started)
  - [Core Features](#core-features)
  - [Advanced Features](#advanced-features)
  - [Integration](#integration)
- [🚀 Quick Start](#-quick-start)
- [📦 Available Modules](#-available-modules)
- [🏗️ Architecture](#-architecture)
- [💡 Usage Patterns](#-usage-patterns)
  - [Pattern 1: Direct cli Usage](#pattern-1-direct-flextcli-usage)
  - [Pattern 2: Service-Specific Import](#pattern-2-service-specific-import)
  - [Pattern 3: With r](#pattern-3-with-flextresult)
  - [Pattern 4: With Configuration](#pattern-4-with-configuration)
- [🎓 Learning Path](#-learning-path)
- [📝 Key Concepts](#-key-concepts)
  - [1. r Railway Pattern](#1-flextresult-railway-pattern)
  - [2. Property-Based Service Access](#2-property-based-service-access)
  - [3. Configuration Management](#3-configuration-management)
  - [4. Type Safety](#4-type-safety)
- [🔧 Common Use Cases](#-common-use-cases)
  - [CLI Application Development](#cli-application-development)
  - [Data Processing Pipeline](#data-processing-pipeline)
  - [Interactive Tool](#interactive-tool)
- [📚 Additional Resources](#-additional-resources)
- [🆘 Getting Help](#-getting-help)
- [✅ Best Practices](#-best-practices)

<!-- TOC END -->

**IMPORTANT**: flext-cli is a **LIBRARY**, not a CLI application. Import `cli` and use it in your Python applications.

## 📚 Overview

This directory contains comprehensive examples demonstrating all flext-cli capabilities. Each example focuses on specific modules and features, showing how to use them through the `cli` API.

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

1. **[ex_01_getting_started.py](ex_01_getting_started.py)** - Start here!

   - Basic cli initialization
   - Accessing domain services
   - r railway pattern
   - Core operations

1. **[ex_02_output_formatting.py](ex_02_output_formatting.py)** - Rich output

   - Styled messages (success, error, warning, info)
   - Table display (Rich and Tabulate)
   - Data formatting (JSON, YAML)
   - Progress bars and spinners

1. **[ex_03_interactive_prompts.py](ex_03_interactive_prompts.py)** - User interaction

   - Confirmation prompts
   - Text input
   - Choice selection
   - Password input
   - Input validation

### Core Features

1. **[ex_04_file_operations.py](ex_04_file_operations.py)** - File handling

   - File reading/writing
   - Path validation
   - Directory operations
   - JSON/YAML file handling

1. **[ex_05_authentication.py](ex_05_authentication.py)** - Auth patterns

   - Token management
   - Authorization headers
   - Session management
   - Protected operations

1. **[ex_06_settings.py](ex_06_settings.py)** - Settings management

   - FlextCliSettings usage
   - Environment variables
   - Pydantic validation
   - Multiple profiles

### Advanced Features

1. **[ex_07_plugin_system.py](ex_07_plugin_system.py)** - Plugins

   - Plugin loading
   - Custom plugin development
   - Plugin lifecycle

1. **[ex_08_shell_interaction.py](ex_08_shell_interaction.py)** - Interactive shell

   - REPL functionality
   - Command history
   - Custom commands

1. **[ex_09_performance_optimization.py](ex_09_performance_optimization.py)** - Performance

   - Caching strategies
   - Lazy loading
   - Performance measurement

1. **[ex_10_testing_utilities.py](ex_10_testing_utilities.py)** - Testing

   - Mock scenarios
   - Output capture
   - Test utilities

### Integration

1. **[ex_11_complete_integration.py](ex_11_complete_integration.py)** - Everything together
    - Complete workflow example
    - Module integration
    - Best practices

## 🚀 Quick Start

```text
# Install flext-cli
pip install flext-cli

# Import and use
from examples import c
from flext_cli import cli

# Initialize

# Use features
cli.print_success("Hello, World!")

# Display data
data = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]
cli.display_rich_table(data, title="Users")

# Interactive prompt
name = cli.prompt("Enter your name:")
cli.print("Hello!", style=c.Cli.MessageStyles.BOLD_GREEN)
```

## 📦 Available Modules

Access all modules through the `cli` facade:

```text
# All services available directly via MRO inheritance:
cli.print_success("msg")  # FlextCliOutput
cli.print("msg", style=c.Cli.MessageStyles.BOLD)  # FlextCliFormatters
cli.display_rich_table(data)  # FlextCliTables
cli.prompt("Enter name:")  # FlextCliPrompts
cli.read_json_file("f.json")  # FlextCliFileTools
cli.settings  # FlextCliSettings
```

Or import modules directly:

```text
from flext_cli import (
    cli,
    FlextCliSettings,
    FlextCliOutput,
    FlextCliFormatters,
    FlextCliTables,
    # ... etc
)
```

## 🏗️ Architecture

flext-cli follows the FLEXT ecosystem architecture:

- **cli** - Main facade providing unified access
- **Services** - Specialized modules (Output, Formatters, Tables, etc.)
- **r** - Railway-oriented error handling (from flext-core)
- **FlextSettings** - Pydantic-based configuration
- **Type Safety** - Complete type hints throughout

## 💡 Usage Patterns

### Pattern 1: Direct cli Usage

```text
from flext_cli import cli

cli.print_success("Operation successful")
```

### Pattern 2: Service-Specific Import

```text
from flext_cli import FlextCliOutput

output = FlextCliOutput()
output.error("Something went wrong")
```

### Pattern 3: With r

```text
from flext_cli import cli
from flext_core import FlextBus
from flext_core import FlextSettings
from flext_core import FlextConstants
from flext_core import FlextContainer
from flext_core import FlextContext
from flext_core import d
from flext_core import FlextDispatcher
from flext_core import e
from flext_core import h
from flext_core import x
from flext_core import FlextModels
from flext_core import FlextProcessors
from flext_core import p
from flext_core import FlextRegistry
from flext_core import r, p
from flext_core import u
from flext_core import s
from flext_core import t
from flext_core import u


def process_data(data: dict) -> p.Result[dict]:
    
    if not data:
        return r[dict].fail("Data is empty")

    cli.print("Processing...")
    # ... processing logic ...

    return r[dict].ok(processed_data)
```

### Pattern 4: With Configuration

```text
from flext_cli import cli, FlextCliSettings

settings = FlextCliSettings(
    debug=True,
    log_level="DEBUG",
)

cli.print(f"Debug mode: {settings.debug}")
```

## 🎓 Learning Path

**Beginner** (Start here):

1. ex_01_getting_started.py
1. ex_02_output_formatting.py
1. ex_03_interactive_prompts.py

**Intermediate**: 4. ex_04_file_operations.py 5. ex_05_authentication.py 6. ex_06_settings.py

**Advanced**: 7. ex_07_plugin_system.py 8. ex_08_shell_interaction.py 9. ex_09_performance_optimization.py 10. ex_10_testing_utilities.py

**Integration**: 11. ex_11_complete_integration.py

## 📝 Key Concepts

### 1. r Railway Pattern

All operations return `r` for type-safe error handling:

```text
result = cli.read_json_file("settings.json")

if result.success:
    data = result.value
else:
    error = result.error
```

### 2. Direct MRO Method Access

Access all services directly on the cli instance:

```text
cli.print_success("Message")  # Direct MRO method
cli.display_rich_table(data)  # Direct MRO method
```

### 3. Configuration Management

Use FlextCliSettings for settings:

```text
settings = FlextCliSettings(
    debug=True,
    environment="development",
)
```

### 4. Type Safety

Complete type hints for IDE support:

```text
from flext_cli import cli
from flext_core import FlextBus
from flext_core import FlextSettings
from flext_core import FlextConstants
from flext_core import FlextContainer
from flext_core import FlextContext
from flext_core import d
from flext_core import FlextDispatcher
from flext_core import e
from flext_core import h
from flext_core import x
from flext_core import FlextModels
from flext_core import FlextProcessors
from flext_core import p
from flext_core import FlextRegistry
from flext_core import r, p
from flext_core import u
from flext_core import s
from flext_core import t
from flext_core import u


def typed_operation(data: dict) -> p.Result[dict]:
    return cli.write_json_file("output.json", data)
```

## 🔧 Common Use Cases

### CLI Application Development

```text
from flext_cli import cli


def main():
    
    # Get user input
    name = cli.prompt("Enter project name:")

    # Process
    cli.print(f"Creating project: {name}")

    # Show results
    cli.print_success("Project created!")


if __name__ == "__main__":
    main()
```

### Data Processing Pipeline

```text
from flext_cli import cli
from flext_core import FlextBus
from flext_core import FlextSettings
from flext_core import FlextConstants
from flext_core import FlextContainer
from flext_core import FlextContext
from flext_core import d
from flext_core import FlextDispatcher
from flext_core import e
from flext_core import h
from flext_core import x
from flext_core import FlextModels
from flext_core import FlextProcessors
from flext_core import p
from flext_core import FlextRegistry
from flext_core import r, p
from flext_core import u
from flext_core import s
from flext_core import t
from flext_core import u


def process_pipeline(input_file: str) -> p.Result[dict]:
    
    # Read input
    data_result = cli.read_json_file(input_file)
    if data_result.failure:
        return r[dict].fail(f"Read failed: {data_result.error}")

    # Process
    cli.print("Processing data...")
    processed = transform_data(data_result.value)

    # Write output
    write_result = cli.write_json_file("output.json", processed)
    if write_result.failure:
        return r[dict].fail(f"Write failed: {write_result.error}")

    cli.print_success("Pipeline complete!")
    return r[dict].ok(processed)
```

### Interactive Tool

```text
from flext_cli import cli


def interactive_tool():
    
    while True:
        action = cli.prompt_choice(
            "Choose action:", choices=["Process", "View", "Exit"]
        )

        if action == "Exit":
            break

        if action == "Process":
            cli.print("Processing...")
            # ... processing logic ...
            cli.print_success("Done!")
```

## 📚 Additional Resources

- **Source Code**: [../src/flext_cli/](../src/flext_cli/)
- **Tests**: [../tests/](../tests/)
- **Main Documentation**: [../README.md](../README.md)
- **Development Guide**: [../AGENTS.md](../AGENTS.md)

## 🆘 Getting Help

1. Review the examples in order (01-11)
1. Check the inline code documentation
1. Refer to [../README.md](../README.md) for API reference
1. See [../AGENTS.md](../AGENTS.md) for development guidelines

## ✅ Best Practices

1. **Use r** for all operations
1. **Initialize cli once** and reuse
1. **Access services via MRO methods** (cli.print_success, cli.prompt)
1. **Handle errors explicitly** with r patterns
1. **Use type hints** for better IDE support
1. **Configure via FlextCliSettings** for environment-specific settings
1. **Combine modules** for complete functionality

______________________________________________________________________

**Remember**: flext-cli is a **LIBRARY** - import and use it in your applications!

Copyright (c) 2025 FLEXT Team. All rights reserved.
