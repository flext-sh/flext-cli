# FLEXT CLI - FlextConfig Integration

## Overview

This document describes the integration of FlextConfig as the single source of truth for configuration in the FLEXT CLI application. The implementation ensures that CLI parameters modify behavior through the FlextConfig singleton pattern while maintaining consistency across the entire application.

## Architecture

### Single Source of Truth Pattern

The FlextConfig singleton from `flext-core` serves as the foundation for all configuration management. The CLI extends this pattern with `FlextCliConfig` while maintaining synchronization with the base configuration.

```
FlextConfig (flext-core)
    ↓ (extends)
FlextCliConfig (flext-cli)
    ↓ (applies CLI overrides)
CLI Parameters → Configuration Behavior
```

### Configuration Priority

Configuration values are applied in the following priority order (highest to lowest):

1. **CLI Parameters** - Direct command-line arguments
2. **Environment Variables** - `FLEXT_CLI_*` and `FLEXT_*` variables
3. **Configuration Files** - `.env`, `config.json`, `config.yaml`, `config.toml`
4. **Default Values** - Defined in FlextConfig fields

## Implementation Details

### Core Components

#### 1. FlextConfig Singleton (flext-core)

- Base configuration management with singleton pattern
- Environment variable integration with `FLEXT_` prefix
- Automatic `.env` file loading
- Type-safe validation using Pydantic v2

#### 2. FlextCliConfig Extension (flext-cli)

- Extends FlextConfig with CLI-specific fields
- Maintains singleton pattern with `_global_cli_instance`
- Provides CLI-specific validation and business rules
- Synchronizes with base FlextConfig singleton

#### 3. CLI Parameter Integration

- Click CLI interface applies parameters to FlextConfig
- Automatic mapping between CLI options and configuration fields
- Validation of parameter values before application
- Error handling with user-friendly messages

### Key Methods

#### `FlextCliConfig.apply_cli_overrides(cli_params)`

Applies CLI parameter overrides to both CLI and base configurations:

```python
# Example usage
cli_overrides = {
    "debug": True,
    "log_level": "DEBUG",
    "output_format": "json",
    "command_timeout": 60,
}

result = FlextCliConfig.apply_cli_overrides(cli_overrides)
```

#### `FlextCliConfig.sync_with_base_config()`

Synchronizes CLI configuration with base FlextConfig singleton:

```python
# Ensures consistency between configurations
sync_result = FlextCliConfig.sync_with_base_config()
```

#### `FlextConfig.get_global_instance()`

Retrieves the singleton instance of FlextConfig:

```python
# Get base configuration singleton
base_config = FlextConfig.get_global_instance()
```

## Usage Examples

### Basic CLI Usage

```bash
# Apply CLI parameters that modify FlextConfig behavior
flext-cli --debug --log-level DEBUG --output json config show
```

### Programmatic Usage

```python
from flext_core import FlextConfig
from flext_cli.config import FlextCliConfig

# Get configurations
base_config = FlextConfig.get_global_instance()
cli_config = FlextCliConfig.get_global_instance()

# Apply CLI overrides
cli_overrides = {
    "debug": True,
    "log_level": "DEBUG",
    "output_format": "json",
}

result = FlextCliConfig.apply_cli_overrides(cli_overrides)
if result.is_success:
    updated_config = result.value
    print(f"Debug mode: {updated_config.debug}")
    print(f"Log level: {updated_config.log_level}")
```

### Environment Variable Integration

```bash
# Set environment variables
export FLEXT_DEBUG=true
export FLEXT_LOG_LEVEL=WARNING
export FLEXT_CLI_PROFILE=production
export FLEXT_CLI_OUTPUT_FORMAT=yaml

# CLI will automatically use these values
flext-cli config show
```

## Configuration Fields

### Base FlextConfig Fields

- `environment`: Deployment environment (development, production, etc.)
- `debug`: Debug mode flag
- `log_level`: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `app_name`: Application name
- `version`: Application version
- `timeout_seconds`: Default timeout
- `max_workers`: Maximum worker threads

### CLI-Specific Fields

- `profile`: Configuration profile name
- `output_format`: Output format (table, JSON, YAML, csv)
- `api_url`: API base URL
- `command_timeout`: Command execution timeout
- `quiet`: Quiet mode flag
- `verbose`: Verbose mode flag
- `no_color`: Disable colored output

## Validation and Error Handling

### Configuration Validation

- Type-safe validation using Pydantic v2
- Business rule validation for CLI-specific constraints
- Runtime requirement validation
- Cross-field consistency checks

### Error Handling

- FlextResult pattern for all operations
- Detailed error messages with error codes
- Graceful fallback to default values
- User-friendly CLI error messages

## Testing

### Test Coverage

- Unit tests for configuration classes
- Integration tests for CLI parameter application
- Environment variable loading tests
- Validation and error handling tests

### Example Test

```python
def test_cli_parameter_override():
    """Test CLI parameter override functionality."""
    cli_overrides = {
        "debug": True,
        "log_level": "DEBUG",
        "output_format": "json",
    }

    result = FlextCliConfig.apply_cli_overrides(cli_overrides)
    assert result.is_success

    config = result.value
    assert config.debug is True
    assert config.log_level == "DEBUG"
    assert config.output_format == "json"
```

## Benefits

### Single Source of Truth

- FlextConfig serves as the authoritative configuration source
- Eliminates configuration inconsistencies
- Centralized configuration management

### CLI Parameter Integration

- CLI parameters directly modify application behavior
- Automatic validation and error handling
- Consistent parameter mapping

### Environment Integration

- Automatic environment variable loading
- Support for multiple configuration file formats
- Proper priority handling

### Type Safety

- Pydantic v2 validation ensures type safety
- Runtime validation prevents invalid configurations
- IDE support with proper type hints

### Extensibility

- Easy to add new configuration fields
- Simple CLI parameter mapping
- Flexible validation rules

## Migration Guide

### From Previous Configuration System

1. Replace direct configuration access with FlextConfig singleton
2. Update CLI parameter handling to use `apply_cli_overrides()`
3. Ensure environment variables use `FLEXT_` or `FLEXT_CLI_` prefixes
4. Update validation logic to use FlextResult pattern

### Best Practices

1. Always use FlextConfig singleton for configuration access
2. Apply CLI overrides early in application startup
3. Validate configurations before use
4. Use environment variables for deployment-specific settings
5. Test configuration changes thoroughly

## Conclusion

The FlextConfig integration provides a robust, type-safe, and extensible configuration management system for the FLEXT CLI. By using FlextConfig as the single source of truth, the CLI ensures consistent behavior across all components while allowing flexible parameter overrides through the command line interface.

The implementation follows SOLID principles, maintains backward compatibility, and provides error handling and validation. This architecture supports the requirements of the FLEXT platform while remaining simple to use and extend.
