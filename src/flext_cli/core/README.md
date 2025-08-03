# Core Layer - CLI Utilities and Base Patterns

**Module**: `src/flext_cli/core/`  
**Architecture Layer**: Cross-cutting (Core CLI Utilities)  
**Status**: 80% implemented - Solid foundation with Rich integration, type safety  
**Sprint Alignment**: Foundation for Sprints 1-10, enhancements planned for Sprint 6-7

## 🎯 Module Overview

The core layer provides foundational CLI utilities, base patterns, and cross-cutting concerns that support all other layers. This module implements common CLI patterns, decorators, formatters, and type definitions using Click framework and Rich terminal UI components.

### **Key Responsibilities**

- **Base CLI Patterns**: Common patterns for Click command implementation
- **Decorators**: Reusable decorators for command handling and error management
- **Formatters**: Output formatting utilities with Rich integration
- **Helper Functions**: Common utilities used across CLI commands
- **Type Definitions**: Click parameter types and CLI-specific types

## 📁 Module Structure

```
src/flext_cli/core/
├── __init__.py           # Core layer exports and public API
├── base.py              # Base CLI patterns and context models
├── decorators.py        # CLI decorators for error handling and validation
├── formatters.py        # Output formatting utilities with Rich integration
├── helpers.py           # Helper functions and utilities
└── types.py             # Click parameter types and CLI type definitions
```

## 🏗️ Architecture Patterns

### **Current Implementation (80% Complete)**

- ✅ **Base Patterns**: CLI context models and base command patterns
- ✅ **Rich Integration**: Beautiful terminal output with tables, progress bars
- ✅ **Error Handling**: FlextResult-based error handling decorators
- ✅ **Type Safety**: Click parameter types with validation
- ✅ **Helper Utilities**: Common CLI operations and utilities
- ⚠️ **Advanced Formatting**: Enhanced formatting patterns (Sprint 6-7)

### **Target Architecture (Sprint 6-7)**

- 🎯 **Interactive Components**: Enhanced Rich components for complex UIs
- 🎯 **Advanced Decorators**: Performance monitoring and caching decorators
- 🎯 **Plugin System**: Base patterns for CLI plugin architecture
- 🎯 **Configuration UI**: Interactive configuration management components

## 📊 Implementation Status

### ✅ **Fully Implemented**

#### **base.py - Base CLI Patterns**

- **Base command patterns**: Common Click command structure
- **Context management**: CLI execution context handling
- **Error handling**: FlextResult integration patterns
- **Session management**: CLI session context models

#### **decorators.py - CLI Decorators**

- **@handle_service_result**: FlextResult error handling decorator
- **Command validation**: Input validation decorators
- **Context injection**: Dependency injection decorators
- **Error reporting**: Consistent error message formatting

#### **formatters.py - Output Formatting**

- **Rich table formatting**: Beautiful tabular data display
- **Progress indicators**: Progress bars and spinners
- **Status formatting**: Success/error message formatting
- **Multiple format support**: Table, JSON, YAML, CSV output

#### **helpers.py - Helper Functions**

- **Configuration helpers**: Config loading and validation utilities
- **Path utilities**: File and directory path handling
- **String utilities**: Text processing and formatting
- **Validation helpers**: Common validation patterns

#### **types.py - Click Types**

- **Custom parameter types**: CLI-specific Click parameter types
- **Validation types**: Input validation with business rules
- **Format types**: Output format selection types
- **Path types**: File and directory path validation types

### ⚠️ **Needs Enhancement (Sprint 6-7)**

#### **Advanced Rich Components**

```python
# Current (Basic Rich Usage)
def display_table(data: List[dict]) -> None:
    table = Table()
    # Basic table formatting

# Target (Advanced Components - Sprint 6-7)
class InteractiveDashboard:
    def __init__(self) -> None:
        self.live = Live()
        self.layout = Layout()

    def display_real_time_metrics(self) -> None:
        # Real-time dashboard with live updates
        # Interactive components for monitoring
```

#### **Plugin System Base (Sprint 6)**

```python
# Target implementation
class CLIPluginBase:
    def register_commands(self, cli_group: click.Group) -> None:
        # Plugin command registration

    def get_command_decorators(self) -> List[Callable]:
        # Plugin-specific decorators
```

### ❌ **Missing Components**

#### **Interactive Configuration UI (Sprint 7)**

```python
# Target implementation
class InteractiveConfigWizard:
    def run_configuration_setup(self) -> FlextResult[CLIConfig]:
        # Interactive configuration setup
        # Rich-based prompts and validation
        # Profile creation and management
```

#### **Performance Monitoring (Sprint 6)**

```python
# Target implementation
def performance_monitor(operation_name: str):
    def decorator(func: Callable) -> Callable:
        # Performance tracking and monitoring
        # Integration with observability systems
```

## 🎯 Sprint Roadmap Alignment

### **Sprint 1-5: Foundation** (Current Status)

- ✅ Base CLI patterns implemented
- ✅ Rich integration for beautiful output
- ✅ Error handling decorators
- ✅ Type safety with Click parameter types

### **Sprint 6: Plugin Architecture Enhancement**

```python
# Plugin system base patterns
class CLIPluginManager:
    def __init__(self) -> None:
        self._plugins: Dict[str, CLIPluginBase] = {}

    def register_plugin(self, plugin: CLIPluginBase) -> FlextResult[None]:
        # Plugin registration and lifecycle management

    def discover_plugins(self) -> FlextResult[List[CLIPluginBase]]:
        # Automatic plugin discovery
```

### **Sprint 7: Interactive Components**

```python
# Enhanced interactive features
class RichInteractiveComponents:
    def create_progress_dashboard(self) -> Layout:
        # Multi-panel progress dashboard

    def create_monitoring_layout(self) -> Layout:
        # Real-time monitoring interface
```

### **Sprint 8: Advanced Formatting**

```python
# Advanced formatting and visualization
class DataVisualization:
    def create_charts(self, data: List[dict]) -> Panel:
        # ASCII charts and graphs

    def create_tree_view(self, hierarchical_data: dict) -> Tree:
        # Interactive tree navigation
```

## 🔧 Development Guidelines

### **Adding New Decorators**

```python
# Pattern for new CLI decorators
from functools import wraps
from flext_core import FlextResult

def new_cli_decorator(option: str):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Decorator logic with FlextResult handling
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Consistent error handling
                return FlextResult.fail(f"Operation failed: {e}")
        return wrapper
    return decorator
```

### **Adding New Formatters**

```python
# Pattern for Rich-based formatters
from rich.table import Table
from rich.console import Console

class NewFormatter:
    def __init__(self, console: Console) -> None:
        self.console = console

    def format_data(self, data: List[dict], format_type: str) -> None:
        if format_type == "table":
            self._format_table(data)
        elif format_type == "json":
            self._format_json(data)
        # Additional format support
```

### **Adding Helper Functions**

```python
# Pattern for CLI helper functions
def new_cli_helper(input_data: Any) -> FlextResult[Any]:
    """Helper function with consistent error handling."""
    try:
        # Helper logic
        result = process_input(input_data)
        return FlextResult.ok(result)
    except ValidationError as e:
        return FlextResult.fail(f"Validation failed: {e}")
    except Exception as e:
        return FlextResult.fail(f"Helper operation failed: {e}")
```

## 🧪 Testing Guidelines

### **Decorator Testing**

```python
def test_handle_service_result_decorator():
    @handle_service_result
    def mock_command() -> FlextResult[str]:
        return FlextResult.ok("success")

    result = mock_command()
    assert result is not None  # Decorator should handle FlextResult properly

def test_decorator_error_handling():
    @handle_service_result
    def failing_command() -> FlextResult[str]:
        return FlextResult.fail("test error")

    # Should handle error gracefully
    result = failing_command()
    # Verify error handling behavior
```

### **Formatter Testing**

```python
def test_table_formatter():
    console = Console(file=StringIO())
    formatter = TableFormatter(console)

    data = [{"name": "test", "status": "active"}]
    formatter.format_data(data, "table")

    output = console.file.getvalue()
    assert "test" in output
    assert "active" in output
```

### **Helper Function Testing**

```python
def test_configuration_helper():
    result = load_config_with_validation("test_config.yaml")
    assert result.is_success

    config = result.unwrap()
    assert isinstance(config, CLIConfig)
```

## 📈 Current vs Target Implementation

### **Current State (80% Implementation)**

- Base patterns: Comprehensive Click integration
- Rich formatting: Tables, progress bars, panels
- Error handling: FlextResult decorators
- Type safety: Click parameter types with validation

### **Target State (Sprint 6-8)**

- Plugin architecture: Extensible CLI plugin system
- Interactive components: Real-time dashboards and monitoring
- Advanced formatting: Charts, graphs, interactive navigation
- Performance monitoring: Operation tracking and optimization

## 🔗 Integration Points

### **Command Layer Integration**

- Provides base patterns for all CLI commands
- Supplies decorators for consistent error handling
- Offers formatters for beautiful output presentation

### **Application Layer Integration**

- Context management for application services
- Error handling patterns for application operations
- Helper utilities for cross-cutting concerns

### **Infrastructure Layer Integration**

- Configuration utilities for infrastructure services
- Path handling for file system operations
- Validation helpers for external system integration

## 🔗 Related Documentation

- [Commands Layer](../commands/README.md) - CLI command implementations using core patterns
- [Application Layer](../application/README.md) - Application services using core utilities
- [TODO.md](../../../docs/TODO.md) - Sprint 6-8 enhancement roadmap
- [Rich Documentation](https://rich.readthedocs.io/) - Rich terminal library integration guide

## 📋 Sprint Implementation Checklist

### **Sprint 6: Plugin Architecture** (MEDIUM PRIORITY)

- [ ] Implement CLIPluginBase and plugin discovery system
- [ ] Add plugin registration and lifecycle management
- [ ] Create plugin-specific decorators and utilities
- [ ] Add comprehensive plugin testing framework

### **Sprint 7: Interactive Components** (MEDIUM PRIORITY)

- [ ] Implement interactive configuration wizard
- [ ] Add real-time monitoring dashboard components
- [ ] Create interactive navigation and selection components
- [ ] Add enhanced progress reporting with live updates

### **Sprint 8: Advanced Formatting** (LOWER PRIORITY)

- [ ] Implement ASCII charts and data visualization
- [ ] Add interactive tree navigation for hierarchical data
- [ ] Create advanced table formatting with sorting and filtering
- [ ] Add custom Rich renderable components

---

**Strong Foundation**: 80% implementation provides solid base for all CLI operations  
**Architecture Layer**: Cross-cutting (Utilities and patterns used by all other layers)  
**Dependencies**: Click framework, Rich terminal library, flext-core patterns
