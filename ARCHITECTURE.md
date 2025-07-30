# FLEXT CLI Architecture Documentation

**Version**: 0.8.0  
**Status**: Clean Architecture Refactoring  
**Foundation**: flext_core

This document describes the new semantic CLI architecture based on Clean Architecture principles and built on the flext_core foundation.

## 🏗️ Architecture Overview

The FLEXT CLI has been completely refactored to implement Clean Architecture patterns with semantic organization and strong separation of concerns.

### Architecture Layers

```
┌─────────────────────────────────────────────────────────────┐
│                        User Interface                       │
│  (Click CLI Framework, Rich Output, Terminal Interaction)   │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                      Adapter Layer                         │
│  ├── cli/           # Click framework integration          │
│  ├── output/        # Rich rendering adapters             │
│  ├── config/        # Configuration adapters              │
│  └── utils/         # Legacy compatibility utilities      │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer                       │
│  ├── services/      # Application services                │
│  ├── use_cases/     # Command handlers and queries        │
│  ├── ports/         # Infrastructure interfaces           │
│  └── dto/           # Data Transfer Objects               │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                      Domain Layer                          │
│  ├── entities/      # Domain entities (Command, Session)  │
│  ├── value_objects/ # Immutable value objects            │
│  ├── services/      # Domain services                     │
│  └── events/        # Domain events                       │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                 Infrastructure Layer                       │
│  ├── persistence/   # Repository implementations          │
│  ├── external/      # External service clients           │
│  └── dependency_injection/ # DI container               │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                     flext_core Foundation                  │
│  (Shared types, patterns, domain base classes, etc.)      │
└─────────────────────────────────────────────────────────────┘
```

## 📁 New Directory Structure

### Semantic Organization

```
src/flext_cli/
├── domain/                    # Pure business logic (Core Layer)
│   ├── entities/              # Domain entities with identity
│   │   ├── command.py         # Command aggregate root
│   │   ├── session.py         # CLI session entity
│   │   ├── configuration.py   # Configuration entity
│   │   ├── plugin.py          # Plugin entity
│   │   └── user.py           # User context entity
│   ├── value_objects/         # Immutable value objects
│   │   ├── cli_context.py     # CLI execution context
│   │   ├── output_format.py   # Output formatting options
│   │   ├── command_spec.py    # Command specification
│   │   └── auth_context.py    # Authentication context
│   ├── services/              # Domain services
│   └── events/                # Domain events
├── application/               # Application orchestration
│   ├── services/              # Application services
│   │   └── cli_service.py     # Main CLI application service
│   ├── use_cases/             # Command and query handlers
│   ├── ports/                 # Infrastructure interfaces
│   │   ├── command_repository.py  # Command persistence port
│   │   └── session_repository.py  # Session persistence port
│   └── dto/                   # Data Transfer Objects
├── adapters/                  # External interface adapters
│   ├── cli/                   # CLI framework integration
│   │   └── foundation.py      # New CLI foundation (replaces BaseCLI)
│   ├── output/                # Output rendering
│   │   └── renderers.py       # Rich and simple renderers
│   ├── config/                # Configuration management
│   └── utils/                 # Legacy compatibility utilities
├── infrastructure/            # Infrastructure implementations
│   ├── persistence/           # Repository implementations
│   ├── external/              # External service clients
│   └── dependency_injection/  # DI container
├── _deprecated.py             # Deprecation warnings and migration helpers
└── [legacy files with deprecation warnings]
```

## 🚀 Key Components

### 1. Domain Layer

#### Command Aggregate Root

```python
from flext_cli.domain.entities.command import Command, CommandContext, CommandResult

# Create and execute commands with rich domain logic
command = Command(
    name="pipeline-run",
    command_line="flext pipeline run my-pipeline",
    command_type=CommandType.PIPELINE,
    context=CommandContext(timeout_seconds=300.0)
)

# Domain-driven execution lifecycle
command.start_execution()
result = CommandResult(exit_code=0, stdout="Success", duration_seconds=1.5)
command.complete_execution(result)
```

#### CLI Context Value Object

```python
from flext_cli.domain.value_objects import CLIContext, OutputFormat

# Immutable context with builder pattern
context = CLIContext()
production_context = context.for_production()
debug_context = context.with_debug(True).with_output_format(OutputFormat.JSON)
```

### 2. Application Layer

#### CLI Application Service

```python
from flext_cli.application.services import CLIApplicationService

# Orchestrates domain entities and infrastructure
app_service = CLIApplicationService(
    command_repository=command_repo,
    session_repository=session_repo
)

# Type-safe service operations
session_result = await app_service.create_session(
    user_id=user_id,
    session_type=SessionType.INTERACTIVE
)

command_result = await app_service.execute_command(
    command_id=command_id,
    session_id=session_result.unwrap().id
)
```

### 3. Adapter Layer

#### New CLI Foundation

```python
from flext_cli.adapters.cli.foundation import CLIFoundation
from flext_cli.application.services import CLIApplicationService

class MyApp(CLIFoundation):
    def register_commands(self, cli_group: click.Group) -> None:
        """Register application-specific commands."""

        @cli_group.command()
        @self.create_command_decorator()
        @handle_service_result
        def my_command(cli_context: CLIContext, app_service: CLIApplicationService):
            """Example command with full integration."""
            return app_service.execute_command(...)

# Usage
app = MyApp(
    name="my-cli",
    version="1.0.0",
    description="My CLI application",
    app_service=app_service
)

cli = app.create_cli()
```

#### Rich Output Rendering

```python
from flext_cli.adapters.output import RichRenderer

renderer = RichRenderer(console=Console())
renderer.render_data(data, context)
renderer.render_table(tabular_data, title="Results", context=context)
renderer.render_success("Operation completed successfully")
```

## 🔄 Migration Guide

### Old vs New Patterns

#### Legacy Pattern (Deprecated)

```python
# OLD - Will show deprecation warnings
from flext_cli import BaseCLI, CLIResultRenderer

class OldApp(BaseCLI):
    def __init__(self):
        super().__init__("app", "1.0.0", "My app")
```

#### New Pattern (Recommended)

```python
# NEW - Clean Architecture
from flext_cli.adapters.cli.foundation import CLIFoundation
from flext_cli.application.services import CLIApplicationService

class NewApp(CLIFoundation):
    def __init__(self, app_service: CLIApplicationService):
        super().__init__(
            name="app",
            version="1.0.0",
            description="My app",
            app_service=app_service
        )
```

### Import Migration

```python
# OLD (deprecated, but still works with warnings)
from flext_cli import BaseCLI, CLICommand, CLIResultRenderer

# NEW (recommended)
from flext_cli.adapters.cli.foundation import CLIFoundation
from flext_cli.domain.entities.command import Command
from flext_cli.adapters.output import CLIRenderer
```

## 🎯 Semantic Benefits

### 1. Clear Responsibility Separation

- **Domain**: Pure business logic with no external dependencies
- **Application**: Orchestration and use case coordination
- **Adapters**: Framework integration and external interfaces
- **Infrastructure**: Concrete implementations and external systems

### 2. Semantic Navigation

- **Quick Location**: `entities/command.py` for command logic
- **Easy Extension**: Add new adapters without touching core logic
- **Clear Dependencies**: Dependency flows from outer to inner layers

### 3. Type Safety and Quality

- **100% MyPy compliance** with modern Python 3.13 typing
- **FlextResult pattern** for type-safe error handling
- **Immutable value objects** prevent state mutation bugs
- **Domain events** for loose coupling between aggregates

### 4. Testing Strategy

```python
# Domain layer - Pure unit tests (fast)
def test_command_execution():
    command = Command(name="test", command_line="echo hello")
    result = CommandResult(exit_code=0, stdout="hello", duration_seconds=0.1)

    command.start_execution()
    assert command.is_running

    command.complete_execution(result)
    assert command.is_successful

# Application layer - Service tests with mocked repositories
async def test_cli_service():
    app_service = CLIApplicationService(
        command_repository=MockCommandRepository(),
        session_repository=MockSessionRepository()
    )

    result = await app_service.execute_command(command_id)
    assert result.is_success

# Adapter layer - Integration tests with real frameworks
def test_cli_foundation():
    app = TestApp(app_service=mock_service)
    cli = app.create_cli()

    runner = CliRunner()
    result = runner.invoke(cli, ['test-command'])
    assert result.exit_code == 0
```

## 🔧 Extension Points

### 1. Adding New Entities

```python
# Create new domain entity
class Pipeline(DomainAggregateRoot, TimestampMixin):
    name: NonEmptyStr
    steps: list[PipelineStep]

    def execute(self) -> FlextResult[PipelineResult]:
        # Domain logic here
        pass
```

### 2. Adding New Adapters

```python
# Create new output adapter
class SlackRenderer(CLIRenderer):
    def render_success(self, message: str, context: CLIContext) -> None:
        # Send to Slack webhook
        pass
```

### 3. Adding New Use Cases

```python
# Create new application service method
class CLIApplicationService:
    async def bulk_execute_commands(
        self,
        commands: list[EntityId],
        parallel: bool = False
    ) -> FlextResult[list[CommandResult]]:
        # Orchestration logic here
        pass
```

## 📊 Quality Standards

### Mandatory Quality Gates

- **Zero lint violations** (Ruff with all rules enabled)
- **Zero type errors** (MyPy strict mode)
- **100% test coverage** for domain layer
- **Integration tests** for all adapters
- **Performance benchmarks** for CLI responsiveness

### Architecture Compliance

- **No domain dependencies** on outer layers
- **Interface segregation** with focused protocols
- **Single responsibility** for each component
- **Composition over inheritance** throughout

## 🔮 Future Enhancements

### Planned Architecture Extensions

1. **Event Sourcing**: Store domain events for audit trails
2. **CQRS**: Separate command and query models for scalability
3. **Plugin Architecture**: Load commands dynamically from plugins
4. **Distributed Tracing**: OpenTelemetry integration for observability
5. **Configuration Validation**: JSON Schema validation for CLI configs

This architecture provides a solid foundation for CLI applications that can scale from simple scripts to enterprise-grade command-line tools while maintaining code quality, testability, and maintainability.
