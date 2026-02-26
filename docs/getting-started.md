# Getting Started with flext-cli

<!-- TOC START -->

- [📌 Quick Navigation](#quick-navigation)
- [v0.10.0 Getting Started (Current)](#v0100-getting-started-current)
  - [Overview](#overview)
- [Prerequisites](#prerequisites)
  - [System Requirements](#system-requirements)
  - [FLEXT Ecosystem Integration](#flext-ecosystem-integration)
- [Installation](#installation)
  - [Development Setup](#development-setup)
  - [As a Dependency](#as-a-dependency)
- [Quick Start (v0.10.0)](#quick-start-v0100)
  - [🚀 Your First CLI Application](#your-first-cli-application)
  - [📊 Working with Tables](#working-with-tables)
  - [📁 File Operations](#file-operations)
  - [🔄 Railway-Oriented Programming](#railway-oriented-programming)
- [Development Workflow (v0.10.0)](#development-workflow-v0100)
  - [Quality Gates](#quality-gates)
  - [Development Pattern (v0.10.0)](#development-pattern-v0100)
  - [Testing Your CLI Code](#testing-your-cli-code)
- [Next Steps](#next-steps)
  - [Learn More](#learn-more)
  - [Migration from v0.9.0](#migration-from-v090)
- [Related Documentation](#related-documentation)
  - [Examples](#examples)
- [v0.9.0 Getting Started (Historical Reference)](#v090-getting-started-historical-reference)
- [Development Patterns (v0.9.0)](#development-patterns-v090)
  - [Working Development Pattern](#working-development-pattern)
- [Quality Validation](#quality-validation)
  - [Validation Commands](#validation-commands)
  - [Implementation Verification](#implementation-verification)
- [Next Steps](#next-steps)

<!-- TOC END -->

**Installation and setup guide for the FLEXT ecosystem CLI foundation library.**

**Last Updated**: 2025-01-24 | **Version**: 0.10.0

---

## 📌 Quick Navigation

- [v0.10.0 Getting Started (Current)](#v0100-getting-started-current) ← **Start Here**
- [v0.9.0 Getting Started (Historical Reference)](#v090-getting-started-historical-reference)

---

## v0.10.0 Getting Started (Current)

**Status**: 📝 Planned | **Release**: Q1 2025 | **Breaking Changes**: Yes

### Overview

flext-cli v0.10.0 is a simplified, streamlined CLI foundation library for the FLEXT ecosystem. It provides:

- **Direct Access API**: Clear ownership with `cli.formatters.*`, `cli.file_tools.*`, `cli.prompts.*`
- **Services for State Only**: FlextService used only where needed (3-4 classes)
- **Simple Utilities**: Stateless operations as simple classes
- **Value Objects**: Immutable data models using Pydantic
- **Railway Pattern**: All operations return `FlextResult[T]`

**Key Improvements in v0.10.0**:

- 30-40% less code (14K → 10K lines)
- 75% fewer services (18 → 3-4)
- 50% fewer API methods (~30 → ~15)
- Clearer architecture and better performance

---

## Prerequisites

### System Requirements

- **Python**: 3.13+ (required for advanced type features)
- **Poetry**: 1.7+ (dependency management)
- **Make**: Build automation
- **FLEXT Ecosystem**: flext-core v0.9.9+

### FLEXT Ecosystem Integration

flext-cli integrates with:

- **[flext-core](https://github.com/organization/flext/tree/main/flext-core/README.md)**: Foundation patterns (FlextResult, FlextService, FlextModels)
- **Click 8.2+**: CLI framework (abstracted)
- **Rich 14.0+**: Terminal UI (abstracted)
- **Pydantic 2.11+**: Data validation

---

## Installation

### Development Setup

```bash
# Clone repository
git clone https://github.com/flext-sh/flext-cli.git
cd flext-cli

# Complete setup (installs dependencies, pre-commit hooks)
make setup

# Verify installation
python -c "from flext_cli import FlextCli; print('✅ Installation successful')"
```

### As a Dependency

Add to your project's `pyproject.toml`:

```toml
[tool.poetry.dependencies]
flext-cli = "^0.10.0"
flext-core = "^0.9.9"
```

Then:

```bash
poetry add flext-cli
# or
pip install flext-cli
```

---

## Quick Start (v0.10.0)

### 🚀 Your First CLI Application

```python
from flext_cli import FlextCli
from flext_core import FlextResult

# Initialize CLI (singleton pattern)
cli = FlextCli()

# Print with styling (direct access to formatters)
cli.formatters.print("Welcome to FLEXT CLI!", style="green bold")

# Read configuration file (direct access to file_tools)
config_result = cli.file_tools.read_json_file("config.json")

if config_result.is_success:
    config = config_result.unwrap()
    cli.formatters.print(f"Loaded config: {config}", style="cyan")
else:
    cli.formatters.print(f"Error: {config_result.error}", style="red")

# Interactive prompt (direct access to prompts)
confirm_result = cli.prompts.confirm("Continue?")

if confirm_result.is_success and confirm_result.unwrap():
    cli.formatters.print("Let's go!", style="green")
```

### 📊 Working with Tables

```python
from flext_cli import FlextCli

cli = FlextCli()

# Create data
users = [
    {"name": "Alice", "role": "Admin", "status": "Active"},
    {"name": "Bob", "role": "User", "status": "Active"},
]

# Format as table (direct access to output)
table_result = cli.output.format_data(
    data={"users": users},
    format_type="table"
)

# Display
if table_result.is_success:
    cli.formatters.print(table_result.unwrap())
```

### 📁 File Operations

```python
from flext_cli import FlextCli

cli = FlextCli()

# JSON operations (direct access to file_tools)
data = {"setting": "value", "enabled": True}

# Write
write_result = cli.file_tools.write_json_file("config.json", data)

if write_result.is_success:
    cli.formatters.print("Config saved!", style="green")

# Read
read_result = cli.file_tools.read_json_file("config.json")

if read_result.is_success:
    loaded_data = read_result.unwrap()
    cli.formatters.print(f"Loaded: {loaded_data}", style="cyan")
```

### 🔄 Railway-Oriented Programming

Chain operations with `FlextResult[T]`:

```python
from flext_cli import FlextCli
from flext_core import FlextResult

cli = FlextCli()

def validate_config(config: dict) -> FlextResult[dict]:
    """Validate configuration."""
    if "required_field" not in config:
        return FlextResult[dict].fail("Missing required_field")
    return FlextResult[dict].ok(config)

def apply_defaults(config: dict) -> dict:
    """Apply default values."""
    return {**{"timeout": 30}, **config}

# Chain operations
result = (
    cli.file_tools.read_json_file("config.json")
    .flat_map(validate_config)  # Validate
    .map(apply_defaults)         # Transform
    .map(lambda cfg: cli.formatters.print(f"Final config: {cfg}"))
)

# Handle result
if not result.is_success:
    cli.formatters.print(f"Error: {result.error}", style="red")
```

---

## Development Workflow (v0.10.0)

### Quality Gates

```bash
# Before committing (MANDATORY)
make validate               # Complete validation: lint + type + security + test

# Individual checks
make lint                   # Ruff linting (ZERO tolerance)
make type-check             # Pyrefly type checking (strict)
make security               # Bandit security scan
make test                   # Test suite with coverage

# Formatting
make format                 # Auto-format with Ruff
```

### Development Pattern (v0.10.0)

```python
from flext_cli import FlextCli
from flext_core import FlextResult

def my_cli_application() -> FlextResult[bool]:
    """Application using v0.10.0 patterns."""
    cli = FlextCli()

    # Direct access to all services
    cli.formatters.print("Starting...", style="cyan")

    # File operations
    config_result = cli.file_tools.read_json_file("config.json")

    if not config_result.is_success:
        cli.formatters.print(f"Error: {config_result.error}", style="red")
        return FlextResult[bool].fail(config_result.error)

    # User interaction
    confirm_result = cli.prompts.confirm("Continue?")
    if confirm_result.is_success and confirm_result.unwrap():
        cli.formatters.print("Processing...", style="green")
        return FlextResult[bool].ok(value=True)
    return FlextResult[bool].fail("Operation cancelled")
```

### Testing Your CLI Code

```python
import pytest
from flext_cli import FlextCli

def test_my_cli_operation():
    """Test using v0.10.0 patterns."""
    cli = FlextCli()

    # Test file operations (direct access)
    result = cli.file_tools.read_json_file("test_config.json")

    assert result.is_success
    config = result.unwrap()
    assert "required_field" in config
```

---

## Next Steps

### Learn More

- **[API Reference](api-reference.md)** - Complete API documentation
- **[Architecture](architecture.md)** - Architecture and design patterns
- **[Development Guide](development.md)** - Contributing and extending

### Migration from v0.9.0

If you're upgrading from v0.9.0, see:

- **[Migration Guide](refactoring/migration-guide-v0.9-to-v0.10.md)** - Step-by-step migration
- **[Breaking Changes](refactoring/breaking-changes.md)** - Complete breaking changes list
- **[Architecture Comparison](refactoring/architecture-comparison.md)** - Before/after comparison

## Related Documentation

**Within Project**:

- [API Reference](api-reference.md) - Complete API documentation
- [Architecture](architecture.md) - Architecture and design patterns
- [Development Guide](development.md) - Contributing and extending
- [Migration Guide](refactoring/migration-guide-v0.9-to-v0.10.md) - v0.9.0 to v0.10.0 migration

**Across Projects**:

- [flext-core Foundation](https://github.com/organization/flext/tree/main/flext-core/docs/guides/railway-oriented-programming.md) - Railway-oriented programming patterns
- [flext-core CLI Patterns](https://github.com/organization/flext/tree/main/flext-core/docs/guides/service-patterns.md) - Service patterns

**External Resources**:

- [PEP 257 - Docstring Conventions](https://peps.python.org/pep-0257/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)

### Examples

Check `examples/` directory for complete application samples:

- Basic CLI application
- File processing workflows
- Interactive prompts
- Table formatting
- Configuration management

---

## v0.9.0 Getting Started (Historical Reference)

**Note**: The following documentation describes v0.9.0 patterns with wrapper methods. This is kept for historical reference during the migration period.

## Development Patterns (v0.9.0)

### Working Development Pattern

```python
# This development pattern demonstrates working functionality
from Flext_cli import FlextCliService, FlextCliAuth, FlextCliSettings
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

# Service initialization and operation
service = FlextCliService()
health = service.get_service_health()
assert health.is_success

# Authentication functionality
auth = FlextCliAuth()
methods = [m for m in dir(auth) if not m.startswith('_')]
print(f"Available auth methods: {len(methods)}")  # 35+ methods

# Configuration management
config = FlextCliSettings(
    profile="development",
    debug=True,
    output_format="table"
)
```

---

## Quality Validation

### Validation Commands

```bash
# Development workflow - these work correctly
make lint                    # Ruff linting (passes for src/)
make type-check             # MyPy strict mode (passes for src/)
make format                 # Auto-format code
make test                   # Run comprehensive test suite
```

### Implementation Verification

```bash
# Verify substantial implementation metrics
find src/ -name "*.py" -exec wc -l {} + | tail -1
# Expected: 10,000+ lines across 32 modules

# Verify core services load
python -c "from flext_cli import FlextCliService, FlextCliAuth, FlextCli; print('✅ All core services import successfully')"
```

---

## Next Steps

**For Development**:

- Library ready for extension and integration
- Focus on Click callback signature fix for CLI commands
- Comprehensive test coverage achievable with substantial codebase
- Modern enterprise patterns already implemented

**Ready For**:

- Service integration (authentication, API, configuration work)
- Extension development (substantial foundation available)
- Architecture evaluation (enterprise-grade patterns in place)

---

**Development Status**: Enterprise-grade foundation with targeted CLI execution fix required.
