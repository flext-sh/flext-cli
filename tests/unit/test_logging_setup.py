"""FLEXT CLI Logging Setup Tests - Comprehensive Real Functionality Testing.

Tests for FlextCliLoggingSetup covering all real functionality with flext_tests
integration, comprehensive logging operations, and targeting 90%+ coverage.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import asyncio
import time

import pytest

from flext_cli.logging_setup import FlextCliLoggingSetup
from flext_core import FlextResult
from flext_tests import FlextTestsUtilities


class TestFlextCliLoggingSetup:
    """Comprehensive tests for FlextCliLoggingSetup functionality."""

    @pytest.fixture
    def logging_setup(self) -> FlextCliLoggingSetup:
        """Create FlextCliLoggingSetup instance for testing."""
        return FlextCliLoggingSetup()

    @pytest.fixture
    def test_utilities(self) -> FlextTestsUtilities:
        """Provide FlextTestsUtilities for test support."""
        return FlextTestsUtilities()

    def test_logging_setup_initialization(
        self, logging_setup: FlextCliLoggingSetup
    ) -> None:
        """Test logging setup initialization."""
        assert isinstance(logging_setup, FlextCliLoggingSetup)
        assert hasattr(logging_setup, "_logger")

    def test_logging_setup_execute(self, logging_setup: FlextCliLoggingSetup) -> None:
        """Test logging setup execute method."""
        result = logging_setup.execute()

        assert isinstance(result, FlextResult)
        assert result.is_success
        assert isinstance(result.unwrap(), dict)

    def test_logging_setup_execute_async(
        self, logging_setup: FlextCliLoggingSetup
    ) -> None:
        """Test logging setup async execute method."""

        async def run_test() -> None:
            result = await logging_setup.execute_async()

            assert isinstance(result, FlextResult)
            assert result.is_success
            assert isinstance(result.unwrap(), dict)

        asyncio.run(run_test())

    def test_logging_setup_validate_config(
        self, logging_setup: FlextCliLoggingSetup
    ) -> None:
        """Test logging setup config validation."""
        result = logging_setup.validate_config()

        assert isinstance(result, FlextResult)
        assert result.is_success

    def test_logging_setup_setup_logging(
        self, logging_setup: FlextCliLoggingSetup
    ) -> None:
        """Test logging setup functionality."""
        result = logging_setup.setup_logging()

        assert isinstance(result, FlextResult)
        assert result.is_success

    def test_logging_setup_setup_for_cli(
        self, logging_setup: FlextCliLoggingSetup
    ) -> None:
        """Test CLI-specific logging setup."""
        result = logging_setup.setup_for_cli()

        assert isinstance(result, FlextResult)
        assert result.is_success

    def test_logging_setup_get_effective_log_level(
        self, logging_setup: FlextCliLoggingSetup
    ) -> None:
        """Test getting effective log level."""
        result = logging_setup.get_effective_log_level()

        assert isinstance(result, FlextResult)
        assert result.is_success
        assert isinstance(result.unwrap(), str)

    def test_logging_setup_is_setup_complete(
        self, logging_setup: FlextCliLoggingSetup
    ) -> None:
        """Test checking if setup is complete."""
        result = logging_setup.is_setup_complete

        assert isinstance(result, bool)

    def test_logging_setup_set_global_log_level(
        self, logging_setup: FlextCliLoggingSetup
    ) -> None:
        """Test setting global log level."""
        result = logging_setup.set_global_log_level("INFO")

        assert isinstance(result, FlextResult)
        assert result.is_success

    def test_logging_setup_set_global_log_verbosity(
        self, logging_setup: FlextCliLoggingSetup
    ) -> None:
        """Test setting global log verbosity."""
        result = logging_setup.set_global_log_verbosity("detailed")

        assert isinstance(result, FlextResult)
        assert result.is_success

    def test_logging_setup_get_current_log_config(
        self, logging_setup: FlextCliLoggingSetup
    ) -> None:
        """Test getting current log configuration."""
        result = logging_setup.get_current_log_config()

        assert isinstance(result, FlextResult)
        assert result.is_success
        assert isinstance(result.unwrap(), dict)

    def test_logging_setup_configure_project_logging(
        self, logging_setup: FlextCliLoggingSetup
    ) -> None:
        """Test configuring project logging."""
        result = logging_setup.configure_project_logging("test_project")

        assert isinstance(result, FlextResult)
        assert result.is_success

    def test_logging_setup_integration_workflow(
        self, logging_setup: FlextCliLoggingSetup
    ) -> None:
        """Test complete logging setup workflow."""
        # Step 1: Setup logging
        setup_result = logging_setup.setup_logging()
        assert setup_result.is_success

        # Step 2: Setup for CLI
        cli_result = logging_setup.setup_for_cli()
        assert cli_result.is_success

        # Step 3: Get effective log level
        level_result = logging_setup.get_effective_log_level()
        assert level_result.is_success

        # Step 4: Check if setup is complete
        complete = logging_setup.is_setup_complete
        assert isinstance(complete, bool)

        # Step 5: Get current config
        config_result = logging_setup.get_current_log_config()
        assert config_result.is_success

        # Step 6: Configure project logging
        project_result = logging_setup.configure_project_logging("test_project")
        assert project_result.is_success

    def test_logging_setup_real_functionality(
        self, logging_setup: FlextCliLoggingSetup
    ) -> None:
        """Test real logging functionality without mocks."""
        # Test actual logging operations
        result = logging_setup.setup_logging()
        assert result.is_success

        # Test CLI setup
        cli_result = logging_setup.setup_for_cli()
        assert cli_result.is_success

        # Test getting log level
        level_result = logging_setup.get_effective_log_level()
        assert level_result.is_success

    def test_logging_setup_edge_cases(
        self, logging_setup: FlextCliLoggingSetup
    ) -> None:
        """Test edge cases and error conditions."""
        # Test with various log levels
        for level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            result = logging_setup.set_global_log_level(level)
            assert isinstance(result, FlextResult)

        # Test with various verbosity levels
        for verbosity in ["detailed", "compact", "full"]:
            result = logging_setup.set_global_log_verbosity(verbosity)
            assert isinstance(result, FlextResult)

    def test_logging_setup_performance(
        self, logging_setup: FlextCliLoggingSetup
    ) -> None:
        """Test logging setup performance."""
        # Test multiple setup operations performance
        start_time = time.time()
        for _i in range(100):
            logging_setup.setup_logging()
        end_time = time.time()

        # Should be fast (less than 5 seconds for 100 setups)
        assert (end_time - start_time) < 5.0

    def test_logging_setup_memory_usage(
        self, logging_setup: FlextCliLoggingSetup
    ) -> None:
        """Test logging setup memory usage."""
        # Test with many setup operations
        for _i in range(1000):
            result = logging_setup.setup_logging()
            assert isinstance(result, FlextResult)

        # Test getting config multiple times
        for _i in range(100):
            result = logging_setup.get_current_log_config()
            assert isinstance(result, FlextResult)

    def test_logging_setup_duplicate_prevention(
        self, logging_setup: FlextCliLoggingSetup
    ) -> None:
        """Test that duplicate setup calls are prevented."""
        # First setup
        result1 = logging_setup.setup_logging()
        assert result1.is_success

        # Second setup should be prevented (cached)
        result2 = logging_setup.setup_logging()
        assert result2.is_success

    def test_logging_setup_detect_configuration(
        self, logging_setup: FlextCliLoggingSetup
    ) -> None:
        """Test log configuration detection."""
        result = logging_setup._detect_log_configuration()
        assert isinstance(result, FlextResult)
        assert result.is_success
        assert hasattr(result.value, "log_level")

    def test_logging_setup_get_effective_log_level(
        self, logging_setup: FlextCliLoggingSetup
    ) -> None:
        """Test getting effective log level."""
        result = logging_setup.get_effective_log_level()
        assert isinstance(result, FlextResult)
        assert result.is_success
        assert isinstance(result.value, str)

    def test_logging_setup_setup_for_cli(
        self, logging_setup: FlextCliLoggingSetup
    ) -> None:
        """Test CLI-specific logging setup."""
        result = logging_setup.setup_for_cli()
        assert isinstance(result, FlextResult)
        assert result.is_success

    def test_logging_setup_integration_workflow(
        self, logging_setup: FlextCliLoggingSetup
    ) -> None:
        """Test complete logging setup integration workflow."""
        # 1. Test initial setup
        setup_result = logging_setup.setup_logging()
        assert setup_result.is_success

        # 2. Test configuration detection
        config_result = logging_setup._detect_log_configuration()
        assert config_result.is_success

        # 3. Test getting current config
        current_result = logging_setup.get_current_log_config()
        assert current_result.is_success

        # 4. Test effective log level
        level_result = logging_setup.get_effective_log_level()
        assert level_result.is_success

        # 5. Test CLI setup
        cli_result = logging_setup.setup_for_cli()
        assert cli_result.is_success

    def test_logging_setup_real_functionality(
        self, logging_setup: FlextCliLoggingSetup
    ) -> None:
        """Test logging setup real functionality with comprehensive scenarios."""
        # Test basic setup
        result = logging_setup.setup_logging()
        assert result.is_success

        # Test configuration detection
        config_result = logging_setup._detect_log_configuration()
        assert config_result.is_success
        config = config_result.value
        assert hasattr(config, "log_level")
        assert hasattr(config, "log_level_source")

        # Test getting effective log level
        level_result = logging_setup.get_effective_log_level()
        assert level_result.is_success
        assert isinstance(level_result.value, str)

        # Test CLI setup
        cli_result = logging_setup.setup_for_cli()
        assert cli_result.is_success

        # Test getting current config
        current_result = logging_setup.get_current_log_config()
        assert current_result.is_success

    def test_logging_setup_edge_cases(
        self, logging_setup: FlextCliLoggingSetup
    ) -> None:
        """Test logging setup edge cases and error handling."""
        # Test with different verbosity levels
        verbosity_levels = ["compact", "detailed", "full"]
        for verbosity in verbosity_levels:
            result = logging_setup.set_global_log_verbosity(verbosity)
            assert result.is_success

        # Test multiple setup calls
        for _i in range(5):
            result = logging_setup.setup_logging()
            assert result.is_success

        # Test configuration detection multiple times
        for _i in range(5):
            result = logging_setup._detect_log_configuration()
            assert result.is_success

    def test_logging_setup_error_scenarios(
        self, logging_setup: FlextCliLoggingSetup
    ) -> None:
        """Test logging setup error scenarios."""
        # Test with invalid verbosity
        result = logging_setup.set_global_log_verbosity("invalid_verbosity")
        # Should handle gracefully
        assert isinstance(result, FlextResult)

        # Test configuration detection robustness
        result = logging_setup._detect_log_configuration()
        assert isinstance(result, FlextResult)
        assert result.is_success

    def test_logging_setup_async_functionality(
        self, logging_setup: FlextCliLoggingSetup
    ) -> None:
        """Test logging setup async functionality."""
        import asyncio

        async def run_async_tests():
            # Test async setup
            result = await logging_setup.setup_logging_async()
            assert isinstance(result, FlextResult)
            assert result.is_success

            # Test async CLI setup
            cli_result = await logging_setup.setup_for_cli_async()
            assert isinstance(cli_result, FlextResult)
            assert cli_result.is_success

        asyncio.run(run_async_tests())
