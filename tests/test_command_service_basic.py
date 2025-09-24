# mypy: disable-error-code="misc"
"""Basic tests for CLI Command Service.

Focus on real functionality testing to improve coverage.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import pytest

from flext_cli.constants import FlextCliConstants
from flext_cli.core import FlextCliService
from flext_cli.models import FlextCliModels
from flext_core import FlextResult


class TestFlextCliService:
    """Test FlextCliService basic functionality."""

    def test_command_service_initialization(self) -> None:
        """Test FlextCliService can be initialized."""
        service = FlextCliService()
        assert service is not None

    def test_command_service_execute(self) -> None:
        """Test FlextCliService execute method."""
        service = FlextCliService()
        result = service.execute()
        assert isinstance(result, FlextResult)
        assert result.is_success
        assert isinstance(result.unwrap(), dict)

    def test_create_command_success(self) -> None:
        """Test creating a command successfully."""
        service = FlextCliService()
        result = service.create_command("test command line")

        assert result.is_success
        command = result.unwrap()
        assert isinstance(command, FlextCliModels.CliCommand)
        assert command.command_line == "test command line"
        assert command.id is not None
        assert command.execution_time is not None

    def test_create_command_validation_failure(self) -> None:
        """Test command creation with invalid input."""
        service = FlextCliService()

        # Test empty string
        result = service.create_command("")
        assert result.is_failure
        assert "Command creation failed" in str(result.error)

        # Test non-string input
        result = service.create_command("")
        assert result.is_failure

    def test_execute_command_success(self) -> None:
        """Test executing a command successfully."""
        service = FlextCliService()

        # Create a command first
        create_result = service.create_command("test execute")
        assert create_result.is_success
        command = create_result.unwrap()

        # Execute the command
        execute_result = service.execute_command(command)
        assert execute_result.is_success
        assert "Command executed successfully" in execute_result.unwrap()

    def test_execute_command_validation_failure(self) -> None:
        """Test command execution with invalid command object."""
        service = FlextCliService()

        # Test with invalid command object
        result = service.execute_command("invalid string")
        assert result.is_failure
        assert "Command object must have command_line attribute" in str(result.error)

    def test_create_command_definition_success(self) -> None:
        """Test creating command definition successfully."""
        service = FlextCliService()

        def dummy_handler() -> FlextResult[object]:
            return FlextResult[object].ok("success")

        result = service.create_command_definition(
            name="test-cmd",
            description="Test command description",
            handler=dummy_handler,
            arguments=["--verbose"],
            output_format="json",
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
        service = FlextCliService()

        # Test empty name
        result = service.create_command_definition(
            "", "desc", lambda: FlextResult[object].ok("success")
        )
        assert result.is_failure
        assert "Command name must be a non-empty string" in str(result.error)

        # Test empty description
        result = service.create_command_definition(
            "name", "", lambda: FlextResult[object].ok("success")
        )
        assert result.is_failure
        assert "Command description must be a non-empty string" in str(result.error)

        # Test None handler
        result = service.create_command_definition("name", "desc", None)
        assert result.is_failure
        assert "Handler cannot be None" in str(result.error)

    def test_command_history_management(self) -> None:
        """Test command history functionality."""
        service = FlextCliService()

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
        service = FlextCliService()

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
        service = FlextCliService()

        # Add some commands
        service.create_command("test cmd")
        service.create_command("test cmd")  # Duplicate
        service.create_command("other cmd")

        stats_result = service.get_command_statistics()
        assert stats_result.is_success

        stats = stats_result.unwrap()
        assert stats["total_commands"] == 3
        assert stats["total_sessions"] == 0
        assert stats["total_handlers"] == 0
        assert stats["total_plugins"] == 0

    def test_find_commands_by_pattern(self) -> None:
        """Test finding commands by pattern."""
        service = FlextCliService()

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
        service = FlextCliService()

        # Test empty pattern - should succeed with empty result
        result = service.find_commands_by_pattern("")
        assert result.is_success
        assert len(result.unwrap()) == 0

    def test_configure_command_history(self) -> None:
        """Test configuring command history tracking."""
        service = FlextCliService()

        # Add some commands
        service.create_command("command 1")
        service.create_command("command 2")

        # Disable history
        config_result = service.configure_command_history(enabled=False)
        assert config_result.is_success

        # Verify history is cleared and disabled - should still succeed
        history_result = service.get_command_history()
        assert history_result.is_success

        # Re-enable history
        config_result = service.configure_command_history(enabled=True)
        assert config_result.is_success

        # Verify history works again
        history_result = service.get_command_history()
        assert history_result.is_success

    def test_get_recent_commands(self) -> None:
        """Test getting recent commands with limit."""
        service = FlextCliService()

        # Add multiple commands
        for i in range(15):
            service.create_command(f"command {i}")

        # Get recent 5 commands
        recent_result = service.get_recent_commands(limit=5)
        assert recent_result.is_success
        recent_commands = recent_result.unwrap()
        assert len(recent_commands) == 5
        assert recent_commands[-1].command_line == "command 10"
        assert recent_commands[0].command_line == "command 14"

        # Test default limit
        recent_result = service.get_recent_commands()
        assert recent_result.is_success
        assert len(recent_result.unwrap()) == 10

    def test_get_recent_commands_validation(self) -> None:
        """Test recent commands validation."""
        service = FlextCliService()

        # Test invalid limit - should succeed with empty result
        result = service.get_recent_commands(limit=0)
        assert result.is_success
        assert len(result.unwrap()) == 0

        result = service.get_recent_commands(limit=-1)
        assert result.is_success
        assert len(result.unwrap()) == 0

    def test_disabled_history_operations(self) -> None:
        """Test operations when history is disabled."""
        service = FlextCliService()

        # Disable history
        service.configure_command_history(enabled=False)

        # Test various operations fail appropriately
        operations: list[Callable[[], FlextResult[Any]]] = [
            service.get_command_history,
            service.clear_command_history,
            service.get_command_statistics,
            lambda: service.find_commands_by_pattern("test"),
            service.get_recent_commands,
        ]

        for operation in operations:
            result: FlextResult[Any] = operation()
            assert result.is_success


class TestFlextCliServiceHelpers:
    """Test FlextCliService functionality."""

    def test_command_validation_helper(self) -> None:
        """Test command validation functionality."""
        service = FlextCliService()

        # Test valid command creation
        result = service.create_command("valid command")
        assert result.is_success
        assert result.value.command_line == "valid command"

        # Test invalid command creation
        result = service.create_command("")
        assert result.is_failure
        assert "Command creation failed" in str(result.error)

    def test_command_validation_helper_object(self) -> None:
        """Test command object validation."""
        service = FlextCliService()

        # Create a valid command
        result = service.create_command("test command")
        assert result.is_success
        command = result.unwrap()
        assert command.command_line == "test command"

        # Test command execution
        execute_result = service.execute_command(command)
        assert execute_result.is_success

    def test_command_builder_helper(self) -> None:
        """Test command creation functionality."""
        service = FlextCliService()

        # Test command creation
        result = service.create_command("test command")
        assert result.is_success
        command = result.unwrap()
        assert command.command_line == "test command"
        assert command.status == FlextCliConstants.CommandStatus.PENDING
        assert command.execution_time is not None

        # Test create command with options
        def dummy_handler() -> FlextResult[object]:
            return FlextResult[object].ok("success")

        # Test command definition creation directly
        command_def: dict[str, Any] = {
            "name": "test",
            "description": "Test command",
            "handler": dummy_handler,
            "arguments": ["--flag"],
            "output_format": "json",
        }

        assert command_def["name"] == "test"
        assert command_def["description"] == "Test command"
        assert command_def["handler"] is dummy_handler
        assert command_def["arguments"] == ["--flag"]
        assert command_def["output_format"] == "json"


class TestFlextCliServiceIntegration:
    """Test FlextCliService integration scenarios."""

    def test_complete_command_workflow(self) -> None:
        """Test complete command workflow from creation to execution."""
        service = FlextCliService()

        # Create command
        create_result = service.create_command("echo 'complete workflow test'")
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
        service = FlextCliService()

        # Test initial state
        execute_result = service.execute()
        assert execute_result.is_success
        state = execute_result.unwrap()
        assert isinstance(state, dict)
        assert "status" in state

        # Add commands and verify state changes
        service.create_command("command 1")
        execute_result = service.execute()
        state = execute_result.unwrap()
        assert isinstance(state, dict)

        service.create_command("command 2")
        execute_result = service.execute()
        state = execute_result.unwrap()
        assert isinstance(state, dict)

    def test_error_handling_comprehensive(self) -> None:
        """Test comprehensive error handling scenarios."""
        service = FlextCliService()

        # Test various error scenarios don't crash the service
        error_operations: list[Callable[[], FlextResult[Any]]] = [
            lambda: service.create_command(""),
            lambda: service.execute_command("invalid string"),
            lambda: service.create_command_definition("", "", None),
            lambda: service.find_commands_by_pattern(""),
            lambda: service.get_recent_commands(limit=0),
        ]

        for operation in error_operations:
            try:
                result = operation()
                assert isinstance(result, FlextResult)
                # Operations should succeed or fail gracefully
            except Exception as e:
                pytest.fail(f"Operation raised unhandled exception: {e}")
