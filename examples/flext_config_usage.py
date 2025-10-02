"""FLEXT CLI - Example of using FlextCliConfig with Pydantic BaseSettings.

This example demonstrates how to use FlextCliConfig with Pydantic's BaseSettings
pattern, showing environment variable loading, explicit values, and configuration methods.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import os
from pathlib import Path

from flext_cli import FlextCliConfig, FlextCliConstants


def main() -> None:
    """Demonstrate FlextCliConfig usage with Pydantic BaseSettings."""
    # =========================================================================
    # 1. BASIC CONFIG CREATION - Using defaults
    # =========================================================================

    # Create config with default values
    config = FlextCliConfig()

    # =========================================================================
    # 2. EXPLICIT VALUE INITIALIZATION
    # =========================================================================

    # Create config with explicit values
    FlextCliConfig(profile="development", output_format="json", debug=True)

    # =========================================================================
    # 3. ENVIRONMENT VARIABLE LOADING (Pydantic BaseSettings feature)
    # =========================================================================

    # Set environment variables (Pydantic will auto-load these)
    os.environ["FLEXT_CLI_PROFILE"] = "production"
    os.environ["FLEXT_CLI_OUTPUT_FORMAT"] = "yaml"
    os.environ["FLEXT_CLI_DEBUG_MODE"] = "false"

    # Create new config - will automatically load from environment
    FlextCliConfig()

    # Clean up environment
    del os.environ["FLEXT_CLI_PROFILE"]
    del os.environ["FLEXT_CLI_OUTPUT_FORMAT"]
    del os.environ["FLEXT_CLI_DEBUG_MODE"]

    # =========================================================================
    # 4. CONFIG METHODS - Using actual FlextCliConfig methods
    # =========================================================================

    config = FlextCliConfig(profile="test", output_format="table", debug=False)

    # Test output format validation
    validation_result = config.validate_output_format_result("json")
    if validation_result.is_success:
        pass

    # Test invalid format
    invalid_result = config.validate_output_format_result("invalid_format")
    if invalid_result.is_failure:
        pass

    # Test debug mode check
    if config.debug:
        pass

    # Test get output format

    # =========================================================================
    # 5. CONFIG DIRECTORY AND FILE PATHS
    # =========================================================================

    config = FlextCliConfig()

    # Get config directory

    # Get config file path
    Path(config.config_dir) / FlextCliConstants.CliDefaults.CONFIG_FILE

    # =========================================================================
    # 6. CLI OPTIONS CREATION
    # =========================================================================

    config = FlextCliConfig(profile="staging", output_format="json", debug=True)

    # Create CLI options from config

    # =========================================================================
    # 7. LOAD CONFIGURATION (if config file exists)
    # =========================================================================

    config = FlextCliConfig()
    # Mock configuration loading for demonstration

    # =========================================================================
    # 8. OUTPUT FORMAT MANAGEMENT
    # =========================================================================

    config = FlextCliConfig(output_format="table")

    # Change output format by creating a new instance
    config = FlextCliConfig(output_format="json")

    # Try invalid format (mock validation)


if __name__ == "__main__":
    main()
