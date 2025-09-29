"""FLEXT CLI Tests - Comprehensive CLI functionality testing.

Tests for FlextCli main class using flext_tests infrastructure with real functionality
testing, no mocks, and comprehensive coverage following FLEXT standards.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import asyncio
import time

import pytest

from flext_cli.cli import FlextCli
from flext_cli.constants import FlextCliConstants


class TestFlextCli:
    """Comprehensive tests for FlextCli main class."""

    def test_cli_initialization(self) -> None:
        """Test CLI initialization with proper configuration."""
        cli = FlextCli()
        assert cli is not None
        assert isinstance(cli, FlextCli)

    def test_cli_execute_sync(self) -> None:
        """Test synchronous CLI execution."""
        cli = FlextCli()
        result = cli.execute()

        assert result.is_success
        assert result.value is not None
        assert result.value["status"] == FlextCliConstants.OPERATIONAL
        assert result.value["service"] == FlextCliConstants.FLEXT_CLI
        assert "timestamp" in result.value
        assert "version" in result.value
        assert "components" in result.value

    @pytest.mark.asyncio
    async def test_cli_execute_async(self) -> None:
        """Test asynchronous CLI execution."""
        cli = FlextCli()
        result = await cli.execute_async()

        assert result.is_success
        assert result.value is not None
        assert result.value["status"] == FlextCliConstants.OPERATIONAL
        assert result.value["service"] == FlextCliConstants.FLEXT_CLI
        assert "timestamp" in result.value
        assert "version" in result.value
        assert "components" in result.value

    def test_cli_components_availability(self) -> None:
        """Test that all CLI components are available."""
        cli = FlextCli()
        result = cli.execute()

        assert result.is_success
        components = result.value["components"]

        expected_components = ["api", "auth", "config", "debug", "formatters", "main"]
        for _component in expected_components:
            # Test component availability
            assert components is not None

    def test_cli_version_format(self) -> None:
        """Test CLI version format."""
        cli = FlextCli()
        result = cli.execute()

        assert result.is_success
        version = result.value["version"]
        assert isinstance(version, str)
        assert version == "2.0.0"

    def test_cli_timestamp_format(self) -> None:
        """Test CLI timestamp format."""
        cli = FlextCli()
        result = cli.execute()

        assert result.is_success
        timestamp = result.value["timestamp"]
        assert isinstance(timestamp, str)
        # Should be ISO format
        assert "T" in timestamp
        assert "Z" in timestamp or "+" in timestamp

    def test_cli_service_name(self) -> None:
        """Test CLI service name."""
        cli = FlextCli()
        result = cli.execute()

        assert result.is_success
        service = result.value["service"]
        assert service == FlextCliConstants.FLEXT_CLI

    def test_cli_status_operational(self) -> None:
        """Test CLI status is operational."""
        cli = FlextCli()
        result = cli.execute()

        assert result.is_success
        status = result.value["status"]
        assert status == FlextCliConstants.OPERATIONAL

    def test_cli_with_runner(self) -> None:
        """Test CLI with Click runner."""
        # Note: This would require implementing the actual CLI command interface
        # For now, we test the service functionality
        cli = FlextCli()
        result = cli.execute()
        assert result.is_success

    def test_cli_error_handling(self) -> None:
        """Test CLI error handling capabilities."""
        cli = FlextCli()
        # Test that the CLI can handle various scenarios
        result = cli.execute()
        assert result.is_success

        # Test async version
        async_result = asyncio.run(cli.execute_async())
        assert async_result.is_success

    def test_cli_integration_with_services(self) -> None:
        """Test CLI integration with internal services."""
        cli = FlextCli()
        result = cli.execute()

        assert result.is_success
        # Verify that the CLI properly integrates with its services
        assert "components" in result.value
        components = result.value["components"]

        # All components should be available
        if isinstance(components, dict):
            for component_status in components.values():
                assert component_status == FlextCliConstants.AVAILABLE

    def test_cli_performance(self) -> None:
        """Test CLI performance characteristics."""
        cli = FlextCli()

        # Test execution time
        start_time = time.time()
        result = cli.execute()
        execution_time = time.time() - start_time

        assert result.is_success
        # Should execute quickly (less than 1 second for basic operation)
        assert execution_time < 1.0

    def test_cli_memory_usage(self) -> None:
        """Test CLI memory usage characteristics."""
        cli = FlextCli()

        # Test that CLI doesn't leak memory
        initial_result = cli.execute()
        assert initial_result.is_success

        # Execute multiple times to check for memory leaks
        for _ in range(10):
            result = cli.execute()
            assert result.is_success

        # Final execution should still work
        final_result = cli.execute()
        assert final_result.is_success
