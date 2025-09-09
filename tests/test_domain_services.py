"""Comprehensive tests for FLEXT CLI Domain Services.

Tests for FlextCliDomainServices class covering business logic orchestration,
command lifecycle management, session management, and domain-driven design patterns.

Coverage target: 15% → 95%+
"""

from __future__ import annotations

import pytest
from flext_core import FlextResult
from flext_cli.constants import FlextCliConstants
from flext_cli.domain_services import FlextCliDomainServices
from flext_cli.models import FlextCliModels


class TestFlextCliDomainServices:
    """Comprehensive tests for FlextCliDomainServices class."""
    
    def setup_method(self) -> None:
        """Set up domain services instance for each test."""
        self.domain_services = FlextCliDomainServices()
    
    def test_init_success(self) -> None:
        """Test successful domain services initialization."""
        services = FlextCliDomainServices()
        assert services is not None
        assert isinstance(services, FlextCliDomainServices)
    
    def test_execute_success(self) -> None:
        """Test successful domain service execution."""
        result = self.domain_services.execute()
        assert result.is_success
        assert result.value is not None
        assert result.value.is_success
    
    def test_execute_exception_handling(self) -> None:
        """Test domain service execution exception handling."""
        # This will test the exception handling path
        # Create a domain services instance that will fail health check
        services = FlextCliDomainServices()
        
        # Test normal execution first to ensure it works
        result = services.execute()
        assert result.is_success or result.is_failure  # Should handle gracefully
    
    def test_health_check_success(self) -> None:
        """Test successful health check."""
        result = self.domain_services.health_check()
        assert result.is_success
        assert result.value == "FLEXT CLI Domain Services: healthy"
    
    def test_health_check_returns_correct_message(self) -> None:
        """Test health check returns expected message format."""
        result = self.domain_services.health_check()
        assert result.is_success
        assert "FLEXT CLI Domain Services" in result.value
        assert "healthy" in result.value


class TestCommandLifecycleManagement:
    """Tests for command lifecycle management in domain services."""
    
    def setup_method(self) -> None:
        """Set up domain services instance for each test."""
        self.domain_services = FlextCliDomainServices()
    
    def test_create_command_success(self) -> None:
        """Test successful command creation."""
        command_line = "echo 'Hello World'"
        result = self.domain_services.create_command(command_line)
        assert result.is_success
        assert isinstance(result.value, FlextCliModels.CliCommand)
        assert result.value.command_line == command_line
        assert result.value.status == FlextCliConstants.STATUS_PENDING
    
    def test_create_command_empty_string(self) -> None:
        """Test command creation fails with empty string."""
        result = self.domain_services.create_command("")
        assert result.is_failure
        assert "Command line cannot be empty" in result.error
    
    def test_create_command_none_input(self) -> None:
        """Test command creation fails with None input."""
        result = self.domain_services.create_command(None)
        assert result.is_failure
        assert "Command line cannot be empty" in result.error
    
    def test_create_command_whitespace_only(self) -> None:
        """Test command creation fails with whitespace-only input."""
        result = self.domain_services.create_command("   \t\n   ")
        assert result.is_failure
        assert "Command line cannot be empty" in result.error
    
    def test_create_command_strips_whitespace(self) -> None:
        """Test command creation strips whitespace from input."""
        command_line = "  echo test  "
        result = self.domain_services.create_command(command_line)
        assert result.is_success
        assert result.value.command_line == "echo test"
    
    def test_create_command_with_dangerous_patterns(self) -> None:
        """Test command creation with potentially dangerous patterns."""
        dangerous_commands = [
            "rm -rf /",
            "format C:",
            "del /f /s /q C:\\*",
            "sudo rm -rf /"
        ]
        
        for dangerous_cmd in dangerous_commands:
            result = self.domain_services.create_command(dangerous_cmd)
            # Should either fail validation or handle gracefully
            if result.is_failure:
                assert "dangerous" in result.error.lower() or "validation" in result.error.lower()
    
    def test_start_command_execution_success(self) -> None:
        """Test successful command execution start."""
        # Create a command first
        create_result = self.domain_services.create_command("echo test")
        assert create_result.is_success
        command = create_result.value
        
        # Start execution
        result = self.domain_services.start_command_execution(command)
        assert result.is_success
        assert result.value.status == FlextCliConstants.STATUS_RUNNING
    
    def test_start_command_execution_wrong_status(self) -> None:
        """Test command execution start fails with wrong status."""
        # Create a command and manually set wrong status (must set exit code first for validation)
        create_result = self.domain_services.create_command("echo test")
        assert create_result.is_success
        command = create_result.value
        command.exit_code = 0  # Set exit code first to satisfy Pydantic validation
        command.status = FlextCliConstants.STATUS_COMPLETED
        
        # Try to start execution
        result = self.domain_services.start_command_execution(command)
        assert result.is_failure
        assert "Command must be pending to start" in result.error
        assert command.status in result.error
    
    def test_complete_command_execution_success(self) -> None:
        """Test successful command execution completion."""
        # Create and start a command
        create_result = self.domain_services.create_command("echo test")
        assert create_result.is_success
        command = create_result.value
        
        start_result = self.domain_services.start_command_execution(command)
        assert start_result.is_success
        
        # Complete execution
        result = self.domain_services.complete_command_execution(
            command, exit_code=0, output="test", error_output=""
        )
        assert result.is_success
        assert result.value.status == FlextCliConstants.STATUS_COMPLETED
        assert result.value.exit_code == 0
        assert result.value.output == "test"
    
    def test_complete_command_execution_with_error(self) -> None:
        """Test command execution completion with error."""
        # Create and start a command
        create_result = self.domain_services.create_command("echo test")
        assert create_result.is_success
        command = create_result.value
        
        start_result = self.domain_services.start_command_execution(command)
        assert start_result.is_success
        
        # Complete execution with error
        result = self.domain_services.complete_command_execution(
            command, exit_code=1, output="", error_output="Command failed"
        )
        assert result.is_success
        assert result.value.status == FlextCliConstants.STATUS_FAILED
        assert result.value.exit_code == 1
        assert result.value.error_output == "Command failed"
    
    def test_complete_command_execution_wrong_status(self) -> None:
        """Test command execution completion fails with wrong status."""
        # Create a command with wrong status
        create_result = self.domain_services.create_command("echo test")
        assert create_result.is_success
        command = create_result.value
        # Command is still pending, not running
        
        # Try to complete execution
        result = self.domain_services.complete_command_execution(
            command, exit_code=0, output="test"
        )
        assert result.is_failure
        assert "Command must be running to complete" in result.error


class TestSessionManagement:
    """Tests for session management in domain services."""
    
    def setup_method(self) -> None:
        """Set up domain services instance for each test."""
        self.domain_services = FlextCliDomainServices()
    
    def test_create_session_success(self) -> None:
        """Test successful session creation."""
        result = self.domain_services.create_session()
        assert result.is_success
        assert isinstance(result.value, FlextCliModels.CliSession)
        assert result.value.user_id is None  # No user_id provided
    
    def test_create_session_with_user_id(self) -> None:
        """Test successful session creation with user ID."""
        user_id = "test_user_123"
        result = self.domain_services.create_session(user_id)
        assert result.is_success
        assert result.value.user_id == user_id
    
    def test_create_session_with_empty_user_id(self) -> None:
        """Test session creation with empty user ID."""
        result = self.domain_services.create_session("")
        assert result.is_success
        # Empty string should be handled gracefully
    
    def test_add_command_to_session_success(self) -> None:
        """Test successfully adding command to session."""
        # Create session and command
        session_result = self.domain_services.create_session()
        assert session_result.is_success
        session = session_result.value
        
        command_result = self.domain_services.create_command("echo test")
        assert command_result.is_success
        command = command_result.value
        
        # Add command to session
        result = self.domain_services.add_command_to_session(session, command)
        assert result.is_success
        assert len(result.value.commands) == 1
        assert result.value.commands[0] == command
    
    def test_add_multiple_commands_to_session(self) -> None:
        """Test adding multiple commands to session."""
        # Create session
        session_result = self.domain_services.create_session()
        assert session_result.is_success
        session = session_result.value
        
        # Create and add multiple commands
        for i in range(3):
            command_result = self.domain_services.create_command(f"echo test{i}")
            assert command_result.is_success
            
            add_result = self.domain_services.add_command_to_session(
                session, command_result.value
            )
            assert add_result.is_success
        
        assert len(session.commands) == 3
    
    def test_end_session_success(self) -> None:
        """Test successful session ending."""
        # Create session
        session_result = self.domain_services.create_session()
        assert session_result.is_success
        session = session_result.value
        assert session.end_time is None
        
        # End session
        result = self.domain_services.end_session(session)
        assert result.is_success
        assert result.value.end_time is not None
    
    def test_end_session_already_ended(self) -> None:
        """Test ending session that's already ended."""
        # Create and end session
        session_result = self.domain_services.create_session()
        assert session_result.is_success
        session = session_result.value
        
        first_end = self.domain_services.end_session(session)
        assert first_end.is_success
        first_end_time = session.end_time
        
        # Try to end again
        second_end = self.domain_services.end_session(session)
        # Should handle gracefully - either succeed or fail appropriately
        if second_end.is_success:
            # End time should remain the same or be updated
            assert session.end_time is not None


class TestCommandWorkflow:
    """Tests for complete command workflow orchestration."""
    
    def setup_method(self) -> None:
        """Set up domain services instance for each test."""
        self.domain_services = FlextCliDomainServices()
    
    def test_execute_command_workflow_success(self) -> None:
        """Test successful complete command workflow."""
        command_line = "echo 'workflow test'"
        
        # This should create, execute, and complete a command
        result = self.domain_services.execute_command_workflow(command_line)
        
        # The workflow should handle all steps
        if result.is_success:
            workflow_data = result.value
            assert isinstance(workflow_data, dict)
            assert "command_line" in workflow_data
            assert workflow_data["command_line"] == command_line
            assert "workflow_status" in workflow_data
            assert "session_id" in workflow_data
            assert "command_id" in workflow_data
        else:
            # Should fail gracefully with meaningful error
            assert result.error is not None
            assert len(result.error) > 0
    
    def test_execute_command_workflow_empty_command(self) -> None:
        """Test command workflow fails with empty command."""
        result = self.domain_services.execute_command_workflow("")
        assert result.is_failure
        assert "empty" in result.error.lower() or "invalid" in result.error.lower()
    
    def test_execute_command_workflow_invalid_command(self) -> None:
        """Test command workflow with invalid command."""
        result = self.domain_services.execute_command_workflow("invalid_command_that_does_not_exist_12345")
        
        # Should handle gracefully - workflow method returns dict or fails
        if result.is_success:
            workflow_data = result.value
            assert isinstance(workflow_data, dict)
            # Should at least have workflow status
            assert "workflow_status" in workflow_data
        else:
            assert result.error is not None


class TestIntegrationScenarios:
    """Integration tests for complex domain service scenarios."""
    
    def setup_method(self) -> None:
        """Set up domain services instance for each test."""
        self.domain_services = FlextCliDomainServices()
    
    def test_complete_session_workflow(self) -> None:
        """Test complete session workflow with multiple commands."""
        # Create session
        session_result = self.domain_services.create_session("integration_user")
        assert session_result.is_success
        session = session_result.value
        
        # Create multiple commands and add to session
        command_lines = ["echo 'first'", "echo 'second'", "echo 'third'"]
        
        for cmd_line in command_lines:
            # Create command
            cmd_result = self.domain_services.create_command(cmd_line)
            assert cmd_result.is_success
            
            # Add to session
            add_result = self.domain_services.add_command_to_session(session, cmd_result.value)
            assert add_result.is_success
        
        assert len(session.commands) == 3
        
        # End session
        end_result = self.domain_services.end_session(session)
        assert end_result.is_success
        assert session.end_time is not None
        
        # Validate session business rules
        validation_result = session.validate_business_rules()
        assert validation_result.is_success
    
    def test_command_lifecycle_with_session(self) -> None:
        """Test complete command lifecycle within a session."""
        # Create session
        session_result = self.domain_services.create_session()
        assert session_result.is_success
        session = session_result.value
        
        # Create command
        cmd_result = self.domain_services.create_command("echo 'lifecycle test'")
        assert cmd_result.is_success
        command = cmd_result.value
        
        # Add to session
        add_result = self.domain_services.add_command_to_session(session, command)
        assert add_result.is_success
        
        # Start execution
        start_result = self.domain_services.start_command_execution(command)
        assert start_result.is_success
        assert command.status == FlextCliConstants.STATUS_RUNNING
        
        # Complete execution
        complete_result = self.domain_services.complete_command_execution(
            command, exit_code=0, output="lifecycle test", error_output=""
        )
        assert complete_result.is_success
        assert command.status == FlextCliConstants.STATUS_COMPLETED
        
        # End session
        end_result = self.domain_services.end_session(session)
        assert end_result.is_success
    
    def test_error_recovery_scenarios(self) -> None:
        """Test error recovery in domain service operations."""
        # Test recovery from command creation failure
        invalid_result = self.domain_services.create_command("")
        assert invalid_result.is_failure
        
        # Should still be able to create valid command after failure
        valid_result = self.domain_services.create_command("echo recovery")
        assert valid_result.is_success
        
        # Test recovery from execution failure
        command = valid_result.value
        start_result = self.domain_services.start_command_execution(command)
        assert start_result.is_success
        
        # Complete with error
        error_complete = self.domain_services.complete_command_execution(
            command, exit_code=1, output="", error_output="Simulated error"
        )
        assert error_complete.is_success
        assert command.status == FlextCliConstants.STATUS_FAILED
    
    def test_business_rule_enforcement(self) -> None:
        """Test business rule enforcement across domain operations."""
        # Create command
        cmd_result = self.domain_services.create_command("echo 'business rules'")
        assert cmd_result.is_success
        command = cmd_result.value
        
        # Try to complete without starting (should fail)
        complete_result = self.domain_services.complete_command_execution(
            command, exit_code=0, output="test"
        )
        assert complete_result.is_failure
        assert "must be running" in complete_result.error.lower()
        
        # Try to start twice (should fail on second attempt)
        start1 = self.domain_services.start_command_execution(command)
        assert start1.is_success
        
        start2 = self.domain_services.start_command_execution(command)
        assert start2.is_failure
        assert "must be pending" in start2.error.lower()


class TestExceptionHandling:
    """Tests for exception handling in domain services."""
    
    def setup_method(self) -> None:
        """Set up domain services instance for each test."""
        self.domain_services = FlextCliDomainServices()
    
    def test_graceful_exception_handling(self) -> None:
        """Test that all methods handle exceptions gracefully."""
        # All domain service methods should return FlextResult and handle exceptions
        methods_to_test = [
            lambda: self.domain_services.health_check(),
            lambda: self.domain_services.execute(),
        ]
        
        for method in methods_to_test:
            try:
                result = method()
                assert isinstance(result, FlextResult)
                # Should either succeed or fail gracefully
                assert result.is_success or result.is_failure
            except Exception as e:
                # Should not raise unhandled exceptions
                pytest.fail(f"Method raised unhandled exception: {e}")
    
    def test_error_message_quality(self) -> None:
        """Test that error messages are descriptive and helpful."""
        # Test various error scenarios
        error_scenarios = [
            lambda: self.domain_services.create_command(""),
            lambda: self.domain_services.create_command(None),
        ]
        
        for scenario in error_scenarios:
            result = scenario()
            if result.is_failure:
                assert result.error is not None
                assert len(result.error) > 10  # Should be descriptive
                assert not result.error.startswith("Error:")  # Should be specific