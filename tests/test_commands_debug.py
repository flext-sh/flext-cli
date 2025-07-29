"""Comprehensive tests for src/flext_cli/commands/debug.py module.

# Constants
EXPECTED_DATA_COUNT = 3

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

Tests all debug command functionality for 100% coverage.
"""

from __future__ import annotations

import asyncio
import os
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import click
import pytest
from flext_cli.commands.debug import (
    connectivity,
    debug_cmd,
    env,
    paths,
    performance,
    trace,
    validate,
)
from rich.console import Console
from rich.table import Table


class TestDebugCommand:
    """Test debug command group."""

    def test_debug_cmd_creation(self) -> None:
        """Test debug command group creation."""
        assert isinstance(debug_cmd, click.Group)
        if debug_cmd.name != "debug":
            raise AssertionError(f"Expected {"debug"}, got {debug_cmd.name}")
        assert debug_cmd.help == "Debug commands for FLEXT CLI."

    def test_debug_cmd_has_all_subcommands(self) -> None:
        """Test that debug command has all expected subcommands."""
        commands = list(debug_cmd.commands.keys())
        expected_commands = [
            "connectivity",
            "performance",
            "validate",
            "trace",
            "env",
            "paths",
        ]

        for cmd in expected_commands:
            if cmd in commands, f"Command '{cmd}' not found not in debug commands":
                raise AssertionError(f"Expected {cmd in commands, f"Command '{cmd}' not found} in {debug commands"}")


class TestConnectivityCommand:
    """Test connectivity debug command."""

    @pytest.fixture
    def mock_context(self):
        """Create mock click context."""
        console = MagicMock(spec=Console)
        ctx = MagicMock(spec=click.Context)
        ctx.obj = {"console": console}
        return ctx, console

    @patch("flext_cli.commands.debug.FlextApiClient")
    @patch("asyncio.run")
    def test_connectivity_success(
        self, mock_asyncio_run, mock_client_class, mock_context
    ) -> None:
        """Test successful connectivity check."""
        ctx, console = mock_context

        # Mock client
        mock_client = AsyncMock()
        mock_client.base_url = "http://localhost:8000"
        mock_client.test_connection.return_value = True
        mock_client.get_system_status.return_value = {
            "version": "1.0.0",
            "status": "healthy",
            "uptime": "5 days",
        }
        mock_client_class.return_value.__aenter__.return_value = mock_client

        # Call the command
        connectivity(ctx)

        # Verify asyncio.run was called
        mock_asyncio_run.assert_called_once()

        # Get the async function that was passed to asyncio.run
        async_func = mock_asyncio_run.call_args[0][0]

        # Run the async function to test it
        asyncio.run(async_func)

        # Verify client interactions
        mock_client.test_connection.assert_called_once()
        mock_client.get_system_status.assert_called_once()

    @patch("flext_cli.commands.debug.FlextApiClient")
    @patch("asyncio.run")
    def test_connectivity_connection_failed(
        self, mock_asyncio_run, mock_client_class, mock_context
    ) -> None:
        """Test connectivity check with connection failure."""
        ctx, console = mock_context

        # Mock client
        mock_client = AsyncMock()
        mock_client.base_url = "http://localhost:8000"
        mock_client.test_connection.return_value = False
        mock_client_class.return_value.__aenter__.return_value = mock_client

        # Call the command
        connectivity(ctx)

        # Verify asyncio.run was called
        mock_asyncio_run.assert_called_once()

        # Get the async function and run it
        async_func = mock_asyncio_run.call_args[0][0]

        # Test the async function
        with pytest.raises(SystemExit):
            asyncio.run(async_func)

        mock_client.test_connection.assert_called_once()

    @patch("flext_cli.commands.debug.FlextApiClient")
    @patch("asyncio.run")
    def test_connectivity_status_exception(
        self, mock_asyncio_run, mock_client_class, mock_context
    ) -> None:
        """Test connectivity check with status retrieval exception."""
        ctx, console = mock_context

        # Mock client
        mock_client = AsyncMock()
        mock_client.base_url = "http://localhost:8000"
        mock_client.test_connection.return_value = True
        mock_client.get_system_status.side_effect = Exception("Status error")
        mock_client_class.return_value.__aenter__.return_value = mock_client

        # Call the command
        connectivity(ctx)

        # Verify asyncio.run was called
        mock_asyncio_run.assert_called_once()

        # Get the async function and run it
        async_func = mock_asyncio_run.call_args[0][0]
        asyncio.run(async_func)

        # Should not exit since connection succeeded
        mock_client.test_connection.assert_called_once()
        mock_client.get_system_status.assert_called_once()

    @patch("flext_cli.commands.debug.FlextApiClient")
    @patch("asyncio.run")
    def test_connectivity_general_exception(
        self, mock_asyncio_run, mock_client_class, mock_context
    ) -> None:
        """Test connectivity check with general exception."""
        ctx, console = mock_context

        # Mock client to raise exception
        mock_client_class.side_effect = Exception("Connection error")

        # Call the command
        connectivity(ctx)

        # Verify asyncio.run was called
        mock_asyncio_run.assert_called_once()

        # Get the async function and test it
        async_func = mock_asyncio_run.call_args[0][0]

        with pytest.raises(SystemExit):
            asyncio.run(async_func)


class TestPerformanceCommand:
    """Test performance debug command."""

    @pytest.fixture
    def mock_context(self):
        """Create mock click context."""
        console = MagicMock(spec=Console)
        ctx = MagicMock(spec=click.Context)
        ctx.obj = {"console": console}
        return ctx, console

    @patch("flext_cli.commands.debug.FlextApiClient")
    @patch("flext_cli.commands.debug.Table")
    @patch("asyncio.run")
    def test_performance_success(
        self, mock_asyncio_run, mock_table_class, mock_client_class, mock_context
    ) -> None:
        """Test successful performance metrics retrieval."""
        ctx, console = mock_context

        # Mock client
        mock_client = AsyncMock()
        mock_client.get_system_metrics.return_value = {
            "cpu_usage": "25%",
            "memory_usage": "60%",
            "disk_usage": "40%",
        }
        mock_client_class.return_value.__aenter__.return_value = mock_client

        # Mock table
        mock_table = MagicMock(spec=Table)
        mock_table_class.return_value = mock_table

        # Call the command
        performance(ctx)

        # Verify asyncio.run was called
        mock_asyncio_run.assert_called_once()

        # Get the async function and run it
        async_func = mock_asyncio_run.call_args[0][0]
        asyncio.run(async_func)

        # Verify client interactions
        mock_client.get_system_metrics.assert_called_once()

        # Verify table creation and population
        mock_table_class.assert_called_once_with(title="System Performance Metrics")
        mock_table.add_column.assert_any_call("Metric", style="cyan")
        mock_table.add_column.assert_any_call("Value", style="white")

        # Should have added rows for each metric
        if mock_table.add_row.call_count != EXPECTED_DATA_COUNT:
            raise AssertionError(f"Expected {3}, got {mock_table.add_row.call_count}")

    @patch("flext_cli.commands.debug.FlextApiClient")
    @patch("asyncio.run")
    def test_performance_exception(
        self, mock_asyncio_run, mock_client_class, mock_context
    ) -> None:
        """Test performance command with exception."""
        ctx, console = mock_context

        # Mock client to raise exception
        mock_client = AsyncMock()
        mock_client.get_system_metrics.side_effect = Exception("Metrics error")
        mock_client_class.return_value.__aenter__.return_value = mock_client

        # Call the command
        performance(ctx)

        # Verify asyncio.run was called
        mock_asyncio_run.assert_called_once()

        # Get the async function and test it
        async_func = mock_asyncio_run.call_args[0][0]

        with pytest.raises(SystemExit):
            asyncio.run(async_func)


class TestValidateCommand:
    """Test validate debug command."""

    @pytest.fixture
    def mock_context(self):
        """Create mock click context."""
        console = MagicMock(spec=Console)
        ctx = MagicMock(spec=click.Context)
        ctx.obj = {"console": console}
        return ctx, console

    @patch("flext_cli.commands.debug.get_config")
    @patch("sys.version_info", (3, 11, 0))
    @patch("sys.version", "3.11.0 (main, Oct 24 2022)")
    def test_validate_success(self, mock_get_config, mock_context) -> None:
        """Test successful validation."""
        ctx, console = mock_context

        # Mock config
        mock_config = MagicMock()
        mock_config.config_dir = Path("/home/user/.flext")
        mock_get_config.return_value = mock_config

        # Mock config file exists
        with patch.object(Path, "exists", return_value=True):
            # Mock all required packages available
            with patch("builtins.__import__") as mock_import:
                mock_import.return_value = MagicMock()

                # Call the command
                validate(ctx)

                # Should not exit
                ctx.exit.assert_not_called()

    @patch("flext_cli.commands.debug.get_config")
    @patch("sys.version_info", (3, 9, 0))
    @patch("sys.version", "3.9.0 (main, Oct 24 2021)")
    def test_validate_old_python(self, mock_get_config, mock_context) -> None:
        """Test validation with old Python version."""
        ctx, console = mock_context

        # Mock config
        mock_config = MagicMock()
        mock_config.config_dir = Path("/home/user/.flext")
        mock_get_config.return_value = mock_config

        # Mock config file exists
        with patch.object(Path, "exists", return_value=True):
            # Mock all required packages available
            with patch("builtins.__import__") as mock_import:
                mock_import.return_value = MagicMock()

                # Call the command
                validate(ctx)

                # Should exit with error
                ctx.exit.assert_called_once_with(1)

    @patch("flext_cli.commands.debug.get_config")
    @patch("sys.version_info", (3, 11, 0))
    @patch("sys.version", "3.11.0 (main, Oct 24 2022)")
    def test_validate_missing_config(self, mock_get_config, mock_context) -> None:
        """Test validation with missing config file."""
        ctx, console = mock_context

        # Mock config
        mock_config = MagicMock()
        mock_config.config_dir = Path("/home/user/.flext")
        mock_get_config.return_value = mock_config

        # Mock config file doesn't exist
        with patch.object(Path, "exists", return_value=False):
            # Mock all required packages available
            with patch("builtins.__import__") as mock_import:
                mock_import.return_value = MagicMock()

                # Call the command
                validate(ctx)

                # Should not exit (warnings don't cause exit)
                ctx.exit.assert_not_called()

    @patch("flext_cli.commands.debug.get_config")
    @patch("sys.version_info", (3, 11, 0))
    @patch("sys.version", "3.11.0 (main, Oct 24 2022)")
    def test_validate_missing_packages(self, mock_get_config, mock_context) -> None:
        """Test validation with missing packages."""
        ctx, console = mock_context

        # Mock config
        mock_config = MagicMock()
        mock_config.config_dir = Path("/home/user/.flext")
        mock_get_config.return_value = mock_config

        # Mock config file exists
        with patch.object(Path, "exists", return_value=True):
            # Mock some packages missing
            def mock_import(package, *args, **kwargs):
                if package in ["click", "missing_package"]:
                    msg = f"No module named '{package}'"
                    raise ImportError(msg)
                return MagicMock()

            with patch("builtins.__import__", side_effect=mock_import):
                # Call the command
                validate(ctx)

                # Should exit with error
                ctx.exit.assert_called_once_with(1)

    @patch("flext_cli.commands.debug.get_config")
    @patch("sys.version_info", (3, 11, 0))
    @patch("sys.version", "3.11.0 (main, Oct 24 2022)")
    @patch("platform.system", return_value="Linux")
    @patch("platform.release", return_value="5.15.0")
    @patch("platform.machine", return_value="x86_64")
    def test_validate_environment_info(
        self, mock_machine, mock_release, mock_system, mock_get_config, mock_context
    ) -> None:
        """Test validation shows environment information."""
        ctx, console = mock_context

        # Mock config
        mock_config = MagicMock()
        mock_config.config_dir = Path("/home/user/.flext")
        mock_get_config.return_value = mock_config

        # Mock config file exists
        with patch.object(Path, "exists", return_value=True):
            # Mock all required packages available
            with patch("builtins.__import__") as mock_import:
                mock_import.return_value = MagicMock()

                # Call the command
                validate(ctx)

                # Verify platform info was called
                mock_system.assert_called_once()
                mock_release.assert_called_once()
                mock_machine.assert_called_once()


class TestTraceCommand:
    """Test trace debug command."""

    @pytest.fixture
    def mock_context(self):
        """Create mock click context."""
        console = MagicMock(spec=Console)
        ctx = MagicMock(spec=click.Context)
        ctx.obj = {"console": console}
        return ctx, console

    def test_trace_command(self, mock_context) -> None:
        """Test trace command."""
        ctx, console = mock_context

        # Call the command with test arguments
        trace(ctx, ("test", "command", "args"))

        # Verify console output
        console.print.assert_any_call(
            "[yellow]Command tracing not yet implemented[/yellow]"
        )
        console.print.assert_any_call("Would trace: test command args")


class TestEnvCommand:
    """Test env debug command."""

    @pytest.fixture
    def mock_context(self):
        """Create mock click context."""
        console = MagicMock(spec=Console)
        ctx = MagicMock(spec=click.Context)
        ctx.obj = {"console": console}
        return ctx, console

    @patch("flext_cli.commands.debug.Table")
    @patch.dict(
        os.environ,
        {
            "FLX_API_URL": "http://localhost:8000",
            "FLX_TOKEN": "secret123456",
            "FLX_DEBUG": "true",
            "OTHER_VAR": "not_flext",
        },
    )
    def test_env_with_variables(self, mock_table_class, mock_context) -> None:
        """Test env command with FLEXT variables."""
        ctx, console = mock_context

        # Mock table
        mock_table = MagicMock(spec=Table)
        mock_table_class.return_value = mock_table

        # Call the command
        env(ctx)

        # Verify table creation
        mock_table_class.assert_called_once_with(title="FLEXT Environment Variables")
        mock_table.add_column.assert_any_call("Variable", style="cyan")
        mock_table.add_column.assert_any_call("Value", style="white")

        # Should have added rows for FLEXT variables only
        if mock_table.add_row.call_count != EXPECTED_DATA_COUNT:
            raise AssertionError(f"Expected {3}, got {mock_table.add_row.call_count}")

        # Verify sensitive values are masked
        calls = mock_table.add_row.call_args_list
        token_call = next(call for call in calls if "FLX_TOKEN" in call[0])
        if "secr****" not in token_call[0][1]  # Token should be masked:
            raise AssertionError(f"Expected {"secr****"} in {token_call[0][1]  # Token should be masked}")

    @patch.dict(os.environ, {}, clear=True)
    def test_env_no_variables(self, mock_context) -> None:
        """Test env command with no FLEXT variables."""
        ctx, console = mock_context

        # Call the command
        env(ctx)

        # Should show no variables message
        console.print.assert_called_with(
            "[yellow]No FLEXT environment variables found[/yellow]"
        )

    @patch("flext_cli.commands.debug.Table")
    @patch.dict(
        os.environ,
        {
            "FLX_SECRET_KEY": "short",
            "FLX_API_KEY": "verylongapikey123456",
        },
    )
    def test_env_mask_sensitive_values(self, mock_table_class, mock_context) -> None:
        """Test env command masks sensitive values correctly."""
        ctx, console = mock_context

        # Mock table
        mock_table = MagicMock(spec=Table)
        mock_table_class.return_value = mock_table

        # Call the command
        env(ctx)

        # Verify both sensitive values are masked
        calls = mock_table.add_row.call_args_list

        # Short value should be completely masked
        short_call = next(call for call in calls if "FLX_SECRET_KEY" in call[0])
        if short_call[0][1] != "****":
            raise AssertionError(f"Expected {"****"}, got {short_call[0][1]}")

        # Long value should show first 4 chars + ****
        long_call = next(call for call in calls if "FLX_API_KEY" in call[0])
        if long_call[0][1] != "very****":
            raise AssertionError(f"Expected {"very****"}, got {long_call[0][1]}")


class TestPathsCommand:
    """Test paths debug command."""

    @pytest.fixture
    def mock_context(self):
        """Create mock click context."""
        console = MagicMock(spec=Console)
        ctx = MagicMock(spec=click.Context)
        ctx.obj = {"console": console}
        return ctx, console

    @patch("flext_cli.commands.debug.get_config")
    @patch("flext_cli.commands.debug.Table")
    @patch("flext_cli.commands.debug.Path")
    def test_paths_command(
        self, mock_path_class, mock_table_class, mock_get_config, mock_context
    ) -> None:
        """Test paths command."""
        ctx, console = mock_context

        # Mock config
        mock_config = MagicMock()
        mock_config.config_dir = Path("/home/user/.flext")
        mock_get_config.return_value = mock_config

        # Mock Path.home()
        mock_home = MagicMock()
        mock_home.__truediv__ = lambda self, other: Path(f"/home/user/{other}")
        mock_path_class.home.return_value = mock_home

        # Mock table
        mock_table = MagicMock(spec=Table)
        mock_table_class.return_value = mock_table

        # Mock path existence checks
        with patch.object(Path, "exists", return_value=True):
            # Call the command
            paths(ctx)

        # Verify table creation
        mock_table_class.assert_called_once_with(title="FLEXT CLI Paths")
        mock_table.add_column.assert_any_call("Path Type", style="cyan")
        mock_table.add_column.assert_any_call("Location", style="white")
        mock_table.add_column.assert_any_call("Exists", style="green")

        # Should have added rows for all paths
        if mock_table.add_row.call_count != 5:
            raise AssertionError(f"Expected {5}, got {mock_table.add_row.call_count}")

        # Verify all paths show as existing
        calls = mock_table.add_row.call_args_list
        for call in calls:
            if call[0][2] != "✅"  # All paths should exist:
                raise AssertionError(f"Expected {"✅"  # All paths should exist}, got {call[0][2]}")

    @patch("flext_cli.commands.debug.get_config")
    @patch("flext_cli.commands.debug.Table")
    @patch("flext_cli.commands.debug.Path")
    def test_paths_command_missing_paths(
        self, mock_path_class, mock_table_class, mock_get_config, mock_context
    ) -> None:
        """Test paths command with missing paths."""
        ctx, console = mock_context

        # Mock config
        mock_config = MagicMock()
        mock_config.config_dir = Path("/home/user/.flext")
        mock_get_config.return_value = mock_config

        # Mock Path.home()
        mock_home = MagicMock()
        mock_home.__truediv__ = lambda self, other: Path(f"/home/user/{other}")
        mock_path_class.home.return_value = mock_home

        # Mock table
        mock_table = MagicMock(spec=Table)
        mock_table_class.return_value = mock_table

        # Mock path existence checks (all missing)
        with patch.object(Path, "exists", return_value=False):
            # Call the command
            paths(ctx)

        # Should have added rows for all paths
        if mock_table.add_row.call_count != 5:
            raise AssertionError(f"Expected {5}, got {mock_table.add_row.call_count}")

        # Verify all paths show as missing
        calls = mock_table.add_row.call_args_list
        for call in calls:
            if call[0][2] != "❌"  # All paths should be missing:
                raise AssertionError(f"Expected {"❌"  # All paths should be missing}, got {call[0][2]}")


class TestDebugIntegration:
    """Integration tests for debug commands."""

    def test_all_commands_registered(self) -> None:
        """Test that all debug commands are properly registered."""
        # Get all command functions
        command_functions = [connectivity, performance, validate, trace, env, paths]

        # Verify they all have click decorators
        for func in command_functions:
            assert hasattr(func, "__click_params__"), (
                f"Function {func.__name__} missing click decorators"
            )

        # Verify they're all part of the debug group
        registered_commands = debug_cmd.commands
        if len(registered_commands) < 6, "Missing commands in debug group":
            raise AssertionError(f"Expected {len(registered_commands)} >= {6, "Missing commands in debug group"}")

    def test_debug_group_help(self) -> None:
        """Test debug group help text."""
        if debug_cmd.help != "Debug commands for FLEXT CLI.":
            raise AssertionError(f"Expected {"Debug commands for FLEXT CLI."}, got {debug_cmd.help}")
        assert debug_cmd.name == "debug"

    @patch("flext_cli.commands.debug.get_config")
    def test_config_integration(self, mock_get_config) -> None:
        """Test that commands properly integrate with config system."""
        # Mock config
        mock_config = MagicMock()
        mock_config.config_dir = Path("/test/config")
        mock_get_config.return_value = mock_config

        # Test that config is called by relevant commands
        console = MagicMock()
        ctx = MagicMock()
        ctx.obj = {"console": console}

        # Test validate command uses config
        with patch.object(Path, "exists", return_value=True):
            with patch("builtins.__import__", return_value=MagicMock()):
                validate(ctx)

        mock_get_config.assert_called()

        # Test paths command uses config
        mock_get_config.reset_mock()
        with patch("flext_cli.commands.debug.Table"):
            with patch("flext_cli.commands.debug.Path"):
                paths(ctx)

        mock_get_config.assert_called()
