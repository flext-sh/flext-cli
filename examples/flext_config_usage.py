"""FLEXT CLI - Example of using FlextConfig as source of truth.

This example demonstrates how to use FlextConfig singleton pattern
in the flext-cli module, showing how parameters can change behavior
and how FlextConfig serves as the single source of truth.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import os

from flext_cli import FlextCliConfig


def main() -> None:
    """Demonstrate FlextConfig usage in flext-cli."""
    print("💻 FLEXT CLI - FlextConfig Singleton Usage Example")
    print("=" * 60)

    # =========================================================================
    # 1. BASIC SINGLETON USAGE - Get global instance
    # =========================================================================
    print("\n📋 1. Basic Singleton Usage")
    print("-" * 30)

    # Get the global singleton instance (source of truth)
    config = FlextCliConfig.get_global_instance()
    print(f"Global config instance: {config}")
    print(f"Profile: {config.profile}")
    print(f"Debug Mode: {config.debug}")
    print(f"Output Format: {config.output_format}")
    print(f"API URL: {config.api_url}")
    print(f"Log Level: {config.log_level}")

    # =========================================================================
    # 2. CLI PARAMETER OVERRIDES - Modify behavior via FlextConfig
    # =========================================================================
    print("\n🔧 2. CLI Parameter Overrides")
    print("-" * 35)

    # Simulate CLI parameters that modify behavior
    cli_params = {
        "debug": True,
        "output_format": "json",
        "log_level": "DEBUG",
        "profile": "development"
    }

    # Apply CLI overrides - this updates BOTH FlextConfig and FlextCliConfig
    override_result = FlextCliConfig.apply_cli_overrides(cli_params)
    if override_result.is_success:
        updated_config = override_result.value
        print("✅ CLI overrides applied successfully")
        print(f"Updated Debug Mode: {updated_config.debug}")
        print(f"Updated Output Format: {updated_config.output_format}")
        print(f"Updated Log Level: {updated_config.log_level}")
        print(f"Updated Profile: {updated_config.profile}")
    else:
        print(f"❌ CLI overrides failed: {override_result.error}")

    # =========================================================================
    # 3. SYNCHRONIZATION WITH FLEXT CONFIG - Ensure consistency
    # =========================================================================
    print("\n🔄 3. Synchronization with FlextConfig")
    print("-" * 40)

    # Ensure CLI config is synchronized with base FlextConfig
    sync_result = FlextCliConfig.sync_with_flext_config()
    if sync_result.is_success:
        synced_config = sync_result.value
        print("✅ Synchronization successful")
        print(f"Synchronized config: {synced_config}")
    else:
        print(f"❌ Synchronization failed: {sync_result.error}")

    # =========================================================================
    # 4. ENVIRONMENT VARIABLE OVERRIDES
    # =========================================================================
    print("\n🌍 4. Environment Variable Overrides")
    print("-" * 40)

    # Set environment variables to override configuration
    os.environ["FLEXT_CLI_PROFILE"] = "production"
    os.environ["FLEXT_CLI_DEBUG"] = "false"
    os.environ["FLEXT_CLI_OUTPUT_FORMAT"] = "json"
    os.environ["FLEXT_CLI_LOG_LEVEL"] = "INFO"
    os.environ["FLEXT_CLI_API_URL"] = "https://api.production.com"

    # Clear global instance to force reload from environment
    FlextCliConfig.clear_global_instance()

    # Get new instance with environment overrides
    env_config = FlextCliConfig.get_global_instance()
    print("Environment overridden config:")
    print(f"  Profile: {env_config.profile}")
    print(f"  Debug Mode: {env_config.debug}")
    print(f"  Output Format: {env_config.output_format}")
    print(f"  Log Level: {env_config.log_level}")
    print(f"  API URL: {env_config.api_url}")

    # =========================================================================
    # 5. FLEXT CONFIG AS SINGLE SOURCE OF TRUTH
    # =========================================================================
    print("\n🎯 5. FlextConfig as Single Source of Truth")
    print("-" * 45)

    # Demonstrate that FlextConfig is the single source of truth
    from flext_core import FlextConfig

    # Get the base FlextConfig singleton
    base_config = FlextConfig.get_global_instance()
    print("Base FlextConfig singleton:")
    print(f"  Debug: {getattr(base_config, 'debug', 'N/A')}")
    print(f"  Log Level: {getattr(base_config, 'log_level', 'N/A')}")
    print(f"  API URL: {getattr(base_config, 'api_url', 'N/A')}")

    # Show that CLI config inherits from base config
    cli_config = FlextCliConfig.get_global_instance()
    print("\nCLI config inherits from base:")
    print(f"  Debug: {cli_config.debug}")
    print(f"  Log Level: {cli_config.log_level}")
    print(f"  API URL: {cli_config.api_url}")
    print(f"  CLI-specific: Profile={cli_config.profile}, Output={cli_config.output_format}")

    # =========================================================================
    # 6. CLI PARAMETER OVERRIDES - Simulate CLI arguments
    # =========================================================================
    print("\n🖥️ 6. CLI Parameter Overrides")
    print("-" * 35)

    # Simulate CLI arguments that would override configuration
    cli_params = {
        "profile": "custom",
        "debug": True,
        "output_format": "yaml",
        "log_level": "DEBUG",
        "verbose": True,
        "api_url": "https://api.custom.com",
        "timeout": 60
    }

    # Apply CLI overrides to global configuration
    override_result = FlextCliConfig.apply_cli_overrides(cli_params)

    if override_result.is_success:
        cli_config = override_result.value
        print("CLI overrides applied:")
        print(f"  Profile: {cli_config.profile}")
        print(f"  Debug Mode: {cli_config.debug}")
        print(f"  Output Format: {cli_config.output_format}")
        print(f"  Log Level: {cli_config.log_level}")
        print(f"  Verbose: {cli_config.verbose}")
        print(f"  API URL: {cli_config.api_url}")
        print(f"  Timeout: {cli_config.timeout}")

    # =========================================================================
    # 7. CONFIGURATION VALIDATION
    # =========================================================================
    print("\n✅ 7. Configuration Validation")
    print("-" * 35)

    # Validate current CLI configuration
    validation_result = cli_config.validate_business_rules()
    if validation_result.is_success:
        print("✅ CLI configuration is valid")
    else:
        print(f"❌ CLI configuration validation failed: {validation_result.error}")

    # Validate base FlextConfig
    base_validation_result = base_config.validate_business_rules()
    if base_validation_result.is_success:
        print("✅ Base FlextConfig is valid")
    else:
        print(f"❌ Base FlextConfig validation failed: {base_validation_result.error}")

    # =========================================================================
    # 8. DIRECTORY VALIDATION
    # =========================================================================
    print("\n📁 8. Directory Validation")
    print("-" * 30)

    # Validate CLI configuration directories
    cli_config = FlextCliConfig.get_global_instance()

    # Validate directories (using ensure_directories for validation)
    dir_validation_result = cli_config.ensure_directories()
    if dir_validation_result.is_success:
        print("✅ All directories are valid and accessible")
    else:
        print(f"❌ Directory validation failed: {dir_validation_result.error}")

    # Ensure setup
    setup_result = cli_config.ensure_setup()
    if setup_result.is_success:
        print("✅ Directory setup completed successfully")
    else:
        print(f"❌ Directory setup failed: {setup_result.error}")

    # =========================================================================
    # 9. CONFIGURATION EXPORT AND SERIALIZATION
    # =========================================================================
    print("\n📤 9. Configuration Export")
    print("-" * 30)

    # Export current CLI configuration
    cli_config = FlextCliConfig.get_global_instance()

    # Export configuration as dictionary
    config_dict = cli_config.model_dump()
    print("Configuration Dictionary:")
    for key, value in config_dict.items():
        if not key.startswith("_"):  # Skip private fields
            print(f"  {key}: {value}")

    # Export as JSON
    config_json = cli_config.to_json(indent=2)
    print("\nConfiguration JSON (first 200 chars):")
    print(config_json[:200] + "..." if len(config_json) > 200 else config_json)

    # =========================================================================
    # 10. GLOBAL INSTANCE MANAGEMENT
    # =========================================================================
    print("\n🌐 10. Global Instance Management")
    print("-" * 40)

    # Set a specific configuration as global
    FlextCliConfig.set_global_instance(cli_config)
    print("✅ CLI configuration set as global instance")

    # Verify global instance
    global_config = FlextCliConfig.get_global_instance()
    print(f"Global instance Profile: {global_config.profile}")
    print(f"Global instance Debug Mode: {global_config.debug}")

    # Clear global instance
    FlextCliConfig.clear_global_instance()
    print("✅ Global instance cleared")

    # =========================================================================
    # 11. SUMMARY - FLEXT CONFIG AS SINGLE SOURCE OF TRUTH
    # =========================================================================
    print("\n🎯 11. Summary - FlextConfig as Single Source of Truth")
    print("-" * 55)

    print("✅ FlextConfig singleton integration completed successfully!")
    print("\nKey Benefits:")
    print("  • FlextConfig serves as the single source of truth")
    print("  • CLI parameters modify behavior via FlextConfig singleton")
    print("  • Automatic synchronization between base and CLI configs")
    print("  • Environment variables override base configuration")
    print("  • CLI-specific settings extend base configuration")
    print("  • Consistent configuration across entire application")

    print("\nUsage Pattern:")
    print("  1. Get base config: FlextConfig.get_global_instance()")
    print("  2. Get CLI config: FlextCliConfig.get_global_instance()")
    print("  3. Apply CLI overrides: FlextCliConfig.apply_cli_overrides()")
    print("  4. Sync configs: FlextCliConfig.sync_with_flext_config()")

    print("\n🚀 FlextConfig singleton integration is ready for production use!")
    print("\n🎉 FlextConfig usage example completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
