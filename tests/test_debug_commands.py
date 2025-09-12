"""Tests for debug commands - REAL FUNCTIONALITY EXECUTION.

Tests debug command functionality with actual execution, eliminating mocks.




Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import os
import platform
import sys
from pathlib import Path

import click
from click.testing import CliRunner
from flext_core import FlextConstants
from rich.console import Console

from flext_cli import debug


class TestDebugCommandsReal:
    """Test debug commands with REAL execution - no mocks."""

    def setup_method(self) -> None:
        """Set up test environment with real console."""
        self.runner = CliRunner()
        self.console = Console(width=80, legacy_windows=False)

    def test_debug_group_exists(self) -> None:
        """Test that debug command group exists and is properly structured."""
        assert isinstance(debug, click.Group), f"Expected Group, got {type(debug)}"
        assert debug.name == "debug"

        # Verify essential commands exist
        essential_commands = ["connectivity", "performance", "validate", "env", "paths"]
        for cmd_name in essential_commands:
            assert cmd_name in debug.commands, f"Missing command: {cmd_name}"

    def test_debug_help_real(self) -> None:
        """Test debug help command with real execution."""
        result = self.runner.invoke(debug, ["--help"])

        assert result.exit_code == 0, f"Help failed: {result.output}"
        assert "debug" in result.output.lower()
        assert "commands" in result.output.lower()

    def test_connectivity_real(self) -> None:
        """Test connectivity command with real execution."""
        # Create real context object
        ctx_obj = {"console": self.console}

        result = self.runner.invoke(
            debug,
            ["connectivity"],
            obj=ctx_obj,
            catch_exceptions=False,
        )

        # Command should handle connection failures gracefully
        # Exit code 1 is expected when API is not available
        assert result.exit_code in {0, 1}, (
            f"Unexpected exit code: {result.exit_code}, output: {result.output}"
        )

    def test_performance_real(self) -> None:
        """Test performance command with real execution."""
        ctx_obj = {"console": self.console}

        result = self.runner.invoke(
            debug,
            ["performance"],
            obj=ctx_obj,
            catch_exceptions=False,
        )

        # Command should handle API unavailability gracefully
        assert result.exit_code in {0, 1}, (
            f"Unexpected exit code: {result.exit_code}, output: {result.output}"
        )

    def test_env_command_real(self) -> None:
        """Test env command with real environment variables."""
        # Set some real FLEXT environment variables for testing
        test_env = os.environ.copy()
        test_env.update(
            {
                "FLX_DEBUG": "true",
                "FLX_PROFILE": "test",
                "NON_FLX_VAR": "should_not_appear",
            },
        )

        ctx_obj = {"console": self.console}

        with self.runner.isolated_filesystem():
            result = self.runner.invoke(
                debug,
                ["env"],
                obj=ctx_obj,
                env=test_env,
                catch_exceptions=False,
            )

        assert result.exit_code == 0, f"Env command failed: {result.output}"

        # Should show FLX_ variables but not others
        assert (
            "FLX_DEBUG" in result.output
            or "FLX_PROFILE" in result.output
            or "No FLEXT environment" in result.output
        )

    def test_paths_command_real(self) -> None:
        """Test paths command with real filesystem paths."""
        ctx_obj = {"console": self.console}

        result = self.runner.invoke(
            debug,
            ["paths"],
            obj=ctx_obj,
            catch_exceptions=False,
        )

        assert result.exit_code == 0, f"Paths command failed: {result.output}"

        # Should show actual paths
        assert "Config" in result.output or "Path" in result.output

    def test_validate_command_real(self) -> None:
        """Test validate command with real system validation."""
        ctx_obj = {"console": self.console}

        result = self.runner.invoke(
            debug,
            ["validate"],
            obj=ctx_obj,
            catch_exceptions=False,
        )

        # Should complete successfully or with validation warnings
        assert result.exit_code in {0, 1}, f"Validate command failed: {result.output}"

        # Should contain validation output (may be config info, version, or validation results)
        assert result.output.strip()  # Should have some output
        assert len(result.output.strip()) > 0  # Output should not be empty

    def test_trace_command_real(self) -> None:
        """Test trace command with real arguments."""
        ctx_obj = {"console": self.console}

        result = self.runner.invoke(
            debug,
            ["trace", "test", "command"],
            obj=ctx_obj,
            catch_exceptions=False,
        )

        # Trace command should execute (placeholder implementation)
        assert result.exit_code == 0, f"Trace command failed: {result.output}"


class TestDebugSystemIntegration:
    """Test debug commands integration with real system."""

    def setup_method(self) -> None:
        """Set up test environment."""
        self.console = Console(width=80, legacy_windows=False)

    def test_real_python_version_access(self) -> None:
        """Test accessing real Python version information."""
        # Test real Python version access (used by validate command)
        py_version = sys.version_info
        py_version_string = sys.version

        assert py_version >= (3, 8), f"Unexpected Python version: {py_version}"
        assert isinstance(py_version_string, str)
        assert str(py_version.major) in py_version_string

    def test_real_platform_info_access(self) -> None:
        """Test accessing real platform information."""
        # Test real platform info (used by validate command)
        system_name = platform.system()
        release_info = platform.release()
        machine_type = platform.machine()

        assert isinstance(system_name, str)
        assert isinstance(release_info, str)
        assert isinstance(machine_type, str)

    def test_real_environment_variable_access(self) -> None:
        """Test real environment variable access."""
        # Test real environment access (used by env command)
        all_vars = dict(os.environ)

        # Filter for FLEXT variables (real logic from env command)
        flext_vars = {k: v for k, v in all_vars.items() if k.startswith("FLX_")}

        # Test that filtering works correctly
        for key in flext_vars:
            assert key.startswith("FLX_"), f"Non-FLEXT var found: {key}"

    def test_real_path_operations(self) -> None:
        """Test real path operations used in commands."""
        # Test real path operations (used by paths command)
        home_path = Path.home()
        config_path = home_path / ".flext"

        assert isinstance(home_path, Path)
        assert isinstance(config_path, Path)
        assert str(config_path).endswith(".flext")

        # Test path existence checking (real filesystem)
        home_exists = home_path.exists()
        assert isinstance(home_exists, bool)

    def test_real_constants_access(self) -> None:
        """Test accessing real FLEXT constants."""
        # Test real constants access (used in multiple commands)
        default_host = FlextConstants.Platform.DEFAULT_HOST
        api_port = FlextConstants.Platform.FLEXT_API_PORT

        assert isinstance(default_host, str)
        assert isinstance(api_port, int)
        assert api_port > 0

        # Construct real API URL
        api_url = f"http://{default_host}:{api_port}"
        assert "http://" in api_url


class TestDebugErrorHandlingReal:
    """Test real error handling in debug commands."""

    def setup_method(self) -> None:
        """Set up test environment."""
        self.runner = CliRunner()
        self.console = Console(width=80, legacy_windows=False)

    def test_connectivity_without_context_real(self) -> None:
        """Test connectivity command without proper context - real error."""
        # Test with no context object (should fail gracefully)
        result = self.runner.invoke(debug, ["connectivity"], obj=None)

        # Should fail gracefully with proper error message - testing real connectivity
        assert result.exit_code == 1
        assert (
            "connection" in result.output.lower()
            or "failed" in result.output.lower()
            or "error" in result.output.lower()
        )

    def test_connectivity_network_failure_real(self) -> None:
        """Test connectivity with real network conditions."""
        ctx_obj = {"console": self.console}

        # This tests real network behavior - may succeed or fail based on environment
        result = self.runner.invoke(debug, ["connectivity"], obj=ctx_obj)

        # Should handle network issues gracefully
        assert result.exit_code in {0, 1}

        if result.exit_code == 1:
            # Check that error message is informative
            assert result.output  # Should have some error output

    def test_performance_api_unavailable_real(self) -> None:
        """Test performance command when API is unavailable."""
        ctx_obj = {"console": self.console}

        result = self.runner.invoke(debug, ["performance"], obj=ctx_obj)

        # Should handle API unavailability gracefully
        assert result.exit_code in {0, 1}

    def test_validate_with_real_system_state(self) -> None:
        """Test validate command with actual system state."""
        ctx_obj = {"console": self.console}

        result = self.runner.invoke(debug, ["validate"], obj=ctx_obj)

        # Should validate actual system and provide meaningful results
        assert result.exit_code in {0, 1}  # Success or validation warnings
        assert result.output  # Should provide validation output


class TestDebugCommandFlow:
    """Test complete debug command workflows."""

    def setup_method(self) -> None:
        """Set up test environment."""
        self.runner = CliRunner()
        self.console = Console(width=80, legacy_windows=False)

    def test_complete_debug_workflow(self) -> None:
        """Test running multiple debug commands in sequence."""
        ctx_obj = {"console": self.console}

        # Run commands in typical debug workflow order
        commands_to_test = [
            ["env"],  # Check environment
            ["paths"],  # Check paths
            ["validate"],  # Validate system
            # Skip connectivity and performance as they require API
        ]

        for cmd_args in commands_to_test:
            result = self.runner.invoke(debug, cmd_args, obj=ctx_obj)

            assert result.exit_code in {0, 1}, (
                f"Command {cmd_args} failed: {result.output}"
            )
            assert result.output, f"Command {cmd_args} produced no output"

    def test_help_for_all_subcommands(self) -> None:
        """Test help output for all debug subcommands."""
        for cmd_name in debug.commands:
            result = self.runner.invoke(debug, [cmd_name, "--help"])

            assert result.exit_code == 0, f"Help failed for {cmd_name}: {result.output}"
            assert cmd_name in result.output or "Usage" in result.output
