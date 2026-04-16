# Development Guide - flext-cli

<!-- TOC START -->
- [📌 Quick Navigation](#quick-navigation)
- [v0.12.0-dev Development Guidelines (Current)](#v0100-development-guidelines-current)
  - [Overview](#overview)
- [When to Use Each Pattern](#when-to-use-each-pattern)
  - [Use s When](#use-flextservice-when)
  - [Use Simple Class When](#use-simple-class-when)
  - [Use Value Object (Pydantic) When](#use-value-object-pydantic-when)
- [Architecture Decision Flowchart](#architecture-decision-flowchart)
- [Code Organization Guidelines](#code-organization-guidelines)
  - [Module Structure](#module-structure)
  - [Direct Access Pattern](#direct-access-pattern)
- [Testing Guidelines (v0.12.0-dev)](#testing-guidelines-v0100)
  - [Test Organization](#test-organization)
  - [Testing Simple Classes](#testing-simple-classes)
- [Contributing to v0.12.0-dev](#contributing-to-v0100)
  - [Implementation Checklist](#implementation-checklist)
  - [Pull Request Guidelines](#pull-request-guidelines)
- [v0.9.0 Development Guidelines (Historical Reference)](#v090-development-guidelines-historical-reference)
- [Development Setup](#development-setup)
  - [Prerequisites](#prerequisites)
  - [Initial Setup](#initial-setup)
- [Development Workflow](#development-workflow)
  - [Essential Commands](#essential-commands)
  - [Code Quality Standards](#code-quality-standards)
- [Architecture Guidelines](#architecture-guidelines)
  - [FLEXT Ecosystem Integration](#flext-ecosystem-integration)
  - [Code Organization](#code-organization)
- [Testing Guidelines](#testing-guidelines)
  - [Test Structure](#test-structure)
  - [Testing Patterns](#testing-patterns)
  - [Test Commands](#test-commands)
- [Contributing Guidelines](#contributing-guidelines)
  - [Code Style](#code-style)
  - [Pull Request Process](#pull-request-process)
  - [Commit Messages](#commit-messages)
- [Extension Development](#extension-development)
  - [Adding New Commands](#adding-new-commands)
  - [Custom Formatters](#custom-formatters)
- [Debug and Troubleshooting](#debug-and-troubleshooting)
  - [Common Issues](#common-issues)
  - [Debug Commands](#debug-commands)
<!-- TOC END -->

**Contributing guidelines and development workflow for flext-cli.**

**Last Updated**: 2025-01-24 | **Version**: 0.10.0

______________________________________________________________________

## 📌 Quick Navigation

- [v0.12.0-dev Development Guidelines (Current)](#v0100-development-guidelines-current) ← **Start Here**
- [v0.9.0 Development Guidelines (Historical Reference)](#v090-development-guidelines-historical-reference)

______________________________________________________________________

## v0.12.0-dev Development Guidelines (Current)

**Status**: 📝 Planned | **Release**: Q1 2025 | **Breaking Changes**: Yes

### Overview

FLEXT-CLI v0.12.0-dev follows a simplified architecture with clear guidelines for when to use services vs simple classes. This guide helps you make the right architectural decisions.

______________________________________________________________________

## When to Use Each Pattern

### Use s When

**Requirements**:

- ✅ Class manages **mutable state** (commands, sessions, configuration)
- ✅ Class requires **dependency injection**
- ✅ Class needs **lifecycle management** (startup, shutdown, cleanup)
- ✅ Class has **complex initialization** with external dependencies

**Example - FlextCliCore (Stateful Service)**:

```python
from flext_core import s

class FlextCliCore(s[CliDataDict]):
    """Core service managing commands and sessions."""

    def __init__(self):
        super().__init__()
        self._commands: Mapping[str, Command] = {}  # MUTABLE STATE
        self._sessions: Mapping[str, Session] = {}  # MUTABLE STATE
        self._config: FlextCliSettings = ...       # MANAGED STATE

    def register_command(self, name: str, command: Command) -> p.Result[bool]:
        """Register command - modifies internal state."""
        self._commands[name] = command
        return r[bool].| ok(value=True)
```

**When NOT to use**:

- ❌ Operations are stateless (just transformations)
- ❌ No initialization needed
- ❌ Methods could all be static
- ❌ Just grouping related functions

### Use Simple Class When

**Requirements**:

- ✅ Class is **stateless** (no internal state to manage)
- ✅ Methods could be **static** (no `self` needed)
- ✅ **No dependency injection** required
- ✅ Just utility functions grouped together
- ✅ Pure **I/O operations** (read/write files)

**Example - FlextCliFileTools (Simple Utility Class)**:

```python
from flext_core import r, p
import json

class FlextCliFileTools:
    """Stateless file operations."""

    @staticmethod
    def read_json_file(path: str) -> p.Result[dict]:
        """Read JSON file - no state needed."""
        try:
            with open(path) as f:
                return r[dict].ok(json.load(f))
        except Exception as e:
            return r[dict].fail(str(e))

    @staticmethod
    def write_json_file(path: str, data: dict) -> p.Result[bool]:
        """Write JSON file - no state needed."""
        try:
            with open(path, 'w') as f:
                json.dump(data, f, indent=2)
            return r[bool].| ok(value=True)
        except Exception as e:
            return r[bool].fail(str(e))
```

**Benefits**:

- No initialization overhead
- Clear that it's stateless
- Can use static methods
- Easy to test

### Use Value Object (Pydantic) When

**Requirements**:

- ✅ Class is **immutable data**
- ✅ Compared by **value**, not identity
- ✅ **No behavior** (no business logic)
- ✅ Just data **validation and structure**
- ✅ Configuration or context data

______________________________________________________________________

## Architecture Decision Flowchart

```
Does the class manage mutable state?
├─ YES → Use s
│        Examples: FlextCliCore, cli
│
└─ NO → Does it have behavior (business logic)?
    ├─ YES → Is it stateless utility functions?
    │   ├─ YES → Use Simple Class
    │   │        Examples: FlextCliFileTools, FlextCliFormatters
    │   └─ NO → Re-evaluate: might need s
    │
    └─ NO → Is it just data with validation?
        └─ YES → Use Value Object (Pydantic)
                 Examples: FlextCliModels.*
```

______________________________________________________________________

## Code Organization Guidelines

### Module Structure

Follow the v0.12.0-dev module organization:

```
src/flext_cli/
├── Services (3-4 only)
│   ├── core.py              # FlextCliCore - stateful
│   ├── api.py               # cli - facade
│   └── cmd.py               # FlextCliCmd - command execution
│
├── Simple Classes (utilities)
│   ├── file_tools.py        # File I/O
│   ├── formatters.py        # Rich formatting
│   ├── tables.py            # Table generation
│   ├── output.py            # Output management
│   ├── prompts.py           # User input
│   └── debug.py             # Debug utilities
│
└── Data Models (value objects)
    ├── models.py            # All Pydantic models
    └── settings.py            # FlextCliSettings
```

### Direct Access Pattern

**Always use direct access** (no wrapper methods):

```python
# ✅ CORRECT - Direct access
cli.formatters.print("Hello", style="green")
cli.file_tools.read_json_file("settings.json")
cli.prompts.confirm("Continue?")

# ❌ WRONG - Wrapper methods (v0.9.0 pattern)
# cli.print("Hello")              # REMOVED
# cli.read_json_file("settings.json")  # REMOVED
# cli.confirm("Continue?")           # REMOVED
```

______________________________________________________________________

## Testing Guidelines (v0.12.0-dev)

### Test Organization

Tests are now organized by feature area:

```
tests/
├── unit/
│   ├── core/              # Core functionality tests
│   │   ├── test_api.py
│   │   ├── test_service_base.py
│   │   └── test_singleton.py
│   ├── io/                # I/O operations tests
│   │   ├── test_json_operations.py
│   │   ├── test_yaml_operations.py
│   │   └── test_csv_operations.py
│   ├── formatting/        # Output formatting tests
│   │   ├── test_rich_formatters.py
│   │   ├── test_tables.py
│   │   └── test_output.py
│   └── cli/               # CLI framework tests
│       ├── test_click_wrapper.py
│       ├── test_commands.py
│       └── test_execution.py
│
├── integration/           # Integration tests
└── fixtures/              # Test utilities (moved from src/)
```

### Testing Simple Classes

```python
import pytest
from flext_cli import FlextCliFileTools


def test_read_json_file():
    """Test static method on simple class."""
    # Simple classes use static methods
    result = FlextCliFileTools.read_json_file("test.json")

    assert result.success
    data = result.unwrap()
    assert isinstance(data, dict)


# No initialization needed - static methods
```

______________________________________________________________________

## Contributing to v0.12.0-dev

### Implementation Checklist

Before implementing new features, review:

Key phases:

1. Documentation (complete)
1. Delete duplicates (validator.py, auth.py, testing.py)
1. Convert services to simple classes
1. Fix context (service → value object)
1. Remove API wrappers
1. Remove unused infrastructure
1. Reorganize tests
1. Quality gates

### Pull Request Guidelines

1. **Follow the Architecture**:

   - Services only for state
   - Simple classes for utilities
   - Value objects for data

1. **Use Direct Access**:

   - No wrapper methods
   - Clear ownership

1. **Quality Gates (MANDATORY)**:

   ```bash
   make validate  # Must pass 100%
   ```

1. **Test Organization**:

   - Tests in appropriate directories
   - No file > 30K lines
   - Feature-based organization

______________________________________________________________________

## v0.9.0 Development Guidelines (Historical Reference)

**Note**: The following documentation describes v0.9.0 patterns. This is kept for historical reference during the migration period.

## Development Setup

### Prerequisites

- Python 3.13+
- Poetry for dependency management
- Make for build automation
- Git for version control

### Initial Setup

```bash
# Clone repository
git clone https://github.com/flext-sh/flext-cli.git
cd flext-cli

# Complete development setup
make setup

# Install pre-commit hooks
poetry run pre-commit install
```

______________________________________________________________________

## Development Workflow

### Essential Commands

```bash
make setup          # Complete development environment setup
make validate       # All quality checks (lint + type + test)
make test          # Run test suite
make lint          # Code linting with Ruff
make type-check    # MyPy type checking
make format        # Auto-format code
make clean         # Clean build artifacts
```

### Code Quality Standards

- **Type Safety**: Complete Python 3.13+ type annotations
- **Linting**: Zero Ruff violations
- **Testing**: Comprehensive test coverage
- **Documentation**: All public APIs documented

______________________________________________________________________

## Architecture Guidelines

### FLEXT Ecosystem Integration

Follow these patterns when extending flext-cli:

1. **CLI Patterns**: Use flext-cli abstractions
1. **Integration**: Follow flext-core patterns (see flext-core documentation)
1. **Type Safety**: Complete type annotations required
1. **Testing**: Comprehensive test coverage

### Code Organization

```python
# ✅ Correct - Use flext-cli patterns
from flext_cli import cli


class ProjectCliService:
    """Project CLI service following FLEXT patterns."""

    def __init__(self):
        self._cli_api = cli()

    def process_data(self, data: dict):
        """Process CLI data."""
        if not data:
            return "Data cannot be empty"

        # Business logic
        return {"processed": True, "data": data}


# ❌ Avoid - Direct framework imports
# import click  # Use flext-cli abstractions instead
# import rich   # Use FlextCliOutput instead
```

______________________________________________________________________

## Testing Guidelines

### Test Structure

```
tests/
├── unit/              # Unit tests for individual components
├── integration/       # Integration tests
├── conftest.py       # Shared fixtures
└── test_*.py         # Test modules
```

### Testing Patterns

```python
import pytest
from flext_cli import cli


def test_cli_api_operation():
    """Test CLI API operations."""
    api = cli()

    result = api.process_command("test")

    assert result is not None
    assert "test" in str(result)


def test_error_handling():
    """Test proper error handling."""
    api = cli()

    result = api.process_command("")  # Invalid input

    # Test appropriate error handling
    assert result or "error" in str(result)
```

### Test Commands

```bash
# Run all tests
pytest tests/

# Unit tests only
pytest tests/unit/

# With coverage
pytest tests/ --cov=src --cov-report=term-missing

# Specific test file
pytest tests/unit/test_api.py -v
```

______________________________________________________________________

## Contributing Guidelines

### Code Style

- Follow PEP 8 with 79-character line limit
- Use descriptive variable names
- Add docstrings for all public functions/classes
- Include type hints for all function signatures

### Pull Request Process

1. Create feature branch from main
1. Implement changes with tests
1. Run `make validate` to ensure quality
1. Submit pull request with description
1. Address review feedback
1. Merge after approval

### Commit Messages

Follow conventional commit format:

```
feat: add new CLI command for data export
fix: resolve authentication timeout issue
docs: update API documentation
test: add integration tests for settings module
```

______________________________________________________________________

## Extension Development

### Adding New Commands

1. Create command handler:

```python
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
from flext_cli import cli

class DataCommands(s):
    """Data management commands."""

    def handle_export(self, **kwargs) -> p.Result[bool]:
        """Handle data export command."""
        # Implementation
        return r[bool].| ok(value=True)
```

2. Register with CLI:

```python
from flext_cli import FlextCliCommands

cli = FlextCliCommands()
cli.register_command_group(
    name="data",
    commands={"export": data_handler.handle_export},
    description="Data management",
)
```

3. Add tests:

```python
def test_data_export_command():
    """Test data export functionality."""
    handler = DataCommands()
    result = handler.handle_export(format="json")
    assert result.success
```

### Custom Formatters

```python
from flext_cli import FlextCliOutput


class ProjectFormatters(FlextCliOutput):
    """Project-specific output formatters."""

    def format_project_data(self, data: dict) -> p.Result[str]:
        """Format project-specific data."""
        # Custom formatting logic
        return r[str].ok("formatted_output")
```

______________________________________________________________________

## Debug and Troubleshooting

### Common Issues

1. **Import Errors**: Ensure proper module structure
1. **Type Errors**: Run `make type-check` for detailed analysis
1. **Test Failures**: Use `pytest -v` for verbose output
1. **Dependency Issues**: Try `poetry install --sync`

### Debug Commands

```bash
# Verbose test output
pytest tests/ -v -s

# Type checking with details
poetry run mypy src/ --show-error-codes

# Dependency tree analysis
poetry show --tree

# Development environment info
flext debug info
```

______________________________________________________________________

For architectural details, see [architecture.md](architecture.md).
For API usage, see [api-reference.md](api-reference.md).
