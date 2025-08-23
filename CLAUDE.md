# CLAUDE.md - FLEXT CLI PROJECT

**References**: See [../CLAUDE.md](../CLAUDE.md) for FLEXT workspace-wide standards and quality gates.

## Project Status: HONEST ASSESSMENT

**⚠️ CRITICAL: Foundation library with significant coverage and quality gaps**

This is a CLI foundation library for FLEXT ecosystem projects. **Current state based on real analysis:**

- **Test Coverage**: ~45% actual coverage (not the inflated numbers previously reported)
- **Working Commands**: Only 3 command groups (`auth`, `config`, `debug`) actually function
- **Critical Files**: Multiple files with 0% coverage (`utilities.py`, `foundation.py`, `ecosystem_integration.py`)
- **Quality Issues**: Several PyRight/MyPy errors still unresolved

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

## CRITICAL LESSONS LEARNED FROM DEVELOPMENT

### ❌ Previous Mistakes in This Project

1. **Coverage Inflation**: Reported inflated coverage numbers without proper verification
2. **Mock Overuse**: Tests were heavily mocked, hiding real functionality gaps
3. **Quantity Over Quality**: Focused on number of test files rather than actual coverage
4. **Premature Celebration**: Celebrated progress without validating real functionality

### ✅ What Actually Works

- **Core Service**: `src/flext_cli/core.py` with 89% coverage
- **CLI Types**: `src/flext_cli/cli_types.py` with 89% coverage
- **Exception Handling**: `src/flext_cli/exceptions.py` with 100% coverage
- **Working Test Files**: ~20 test files with real functionality (out of 87 total)

## Library Architecture

**⚠️ Reality Check:** Architecture is designed correctly but implementation has significant gaps.

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

## Development Commands & Reality Check

**⚠️ IMPORTANT**: Follow [../CLAUDE.md](../CLAUDE.md) quality gates. These are project-specific additions.

### Current Quality Status (HONEST)

```bash
# What actually works:
make lint           # ✅ Passes - Ruff linting clean
make type-check     # ❌ Has errors - PyRight/MyPy issues remain
make test           # ⚠️  Partial - Only ~45% real coverage

# Critical gaps:
# - utilities.py: 0% coverage (227 lines uncovered)
# - cli_utils.py: 15% coverage (407 lines uncovered)
# - decorators.py: 13% coverage (263 lines uncovered)
```

### Mandatory Pre-Development Steps

```bash
# FIRST: Verify current state honestly
pytest tests/ --cov=src --cov-report=term-missing --tb=no -q | grep TOTAL
# SECOND: Check quality gate compliance
make lint && echo "✅ Lint clean" || echo "❌ Lint issues"
# THIRD: Verify imports work
python -c "from flext_cli import FlextCliConfig; print('✅ Imports work')"
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

## PRIORITY FIXES NEEDED (Based on Real Analysis)

### 🔥 URGENT: Critical Coverage Gaps

**Files requiring immediate functional tests:**

1. **cli_utils.py** (477 lines, 15% coverage)
   - Functions: `cli_quick_setup`, `cli_batch_process_files`, `cli_load_data_file`
   - Status: Core functionality completely untested

2. **decorators.py** (302 lines, 13% coverage)
   - Functions: Authentication decorators, service result handlers
   - Status: Critical decorator functionality not validated

3. **utilities.py** (227 lines, 0% coverage)
   - Classes: `FlextCliValidationUtilities`, `FlextCliFileUtilities`
   - Status: Utility functions never executed in tests

### 🔧 MEDIUM: Quality Issues

- **PyRight/MyPy Errors**: Multiple type annotation issues
- **FlextResult Migration**: Still using `.data` instead of `.value` in some places
- **Mock Removal**: Several test files still over-mocked

### ✅ VERIFIED WORKING (Don't Break These)

- `core.py` (89% coverage) - Core service functionality
- `exceptions.py` (100% coverage) - Error handling
- `cli_types.py` (89% coverage) - Type definitions
- Working test files: `test_core_real.py`, `test_api_comprehensive.py`, etc.

## Key File Locations

### Core Entry Points

- `src/flext_cli/cli.py:70` - Main CLI group definition with global options
- `src/flext_cli/commands/` - Only auth.py, config.py, debug.py implemented
- `pyproject.toml:103` - Entry point: `flext = "flext_cli.cli:main"`

### Domain Layer (CLI Architecture)

- `src/flext_cli/domain/entities.py` - CLICommand, CLISession, CLIPlugin entities
- `src/flext_cli/core/base.py:93` - handle_service_result decorator for FlextResult
- `src/flext_cli/client.py` - HTTP client for FLEXT services (currently unused)

## Development Workflow: ANTI-MISTAKE PROTOCOL

**⚠️ CRITICAL**: This project has a history of inflated progress claims. Follow this protocol strictly.

### MANDATORY Validation Before Any Claims

```bash
# 1. VERIFY coverage honestly (no inflation)
pytest tests/ --cov=src --cov-report=term | grep "TOTAL.*[0-9]\+%"

# 2. VERIFY tests actually run code (no mock-only tests)
grep -r "@patch\|mock\|Mock" tests/ | wc -l  # Should be minimal

# 3. VERIFY imports work
python -c "
from flext_cli.utilities import FlextCliValidationUtilities
from flext_cli.cli_utils import cli_quick_setup
print('✅ Critical imports work')
"

# 4. VERIFY quality gates
make lint && make type-check && echo "✅ Quality gates pass"
```

### BEFORE Making Changes - REALITY CHECK

1. **READ coverage report completely** - don't assume
2. **VERIFY test files actually test functionality** - check for mocks
3. **CONFIRM impact** - changes affect ecosystem projects
4. **VALIDATE claims** - never report success without proof

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

## LESSONS LEARNED: DEVELOPMENT ANTI-PATTERNS

### ❌ NEVER DO THESE AGAIN

1. **Inflated Progress Reporting**
   - WRONG: "PROGRESSO FANTÁSTICO: 850+ tests!"
   - RIGHT: "Fixed 11 test files, actual coverage: 45%"

2. **Mock Overuse**
   - WRONG: `@patch("flext_cli.module.function")` everywhere
   - RIGHT: Test real function calls with actual implementations

3. **Coverage Celebration Without Validation**
   - WRONG: Assume coverage tools work correctly
   - RIGHT: Verify coverage by checking if code actually executes

4. **Quality Over Quantity Confusion**
   - WRONG: "32+ files working" without verification
   - RIGHT: "20 files confirmed working with real functionality"

### ✅ PROVEN WORKING APPROACHES

1. **Systematic File-by-File Validation**
   - Read each test file completely
   - Verify imports work in isolation
   - Check if tests exercise real code paths

2. **Honest Coverage Measurement**
   - Run coverage on individual files
   - Verify high-coverage files actually work
   - Focus on critical functionality first

3. **Conservative Progress Claims**
   - Report actual working state
   - Admit limitations and gaps
   - Focus on fixing one file completely before moving to next

---

## WORKSPACE REFERENCE

**See [../CLAUDE.md](../CLAUDE.md)** for:
- FLEXT ecosystem-wide standards
- Quality gates and validation requirements
- Anti-duplication enforcement
- Universal command patterns

This project-specific CLAUDE.md focuses on **flext-cli** specific issues and lessons learned from its development process.

---

**PROJECT AUTHORITY**: Foundation library requiring 90%+ coverage with functional tests
**ECOSYSTEM DEPENDENCY**: Changes affect flext-meltano, client-a-oud-mig, client-b-meltano-native
**QUALITY GATE**: Must pass workspace-level validation before any integration
