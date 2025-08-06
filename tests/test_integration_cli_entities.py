"""Integration tests between CLI commands and core entities.

Tests that validate CLI commands work correctly with domain entities.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import tempfile
import uuid
from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner
from flext_cli.cli import cli
from flext_cli.domain.cli_context import CLIContext, CLIExecutionContext
from flext_cli.domain.cli_services import CLICommandService, CLISessionService
from flext_cli.domain.entities import (
    CLICommand,
    CLIConfig,
    CLIEntityFactory,
    CLIPlugin,
    CLISession,
    CommandStatus,
    CommandType,
    PluginStatus,
    SessionStatus,
)


class TestCLICommandEntityIntegration:
    """Test CLI commands integrate with CLICommand entities."""

    def test_command_execution_with_entities(self) -> None:
        """Test CLI command execution creates and manages entities."""
        runner = CliRunner()

        # Execute a command
        result = runner.invoke(cli, ["config", "show"])
        assert result.exit_code == 0

        # In a real implementation, this would create CLICommand entities
        # For now, we test that entities can be created manually
        command = CLICommand(
            id=str(uuid.uuid4()),
            name="config-show",
            command_line="flext config show",
            command_type=CommandType.CLI,
        )

        # Test command lifecycle - properly unwrap FlextResult
        start_result = command.start_execution()
        assert start_result.success, f"Start execution failed: {start_result.error}"
        command = start_result.data

        assert command.command_status == CommandStatus.RUNNING

        complete_result = command.complete_execution(exit_code=0, stdout=result.output)
        assert complete_result.success, (
            f"Complete execution failed: {complete_result.error}"
        )
        command = complete_result.data

        assert command.command_status == CommandStatus.COMPLETED
        assert command.successful

    def test_command_with_different_types(self) -> None:
        """Test CLI commands with different command types."""
        command_types_tests = [
            (CommandType.CLI, "flext config show"),
            (CommandType.SYSTEM, "echo hello"),
            (CommandType.SCRIPT, "python script.py"),
            (CommandType.SQL, "SELECT * FROM table"),
        ]

        for cmd_type, cmd_line in command_types_tests:
            command = CLICommand(
                id=str(uuid.uuid4()),
                name=f"test-{cmd_type.value}",
                command_line=cmd_line,
                command_type=cmd_type,
            )

            # All command types should be creatable
            assert command.command_type == cmd_type
            assert command.command_line == cmd_line
            assert command.command_status == CommandStatus.PENDING

    def test_command_failure_scenarios(self) -> None:
        """Test CLI command failure scenarios."""
        # Test invalid CLI command
        runner = CliRunner()
        result = runner.invoke(cli, ["invalid-command"])
        assert result.exit_code != 0

        # Create entity for failed command
        command = CLICommand(
            id=str(uuid.uuid4()),
            name="invalid-command",
            command_line="flext invalid-command",
            command_type=CommandType.CLI,
        )

        start_result = command.start_execution()
        assert start_result.success, f"Start execution failed: {start_result.error}"
        command = start_result.data

        complete_result = command.complete_execution(
            exit_code=result.exit_code, stderr="Command not found"
        )
        assert complete_result.success, (
            f"Complete execution failed: {complete_result.error}"
        )
        command = complete_result.data

        assert command.command_status == CommandStatus.FAILED
        assert not command.successful
        assert command.exit_code == result.exit_code

    def test_command_with_arguments(self) -> None:
        """Test CLI commands with various arguments."""
        runner = CliRunner()

        # Test command with profile argument
        result = runner.invoke(cli, ["--profile", "dev", "config", "show"])
        assert result.exit_code == 0

        # Create entity
        command = CLICommand(
            id=str(uuid.uuid4()),
            name="config-show-dev",
            command_line="flext --profile dev config show",
            command_type=CommandType.CLI,
        )

        # Test command metadata
        assert command.name == "config-show-dev"
        assert "--profile dev" in command.command_line

    def test_command_with_output_formats(self) -> None:
        """Test CLI commands with different output formats."""
        runner = CliRunner()
        formats = ["table", "json", "yaml"]

        for fmt in formats:
            result = runner.invoke(cli, ["--output", fmt, "config", "show"])
            assert result.exit_code == 0

            # Create entity for each format
            command = CLICommand(
                id=str(uuid.uuid4()),
                name=f"config-show-{fmt}",
                command_line=f"flext --output {fmt} config show",
                command_type=CommandType.CLI,
            )

            start_result = command.start_execution()
            assert start_result.success
            command = start_result.unwrap()

            complete_result = command.complete_execution(
                exit_code=0, stdout=result.output
            )
            assert complete_result.success
            command = complete_result.unwrap()

            assert command.successful
            assert fmt in command.command_line


class TestCLISessionEntityIntegration:
    """Test CLI session integration with CLISession entities."""

    def test_session_tracks_multiple_commands(self) -> None:
        """Test session tracks multiple CLI commands."""
        runner = CliRunner()
        session = CLISession(id=str(uuid.uuid4()), session_id="test-session-multi")

        # Execute multiple commands
        commands = [
            (["config", "show"], 0),  # Should work
            (["config", "validate"], 0),  # Should work
            (["auth", "status"], 1),  # Fails when not authenticated (expected)
            (["debug", "info"], 0),  # Should work
        ]

        for cmd_args, expected_exit_code in commands:
            result = runner.invoke(cli, cmd_args)
            assert result.exit_code == expected_exit_code

            # Create command entity with factory
            command_result = CLIEntityFactory.create_command(
                name="-".join(cmd_args),
                command_line=f"flext {' '.join(cmd_args)}",
                command_type=CommandType.CLI,
            )
            assert command_result.success
            command = command_result.unwrap()

            # Add to session
            session_result = session.add_command(command.id)
            assert session_result.success
            session = session_result.unwrap()

        # Verify session state
        assert len(session.command_history) == len(commands)
        assert session.session_status == SessionStatus.ACTIVE

    def test_session_with_command_failures(self) -> None:
        """Test session handles command failures."""
        runner = CliRunner()
        session = CLISession(id=str(uuid.uuid4()), session_id="test-session-failures")

        # Mix of successful and failed commands
        test_commands = [
            (["config", "show"], True),
            (["invalid-command"], False),
            (["config", "validate"], True),
            (["another-invalid"], False),
        ]

        for cmd_args, should_succeed in test_commands:
            result = runner.invoke(cli, cmd_args)

            if should_succeed:
                assert result.exit_code == 0
            else:
                assert result.exit_code != 0

            # Create command entity with factory
            command_result = CLIEntityFactory.create_command(
                name="-".join(cmd_args),
                command_line=f"flext {' '.join(cmd_args)}",
                command_type=CommandType.CLI,
            )
            assert command_result.success
            command = command_result.unwrap()

            start_result = command.start_execution()
            assert start_result.success
            command = start_result.unwrap()

            complete_result = command.complete_execution(
                exit_code=result.exit_code,
                stdout=result.output if should_succeed else None,
                stderr=result.output if not should_succeed else None,
            )
            assert complete_result.success
            command = complete_result.unwrap()

            session_result = session.add_command(command.id)
            assert session_result.success
            session = session_result.unwrap()

        # Session should track all commands
        assert len(session.command_history) == len(test_commands)

    def test_session_lifecycle_with_cli(self) -> None:
        """Test complete session lifecycle with CLI commands."""
        session = CLISession(id=str(uuid.uuid4()), session_id="test-lifecycle")
        runner = CliRunner()

        # Session should start active
        assert session.session_status == SessionStatus.ACTIVE

        # Execute some commands
        result = runner.invoke(cli, ["config", "show"])
        assert result.exit_code == 0

        command = CLICommand(
            id=str(uuid.uuid4()),
            name="config-show",
            command_line="flext config show",
            command_type=CommandType.CLI,
        )
        session_result = session.add_command(command.id)
        assert session_result.success
        session = session_result.unwrap()

        # End session
        end_result = session.end_session()
        assert end_result.success
        session = end_result.unwrap()
        assert session.session_status == SessionStatus.COMPLETED
        assert session.ended_at is not None

    def test_session_context_integration(self) -> None:
        """Test session integrates with CLI context."""
        from flext_cli.config import CLISettings, get_config
        from rich.console import Console

        session = CLISession(id=str(uuid.uuid4()), session_id="test-context")

        # Create CLI context with proper components (SOLID: Dependency Injection)
        config = get_config()
        config.profile = "test"
        config.output_format = "json"
        config.debug = True

        context = CLIContext(config=config, settings=CLISettings(), console=Console())

        # Session should be able to track context
        assert session.session_id == "test-context"
        assert context.config.profile == "test"
        assert context.config.debug is True


class TestCLIPluginEntityIntegration:
    """Test CLI plugin integration with CLIPlugin entities."""

    def test_plugin_lifecycle_with_cli(self) -> None:
        """Test plugin lifecycle with CLI integration."""
        plugin = CLIPlugin(
            id=str(uuid.uuid4()),
            name="test-plugin",
            entry_point="test.main",
            commands=["test", "validate", "process"],
        )

        # Initial state
        assert plugin.plugin_status == PluginStatus.INACTIVE
        assert len(plugin.commands) == 3

        # Activate plugin
        activated_result = plugin.activate()
        assert activated_result.success
        plugin = activated_result.unwrap()
        assert plugin.plugin_status == PluginStatus.ACTIVE

        # Plugin should be able to provide commands
        assert "test" in plugin.commands
        assert "validate" in plugin.commands
        assert "process" in plugin.commands

        # Deactivate plugin
        deactivated_result = plugin.deactivate()
        assert deactivated_result.success
        plugin = deactivated_result.unwrap()
        assert plugin.plugin_status == PluginStatus.INACTIVE

    def test_plugin_command_integration(self) -> None:
        """Test plugin commands integrate with CLI."""
        plugin = CLIPlugin(
            id=str(uuid.uuid4()),
            name="config-plugin",
            entry_point="flext_cli.commands.config",
            commands=["show", "validate"],
        )

        runner = CliRunner()

        # Test that plugin commands work
        for command_name in plugin.commands:
            if command_name in {"show", "validate"}:
                result = runner.invoke(cli, ["config", command_name])
                assert result.exit_code == 0

    def test_plugin_with_dependencies(self) -> None:
        """Test plugin with dependencies."""
        plugin = CLIPlugin(
            id=str(uuid.uuid4()),
            name="advanced-plugin",
            entry_point="advanced.main",
            commands=["advanced-cmd"],
            dependencies=["flext-core", "flext-cli"],
        )

        # Plugin should track dependencies
        assert len(plugin.dependencies) == 2
        assert "flext-core" in plugin.dependencies
        assert "flext-cli" in plugin.dependencies


class TestCLIConfigEntityIntegration:
    """Test CLI configuration integration with CLIConfig entities."""

    def test_config_entity_with_cli_options(self) -> None:
        """Test CLIConfig entity reflects CLI options."""
        runner = CliRunner()

        # Test different configuration scenarios
        config_scenarios: list[dict[str, object]] = [
            {
                "args": ["--profile", "dev", "--debug", "config", "show"],
                "expected": {"profile": "dev", "debug": True},
            },
            {
                "args": ["--output", "json", "config", "show"],
                "expected": {"output_format": "json"},
            },
            {
                "args": ["--profile", "prod", "--output", "yaml", "config", "show"],
                "expected": {"profile": "prod", "output_format": "yaml"},
            },
        ]

        for scenario in config_scenarios:
            result = runner.invoke(cli, scenario["args"])
            assert result.exit_code == 0

            # Type the expected dict for MyPy
            expected: dict[str, object] = scenario["expected"]

            # Create config entity that reflects the CLI options
            config = CLIConfig(
                profile=str(expected.get("profile", "default")),
                debug=bool(expected.get("debug")),
                output_format=str(expected.get("output_format", "table")),
            )

            # Verify config matches expectations
            if "profile" in expected:
                assert config.profile == expected["profile"]
            if "debug" in expected:
                assert config.debug == expected["debug"]
            if "output_format" in expected:
                assert config.output_format == expected["output_format"]

    def test_config_validation_with_cli(self) -> None:
        """Test config validation integrates with CLI."""
        runner = CliRunner()

        # Test config validation command
        result = runner.invoke(cli, ["config", "validate"])
        assert result.exit_code == 0

        # Test different output formats for validation
        formats = ["table", "json", "yaml"]

        for fmt in formats:
            result = runner.invoke(cli, ["--output", fmt, "config", "validate"])
            assert result.exit_code == 0

            # Create config for this format
            config = CLIConfig(output_format=fmt)
            assert config.output_format == fmt

    def test_config_with_environment_variables(self) -> None:
        """Test config entity with environment variables."""
        import os

        test_env = {
            "FLEXT_CLI_DEBUG": "true",
            "FLEXT_CLI_PROFILE": "testing",
            "FLEXT_CLI_OUTPUT_FORMAT": "json",
        }

        with patch.dict(os.environ, test_env):
            # Environment variables should influence config
            config = CLIConfig(
                profile=os.getenv("FLEXT_CLI_PROFILE", "default"),
                debug=os.getenv("FLEXT_CLI_DEBUG", "false").lower() == "true",
                output_format=os.getenv("FLEXT_CLI_OUTPUT_FORMAT", "table"),
            )

            assert config.profile == "testing"
            assert config.debug is True
            assert config.output_format == "json"


class TestCLIServiceIntegration:
    """Test CLI services integration with entities."""

    def test_command_service_integration(self) -> None:
        """Test CLICommandService integrates with CLI."""
        service = CLICommandService()
        runner = CliRunner()

        # Execute a command via CLI
        result = runner.invoke(cli, ["config", "show"])
        assert result.exit_code == 0

        # Service should be able to create command entities
        command = CLICommand(
            id=str(uuid.uuid4()),
            name="config-show",
            command_line="flext config show",
            command_type=CommandType.CLI,
        )

        # Service operations should work
        assert service is not None
        assert command.name == "config-show"

    def test_session_service_integration(self) -> None:
        """Test CLISessionService integrates with CLI."""
        service = CLISessionService()
        runner = CliRunner()

        # Create a session for CLI operations
        session = CLISession(id=str(uuid.uuid4()), session_id="service-test")

        # Execute commands and track in session
        commands = [
            ["config", "show"],
            ["config", "validate"],
        ]

        for cmd_args in commands:
            result = runner.invoke(cli, cmd_args)
            assert result.exit_code == 0

            command = CLICommand(
                id=str(uuid.uuid4()),
                name="-".join(cmd_args),
                command_line=f"flext {' '.join(cmd_args)}",
                command_type=CommandType.CLI,
            )
            session_result = session.add_command(command.id)
            assert session_result.success
            session = session_result.unwrap()

        # Service should handle session operations
        assert service is not None
        assert len(session.command_history) == len(commands)


class TestCLIContextIntegration:
    """Test CLI context integration with entities."""

    def test_cli_context_with_commands(self) -> None:
        """Test CLIContext integrates with command execution."""
        from flext_cli.config import CLISettings, get_config
        from rich.console import Console

        # Create proper CLI context (SOLID: Dependency Injection)
        config = get_config()
        config.profile = "integration-test"
        config.output_format = "json"
        config.debug = True

        context = CLIContext(config=config, settings=CLISettings(), console=Console())

        runner = CliRunner()

        # Commands should work with context settings
        result = runner.invoke(
            cli,
            [
                "--profile",
                context.config.profile,
                "--output",
                context.config.output_format,
                "--debug" if context.config.debug else "--no-debug",
                "config",
                "show",
            ],
        )
        assert result.exit_code == 0

    def test_execution_context_with_entities(self) -> None:
        """Test CLIExecutionContext with command entities."""
        execution_context = CLIExecutionContext(
            command_name="config-show", user_id="test-user", session_id="test-session"
        )

        # Create related entities
        command = CLICommand(
            id=str(uuid.uuid4()),
            name=execution_context.command_name,
            command_line="flext config show",
            command_type=CommandType.CLI,
        )

        session = CLISession(
            id=str(uuid.uuid4()),
            session_id=execution_context.session_id or "test-session",
        )
        session_result = session.add_command(command.id)
        assert session_result.success
        session = session_result.unwrap()

        # Context should link entities
        assert execution_context.command_name == command.name
        assert execution_context.session_id == session.session_id
        assert command.id in session.command_history

    def test_context_with_file_operations(self) -> None:
        """Test context with file-based operations."""
        from flext_cli.config import CLISettings, get_config
        from rich.console import Console

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create proper CLI context (SOLID: Dependency Injection)
            config = get_config()
            config.profile = "file-test"
            config.output_format = "yaml"
            config.debug = False

            context = CLIContext(
                config=config, settings=CLISettings(), console=Console()
            )

            test_file = Path(tmpdir) / "test_config.yaml"
            test_file.write_text("test: config")

            runner = CliRunner()

            # Test commands work with files
            result = runner.invoke(
                cli,
                [
                    "--profile",
                    context.config.profile,
                    "--output",
                    context.config.output_format,
                    "config",
                    "show",
                ],
            )
            assert result.exit_code == 0


class TestIntegrationErrorHandling:
    """Test error handling in CLI-entity integration."""

    def test_entity_validation_errors_with_cli(self) -> None:
        """Test entity validation errors are handled in CLI context."""
        # Test invalid command creation - Business rule validation
        command = CLICommand(
            id=str(uuid.uuid4()),
            name="",  # Invalid - empty string
            command_line="test",
            command_type=CommandType.CLI,
        )
        validation_result = command.validate_business_rules()
        assert validation_result.is_failure
        assert "Command name cannot be empty" in validation_result.error

        # Test invalid session creation - Pydantic validation (has min_length=1)
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            CLISession(id=str(uuid.uuid4()), session_id="")  # Invalid - empty string

        # Test invalid plugin creation - Pydantic validation (has min_length=1)
        with pytest.raises(ValidationError):
            CLIPlugin(
                id=str(uuid.uuid4()),
                name="",  # Invalid - empty string
                entry_point="test.main",
                commands=["test"],
            )

    def test_cli_error_handling_with_entities(self) -> None:
        """Test CLI error handling creates appropriate entities."""
        runner = CliRunner()

        # Execute invalid command
        result = runner.invoke(cli, ["completely-invalid-command"])
        assert result.exit_code != 0

        # Create entity for failed command
        command = CLICommand(
            id=str(uuid.uuid4()),
            name="completely-invalid-command",
            command_line="flext completely-invalid-command",
            command_type=CommandType.CLI,
        )

        start_result = command.start_execution()
        assert start_result.success
        command = start_result.unwrap()

        complete_result = command.complete_execution(
            exit_code=result.exit_code, stderr=result.output
        )
        assert complete_result.success
        command = complete_result.unwrap()

        assert command.command_status == CommandStatus.FAILED
        assert not command.successful

    def test_entity_state_consistency(self) -> None:
        """Test entity state remains consistent during CLI operations."""
        command = CLICommand(
            id=str(uuid.uuid4()),
            name="test-consistency",
            command_line="echo test",
            command_type=CommandType.SYSTEM,
        )

        # Initial state
        assert command.command_status == CommandStatus.PENDING
        assert command.started_at is None
        assert command.finished_at is None

        # Start execution
        start_result = command.start_execution()
        assert start_result.success
        command = start_result.unwrap()
        assert command.command_status == CommandStatus.RUNNING
        assert command.started_at is not None
        assert command.finished_at is None

        # Complete execution
        complete_result = command.complete_execution(exit_code=0, stdout="test")
        assert complete_result.success
        command = complete_result.unwrap()
        assert command.command_status == CommandStatus.COMPLETED
        assert command.finished_at is not None
        assert command.successful


class TestRealWorldIntegrationScenarios:
    """Test real-world integration scenarios."""

    def test_development_session_scenario(self) -> None:
        """Test complete development session scenario."""
        # Developer starts a session
        session = CLISession(id=str(uuid.uuid4()), session_id="dev-session-001")
        runner = CliRunner()

        # Developer workflow
        dev_commands = [
            (["--profile", "dev", "config", "show"], 0),  # Should work
            (["--debug", "debug", "info"], 0),  # Should work
            (["--profile", "dev", "config", "validate"], 0),  # Should work
            (["--output", "json", "auth", "status"], 1),  # Fails when not authenticated
        ]

        for cmd_args, expected_exit_code in dev_commands:
            result = runner.invoke(cli, cmd_args)
            assert result.exit_code == expected_exit_code

            command = CLICommand(
                id=str(uuid.uuid4()),
                name=f"dev-{'-'.join([arg for arg in cmd_args if not arg.startswith('--')])}",
                command_line=f"flext {' '.join(cmd_args)}",
                command_type=CommandType.CLI,
            )

            start_result = command.start_execution()
            assert start_result.success
            command = start_result.unwrap()

            complete_result = command.complete_execution(
                exit_code=expected_exit_code, stdout=result.output
            )
            assert complete_result.success
            command = complete_result.unwrap()

            session_result = session.add_command(command.id)
            assert session_result.success
            session = session_result.unwrap()

        # Session should track all developer commands
        assert len(session.command_history) == len(dev_commands)

        # End development session
        end_result = session.end_session()
        assert end_result.success
        session = end_result.unwrap()
        assert session.session_status == SessionStatus.COMPLETED

    def test_production_monitoring_scenario(self) -> None:
        """Test production monitoring scenario."""
        # Ops engineer monitoring session
        session = CLISession(id=str(uuid.uuid4()), session_id="ops-monitoring-001")
        runner = CliRunner()

        # Monitoring commands (all in JSON for automation)
        monitoring_commands = [
            (
                ["--profile", "prod", "--output", "json", "auth", "status"],
                1,
            ),  # Fails when not authenticated
            (
                ["--profile", "prod", "--output", "json", "config", "validate"],
                0,
            ),  # Should work
            (
                ["--profile", "prod", "--output", "json", "debug", "check"],
                0,
            ),  # Should work
        ]

        for cmd_args, expected_exit_code in monitoring_commands:
            result = runner.invoke(cli, cmd_args)
            assert result.exit_code == expected_exit_code

            command = CLICommand(
                id=str(uuid.uuid4()),
                name=f"monitor-{'-'.join([arg for arg in cmd_args if not arg.startswith('--')])}",
                command_line=f"flext {' '.join(cmd_args)}",
                command_type=CommandType.CLI,
            )

            start_result = command.start_execution()
            assert start_result.success
            command = start_result.unwrap()

            complete_result = command.complete_execution(
                exit_code=expected_exit_code, stdout=result.output
            )
            assert complete_result.success
            command = complete_result.unwrap()

            session_result = session.add_command(command.id)
            assert session_result.success
            session = session_result.unwrap()

        assert len(session.command_history) == len(monitoring_commands)
        end_result = session.end_session()
        assert end_result.success
        session = end_result.unwrap()

    def test_troubleshooting_scenario(self) -> None:
        """Test troubleshooting scenario."""
        # Support engineer troubleshooting session
        session = CLISession(id=str(uuid.uuid4()), session_id="troubleshoot-001")
        runner = CliRunner()

        # Troubleshooting workflow
        troubleshoot_commands = [
            (["--debug", "debug", "info"], 0),  # Should work
            (["--debug", "debug", "check"], 0),  # Should work
            (["--debug", "config", "validate"], 0),  # Should work
            (
                ["--debug", "--output", "json", "auth", "status"],
                1,
            ),  # Fails when not authenticated
        ]

        for cmd_args, expected_exit_code in troubleshoot_commands:
            result = runner.invoke(cli, cmd_args)
            # Auth commands expected to fail when not authenticated
            assert result.exit_code == expected_exit_code

            command = CLICommand(
                id=str(uuid.uuid4()),
                name=f"troubleshoot-{'-'.join([arg for arg in cmd_args if not arg.startswith('--')])}",
                command_line=f"flext {' '.join(cmd_args)}",
                command_type=CommandType.CLI,
            )

            start_result = command.start_execution()
            assert start_result.success
            command = start_result.unwrap()

            complete_result = command.complete_execution(
                exit_code=expected_exit_code, stdout=result.output
            )
            assert complete_result.success
            command = complete_result.unwrap()

            session_result = session.add_command(command.id)
            assert session_result.success
            session = session_result.unwrap()

        # All troubleshooting commands should be tracked
        assert len(session.command_history) == len(troubleshoot_commands)
        end_result = session.end_session()
        assert end_result.success
        session = end_result.unwrap()
