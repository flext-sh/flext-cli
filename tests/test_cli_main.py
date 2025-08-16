"""Tests for CLI main entry point.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import os
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from flext_cli.cli import cli, main


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
        """Test CLI output format option."""
        result = self.runner.invoke(cli, ["--output", "json", "--debug"])
        assert result.exit_code == 0
        # Should show json format
        assert "Output format: json" in result.output

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

    def test_cli_context_setup(self) -> None:
        """Test CLI context is properly set up."""
        with (
            patch("flext_cli.cli.get_config") as mock_get_config,
            patch("flext_cli.cli.CLIContext") as mock_cli_context,
        ):
            # Mock config
            mock_config = MagicMock()
            mock_config.model_copy.return_value = mock_config
            mock_get_config.return_value = mock_config

            # Mock CLIContext
            mock_cli_context.return_value = MagicMock()

            result = self.runner.invoke(cli, ["--debug"])
            assert result.exit_code == 0

            # Config should be loaded
            mock_get_config.assert_called_once()

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

    @patch("flext_cli.cli.FlextUtilities.handle_cli_main_errors")
    def test_main_calls_error_handler(self, mock_handler: MagicMock) -> None:
        """Test main() calls FlextUtilities error handler."""
        main()

        # Should call error handler with cli function
        mock_handler.assert_called_once_with(cli, debug_mode=True)

    def test_main_integration(self) -> None:
        """Test main() integration with actual CLI."""
        # This tests the real integration but in a controlled way
        with patch("sys.argv", ["flext", "--version"]):
            with pytest.raises(SystemExit) as exc_info:
                main()

            # Should exit cleanly (version command exits with 0)
            assert exc_info.value.code == 0


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

    def test_cli_environment_variable_integration(self) -> None:
        """Test CLI respects environment variables."""
        # Test with environment variable
        with patch.dict(os.environ, {"FLX_DEBUG": "true"}):
            result = self.runner.invoke(cli, [])
            assert result.exit_code == 0
            # Should show debug output due to env var
            assert "Profile:" in result.output

        # Test with environment variable for profile
        with patch.dict(os.environ, {"FLX_PROFILE": "production"}):
            result = self.runner.invoke(cli, ["--debug"])
            assert result.exit_code == 0
            # Should show production profile
            assert "Profile: production" in result.output


class TestCliConfiguration:
    """Test CLI configuration handling."""

    def setup_method(self) -> None:
        """Set up test environment."""
        self.runner = CliRunner()

    @patch("flext_cli.cli.CLIContext")
    @patch("flext_cli.cli.get_config")
    def test_cli_config_loading(
        self,
        mock_get_config: MagicMock,
        mock_cli_context: MagicMock,
    ) -> None:
        """Test CLI loads configuration correctly."""
        # Setup mock config
        mock_config = MagicMock()
        mock_config.model_copy.return_value = mock_config
        mock_get_config.return_value = mock_config

        # Mock CLIContext
        mock_cli_context.return_value = MagicMock()

        result = self.runner.invoke(cli, ["--debug"])

        assert result.exit_code == 0
        # Config should be loaded
        mock_get_config.assert_called_once()
        # Config should be copied with updates
        mock_config.model_copy.assert_called_once()

    @patch("flext_cli.cli.CLIContext")
    def test_cli_context_creation(self, mock_cli_context: MagicMock) -> None:
        """Test CLI creates proper CLI context."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--debug"])

        assert result.exit_code == 0
        # CLIContext should be created
        mock_cli_context.assert_called_once()
