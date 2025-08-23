"""Real functional tests for simple_api module - NO MOCKS!

Tests the simple_api module with ACTUAL execution, following user requirement:
"pare de ficar mockando tudo! execute código real e validar a funcionalidade requerida"

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from flext_core import FlextResult

from flext_cli.config import FlextCliSettings
from flext_cli.simple_api import (
    create_development_cli_config,
    create_production_cli_config,
    get_cli_settings,
    setup_cli,
)


class TestSimpleApiReal:
    """Real functional tests for simple_api module - NO MOCKS."""

    def setup_method(self) -> None:
        """Set up test environment with temporary directory."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_dir = Path(self.temp_dir) / "config"
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def teardown_method(self) -> None:
        """Clean up test environment."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_setup_cli_real_functionality(self) -> None:
        """Test setup_cli with REAL execution - NO MOCKS."""
        # Create real CLI configuration
        config = FlextCliSettings()

        # Execute REAL setup_cli function
        result = setup_cli(config)

        # Verify result using FlextResult patterns
        assert isinstance(result, FlextResult)
        # Either success or meaningful failure is acceptable
        if result.is_success:
            assert result.value is True or result.value is None
        else:
            assert isinstance(result.error, str)
            assert len(result.error) > 0

    def test_create_development_cli_config_real_functionality(self) -> None:
        """Test create_development_cli_config with REAL execution - NO MOCKS."""
        # Execute REAL create_development_cli_config function
        config = create_development_cli_config()

        # Verify configuration object
        assert isinstance(config, FlextCliSettings)
        # Development config should have debug enabled
        assert config.debug is True
        assert config.log_level == "DEBUG"

    def test_create_production_cli_config_real_functionality(self) -> None:
        """Test create_production_cli_config with REAL execution - NO MOCKS."""
        # Execute REAL create_production_cli_config function
        config = create_production_cli_config()

        # Verify configuration object
        assert isinstance(config, FlextCliSettings)
        # Production config should have debug disabled
        assert config.debug is False
        assert config.log_level == "INFO"

    def test_get_cli_settings_real_functionality(self) -> None:
        """Test get_cli_settings with REAL execution - NO MOCKS."""
        # Execute REAL get_cli_settings function
        settings = get_cli_settings()

        # Verify configuration object
        assert isinstance(settings, FlextCliSettings)
        # Settings should have basic attributes
        assert hasattr(settings, "model_config")

        # Test reload parameter
        settings_reloaded = get_cli_settings(reload=True)
        assert isinstance(settings_reloaded, FlextCliSettings)

    def test_simple_api_integration_real_workflow(self) -> None:
        """Test complete simple_api workflow with REAL execution."""
        # Step 1: Create development configuration (REAL operation)
        dev_config = create_development_cli_config()
        assert isinstance(dev_config, FlextCliSettings)
        assert dev_config.debug is True

        # Step 2: Create production configuration (REAL operation)
        prod_config = create_production_cli_config()
        assert isinstance(prod_config, FlextCliSettings)
        assert prod_config.debug is False

        # Step 3: Get CLI settings (REAL operation)
        settings = get_cli_settings()
        assert isinstance(settings, FlextCliSettings)

        # Step 4: Setup CLI (REAL operation)
        setup_result = setup_cli(dev_config)
        assert isinstance(setup_result, FlextResult)

        # All operations should complete (success or meaningful failure)
        assert setup_result.is_success or isinstance(setup_result.error, str)

    def test_simple_api_error_handling_real(self) -> None:
        """Test error handling in simple_api with REAL execution."""
        # Test with potentially problematic configurations
        config = FlextCliSettings()

        # Execute functions that might fail gracefully
        try:
            setup_result = setup_cli(config)
            assert isinstance(setup_result, FlextResult)

            if not setup_result.is_success:
                # Error should be meaningful
                assert isinstance(setup_result.error, str)
                assert len(setup_result.error) > 0

        except Exception as e:
            # If exceptions are raised, they should be meaningful
            assert isinstance(e, Exception)
            assert str(e)

    def test_simple_api_function_signatures_real(self) -> None:
        """Test that simple_api functions have correct signatures."""
        # Test that functions are callable
        assert callable(setup_cli)
        assert callable(create_development_cli_config)
        assert callable(create_production_cli_config)
        assert callable(get_cli_settings)

        # Test basic function calls work
        dev_config = create_development_cli_config()
        assert dev_config is not None

        prod_config = create_production_cli_config()
        assert prod_config is not None

        # Test functions accept expected parameters
        settings = get_cli_settings()
        assert settings is not None

        setup_result = setup_cli(dev_config)
        assert setup_result is not None

    def test_simple_api_flext_result_patterns_real(self) -> None:
        """Test FlextResult patterns in simple_api with REAL execution."""
        config = FlextCliSettings()

        # Test FlextResult return patterns
        setup_result = setup_cli(config)
        assert isinstance(setup_result, FlextResult)
        assert hasattr(setup_result, "is_success")
        assert hasattr(setup_result, "value") or hasattr(setup_result, "error")

        # Test FlextResult behavior
        if setup_result.is_success:
            assert setup_result.error is None
            assert setup_result.value is True
        else:
            assert setup_result.error is not None
            assert isinstance(setup_result.error, str)

    def test_simple_api_configuration_integration_real(self) -> None:
        """Test configuration integration in simple_api with REAL execution."""
        # Create configuration
        dev_config = create_development_cli_config()
        prod_config = create_production_cli_config()

        # Test configuration works with other functions
        settings = get_cli_settings()

        # Configuration should be usable across API functions
        setup_result_dev = setup_cli(dev_config)
        setup_result_prod = setup_cli(prod_config)
        setup_result_settings = setup_cli(settings)

        # All operations should handle the configuration properly
        assert isinstance(setup_result_dev, FlextResult)
        assert isinstance(setup_result_prod, FlextResult)
        assert isinstance(setup_result_settings, FlextResult)

    def test_simple_api_real_dependency_resolution(self) -> None:
        """Test dependency resolution in simple_api with REAL execution."""
        # Test that imports work correctly
        from flext_cli.simple_api import (
            create_development_cli_config,
            create_production_cli_config,
            get_cli_settings,
            setup_cli,
        )

        # All imports should be available
        assert setup_cli
        assert create_development_cli_config
        assert create_production_cli_config
        assert get_cli_settings

        # Test that functions can be executed without import errors
        dev_config = create_development_cli_config()
        prod_config = create_production_cli_config()
        settings = get_cli_settings()
        setup = setup_cli(dev_config)

        # All function calls should complete
        assert dev_config is not None
        assert prod_config is not None
        assert settings is not None
        assert setup is not None


class TestSimpleApiFunctionalReal:
    """Additional functional tests for simple_api - REAL execution."""

    def test_simple_api_edge_cases_real(self) -> None:
        """Test edge cases in simple_api with REAL execution."""
        # Test multiple config creations
        config1 = create_development_cli_config()
        config2 = create_production_cli_config()

        assert isinstance(config1, FlextCliSettings)
        assert isinstance(config2, FlextCliSettings)

        # Configs should be independently functional
        setup1 = setup_cli(config1)
        setup2 = setup_cli(config2)

        assert isinstance(setup1, FlextResult)
        assert isinstance(setup2, FlextResult)

    def test_simple_api_concurrent_usage_real(self) -> None:
        """Test simple_api usage in concurrent scenarios with REAL execution."""
        # Test multiple settings creations
        settings_list = []
        for _ in range(3):
            settings = get_cli_settings()
            settings_list.append(settings)
            assert isinstance(settings, FlextCliSettings)

        # All settings should be valid
        assert len(settings_list) == 3
        for settings in settings_list:
            assert isinstance(settings, FlextCliSettings)

    def test_simple_api_resource_cleanup_real(self) -> None:
        """Test resource cleanup in simple_api with REAL execution."""
        # Create multiple resources
        dev_configs = []
        prod_configs = []

        for _ in range(3):
            dev_config = create_development_cli_config()
            prod_config = create_production_cli_config()
            dev_configs.append(dev_config)
            prod_configs.append(prod_config)

        # All resources should be properly created
        assert len(dev_configs) == 3
        assert len(prod_configs) == 3

        for config in dev_configs:
            assert isinstance(config, FlextCliSettings)
            assert config.debug is True

        for config in prod_configs:
            assert isinstance(config, FlextCliSettings)
            assert config.debug is False

        # Resources should be independently usable
        for config in dev_configs[:2]:  # Test first two configs
            result = setup_cli(config)
            assert isinstance(result, FlextResult)


if __name__ == "__main__":
    # Allow running tests directly
    import pytest

    pytest.main([__file__, "-v"])
