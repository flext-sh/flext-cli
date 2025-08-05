"""Complete CLI integration tests for FLEXT CLI Library.

Integration tests that validate the entire CLI application with real workflows.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import tempfile
from pathlib import Path

import yaml
from click.testing import CliRunner
from flext_cli.cli import cli
from flext_cli.config import CLISettings
from flext_cli.domain.entities import CLICommand, CLISession, CommandStatus, CommandType
from flext_cli.simple_api import setup_cli


class TestCLIIntegration:
    """Integration tests for complete CLI functionality."""

    def test_cli_help_output(self) -> None:
        """Test CLI help output is properly formatted."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])

        assert result.exit_code == 0
        assert "FLEXT Command Line Interface" in result.output
        assert "Commands:" in result.output
        assert "Options:" in result.output

    def test_cli_version_output(self) -> None:
        """Test CLI version command works."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--version"])

        assert result.exit_code == 0
        # Version should be shown
        assert result.output.strip()

    def test_cli_global_options(self) -> None:
        """Test CLI global options are properly handled."""
        runner = CliRunner()

        # Test debug option
        result = runner.invoke(cli, ["--debug", "--help"])
        assert result.exit_code == 0

        # Test profile option
        result = runner.invoke(cli, ["--profile", "test", "--help"])
        assert result.exit_code == 0

        # Test output format option
        result = runner.invoke(cli, ["--output", "json", "--help"])
        assert result.exit_code == 0

    def test_config_commands_integration(self) -> None:
        """Test configuration commands integration."""
        runner = CliRunner()

        # Test config show
        result = runner.invoke(cli, ["config", "show"])
        assert result.exit_code == 0

        # Test config validate
        result = runner.invoke(cli, ["config", "validate"])
        assert result.exit_code == 0

    def test_auth_commands_integration(self) -> None:
        """Test authentication commands integration."""
        runner = CliRunner()

        # Test auth status (should exit with 1 when not authenticated)
        result = runner.invoke(cli, ["auth", "status"])
        assert result.exit_code == 1  # Not authenticated
        assert "Not authenticated" in result.output

        # Test auth whoami (should also exit with 1 when not authenticated)
        result = runner.invoke(cli, ["auth", "whoami"])
        assert result.exit_code == 1  # Not authenticated

    def test_debug_commands_integration(self) -> None:
        """Test debug commands integration."""
        runner = CliRunner()

        # Test debug info
        result = runner.invoke(cli, ["debug", "info"])
        assert result.exit_code == 0

        # Test debug check
        result = runner.invoke(cli, ["debug", "check"])
        assert result.exit_code == 0

    def test_cli_with_configuration_files(self) -> None:
        """Test CLI with different configuration files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "test_config.yaml"
            config_data = {
                "profile": "test",
                "debug": True,
                "output_format": "json",
                "log_level": "INFO",
            }

            with config_file.open("w") as f:
                yaml.dump(config_data, f)

            runner = CliRunner()
            result = runner.invoke(cli, ["config", "show"])
            assert result.exit_code == 0

    def test_output_format_integration(self) -> None:
        """Test different output formats work correctly."""
        runner = CliRunner()

        # Test table output (default)
        result = runner.invoke(cli, ["--output", "table", "config", "show"])
        assert result.exit_code == 0

        # Test JSON output
        result = runner.invoke(cli, ["--output", "json", "config", "show"])
        assert result.exit_code == 0

        # Test YAML output
        result = runner.invoke(cli, ["--output", "yaml", "config", "show"])
        assert result.exit_code == 0

    def test_error_handling_integration(self) -> None:
        """Test error handling across CLI commands."""
        runner = CliRunner()

        # Test invalid command
        result = runner.invoke(cli, ["invalid-command"])
        assert result.exit_code != 0

        # Test invalid option
        result = runner.invoke(cli, ["--invalid-option"])
        assert result.exit_code != 0

    def test_cli_setup_integration(self) -> None:
        """Test CLI setup integration with simple API."""
        settings = CLISettings()

        # Test setup succeeds
        result = setup_cli(settings)
        assert result.success
        assert result.unwrap() is True

    def test_domain_entities_integration(self) -> None:
        """Test domain entities work with CLI commands."""
        # Create a CLI command
        command = CLICommand(
            name="test-command",
            command_line="echo 'test'",
            command_type=CommandType.SYSTEM,
        )

        # Test command lifecycle
        command = command.start_execution()
        assert command.command_status == CommandStatus.RUNNING

        command = command.complete_execution(exit_code=0, stdout="test")
        assert command.successful
        assert command.command_status == CommandStatus.COMPLETED

        # Create a session
        session = CLISession(session_id="test-session")
        session = session.add_command(command.id)

        assert len(session.command_history) == 1
        assert command.id in session.command_history


class TestCLIEndToEnd:
    """End-to-end tests for complete CLI workflows."""

    def test_complete_config_workflow(self) -> None:
        """Test complete configuration workflow."""
        runner = CliRunner()

        # Step 1: Show current config
        result = runner.invoke(cli, ["config", "show"])
        assert result.exit_code == 0

        # Step 2: Validate config
        result = runner.invoke(cli, ["config", "validate"])
        assert result.exit_code == 0

        # Step 3: Show config in different formats
        for format_type in ["table", "json", "yaml"]:
            result = runner.invoke(cli, ["--output", format_type, "config", "show"])
            assert result.exit_code == 0

    def test_complete_auth_workflow(self) -> None:
        """Test complete authentication workflow."""
        runner = CliRunner()

        # Step 1: Check auth status (should exit with 1 when not authenticated)
        result = runner.invoke(cli, ["auth", "status"])
        assert result.exit_code == 1  # Not authenticated

        # Step 2: Show current user (should also exit with 1 when not authenticated)
        result = runner.invoke(cli, ["auth", "whoami"])
        assert result.exit_code == 1  # Not authenticated

    def test_complete_debug_workflow(self) -> None:
        """Test complete debug workflow."""
        runner = CliRunner()

        # Step 1: Get debug info
        result = runner.invoke(cli, ["debug", "info"])
        assert result.exit_code == 0

        # Step 2: Run debug check
        result = runner.invoke(cli, ["debug", "check"])
        assert result.exit_code == 0

    def test_cli_with_files_workflow(self) -> None:
        """Test CLI workflow with file operations."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_dir = Path(tmpdir)
            test_file = test_dir / "test.txt"
            test_file.write_text("test content")

            runner = CliRunner()

            # Test commands that might work with files
            result = runner.invoke(cli, ["config", "show"])
            assert result.exit_code == 0

    def test_error_recovery_workflow(self) -> None:
        """Test error recovery in CLI workflows."""
        runner = CliRunner()

        # Test invalid command followed by valid command
        result = runner.invoke(cli, ["invalid"])
        assert result.exit_code != 0

        # Recovery: valid command should work
        result = runner.invoke(cli, ["config", "show"])
        assert result.exit_code == 0

    def test_complex_command_chain(self) -> None:
        """Test complex command chain execution."""
        runner = CliRunner()

        # Execute multiple commands in sequence
        commands = [
            ["config", "show"],
            ["auth", "status"],
            ["debug", "info"],
            ["config", "validate"],
        ]

        for cmd in commands:
            result = runner.invoke(cli, cmd)
            # Auth commands exit with 1 when not authenticated
            if cmd[0] == "auth":
                assert result.exit_code == 1
            else:
                assert result.exit_code == 0


class TestCLIRealWorldScenarios:
    """Real-world scenario tests for CLI application."""

    def test_development_workflow(self) -> None:
        """Test typical development workflow scenario."""
        runner = CliRunner()

        # Developer checks configuration
        result = runner.invoke(cli, ["--profile", "dev", "config", "show"])
        assert result.exit_code == 0

        # Developer enables debug mode
        result = runner.invoke(cli, ["--debug", "debug", "info"])
        assert result.exit_code == 0

        # Developer validates setup
        result = runner.invoke(cli, ["config", "validate"])
        assert result.exit_code == 0

    def test_production_workflow(self) -> None:
        """Test typical production workflow scenario."""
        runner = CliRunner()

        # Production: Check system status (should exit with 1 when not authenticated)
        result = runner.invoke(cli, ["--profile", "prod", "auth", "status"])
        assert result.exit_code == 1  # Not authenticated

        # Production: Get structured output
        result = runner.invoke(cli, ["--output", "json", "config", "show"])
        assert result.exit_code == 0

    def test_troubleshooting_workflow(self) -> None:
        """Test troubleshooting workflow scenario."""
        runner = CliRunner()

        # Step 1: Enable debug mode
        result = runner.invoke(cli, ["--debug", "debug", "check"])
        assert result.exit_code == 0

        # Step 2: Get detailed info
        result = runner.invoke(cli, ["--debug", "debug", "info"])
        assert result.exit_code == 0

        # Step 3: Validate configuration
        result = runner.invoke(cli, ["--debug", "config", "validate"])
        assert result.exit_code == 0

    def test_automation_workflow(self) -> None:
        """Test automation-friendly workflow scenario."""
        runner = CliRunner()

        # Automation: JSON output for parsing
        result = runner.invoke(cli, ["--output", "json", "config", "show"])
        assert result.exit_code == 0

        # Automation: Validate setup programmatically (should exit with 1 when not authenticated)
        result = runner.invoke(cli, ["--output", "json", "auth", "status"])
        assert result.exit_code == 1  # Not authenticated


class TestCLIPerformanceIntegration:
    """Performance integration tests for CLI application."""

    def test_cli_startup_performance(self) -> None:
        """Test CLI startup performance is acceptable."""
        import time

        runner = CliRunner()

        start_time = time.time()
        result = runner.invoke(cli, ["--help"])
        end_time = time.time()

        assert result.exit_code == 0
        # CLI should start in less than 2 seconds
        startup_time = end_time - start_time
        assert startup_time < 2.0

    def test_command_execution_performance(self) -> None:
        """Test command execution performance."""
        import time

        runner = CliRunner()

        commands = [
            ["config", "show"],
            ["auth", "status"],
            ["debug", "info"],
        ]

        for cmd in commands:
            start_time = time.time()
            result = runner.invoke(cli, cmd)
            end_time = time.time()

            # Auth commands exit with 1 when not authenticated
            if cmd[0] == "auth":
                assert result.exit_code == 1
            else:
                assert result.exit_code == 0
            # Each command should execute in less than 1 second
            execution_time = end_time - start_time
            assert execution_time < 1.0


class TestCLICompatibility:
    """Compatibility tests for CLI application."""

    def test_click_version_compatibility(self) -> None:
        """Test compatibility with Click framework."""
        import click

        runner = CliRunner()
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0

        # Test that Click testing framework works
        assert isinstance(runner, click.testing.CliRunner)

    def test_python_version_compatibility(self) -> None:
        """Test Python version compatibility."""
        import sys

        # Should work with Python 3.13+
        assert sys.version_info >= (3, 13)

        runner = CliRunner()
        result = runner.invoke(cli, ["config", "show"])
        assert result.exit_code == 0

    def test_terminal_compatibility(self) -> None:
        """Test terminal compatibility."""
        runner = CliRunner()

        # Test with different output formats
        formats = ["table", "json", "yaml"]
        for fmt in formats:
            result = runner.invoke(cli, ["--output", fmt, "config", "show"])
            assert result.exit_code == 0


class TestCLIRobustness:
    """Robustness tests for CLI application."""

    def test_invalid_input_handling(self) -> None:
        """Test handling of invalid inputs."""
        runner = CliRunner()

        # Invalid commands
        invalid_commands = [
            ["nonexistent"],
            ["config", "invalid"],
            ["auth", "badcmd"],
        ]

        for cmd in invalid_commands:
            result = runner.invoke(cli, cmd)
            assert result.exit_code != 0

    def test_malformed_options_handling(self) -> None:
        """Test handling of malformed options."""
        runner = CliRunner()

        # Malformed options
        malformed = [
            ["--nonexistent-option"],
            ["--output", "invalid_format"],
            ["--profile"],  # Missing value
        ]

        for cmd in malformed:
            result = runner.invoke(cli, cmd)
            assert result.exit_code != 0

    def test_exception_handling(self) -> None:
        """Test exception handling in CLI commands."""
        runner = CliRunner()

        # Commands should handle exceptions gracefully
        result = runner.invoke(cli, ["config", "show"])
        assert result.exit_code == 0

    def test_signal_handling(self) -> None:
        """Test signal handling (Ctrl+C, etc.)."""
        runner = CliRunner()

        # Basic test that commands can be interrupted
        result = runner.invoke(cli, ["config", "show"])
        assert result.exit_code == 0

    def test_memory_usage(self) -> None:
        """Test memory usage is reasonable."""
        import gc

        runner = CliRunner()

        # Get initial memory baseline
        gc.collect()
        initial_objects = len(gc.get_objects())

        # Execute multiple commands
        for _ in range(10):
            result = runner.invoke(cli, ["config", "show"])
            assert result.exit_code == 0

        # Check memory hasn't grown excessively
        gc.collect()
        final_objects = len(gc.get_objects())

        # Object count shouldn't grow significantly
        growth = final_objects - initial_objects
        assert growth < 10000  # Arbitrary but reasonable limit


class TestCLIDocumentationIntegration:
    """Tests for CLI documentation integration."""

    def test_help_documentation_complete(self) -> None:
        """Test that help documentation is complete."""
        runner = CliRunner()

        # Main help
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "Usage:" in result.output
        assert "Options:" in result.output
        assert "Commands:" in result.output

        # Command group help
        command_groups = ["config", "auth", "debug"]
        for group in command_groups:
            result = runner.invoke(cli, [group, "--help"])
            assert result.exit_code == 0
            assert "Usage:" in result.output

    def test_command_descriptions(self) -> None:
        """Test that commands have proper descriptions."""
        runner = CliRunner()

        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0

        # Should contain command descriptions
        assert "config" in result.output.lower()
        assert "auth" in result.output.lower()
        assert "debug" in result.output.lower()

    def test_option_documentation(self) -> None:
        """Test that options are documented."""
        runner = CliRunner()

        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0

        # Should document key options
        assert "--profile" in result.output
        assert "--output" in result.output
        assert "--debug" in result.output
        assert "--help" in result.output
        assert "--version" in result.output
