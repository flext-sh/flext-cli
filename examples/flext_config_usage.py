"""FLEXT CLI - Example of using FlextCliConfig with Pydantic BaseSettings.

This example demonstrates how to use FlextCliConfig with Pydantic's BaseSettings
pattern, showing environment variable loading, explicit values, and configuration methods.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import os

from flext_cli import FlextCliConfig


def main() -> None:
    """Demonstrate FlextCliConfig usage with Pydantic BaseSettings."""
    print("💻 FLEXT CLI - FlextCliConfig Pydantic BaseSettings Example")
    print("=" * 60)

    # =========================================================================
    # 1. BASIC CONFIG CREATION - Using defaults
    # =========================================================================
    print("\n📋 1. Basic Config Creation with Defaults")
    print("-" * 40)

    # Create config with default values
    config = FlextCliConfig.MainConfig()
    print(f"Profile: {config.profile}")
    print(f"Debug Mode: {config.debug_mode}")
    print(f"Output Format: {config.output_format}")

    # =========================================================================
    # 2. EXPLICIT VALUE INITIALIZATION
    # =========================================================================
    print("\n🔧 2. Explicit Value Initialization")
    print("-" * 35)

    # Create config with explicit values
    custom_config = FlextCliConfig.MainConfig(
        profile="development", output_format="json", debug=True
    )

    print(f"Custom Profile: {custom_config.profile}")
    print(f"Custom Output Format: {custom_config.output_format}")
    print(f"Custom Debug Mode: {custom_config.debug_mode}")

    # =========================================================================
    # 3. ENVIRONMENT VARIABLE LOADING (Pydantic BaseSettings feature)
    # =========================================================================
    print("\n🌍 3. Environment Variable Loading")
    print("-" * 35)

    # Set environment variables (Pydantic will auto-load these)
    os.environ["FLEXT_CLI_PROFILE"] = "production"
    os.environ["FLEXT_CLI_OUTPUT_FORMAT"] = "yaml"
    os.environ["FLEXT_CLI_DEBUG_MODE"] = "false"

    # Create new config - will automatically load from environment
    env_config = FlextCliConfig.MainConfig()

    print(f"Env Profile: {env_config.profile}")
    print(f"Env Output Format: {env_config.output_format}")
    print(f"Env Debug Mode: {env_config.debug_mode}")

    # Clean up environment
    del os.environ["FLEXT_CLI_PROFILE"]
    del os.environ["FLEXT_CLI_OUTPUT_FORMAT"]
    del os.environ["FLEXT_CLI_DEBUG_MODE"]

    # =========================================================================
    # 4. CONFIG METHODS - Using actual FlextCliConfig methods
    # =========================================================================
    print("\n🛠️ 4. Configuration Methods")
    print("-" * 30)

    config = FlextCliConfig.MainConfig(
        profile="test", output_format="table", debug=False
    )

    # Test output format validation
    validation_result = config.validate_output_format("json")
    if validation_result.is_success:
        print(f"✅ Format 'json' is valid: {validation_result.value}")

    # Test invalid format
    invalid_result = config.validate_output_format("invalid_format")
    if invalid_result.is_failure:
        print(f"❌ Invalid format rejected: {invalid_result.error}")

    # Test debug mode check
    if config.debug:
        print("Debug mode is enabled")
    else:
        print("Debug mode is disabled")

    # Test get output format
    current_format = config.output_format
    print(f"Current output format: {current_format}")

    # =========================================================================
    # 5. CONFIG DIRECTORY AND FILE PATHS
    # =========================================================================
    print("\n📁 5. Configuration Paths")
    print("-" * 25)

    config = FlextCliConfig.MainConfig()

    # Get config directory
    config_dir = config.config_dir
    print(f"Config directory: {config_dir}")

    # Get config file path
    from flext_cli.constants import FlextCliConstants
    config_file = config.config_dir / FlextCliConstants.CliDefaults.CONFIG_FILE
    print(f"Config file: {config_file}")

    # =========================================================================
    # 6. CLI OPTIONS CREATION
    # =========================================================================
    print("\n⚙️ 6. CLI Options Creation")
    print("-" * 30)

    config = FlextCliConfig.MainConfig(
        profile="staging", output_format="json", debug=True
    )

    # Create CLI options from config
    from flext_cli.constants import FlextCliConstants
    cli_options = FlextCliConfig.CliOptions(
        output_format=config.output_format,
        debug=config.debug,
        max_width=FlextCliConstants.CliDefaults.MAX_WIDTH,
        no_color=config.no_color,
    )
    print(f"CLI Options: {cli_options}")

    # =========================================================================
    # 7. LOAD CONFIGURATION (if config file exists)
    # =========================================================================
    print("\n📂 7. Load Configuration from File")
    print("-" * 35)

    config = FlextCliConfig.MainConfig()
    load_result = config.load_configuration()

    if load_result.is_success:
        loaded_config = load_result.value
        print("✅ Configuration loaded successfully")
        print(f"Loaded profile: {loaded_config.get('profile', 'N/A')}")
    else:
        print(f"i No config file found (expected for new setups): {load_result.error}")

    # =========================================================================
    # 8. OUTPUT FORMAT MANAGEMENT
    # =========================================================================
    print("\n📤 8. Output Format Management")
    print("-" * 30)

    config = FlextCliConfig.MainConfig(output_format="table")
    print(f"Initial format: {config.output_format}")

    # Change output format
    set_result = config.set_output_format("json")
    if set_result.is_success:
        print(f"✅ Format changed to: {config.output_format}")

    # Try invalid format
    invalid_set = config.set_output_format("invalid")
    if invalid_set.is_failure:
        print(f"❌ Invalid format rejected: {invalid_set.error}")

    print("\n" + "=" * 60)
    print("✅ FlextCliConfig Pydantic BaseSettings examples completed!")


if __name__ == "__main__":
    main()
