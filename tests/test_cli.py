"""Tests for CLI main entry point.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""


from __future__ import annotations

import inspect
import os

from click.testing import CliRunner

from flext_cli import cli, main
from flext_cli.cli import FlextCliMain
from flext_cli.config import FlextCliConfig


class TestCliMain:
    """Test CLI main command group."""

    def setup_method(self) -> None:
        """Set up test environment."""
        self.runner = CliRunner()

    def test_cli_help(self) -> None:
        """Test CLI shows help when no command provided."""
        result = self.runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "FLEXT Command Line Interface" in result.output

    def test_cli_version(self) -> None:
        """Test CLI version display."""
        result = self.runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        # Should contain version info
        assert "flext" in result.output.lower()

    def test_cli_no_command_shows_help(self) -> None:
        """Test CLI shows help when invoked without subcommand."""
        result = self.runner.invoke(cli, [])
        assert result.exit_code == 0
        # Should show help content
        assert "Usage:" in result.output

    def test_cli_main_initialization(self) -> None:
        """Test FlextCliMain initialization."""
        # Test normal initialization
        cli_main = FlextCliMain()
        assert cli_main is not None
        assert hasattr(cli_main, "_constants")
        assert hasattr(cli_main, "_container")
        assert hasattr(cli_main, "_logger")

    def test_load_constants_metadata_success(self) -> None:
        """Test _load_constants_metadata success case."""
        cli_main = FlextCliMain()
        result = cli_main._load_constants_metadata()

        assert result.is_success
        assert result.value is not None

    def test_get_logger(self) -> None:
        """Test get_logger method."""
        cli_main = FlextCliMain()
        logger = cli_main.get_logger()

        assert logger is not None
        assert hasattr(logger, "info")
        assert hasattr(logger, "error")
        assert hasattr(logger, "debug")

    def test_create_cli_options_default(self) -> None:
        """Test create_cli_options with default values."""
        cli_main = FlextCliMain()
        result = cli_main.create_cli_options()

        assert result.is_success
        options = result.value
        assert options["profile"] == "default"
        assert options["output_format"] == "table"
        assert options["debug"] is False
        assert options["quiet"] is False
        assert options["log_level"] is None

    def test_create_cli_options_custom(self) -> None:
        """Test create_cli_options with custom values."""
        cli_main = FlextCliMain()
        result = cli_main.create_cli_options(
            profile="test",
            output="json",
            debug=True,
            quiet=True,
            log_level="DEBUG"
        )

        assert result.is_success
        options = result.value
        assert options["profile"] == "test"
        assert options["output_format"] == "json"
        assert options["debug"] is True
        assert options["quiet"] is True
        assert options["log_level"] == "DEBUG"

    def test_cli_debug_option(self) -> None:
        """Test CLI debug option."""
        result = self.runner.invoke(cli, ["--debug"])
        assert result.exit_code == 0
        # Debug output should show profile info
        assert "Profile:" in result.output

    def test_cli_profile_option(self) -> None:
        """Test CLI profile option."""
        result = self.runner.invoke(cli, ["--profile", "test", "--debug"])
        assert result.exit_code == 0
        # Should show the test profile
        assert "Profile: test" in result.output

    def test_cli_output_format_option(self) -> None:
        """Test CLI debug option shows output format."""
        result = self.runner.invoke(cli, ["--debug"])
        assert result.exit_code == 0
        # Should show default table format
        assert "Output Format: table" in result.output

    def test_cli_quiet_option(self) -> None:
        """Test CLI quiet option suppresses output."""
        result = self.runner.invoke(cli, ["--quiet"])
        assert result.exit_code == 0
        # Quiet mode should still work but suppress non-error output
        # Help is still shown when no command provided

    def test_cli_invalid_output_format(self) -> None:
        """Test CLI with invalid output format."""
        result = self.runner.invoke(cli, ["--output", "invalid"])
        assert result.exit_code != 0
        # Should show error for invalid choice

    def test_cli_context_setup_real(self) -> None:
        """Test CLI context is properly set up with real implementation."""
        # Test that CLI can execute without context errors
        result = self.runner.invoke(cli, ["--debug"])
        assert result.exit_code == 0

        # Verify debug output shows actual configuration
        assert "Profile:" in result.output

        # Test that configuration can be accessed
        test_config = FlextCliConfig().model_dump()
        assert "profile" in test_config
        assert "debug" in test_config

    def test_cli_interactive_command(self) -> None:
        """Test interactive command placeholder."""
        result = self.runner.invoke(cli, ["interactive"])
        assert result.exit_code == 0
        # Should show placeholder message
        assert "PLACEHOLDER" in result.output or "coming soon" in result.output.lower()

    def test_cli_version_command(self) -> None:
        """Test version command."""
        result = self.runner.invoke(cli, ["version"])
        assert result.exit_code == 0
        # Should show version information
        assert "FLEXT CLI" in result.output or "Version" in result.output


class TestMainEntryPoint:
    """Test main() entry point function."""

    def test_main_function_signature(self) -> None:
        """Test main() function signature and existence."""
        # Verify main function exists and is callable
        assert callable(main)

        # Check function signature
        sig = inspect.signature(main)
        assert len(sig.parameters) == 0  # main() takes no parameters

        # Verify main function is importable and accessible
        assert main is not None

    def test_main_cli_integration_real(self) -> None:
        """Test main() integration with real CLI functionality."""
        # Test main integrates with CLI by checking it can handle help
        # We can't easily test the real main() without SystemExit,
        # but we can test the CLI it wraps
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "FLEXT Command Line Interface" in result.output

        # Test version command integration
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "flext" in result.output.lower()


class TestCliIntegration:
    """Integration tests for CLI with command groups."""

    def setup_method(self) -> None:
        """Set up test environment."""
        self.runner = CliRunner()

    def test_auth_command_registered(self) -> None:
        """Test auth command is registered and accessible."""
        result = self.runner.invoke(cli, ["auth", "--help"])
        assert result.exit_code == 0
        assert "authentication" in result.output.lower()

    def test_config_command_registered(self) -> None:
        """Test config command is registered and accessible."""
        result = self.runner.invoke(cli, ["config", "--help"])
        assert result.exit_code == 0
        assert "configuration" in result.output.lower()

    def test_debug_command_registered(self) -> None:
        """Test debug command is registered and accessible."""
        result = self.runner.invoke(cli, ["debug", "--help"])
        assert result.exit_code == 0
        assert "debug" in result.output.lower()

    def test_cli_with_global_options_and_subcommand(self) -> None:
        """Test CLI with global options combined with subcommand."""
        result = self.runner.invoke(
            cli,
            ["--debug", "--profile", "test", "auth", "--help"],
        )
        assert result.exit_code == 0
        # Should show debug info and auth help
        assert "Profile: test" in result.output
        assert "authentication" in result.output.lower()

    def test_cli_context_passed_to_subcommands(self) -> None:
        """Test CLI context is properly passed to subcommands."""
        # This is tested indirectly through successful subcommand execution
        result = self.runner.invoke(cli, ["debug", "env"])
        # Should execute without context errors
        assert result.exit_code == 0


class TestCliErrorHandling:
    """Test CLI error handling scenarios."""

    def setup_method(self) -> None:
        """Set up test environment."""
        self.runner = CliRunner()

    def test_cli_with_unknown_command(self) -> None:
        """Test CLI behavior with unknown command."""
        result = self.runner.invoke(cli, ["unknown-command"])
        assert result.exit_code != 0
        # Should show error message
        assert "No such command" in result.output or "Usage:" in result.output

    def test_cli_with_invalid_option(self) -> None:
        """Test CLI behavior with invalid global option."""
        result = self.runner.invoke(cli, ["--invalid-option"])
        assert result.exit_code != 0
        # Should show error about unknown option

    def test_cli_environment_variable_integration_real(self) -> None:
        """Test CLI functionality with environment variables."""
        # Test that CLI executes successfully regardless of environment
        original_debug = os.environ.get("FLX_DEBUG")
        original_profile = os.environ.get("FLX_PROFILE")

        try:
            # Set environment variables (CLI may use them in future)
            os.environ["FLX_DEBUG"] = "true"
            os.environ["FLX_PROFILE"] = "test"

            # Test that CLI still works with explicit options
            result = self.runner.invoke(cli, ["--debug"])
            assert result.exit_code == 0
            # Should show debug output from explicit flag
            assert "Profile:" in result.output

        finally:
            # Restore original environment
            if original_debug is not None:
                os.environ["FLX_DEBUG"] = original_debug
            elif "FLX_DEBUG" in os.environ:
                del os.environ["FLX_DEBUG"]

            if original_profile is not None:
                os.environ["FLX_PROFILE"] = original_profile
            elif "FLX_PROFILE" in os.environ:
                del os.environ["FLX_PROFILE"]


class TestCliConfiguration:
    """Test CLI configuration handling."""

    def setup_method(self) -> None:
        """Set up test environment."""
        self.runner = CliRunner()

    def test_cli_config_loading_real(self) -> None:
        """Test CLI loads configuration correctly with real implementation."""
        # Test that CLI can load and use real configuration
        result = self.runner.invoke(cli, ["--debug"])
        assert result.exit_code == 0

        # Verify configuration is loaded by checking debug output
        assert "Profile:" in result.output
        assert "Output Format:" in result.output

        # Test configuration with different values
        result = self.runner.invoke(
            cli, ["--profile", "test", "--debug"],
        )
        assert result.exit_code == 0
        assert "Profile: test" in result.output
        assert "Output Format: table" in result.output

    def test_cli_context_creation_real(self) -> None:
        """Test CLI creates proper CLI context with real implementation."""
        # Test that CLI context is created and works properly
        result = self.runner.invoke(cli, ["--debug"])
        assert result.exit_code == 0

        # Test that CLI can execute subcommands (proves context works)
        result = self.runner.invoke(cli, ["debug", "env"])
        assert result.exit_code == 0

        # Test that CLI can handle configuration commands
        result = self.runner.invoke(cli, ["config", "--help"])
        assert result.exit_code == 0

    def test_cli_configuration_validation(self) -> None:
        """Test CLI configuration validation with real values."""
        # Test valid profile options (existing CLI option)
        valid_profiles = ["default", "test", "dev", "prod"]
        for profile in valid_profiles:
            result = self.runner.invoke(cli, ["--profile", profile, "--debug"])
            assert result.exit_code == 0
            assert f"Profile: {profile}" in result.output

        # Test that CLI configuration can be inspected
        test_config = FlextCliConfig().model_dump()
        assert isinstance(test_config, dict)
        assert "profile" in test_config
