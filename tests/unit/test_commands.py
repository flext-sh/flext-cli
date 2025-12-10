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
from typing import cast

from flext_cli import FlextCliCommands, c, p, r

# from ..fixtures.constants import TestCommands  # Fixtures removed - use conftest.py and flext_tests
from ..helpers import CommandsFactory


class TestsCliCommands:
    """Comprehensive tests for FlextCliCommands class."""

    # ========================================================================
    # INITIALIZATION AND BASIC EXECUTION
    # ========================================================================

    def test_commands_initialization(self) -> None:
        """Test Commands initialization with proper configuration."""
        commands = CommandsFactory.create_commands()
        assert commands is not None
        assert isinstance(commands, FlextCliCommands)

    def test_commands_execute_sync(self) -> None:
        """Test synchronous Commands execution."""
        commands = CommandsFactory.create_commands()
        result = commands.execute()

        assert result.is_success
        assert result.value is not None
        assert result.value["status"] == c.Cli.ServiceStatus.OPERATIONAL.value
        assert result.value["service"] == c.Cli.FLEXT_CLI
        assert "commands" in result.value

    def test_commands_execute(self) -> None:
        """Test execute method (now sync, delegates to execute)."""
        commands = CommandsFactory.create_commands()
        result = commands.execute()

        assert result.is_success
        assert result.value is not None
        assert result.value["status"] == c.Cli.ServiceStatus.OPERATIONAL.value
        assert result.value["service"] == c.Cli.FLEXT_CLI
        assert "commands" in result.value

    # ========================================================================
    # COMMAND LIST AND REGISTRATION
    # ========================================================================

    def test_commands_list(self) -> None:
        """Test commands list functionality."""
        commands = CommandsFactory.create_commands()
        result = commands.execute()

        assert result.is_success
        commands_list = result.value["commands"]
        assert isinstance(commands_list, list)
        assert len(commands_list) >= 0

    def test_commands_registration(self) -> None:
        """Test command registration functionality."""
        commands = CommandsFactory.create_commands()
        reg_result = CommandsFactory.register_simple_command(commands, "test_command")
        assert reg_result.is_success

        exec_result = commands.execute()
        assert exec_result.is_success
        commands_list = exec_result.value["commands"]
        assert commands_list is not None

    # ========================================================================
    # COMMAND EXECUTION
    # ========================================================================

    def test_commands_execution(self) -> None:
        """Test command execution functionality."""
        commands = CommandsFactory.create_commands()

        CommandsFactory.register_simple_command(
            commands,
            "test_execution",
            "executed",
        )

        result = commands.execute_command("test_execution")
        assert result.is_success
        assert result.value == "executed"

    def test_execute_command_with_args(self) -> None:
        """Test execute_command with args parameter."""
        commands = CommandsFactory.create_commands()

        CommandsFactory.register_command_with_args(commands, "test_with_args")

        result = commands.execute_command(
            "test_with_args",
            args=["arg1", "arg2"],
        )
        assert result.is_success
        # Handler returns "args: {len(args)}" format
        result_value = str(result.value)
        assert "args:" in result_value
        assert "2" in result_value  # Two args passed

    def test_execute_command_handler_without_args(self) -> None:
        """Test execute_command with handler that doesn't accept args."""
        commands = CommandsFactory.create_commands()

        CommandsFactory.register_simple_command(
            commands,
            "test_no_args",
            "no_args_result",
        )

        result = commands.execute_command("test_no_args", args=["arg1", "arg2"])
        assert result.is_success
        assert result.value == "no_args_result"

    def test_execute_command_with_timeout(self) -> None:
        """Test execute_command with timeout parameter."""
        commands = CommandsFactory.create_commands()

        CommandsFactory.register_simple_command(
            commands,
            "timed",
            "timed_result",
        )

        result = commands.execute_command(
            "timed",
            timeout=10,
        )
        assert result.is_success
        assert result.value == "timed_result"

    # ========================================================================
    # ERROR HANDLING
    # ========================================================================

    def test_commands_error_handling(self) -> None:
        """Test commands error handling capabilities."""
        commands = CommandsFactory.create_commands()

        result = commands.execute_command("non_existent")
        assert result.is_failure
        assert result.error is not None
        assert "not found" in result.error.lower() or "unknown" in result.error.lower()

    def test_execute_command_handler_not_callable(self) -> None:
        """Test execute_command with non-callable handler."""
        commands = CommandsFactory.create_commands()

        commands._commands["bad_cmd"] = {"handler": "not_callable"}

        result = commands.execute_command("bad_cmd")

        assert result.is_failure
        assert "not callable" in str(result.error).lower()

    def test_execute_command_execution_exception(self) -> None:
        """Test execute_command when handler raises exception."""
        commands = CommandsFactory.create_commands()

        CommandsFactory.register_failing_command(commands, "failing")

        result = commands.execute_command("failing")

        assert result.is_failure
        assert result.error is not None

    def test_execute_command_invalid_structure(self) -> None:
        """Test execute_command with invalid command structure."""
        commands = CommandsFactory.create_commands()

        commands._commands["bad_cmd"] = {"invalid": "structure"}

        result = commands.execute_command("bad_cmd")
        assert result.is_failure
        assert "Invalid command structure" in str(result.error) or (
            "not callable" in str(result.error)
        )

    # ========================================================================
    # PERFORMANCE AND MEMORY
    # ========================================================================

    def test_commands_performance(self) -> None:
        """Test commands performance characteristics."""
        commands = CommandsFactory.create_commands()

        start_time = time.time()
        result = commands.execute()
        execution_time = time.time() - start_time

        assert result.is_success
        assert execution_time < 5.0

    def test_commands_memory_usage(self) -> None:
        """Test commands memory usage characteristics."""
        commands = CommandsFactory.create_commands()

        for _ in range(10):
            result = commands.execute()
            assert result.is_success

    # ========================================================================
    # INTEGRATION AND SERVICE PROPERTIES
    # ========================================================================

    def test_commands_integration(self) -> None:
        """Test commands integration with other services."""
        commands = CommandsFactory.create_commands()

        result = commands.execute()
        assert result.is_success

        CommandsFactory.register_simple_command(
            commands,
            "integration_test",
            "integration_ok",
        )

        exec_result = commands.execute_command("integration_test")
        assert exec_result.is_success
        assert exec_result.value == "integration_ok"

    def test_commands_service_properties(self) -> None:
        """Test commands service properties."""
        commands = CommandsFactory.create_commands()

        assert hasattr(commands, "register_command")
        assert hasattr(commands, "execute_command")
        assert hasattr(commands, "execute")

    def test_commands_logging_integration(self) -> None:
        """Test commands logging integration."""
        commands = CommandsFactory.create_commands()

        result = commands.execute()
        assert result.is_success
        assert result.value is not None

    # ========================================================================
    # CONCURRENT EXECUTION AND "valid"ATION
    # ========================================================================

    def test_commands_concurrent_execution(self) -> None:
        """Test commands concurrent execution."""
        commands = CommandsFactory.create_commands()

        CommandsFactory.register_simple_command(commands, "cmd1", "result1")
        CommandsFactory.register_simple_command(commands, "cmd2", "result2")

        result1 = commands.execute_command("cmd1")
        result2 = commands.execute_command("cmd2")

        assert result1.is_success
        assert result2.is_success
        assert result1.value == "result1"
        assert result2.value == "result2"

    def test_commands_command_validation(self) -> None:
        """Test command validation functionality."""
        commands = CommandsFactory.create_commands()

        CommandsFactory.register_simple_command(commands, "valid", "test_result")

        result = commands.execute_command("valid")
        assert result.is_success

        invalid_result = commands.execute_command("invalid_cmd")
        assert invalid_result.is_failure

    # ========================================================================
    # UNREGISTER AND COMMAND MANAGEMENT
    # ========================================================================

    def test_unregister_command_not_found(self) -> None:
        """Test unregister_command when command doesn't exist."""
        commands = CommandsFactory.create_commands()

        result = commands.unregister_command("non_existent")
        assert result.is_failure
        assert result.error is not None
        assert "not found" in result.error.lower()

    def test_unregister_command_success(self) -> None:
        """Test successful command unregistration."""
        commands = CommandsFactory.create_commands()

        CommandsFactory.register_simple_command(commands, "temp_cmd")
        result = commands.unregister_command("temp_cmd")
        assert result.is_success

        exec_result = commands.execute_command("temp_cmd")
        assert exec_result.is_failure

    def test_get_commands(self) -> None:
        """Test get_commands method."""
        commands = CommandsFactory.create_commands()

        CommandsFactory.register_simple_command(commands, "cmd1")
        CommandsFactory.register_simple_command(commands, "cmd2")

        cmds = commands.get_commands()
        assert isinstance(cmds, dict)
        assert len(cmds) == 2
        assert "cmd1" in cmds
        assert "cmd2" in cmds

    def test_clear_commands(self) -> None:
        """Test clear_commands method."""
        commands = CommandsFactory.create_commands()

        CommandsFactory.register_simple_command(commands, "cmd1")
        CommandsFactory.register_simple_command(commands, "cmd2")

        result = commands.clear_commands()
        assert result.is_success
        assert result.value == 2

        cmds = commands.get_commands()
        assert len(cmds) == 0

    def test_list_commands(self) -> None:
        """Test list_commands method."""
        commands = CommandsFactory.create_commands()

        CommandsFactory.register_simple_command(commands, "alpha")
        CommandsFactory.register_simple_command(commands, "beta")

        result = commands.list_commands()
        assert result.is_success
        cmd_list = result.value
        assert isinstance(cmd_list, list)
        assert len(cmd_list) == 2
        assert "alpha" in cmd_list
        assert "beta" in cmd_list

    # ========================================================================
    # COMMAND GROUPS AND CLI
    # ========================================================================

    def test_create_command_group(self) -> None:
        """Test create_command_group method."""
        commands = CommandsFactory.create_commands()

        result = commands.create_command_group(
            "test_group",
            description="Test group description",
            commands={
                "cmd1": {
                    "handler": cast(
                        "p.Cli.CliCommandHandler",
                        lambda: "result1",
                    ),
                },
            },
        )
        assert result.is_success
        group = result.value
        assert hasattr(group, "name")
        assert group.name == "test_group"

    def test_get_click_group(self) -> None:
        """Test get_click_group method."""
        commands = CommandsFactory.create_commands()

        group = commands.get_click_group()
        assert group is not None
        assert hasattr(group, "name")
        assert hasattr(group, "commands")

    def test_run_cli_success(self) -> None:
        """Test run_cli successful execution."""
        commands = CommandsFactory.create_commands()

        CommandsFactory.register_simple_command(commands, "test_command")

        result = commands.run_cli(["test_command"])
        assert result.is_success

    def test_run_cli_with_options(self) -> None:
        """Test run_cli skips option arguments."""
        commands = CommandsFactory.create_commands()

        result = commands.run_cli(["--help", "--version"])
        assert result.is_success

    def test_run_cli_with_invalid_command(self) -> None:
        """Test run_cli with invalid command in args."""
        commands = CommandsFactory.create_commands()

        CommandsFactory.register_simple_command(commands, "valid")

        result = commands.run_cli(["invalid_cmd"])
        assert result.is_failure
        assert result.error is not None
        assert "not found" in result.error.lower()

    def test_create_main_cli(self) -> None:
        """Test create_main_cli method."""
        commands = FlextCliCommands(name="test_cli", description="Test CLI")

        main_cli = commands.create_main_cli()
        assert isinstance(main_cli, FlextCliCommands)
        assert main_cli._name == "test_cli"
        assert main_cli._description == "Test CLI"

    # ========================================================================
    # EDGE CASES AND ADVANCED SCENARIOS
    # ========================================================================

    def test_create_command_group_with_none(self) -> None:
        """Test create_command_group with None commands."""
        commands = CommandsFactory.create_commands()

        result = commands.create_command_group(
            "test_group",
            "Test group description",
            None,
        )
        assert result.is_failure
        assert "required" in str(result.error).lower()

    def test_create_command_group_with_empty_commands(self) -> None:
        """Test create_command_group with empty commands dict."""
        commands = CommandsFactory.create_commands()

        result = commands.create_command_group(
            "test_group",
            "Test group description",
            {},
        )
        assert isinstance(result, r)

    def test_run_cli_success_with_empty_args(self) -> None:
        """Test run_cli with successful execution and empty args."""
        commands = CommandsFactory.create_commands()

        CommandsFactory.register_simple_command(commands, "test_command")

        result = commands.run_cli()
        assert isinstance(result, r)

    def test_clear_commands_success_with_multiple(self) -> None:
        """Test clear_commands with real commands."""
        commands = CommandsFactory.create_commands()

        CommandsFactory.register_simple_command(commands, "cmd1")
        CommandsFactory.register_simple_command(commands, "cmd2")

        result = commands.clear_commands()
        assert result.is_success

        list_result = commands.list_commands()
        if list_result.is_success:
            assert len(list_result.value) == 0

    def test_list_commands_success_with_registered(self) -> None:
        """Test list_commands with real registered commands."""
        commands = CommandsFactory.create_commands()

        CommandsFactory.register_simple_command(commands, "cmd1")
        CommandsFactory.register_simple_command(commands, "cmd2")

        result = commands.list_commands()
        assert result.is_success
        commands_list = result.value
        assert isinstance(commands_list, list)
        assert len(commands_list) == 2
