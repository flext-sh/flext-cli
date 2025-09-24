"""Simple test coverage for FlextCliLoggingSetup module.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

from flext_cli import FlextCliConfig, FlextCliLoggingSetup


def get_temp_log_file() -> str:
    """Get a temporary log file path."""
    with tempfile.NamedTemporaryFile(suffix=".log", delete=False) as tmp_file:
        return tmp_file.name


class TestFlextCliLoggingSetupSimple:
    """Test FlextCliLoggingSetup class with existing methods only."""

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
        # Check that the result contains logging configuration
        assert isinstance(result.value, dict)
        assert "status" in result.value

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

    def test_logging_config_model_creation(self) -> None:
        """Test LoggingConfig model creation."""
        config = FlextCliConfig.LoggingConfig(
            log_level="DEBUG", log_file=Path(get_temp_log_file())
        )
        assert config.log_level == "DEBUG"
        assert config.log_file is not None

    def test_logging_config_model_defaults(self) -> None:
        """Test LoggingConfig model defaults."""
        config = FlextCliConfig.LoggingConfig()
        assert config.log_level == "INFO"
        assert config.log_file is None
