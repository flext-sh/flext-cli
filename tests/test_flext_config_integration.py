"""Copyright (c) 2025 FLEXT Team. All rights reserved.

SPDX-License-Identifier: MIT.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest
from pydantic import ValidationError

from flext_cli import FlextCliConfig, FlextCliConstants


class TestFlextConfigIntegration:
    """Test FlextConfig integration with flext-cli using actual API."""

    def setup_method(self) -> None:
        """Setup test environment."""
        # Clear environment variables that might affect configuration
        for key in os.environ.copy():
            if key.startswith("FLEXT_CLI_"):
                del os.environ[key]

    def teardown_method(self) -> None:
        """Cleanup test environment."""
        # Clean up any test environment variables
        for key in os.environ.copy():
            if key.startswith("FLEXT_CLI_"):
                del os.environ[key]

    def test_flext_config_basic_functionality(self) -> None:
        """Test that FlextCliConfig works with actual Pydantic BaseSettings API."""
        # Create CLI config using actual API
        cli_config = FlextCliConfig.MainConfig()

        # Verify CLI-specific fields are present with defaults
        assert hasattr(cli_config, "profile")
        assert hasattr(cli_config, "output_format")
        assert hasattr(cli_config, "debug_mode")

        # Test default values
        assert isinstance(cli_config.profile, str)
        assert isinstance(cli_config.output_format, str)
        assert isinstance(cli_config.debug_mode, bool)

    def test_flext_config_environment_variables(self) -> None:
        """Test that FlextCliConfig reads from environment variables."""
        # Set environment variables (with FLEXT_CLI_ prefix)
        os.environ["FLEXT_CLI_PROFILE"] = "test-profile"
        os.environ["FLEXT_CLI_OUTPUT_FORMAT"] = "json"
        os.environ["FLEXT_CLI_DEBUG"] = "true"

        # Create config (should read from environment)
        cli_config = FlextCliConfig.MainConfig()

        # Verify environment variables are loaded
        assert cli_config.profile == "test-profile"
        assert cli_config.output_format == "json"
        assert cli_config.debug_mode is True

    def test_flext_config_explicit_values(self) -> None:
        """Test FlextCliConfig with explicit constructor values."""
        # Create config with explicit values
        cli_config = FlextCliConfig.MainConfig(
            profile="explicit-profile", output_format="yaml", debug=True
        )

        # Verify explicit values are used
        assert cli_config.profile == "explicit-profile"
        assert cli_config.output_format == "yaml"
        assert cli_config.debug_mode is True

    def test_flext_config_methods(self) -> None:
        """Test actual FlextCliConfig methods."""
        cli_config = FlextCliConfig.MainConfig()

        # Test config_dir field
        config_dir = cli_config.config_dir
        assert isinstance(config_dir, Path)

        # Test config file path composition
        config_file = cli_config.config_dir / FlextCliConstants.CliDefaults.CONFIG_FILE
        assert isinstance(config_file, Path)
        assert config_file.suffix in {".json", ".toml"}  # Accept either format

    def test_output_format_validation(self) -> None:
        """Test output format validation."""
        cli_config = FlextCliConfig.MainConfig()

        # Test valid format
        result = cli_config.validate_output_format("json")
        assert result.is_success
        assert result.value == "json"

        # Test valid format
        result = cli_config.validate_output_format("table")
        assert result.is_success
        assert result.value == "table"

        # Test invalid format
        result = cli_config.validate_output_format("invalid_format")
        assert result.is_failure
        assert result.error is not None
        assert "not supported" in result.error or "Invalid" in result.error

    def test_config_model_validation(self) -> None:
        """Test Pydantic model validation."""
        # Test valid config creation
        config = FlextCliConfig.MainConfig(
            profile="test", output_format="json", debug=False
        )
        assert config.profile == "test"
        assert config.output_format == "json"
        assert config.debug_mode is False

        # Test that the model validates types properly
        with pytest.raises((ValueError, TypeError, ValidationError)):
            FlextCliConfig.MainConfig(debug="invalid_boolean")
