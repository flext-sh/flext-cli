# Development Guide - flext-cli


<!-- TOC START -->
- [📌 Quick Navigation](#-quick-navigation)
- [v0.10.0 Development Guidelines (Current)](#v0100-development-guidelines-current)
  - [Overview](#overview)
- [When to Use Each Pattern](#when-to-use-each-pattern)
  - [Use FlextService When](#use-flextservice-when)
  - [Use Simple Class When](#use-simple-class-when)
  - [Use Value Object (Pydantic) When](#use-value-object-pydantic-when)
- [Architecture Decision Flowchart](#architecture-decision-flowchart)
- [Code Organization Guidelines](#code-organization-guidelines)
  - [Module Structure](#module-structure)
  - [Direct Access Pattern](#direct-access-pattern)
- [Testing Guidelines (v0.10.0)](#testing-guidelines-v0100)
  - [Test Organization](#test-organization)
  - [Testing Simple Classes](#testing-simple-classes)
  - [Testing Value Objects](#testing-value-objects)
- [Contributing to v0.10.0](#contributing-to-v0100)
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

---

## 📌 Quick Navigation

- [v0.10.0 Development Guidelines (Current)](#v0100-development-guidelines-current) ← **Start Here**
- [v0.9.0 Development Guidelines (Historical Reference)](#v090-development-guidelines-historical-reference)

---

## v0.10.0 Development Guidelines (Current)

**Status**: 📝 Planned | **Release**: Q1 2025 | **Breaking Changes**: Yes

### Overview

FLEXT-CLI v0.10.0 follows a simplified architecture with clear guidelines for when to use services vs simple classes. This guide helps you make the right architectural decisions.

---

## When to Use Each Pattern

### Use FlextService When

**Requirements**:

- ✅ Class manages **mutable state** (commands, sessions, configuration)
- ✅ Class requires **dependency injection**
- ✅ Class needs **lifecycle management** (startup, shutdown, cleanup)
- ✅ Class has **complex initialization** with external dependencies

**Example - FlextCliCore (Stateful Service)**:

```python
from flext_core import FlextService

class FlextCliCore(FlextService[CliDataDict]):
    """Core service managing commands and sessions."""

    def __init__(self):
        super().__init__()
        self._commands: dict[str, Command] = {}  # MUTABLE STATE
        self._sessions: dict[str, Session] = {}  # MUTABLE STATE
        self._config: FlextCliSettings = ...       # MANAGED STATE

    def register_command(self, name: str, command: Command) -> FlextResult[bool]:
        """Register command - modifies internal state."""
        self._commands[name] = command
        return FlextResult[bool].| ok(value=True)
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
from flext_core import FlextResult
import json

class FlextCliFileTools:
    """Stateless file operations."""

    @staticmethod
    def read_json_file(path: str) -> FlextResult[dict]:
        """Read JSON file - no state needed."""
        try:
            with open(path) as f:
                return FlextResult[dict].ok(json.load(f))
        except Exception as e:
            return FlextResult[dict].fail(str(e))

    @staticmethod
    def write_json_file(path: str, data: dict) -> FlextResult[bool]:
        """Write JSON file - no state needed."""
        try:
            with open(path, 'w') as f:
                json.dump(data, f, indent=2)
            return FlextResult[bool].| ok(value=True)
        except Exception as e:
            return FlextResult[bool].fail(str(e))
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

**Example - FlextCliContext (Value Object)**:

```python
from flext_core import FlextModels
from pydantic import Field

class FlextCliContext(m.Value):
    """Immutable execution context."""
    command: str | None = None
    arguments: list[str] = Field(default_factory=list)
    environment_variables: dict[str, object] = Field(default_factory=dict)
    working_directory: str | None = None

    # No methods - just validated, immutable data
```

**When to use**:

- Configuration data
- Request/response models
- Event data
- Execution context

---

## Architecture Decision Flowchart

```
Does the class manage mutable state?
├─ YES → Use FlextService
│        Examples: FlextCliCore, FlextCli
│
└─ NO → Does it have behavior (business logic)?
    ├─ YES → Is it stateless utility functions?
    │   ├─ YES → Use Simple Class
    │   │        Examples: FlextCliFileTools, FlextCliFormatters
    │   └─ NO → Re-evaluate: might need FlextService
    │
    └─ NO → Is it just data with validation?
        └─ YES → Use Value Object (Pydantic)
                 Examples: FlextCliContext, FlextCliModels.*
```

---

## Code Organization Guidelines

### Module Structure

Follow the v0.10.0 module organization:

```
src/flext_cli/
├── Services (3-4 only)
│   ├── core.py              # FlextCliCore - stateful
│   ├── api.py               # FlextCli - facade
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
    ├── context.py           # FlextCliContext
    ├── models.py            # All Pydantic models
    └── config.py            # FlextCliSettings
```

### Direct Access Pattern

**Always use direct access** (no wrapper methods):

```python
# ✅ CORRECT - Direct access
cli = FlextCli()
cli.formatters.print("Hello", style="green")
cli.file_tools.read_json_file("config.json")
cli.prompts.confirm("Continue?")

# ❌ WRONG - Wrapper methods (v0.9.0 pattern)
# cli.print("Hello")              # REMOVED
# cli.read_json_file("config.json")  # REMOVED
# cli.confirm("Continue?")           # REMOVED
```

---

## Testing Guidelines (v0.10.0)

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

    assert result.is_success
    data = result.unwrap()
    assert isinstance(data, dict)

# No initialization needed - static methods
```

### Testing Value Objects

```python
import pytest
from flext_cli import FlextCliContext

def test_context_immutability():
    """Test context is immutable."""
    context = FlextCliContext(
        command="test",
        arguments=["arg1"]
    )

    # Cannot modify (immutable)
    with pytest.raises(Exception):
        context.command = "modified"

    # Create new instance for changes
    updated = context.model_copy(
        update={"command": "new_command"}
    )

    assert context.command == "test"
    assert updated.command == "new_command"
```

---

## Contributing to v0.10.0

### Implementation Checklist

Before implementing new features, review:

Key phases:

1. Documentation (complete)
2. Delete duplicates (validator.py, auth.py, testing.py)
3. Convert services to simple classes
4. Fix context (service → value object)
5. Remove API wrappers
6. Remove unused infrastructure
7. Reorganize tests
8. Quality gates

### Pull Request Guidelines

1. **Follow the Architecture**:
   - Services only for state
   - Simple classes for utilities
   - Value objects for data

2. **Use Direct Access**:
   - No wrapper methods
   - Clear ownership

3. **Quality Gates (MANDATORY)**:

   ```bash
   make validate  # Must pass 100%
   ```

4. **Test Organization**:
   - Tests in appropriate directories
   - No file > 30K lines
   - Feature-based organization

---

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

---

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

---

## Architecture Guidelines

### FLEXT Ecosystem Integration

Follow these patterns when extending flext-cli:

1. **CLI Patterns**: Use flext-cli abstractions
2. **Integration**: Follow flext-core patterns (see flext-core documentation)
3. **Type Safety**: Complete type annotations required
4. **Testing**: Comprehensive test coverage

### Code Organization

```python
# ✅ Correct - Use flext-cli patterns
from flext_cli import FlextCli

class ProjectCliService:
    """Project CLI service following FLEXT patterns."""

    def __init__(self):
        self._cli_api = FlextCli()

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

---

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
from flext_cli import FlextCli

def test_cli_api_operation():
    """Test CLI API operations."""
    api = FlextCli()

    result = api.process_command("test")

    assert result is not None
    assert "test" in str(result)

def test_error_handling():
    """Test proper error handling."""
    api = FlextCli()

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

---

## Contributing Guidelines

### Code Style

- Follow PEP 8 with 79-character line limit
- Use descriptive variable names
- Add docstrings for all public functions/classes
- Include type hints for all function signatures

### Pull Request Process

1. Create feature branch from main
2. Implement changes with tests
3. Run `make validate` to ensure quality
4. Submit pull request with description
5. Address review feedback
6. Merge after approval

### Commit Messages

Follow conventional commit format:

```
feat: add new CLI command for data export
fix: resolve authentication timeout issue
docs: update API documentation
test: add integration tests for config module
```

---

## Extension Development

### Adding New Commands

1. Create command handler:

```python
from flext_core import FlextBus
from flext_core import FlextSettings
from flext_core import FlextConstants
from flext_core import FlextContainer
from flext_core import FlextContext
from flext_core import FlextDecorators
from flext_core import FlextDispatcher
from flext_core import FlextExceptions
from flext_core import h
from flext_core import FlextLogger
from flext_core import x
from flext_core import FlextModels
from flext_core import FlextProcessors
from flext_core import p
from flext_core import FlextRegistry
from flext_core import FlextResult
from flext_core import FlextRuntime
from flext_core import FlextService
from flext_core import t
from flext_core import u
from flext_cli import FlextCli

class DataCommands(FlextService):
    """Data management commands."""

    def handle_export(self, **kwargs) -> FlextResult[bool]:
        """Handle data export command."""
        # Implementation
        return FlextResult[bool].| ok(value=True)
```

2. Register with CLI:

```python
from flext_cli import FlextCliCommands

cli = FlextCliCommands()
cli.register_command_group(
    name="data",
    commands={"export": data_handler.handle_export},
    description="Data management"
)
```

3. Add tests:

```python
def test_data_export_command():
    """Test data export functionality."""
    handler = DataCommands()
    result = handler.handle_export(format="json")
    assert result.is_success
```

### Custom Formatters

```python
from flext_cli import FlextCliOutput

class ProjectFormatters(FlextCliOutput):
    """Project-specific output formatters."""

    def format_project_data(self, data: dict) -> FlextResult[str]:
        """Format project-specific data."""
        # Custom formatting logic
        return FlextResult[str].ok("formatted_output")
```

---

## Debug and Troubleshooting

### Common Issues

1. **Import Errors**: Ensure proper module structure
2. **Type Errors**: Run `make type-check` for detailed analysis
3. **Test Failures**: Use `pytest -v` for verbose output
4. **Dependency Issues**: Try `poetry install --sync`

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

---

For architectural details, see [architecture.md](architecture.md).
For API usage, see [api-reference.md](api-reference.md).
