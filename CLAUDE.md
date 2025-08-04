# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FLEXT CLI is a modern command-line interface built with Python 3.13+, Click, and Rich libraries. It implements Clean Architecture with Domain-Driven Design (DDD) patterns, using flext-core as the foundation library. The CLI provides commands for the entire FLEXT ecosystem including authentication, configuration, debug operations, and integration with 32+ distributed data platform projects.

**Current Status (Updated 2025-08-02):**

- **Architecture**: 70% implemented - solid foundations with comprehensive docstring alignment
- **Functionality**: 30% implemented - only 3 of 10+ command groups functional
- **Documentation**: 95% complete - all source files have standardized English docstrings
- **Sprint Roadmap**: 10-sprint development plan established with clear milestones

**Key Architectural Principles:**

- Clean Architecture with strict layer separation (Domain → Application → Infrastructure)
- Domain-Driven Design with rich domain entities (CLICommand, CLISession, CLIPlugin, CLIConfig)
- **flext-core integration (60% complete)** - Good foundations but missing enterprise patterns
- Type-safe implementation with MyPy strict mode (zero errors tolerated)
- 90% test coverage requirement with comprehensive quality gates
- **Complete docstring standardization** - All 35 source files updated with 251 status indicators

**flext-core Integration Status:**

- ✅ **Well-Implemented**: FlextResult, FlextEntity, FlextValueObject, FlextBaseSettings
- ⚠️ **Partially Implemented**: Service layer, basic dependency injection
- ❌ **Missing Critical Patterns**: CQRS, Domain Events, FlextContainer, Repository pattern

**Recent Major Achievements:**

- ✅ **Complete docstring standardization** - All source files updated with comprehensive documentation
- ✅ **English standardization** - Zero Portuguese text remaining across entire codebase
- ✅ **Sprint alignment** - All modules reference specific Sprint requirements (1-10)
- ✅ **Architecture documentation** - Comprehensive patterns documented in all layers
- ✅ **Status indicators** - 251 status indicators providing clear implementation status

## Architecture

### Current Structure

The project follows Clean Architecture principles with flext-core integration:

```
src/flext_cli/
├── domain/                    # Core business logic (innermost layer)
│   ├── entities.py           # Domain entities (CLICommand, CLIConfig, CLISession, CLIPlugin)
│   ├── cli_context.py        # CLI context value objects
│   └── cli_services.py       # Domain services
├── application/               # Application orchestration layer
│   └── commands.py           # Command handlers
├── infrastructure/            # Infrastructure implementations
│   ├── container.py          # Dependency injection container
│   └── config.py             # Configuration management
├── commands/                  # Concrete CLI command implementations (CURRENT: auth, config, debug only)
│   ├── auth.py              # Authentication commands
│   ├── config.py            # Configuration commands
│   └── debug.py             # Debug and diagnostic commands
├── core/                     # Core CLI utilities and patterns
│   ├── base.py              # Base CLI patterns and context models
│   ├── decorators.py        # CLI decorators
│   ├── formatters.py        # Output formatting utilities
│   ├── helpers.py           # Helper functions
│   └── types.py             # Click parameter types
├── config/                   # Configuration management
│   └── cli_config.py        # CLI configuration models
├── utils/                    # Utility modules
│   ├── auth.py              # Authentication utilities
│   ├── config.py            # Configuration utilities
│   └── output.py            # Output formatting utilities
├── cli.py                   # Main CLI entry point with Click group
├── client.py                # HTTP client for FLEXT services
├── simple_api.py            # Simple API for CLI setup
└── types.py                 # Type definitions
```

### Key Architectural Principles

- **flext-core Integration**: Uses flext-core DomainEntity, ServiceResult patterns
- **Click Framework**: Hierarchical command structure with rich help
- **Rich UI**: Beautiful terminal output with tables, progress bars, panels
- **Dependency Injection**: Container-based service registration
- **Type Safety**: Complete type coverage with MyPy strict mode

## Development Commands

### Essential Quality Gates (MANDATORY)

**⚠️ ALWAYS run before any code changes:**

```bash
# Complete validation pipeline (run before commits)
make validate                 # lint + type-check + security + test (90% coverage)

# Quick quality checks
make check                   # lint + type-check + test

# Individual checks
make lint                    # Ruff linting (ALL rules enabled)
make type-check              # MyPy strict mode (zero errors tolerated)
make test                    # pytest with 90% coverage requirement
make security                # Bandit + pip-audit + secrets scan
```

**Quality Gate Failures = STOP WORK:**

- Any linting errors must be fixed before proceeding
- Type check failures must be resolved (zero tolerance)
- Test coverage below 90% blocks commits
- Security vulnerabilities must be addressed

### Development Setup

```bash
# Full development environment
make setup                   # Complete setup with pre-commit hooks
make install                 # Install dependencies with Poetry

# Testing commands
make test                    # Full test suite with 90% coverage
make test-unit               # Unit tests only
make test-integration        # Integration tests only
make test-fast               # Tests without coverage

# Coverage reports
make coverage-html           # Generate HTML coverage report

# CLI testing
make cli-test                # Test CLI commands directly

# Build and maintenance
make build                   # Build package
make clean                   # Clean build artifacts
make deps-update             # Update dependencies
make deps-audit              # Audit dependencies for security
```

### Testing Commands

```bash
# Test execution
make test                    # Full test suite with 90% coverage requirement
make coverage                # Generate detailed coverage report
make coverage-html           # Generate and open HTML coverage report

# Individual test types (use pytest markers)
pytest -m unit               # Unit tests only
pytest -m integration        # Integration tests only
pytest -m "not slow"         # Exclude slow tests

# Test specific modules
pytest tests/test_auth_commands.py -v
pytest tests/test_domain_entities.py -v
pytest tests/test_core_decorators.py -v
```

## Core Patterns & Implementation Details

### CLI Entry Point Architecture

The main CLI is implemented in `src/flext_cli/cli.py:54` with Click groups:

```python
from flext_cli.cli import cli

# Main CLI group with global options and error handling
@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(version=__version__, prog_name="flext")
@click.option('--profile', default='default', envvar='FLX_PROFILE')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml', 'csv', 'plain']))
@click.option('--debug/--no-debug', default=False, envvar='FLX_DEBUG')
@click.option('--quiet/--no-quiet', default=False)
def cli(ctx, profile, output, debug, quiet):
    """FLEXT Command Line Interface with centralized error handling."""
```

**Entry Point:** `flext` command defined in `pyproject.toml:103` → `flext_cli.cli:main`

### Domain Entities (flext-core FlextEntity Pattern)

Core domain entities properly inherit from FlextEntity (`src/flext_cli/domain/entities.py`):

- **CLICommand** (line 77): Command execution with status tracking, proper validation rules
- **CLISession** (line 248): Session tracking with command history and immutable updates
- **CLIPlugin** (line 356): Plugin management with lifecycle methods
- **CLIConfig** (line 491): Value object using FlextValueObject pattern

**flext-core Integration Quality:**

```python
# ✅ GOOD: Proper FlextEntity usage
class CLICommand(FlextEntity):
    def validate_domain_rules(self) -> FlextResult[None]:
        if not self.name or not self.name.strip():
            return FlextResult.fail("Command name cannot be empty")
        return FlextResult.ok(None)

    def start_execution(self) -> CLICommand:
        return self.model_copy(update={"command_status": CommandStatus.RUNNING})
```

### FlextResult Pattern (Railway-Oriented Programming)

**✅ EXCELLENT flext-core Integration** - Consistently used across codebase:

```python
from flext_core import FlextResult

# Example from src/flext_cli/utils/auth.py:43
def save_auth_token(token: str) -> FlextResult[None]:
    try:
        # ... implementation
        return FlextResult.ok(None)
    except (OSError, PermissionError, ValueError) as e:
        return FlextResult.fail(f"Failed to save auth token: {e}")

# Usage pattern with handle_service_result decorator
@handle_service_result  # from src/flext_cli/core/base.py:93
def setup_cli(settings: CLISettings) -> FlextResult[bool]:
    # Returns FlextResult, decorator handles success/failure
```

**Pattern Usage Quality**: Excellent - proper error chaining, type safety, railway pattern

### Configuration Management (flext-core FlextBaseSettings)

**✅ GOOD flext-core Integration** - Uses FlextBaseSettings pattern:

```python
from flext_cli.utils.config import CLIConfig, CLISettings, get_config

# Configuration classes from src/flext_cli/utils/config.py:19
class CLIConfig(FlextBaseSettings):  # Uses flext-core FlextBaseSettings
    """CLI configuration using flext-core patterns."""
    profile: str = "default"
    output_format: str = "table"
    debug: bool = False

# Context management from src/flext_cli/core/base.py:21
class CLIContext(FlextValueObject):  # Uses flext-core FlextValueObject
    def validate_domain_rules(self) -> FlextResult[None]:
        # Domain validation with FlextResult
```

**Integration Quality**: Good - proper settings management, validation, environment variable support

## Command Implementation Patterns

### CLI Command Structure

Commands are organized into groups with standard patterns:

```python
import click
from rich.console import Console

@click.group()
def pipeline():
    """Pipeline management commands."""
    pass

@pipeline.command()
@click.option('--output', '-o', type=click.Choice(['table', 'json', 'yaml']), default='table')
@click.pass_context
def list(ctx: click.Context, output: str) -> None:
    """List all pipelines."""
    console: Console = ctx.obj["console"]
    config = ctx.obj["config"]

    # Use Rich for beautiful output
    console.print("[green]Available Pipelines:[/green]")
```

### Current Command Structure (LIMITED - Only 3 Commands Implemented)

**⚠️ IMPORTANT:** CLI currently has only 3 command groups implemented:

```python
# Commands registered in cli.py:100-102
cli.add_command(auth.auth)           # Authentication commands
cli.add_command(config.config)       # Configuration commands
cli.add_command(debug.debug_cmd)     # Debug commands

# Built-in placeholder commands
@cli.command()
def interactive(ctx: click.Context) -> None:
    """Start interactive mode (placeholder)."""  # NOT IMPLEMENTED

@cli.command()
def version(ctx: click.Context) -> None:
    """Show version information."""
```

**CRITICAL GAPS:**

- Pipeline management commands (mentioned but missing)
- Service integration commands (FlexCore port 8080, FLEXT Service port 8081)
- Plugin management commands
- Project-specific commands (ALGAR, GrupoNos, Meltano)
- Data management commands (taps, targets, dbt)

### Rich UI Patterns

Use Rich library for enhanced terminal output:

```python
from rich.table import Table
from rich.progress import track

# Create beautiful tables
table = Table(title="Pipeline Status")
table.add_column("Name", style="cyan")
table.add_column("Status", style="green")

# Progress bars and spinners
for item in track(items, description="Processing..."):
    process_item(item)
```

## Testing Strategy

### Domain Entity Testing

```python
from flext_cli.domain.entities import CLICommand, CommandStatus

def test_command_lifecycle():
    command = CLICommand(
        name="test",
        command_line="echo hello",
        command_type=CommandType.SYSTEM
    )

    # Test execution lifecycle
    command.start_execution()
    assert command.command_status == CommandStatus.RUNNING
    assert command.started_at is not None

    command.complete_execution(exit_code=0, stdout="hello")
    assert command.successful
    assert command.command_status == CommandStatus.COMPLETED
```

### CLI Command Testing

```python
from click.testing import CliRunner
from flext_cli.cli import cli

def test_cli_version():
    runner = CliRunner()
    result = runner.invoke(cli, ['--version'])
    assert result.exit_code == 0
    assert "FLEXT CLI" in result.output

def test_pipeline_list():
    runner = CliRunner()
    result = runner.invoke(cli, ['pipeline', 'list'])
    assert result.exit_code == 0
```

### Service Testing with ServiceResult

```python
from flext_cli.simple_api import setup_cli
from flext_cli.utils.config import CLISettings

def test_cli_setup():
    settings = CLISettings()
    result = setup_cli(settings)
    assert result.success
    assert result.unwrap() is True
```

## Configuration Management

### CLI Entry Points

The project provides the main CLI entry point:

- `flext`: Main CLI command (`flext --help`)

### Configuration Files

- Project config: `config/dev.yaml`, `config/prod.yaml`
- User config: `~/.flx/config.yaml` (future)
- Environment variables override file settings

### Environment Variables

```bash
export FLEXT_CLI_DEV_MODE=true
export FLEXT_CLI_LOG_LEVEL=debug
export FLEXT_CLI_CONFIG_PATH=/path/to/config.yaml
export FLX_PROFILE=development
export FLX_DEBUG=true
```

## Quality Standards

### Mandatory Requirements

- **Zero lint violations**: Ruff with ALL rules enabled
- **Zero type errors**: MyPy strict mode (no `Any` types)
- **90% test coverage**: Enforced by pytest-cov
- **Security scanning**: Bandit + pip-audit clean
- **Pre-commit hooks**: Automatic quality enforcement

### Code Style

- **Python 3.13+**: Modern syntax and type hints
- **Clean Architecture**: Strict layer separation
- **Domain-Driven Design**: Rich domain entities
- **Type Safety**: Complete type coverage with MyPy

## Dependencies

### Core Dependencies

- **flext-core**: Foundation library with FlextEntity, FlextResult patterns
- **flext-observability**: Monitoring and metrics
- **Click 8.2+**: CLI framework with groups and commands
- **Rich 14.0+**: Terminal UI components (tables, progress, panels)
- **Pydantic 2.11+**: Data validation and settings management
- **httpx**: HTTP client for API communication
- **structlog**: Structured logging

### FLEXT Ecosystem Dependencies

- **algar-oud-mig**: ALGAR project integration (local dependency)
- **gruponos-meltano-native**: GrupoNos project integration (local dependency)
- **flext-meltano**: Meltano orchestration (local dependency)

### Quality & Development Tools

- **MyPy**: Strict type checking (zero errors tolerated)
- **Ruff**: Linting with ALL rules enabled
- **pytest**: Testing with 90% coverage requirement
- **Bandit**: Security scanning
- **pre-commit**: Quality gate automation

## Common Workflows

### Adding New CLI Commands

**MANDATORY PROCESS:**

1. **Create command module** in `src/flext_cli/commands/` directory
2. **Follow existing patterns** from `auth.py`, `config.py`, `debug.py`
3. **Use Click decorators** with Rich output formatting
4. **Register command** in `src/flext_cli/cli.py` main group (around line 100)
5. **Add comprehensive tests** in `tests/test_[command_name].py` with CliRunner
6. **Run quality gates** `make validate` before committing

**REAL EXAMPLE (following exact project patterns):**

```python
# src/flext_cli/commands/pipeline.py
import click
from rich.console import Console
from flext_cli.core.base import handle_service_result

@click.group()
def pipeline():
    """Pipeline management commands."""
    pass

@pipeline.command()
@click.option('--output', '-o', type=click.Choice(['table', 'json', 'yaml']), default='table')
@click.pass_context
@handle_service_result
def list(ctx: click.Context, output: str) -> None:
    """List all pipelines."""
    console: Console = ctx.obj["console"]
    config = ctx.obj["config"]

    # Implementation using flext-core patterns
    console.print("[green]Available Pipelines:[/green]")

# Register in src/flext_cli/cli.py (add after line 102)
from flext_cli.commands import pipeline
cli.add_command(pipeline.pipeline)
```

**Testing Pattern:**

```python
# tests/test_pipeline_commands.py
from click.testing import CliRunner
from flext_cli.cli import cli

def test_pipeline_list():
    runner = CliRunner()
    result = runner.invoke(cli, ['pipeline', 'list'])
    assert result.exit_code == 0
```

### Extending Domain Entities

1. Add new entities in `domain/entities.py` using flext-core patterns
2. Follow `DomainEntity` base class with proper field validation
3. Add domain events for entity lifecycle changes
4. Create comprehensive unit tests for entity behavior
5. Consider adding to service container if needed

### Adding New Command Groups

1. Create new command module in `commands/`
2. Follow existing patterns from `auth.py`, `config.py`, `debug.py`
3. Use Click groups and Rich console for output
4. Register commands in `cli.py` main group
5. Add comprehensive tests with CliRunner

### Testing Commands

```bash
# Test specific command module
pytest tests/test_auth_commands.py -v
pytest tests/test_debug_commands.py -v

# Test with actual CLI
poetry run flext auth --help
poetry run flext config --help
poetry run flext debug --help
poetry run flext --version

# Run full test suite with coverage
make test                        # 90% coverage requirement
pytest tests/ -v --cov=src/flext_cli --cov-report=term-missing
```

## Current Command Structure

**ACTUAL implementation (only 3 command groups work):**

```bash
flext --help                     # Main CLI help
├── auth                        # Authentication commands (IMPLEMENTED)
├── config                      # Configuration management (IMPLEMENTED)
├── debug                       # Debug and diagnostic tools (IMPLEMENTED)
├── interactive                 # Interactive mode (PLACEHOLDER - not functional)
└── version                     # Version information (basic implementation)
```

**Testing current commands:**

```bash
poetry run flext auth --help      # Works
poetry run flext config --help    # Works
poetry run flext debug --help     # Works
poetry run flext interactive      # Shows "coming soon" message
poetry run flext version          # Shows version info
```

Entry point is defined in `pyproject.toml:103`:

```toml
[project.scripts]
flext = "flext_cli.cli:main"
```

## CLI Development Patterns

### Adding New Commands

Follow the established pattern using Click groups:

```python
# commands/new_feature.py
import click
from rich.console import Console

@click.group()
def new_feature():
    """New feature commands."""
    pass

@new_feature.command()
@click.pass_context
def action(ctx: click.Context) -> None:
    """Perform new feature action."""
    console: Console = ctx.obj["console"]
    console.print("[green]Success![/green]")

# Register in cli.py
from flext_cli.commands import new_feature
cli.add_command(new_feature.new_feature)
```

## Key Files Reference (Exact Locations)

### Core Entry Points

- `src/flext_cli/cli.py:54` - Main CLI group definition with global options
- `src/flext_cli/cli.py:132` - Main entry point function with FlextUtilities error handling
- `src/flext_cli/cli.py:100-102` - Command registration (auth, config, debug only)

### Domain Layer (Clean Architecture)

- `src/flext_cli/domain/entities.py:77` - CLICommand entity with execution lifecycle
- `src/flext_cli/domain/entities.py:248` - CLISession entity for session tracking
- `src/flext_cli/domain/entities.py:356` - CLIPlugin entity for plugin management
- `src/flext_cli/domain/cli_context.py` - CLI context value objects
- `src/flext_cli/core/base.py:21` - CLIContext with validation rules

### Current Command Implementations (Only 3)

- `src/flext_cli/commands/auth.py` - Authentication commands (functional)
- `src/flext_cli/commands/config.py` - Configuration management (functional)
- `src/flext_cli/commands/debug.py` - Debug and diagnostic tools (functional)

### Core Utilities & Infrastructure

- `src/flext_cli/core/base.py:93` - handle_service_result decorator for FlextResult
- `src/flext_cli/core/decorators.py` - CLI decorators and patterns
- `src/flext_cli/core/formatters.py` - Output formatting utilities
- `src/flext_cli/utils/output.py` - Rich console output utilities
- `src/flext_cli/utils/config.py` - Configuration utilities and settings
- `src/flext_cli/infrastructure/container.py` - Dependency injection container

### Configuration Files

- `pyproject.toml:103` - CLI entry point definition
- `pyproject.toml:27-44` - Dependencies (flext-core, algar-oud-mig, etc.)
- `Makefile:26` - Quality gates (validate = lint + type-check + security + test)

## Architecture Implementation Status & Critical Gaps

### ✅ IMPLEMENTED (Functional)

- **Clean Architecture**: Domain → Application → Infrastructure layers working
- **flext-core Foundation**: FlextResult pattern, FlextEntity, FlextValueObject, FlextBaseSettings
- **Quality Gates**: 90% coverage, MyPy strict mode, Ruff linting
- **Core Commands**: auth, config, debug command groups functional
- **Rich UI**: Terminal output with tables, progress bars, panels
- **Type Safety**: Complete MyPy coverage with zero errors tolerated

### 🚨 CRITICAL GAPS (Missing Core Functionality)

#### GAP 1: Limited Command Coverage (Only 3/10+ Expected)

**Current:** auth, config, debug only  
**Missing:** pipeline, plugin, service, data, monitoring, project-specific commands  
**Impact:** CLI cannot manage FLEXT ecosystem as designed

#### GAP 2: Service Integration Missing

**Missing:** FlexCore (port 8080) and FLEXT Service (port 8081) integration  
**Current:** HTTP client exists (`src/flext_cli/client.py`) but unused  
**Impact:** Cannot manage distributed services

#### GAP 3: Interactive Mode Placeholder

**Current:** `flext interactive` shows "coming soon" message  
**Missing:** REPL, tab completion, command history  
**Impact:** Reduced developer experience

#### GAP 4: Configuration Profile System Incomplete

**Current:** `--profile` option exists but loading not implemented  
**Missing:** Profile loading, user config (~/.flx/config.YAML), multi-environment  
**Impact:** Cannot manage different deployment environments

### 🏗️ FLEXT-CORE INTEGRATION ANALYSIS (60% Complete)

#### ✅ **Excellent Integration (Core Patterns)**

1. **FlextResult Pattern** - Consistent railway-oriented programming

   - Files: `utils/auth.py`, `api.py`, `core.py`, all domain entities
   - Quality: Excellent error handling, proper type safety

2. **FlextEntity Pattern** - Proper domain entity inheritance

   - Files: `domain/entities.py:77` (CLICommand), line 248 (CLISession), line 356 (CLIPlugin)
   - Quality: Good domain modeling with validation rules

3. **FlextValueObject Pattern** - Immutable value objects

   - Files: `domain/entities.py:491` (CLIConfig), `core/base.py:21` (CLIContext)
   - Quality: Proper immutability and validation

4. **FlextBaseSettings Pattern** - Configuration management
   - Files: `utils/config.py:19` (CLIConfig class)
   - Quality: Good environment variable integration

#### ⚠️ **Partial Integration (Missing Advanced Patterns)**

1. **Service Layer** - Basic services but not using FlextDomainService

   - Current: `domain/cli_services.py:29` (basic service classes)
   - Missing: FlextDomainService inheritance, proper service patterns

2. **Dependency Injection** - Custom container instead of FlextContainer
   - Current: `infrastructure/container.py:18` (SimpleDIContainer)
   - Missing: FlextContainer integration, type-safe dependency resolution

#### ❌ **Missing Critical Enterprise Patterns**

1. **CQRS Pattern** - No command/query separation

   - Missing: FlextCommands, command handlers
   - Impact: No separation between commands and queries

2. **Domain Events** - Events defined but not used

   - Current: Events defined in `domain/entities.py:510` but unused
   - Missing: FlextEvent, FlextEventPublisher, FlextEventSubscriber
   - Impact: No event-driven architecture

3. **Repository Pattern** - Only mock implementations

   - Current: Mock repositories in `infrastructure/container.py:129`
   - Missing: Real FlextRepository implementations
   - Impact: No persistent storage for entities

4. **Aggregate Root Pattern** - No domain aggregates
   - Missing: FlextAggregateRoot usage
   - Impact: No aggregate boundaries or complex business rules

## Working with This Codebase

### Before Making Changes

1. **Run quality gates:** `make validate` (MANDATORY)
2. **Check current command structure:** `poetry run flext --help`
3. **Understand architecture:** Read domain entities in `src/flext_cli/domain/entities.py`
4. **Follow existing patterns:** Study `auth.py`, `config.py`, `debug.py`

### When Adding Commands (Follow flext-core Patterns)

1. **Create in correct location:** `src/flext_cli/commands/[name].py`
2. **Use flext-core patterns properly:**

   ```python
   from flext_core import FlextResult, get_logger
   from flext_cli.core.base import handle_service_result

   @handle_service_result  # Handles FlextResult automatically
   def my_command() -> FlextResult[Any]:
       return FlextResult.ok(data)
   ```

3. **Register in cli.py:** Add import and `cli.add_command()` call around line 102
4. **Add comprehensive tests:** Use CliRunner in `tests/test_[name].py`
5. **Verify quality gates:** `make validate` must pass before commit

### When Working with Domain Entities

1. **Always inherit from FlextEntity:** Use proper domain entity patterns
2. **Implement validation rules:** Every entity must have `validate_domain_rules() -> FlextResult[None]`
3. **Use immutable updates:** `return self.model_copy(update={...})` for state changes
4. **Add domain events:** Consider adding events for entity lifecycle changes

### When Debugging Issues

1. **Use debug mode:** `poetry run flext --debug [command]`
2. **Check logs:** Structured logging with flext-core
3. **Run individual tests:** `pytest tests/test_[specific].py -v`
4. **Verify coverage:** `make coverage-html` and check reports/

### Understanding flext-core Integration Levels

- **Level 1 (Basic)**: FlextResult, FlextEntity, FlextValueObject ✅ **IMPLEMENTED**
- **Level 2 (Enterprise)**: FlextDomainService, FlextContainer, FlextRepository ⚠️ **PARTIAL**
- **Level 3 (Advanced)**: CQRS, Domain Events, Aggregate Roots ❌ **MISSING**

### Dependencies (flext-core Ecosystem)

- **flext-core:** Foundation library - 60% integration complete
  - ✅ FlextResult (excellent), FlextEntity (good), FlextBaseSettings (good)
  - ❌ FlextContainer, CQRS, Domain Events, Repository pattern
- **Click:** CLI framework with hierarchical commands
- **Rich:** Terminal UI (tables, progress bars, panels)
- **Pydantic:** Data validation (used via flext-core)
- **Local dependencies:** algar-oud-mig, gruponos-meltano-native, flext-meltano

### Improving flext-core Integration

When adding new features, prioritize implementing missing flext-core patterns:

1. **Use FlextContainer** instead of SimpleDIContainer
2. **Implement CQRS** for command/query separation
3. **Add Domain Events** for entity lifecycle
4. **Create Repository implementations** for data persistence

This CLI has good foundations but needs enterprise patterns to be production-ready.
