#!/usr/bin/env python3
"""FLEXT CLI Global Configuration Refactoring Example.

Demonstrates how all modules now use FlextConfig singleton as the
SINGLE SOURCE OF TRUTH for configuration, eliminating all other
configuration patterns and ensuring consistency across the entire
CLI application.

This example shows:
1. FlextConfig singleton as the only configuration source
2. All modules (API, Auth) using FlextConfig
3. Dynamic configuration updates across all modules
4. CLI parameters modifying behavior through FlextConfig
5. Elimination of duplicate configuration patterns

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import FlextConfig

from flext_cli import FlextCli, FlextCliAuth, FlextCliConfig


def demonstrate_global_configuration_refactoring() -> None:
    """Demonstrate global configuration refactoring across all modules."""
    # 1. Show FlextConfig as SINGLE SOURCE OF TRUTH
    base_config = FlextConfig.get_global_instance()
    cli_config = FlextCliConfig()

    # 2. Initialize all modules using FlextConfig singleton

    # Initialize CLI API
    cli_api = FlextCli()

    # Initialize CLI Auth
    FlextCliAuth()

    # 3. Apply CLI parameter overrides
    cli_overrides: dict[str, object] = {
        "debug": True,
        "log_level": "DEBUG",
        "output_format": "json",
    }

    for _key, _value in cli_overrides.items():
        pass

    # Apply overrides to CLI config by creating a new instance
    cli_config = FlextCliConfig(
        debug=bool(cli_overrides["debug"]),
        log_level=str(cli_overrides["log_level"]),
        output_format=str(cli_overrides["output_format"]),
    )

    # 4. Demonstrate configuration usage

    # Show debug status

    # Show output format

    # Show config directory

    # 5. Show integration with CLI API

    # Create sample data for API demonstration
    sample_data: dict[str, dict[str, object]] = {
        "config": {
            "environment": base_config.environment,
            "debug": base_config.debug,
            "log_level": base_config.log_level,
        },
        "cli": {
            "profile": cli_config.profile,
            "debug": cli_config.debug,
            "output_format": cli_config.output_format,
        },
    }

    # Format data using CLI API
    formatted_result = cli_api.format_data(sample_data, "json")
    if formatted_result.is_success:
        pass


def demonstrate_elimination_of_duplicate_patterns() -> None:
    """Demonstrate elimination of duplicate configuration patterns."""


def demonstrate_dynamic_configuration_updates() -> None:
    """Demonstrate dynamic configuration updates across all modules."""
    # Get current configuration
    FlextConfig.get_global_instance()
    cli_config = FlextCliConfig()

    # Simulate dynamic updates

    # Update CLI config by creating a new instance
    cli_config = FlextCliConfig(debug=True, output_format="yaml", log_level="INFO")

    # Demonstrate API integration with updated config

    cli_api = FlextCli()
    sample_data = {"updated_config": cli_config.model_dump()}

    formatted_result = cli_api.format_data(sample_data, cli_config.output_format)
    if formatted_result.is_success:
        pass


def demonstrate_cli_parameter_integration() -> None:
    """Demonstrate CLI parameter integration with FlextConfig."""
    # Simulate CLI parameters
    cli_params: dict[str, object] = {
        "debug": True,
        "log_level": "DEBUG",
        "output_format": "table",
        "profile": "development",
    }

    for _key, _value in cli_params.items():
        pass

    # Apply parameters to configuration

    cli_config = FlextCliConfig()

    # Apply CLI overrides by creating a new instance
    cli_config = FlextCliConfig(
        debug=bool(cli_params["debug"]),
        log_level=str(cli_params["log_level"]),
        output_format=str(cli_params["output_format"]),
        profile=str(cli_params["profile"]),
    )

    # Demonstrate usage with CLI parameters

    cli_api = FlextCli()
    sample_data: dict[str, object] = {
        "cli_params": cli_params,
        "final_config": cli_config.model_dump(),
    }

    formatted_result = cli_api.format_data(sample_data, cli_config.output_format)
    if formatted_result.is_success:
        pass


def main() -> None:
    """Main function to run all demonstrations."""
    demonstrate_global_configuration_refactoring()

    demonstrate_elimination_of_duplicate_patterns()

    demonstrate_dynamic_configuration_updates()

    demonstrate_cli_parameter_integration()


if __name__ == "__main__":
    main()
