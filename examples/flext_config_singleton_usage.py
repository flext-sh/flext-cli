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

from flext_core import FlextConfig

from flext_cli.config import FlextCliConfig


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

    # 2. Show initial FlextCliConfig state
    print("2. Initial FlextCliConfig State:")
    cli_config = FlextCliConfig.get_global_instance()
    print(f"   Profile: {cli_config.profile}")
    print(f"   Output Format: {cli_config.output_format}")
    print(f"   API URL: {cli_config.api_url}")
    print(f"   Command Timeout: {cli_config.command_timeout}s")
    print()

    # 3. Simulate CLI parameter overrides
    print("3. Applying CLI Parameter Overrides:")
    cli_overrides = {
        "debug": True,
        "profile": "development",
        "log_level": "DEBUG",
        "output_format": "json",
        "command_timeout": 60,
    }

    print("   CLI Parameters:")
    for key, value in cli_overrides.items():
        print(f"     {key}: {value}")

    # Apply overrides to FlextConfig singleton
    result = FlextCliConfig.apply_cli_overrides(cli_overrides)
    if result.is_failure:
        print(f"   Error: {result.error}")
        return

    print("   ✅ Overrides applied successfully")
    print()

    # 4. Show updated configurations
    print("4. Updated FlextConfig Singleton State:")
    updated_base_config = FlextConfig.get_global_instance()
    print(f"   Environment: {updated_base_config.environment}")
    print(f"   Debug Mode: {updated_base_config.debug}")
    print(f"   Log Level: {updated_base_config.log_level}")
    print(f"   App Name: {updated_base_config.app_name}")
    print(f"   Timeout: {updated_base_config.timeout_seconds}s")
    print()

    print("5. Updated FlextCliConfig State:")
    updated_cli_config = FlextCliConfig.get_global_instance()
    print(f"   Profile: {updated_cli_config.profile}")
    print(f"   Output Format: {updated_cli_config.output_format}")
    print(f"   API URL: {updated_cli_config.api_url}")
    print(f"   Command Timeout: {updated_cli_config.command_timeout}s")
    print()

    # 5. Demonstrate synchronization
    print("6. Configuration Synchronization:")
    sync_result = FlextCliConfig.sync_with_flext_config()
    if sync_result.is_success:
        print("   ✅ Configurations synchronized successfully")
        synced_config = sync_result.value
        print(f"   Synchronized Profile: {synced_config.profile}")
        print(f"   Synchronized Debug: {synced_config.debug}")
    else:
        print(f"   ❌ Synchronization failed: {sync_result.error}")
    print()


def demonstrate_environment_integration() -> None:
    """Demonstrate environment variable integration."""
    print("=== ENVIRONMENT INTEGRATION DEMONSTRATION ===\n")

    # Set some environment variables
    os.environ["FLEXT_DEBUG"] = "true"
    os.environ["FLEXT_LOG_LEVEL"] = "WARNING"
    os.environ["FLEXT_CLI_PROFILE"] = "production"
    os.environ["FLEXT_CLI_OUTPUT_FORMAT"] = "yaml"

    print("1. Environment Variables Set:")
    print("   FLEXT_DEBUG=true")
    print("   FLEXT_LOG_LEVEL=WARNING")
    print("   FLEXT_CLI_PROFILE=production")
    print("   FLEXT_CLI_OUTPUT_FORMAT=yaml")
    print()

    # Clear singleton instances to force reload from environment
    FlextConfig.clear_global_instance()
    FlextCliConfig.clear_global_instance()

    # Reload configurations
    print("2. Reloading Configurations from Environment:")
    base_config = FlextConfig.get_global_instance()
    cli_config = FlextCliConfig.get_global_instance()

    print("   FlextConfig (from FLEXT_* env vars):")
    print(f"     Debug: {base_config.debug}")
    print(f"     Log Level: {base_config.log_level}")

    print("   FlextCliConfig (from FLEXT_CLI_* env vars):")
    print(f"     Profile: {cli_config.profile}")
    print(f"     Output Format: {cli_config.output_format}")
    print()

    # Clean up environment variables
    for key in [
        "FLEXT_DEBUG",
        "FLEXT_LOG_LEVEL",
        "FLEXT_CLI_PROFILE",
        "FLEXT_CLI_OUTPUT_FORMAT",
    ]:
        os.environ.pop(key, None)


def demonstrate_cli_parameter_priority() -> None:
    """Demonstrate CLI parameter priority over environment variables."""
    print("=== CLI PARAMETER PRIORITY DEMONSTRATION ===\n")

    # Set environment variables
    os.environ["FLEXT_CLI_DEBUG"] = "false"
    os.environ["FLEXT_CLI_LOG_LEVEL"] = "INFO"

    print("1. Environment Variables:")
    print("   FLEXT_CLI_DEBUG=false")
    print("   FLEXT_CLI_LOG_LEVEL=INFO")

    # Clear and reload
    FlextCliConfig.clear_global_instance()
    env_config = FlextCliConfig.get_global_instance()

    print("2. Configuration from Environment:")
    print(f"   Debug: {env_config.debug}")
    print(f"   Log Level: {env_config.log_level}")
    print()

    # Apply CLI overrides (higher priority)
    print("3. Applying CLI Overrides (Higher Priority):")
    cli_overrides = {
        "debug": True,
        "log_level": "DEBUG",
    }

    result = FlextCliConfig.apply_cli_overrides(cli_overrides)
    if result.is_success:
        updated_config = result.value
        print("   ✅ CLI overrides applied")
        print("4. Final Configuration (CLI overrides environment):")
        print(f"   Debug: {updated_config.debug}")
        print(f"   Log Level: {updated_config.log_level}")
    else:
        print(f"   ❌ Failed to apply CLI overrides: {result.error}")

    # Clean up
    for key in ["FLEXT_CLI_DEBUG", "FLEXT_CLI_LOG_LEVEL"]:
        os.environ.pop(key, None)
    print()


def demonstrate_configuration_validation() -> None:
    """Demonstrate configuration validation."""
    print("=== CONFIGURATION VALIDATION DEMONSTRATION ===\n")

    # Test valid configuration
    print("1. Valid Configuration:")
    valid_overrides = {
        "debug": True,
        "log_level": "DEBUG",
        "output_format": "json",
        "command_timeout": 30,
    }

    result = FlextCliConfig.apply_cli_overrides(valid_overrides)
    if result.is_success:
        print("   ✅ Valid configuration accepted")
    else:
        print(f"   ❌ Valid configuration rejected: {result.error}")
    print()

    # Test invalid configuration
    print("2. Invalid Configuration:")
    invalid_overrides = {
        "debug": True,
        "log_level": "INVALID_LEVEL",  # Invalid log level
        "output_format": "invalid_format",  # Invalid output format
        "command_timeout": -1,  # Invalid timeout
    }

    result = FlextCliConfig.apply_cli_overrides(invalid_overrides)
    if result.is_failure:
        print("   ✅ Invalid configuration properly rejected")
        print(f"   Error: {result.error}")
    else:
        print("   ❌ Invalid configuration was accepted (unexpected)")
    print()


def main() -> None:
    """Main demonstration function."""
    print("FLEXT CLI Configuration Singleton Usage Example")
    print("=" * 50)
    print()

    try:
        demonstrate_flext_config_singleton()
        demonstrate_environment_integration()
        demonstrate_cli_parameter_priority()
        demonstrate_configuration_validation()

        print("=== SUMMARY ===")
        print("✅ FlextConfig serves as single source of truth")
        print("✅ CLI parameters override configuration values")
        print("✅ Environment variables are automatically loaded")
        print("✅ Configuration validation prevents invalid states")
        print("✅ Synchronization maintains consistency between configs")
        print()
        print("The FlextConfig singleton pattern ensures:")
        print("- Single source of truth for all configuration")
        print("- CLI parameters modify behavior through overrides")
        print("- Environment integration with proper priority")
        print("- Type-safe validation and error handling")
        print("- Consistent state across the application")

    except Exception as e:
        print(f"❌ Demonstration failed: {e}")
        raise


if __name__ == "__main__":
    main()
