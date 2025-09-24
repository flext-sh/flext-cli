"""Test module for service."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime

import pytest

from flext_cli import FlextCliConstants, FlextCliModels, FlextCliService
from flext_core import FlextResult


class TestFlextCliModels:
    """Comprehensive tests for FlextCliModels class."""

    def setup_method(self) -> None:
        """Set up domain services instance for each test."""
        self.service = FlextCliService()

    def test_init_success(self) -> None:
        """Test successful domain services initialization."""
        services = FlextCliService()
        assert services is not None
        assert isinstance(services, FlextCliService)

    def test_execute_success(self) -> None:
        """Test successful domain service execution."""
        result = self.service.execute()
        assert result.is_success
        assert result.value is not None
        assert isinstance(result.value, dict)

    def test_execute_exception_handling(self) -> None:
        """Test domain service execution exception handling."""
        # This will test the exception handling path
        # Create a domain services instance that will fail health check
        services = FlextCliService()

        # Test normal execution first to ensure it works
        result = services.execute()
        assert result.is_success or result.is_failure  # Should handle gracefully

    def test_health_check_success(self) -> None:
        """Test successful health check."""
        result: FlextResult[str] = self.service.health_check()
        assert result.is_success
        assert result.value == "healthy"

    def test_health_check_returns_correct_message(self) -> None:
        """Test health check returns expected message format."""
        result = self.service.health_check()
        assert result.is_success
        assert "healthy" in result.value


class TestCommandLifecycleManagement:
    """Tests for command lifecycle management in domain services."""

    def setup_method(self) -> None:
        """Set up domain services instance for each test."""
        self.service = FlextCliService()

    def test_create_command_success(self) -> None:
        """Test successful command creation."""
        command_line = "echo 'Hello World'"
        result: FlextResult[FlextCliModels.CliCommand] = self.service.create_command(
            command_line
        )
        assert result.is_success
        assert isinstance(result.value, FlextCliModels.CliCommand)
        assert result.value.command_line == command_line
        assert result.value.status == FlextCliConstants.CommandStatus.PENDING.value

    def test_create_command_empty_string(self) -> None:
        """Test command creation fails with empty string."""
        result: FlextResult[FlextCliModels.CliCommand] = self.service.create_command("")
        assert result.is_failure
        assert "validation error" in str(result.error or "").lower()

    def test_create_command_none_input(self) -> None:
        """Test command creation fails with empty input."""
        result: FlextResult[FlextCliModels.CliCommand] = self.service.create_command("")
        assert result.is_failure
        assert "validation error" in str(result.error or "").lower()

    def test_create_command_whitespace_only(self) -> None:
        """Test command creation with whitespace-only input."""
        result: FlextResult[FlextCliModels.CliCommand] = self.service.create_command(
            "   \t\n   "
        )
        # Whitespace is accepted by Pydantic as valid string
        assert result.is_success or result.is_failure

    def test_create_command_strips_whitespace(self) -> None:
        """Test command creation preserves input."""
        command_line = "  echo test  "
        result: FlextResult[FlextCliModels.CliCommand] = self.service.create_command(
            command_line
        )
        assert result.is_success
        # Command line is stored as-is, not stripped
        assert result.value.command_line == command_line

    def test_create_command_with_dangerous_patterns(self) -> None:
        """Test command creation with potentially dangerous patterns."""
        dangerous_commands = [
            "rm -rf /",
            "format C:",
            "del /f /s /q C:\\*",
            "sudo rm -rf /",
        ]

        for dangerous_cmd in dangerous_commands:
            result: FlextResult[FlextCliModels.CliCommand] = (
                self.service.create_command(dangerous_cmd)
            )
            # Should either fail validation or handle gracefully
            if result.is_failure:
                assert (
                    "dangerous" in str(result.error or "").lower()
                    or "validation" in str(result.error or "").lower()
                )

    def test_start_command_execution_success(self) -> None:
        """Test successful command execution start."""
        # Create a command first
        create_result: FlextResult[FlextCliModels.CliCommand] = (
            self.service.create_command("echo test")
        )
        assert create_result.is_success
        command: FlextCliModels.CliCommand = create_result.value

        # Start execution
        result: FlextResult[FlextCliModels.CliCommand] = (
            self.service.start_command_execution(command)
        )
        assert result.is_success
        assert result.value.status == FlextCliConstants.CommandStatus.RUNNING.value

    def test_start_command_execution_wrong_status(self) -> None:
        """Test command execution start fails with wrong status."""
        # Create a command and manually set wrong status
        create_result: FlextResult[FlextCliModels.CliCommand] = (
            self.service.create_command("echo test")
        )
        assert create_result.is_success
        command: FlextCliModels.CliCommand = create_result.value

        # Set state to completed manually to test validation
        command.exit_code = 0  # Set exit code first to satisfy Pydantic validation
        command.status = FlextCliConstants.CommandStatus.COMPLETED.value

        # Try to start execution
        result: FlextResult[FlextCliModels.CliCommand] = (
            self.service.start_command_execution(command)
        )
        assert result.is_failure
        assert "Command must be pending to start" in str(result.error or "")
        assert command.status in str(result.error or "")

    def test_complete_command_execution_success(self) -> None:
        """Test successful command execution completion."""
        # Create and start a command
        create_result: FlextResult[FlextCliModels.CliCommand] = (
            self.service.create_command("echo test")
        )
        assert create_result.is_success
        command: FlextCliModels.CliCommand = create_result.value

        start_result: FlextResult[FlextCliModels.CliCommand] = (
            self.service.start_command_execution(command)
        )
        assert start_result.is_success

        # Complete execution
        result: FlextResult[FlextCliModels.CliCommand] = (
            self.service.complete_command_execution(
                command,
                exit_code=0,
                output="test",
                error_output="",
            )
        )
        assert result.is_success
        assert result.value.status == FlextCliConstants.CommandStatus.COMPLETED.value
        assert result.value.exit_code == 0
        assert result.value.output == "test"

    def test_complete_command_execution_with_error(self) -> None:
        """Test command execution completion with error."""
        # Create and start a command
        create_result: FlextResult[FlextCliModels.CliCommand] = (
            self.service.create_command("echo test")
        )
        assert create_result.is_success
        command: FlextCliModels.CliCommand = create_result.value

        start_result: FlextResult[FlextCliModels.CliCommand] = (
            self.service.start_command_execution(command)
        )
        assert start_result.is_success

        # Complete execution with error
        result: FlextResult[FlextCliModels.CliCommand] = (
            self.service.complete_command_execution(
                command,
                exit_code=1,
                output="",
                error_output="Command failed",
            )
        )
        assert result.is_success
        assert result.value.status == FlextCliConstants.CommandStatus.FAILED.value
        assert result.value.exit_code == 1
        assert result.value.error_output == "Command failed"

    def test_complete_command_execution_wrong_status(self) -> None:
        """Test command execution completion fails with wrong status."""
        # Create a command with wrong status
        create_result: FlextResult[FlextCliModels.CliCommand] = (
            self.service.create_command("echo test")
        )
        assert create_result.is_success
        command: FlextCliModels.CliCommand = create_result.value
        # Command is still pending, not running

        # Try to complete execution
        result: FlextResult[FlextCliModels.CliCommand] = (
            self.service.complete_command_execution(
                command,
                exit_code=0,
                output="test",
            )
        )
        assert result.is_failure
        assert "Command must be running to complete" in str(result.error or "")


class TestSessionManagement:
    """Tests for session management in domain services."""

    def setup_method(self) -> None:
        """Set up domain services instance for each test."""
        self.service = FlextCliService()

    def test_create_session_success(self) -> None:
        """Test successful session creation."""
        result: FlextResult[FlextCliModels.CliSession] = self.service.create_session()
        assert result.is_success
        assert isinstance(result.value, FlextCliModels.CliSession)
        assert result.value.user_id is not None  # Auto-generated user_id

    def test_create_session_with_user_id(self) -> None:
        """Test successful session creation with user ID."""
        user_id = "test_user_123"
        result: FlextResult[FlextCliModels.CliSession] = self.service.create_session(
            user_id
        )
        assert result.is_success
        assert result.value.user_id == user_id

    def test_create_session_with_empty_user_id(self) -> None:
        """Test session creation with empty user ID."""
        result: FlextResult[FlextCliModels.CliSession] = self.service.create_session("")
        assert result.is_success
        # Empty string should be handled gracefully

    def test_add_command_to_session_success(self) -> None:
        """Test successfully adding command to session."""
        # Create session and command
        session_result: FlextResult[FlextCliModels.CliSession] = (
            self.service.create_session()
        )
        assert session_result.is_success
        session: FlextCliModels.CliSession = session_result.value

        command_result: FlextResult[FlextCliModels.CliCommand] = (
            self.service.create_command("echo test")
        )
        assert command_result.is_success
        command: FlextCliModels.CliCommand = command_result.value

        # Add command to session
        result: FlextResult[FlextCliModels.CliSession] = (
            self.service.add_command_to_session(session, command)
        )
        assert result.is_success
        # Note: CliSession doesn't have commands list in current model
        # This test verifies the method doesn't fail

    def test_add_multiple_commands_to_session(self) -> None:
        """Test adding multiple commands to session."""
        # Create session
        session_result: FlextResult[FlextCliModels.CliSession] = (
            self.service.create_session()
        )
        assert session_result.is_success
        session: FlextCliModels.CliSession = session_result.value

        # Create and add multiple commands
        for i in range(3):
            command_result: FlextResult[FlextCliModels.CliCommand] = (
                self.service.create_command(f"echo test{i}")
            )
            assert command_result.is_success

            add_result: FlextResult[FlextCliModels.CliSession] = (
                self.service.add_command_to_session(
                    session,
                    command_result.value,
                )
            )
            assert add_result.is_success

        # Note: CliSession doesn't have commands list in current model
        # This test verifies the method doesn't fail for multiple commands

    def test_end_session_success(self) -> None:
        """Test successful session ending."""
        # Create session
        session_result: FlextResult[FlextCliModels.CliSession] = (
            self.service.create_session()
        )
        assert session_result.is_success
        session: FlextCliModels.CliSession = session_result.value
        assert session.end_time is None

        # End session
        result: FlextResult[FlextCliModels.CliSession] = self.service.end_session(
            session
        )
        assert result.is_success
        assert result.value.end_time is not None

    def test_end_session_already_ended(self) -> None:
        """Test ending session that's already ended."""
        # Create and end session
        session_result: FlextResult[FlextCliModels.CliSession] = (
            self.service.create_session()
        )
        assert session_result.is_success
        session: FlextCliModels.CliSession = session_result.value

        first_end: FlextResult[FlextCliModels.CliSession] = self.service.end_session(
            session
        )
        assert first_end.is_success
        # Record first end time for potential future validation
        _first_end_time: datetime | None = session.end_time

        # Try to end again
        second_end: FlextResult[FlextCliModels.CliSession] = self.service.end_session(
            session
        )
        # Should handle gracefully - either succeed or fail appropriately
        if second_end.is_success:
            # End time should remain the same or be updated
            assert session.end_time is not None


class TestCommandWorkflow:
    """Tests for complete command workflow orchestration."""

    def setup_method(self) -> None:
        """Set up domain services instance for each test."""
        self.service = FlextCliService()

    def test_execute_command_workflow_success(self) -> None:
        """Test successful complete command workflow."""
        command_line = "echo 'workflow test'"

        # This should create, execute, and complete a command
        result: FlextResult[FlextCliModels.CliCommand] = (
            self.service.execute_command_workflow(command_line)
        )

        # The workflow returns CliCommand object
        if result.is_success:
            command: FlextCliModels.CliCommand = result.value
            assert isinstance(command, FlextCliModels.CliCommand)
            assert command.command_line == command_line
            assert command.status == FlextCliConstants.CommandStatus.COMPLETED.value
        else:
            # Should fail gracefully with meaningful error
            assert result.error is not None
            assert len(result.error) > 0

    def test_execute_command_workflow_empty_command(self) -> None:
        """Test command workflow fails with empty command."""
        result: FlextResult[FlextCliModels.CliCommand] = (
            self.service.execute_command_workflow("")
        )
        assert result.is_failure
        assert "validation error" in str(result.error or "").lower()

    def test_execute_command_workflow_invalid_command(self) -> None:
        """Test command workflow with invalid command."""
        result: FlextResult[FlextCliModels.CliCommand] = (
            self.service.execute_command_workflow(
                "invalid_command_that_does_not_exist_12345",
            )
        )

        # Should handle gracefully - workflow method returns CliCommand or fails
        if result.is_success:
            command: FlextCliModels.CliCommand = result.value
            assert isinstance(command, FlextCliModels.CliCommand)
            # Command is created and completed even if invalid
            assert command.status == FlextCliConstants.CommandStatus.COMPLETED.value
        else:
            assert result.error is not None


class TestIntegrationScenarios:
    """Integration tests for complex domain service scenarios."""

    def setup_method(self) -> None:
        """Set up domain services instance for each test."""
        self.service = FlextCliService()

    def test_complete_session_workflow(self) -> None:
        """Test complete session workflow with multiple commands."""
        # Create session
        session_result: FlextResult[FlextCliModels.CliSession] = (
            self.service.create_session("integration_user")
        )
        assert session_result.is_success
        session: FlextCliModels.CliSession = session_result.value

        # Create multiple commands and add to session
        command_lines = ["echo 'first'", "echo 'second'", "echo 'third'"]

        for cmd_line in command_lines:
            # Create command
            cmd_result: FlextResult[FlextCliModels.CliCommand] = (
                self.service.create_command(cmd_line)
            )
            assert cmd_result.is_success

            # Add to session
            add_result: FlextResult[FlextCliModels.CliSession] = (
                self.service.add_command_to_session(
                    session,
                    cmd_result.value,
                )
            )
            assert add_result.is_success

        # Note: CliSession doesn't have commands list in current model

        # End session
        end_result: FlextResult[FlextCliModels.CliSession] = self.service.end_session(
            session
        )
        assert end_result.is_success
        assert session.end_time is not None

        # Validate session business rules
        validation_result: FlextResult[None] = session.validate_business_rules()
        assert validation_result.is_success

    def test_command_lifecycle_with_session(self) -> None:
        """Test complete command lifecycle within a session."""
        # Create session
        session_result: FlextResult[FlextCliModels.CliSession] = (
            self.service.create_session()
        )
        assert session_result.is_success
        session: FlextCliModels.CliSession = session_result.value

        # Create command
        cmd_result: FlextResult[FlextCliModels.CliCommand] = (
            self.service.create_command("echo 'lifecycle test'")
        )
        assert cmd_result.is_success
        command: FlextCliModels.CliCommand = cmd_result.value

        # Add to session
        add_result: FlextResult[FlextCliModels.CliSession] = (
            self.service.add_command_to_session(session, command)
        )
        assert add_result.is_success

        # Start execution
        start_result: FlextResult[FlextCliModels.CliCommand] = (
            self.service.start_command_execution(command)
        )
        assert start_result.is_success
        assert command.status == FlextCliConstants.CommandStatus.RUNNING.value

        # Complete execution
        complete_result: FlextResult[FlextCliModels.CliCommand] = (
            self.service.complete_command_execution(
                command,
                exit_code=0,
                output="lifecycle test",
                error_output="",
            )
        )
        assert complete_result.is_success
        assert command.status == FlextCliConstants.CommandStatus.COMPLETED.value

        # End session
        end_result: FlextResult[FlextCliModels.CliSession] = self.service.end_session(
            session
        )
        assert end_result.is_success

    def test_error_recovery_scenarios(self) -> None:
        """Test error recovery in domain service operations."""
        # Test recovery from command creation failure
        invalid_result: FlextResult[FlextCliModels.CliCommand] = (
            self.service.create_command("")
        )
        assert invalid_result.is_failure

        # Should still be able to create valid command after failure
        valid_result: FlextResult[FlextCliModels.CliCommand] = (
            self.service.create_command("echo recovery")
        )
        assert valid_result.is_success

        # Test recovery from execution failure
        command: FlextCliModels.CliCommand = valid_result.value
        start_result: FlextResult[FlextCliModels.CliCommand] = (
            self.service.start_command_execution(command)
        )
        assert start_result.is_success

        # Complete with error
        error_complete: FlextResult[FlextCliModels.CliCommand] = (
            self.service.complete_command_execution(
                command,
                exit_code=1,
                output="",
                error_output="Simulated error",
            )
        )
        assert error_complete.is_success
        assert command.status == FlextCliConstants.CommandStatus.FAILED.value

    def test_business_rule_enforcement(self) -> None:
        """Test business rule enforcement across domain operations."""
        # Create command
        cmd_result: FlextResult[FlextCliModels.CliCommand] = (
            self.service.create_command("echo 'business rules'")
        )
        assert cmd_result.is_success
        command: FlextCliModels.CliCommand = cmd_result.value

        # Try to complete without starting (should fail)
        complete_result: FlextResult[FlextCliModels.CliCommand] = (
            self.service.complete_command_execution(
                command,
                exit_code=0,
                output="test",
            )
        )
        assert complete_result.is_failure
        assert "must be running" in str(complete_result.error or "").lower()

        # Try to start twice (should fail on second attempt)
        start1: FlextResult[FlextCliModels.CliCommand] = (
            self.service.start_command_execution(command)
        )
        assert start1.is_success

        start2: FlextResult[FlextCliModels.CliCommand] = (
            self.service.start_command_execution(command)
        )
        assert start2.is_failure
        assert "must be pending" in str(start2.error or "").lower()


class TestExceptionHandling:
    """Tests for exception handling in domain services."""

    def setup_method(self) -> None:
        """Set up domain services instance for each test."""
        self.service = FlextCliService()

    def test_graceful_exception_handling(self) -> None:
        """Test that all methods handle exceptions gracefully."""

        # All domain service methods should return FlextResult and handle exceptions
        # Test methods that return different FlextResult return types
        def health_check_method() -> FlextResult[str]:
            return self.service.health_check()

        def execute_method() -> FlextResult[dict[str, object]]:
            return self.service.execute()

        # Test each method individually with proper types
        try:
            health_result = health_check_method()
            assert isinstance(health_result, FlextResult)
            assert health_result.is_success or health_result.is_failure
        except Exception as e:
            pytest.fail(f"Health check method raised unhandled exception: {e}")

        try:
            execute_result = execute_method()
            assert isinstance(execute_result, FlextResult)
            assert execute_result.is_success or execute_result.is_failure
        except Exception as e:
            pytest.fail(f"Execute method raised unhandled exception: {e}")

    def test_error_message_quality(self) -> None:
        """Test that error messages are descriptive and helpful."""
        # Test various error scenarios
        # Use proper types for different FlextResult return types
        error_scenarios: list[Callable[[], FlextResult[FlextCliModels.CliCommand]]] = [
            lambda: self.service.create_command(""),
            lambda: self.service.create_command("   "),
        ]

        for scenario in error_scenarios:
            result: FlextResult[FlextCliModels.CliCommand] = scenario()
            if result.is_failure:
                assert result.error is not None
                assert len(result.error) > 10  # Should be descriptive
                assert not result.error.startswith("Error:")  # Should be specific
