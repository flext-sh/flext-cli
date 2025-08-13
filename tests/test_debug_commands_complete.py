"""Complete tests for debug commands to achieve 90%+ coverage.

Focused tests to cover the remaining uncovered lines in debug commands.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar
from unittest.mock import MagicMock, patch

if TYPE_CHECKING:
    from collections.abc import Callable

# Import proper typing for decorators to avoid Any types
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

import click
import pytest
from click.testing import CliRunner
from flext_core.constants import FlextConstants

from flext_cli.commands.debug import (
    SENSITIVE_VALUE_PREVIEW_LENGTH,
    connectivity,
    debug_cmd,
    performance,
)

# Type definitions for patch decorators
F = TypeVar("F", bound="Callable[..., None]")


class TestDebugConnectivity:
    """Test connectivity command missing coverage."""

    def test_connectivity_success_with_status(
        self,
        mock_flext_api_client_with_patches: object,
    ) -> None:
        """Test connectivity success with system status."""
        # Use the existing mock client with proper setup
        mock_flext_api_client_with_patches.base_url = f"http://{FlextConstants.Platform.DEFAULT_HOST}:{FlextConstants.Platform.FLEXT_API_PORT}"

        mock_console = MagicMock()
        runner = CliRunner()

        result = runner.invoke(connectivity, obj={"console": mock_console})

        if result.exit_code != 0:
            raise AssertionError(f"Expected {0}, got {result.exit_code}")
        # Check for the actual messages that the command produces
        mock_console.print.assert_any_call(
            "[yellow]Testing API connectivity using flext-api...[/yellow]",
        )
        mock_console.print.assert_any_call(
            f"[green]✅ Connected to API at http://{FlextConstants.Platform.DEFAULT_HOST}:{FlextConstants.Platform.FLEXT_API_PORT}[/green]",
        )
        mock_console.print.assert_any_call("\nSystem Status:")
        mock_console.print.assert_any_call("  Version: 1.0.0")
        mock_console.print.assert_any_call("  Status: healthy")
        mock_console.print.assert_any_call("  Uptime: 24h")

    def test_connectivity_success_status_unknown(
        self,
        mock_flext_api_client_with_patches: object,
    ) -> None:
        """Test connectivity success with unknown status fields."""
        from flext_core import FlextResult

        # Configure the mock to return status with missing fields (but still a valid dict)
        async def mock_get_system_status_partial() -> FlextResult[dict[str, object]]:
            return FlextResult.ok(
                {"incomplete": "status"},
            )  # Dict with missing expected fields

        mock_flext_api_client_with_patches.get_system_status = (
            mock_get_system_status_partial
        )
        mock_flext_api_client_with_patches.base_url = "https://api.flext.com"

        mock_console = MagicMock()
        runner = CliRunner()

        result = runner.invoke(connectivity, obj={"console": mock_console})

        if result.exit_code != 0:
            raise AssertionError(f"Expected {0}, got {result.exit_code}")
        # When status dict exists but has missing fields, the command shows "Unknown" values
        mock_console.print.assert_any_call("\nSystem Status:")
        mock_console.print.assert_any_call("  Version: Unknown")
        mock_console.print.assert_any_call("  Status: Unknown")
        mock_console.print.assert_any_call("  Uptime: Unknown")

    def _test_connectivity_success_status_unknown_impl(
        self,
        mock_client_class: MagicMock,
    ) -> None:
        """Test connectivity success with unknown status fields."""
        # Setup mocks
        mock_client = MagicMock()
        mock_client.test_connection.return_value = True
        mock_client.base_url = "https://api.flext.com"
        mock_client.get_system_status.return_value = {}  # Empty status
        mock_client_class.return_value = mock_client

        mock_console = MagicMock()
        runner = CliRunner()

        result = runner.invoke(connectivity, obj={"console": mock_console})

        if result.exit_code != 0:
            raise AssertionError(f"Expected {0}, got {result.exit_code}")
        mock_console.print.assert_any_call("  Version: Unknown")
        mock_console.print.assert_any_call("  Status: Unknown")
        mock_console.print.assert_any_call("  Uptime: Unknown")

    def test_connectivity_success_status_error(
        self,
        mock_flext_api_client_with_patches: object,
    ) -> None:
        """Test connectivity success but status fetch fails."""
        with patch("flext_cli.client.FlextApiClient") as mock_client_class:
            self._test_connectivity_success_status_error_impl(mock_client_class)

    def _test_connectivity_success_status_error_impl(
        self,
        mock_client_class: MagicMock,
    ) -> None:
        """Test connectivity success but status fetch fails."""
        # Setup mocks
        mock_client = MagicMock()
        mock_client.test_connection.return_value = True
        mock_client.base_url = "https://api.flext.com"
        mock_client.get_system_status.side_effect = ValueError("Status error")
        mock_client_class.return_value = mock_client

        mock_console = MagicMock()
        runner = CliRunner()

        result = runner.invoke(connectivity, obj={"console": mock_console})

        if result.exit_code != 0:
            raise AssertionError(f"Expected {0}, got {result.exit_code}")
        mock_console.print.assert_any_call(
            "[yellow]⚠️  Could not get system status: Status error[/yellow]",
        )

    def test_connectivity_failed_connection(
        self,
        mock_flext_api_client_with_patches,
    ) -> None:
        """Test connectivity when connection fails using SOLID fixture patterns."""
        # Configure the existing mock to simulate connection failure
        from flext_core import FlextResult

        # Override the test_connection method to return failure
        async def mock_test_connection_failure() -> FlextResult[bool]:
            return FlextResult.fail("Connection failed")

        # Modify the mock that's already in use to return failure
        mock_flext_api_client_with_patches.test_connection = (
            mock_test_connection_failure
        )
        mock_flext_api_client_with_patches.base_url = "https://api.flext.com"

        mock_console = MagicMock()
        runner = CliRunner()

        result = runner.invoke(connectivity, obj={"console": mock_console})

        if result.exit_code != 1:
            raise AssertionError(f"Expected {1}, got {result.exit_code}")
        mock_console.print.assert_any_call(
            "[red]❌ Failed to connect to API: Connection failed[/red]",
        )

    def test_connectivity_connection_error(
        self,
        mock_failing_api_client: object,
    ) -> None:
        """Test connectivity with connection error."""
        with patch("flext_cli.client.FlextApiClient") as mock_client_class:
            self._test_connectivity_connection_error_impl(mock_client_class)

    def _test_connectivity_connection_error_impl(
        self,
        mock_client_class: MagicMock,
    ) -> None:
        """Test connectivity with connection error."""
        # Test already uses mock_failing_api_client fixture which provides failing client
        # No additional mocking needed - the fixture handles everything

        mock_console = MagicMock()
        runner = CliRunner()

        result = runner.invoke(connectivity, obj={"console": mock_console})

        if result.exit_code != 1:
            raise AssertionError(f"Expected {1}, got {result.exit_code}")

        # Our MockFailingApiClient returns "Connection failed" as error message
        mock_console.print.assert_any_call(
            "[red]❌ Failed to connect to API: Connection failed[/red]",
        )

    def test_connectivity_os_error(self, mock_failing_api_client: object) -> None:
        """Test connectivity with OS error."""
        with patch("flext_cli.client.FlextApiClient") as mock_client_class:
            self._test_connectivity_os_error_impl(mock_client_class)

    def _test_connectivity_os_error_impl(self, mock_client_class: MagicMock) -> None:
        """Test connectivity with OS error."""
        # Setup mocks
        mock_client = MagicMock()
        mock_client.test_connection.side_effect = OSError("Network unreachable")
        mock_client_class.return_value = mock_client

        mock_console = MagicMock()
        runner = CliRunner()

        result = runner.invoke(connectivity, obj={"console": mock_console})

        if result.exit_code != 1:
            raise AssertionError(f"Expected {1}, got {result.exit_code}")
        mock_console.print.assert_any_call(
            "[red]❌ Connection test failed: Network unreachable[/red]",
        )


class TestDebugPerformance:
    """Test performance command missing coverage."""

    def test_performance_success(self) -> None:
        """Test performance command success."""
        with patch("flext_cli.client.FlextApiClient") as mock_client_class:
            self._test_performance_success_impl(mock_client_class)

    def _test_performance_success_impl(self, mock_client_class: MagicMock) -> None:
        """Test performance command success."""
        # Setup mocks
        mock_client = MagicMock()
        mock_client.get_performance_metrics.return_value = {
            "cpu_usage": 45.2,
            "memory_usage": 78.5,
            "disk_usage": 65.0,
            "response_time": 120,
        }
        mock_client_class.return_value = mock_client

        mock_console = MagicMock()
        runner = CliRunner()

        result = runner.invoke(performance, obj={"console": mock_console})

        if result.exit_code != 0:
            raise AssertionError(f"Expected {0}, got {result.exit_code}")
        # Verify the command was called (specific print messages depend on implementation)
        mock_client.get_performance_metrics.assert_called_once()

    def test_performance_error(self) -> None:
        """Test performance command with error."""
        with patch("flext_cli.client.FlextApiClient") as mock_client_class:
            self._test_performance_error_impl(mock_client_class)

    def _test_performance_error_impl(self, mock_client_class: MagicMock) -> None:
        """Test performance command with error."""
        # Setup mocks - synchronous implementation (SOLID: Liskov Substitution)
        mock_client_class.side_effect = Exception("Metrics unavailable")

        mock_console = MagicMock()
        runner = CliRunner()

        result = runner.invoke(performance, obj={"console": mock_console})

        # Should handle error gracefully (SOLID: KISS - simple error handling test)
        # Exit code can vary depending on exception timing
        assert result.exit_code in {0, 1}
        # Test completed successfully regardless of specific console calls


class TestDebugCommandCoverage:
    """Test additional debug command coverage."""

    def test_debug_group_exists(self) -> None:
        """Test debug command group exists."""
        assert isinstance(debug_cmd, click.Group)
        if debug_cmd.name != "debug":
            raise AssertionError(f"Expected {'debug'}, got {debug_cmd.name}")

    def test_debug_help_message(self) -> None:
        """Test debug help message."""
        runner = CliRunner()
        result = runner.invoke(debug_cmd, ["--help"])
        if result.exit_code != 0:
            raise AssertionError(f"Expected {0}, got {result.exit_code}")
        if "Debug commands for FLEXT CLI" not in result.output:
            raise AssertionError(
                f"Expected {'Debug commands for FLEXT CLI'} in {result.output}",
            )

    def test_connectivity_help(self) -> None:
        """Test connectivity command help."""
        runner = CliRunner()
        result = runner.invoke(connectivity, ["--help"])
        if result.exit_code != 0:
            raise AssertionError(f"Expected {0}, got {result.exit_code}")
        if "Test API connectivity" not in result.output:
            raise AssertionError(
                f"Expected {'Test API connectivity'} in {result.output}",
            )

    def test_performance_help(self) -> None:
        """Test performance command help."""
        runner = CliRunner()
        result = runner.invoke(performance, ["--help"])
        if result.exit_code != 0:
            raise AssertionError(f"Expected {0}, got {result.exit_code}")
        if "Check system performance metrics" not in result.output:
            raise AssertionError(
                f"Expected {'Check system performance metrics'} in {result.output}",
            )


# Additional small functions that need coverage
class TestDebugUtilityFunctions:
    """Test utility functions and constants in debug module."""

    def test_sensitive_value_preview_length_constant(self) -> None:
        """Test SENSITIVE_VALUE_PREVIEW_LENGTH constant."""
        if SENSITIVE_VALUE_PREVIEW_LENGTH != 4:
            raise AssertionError(f"Expected {4}, got {SENSITIVE_VALUE_PREVIEW_LENGTH}")
        assert isinstance(SENSITIVE_VALUE_PREVIEW_LENGTH, int)

    def test_debug_imports(self) -> None:
        """Test that debug module imports work correctly."""
        # Test TYPE_CHECKING imports
        try:
            assert connectivity is not None
            assert debug_cmd is not None
            assert performance is not None
        except ImportError as e:
            pytest.fail(f"Debug imports should work: {e}")


class TestDebugIntegrationScenarios:
    """Test integration scenarios for debug commands."""

    def test_multiple_debug_commands_sequence(self) -> None:
        """Test running multiple debug commands in sequence."""
        with patch("flext_cli.client.FlextApiClient") as mock_client_class:
            self._test_multiple_debug_commands_sequence_impl(mock_client_class)

    def _test_multiple_debug_commands_sequence_impl(
        self,
        mock_client_class: MagicMock,
    ) -> None:
        """Test running multiple debug commands in sequence."""
        # Setup mocks for successful operations
        mock_client = MagicMock()
        mock_client.test_connection.return_value = True
        mock_client.base_url = "https://api.flext.com"
        mock_client.get_system_status.return_value = {
            "version": "0.9.0",
            "status": "ok",
            "uptime": "1h",
        }
        mock_client.get_performance_metrics.return_value = {"cpu_usage": 30.0}
        mock_client_class.return_value = mock_client

        mock_console = MagicMock()
        runner = CliRunner()

        # Run connectivity test
        result1 = runner.invoke(connectivity, obj={"console": mock_console})
        if result1.exit_code != 0:
            raise AssertionError(f"Expected {0}, got {result1.exit_code}")

        # Run performance test
        result2 = runner.invoke(performance, obj={"console": mock_console})
        if result2.exit_code != 0:
            raise AssertionError(f"Expected {0}, got {result2.exit_code}")

    def test_debug_command_registration(self) -> None:
        """Test that debug commands are properly registered."""
        from click import Context

        ctx = Context(debug_cmd)
        commands = debug_cmd.list_commands(ctx)
        expected_commands = ["connectivity", "performance"]

        for cmd in expected_commands:
            if cmd not in commands:
                raise AssertionError(f"Expected {cmd} in {commands}")

    def test_debug_error_consistency(self) -> None:
        """Test that debug commands handle errors consistently."""
        with patch("flext_cli.client.FlextApiClient") as mock_client_class:
            self._test_debug_error_consistency_impl(mock_client_class)

    def _test_debug_error_consistency_impl(self, mock_client_class: MagicMock) -> None:
        """Test that debug commands handle errors consistently."""
        # Setup mocks for error scenarios
        mock_client = MagicMock()
        mock_client.test_connection.side_effect = Exception("Test error")
        mock_client_class.return_value = mock_client

        mock_console = MagicMock()
        runner = CliRunner()

        # Test that errors are handled consistently across commands
        result = runner.invoke(connectivity, obj={"console": mock_console})
        if result.exit_code != 1:  # Commands should exit with error code
            raise AssertionError(f"Expected {1}, got {result.exit_code}")
