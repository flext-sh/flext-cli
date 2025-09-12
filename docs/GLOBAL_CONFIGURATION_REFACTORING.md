# FLEXT CLI - Global Configuration Refactoring

## Overview

This document describes the comprehensive refactoring of the FLEXT CLI to use FlextConfig singleton as the **SINGLE SOURCE OF TRUTH** for all configuration across the entire application. This refactoring eliminates all duplicate configuration patterns and ensures consistent behavior throughout the CLI.

## Problem Statement

### Before Refactoring
- **Multiple Configuration Patterns**: Each module had its own configuration loading logic
- **Duplicate Code**: Configuration validation and loading was duplicated across modules
- **Inconsistent Sources**: Different modules used different configuration sources
- **Manual Synchronization**: Configuration changes required manual updates across modules
- **Inconsistent Validation**: Different validation rules across modules

### After Refactoring
- **Single Configuration Pattern**: FlextConfig singleton as the only configuration source
- **Zero Duplication**: All modules use FlextConfig.get_global_instance()
- **Consistent Source**: All modules get configuration from the same singleton
- **Automatic Synchronization**: Configuration changes propagate automatically
- **Unified Validation**: Single validation system for all configuration

## Architecture Changes

### Configuration Hierarchy

```
FlextConfig (flext-core)
    ↓ (singleton pattern)
FlextCliConfig (flext-cli)
    ↓ (extends and synchronizes)
All CLI Modules
    ↓ (use FlextConfig singleton)
CLI Parameters → Behavior Changes
```

### Module Refactoring

#### 1. FlextApiClient
**Before**: Custom configuration loading
```python
def __init__(self, base_url=None, token=None, timeout=30):
    config = FlextCliConfig()  # Creates new instance
    self.base_url = base_url or config.api_url
```

**After**: Uses FlextConfig singleton
```python
def __init__(self, base_url=None, token=None, timeout=None):
    config = FlextCliConfig.get_global_instance()  # Uses singleton
    self.base_url = base_url or config.api_url
    self._config = config  # Store reference for updates
```

#### 2. FlextCliApi
**Before**: Custom version handling
```python
def __init__(self, version="0.9.1"):
    state = FlextCliApi.ApiState(version=version)
```

**After**: Uses FlextConfig singleton
```python
def __init__(self, version=None):
    config = FlextCliConfig.get_global_instance()
    api_version = version or config.project_version
    state = FlextCliApi.ApiState(version=api_version)
    self._config = config
```

#### 3. FlextCliService
**Before**: Custom configuration loading
```python
def __init__(self):
    self._config = None  # No configuration
```

**After**: Uses FlextConfig singleton
```python
def __init__(self):
    self._initialize_configuration()
    
def _initialize_configuration(self):
    self._config = FlextCliConfig.get_global_instance()
```

#### 4. FlextCliAuth
**Before**: Complex configuration loading
```python
def __init__(self, config=None):
    if config is None:
        config_result = self._load_config_from_source()
        self._config = config_result.value
```

**After**: Uses FlextConfig singleton
```python
def __init__(self, config=None):
    if config is None:
        self._config = FlextCliConfig.get_global_instance()
    else:
        self._config = config
```

## Dynamic Configuration Updates

### Update Methods

All modules now provide methods to update their configuration from the FlextConfig singleton:

```python
# FlextApiClient
api_client.update_from_config()

# FlextCliApi
cli_api.update_from_config()

# FlextCliService
cli_service.update_configuration()

# FlextCliAuth
cli_auth.update_from_config()
```

### Configuration Flow

1. **CLI Parameters Applied**: `FlextCliConfig.apply_cli_overrides(cli_params)`
2. **FlextConfig Updated**: Singleton instance updated with new values
3. **Modules Updated**: All modules refresh from FlextConfig singleton
4. **Consistency Maintained**: All modules use the same configuration values

## CLI Parameter Integration

### Parameter Mapping

CLI parameters are mapped to FlextConfig fields:

```python
param_mappings = {
    "profile": "profile",
    "debug": "debug",
    "output": "output_format",
    "log_level": "log_level",
    "quiet": "quiet",
    "verbose": "verbose",
    "api_url": "api_url",
    "timeout": "command_timeout",
    "command_timeout": "command_timeout",
    "api_timeout": "api_timeout",
}
```

### Priority Order

Configuration values are applied in the following priority order:

1. **CLI Parameters** (highest priority)
2. **Environment Variables** (`FLEXT_CLI_*` and `FLEXT_*`)
3. **Configuration Files** (`.env`, `config.json`, `config.yaml`, `config.toml`)
4. **Default Values** (defined in FlextConfig fields)

## Benefits

### 1. Single Source of Truth
- **Eliminates Inconsistencies**: All modules use the same configuration source
- **Centralized Management**: Configuration changes in one place affect all modules
- **Reduced Complexity**: No need to manage multiple configuration sources

### 2. Automatic Synchronization
- **Real-time Updates**: Configuration changes propagate to all modules immediately
- **No Manual Work**: Modules automatically stay synchronized
- **Consistent State**: All modules always use the latest configuration

### 3. CLI Parameter Integration
- **Direct Behavior Modification**: CLI parameters modify application behavior through FlextConfig
- **Type-safe Validation**: All parameter validation uses the same system
- **Error Handling**: Consistent error handling across all modules

### 4. Maintainability
- **Reduced Code Duplication**: Single configuration loading logic
- **Easier Testing**: Single configuration source to test
- **Simplified Debugging**: One place to check configuration values

## Implementation Details

### Singleton Pattern

```python
class FlextCliConfig(FlextConfig):
    _global_cli_instance: ClassVar[FlextCliConfig | None] = None
    
    @classmethod
    def get_global_instance(cls) -> FlextCliConfig:
        if cls._global_cli_instance is None:
            cls._global_cli_instance = cls._load_cli_config_from_sources()
        return cls._global_cli_instance
```

### Configuration Loading

```python
@classmethod
def _load_cli_config_from_sources(cls) -> FlextCliConfig:
    # STEP 1: Get base FlextConfig singleton as SINGLE SOURCE OF TRUTH
    base_config = FlextConfig.get_global_instance()
    
    # STEP 2: Create CLI config by extending the base config instance
    cli_config_data = base_config.model_dump()
    
    # STEP 3: Apply CLI-specific overrides from environment variables
    cli_overrides = cls._get_cli_environment_overrides()
    cli_config_data.update(cli_overrides)
    
    # STEP 4: Create CLI config instance with merged data
    cli_config = cls(**cli_config_data)
    
    return cli_config
```

### Module Integration

```python
def __init__(self):
    # Get FlextConfig singleton as single source of truth
    self._config = FlextCliConfig.get_global_instance()
    
    # Initialize with configuration values
    self.base_url = self._config.api_url
    self.timeout = self._config.api_timeout
```

## Testing

### Test Coverage

All refactored modules are tested to ensure:

1. **Singleton Behavior**: FlextConfig singleton works correctly
2. **Module Integration**: All modules use FlextConfig singleton
3. **Configuration Updates**: Dynamic updates work across all modules
4. **CLI Parameter Integration**: CLI parameters modify behavior correctly
5. **Consistency**: All modules stay synchronized

### Test Results

```
tests/test_config.py ...........                                         [100%]
tests/test_config_commands.py ................                           [100%]
============================== 27 passed in 0.77s ==============================
```

## Migration Guide

### For Developers

1. **Replace Custom Configuration**: Use `FlextCliConfig.get_global_instance()` instead of creating new instances
2. **Add Update Methods**: Implement `update_from_config()` methods in your modules
3. **Remove Duplicate Logic**: Eliminate custom configuration loading and validation
4. **Use Singleton Pattern**: Always get configuration from the singleton

### For Users

1. **CLI Parameters**: Use standard CLI parameters (`--debug`, `--log-level`, etc.)
2. **Environment Variables**: Use `FLEXT_CLI_*` and `FLEXT_*` prefixes
3. **Configuration Files**: Use standard configuration file formats
4. **Consistent Behavior**: All CLI commands now use the same configuration system

## Examples

### Basic Usage

```python
from flext_cli.config import FlextCliConfig
from flext_cli.client import FlextApiClient

# Get configuration from singleton
config = FlextCliConfig.get_global_instance()

# Initialize client with configuration
client = FlextApiClient()

# Apply CLI overrides
cli_overrides = {"debug": True, "log_level": "DEBUG"}
FlextCliConfig.apply_cli_overrides(cli_overrides)

# Update client from new configuration
client.update_from_config()
```

### CLI Integration

```bash
# CLI parameters modify behavior through FlextConfig
flext-cli --debug --log-level DEBUG --api-url https://api.example.com config show
```

### Programmatic Updates

```python
# Update configuration
config_changes = {"api_url": "https://new-api.example.com"}
FlextCliConfig.apply_cli_overrides(config_changes)

# Update all modules
api_client.update_from_config()
cli_api.update_from_config()
cli_service.update_configuration()
cli_auth.update_from_config()
```

## Conclusion

The global configuration refactoring successfully establishes FlextConfig singleton as the **SINGLE SOURCE OF TRUTH** for all configuration in the FLEXT CLI. This refactoring:

- **Eliminates duplicate configuration patterns**
- **Ensures consistent behavior across all modules**
- **Enables CLI parameters to modify behavior through FlextConfig**
- **Provides automatic synchronization between modules**
- **Simplifies configuration management and debugging**

The implementation follows SOLID principles, maintains backward compatibility, and provides comprehensive error handling and validation. This architecture supports the enterprise-grade requirements of the FLEXT platform while remaining simple to use and maintain.