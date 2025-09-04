# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FLEXT CLI is a command-line interface foundation library for the FLEXT ecosystem. It serves as both a standalone CLI tool and a library for other projects to build their own CLI interfaces.

**Current Status**: ~30% functional - 3 working command groups (auth, config, debug) out of planned 10+ groups.

## Key Architecture Insights

**Modern Python 3.13+ Patterns**: The codebase utilizes advanced Python features including pattern matching (match-case), functional programming patterns, and comprehensive type annotations.

**flext-core Integration**: Heavy integration with the foundation library provides FlextResult railway-oriented programming, FlextPipeline for sequential operations, and FlextUtilities for safe operations.

**Code Quality Focus**: Zero-tolerance quality approach with comprehensive linting (Ruff), type checking (MyPy strict mode), and 90% test coverage requirements.

## Development Commands

### Essential Commands

```bash
# Complete validation pipeline (run before commits)
make validate                 # lint + type-check + security + test (90% coverage)

# Quick development checks
make check                   # lint + type-check only
make lint                    # Ruff linting
make type-check              # MyPy strict mode
make test                    # pytest with coverage
make format                  # Auto-format code
make security               # Bandit security scan
```

### Setup Commands

```bash
make setup                   # Complete setup with pre-commit hooks
make install                 # Install dependencies with Poetry
make install-dev             # Install with dev dependencies
make clean                   # Clean build artifacts
make reset                   # Complete reset (clean + setup)
```

### Testing Commands

```bash
make test                    # Full test suite with 90% coverage requirement
make test-unit               # Unit tests only
make test-integration        # Integration tests only
make test-fast               # Tests without coverage
make coverage-html           # Generate HTML coverage report

# Test specific modules
pytest tests/test_core.py -v
pytest tests/test_commands_auth.py -v
```

### CLI Testing

```bash
# Test CLI functionality
make cli-test                # Basic CLI import test
poetry run flext --help     # Test main CLI
poetry run flext auth --help # Test auth commands
poetry run flext config --help # Test config commands
poetry run flext debug --help  # Test debug commands
```

## Architecture

### High-Level Structure

```
src/flext_cli/
├── cli.py                   # Main CLI entry point with Click framework
├── auth.py                  # Authentication command group
├── cmd.py                   # Configuration commands 
├── debug.py                 # Debug/diagnostic commands
├── api.py                   # High-level API for library consumers
├── core.py                  # Core service implementation
├── client.py                # HTTP client for FLEXT services
├── config.py                # Configuration management (FlextCliConfig)
├── models.py                # Domain models and entities
├── constants.py             # Project constants (FlextCliConstants)
├── exceptions.py            # Custom exception classes
├── formatters.py            # Output formatting utilities
├── data_processing.py       # Data processing operations
└── services.py              # Business logic services
```

### Key Patterns

**FlextResult Pattern**: Railway-oriented programming for error handling

```python
from flext_core import FlextResult

def save_config() -> FlextResult[None]:
    try:
        # Operation here
        return FlextResult[None].ok(None)
    except Exception as e:
        return FlextResult[None].fail(f"Failed: {e}")
```

**Python 3.13+ Pattern Matching**: Modern conditional logic using match-case

```python
def format_data(data: object, format_type: str) -> FlextResult[str]:
    match format_type.lower():
        case "json":
            return FlextUtilities.safe_json_stringify(data, indent=2)
        case "yaml":
            return FlextUtilities.safe_yaml_stringify(data)
        case "table" | "plain":
            return FlextResult[str].ok(str(data))
        case _:
            return FlextResult[str].ok(str(data))
```

**FlextPipeline Pattern**: Sequential operation execution

```python
from flext_core import FlextPipeline

pipeline = FlextPipeline[None]()
return pipeline.execute([
    lambda: step_one(),
    lambda: step_two(),
    lambda: step_three()
])
```

**Clean Architecture**: Domain-driven design with flext-core integration

- Configuration inherits from `FlextCliConfig`
- Models use Pydantic v2 with comprehensive validation
- Services implement functional patterns with reduce/filter operations
- Commands integrate with Click framework for CLI interfaces

**Rich UI**: Consistent terminal output using Rich library

- Tables, progress bars, panels for output
- Multiple output formats: table, JSON, YAML, CSV

## Dependencies

### Core Dependencies

- **flext-core**: Foundation library (FlextResult, FlextEntity, etc.)
- **Click 8.2+**: CLI framework
- **Rich 14.0+**: Terminal UI components
- **Pydantic 2.11+**: Data validation
- **httpx**: HTTP client

### Local Workspace Dependencies

- **flext-api**: REST API services integration
- **flext-observability**: Monitoring integration
- **flext-meltano**: Meltano orchestration
- **algar-oud-mig**: ALGAR project CLI
- **gruponos-meltano-native**: GrupoNos project CLI

## Quality Standards

### Requirements

- **Test Coverage**: Minimum 90% for core modules
- **Type Safety**: MyPy strict mode enabled
- **Linting**: Ruff with comprehensive rules
- **Security**: Bandit scanning in CI
- **Documentation**: All public APIs documented

### Pre-commit Workflow

1. Run `make validate` before any commit
2. All quality gates must pass
3. Tests must have real functionality, not excessive mocking
4. Follow flext-core patterns for new code

## Testing Strategy

**Real Functionality Tests**: Tests should execute actual code paths, not just mock everything.

Key test files:

- `tests/test_core.py` - Core service functionality
- `tests/test_commands_auth.py` - Authentication commands
- `tests/test_api.py` - API functionality
- `tests/conftest.py` - Test fixtures with minimal mocking

## Adding New Commands

1. Create command module (e.g., `pipeline.py`) in `src/flext_cli/`
2. Use Click decorators with Rich output following existing patterns
3. Follow auth/config/debug patterns for consistency
4. Register command in `cli.py` via `FlextCliMain.register_commands()`
5. Add comprehensive tests with 90%+ coverage
6. Run `make validate` to ensure quality gates pass

Example structure:

```python
# pipeline.py
import click
from rich.console import Console
from flext_core import FlextResult
from flext_cli.constants import FlextCliConstants

@click.group()
def pipeline():
    """Pipeline management commands."""
    pass

@pipeline.command()
@click.pass_context
def list_pipelines(ctx: click.Context):
    """List all data pipelines."""
    console: Console = ctx.obj["console"]
    # Use FlextResult pattern for error handling
    result = _get_pipelines()
    if result.is_success:
        console.print_json(result.value)
    else:
        console.print(f"[red]Error: {result.error}[/red]")

def _get_pipelines() -> FlextResult[dict]:
    # Implementation here
    return FlextResult[dict].ok({"pipelines": []})
```

**Registration in cli.py**:
```python
# Add to FlextCliMain.register_commands()
from flext_cli.pipeline import pipeline
cli.add_command(pipeline)
```

## Known Issues & Current State

### Working (✅)

- Authentication commands (`flext auth`)
- Configuration management (`flext config`)
- Debug/diagnostic tools (`flext debug`)
- Core library functionality
- Rich terminal output

### Partially Working (⚠️)

- flext-core integration (60% complete)
- Test coverage (~45% actual)
- Type safety (some MyPy errors remain)

### Missing/Planned (❌)

- Pipeline management commands
- Service orchestration
- Interactive mode (placeholder only)
- Plugin management
- Project-specific commands (ALGAR, GrupoNos)
- Monitoring/observability features

## Configuration

### Environment Variables

```bash
export FLX_PROFILE=development    # Configuration profile
export FLX_DEBUG=true            # Enable debug mode
export FLEXT_CLI_LOG_LEVEL=debug # Logging level
```

### CLI Options

```bash
flext --profile production --output json --debug command
```

## Troubleshooting

### Common Issues

1. **Import Errors**

   ```bash
   rm -rf .venv && poetry install --all-extras
   ```

2. **Type Check Failures**

   ```bash
   poetry run mypy src/flext_cli --show-error-codes
   ```

3. **Test Failures**

   ```bash
   poetry run pytest tests/ -v --tb=short
   ```

### Entry Points

- Main CLI: `src/flext_cli/cli.py` - Main CLI group definition with FlextCliMain
- Commands: `src/flext_cli/{auth,cmd,debug}.py` - Individual command implementations
- API: `src/flext_cli/api.py` - Programmatic access with FlextCliApi class
- Configuration: `src/flext_cli/config.py` - FlextCliConfig settings management
- Client: `src/flext_cli/client.py` - FlextApiClient for HTTP operations
- Entry script: Configured in `pyproject.toml:101` as `flext = "flext_cli.cli:main"`

### Important Implementation Details

**Code Quality Tools Integration**:
- Use `qlty smells --all` for code smell detection and advanced refactoring guidance
- Apply functional programming patterns (reduce, filter, map) for complex operations
- Prefer flext-core utilities over custom implementations

**Error Handling Strategy**:
- All functions should return `FlextResult[T]` for consistent error handling
- Use pattern matching for cleaner conditional logic
- Implement FlextPipeline for sequential operations that may fail

## Development Workflow

1. **Setup**: `make setup` - Install dependencies and pre-commit hooks
2. **Development**: Use `make check` frequently for quick validation
3. **Testing**: Add real functionality tests, not just mocks
4. **Quality**: Run `make validate` before commits
5. **Integration**: Follow flext-core patterns and Clean Architecture principles

The codebase follows Clean Architecture with Domain-Driven Design patterns, integrates deeply with flext-core foundation library, and serves both as a standalone CLI and library for other FLEXT ecosystem projects.
