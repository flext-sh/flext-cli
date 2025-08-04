# Commands Layer - CLI Command Implementations

**Module**: `src/flext_cli/commands/`  
**Architecture Layer**: Presentation (CLI Interface)  
**Status**: 30% implemented - Only 3 of 10+ command groups functional  
**Sprint Alignment**: Critical expansion target for Sprints 1-10

## 🎯 Module Overview

The commands layer implements the actual CLI commands that users interact with. This layer provides the presentation interface for the FLEXT CLI, handling user input, formatting output, and coordinating with the application layer to fulfill user requests.

### **Key Responsibilities**

- **CLI Command Implementation**: Click-based command definitions
- **User Input Handling**: Argument parsing, validation, and processing
- **Output Formatting**: Rich console output with multiple format support
- **Error Presentation**: User-friendly error messages and help
- **Context Management**: CLI session and execution context handling

## 📁 Module Structure

```
src/flext_cli/commands/
├── __init__.py           # Command layer exports and registration
├── auth.py              # Authentication commands (✅ IMPLEMENTED)
├── config.py            # Configuration management commands (✅ IMPLEMENTED)
└── debug.py             # Debug and diagnostic commands (✅ IMPLEMENTED)
```

## 🚨 Critical Implementation Gap

### **Only 30% Implementation Complete**

**✅ Currently Implemented (3 command groups):**

- `auth.py` - Authentication and authorization commands
- `config.py` - Configuration management commands
- `debug.py` - Debug and diagnostic commands

**❌ Missing Critical Command Groups (7+ groups needed):**

- `pipeline.py` - Pipeline management (Sprint 1 - CRITICAL)
- `service.py` - Service orchestration (Sprint 1 - CRITICAL)
- `data.py` - Data management (Sprint 5)
- `plugin.py` - Plugin management (Sprint 6)
- `monitor.py` - Monitoring and observability (Sprint 7)
- Project-specific commands:
  - `projects/client-a.py` - client-a integration (Sprint 9)
  - `projects/client-b.py` - client-b integration (Sprint 9)
  - `projects/meltano.py` - Meltano integration (Sprint 9)

## 📊 Implementation Status

### ✅ **Fully Implemented Commands**

#### **auth.py - Authentication Commands**

```bash
flext auth login          # User authentication
flext auth logout         # Session termination
flext auth status         # Authentication status
flext auth token          # Token management
```

#### **config.py - Configuration Commands**

```bash
flext config show         # Display current configuration
flext config set <key>    # Set configuration value
flext config get <key>    # Get configuration value
flext config reset        # Reset to defaults
```

#### **debug.py - Debug Commands**

```bash
flext debug info          # System information
flext debug health        # Health checks
flext debug logs          # View logs
flext debug validate      # Validate installation
```

### ❌ **Missing Critical Commands (Sprint Implementation)**

#### **Sprint 1: Pipeline Management (CRITICAL)**

```bash
# Target commands - NOT IMPLEMENTED
flext pipeline list                    # List all data pipelines
flext pipeline start <name>           # Start specific pipeline
flext pipeline stop <name>            # Stop running pipeline
flext pipeline status <name>          # Check pipeline status
flext pipeline logs <name>            # View pipeline logs
```

**Implementation Location**: `src/flext_cli/commands/pipeline.py` (TO BE CREATED)

#### **Sprint 1: Service Orchestration (CRITICAL)**

```bash
# Target commands - NOT IMPLEMENTED
flext service health                   # Health check all services
flext service status                   # Overall ecosystem status
flext service start <service>         # Start FLEXT service
flext service stop <service>          # Stop FLEXT service
flext service logs <service>          # View service logs
```

**Implementation Location**: `src/flext_cli/commands/service.py` (TO BE CREATED)

#### **Sprint 5: Data Management**

```bash
# Target commands - NOT IMPLEMENTED
flext data taps list                   # List available Singer taps
flext data targets list               # List available Singer targets
flext data dbt run <project>          # Execute DBT transformations
flext data pipeline create <config>   # Create new data pipeline
```

**Implementation Location**: `src/flext_cli/commands/data.py` (TO BE CREATED)

## 🎯 Sprint Implementation Roadmap

### **Sprint 1: Core Infrastructure Commands** (CRITICAL - Blocks ecosystem management)

#### **1.1 Pipeline Management (`pipeline.py`)**

```python
# Target implementation
import click
from rich.console import Console
from flext_cli.core.base import handle_service_result

@click.group()
def pipeline():
    """Pipeline management commands."""
    pass

@pipeline.command()
@click.option('--status', help='Filter by status')
@click.option('--format', type=click.Choice(['table', 'json', 'yaml']), default='table')
@click.pass_context
@handle_service_result
def list(ctx: click.Context, status: Optional[str], format: str) -> FlextResult[None]:
    """List all data pipelines."""
    # Implementation using application layer services
```

#### **1.2 Service Orchestration (`service.py`)**

```python
# Target implementation
@click.group()
def service():
    """Service orchestration commands."""
    pass

@service.command()
@click.pass_context
@handle_service_result
def health(ctx: click.Context) -> FlextResult[None]:
    """Health check all FLEXT services."""
    # FlexCore:8080 and FLEXT Service:8081 integration
```

### **Sprint 5: Data Platform Commands**

#### **5.1 Data Management (`data.py`)**

```python
@click.group()
def data():
    """Data management commands."""
    pass

@data.group()
def taps():
    """Singer tap management."""
    pass

@taps.command()
def list():
    """List available Singer taps."""
    # Implementation for Singer ecosystem
```

### **Sprint 6: Plugin System Commands**

#### **6.1 Plugin Management (`plugin.py`)**

```python
@click.group()
def plugin():
    """Plugin management commands."""
    pass

@plugin.command()
def list():
    """List installed plugins."""
    # Plugin discovery and status
```

### **Sprint 7: Monitoring Commands**

#### **7.1 Monitoring (`monitor.py`)**

```python
@click.group()
def monitor():
    """Monitoring and observability commands."""
    pass

@monitor.command()
def dashboard():
    """Real-time monitoring dashboard."""
    # Rich-based dashboard implementation
```

### **Sprint 9: Project-Specific Commands**

#### **9.1 client-a Integration (`projects/client-a.py`)**

```python
@click.group()
def client-a():
    """client-a project operations."""
    pass

@client-a.command()
def migration():
    """client-a migration operations."""
    # client-a-specific functionality
```

## 🏗️ Architecture Patterns

### **Click Framework Integration**

All commands follow consistent Click patterns:

```python
import click
from rich.console import Console
from flext_cli.core.base import handle_service_result

@click.group()
def command_group():
    """Command group description."""
    pass

@command_group.command()
@click.option('--option', help='Option description')
@click.argument('argument')
@click.pass_context
@handle_service_result
def command_action(ctx: click.Context, option: str, argument: str) -> FlextResult[None]:
    """Command description."""
    console: Console = ctx.obj["console"]

    # Use application layer services
    result = service.execute_operation(argument, option)

    if result.success:
        console.print("[green]Operation completed successfully[/green]")

    return result
```

### **Rich UI Integration**

All commands use Rich for beautiful terminal output:

```python
from rich.table import Table
from rich.progress import track

def display_data(console: Console, data: List[dict]) -> None:
    table = Table(title="Results")
    table.add_column("Name", style="cyan")
    table.add_column("Status", style="green")

    for item in data:
        table.add_row(item["name"], item["status"])

    console.print(table)
```

## 🔧 Development Guidelines

### **Adding New Command Groups**

1. **Create Command Module**: `src/flext_cli/commands/{group}.py`
2. **Follow Click Patterns**: Use consistent command structure
3. **Register in CLI**: Add to main CLI group in `cli.py`
4. **Add Tests**: Comprehensive CLI testing with CliRunner
5. **Documentation**: Complete docstrings and help text

### **Command Implementation Template**

```python
# src/flext_cli/commands/new_group.py
import click
from rich.console import Console
from flext_cli.core.base import handle_service_result
from flext_cli.application.services import NewService

@click.group()
def new_group():
    """New command group description aligned with Sprint X objectives."""
    pass

@new_group.command()
@click.option('--format', type=click.Choice(['table', 'json', 'yaml']), default='table')
@click.pass_context
@handle_service_result
def list(ctx: click.Context, format: str) -> FlextResult[None]:
    """List items with rich formatting."""
    console: Console = ctx.obj["console"]
    service: NewService = ctx.obj["services"]["new_service"]

    result = service.list_items()
    if result.success:
        # Format and display results
        display_items(console, result.unwrap(), format)

    return result

# Register in src/flext_cli/cli.py
from flext_cli.commands import new_group
cli.add_command(new_group.new_group)
```

## 🧪 Testing Guidelines

### **CLI Command Testing**

```python
from click.testing import CliRunner
from flext_cli.cli import cli

def test_command_execution():
    runner = CliRunner()
    result = runner.invoke(cli, ['group', 'command', '--option', 'value'])

    assert result.exit_code == 0
    assert "expected output" in result.output

def test_command_error_handling():
    runner = CliRunner()
    result = runner.invoke(cli, ['group', 'command', '--invalid'])

    assert result.exit_code != 0
    assert "Error:" in result.output
```

### **Integration Testing**

```python
@pytest.mark.integration
def test_command_with_real_services():
    runner = CliRunner()
    result = runner.invoke(cli, ['pipeline', 'list'], catch_exceptions=False)

    assert result.exit_code == 0
    # Verify actual service integration
```

## 📈 Implementation Priority Matrix

### **Critical (Sprint 1-2)** - Blocks ecosystem functionality

1. **Pipeline Management** - Core data pipeline operations
2. **Service Orchestration** - Distributed service management

### **High (Sprint 5-6)** - Core platform features

3. **Data Management** - Singer ecosystem operations
4. **Plugin Management** - Extensibility and modularity

### **Medium (Sprint 7-8)** - Enhanced operations

5. **Monitoring** - Observability and diagnostics
6. **Interactive Mode** - Enhanced user experience

### **Lower (Sprint 9-10)** - Project-specific features

7. **client-a Commands** - Project-specific operations
8. **client-b Commands** - Project-specific operations
9. **Meltano Commands** - Meltano-specific operations

## 🔗 Integration Points

### **Application Layer Integration**

- Uses application services for business logic
- Coordinates with command and query handlers
- Manages application-level error handling

### **Infrastructure Layer Integration**

- Accesses configuration through dependency injection
- Uses external service clients for remote operations
- Leverages repository patterns for data access

### **Domain Layer Integration**

- Works with domain entities and value objects
- Respects domain business rules and validation
- Handles domain events and notifications

## 🔗 Related Documentation

- [Main CLI Entry Point](../cli.py) - CLI registration and main interface
- [Application Layer](../application/README.md) - Business logic coordination
- [TODO.md](../../../docs/TODO.md) - Sprint implementation roadmap
- [Command Reference](../../../docs/api/commands.md) - Complete command documentation

## 📋 Sprint Implementation Checklist

### **Sprint 1: Critical Commands** (BLOCKING)

- [ ] Implement `pipeline.py` with complete pipeline management
- [ ] Implement `service.py` with service orchestration
- [ ] Add comprehensive testing for both command groups
- [ ] Register commands in main CLI interface

### **Sprint 5: Data Platform Commands**

- [ ] Implement `data.py` with Singer ecosystem management
- [ ] Add DBT integration commands
- [ ] Implement data pipeline creation and management

### **Sprint 6: Plugin System Commands**

- [ ] Implement `plugin.py` with plugin lifecycle management
- [ ] Add plugin discovery and installation features
- [ ] Implement plugin dependency management

---

**Critical Blocker**: Pipeline and Service commands missing - CLI cannot manage FLEXT ecosystem without these  
**Architecture Layer**: Presentation (User interface and command processing)  
**Next Sprint Priority**: Implement pipeline.py and service.py in Sprint 1
