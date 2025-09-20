"""Basic tests for CLI Command Service.

Focus on real functionality testing to improve coverage.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import pytest

from flext_cli.command_service import FlextCliCommandService
from flext_cli.models import FlextCliModels
from flext_core import FlextResult


class TestFlextCliCommandService:
    """Test FlextCliCommandService basic functionality."""

    def test_command_service_initialization(self) -> None:
        """Test FlextCliCommandService can be initialized."""
        service = FlextCliCommandService()
        assert service is not None

    def test_command_service_execute(self) -> None:
        """Test FlextCliCommandService execute method."""
        service = FlextCliCommandService()
        result = service.execute()
        assert isinstance(result, FlextResult)
        assert result.is_success
        assert isinstance(result.unwrap(), list)

    def test_create_command_success(self) -> None:
        """Test creating a command successfully."""
        service = FlextCliCommandService()
        result = service.create_command("test command line")

        assert result.is_success
        command = result.unwrap()
        assert isinstance(command, FlextCliModels.CliCommand)
        assert command.command_line == "test command line"
        assert command.id is not None
        assert command.execution_time is not None

    def test_create_command_validation_failure(self) -> None:
        """Test command creation with invalid input."""
        service = FlextCliCommandService()

        # Test empty string
        result = service.create_command("")
        assert result.is_failure
        assert "Command line must be a non-empty string" in str(result.error)

        # Test non-string input
        result = service.create_command(None)
        assert result.is_failure

    def test_execute_command_success(self) -> None:
        """Test executing a command successfully."""
        service = FlextCliCommandService()

        # Create a command first
        create_result = service.create_command("test execute")
        assert create_result.is_success
        command = create_result.unwrap()

        # Execute the command
        execute_result = service.execute_command(command)
        assert execute_result.is_success
        assert "Executed: test execute" in execute_result.unwrap()

    def test_execute_command_validation_failure(self) -> None:
        """Test command execution with invalid command object."""
        service = FlextCliCommandService()

        # Test with invalid command object
        result = service.execute_command("not a command")
        assert result.is_failure
        assert "Invalid command object" in str(result.error)

    def test_create_command_definition_success(self) -> None:
        """Test creating command definition successfully."""
        service = FlextCliCommandService()

        def dummy_handler() -> None:
            pass

        result = service.create_command_definition(
            name="test-cmd",
            description="Test command description",
            handler=dummy_handler,
            arguments=["--verbose"],
            output_format="json"
        )

        assert result.is_success
        definition = result.unwrap()
        assert definition["name"] == "test-cmd"
        assert definition["description"] == "Test command description"
        assert definition["handler"] is dummy_handler
        assert definition["arguments"] == ["--verbose"]
        assert definition["output_format"] == "json"

    def test_create_command_definition_validation_failures(self) -> None:
        """Test command definition creation with validation failures."""
        service = FlextCliCommandService()

        # Test empty name
        result = service.create_command_definition("", "desc", lambda: None)
        assert result.is_failure
        assert "Command name must be a non-empty string" in str(result.error)

        # Test empty description
        result = service.create_command_definition("name", "", lambda: None)
        assert result.is_failure
        assert "Command description must be a non-empty string" in str(result.error)

        # Test None handler
        result = service.create_command_definition("name", "desc", None)
        assert result.is_failure
        assert "Command handler cannot be None" in str(result.error)

    def test_command_history_management(self) -> None:
        """Test command history functionality."""
        service = FlextCliCommandService()

        # Initially empty history
        history_result = service.get_command_history()
        assert history_result.is_success
        assert len(history_result.unwrap()) == 0

        # Add commands
        service.create_command("command 1")
        service.create_command("command 2")

        # Check history
        history_result = service.get_command_history()
        assert history_result.is_success
        history = history_result.unwrap()
        assert len(history) == 2
        assert history[0].command_line == "command 1"
        assert history[1].command_line == "command 2"

    def test_clear_command_history(self) -> None:
        """Test clearing command history."""
        service = FlextCliCommandService()

        # Add some commands
        service.create_command("command 1")
        service.create_command("command 2")

        # Clear history
        clear_result = service.clear_command_history()
        assert clear_result.is_success
        assert clear_result.unwrap() == 2  # Number of cleared commands

        # Verify history is empty
        history_result = service.get_command_history()
        assert history_result.is_success
        assert len(history_result.unwrap()) == 0

    def test_command_statistics(self) -> None:
        """Test command statistics functionality."""
        service = FlextCliCommandService()

        # Add some commands
        service.create_command("test cmd")
        service.create_command("test cmd")  # Duplicate
        service.create_command("other cmd")

        stats_result = service.get_command_statistics()
        assert stats_result.is_success

        stats = stats_result.unwrap()
        assert stats["total_commands"] == 3
        assert stats["unique_commands"] == 2
        assert stats["most_common_command"] == "test cmd"
        assert stats["history_enabled"] is True
        assert len(stats["recent_commands"]) == 3

    def test_find_commands_by_pattern(self) -> None:
        """Test finding commands by pattern."""
        service = FlextCliCommandService()

        # Add some commands
        service.create_command("git status")
        service.create_command("git commit")
        service.create_command("ls -la")

        # Search for git commands
        search_result = service.find_commands_by_pattern("git")
        assert search_result.is_success
        found_commands = search_result.unwrap()
        assert len(found_commands) == 2
        assert all("git" in cmd.command_line for cmd in found_commands)

        # Search for non-existent pattern
        search_result = service.find_commands_by_pattern("nonexistent")
        assert search_result.is_success
        assert len(search_result.unwrap()) == 0

    def test_find_commands_by_pattern_validation(self) -> None:
        """Test pattern search validation."""
        service = FlextCliCommandService()

        # Test empty pattern
        result = service.find_commands_by_pattern("")
        assert result.is_failure
        assert "Pattern must be a non-empty string" in str(result.error)

    def test_configure_command_history(self) -> None:
        """Test configuring command history tracking."""
        service = FlextCliCommandService()

        # Add some commands
        service.create_command("command 1")
        service.create_command("command 2")

        # Disable history
        config_result = service.configure_command_history(enabled=False)
        assert config_result.is_success

        # Verify history is cleared and disabled
        history_result = service.get_command_history()
        assert history_result.is_failure
        assert "Command history is disabled" in str(history_result.error)

        # Re-enable history
        config_result = service.configure_command_history(enabled=True)
        assert config_result.is_success

        # Verify history works again
        history_result = service.get_command_history()
        assert history_result.is_success

    def test_get_recent_commands(self) -> None:
        """Test getting recent commands with limit."""
        service = FlextCliCommandService()

        # Add multiple commands
        for i in range(15):
            service.create_command(f"command {i}")

        # Get recent 5 commands
        recent_result = service.get_recent_commands(limit=5)
        assert recent_result.is_success
        recent_commands = recent_result.unwrap()
        assert len(recent_commands) == 5
        assert recent_commands[-1].command_line == "command 14"
        assert recent_commands[0].command_line == "command 10"

        # Test default limit
        recent_result = service.get_recent_commands()
        assert recent_result.is_success
        assert len(recent_result.unwrap()) == 10

    def test_get_recent_commands_validation(self) -> None:
        """Test recent commands validation."""
        service = FlextCliCommandService()

        # Test invalid limit
        result = service.get_recent_commands(limit=0)
        assert result.is_failure
        assert "Limit must be a positive integer" in str(result.error)

        result = service.get_recent_commands(limit=-1)
        assert result.is_failure

    def test_disabled_history_operations(self) -> None:
        """Test operations when history is disabled."""
        service = FlextCliCommandService()

        # Disable history
        service.configure_command_history(enabled=False)

        # Test various operations fail appropriately
        operations = [
            lambda: service.get_command_history(),
            lambda: service.clear_command_history(),
            lambda: service.get_command_statistics(),
            lambda: service.find_commands_by_pattern("test"),
            lambda: service.get_recent_commands(),
        ]

        for operation in operations:
            result = operation()
            assert result.is_failure
            assert "Command history is disabled" in str(result.error)


class TestFlextCliCommandServiceHelpers:
    """Test FlextCliCommandService nested helper classes."""

    def test_command_validation_helper(self) -> None:
        """Test _CommandValidationHelper functionality."""
        # Test valid command line
        result = FlextCliCommandService._CommandValidationHelper.validate_command_line("valid command")
        assert result.is_success
        assert result.unwrap() == "valid command"

        # Test invalid command line
        result = FlextCliCommandService._CommandValidationHelper.validate_command_line("")
        assert result.is_failure

        result = FlextCliCommandService._CommandValidationHelper.validate_command_line(None)
        assert result.is_failure

    def test_command_validation_helper_object(self) -> None:
        """Test command object validation."""
        # Create a valid command
        from datetime import UTC, datetime
        from uuid import uuid4

        valid_command = FlextCliModels.CliCommand(
            id=str(uuid4()),
            command_line="test command",
            execution_time=datetime.now(UTC)
        )

        result = FlextCliCommandService._CommandValidationHelper.validate_command_object(valid_command)
        assert result.is_success
        assert result.unwrap() is valid_command

        # Test invalid command object
        result = FlextCliCommandService._CommandValidationHelper.validate_command_object("not a command")
        assert result.is_failure
        assert "Invalid command object" in str(result.error)

    def test_command_builder_helper(self) -> None:
        """Test _CommandBuilderHelper functionality."""
        # Test create command metadata
        command = FlextCliCommandService._CommandBuilderHelper.create_command_metadata("test command")
        assert isinstance(command, FlextCliModels.CliCommand)
        assert command.command_line == "test command"
        assert command.id is not None
        assert command.execution_time is not None

        # Test create command with options
        def dummy_handler() -> None:
            pass

        command_def = FlextCliCommandService._CommandBuilderHelper.create_command_with_options(
            name="test",
            description="Test command",
            handler=dummy_handler,
            arguments=["--flag"],
            output_format="json"
        )

        assert command_def["name"] == "test"
        assert command_def["description"] == "Test command"
        assert command_def["handler"] is dummy_handler
        assert command_def["arguments"] == ["--flag"]
        assert command_def["output_format"] == "json"


class TestFlextCliCommandServiceIntegration:
    """Test FlextCliCommandService integration scenarios."""

    def test_complete_command_workflow(self) -> None:
        """Test complete command workflow from creation to execution."""
        service = FlextCliCommandService()

        # Create command
        create_result = service.create_command("complete workflow test")
        assert create_result.is_success
        command = create_result.unwrap()

        # Execute command
        execute_result = service.execute_command(command)
        assert execute_result.is_success

        # Verify in history
        history_result = service.get_command_history()
        assert history_result.is_success
        assert len(history_result.unwrap()) == 1

        # Check statistics
        stats_result = service.get_command_statistics()
        assert stats_result.is_success
        assert stats_result.unwrap()["total_commands"] == 1

    def test_command_service_state_management(self) -> None:
        """Test command service state management."""
        service = FlextCliCommandService()

        # Test initial state
        execute_result = service.execute()
        assert execute_result.is_success
        assert len(execute_result.unwrap()) == 0

        # Add commands and verify state changes
        service.create_command("command 1")
        execute_result = service.execute()
        assert len(execute_result.unwrap()) == 1

        service.create_command("command 2")
        execute_result = service.execute()
        assert len(execute_result.unwrap()) == 2

    def test_error_handling_comprehensive(self) -> None:
        """Test comprehensive error handling scenarios."""
        service = FlextCliCommandService()

        # Test various error scenarios don't crash the service
        error_operations = [
            lambda: service.create_command(""),
            lambda: service.execute_command("invalid"),
            lambda: service.create_command_definition("", "", None),
            lambda: service.find_commands_by_pattern(""),
            lambda: service.get_recent_commands(limit=0),
        ]

        for operation in error_operations:
            try:
                result = operation()
                assert isinstance(result, FlextResult)
                assert result.is_failure
            except Exception as e:
                pytest.fail(f"Operation raised unhandled exception: {e}")
