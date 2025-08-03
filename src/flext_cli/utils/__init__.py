"""FLEXT CLI Utils Package - Utility Functions and Infrastructure Helpers.

This package provides utility functions and infrastructure helpers for FLEXT CLI
operations including configuration management, authentication, output formatting,
and common CLI patterns. Uses flext-core patterns exclusively with Clean
Architecture principles.

Utility Components:
    - Configuration: CLIConfig, CLISettings with FlextBaseSettings integration
    - Authentication: Token management and security operations
    - Output: Rich console formatting and display utilities
    - Common patterns: Reusable CLI utilities and helpers

Architecture:
    - Clean Architecture utility layer following infrastructure patterns
    - flext-core integration (FlextBaseSettings, FlextResult)
    - Type-safe configuration management with validation
    - Security-first authentication and token management
    - Rich console integration for enhanced UX

Current Implementation Status:
    ✅ Configuration management with FlextBaseSettings
    ✅ Authentication utilities with secure token storage
    ✅ Output formatting with Rich console integration
    ✅ flext-core pattern integration
    ✅ Type safety and comprehensive validation
    ⚠️ Clean implementation (TODO: Sprint 2 - enhance utility features)

Package Exports:
    Configuration Management:
        - CLIConfig: Main CLI configuration with validation
        - CLISettings: Settings model with environment variable support
        - get_config: Configuration factory and singleton access

Features:
    - Type-safe configuration with validation
    - Environment variable support and hierarchical config
    - Secure authentication token management
    - Rich console output formatting and utilities
    - Clean Architecture infrastructure patterns

Usage Examples:
    Configuration:
    >>> config = get_config()
    >>> config.debug = True
    >>> config.output_format = "json"

    Settings:
    >>> settings = CLISettings(debug=True, log_level="DEBUG")

Integration:
    - Used by all CLI layers for consistent utilities
    - Provides infrastructure support for Clean Architecture
    - Integrates with flext-core patterns and utilities
    - Supports configuration and authentication across CLI

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_cli.utils.config import CLIConfig, CLISettings, get_config

__all__ = [
    "CLIConfig",
    "CLISettings",
    "get_config",
]
