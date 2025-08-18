# FLEXT CLI Examples - Practical Usage Demonstrations

**Directory**: `examples/`  
**Architecture Layer**: Examples (All Layer Demonstrations)  
**Status**: 75% implemented - Comprehensive examples covering core patterns  
**Sprint Alignment**: Examples evolve with Sprints 1-10 implementation roadmap

## 🎯 Examples Overview

This directory contains practical examples demonstrating FLEXT CLI usage across all architectural layers, showcasing enterprise-grade CLI development patterns with Clean Architecture, Domain-Driven Design, and flext-core integration.

### **Example Categories**

- **Foundation Examples**: Core library patterns and basic usage
- **Architecture Examples**: Clean Architecture layer demonstrations
- **Integration Examples**: Real-world CLI application patterns
- **Advanced Examples**: Enterprise patterns and complex workflows
- **Sprint Examples**: Implementation examples following the 10-sprint roadmap

### **Key Technologies Demonstrated**

- **flext-core Foundation**: FlextResult, FlextEntity, FlextContainer patterns
- **Clean Architecture**: Domain, Application, Infrastructure, Commands layer separation
- **Click Integration**: Enhanced CLI framework with Rich terminal UI
- **Domain-Driven Design**: CLI-specific entities, value objects, domain services
- **CQRS Patterns**: Command Query Responsibility Segregation (Sprint 2-3)
- **Enterprise Patterns**: Configuration, validation, error handling, monitoring

## 📋 Example Catalog

### ✅ **Foundation Examples** (Implemented)

#### **1. Basic CLI Usage** (`01_basic_cli_usage.py`)

**Architecture Layer**: All layers introduction  
**Sprint Alignment**: Foundation for all sprints

**Purpose**: Introduction to FLEXT CLI core patterns and setup

**Features Demonstrated**:

- Configuration management with `CLIConfig` and `CLISettings`
- CLI context creation and execution management
- Helper utilities for validation and formatting
- FlextResult pattern integration throughout
- Basic CLI setup and initialization patterns

**Key Concepts**:

```python
# Configuration management
config = flext_cli.get_config()
settings = flext_cli.get_settings()

# Context creation
context = flext_cli.CLIContext(profile="development")

# Helper utilities
helper = flext_cli.CLIHelper()
result = helper.validate_email("user@example.com")

# Service result handling
@flext_cli.handle_service_result
def operation() -> FlextResult[str]:
    return FlextResult.ok("Success")
```

**Run**: `python examples/01_basic_cli_usage.py`

#### **2. Click Integration** (`02_click_integration.py`)

**Architecture Layer**: Commands/Presentation layer  
**Sprint Alignment**: Foundation + Sprint 6-7 advanced features

**Purpose**: Complete Click-based CLI application with FLEXT CLI enhancements

**Features Demonstrated**:

- Full Click command group with FLEXT CLI parameter types
- Enhanced decorators (time measurement, confirmation, spinners)
- Async command support with proper error handling
- Retry mechanisms for unreliable operations
- Path validation with custom Click types
- Configuration-aware command execution

**Key Concepts**:

```python
import click
import flext_cli

@click.group()
def cli():
    """FLEXT CLI Example Application."""
    pass

@cli.command()
@click.option("--count", type=flext_cli.PositiveInt)
@click.option("--url", type=flext_cli.URL)
@flext_cli.measure_time(show_in_output=True)
@flext_cli.with_spinner("Processing...")
@flext_cli.retry(max_attempts=3, delay=1.0)
def process(count: int, url: str):
    """Process data with enhanced CLI features."""
    pass
```

**Run**:

```bash
python examples/02_click_integration.py --help
python examples/02_click_integration.py process --count 5 --url https://api.example.com
```

#### **3. Domain Entities** (`03_domain_entities.py`)

**Architecture Layer**: Domain layer  
**Sprint Alignment**: Foundation + Sprint 2-3 domain events

**Purpose**: Demonstrate CLI domain modeling with FLEXT CLI entities

**Features Demonstrated**:

- CLI command lifecycle management with status tracking
- CLI session tracking with command history
- CLI plugin management with dependencies
- Domain events for CLI operations (Sprint 2-3)
- Business rule validation with FlextResult patterns
- Domain-driven design patterns in CLI context

**Key Concepts**:

```python
# Command lifecycle
command = flext_cli.CLICommand(
    name="deploy",
    command_line="kubectl apply -f app.yaml",
    command_type=flext_cli.CommandType.SYSTEM
)

# Start execution
running_command = command.start_execution()
assert running_command.command_status == CommandStatus.RUNNING

# Complete execution
completed = running_command.complete_execution(exit_code=0, stdout="Success")
assert completed.successful

# Session management
session = flext_cli.CLISession(session_id="session-123")
session.add_command(command.id)

# Plugin management
plugin = flext_cli.CLIPlugin(
    name="k8s-plugin",
    entry_point="k8s.main",
    commands=["deploy", "scale"]
)
```

**Run**: `python examples/03_domain_entities.py`

### ✅ **Application Examples** (Implemented)

#### **CLI App Structure** (`cli_app/`)

**Architecture Layer**: Complete application architecture  
**Sprint Alignment**: Sprints 1-10 implementation roadmap

**Purpose**: Complete CLI application demonstrating Clean Architecture

**Structure**:

```
cli_app/
├── cli.py                      # Main CLI entry point
├── application/
│   ├── __init__.py
│   └── commands.py             # Application layer command handlers
└── commands/                   # Command implementations
    ├── __init__.py
    ├── auth.py                 # Authentication commands
    ├── config.py               # Configuration commands
    ├── debug.py                # Debug commands
    ├── pipeline.py             # Pipeline commands (Sprint 1)
    ├── plugin.py               # Plugin commands (Sprint 6)
    └── projects/               # Project-specific commands
        ├── __init__.py
        ├── client-a.py            # client-a project commands (Sprint 9)
        ├── client-b.py         # client-b project commands (Sprint 9)
        └── meltano.py          # Meltano integration commands (Sprint 6)
```

**Features Demonstrated**:

- Complete CLI application architecture
- Command organization by domain/feature
- Application layer service coordination
- Project-specific command groups
- Sprint-based implementation progression

**Run**:

```bash
python examples/cli_app/cli.py --help
python examples/cli_app/cli.py auth login --username REDACTED_LDAP_BIND_PASSWORD
python examples/cli_app/cli.py pipeline list
```

### 📋 **Planned Examples** (Sprint Roadmap)

#### **Sprint 1: Infrastructure Examples** (PLANNED)

- **FlextContainer Integration**: Dependency injection examples
- **Service Client Examples**: FlexCore and FLEXT Service integration
- **Repository Examples**: Data persistence patterns

#### **Sprint 2-3: CQRS Examples** (PLANNED)

- **Command Handler Examples**: CQRS command processing
- **Query Handler Examples**: Read-only operations
- **Event Handler Examples**: Domain event processing

#### **Sprint 5: Data Pipeline Examples** (PLANNED)

- **Singer Tap Examples**: Data extraction patterns
- **DBT Integration Examples**: Data transformation workflows
- **Meltano Orchestration Examples**: Complete pipeline management

#### **Sprint 6: Plugin System Examples** (PLANNED)

- **Plugin Development**: Creating CLI plugins
- **Plugin Discovery**: Dynamic plugin loading
- **Plugin Integration**: Cross-plugin communication

#### **Sprint 7: Monitoring Examples** (PLANNED)

- **Observability Integration**: Metrics and monitoring
- **Performance Monitoring**: CLI performance tracking
- **Health Check Examples**: Service health monitoring

## 🚀 Usage Patterns

### **Configuration Management**

```python
# Environment-specific configuration
config = flext_cli.get_config()
config.profile = "production"
config.debug = False

# Settings with validation
settings = flext_cli.CLISettings(
    api_url="https://api.production.com",
    timeout=30,
    max_retries=3
)

# Context creation
context = flext_cli.CLIContext(
    profile="production",
    output_format="json",
    debug=False
)
```

### **Click Parameter Types**

```python
@click.command()
@click.option("--count", type=flext_cli.PositiveInt)
@click.option("--url", type=flext_cli.URL)
@click.option("--input-file", type=flext_cli.ExistingFile)
@click.option("--output-dir", type=flext_cli.ExistingDir)
@click.option("--new-file", type=flext_cli.NewFile)
def command(count, url, input_file, output_dir, new_file):
    """Command with validated parameters."""
    pass
```

### **CLI Decorators**

```python
@flext_cli.measure_time(show_in_output=True)
@flext_cli.confirm_action("Are you sure you want to proceed?")
@flext_cli.with_spinner("Processing data...")
@flext_cli.retry(max_attempts=3, delay=1.0, backoff=2.0)
@flext_cli.require_auth(roles=["REDACTED_LDAP_BIND_PASSWORD"])
@flext_cli.validate_config(required_keys=["api_url"])
@flext_cli.async_command
@flext_cli.handle_service_result
async def advanced_command():
    """Command with full decorator stack."""
    # Implementation using FlextResult patterns
    return FlextResult.ok("Operation completed successfully")
```

### **Helper Utilities**

```python
helper = flext_cli.CLIHelper()

# Validation utilities
url_result = helper.validate_url("https://api.example.com")
email_result = helper.validate_email("user@example.com")
path_result = helper.validate_path("/path/to/file")

# Formatting utilities
size_str = helper.format_size(1024 * 1024)  # "1.0 MB"
truncated = helper.truncate_text("Long text...", max_length=20)
safe_name = helper.sanitize_filename("unsafe/filename")

# User interaction
confirmed = helper.confirm("Continue with operation?")
value = helper.prompt("Enter configuration value:")

# Output formatting
helper.print_success("✅ Operation completed successfully")
helper.print_error("❌ Operation failed")
helper.print_warning("⚠️ Warning: Check configuration")
helper.print_info("ℹ️ Information: Process starting")
```

### **Domain Entity Patterns**

```python
# Command lifecycle management
command = flext_cli.CLICommand(
    name="deploy-service",
    command_line="docker deploy service:latest",
    command_type=flext_cli.CommandType.SYSTEM,
    timeout=300
)

# Domain validation
validation_result = command.validate_domain_rules()
if not validation_result.success:
    print(f"Validation failed: {validation_result.error}")

# Execution with tracking
running = command.start_execution()
# ... perform actual execution ...
completed = running.complete_execution(
    exit_code=0,
    stdout="Deployment successful",
    stderr="",
    execution_time=45.2
)

# Session tracking
session = flext_cli.CLISession(
    session_id="deploy-session-001",
    user_id="REDACTED_LDAP_BIND_PASSWORD",
    profile="production"
)
session.add_command(command.id)
session.add_context("environment", "production")
```

## 🏗️ Architecture Demonstration

### **Clean Architecture Layers**

The examples demonstrate all four architectural layers:

1. **Domain Layer** (`03_domain_entities.py`):

   - CLI entities with business logic
   - Value objects and domain services
   - Business rule validation

2. **Application Layer** (`cli_app/application/commands.py`):

   - Use case orchestration
   - Command and query handlers (Sprint 2-3)
   - Application service coordination

3. **Infrastructure Layer** (Utilities and configuration):

   - External service integration
   - Configuration management
   - Dependency injection (Sprint 1)

4. **Commands Layer** (`cli_app/commands/`):
   - Click command implementations
   - User interface and interaction
   - Error presentation and formatting

### **Enterprise Patterns**

- **Configuration**: Environment-specific settings with validation
- **Error Handling**: FlextResult pattern throughout
- **Validation**: Business rules and input validation
- **Monitoring**: Operation tracking and metrics (Sprint 7)
- **Security**: Authentication and authorization patterns

## 📚 Learning Path

### **Beginner Path**

1. Start with `01_basic_cli_usage.py` for foundations
2. Explore `02_click_integration.py` for Click patterns
3. Study `03_domain_entities.py` for domain modeling

### **Intermediate Path**

1. Examine `cli_app/` structure for architecture understanding
2. Study command organization patterns
3. Explore configuration and validation patterns

### **Advanced Path**

1. Study Sprint-specific examples as they're implemented
2. Explore CQRS patterns (Sprint 2-3)
3. Implement custom plugins (Sprint 6)

### **Enterprise Path**

1. Study complete application architecture
2. Implement monitoring and observability (Sprint 7)
3. Create project-specific integrations (Sprint 9)

## 🔗 Related Documentation

- [Source Code](../src/flext_cli/) - Implementation details
- [Tests](../tests/) - Testing patterns and examples
- [CLAUDE.md](../CLAUDE.md) - Development guidelines
- [docs/TODO.md](../docs/TODO.md) - Sprint implementation roadmap

## 📋 Example Development Checklist

### **Sprint 1: Infrastructure Examples** (HIGH PRIORITY)

- [ ] Create FlextContainer integration examples
- [ ] Add service client integration examples
- [ ] Implement repository pattern examples
- [ ] Add configuration management examples

### **Sprint 2-3: CQRS Examples** (HIGH PRIORITY)

- [ ] Create command handler examples
- [ ] Add query handler examples
- [ ] Implement event handler examples
- [ ] Add CQRS architecture demonstration

### **Sprint 5: Data Pipeline Examples** (MEDIUM PRIORITY)

- [ ] Create Singer tap/target examples
- [ ] Add DBT transformation examples
- [ ] Implement Meltano orchestration examples

### **Sprint 6-7: Advanced Examples** (MEDIUM PRIORITY)

- [ ] Create plugin development examples
- [ ] Add monitoring and observability examples
- [ ] Implement interactive CLI examples

---

**Comprehensive Examples**: 75% coverage of CLI development patterns  
**Architecture Demonstration**: Complete Clean Architecture example  
**Sprint Alignment**: Examples evolve with development roadmap
