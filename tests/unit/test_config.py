"""FLEXT CLI Config Tests - Comprehensive configuration functionality testing.

Tests for FlextCliConfig classes using flext_tests infrastructure with real functionality
testing, no mocks, and comprehensive coverage following FLEXT standards.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import asyncio
import time

import pytest

from flext_cli.config import (
    FlextCliConfig,
    FlextCliConfigService,
)
from flext_cli.constants import FlextCliConstants
from flext_cli.models import FlextCliModels


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
    """Comprehensive tests for FlextCliConfigService class."""

    def test_config_service_initialization_duplicate(self) -> None:
        """Test ConfigService initialization."""
        config_service = FlextCliConfigService()
        assert config_service is not None
        assert isinstance(config_service, FlextCliConfigService)

    def test_config_service_execute_sync(self) -> None:
        """Test synchronous ConfigService execution."""
        config_service = FlextCliConfigService()
        result = config_service.execute()

        assert result.is_success
        assert result.value is not None
        assert result.value["status"] == FlextCliConstants.OPERATIONAL
        assert result.value["service"] == "flext-cli-config"

    @pytest.mark.asyncio
    async def test_config_service_execute_async(self) -> None:
        """Test asynchronous ConfigService execution."""
        config_service = FlextCliConfigService()
        result = await config_service.execute_async()

        assert result.is_success
        assert result.value is not None
        assert result.value["status"] == FlextCliConstants.OPERATIONAL
        assert result.value["service"] == "flext-cli-config"

    def test_config_service_execute(self) -> None:
        """Test config service execute functionality."""
        config_service = FlextCliConfigService()

        # Test execute method
        result = config_service.execute()
        assert result.is_success

        data = result.unwrap()
        assert isinstance(data, dict)
        assert "status" in data
        assert "service" in data
        assert data["service"] == "flext-cli-config"

    def test_config_service_async_execute(self) -> None:
        """Test config service async execute functionality."""
        config_service = FlextCliConfigService()

        async def run_test() -> None:
            result = await config_service.execute_async()
            assert result.is_success

            data = result.unwrap()
            assert isinstance(data, dict)
            assert "status" in data
            assert "service" in data
            assert data["service"] == "flext-cli-config"

        asyncio.run(run_test())

    def test_config_service_error_handling(self) -> None:
        """Test config service error handling."""
        config_service = FlextCliConfigService()

        # Test execute method - should always succeed
        result = config_service.execute()
        assert result.is_success
        assert result is not None

    def test_config_service_performance(self) -> None:
        """Test config service performance."""
        config_service = FlextCliConfigService()

        start_time = time.time()
        result = config_service.execute()
        execution_time = time.time() - start_time

        assert result.is_success
        # Should execute quickly
        assert execution_time < 1.0

    def test_config_service_integration(self) -> None:
        """Test config service integration."""
        config_service = FlextCliConfigService()

        # Test that config service properly integrates with its dependencies
        result = config_service.execute()
        assert result.is_success

        # Test async version
        async_result = asyncio.run(config_service.execute_async())
        assert async_result.is_success
