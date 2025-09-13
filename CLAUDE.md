# FLEXT-CLI CLAUDE.MD

**The CLI Foundation Library for FLEXT Ecosystem**
**Version**: 2.1.0 | **Authority**: CLI FOUNDATION | **Updated**: 2025-01-08
**Status**: 30% functional, targeting 75%+ with ZERO TOLERANCE quality standards

**References**: See [../CLAUDE.md](../CLAUDE.md) for FLEXT ecosystem standards and [README.md](README.md) for project overview.

---

## 🎯 FLEXT-CLI MISSION (CLI ECOSYSTEM AUTHORITY)

**CRITICAL ROLE**: flext-cli is the CLI FOUNDATION for the entire FLEXT ecosystem. ALL CLI functionality across 32+ projects MUST flow through this library. ZERO TOLERANCE for direct Click/Rich imports in CLI projects.

**CLI AUTHORITY RESPONSIBILITIES**:

- ✅ **Universal CLI Interface**: ALL CLI projects use flext-cli exclusively
- ✅ **Output Standardization**: ALL data output, tables, progress bars through flext-cli
- ✅ **Click/Rich Abstraction**: Provide comprehensive wrapper layer over Click/Rich
- ✅ **CLI Configuration**: Unified configuration management for all CLI tools
- ✅ **Zero Direct Imports**: NO direct Click/Rich imports allowed in ecosystem
- ✅ **Foundation Quality**: Set CLI quality standards for entire ecosystem

**ECOSYSTEM CLI IMPACT** (ALL CLI Projects Depend on This):

- **Core CLI Projects**: flext-cli (self), client-a-oud-mig CLI, client-b-meltano-native CLI
- **Infrastructure CLIs**: Database management tools, deployment CLIs
- **Data Integration CLIs**: ETL command interfaces, pipeline management
- **Development Tools**: Build scripts, testing utilities, deployment automation

**CLI QUALITY IMPERATIVES** (ZERO TOLERANCE ENFORCEMENT):

- 🔴 **ZERO direct Click imports** in ANY ecosystem CLI project
- 🔴 **ZERO direct Rich imports** for output/formatting in ANY CLI project
- 🟢 **75%+ test coverage** with REAL CLI functionality tests
- 🟢 **Complete Click/Rich wrapper** coverage for all common CLI needs
- 🟢 **Zero errors** in MyPy strict mode, PyRight, and Ruff
- 🟢 **Comprehensive CLI API** documentation with examples

## CLI ARCHITECTURE INSIGHTS (ECOSYSTEM CLI FOUNDATION)

**CLI Abstraction Layer**: Complete wrapper over Click and Rich, providing unified CLI experience across entire FLEXT ecosystem with ZERO direct Click/Rich imports required.

**flext-core Integration**: Deep integration with foundation library using FlextResult railway patterns, FlextContainer dependency injection, and FlextDomainService architecture.

**Zero Tolerance CLI Policy**: ABSOLUTE prohibition of direct Click/Rich imports anywhere in ecosystem - ALL CLI functionality flows through flext-cli wrappers only.

**Modern Python 3.13+ CLI Patterns**: Advanced pattern matching, functional programming, comprehensive type annotations specifically for CLI development contexts.

**Quality Leadership**: Sets CLI quality standards for entire ecosystem with zero-compromise approach to CLI infrastructure.

## FLEXT-CLI DEVELOPMENT WORKFLOW (CLI FOUNDATION QUALITY)

### Essential CLI Development Workflow (MANDATORY FOR CLI FOUNDATION)

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

### CLI Foundation Testing (ECOSYSTEM CRITICAL)

```bash
# CRITICAL: CLI foundation testing - affects entire ecosystem
make cli-test                # Basic CLI import test
poetry run flext --help     # Test main CLI
poetry run flext auth --help # Test auth commands
poetry run flext config --help # Test config commands
poetry run flext debug --help  # Test debug commands

# CLI FOUNDATION VALIDATION (ZERO TOLERANCE)
echo "=== CLI FOUNDATION VALIDATION ==="

# 1. Verify NO direct Click imports in codebase
echo "Checking for forbidden Click imports..."
grep -r "import click" src/ && echo "❌ CRITICAL: Direct Click imports found" && exit 1
grep -r "from click" src/ && echo "❌ CRITICAL: Click component imports found" && exit 1

# 2. Verify NO direct Rich imports for output
echo "Checking for forbidden Rich imports..."
grep -r "import rich" src/ && echo "❌ CRITICAL: Direct Rich imports found" && exit 1
grep -r "from rich" src/ && echo "❌ CRITICAL: Rich component imports found" && exit 1

# 3. Verify flext-cli wrapper APIs are available
python -c "
from flext_cli import FlextCliApi, FlextCliMain, FlextCliConfig
api = FlextCliApi()
main = FlextCliMain()
config = FlextCliConfig()
print('✅ CLI Foundation APIs available')
"

echo "✅ CLI Foundation validation completed"
```

## CLI FOUNDATION ARCHITECTURE (ECOSYSTEM CLI LAYER)

### CLI Foundation Structure (ABSTRACTION AUTHORITY)

```
src/flext_cli/
├── cli.py                   # Main CLI entry point (Click abstraction layer)
├── api.py                   # HIGH-LEVEL CLI API (ecosystem interface)
├── main.py                  # FlextCliMain (command registration system)
├── config.py                # FlextCliConfig (unified CLI configuration)
├── constants.py             # FlextCliConstants (CLI system constants)
├── formatters.py            # OUTPUT ABSTRACTION (Rich wrapper layer)
├── context.py               # CLI execution context management
├── exceptions.py            # CLI-specific exception hierarchy
├── models.py                # CLI domain models (Pydantic-based)
├── services.py              # CLI business logic services
├── client.py                # HTTP client integration
├── core.py                  # Core CLI service implementation
├── auth.py                  # Authentication command group
├── cmd.py                   # Configuration commands
├── debug.py                 # Debug/diagnostic commands
└── data_processing.py       # Data processing for CLI operations
```

### CLI Abstraction Layers (ZERO TOLERANCE ENFORCEMENT)

**Layer 1: Click Abstraction** (INTERNAL ONLY)

- `cli.py` - Contains ALL Click imports (ONLY file allowed to import Click)
- `main.py` - FlextCliMain wrapper around Click commands
- NO other file in ecosystem allowed to import Click directly

**Layer 2: Rich Abstraction** (INTERNAL ONLY)

- `formatters.py` - Contains ALL Rich imports (ONLY file allowed to import Rich)
- Provides complete wrapper API for tables, progress bars, styling
- NO other file in ecosystem allowed to import Rich directly

**Layer 3: Ecosystem API** (PUBLIC INTERFACE)

- `api.py` - FlextCliApi for programmatic CLI access
- `config.py` - FlextCliConfig for configuration management
- `constants.py` - FlextCliConstants for CLI constants
- ALL ecosystem CLI projects use ONLY these public APIs

## CLI FOUNDATION DEVELOPMENT PATTERNS (ZERO TOLERANCE ENFORCEMENT)

### CLI Foundation Patterns (ECOSYSTEM AUTHORITY)

**CRITICAL**: These patterns demonstrate how flext-cli provides CLI foundation for entire ecosystem while maintaining ZERO TOLERANCE for direct Click/Rich imports.

### FlextResult CLI Pattern (CLI-SPECIFIC ERROR HANDLING)

```python
# ✅ CORRECT - CLI operations with FlextResult from flext-core
from flext_core import FlextResult, FlextLogger
from flext_cli import FlextCliApi, FlextCliConfig

def cli_save_config(config_data: dict) -> FlextResult[None]:
    """CLI operation with proper error handling - NO try/except fallbacks."""
    # Input validation with early return
    if not config_data:
        return FlextResult[None].fail("Configuration data cannot be empty")

    # Use flext-cli API exclusively - NO direct Click usage
    cli_api = FlextCliApi()

    # Configuration validation through flext-cli
    config_result = cli_api.validate_config(config_data)
    if config_result.is_failure:
        return FlextResult[None].fail(f"Config validation failed: {config_result.error}")

    # Save through flext-cli API
    save_result = cli_api.save_config(config_result.unwrap())
    if save_result.is_failure:
        return FlextResult[None].fail(f"Config save failed: {save_result.error}")

    return FlextResult[None].ok(None)

# ❌ ABSOLUTELY FORBIDDEN - Direct Click usage in CLI projects
# import click  # ZERO TOLERANCE VIOLATION
# @click.command()  # FORBIDDEN - use flext-cli wrappers
```

### CLI Output Abstraction Pattern (ZERO TOLERANCE FOR DIRECT RICH)

```python
# ✅ CORRECT - ALL output through flext-cli wrappers
from flext_core import FlextResult
from flext_cli import FlextCliApi

def display_cli_data(data: dict, output_format: str = "table") -> FlextResult[None]:
    """Display data using flext-cli output wrappers - NO direct Rich usage."""
    cli_api = FlextCliApi()

    # Format data through flext-cli (abstracts Rich internally)
    format_result = cli_api.format_output(
        data=data,
        format_type=output_format,
        headers=list(data.keys()) if isinstance(data, dict) else None,
        title="CLI Data Display"
    )

    if format_result.is_failure:
        return FlextResult[None].fail(f"Data formatting failed: {format_result.error}")

    # Display through flext-cli (abstracts Rich internally)
    display_result = cli_api.display_output(format_result.unwrap())
    if display_result.is_failure:
        return FlextResult[None].fail(f"Data display failed: {display_result.error}")

    return FlextResult[None].ok(None)

def show_cli_progress(task_name: str, total: int) -> FlextResult[None]:
    """Show progress using flext-cli progress wrappers - NO direct Rich."""
    cli_api = FlextCliApi()

    # Create progress bar through flext-cli abstraction
    progress_result = cli_api.create_progress_bar(
        task_name=task_name,
        total=total,
        show_percentage=True,
        show_eta=True
    )

    if progress_result.is_failure:
        return FlextResult[None].fail(f"Progress bar creation failed: {progress_result.error}")

    return FlextResult[None].ok(None)

# ❌ ABSOLUTELY FORBIDDEN - Direct Rich usage in CLI projects
# from rich.console import Console  # ZERO TOLERANCE VIOLATION
# from rich.table import Table      # FORBIDDEN - use flext-cli wrappers
# from rich.progress import Progress # FORBIDDEN - use flext-cli wrappers
```

### CLI Command Registration Pattern (FLEXT-CLI FOUNDATION)

```python
# ✅ CORRECT - Command registration through flext-cli system
from flext_core import FlextResult
from flext_cli import FlextCliMain, FlextCliApi

class ProjectCliService:
    """Project CLI service using flext-cli foundation exclusively."""

    def __init__(self) -> None:
        self._cli_api = FlextCliApi()

    def create_project_cli(self) -> FlextResult[FlextCliMain]:
        """Create project CLI using flext-cli foundation - NO Click imports."""
        # Initialize CLI through flext-cli (abstracts Click internally)
        cli_main = FlextCliMain(
            name="project-cli",
            description="Project CLI using flext-cli foundation"
        )

        # Register command groups through flext-cli abstraction
        data_commands_result = cli_main.register_command_group(
            name="data",
            commands=self._create_data_commands(),
            description="Data management commands"
        )

        if data_commands_result.is_failure:
            return FlextResult[FlextCliMain].fail(f"Data commands registration failed: {data_commands_result.error}")

        return FlextResult[FlextCliMain].ok(cli_main)

    def _create_data_commands(self) -> dict:
        """Create data commands using flext-cli command builders."""
        return {
            "list": self._cli_api.create_command(
                name="list",
                description="List data entries",
                handler=self._handle_data_list,
                output_format="table"  # flext-cli handles formatting
            ),
            "export": self._cli_api.create_command(
                name="export",
                description="Export data",
                handler=self._handle_data_export,
                output_format="json"   # flext-cli handles formatting
            )
        }

# ❌ ABSOLUTELY FORBIDDEN - Direct Click command creation
# @click.group()      # ZERO TOLERANCE VIOLATION
# @click.command()    # FORBIDDEN - use flext-cli command builders
```

### CLI Configuration Pattern (UNIFIED ECOSYSTEM CONFIG)

```python
# ✅ CORRECT - Configuration through flext-cli system
from flext_core import FlextResult
from flext_cli import FlextCliConfig, FlextCliConstants

class ProjectCliConfig:
    """Project CLI configuration using flext-cli foundation."""

    def __init__(self) -> None:
        # Use flext-cli configuration system
        self._cli_config = FlextCliConfig(
            profile="project",
            debug_mode=False,
            output_format="table",
            no_color=False
        )

    def load_project_config(self) -> FlextResult[FlextCliConfig]:
        """Load configuration using flext-cli config management."""
        # Configuration validation through flext-cli
        validation_result = self._cli_config.validate_business_rules()
        if validation_result.is_failure:
            return FlextResult[FlextCliConfig].fail(f"Config validation failed: {validation_result.error}")

        return FlextResult[FlextCliConfig].ok(self._cli_config)

    def get_output_format(self) -> str:
        """Get output format from CLI configuration."""
        return self._cli_config.output_format

    def is_debug_mode(self) -> bool:
        """Check if debug mode is enabled."""
        return bool(self._cli_config.debug_mode)
```

## CLI FOUNDATION DEPENDENCIES (ABSTRACTION MANAGEMENT)

### Foundation Dependencies (CLI ABSTRACTION LAYER)

**CRITICAL**: flext-cli manages ALL CLI dependencies for the ecosystem. Other projects should NOT import these directly.

- **flext-core**: Foundation library (FlextResult, FlextContainer, FlextDomainService)
- **Click 8.2+**: CLI framework (INTERNAL ABSTRACTION - not exposed to ecosystem)
- **Rich 14.0+**: Terminal UI (INTERNAL ABSTRACTION - not exposed to ecosystem)
- **Pydantic 2.11+**: Data validation and configuration management
- **httpx**: HTTP client for API integrations

### Ecosystem CLI Integration

**ZERO TOLERANCE POLICY**: These projects MUST use flext-cli exclusively for CLI functionality:

- **client-a-oud-mig**: client-a project CLI (MUST use flext-cli, NO direct Click/Rich)
- **client-b-meltano-native**: client-b CLI (MUST use flext-cli, NO direct Click/Rich)
- **flext-api**: API CLI tools (MUST use flext-cli wrappers)
- **flext-observability**: Monitoring CLI (MUST use flext-cli for all output)
- **flext-meltano**: Meltano CLI integration (MUST use flext-cli abstraction)

## CLI FOUNDATION QUALITY STANDARDS (ECOSYSTEM CLI AUTHORITY)

### CLI Foundation Requirements (ZERO TOLERANCE ENFORCEMENT)

**CRITICAL**: As the CLI foundation, flext-cli must achieve the highest standards while enforcing ecosystem-wide CLI compliance.

- **Zero Direct Imports**: ZERO tolerance for direct Click/Rich imports anywhere in ecosystem
- **Test Coverage**: 75%+ real CLI functionality tests (current target from 30% functional)
- **CLI API Coverage**: Complete wrapper coverage for ALL common CLI/output operations
- **Type Safety**: MyPy strict mode enabled with ZERO errors in src/
- **CLI Documentation**: ALL public CLI APIs documented with complete examples
- **Abstraction Completeness**: NO gaps in Click/Rich abstraction layer

### CLI Foundation Quality Gates (MANDATORY FOR ALL COMMITS)

```bash
# PHASE 1: CLI Foundation Quality (ZERO TOLERANCE)
make lint                    # Ruff: ZERO violations in src/
make type-check              # MyPy strict: ZERO errors in src/
make security                # Bandit: ZERO critical vulnerabilities

# PHASE 2: CLI Abstraction Validation (ECOSYSTEM PROTECTION)
echo "=== CLI ABSTRACTION VALIDATION ==="

# Verify Click imports are contained
click_imports=$(find src/ -name "*.py" -exec grep -l "import click\|from click" {} \;)
if [ $(echo "$click_imports" | grep -v "src/flext_cli/cli.py" | wc -l) -gt 0 ]; then
    echo "❌ CRITICAL: Click imports outside cli.py found"
    echo "$click_imports" | grep -v "src/flext_cli/cli.py"
    exit 1
fi

# Verify Rich imports are contained
rich_imports=$(find src/ -name "*.py" -exec grep -l "import rich\|from rich" {} \;)
if [ $(echo "$rich_imports" | grep -v "src/flext_cli/formatters.py" | wc -l) -gt 0 ]; then
    echo "❌ CRITICAL: Rich imports outside formatters.py found"
    echo "$rich_imports" | grep -v "src/flext_cli/formatters.py"
    exit 1
fi

echo "✅ CLI abstraction boundaries maintained"

# PHASE 3: CLI Foundation Test Coverage
make test                    # 75%+ coverage with REAL CLI tests
pytest tests/ --cov=src/flext_cli --cov-fail-under=75

# PHASE 4: CLI API Completeness Validation
python -c "
from flext_cli import FlextCliApi, FlextCliMain, FlextCliConfig, FlextCliConstants
api = FlextCliApi()
main = FlextCliMain()
config = FlextCliConfig()
print('✅ CLI Foundation APIs complete and importable')
"
```

### CLI Foundation Development Standards (ECOSYSTEM LEADERSHIP)

**ABSOLUTELY FORBIDDEN IN FLEXT-CLI**:

- ❌ **Exposing Click/Rich directly** - all abstractions must be complete
- ❌ **Incomplete abstraction layers** - every CLI/output need must have wrapper
- ❌ **Try/except fallbacks** - CLI operations must use explicit FlextResult patterns
- ❌ **Multiple classes per module** - single responsibility with unified classes
- ❌ **Breaking ecosystem CLI contracts** - maintain API compatibility

**MANDATORY IN FLEXT-CLI**:

- ✅ **Complete Click abstraction** - no CLI operation should require direct Click import
- ✅ **Complete Rich abstraction** - no output operation should require direct Rich import
- ✅ **Comprehensive CLI API** - FlextCliApi covers all common CLI development needs
- ✅ **Zero tolerance enforcement** - detect and prevent direct Click/Rich imports in ecosystem
- ✅ **Professional CLI documentation** - every wrapper API fully documented with examples

## CLI FOUNDATION TESTING STRATEGY (REAL CLI FUNCTIONALITY)

### CLI Foundation Testing Requirements

**CRITICAL**: CLI foundation tests must validate REAL CLI functionality and abstraction layer completeness.

**CLI-Specific Test Requirements**:

- ✅ **Real CLI execution tests** - test actual command registration and execution
- ✅ **Abstraction layer tests** - validate Click/Rich wrappers work correctly
- ✅ **API completeness tests** - verify all common CLI needs are covered
- ✅ **Output formatting tests** - test all supported output formats (table, JSON, YAML)
- ✅ **Configuration tests** - validate CLI config management
- ✅ **Error handling tests** - test CLI error scenarios with FlextResult patterns

### CLI Foundation Test Files

- `tests/test_api.py` - FlextCliApi functionality (ecosystem interface)
- `tests/test_main.py` - FlextCliMain command registration system
- `tests/test_config.py` - FlextCliConfig management
- `tests/test_formatters.py` - Rich abstraction layer functionality
- `tests/test_commands_auth.py` - Authentication commands
- `tests/test_commands_config.py` - Configuration commands
- `tests/test_commands_debug.py` - Debug commands
- `tests/conftest.py` - CLI test fixtures and utilities

## ADDING NEW CLI FUNCTIONALITY (ECOSYSTEM FOUNDATION)

### Extending CLI Foundation (ZERO TOLERANCE COMPLIANCE)

**CRITICAL**: When adding CLI functionality, maintain ZERO TOLERANCE for direct Click/Rich exposure to ecosystem.

### 1. Adding New Command Groups

```python
# ✅ CORRECT - New command module following CLI foundation patterns
# File: src/flext_cli/data.py

from flext_core import FlextResult, FlextLogger
from flext_cli import FlextCliApi, FlextCliConfig

class DataCommands:
    """Data management commands using CLI foundation - NO Click imports."""

    def __init__(self) -> None:
        self._logger = FlextLogger(__name__)
        self._cli_api = FlextCliApi()

    def create_data_command_group(self) -> FlextResult[dict]:
        \"\"\"Create data command group using flext-cli builders.\"\"\"
        commands = {
            "list": self._cli_api.create_command(
                name="list",
                description="List data entries",
                handler=self._handle_data_list,
                arguments=["--format", "--filter"],
                output_format="table"
            ),
            "import": self._cli_api.create_command(
                name="import",
                description="Import data from file",
                handler=self._handle_data_import,
                arguments=["--file", "--format"],
                output_format="json"
            )
        }
        return FlextResult[dict].ok(commands)

    def _handle_data_list(self, **kwargs: object) -> FlextResult[None]:
        \"\"\"Handle data list command using CLI foundation.\"\"\"
        # Get data (business logic)
        data = {"entries": [{"id": 1, "name": "example"}]}

        # Display using flext-cli abstraction - NO direct Rich
        display_result = self._cli_api.display_output(
            data=data,
            format_type=str(kwargs.get("format", "table")),
            title="Data Entries"
        )

        if display_result.is_failure:
            return FlextResult[None].fail(f"Display failed: {display_result.error}")

        return FlextResult[None].ok(None)

# ❌ ABSOLUTELY FORBIDDEN - Direct Click usage
# import click  # ZERO TOLERANCE VIOLATION
# @click.group()  # FORBIDDEN - use flext-cli command builders
```

### 2. Registration in CLI Foundation

```python
# File: src/flext_cli/cli.py (ONLY file allowed to import Click)
import click  # ONLY THIS FILE can import Click
from flext_cli.data import DataCommands

class FlextCliMain:
    \"\"\"Main CLI class - abstracts Click for ecosystem.\"\"\"

    def register_data_commands(self) -> FlextResult[None]:
        \"\"\"Register data commands through CLI foundation.\"\"\"
        data_commands = DataCommands()
        commands_result = data_commands.create_data_command_group()

        if commands_result.is_failure:
            return FlextResult[None].fail(f"Data commands creation failed: {commands_result.error}")

        # Register with internal Click system (abstracted from ecosystem)
        for name, command in commands_result.unwrap().items():
            self._register_click_command(name, command)  # Internal abstraction

        return FlextResult[None].ok(None)
```

### 3. Adding New Output Formats

```python
# File: src/flext_cli/formatters.py (ONLY file allowed to import Rich)
from rich.console import Console  # ONLY THIS FILE can import Rich
from rich.table import Table
from flext_core import FlextResult

class FlextCliFormatters:
    \"\"\"Output formatters - abstracts Rich for ecosystem.\"\"\"

    def __init__(self) -> None:
        self._console = Console()  # Internal Rich usage

    def format_as_custom_table(self, data: dict, **options: object) -> FlextResult[str]:
        \"\"\"Add new table format while maintaining Rich abstraction.\"\"\"
        try:
            # Internal Rich usage - NOT exposed to ecosystem
            table = Table(title=str(options.get("title", "")))

            # Add table formatting logic
            for key in data.keys():
                table.add_column(str(key))

            # Return formatted result WITHOUT exposing Rich objects
            return FlextResult[str].ok("formatted_output")

        except Exception as e:
            return FlextResult[str].fail(f"Custom table formatting failed: {e}")
```

### CLI Foundation Extension Requirements

**MANDATORY STEPS** for extending CLI foundation:

1. **Abstraction Completeness**: New functionality MUST be fully abstracted - no Click/Rich exposure
2. **API Coverage**: Add to FlextCliApi if needed for ecosystem consumption
3. **Documentation**: Complete API documentation with ecosystem usage examples
4. **Testing**: Real functionality tests with 75%+ coverage
5. **Zero Tolerance Validation**: Ensure no direct Click/Rich imports in new code

## CLI FOUNDATION STATUS & ECOSYSTEM IMPACT

### Current CLI Foundation Status (30% → 75% TARGET)

**WORKING CLI INFRASTRUCTURE** (✅):

- CLI abstraction layer architecture (Click/Rich containment)
- Authentication commands (`flext auth`) - ecosystem ready
- Configuration management (`flext config`) - ecosystem ready
- Debug/diagnostic tools (`flext debug`) - ecosystem ready
- FlextResult CLI error handling patterns
- Basic CLI API structure (FlextCliApi, FlextCliMain, FlextCliConfig)

**IN PROGRESS CLI FOUNDATION** (🚧):

- Complete Click abstraction coverage (75% complete)
- Complete Rich abstraction coverage (60% complete)
- Comprehensive CLI test suite (targeting 75% coverage)
- CLI API documentation (ecosystem usage examples)
- FlextCliApi completeness (covering all common CLI needs)

**CRITICAL CLI FOUNDATION GAPS** (❌):

- **Output format coverage**: Missing YAML, CSV formatters in Rich abstraction
- **Progress bar abstraction**: Incomplete Rich progress wrapper
- **Interactive CLI features**: No abstraction for prompts, selections
- **CLI plugin system**: No extensibility framework for ecosystem projects
- **Command validation**: Missing input validation patterns
- **CLI error display**: Inconsistent error formatting across commands

### Ecosystem CLI Enforcement Status

**ZERO TOLERANCE ENFORCEMENT** (🔴 CRITICAL):

- client-a-oud-mig: NOT COMPLIANT - has direct Click imports (VIOLATION)
- client-b-meltano-native: NOT COMPLIANT - has direct Rich imports (VIOLATION)
- flext-api CLI tools: PARTIALLY COMPLIANT - mixed usage patterns
- flext-observability: NOT VALIDATED - unknown CLI compliance status

**IMMEDIATE ACTION REQUIRED**: All ecosystem CLI violations must be corrected.

## CLI FOUNDATION TROUBLESHOOTING (ECOSYSTEM CRITICAL)

### CLI Abstraction Validation

```bash
# CRITICAL: Validate CLI abstraction boundaries
echo "=== CLI FOUNDATION BOUNDARY VALIDATION ==="

# 1. Verify Click imports are properly contained
echo "Checking Click import containment..."
click_violations=$(find ../flext-* -name "*.py" -exec grep -l "import click\|from click" {} \; 2>/dev/null | grep -v "flext-cli")
if [ -n "$click_violations" ]; then
    echo "❌ ECOSYSTEM VIOLATION: Direct Click imports found:"
    echo "$click_violations"
    echo "RESOLUTION: Refactor to use flext-cli CLI foundation"
fi

# 2. Verify Rich imports are properly contained
rich_violations=$(find ../flext-* -name "*.py" -exec grep -l "import rich\|from rich" {} \; 2>/dev/null | grep -v "flext-cli")
if [ -n "$rich_violations" ]; then
    echo "❌ ECOSYSTEM VIOLATION: Direct Rich imports found:"
    echo "$rich_violations"
    echo "RESOLUTION: Refactor to use flext-cli output wrappers"
fi

# 3. Validate CLI foundation APIs are available
python -c "
try:
    from flext_cli import FlextCliApi, FlextCliMain, FlextCliConfig, FlextCliConstants
    api = FlextCliApi()
    main = FlextCliMain()
    config = FlextCliConfig()
    print('✅ CLI Foundation APIs available')
except Exception as e:
    print(f'❌ CLI Foundation APIs incomplete: {e}')
    exit(1)
"

echo "✅ CLI foundation boundary validation completed"
```

### CLI Foundation Development Issues

**Common CLI Foundation Issues**:

1. **Incomplete Abstraction Coverage**

   ```bash
   # Check for missing wrapper coverage
   grep -r "TODO.*Click\|TODO.*Rich" src/flext_cli/
   ```

2. **CLI API Completeness Gaps**

   ```bash
   # Test CLI API coverage
   python -c "
   from flext_cli import FlextCliApi
   api = FlextCliApi()
   methods = [m for m in dir(api) if not m.startswith('_')]
   print(f'CLI API methods: {len(methods)}')
   print('Coverage areas:', methods[:10])
   "
   ```

3. **Ecosystem CLI Compliance**

   ```bash
   # Run ecosystem CLI compliance check
   ./scripts/validate_ecosystem_cli_compliance.sh
   ```

## CLI FOUNDATION DEVELOPMENT SUMMARY

**CLI ECOSYSTEM AUTHORITY**: flext-cli is the CLI foundation for the entire FLEXT ecosystem
**ZERO TOLERANCE ENFORCEMENT**: NO direct Click/Rich imports allowed anywhere in ecosystem
**ABSTRACTION COMPLETENESS**: ALL CLI and output needs must be covered by flext-cli wrappers
**ECOSYSTEM PROTECTION**: Every CLI change validated against dependent project compliance
**FOUNDATION QUALITY**: Sets CLI standards for all ecosystem projects with comprehensive abstraction

**DEVELOPMENT PRIORITIES**:

1. **Complete Click/Rich Abstraction**: Fill all wrapper gaps for 100% ecosystem coverage
2. **Ecosystem CLI Compliance**: Fix ALL direct Click/Rich imports in dependent projects
3. **Test Coverage Improvement**: Achieve 75% with REAL CLI functionality tests
4. **API Documentation**: Complete ecosystem usage examples for all CLI patterns
5. **Quality Leadership**: Maintain zero-compromise CLI infrastructure standards

---

**FLEXT-CLI AUTHORITY**: These guidelines are specific to CLI foundation development
**ECOSYSTEM CLI STANDARDS**: ALL CLI projects must follow these zero tolerance patterns
**EVIDENCE-BASED**: All patterns verified against current 30% functional baseline targeting 75%
