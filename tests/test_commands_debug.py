"""Comprehensive tests for src/flext_cli/commands/debug.py module.

Tests all debug command functionality for 100% coverage.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import asyncio
import os
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import click
import pytest
from click.testing import CliRunner
from flext_core import FlextConstants, FlextResult
from rich.console import Console
from rich.table import Table

from flext_cli import (
    connectivity,
    debug_cmd,
    env,
    paths,
    performance,
    trace,
    validate,
)

# Constants
EXPECTED_DATA_COUNT = 3


class TestDebugCommand:
    """Test debug command group."""

    def test_debug_cmd_creation(self) -> None:
        """Test debug command group creation."""
        assert isinstance(debug_cmd, click.Group)
        if debug_cmd.name != "debug":
            raise AssertionError(f"Expected {'debug'}, got {debug_cmd.name}")
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
            if cmd not in commands:
                raise AssertionError(f"Expected {cmd} in debug commands")


class TestConnectivityCommand:
    """Test connectivity debug command."""

    def setup_method(self) -> None:
        """Setup test method."""
        self.runner = CliRunner()
        self.mock_console = MagicMock(spec=Console)

    def test_connectivity_success(
        self,
        mock_context: tuple[MagicMock, MagicMock],
    ) -> None:
        """Test successful connectivity check."""
        with (
            patch("flext_cli.commands.debug.get_default_cli_client") as mock_get_client,
            patch("asyncio.run") as mock_asyncio_run,
        ):
            self._test_connectivity_success_impl(
                mock_asyncio_run,
                mock_get_client,
                mock_context,
            )

    def _test_connectivity_success_impl(
        self,
        mock_asyncio_run: MagicMock,
        mock_get_client: MagicMock,
        mock_context: tuple[MagicMock, MagicMock],
    ) -> None:
        """Test successful connectivity check implementation."""
        _ctx, console = mock_context

        # Mock client with FlextResult patterns
        mock_client = AsyncMock()
        mock_client.base_url = f"http://{FlextConstants.Platform.DEFAULT_HOST}:{FlextConstants.Platform.FLEXT_API_PORT}"
        mock_client.test_connection.return_value = FlextResult[None].ok(True)
        mock_client.get_system_status.return_value = FlextResult[None].ok(
            {
                "version": "0.9.0",
                "status": "healthy",
                "uptime": "5 days",
            },
        )
        mock_get_client.return_value = mock_client

        # Import and call command using Click runner
        runner = CliRunner()
        result = runner.invoke(connectivity, obj={"console": console})

        # Should complete successfully
        assert result.exit_code == 0

        # Verify asyncio.run was called
        mock_asyncio_run.assert_called_once()

        # Get the async function that was passed to asyncio.run
        async_func = mock_asyncio_run.call_args[0][0]

        # Run the async function to test it
        asyncio.run(async_func)

        # Verify client interactions
        mock_client.test_connection.assert_called_once()
        mock_client.get_system_status.assert_called_once()

    def test_connectivity_connection_failed(self) -> None:
        """Test connectivity check with connection failure."""
        with patch(
            "flext_cli.commands.debug.get_default_cli_client",
        ) as mock_get_client:
            self._test_connectivity_connection_failed_impl(mock_get_client)

    def _test_connectivity_connection_failed_impl(
        self,
        mock_get_client: MagicMock,
    ) -> None:
        mock_client = AsyncMock()
        mock_client.base_url = f"http://{FlextConstants.Platform.DEFAULT_HOST}:{FlextConstants.Platform.FLEXT_API_PORT}"
        mock_client.test_connection.return_value = FlextResult[None].fail("Connection failed")
        mock_get_client.return_value = mock_client

        # Use CliRunner to test command
        result = self.runner.invoke(
            connectivity,
            [],
            obj={"console": self.mock_console},
        )

        # Should exit with error code 1
        assert result.exit_code == 1

    def test_connectivity_status_exception(
        self,
        mock_context: tuple[MagicMock, MagicMock],
    ) -> None:
        """Test connectivity check with status retrieval exception."""
        with (
            patch("flext_cli.commands.debug.get_default_cli_client") as mock_get_client,
            patch("asyncio.run") as mock_asyncio_run,
        ):
            self._test_connectivity_status_exception_impl(
                mock_asyncio_run,
                mock_get_client,
                mock_context,
            )

    def _test_connectivity_status_exception_impl(
        self,
        mock_asyncio_run: MagicMock,
        mock_get_client: MagicMock,
        mock_context: tuple[MagicMock, MagicMock],
    ) -> None:
        """Test connectivity check with status retrieval exception implementation."""
        ctx, _console = mock_context

        # Mock client
        mock_client = AsyncMock()
        mock_client.base_url = f"http://{FlextConstants.Platform.DEFAULT_HOST}:{FlextConstants.Platform.FLEXT_API_PORT}"
        mock_client.test_connection.return_value = FlextResult[None].ok(True)
        mock_client.get_system_status.side_effect = Exception("Status error")
        mock_get_client.return_value = mock_client

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

    def test_connectivity_general_exception(
        self,
        mock_context: tuple[MagicMock, MagicMock],
    ) -> None:
        """Test connectivity check with general exception."""
        with (
            patch("flext_cli.commands.debug.get_default_cli_client") as mock_get_client,
            patch("asyncio.run") as mock_asyncio_run,
        ):
            self._test_connectivity_general_exception_impl(
                mock_asyncio_run,
                mock_get_client,
                mock_context,
            )

    def _test_connectivity_general_exception_impl(
        self,
        mock_asyncio_run: MagicMock,
        mock_get_client: MagicMock,
        mock_context: tuple[MagicMock, MagicMock],
    ) -> None:
        """Test connectivity check with general exception implementation."""
        ctx, _console = mock_context

        # Mock client to raise exception
        mock_get_client.side_effect = Exception("Connection error")

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

    def test_performance_success(
        self,
        mock_context: tuple[MagicMock, MagicMock],
    ) -> None:
        """Test successful performance metrics retrieval."""
        with (
            patch("flext_cli.commands.debug.get_default_cli_client") as mock_get_client,
            patch("flext_cli.commands.debug.Table") as mock_table_class,
        ):
            self._test_performance_success_simplified(
                mock_table_class,
                mock_get_client,
                mock_context,
            )

    def _test_performance_success_simplified(
        self,
        mock_table_class: MagicMock,
        mock_get_client: MagicMock,
        mock_context: tuple[MagicMock, MagicMock],
    ) -> None:
        """Test successful performance metrics retrieval - simplified approach."""
        _ctx, console = mock_context

        # Mock client with FlextResult response

        mock_client = AsyncMock()
        mock_client.get_system_status.return_value = FlextResult[None].ok(
            {
                "cpu_usage": "25%",
                "memory_usage": "60%",
                "disk_usage": "40%",
            },
        )
        mock_get_client.return_value = mock_client

        # Mock table
        mock_table = MagicMock(spec=Table)
        mock_table_class.return_value = mock_table

        # Call the command using CliRunner (without mocking asyncio.run)

        runner = CliRunner()
        result = runner.invoke(performance, obj={"console": console})

        # Should complete successfully
        assert result.exit_code == 0

        # Verify table creation and population
        mock_table_class.assert_called_once_with(title="System Performance Metrics")
        mock_table.add_column.assert_any_call("Metric", style="cyan")
        mock_table.add_column.assert_any_call("Value", style="white")

        # Should have added rows for each metric (4 metrics total)
        assert mock_table.add_row.call_count == 4

    def test_performance_exception(self) -> None:
        """Test performance command with exception."""
        with patch(
            "flext_cli.commands.debug.get_default_cli_client",
        ) as mock_get_client:
            # Setup mock to raise exception
            mock_client = AsyncMock()
            mock_client.get_system_status.side_effect = Exception("API error")
            mock_get_client.return_value = mock_client

            # Call the command using CliRunner

            runner = CliRunner()
            mock_console = MagicMock()
            result = runner.invoke(performance, obj={"console": mock_console})

            # Should exit with error
            assert result.exit_code == 1


class TestValidateCommand:
    """Test validate debug command."""

    def test_validate_success(
        self,
        mock_context: tuple[MagicMock, MagicMock],
    ) -> None:
        """Test successful validation."""
        with (
            patch("flext_cli.commands.debug.get_config") as mock_get_config,
            patch("sys.version_info", (3, 11, 0)),
            patch("sys.version", "3.11.0 (main, Oct 24 2022)"),
        ):
            self._test_validate_success_impl(mock_get_config, mock_context)

    def _test_validate_success_impl(
        self,
        mock_get_config: MagicMock,
        mock_context: tuple[MagicMock, MagicMock],
    ) -> None:
        """Test successful validation implementation."""
        ctx, _console = mock_context

        # Mock config
        mock_config = MagicMock()
        mock_config.config_dir = Path("/home/user/.flext")
        mock_get_config.return_value = mock_config

        # Mock config file exists
        with (
            patch.object(Path, "exists", return_value=True),
            # Mock all required packages available
            patch("builtins.__import__") as mock_import,
        ):
            mock_import.return_value = MagicMock()

            # Call the command
            validate(ctx)

            # Should not exit
            ctx.exit.assert_not_called()

    @patch("flext_cli.commands.debug.get_config")
    @patch("sys.version_info", (3, 9, 0))
    @patch("sys.version", "3.9.0 (main, Oct 24 2021)")
    def test_validate_old_python(
        self,
        mock_get_config: MagicMock,
        mock_context: tuple[MagicMock, MagicMock],
    ) -> None:
        """Test validation with old Python version."""
        ctx, _console = mock_context

        # Mock config
        mock_config = MagicMock()
        mock_config.config_dir = Path("/home/user/.flext")
        mock_get_config.return_value = mock_config

        # Mock config file exists
        with (
            patch.object(Path, "exists", return_value=True),
            # Mock all required packages available
            patch("builtins.__import__") as mock_import,
        ):
            mock_import.return_value = MagicMock()

            # Call the command
            validate(ctx)

            # Should exit with error
            ctx.exit.assert_called_once_with(1)

    @patch("flext_cli.commands.debug.get_config")
    @patch("sys.version_info", (3, 11, 0))
    @patch("sys.version", "3.11.0 (main, Oct 24 2022)")
    def test_validate_missing_config(
        self,
        mock_get_config: MagicMock,
        mock_context: tuple[MagicMock, MagicMock],
    ) -> None:
        """Test validation with missing config file."""
        ctx, _console = mock_context

        # Mock config
        mock_config = MagicMock()
        mock_config.config_dir = Path("/home/user/.flext")
        mock_get_config.return_value = mock_config

        # Mock config file doesn't exist
        with (
            patch.object(Path, "exists", return_value=False),
            # Mock all required packages available
            patch("builtins.__import__") as mock_import,
        ):
            mock_import.return_value = MagicMock()

            # Call the command
            validate(ctx)

            # Should not exit (warnings don't cause exit)
            ctx.exit.assert_not_called()

    @patch("flext_cli.commands.debug.get_config")
    @patch("sys.version_info", (3, 11, 0))
    @patch("sys.version", "3.11.0 (main, Oct 24 2022)")
    def test_validate_missing_packages(
        self,
        mock_get_config: MagicMock,
        mock_context: tuple[MagicMock, MagicMock],
    ) -> None:
        """Test validation with missing packages."""
        ctx, _console = mock_context

        # Mock config
        mock_config = MagicMock()
        mock_config.config_dir = Path("/home/user/.flext")
        mock_get_config.return_value = mock_config

        # Mock config file exists
        with patch.object(Path, "exists", return_value=True):
            # Mock some packages missing
            def mock_import(package: str, *args: object, **kwargs: object) -> object:  # noqa: ARG001
                if package in {"click", "missing_package"}:
                    msg: str = f"No module named '{package}'"
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
        self,
        mock_machine: MagicMock,
        mock_release: MagicMock,
        mock_system: MagicMock,
        mock_get_config: MagicMock,
        mock_context: tuple[MagicMock, MagicMock],
    ) -> None:
        """Test validation shows environment information."""
        ctx, _console = mock_context

        # Mock config
        mock_config = MagicMock()
        mock_config.config_dir = Path("/home/user/.flext")
        mock_get_config.return_value = mock_config

        # Mock config file exists
        with (
            patch.object(Path, "exists", return_value=True),
            # Mock all required packages available
            patch("builtins.__import__") as mock_import,
        ):
            mock_import.return_value = MagicMock()

            # Call the command
            validate(ctx)

            # Verify platform info was called
            mock_system.assert_called_once()
            mock_release.assert_called_once()
            mock_machine.assert_called_once()


class TestTraceCommand:
    """Test trace debug command."""

    def test_trace_command(self) -> None:
        """Test trace command."""
        # Use CliRunner to test the command with proper console mock
        runner = CliRunner()
        result = runner.invoke(
            trace,
            ["test", "command", "args"],
            obj={"console": MagicMock()},
        )

        # Command should succeed
        assert result.exit_code == 0
        # Note: Output is captured by console mock, not result.output


class TestEnvCommand:
    """Test env debug command."""

    @patch("flext_cli.commands.debug.Table")
    @patch.dict(
        os.environ,
        {
            "FLX_API_URL": f"http://{FlextConstants.Platform.DEFAULT_HOST}:{FlextConstants.Platform.FLEXT_API_PORT}",
            "FLX_TOKEN": "secret123456",
            "FLX_DEBUG": "true",
            "OTHER_VAR": "not_flext",
        },
    )
    def test_env_with_variables(
        self,
        mock_table_class: MagicMock,
    ) -> None:
        """Test env command with FLEXT variables."""
        # Mock table
        mock_table = MagicMock(spec=Table)
        mock_table_class.return_value = mock_table

        # Use CliRunner to test the command with console
        runner = CliRunner()
        mock_console = MagicMock()
        result = runner.invoke(env, [], obj={"console": mock_console})

        # Command should succeed
        assert result.exit_code == 0

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
        if "secr****" not in token_call[0][1]:  # Token should be masked
            raise AssertionError(f"Expected {'secr****'} in {token_call[0][1]}")

    @patch.dict(os.environ, {}, clear=True)
    def test_env_no_variables(self) -> None:
        """Test env command with no FLEXT variables."""
        # Use CliRunner to test the command with console
        runner = CliRunner()
        mock_console = MagicMock()
        result = runner.invoke(env, [], obj={"console": mock_console})

        # Command should succeed
        assert result.exit_code == 0
        # Should call console.print with no variables message
        mock_console.print.assert_called_with(
            "[yellow]No FLEXT environment variables found[/yellow]",
        )

    @patch("flext_cli.commands.debug.Table")
    @patch.dict(
        os.environ,
        {
            "FLX_SECRET_KEY": "short",
            "FLX_API_KEY": "verylongapikey123456",
        },
    )
    def test_env_mask_sensitive_values(
        self,
        mock_table_class: MagicMock,
    ) -> None:
        """Test env command masks sensitive values correctly."""
        # Mock table
        mock_table = MagicMock(spec=Table)
        mock_table_class.return_value = mock_table

        # Use CliRunner to test the command with proper console mock
        runner = CliRunner()
        mock_console = MagicMock()
        result = runner.invoke(env, [], obj={"console": mock_console})

        # Command should succeed
        assert result.exit_code == 0

        # Verify both sensitive values are masked
        calls = mock_table.add_row.call_args_list

        # Short value (5 chars) should show first 4 chars + ****
        short_call = next(call for call in calls if "FLX_SECRET_KEY" in call[0])
        if short_call[0][1] != "shor****":
            raise AssertionError(f"Expected {'shor****'}, got {short_call[0][1]}")

        # Long value should show first 4 chars + ****
        long_call = next(call for call in calls if "FLX_API_KEY" in call[0])
        if long_call[0][1] != "very****":
            raise AssertionError(f"Expected {'very****'}, got {long_call[0][1]}")


class TestPathsCommand:
    """Test paths debug command."""

    @patch("flext_cli.commands.debug.get_config")
    @patch("flext_cli.commands.debug.Table")
    @patch("flext_cli.commands.debug.Path")
    def test_paths_command(
        self,
        mock_path_class: MagicMock,
        mock_table_class: MagicMock,
        mock_get_config: MagicMock,
    ) -> None:
        """Test paths command."""
        # Mock config
        mock_config = MagicMock()
        mock_config.config_dir = Path("/home/user/.flext")
        mock_get_config.return_value = mock_config

        # Mock Path.home()
        mock_home = MagicMock()
        mock_home.__truediv__ = lambda self, other: Path(f"/home/user/{other}")  # noqa: ARG005
        mock_path_class.home.return_value = mock_home

        # Mock table
        mock_table = MagicMock(spec=Table)
        mock_table_class.return_value = mock_table

        # Mock path existence checks
        with patch.object(Path, "exists", return_value=True):
            # Use CliRunner to test the command with proper console mock
            runner = CliRunner()
            result = runner.invoke(paths, [], obj={"console": MagicMock()})

            # Command should succeed
            assert result.exit_code == 0

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
            if call[0][2] != "✅":
                raise AssertionError(f"Expected {'✅'} in {call[0][2]}")

    @patch("flext_cli.commands.debug.get_config")
    @patch("flext_cli.commands.debug.Table")
    @patch("flext_cli.commands.debug.Path")
    def test_paths_command_missing_paths(
        self,
        mock_path_class: MagicMock,
        mock_table_class: MagicMock,
        mock_get_config: MagicMock,
    ) -> None:
        """Test paths command with missing paths."""
        # Mock config
        mock_config = MagicMock()
        mock_config.config_dir = Path("/home/user/.flext")
        mock_get_config.return_value = mock_config

        # Mock Path.home()
        mock_home = MagicMock()
        mock_home.__truediv__ = lambda self, other: Path(f"/home/user/{other}")  # noqa: ARG005
        mock_path_class.home.return_value = mock_home

        # Mock table
        mock_table = MagicMock(spec=Table)
        mock_table_class.return_value = mock_table

        # Mock path existence checks (all missing)
        with patch.object(Path, "exists", return_value=False):
            # Use CliRunner to test the command with proper console mock
            runner = CliRunner()
            result = runner.invoke(paths, [], obj={"console": MagicMock()})

            # Command should succeed
            assert result.exit_code == 0

        # Should have added rows for all paths
        if mock_table.add_row.call_count != 5:
            raise AssertionError(f"Expected {5}, got {mock_table.add_row.call_count}")

        # Verify all paths show as missing
        calls = mock_table.add_row.call_args_list
        for call in calls:
            if call[0][2] != "❌":
                raise AssertionError(f"Expected {'❌'} in {call[0][2]}")


class TestDebugIntegration:
    """Integration tests for debug commands."""

    def test_all_commands_registered(self) -> None:
        """Test that all debug commands are properly registered."""
        # Get all command functions
        command_functions = [connectivity, performance, validate, trace, env, paths]

        # Verify they all have click decorators
        for func in command_functions:
            func_name = getattr(func, "__name__", "unknown_function")
            assert hasattr(func, "__click_params__"), (
                f"Function {func_name} missing click decorators"
            )

        # Verify they're all part of the debug group
        registered_commands = debug_cmd.commands
        if len(registered_commands) < 6:
            raise AssertionError(
                f"Expected {len(registered_commands)} >= {6}, Missing commands in debug group",
            )

    def test_debug_group_help(self) -> None:
        """Test debug group help text."""
        if debug_cmd.help != "Debug commands for FLEXT CLI.":
            raise AssertionError(
                f"Expected {'Debug commands for FLEXT CLI.'}, got {debug_cmd.help}",
            )
        assert debug_cmd.name == "debug"

    @patch("flext_cli.commands.debug.get_config")
    def test_config_integration(
        self,
        mock_get_config: MagicMock,
    ) -> None:
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
        with (
            patch.object(Path, "exists", return_value=True),
            patch("builtins.__import__", return_value=MagicMock()),
        ):
            validate(ctx)

        mock_get_config.assert_called()

        # Test paths command uses config
        mock_get_config.reset_mock()
        with (
            patch("flext_cli.commands.debug.Table"),
            patch("flext_cli.commands.debug.Path"),
        ):
            paths(ctx)

        mock_get_config.assert_called()
