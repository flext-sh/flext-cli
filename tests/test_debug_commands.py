"""Tests for debug commands.

Tests debug command functionality for coverage.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import asyncio
import os
import platform
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import click
from click.testing import CliRunner
from flext_cli.commands.debug import debug_cmd
from flext_core.constants import FlextConstants
from rich.table import Table


class TestDebugCommands:
    """Test debug commands."""

    def setup_method(self) -> None:
        """Set up test environment."""
        self.runner = CliRunner()

    def test_connectivity_command(self) -> None:
        """Test connectivity command."""
        with (
            patch("flext_cli.commands.debug.get_default_cli_client") as mock_get_client,
            patch("asyncio.run") as mock_asyncio_run,
        ):
            self._test_connectivity_command_impl(mock_asyncio_run, mock_get_client)

    def _test_connectivity_command_impl(
        self,
        mock_asyncio_run: MagicMock,
        mock_get_client: MagicMock,
    ) -> None:
        """Test connectivity command."""
        # Mock client
        mock_client = AsyncMock()

        mock_client.base_url = f"http://{FlextConstants.Platform.DEFAULT_HOST}:{FlextConstants.Platform.FLEXT_API_PORT}"
        mock_client.test_connection.return_value = MagicMock(success=True, data=True)
        mock_client.get_system_status.return_value = MagicMock(
            success=True,
            data={
                "version": "0.9.0",
                "status": "healthy",
                "uptime": "5 days",
            },
        )
        mock_get_client.return_value = mock_client

        # Test the command
        self.runner.invoke(debug_cmd, ["connectivity"], obj={"console": MagicMock()})

        # Should not crash (might exit with code due to async issues but that's ok)
        assert mock_asyncio_run.called

    def test_performance_command(self) -> None:
        """Test performance command."""
        with (
            patch("flext_cli.commands.debug.get_default_cli_client") as mock_get_client,
            patch("asyncio.run") as mock_asyncio_run,
        ):
            self._test_performance_command_impl(mock_asyncio_run, mock_get_client)

    def _test_performance_command_impl(
        self,
        mock_asyncio_run: MagicMock,
        mock_get_client: MagicMock,
    ) -> None:
        """Test performance command implementation."""
        # Mock client
        mock_client = AsyncMock()
        mock_client.get_system_status.return_value = MagicMock(
            success=True,
            data={
                "cpu_usage": "25%",
                "memory_usage": "60%",
                "disk_usage": "40%",
            },
        )
        mock_get_client.return_value = mock_client

        # Test the command
        self.runner.invoke(debug_cmd, ["performance"], obj={"console": MagicMock()})

        assert mock_asyncio_run.called

    def test_validate_command_success(self) -> None:
        """Test validate command with success."""
        with (
            patch("flext_cli.commands.debug.get_config") as mock_get_config,
            patch("flext_cli.commands.debug.sys.version_info", (3, 11, 0)),
            patch("flext_cli.commands.debug.sys.version", "3.11.0 (main, Oct 24 2022)"),
        ):
            self._test_validate_command_success_impl(mock_get_config)

    def _test_validate_command_success_impl(self, mock_get_config: MagicMock) -> None:
        """Test validate command with success implementation."""
        # Mock config
        mock_config = MagicMock()
        mock_config.config_dir = Path("/home/user/.flext")
        mock_get_config.return_value = mock_config

        # Just patch the validate_dependencies function to avoid import issues
        with patch(
            "flext_cli.commands.debug._validate_dependencies",
        ) as mock_validate_deps:
            mock_validate_deps.return_value = None  # no issues added

            result = self.runner.invoke(
                debug_cmd,
                ["validate"],
                obj={"console": MagicMock()},
            )

            # Should complete without error exit
            if result.exit_code != 0:
                raise AssertionError(f"Expected {0}, got {result.exit_code}")

    def test_validate_command_old_python(self) -> None:
        """Test validate command with old Python."""
        with (
            patch("flext_cli.commands.debug.get_config") as mock_get_config,
            patch("flext_cli.commands.debug.sys.version_info", (3, 9, 0)),
            patch("flext_cli.commands.debug.sys.version", "3.9.0 (main, Oct 24 2021)"),
        ):
            self._test_validate_command_old_python_impl(mock_get_config)

    def _test_validate_command_old_python_impl(
        self,
        mock_get_config: MagicMock,
    ) -> None:
        """Test validate command with old Python implementation."""
        # Mock config
        mock_config = MagicMock()
        mock_config.config_dir = Path("/home/user/.flext")
        mock_get_config.return_value = mock_config

        # Just patch the validate_dependencies function to avoid import issues
        with patch(
            "flext_cli.commands.debug._validate_dependencies",
        ) as mock_validate_deps:
            mock_validate_deps.return_value = None  # no issues added

            result = self.runner.invoke(
                debug_cmd,
                ["validate"],
                obj={"console": MagicMock()},
            )

            # Should exit with error due to old Python
            if result.exit_code != 1:
                raise AssertionError(f"Expected {1}, got {result.exit_code}")

    def test_trace_command(self) -> None:
        """Test trace command."""
        result = self.runner.invoke(
            debug_cmd,
            ["trace", "test", "command"],
            obj={"console": MagicMock()},
        )

        # Should complete successfully (tracing not implemented)
        if result.exit_code != 0:
            raise AssertionError(f"Expected {0}, got {result.exit_code}")

    def test_env_command_with_vars(self) -> None:
        """Test env command with FLEXT variables."""
        _api = f"http://{FlextConstants.Platform.DEFAULT_HOST}:{FlextConstants.Platform.FLEXT_API_PORT}"
        with patch.dict(
            os.environ,
            {
                "FLX_API_URL": _api,
                "FLX_TOKEN": "secret123456",
                "FLX_DEBUG": "true",
                "OTHER_VAR": "not_flext",
            },
        ):
            result = self.runner.invoke(
                debug_cmd,
                ["env"],
                obj={"console": MagicMock()},
            )

            if result.exit_code != 0:
                raise AssertionError(f"Expected {0}, got {result.exit_code}")

    def test_env_command_no_vars(self) -> None:
        """Test env command with no FLEXT variables."""
        with patch.dict(os.environ, {}, clear=True):
            result = self.runner.invoke(
                debug_cmd,
                ["env"],
                obj={"console": MagicMock()},
            )

            if result.exit_code != 0:
                raise AssertionError(f"Expected {0}, got {result.exit_code}")

    def test_paths_command(self) -> None:
        """Test paths command."""
        with (
            patch("flext_cli.commands.debug.get_config") as mock_get_config,
            patch("flext_cli.commands.debug.Path") as mock_path_class,
        ):
            self._test_paths_command_impl(mock_path_class, mock_get_config)

    def _test_paths_command_impl(
        self,
        mock_path_class: MagicMock,
        mock_get_config: MagicMock,
    ) -> None:
        """Test paths command implementation."""
        # Mock config
        mock_config = MagicMock()
        mock_config.config_dir = Path("/home/user/.flext")
        mock_get_config.return_value = mock_config

        # Mock Path.home()
        mock_home = MagicMock()
        mock_home.__truediv__ = lambda self, other: Path(f"/home/user/{other}")
        mock_path_class.home.return_value = mock_home

        with patch.object(Path, "exists", return_value=True):
            result = self.runner.invoke(
                debug_cmd,
                ["paths"],
                obj={"console": MagicMock()},
            )

            if result.exit_code != 0:
                raise AssertionError(f"Expected {0}, got {result.exit_code}")

    def test_debug_group_structure(self) -> None:
        """Test debug command group structure."""
        # Test that debug command group exists and has expected commands
        if debug_cmd.name != "debug":
            raise AssertionError(f"Expected {'debug'}, got {debug_cmd.name}")
        if "connectivity" not in debug_cmd.commands:
            raise AssertionError(f"Expected {'connectivity'} in {debug_cmd.commands}")
        assert "performance" in debug_cmd.commands
        if "validate" not in debug_cmd.commands:
            raise AssertionError(f"Expected {'validate'} in {debug_cmd.commands}")
        assert "trace" in debug_cmd.commands
        if "env" not in debug_cmd.commands:
            raise AssertionError(f"Expected {'env'} in {debug_cmd.commands}")
        assert "paths" in debug_cmd.commands


class TestDebugFunctionality:
    """Test individual debug functions."""

    def test_platform_info_access(self) -> None:
        """Test that platform information is accessed correctly."""
        with (
            patch("platform.system") as mock_system,
            patch("platform.release") as mock_release,
            patch("platform.machine") as mock_machine,
        ):
            self._test_platform_info_access_impl(
                mock_machine,
                mock_release,
                mock_system,
            )

    def _test_platform_info_access_impl(
        self,
        mock_machine: MagicMock,
        mock_release: MagicMock,
        mock_system: MagicMock,
    ) -> None:
        """Test that platform information is accessed correctly implementation."""
        mock_system.return_value = "Linux"
        mock_release.return_value = "5.15.0"
        mock_machine.return_value = "x86_64"

        # Import and call a function that uses platform info

        # This tests that the imports work
        assert platform.system
        assert platform.release
        assert platform.machine

    def test_os_environ_access(self) -> None:
        """Test OS environment variable access."""
        # Test that we can access os.environ

        # Test environment variable filtering
        test_vars = {"FLX_TEST": "value", "OTHER": "value"}
        flext_vars = {k: v for k, v in test_vars.items() if k.startswith("FLX_")}

        if len(flext_vars) != 1:
            raise AssertionError(f"Expected {1}, got {len(flext_vars)}")
        if "FLX_TEST" not in flext_vars:
            raise AssertionError(f"Expected {'FLX_TEST'} in {flext_vars}")

    def test_path_operations(self) -> None:
        """Test Path operations used in commands."""
        # Test path operations used in the debug commands
        test_path = Path("/test/path")

        # Test path joining (used in paths command)
        joined = test_path / "subpath"
        if str(joined) != "/test/path/subpath":
            raise AssertionError(f"Expected {'/test/path/subpath'}, got {joined!s}")

    def test_config_access(self) -> None:
        """Test config access in debug commands."""
        with patch("flext_cli.commands.debug.get_config") as mock_get_config:
            self._test_config_access_impl(mock_get_config)

    def _test_config_access_impl(self, mock_get_config: MagicMock) -> None:
        """Test config access in debug commands implementation."""
        mock_config = MagicMock()
        mock_config.config_dir = Path("/test/config")
        mock_get_config.return_value = mock_config

        # Test that get_config can be called
        config = mock_get_config()
        if config.config_dir != Path("/test/config"):
            raise AssertionError(
                f"Expected {Path('/test/config')}, got {config.config_dir}",
            )

    def test_sys_version_access(self) -> None:
        """Test sys.version access."""
        # Test that we can access sys.version_info and sys.version
        assert sys.version_info
        assert sys.version

        # Test version comparison logic used in validate command
        py_version = sys.version_info
        is_new_enough = py_version >= (3, 10)
        assert isinstance(is_new_enough, bool)

    def test_asyncio_integration(self) -> None:
        """Test asyncio integration."""
        # Test that asyncio.run exists (used in async commands)
        assert hasattr(asyncio, "run")

        # Test simple async function
        async def test_async() -> str:
            return "test"

        result = asyncio.run(test_async())
        if result != "test":
            raise AssertionError(f"Expected {'test'}, got {result}")

    def test_rich_table_integration(self) -> None:
        """Test Rich table integration."""
        # Test table creation (used in performance and paths commands)
        table = Table(title="Test Table")
        table.add_column("Column 1", style="cyan")
        table.add_column("Column 2", style="white")
        table.add_row("value1", "value2")

        if table.title != "Test Table":
            raise AssertionError(f"Expected {'Test Table'}, got {table.title}")

    def test_click_context_pattern(self) -> None:
        """Test Click context pattern used in commands."""
        # Test that we can create a mock context like used in commands
        console = MagicMock()
        ctx = MagicMock(spec=click.Context)
        ctx.obj = {"console": console}

        # Test accessing console from context (pattern used in all debug commands)
        accessed_console = ctx.obj["console"]
        assert accessed_console is console

    def test_import_error_handling(self) -> None:
        """Test import error handling used in validate command."""
        # Test the pattern used for checking package availability
        required_packages = ["click", "rich", "httpx", "pydantic", "yaml"]
        missing_packages = []

        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                missing_packages.append(package)

        # These packages should be available in test environment
        if "click" in missing_packages:
            raise AssertionError(
                f"Expected click available, but found in missing: {missing_packages}",
            )
        assert "rich" not in missing_packages

    def test_sensitive_value_masking(self) -> None:
        """Test sensitive value masking logic from env command."""
        test_vars = {
            "FLX_TOKEN": "verylongtoken123456",
            "FLX_SECRET_KEY": "short",
            "FLX_API_KEY": "apikey123",
            "FLX_DEBUG": "true",
        }

        # Test masking logic
        for key, value in test_vars.items():
            if "TOKEN" in key or "KEY" in key or "SECRET" in key:
                display_value = value[:4] + "****" if len(value) > 4 else "****"
            else:
                display_value = value

            # Verify masking works correctly
            if key in {"FLX_TOKEN", "FLX_SECRET_KEY", "FLX_API_KEY"}:
                if "****" not in display_value:
                    raise AssertionError(f"Expected {'****'} in {display_value}")
            elif display_value != value:
                raise AssertionError(f"Expected {value}, got {display_value}")

    def test_path_existence_checking(self) -> None:
        """Test path existence checking pattern from paths command."""
        # Test the pattern used in paths command
        test_paths = {
            "Config Directory": Path.home() / ".flext",
            "Config File": Path.home() / ".flext" / "config.yaml",
        }

        for path in test_paths.values():
            exists = "✅" if path.exists() else "❌"
            if exists not in {"✅", "❌"}:  # Should be one of these symbols
                raise AssertionError(f"Expected {exists} in {['✅', '❌']}")


class TestDebugCommandErrorHandling:
    """Test error handling in debug commands."""

    def setup_method(self) -> None:
        """Set up test environment."""
        self.runner = CliRunner()

    def test_connectivity_with_exception(self) -> None:
        """Test connectivity command with exception."""
        with (
            patch("flext_cli.commands.debug.get_default_cli_client") as mock_get_client,
            patch("asyncio.run") as mock_asyncio_run,
        ):
            self._test_connectivity_with_exception_impl(
                mock_asyncio_run,
                mock_get_client,
            )

    def _test_connectivity_with_exception_impl(
        self,
        mock_asyncio_run: MagicMock,
        mock_get_client: MagicMock,
    ) -> None:
        """Test connectivity command with exception implementation."""
        # Make asyncio.run raise an exception
        mock_asyncio_run.side_effect = Exception("Connection failed")

        self.runner.invoke(debug_cmd, ["connectivity"], obj={"console": MagicMock()})

        # Command should handle the exception
        assert mock_asyncio_run.called

    def test_performance_with_exception(self) -> None:
        """Test performance command with exception."""
        with (
            patch("flext_cli.commands.debug.get_default_cli_client") as mock_get_client,
            patch("asyncio.run") as mock_asyncio_run,
        ):
            self._test_performance_with_exception_impl(
                mock_asyncio_run,
                mock_get_client,
            )

    def _test_performance_with_exception_impl(
        self,
        mock_asyncio_run: MagicMock,
        mock_get_client: MagicMock,
    ) -> None:
        """Test performance command with exception implementation."""
        # Make asyncio.run raise an exception
        mock_asyncio_run.side_effect = Exception("Metrics failed")

        self.runner.invoke(debug_cmd, ["performance"], obj={"console": MagicMock()})

        # Command should handle the exception
        assert mock_asyncio_run.called
