"""Test coverage for FlextCliLoggingSetup module.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

import os
import logging
import pytest
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path

from flext_cli.logging_setup import FlextCliLoggingSetup
from flext_cli.models import FlextCliModels
from flext_core import FlextResult


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

    @patch.dict(os.environ, {'FLEXT_LOG_LEVEL': 'DEBUG'})
    def test_detect_log_configuration_from_env(self) -> None:
        """Test detect log configuration from environment."""
        result = self.logging_setup._detect_log_configuration()
        assert result.is_success
        assert result.value.log_level == "DEBUG"
        assert result.value.source == "environment"

    @patch.dict(os.environ, {'FLEXT_CLI_LOG_LEVEL': 'INFO'})
    def test_detect_log_configuration_from_cli_env(self) -> None:
        """Test detect log configuration from CLI environment."""
        result = self.logging_setup._detect_log_configuration()
        assert result.is_success
        assert result.value.log_level == "INFO"
        assert result.value.source == "environment"

    def test_detect_log_configuration_from_config(self) -> None:
        """Test detect log configuration from config."""
        config = FlextCliModels.FlextCliConfig(log_level="WARNING")
        setup = FlextCliLoggingSetup(config)
        result = setup._detect_log_configuration()
        assert result.is_success
        assert result.value.log_level == "WARNING"
        assert result.value.source == "config"

    def test_detect_log_configuration_default(self) -> None:
        """Test detect log configuration with default values."""
        result = self.logging_setup._detect_log_configuration()
        assert result.is_success
        assert result.value.log_level == "INFO"
        assert result.value.source == "default"

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

    @patch('flext_cli.logging_setup.FlextLogger.configure')
    def test_setup_logging_with_file(self, mock_configure: MagicMock) -> None:
        """Test setup logging with log file."""
        config = FlextCliModels.FlextCliConfig(log_file="/tmp/test.log")
        setup = FlextCliLoggingSetup(config)
        result = setup.setup_logging()
        assert result.is_success

    @patch('flext_cli.logging_setup.FlextLogger.configure')
    def test_setup_logging_with_verbosity(self, mock_configure: MagicMock) -> None:
        """Test setup logging with verbosity."""
        with patch.dict(os.environ, {'FLEXT_LOG_VERBOSITY': 'minimal'}):
            result = self.logging_setup.setup_logging()
            assert result.is_success

    def test_get_logger_existing(self) -> None:
        """Test get logger for existing logger."""
        logger_name = "test_logger"
        logger = logging.getLogger(logger_name)
        FlextCliLoggingSetup._loggers[logger_name] = logger
        
        result = self.logging_setup._get_logger(logger_name)
        assert result.is_success
        assert result.value is logger

    def test_get_logger_new(self) -> None:
        """Test get logger for new logger."""
        logger_name = "new_test_logger"
        result = self.logging_setup._get_logger(logger_name)
        assert result.is_success
        assert logger_name in FlextCliLoggingSetup._loggers

    def test_configure_logger(self) -> None:
        """Test configure logger."""
        logger = logging.getLogger("test_configure")
        log_config = FlextCliModels.LoggingConfig(
            log_level="DEBUG",
            source="test",
            log_file=None
        )
        
        result = self.logging_setup._configure_logger(logger, log_config)
        assert result.is_success

    def test_configure_logger_with_file(self) -> None:
        """Test configure logger with file."""
        logger = logging.getLogger("test_configure_file")
        log_config = FlextCliModels.LoggingConfig(
            log_level="DEBUG",
            source="test",
            log_file="/tmp/test.log"
        )
        
        with patch('builtins.open', mock_open()):
            result = self.logging_setup._configure_logger(logger, log_config)
            assert result.is_success

    def test_validate_log_level_valid(self) -> None:
        """Test validate log level with valid level."""
        result = self.logging_setup._validate_log_level("DEBUG")
        assert result.is_success
        assert result.value == "DEBUG"

    def test_validate_log_level_invalid(self) -> None:
        """Test validate log level with invalid level."""
        result = self.logging_setup._validate_log_level("INVALID")
        assert result.is_success
        assert result.value == "INFO"  # default fallback

    def test_validate_log_level_case_insensitive(self) -> None:
        """Test validate log level case insensitive."""
        result = self.logging_setup._validate_log_level("debug")
        assert result.is_success
        assert result.value == "DEBUG"

    def test_get_log_file_path_default(self) -> None:
        """Test get log file path with default."""
        result = self.logging_setup._get_log_file_path()
        assert result.is_success
        assert result.value is None

    def test_get_log_file_path_from_config(self) -> None:
        """Test get log file path from config."""
        config = FlextCliModels.FlextCliConfig(log_file="/tmp/test.log")
        setup = FlextCliLoggingSetup(config)
        result = setup._get_log_file_path()
        assert result.is_success
        assert result.value == "/tmp/test.log"

    def test_get_log_file_path_from_env(self) -> None:
        """Test get log file path from environment."""
        with patch.dict(os.environ, {'FLEXT_LOG_FILE': '/tmp/env.log'}):
            result = self.logging_setup._get_log_file_path()
            assert result.is_success
            assert result.value == "/tmp/env.log"

    def test_create_file_handler(self) -> None:
        """Test create file handler."""
        log_file = "/tmp/test.log"
        with patch('builtins.open', mock_open()):
            result = self.logging_setup._create_file_handler(log_file)
            assert result.is_success
            assert result.value is not None

    def test_create_file_handler_invalid_path(self) -> None:
        """Test create file handler with invalid path."""
        log_file = "/invalid/path/test.log"
        result = self.logging_setup._create_file_handler(log_file)
        assert result.is_failure

    def test_get_log_level_from_config(self) -> None:
        """Test get log level from config."""
        config = FlextCliModels.FlextCliConfig(log_level="WARNING")
        setup = FlextCliLoggingSetup(config)
        result = setup._get_log_level_from_config()
        assert result.is_success
        assert result.value == "WARNING"

    def test_get_log_level_from_config_default(self) -> None:
        """Test get log level from config with default."""
        result = self.logging_setup._get_log_level_from_config()
        assert result.is_success
        assert result.value == "INFO"

    def test_get_log_level_from_env(self) -> None:
        """Test get log level from environment."""
        with patch.dict(os.environ, {'FLEXT_LOG_LEVEL': 'ERROR'}):
            result = self.logging_setup._get_log_level_from_env()
            assert result.is_success
            assert result.value == "ERROR"

    def test_get_log_level_from_env_cli(self) -> None:
        """Test get log level from CLI environment."""
        with patch.dict(os.environ, {'FLEXT_CLI_LOG_LEVEL': 'CRITICAL'}):
            result = self.logging_setup._get_log_level_from_env()
            assert result.is_success
            assert result.value == "CRITICAL"

    def test_get_log_level_from_env_not_found(self) -> None:
        """Test get log level from environment when not found."""
        with patch.dict(os.environ, {}, clear=True):
            result = self.logging_setup._get_log_level_from_env()
            assert result.is_success
            assert result.value is None

    def test_logging_config_model_creation(self) -> None:
        """Test LoggingConfig model creation."""
        config = FlextCliModels.LoggingConfig(
            log_level="DEBUG",
            source="test",
            log_file="/tmp/test.log"
        )
        assert config.log_level == "DEBUG"
        assert config.source == "test"
        assert config.log_file == "/tmp/test.log"

    def test_logging_config_model_defaults(self) -> None:
        """Test LoggingConfig model defaults."""
        config = FlextCliModels.LoggingConfig()
        assert config.log_level == "INFO"
        assert config.source == "default"
        assert config.log_file is None
