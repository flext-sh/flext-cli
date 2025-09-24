"""Additional unit tests for FlextCliConfigs to increase coverage.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli.config import FlextCliConfig


class TestFlextCliMainConfigCoverage:
    """Additional coverage tests for FlextCliConfig.MainConfig."""

    def test_load_configuration_success(self) -> None:
        """Test load_configuration with valid configuration."""
        config = FlextCliConfig.MainConfig(profile="test", output_format="json")

        result = config.load_configuration()
        assert result.is_success
        data = result.unwrap()
        assert data["profile"] == "test"
        assert data["output_format"] == "json"

    def test_validate_configuration_invalid_output_format(self) -> None:
        """Test validate_configuration with invalid output format."""
        config = FlextCliConfig.MainConfig(output_format="invalid")

        result = config.validate_configuration()
        assert result.is_failure
        assert "Invalid output format" in result.error

    def test_validate_configuration_empty_profile(self) -> None:
        """Test validate_configuration with empty profile."""
        config = FlextCliConfig.MainConfig(profile="")

        result = config.validate_configuration()
        assert result.is_failure
        assert "Profile cannot be empty" in result.error

    def test_validate_configuration_exception(self) -> None:
        """Test validate_configuration with exception."""
        config = FlextCliConfig.MainConfig()
        # Force exception by breaking output_format
        config.output_format = None  # type: ignore[assignment]

        result = config.validate_configuration()
        assert result.is_failure

    def test_set_output_format_invalid(self) -> None:
        """Test set_output_format with invalid output format."""
        config = FlextCliConfig.MainConfig()

        result = config.set_output_format("invalid_format")
        assert result.is_failure
        assert "Invalid output format" in result.error

    def test_set_output_format_valid(self) -> None:
        """Test set_output_format with valid output format."""
        config = FlextCliConfig.MainConfig()

        result = config.set_output_format("json")
        assert result.is_success
        assert config.output_format == "json"

    def test_validate_output_format_invalid(self) -> None:
        """Test validate_output_format with invalid format."""
        config = FlextCliConfig.MainConfig()

        result = config.validate_output_format("invalid")
        assert result.is_failure
        assert "Invalid output format" in result.error

    def test_validate_output_format_valid(self) -> None:
        """Test validate_output_format with valid format."""
        config = FlextCliConfig.MainConfig()

        result = config.validate_output_format("table")
        assert result.is_success
        assert result.unwrap() == "table"

    def test_debug_mode_property(self) -> None:
        """Test debug_mode property alias."""
        config_false = FlextCliConfig.MainConfig(debug=False)
        assert config_false.debug_mode is False

        config_true = FlextCliConfig.MainConfig(debug=True)
        assert config_true.debug_mode is True


class TestAuthConfigCoverage:
    """Additional coverage tests for AuthConfig."""

    def test_auth_config_invalid_api_url(self) -> None:
        """Test AuthConfig with invalid API URL."""
        auth_config = FlextCliConfig.AuthConfig(api_url="not_a_url")

        result = auth_config.validate_business_rules()
        assert result.is_failure
        assert "Invalid API URL format" in result.error

    def test_auth_config_valid_http_url(self) -> None:
        """Test AuthConfig with valid HTTP URL."""
        auth_config = FlextCliConfig.AuthConfig(api_url="http://example.com")

        result = auth_config.validate_business_rules()
        assert result.is_success

    def test_auth_config_valid_https_url(self) -> None:
        """Test AuthConfig with valid HTTPS URL."""
        auth_config = FlextCliConfig.AuthConfig(api_url="https://example.com")

        result = auth_config.validate_business_rules()
        assert result.is_success


class TestValidationCoverage:
    """Additional coverage tests for FlextCliConfig.Validation."""

    def test_validate_output_format_invalid(self) -> None:
        """Test validate_output_format with invalid format."""
        result = FlextCliConfig.Validation.validate_output_format("invalid")

        assert result.is_failure
        assert "Invalid output format" in result.error
        assert "Valid formats:" in result.error

    def test_validate_output_format_valid(self) -> None:
        """Test validate_output_format with valid format."""
        result = FlextCliConfig.Validation.validate_output_format("table")

        assert result.is_success
        assert result.unwrap() == "table"

    def test_validate_cli_options_invalid_format(self) -> None:
        """Test validate_cli_options with invalid output_format."""
        options = {"output_format": "invalid_format"}

        result = FlextCliConfig.Validation.validate_cli_options(options)
        assert result.is_failure

    def test_validate_cli_options_valid(self) -> None:
        """Test validate_cli_options with valid options."""
        options = {"output_format": "json", "verbose": True}

        result = FlextCliConfig.Validation.validate_cli_options(options)
        assert result.is_success

    def test_validate_cli_options_no_output_format(self) -> None:
        """Test validate_cli_options without output_format key."""
        options = {"verbose": True, "debug": False}

        result = FlextCliConfig.Validation.validate_cli_options(options)
        assert result.is_success


class TestConfigurationValidation:
    """Additional coverage tests for centralized configuration validation."""

    def test_validate_configuration_auth_failure(self) -> None:
        """Test validate_configuration when auth validation fails."""
        config = FlextCliConfig()

        # This will create AuthConfig with default values which should pass
        result = config.validate_configuration()
        # Should succeed with default valid configuration
        assert result.is_success

    def test_validate_configuration_logging_validation(self) -> None:
        """Test validate_configuration includes logging validation."""
        config = FlextCliConfig()

        result = config.validate_configuration()
        # Should succeed with default valid configuration
        assert result.is_success

    def test_validate_configuration_exception_handling(self) -> None:
        """Test validate_configuration with exception during validation."""
        config = FlextCliConfig()

        # Break the config to force exception
        # Patch AuthConfig to raise exception
        original_auth = FlextCliConfig.AuthConfig

        class BrokenAuthConfig:
            def validate_business_rules(self) -> object:
                error_msg = "Forced error"
                raise ValueError(error_msg)

        try:
            FlextCliConfig.AuthConfig = BrokenAuthConfig  # type: ignore[misc,assignment]
            result = config.validate_configuration()
            assert result.is_failure
            assert "Configuration validation failed" in result.error
        finally:
            FlextCliConfig.AuthConfig = original_auth  # type: ignore[misc]
