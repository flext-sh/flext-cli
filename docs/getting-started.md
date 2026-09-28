# Getting Started with flext-cli

<!-- TOC START -->

- [📌 Quick Navigation](#quick-navigation)
- [v0.12.0-dev Getting Started (Current)](#v0120-dev-getting-started-current)
  - [Overview](#overview)
- [Prerequisites](#prerequisites)
  - [System Requirements](#system-requirements)
  - [FLEXT Ecosystem Integration](#flext-ecosystem-integration)
- [Installation](#installation)
  - [Development Setup](#development-setup)
  - [As a Dependency](#as-a-dependency)
- [Quick Start (v0.12.0-dev)](#quick-start-v0120-dev)
  - [🚀 Your First CLI Application](#your-first-cli-application)
  - [📊 Working with Tables](#working-with-tables)
  - [📁 File Operations](#file-operations)
  - [🔄 Railway-Oriented Programming](#railway-oriented-programming)
- [Development Workflow (v0.12.0-dev)](#development-workflow-v0120-dev)
  - [Quality Gates](#quality-gates)
  - [Development Pattern (v0.12.0-dev)](#development-pattern-v0120-dev)
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
- [Next Steps (v0.9.0)](#next-steps-v090)

<!-- TOC END -->

**Installation and setup guide for the FLEXT ecosystem CLI foundation library.**

**Last Updated**: 2026-09-17 | **Version**: 0.12.0

---

## 📌 Quick Navigation

- [v0.12.0-dev Getting Started (Current)](#v0120-dev-getting-started-current) ←
  **Start Here**
- [v0.9.0 Getting Started (Historical Reference)](#v090-getting-started-historical-reference)

---

## v0.12.0-dev Getting Started (Current)

**Status**: 🔄 Active Development | **Release**: 0.12.0 | **Breaking Changes**: Yes

### Overview

flext-cli v0.12.0-dev is a simplified, streamlined CLI foundation library for the FLEXT
ecosystem. It provides:

- **Direct MRO API**: All services available directly on `cli.*` via MRO inheritance
- **Services for State Only**: s used only where needed (3-4 classes)
- **Simple Utilities**: Stateless operations as simple classes
- **Value Objects**: Immutable data models using Pydantic
- **Railway Pattern**: All operations return `r[T]`

**Key Improvements in v0.12.0-dev**:

- 30-40% less code (14K → 10K lines)
- 75% fewer services (18 → 3-4)
- 50% fewer API methods (~30 → ~15)
- Clearer architecture and better performance

---

## Prerequisites

### System Requirements

- **Python**: 3.13+ (required for advanced type features)
- **Make**: Build automation
- **FLEXT Ecosystem**: flext-core v0.12.0-dev+

### FLEXT Ecosystem Integration

flext-cli integrates with:

- **[flext-core](https://github.com/flext-sh/flext-core/blob/0.12.0-dev/README.md)**:
  Foundation patterns (`r`, `s`, `FlextModels`)
- **Click 8.2+**: CLI framework (abstracted)
- **Rich 14.0+**: Terminal UI (abstracted)
- **Pydantic 2.13.5+**: Data validation

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
python -c "print('✅ Installation successful')"
```

### As a Dependency

Add to your project's `pyproject.toml`:

```toml
[dependency-groups]
dev = ["flext-cli>=0.12.0", "flext-core>=0.12.0"]
```

Then:

```bash
pip install flext-cli
```

---

## Quick Start (v0.12.0-dev)

### 🚀 Your First CLI Application

```text
from flext_cli import cli
from flext_core import r, p

# Initialize CLI (singleton pattern)

# Print with styling (MRO inheritance)
cli.print("Welcome to FLEXT CLI!", style="green bold")

# Read configuration file
config_result = cli.read_json_file("settings.json")

if config_result.success:
    settings = config_result.unwrap()
    cli.print(f"Loaded settings: {settings}", style="cyan")
else:
    cli.print(f"Error: {config_result.error}", style="red")

# Interactive prompt
confirm_result = cli.confirm("Continue?")

if confirm_result.success and confirm_result.unwrap():
    cli.print("Let's go!", style="green")
```

### 📊 Working with Tables

```text
from flext_cli import cli


# Create data
users = [
    {"name": "Alice", "role": "Admin", "status": "Active"},
    {"name": "Bob", "role": "User", "status": "Active"},
]

# Display as table
cli.show_table(users, title="Users")
```

### 📁 File Operations

```text
from flext_cli import cli


# JSON operations
data = {"setting": "value", "enabled": True}

# Write
write_result = cli.write_json_file("settings.json", data)

if write_result.success:
    cli.print("Config saved!", style="green")

# Read
read_result = cli.read_json_file("settings.json")

if read_result.success:
    loaded_data = read_result.unwrap()
    cli.print(f"Loaded: {loaded_data}", style="cyan")
```

### 🔄 Railway-Oriented Programming

Chain operations with `r[T]`:

```text
from flext_cli import cli
from flext_core import r, p


def validate_settings(settings: dict) -> p.Result[dict]:
    """Validate settings."""
    if "required_field" not in settings:
        return r[dict].fail("Missing required_field")
    return r[dict].ok(settings)


def apply_defaults(settings: dict) -> dict:
    """Apply default values."""
    return {**{"timeout": 30}, **settings}


# Chain operations
result = (
    cli.read_json_file("settings.json")
    .flat_map(validate_settings)  # Validate
    .map(apply_defaults)  # Transform
    .map(lambda cfg: cli.print(f"Final settings: {cfg}"))
)

# Handle result
if result.failure:
    cli.print(f"Error: {result.error}", style="red")
```

---

## Development Workflow (v0.12.0-dev)

### Quality Gates

```bash
# Before committing (MANDATORY)
make check # Complete validation: lint + type + test

# Individual checks
make check # Ruff linting + type checking (strict)
make fix   # Auto-fix findings
make test  # Test suite with coverage

# Formatting
make fmt # Auto-format with Ruff
```

### Development Pattern (v0.12.0-dev)

```text
from flext_cli import cli
from flext_core import r, p


def my_cli_application() -> p.Result[bool]:
    """Application using v0.12.0-dev patterns."""

    # Direct access to all services
    cli.print("Starting...", style="cyan")

    # File operations
    config_result = cli.read_json_file("settings.json")

    if not config_result.success:
        cli.print(f"Error: {config_result.error}", style="red")
        return r[bool].fail(config_result.error)

    # User interaction
    confirm_result = cli.confirm("Continue?")
    if confirm_result.success and confirm_result.unwrap():
        cli.print("Processing...", style="green")
        return r[bool].ok(value=True)
    return r[bool].fail("Operation cancelled")
```

### Testing Your CLI Code

```text
import pytest
from flext_cli import cli


def test_my_cli_operation():
    """Test using v0.12.0-dev patterns."""

    # Test file operations (direct access)
    result = cli.read_json_file("test_config.json")

    assert result.success
    settings = result.unwrap()
    assert "required_field" in settings
```

---

## Next Steps

### Learn More

- **[API Reference](api-reference/README.md)** - Complete API documentation
- **[Architecture](architecture.md)** - Architecture and design patterns
- **[Development Guide](development.md)** - Contributing and extending

### Migration from v0.9.0

If you're upgrading from v0.9.0, see:

- **[Migration Guide](refactoring/migration-guide-v0.9-to-v0.10.md)** - Step-by-step
  migration
- **[Breaking Changes](refactoring/breaking-changes.md)** - Complete breaking changes
  list
- **[Architecture Comparison](refactoring/architecture-comparison.md)** - Before/after
  comparison

## Related Documentation

**Within Project**:

- [API Reference](api-reference/README.md) - Complete API documentation
- [Architecture](architecture.md) - Architecture and design patterns
- [Development Guide](development.md) - Contributing and extending
- [Migration Guide](refactoring/migration-guide-v0.9-to-v0.10.md) - v0.9.0 to
  v0.12.0-dev migration

**Across Projects**:

- [flext-core Foundation](https://github.com/flext-sh/flext-core/blob/0.12.0-dev/docs/guides/railway-oriented-programming.md) -
  Railway-oriented programming patterns
- [flext-core CLI Patterns](https://github.com/flext-sh/flext-core/blob/0.12.0-dev/docs/guides/service-patterns.md) -
  Service patterns

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

**Note**: The following documentation describes v0.9.0 patterns with wrapper methods.
This is kept for historical reference during the migration period.

## Development Patterns (v0.9.0)

### Working Development Pattern

```text
# This development pattern demonstrates working functionality
from Flext_cli import FlextCliService, FlextCliAuth, FlextCliSettings
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
from flext_core import r, p
from flext_core import u
from flext_core import s
from flext_core import t
from flext_core import u

# Service initialization and operation
service = FlextCliService()
health = service.get_service_health()
assert health.success

# Authentication functionality
auth = FlextCliAuth()
methods = [m for m in dir(auth) if not m.startswith("_")]
print(f"Available auth methods: {len(methods)}")  # 35+ methods

# Configuration management
settings = FlextCliSettings(profile="development", debug=True, output_format="table")
```

---

## Quality Validation

### Validation Commands

```bash
make check # Complete validation: lint + type + test
make fmt   # Auto-format code
make test  # Run comprehensive test suite
```

### Implementation Verification

```bash
# Verify core facade loads correctly
python -c "from flext_cli import FlextCli, cli; print('✅ Core facade loads')"
```

---

## Next Steps (v0.9.0)

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

**Development Status**: Enterprise-grade foundation with targeted CLI execution fix
required.
