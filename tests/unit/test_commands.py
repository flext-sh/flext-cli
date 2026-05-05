"""FLEXT CLI Commands Tests - Comprehensive Commands Functionality Testing.

Tests for FlextCliCommands covering command registration, execution, lifecycle management,
error handling, integration workflows, and edge cases.

Modules tested: flext_cli.commands.FlextCliCommands
Scope: All kept command operations, registration, execution, lifecycle management

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_tests import tm

from flext_cli import cli
from tests import c, r, u


class TestsFlextCliCommands:
    """Comprehensive tests for public command-registry behavior."""

    def test_commands_initialization(self) -> None:
        """Test Commands initialization with proper configuration."""
        commands = u.Tests.CommandsFactory.create_commands()
        tm.that(commands, none=False)
        tm.that(commands, is_=type(cli))

    def test_commands_execute_sync(self) -> None:
        """Test synchronous public cli execution status."""
        commands = u.Tests.CommandsFactory.create_commands()
        result = commands.execute()
        tm.ok(result)
        tm.that(result.value, none=False)
        tm.that(result.value, is_=dict)
        tm.that(result.value[c.Cli.DICT_KEY_STATUS], eq=c.Cli.ServiceStatus.OPERATIONAL)
        tm.that(result.value[c.Cli.DICT_KEY_SERVICE], eq=c.Cli.CMD_SERVICE_NAME)

    def test_commands_list(self) -> None:
        """Test the public command list starts empty."""
        commands = u.Tests.CommandsFactory.create_commands()
        result = commands.list_commands()
        tm.ok(result)
        tm.that(result.value, is_=list)
        tm.that(len(result.value), eq=0)

    def test_commands_registration(self) -> None:
        """Test public command registration updates the visible registry."""
        commands = u.Tests.CommandsFactory.create_commands()
        reg_result = u.Tests.CommandsFactory.register_command(commands, "test_command")
        tm.ok(reg_result)
        list_result = commands.list_commands()
        tm.ok(list_result)
        tm.that(list_result.value, has="test_command")

    def test_commands_execution(self) -> None:
        """Test command execution functionality."""
        commands = u.Tests.CommandsFactory.create_commands()
        _ = u.Tests.CommandsFactory.register_command(
            commands,
            "test_execution",
            result_value="executed",
        )
        result = commands.execute_command("test_execution")
        tm.ok(result)
        tm.that(result.value, eq="executed")

    def test_execute_command_with_args(self) -> None:
        """Test execute_command with args parameter."""
        commands = u.Tests.CommandsFactory.create_commands()
        _ = u.Tests.CommandsFactory.register_command(
            commands, "test_with_args", reflect_args=True
        )
        result = commands.execute_command("test_with_args", args=["arg1", "arg2"])
        tm.ok(result)
        result_value = str(result.value)
        tm.that(result_value, has="args:")
        tm.that(result_value, has="2")

    def test_execute_command_handler_without_args(self) -> None:
        """Test execute_command with handler that doesn't accept args."""
        commands = u.Tests.CommandsFactory.create_commands()
        _ = u.Tests.CommandsFactory.register_command(
            commands,
            "test_no_args",
            result_value="no_args_result",
        )
        result = commands.execute_command("test_no_args", args=["arg1", "arg2"])
        tm.ok(result)
        tm.that(result.value, eq="no_args_result")

    def test_execute_command_with_timeout(self) -> None:
        """Test execute_command with timeout parameter."""
        commands = u.Tests.CommandsFactory.create_commands()
        _ = u.Tests.CommandsFactory.register_command(
            commands, "timed", result_value="timed_result"
        )
        result = commands.execute_command("timed", timeout=10)
        tm.ok(result)
        tm.that(result.value, eq="timed_result")

    def test_commands_error_handling(self) -> None:
        """Test commands error handling capabilities."""
        commands = u.Tests.CommandsFactory.create_commands()
        result = commands.execute_command("non_existent")
        tm.fail(result)
        tm.that(result.error, none=False)
        tm.that(
            "not found" in (result.error or "").lower()
            or "unknown" in (result.error or "").lower(),
            eq=True,
        )

    def test_execute_command_execution_exception(self) -> None:
        """Test execute_command when handler raises exception."""
        commands = u.Tests.CommandsFactory.create_commands()
        _ = u.Tests.CommandsFactory.register_command(
            commands, "failing", error_message="Test error"
        )
        result = commands.execute_command("failing")
        tm.fail(result)
        tm.that(result.error, none=False)

    def test_commands_concurrent_execution(self) -> None:
        """Test commands concurrent execution."""
        commands = u.Tests.CommandsFactory.create_commands()
        _ = u.Tests.CommandsFactory.register_command(
            commands, "cmd1", result_value="result1"
        )
        _ = u.Tests.CommandsFactory.register_command(
            commands, "cmd2", result_value="result2"
        )
        result1 = commands.execute_command("cmd1")
        result2 = commands.execute_command("cmd2")
        tm.ok(result1)
        tm.ok(result2)
        tm.that(result1.value, eq="result1")
        tm.that(result2.value, eq="result2")

    def test_commands_command_validation(self) -> None:
        """Test command validation functionality."""
        commands = u.Tests.CommandsFactory.create_commands()
        _ = u.Tests.CommandsFactory.register_command(
            commands, "valid", result_value="test_result"
        )
        result = commands.execute_command("valid")
        tm.ok(result)
        invalid_result = commands.execute_command("invalid_cmd")
        tm.fail(invalid_result)

    def test_list_commands(self) -> None:
        """Test list_commands method."""
        commands = u.Tests.CommandsFactory.create_commands()
        _ = u.Tests.CommandsFactory.register_command(commands, "alpha")
        _ = u.Tests.CommandsFactory.register_command(commands, "beta")
        result = commands.list_commands()
        tm.ok(result)
        cmd_list = result.value
        tm.that(cmd_list, is_=list)
        tm.that(len(cmd_list), eq=2)
        tm.that(cmd_list, has="alpha")
        tm.that(cmd_list, has="beta")

    def test_run_cli_success(self) -> None:
        """Test run_cli successful execution."""
        commands = u.Tests.CommandsFactory.create_commands()
        _ = u.Tests.CommandsFactory.register_command(commands, "test_command")
        result = commands.run_cli(["test_command"])
        tm.ok(result)

    def test_run_cli_with_options(self) -> None:
        """Test run_cli skips option arguments."""
        commands = u.Tests.CommandsFactory.create_commands()
        result = commands.run_cli(["--help", "--version"])
        tm.ok(result)

    def test_run_cli_with_invalid_command(self) -> None:
        """Test run_cli with invalid command in args."""
        commands = u.Tests.CommandsFactory.create_commands()
        _ = u.Tests.CommandsFactory.register_command(commands, "valid")
        result = commands.run_cli(["invalid_cmd"])
        tm.fail(result)
        tm.that(result.error, none=False)
        tm.that((result.error or "").lower(), has="not found")

    def test_run_cli_success_with_empty_args(self) -> None:
        """Test run_cli with successful execution and empty args."""
        commands = u.Tests.CommandsFactory.create_commands()
        _ = u.Tests.CommandsFactory.register_command(commands, "test_command")
        result = commands.run_cli()
        tm.that(result, is_=r)

    def test_list_commands_success_with_registered(self) -> None:
        """Test list_commands with real registered commands."""
        commands = u.Tests.CommandsFactory.create_commands()
        _ = u.Tests.CommandsFactory.register_command(commands, "cmd1")
        _ = u.Tests.CommandsFactory.register_command(commands, "cmd2")
        result = commands.list_commands()
        tm.ok(result)
        commands_list = result.value
        tm.that(commands_list, is_=list)
        tm.that(len(commands_list), eq=2)
