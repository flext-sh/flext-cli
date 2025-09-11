# FLEXT-CLI Examples - Comprehensive Learning Path

This directory contains a comprehensive set of examples demonstrating all flext-cli patterns and capabilities in a progressive learning structure.

## 📚 Learning Path Overview

The examples are organized in a sequential learning path from foundational patterns to advanced integration techniques:

1. **[01_foundation_patterns.py](01_foundation_patterns.py)** - Core flext-core integration patterns
2. **[02_cli_commands_integration.py](02_cli_commands_integration.py)** - Click framework integration with decorators
3. **[03_data_processing_and_output.py](03_data_processing_and_output.py)** - Data processing and output formatting
4. **[04_authentication_and_authorization.py](04_authentication_and_authorization.py)** - Security patterns and token management
5. **[05_advanced_service_integration.py](05_advanced_service_integration.py)** - Advanced patterns with async operations
6. **[06_comprehensive_cli_application.py](06_comprehensive_cli_application.py)** - Complete real-world CLI application

## 🏗️ Architecture Patterns Demonstrated

### Clean Architecture Integration

- **Domain Layer**: CLI entities (CLICommand, FlextCliSession, FlextCliPlugin) with business rules
- **Application Layer**: Command handlers and service orchestration
- **Infrastructure Layer**: External service integration, file I/O, API clients

### flext-core Foundation Patterns

- **FlextResult[T]**: Railway-oriented programming for error handling
- **FlextModels**: Pydantic-based domain models with validation
- **FlextContainer**: Dependency injection container for service composition
- **FlextModels**: Entity creation patterns with validation

## 📖 Example Details

### 01 - Foundation Patterns

**File**: `01_foundation_patterns.py`

**Key Patterns**:

- FlextResult railway-oriented programming
- FlextModels with Pydantic validation
- FlextContainer dependency injection
- CLI domain entities with business rules
- Entity lifecycle management

**What You'll Learn**:

- How to use FlextResult for error handling
- Creating domain entities with validation
- Service composition with dependency injection
- CLI-specific domain modeling

### 02 - CLI Commands Integration

**File**: `02_cli_commands_integration.py`

**Key Patterns**:

- Click framework integration with flext-cli decorators
- Type-safe CLI options (URL, PositiveInt, ExistingFile)
- CLI decorators (@cli_enhanced, @cli_measure_time, @cli_confirm)
- Interactive prompts and user confirmation
- Command lifecycle with validation and execution

**What You'll Learn**:

- Building type-safe CLI commands
- Using flext-cli decorators for enhanced functionality
- Interactive CLI patterns with Rich UI
- Command parameter validation and transformation

### 03 - Data Processing and Output

**File**: `03_data_processing_and_output.py`

**Key Patterns**:

- Data transformation and aggregation utilities
- Multiple output formats (JSON, YAML, CSV, Rich tables)
- Type-safe file operations (ExistingFile, NewFile, ExistingDir)
- FormatterFactory pattern for consistent output
- Batch processing workflows

**What You'll Learn**:

- Processing and transforming data in CLI applications
- Creating beautiful terminal output with Rich
- Type-safe file handling patterns
- Implementing flexible output formatting

### 04 - Authentication and Authorization

**File**: `04_authentication_and_authorization.py`

**Key Patterns**:

- Token management (save, retrieve, validate)
- Authorization headers and API authentication
- Protected operations with @require_auth decorator
- Role-based access control (RBAC)
- Session management and token refresh

**What You'll Learn**:

- Implementing secure authentication in CLI apps
- Token-based authentication patterns
- Role-based permission systems
- Secure credential handling

### 05 - Advanced Service Integration

**File**: `05_advanced_service_integration.py`

**Key Patterns**:

- FlextCliService with comprehensive mixins
- Async command execution with @async_command
- Circuit breaker pattern for service resilience
- Service orchestration and coordination
- Health monitoring and performance tracking

**What You'll Learn**:

- Building resilient service integrations
- Implementing async operations in CLI apps
- Circuit breaker patterns for fault tolerance
- Service health monitoring and orchestration

### 06 - Comprehensive CLI Application

**File**: `06_comprehensive_cli_application.py`

**Key Patterns**:

- Multi-command CLI with nested command groups
- Plugin architecture for extensibility
- Configuration management with profiles
- Service integration with external APIs
- Rich terminal UI with progress tracking

**What You'll Learn**:

- Building complete, production-ready CLI applications
- Implementing plugin architectures
- Advanced configuration management
- Creating rich, interactive terminal experiences

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
settings = flext_cli.FlextCliSettings(
    api_url="https://api.production.com",
    timeout=30,
    max_retries=3
)

# Context creation
context = flext_cli.FlextCliContext(
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
    return FlextResult[None].ok("Operation completed successfully")
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
session = flext_cli.FlextCliSession(
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
