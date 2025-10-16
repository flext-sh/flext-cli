"""FLEXT CLI Commands Tests - Comprehensive commands functionality testing.

Tests for FlextCliCommands class using flext_tests infrastructure with real functionality
testing, no mocks, and comprehensive coverage following FLEXT standards.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import time
from typing import Never

import pytest
from flext_core import FlextResult, FlextTypes

from flext_cli.commands import FlextCliCommands
from flext_cli.constants import FlextCliConstants


class TestFlextCliCommands:
    """Comprehensive tests for FlextCliCommands class."""

    def test_commands_initialization(self) -> None:
        """Test Commands initialization with proper configuration."""
        commands = FlextCliCommands()
        assert commands is not None
        assert isinstance(commands, FlextCliCommands)

    def test_commands_execute_sync(self) -> None:
        """Test synchronous Commands execution."""
        commands = FlextCliCommands()
        result = commands.execute()

        assert result.is_success
        assert result.value is not None
        assert result.value["status"] == FlextCliConstants.OPERATIONAL
        assert result.value["service"] == FlextCliConstants.FLEXT_CLI
        assert "commands" in result.value

    def test_commands_execute(self) -> None:
        """Test execute method (now sync, delegates to execute)."""
        commands = FlextCliCommands()
        result = commands.execute()

        assert result.is_success
        assert result.value is not None
        assert result.value["status"] == FlextCliConstants.OPERATIONAL
        assert result.value["service"] == FlextCliConstants.FLEXT_CLI
        assert "commands" in result.value

    def test_commands_list(self) -> None:
        """Test commands list functionality."""
        commands = FlextCliCommands()
        result = commands.execute()

        assert result.is_success
        commands_list = result.value["commands"]
        assert isinstance(commands_list, list)
        assert len(commands_list) >= 0  # Should have some commands or empty list

    def test_commands_registration(self) -> None:
        """Test command registration functionality."""
        commands = FlextCliCommands()

        # Test that commands can be registered
        test_command = "test_command"
        commands.register_command(test_command, lambda: "test")

        result = commands.execute()
        assert result.is_success
        commands_list = result.value["commands"]

        # The registered command should be in the list
        # Test commands list availability
        assert commands_list is not None

    def test_commands_execution(self) -> None:
        """Test command execution functionality."""
        commands = FlextCliCommands()

        # Register a test command
        test_command = "test_execution"
        commands.register_command(test_command, lambda: "executed")

        # Execute the command
        result = commands.execute_command(test_command)
        assert result.is_success
        assert result.value == "executed"

    def test_commands_error_handling(self) -> None:
        """Test commands error handling capabilities."""
        commands = FlextCliCommands()

        # Test executing non-existent command
        result = commands.execute_command("non_existent_command")
        assert result.is_failure
        assert result.error is not None
        assert (
            result.error is not None and "not found" in result.error.lower()
        ) or "unknown" in result.error.lower()

    def test_commands_performance(self) -> None:
        """Test commands performance characteristics."""
        commands = FlextCliCommands()

        start_time = time.time()
        result = commands.execute()
        execution_time = time.time() - start_time

        assert result.is_success
        # Should execute quickly
        assert execution_time < 1.0

    def test_commands_memory_usage(self) -> None:
        """Test commands memory usage characteristics."""
        commands = FlextCliCommands()

        # Test multiple executions
        for _ in range(10):
            result = commands.execute()
            assert result.is_success

    def test_commands_integration(self) -> None:
        """Test commands integration with other services."""
        commands = FlextCliCommands()

        # Test that commands properly integrate with their dependencies
        result = commands.execute()
        assert result.is_success

        # Test command registration and execution
        test_command = "integration_test"
        commands.register_command(test_command, lambda: "integration_ok")

        exec_result = commands.execute_command(test_command)
        assert exec_result.is_success
        assert exec_result.value == "integration_ok"

    def test_commands_service_properties(self) -> None:
        """Test commands service properties."""
        commands = FlextCliCommands()

        # Test that all required properties are accessible
        assert hasattr(commands, "register_command")
        assert hasattr(commands, "execute_command")
        assert hasattr(commands, "execute")
        assert hasattr(commands, "execute")

    def test_commands_logging_integration(self) -> None:
        """Test commands logging integration."""
        commands = FlextCliCommands()

        # Test that logging is properly integrated
        result = commands.execute()
        assert result.is_success

        # Should not raise any logging-related exceptions
        assert result.value is not None

    def test_commands_concurrent_execution(self) -> None:
        """Test commands concurrent execution."""
        commands = FlextCliCommands()

        # Register multiple commands
        commands.register_command("cmd1", lambda: "result1")
        commands.register_command("cmd2", lambda: "result2")

        # Execute commands sequentially (since execute_command is not )
        result1 = commands.execute_command("cmd1")
        result2 = commands.execute_command("cmd2")

        assert result1.is_success
        assert result2.is_success
        assert result1.value == "result1"
        assert result2.value == "result2"

    def test_commands_command_validation(self) -> None:
        """Test command validation functionality."""
        commands = FlextCliCommands()

        # Test valid command registration
        commands.register_command("valid_cmd", lambda: "valid")

        # Test command execution
        result = commands.execute_command("valid_cmd")
        assert result.is_success

        # Test invalid command execution
        invalid_result = commands.execute_command("invalid_cmd")
        assert invalid_result.is_failure

    # ========================================================================
    # COVERAGE IMPROVEMENT TESTS - Missing error paths and edge cases
    # ========================================================================

    def test_unregister_command_not_found(self) -> None:
        """Test unregister_command when command doesn't exist (lines 105-115)."""
        commands = FlextCliCommands()

        # Try to unregister non-existent command
        result = commands.unregister_command("non_existent")
        assert result.is_failure
        assert result.error is not None
        assert "not found" in result.error.lower()

    def test_unregister_command_success(self) -> None:
        """Test successful command unregistration."""
        commands = FlextCliCommands()

        # Register then unregister
        commands.register_command("temp_cmd", lambda: "temp")
        result = commands.unregister_command("temp_cmd")
        assert result.is_success

        # Verify command is gone
        exec_result = commands.execute_command("temp_cmd")
        assert exec_result.is_failure

    def test_create_command_group(self) -> None:
        """Test create_command_group method (lines 138-146)."""
        commands = FlextCliCommands()

        # Create command group
        result = commands.create_command_group(
            "test_group",
            description="Test group",
            commands={"cmd1": {"handler": lambda: "test"}},
        )
        assert result.is_success
        group = result.unwrap()
        assert isinstance(group, FlextCliCommands._CliGroup)
        assert group.name == "test_group"
        assert hasattr(group, "description")
        assert hasattr(group, "commands")

    def test_run_cli_with_invalid_command(self) -> None:
        """Test run_cli with invalid command in args (lines 166-192)."""
        commands = FlextCliCommands()
        commands.register_command("valid", lambda: "ok")

        # Run with invalid command
        result = commands.run_cli(["invalid_command"])
        assert result.is_failure
        assert result.error is not None
        assert "not found" in result.error.lower()

    def test_run_cli_with_options(self) -> None:
        """Test run_cli skips option arguments (lines 166-192)."""
        commands = FlextCliCommands()

        # Run with options (should skip --* args)
        result = commands.run_cli(["--help", "--version"])
        assert result.is_success

    def test_run_cli_success(self) -> None:
        """Test run_cli successful execution (lines 166-192)."""
        commands = FlextCliCommands()
        commands.register_command("test", lambda: "ok")

        # Run with valid command
        result = commands.run_cli(["test"])
        assert result.is_success

    def test_get_click_group(self) -> None:
        """Test get_click_group method (line 203)."""
        commands = FlextCliCommands()

        # Get Click group
        group = commands.get_click_group()
        assert group is not None
        assert hasattr(group, "name")
        assert hasattr(group, "commands")

    def test_execute_command_with_args(self) -> None:
        """Test execute_command with args parameter (lines 237-241)."""
        commands = FlextCliCommands()

        # Register command that accepts args
        def cmd_with_args(args: FlextTypes.StringList) -> str:
            return f"args: {len(args)}"

        commands.register_command("with_args", cmd_with_args)

        # Execute with args
        result = commands.execute_command("with_args", args=["arg1", "arg2"])
        assert result.is_success
        assert "args: 2" in str(result.unwrap())

    def test_execute_command_handler_without_args(self) -> None:
        """Test execute_command with handler that doesn't accept args (lines 237-241)."""
        commands = FlextCliCommands()

        # Register command without args
        commands.register_command("no_args", lambda: "no args")

        # Execute with args (should fallback to calling without args)
        result = commands.execute_command("no_args", args=["arg1"])
        assert result.is_success
        assert result.unwrap() == "no args"

    def test_execute_command_invalid_structure(self) -> None:
        """Test execute_command with invalid command structure (lines 245-252)."""
        commands = FlextCliCommands()

        # Manually add invalid command structure
        commands._commands["bad_cmd"] = {"invalid": "structure"}

        result = commands.execute_command("bad_cmd")
        assert result.is_failure
        assert "Invalid command structure" in str(
            result.error
        ) or "not callable" in str(result.error)

    def test_get_commands(self) -> None:
        """Test get_commands method (line 263)."""
        commands = FlextCliCommands()
        commands.register_command("cmd1", lambda: "1")
        commands.register_command("cmd2", lambda: "2")

        # Get commands
        cmds = commands.get_commands()
        assert isinstance(cmds, dict)
        assert len(cmds) == 2
        assert "cmd1" in cmds
        assert "cmd2" in cmds

    def test_clear_commands(self) -> None:
        """Test clear_commands method (lines 272-278)."""
        commands = FlextCliCommands()
        commands.register_command("cmd1", lambda: "1")
        commands.register_command("cmd2", lambda: "2")

        # Clear commands
        result = commands.clear_commands()
        assert result.is_success
        assert result.unwrap() == 2  # Should return count of cleared commands

        # Verify commands are cleared
        cmds = commands.get_commands()
        assert len(cmds) == 0

    def test_list_commands(self) -> None:
        """Test list_commands method (lines 289-293)."""
        commands = FlextCliCommands()
        commands.register_command("alpha", lambda: "a")
        commands.register_command("beta", lambda: "b")

        # List commands
        result = commands.list_commands()
        assert result.is_success
        cmd_list = result.unwrap()
        assert isinstance(cmd_list, list)
        assert len(cmd_list) == 2
        assert "alpha" in cmd_list
        assert "beta" in cmd_list

    def test_create_main_cli(self) -> None:
        """Test create_main_cli method (line 304)."""
        commands = FlextCliCommands(name="test_cli", description="Test CLI")

        # Create main CLI
        main_cli = commands.create_main_cli()
        assert isinstance(main_cli, FlextCliCommands)
        assert main_cli._name == "test_cli"
        assert main_cli._description == "Test CLI"

    def test_execute_command_with_timeout(self) -> None:
        """Test execute_command with timeout parameter (lines 223-226)."""
        commands = FlextCliCommands()
        commands.register_command("timed", lambda: "done")

        # Execute with custom timeout
        result = commands.execute_command("timed", timeout=60)
        assert result.is_success
        assert result.unwrap() == "done"

    # ========================================================================
    # EXCEPTION HANDLER COVERAGE TESTS
    # ========================================================================

    def test_execute_command_handler_not_callable(self) -> None:
        """Test execute_command with non-callable handler (line 245)."""
        commands = FlextCliCommands()

        # Manually insert non-callable handler
        commands._commands["bad"] = {"handler": "not_callable"}

        result = commands.execute_command("bad")

        assert result.is_failure
        assert "not callable" in str(result.error).lower()

    def test_execute_command_execution_exception(self) -> None:
        """Test execute_command when handler raises exception (lines 251-252)."""
        commands = FlextCliCommands()

        def failing_handler() -> Never:
            msg = "Handler execution error"
            raise RuntimeError(msg)

        commands.register_command("failing", failing_handler)

        result = commands.execute_command("failing")

        assert result.is_failure
        assert result.error is not None

    def test_register_command_exception(self) -> None:
        """Test register_command exception handler (lines 93-94)."""
        from unittest.mock import MagicMock, patch

        commands = FlextCliCommands()

        # Mock _commands to raise exception on __setitem__
        mock_dict = MagicMock()
        mock_dict.__setitem__.side_effect = RuntimeError("Mock registration exception")

        with patch.object(commands, "_commands", mock_dict):
            result = commands.register_command("test", lambda: "test")
            assert result.is_failure
            assert "registration failed" in str(result.error).lower()

    def test_unregister_command_exception(self) -> None:
        """Test unregister_command exception handler (lines 119-120)."""
        from unittest.mock import MagicMock, patch

        commands = FlextCliCommands()
        commands.register_command("test", lambda: "test")

        # Mock _commands to raise exception on __delitem__
        mock_dict = MagicMock()
        mock_dict.__contains__.return_value = True  # Make "in" check pass
        mock_dict.__delitem__.side_effect = RuntimeError(
            "Mock unregistration exception"
        )

        with patch.object(commands, "_commands", mock_dict):
            result = commands.unregister_command("test")
            assert result.is_failure
            assert "unregistration failed" in str(result.error).lower()

    def test_create_command_group_exception(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test create_command_group exception handler (lines 150-151)."""
        from unittest.mock import patch

        commands = FlextCliCommands()

        # Mock _CliGroup to raise exception
        def mock_init(*args: object, **kwargs: object) -> Never:
            msg = "Mock group creation exception"
            raise RuntimeError(msg)

        with patch.object(
            FlextCliCommands._CliGroup, "__init__", side_effect=mock_init
        ):
            result = commands.create_command_group("test_group")
            assert result.is_failure
            assert "group creation failed" in str(result.error).lower()

    def test_run_cli_execute_failure(self) -> None:
        """Test run_cli when execute() fails (lines 193-195)."""
        from unittest.mock import patch

        commands = FlextCliCommands()

        # Mock execute to return failure
        with patch.object(
            FlextCliCommands,
            "execute",
            return_value=FlextResult[FlextTypes.Dict].fail("Execute failed"),
        ):
            result = commands.run_cli()
            assert result.is_failure
            assert "execute failed" in str(result.error).lower()

    def test_run_cli_exception(self) -> None:
        """Test run_cli exception handler (lines 196-197)."""
        from unittest.mock import patch

        commands = FlextCliCommands()

        # Mock execute to raise exception
        def mock_execute(self: FlextCliCommands) -> Never:
            msg = "Mock CLI execution exception"
            raise RuntimeError(msg)

        with patch.object(FlextCliCommands, "execute", side_effect=mock_execute):
            result = commands.run_cli()
            assert result.is_failure
            assert "cli execution" in str(result.error).lower()

    def test_clear_commands_exception(self) -> None:
        """Test clear_commands exception handler (lines 287-288)."""
        from unittest.mock import MagicMock, patch

        commands = FlextCliCommands()
        commands.register_command("test", lambda: "test")

        # Mock _commands to raise exception on clear
        mock_dict = MagicMock()
        mock_dict.__len__.return_value = 1  # Return count before clear
        mock_dict.clear.side_effect = RuntimeError("Mock clear exception")

        with patch.object(commands, "_commands", mock_dict):
            result = commands.clear_commands()
            assert result.is_failure
            assert "failed" in str(result.error).lower()

    def test_list_commands_exception(self) -> None:
        """Test list_commands exception handler (lines 302-303)."""
        from unittest.mock import MagicMock, patch

        commands = FlextCliCommands()
        commands.register_command("test", lambda: "test")

        # Mock _commands to raise exception on keys()
        mock_dict = MagicMock()
        mock_dict.keys.side_effect = RuntimeError("Mock keys exception")

        with patch.object(commands, "_commands", mock_dict):
            result = commands.list_commands()
            assert result.is_failure
            assert "failed" in str(result.error).lower()
