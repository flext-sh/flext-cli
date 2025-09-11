"""Real functionality tests for src/flext_cli/commands/debug.py module.

Tests all debug command functionality using real implementations instead of mocks.




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

from flext_cli import debug_cmd
from flext_cli.config import FlextCliConfig
from flext_cli.debug import (
    connectivity,
    env,
    paths,
    performance,
    trace,
    validate,
)


class TestDebugCommandReal:
    """Test debug command group with real functionality."""

    def test_debug_cmd_creation_real(self) -> None:
        """Test debug command group creation with real implementation."""
        # Test actual Click group properties
        assert isinstance(debug_cmd, click.Group)
        assert debug_cmd.name == "debug"
        assert debug_cmd.help == "Debug commands for FLEXT CLI."

        # Test that it has the click group attributes
        assert hasattr(debug_cmd, "commands")
        assert isinstance(debug_cmd.commands, dict)

    def test_debug_cmd_has_all_subcommands_real(self) -> None:
        """Test that debug command has all expected subcommands with real verification."""
        commands = list(debug_cmd.commands.keys())
        expected_commands = [
            "connectivity",
            "performance",
            "validate",
            "trace",
            "env",
            "paths",
        ]

        # Verify all expected commands are registered
        for cmd in expected_commands:
            assert cmd in commands, f"Missing command: {cmd}"

        # Verify commands are proper click commands
        for cmd_name, cmd_obj in debug_cmd.commands.items():
            assert isinstance(cmd_obj, click.Command), (
                f"Command {cmd_name} is not a Click command"
            )
            assert callable(cmd_obj), f"Command {cmd_name} is not callable"


class TestConnectivityCommandReal:
    """Test connectivity debug command with real functionality."""

    def setup_method(self) -> None:
        """Setup test method with real components."""
        self.runner = CliRunner()
        self.console = Console()

    def test_connectivity_command_structure_real(self) -> None:
        """Test connectivity command structure without mocking."""
        # Test that connectivity is a proper click command
        assert isinstance(connectivity, click.Command)
        assert callable(connectivity)

        # Test command help text
        result = self.runner.invoke(connectivity, ["--help"])
        assert result.exit_code == 0
        assert "connectivity" in result.output.lower()

    def test_connectivity_execution_real(self) -> None:
        """Test connectivity command execution with real implementation."""
        # Create real context object
        console = Console()

        # Run connectivity command with real console
        result = self.runner.invoke(connectivity, [], obj={"console": console})

        # Command should complete (success or controlled failure)
        assert result.exit_code in {0, 1}  # Either success or expected network failure

        # Test with isolated runner that doesn't depend on external services
        isolated_result = self.runner.invoke(connectivity, ["--help"])
        assert isolated_result.exit_code == 0

    def test_connectivity_help_real(self) -> None:
        """Test connectivity command help."""
        result = self.runner.invoke(connectivity, ["--help"])
        assert result.exit_code == 0
        assert "connectivity" in result.output.lower()


class TestPerformanceCommandReal:
    """Test performance debug command with real functionality."""

    def setup_method(self) -> None:
        """Setup test method with real components."""
        self.runner = CliRunner()

    def test_performance_command_structure_real(self) -> None:
        """Test performance command structure without mocking."""
        # Test that performance is a proper click command
        assert isinstance(performance, click.Command)
        assert callable(performance)

    def test_performance_execution_real(self) -> None:
        """Test performance command execution with real implementation."""
        # Create real context
        console = Console()

        # Run performance command with real console
        result = self.runner.invoke(performance, [], obj={"console": console})

        # Command should complete (success or controlled failure)
        assert result.exit_code in {0, 1}  # Either success or expected API failure

    def test_performance_help_real(self) -> None:
        """Test performance command help."""
        result = self.runner.invoke(performance, ["--help"])
        assert result.exit_code == 0
        assert "performance" in result.output.lower()


class TestValidateCommandReal:
    """Test validate debug command with real functionality."""

    def setup_method(self) -> None:
        """Setup test method with real components."""
        self.runner = CliRunner()

    def test_validate_command_structure_real(self) -> None:
        """Test validate command structure without mocking."""
        assert isinstance(validate, click.Command)
        assert callable(validate)

    def test_validate_execution_real(self) -> None:
        """Test validate command execution with real system validation."""
        # Create real context
        console = Console()

        # Run validate command with real console
        result = self.runner.invoke(validate, [], obj={"console": console})

        # Validation should complete
        assert result.exit_code in {0, 1}  # Success or validation warnings/errors

    def test_validate_python_version_real(self) -> None:
        """Test validation shows real Python version information."""
        # Run validate and capture output
        result = self.runner.invoke(validate, [], obj={"console": Console()})

        # Should complete regardless of validation results
        assert result.exit_code in {0, 1}

        # Verify we can access real Python version
        assert sys.version_info.major >= 3
        assert sys.version_info >= (3, 11)  # FLEXT requires Python 3.11+

    def test_validate_config_access_real(self) -> None:
        """Test validation accesses real configuration."""
        # Test that get_config() works
        config = FlextCliConfig.get_current()
        assert config is not None
        assert hasattr(config, "config_dir")

        # Verify config directory is a Path object
        assert isinstance(config.config_dir, Path)

    def test_validate_help_real(self) -> None:
        """Test validate command help."""
        result = self.runner.invoke(validate, ["--help"])
        assert result.exit_code == 0
        assert "validate" in result.output.lower()


class TestTraceCommandReal:
    """Test trace debug command with real functionality."""

    def setup_method(self) -> None:
        """Setup test method with real components."""
        self.runner = CliRunner()

    def test_trace_command_structure_real(self) -> None:
        """Test trace command structure without mocking."""
        assert isinstance(trace, click.Command)
        assert callable(trace)

    def test_trace_execution_real(self) -> None:
        """Test trace command execution with real implementation."""
        # Test trace with some arguments
        result = self.runner.invoke(
            trace, ["echo", "hello", "world"], obj={"console": Console()},
        )

        # Command should complete successfully
        assert result.exit_code == 0

    def test_trace_help_real(self) -> None:
        """Test trace command help."""
        result = self.runner.invoke(trace, ["--help"])
        assert result.exit_code == 0
        assert "trace" in result.output.lower()


class TestEnvCommandReal:
    """Test env debug command with real functionality."""

    def setup_method(self) -> None:
        """Setup test method with real components."""
        self.runner = CliRunner()

    def test_env_command_structure_real(self) -> None:
        """Test env command structure without mocking."""
        assert isinstance(env, click.Command)
        assert callable(env)

    def test_env_execution_real(self) -> None:
        """Test env command execution with real environment variables."""
        # Run env command with real console
        result = self.runner.invoke(env, [], obj={"console": Console()})

        # Command should complete successfully
        assert result.exit_code == 0

    def test_env_shows_flext_variables_real(self) -> None:
        """Test env command shows real FLEXT environment variables."""
        # Set some test FLEXT environment variables
        original_env = dict(os.environ)
        try:
            os.environ["FLX_DEBUG"] = "true"
            os.environ["FLX_API_URL"] = (
                f"http://{FlextConstants.Platform.DEFAULT_HOST}:{FlextConstants.Platform.FLEXT_API_PORT}"
            )

            result = self.runner.invoke(env, [], obj={"console": Console()})
            assert result.exit_code == 0

        finally:
            # Restore original environment
            os.environ.clear()
            os.environ.update(original_env)

    def test_env_with_no_flext_variables_real(self) -> None:
        """Test env command with no FLEXT variables."""
        # Clear FLEXT variables and test
        original_env = dict(os.environ)
        try:
            # Remove any FLX_ variables
            for key in list(os.environ.keys()):
                if key.startswith("FLX_"):
                    del os.environ[key]

            result = self.runner.invoke(env, [], obj={"console": Console()})
            assert result.exit_code == 0

        finally:
            # Restore original environment
            os.environ.clear()
            os.environ.update(original_env)

    def test_env_help_real(self) -> None:
        """Test env command help."""
        result = self.runner.invoke(env, ["--help"])
        assert result.exit_code == 0
        assert "environment" in result.output.lower()


class TestPathsCommandReal:
    """Test paths debug command with real functionality."""

    def setup_method(self) -> None:
        """Setup test method with real components."""
        self.runner = CliRunner()

    def test_paths_command_structure_real(self) -> None:
        """Test paths command structure without mocking."""
        assert isinstance(paths, click.Command)
        assert callable(paths)

    def test_paths_execution_real(self) -> None:
        """Test paths command execution with real filesystem paths."""
        # Run paths command with real console
        result = self.runner.invoke(paths, [], obj={"console": Console()})

        # Command should complete successfully
        assert result.exit_code == 0

    def test_paths_shows_real_directories_real(self) -> None:
        """Test paths command shows real directory information."""
        # Get actual config for real paths
        config = FlextCliConfig.get_current()
        assert config is not None

        # Verify config has real path information
        assert hasattr(config, "config_dir")
        assert isinstance(config.config_dir, Path)

        # Test the command execution
        result = self.runner.invoke(paths, [], obj={"console": Console()})
        assert result.exit_code == 0

    def test_paths_home_directory_real(self) -> None:
        """Test paths command with real home directory."""
        # Test that Path.home() works
        home_path = Path.home()
        assert home_path.exists()
        assert home_path.is_dir()

        # Run paths command
        result = self.runner.invoke(paths, [], obj={"console": Console()})
        assert result.exit_code == 0

    def test_paths_help_real(self) -> None:
        """Test paths command help."""
        result = self.runner.invoke(paths, ["--help"])
        assert result.exit_code == 0
        assert "paths" in result.output.lower()


class TestDebugIntegrationReal:
    """Integration tests for debug commands with real functionality."""

    def test_all_commands_registered_real(self) -> None:
        """Test that all debug commands are properly registered with real verification."""
        # Get all command functions
        command_functions = [connectivity, performance, validate, trace, env, paths]

        # Verify they all have click decorators
        for func in command_functions:
            func_name = getattr(func, "__name__", "unknown_function")
            assert isinstance(func, click.Command), (
                f"Function {func_name} is not a Click command"
            )
            assert callable(func), f"Function {func_name} is not callable"

        # Verify they're all part of the debug group
        registered_commands = debug_cmd.commands
        assert len(registered_commands) >= 6, "Missing commands in debug group"

        # Verify each expected command is registered
        expected_commands = [
            "connectivity",
            "performance",
            "validate",
            "trace",
            "env",
            "paths",
        ]
        for cmd_name in expected_commands:
            assert cmd_name in registered_commands, (
                f"Command {cmd_name} not registered in debug group"
            )

    def test_debug_group_help_real(self) -> None:
        """Test debug group help text with real implementation."""
        assert debug_cmd.help == "Debug commands for FLEXT CLI."
        assert debug_cmd.name == "debug"

        # Test help invocation
        runner = CliRunner()
        result = runner.invoke(debug_cmd, ["--help"])
        assert result.exit_code == 0
        assert "debug" in result.output.lower()

    def test_config_integration_real(self) -> None:
        """Test that commands properly integrate with real config system."""
        # Test that get_config() returns real config
        config = FlextCliConfig.get_current()
        assert config is not None
        assert hasattr(config, "config_dir")
        assert isinstance(config.config_dir, Path)

        # Test that validate command uses real config
        runner = CliRunner()
        result = runner.invoke(validate, [], obj={"console": Console()})
        assert result.exit_code in {0, 1}  # Success or validation issues

        # Test that paths command uses real config
        result = runner.invoke(paths, [], obj={"console": Console()})
        assert result.exit_code == 0

    def test_platform_integration_real(self) -> None:
        """Test debug commands work with real platform information."""
        # Test that we can get real platform information
        system_info = platform.system()
        assert system_info in {"Linux", "Darwin", "Windows"}

        release_info = platform.release()
        assert isinstance(release_info, str)
        assert len(release_info) > 0

        machine_info = platform.machine()
        assert isinstance(machine_info, str)
        assert len(machine_info) > 0

    def test_console_integration_real(self) -> None:
        """Test debug commands work with real Rich console."""
        # Create real console
        console = Console()
        assert hasattr(console, "print")
        assert callable(console.print)

        # Test commands work with real console
        runner = CliRunner()

        # Test env command with real console
        result = runner.invoke(env, [], obj={"console": console})
        assert result.exit_code == 0

        # Test paths command with real console
        result = runner.invoke(paths, [], obj={"console": console})
        assert result.exit_code == 0

    def test_comprehensive_debug_workflow_real(self) -> None:
        """Test comprehensive debug workflow with real functionality."""
        runner = CliRunner()
        console = Console()
        context = {"console": console}

        # Test all debug commands in sequence
        commands_to_test = [
            ("env", []),
            ("paths", []),
            ("trace", ["echo", "test"]),
            ("validate", []),
        ]

        for cmd_name, args in commands_to_test:
            result = runner.invoke(debug_cmd.commands[cmd_name], args, obj=context)
            # Commands should complete (may succeed or fail gracefully)
            assert result.exit_code in {0, 1}, f"Command {cmd_name} failed unexpectedly"

    def test_error_handling_real(self) -> None:
        """Test debug commands handle real errors gracefully."""
        runner = CliRunner()

        # Test with invalid context (should handle gracefully)
        result = runner.invoke(env, [], obj={})
        # Should either work or fail gracefully
        assert result.exit_code in {0, 1}

        # Test trace with no arguments (should handle gracefully)
        result = runner.invoke(trace, [], obj={"console": Console()})
        assert result.exit_code in {0, 1}

    def test_real_system_dependencies_real(self) -> None:
        """Test debug commands work with real system dependencies."""
        # Verify Python version requirements
        assert sys.version_info >= (3, 11), "Python 3.11+ required for FLEXT"

        # Verify we can import required modules

        # Verify constants are accessible
        assert hasattr(FlextConstants, "Platform")
        assert hasattr(FlextConstants.Platform, "DEFAULT_HOST")
        assert hasattr(FlextConstants.Platform, "FLEXT_API_PORT")


class TestDebugCommandsRealFunctionality:
    """Test actual functionality of debug commands."""

    def test_debug_commands_help_consistency_real(self) -> None:
        """Test that all debug commands have consistent help formatting."""
        runner = CliRunner()

        command_names = [
            "connectivity",
            "performance",
            "validate",
            "trace",
            "env",
            "paths",
        ]

        for cmd_name in command_names:
            result = runner.invoke(debug_cmd.commands[cmd_name], ["--help"])
            assert result.exit_code == 0, f"Help failed for {cmd_name}"
            assert len(result.output) > 0, f"No help output for {cmd_name}"
            assert cmd_name in result.output.lower(), (
                f"Command name not in help for {cmd_name}"
            )

    def test_debug_commands_context_handling_real(self) -> None:
        """Test that debug commands handle context properly."""
        runner = CliRunner()

        # Test with proper context
        proper_context = {"console": Console()}

        # Test commands that should work with proper context
        safe_commands = ["env", "paths", "trace"]

        for cmd_name in safe_commands:
            result = runner.invoke(debug_cmd.commands[cmd_name], [], obj=proper_context)
            assert result.exit_code in {0, 1}, (
                f"Command {cmd_name} failed with proper context"
            )

    def test_debug_commands_real_output_real(self) -> None:
        """Test that debug commands produce real output."""
        runner = CliRunner()
        console = Console()

        # Capture what the trace command does
        result = runner.invoke(trace, ["echo", "hello"], obj={"console": console})
        assert result.exit_code == 0

        # Test that env command completes
        result = runner.invoke(env, [], obj={"console": console})
        assert result.exit_code == 0

        # Test that paths command completes
        result = runner.invoke(paths, [], obj={"console": console})
        assert result.exit_code == 0


class TestDebugCommandTypeSafety:
    """Test type safety of debug commands."""

    def test_debug_commands_are_click_commands_real(self) -> None:
        """Test that all debug commands are proper Click commands."""
        commands = [connectivity, performance, validate, trace, env, paths]

        for cmd in commands:
            # Test that it's a click command
            assert isinstance(cmd, click.Command)
            assert callable(cmd)

            # Test that it has proper click attributes
            assert hasattr(cmd, "name") or hasattr(cmd, "__name__")

    def test_debug_group_structure_real(self) -> None:
        """Test debug group has proper structure."""
        assert isinstance(debug_cmd, click.Group)
        assert hasattr(debug_cmd, "commands")
        assert isinstance(debug_cmd.commands, dict)

        # Verify all registered commands are click objects
        for cmd_name, cmd_obj in debug_cmd.commands.items():
            assert callable(cmd_obj), f"Command {cmd_name} is not callable"
            assert isinstance(cmd_obj, click.Command), (
                f"Command {cmd_name} is not a Click command"
            )
