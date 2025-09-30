"""FLEXT CLI Debug Tests - Comprehensive Real Functionality Testing.

Tests for FlextCliDebug covering all real functionality with flext_tests
integration, comprehensive debug operations, and targeting 90%+ coverage.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import time

import pytest

from flext_cli.debug import FlextCliDebug
from flext_core import FlextResult
from flext_tests import FlextTestsUtilities


class TestFlextCliDebug:
    """Comprehensive tests for FlextCliDebug functionality."""

    @pytest.fixture
    def debug(self) -> FlextCliDebug:
        """Create FlextCliDebug instance for testing."""
        return FlextCliDebug()

    @pytest.fixture
    def test_utilities(self) -> FlextTestsUtilities:
        """Provide FlextTestsUtilities for test support."""
        return FlextTestsUtilities()

    def test_debug_initialization(self, debug: FlextCliDebug) -> None:
        """Test debug initialization."""
        assert isinstance(debug, FlextCliDebug)
        assert hasattr(debug, "_logger")

    def test_debug_execute(self, debug: FlextCliDebug) -> None:
        """Test debug execute method."""
        result = debug.execute()

        assert isinstance(result, FlextResult)
        assert result.is_success
        assert isinstance(result.unwrap(), str)

    async def test_debug_execute_async(self, debug: FlextCliDebug) -> None:
        """Test debug async execute method."""
        result = await debug.execute_async()

        assert isinstance(result, FlextResult)
        assert result.is_success
        assert isinstance(result.unwrap(), str)

    def test_debug_validate_config(self, debug: FlextCliDebug) -> None:
        """Test debug config validation."""
        result = debug.validate_config()

        assert isinstance(result, FlextResult)
        assert result.is_success

    def test_debug_get_system_paths(self, debug: FlextCliDebug) -> None:
        """Test getting system paths."""
        result = debug.get_system_paths()

        assert isinstance(result, FlextResult)
        assert result.is_success
        assert isinstance(result.unwrap(), list)

    def test_debug_validate_environment_setup(self, debug: FlextCliDebug) -> None:
        """Test validating environment setup."""
        result = debug.validate_environment_setup()

        assert isinstance(result, FlextResult)
        assert result.is_success
        assert isinstance(result.unwrap(), list)

    def test_debug_test_connectivity(self, debug: FlextCliDebug) -> None:
        """Test connectivity testing."""
        result = debug.test_connectivity()

        assert isinstance(result, FlextResult)
        assert result.is_success
        assert isinstance(result.unwrap(), dict)

    def test_debug_execute_health_check(self, debug: FlextCliDebug) -> None:
        """Test executing health check."""
        result = debug.execute_health_check()

        assert isinstance(result, FlextResult)
        assert result.is_success
        assert isinstance(result.unwrap(), dict)

    def test_debug_execute_trace(self, debug: FlextCliDebug) -> None:
        """Test executing trace."""
        result = debug.execute_trace(["test", "args"])

        assert isinstance(result, FlextResult)
        assert result.is_success
        assert isinstance(result.unwrap(), dict)

    def test_debug_get_debug_info(self, debug: FlextCliDebug) -> None:
        """Test getting debug information."""
        result = debug.get_debug_info()

        assert isinstance(result, FlextResult)
        assert result.is_success
        assert isinstance(result.unwrap(), dict)

    def test_debug_integration_workflow(self, debug: FlextCliDebug) -> None:
        """Test complete debug workflow."""
        # Step 1: Get system paths
        paths_result = debug.get_system_paths()
        assert paths_result.is_success

        # Step 2: Validate environment
        validate_result = debug.validate_environment_setup()
        assert validate_result.is_success

        # Step 3: Test connectivity
        connectivity_result = debug.test_connectivity()
        assert connectivity_result.is_success

        # Step 4: Execute health check
        health_result = debug.execute_health_check()
        assert health_result.is_success

        # Step 5: Get debug info
        debug_info_result = debug.get_debug_info()
        assert debug_info_result.is_success

    def test_debug_real_functionality(self, debug: FlextCliDebug) -> None:
        """Test real debug functionality without mocks."""
        # Test actual debug operations
        result = debug.get_system_paths()
        assert result.is_success

        paths = result.unwrap()
        assert isinstance(paths, list)

        # Test environment validation
        env_result = debug.validate_environment_setup()
        assert env_result.is_success

        env_issues = env_result.unwrap()
        assert isinstance(env_issues, list)

    def test_debug_edge_cases(self, debug: FlextCliDebug) -> None:
        """Test edge cases and error conditions."""
        # Test with empty trace args
        result = debug.execute_trace([])
        assert isinstance(result, FlextResult)

        # Test with various trace args
        result = debug.execute_trace(["arg1", "arg2", "arg3"])
        assert isinstance(result, FlextResult)

        # Test with special characters in trace args
        result = debug.execute_trace([
            "arg with spaces",
            "arg-with-dashes",
            "arg_with_underscores",
        ])
        assert isinstance(result, FlextResult)

    def test_debug_performance(self, debug: FlextCliDebug) -> None:
        """Test debug performance."""
        # Test multiple debug operations performance
        start_time = time.time()
        for _i in range(100):
            debug.get_system_paths()
        end_time = time.time()

        # Should be fast (less than 1 second for 100 operations)
        assert (end_time - start_time) < 1.0

    def test_debug_memory_usage(self, debug: FlextCliDebug) -> None:
        """Test debug memory usage."""
        # Test with many debug operations
        for _i in range(1000):
            result = debug.get_system_paths()
            assert isinstance(result, FlextResult)

        # Test getting debug info multiple times
        for _i in range(100):
            result = debug.get_debug_info()
            assert isinstance(result, FlextResult)
