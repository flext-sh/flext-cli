"""Test coverage for FlextCliLoggingSetup module.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

from flext_cli.config import FlextCliConfig
from flext_cli.logging_setup import FlextCliLoggingSetup


def get_temp_log_file() -> Path:
    """Get a temporary log file path."""
    with tempfile.NamedTemporaryFile(suffix=".log", delete=False) as tmp_file:
        return Path(tmp_file.name)


class TestFlextCliLoggingSetup:
    """Test FlextCliLoggingSetup class."""

    def setup_method(self) -> None:
        """Set up test environment."""
        # Reset class state
        FlextCliLoggingSetup._loggers.clear()
        FlextCliLoggingSetup._setup_complete = False
        self.logging_setup = FlextCliLoggingSetup()

    def teardown_method(self) -> None:
        """Clean up after tests."""
        # Reset class state
        FlextCliLoggingSetup._loggers.clear()
        FlextCliLoggingSetup._setup_complete = False

    def test_logging_setup_initialization(self) -> None:
        """Test logging setup initialization."""
        setup = FlextCliLoggingSetup()
        assert setup is not None
        assert hasattr(setup, "_container")
        assert hasattr(setup, "_logger")
        assert hasattr(setup, "_resolved_config")

    def test_logging_setup_initialization_with_config(self) -> None:
        """Test logging setup initialization with custom config."""
        config = FlextCliConfig.MainConfig()
        setup = FlextCliLoggingSetup(config)
        assert setup._resolved_config is config

    def test_execute(self) -> None:
        """Test execute method."""
        result = self.logging_setup.execute()
        assert result.is_success
        assert result.value["status"] == "completed"
        assert result.value["message"] == "Logging setup executed"

    @patch.dict(os.environ, {"FLEXT_CLI_LOG_LEVEL": "DEBUG"})
    def test_detect_log_configuration_from_env(self) -> None:
        """Test detect log configuration from environment."""
        result = self.logging_setup._detect_log_configuration()
        assert result.is_success
        assert result.value.log_level == "DEBUG"
        assert result.value.log_level_source == "environment_variable"

    @patch.dict(os.environ, {"FLEXT_CLI_LOG_LEVEL": "INFO"})
    def test_detect_log_configuration_from_cli_env(self) -> None:
        """Test detect log configuration from CLI environment."""
        result = self.logging_setup._detect_log_configuration()
        assert result.is_success
        assert result.value.log_level == "INFO"
        assert result.value.log_level_source == "environment_variable"

    def test_detect_log_configuration_from_config(self) -> None:
        """Test detect log configuration from config."""
        config = FlextCliConfig.MainConfig(log_level="WARNING")
        setup = FlextCliLoggingSetup(config)
        result = setup._detect_log_configuration()
        assert result.is_success
        assert result.value.log_level == "WARNING"
        assert result.value.log_level_source == "config_instance"

    def test_detect_log_configuration_default(self) -> None:
        """Test detect log configuration with default values."""
        result = self.logging_setup._detect_log_configuration()
        assert result.is_success
        assert result.value.log_level == "INFO"
        assert result.value.log_level_source == "default"

    @patch("flext_cli.logging_setup.FlextLogger.configure")
    def test_setup_logging_success(self, mock_configure: MagicMock) -> None:
        """Test setup logging success."""
        result = self.logging_setup.setup_logging()
        assert result.is_success
        assert isinstance(result.value, FlextCliConfig.LoggingConfig)
        mock_configure.assert_called_once()

    @patch("flext_cli.logging_setup.FlextLogger.configure")
    def test_setup_logging_already_complete(self, _mock_configure: MagicMock) -> None:
        """Test setup logging when already complete."""
        # First setup
        result1 = self.logging_setup.setup_logging()
        assert result1.is_success

        # Second setup should return cached result
        result2 = self.logging_setup.setup_logging()
        assert result2.is_success
        assert result1.value.log_level == result2.value.log_level

    @patch("flext_cli.logging_setup.FlextLogger.configure")
    def test_setup_logging_with_file(self, _mock_configure: MagicMock) -> None:
        """Test setup logging with log file."""
        with tempfile.NamedTemporaryFile(suffix=".log", delete=False) as tmp_file:
            config = FlextCliConfig.MainConfig(log_file=tmp_file.name)
        setup = FlextCliLoggingSetup(config)
        result = setup.setup_logging()
        assert result.is_success

    @patch("flext_cli.logging_setup.FlextLogger.configure")
    def test_setup_logging_with_verbosity(self, _mock_configure: MagicMock) -> None:
        """Test setup logging with verbosity."""
        with patch.dict(os.environ, {"FLEXT_LOG_VERBOSITY": "minimal"}):
            result = self.logging_setup.setup_logging()
            assert result.is_success

    # Tests for non-existent private methods removed - these methods don't exist in the actual implementation

    def test_logging_config_model_creation(self) -> None:
        """Test LoggingConfig model creation."""
        temp_file = get_temp_log_file()
        config = FlextCliConfig.LoggingConfig(
            log_level="DEBUG", log_level_source="test", log_file=temp_file
        )
        assert config.log_level == "DEBUG"
        assert config.log_level_source == "test"
        assert config.log_file == temp_file

    def test_logging_config_model_defaults(self) -> None:
        """Test LoggingConfig model defaults."""
        config = FlextCliConfig.LoggingConfig()
        assert config.log_level == "INFO"
        assert config.log_level_source == "default"
        assert config.log_file is None
