"""Simple test coverage for FlextCliLoggingSetup module.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

import os
import logging
import pytest
from unittest.mock import patch, MagicMock

from flext_cli.logging_setup import FlextCliLoggingSetup
from flext_cli.models import FlextCliModels
from flext_core import FlextResult


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
        assert hasattr(setup, '_container')
        assert hasattr(setup, '_logger')
        assert hasattr(setup, '_resolved_config')

    def test_logging_setup_initialization_with_config(self) -> None:
        """Test logging setup initialization with custom config."""
        config = FlextCliModels.FlextCliConfig()
        setup = FlextCliLoggingSetup(config)
        assert setup._resolved_config is config

    def test_execute(self) -> None:
        """Test execute method."""
        result = self.logging_setup.execute()
        assert result.is_success
        assert result.value["status"] == "completed"
        assert result.value["message"] == "Logging setup executed"

    @patch('flext_cli.logging_setup.FlextLogger.configure')
    def test_setup_logging_success(self, mock_configure: MagicMock) -> None:
        """Test setup logging success."""
        result = self.logging_setup.setup_logging()
        assert result.is_success
        assert isinstance(result.value, FlextCliModels.LoggingConfig)
        mock_configure.assert_called_once()

    @patch('flext_cli.logging_setup.FlextLogger.configure')
    def test_setup_logging_already_complete(self, mock_configure: MagicMock) -> None:
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
        config = FlextCliModels.LoggingConfig(
            log_level="DEBUG",
            log_file="/tmp/test.log"
        )
        assert config.log_level == "DEBUG"
        assert config.log_file is not None

    def test_logging_config_model_defaults(self) -> None:
        """Test LoggingConfig model defaults."""
        config = FlextCliModels.LoggingConfig()
        assert config.log_level == "INFO"
        assert config.log_file is None
