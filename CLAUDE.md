# FLEXT-CLI Project Guidelines

**Reference**: See [../CLAUDE.md](../CLAUDE.md) for FLEXT ecosystem standards and general rules.

---

## Project Overview

**FLEXT-CLI** is the CLI foundation library for the FLEXT ecosystem, providing a unified command-line interface abstraction layer over Click and Rich. It serves 32+ projects with standardized CLI patterns, configuration management, and output formatting.

**Version**: 0.10.0  
**Status**: Production-ready  
**Python**: 3.13+ exclusive with strict type safety  
**Standards**: FLEXT Advanced Standards, PEP+, Pydantic 2, SOLID, DRY

**Key Architecture**:
- Single consolidated API class: `FlextCli`
- Wraps Click (CLI framework) and Rich (terminal UI) internally
- Uses flext-core patterns: `FlextResult[T]` railway pattern, `FlextService`
- Poetry-based dependency management

---

## Architecture

### Module Structure and Responsibilities

**CRITICAL**: All modules follow strict "ONE class per module" pattern:

```
src/flext_cli/
├── __init__.py          # Public API exports with short aliases (t, c, p, m, u, s, r, e, d, x)
├── api.py               # FlextCli - main facade API (ONE class)
├── app_base.py          # FlextCliAppBase - base class for CLI apps (ONE class)
├── base.py              # FlextCliServiceBase - service base (ONE class, alias: s)
├── cli.py               # FlextCliCli - Click abstraction (ONE class, ONLY Click import)
├── cli_params.py        # FlextCliCommonParams - reusable CLI parameters (ONE class)
├── commands.py          # FlextCliCommands - command registration (ONE class)
├── config.py            # FlextCliConfig - singleton configuration (ONE class)
├── constants.py         # FlextCliConstants - all constants (ONE class, extends FlextConstants, alias: c)
├── context.py           # FlextCliContext - execution context (ONE class)
├── debug.py             # FlextCliDebug - debug utilities (ONE class)
├── file_tools.py        # FlextCliFileTools - JSON/YAML/CSV operations (ONE class)
├── formatters.py        # FlextCliFormatters - Rich abstraction (ONE class, ONLY Rich import)
├── mixins.py            # FlextCliMixins - reusable mixins (ONE class)
├── models.py            # FlextCliModels - ALL Pydantic models (ONE class, extends FlextModels, alias: m)
├── protocols.py         # FlextCliProtocols - structural typing (ONE class, extends FlextProtocols, alias: p)
├── typings.py           # FlextCliTypes - type aliases (ONE class, extends FlextTypes, alias: t)
├── utilities.py         # FlextCliUtilities - utilities (ONE class, extends FlextUtilities, alias: u)
└── services/
    ├── cmd.py           # FlextCliCmd - command execution (ONE class)
    ├── core.py          # FlextCliCore - extends FlextService (ONE class)
    ├── output.py        # FlextCliOutput - output management (ONE class)
    ├── prompts.py       # FlextCliPrompts - interactive prompts (ONE class)
    └── tables.py        # FlextCliTables - Tabulate integration (ONE class)
```

**Pattern Rules**:
- **ONE class per module** - Each module has exactly ONE class prefixed with `FlextCli*`
- **Short aliases** - `t` (Types), `c` (Constants), `p` (Protocols), `m` (Models), `u` (Utilities), `s` (ServiceBase)
- **Core aliases** - `r` (FlextResult), `e` (FlextExceptions), `d` (FlextDecorators), `x` (FlextMixins) from `flext_core`
- **Extension pattern** - All classes extend corresponding `Flext*` classes from `flext-core`
- **NO bad-override** - `@override` only when amplifying scope or overriding abstract methods
- **NO duplicate classes** - Each class has unique responsibility (SOLID)

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

**CRITICAL**: All test modules follow strict FLEXT standards:

```
tests/
├── typings.py            # TestsCliTypes - extends FlextTestsTypes and FlextCliTypes (alias: t)
├── constants.py          # TestsCliConstants - extends FlextTestsConstants and FlextCliConstants (alias: c)
├── protocols.py          # TestsCliProtocols - extends FlextTestsProtocols and FlextCliProtocols (alias: p)
├── models.py             # TestsCliModels - extends FlextTestsModels and FlextCliModels (alias: m)
├── utilities.py          # TestsCliUtilities - extends FlextTestsUtilities and FlextCliUtilities (alias: u)
├── base.py               # TestsCliServiceBase - extends FlextTestsServiceBase and FlextCliServiceBase (alias: s)
├── __init__.py           # Exports all TestsCli classes and short aliases (t, c, p, m, u, s)
├── conftest.py           # Centralized pytest configuration and fixtures (ONLY pytest config, no test helpers)
├── helpers/              # Domain-specific helpers ONLY (uses conftest, flext_tests, base classes)
│   └── __init__.py       # Only flext-cli specific helpers (NO duplicates from conftest or flext_tests)
├── fixtures/             # Data fixtures ONLY (NO Python modules, only data files - JSON, YAML, CSV, etc.)
├── unit/                 # Unit tests - one TestsCli* class per module
│   ├── test_output.py    # TestsCliOutput class
│   ├── test_prompts.py   # TestsCliPrompts class
│   └── ...
└── integration/          # Integration tests
```

**Test Module Pattern**: ONE class per module, prefixed with `TestsCli*`:
- `TestsCliOutput` in `test_output.py`
- `TestsCliPrompts` in `test_prompts.py`
- `TestsCliTables` in `test_tables.py`
- etc.

**Short Aliases Usage**:
- Use `t`, `c`, `m`, `p`, `u`, `s` from `tests` module for support (NOT for test declarations)
- Use `r` (FlextResult), `e` (FlextExceptions), `d` (FlextDecorators), `x` (FlextMixins) directly from `flext_core`
- All aliases must work with class short names without lint complaints

### TestsCli Structure Pattern

**CRITICAL**: All test modules follow the `TestsCli*` pattern:

1. **TestsCliTypes** (`tests/typings.py`):
   - Extends `FlextTestsTypes` and `FlextCliTypes`
   - Provides short alias `t`
   - Centralizes all test-specific type definitions

2. **TestsCliConstants** (`tests/constants.py`):
   - Extends `FlextTestsConstants` and `FlextCliConstants`
   - Provides short alias `c`
   - Centralizes all test-specific constants

3. **TestsCliProtocols** (`tests/protocols.py`):
   - Extends `FlextTestsProtocols` and `FlextCliProtocols`
   - Provides short alias `p`
   - Centralizes all test-specific protocols

4. **TestsCliModels** (`tests/models.py`):
   - Extends `FlextTestsModels` and `FlextCliModels`
   - Provides short alias `m`
   - Centralizes all test-specific models

5. **TestsCliUtilities** (`tests/utilities.py`):
   - Extends `FlextTestsUtilities` and `FlextCliUtilities`
   - Provides short alias `u`
   - Centralizes all test-specific utilities

6. **TestsCliServiceBase** (`tests/base.py`):
   - Extends `FlextTestsServiceBase` and `FlextCliServiceBase`
   - Provides short alias `s`
   - Base service for test infrastructure

### Test Module Pattern

**Each test module must have ONE class prefixed with `TestsCli*`**:

```python
from tests import c, m, t, u, p, s  # TestsCli structure
from flext_cli import r, e, d, x  # Direct from flext-core

class TestsCliOutput:
    """Comprehensive tests for FlextCliOutput functionality."""
    
    def test_something(self, output: FlextCliOutput) -> None:
        """Test description."""
        result = output.format_data(c.TestData.SAMPLE, "json")
        assert result.is_success
```

### Test Fixtures

Common fixtures available in all tests (from `conftest.py`):
- Service fixtures (all modules have fixtures)
- Utility fixtures (temp_dir, temp_file, sample_config_data, etc.)
- Model factories (cli_command_factory, cli_session_factory, etc.)
- Docker support (flext_test_docker)

### Writing Tests

**CRITICAL TESTING RULES**:
- **ONE class per module** - Prefix with `TestsCli*` (e.g., `TestsCliOutput`)
- **Use short aliases** - `t`, `c`, `m`, `p`, `u`, `s` from `tests` module for support (NOT for test declarations)
- **Use flext-core aliases** - `r` (FlextResult), `e` (FlextExceptions), `d` (FlextDecorators), `x` (FlextMixins) directly from `flext_core`
- **NO monkeypatch usage** - Use fixtures with data and behavior validation instead
- **Test real functionality** - Use fixtures with actual data, not mocks
- **Validate outputs** - Test behavior and output validation, not just coverage
- **100% coverage** - All code paths must be tested (pragma only for untestable code)
- **NO skipped tests** - All tests must run and pass (no `@pytest.mark.skip`)
- **NO Python modules in fixtures/** - Use only data files (JSON, YAML, CSV, etc.), rely on conftest.py and flext_tests
- **helpers/** - Only domain-specific helpers, always use conftest, flext_tests, and base classes
- **NO bad-override** - All `@override` must amplify scope or correctly override abstract methods
- **TestsCli structure** - All test support classes must extend both `FlextTests*` and `FlextCli*` classes

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
