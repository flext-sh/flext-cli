# Architecture Overview

## Introduction

FLEXT CLI implementa Clean Architecture com Domain-Driven Design (DDD), utilizando flext-core como biblioteca base. Esta arquitetura garante separação clara de responsabilidades, testabilidade e manutenibilidade.

## Architectural Layers

### 🏗️ Clean Architecture Structure

```
src/flext_cli/
├── domain/                    # 🎯 Core Business Logic (Innermost Layer)
│   ├── entities.py           # Entidades de domínio
│   ├── cli_context.py        # Value objects e contexto
│   └── cli_services.py       # Serviços de domínio
├── application/               # 🔄 Application Orchestration Layer
│   └── commands.py           # Command handlers
├── infrastructure/            # 🔧 Infrastructure Layer (Outermost)
│   ├── container.py          # Dependency injection container
│   └── config.py             # Configuration management
├── commands/                  # 🎮 CLI Command Implementations
│   ├── auth.py              # Authentication commands
│   ├── config.py            # Configuration commands
│   ├── debug.py             # Debug and diagnostic commands
│   ├── pipeline.py          # Pipeline management commands
│   ├── plugin.py            # Plugin management commands
│   └── projects/            # Project-specific commands
├── core/                     # ⚙️ Core CLI Utilities
│   ├── base.py              # Base CLI patterns
│   ├── decorators.py        # CLI decorators
│   ├── formatters.py        # Output formatting
│   ├── helpers.py           # Helper functions
│   └── types.py             # Click parameter types
├── config/                   # 📋 Configuration Management
├── utils/                    # 🛠️ Utility Modules
├── api.py                    # 🌐 API client interface
├── cli.py                   # 🎯 Main CLI entry point
└── client.py                # 📡 HTTP client for FLEXT services
```

## Key Architectural Principles

### 1. Dependency Inversion

```python
# Dependencies flow from outer to inner layers
from flext_core import ServiceResult  # Core dependency
from flext_cli.domain.entities import CLICommand  # Domain entity
```

### 2. Single Responsibility

Each module has one clear purpose:

- `domain/entities.py`: Define domain entities
- `commands/auth.py`: Handle authentication commands
- `infrastructure/container.py`: Manage dependency injection

### 3. Interface Segregation

```python
# Focused protocols and interfaces
from flext_cli.domain.interfaces import CLICommandRepository
```

### 4. Clean Separation

Domain logic isolated from framework concerns:

```python
# Domain entity (no framework dependencies)
class CLICommand(DomainEntity):
    def start_execution(self) -> None:
        self.command_status = CommandStatus.RUNNING

# CLI command (framework specific)
@click.command()
def run_command():
    pass
```

## flext-core Integration

### Domain Entities

```python
from flext_core.domain.pydantic_base import DomainEntity

class CLICommand(DomainEntity):
    """CLI command using flext-core patterns."""
    name: str = Field(...)
    command_status: CommandStatus = Field(default=CommandStatus.PENDING)
```

### Service Result Pattern

```python
from flext_core.domain.types import ServiceResult

def setup_cli(settings: CLISettings) -> ServiceResult[bool]:
    try:
        # Setup logic
        return ServiceResult.ok(True)
    except Exception as e:
        return ServiceResult.fail(f"Setup failed: {e}")
```

### Dependency Injection

```python
from flext_core.config.base import get_container

container = get_container()
service_container = CLIServiceContainer(name="flext-cli", version="0.8.0")
container.register(CLIServiceContainer, service_container)
```

## Command Structure

### Click Framework Integration

```python
@click.group()
@click.option('--profile', default='default')
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']))
@click.option('--debug/--no-debug', default=False)
def cli(profile: str, output: str, debug: bool) -> None:
    """FLEXT Command Line Interface."""
```

### Rich UI Components

```python
from rich.console import Console
from rich.table import Table

console = Console()
table = Table(title="Pipeline Status")
table.add_column("Name", style="cyan")
table.add_column("Status", style="green")
console.print(table)
```

## Design Patterns

### 1. Command Pattern

CLI commands encapsulate operations:

```python
class CLICommand(DomainEntity):
    def execute(self) -> ServiceResult[Any]:
        # Command execution logic
        pass
```

### 2. Factory Pattern

Command creation:

```python
def create_cli_command(name: str, command_line: str) -> CLICommand:
    return CLICommand(
        name=name,
        command_line=command_line,
        command_type=CommandType.SYSTEM
    )
```

### 3. Strategy Pattern

Output formatting:

```python
class OutputFormatter(ABC):
    @abstractmethod
    def format(self, data: Any) -> str:
        pass

class JSONFormatter(OutputFormatter):
    def format(self, data: Any) -> str:
        return json.dumps(data, indent=2)
```

## Testing Architecture

### Layer Testing Strategy

1. **Domain Layer**: Unit tests for entities and business logic
2. **Application Layer**: Service tests with mocked dependencies
3. **Infrastructure Layer**: Integration tests
4. **CLI Layer**: End-to-end tests with CliRunner

### Test Structure

```
tests/
├── unit/                    # Fast unit tests
│   ├── test_domain.py
│   └── test_services.py
├── integration/             # Integration tests
│   ├── test_cli_commands.py
│   └── test_config.py
└── e2e/                    # End-to-end tests
    └── test_full_workflow.py
```

## Quality Assurance

### Static Analysis

- **MyPy**: Strict type checking (zero errors tolerated)
- **Ruff**: Comprehensive linting (ALL rules enabled)
- **Bandit**: Security scanning
- **pip-audit**: Dependency vulnerability scanning

### Coverage Requirements

- **Minimum**: 90% test coverage
- **Domain Layer**: 95%+ coverage
- **Critical Paths**: 100% coverage

### Pre-commit Hooks

```yaml
repos:
  - repo: local
    hooks:
      - id: ruff-check
        name: ruff-check
        entry: poetry run ruff check
      - id: mypy
        name: mypy
        entry: poetry run mypy
      - id: pytest
        name: pytest
        entry: poetry run pytest
```

## Performance Considerations

### Lazy Loading

```python
# Commands are loaded on-demand
@click.group()
def cli():
    pass

# Add commands dynamically
cli.add_command(auth.auth)
cli.add_command(pipeline.pipeline)
```

### Efficient Output

```python
# Use Rich for efficient terminal output
from rich.progress import track

for item in track(items, description="Processing..."):
    process_item(item)
```

## Future Architecture Considerations

### Extensibility

- Plugin system for custom commands
- Configuration providers
- Output formatters

### Scalability

- Async command execution
- Parallel processing
- Caching strategies

---

**Next**: [Clean Architecture Implementation](clean-architecture.md) | **Previous**: [Documentation Home](../README.md)
