# flext-cli

<!-- TOC START -->

- [🚀 Key Features](#-key-features)
- [📦 Installation](#-installation)
- [🛠️ Usage](#-usage)
  - [Basic CLI Application](#basic-cli-application)
  - [File Operations](#file-operations)
  - [Interactive Prompts](#interactive-prompts)
  - [Tables and Formatting](#tables-and-formatting)
- [🏗️ Architecture](#-architecture)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)

<!-- TOC END -->

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**flext-cli** is the foundational command-line interface library for the FLEXT ecosystem. It provides robust CLI primitives, abstracting underlying libraries like Click and Rich to ensure consistent interaction patterns, strict type safety, and seamless integration with `flext-core`.

**Reviewed**: 2026-02-17 | **Version**: 0.10.0-dev

Part of the [FLEXT](https://github.com/flext-sh/flext) ecosystem.

## 🚀 Key Features

- **Robust CLI Framework**: Typesafe abstractions over `Click` and `Rich` for building complex commands.
- **File Operations**: Comprehensive support for reading and writing JSON, YAML, and CSV files with Pydantic validation.
- **Rich Output**: Pre-configured formatters and table styling powered by `Rich` and `Tabulate`.
- **Interactive Prompts**: Safe, validated user input handling for text, confirmations, and choices.
- **Configuration Management**: Strong configuration with Pydantic models and environment variable support.
- **Authentication Flow**: Built-in support for secure credential management and `flext-auth` integration.
- **Railway Oriented**: All operations return `FlextResult[T]` for predictable error handling.

## 📦 Installation

To install `flext-cli`:

```bash
pip install flext-cli
```

Or with Poetry:

```bash
poetry add flext-cli
```

## 🛠️ Usage

### Basic CLI Application

Create type-safe CLI commands with minimal boilerplate.

```python
from flext_cli import FlextCli, FlextResult as r

cli = FlextCli()

@cli.command()
def greet(name: str):
    cli.formatters.print(f"Hello, {name}!", style="green bold")

if __name__ == "__main__":
    cli.run()
```

### File Operations

Safely read and write structured data files.

```python
from flext_cli import FlextCli

cli = FlextCli()

# Write JSON
data = {"app": "myapp", "version": "1.0.0"}
cli.file_tools.write_json_file("config.json", data)

# Read JSON
result = cli.file_tools.read_json_file("config.json")
if result.is_success:
    config = result.unwrap()
    cli.formatters.print(f"Config loaded: {config}")
```

### Interactive Prompts

Securely collect user input with validation.

```python
from flext_cli import FlextCli

cli = FlextCli()

if cli.prompts.confirm("Do you want to continue?", default=True).unwrap():
    username = cli.prompts.prompt_text("Username:").unwrap()
    cli.formatters.print(f"Welcome back, {username}!")
```

### Tables and Formatting

Display data beautifully using `Tabulate` and `Rich`.

```python
from flext_cli import FlextCli

cli = FlextCli()

users = [
    {"name": "Alice", "role": "Admin"},
    {"name": "Bob", "role": "User"},
]

cli.output.format_data(
    data={"users": users},
    format_type="table"
).map(lambda table: cli.formatters.print(table))
```

## 🏗️ Architecture

`flext-cli` abstracts direct dependencies (Click, Rich) into clean service layers, ensuring that your CLI logic remains decoupled from specific libraries. It strictly adheres to FLEXT architectural patterns:

- **Models**: Pydantic models for strictly typed data structures.
- **Services**: All functionality is exposed via `FlextService` implementations.
- **Results**: Every operation returns a `FlextResult`, enforcing explicit error handling.

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](docs/development.md) for details on setting up your environment and submitting pull requests.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
