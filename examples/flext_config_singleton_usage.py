#!/usr/bin/env python3
"""FLEXT CLI Configuration Singleton Usage Example.

Demonstrates how FlextConfig serves as the single source of truth for
configuration across the CLI application, with CLI parameters modifying
behavior through the singleton pattern.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import os
from typing import Any

from flext_cli import FlextCliConfig
from flext_core import FlextConfig


def demonstrate_flext_config_singleton() -> None:
    """Demonstrate FlextConfig as single source of truth."""
    print("=== FLEXT CONFIG SINGLETON DEMONSTRATION ===\n")

    # 1. Show initial FlextConfig singleton state
    print("1. Initial FlextConfig Singleton State:")
    base_config = FlextConfig.get_global_instance()
    print(f"   Environment: {base_config.environment}")
    print(f"   Debug Mode: {base_config.debug}")
    print(f"   Log Level: {base_config.log_level}")
    print(f"   App Name: {base_config.app_name}")
    print(f"   Timeout: {base_config.timeout_seconds}s")
    print()

    # 2. Show initial FlextCliConfig.MainConfig state
    print("2. Initial FlextCliConfig.MainConfig State:")
    cli_config = FlextCliConfig.MainConfig()
    print(f"   Profile: {cli_config.profile}")
    print(f"   Output Format: {cli_config.output_format}")
    print(f"   Debug Mode: {cli_config.debug_mode}")
    print(f"   Log Level: {cli_config.log_level}")
    print()

    # 3. Simulate CLI parameter overrides
    print("3. Applying CLI Parameter Overrides:")
    cli_overrides: dict[str, Any] = {
        "debug": True,
        "profile": "development",
        "log_level": "DEBUG",
        "output_format": "json",
    }

    print("   CLI Parameters:")
    for key, value in cli_overrides.items():
        print(f"     {key}: {value}")

    # Apply overrides to CLI config
    cli_config.debug = cli_overrides.get("debug", False)
    cli_config.profile = cli_overrides.get("profile", "default")
    cli_config.log_level = cli_overrides.get("log_level", "INFO")
    cli_config.output_format = cli_overrides.get("output_format", "table")

    print("   ✅ Overrides applied successfully")
    print()

    # 4. Show updated configurations
    print("4. Updated FlextConfig Singleton:")
    updated_base_config = FlextConfig.get_global_instance()
    print(f"   Debug Mode: {updated_base_config.debug}")
    print(f"   Log Level: {updated_base_config.log_level}")
    print(f"   Timeout: {updated_base_config.timeout_seconds}s")
    print()

    print("5. Updated FlextCliConfig.MainConfig:")
    print(f"   Profile: {cli_config.profile}")
    print(f"   Output Format: {cli_config.output_format}")
    print(f"   Debug Mode: {cli_config.debug_mode}")
    print(f"   Log Level: {cli_config.log_level}")
    print()


def demonstrate_environment_integration() -> None:
    """Demonstrate environment variable integration."""
    print("=== ENVIRONMENT INTEGRATION ===\n")

    # 1. Show environment variable support
    print("1. Environment Variable Support:")
    print("   ✅ FLEXT_ENVIRONMENT")
    print("   ✅ FLEXT_DEBUG")
    print("   ✅ FLEXT_LOG_LEVEL")
    print("   ✅ FLEXT_TIMEOUT_SECONDS")
    print()

    # 2. Show current environment values
    print("2. Current Environment Values:")
    print(f"   FLEXT_ENVIRONMENT: {os.getenv('FLEXT_ENVIRONMENT', 'development')}")
    print(f"   FLEXT_DEBUG: {os.getenv('FLEXT_DEBUG', 'false')}")
    print(f"   FLEXT_LOG_LEVEL: {os.getenv('FLEXT_LOG_LEVEL', 'INFO')}")
    print(f"   FLEXT_TIMEOUT_SECONDS: {os.getenv('FLEXT_TIMEOUT_SECONDS', '30')}")
    print()

    # 3. Show integration with FlextConfig
    print("3. Environment Integration:")
    base_config = FlextConfig.get_global_instance()
    print(f"   Environment: {base_config.environment}")
    print(f"   Debug: {base_config.debug}")
    print(f"   Log Level: {base_config.log_level}")
    print(f"   Timeout: {base_config.timeout_seconds}s")
    print()


def demonstrate_configuration_validation() -> None:
    """Demonstrate configuration validation."""
    print("=== CONFIGURATION VALIDATION ===\n")

    # 1. Validate CLI configuration
    print("1. CLI Configuration Validation:")
    cli_config = FlextCliConfig.MainConfig()

    # Test output format validation
    validation_result = cli_config.validate_output_format("json")
    if validation_result.is_success:
        print("   ✅ JSON output format valid")
    else:
        print(f"   ❌ JSON output format invalid: {validation_result.error}")

    validation_result = cli_config.validate_output_format("invalid_format")
    if validation_result.is_success:
        print("   ✅ Invalid format accepted (unexpected)")
    else:
        print(f"   ✅ Invalid format rejected: {validation_result.error}")

    print()

    # 2. Show debug status
    print("2. Debug Status Check:")
    debug_enabled = cli_config.debug
    print(f"   Debug Enabled: {debug_enabled}")
    print(f"   Debug Mode: {cli_config.debug_mode}")
    print()

    # 3. Show configuration directory
    print("3. Configuration Directory:")
    from flext_cli.constants import FlextCliConstants
    config_dir = cli_config.config_dir
    config_file = cli_config.config_dir / FlextCliConstants.CliDefaults.CONFIG_FILE
    print(f"   Config Directory: {config_dir}")
    print(f"   Config File: {config_file}")
    print()


def demonstrate_configuration_loading() -> None:
    """Demonstrate configuration loading."""
    print("=== CONFIGURATION LOADING ===\n")

    # 1. Load configuration data
    print("1. Loading Configuration Data:")
    cli_config = FlextCliConfig.MainConfig()

    load_result = cli_config.load_configuration()
    if load_result.is_success:
        print("   ✅ Configuration loaded successfully")
        config_data = load_result.value
        print(f"   Profile: {config_data.get('profile', 'unknown')}")
        print(f"   Output Format: {config_data.get('output_format', 'unknown')}")
        print(f"   Debug Mode: {config_data.get('debug_mode', 'unknown')}")
    else:
        print(f"   ❌ Configuration load failed: {load_result.error}")

    print()

    # 2. Show configuration options
    print("2. Configuration Options:")
    from flext_cli.constants import FlextCliConstants
    cli_options = FlextCliConfig.CliOptions(
        output_format=cli_config.output_format,
        debug=cli_config.debug,
        max_width=FlextCliConstants.CliDefaults.MAX_WIDTH,
        no_color=cli_config.no_color,
    )
    print(f"   CLI Options Created: {type(cli_options).__name__}")
    print()

    # 3. Show configuration summary
    print("3. Configuration Summary:")
    print(f"   Profile: {cli_config.profile}")
    print(f"   Output Format: {cli_config.output_format}")
    print(f"   Debug Mode: {cli_config.debug_mode}")
    print(f"   Log Level: {cli_config.log_level}")
    print(f"   Project Name: {cli_config.project_name}")
    print()


def main() -> None:
    """Main function to run all demonstrations."""
    print("FLEXT CLI Configuration Singleton Usage Examples")
    print("=" * 55)
    print()

    try:
        demonstrate_flext_config_singleton()
        print()

        demonstrate_environment_integration()
        print()

        demonstrate_configuration_validation()
        print()

        demonstrate_configuration_loading()
        print()

        print("🎉 All demonstrations completed successfully!")

    except Exception as e:
        print(f"❌ Error during demonstration: {e}")
        raise


if __name__ == "__main__":
    main()
