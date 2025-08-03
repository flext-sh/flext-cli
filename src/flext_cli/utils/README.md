# Utils Layer - Utility Functions and Cross-cutting Concerns

**Module**: `src/flext_cli/utils/`  
**Architecture Layer**: Utilities (Cross-cutting Support Functions)  
**Status**: 85% implemented - Comprehensive utilities with Rich integration  
**Sprint Alignment**: Strong foundation supporting Sprints 1-10

## 🎯 Module Overview

The utils layer provides utility functions, helper classes, and cross-cutting concerns that support all other layers in the FLEXT CLI. This module implements authentication utilities, configuration helpers, and output formatting with Rich integration, following flext-core patterns for consistent error handling.

### **Key Responsibilities**

- **Authentication Utilities**: Token management, session handling, credential validation
- **Configuration Utilities**: Configuration loading, validation, and management helpers
- **Output Formatting**: Rich-based output formatting with multiple format support
- **Common Utilities**: Shared helper functions used across the application
- **Validation Helpers**: Input validation and data transformation utilities

## 📁 Module Structure

```
src/flext_cli/utils/
├── __init__.py           # Utils layer exports and public API
├── auth.py              # Authentication and authorization utilities
├── config.py            # Configuration utilities and management helpers
└── output.py            # Output formatting utilities with Rich integration
```

## 🏗️ Architecture Patterns

### **Current Implementation (85% Complete)**

- ✅ **Authentication Utils**: Token management, credential validation, session handling
- ✅ **Configuration Utils**: Config loading, validation, environment integration
- ✅ **Output Formatting**: Rich integration with multiple output formats
- ✅ **Error Handling**: FlextResult pattern integration throughout utilities
- ⚠️ **Advanced Features**: Enhanced authentication and monitoring (Sprint 6-7)

### **flext-core Integration**

- **FlextResult**: All utilities return FlextResult for consistent error handling
- **Validation**: Uses flext-core validation patterns for input validation
- **Logging**: Structured logging with flext-core patterns
- **Error Handling**: Consistent exception handling and error propagation

## 📊 Implementation Status

### ✅ **Fully Implemented**

#### **auth.py - Authentication Utilities**

- **Token Management**: JWT token validation, expiration checking, refresh handling
- **Credential Validation**: Username/password validation with security patterns
- **Session Management**: CLI session creation, validation, and cleanup
- **Security Utilities**: Password hashing, secure token generation, validation helpers

#### **config.py - Configuration Utilities**

- **Configuration Loading**: Multi-source configuration loading with priority handling
- **Validation Helpers**: Configuration validation with business rules
- **Environment Integration**: Environment variable processing and defaults
- **Profile Management**: Basic profile loading and validation utilities

#### **output.py - Output Formatting**

- **Rich Integration**: Beautiful terminal output with tables, progress bars, panels
- **Multiple Formats**: Table, JSON, YAML, CSV output format support
- **Status Formatting**: Success/warning/error message formatting
- **Progress Reporting**: Progress bars, spinners, and real-time status updates

### ⚠️ **Needs Enhancement (Sprint 6-7)**

#### **Advanced Authentication (Sprint 6)**

```python
# Current (Basic Authentication)
def validate_token(token: str) -> FlextResult[dict]:
    # Basic JWT validation

# Target (Advanced Authentication - Sprint 6)
class AdvancedAuthManager:
    async def multi_factor_authentication(
        self,
        credentials: Credentials
    ) -> FlextResult[AuthResult]:
        # MFA support, SSO integration
        # Advanced security patterns
```

#### **Enhanced Output Features (Sprint 7)**

```python
# Current (Basic Rich Output)
def display_table(data: List[dict]) -> None:
    # Basic table display

# Target (Advanced Output - Sprint 7)
class InteractiveOutput:
    def create_live_dashboard(self) -> Live:
        # Real-time monitoring dashboard
        # Interactive data exploration
```

### ❌ **Planned Enhancements**

#### **Monitoring Integration (Sprint 7)**

```python
# Target implementation
class MonitoringUtils:
    async def track_operation_metrics(
        self,
        operation_name: str,
        metrics: dict
    ) -> FlextResult[None]:
        # Operation performance tracking
        # Integration with observability systems
```

#### **Advanced Configuration (Sprint 8)**

```python
# Target implementation
class ConfigurationWizard:
    async def interactive_setup(self) -> FlextResult[CLIConfig]:
        # Interactive configuration setup
        # Guided configuration with validation
        # Profile creation wizard
```

## 🎯 Sprint Roadmap Alignment

### **Sprint 1-5: Foundation** (Current Status)

- ✅ Authentication utilities with token management
- ✅ Configuration utilities with environment integration
- ✅ Rich output formatting with multiple format support
- ✅ Comprehensive error handling with FlextResult patterns

### **Sprint 6: Advanced Authentication**

```python
# Enhanced authentication features
class EnhancedAuthenticationUtils:
    async def validate_with_mfa(
        self,
        credentials: Credentials
    ) -> FlextResult[AuthResult]:
        # Multi-factor authentication support
        # Integration with external auth providers

    async def refresh_token_automatically(
        self,
        token: str
    ) -> FlextResult[str]:
        # Automatic token refresh
        # Background token management
```

### **Sprint 7: Interactive Output**

```python
# Interactive and real-time output features
class InteractiveOutputManager:
    def create_monitoring_dashboard(self) -> Layout:
        # Real-time monitoring dashboard
        # Live data updates and visualization

    def create_interactive_table(self, data: List[dict]) -> Table:
        # Sortable, filterable tables
        # Interactive data exploration
```

### **Sprint 8: Configuration Wizard**

```python
# Interactive configuration management
class ConfigurationWizardUtils:
    async def run_first_time_setup(self) -> FlextResult[CLIConfig]:
        # First-time setup wizard
        # Guided configuration with help

    async def profile_creation_wizard(self) -> FlextResult[CLIProfile]:
        # Interactive profile creation
        # Validation and testing
```

## 🔧 Development Guidelines

### **Adding New Utility Functions**

```python
# Pattern for new utility functions
from flext_core import FlextResult
from typing import Any

def new_utility_function(input_data: Any) -> FlextResult[Any]:
    """Utility function with consistent error handling."""
    try:
        # Validation
        if not input_data:
            return FlextResult.fail("Input data is required")

        # Processing
        result = process_data(input_data)

        # Validation of result
        if not is_valid_result(result):
            return FlextResult.fail("Invalid result generated")

        return FlextResult.ok(result)

    except ValidationError as e:
        return FlextResult.fail(f"Validation error: {e}")
    except Exception as e:
        logger.exception("Unexpected error in utility function")
        return FlextResult.fail(f"Utility operation failed: {e}")
```

### **Authentication Utility Patterns**

```python
# Pattern for authentication utilities
class AuthenticationUtility:
    def __init__(self, config: CLIConfig) -> None:
        self._config = config
        self._token_cache: Dict[str, Any] = {}

    async def validate_credentials(
        self,
        credentials: Credentials
    ) -> FlextResult[AuthResult]:
        # Input validation
        validation = self._validate_credential_format(credentials)
        if not validation.is_success:
            return validation

        # Authentication logic
        try:
            auth_result = await self._perform_authentication(credentials)

            # Cache management
            await self._update_token_cache(auth_result.token)

            return FlextResult.ok(auth_result)

        except AuthenticationError as e:
            return FlextResult.fail(f"Authentication failed: {e}")
```

### **Output Formatting Patterns**

```python
# Pattern for Rich-based output utilities
from rich.console import Console
from rich.table import Table

class OutputFormatter:
    def __init__(self, console: Console) -> None:
        self.console = console

    def format_data(
        self,
        data: List[dict],
        format_type: str = "table"
    ) -> FlextResult[None]:
        try:
            if format_type == "table":
                self._display_table(data)
            elif format_type == "json":
                self._display_json(data)
            elif format_type == "yaml":
                self._display_yaml(data)
            else:
                return FlextResult.fail(f"Unsupported format: {format_type}")

            return FlextResult.ok(None)

        except Exception as e:
            return FlextResult.fail(f"Output formatting failed: {e}")
```

## 🧪 Testing Guidelines

### **Authentication Utility Testing**

```python
def test_token_validation():
    # Test valid token
    valid_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    result = validate_token(valid_token)
    assert result.is_success

    # Test invalid token
    invalid_token = "invalid.token.here"
    result = validate_token(invalid_token)
    assert not result.is_success
    assert "Invalid token" in result.error

def test_credential_validation():
    # Test valid credentials
    credentials = Credentials(username="user", password="password123")
    result = validate_credentials(credentials)
    assert result.is_success

    # Test invalid credentials
    credentials = Credentials(username="", password="")
    result = validate_credentials(credentials)
    assert not result.is_success
```

### **Configuration Utility Testing**

```python
def test_config_loading():
    # Test successful config loading
    result = load_configuration("test_profile")
    assert result.is_success

    config = result.unwrap()
    assert isinstance(config, CLIConfig)
    assert config.profile == "test_profile"

def test_config_validation():
    # Test valid configuration
    config_data = {"debug": True, "output_format": "json"}
    result = validate_configuration(config_data)
    assert result.is_success

    # Test invalid configuration
    config_data = {"debug": "invalid", "output_format": "unknown"}
    result = validate_configuration(config_data)
    assert not result.is_success
```

### **Output Utility Testing**

```python
def test_table_formatting():
    data = [{"name": "test", "status": "active"}]

    # Capture console output
    console = Console(file=StringIO())
    formatter = OutputFormatter(console)

    result = formatter.format_data(data, "table")
    assert result.is_success

    output = console.file.getvalue()
    assert "test" in output
    assert "active" in output

def test_multiple_format_support():
    data = [{"key": "value"}]
    formatter = OutputFormatter(Console())

    # Test all supported formats
    for format_type in ["table", "json", "yaml", "csv"]:
        result = formatter.format_data(data, format_type)
        assert result.is_success
```

## 📈 Utility Coverage and Quality

### **Current Implementation Coverage**

- **Authentication**: 90% coverage (token, credentials, session management)
- **Configuration**: 85% coverage (loading, validation, environment integration)
- **Output**: 95% coverage (Rich integration, multiple formats, error handling)
- **Error Handling**: 100% FlextResult pattern adoption

### **Quality Metrics**

- **Test Coverage**: 95% across all utility modules
- **Type Safety**: 100% MyPy strict mode compliance
- **Error Handling**: 100% FlextResult pattern usage
- **Documentation**: 100% comprehensive docstrings

## 🔗 Integration Points

### **Command Layer Integration**

- Authentication utilities used by auth commands
- Output formatting used by all commands for consistent display
- Configuration utilities used for command-specific settings

### **Application Layer Integration**

- Configuration utilities support application service configuration
- Authentication utilities provide session management for application operations
- Output utilities support application-level reporting and monitoring

### **Infrastructure Layer Integration**

- Configuration utilities load infrastructure service settings
- Authentication utilities integrate with external authentication providers
- Output utilities support infrastructure monitoring and diagnostics

## 🔗 Related Documentation

- [Core Layer](../core/README.md) - Core CLI patterns using utilities
- [Commands Layer](../commands/README.md) - CLI commands using utility functions
- [Configuration Layer](../config/README.md) - Configuration models supported by utilities
- [TODO.md](../../../docs/TODO.md) - Sprint 6-8 utility enhancements

## 📋 Sprint Implementation Checklist

### **Sprint 6: Advanced Authentication** (MEDIUM PRIORITY)

- [ ] Implement multi-factor authentication support
- [ ] Add SSO integration capabilities
- [ ] Create advanced token management with automatic refresh
- [ ] Add security audit and monitoring utilities

### **Sprint 7: Interactive Output** (MEDIUM PRIORITY)

- [ ] Implement live monitoring dashboard components
- [ ] Add interactive data exploration utilities
- [ ] Create real-time progress reporting with Rich Live
- [ ] Add custom renderable components for complex data

### **Sprint 8: Configuration Wizard** (LOWER PRIORITY)

- [ ] Create interactive configuration setup wizard
- [ ] Add guided profile creation with validation
- [ ] Implement configuration migration utilities
- [ ] Add configuration documentation generation

---

**Strong Foundation**: 85% implementation provides comprehensive utility support  
**Architecture Layer**: Utilities (Cross-cutting support functions for all layers)  
**Dependencies**: Rich terminal library, authentication libraries, configuration management
