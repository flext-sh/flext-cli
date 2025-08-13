# flext-cli - FLEXT Command Interface

**Type**: Application | **Status**: Active Development (~30% functional) | **Dependencies**: flext-core

**Unified command-line interface for the FLEXT distributed data integration ecosystem**. Provides centralized management, orchestration, and monitoring for all 32+ FLEXT projects including FlexCore services, data pipelines, Singer taps/targets, DBT transformations, and project-specific integrations.

> ⚠️ Current Status: Core foundations implemented; major functionality under development. See roadmap for completion timeline.

## 📋 **Recent Major Achievements**

- ✅ **Complete docstring standardization** - All 35 source files updated with comprehensive documentation
- ✅ **English standardization** - Repository moving toward English-only documentation
- ✅ **Sprint alignment** - All modules reference specific Sprint requirements from 10-sprint roadmap
- ✅ **Architecture documentation** - Comprehensive patterns documented in all layers (Domain, Application, Infrastructure)
- ✅ **Status indicators** - 251 status indicators (✅/⚠️/❌/🎯) across all files providing clear implementation status
- ✅ **Documentation modernization** - Complete English translation and modernization of all docs/ directory

## Mission & Vision

### 🎯 **Mission**

Provide a unified, enterprise-grade CLI that simplifies management and orchestration of the entire FLEXT distributed data integration ecosystem, enabling developers and operators to efficiently work with 32+ interconnected projects from a single command interface.

### 🚀 **Vision**

Become the primary interface for FLEXT ecosystem operations, offering:

- **Unified Management**: Single CLI for all FLEXT services, pipelines, and projects
- **Enterprise Operations**: Production-ready orchestration, monitoring, and debugging
- **Developer Productivity**: Streamlined workflows for development, testing, and deployment
- **Ecosystem Integration**: Seamless interaction between FlexCore, Singer pipelines, DBT, and project-specific tools

### 🏗️ **FLEXT Ecosystem Integration**

FLEXT CLI serves as the central command hub for:

#### **Core Services (2 services)**

- **FlexCore** (Go): Runtime container service (port 8080)
- **FLEXT Service** (Go/Python): Main data platform service (port 8081)

#### **Data Integration (15 Singer projects)**

- **5 Taps**: Oracle, LDAP, LDIF, Oracle OIC, Oracle WMS extractors
- **5 Targets**: Oracle, LDAP, LDIF, Oracle OIC, Oracle WMS loaders
- **4 DBT Projects**: LDAP, LDIF, Oracle, Oracle WMS transformers
- **1 Extension**: Oracle OIC extensions

#### **Application Services (5 projects)**

- **flext-api**: REST API services
- **flext-auth**: Authentication and authorization
- **flext-web**: Web interface and dashboard
- **flext-quality**: Code quality analysis
- **flext-cli**: This command-line interface

#### **Infrastructure & Foundation (8 projects)**

- **flext-core**: Base patterns and shared library
- **flext-observability**: Monitoring and metrics
- **flext-db-oracle**: Oracle database connectivity
- **flext-ldap**: LDAP directory services
- **flext-ldif**: LDIF file processing
- **flext-oracle-wms**: Oracle WMS integration
- **flext-grpc**: gRPC communication
- **flext-meltano**: Singer/Meltano/DBT orchestration

#### **Project-Specific Integrations (2 projects)**

- **client-a-oud-mig**: client-a Oracle Unified Directory migration
- **client-b-meltano-native**: client-b-specific Meltano implementation

## Current Features (30% Complete)

### ✅ Implemented & Working

- **🎨 Rich Terminal UI**: Beautiful output with tables, progress bars, panels (Rich library)
- **🏗️ Clean Architecture**: Domain-driven design with flext-core foundation
- **🔐 Authentication**: User authentication and token management (`flext auth`)
- **⚙️ Configuration**: Basic configuration management (`flext config`)
- **🐛 Debugging**: Diagnostic and debugging tools (`flext debug`)
- **📊 Multiple Output Formats**: JSON, YAML, Table, CSV, Plain text support
- **🎯 Type Safety**: MyPy strict mode enabled; ongoing work to reach zero errors
- **🧪 Quality Gates**: Coverage improving toward 90%; validation pipeline enabled

### ⚠️ Partially Implemented

- **🏗️ flext-core Integration (60%)**: Good foundations, missing enterprise patterns
  - ✅ FlextResult (railway-oriented programming)
  - ✅ FlextEntity (domain modeling)
  - ✅ FlextValueObject (immutable value objects)
  - ✅ FlextSettings (configuration)
  - ❌ FlextContainer (dependency injection)
  - ❌ CQRS (command/query separation)
  - ❌ Domain Events (event-driven architecture)

### ❌ Missing Critical Features

#### **Pipeline Management** (Priority 1)

```bash
flext pipeline list                    # List all data pipelines
flext pipeline start <name>           # Start specific pipeline
flext pipeline stop <name>            # Stop running pipeline
flext pipeline status <name>          # Check pipeline status
flext pipeline logs <name>            # View pipeline logs
```

#### **Service Orchestration** (Priority 1)

```bash
flext service health                   # Health check all services
flext service start <service>         # Start FLEXT service
flext service stop <service>          # Stop FLEXT service
flext service logs <service>          # View service logs
flext service status                  # Overall ecosystem status
```

#### **Data Management** (Priority 2)

```bash
flext data taps list                   # List available Singer taps
flext data targets list               # List available Singer targets
flext data dbt run <project>          # Execute DBT transformations
flext data pipeline create <config>   # Create new data pipeline
```

#### **Plugin & Extension Management** (Priority 2)

```bash
flext plugin list                      # List installed plugins
flext plugin install <name>           # Install plugin/extension
flext plugin enable <name>            # Enable plugin
flext plugin disable <name>           # Disable plugin
```

#### **Project-Specific Commands** (Priority 3)

```bash
flext client-a migration status          # client-a migration operations
flext client-a oud sync                  # Oracle Unified Directory sync
flext client-b pipeline deploy        # client-b pipeline deployment
flext meltano project init           # Meltano project initialization
```

#### **Monitoring & Observability** (Priority 3)

```bash
flext monitor dashboard               # Real-time monitoring dashboard
flext monitor metrics <service>       # Service-specific metrics
flext monitor alerts list            # Active alerts and warnings
flext logs search <query>            # Distributed log search
```

## Architecture & Design

### 🏗️ **Target Architecture (Enterprise-Grade)**

FLEXT CLI follows Clean Architecture principles with full flext-core integration to provide enterprise-grade functionality:

```
┌─────────────────────────────────────────────────────────────────┐
│                    FLEXT CLI - Unified Interface                │
├─────────────────────────────────────────────────────────────────┤
│                     Command Layer (Click)                      │
├─────────────────────────────────────────────────────────────────┤
│  pipeline │ service │ data │ plugin │ monitor │ project │ auth  │
├─────────────────────────────────────────────────────────────────┤
│                  Application Layer (CQRS)                      │
│     Commands    │    Queries     │    Event Handlers          │
├─────────────────────────────────────────────────────────────────┤
│                    Domain Layer (DDD)                          │
│  Entities │ Value Objects │ Domain Events │ Business Rules     │
├─────────────────────────────────────────────────────────────────┤
│                 Infrastructure Layer                           │
│   Repositories │ External APIs │ File System │ Configuration   │
├─────────────────────────────────────────────────────────────────┤
│                      flext-core Foundation                     │
│ FlextResult │ FlextContainer │ FlextEvents │ FlextRepository   │
└─────────────────────────────────────────────────────────────────┘
                                 │
                    ┌─────────────┴─────────────┐
                    │     FLEXT Ecosystem      │
                    │                          │
            ┌───────┴────────┐        ┌───────┴────────┐
            │   FlexCore     │        │ FLEXT Service  │
            │   (Go:8080)    │        │ (Go/Py:8081)   │
            └────────────────┘        └────────────────┘
                    │                          │
    ┌───────────────┼──────────────────────────┼──────────────────┐
    │                                                             │
┌───▼────┐  ┌─────────┐  ┌─────────┐  ┌──────────┐  ┌──────────┐
│ Singer │  │   DBT   │  │ Project │  │    Web   │  │   API    │
│ Pipes  │  │Transform│  │Specific │  │Interface │  │Services  │
│(15 proj│  │(4 proj) │  │(2 proj) │  │          │  │          │
└────────┘  └─────────┘  └─────────┘  └──────────┘  └──────────┘
```

### 📁 **Current Implementation Status**

```
src/flext_cli/
├── domain/                    # ✅ GOOD: FlextEntity domain modeling
│   ├── entities.py           # ✅ CLICommand, CLISession, CLIPlugin entities
│   ├── cli_context.py        # ✅ Value objects with validation
│   └── cli_services.py       # ⚠️ BASIC: Services need FlextDomainService
├── application/               # ⚠️ INCOMPLETE: Missing CQRS implementation
│   └── commands.py           # ⚠️ Basic handlers, need proper command pattern
├── infrastructure/            # ⚠️ PARTIAL: Custom DI, need FlextContainer
│   ├── container.py          # ❌ SimpleDIContainer instead of FlextContainer
│   └── config.py             # ✅ Configuration management
├── commands/                  # ❌ CRITICAL GAP: Only 3 of 10+ groups
│   ├── auth.py              # ✅ Authentication (functional)
│   ├── config.py            # ✅ Configuration (functional)
│   ├── debug.py             # ✅ Debugging (functional)
│   │
│   └── [MISSING COMMANDS]    # ❌ See "Missing Critical Features" above
├── core/                      # ✅ GOOD: CLI utilities with FlextResult
│   ├── base.py              # ✅ CLIContext, handle_service_result
│   ├── decorators.py        # ✅ CLI decorators and patterns
│   └── formatters.py        # ✅ Output formatting utilities
└── utils/                     # ✅ GOOD: FlextSettings integration
    ├── auth.py              # ✅ Authentication utilities
    ├── config.py            # ✅ Configuration with FlextSettings
    └── output.py            # ✅ Rich console output
```

### 🎯 **Architecture Goals & Principles**

1. **Unified Interface**: Single CLI for entire FLEXT ecosystem (32+ projects)
2. **Enterprise Patterns**: Full flext-core integration (CQRS, Events, DI)
3. **Service Integration**: Direct communication with FlexCore & FLEXT services
4. **Extensibility**: Plugin architecture for project-specific functionality
5. **Observability**: Comprehensive logging, metrics, and monitoring
6. **Developer Experience**: Rich UI, tab completion, interactive mode

## Installation

```bash
# Install dependencies with Poetry
cd /home/marlonsc/flext/flext-cli
poetry install --all-extras --with dev,test,docs,security

# Install CLI globally
make install-cli

# Verify installation
poetry run flext --version
```

## Development Commands

### Quality Standards

```bash
# Complete validation pipeline (run before commits)
make validate                 # lint + type-check + security + test (90% coverage)

# Essential checks
make check                   # lint + type-check + test

# Individual quality gates
make lint                    # Ruff linting (ALL rules enabled)
make type-check              # MyPy strict mode (working toward zero errors)
make test                    # pytest with 90% coverage requirement
make security                # Bandit + pip-audit + secrets scan
```

### Development Setup

```bash
# Complete setup
make setup                   # Complete setup with pre-commit hooks
make install                 # Install dependencies with Poetry
make dev-install             # Development mode with all extras

# CLI operations
make install-cli             # Install CLI globally
make test-cli                # Test CLI commands
make cli-smoke-test          # Run smoke tests
```

## Quick Start

```bash
# List available commands
poetry run flext --help

# ✅ Working command groups (only 3 implemented)
poetry run flext auth --help        # Authentication commands
poetry run flext config --help      # Configuration management
poetry run flext debug --help       # Debug and diagnostic tools

# ⚠️ Placeholder commands (show "coming soon")
poetry run flext interactive        # Shows "Interactive mode coming soon!"
poetry run flext version           # Basic version information

# ❌ Missing command groups (not implemented)
# poetry run flext pipeline --help    # Not implemented
# poetry run flext plugin --help      # Not implemented
# poetry run flext client-a --help       # Not implemented
# poetry run flext client-b --help    # Not implemented
# poetry run flext meltano --help     # Not implemented
```

### 🎯 **Quick Start Guide**

#### **1. Current Functional Commands**

```bash
# ✅ Authentication & Authorization
flext auth login                       # Login to FLEXT ecosystem
flext auth logout                      # Logout and clear tokens
flext auth status                      # Check authentication status
flext auth token                       # Display current auth token

# ✅ Configuration Management
flext config show                      # Display current configuration
flext config set <key> <value>        # Set configuration value
flext config get <key>                # Get configuration value
flext config reset                     # Reset to default configuration

# ✅ Debugging & Diagnostics
flext debug info                       # System and environment information
flext debug health                     # Basic health checks
flext debug logs                       # View application logs
flext debug validate                   # Validate CLI installation
```

#### **2. Placeholder Commands (Show "Coming Soon")**

```bash
# ⚠️ These show status messages but don't perform operations
flext interactive                      # "Interactive mode coming soon!"
flext version                          # Basic version information
```

#### **3. Priority Development Targets**

**Next Sprint (Priority 1)**:

```bash
# 🚧 Pipeline Management (Critical for FLEXT ecosystem)
flext pipeline list                    # List all active pipelines
flext pipeline status <name>          # Check specific pipeline status
flext pipeline start <name>           # Start data pipeline
flext pipeline stop <name>            # Stop running pipeline

# 🚧 Service Orchestration (Critical for distributed services)
flext service health                   # Health check all FLEXT services
flext service status                   # Overall ecosystem status
flext service logs <service>          # View service-specific logs
```

**Sprint 2-3 (Priority 2)**:

```bash
# 🚧 Data Management
flext data taps list                   # Available Singer taps
flext data targets list               # Available Singer targets
flext data dbt run <project>          # Execute DBT transformations

# 🚧 Plugin Management
flext plugin list                      # Installed plugins
flext plugin install <name>           # Install new plugin
```

**Future Sprints (Priority 3)**:

```bash
# 🚧 Project-Specific Integration
flext client-a migration status          # client-a-specific operations
flext client-b pipeline deploy        # client-b-specific operations
flext meltano project init           # Meltano project management

# 🚧 Monitoring & Observability
flext monitor dashboard               # Real-time monitoring
flext monitor metrics <service>       # Service metrics
flext logs search <query>            # Distributed log search
```

## Command Structure (Current vs Planned)

```
flext
├── auth                   # ✅ Authentication commands (IMPLEMENTED)
├── config                 # ✅ Configuration management (IMPLEMENTED)
├── debug                  # ✅ Debug and diagnostic tools (IMPLEMENTED)
├── interactive            # ⚠️ Interactive mode (placeholder - shows "coming soon")
├── version                # ⚠️ Version information (basic implementation)
└── [MISSING COMMANDS]     # ❌ The following are NOT implemented:
    ├── pipeline           # ❌ Pipeline operations (missing)
    ├── plugin             # ❌ Plugin management (missing)
    ├── client-a              # ❌ client-a project commands (missing)
    ├── client-b           # ❌ client-b project commands (missing)
    └── meltano            # ❌ Meltano integration commands (missing)
```

**Implementation Status**: 3 out of 10+ expected command groups

## Configuration

### Global CLI Options

```bash
# Profile support
flext --profile development command
flext --profile production command

# Output formats
flext --output json command
flext --output table command  # default
flext --output yaml command
flext --output csv command

# Debug mode
flext --debug command
flext --quiet command
```

### Environment Variables

```bash
# CLI Configuration
export FLEXT_CLI_DEV_MODE=true
export FLEXT_CLI_LOG_LEVEL=debug
export FLEXT_CLI_CONFIG_PATH=/path/to/config.yaml

# Profile and output
export FLX_PROFILE=development
export FLX_DEBUG=true
```

### Configuration Files

- Project config: `config/dev.yaml`, `config/prod.yaml`
- User config: `~/.flx/config.yaml` (future implementation)
- Environment variables override file settings

## Testing

### flext-core Integration Testing

```python
from flext_cli.domain.entities import CLICommand, CommandStatus, CommandType
from flext_core import FlextResult

def test_command_lifecycle_with_flext_patterns():
    # ✅ Good: Uses FlextEntity inheritance
    command = CLICommand(
        name="test",
        command_line="echo hello",
        command_type=CommandType.SYSTEM
    )

    # ✅ Good: Domain validation with FlextResult
    validation_result = command.validate_domain_rules()
    assert validation_result.success

    # ✅ Good: Immutable updates with model_copy
    running_command = command.start_execution()
    assert running_command.command_status == CommandStatus.RUNNING

    completed_command = running_command.complete_execution(exit_code=0, stdout="hello")
    assert completed_command.successful
```

### CLI Command Testing

```python
from click.testing import CliRunner
from flext_cli.cli import cli

def test_cli_commands():
    runner = CliRunner()

    # Test main CLI
    result = runner.invoke(cli, ['--version'])
    assert result.exit_code == 0

    # Test command groups
    result = runner.invoke(cli, ['auth', '--help'])
    assert result.exit_code == 0
```

### Running Tests

```bash
# Full test suite with coverage
make test

# Test specific modules
pytest tests/test_domain.py -v
pytest tests/test_commands.py -v

# Integration tests
pytest tests/test_integration.py -v
```

## Dependencies

### Core Dependencies (flext-core Ecosystem)

- **flext-core**: Foundation library - **60% integration complete**

  - ✅ FlextResult (excellent railway-oriented programming)
  - ✅ FlextEntity (good domain modeling with validation)
  - ✅ FlextValueObject (proper immutable value objects)
  - ✅ FlextSettings (good configuration management)
  - ❌ FlextContainer (using custom SimpleDIContainer instead)
  - ❌ CQRS patterns (no command/query separation)
  - ❌ Domain Events (defined but unused)
  - ❌ Repository pattern (only mock implementations)

- **flext-observability**: Monitoring and metrics
- **Click 8.2+**: CLI framework with hierarchical commands
- **Rich 14.0+**: Terminal UI components (tables, progress bars, panels)
- **Pydantic 2.11+**: Data validation (used via flext-core integration)

### Project-Specific Dependencies (Local Development)

- **client-a-oud-mig**: client-a project integration (local dependency)
- **client-b-meltano-native**: client-b project integration (local dependency)
- **flext-meltano**: Meltano orchestration (local dependency)

**Integration Status**: Good foundations but missing enterprise-grade flext-core patterns

## Development Workflow

### Adding New Commands

1. Create command module in `commands/` or `commands/projects/`
2. Use Click decorators with Rich output formatting
3. Register command in `cli.py` main group
4. Add comprehensive tests with CliRunner
5. Run `make validate` before committing

### Example New Command (Following flext-core Patterns)

```python
# commands/new_feature.py
import click
from rich.console import Console
from flext_core import FlextResult, get_logger
from flext_cli.core.base import handle_service_result

logger = get_logger(__name__)

@click.group()
def new_feature():
    """New feature commands using flext-core patterns."""
    pass

@new_feature.command()
@click.pass_context
@handle_service_result  # ✅ Handles FlextResult automatically
def action(ctx: click.Context) -> FlextResult[None]:
    """Perform new feature action with proper error handling."""
    console: Console = ctx.obj["console"]

    try:
        # Business logic here
        console.print("[green]Success![/green]")
        logger.info("New feature action completed successfully")
        return FlextResult.ok(None)
    except Exception as e:
        logger.error(f"New feature action failed: {e}")
        return FlextResult.fail(f"Action failed: {e}")

# Register in cli.py (add after line 102)
from flext_cli.commands import new_feature
cli.add_command(new_feature.new_feature)
```

**Key Improvements**: Uses FlextResult, structured logging, proper error handling

## Quality Standards

### Quality Targets

- **Linting**: Ruff compliance with comprehensive rule set
- **Type Safety**: MyPy strict mode adoption; aim for zero errors
- **Test Coverage**: 90% target across core modules
- **Security**: Bandit + pip-audit scanning in CI
- **Pre-commit hooks**: Recommended for local enforcement

### Code Style

- **Python 3.13+**: Modern syntax and type hints
- **Clean Architecture**: Strict layer separation
- **Domain-Driven Design**: Rich domain entities
- **Type Safety**: Complete type coverage with MyPy

## Troubleshooting

### Common Issues

1. **Import Errors**

   ```bash
   # Clean and reinstall dependencies
   rm -rf .venv && poetry install --all-extras
   ```

2. **Type Check Failures**

   ```bash
   # Run MyPy with specific paths
   poetry run mypy src/flext_cli --show-error-codes
   ```

3. **Test Failures**

   ```bash
   # Run tests with verbose output
   poetry run pytest tests/ -v -s
   ```

### Getting Help

```bash
# General help
poetry run flext --help

# Command group help
poetry run flext auth --help
poetry run flext config --help

# View project structure
ls -la src/flext_cli/
```

## Project Status (Honest Assessment)

### ✅ **Implemented & Working**

- **Clean Architecture Foundation**: Good domain layer with flext-core FlextEntity
- **Core Commands**: 3 command groups (auth, config, debug) functional
- **Quality Gates**: Comprehensive validation pipeline with 90% coverage
- **Testing**: Complete test suite with pytest framework
- **flext-core Basics**: FlextResult, FlextEntity, FlextValueObject, FlextSettings

### ⚠️ **Partial Implementation**

- **flext-core Integration**: 60% complete - good foundations, missing enterprise patterns
- **CLI Functionality**: Only 3 out of 10+ expected command groups
- **Service Layer**: Basic services but not using FlextDomainService patterns
- **Dependency Injection**: Custom container instead of FlextContainer

### ❌ **Missing Critical Features**

- **Pipeline Commands**: Pipeline management not implemented
- **Interactive Mode**: Placeholder only - no REPL functionality
- **Service Integration**: No FlexCore (8080) or FLEXT Service (8081) integration
- **Project Commands**: client-a, client-b, Meltano commands missing
- **Enterprise Patterns**: CQRS, Domain Events, Repository pattern not implemented

## 📋 **Development Roadmap**

### **Phase 1: Critical Infrastructure (Sprint 1-2)**

**Goal**: Enable basic FLEXT ecosystem management

1. **Pipeline Management Commands** (Priority 1)

   - `flext pipeline list|start|stop|status|logs`
   - Integration with FlexCore (Go:8080) and FLEXT Service (Go/Py:8081)
   - Real-time pipeline monitoring and control

2. **Service Orchestration** (Priority 1)

   - `flext service health|status|logs|start|stop`
   - Health checks for all 32+ FLEXT ecosystem projects
   - Service discovery and dependency mapping

3. **FlextContainer Migration** (Technical Debt)
   - Replace SimpleDIContainer with flext-core FlextContainer
   - Type-safe dependency injection across all services
   - Proper service lifecycle management

### **Phase 2: Data Platform Integration (Sprint 3-4)**

**Goal**: Complete data pipeline management capabilities

1. **Data Management Commands**

   - `flext data taps|targets|dbt` - Singer ecosystem management
   - Integration with 15 Singer projects (5 taps + 5 targets + 4 DBT + 1 extension)
   - Pipeline creation, monitoring, and troubleshooting

2. **Plugin & Extension Management**

   - `flext plugin list|install|enable|disable`
   - Dynamic loading of project-specific functionality
   - Extension marketplace and dependency resolution

3. **CQRS Implementation** (Technical Enhancement)
   - Command/Query separation for complex operations
   - Event-driven architecture with Domain Events
   - Improved scalability and maintainability

### **Phase 3: Project-Specific Integration (Sprint 5-6)**

**Goal**: Full ecosystem project support

1. **client-a Integration** (`flext client-a`)

   - Oracle Unified Directory migration commands
   - client-a-specific pipeline and data operations
   - Integration with client-a-oud-mig project

2. **client-b Integration** (`flext client-b`)

   - client-b-specific Meltano operations
   - Pipeline deployment and management
   - Integration with client-b-meltano-native project

3. **Meltano Native Support** (`flext meltano`)
   - Meltano project initialization and management
   - Singer tap/target orchestration
   - DBT transformation execution

### **Phase 4: Enterprise Operations (Sprint 7-8)**

**Goal**: Production-ready enterprise features

1. **Monitoring & Observability**

   - `flext monitor dashboard|metrics|alerts`
   - Real-time monitoring dashboard with Rich UI
   - Integration with flext-observability project

2. **Distributed Logging**

   - `flext logs search|tail|export`
   - Centralized log aggregation and search
   - Correlation across all FLEXT services

3. **Interactive Mode & UX**
   - Functional REPL with tab completion
   - Context-aware help and command suggestion
   - Command history and session management

### **Phase 5: Advanced Features (Sprint 9-10)**

**Goal**: Advanced operational capabilities

1. **Configuration Management**

   - Profile system (dev/staging/prod environments)
   - Hierarchical configuration with inheritance
   - Secrets management integration

2. **Performance & Reliability**

   - Circuit breaker patterns for service calls
   - Retry policies and graceful degradation
   - Performance benchmarking and optimization

3. **Security & Compliance**
   - Enhanced authentication and authorization
   - Audit logging and compliance reporting
   - Security scanning and vulnerability management

## 📊 **Success Metrics & Goals**

### **Completion Targets**

- **Sprint 2**: 50% functional (pipeline + service commands)
- **Sprint 4**: 70% functional (data management + plugins)
- **Sprint 6**: 85% functional (project integrations)
- **Sprint 8**: 95% functional (monitoring + observability)
- **Sprint 10**: 100% functional (advanced features)

### **Quality Gates**

- **Test Coverage**: Maintain 90%+ throughout development
- **flext-core Integration**: Achieve 95% pattern compliance
- **Performance**: <1s response time for basic commands
- **Documentation**: 100% command coverage with examples
- **Integration**: Seamless operation with all 32+ FLEXT projects

### **Developer Experience Goals**

- **Discoverability**: Intuitive command structure and help system
- **Productivity**: Streamlined workflows for common operations
- **Reliability**: Consistent behavior across all environments
- **Extensibility**: Easy plugin development and integration

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Run `make validate` before committing
4. Commit your changes (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

## License

MIT License - see [LICENSE](LICENSE) for details.

## Documentation

### Architecture & Development

- [CLAUDE.md](CLAUDE.md) - Development guidance and architectural patterns
- [ARCHITECTURE.md](ARCHITECTURE.md) - Detailed architectural decisions and patterns
- [docs/](docs/) - Comprehensive project documentation

### Related Projects

- [../../flext-core/](../../flext-core/) - Foundation library with shared patterns
- [../../flext-observability/](../../flext-observability/) - Monitoring and metrics integration
- [../../flext-meltano/](../../flext-meltano/) - Meltano orchestration platform

### Ecosystem Integration

- [../../flexcore/](../../flexcore/) - Go runtime container service (port 8080)
- [../../cmd/flext/](../../cmd/flext/) - Go/Python data integration service (port 8081)
- [../../flext-api/](../../flext-api/) - REST API services
- [../../flext-web/](../../flext-web/) - Web interface and dashboard

---

**Framework**: FLEXT Ecosystem | **Language**: Python 3.13+ | **Architecture**: Clean Architecture + DDD | **Updated**: 2025-08-13
