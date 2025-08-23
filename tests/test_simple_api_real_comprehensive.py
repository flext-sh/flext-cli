"""Comprehensive real functionality tests for simple_api.py - NO MOCKING.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

Following user requirement: "melhore bem os tests para executar codigo de verdade e validar
a funcionalidade requerida, pare de ficar mockando tudo!"

These tests execute REAL simple API functionality and validate actual business logic.
Coverage target: Increase simple_api.py from current to 90%+
"""

from __future__ import annotations

import unittest

from flext_core import FlextResult

from flext_cli.config import FlextCliSettings
from flext_cli.simple_api import (
    create_development_cli_config,
    create_production_cli_config,
    get_cli_settings,
    setup_cli,
)


class TestSetupCli(unittest.TestCase):
    """Real functionality tests for setup_cli function."""

    def test_setup_cli_with_no_config(self) -> None:
        """Test setup_cli with no configuration provided."""
        result = setup_cli()

        assert result.is_success
        success_value = result.value
        assert success_value is True

    def test_setup_cli_with_valid_config(self) -> None:
        """Test setup_cli with valid configuration provided."""
        config = FlextCliSettings(
            debug=True, log_level="DEBUG", project_name="test-project"
        )

        result = setup_cli(config)

        assert result.is_success
        success_value = result.value
        assert success_value is True

    def test_setup_cli_with_minimal_config(self) -> None:
        """Test setup_cli with minimal configuration."""
        config = FlextCliSettings()

        result = setup_cli(config)

        assert result.is_success
        success_value = result.value
        assert success_value is True

    def test_setup_cli_with_production_config(self) -> None:
        """Test setup_cli with production-style configuration."""
        config = FlextCliSettings(
            debug=False, log_level="INFO", project_name="production-app"
        )

        result = setup_cli(config)

        assert result.is_success
        success_value = result.value
        assert success_value is True

    def test_setup_cli_with_development_config(self) -> None:
        """Test setup_cli with development-style configuration."""
        config = FlextCliSettings(debug=True, log_level="DEBUG", project_name="dev-app")

        result = setup_cli(config)

        assert result.is_success
        success_value = result.value
        assert success_value is True

    def test_setup_cli_return_type_is_flext_result(self) -> None:
        """Test setup_cli returns FlextResult type."""
        result = setup_cli()

        assert isinstance(result, FlextResult)
        assert hasattr(result, "success")
        assert hasattr(result, "unwrap")
        assert hasattr(result, "error")

    def test_setup_cli_multiple_calls_consistent(self) -> None:
        """Test setup_cli works consistently across multiple calls."""
        config1 = FlextCliSettings(project_name="test1")
        config2 = FlextCliSettings(project_name="test2")

        result1 = setup_cli(config1)
        result2 = setup_cli(config2)
        result3 = setup_cli()

        assert result1.success
        assert result2.success
        assert result3.success

        # All should return True for success
        assert result1.value is True
        assert result2.value is True
        assert result3.value is True


class TestCreateDevelopmentCliConfig(unittest.TestCase):
    """Real functionality tests for create_development_cli_config function."""

    def test_create_development_config_defaults(self) -> None:
        """Test creating development config with default settings."""
        config = create_development_cli_config()

        assert isinstance(config, FlextCliSettings)
        assert config.debug is True
        assert config.log_level == "DEBUG"

    def test_create_development_config_with_overrides(self) -> None:
        """Test creating development config with override parameters."""
        config = create_development_cli_config(
            project_name="dev-test-project", api_url="http://dev.api.test:8080"
        )

        assert isinstance(config, FlextCliSettings)
        assert config.debug is True  # Still development default
        assert config.log_level == "DEBUG"  # Still development default
        assert config.project_name == "dev-test-project"
        assert config.api_url == "http://dev.api.test:8080"

    def test_create_development_config_with_debug_override(self) -> None:
        """Test creating development config with debug override."""
        config = create_development_cli_config(debug=False)

        assert isinstance(config, FlextCliSettings)
        assert config.debug is False  # Overridden
        assert config.log_level == "DEBUG"  # Still development default

    def test_create_development_config_with_log_level_override(self) -> None:
        """Test creating development config with log level override."""
        config = create_development_cli_config(log_level="WARNING")

        assert isinstance(config, FlextCliSettings)
        assert config.debug is True  # Still development default
        assert config.log_level == "WARNING"  # Overridden

    def test_create_development_config_multiple_overrides(self) -> None:
        """Test creating development config with multiple overrides."""
        config = create_development_cli_config(
            project_name="multi-override-test",
            debug=False,
            log_level="ERROR",
            api_url="http://custom.test:9000",
        )

        assert isinstance(config, FlextCliSettings)
        assert config.project_name == "multi-override-test"
        assert config.debug is False
        assert config.log_level == "ERROR"
        assert config.api_url == "http://custom.test:9000"

    def test_create_development_config_invalid_override(self) -> None:
        """Test creating development config with invalid override is ignored."""
        # Invalid fields are ignored by model_copy, doesn't raise error
        config = create_development_cli_config(invalid_field="should_fail")

        assert isinstance(config, FlextCliSettings)
        assert config.debug is True  # Development default preserved
        assert config.log_level == "DEBUG"  # Development default preserved
        # invalid_field is ignored

    def test_create_development_config_empty_overrides(self) -> None:
        """Test creating development config with empty overrides dict."""
        config = create_development_cli_config()

        assert isinstance(config, FlextCliSettings)
        assert config.debug is True
        assert config.log_level == "DEBUG"

    def test_create_development_config_type_safety(self) -> None:
        """Test development config creation maintains type safety."""
        config = create_development_cli_config(debug=True, log_level="DEBUG")

        # Verify type annotations work correctly
        assert isinstance(config.debug, bool)
        assert isinstance(config.log_level, str)
        assert isinstance(config.project_name, str)


class TestCreateProductionCliConfig(unittest.TestCase):
    """Real functionality tests for create_production_cli_config function."""

    def test_create_production_config_defaults(self) -> None:
        """Test creating production config with default settings."""
        config = create_production_cli_config()

        assert isinstance(config, FlextCliSettings)
        assert config.debug is False
        assert config.log_level == "INFO"

    def test_create_production_config_with_overrides(self) -> None:
        """Test creating production config with override parameters."""
        config = create_production_cli_config(
            project_name="prod-app", api_url="https://prod.api.company.com"
        )

        assert isinstance(config, FlextCliSettings)
        assert config.debug is False  # Still production default
        assert config.log_level == "INFO"  # Still production default
        assert config.project_name == "prod-app"
        assert config.api_url == "https://prod.api.company.com"

    def test_create_production_config_with_debug_override(self) -> None:
        """Test creating production config with debug override (unusual but allowed)."""
        config = create_production_cli_config(debug=True)

        assert isinstance(config, FlextCliSettings)
        assert config.debug is True  # Overridden to True
        assert config.log_level == "INFO"  # Still production default

    def test_create_production_config_with_log_level_override(self) -> None:
        """Test creating production config with log level override."""
        config = create_production_cli_config(log_level="ERROR")

        assert isinstance(config, FlextCliSettings)
        assert config.debug is False  # Still production default
        assert config.log_level == "ERROR"  # Overridden

    def test_create_production_config_security_focused(self) -> None:
        """Test creating production config with security-focused settings."""
        config = create_production_cli_config(
            debug=False,  # Explicit security
            log_level="WARNING",  # Reduce log verbosity
            project_name="secure-production-app",
        )

        assert isinstance(config, FlextCliSettings)
        assert config.debug is False
        assert config.log_level == "WARNING"
        assert config.project_name == "secure-production-app"

    def test_create_production_config_performance_optimized(self) -> None:
        """Test creating production config with performance optimizations."""
        config = create_production_cli_config(
            log_level="ERROR",  # Minimal logging for performance
            project_name="high-performance-app",
        )

        assert isinstance(config, FlextCliSettings)
        assert config.debug is False
        assert config.log_level == "ERROR"
        assert config.project_name == "high-performance-app"

    def test_create_production_config_invalid_override(self) -> None:
        """Test creating production config with invalid override is ignored."""
        # Invalid fields are ignored by model_copy, doesn't raise error
        config = create_production_cli_config(nonexistent_field="invalid_value")

        assert isinstance(config, FlextCliSettings)
        assert config.debug is False  # Production default preserved
        assert config.log_level == "INFO"  # Production default preserved
        # nonexistent_field is ignored

    def test_create_production_config_comparison_with_development(self) -> None:
        """Test production config has different defaults from development."""
        dev_config = create_development_cli_config()
        prod_config = create_production_cli_config()

        # Should have opposite debug settings
        assert dev_config.debug is True
        assert prod_config.debug is False

        # Should have different log levels
        assert dev_config.log_level == "DEBUG"
        assert prod_config.log_level == "INFO"


class TestGetCliSettings(unittest.TestCase):
    """Real functionality tests for get_cli_settings function."""

    def test_get_cli_settings_basic(self) -> None:
        """Test basic get_cli_settings functionality."""
        settings = get_cli_settings()

        assert isinstance(settings, FlextCliSettings)
        # Should have basic required attributes
        assert hasattr(settings, "debug")
        assert hasattr(settings, "log_level")
        assert hasattr(settings, "project_name")

    def test_get_cli_settings_with_reload_false(self) -> None:
        """Test get_cli_settings with reload=False."""
        settings1 = get_cli_settings(reload=False)
        settings2 = get_cli_settings(reload=False)

        assert isinstance(settings1, FlextCliSettings)
        assert isinstance(settings2, FlextCliSettings)
        # Both calls should work
        assert settings1.project_name == settings2.project_name

    def test_get_cli_settings_with_reload_true(self) -> None:
        """Test get_cli_settings with reload=True."""
        settings1 = get_cli_settings(reload=True)
        settings2 = get_cli_settings(reload=True)

        assert isinstance(settings1, FlextCliSettings)
        assert isinstance(settings2, FlextCliSettings)
        # Both calls should work and return valid settings
        assert hasattr(settings1, "project_name")
        assert hasattr(settings2, "project_name")

    def test_get_cli_settings_with_reload_none(self) -> None:
        """Test get_cli_settings with reload=None (default)."""
        settings = get_cli_settings(reload=None)

        assert isinstance(settings, FlextCliSettings)
        assert hasattr(settings, "debug")
        assert hasattr(settings, "log_level")

    def test_get_cli_settings_consistency(self) -> None:
        """Test get_cli_settings returns consistent types across calls."""
        settings1 = get_cli_settings()
        settings2 = get_cli_settings(reload=False)
        settings3 = get_cli_settings(reload=True)

        # All should be FlextCliSettings instances
        assert isinstance(settings1, FlextCliSettings)
        assert isinstance(settings2, FlextCliSettings)
        assert isinstance(settings3, FlextCliSettings)

        # All should have same basic structure
        for settings in [settings1, settings2, settings3]:
            assert hasattr(settings, "debug")
            assert hasattr(settings, "log_level")
            assert hasattr(settings, "project_name")
            assert hasattr(settings, "api_url")

    def test_get_cli_settings_return_value_properties(self) -> None:
        """Test get_cli_settings return value has expected properties."""
        settings = get_cli_settings()

        # Check that we can access all expected properties without errors
        assert isinstance(settings.debug, bool)
        assert isinstance(settings.log_level, str)
        assert isinstance(settings.project_name, str)
        assert isinstance(settings.api_url, str)


class TestSimpleApiIntegration(unittest.TestCase):
    """Real functionality integration tests for simple API functions."""

    def test_development_config_with_setup_cli(self) -> None:
        """Test using development config with setup_cli integration."""
        # Create development config
        dev_config = create_development_cli_config(project_name="integration-dev-test")

        # Use it with setup_cli
        result = setup_cli(dev_config)

        assert result.is_success
        assert result.value is True

        # Verify config properties were maintained
        assert dev_config.debug is True
        assert dev_config.log_level == "DEBUG"
        assert dev_config.project_name == "integration-dev-test"

    def test_production_config_with_setup_cli(self) -> None:
        """Test using production config with setup_cli integration."""
        # Create production config
        prod_config = create_production_cli_config(project_name="integration-prod-test")

        # Use it with setup_cli
        result = setup_cli(prod_config)

        assert result.is_success
        assert result.value is True

        # Verify config properties were maintained
        assert prod_config.debug is False
        assert prod_config.log_level == "INFO"
        assert prod_config.project_name == "integration-prod-test"

    def test_get_cli_settings_vs_created_configs(self) -> None:
        """Test get_cli_settings compared to manually created configs."""
        # Get settings from function
        retrieved_settings = get_cli_settings()

        # Create configs manually
        dev_config = create_development_cli_config()
        prod_config = create_production_cli_config()

        # All should be FlextCliSettings instances
        assert isinstance(retrieved_settings, FlextCliSettings)
        assert isinstance(dev_config, FlextCliSettings)
        assert isinstance(prod_config, FlextCliSettings)

        # All should have required attributes
        for config in [retrieved_settings, dev_config, prod_config]:
            assert hasattr(config, "debug")
            assert hasattr(config, "log_level")
            assert hasattr(config, "project_name")

    def test_complete_workflow_development(self) -> None:
        """Test complete development workflow with all functions."""
        # Step 1: Create development config
        config = create_development_cli_config(
            project_name="workflow-dev-test", api_url="https://internal.invalid/REDACTEDhost:8080"
        )

        # Step 2: Setup CLI with config
        setup_result = setup_cli(config)
        assert setup_result.is_success

        # Step 3: Get CLI settings
        settings = get_cli_settings()
        assert isinstance(settings, FlextCliSettings)

        # Verify development characteristics
        assert config.debug is True
        assert config.log_level == "DEBUG"
        assert config.project_name == "workflow-dev-test"

    def test_complete_workflow_production(self) -> None:
        """Test complete production workflow with all functions."""
        # Step 1: Create production config
        config = create_production_cli_config(
            project_name="workflow-prod-test", api_url="https://api.production.com"
        )

        # Step 2: Setup CLI with config
        setup_result = setup_cli(config)
        assert setup_result.is_success

        # Step 3: Get CLI settings
        settings = get_cli_settings()
        assert isinstance(settings, FlextCliSettings)

        # Verify production characteristics
        assert config.debug is False
        assert config.log_level == "INFO"
        assert config.project_name == "workflow-prod-test"

    def test_error_handling_integration(self) -> None:
        """Test error handling across integrated simple API functions."""
        # Test setup_cli with None (should work)
        setup_result = setup_cli(None)
        assert setup_result.is_success

        # Test config creation with invalid data is handled gracefully
        dev_config = create_development_cli_config(invalid_attribute="fail")
        prod_config = create_production_cli_config(another_invalid="fail")

        # Invalid attributes are ignored, configs created successfully
        assert isinstance(dev_config, FlextCliSettings)
        assert isinstance(prod_config, FlextCliSettings)

        # get_cli_settings should always work regardless
        settings = get_cli_settings()
        assert isinstance(settings, FlextCliSettings)

    def test_type_consistency_across_functions(self) -> None:
        """Test type consistency across all simple API functions."""
        # All config creation functions should return FlextCliSettings
        dev_config = create_development_cli_config()
        prod_config = create_production_cli_config()
        retrieved_settings = get_cli_settings()

        assert type(dev_config) == type(prod_config) == type(retrieved_settings)
        assert all(
            isinstance(config, FlextCliSettings)
            for config in [dev_config, prod_config, retrieved_settings]
        )

        # setup_cli should always return FlextResult[bool]
        result = setup_cli()
        assert isinstance(result, FlextResult)
        assert isinstance(result.value, bool)


if __name__ == "__main__":
    unittest.main()
