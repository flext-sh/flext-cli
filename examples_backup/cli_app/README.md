# CLI App Example - Complete FLEXT CLI Application

**Directory**: `examples/cli_app/`  
**Architecture Layer**: Complete Application Example  
**Status**: 80% implemented - Comprehensive CLI application architecture demonstration  
**Sprint Alignment**: Implementation roadmap for Sprints 1-10

## 🎯 Application Overview

This directory contains a complete CLI application example demonstrating Clean Architecture implementation with FLEXT CLI patterns. It serves as a reference implementation showing how to structure a real-world CLI application using all architectural layers.

### **Application Purpose**

Demonstrates a production-ready CLI application structure with:

- Complete Clean Architecture layer separation
- Domain-Driven Design patterns
- CQRS command/query handling (planned Sprint 2-3)
- Sprint-based feature implementation
- Project-specific command organization

## 📁 Application Structure

```
cli_app/
├── README.md                           # This file - application documentation
├── cli.py                              # Main CLI entry point with Click groups
├── application/                        # Application Layer (Orchestration)
│   ├── __init__.py                     # Application layer exports
│   └── commands.py                     # Command handlers and application services
└── commands/                           # Commands Layer (Presentation)
    ├── __init__.py                     # Command layer exports
    ├── auth.py                         # Authentication commands (✅ implemented)
    ├── config.py                       # Configuration commands (✅ implemented)
    ├── debug.py                        # Debug commands (✅ implemented)
    ├── pipeline.py                     # Pipeline commands (🎯 Sprint 1)
    ├── plugin.py                       # Plugin commands (🎯 Sprint 6)
    └── projects/                       # Project-specific commands
        ├── __init__.py                 # Project commands exports
        ├── algar.py                    # ALGAR project commands (🎯 Sprint 9)
        ├── gruponos.py                 # GrupoNos project commands (🎯 Sprint 9)
        └── meltano.py                  # Meltano integration commands (🎯 Sprint 6)
```

## 🏗️ Architecture Layers

### **Presentation Layer** (`cli.py` + `commands/`)

**Purpose**: User interface and command processing  
**Implementation**: 60% complete

- **Main CLI Entry Point** (`cli.py`): Click-based command groups with global options
- **Command Implementations** (`commands/*.py`): Individual command group implementations
- **Rich UI Integration**: Beautiful terminal output with tables, progress bars, panels

### **Application Layer** (`application/`)

**Purpose**: Use case orchestration and business workflow coordination  
**Implementation**: 40% complete

- **Command Handlers** (`commands.py`): Application-level command processing
- **Application Services**: Cross-cutting application concerns (planned)
- **CQRS Handlers**: Command/Query separation (Sprint 2-3)

### **Domain Layer** (Referenced from main project)

**Purpose**: Business logic and domain entities  
**Implementation**: Uses main project domain layer

- Domain entities: `CLICommand`, `CLISession`, `CLIPlugin`
- Business rules and validation
- Domain events and integration patterns

### **Infrastructure Layer** (Referenced from main project)

**Purpose**: External concerns and technical implementation  
**Implementation**: Uses main project infrastructure layer

- Configuration management and dependency injection
- External service clients (FlexCore, FLEXT Service)
- Repository patterns and data persistence

## 🚀 Usage Examples

### **Running the Application**

```bash
# Navigate to the example
cd examples/cli_app/

# Show all available commands
python cli.py --help

# Use implemented commands
python cli.py auth login --username admin
python cli.py config show --format json
python cli.py debug health --verbose

# Try planned commands (will show structure but may not be fully functional)
python cli.py pipeline list
python cli.py plugin status
python cli.py projects algar status
```

### **Global Options**

```bash
# Use different output formats
python cli.py --output json config show
python cli.py --output table debug health

# Use different profiles
python cli.py --profile production auth status
python cli.py --profile development config show

# Enable debug mode
python cli.py --debug pipeline list
```

### **Command Structure Examples**

```bash
# Authentication commands
python cli.py auth login --username admin --password secret
python cli.py auth logout
python cli.py auth status
python cli.py auth token --refresh

# Configuration commands
python cli.py config show
python cli.py config set api_url https://api.production.com
python cli.py config get debug
python cli.py config reset --confirm

# Debug commands
python cli.py debug info
python cli.py debug health --check-all
python cli.py debug logs --tail 100
python cli.py debug validate --fix-issues
```

## 📊 Implementation Status

### ✅ **Fully Implemented Commands**

#### **Authentication Commands** (`commands/auth.py`)

- User authentication and session management
- Token handling with refresh capabilities
- Status checking and validation
- Production-ready implementation

#### **Configuration Commands** (`commands/config.py`)

- Configuration display and management
- Key-value setting and retrieval
- Profile-based configuration
- Reset and validation functionality

#### **Debug Commands** (`commands/debug.py`)

- System information and diagnostics
- Health checks with detailed reporting
- Log access and analysis
- Validation and troubleshooting tools

### 🎯 **Planned Commands** (Sprint Implementation)

#### **Sprint 1: Pipeline Commands** (`commands/pipeline.py`)

```bash
# Target command structure
python cli.py pipeline list --status running
python cli.py pipeline start sample-etl --environment production
python cli.py pipeline stop sample-etl --graceful
python cli.py pipeline status sample-etl --detailed
python cli.py pipeline logs sample-etl --tail 50
```

#### **Sprint 6: Plugin Commands** (`commands/plugin.py`)

```bash
# Target command structure
python cli.py plugin list --enabled-only
python cli.py plugin install k8s-plugin --version latest
python cli.py plugin enable k8s-plugin
python cli.py plugin configure k8s-plugin --key value
python cli.py plugin status k8s-plugin
```

#### **Sprint 9: Project Commands** (`commands/projects/`)

```bash
# ALGAR project commands
python cli.py projects algar migration start --type oud
python cli.py projects algar status --detailed

# GrupoNos project commands
python cli.py projects gruponos sync --environment staging
python cli.py projects gruponos health --all-services

# Meltano integration commands
python cli.py projects meltano run sample-pipeline
python cli.py projects meltano schedule list
```

## 🎯 Sprint Development Roadmap

### **Sprint 1: Pipeline Management** (CRITICAL)

- **Target**: Implement complete pipeline management commands
- **Files**: `commands/pipeline.py`, application handlers
- **Integration**: FlexCore and FLEXT Service communication
- **Commands**: list, start, stop, status, logs, create, delete

### **Sprint 2-3: CQRS Enhancement**

- **Target**: Implement CQRS command/query separation
- **Files**: `application/commands.py` enhancement with CQRS handlers
- **Pattern**: Command handlers, query handlers, event handlers
- **Integration**: Domain events and application service coordination

### **Sprint 6: Plugin System**

- **Target**: Complete plugin management functionality
- **Files**: `commands/plugin.py`, plugin discovery system
- **Features**: install, configure, enable/disable, status, list
- **Integration**: Plugin discovery, dependency management, lifecycle

### **Sprint 9: Project Integration**

- **Target**: Project-specific command implementations
- **Files**: `commands/projects/*.py` full implementation
- **Projects**: ALGAR, GrupoNos, Meltano integration
- **Features**: Project-specific operations, status, configuration

## 🔧 Development Guidelines

### **Adding New Commands**

1. **Create Command Module**: Add new file in `commands/` directory
2. **Follow Pattern**: Use existing commands as templates
3. **Register Commands**: Add to main CLI group in `cli.py`
4. **Add Tests**: Create comprehensive test coverage
5. **Update Documentation**: Add to this README and main documentation

### **Command Implementation Template**

```python
# commands/new_feature.py
import click
from rich.console import Console
from flext_cli.core.base import handle_service_result

@click.group()
def new_feature():
    """New feature command group."""
    pass

@new_feature.command()
@click.option('--format', type=click.Choice(['table', 'json', 'yaml']), default='table')
@click.pass_context
@handle_service_result
def list(ctx: click.Context, format: str):
    """List new feature items."""
    console: Console = ctx.obj["console"]
    # Implementation
    console.print("[green]Success![/green]")

# Register in cli.py
from commands import new_feature
cli.add_command(new_feature.new_feature)
```

### **Application Layer Integration**

```python
# application/commands.py enhancement
class NewFeatureCommandHandler:
    def __init__(self, service: NewFeatureService):
        self._service = service

    async def handle_list_command(self, request: ListRequest) -> FlextResult[List[Item]]:
        # Application logic coordination
        return await self._service.list_items(request)
```

## 🧪 Testing the Application

### **Manual Testing**

```bash
# Test implemented functionality
python cli.py auth login --username test --password test
python cli.py config set test_key test_value
python cli.py debug info

# Test error handling
python cli.py auth login --username invalid
python cli.py config get nonexistent_key
```

### **Automated Testing**

```bash
# From project root, test CLI app integration
pytest tests/test_integration_cli_complete.py -v
pytest tests/test_e2e_workflows.py -v

# Test specific command groups
pytest tests/test_auth_commands.py -v
pytest tests/test_config_commands.py -v
pytest tests/test_debug_commands.py -v
```

## 📚 Learning Objectives

This example demonstrates:

1. **Clean Architecture**: Clear separation of concerns across layers
2. **Domain-Driven Design**: Rich domain entities and business logic
3. **Click Framework**: Professional CLI structure with hierarchical commands
4. **Rich UI**: Beautiful terminal interface with formatting
5. **Error Handling**: Comprehensive error handling with FlextResult patterns
6. **Configuration**: Multi-environment configuration management
7. **Testing**: Comprehensive testing strategies for CLI applications
8. **Sprint Planning**: Incremental development following roadmap

## 🔗 Related Documentation

- [Main FLEXT CLI](../../README.md) - Project overview and setup
- [Architecture Documentation](../../docs/architecture/) - Detailed architecture guides
- [Command Reference](../../docs/api/commands.md) - Complete command documentation
- [Development Guide](../../docs/development/) - Development patterns and standards
- [Sprint Roadmap](../../docs/TODO.md) - 10-sprint implementation plan

---

**Complete Example**: Production-ready CLI application architecture  
**Implementation**: 80% structure complete, 40% functionality implemented  
**Sprint Alignment**: Roadmap-driven development for Sprints 1-10
