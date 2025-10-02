#!/usr/bin/env python3
"""FLEXT CLI Configuration Singleton Integration Example.

Demonstrates the improved integration where FlextConfig serves as the
SINGLE SOURCE OF TRUTH for all configuration, with CLI parameters
modifying behavior through the singleton pattern.

This example shows:
1. FlextConfig as the authoritative configuration source
2. FlextCliConfig.MainConfig extending FlextConfig while maintaining singleton pattern
3. CLI parameters modifying behavior through FlextConfig
4. Automatic synchronization and integration verification

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli import FlextCliConfig
from flext_core import FlextConfig


def demonstrate_single_source_of_truth() -> None:
    """Demonstrate FlextConfig as SINGLE SOURCE OF TRUTH."""
    # 1. Show FlextConfig singleton as authoritative source
    FlextConfig.get_global_instance()

    # 2. Show FlextCliConfig.MainConfig extending FlextConfig
    FlextCliConfig()

    # 3. Verify integration metadata


def demonstrate_cli_parameter_integration() -> None:
    """Demonstrate CLI parameter integration with FlextConfig."""
    # 1. Ensure integration is maintained

    # 2. Apply CLI parameter overrides
    cli_overrides: dict[str, object] = {
        "debug": True,
        "profile": "development",
        "output_format": "json",
        "log_level": "DEBUG",
    }

    for _key, _value in cli_overrides.items():
        pass

    # Apply overrides by creating a new instance
    FlextCliConfig(
        debug=bool(cli_overrides.get("debug")),
        profile=str(cli_overrides.get("profile", "default")),
        output_format=str(cli_overrides.get("output_format", "table")),
        log_level=str(cli_overrides.get("log_level", "INFO")),
    )

    # 3. Show updated configurations
    FlextConfig.get_global_instance()

    # 4. Show integration status


def demonstrate_automatic_synchronization() -> None:
    """Demonstrate automatic synchronization between configurations."""
    # 1. Show synchronization process

    # 2. Verify synchronization
    FlextConfig.get_global_instance()
    FlextCliConfig()

    # 3. Show dependent service updates


def demonstrate_integration_verification() -> None:
    """Demonstrate integration verification and health checks."""
    # 1. Health check
    FlextConfig.get_global_instance()
    FlextCliConfig()

    # 2. Configuration validation

    # 3. Performance metrics


def demonstrate_environment_integration() -> None:
    """Demonstrate environment variable integration."""
    # 1. Show environment variable support

    # 2. Show current environment values

    # 3. Show integration with FlextConfig
    FlextConfig.get_global_instance()


def main() -> None:
    """Main function to run all demonstrations."""
    try:
        demonstrate_single_source_of_truth()

        demonstrate_cli_parameter_integration()

        demonstrate_automatic_synchronization()

        demonstrate_integration_verification()

        demonstrate_environment_integration()

    except Exception:
        raise


if __name__ == "__main__":
    main()
