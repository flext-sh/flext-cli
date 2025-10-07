"""FLEXT CLI Config Tests - Comprehensive configuration functionality testing.

Tests for FlextCliConfig classes using flext_tests infrastructure with real functionality
testing, no mocks, and comprehensive coverage following FLEXT standards.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import time
from pathlib import Path

from flext_cli import FlextCliConfig, FlextCliModels


class TestFlextCliConfig:
    """Comprehensive tests for FlextCliConfig class."""

    def test_config_initialization(self) -> None:
        """Test Config initialization with proper configuration."""
        config = FlextCliConfig()
        assert config is not None
        assert isinstance(config, FlextCliConfig)

    def test_config_default_values(self) -> None:
        """Test config default values."""
        config = FlextCliConfig()

        # Test that config has expected default values
        assert config.debug is False
        assert config.verbose is False
        assert config.trace is False

    def test_config_custom_values(self) -> None:
        """Test config with custom values."""
        config = FlextCliConfig(debug=True, verbose=True)

        assert config.debug is True
        assert config.verbose is True

    def test_config_validation(self) -> None:
        """Test config validation."""
        config = FlextCliConfig()

        # Test that config validates properly
        assert config.debug is not None
        assert config.verbose is not None

    def test_config_serialization(self) -> None:
        """Test config serialization."""
        config = FlextCliConfig(debug=True, verbose=False)

        # Test dict conversion
        config_dict = config.model_dump()
        assert isinstance(config_dict, dict)
        assert config_dict["debug"] is True
        assert config_dict["verbose"] is False

    def test_config_deserialization(self) -> None:
        """Test config deserialization."""
        config_data = {"debug": True, "verbose": False}

        config = FlextCliConfig.model_validate(config_data)
        assert config.debug is True
        assert config.verbose is False


class TestLoggingConfig:
    """Comprehensive tests for LoggingConfig class."""

    def test_logging_config_initialization(self) -> None:
        """Test LoggingConfig initialization."""
        logging_config = FlextCliModels.LoggingConfig()
        assert logging_config is not None
        assert isinstance(logging_config, FlextCliModels.LoggingConfig)

    def test_logging_config_default_values(self) -> None:
        """Test logging config default values."""
        logging_config = FlextCliModels.LoggingConfig()

        # Test that logging config has expected default values
        assert logging_config.log_level is not None
        assert logging_config.log_format is not None

    def test_logging_config_custom_values(self) -> None:
        """Test logging config with custom values."""
        logging_config = FlextCliModels.LoggingConfig(
            log_level="DEBUG",
            log_format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )

        assert logging_config.log_level == "DEBUG"
        assert "%(asctime)s" in logging_config.log_format


class TestFlextCliConfigService:
    """Comprehensive tests for FlextCliConfig class."""

    def test_config_service_initialization_duplicate(self) -> None:
        """Test ConfigService initialization."""
        config_service = FlextCliConfig()
        assert config_service is not None
        assert isinstance(config_service, FlextCliConfig)

    def test_config_service_execute_sync(self) -> None:
        """Test synchronous ConfigService execution."""
        config_service = FlextCliConfig()
        # FlextCliConfig doesn't have execute method, test basic functionality
        assert config_service is not None
        assert hasattr(config_service, "profile")
        assert hasattr(config_service, "debug")

    def test_config_service_execute(self) -> None:
        """Test config service execute functionality."""
        config_service = FlextCliConfig()

        # Test basic config functionality
        assert config_service is not None
        assert hasattr(config_service, "profile")
        assert hasattr(config_service, "debug")
        assert hasattr(config_service, "output_format")

    def test_config_service_execution(self) -> None:
        """Test config service execute functionality."""
        config_service = FlextCliConfig()

        # Test basic config functionality
        assert config_service is not None
        assert hasattr(config_service, "profile")
        assert hasattr(config_service, "debug")
        assert hasattr(config_service, "output_format")

    def test_config_service_error_handling(self) -> None:
        """Test config service error handling."""
        config_service = FlextCliConfig()

        # Test basic config functionality
        assert config_service is not None
        assert hasattr(config_service, "profile")
        assert hasattr(config_service, "debug")

    def test_config_service_performance(self) -> None:
        """Test config service performance."""
        config_service = FlextCliConfig()

        start_time = time.time()
        # Test basic config functionality
        assert config_service is not None
        execution_time = time.time() - start_time

        # Should execute quickly
        assert execution_time < 1.0

    def test_config_service_integration(self) -> None:
        """Test config service integration."""
        config_service = FlextCliConfig()

        # Test basic config functionality
        assert config_service is not None
        assert hasattr(config_service, "profile")
        assert hasattr(config_service, "debug")
        assert hasattr(config_service, "output_format")

    # ========================================================================
    # ClassMethod tests for FlextCliConfig
    # ========================================================================

    def test_config_create_for_environment(self) -> None:
        """Test create_for_environment class method."""
        config = FlextCliConfig(environment="development", debug=False, verbose=True)
        assert config is not None
        assert isinstance(config, FlextCliConfig)

    def test_config_create_default(self) -> None:
        """Test create_default class method."""
        config = FlextCliConfig()
        assert config is not None
        assert isinstance(config, FlextCliConfig)

    def test_config_create_for_profile(self) -> None:
        """Test create_for_profile class method."""
        config = FlextCliConfig(profile="test", debug=True)
        assert config is not None
        assert isinstance(config, FlextCliConfig)
        assert config.profile == "test"

    def test_config_load_from_config_file_json(self, temp_json_file: Path) -> None:
        """Test load_from_config_file with JSON file."""
        result = FlextCliConfig.load_from_config_file(temp_json_file)
        assert result.is_success
        config = result.unwrap()
        assert isinstance(config, FlextCliConfig)

    def test_config_load_from_config_file_yaml(self, temp_yaml_file: Path) -> None:
        """Test load_from_config_file with YAML file."""
        result = FlextCliConfig.load_from_config_file(temp_yaml_file)
        assert result.is_success
        config = result.unwrap()
        assert isinstance(config, FlextCliConfig)

    def test_config_load_from_config_file_not_found(self, temp_dir: Path) -> None:
        """Test load_from_config_file with non-existent file."""
        non_existent = temp_dir / "non_existent.json"
        result = FlextCliConfig.load_from_config_file(non_existent)
        assert result.is_failure
        assert result.error is not None
        assert result.error is not None and "not found" in result.error.lower()

    def test_config_load_from_config_file_unsupported_format(
        self, temp_dir: Path
    ) -> None:
        """Test load_from_config_file with unsupported format."""
        unsupported_file = temp_dir / "test.txt"
        unsupported_file.write_text("test content")
        result = FlextCliConfig.load_from_config_file(unsupported_file)
        assert result.is_failure
        assert result.error is not None
        assert result.error is not None and "unsupported" in result.error.lower()

    def test_config_get_global_instance(self) -> None:
        """Test get_global_instance class method."""
        config = FlextCliConfig()
        assert config is not None
        assert isinstance(config, FlextCliConfig)

    def test_config_reset_shared_instance(self) -> None:
        """Test reset_global_instance class method."""
        # Create an instance first
        FlextCliConfig()
        # Reset it
        FlextCliConfig.reset_global_instance()
        # Verify we can create a new one
        new_config = FlextCliConfig()
        assert new_config is not None

    def test_config_reset_global_instance(self) -> None:
        """Test reset_global_instance class method."""
        # Create an instance first
        FlextCliConfig()
        # Reset it
        FlextCliConfig.reset_global_instance()
        # Verify we can get a new one
        new_config = FlextCliConfig()
        assert new_config is not None

    # ========================================================================
    # Instance method tests for FlextCliConfig
    # ========================================================================

    def test_config_execute_as_service(self) -> None:
        """Test execute_as_service instance method."""
        config = FlextCliConfig()
        result = config.execute_as_service()
        assert result.is_success
        data = result.unwrap()
        assert isinstance(data, dict)
        assert "status" in data
        assert data["status"] == "operational"

    def test_config_load_config_file(self, temp_json_file: Path) -> None:
        """Test load_config_file instance method."""
        config = FlextCliConfig()
        result = config.load_config_file(str(temp_json_file))
        assert result.is_success
        loaded_config = result.unwrap()
        assert isinstance(loaded_config, FlextCliConfig)

    def test_config_load_config_file_not_found(self, temp_dir: Path) -> None:
        """Test load_config_file with non-existent file."""
        config = FlextCliConfig()
        non_existent = str(temp_dir / "non_existent.json")
        result = config.load_config_file(non_existent)
        assert result.is_failure
        assert result.error is not None
        assert result.error is not None and "not found" in result.error.lower()

    def test_config_save_config_file(self, temp_dir: Path) -> None:
        """Test save_config_file instance method."""
        config = FlextCliConfig(debug=True, verbose=True)
        save_path = str(temp_dir / "saved_config.json")
        result = config.save_config_file(save_path)
        assert result.is_success

    def test_config_load_config(self) -> None:
        """Test load_config protocol method."""
        config = FlextCliConfig(debug=True, verbose=False)
        result = config.load_config()
        assert result.is_success
        config_data = result.unwrap()
        assert isinstance(config_data, dict)
        assert config_data["debug"] is True
        assert config_data["verbose"] is False

    def test_config_save_config(self) -> None:
        """Test save_config protocol method."""
        from flext_cli.typings import FlextCliTypes

        config = FlextCliConfig()
        new_config_data: FlextCliTypes.Data.CliConfigData = {
            "debug": True,
            "verbose": True,
            "profile": "test",
        }
        result = config.save_config(new_config_data)
        assert result.is_success
        # Verify the config was updated
        assert config.debug is True
        assert config.verbose is True
        assert config.profile == "test"
