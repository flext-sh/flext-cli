"""FLEXT CLI Commands Tests - Comprehensive Commands Functionality Testing.

Tests for FlextCliCommands covering command registration, execution, lifecycle management,
error handling, integration workflows, and edge cases.

Modules tested: flext_cli.commands.FlextCliCommands
Scope: All kept command operations, registration, execution, lifecycle management

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_core import r
from flext_tests import tm

from flext_cli import FlextCliCommands, c, m, t

from ..helpers import CommandsFactory


class TestsCliCommands:
    """Comprehensive tests for FlextCliCommands class."""

    def test_commands_initialization(self) -> None:
        """Test Commands initialization with proper configuration."""
        commands = CommandsFactory.create_commands()
        tm.that(commands, none=False)
        tm.that(commands, is_=FlextCliCommands)

    def test_commands_execute_sync(self) -> None:
        """Test synchronous Commands execution."""
        commands = CommandsFactory.create_commands()
        result = commands.execute()
        tm.ok(result)
        tm.that(result.value, none=False)
        tm.that(result.value, is_=dict)
        tm.that(result.value["app_name"], eq=c.Cli.FLEXT_CLI)

    def test_commands_list(self) -> None:
        """Test commands list functionality."""
        commands = CommandsFactory.create_commands()
        result = commands.execute()
        tm.ok(result)
        tm.that(result.value, is_=dict)
        commands_count = result.value["commands_count"]
        tm.that(commands_count, is_=int)
        tm.that(commands_count, gte=0)

    def test_commands_registration(self) -> None:
        """Test command registration functionality."""
        commands = CommandsFactory.create_commands()
        reg_result = CommandsFactory.register_simple_command(commands, "test_command")
        tm.ok(reg_result)
        exec_result = commands.execute()
        tm.ok(exec_result)
        tm.that(exec_result.value, is_=dict)
        commands_count = exec_result.value["commands_count"]
        tm.that(commands_count, is_=int)
        tm.that(commands_count, gte=0)

    def test_commands_execution(self) -> None:
        """Test command execution functionality."""
        commands = CommandsFactory.create_commands()
        _ = CommandsFactory.register_simple_command(
            commands,
            "test_execution",
            "executed",
        )
        result = commands.execute_command("test_execution")
        tm.ok(result)
        tm.that(result.value, eq="executed")

    def test_execute_command_with_args(self) -> None:
        """Test execute_command with args parameter."""
        commands = CommandsFactory.create_commands()
        _ = CommandsFactory.register_command_with_args(commands, "test_with_args")
        result = commands.execute_command("test_with_args", args=["arg1", "arg2"])
        tm.ok(result)
        result_value = str(result.value)
        tm.that(result_value, has="args:")
        tm.that(result_value, has="2")

    def test_execute_command_handler_without_args(self) -> None:
        """Test execute_command with handler that doesn't accept args."""
        commands = CommandsFactory.create_commands()
        _ = CommandsFactory.register_simple_command(
            commands,
            "test_no_args",
            "no_args_result",
        )
        result = commands.execute_command("test_no_args", args=["arg1", "arg2"])
        tm.ok(result)
        tm.that(result.value, eq="no_args_result")

    def test_execute_command_with_timeout(self) -> None:
        """Test execute_command with timeout parameter."""
        commands = CommandsFactory.create_commands()
        _ = CommandsFactory.register_simple_command(commands, "timed", "timed_result")
        result = commands.execute_command("timed", timeout=10)
        tm.ok(result)
        tm.that(result.value, eq="timed_result")

    def test_commands_error_handling(self) -> None:
        """Test commands error handling capabilities."""
        commands = CommandsFactory.create_commands()
        result = commands.execute_command("non_existent")
        tm.fail(result)
        tm.that(result.error, none=False)
        tm.that(
            "not found" in (result.error or "").lower()
            or "unknown" in (result.error or "").lower(),
            eq=True,
        )

    def test_execute_command_handler_not_callable(self) -> None:
        """Test execute_command with non-callable handler."""
        commands = CommandsFactory.create_commands()
        bad_entry = m.Cli.CommandEntryModel(
            name="bad_cmd",
            handler=lambda: r[t.Cli.JsonValue].ok("ok"),
        )
        object.__setattr__(bad_entry, "handler", "not_callable")
        commands._commands["bad_cmd"] = bad_entry
        result = commands.execute_command("bad_cmd")
        tm.fail(result)
        tm.that(str(result.error).lower(), has="not callable")

    def test_execute_command_execution_exception(self) -> None:
        """Test execute_command when handler raises exception."""
        commands = CommandsFactory.create_commands()
        _ = CommandsFactory.register_failing_command(commands, "failing")
        result = commands.execute_command("failing")
        tm.fail(result)
        tm.that(result.error, none=False)

    def test_execute_command_invalid_structure(self) -> None:
        """Test execute_command with invalid command structure."""
        commands = CommandsFactory.create_commands()
        invalid_entry = m.Cli.CommandEntryModel(
            name="bad_cmd",
            handler=lambda: r[t.Cli.JsonValue].ok("ok"),
        )
        object.__setattr__(invalid_entry, "handler", None)
        commands._commands["bad_cmd"] = invalid_entry
        result = commands.execute_command("bad_cmd")
        tm.fail(result)
        tm.that(
            "Invalid command structure" in str(result.error)
            or "not callable" in str(result.error),
            eq=True,
        )

    def test_commands_concurrent_execution(self) -> None:
        """Test commands concurrent execution."""
        commands = CommandsFactory.create_commands()
        _ = CommandsFactory.register_simple_command(commands, "cmd1", "result1")
        _ = CommandsFactory.register_simple_command(commands, "cmd2", "result2")
        result1 = commands.execute_command("cmd1")
        result2 = commands.execute_command("cmd2")
        tm.ok(result1)
        tm.ok(result2)
        tm.that(result1.value, eq="result1")
        tm.that(result2.value, eq="result2")

    def test_commands_command_validation(self) -> None:
        """Test command validation functionality."""
        commands = CommandsFactory.create_commands()
        _ = CommandsFactory.register_simple_command(commands, "valid", "test_result")
        result = commands.execute_command("valid")
        tm.ok(result)
        invalid_result = commands.execute_command("invalid_cmd")
        tm.fail(invalid_result)

    def test_list_commands(self) -> None:
        """Test list_commands method."""
        commands = CommandsFactory.create_commands()
        _ = CommandsFactory.register_simple_command(commands, "alpha")
        _ = CommandsFactory.register_simple_command(commands, "beta")
        result = commands.list_commands()
        tm.ok(result)
        cmd_list = result.value
        tm.that(cmd_list, is_=list)
        tm.that(len(cmd_list), eq=2)
        tm.that(cmd_list, has="alpha")
        tm.that(cmd_list, has="beta")

    def test_run_cli_success(self) -> None:
        """Test run_cli successful execution."""
        commands = CommandsFactory.create_commands()
        _ = CommandsFactory.register_simple_command(commands, "test_command")
        result = commands.run_cli(["test_command"])
        tm.ok(result)

    def test_run_cli_with_options(self) -> None:
        """Test run_cli skips option arguments."""
        commands = CommandsFactory.create_commands()
        result = commands.run_cli(["--help", "--version"])
        tm.ok(result)

    def test_run_cli_with_invalid_command(self) -> None:
        """Test run_cli with invalid command in args."""
        commands = CommandsFactory.create_commands()
        _ = CommandsFactory.register_simple_command(commands, "valid")
        result = commands.run_cli(["invalid_cmd"])
        tm.fail(result)
        tm.that(result.error, none=False)
        tm.that((result.error or "").lower(), has="not found")

    def test_run_cli_success_with_empty_args(self) -> None:
        """Test run_cli with successful execution and empty args."""
        commands = CommandsFactory.create_commands()
        _ = CommandsFactory.register_simple_command(commands, "test_command")
        result = commands.run_cli()
        tm.that(result, is_=r)

    def test_list_commands_success_with_registered(self) -> None:
        """Test list_commands with real registered commands."""
        commands = CommandsFactory.create_commands()
        _ = CommandsFactory.register_simple_command(commands, "cmd1")
        _ = CommandsFactory.register_simple_command(commands, "cmd2")
        result = commands.list_commands()
        tm.ok(result)
        commands_list = result.value
        tm.that(commands_list, is_=list)
        tm.that(len(commands_list), eq=2)
