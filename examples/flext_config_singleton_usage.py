#!/usr/bin/env python3
"""FLEXT CLI Configuration Singleton Usage Example.

Demonstrates how FlextConfig serves as the single source of truth for
configuration across the CLI application, with CLI parameters modifying
behavior through the singleton pattern.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from pathlib import Path

from flext_core import FlextConfig, FlextTypes

from flext_cli import FlextCliConfig, FlextCliConstants


def demonstrate_flext_config_singleton() -> None:
    """Demonstrate FlextConfig as single source of truth."""
    # 1. Show initial FlextConfig singleton state
    FlextConfig.get_global_instance()

    # 2. Show initial FlextCliConfig.MainConfig state
    FlextCliConfig()

    # 3. Simulate CLI parameter overrides
    cli_overrides: FlextTypes.Dict = {
        "debug": True,
        "profile": "development",
        "log_level": "DEBUG",
        "output_format": "json",
    }

    for _key, _value in cli_overrides.items():
        pass

    # Apply overrides to CLI config by creating a new instance
    FlextCliConfig(
        debug=bool(cli_overrides.get("debug")),
        profile=str(cli_overrides.get("profile", "default")),
        log_level=str(cli_overrides.get("log_level", "INFO")),
        output_format=str(cli_overrides.get("output_format", "table")),
    )

    # 4. Show updated configurations
    FlextConfig.get_global_instance()


def demonstrate_environment_integration() -> None:
    """Demonstrate environment variable integration."""
    # 1. Show environment variable support

    # 2. Show current environment values

    # 3. Show integration with FlextConfig
    FlextConfig.get_global_instance()


def demonstrate_configuration_validation() -> None:
    """Demonstrate configuration validation."""
    # 1. Validate CLI configuration
    cli_config = FlextCliConfig()

    # Test output format validation
    validation_result = cli_config.validate_output_format_result("json")
    if validation_result.is_success:
        pass

    validation_result = cli_config.validate_output_format_result("invalid_format")
    if validation_result.is_success:
        pass

    # 2. Show debug status

    # 3. Show configuration directory
    (Path(cli_config.config_dir) / FlextCliConstants.CliDefaults.CONFIG_FILE)


def demonstrate_configuration_loading() -> None:
    """Demonstrate configuration loading."""
    # 1. Load configuration data
    FlextCliConfig()

    # Mock configuration loading for demonstration

    # 2. Show configuration options
    cli_options = FlextCliConfig()
    cli_options.verbose = True
    cli_options.quiet = False
    cli_options.interactive = True

    # 3. Show configuration summary


def main() -> None:
    """Main function to run all demonstrations."""
    demonstrate_flext_config_singleton()

    demonstrate_environment_integration()

    demonstrate_configuration_validation()

    demonstrate_configuration_loading()


if __name__ == "__main__":
    main()
