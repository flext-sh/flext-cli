# Python Module Organization & Semantic Patterns

**FLEXT CLI Module Architecture & Integration with the FLEXT Ecosystem**

---

## 🏗️ **Module Architecture Overview**

FLEXT CLI implements a **layered module architecture** following Clean Architecture, Domain-Driven Design, and railway-oriented programming patterns established by flext-core. As the unified command-line interface for the entire FLEXT ecosystem (32+ projects), it serves as the operational gateway while maintaining consistency with ecosystem standards.

### **Core Design Principles**

1. **CLI-First Design**: Optimized for command-line interface patterns and user experience
2. **Ecosystem Integration**: Seamless integration with all 32+ FLEXT projects
3. **flext-core Compliance**: Full adoption of established ecosystem patterns
4. **Command-Oriented**: Command and query patterns for CLI operations
5. **Rich UX**: Beautiful terminal interface with comprehensive feedback

---

## 📁 **Module Structure & Responsibilities**

### **CLI Presentation Layer**

```python
# Command-line interface and user interaction
src/flext_cli/
├── __init__.py              # 🎯 Public CLI API gateway
├── cli.py                   # 🎯 Main CLI entry point (Click)
├── simple_api.py            # 🎯 Simple API for CLI setup
└── flext_cli.py             # 🎯 Legacy entry point
```

**Responsibility**: Provide the main command-line interface entry points and public API.

**Import Pattern**:

```python
# Primary CLI usage
from flext_cli.cli import cli
from flext_cli.simple_api import setup_cli

# Direct CLI execution
if __name__ == "__main__":
    cli()
```

### **Domain Layer (DDD Patterns)**

```python
# Business logic and domain modeling
├── domain/
│   ├── __init__.py          # 🏛️ Domain public API
│   ├── entities.py          # 🏛️ CLI domain entities (FlextEntity)
│   ├── cli_context.py       # 🏛️ CLI value objects and context
│   └── cli_services.py      # 🏛️ Domain services and business logic
```

**Responsibility**: Define CLI business logic, domain entities, and core business rules.

**Domain Entity Pattern**:

```python
from flext_core import FlextEntity, FlextResult
from flext_cli.domain.entities import CLICommand, CLISession

# Rich domain entities with business logic
class CLICommand(FlextEntity):
    name: str
    command_line: str
    command_type: CommandType

    def start_execution(self) -> FlextResult[None]:
        """Start command execution with domain events"""
        if self.command_status != CommandStatus.PENDING:
            return FlextResult.fail("Command already started")

        self.command_status = CommandStatus.RUNNING
        self.started_at = datetime.utcnow()
        self.add_domain_event(CommandStartedEvent(command_id=self.id))
        return FlextResult.ok(None)
```

### **Application Layer (CQRS & Commands)**

```python
# Application orchestration and command handling
├── application/
│   ├── __init__.py          # 📤 Application layer public API
│   └── commands.py          # 📤 Command handlers and application services
```

**Responsibility**: Orchestrate CLI operations and implement command/query separation.

**Command Handler Pattern**:

```python
from flext_core import FlextCommand, FlextCommandHandler, FlextResult
from flext_cli.application.commands import ExecuteCLICommandHandler

class ExecuteCLICommand(FlextCommand):
    command_line: str
    working_directory: str
    environment: dict

class ExecuteCLICommandHandler(FlextCommandHandler[ExecuteCLICommand]):
    async def handle(self, command: ExecuteCLICommand) -> FlextResult[CLICommandResult]:
        # Command execution logic with proper error handling
        return FlextResult.ok(result)
```

### **Command Implementation Layer**

```python
# Concrete CLI command implementations
├── commands/
│   ├── __init__.py          # 🖥️ Commands module public API
│   ├── auth.py              # 🖥️ Authentication commands (✅ implemented)
│   ├── config.py            # 🖥️ Configuration commands (✅ implemented)
│   ├── debug.py             # 🖥️ Debug commands (✅ implemented)
│   │
│   # 📋 PLANNED: Additional command groups (Sprint 1-10)
│   ├── pipeline.py          # 🖥️ Pipeline management (Sprint 1)
│   ├── service.py           # 🖥️ Service orchestration (Sprint 1-2)
│   ├── data.py              # 🖥️ Data management (Sprint 3-4)
│   ├── plugin.py            # 🖥️ Plugin management (Sprint 4)
│   ├── monitor.py           # 🖥️ Monitoring & observability (Sprint 7)
│   ├── algar.py             # 🖥️ ALGAR project commands (Sprint 5)
│   ├── gruponos.py          # 🖥️ GrupoNos project commands (Sprint 5)
│   └── meltano.py           # 🖥️ Meltano integration (Sprint 6)
```

**Responsibility**: Implement concrete CLI commands following Click framework patterns.

**Command Implementation Pattern**:

```python
import click
from rich.console import Console
from flext_cli.core.base import handle_service_result

@click.group()
def pipeline():
    """Pipeline management commands."""
    pass

@pipeline.command()
@click.option('--environment', '-e', default='development')
@click.argument('pipeline_name')
@click.pass_context
@handle_service_result
async def start(ctx: click.Context, pipeline_name: str, environment: str):
    """Start a data pipeline."""
    console: Console = ctx.obj["console"]

    # Use domain service with proper error handling
    result = await pipeline_service.start_pipeline(pipeline_name, environment)
    if result.success:
        console.print(f"[green]✅ Pipeline '{pipeline_name}' started[/green]")
    else:
        console.print(f"[red]❌ Failed: {result.error}[/red]")
```

### **Core Utilities Layer**

```python
# CLI-specific utilities and patterns
├── core/
│   ├── __init__.py          # 🔧 Core utilities public API
│   ├── base.py              # 🔧 Base CLI patterns and context models
│   ├── decorators.py        # 🔧 CLI decorators and error handling
│   ├── formatters.py        # 🔧 Output formatting utilities
│   ├── helpers.py           # 🔧 Helper functions and utilities
│   └── types.py             # 🔧 Click parameter types and CLI types
```

**Responsibility**: Provide CLI-specific utilities, decorators, and cross-cutting concerns.

**Decorator Pattern**:

```python
from functools import wraps
from flext_core import FlextResult
from rich.console import Console

def handle_service_result(func):
    """Decorator to handle FlextResult in CLI commands"""
    @wraps(func)
    async def wrapper(ctx: click.Context, *args, **kwargs):
        try:
            result = await func(ctx, *args, **kwargs)
            if isinstance(result, FlextResult) and result.is_failure:
                console: Console = ctx.obj["console"]
                console.print(f"[red]Error: {result.error}[/red]")
                ctx.exit(1)
            return result
        except Exception as e:
            console: Console = ctx.obj["console"]
            console.print(f"[red]Unexpected error: {e}[/red]")
            ctx.exit(1)
    return wrapper
```

### **Infrastructure Layer**

```python
# External integrations and persistence
├── infrastructure/
│   ├── __init__.py          # ⚙️ Infrastructure layer public API
│   ├── container.py         # ⚙️ Dependency injection container
│   └── config.py            # ⚙️ Configuration management
```

**Responsibility**: Handle external system integration and dependency management.

**Container Pattern**:

```python
from flext_core import FlextContainer
from flext_cli.infrastructure.container import setup_container

# TARGET: Migration from SimpleDIContainer to FlextContainer
def setup_cli_container() -> FlextContainer:
    """Setup dependency injection container with CLI services"""
    container = FlextContainer()

    # Register CLI services
    container.register_typed(CLICommandService, CLICommandService)
    container.register_typed(ConfigService, ConfigService)
    container.register_typed(AuthService, AuthService)

    # Register external service clients
    container.register_typed(FlexCoreClient, FlexCoreClient)
    container.register_typed(FlextServiceClient, FlextServiceClient)

    return container
```

### **Utility & Configuration Layer**

```python
# Configuration and utility modules
├── utils/
│   ├── __init__.py          # 🛠️ Utilities public API
│   ├── auth.py              # 🛠️ Authentication utilities
│   ├── config.py            # 🛠️ Configuration utilities (FlextBaseSettings)
│   └── output.py            # 🛠️ Rich console output utilities
├── config/
│   ├── __init__.py          # 📋 Configuration module public API
│   └── cli_config.py        # 📋 CLI configuration models
```

**Responsibility**: Provide configuration management and utility functions.

**Configuration Pattern**:

```python
from flext_core import FlextBaseSettings
from typing import Optional

class CLISettings(FlextBaseSettings):
    """CLI configuration with environment variable support"""
    profile: str = "default"
    debug: bool = False
    output_format: str = "table"
    log_level: str = "INFO"

    # Service endpoints
    flexcore_url: str = "http://localhost:8080"
    flext_service_url: str = "http://localhost:8081"

    class Config:
        env_prefix = "FLEXT_CLI_"
        env_file = ".env"

class CLIConfig(FlextBaseSettings):
    """Hierarchical CLI configuration"""
    auth: AuthConfig = field(default_factory=AuthConfig)
    services: ServiceConfig = field(default_factory=ServiceConfig)
    output: OutputConfig = field(default_factory=OutputConfig)

    class Config:
        env_nested_delimiter = "__"
```

### **External Integration Layer**

```python
# Service clients and external API integration
├── clients/                 # 🌐 External service clients (planned)
│   ├── __init__.py         # 🌐 Clients public API
│   ├── flexcore_client.py  # 🌐 FlexCore service client (Sprint 1)
│   ├── flext_service_client.py  # 🌐 FLEXT Service client (Sprint 1)
│   ├── singer_client.py    # 🌐 Singer ecosystem client (Sprint 3)
│   └── meltano_client.py   # 🌐 Meltano integration client (Sprint 6)
├── client.py               # 🌐 Legacy HTTP client (to be refactored)
└── types.py                # 🔷 Type definitions and CLI types
```

**Responsibility**: Manage integration with external FLEXT ecosystem services.

**Service Client Pattern**:

```python
from flext_core import FlextResult
import httpx

class FlexCoreClient:
    """Client for FlexCore service integration"""

    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(base_url=base_url, timeout=30.0)

    async def health_check(self) -> FlextResult[ServiceHealth]:
        """Check FlexCore service health"""
        try:
            response = await self.client.get("/health")
            if response.status_code == 200:
                data = response.json()
                health = ServiceHealth.from_response(data)
                return FlextResult.ok(health)
            else:
                return FlextResult.fail(f"Health check failed: {response.status_code}")
        except httpx.TimeoutException:
            return FlextResult.fail("Service timeout")
        except httpx.ConnectError:
            return FlextResult.fail("Cannot connect to FlexCore")
        except Exception as e:
            return FlextResult.fail(f"Health check error: {e}")
```

---

## 🎯 **Semantic Naming Conventions**

### **CLI-Specific Naming Patterns**

Following flext-core conventions while adding CLI-specific semantics:

```python
# Core CLI entities (inherit from flext-core)
CLICommand                  # Domain entity for command execution
CLISession                  # Domain entity for session management
CLIPlugin                   # Domain entity for plugin management
CLIConfig                   # Configuration value object

# CLI services (follow FlextDomainService pattern)
CLICommandService          # Domain service for command operations
AuthService                # Authentication service
ConfigService              # Configuration management service

# CLI context objects (value objects)
CLIContext                 # Command execution context
CLIResult                  # CLI-specific result wrapper
CLISettings               # Settings configuration

# Command handlers (CQRS pattern)
ExecuteCLICommandHandler   # Command handler for CLI execution
StartPipelineHandler       # Command handler for pipeline operations
```

**Rationale**: Consistent with flext-core patterns while clearly identifying CLI-specific components.

### **Module-Level Naming**

```python
# Command modules are verb-oriented
auth.py                    # Authentication commands (login, logout, status)
config.py                  # Configuration commands (get, set, show, reset)
debug.py                   # Debug commands (info, health, logs, validate)
pipeline.py                # Pipeline commands (list, start, stop, status)
service.py                 # Service commands (health, status, logs)

# Domain modules are noun-oriented
entities.py                # Domain entities (CLICommand, CLISession)
cli_context.py            # Context and value objects
cli_services.py           # Domain services and business logic

# Utility modules are function-oriented
formatters.py             # Output formatting functions
helpers.py                # Helper and utility functions
decorators.py             # Decorator patterns and cross-cutting concerns
```

**Pattern**: Commands are action-oriented, domain modules are entity-oriented, utilities are function-oriented.

### **Internal Naming (\_xxx)**

```python
# Internal CLI implementation details
_command_executor.py       # Internal command execution logic
_result_formatters.py      # Internal result formatting implementation
_container_setup.py        # Internal container setup logic

# Internal functions and classes
def _validate_command_args(args: dict) -> bool:
    """Internal command argument validation"""

class _CLIExecutionContext:
    """Internal execution context implementation"""
```

**Rule**: Anything with `_` prefix is internal implementation and not part of public CLI API.

---

## 📦 **Import Patterns & Best Practices**

### **Recommended Import Styles**

#### **1. Primary Pattern (Recommended for CLI Usage)**

```python
# Import from main CLI package
from flext_cli import setup_cli, CLISettings
from flext_cli.cli import cli

# Combined with flext-core patterns
from flext_core import FlextResult, FlextContainer
from flext_cli.domain.entities import CLICommand

# CLI command implementation
def create_pipeline_command() -> FlextResult[CLICommand]:
    return FlextResult.ok(CLICommand(
        name="create-pipeline",
        command_line="flext pipeline create",
        command_type=CommandType.SYSTEM
    ))
```

#### **2. Specific Module Pattern (For Command Development)**

```python
# Import from specific command modules
from flext_cli.commands.auth import auth
from flext_cli.commands.pipeline import pipeline
from flext_cli.commands.service import service

# Import CLI utilities
from flext_cli.core.decorators import handle_service_result
from flext_cli.core.formatters import format_table_output
from flext_cli.utils.output import print_success, print_error
```

#### **3. Client Integration Pattern**

```python
# Import service clients for ecosystem integration
from flext_cli.clients.flexcore_client import FlexCoreClient
from flext_cli.clients.flext_service_client import FlextServiceClient

# Use with dependency injection
async def check_ecosystem_health(container: FlextContainer) -> FlextResult[SystemHealth]:
    flexcore_client = container.get_typed(FlexCoreClient).unwrap()
    return await flexcore_client.health_check()
```

### **Anti-Patterns (Forbidden)**

```python
# ❌ Don't import everything
from flext_cli import *

# ❌ Don't import internal modules
from flext_cli._command_executor import _execute_internal

# ❌ Don't break layer boundaries
from flext_cli.infrastructure.container import _internal_setup

# ❌ Don't alias core CLI components
from flext_cli.cli import cli as main_cli  # Confusing across ecosystem
```

---

## 🏛️ **Architectural Patterns**

### **Layer Separation**

```python
# CLI-specific layer architecture
┌─────────────────────────────────────┐
│        CLI Presentation Layer       │  # cli.py, commands/*.py
│   (Click Commands, Rich Output)     │
├─────────────────────────────────────┤
│        Application Layer            │  # application/commands.py
│     (Command Handlers, CQRS)        │  # (handles CLI operations)
├─────────────────────────────────────┤
│          Domain Layer               │  # domain/entities.py
│  (CLI Entities, Business Logic)     │  # domain/cli_services.py
├─────────────────────────────────────┤
│       Infrastructure Layer          │  # infrastructure/container.py
│  (DI Container, External Clients)   │  # clients/*.py
├─────────────────────────────────────┤
│      flext-core Foundation          │  # FlextResult, FlextEntity
│   (Railway Pattern, DDD Patterns)   │  # FlextContainer, FlextCommand
└─────────────────────────────────────┘
```

### **Command Execution Flow**

```python
# CLI command execution with proper layer separation
┌─────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Click       │    │ Command         │    │ Domain          │
│ Command     │───▶│ Handler         │───▶│ Service         │
│ (CLI)       │    │ (Application)   │    │ (Business)      │
└─────────────┘    └─────────────────┘    └─────────────────┘
        │                   │                       │
        ▼                   ▼                       ▼
┌─────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Rich        │    │ FlextResult     │    │ External        │
│ Output      │◀───│ Error Handling  │◀───│ Service Client  │
│ (UI)        │    │ (Railway)       │    │ (Infrastructure)│
└─────────────┘    └─────────────────┘    └─────────────────┘
```

### **Cross-Cutting Concerns**

```python
# CLI cross-cutting concerns via decorators and mixins
from flext_cli.core.decorators import (
    handle_service_result,
    with_rich_console,
    with_correlation_id,
    with_performance_metrics
)

@click.command()
@with_correlation_id
@with_performance_metrics("pipeline.start")
@handle_service_result
@with_rich_console
async def start_pipeline(ctx: click.Context, pipeline_name: str):
    """Start pipeline with full observability"""
    console: Console = ctx.obj["console"]

    result = await pipeline_service.start_pipeline(pipeline_name)
    if result.success:
        console.print(f"[green]✅ Pipeline started: {pipeline_name}[/green]")
    # Error handling automatically handled by decorators
```

---

## 🔄 **CLI-Specific Patterns**

### **Command Definition Patterns**

```python
# Standard CLI command structure
import click
from rich.console import Console
from flext_cli.core.base import handle_service_result

@click.group()
def command_group():
    """Command group with consistent help format."""
    pass

@command_group.command()
@click.option('--format', '-f',
              type=click.Choice(['table', 'json', 'yaml']),
              default='table',
              help='Output format')
@click.option('--verbose', '-v',
              is_flag=True,
              help='Verbose output')
@click.argument('resource_name', required=False)
@click.pass_context
@handle_service_result
async def list_resources(ctx: click.Context, format: str, verbose: bool, resource_name: str):
    """List resources with optional filtering."""
    console: Console = ctx.obj["console"]
    config = ctx.obj["config"]

    # Use domain service with proper error handling
    result = await resource_service.list_resources(
        filter_name=resource_name,
        verbose=verbose
    )

    if result.success:
        resources = result.unwrap()
        output = format_output(resources, format)
        console.print(output)
```

### **Context Management Patterns**

```python
from dataclasses import dataclass
from rich.console import Console
from flext_cli.utils.config import CLIConfig

@dataclass
class CLIContext:
    """CLI execution context with all necessary components"""
    console: Console
    config: CLIConfig
    container: FlextContainer
    correlation_id: str

# Context setup in main CLI
@click.group()
@click.option('--profile', default='default', help='Configuration profile')
@click.option('--debug', is_flag=True, help='Enable debug mode')
@click.pass_context
def cli(ctx: click.Context, profile: str, debug: bool):
    """FLEXT CLI with context setup."""
    # Setup CLI context
    console = Console()
    config = CLIConfig(profile=profile, debug=debug)
    container = setup_cli_container()

    ctx.obj = CLIContext(
        console=console,
        config=config,
        container=container,
        correlation_id=generate_correlation_id()
    )
```

### **Output Formatting Patterns**

```python
from rich.table import Table
from rich.panel import Panel
from rich.progress import track

def format_service_health(services: List[ServiceHealth]) -> Table:
    """Format service health as Rich table"""
    table = Table(title="FLEXT Service Health")
    table.add_column("Service", style="cyan")
    table.add_column("Status", style="bold")
    table.add_column("Response Time", style="green")
    table.add_column("Version", style="blue")

    for service in services:
        status_color = "green" if service.status == "healthy" else "red"
        table.add_row(
            service.name,
            f"[{status_color}]{service.status}[/{status_color}]",
            f"{service.response_time_ms:.1f}ms",
            service.version
        )

    return table

def format_command_result(result: FlextResult[Any], format: str) -> str:
    """Format command result based on output format"""
    if format == "json":
        return json.dumps(result.data, indent=2)
    elif format == "yaml":
        return yaml.dump(result.data, default_flow_style=False)
    elif format == "table":
        return format_as_table(result.data)
    else:
        return str(result.data)
```

---

## 🧪 **CLI Testing Patterns**

### **Test Organization**

```python
# Test structure mirrors CLI command structure
tests/
├── unit/                    # Unit tests (isolated)
│   ├── commands/           # Command-specific unit tests
│   │   ├── test_auth_commands.py
│   │   ├── test_config_commands.py
│   │   └── test_debug_commands.py
│   ├── domain/             # Domain logic tests
│   │   ├── test_entities.py
│   │   └── test_services.py
│   ├── core/               # Core utility tests
│   │   ├── test_decorators.py
│   │   └── test_formatters.py
│   └── utils/              # Utility function tests
├── integration/             # Integration tests
│   ├── test_cli_integration.py
│   ├── test_service_clients.py
│   └── test_container_setup.py
├── e2e/                     # End-to-end CLI tests
│   ├── test_cli_workflows.py
│   └── test_ecosystem_integration.py
└── conftest.py              # Test configuration and fixtures
```

### **CLI Command Testing Patterns**

```python
import pytest
from click.testing import CliRunner
from flext_cli.cli import cli

def test_auth_login_success():
    """Test successful authentication"""
    runner = CliRunner()
    result = runner.invoke(cli, ['auth', 'login', '--username', 'testuser'])

    assert result.exit_code == 0
    assert "Login successful" in result.output
    assert "testuser" in result.output

def test_auth_login_failure():
    """Test authentication failure"""
    runner = CliRunner()
    result = runner.invoke(cli, ['auth', 'login', '--username', 'invalid'])

    assert result.exit_code == 1
    assert "Authentication failed" in result.output

@pytest.mark.asyncio
async def test_pipeline_start_command():
    """Test pipeline start command with mocked service"""
    runner = CliRunner()

    # Mock the service response
    with patch('flext_cli.commands.pipeline.pipeline_service') as mock_service:
        mock_service.start_pipeline.return_value = FlextResult.ok(
            PipelineStatus(name="test-pipeline", status="running")
        )

        result = runner.invoke(cli, ['pipeline', 'start', 'test-pipeline'])

        assert result.exit_code == 0
        assert "Pipeline started" in result.output
        mock_service.start_pipeline.assert_called_once_with("test-pipeline", "development")
```

### **Domain Entity Testing Patterns**

```python
import pytest
from flext_cli.domain.entities import CLICommand, CommandStatus

def test_cli_command_lifecycle():
    """Test CLI command execution lifecycle"""
    command = CLICommand(
        name="test-command",
        command_line="echo hello",
        command_type=CommandType.SYSTEM
    )

    # Initial state
    assert command.command_status == CommandStatus.PENDING
    assert command.started_at is None

    # Start execution
    result = command.start_execution()
    assert result.success
    assert command.command_status == CommandStatus.RUNNING
    assert command.started_at is not None

    # Complete execution
    result = command.complete_execution(exit_code=0, stdout="hello")
    assert result.success
    assert command.command_status == CommandStatus.COMPLETED
    assert command.successful
    assert command.stdout == "hello"

def test_cli_command_failure():
    """Test CLI command failure handling"""
    command = CLICommand(
        name="failing-command",
        command_line="false",  # Command that always fails
        command_type=CommandType.SYSTEM
    )

    command.start_execution()
    result = command.complete_execution(exit_code=1, stderr="Command failed")

    assert result.success  # Completion is successful even if command failed
    assert command.command_status == CommandStatus.FAILED
    assert not command.successful
    assert command.stderr == "Command failed"
```

### **Service Integration Testing Patterns**

```python
import pytest
from flext_cli.clients.flexcore_client import FlexCoreClient

@pytest.mark.integration
@pytest.mark.asyncio
async def test_flexcore_health_check():
    """Test FlexCore service integration"""
    client = FlexCoreClient()
    result = await client.health_check()

    if result.success:
        health = result.unwrap()
        assert health.service_name == "flexcore"
        assert health.status in ["healthy", "unhealthy"]
        assert health.response_time_ms > 0
    else:
        # If FlexCore is not running, should get connection error
        assert "connect" in result.error.lower()

@pytest.mark.integration
@pytest.mark.asyncio
async def test_cli_container_setup():
    """Test CLI dependency container setup"""
    from flext_cli.infrastructure.container import setup_cli_container

    container = setup_cli_container()

    # Test service resolution
    auth_service = container.get_typed(AuthService)
    assert auth_service.success

    config_service = container.get_typed(ConfigService)
    assert config_service.success
```

---

## 📏 **CLI Quality Standards**

### **Command Interface Standards**

```python
# ✅ Standard command interface pattern
@click.command()
@click.option('--format', '-f',
              type=click.Choice(['table', 'json', 'yaml', 'csv']),
              default='table',
              help='Output format')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
@click.option('--timeout', '-t', type=int, default=30, help='Timeout in seconds')
@click.argument('resource_name', required=False)
@click.pass_context
@handle_service_result
async def command_template(
    ctx: click.Context,
    format: str,
    verbose: bool,
    timeout: int,
    resource_name: Optional[str]
) -> FlextResult[Any]:
    """
    Command template with standard options and error handling.

    Args:
        resource_name: Optional resource identifier

    Examples:
        flext group command --format json
        flext group command resource-123 --verbose
    """
    console: Console = ctx.obj["console"]
    config: CLIConfig = ctx.obj["config"]

    # Implementation with proper error handling
    return FlextResult.ok(result)

# ❌ Missing standard options
@click.command()
def bad_command(name):  # No help, no error handling, no standard options
    print(f"Processing {name}")
```

### **Error Handling Standards**

```python
# ✅ Proper CLI error handling with Rich output
from flext_cli.core.decorators import handle_service_result

@handle_service_result
async def cli_operation() -> FlextResult[Any]:
    """CLI operation with proper error handling"""
    try:
        result = await external_service.perform_operation()
        if result.success:
            return result
        else:
            # Domain error - handled by decorator
            return result
    except httpx.TimeoutException:
        return FlextResult.fail("Service timeout - check network connection")
    except httpx.ConnectError:
        return FlextResult.fail("Cannot connect to service - is it running?")
    except Exception as e:
        return FlextResult.fail(f"Unexpected error: {e}")

# ❌ Poor error handling
def bad_cli_operation():
    try:
        result = service.operation()
        print(result)  # No proper output formatting
    except Exception as e:
        print(f"Error: {e}")  # No structured error handling
        sys.exit(1)  # Abrupt exit without cleanup
```

### **Documentation Standards**

```python
@click.command()
@click.option('--environment', '-e',
              type=click.Choice(['dev', 'staging', 'prod']),
              default='dev',
              help='Target environment for pipeline execution')
@click.argument('pipeline_name')
@click.pass_context
async def start_pipeline(ctx: click.Context, pipeline_name: str, environment: str):
    """
    Start a data pipeline in the specified environment.

    This command initiates pipeline execution and provides real-time status
    updates. The pipeline must be configured and available in the target
    environment before execution.

    Args:
        pipeline_name: Name of the pipeline to start (must exist in environment)

    Options:
        --environment: Target environment (dev/staging/prod)

    Examples:
        Start pipeline in development:
        $ flext pipeline start user-sync --environment dev

        Start pipeline in production:
        $ flext pipeline start analytics-etl --environment prod

    Exit Codes:
        0: Pipeline started successfully
        1: Pipeline start failed (see error message)
        2: Pipeline not found in environment
        3: Authentication/permission error
    """
    # Implementation
```

---

## 🌐 **Ecosystem Integration Guidelines**

### **Service Client Standards**

```python
# ✅ Standard service client implementation
from flext_core import FlextResult
from flext_cli.clients.base import BaseServiceClient

class FlexCoreClient(BaseServiceClient):
    """FlexCore service client following ecosystem patterns"""

    def __init__(self, base_url: str = "http://localhost:8080"):
        super().__init__(base_url, service_name="flexcore")

    async def health_check(self) -> FlextResult[ServiceHealth]:
        """Standard health check implementation"""
        return await self._make_request("GET", "/health")

    async def list_plugins(self) -> FlextResult[List[PluginInfo]]:
        """List installed plugins"""
        return await self._make_request("GET", "/api/v1/plugins")

    async def get_plugin_info(self, plugin_name: str) -> FlextResult[PluginInfo]:
        """Get specific plugin information"""
        return await self._make_request("GET", f"/api/v1/plugins/{plugin_name}")

# ❌ Non-standard client implementation
class BadServiceClient:
    def check_health(self):  # Inconsistent naming
        response = requests.get(self.url)  # No error handling
        return response.json()  # No FlextResult wrapper
```

### **Configuration Integration**

```python
# ✅ Extend flext-core configuration patterns
from flext_core import FlextBaseSettings

class FlexCoreClientConfig(FlextBaseSettings):
    """FlexCore client configuration"""
    url: str = "http://localhost:8080"
    timeout: int = 30
    retries: int = 3

    class Config:
        env_prefix = "FLEXCORE_"

class CLIEcosystemConfig(FlextBaseSettings):
    """Complete CLI ecosystem configuration"""
    flexcore: FlexCoreClientConfig = field(default_factory=FlexCoreClientConfig)
    flext_service: FlextServiceConfig = field(default_factory=FlextServiceConfig)
    auth: AuthConfig = field(default_factory=AuthConfig)
    output: OutputConfig = field(default_factory=OutputConfig)

    class Config:
        env_nested_delimiter = "__"

# Usage across CLI commands
settings = CLIEcosystemConfig()
flexcore_client = FlexCoreClient(settings.flexcore.url)
```

### **Domain Model Consistency**

```python
# ✅ Consistent domain models across ecosystem
from flext_core import FlextEntity

class CLICommand(FlextEntity):
    """CLI command entity following ecosystem patterns"""
    name: str
    command_line: str
    command_type: CommandType
    execution_context: ExecutionContext

    def to_ecosystem_format(self) -> dict[str, Any]:
        """Convert to standard ecosystem format"""
        return {
            "command_id": str(self.id),
            "name": self.name,
            "type": self.command_type.value,
            "status": self.command_status.value,
            "created_at": self.created_at.isoformat(),
            "context": self.execution_context.to_dict()
        }

    @classmethod
    def from_ecosystem_format(cls, data: dict[str, Any]) -> 'CLICommand':
        """Create from standard ecosystem format"""
        return cls(
            id=UUID(data["command_id"]),
            name=data["name"],
            command_type=CommandType(data["type"]),
            command_status=CommandStatus(data["status"])
        )
```

---

## 🔄 **Migration & Evolution Patterns**

### **CLI Version Management**

```python
# CLI version compatibility with ecosystem
CLI_VERSION = "0.9.0"
SUPPORTED_FLEXT_CORE_VERSIONS = ["0.9.x", "1.0.x"]
REQUIRED_ECOSYSTEM_SERVICES = {
    "flexcore": ">=1.0.0",
    "flext-service": ">=1.0.0",
    "flext-observability": ">=0.9.0"
}

def check_ecosystem_compatibility() -> FlextResult[CompatibilityReport]:
    """Check CLI compatibility with ecosystem services"""
    report = CompatibilityReport()

    for service, required_version in REQUIRED_ECOSYSTEM_SERVICES.items():
        service_version = get_service_version(service)
        compatible = check_version_compatibility(service_version, required_version)
        report.add_service(service, service_version, compatible)

    return FlextResult.ok(report)
```

### **Command Migration Patterns**

```python
# Deprecation pattern for CLI commands
@click.command(deprecated=True)
@click.pass_context
def old_command(ctx: click.Context):
    """
    DEPRECATED: Use 'flext new-command' instead.

    This command will be removed in version 2.0.0.
    """
    console: Console = ctx.obj["console"]
    console.print("[yellow]⚠️  Warning: This command is deprecated[/yellow]")
    console.print("[yellow]   Use 'flext new-command' instead[/yellow]")
    console.print("[yellow]   This command will be removed in version 2.0.0[/yellow]")

    # Delegate to new implementation
    ctx.invoke(new_command)
```

---

## 📋 **CLI Development Checklist**

### **New Command Checklist**

- [ ] **Command Structure**: Follows Click group/command pattern
- [ ] **Standard Options**: Includes --format, --verbose, --help
- [ ] **Error Handling**: Uses @handle_service_result decorator
- [ ] **Type Annotations**: Complete type hints for all parameters
- [ ] **Documentation**: Comprehensive docstring with examples
- [ ] **Rich Output**: Uses Rich console for beautiful output
- [ ] **Tests**: Unit tests with CliRunner and integration tests
- [ ] **Error Codes**: Standard exit codes (0=success, 1=error, etc.)
- [ ] **Configuration**: Respects CLI configuration and profiles
- [ ] **Ecosystem Integration**: Integrates with relevant FLEXT services

### **Quality Gate Checklist**

- [ ] **Linting**: `make lint` passes (Ruff with all rules)
- [ ] **Type Check**: `make type-check` passes (MyPy strict mode)
- [ ] **Tests**: `make test` passes (90% coverage minimum)
- [ ] **CLI Tests**: `make test-cli` passes (CLI-specific tests)
- [ ] **Integration**: Works with ecosystem services
- [ ] **Documentation**: Command help is comprehensive and accurate
- [ ] **UX**: Command provides good user experience with clear feedback
- [ ] **Performance**: Command responds within 1-3 seconds for basic operations

---

**Last Updated**: August 2, 2025  
**Target Audience**: FLEXT CLI developers and ecosystem contributors  
**Scope**: Python module organization for CLI integration with 32+ project ecosystem  
**Version**: 0.9.0 → 1.0.0 development guidelines
