"""Additional unit tests for FlextCliCommands to increase coverage.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli.commands import FlextCliCommands, create_main_cli


class TestFlextCliCommandsCoverage:
    """Additional coverage tests for FlextCliCommands."""

    def test_initialization(self) -> None:
        """Test FlextCliCommands initialization."""
        cli = FlextCliCommands(name="test-cli", description="Test CLI")
        assert cli._name == "test-cli"
        assert cli._description == "Test CLI"
        assert isinstance(cli._commands, dict)
        assert len(cli._commands) == 0

    def test_execute_method(self) -> None:
        """Test execute method returns operational status."""
        cli = FlextCliCommands()
        result = cli.execute()

        assert result.is_success
        data = result.unwrap()
        assert data["status"] == "operational"
        assert data["service"] == "flext-cli"
        assert isinstance(data["commands"], list)

    def test_register_command_success(self) -> None:
        """Test registering a command successfully."""
        cli = FlextCliCommands()

        def test_handler() -> str:
            return "test"

        result = cli.register_command("test", test_handler, "Test command")

        assert result.is_success
        assert "test" in cli._commands
        assert cli._commands["test"]["name"] == "test"
        assert cli._commands["test"]["handler"] == test_handler
        assert cli._commands["test"]["description"] == "Test command"

    def test_register_command_exception(self) -> None:
        """Test register_command with exception."""
        cli = FlextCliCommands()

        # Force exception by making _commands None
        cli._commands = None  # type: ignore[assignment]

        result = cli.register_command("test", lambda: "test", "Test")
        assert result.is_failure
        assert "Command registration failed" in result.error

    def test_register_command_group_success(self) -> None:
        """Test registering a command group successfully."""
        cli = FlextCliCommands()

        commands = {"cmd1": {"handler": lambda: "test"}}
        result = cli.register_command_group("group", commands, "Test group")

        assert result.is_success
        assert "group" in cli._commands
        assert cli._commands["group"]["is_group"] is True

    def test_register_command_group_exception(self) -> None:
        """Test register_command_group with exception."""
        cli = FlextCliCommands()

        # Force exception by making _commands None
        cli._commands = None  # type: ignore[assignment]

        result = cli.register_command_group("group", {}, "Test")
        assert result.is_failure
        assert "Command group registration failed" in result.error

    def test_add_command_with_none_handler(self) -> None:
        """Test add_command with None handler."""
        cli = FlextCliCommands()

        result = cli.add_command("test", None, "Test command")  # type: ignore[arg-type]

        assert result.is_failure
        assert "not callable" in result.error

    def test_add_command_with_empty_name(self) -> None:
        """Test add_command with empty name."""
        cli = FlextCliCommands()

        result = cli.add_command("", lambda: "test", "Test command")

        assert result.is_failure
        assert "name cannot be empty" in result.error

    def test_add_command_with_whitespace_name(self) -> None:
        """Test add_command with whitespace-only name."""
        cli = FlextCliCommands()

        result = cli.add_command("   ", lambda: "test", "Test command")

        assert result.is_failure
        assert "name cannot be empty" in result.error

    def test_add_command_with_click_options(self) -> None:
        """Test add_command with click options."""
        cli = FlextCliCommands()

        def test_handler() -> str:
            return "test"

        result = cli.add_command(
            "test",
            test_handler,
            "Test command",
            click_options={"help": "Test help", "no_args_is_help": True},
        )

        assert result.is_success

    def test_add_group_success(self) -> None:
        """Test add_group successfully."""
        cli = FlextCliCommands()

        result = cli.add_group("test-group", "Test group description")

        assert result.is_success
        group = result.unwrap()
        assert hasattr(group, "name")
        assert group.name == "test-group"  # type: ignore[attr-defined]
        assert hasattr(group, "description")
        assert group.description == "Test group description"  # type: ignore[attr-defined]

    def test_add_group_exception(self) -> None:
        """Test add_group with exception."""
        cli = FlextCliCommands()

        # Force exception by making _commands None
        cli._commands = None  # type: ignore[assignment]

        result = cli.add_group("test-group", "Test")
        assert result.is_failure
        assert "Group creation failed" in result.error

    def test_run_cli_with_invalid_command(self) -> None:
        """Test run_cli with invalid command argument."""
        cli = FlextCliCommands()

        result = cli.run_cli(args=["nonexistent-command"])

        assert result.is_failure
        assert "Command not found" in result.error

    def test_run_cli_with_options(self) -> None:
        """Test run_cli with option arguments."""
        cli = FlextCliCommands()

        result = cli.run_cli(args=["--help"])

        # Options should be skipped, so execution succeeds
        assert result.is_success

    def test_run_cli_standalone_mode(self) -> None:
        """Test run_cli with standalone_mode parameter."""
        cli = FlextCliCommands()

        result = cli.run_cli(args=None, standalone_mode=False)

        assert result.is_success

    def test_run_cli_exception(self) -> None:
        """Test run_cli with exception."""
        cli = FlextCliCommands()

        # Force exception by breaking execute method
        cli._commands = None  # type: ignore[assignment]

        result = cli.run_cli()
        assert result.is_failure
        assert "CLI execution failed" in result.error

    def test_get_click_group(self) -> None:
        """Test get_click_group returns cli group object."""
        cli = FlextCliCommands(name="test-cli")

        group = cli.get_click_group()

        assert group is not None
        assert hasattr(group, "name")
        assert group.name == "test-cli"  # type: ignore[attr-defined]

    def test_execute_command_success(self) -> None:
        """Test execute_command successfully."""
        cli = FlextCliCommands()

        def test_handler() -> str:
            return "result"

        cli.register_command("test", test_handler)

        result = cli.execute_command("test")

        assert result.is_success
        assert result.unwrap() == "result"

    def test_execute_command_not_found(self) -> None:
        """Test execute_command with non-existent command."""
        cli = FlextCliCommands()

        result = cli.execute_command("nonexistent")

        assert result.is_failure
        assert "Command not found" in result.error

    def test_execute_command_not_callable(self) -> None:
        """Test execute_command with non-callable handler."""
        cli = FlextCliCommands()

        cli._commands["test"] = {"name": "test", "handler": "not_callable"}

        result = cli.execute_command("test")

        assert result.is_failure
        assert "not callable" in result.error

    def test_execute_command_invalid_structure(self) -> None:
        """Test execute_command with invalid command structure."""
        cli = FlextCliCommands()

        cli._commands["test"] = "invalid_structure"

        result = cli.execute_command("test")

        assert result.is_failure
        assert "Invalid command structure" in result.error

    def test_execute_command_with_args(self) -> None:
        """Test execute_command with arguments."""
        cli = FlextCliCommands()

        def test_handler() -> str:
            return "result"

        cli.register_command("test", test_handler)

        result = cli.execute_command("test", args=["arg1", "arg2"])

        assert result.is_success

    def test_execute_command_exception(self) -> None:
        """Test execute_command with exception."""
        cli = FlextCliCommands()

        def failing_handler() -> str:
            error_msg = "Test error"
            raise ValueError(error_msg)

        cli.register_command("test", failing_handler)

        result = cli.execute_command("test")

        assert result.is_failure
        assert "Command execution failed" in result.error

    def test_list_commands_success(self) -> None:
        """Test list_commands successfully."""
        cli = FlextCliCommands()

        cli.register_command("cmd1", lambda: "1")
        cli.register_command("cmd2", lambda: "2")

        result = cli.list_commands()

        assert result.is_success
        commands = result.unwrap()
        assert "cmd1" in commands
        assert "cmd2" in commands
        assert len(commands) == 2

    def test_list_commands_empty(self) -> None:
        """Test list_commands with no commands."""
        cli = FlextCliCommands()

        result = cli.list_commands()

        assert result.is_success
        assert len(result.unwrap()) == 0

    def test_list_commands_exception(self) -> None:
        """Test list_commands with exception."""
        cli = FlextCliCommands()

        # Force exception by making _commands None
        cli._commands = None  # type: ignore[assignment]

        result = cli.list_commands()

        assert result.is_failure
        assert "Failed to list commands" in result.error

    def test_create_main_cli(self) -> None:
        """Test create_main_cli factory function."""
        cli = create_main_cli()

        assert isinstance(cli, FlextCliCommands)
        assert cli._name == "flext"
        assert "FLEXT Enterprise" in cli._description
