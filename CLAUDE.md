# FLEXT-CLI Project Guidelines

**Reference**: See [../CLAUDE.md](../CLAUDE.md) for FLEXT ecosystem standards and general rules.

---

## Project Overview

**FLEXT-CLI** is the CLI foundation library for the FLEXT ecosystem, providing a unified command-line interface abstraction layer over Click and Rich. It serves 32+ projects with standardized CLI patterns, configuration management, and output formatting.

**Version**: 0.9.0  
**Status**: Production-ready  
**Python**: 3.13+ exclusive with strict type safety

**Key Architecture**:
- Single consolidated API class: `FlextCli`
- Wraps Click (CLI framework) and Rich (terminal UI) internally
- Uses flext-core patterns: `FlextResult[T]` railway pattern, `FlextService`
- Poetry-based dependency management

---

## Architecture

### Module Structure and Responsibilities

```
src/flext_cli/
├── __init__.py          # Public API exports (19 classes)
├── api.py               # FlextCli - main facade API
├── cli.py               # FlextCliCli - Click abstraction (ONLY Click import)
├── cli_params.py       # FlextCliCommonParams - reusable CLI parameters
├── formatters.py       # FlextCliFormatters - Rich abstraction (ONLY Rich import)
├── tables.py            # FlextCliTables - Tabulate integration (22+ formats)
├── output.py            # FlextCliOutput - output management service
├── prompts.py           # FlextCliPrompts - interactive user input
├── file_tools.py        # FlextCliFileTools - JSON/YAML/CSV operations
├── config.py            # FlextCliConfig - singleton configuration
├── constants.py         # FlextCliConstants - all system constants
├── models.py            # FlextCliModels - ALL Pydantic models
├── typings.py           # FlextCliTypes - type aliases and definitions
├── protocols.py         # FlextCliProtocols - structural typing
├── exceptions.py        # FlextCliExceptions - exception hierarchy
├── core.py              # FlextCliCore - extends FlextService
├── cmd.py               # FlextCliCmd - command execution
├── commands.py          # FlextCliCommands - command registration
├── context.py           # FlextCliContext - execution context
├── debug.py             # FlextCliDebug - debug utilities
└── mixins.py            # FlextCliMixins - reusable mixins
```

**Key Module Dependencies**:
- `api.py` → Main entry point, imports most other modules
- `cli.py` → ONLY file that imports Click (ZERO TOLERANCE)
- `formatters.py` + `typings.py` → ONLY files that import Rich (ZERO TOLERANCE)
- `models.py` → Contains ALL Pydantic models (largest module)
- `constants.py` → No external dependencies, used everywhere
- All modules → Extend or use `flext_core` patterns

### Core Classes (Actual Exports)

```python
from flext_cli import (
    FlextCli,              # Main consolidated API (NOT FlextCliApi)
    FlextCliConfig,        # Configuration (NOT FlextCliConfigs)
    FlextCliConstants,     # Constants
    FlextCliFormatters,    # Rich formatting abstraction
    FlextCliTables,        # Table formatting
    FlextCliOutput,        # Output service
    FlextCliPrompts,       # Interactive prompts
    FlextCliFileTools,     # File operations
    FlextCliCore,          # Core service
    FlextCliCmd,           # Command execution
    FlextCliDebug,         # Debug utilities
    FlextCliCommands,      # Command management
    FlextCliContext,       # Execution context
    FlextCliModels,        # Pydantic models
    FlextCliTypes,         # Type definitions
    FlextCliProtocols,    # Protocols
    FlextCliMixins,        # Mixins
    FlextCliExceptions,    # Exceptions
)
```

### Design Patterns

**Railway-Oriented Programming**:
All operations return `FlextResult[T]` for composable error handling:

```python
from flext_cli import FlextCli
from flext_core import FlextResult

cli = FlextCli()

# All operations return FlextResult
result = cli.authenticate({"token": "abc123"})
if result.is_success:
    token = result.unwrap()
else:
    print(f"Auth failed: {result.error}")
```

**Domain Library Pattern**:
Each module follows the unified class pattern from flext-core:

```python
class FlextCliFormatters:
    """Single class per module - domain library pattern."""
    # All formatting functionality consolidated here
```

**Configuration Singleton Pattern**:
Configuration uses global singleton with environment variable support:

```python
from flext_cli import FlextCliConfig

# Get singleton instance (creates if needed)
config = FlextCliConfig.get_global_instance()

# All configuration is read-only properties
debug = config.debug               # FLEXT_DEBUG env var
output_format = config.output_format  # FLEXT_OUTPUT_FORMAT
token_file = config.token_file     # ~/.flext/auth/token.json
```

**Click/Rich Abstraction Pattern**:
Never import Click or Rich directly except in designated files:

```python
# ❌ FORBIDDEN in most files
import click
from rich.console import Console

# ✅ CORRECT - Use abstraction layers
from flext_cli import FlextCli, FlextCliFormatters, FlextCliTables

cli = FlextCli()
cli.print("Success!", style="green")  # Rich abstraction
table = cli.create_table(...)          # Table abstraction
```

---

## Essential Commands

```bash
# Setup and installation
make setup                   # Complete setup with pre-commit hooks
make install                 # Install dependencies with Poetry
make install-dev             # Install with dev dependencies

# Quality gates (run before commits)
make validate                # Full validation: lint + type-check + security + test
make check                   # Quick check: lint + type-check only
make lint                    # Ruff linting
make type-check              # Pyrefly type checking
make security                # Bandit security scan
make format                  # Auto-format code with Ruff

# Testing
make test                    # Full test suite with coverage
make test-unit               # Unit tests only
make test-integration        # Integration tests only
make test-fast               # Tests without coverage
make coverage-html            # Generate HTML coverage report

# Specific test execution
PYTHONPATH=src poetry run pytest tests/unit/test_api.py -v
PYTHONPATH=src poetry run pytest tests/unit/test_config.py::TestFlextCliConfig -v
PYTHONPATH=src poetry run pytest -m unit -v

# Build and maintenance
make build                   # Build package
make clean                   # Clean build artifacts
make reset                   # Complete reset (clean + setup)
```

---

## Critical Constraints

**ZERO TOLERANCE**:
- **cli.py** is the ONLY file that may import Click directly
- **formatters.py** and **typings.py** are the ONLY files that may import Rich directly
- ALL other code must use the abstraction layers
- Breaking this constraint violates the foundation library's core purpose

---

## Testing Strategy

### Test Structure

```
tests/
├── unit/                    # Unit tests for individual components
│   ├── test_api.py         # FlextCli tests
│   ├── test_config.py      # FlextCliConfig tests
│   ├── test_formatters.py  # FlextCliFormatters tests
│   ├── test_tables.py      # FlextCliTables tests
│   └── ...
├── integration/            # Integration tests
└── conftest.py            # Shared fixtures
```

### Test Fixtures

Common fixtures available in all tests (from `conftest.py`):
- Service fixtures (all 19 modules have fixtures)
- Utility fixtures (temp_dir, temp_file, sample_config_data, etc.)
- Fixture data loaders

### Writing Tests

**CRITICAL TESTING RULES**:
- **NO monkeypatch usage** - Use fixtures with data and behavior validation instead
- **Relative imports ONLY** - tests/, examples/, and scripts/ must use relative imports
- **Test real functionality** - Use fixtures with actual data, not mocks
- **Validate outputs** - Test behavior and output validation, not just coverage

---

## Pydantic v2 Standards

**ALL models in FlextCliModels must use Pydantic v2 patterns. Pydantic v1 patterns are FORBIDDEN.**

### Required Patterns

**Model Configuration**:
```python
from pydantic import BaseModel, ConfigDict

class CommandExecutionConfig(BaseModel):
    model_config = ConfigDict(frozen=False, validate_assignment=True)
```

**Field Validators**:
```python
from pydantic import field_validator

class CommandModel(BaseModel):
    command_name: str

    @field_validator('command_name')
    @classmethod
    def validate_command_name(cls, v: str) -> str:
        return v.lower()
```

**Serialization**:
```python
model.model_dump()           # Python dict
model.model_dump_json()      # JSON string (FASTEST)
```

**Validation**:
```python
CommandModel.model_validate(data)        # From dict
CommandModel.model_validate_json(json)   # From JSON (FAST)
```

### Forbidden Patterns

- ❌ `class Config:` → Use `model_config = ConfigDict()`
- ❌ `.dict()`, `.json()`, `parse_obj()` → Use `.model_dump()`, `.model_dump_json()`, `.model_validate()`
- ❌ `@validator`, `@root_validator` → Use `@field_validator`, `@model_validator`

---

## Common Issues and Solutions

### Import Errors

```bash
# If you get "ModuleNotFoundError: No module named 'flext_cli'"
PYTHONPATH=src poetry run python -c "from flext_cli import FlextCli"

# Always set PYTHONPATH when running tests or scripts
PYTHONPATH=src poetry run pytest tests/
```

### Type Check Failures

```bash
# Run type check to see errors
make type-check

# Note: Some import errors in examples/ are expected
# Focus on errors in src/flext_cli/
```

### Circular Import Errors

If you encounter circular imports:
- Usually caused by incorrect import order in `__init__.py` or `api.py`
- Check the dependency chain
- Move shared types to `typings.py`, shared constants to `constants.py`

---

## Integration with FLEXT Ecosystem

This project is part of the FLEXT monorepo workspace. Key integration points:

- **Depends on**: flext-core (foundation library)
- **Used by**: client-a-oud-mig, client-b-meltano-native, flext-api, flext-observability, flext-meltano
- **Architecture**: Follows workspace-level patterns defined in `../CLAUDE.md`
- **Quality Gates**: Must pass workspace-level validation before commits

See `../CLAUDE.md` for workspace-level standards and `README.md` for project overview.

---

**Additional Resources**: [../CLAUDE.md](../CLAUDE.md) (workspace), [README.md](README.md) (overview), [docs/README.md](docs/README.md) (documentation index)
