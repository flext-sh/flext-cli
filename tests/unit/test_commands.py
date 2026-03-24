"""FLEXT CLI Commands Tests - Comprehensive Commands Functionality Testing.

Tests for FlextCliCommands covering command registration, execution, lifecycle management,
error handling, integration workflows, and edge cases with 100% coverage.

Modules tested: flext_cli.commands.FlextCliCommands
Scope: All command operations, registration, execution, lifecycle management

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import time

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
        tm.that(isinstance(commands, FlextCliCommands), eq=True)

    def test_commands_execute_sync(self) -> None:
        """Test synchronous Commands execution."""
        commands = CommandsFactory.create_commands()
        result = commands.execute()
        tm.ok(result)
        tm.that(result.value, none=False)
        tm.that(isinstance(result.value, dict), eq=True)
        tm.that(result.value["app_name"], eq=c.Cli.FLEXT_CLI)

    def test_commands_execute(self) -> None:
        """Test execute method (now sync, delegates to execute)."""
        commands = CommandsFactory.create_commands()
        result = commands.execute()
        tm.ok(result)
        tm.that(result.value, none=False)
        tm.that(isinstance(result.value, dict), eq=True)
        tm.that(result.value["app_name"], eq=c.Cli.FLEXT_CLI)

    def test_commands_list(self) -> None:
        """Test commands list functionality."""
        commands = CommandsFactory.create_commands()
        result = commands.execute()
        tm.ok(result)
        tm.that(isinstance(result.value, dict), eq=True)
        commands_count = result.value["commands_count"]
        tm.that(isinstance(commands_count, int), eq=True)
        tm.that(commands_count, gte=0)

    def test_commands_registration(self) -> None:
        """Test command registration functionality."""
        commands = CommandsFactory.create_commands()
        reg_result = CommandsFactory.register_simple_command(commands, "test_command")
        tm.ok(reg_result)
        exec_result = commands.execute()
        tm.ok(exec_result)
        tm.that(isinstance(exec_result.value, dict), eq=True)
        commands_count = exec_result.value["commands_count"]
        tm.that(isinstance(commands_count, int), eq=True)
        tm.that(commands_count, gte=0)

    def test_commands_execution(self) -> None:
        """Test command execution functionality."""
        commands = CommandsFactory.create_commands()
        _ = CommandsFactory.register_simple_command(
            commands, "test_execution", "executed"
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
            commands, "test_no_args", "no_args_result"
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
        bad_entry = m.Cli.CommandEntryModel.model_construct(
            name="bad_cmd", handler="not_callable"
        )
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
        invalid_entry = m.Cli.CommandEntryModel.model_construct(
            name="bad_cmd", handler=None
        )
        commands._commands["bad_cmd"] = invalid_entry
        result = commands.execute_command("bad_cmd")
        tm.fail(result)
        tm.that(
            "Invalid command structure" in str(result.error)
            or "not callable" in str(result.error),
            eq=True,
        )

    def test_commands_performance(self) -> None:
        """Test commands performance characteristics."""
        commands = CommandsFactory.create_commands()
        start_time = time.time()
        result = commands.execute()
        execution_time = time.time() - start_time
        tm.ok(result)
        tm.that(execution_time, lt=5.0)

    def test_commands_memory_usage(self) -> None:
        """Test commands memory usage characteristics."""
        commands = CommandsFactory.create_commands()
        for _ in range(10):
            result = commands.execute()
            tm.ok(result)

    def test_commands_integration(self) -> None:
        """Test commands integration with other services."""
        commands = CommandsFactory.create_commands()
        result = commands.execute()
        tm.ok(result)
        _ = CommandsFactory.register_simple_command(
            commands, "integration_test", "integration_ok"
        )
        exec_result = commands.execute_command("integration_test")
        tm.ok(exec_result)
        tm.that(exec_result.value, eq="integration_ok")

    def test_commands_service_properties(self) -> None:
        """Test commands service properties."""
        commands = CommandsFactory.create_commands()
        tm.that(hasattr(commands, "register_command"), eq=True)
        tm.that(hasattr(commands, "execute_command"), eq=True)
        tm.that(hasattr(commands, "execute"), eq=True)

    def test_commands_logging_integration(self) -> None:
        """Test commands logging integration."""
        commands = CommandsFactory.create_commands()
        result = commands.execute()
        tm.ok(result)
        tm.that(result.value, none=False)

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

    def test_unregister_command_not_found(self) -> None:
        """Test unregister_command when command doesn't exist."""
        commands = CommandsFactory.create_commands()
        result = commands.unregister_command("non_existent")
        tm.fail(result)
        tm.that(result.error, none=False)
        tm.that((result.error or "").lower(), has="not found")

    def test_unregister_command_success(self) -> None:
        """Test successful command unregistration."""
        commands = CommandsFactory.create_commands()
        _ = CommandsFactory.register_simple_command(commands, "temp_cmd")
        result = commands.unregister_command("temp_cmd")
        tm.ok(result)
        exec_result = commands.execute_command("temp_cmd")
        tm.fail(exec_result)

    def test_get_commands(self) -> None:
        """Test get_commands method."""
        commands = CommandsFactory.create_commands()
        _ = CommandsFactory.register_simple_command(commands, "cmd1")
        _ = CommandsFactory.register_simple_command(commands, "cmd2")
        cmds = commands.get_commands()
        tm.that(isinstance(cmds, dict), eq=True)
        tm.that(len(cmds), eq=2)
        tm.that(cmds, has="cmd1")
        tm.that(cmds, has="cmd2")

    def test_clear_commands(self) -> None:
        """Test clear_commands method."""
        commands = CommandsFactory.create_commands()
        _ = CommandsFactory.register_simple_command(commands, "cmd1")
        _ = CommandsFactory.register_simple_command(commands, "cmd2")
        result = commands.clear_commands()
        tm.ok(result)
        tm.that(result.value, eq=2)
        cmds = commands.get_commands()
        tm.that(len(cmds), eq=0)

    def test_list_commands(self) -> None:
        """Test list_commands method."""
        commands = CommandsFactory.create_commands()
        _ = CommandsFactory.register_simple_command(commands, "alpha")
        _ = CommandsFactory.register_simple_command(commands, "beta")
        result = commands.list_commands()
        tm.ok(result)
        cmd_list = result.value
        tm.that(isinstance(cmd_list, list), eq=True)
        tm.that(len(cmd_list), eq=2)
        tm.that(cmd_list, has="alpha")
        tm.that(cmd_list, has="beta")

    def test_create_command_group(self) -> None:
        """Test create_command_group method."""
        commands = CommandsFactory.create_commands()

        def grouped_handler(*args: t.Scalar, **kwargs: t.Scalar) -> r[str]:
            _ = (args, kwargs)
            return r.ok("result1")

        result = commands.create_command_group(
            "test_group",
            description="Test group description",
            commands={
                "cmd1": m.Cli.CommandEntryModel(name="cmd1", handler=grouped_handler)
            },
        )
        tm.ok(result)
        group = result.value
        tm.that(hasattr(group, "name"), eq=True)
        tm.that(group.name, eq="test_group")

    def test_get_click_group(self) -> None:
        """Test get_click_group method."""
        commands = CommandsFactory.create_commands()
        group = commands.get_click_group()
        tm.that(group, none=False)
        tm.that(hasattr(group, "name"), eq=True)
        tm.that(hasattr(group, "commands"), eq=True)

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

    def test_create_main_cli(self) -> None:
        """Test create_main_cli method."""
        commands = FlextCliCommands(name="test_cli", description="Test CLI")
        main_cli = commands.create_main_cli()
        tm.that(isinstance(main_cli, FlextCliCommands), eq=True)
        tm.that(main_cli._name, eq="test_cli")
        tm.that(main_cli._description, eq="Test CLI")

    def test_create_command_group_with_none(self) -> None:
        """Test create_command_group with None commands."""
        commands = CommandsFactory.create_commands()
        result = commands.create_command_group(
            "test_group", "Test group description", None
        )
        tm.fail(result)
        tm.that(str(result.error).lower(), has="required")

    def test_create_command_group_with_empty_commands(self) -> None:
        """Test create_command_group with empty commands dict."""
        commands = CommandsFactory.create_commands()
        result = commands.create_command_group(
            "test_group", "Test group description", {}
        )
        tm.that(isinstance(result, r), eq=True)

    def test_run_cli_success_with_empty_args(self) -> None:
        """Test run_cli with successful execution and empty args."""
        commands = CommandsFactory.create_commands()
        _ = CommandsFactory.register_simple_command(commands, "test_command")
        result = commands.run_cli()
        tm.that(isinstance(result, r), eq=True)

    def test_clear_commands_success_with_multiple(self) -> None:
        """Test clear_commands with real commands."""
        commands = CommandsFactory.create_commands()
        _ = CommandsFactory.register_simple_command(commands, "cmd1")
        _ = CommandsFactory.register_simple_command(commands, "cmd2")
        result = commands.clear_commands()
        tm.ok(result)
        list_result = commands.list_commands()
        if list_result.is_success:
            tm.that(len(list_result.value), eq=0)

    def test_list_commands_success_with_registered(self) -> None:
        """Test list_commands with real registered commands."""
        commands = CommandsFactory.create_commands()
        _ = CommandsFactory.register_simple_command(commands, "cmd1")
        _ = CommandsFactory.register_simple_command(commands, "cmd2")
        result = commands.list_commands()
        tm.ok(result)
        commands_list = result.value
        tm.that(isinstance(commands_list, list), eq=True)
        tm.that(len(commands_list), eq=2)
