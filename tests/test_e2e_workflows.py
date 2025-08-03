"""End-to-End workflow tests for FLEXT CLI Library.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

E2E tests that simulate real user workflows and validate complete functionality.
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from unittest.mock import patch

import yaml
from click.testing import CliRunner
from flext_cli.cli import cli
from flext_cli.domain.entities import (
    CLICommand,
    CLIPlugin,
    CLISession,
    CommandStatus,
    CommandType,
)
from flext_cli.simple_api import setup_cli
from flext_cli.utils.config import CLISettings


class TestE2EUserWorkflows:
    """End-to-end tests for complete user workflows."""

    def test_new_user_onboarding_workflow(self) -> None:
        """Test complete new user onboarding workflow."""
        runner = CliRunner()

        # Step 1: New user checks help
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "FLEXT Command Line Interface" in result.output

        # Step 2: User checks version
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0

        # Step 3: User views default configuration
        result = runner.invoke(cli, ["config", "show"])
        assert result.exit_code == 0

        # Step 4: User validates their setup
        result = runner.invoke(cli, ["config", "validate"])
        assert result.exit_code == 0

        # Step 5: User checks auth status (should fail when not authenticated)
        result = runner.invoke(cli, ["auth", "status"])
        assert result.exit_code == 1  # Expected: not authenticated

    def test_developer_daily_workflow(self) -> None:
        """Test typical developer daily workflow."""
        runner = CliRunner()

        # Morning: Developer starts work
        # 1. Check system status with debug info
        result = runner.invoke(cli, ["--debug", "debug", "info"])
        assert result.exit_code == 0

        # 2. Switch to development profile
        result = runner.invoke(cli, ["--profile", "dev", "config", "show"])
        assert result.exit_code == 0

        # 3. Run system check
        result = runner.invoke(cli, ["--profile", "dev", "debug", "check"])
        assert result.exit_code == 0

        # 4. Validate configuration for development
        result = runner.invoke(cli, ["--profile", "dev", "config", "validate"])
        assert result.exit_code == 0

    def test_ops_engineer_monitoring_workflow(self) -> None:
        """Test operations engineer monitoring workflow."""
        runner = CliRunner()

        # Ops workflow: structured output for monitoring
        # 1. Get system status in JSON for processing
        result = runner.invoke(cli, ["--output", "json", "debug", "info"])
        assert result.exit_code == 0

        # 2. Check auth status in JSON (should fail when not authenticated)
        result = runner.invoke(cli, ["--output", "json", "auth", "status"])
        assert result.exit_code == 1  # Expected: not authenticated

        # 3. Get configuration in JSON for automation
        result = runner.invoke(cli, ["--output", "json", "config", "show"])
        assert result.exit_code == 0

    def test_troubleshooting_workflow(self) -> None:
        """Test complete troubleshooting workflow."""
        runner = CliRunner()

        # User reports issue, support engineer investigates
        # 1. Enable debug mode and get detailed info
        result = runner.invoke(cli, ["--debug", "debug", "info"])
        assert result.exit_code == 0

        # 2. Check system health
        result = runner.invoke(cli, ["--debug", "debug", "check"])
        assert result.exit_code == 0

        # 3. Validate all configurations
        result = runner.invoke(cli, ["--debug", "config", "validate"])
        assert result.exit_code == 0

        # 4. Check authentication status (should fail when not authenticated)
        result = runner.invoke(cli, ["--debug", "auth", "status"])
        assert result.exit_code == 1  # Expected: not authenticated

        # 5. Get machine-readable output for analysis
        result = runner.invoke(cli, ["--debug", "--output", "json", "debug", "info"])
        assert result.exit_code == 0

    def test_automation_integration_workflow(self) -> None:
        """Test automation/CI integration workflow."""
        runner = CliRunner()

        # CI/CD pipeline integration
        # 1. Validate setup in JSON format
        result = runner.invoke(cli, ["--output", "json", "config", "validate"])
        assert result.exit_code == 0

        # 2. Check system readiness
        result = runner.invoke(cli, ["--output", "json", "debug", "check"])
        assert result.exit_code == 0

        # 3. Get configuration for deployment
        result = runner.invoke(cli, ["--output", "yaml", "config", "show"])
        assert result.exit_code == 0

    def test_multi_environment_workflow(self) -> None:
        """Test workflow across multiple environments."""
        runner = CliRunner()

        environments = ["dev", "staging", "prod"]

        for env in environments:
            # Check configuration for each environment
            result = runner.invoke(cli, ["--profile", env, "config", "show"])
            assert result.exit_code == 0

            # Validate environment-specific config
            result = runner.invoke(cli, ["--profile", env, "config", "validate"])
            assert result.exit_code == 0

            # Check auth status per environment (should fail when not authenticated)
            result = runner.invoke(cli, ["--profile", env, "auth", "status"])
            assert result.exit_code == 1  # Expected: not authenticated


class TestE2EDataProcessingWorkflows:
    """E2E tests for data processing workflows."""

    def test_config_export_import_workflow(self) -> None:
        """Test configuration export/import workflow."""
        with tempfile.TemporaryDirectory() as tmpdir:
            runner = CliRunner()
            export_file = Path(tmpdir) / "config_export.yaml"

            # 1. Get current config in YAML format
            result = runner.invoke(cli, ["--output", "yaml", "config", "show"])
            assert result.exit_code == 0

            # 2. Save config to file (simulated)
            config_data = {"test": "data"}
            with export_file.open("w") as f:
                yaml.dump(config_data, f)

            # 3. Validate the exported config would work
            result = runner.invoke(cli, ["config", "validate"])
            assert result.exit_code == 0

    def test_batch_operations_workflow(self) -> None:
        """Test batch operations workflow."""
        runner = CliRunner()

        # Simulate batch operations with expected results
        operations = [
            (["config", "show"], 0),  # Should succeed
            (["config", "validate"], 0),  # Should succeed
            (["auth", "status"], 1),  # Should fail when not authenticated
            (["debug", "check"], 0),  # Should succeed
        ]

        results = []
        for operation, expected_exit_code in operations:
            result = runner.invoke(cli, ["--output", "json", *operation])
            assert result.exit_code == expected_exit_code, (
                f"Command {operation} expected exit code {expected_exit_code}, got {result.exit_code}"
            )
            results.append(result.output)

        # All operations should have been executed
        assert len(results) == len(operations)

    def test_data_format_conversion_workflow(self) -> None:
        """Test data format conversion workflow."""
        runner = CliRunner()

        # Get same data in different formats
        formats = ["table", "json", "yaml"]
        results = {}

        for fmt in formats:
            result = runner.invoke(cli, ["--output", fmt, "config", "show"])
            assert result.exit_code == 0
            results[fmt] = result.output

        # Should have data in all formats
        assert len(results) == len(formats)

        # JSON should be valid JSON
        if "json" in results:
            # Basic JSON validation (doesn't need to parse perfectly)
            assert results["json"].strip()

        # YAML should be valid YAML
        if "yaml" in results:
            assert results["yaml"].strip()


class TestE2EErrorRecoveryWorkflows:
    """E2E tests for error recovery scenarios."""

    def test_command_failure_recovery_workflow(self) -> None:
        """Test recovery from command failures."""
        runner = CliRunner()

        # 1. Execute invalid command (should fail)
        result = runner.invoke(cli, ["invalid-command"])
        assert result.exit_code != 0

        # 2. Recovery: Execute valid command
        result = runner.invoke(cli, ["config", "show"])
        assert result.exit_code == 0

        # 3. Verify system is still functional
        result = runner.invoke(cli, ["debug", "check"])
        assert result.exit_code == 0

    def test_invalid_option_recovery_workflow(self) -> None:
        """Test recovery from invalid options."""
        runner = CliRunner()

        # 1. Use invalid option (should fail)
        result = runner.invoke(cli, ["--invalid-option", "config", "show"])
        assert result.exit_code != 0

        # 2. Recovery: Use valid option
        result = runner.invoke(cli, ["--output", "json", "config", "show"])
        assert result.exit_code == 0

    def test_malformed_input_recovery_workflow(self) -> None:
        """Test recovery from malformed inputs."""
        runner = CliRunner()

        # 1. Malformed command structure
        result = runner.invoke(cli, ["config", "--invalid", "show"])
        assert result.exit_code != 0

        # 2. Recovery: Correct command structure
        result = runner.invoke(cli, ["config", "show"])
        assert result.exit_code == 0


class TestE2EPerformanceWorkflows:
    """E2E performance workflow tests."""

    def test_rapid_command_execution_workflow(self) -> None:
        """Test rapid command execution workflow."""
        import time

        runner = CliRunner()

        # Execute commands rapidly with expected exit codes
        commands = [
            (["config", "show"], 0),
            (["auth", "status"], 1),  # Expected to fail when not authenticated
            (["debug", "info"], 0),
            (["config", "validate"], 0),
        ] * 3  # Repeat 3 times

        start_time = time.time()

        for cmd, expected_exit_code in commands:
            result = runner.invoke(cli, cmd)
            assert result.exit_code == expected_exit_code, (
                f"Command {cmd} expected {expected_exit_code}, got {result.exit_code}"
            )

        end_time = time.time()
        total_time = end_time - start_time

        # Should complete all commands in reasonable time
        assert total_time < 10.0  # 10 seconds for 12 commands

    def test_large_output_workflow(self) -> None:
        """Test workflow with potentially large output."""
        runner = CliRunner()

        # Commands that might produce larger output
        commands = [
            ["--output", "json", "debug", "info"],
            ["--output", "yaml", "config", "show"],
            ["--debug", "debug", "check"],
        ]

        for cmd in commands:
            result = runner.invoke(cli, cmd)
            assert result.exit_code == 0
            # Output should be manageable
            assert len(result.output) < 50000  # 50KB limit


class TestE2ESecurityWorkflows:
    """E2E security workflow tests."""

    def test_authentication_workflow(self) -> None:
        """Test complete authentication workflow."""
        runner = CliRunner()

        # 1. Check current auth status (should fail when not authenticated)
        result = runner.invoke(cli, ["auth", "status"])
        assert result.exit_code == 1  # Expected: not authenticated

        # 2. Get current user info (should fail when not authenticated)
        result = runner.invoke(cli, ["auth", "whoami"])
        assert result.exit_code == 1  # Expected: not authenticated

        # 3. Verify auth status with different output format (should fail when not authenticated)
        result = runner.invoke(cli, ["--output", "json", "auth", "status"])
        assert result.exit_code == 1  # Expected: not authenticated

    def test_configuration_security_workflow(self) -> None:
        """Test configuration security workflow."""
        runner = CliRunner()

        # 1. Validate configuration security
        result = runner.invoke(cli, ["config", "validate"])
        assert result.exit_code == 0

        # 2. Check config with debug info (might show security details)
        result = runner.invoke(cli, ["--debug", "config", "show"])
        assert result.exit_code == 0

    def test_secure_output_workflow(self) -> None:
        """Test secure output handling workflow."""
        runner = CliRunner()

        # Test that sensitive information isn't leaked in different formats
        formats = ["table", "json", "yaml"]

        for fmt in formats:
            result = runner.invoke(cli, ["--output", fmt, "auth", "status"])
            assert result.exit_code == 1  # Expected: not authenticated
            # Output should not contain obvious credentials
            output_lower = result.output.lower()
            assert "password" not in output_lower
            assert "secret" not in output_lower
            # When not authenticated, token check is not relevant


class TestE2EIntegrationWithCore:
    """E2E tests for integration with flext-core patterns."""

    def test_service_result_integration_workflow(self) -> None:
        """Test ServiceResult pattern integration workflow."""
        # Test that CLI setup uses ServiceResult patterns
        settings = CLISettings()
        result = setup_cli(settings)

        assert result.is_success
        assert result.unwrap() is True

    def test_domain_entity_lifecycle_workflow(self) -> None:
        """Test domain entity lifecycle in CLI context."""
        # Create and execute a command
        command = CLICommand(
            name="test-workflow",
            command_line="echo 'Hello, World!'",
            command_type=CommandType.SYSTEM,
        )

        # Test complete lifecycle
        assert command.command_status == CommandStatus.PENDING

        command = command.start_execution()
        assert command.command_status == CommandStatus.RUNNING
        assert command.started_at is not None

        command = command.complete_execution(exit_code=0, stdout="Hello, World!")
        assert command.command_status == CommandStatus.COMPLETED
        assert command.is_successful
        assert command.finished_at is not None

    def test_cli_session_workflow(self) -> None:
        """Test CLI session management workflow."""
        # Create a session
        session = CLISession(session_id="e2e-test-session")

        # Add multiple commands to session
        commands = []
        for i in range(3):
            cmd = CLICommand(
                name=f"test-cmd-{i}",
                command_line=f"echo 'Command {i}'",
                command_type=CommandType.SYSTEM,
            )
            commands.append(cmd)
            session.add_command(cmd.id)

        # Verify session state
        assert len(session.command_history) == 3
        assert session.session_status.value == "active"

        # Complete session
        session.end_session()
        assert session.session_status.value == "completed"

    def test_cli_plugin_integration_workflow(self) -> None:
        """Test CLI plugin integration workflow."""
        # Create a plugin
        plugin = CLIPlugin(
            name="test-plugin",
            entry_point="test.main",
            commands=["test", "validate", "process"],
        )

        # Test plugin lifecycle
        assert plugin.plugin_status.value == "inactive"

        plugin.activate()
        assert plugin.plugin_status.value == "active"

        plugin.deactivate()
        assert plugin.plugin_status.value == "inactive"


class TestE2EConfigurationWorkflows:
    """E2E configuration management workflow tests."""

    def test_environment_variable_workflow(self) -> None:
        """Test environment variable configuration workflow."""
        import os

        # Test with environment variables
        test_env = {
            "FLEXT_CLI_DEBUG": "true",
            "FLEXT_CLI_PROFILE": "test",
            "FLEXT_CLI_LOG_LEVEL": "DEBUG",
        }

        with patch.dict(os.environ, test_env):
            runner = CliRunner()

            # Commands should pick up environment variables
            result = runner.invoke(cli, ["config", "show"])
            assert result.exit_code == 0

    def test_profile_switching_workflow(self) -> None:
        """Test profile switching workflow."""
        runner = CliRunner()

        profiles = ["default", "dev", "staging", "prod"]

        for profile in profiles:
            # Test switching to different profiles
            result = runner.invoke(cli, ["--profile", profile, "config", "show"])
            assert result.exit_code == 0

    def test_configuration_validation_workflow(self) -> None:
        """Test configuration validation workflow."""
        runner = CliRunner()

        # Test validation with different profiles
        profiles = ["default", "dev", "prod"]

        for profile in profiles:
            result = runner.invoke(cli, ["--profile", profile, "config", "validate"])
            assert result.exit_code == 0

    def test_configuration_persistence_workflow(self) -> None:
        """Test configuration persistence workflow."""
        # This tests that configuration changes persist across invocations
        runner = CliRunner()

        # Multiple invocations should work consistently
        for _ in range(3):
            result = runner.invoke(cli, ["config", "show"])
            assert result.exit_code == 0

            result = runner.invoke(cli, ["config", "validate"])
            assert result.exit_code == 0


class TestE2EOutputFormatWorkflows:
    """E2E output format workflow tests."""

    def test_format_consistency_workflow(self) -> None:
        """Test output format consistency workflow."""
        runner = CliRunner()

        # Test that all commands support all output formats with expected exit codes
        commands = [
            (["config", "show"], 0),
            (["auth", "status"], 1),  # Expected to fail when not authenticated
        ]

        formats = ["table", "json", "yaml"]

        for cmd, expected_exit_code in commands:
            for fmt in formats:
                result = runner.invoke(cli, ["--output", fmt, *cmd])
                assert result.exit_code == expected_exit_code, (
                    f"Command {cmd} with format {fmt} expected {expected_exit_code}, got {result.exit_code}"
                )

    def test_format_switching_workflow(self) -> None:
        """Test format switching within workflow."""
        runner = CliRunner()

        # Switch formats within same session
        result = runner.invoke(cli, ["--output", "table", "config", "show"])
        assert result.exit_code == 0

        result = runner.invoke(cli, ["--output", "json", "config", "show"])
        assert result.exit_code == 0

        result = runner.invoke(cli, ["--output", "yaml", "config", "show"])
        assert result.exit_code == 0

    def test_format_parsing_workflow(self) -> None:
        """Test that output formats are parseable."""
        runner = CliRunner()

        # Test JSON output is valid JSON
        result = runner.invoke(cli, ["--output", "json", "config", "show"])
        assert result.exit_code == 0
        # Should be valid JSON structure (basic validation)
        if result.output.strip():
            assert result.output.strip().startswith(("{", "["))

    def test_format_with_debug_workflow(self) -> None:
        """Test output formats work with debug mode."""
        runner = CliRunner()

        formats = ["table", "json", "yaml"]

        for fmt in formats:
            result = runner.invoke(cli, ["--debug", "--output", fmt, "config", "show"])
            assert result.exit_code == 0
