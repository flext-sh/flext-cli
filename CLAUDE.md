# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FLEXT CLI is a modern command-line interface built with Python 3.13+, Click, and Rich libraries. It uses flext-core patterns for domain modeling and dependency injection, providing CLI commands for the FLEXT ecosystem including authentication, configuration, and debug operations.

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

### Essential Quality Gates
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

### Development Setup
```bash
# Full development environment
make setup                   # Complete setup with pre-commit hooks
make install                 # Install dependencies with Poetry
make dev-install             # Development mode with all extras

# CLI-specific operations
make install-cli             # Install CLI globally with pip  
make test-cli                # Test CLI commands
make cli-smoke-test          # Run smoke tests
make cli-validate            # Validate CLI implementation
make cli-performance         # Test CLI performance
make build-docs              # Build CLI documentation
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

## Core Patterns

### CLI Entry Point

Main CLI structure with Click groups and commands:

```python
from flext_cli.cli import cli

# Main CLI group with global options
@click.group()
@click.option('--profile', default='default', help='Configuration profile')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml', 'csv']), default='table')
@click.option('--debug/--no-debug', default=False, help='Enable debug mode')
def cli(profile: str, output: str, debug: bool) -> None:
    """FLEXT Command Line Interface."""
```

### Domain Entities (flext-core based)

Core domain entities using flext-core patterns:

- **CLICommand**: Command execution with status tracking (`CommandStatus.PENDING/RUNNING/COMPLETED/FAILED`)
- **CLIConfig**: Configuration with validation and hierarchical settings
- **CLISession**: Session tracking with command history and user context
- **CLIPlugin**: Plugin management with dependencies and lifecycle methods

### Service Result Pattern

All services use `ServiceResult[T]` for type-safe error handling:

```python
from flext_core.domain.types import ServiceResult

result: ServiceResult[Any] = setup_cli(settings)
if result.is_success:
    data = result.unwrap()
else:
    error = result.error
```

### CLI Context and Configuration

Configuration management using flext-core patterns:

```python
from flext_cli.utils.config import CLIConfig, get_config

# Get configuration with profile support
config = get_config()
config.profile = "development"
config.output_format = "json"
config.debug = True
```

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

### Current Command Structure

Available commands as currently implemented:

```python
# Commands registered in cli.py
cli.add_command(auth.auth)           # Authentication commands
cli.add_command(config.config)       # Configuration commands  
cli.add_command(debug.debug_cmd)     # Debug commands

# Built-in commands
@cli.command()
def interactive(ctx: click.Context) -> None:
    """Start interactive mode (placeholder)."""

@cli.command()
def version(ctx: click.Context) -> None:
    """Show version information."""
```

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
    assert command.is_successful
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
    assert result.is_success
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
- **client-a-oud-mig**: client-a project integration (local dependency)
- **client-b-meltano-native**: client-b project integration (local dependency)
- **flext-meltano**: Meltano orchestration (local dependency)

### Quality & Development Tools
- **MyPy**: Strict type checking (zero errors tolerated)
- **Ruff**: Linting with ALL rules enabled
- **pytest**: Testing with 90% coverage requirement
- **Bandit**: Security scanning
- **pre-commit**: Quality gate automation

## Common Workflows

### Adding New CLI Commands
1. Create command module in `commands/` or `commands/projects/`
2. Use Click decorators with Rich output formatting
3. Register command in `cli.py` main group
4. Add comprehensive tests with CliRunner
5. Run `make validate` before committing

Example new command:
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

The CLI currently provides these command groups:

```bash
flext --help                     # Main CLI help
├── auth                        # Authentication commands
├── config                      # Configuration management  
├── debug                       # Debug and diagnostic tools
├── interactive                 # Interactive mode (placeholder)
└── version                     # Version information
```

Entry point is defined in `pyproject.toml`:
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

## Key Files Reference

### Core Entry Points
- `src/flext_cli/cli.py:54` - Main CLI group definition with global options
- `src/flext_cli/cli.py:132` - Main entry point function with error handling

### Domain Layer
- `src/flext_cli/domain/entities.py:77` - CLICommand entity with execution tracking
- `src/flext_cli/domain/cli_context.py` - CLI context value objects
- `src/flext_cli/domain/cli_services.py` - Domain services

### Command Implementations
- `src/flext_cli/commands/auth.py` - Authentication commands
- `src/flext_cli/commands/config.py` - Configuration management
- `src/flext_cli/commands/debug.py` - Debug and diagnostic tools

### Core Utilities
- `src/flext_cli/core/decorators.py` - CLI decorators and patterns
- `src/flext_cli/core/formatters.py` - Output formatting utilities
- `src/flext_cli/utils/output.py` - Rich console output utilities

### Configuration & Infrastructure
- `src/flext_cli/infrastructure/container.py` - Dependency injection container
- `src/flext_cli/utils/config.py` - Configuration utilities and settings

## TODO: GAPS DE ARQUITETURA IDENTIFICADOS - PRIORIDADE ALTA

### 🚨 GAP 1: Funcionalidade CLI Incompleta (Apenas 3 Commands)
**Status**: CRÍTICO - CLI tem apenas auth, config, debug commands
**Problema**:
- CLI menciona pipeline management mas não implementado
- Ecosystem services (32 projetos) não têm CLI commands
- Commands críticos missing: pipeline, deploy, service, data, monitor

**TODO**:
- [ ] Implementar pipeline management commands (list, start, stop, status)
- [ ] Criar service management commands para ecosystem services
- [ ] Adicionar data management commands (taps, targets, dbt)
- [ ] Implementar monitoring/observability commands
- [ ] Criar deployment/orchestration commands

### 🚨 GAP 2: Integração com Ecosystem Services Missing
**Status**: ALTO - CLI não integra com FlexCore, FLEXT Service, etc
**Problema**:
- HTTP client existe mas não integra com ecosystem services
- Não tem commands para FlexCore (Go) port 8080
- Não tem commands para FLEXT Service (Go/Python) port 8081
- Service discovery não implementado

**TODO**:
- [ ] Implementar integration com FlexCore (Go) service
- [ ] Criar commands para FLEXT Service management
- [ ] Implementar service discovery patterns
- [ ] Adicionar health check commands para todos os services

### 🚨 GAP 3: Interactive Mode Placeholder
**Status**: ALTO - Interactive mode mencionado mas não implementado
**Problema**:
- Interactive command é placeholder
- Não tem REPL ou interactive shell
- Tab completion não implementado

**TODO**:
- [ ] Implementar interactive mode com Rich-based REPL
- [ ] Adicionar tab completion para commands e options
- [ ] Criar context-aware help system
- [ ] Implementar command history e recall

### 🚨 GAP 4: Configuration Profile System Incomplete
**Status**: ALTO - Profile system mencionado mas não completo
**Problema**:
- Profile option existe mas profile loading não implementado
- Multi-environment configuration não funcional
- User config (~/.flx/config.yaml) não implementado

**TODO**:
- [ ] Implementar profile loading system
- [ ] Criar user configuration directory e files
- [ ] Implementar environment-specific profiles
- [ ] Adicionar profile management commands (create, list, switch)
