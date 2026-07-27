<!-- Generated from docs/guides/settings.md for flext-cli. -->

<!-- Source of truth: workspace docs/guides/. -->

# flext-cli - FLEXT Configuration Guide

> Project profile: `flext-cli`

<!-- TOC START -->
- [Overview](#overview)
- [Configuration Sources](#configuration-sources)
- [Basic Configuration](#basic-configuration)
  - [Environment Variables](#environment-variables)
  - [Configuration Files](#configuration-files)
  - [Programmatic Configuration](#programmatic-configuration)
- [Project-Specific Configuration](#project-specific-configuration)
  - [flext-ldif Configuration](#flext-ldif-configuration)
  - [flext-api Configuration](#flext-api-configuration)
  - [flext-auth Configuration](#flext-auth-configuration)
- [Environment-Specific Configuration](#environment-specific-configuration)
  - [Development Environment](#development-environment)
  - [Production Environment](#production-environment)
- [Configuration Validation](#configuration-validation)
- [Configuration Inheritance](#configuration-inheritance)
- [Best Practices](#best-practices)
  - [1. Use Environment Variables for Secrets](#1-use-environment-variables-for-secrets)
  - [2. Validate Configuration Early](#2-validate-configuration-early)
  - [3. Use Configuration Classes](#3-use-configuration-classes)
  - [4. Document Configuration Options](#4-document-configuration-options)
- [Troubleshooting](#troubleshooting)
  - [Common Configuration Issues](#common-configuration-issues)
  - [Debug Configuration](#debug-configuration)
- [Examples](#examples)
  - [Complete Configuration Example](#complete-configuration-example)
- [Reference](#reference)
<!-- TOC END -->

This guide covers how to configure FLEXT for your specific environment and requirements.

## Overview

FLEXT uses a hierarchical configuration system that supports environment variables, configuration files,
and programmatic configuration. All configuration is validated using Pydantic v2 models for type safety and validation.

## Configuration Sources

FLEXT loads configuration in the following order (later sources override earlier ones):

1. **Default values** in Pydantic models
1. **Environment variables** (prefixed with `FLEXT_`)
1. **Configuration files** (YAML, JSON, or TOML)
1. **Programmatic configuration** in code

## Basic Configuration

### Environment Variables

Set configuration using environment variables with the `FLEXT_` prefix:

```bash
# Core configuration
export FLEXT_LOG_LEVEL=INFO
export FLEXT_DEBUG=false
export FLEXT_ENVIRONMENT=production

# LDIF processing
export FLEXT_LDIF_DEFAULT_ENCODING=utf-8
export FLEXT_LDIF_STRICT_VALIDATION=true
export FLEXT_LDIF_SERVERS_ENABLED=true

# API configuration
export FLEXT_API_BASE_URL=https://api.example.com
export FLEXT_API_TIMEOUT=30
```

### Configuration Files

Create configuration files in YAML, JSON, or TOML format:

**settings.YAML:**

```yaml
# FLEXT Configuration
log_level: INFO
debug: false
environment: production

# LDIF Processing
ldif:
  default_encoding: utf-8
  strict_validation: true
  servers_enabled: true
  batch_size: 1000

# API Configuration
api:
  base_url: https://api.example.com
  timeout: 30
  retry_attempts: 3
```

### Programmatic Configuration

Configure FLEXT programmatically in your code:

```python
from __future__ import annotations

from flext_cli import settings, u
from flext_ldif import settings as ldif_settings

# Core configuration (settings is the singleton instance; FlextCliSettings is the class)
print(u.out(f"log level: {settings.log_level}"))
print(u.out(f"debug: {settings.debug}"))

# LDIF sub-configuration
print(u.out(f"ldif encoding: {ldif_settings.ldif.ldif_encoding}"))
print(u.out(f"strict validation: {ldif_settings.ldif.ldif_strict_validation}"))
```

## Project-Specific Configuration

### flext-ldif Configuration

```python
from __future__ import annotations

from flext_ldif import settings, ldif, u

# Settings are read from the singleton instance (env/defaults).
# Override specific LDIF settings locally by creating a new instance.
local = settings.__class__(
    ldif=settings.__class__.LdifSettings(
        ldif_encoding="utf-8", ldif_strict_validation=True
    )
)

# Parse a minimal LDIF record to verify configuration
content = """dn: cn=test,dc=example,dc=com
cn: test
objectClass: inetOrgPerson
"""
result = ldif.parse_string(content)
print(u.out(f"parsed successfully: {result.success}"))
print(u.out(f"encoding: {local.ldif.ldif_encoding}"))
print(u.out(f"strict validation: {local.ldif.ldif_strict_validation}"))
```

### flext-api Configuration

```python
from __future__ import annotations

from flext_cli import m, u


# Example domain settings model (replace with your project's settings class)
class ApiSettings(m.BaseModel):
    base_url: str = "https://api.example.com"
    timeout: int = 30
    retry_attempts: int = 3


api_config = ApiSettings(
    base_url="https://api.example.com", timeout=30, retry_attempts=3
)
print(u.out(f"API base URL: {api_config.base_url}"))
print(u.out(f"timeout: {api_config.timeout}"))
```

### flext-auth Configuration

```python
from __future__ import annotations

from flext_cli import c, m, u


# Example auth settings model using real FLEXT constants
class AuthSettings(m.BaseModel):
    secret_key: str = "your-secret-key"
    algorithm: c.Compression = c.Compression.NONE
    access_token_expire_minutes: int = 30


auth_config = AuthSettings(
    secret_key="your-secret-key",
    algorithm=c.Compression.NONE,
    access_token_expire_minutes=30,
)
print(u.out(f"algorithm: {auth_config.algorithm.value}"))
print(
    u.out(f"access token expires in {auth_config.access_token_expire_minutes} minutes")
)
```

## Environment-Specific Configuration

### Development Environment

```yaml
# settings.dev.yaml
log_level: DEBUG
debug: true
environment: development

ldif:
  strict_validation: false
  servers_enabled: false

api:
  base_url: http://localhost:8000
  timeout: 60
```

### Production Environment

```yaml
# settings.prod.yaml
log_level: WARNING
debug: false
environment: production

ldif:
  strict_validation: true
  servers_enabled: true
  batch_size: 5000

api:
  base_url: https://api.production.com
  timeout: 30
  retry_attempts: 5
```

## Configuration Validation

All configuration is validated using Pydantic v2 models:

```python
from __future__ import annotations

from pydantic import ValidationError
from flext_cli import FlextCliSettings, u

try:
    FlextCliSettings(log_level="INVALID_LEVEL")
except ValidationError as exc:
    u.out("Configuration error: invalid log level")
    u.out(str(exc.errors()[0]["msg"]))
```

## Configuration Inheritance

FLEXT supports configuration inheritance for complex setups:

```python
from __future__ import annotations

from flext_cli import FlextCliSettings, u

# Base configuration
base_config = FlextCliSettings(log_level="INFO", debug=False)

# Extended configuration using model_dump for inheritance
extended_config = FlextCliSettings(
    **base_config.model_dump(exclude={"debug"}),
    debug=True,  # Override for development
)

print(u.out(f"base log level: {base_config.log_level}"))
print(u.out(f"extended debug: {extended_config.debug}"))
```

## Best Practices

### 1. Use Environment Variables for Secrets

```bash
# Never put secrets in configuration files
export FLEXT_DATABASE_PASSWORD=secret_password
export FLEXT_API_KEY=your_api_key
```

### 2. Validate Configuration Early

```python
from __future__ import annotations

from flext_cli import FlextCliSettings, u


def main() -> int:
    # Validate configuration at startup by instantiating the settings class
    settings = FlextCliSettings()

    if settings.debug:
        u.out("Running in debug mode")

    u.out(f"Configuration loaded: log_level={settings.log_level}")
    return 0


main()
```

### 3. Use Configuration Classes

```python
from __future__ import annotations

from flext_cli import m, u
from pydantic import field_validator


class MyAppSettings(m.BaseModel):
    custom_setting: str = "default_value"
    another_setting: int = 42

    @field_validator("another_setting")
    @classmethod
    def validate_another_setting(cls, value: int) -> int:
        if value < 0:
            raise ValueError("another_setting must be positive")
        return value


settings = MyAppSettings(another_setting=10)
print(u.out(f"custom: {settings.custom_setting}"))
print(u.out(f"another: {settings.another_setting}"))
```

### 4. Document Configuration Options

```python
from __future__ import annotations

from flext_cli import m, u


class LdifSettingsExample(m.BaseModel):
    """Configuration for LDIF processing."""

    default_encoding: str = m.Field(
        default="utf-8", description="Default encoding for LDIF files"
    )

    strict_validation: bool = m.Field(
        default=True, description="Enable strict RFC validation"
    )


example = LdifSettingsExample()
print(u.out(f"encoding: {example.default_encoding}"))
print(u.out(f"strict: {example.strict_validation}"))
```

## Troubleshooting

### Common Configuration Issues

1. **Environment Variables Not Loading**

   - Ensure variables are prefixed with `FLEXT_`
   - Check for typos in variable names
   - Verify environment is set before running application

1. **Configuration File Not Found**

   - Check file path is correct
   - Ensure file has proper permissions
   - Verify file format (YAML, JSON, or TOML)

1. **Validation Errors**

   - Check Pydantic model field types
   - Verify required fields are provided
   - Review field validators for constraints

### Debug Configuration

```python
from __future__ import annotations

from flext_cli import FlextCliSettings, u

# Enable debug logging
settings = FlextCliSettings(debug=True)

# Print configuration
print(u.out(settings.model_dump()))

# Validate configuration implicitly by instantiating
if settings.debug:
    print(u.out("Debug mode is enabled"))
else:
    print(u.out("Debug mode is disabled"))
```

## Examples

### Complete Configuration Example

```python
from __future__ import annotations

"""Complete FLEXT configuration example."""

import os
from flext_cli import FlextCliSettings, u
from flext_ldif import FlextLdifSettings, ldif


def main() -> None:
    # Load configuration from environment/defaults
    settings = FlextCliSettings()

    # Configure LDIF processing
    ldif_config = FlextLdifSettings(
        ldif=FlextLdifSettings.LdifSettings(
            ldif_encoding=os.getenv("FLEXT_LDIF_ENCODING", "utf-8"),
            ldif_strict_validation=os.getenv(
                "FLEXT_LDIF_STRICT_VALIDATION", "true"
            ).lower()
            == "true",
        )
    )

    # Verify LDIF parsing works with the loaded settings
    content = """dn: cn=test,dc=example,dc=com
cn: test
objectClass: inetOrgPerson
"""
    result = ldif.parse_string(content)

    u.out("Configuration loaded successfully")
    u.out(f"Log level: {settings.log_level}")
    u.out(f"LDIF encoding: {ldif_config.ldif.ldif_encoding}")
    u.out(f"LDIF strict validation: {ldif_config.ldif.ldif_strict_validation}")
    u.out(f"Sample parse succeeded: {result.success}")


main()
```

## Reference

- FLEXT Core Configuration
- Environment Variables
- [Pydantic v2 Documentation](https://docs.pydantic.dev/2.0/)
- Configuration Best Practices
