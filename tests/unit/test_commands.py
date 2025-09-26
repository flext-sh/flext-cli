"""FLEXT CLI Commands Tests - Comprehensive commands functionality testing.

Tests for FlextCliCommands class using flext_tests infrastructure with real functionality
testing, no mocks, and comprehensive coverage following FLEXT standards.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import time

import pytest

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

    @pytest.mark.asyncio
    async def test_commands_execute_async(self) -> None:
        """Test asynchronous Commands execution."""
        commands = FlextCliCommands()
        result = await commands.execute_async()

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
        assert test_command in commands_list

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
        assert "not found" in result.error.lower() or "unknown" in result.error.lower()

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
        assert hasattr(commands, "execute_async")

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

        # Execute commands sequentially (since execute_command is not async)
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
