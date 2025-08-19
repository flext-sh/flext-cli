# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**⚠️ IMPORTANT: This is a CLI foundation library that serves as the base for FLEXT ecosystem CLI implementations.**

FLEXT CLI is a Python 3.13 foundation library for command-line interfaces built with Click, Rich, and flext-core integration patterns. It provides the foundational layer for CLI implementations across the FLEXT ecosystem.

## Primary Functions

This library has **3 main functions**:

### 1. **CLI Foundation Base**

Foundation library for any standalone CLI implementation or flext-service CLI integration:

- Clean Architecture patterns following `flext/docs/patterns`
- FlextModel/FlextEntity/FlextResult standard patterns
- Rich terminal UI components with consistent theming
- Command execution lifecycle with proper error handling

### 2. **flext-core Integration Bridge**

Deep integration bridge that connects CLI usage with flext-core basic configuration:

- FlextCLIConfigHierarchical for configuration management
- FlextBaseSettings with automatic environment loading
- FlextEntity patterns for CLI domain entities (CLICommand, CLISession, CLIPlugin)
- FlextResult railway-oriented programming throughout
- Standard FlextFactory patterns for entity creation

### 3. **Ecosystem Library Base**

Generic foundation patterns for ANY ecosystem project to implement in their own codebase:

- Unified CLI utilities and patterns (`src/flext_cli/simple_api.py`, `src/flext_cli/api.py`)
- Standardized data formatting and export (JSON, YAML, CSV, Rich tables)
- Generic command patterns (`FlextCliGenericCommand`) that projects extend
- Configuration factory patterns (`FlextCliConfigFactory`) for project-specific settings
- Project-agnostic setup functions that eliminate 85% of CLI boilerplate

**Current Status:** Foundation library with 3 working command groups (`auth`, `config`, `debug`). API and core services implemented. CLI entry point: `flext` command via `pyproject.toml:103`.

## Library Architecture

**⚠️ Note:** This implements Clean Architecture for CLI foundation, designed to be reused across FLEXT ecosystem projects.

### Foundation Library Structure

```
src/flext_cli/
├── domain/                 # CLI domain entities (CLICommand, CLISession, CLIPlugin)
├── application/           # CLI command handlers
├── infrastructure/        # HTTP clients, dependency injection
├── commands/              # Reference CLI implementations (auth, config, debug)
├── core/                  # Base patterns, decorators, formatters
├── api.py                 # High-level API functions for library consumers
├── simple_api.py          # Zero-boilerplate setup functions
├── core.py                # Core service implementation
└── cli.py                # Reference CLI entry point
```

**Foundation Patterns:**

- **FlextResult**: Railway-oriented programming for CLI error handling
- **FlextEntity Integration**: CLI domain entities with flext-core patterns
- **FlextService Implementation**: Service interfaces for ecosystem integration
- **Rich UI Patterns**: Reusable terminal output components
- **Click Framework**: Extensible command structure patterns

## Development Commands

### Quality Gates (Run Before Commits)

```bash
make validate         # Complete validation: lint + type-check + security + test
make check           # Quick check: lint + type-check
make test           # Run tests with 90% coverage requirement
make lint           # Ruff linting
make type-check     # MyPy strict mode (zero errors tolerated)
```

### Development Setup

```bash
make setup          # Complete setup with pre-commit hooks
make install        # Install dependencies
make build          # Build package
make clean          # Clean build artifacts
```

### Testing

```bash
make test                              # Full test suite with coverage
make test-unit                         # Unit tests only
make test-integration                  # Integration tests only
pytest tests/test_auth_commands.py -v  # Test specific module
make coverage-html                     # Generate HTML coverage report
```

## Core Patterns & Implementation

### FlextResult Pattern (Railway-Oriented Programming)

```python
from flext_core import FlextResult

def save_auth_token(token: str) -> FlextResult[None]:
    try:
        return FlextResult[None].ok(None)
    except (OSError, PermissionError, ValueError) as e:
        return FlextResult[None].fail(f"Failed to save auth token: {e}")

# Usage with decorator
@handle_service_result  # from src/flext_cli/core/base.py:93
def setup_cli(settings: CLISettings) -> FlextResult[bool]:
    return FlextResult[None].ok(True)
```

### Domain Entities (flext-core Integration)

```python
class CLICommand(FlextEntity):
    def validate_domain_rules(self) -> FlextResult[None]:
        if not self.name or not self.name.strip():
            return FlextResult[None].fail("Command name cannot be empty")
        return FlextResult[None].ok(None)

    def start_execution(self) -> CLICommand:
        return self.model_copy(update={"command_status": CommandStatus.RUNNING})
```

### CLI Entry Point

Main CLI in `src/flext_cli/cli.py:70`:

```python
@click.group()
@click.option('--profile', default='default', envvar='FLX_PROFILE')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml', 'csv']))
@click.option('--debug/--no-debug', default=False, envvar='FLX_DEBUG')
def cli(ctx, profile, output, debug):
    """FLEXT Command Line Interface."""
    # Context setup with Rich console and configuration
```

## Adding New CLI Commands

**⚠️ Important:** This CLI only implements command-line interfaces to interact with FLEXT services. It does not implement business logic - it sends requests to the actual FLEXT services.

**Current Status:** Only 3 command groups work: `auth`, `config`, `debug`. Most ecosystem service integration commands are missing.

### Implementation Process

1. Create command module in `src/flext_cli/commands/[name].py`
2. Follow patterns from existing `auth.py`, `config.py`, `debug.py`
3. Use HTTP client (`src/flext_cli/client.py`) to communicate with FLEXT services
4. Register command in `src/flext_cli/cli.py` around line 100
5. Add tests in `tests/test_[name].py` using CliRunner
6. Run `make validate` before committing

### Example Implementation (Service Integration)

```python
# src/flext_cli/commands/pipeline.py
import click
from rich.console import Console
from flext_cli.core.base import handle_service_result
from flext_cli.client import FlextClient  # HTTP client for FLEXT services

@click.group()
def pipeline():
    """Pipeline management commands - connects to FLEXT Service."""
    pass

@pipeline.command()
@click.option('--output', '-o', type=click.Choice(['table', 'json']), default='table')
@click.pass_context
@handle_service_result
def list(ctx: click.Context, output: str) -> None:
    """List all pipelines from FLEXT Service."""
    console: Console = ctx.obj["console"]
    client = FlextClient()

    # Call actual FLEXT service - this CLI doesn't contain pipeline logic
    result = client.get_pipelines()
    if result.success:
        console.print("[green]Available Pipelines:[/green]")
        # Display results from FLEXT service
    else:
        console.print(f"[red]Error: {result.error}[/red]")

# Register in src/flext_cli/cli.py
from flext_cli.commands import pipeline
cli.add_command(pipeline.pipeline)
```

## Testing & Configuration

### CLI Testing Patterns

```python
from click.testing import CliRunner
from flext_cli.cli import cli

def test_cli_command():
    runner = CliRunner()
    result = runner.invoke(cli, ['auth', '--help'])
    assert result.exit_code == 0

def test_command_lifecycle():
    command = CLICommand(name="test", command_line="echo hello")
    result = command.validate_domain_rules()
    assert result.success
```

### Environment Variables

```bash
export FLX_PROFILE=development    # Configuration profile
export FLX_DEBUG=true            # Enable debug mode
export FLEXT_CLI_LOG_LEVEL=debug # Logging level
```

### Current Commands (Limited - Only 3 Work)

```bash
poetry run flext --help              # Main CLI help
poetry run flext auth --help         # Authentication commands ✅
poetry run flext config --help       # Configuration commands ✅
poetry run flext debug --help        # Debug commands ✅
poetry run flext interactive          # Placeholder - shows "coming soon"
poetry run flext version             # Basic version information
```

## Ecosystem Integration Analysis

### flext-core Integration (Foundation Layer)

This library is **deeply integrated** with flext-core as the foundation:

```python
# FlextResult patterns throughout CLI operations
from flext_core import FlextResult, FlextEntity, FlextBaseSettings

# Domain entities inherit from flext-core
class CLICommand(FlextEntity):
    def validate_domain_rules(self) -> FlextResult[None]:
        # Validation with railway-oriented programming

# Configuration management
class CLIConfig(FlextBaseSettings):
    # Automatic environment variable loading
```

### Library Dependencies & Integration

**Core Foundation:**

- **flext-core**: FlextEntity, FlextResult, FlextBaseSettings, FlextService patterns
- **flext-observability**: Monitoring integration
- **flext-api**: Service communication patterns

**Ecosystem Projects Using This Library:**

- **flext-meltano**: Uses CLI patterns for Meltano orchestration
- **client-a-oud-mig**: client-a project CLI integration
- **client-b-meltano-native**: client-b project CLI

**CLI Framework:**

- **Click 8.2+**: Command structure framework
- **Rich 14.0+**: Terminal UI components
- **httpx**: HTTP client patterns for service communication

### Library Usage Patterns

**For Standalone CLIs:**

```python
from flext_cli import setup_cli, CLIConfig
from flext_cli.api import FlextCliApi

# Zero-boilerplate setup
config = CLIConfig()
result = setup_cli(config)
```

**For Service Integration:**

```python
from flext_cli.core import FlextCliService
from flext_cli.simple_api import create_cli_context

# Service-based integration
service = FlextCliService()
context = create_cli_context()
```

## Implementation Status & Critical Gaps

### ✅ Implemented

- Clean Architecture with Domain/Application/Infrastructure layers
- flext-core FlextResult and FlextEntity patterns
- 3 functional command groups: auth, config, debug
- Quality gates: MyPy strict mode, Ruff linting, 90% test coverage

### 🚨 Critical Gaps

- **Limited Commands**: Only 3/10+ planned commands implemented
- **Service Integration Missing**: HTTP client exists (`src/flext_cli/client.py`) but unused by commands
- **Interactive Mode**: Placeholder only ("coming soon" message)
- **Profile System Incomplete**: `--profile` option exists but loading not implemented
- **Enterprise Patterns Missing**: CQRS, Domain Events, Repository Pattern (mocks only)

## Key File Locations

### Core Entry Points

- `src/flext_cli/cli.py:70` - Main CLI group definition with global options
- `src/flext_cli/commands/` - Only auth.py, config.py, debug.py implemented
- `pyproject.toml:103` - Entry point: `flext = "flext_cli.cli:main"`

### Domain Layer (CLI Architecture)

- `src/flext_cli/domain/entities.py` - CLICommand, CLISession, CLIPlugin entities
- `src/flext_cli/core/base.py:93` - handle_service_result decorator for FlextResult
- `src/flext_cli/client.py` - HTTP client for FLEXT services (currently unused)

## Development Workflow

### Working with Foundation Library

**⚠️ Remember:** This is a **foundation library** providing CLI patterns for the FLEXT ecosystem, not just a standalone CLI.

### Before Making Changes

1. Run `make validate` (MANDATORY quality gate)
2. Check library APIs: `src/flext_cli/api.py`, `src/flext_cli/simple_api.py`
3. Study foundation patterns in `src/flext_cli/core/`, `src/flext_cli/domain/`
4. **Consider impact**: Changes affect all projects using this library (flext-meltano, client-a-oud-mig, client-b-meltano-native)

### Adding Foundation Patterns

1. Add reusable patterns in `src/flext_cli/core/` following Clean Architecture
2. Extend API functions in `src/flext_cli/api.py` for programmatic use
3. Update `src/flext_cli/simple_api.py` for zero-boilerplate usage
4. Add comprehensive tests covering library usage patterns
5. Run `make validate` before committing

### Adding Reference Commands

1. Create reference implementations in `src/flext_cli/commands/[name].py`
2. These serve as **examples** for other projects, not production commands
3. Focus on demonstrating foundation patterns and flext-core integration
4. Document usage patterns for ecosystem projects

### Library Integration Guide

**For projects using flext-cli as dependency:**

1. Import foundation patterns: `from flext_cli.api import FlextCliApi`
2. Use zero-boilerplate setup: `from flext_cli import setup_cli`
3. Extend CLI entities: `from flext_cli.domain.entities import CLICommand`
4. Follow flext-core integration patterns demonstrated in this library

This library provides the **foundation** for CLI implementations across FLEXT ecosystem projects.
