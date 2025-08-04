"""FLEXT CLI Config Package - Configuration Management and Settings.

This package provides comprehensive configuration management for FLEXT CLI
with type-safe Pydantic models, environment variable support, and structured
configuration organization. Implements the configuration layer for Clean
Architecture with flext-core integration.

Configuration Modules:
    - cli_config: Main configuration models and settings management

Features:
    - Type-safe configuration with Pydantic validation
    - Environment variable support with FLEXT_CLI_ prefix
    - Nested configuration structure with component composition
    - Backward compatibility with legacy configuration interfaces
    - Directory management and setup utilities
    - Authentication token management

Current Implementation Status:
    ✅ Complete configuration model implementation
    ✅ Environment variable integration
    ✅ Type safety with Pydantic validation
    ✅ Backward compatibility support
    ✅ Directory and authentication management
    ⚠️ Full functionality (TODO: Sprint 2 - enhanced features)

TODO (docs/TODO.md):
    Sprint 2: Add configuration file loading (YAML, JSON, TOML)
    Sprint 3: Add profile-based configuration inheritance
    Sprint 5: Add encrypted configuration support
    Sprint 7: Add configuration monitoring and hot-reload

Package Exports:
    cli_config: Configuration models and utilities module

Integration:
    - Used throughout FLEXT CLI for configuration management
    - Provides foundation for environment-specific settings
    - Supports Clean Architecture configuration patterns
    - Integrates with flext-core settings and validation

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

__all__: list[str] = ["cli_config"]

from . import cli_config
