#!/usr/bin/env python3
"""FLEXT CLI Configuration Singleton Integration Example.

Demonstrates the improved integration where FlextConfig serves as the
SINGLE SOURCE OF TRUTH for all configuration, with CLI parameters
modifying behavior through the singleton pattern.

This example shows:
1. FlextConfig as the authoritative configuration source
2. FlextCliConfigs extending FlextConfig while maintaining singleton pattern
3. CLI parameters modifying behavior through FlextConfig
4. Automatic synchronization and integration verification

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import os

from flext_cli.configs import FlextCliConfigs
from flext_core import FlextConfig


def demonstrate_single_source_of_truth() -> None:
    """Demonstrate FlextConfig as SINGLE SOURCE OF TRUTH."""
    print("=== FLEXT CONFIG AS SINGLE SOURCE OF TRUTH ===\n")

    # 1. Show FlextConfig singleton as authoritative source
    print("1. FlextConfig Singleton (SINGLE SOURCE OF TRUTH):")
    base_config = FlextConfig.get_global_instance()
    print(f"   Environment: {base_config.environment}")
    print(f"   Debug Mode: {base_config.debug}")
    print(f"   Log Level: {base_config.log_level}")
    print(f"   App Name: {base_config.app_name}")
    print(f"   Timeout: {base_config.timeout_seconds}s")
    print()

    # 2. Show FlextCliConfigs extending FlextConfig
    print("2. FlextCliConfigs Extends FlextConfig:")
    cli_config = FlextCliConfigs.get_global_instance()
    print(f"   Profile: {cli_config.profile}")
    print(f"   Output Format: {cli_config.output_format}")
    print(f"   API URL: {cli_config.api_url}")
    print(f"   Command Timeout: {cli_config.command_timeout}s")
    print()

    # 3. Verify integration metadata
    print("3. Integration Metadata:")
    metadata = cli_config.get_metadata()
    print(
        f"   Base Config Source: {metadata.get('base_config_source', 'unknown')}"
    )
    print(
        f"   CLI Extensions Applied: {metadata.get('cli_extensions_applied', 'false')}"
    )
    print(f"   Override Count: {metadata.get('override_count', '0')}")
    print()


def demonstrate_cli_parameter_integration() -> None:
    """Demonstrate CLI parameter integration with FlextConfig."""
    print("=== CLI PARAMETER INTEGRATION ===\n")

    # 1. Ensure integration is maintained
    print("1. Ensuring FlextConfig Integration:")
    integration_result = FlextCliConfigs.ensure_flext_config_integration()
    if integration_result.is_success:
        print("   ✅ Integration verified")
    else:
        print(f"   ❌ Integration failed: {integration_result.error}")
        return
    print()

    # 2. Apply CLI parameter overrides
    print("2. Applying CLI Parameter Overrides:")
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

    # Apply overrides
    result = FlextCliConfigs.apply_cli_overrides(cli_overrides)
    if result.is_failure:
        print(f"   ❌ Failed to apply overrides: {result.error}")
        return

    print("   ✅ Overrides applied successfully")
    print()

    # 3. Show updated configurations
    print("3. Updated FlextConfig Singleton:")
    updated_base_config = FlextConfig.get_global_instance()
    print(f"   Debug Mode: {updated_base_config.debug}")
    print(f"   Log Level: {updated_base_config.log_level}")
    print(f"   Timeout: {updated_base_config.timeout_seconds}s")
    print()

    print("4. Updated FlextCliConfigs:")
    updated_cli_config = FlextCliConfigs.get_global_instance()
    print(f"   Profile: {updated_cli_config.profile}")
    print(f"   Output Format: {updated_cli_config.output_format}")
    print(f"   Command Timeout: {updated_cli_config.command_timeout}s")
    print()

    # 4. Show integration metadata
    print("5. Integration Status:")
    updated_metadata = updated_cli_config.get_metadata()
    print(
        f"   CLI Overrides Applied: {updated_metadata.get('cli_overrides_applied', 'false')}"
    )
    print(
        f"   Override Count: {updated_metadata.get('override_count', '0')}"
    )
    print(
        f"   Base Config Synchronized: {updated_metadata.get('base_config_synchronized', 'false')}"
    )
    print()


def demonstrate_environment_integration() -> None:
    """Demonstrate environment variable integration."""
    print("=== ENVIRONMENT INTEGRATION ===\n")

    # Set environment variables
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
    FlextCliConfigs.clear_global_instance()

    print("2. Reloading from Environment:")
    base_config = FlextConfig.get_global_instance()
    cli_config = FlextCliConfigs.get_global_instance()

    print("   FlextConfig (from FLEXT_* env vars):")
    print(f"     Debug: {base_config.debug}")
    print(f"     Log Level: {base_config.log_level}")

    print("   FlextCliConfigs (from FLEXT_CLI_* env vars):")
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


def demonstrate_priority_hierarchy() -> None:
    """Demonstrate configuration priority hierarchy."""
    print("=== CONFIGURATION PRIORITY HIERARCHY ===\n")

    # Set environment variables (lower priority)
    os.environ["FLEXT_CLI_DEBUG"] = "false"
    os.environ["FLEXT_CLI_LOG_LEVEL"] = "INFO"

    print("1. Environment Variables (Lower Priority):")
    print("   FLEXT_CLI_DEBUG=false")
    print("   FLEXT_CLI_LOG_LEVEL=INFO")

    # Clear and reload
    FlextCliConfigs.clear_global_instance()
    env_config = FlextCliConfigs.get_global_instance()

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

    result = FlextCliConfigs.apply_cli_overrides(cli_overrides)
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


def demonstrate_validation_and_error_handling() -> None:
    """Demonstrate validation and error handling."""
    print("=== VALIDATION AND ERROR HANDLING ===\n")

    # Test valid configuration
    print("1. Valid Configuration:")
    valid_overrides = {
        "debug": True,
        "log_level": "DEBUG",
        "output_format": "json",
        "command_timeout": 30,
    }

    result = FlextCliConfigs.apply_cli_overrides(valid_overrides)
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

    result = FlextCliConfigs.apply_cli_overrides(invalid_overrides)
    if result.is_failure:
        print("   ✅ Invalid configuration properly rejected")
        print(f"   Error: {result.error}")
    else:
        print("   ❌ Invalid configuration was accepted (unexpected)")
    print()


def demonstrate_synchronization() -> None:
    """Demonstrate configuration synchronization."""
    print("=== CONFIGURATION SYNCHRONIZATION ===\n")

    # Get initial configurations
    base_config = FlextConfig.get_global_instance()
    cli_config = FlextCliConfigs.get_global_instance()

    print("1. Initial Configurations:")
    print(f"   FlextConfig Debug: {base_config.debug}")
    print(f"   FlextCliConfigs Debug: {cli_config.debug}")
    print()

    # Apply CLI overrides
    cli_overrides = {"debug": True, "log_level": "DEBUG"}
    result = FlextCliConfigs.apply_cli_overrides(cli_overrides)

    if result.is_success:
        print("2. After CLI Overrides:")
        updated_base = FlextConfig.get_global_instance()
        updated_cli = FlextCliConfigs.get_global_instance()

        print(f"   FlextConfig Debug: {updated_base.debug}")
        print(f"   FlextCliConfigs Debug: {updated_cli.debug}")
        print(f"   Synchronized: {updated_base.debug == updated_cli.debug}")
        print()

        # Test synchronization method
        print("3. Manual Synchronization:")
        sync_result = FlextCliConfigs.sync_with_flext_config()
        if sync_result.is_success:
            synced_config = sync_result.value
            print("   ✅ Synchronization successful")
            print(f"   Synced Debug: {synced_config.debug}")
        else:
            print(f"   ❌ Synchronization failed: {sync_result.error}")
    else:
        print(f"   ❌ Failed to apply CLI overrides: {result.error}")
    print()


def main() -> None:
    """Main demonstration function."""
    print("FLEXT CLI Configuration Singleton Integration Example")
    print("=" * 60)
    print()

    try:
        demonstrate_single_source_of_truth()
        demonstrate_cli_parameter_integration()
        demonstrate_environment_integration()
        demonstrate_priority_hierarchy()
        demonstrate_validation_and_error_handling()
        demonstrate_synchronization()

        print("=== SUMMARY ===")
        print("✅ FlextConfig serves as SINGLE SOURCE OF TRUTH")
        print("✅ FlextCliConfigs extends FlextConfig while maintaining singleton")
        print("✅ CLI parameters modify behavior through FlextConfig")
        print("✅ Environment variables integrate automatically")
        print("✅ Configuration validation prevents invalid states")
        print("✅ Synchronization maintains consistency")
        print("✅ Integration verification ensures proper operation")
        print()
        print("The improved singleton pattern ensures:")
        print("- FlextConfig is the authoritative configuration source")
        print("- CLI parameters modify behavior through FlextConfig singleton")
        print("- Automatic synchronization between configurations")
        print("- Integration verification and metadata tracking")
        print("- Type-safe validation and error handling")
        print("- Consistent state across the entire application")

    except Exception as e:
        print(f"❌ Demonstration failed: {e}")
        raise


if __name__ == "__main__":
    main()
