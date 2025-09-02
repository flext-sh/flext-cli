"""Real functionality tests for services.py - NO MOCKING.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

Following user requirement: "pare de ficar mockando tudo!"
Tests execute REAL service functionality.
"""

from __future__ import annotations

from flext_core import FlextResult

# Import the module for coverage tracking
from flext_cli.context import FlextCliExecutionContext

# Import module-level objects to ensure coverage
from flext_cli.services import (
    BasicFlextCliCommandService,
    BasicFlextCliSessionService,
)


class TestBasicFlextCliCommandService:
    """Test BasicFlextCliCommandService with REAL execution."""

    def test_init_creates_empty_commands_dict(self) -> None:
        """Test service initialization creates empty commands dict."""
        service = BasicFlextCliCommandService()
        assert hasattr(service, "commands")
        assert isinstance(service.commands, dict)
        assert len(service.commands) == 0

    def test_register_command_adds_to_dict(self) -> None:
        """Test register_command adds callable to commands dict."""
        service = BasicFlextCliCommandService()

        def test_handler(context: FlextCliExecutionContext, **kwargs: object) -> str:
            return "test_result"

        service.register_command("test_cmd", test_handler)

        assert "test_cmd" in service.commands
        assert service.commands["test_cmd"] is test_handler

    def test_list_commands_returns_keys_as_list(self) -> None:
        """Test list_commands returns command names as list."""
        service = BasicFlextCliCommandService()

        def handler1(context: FlextCliExecutionContext, **kwargs: object) -> str:
            return "result1"

        def handler2(context: FlextCliExecutionContext, **kwargs: object) -> str:
            return "result2"

        service.register_command("zebra", handler1)
        service.register_command("alpha", handler2)

        commands = service.list_commands()
        assert isinstance(commands, list)
        assert len(commands) == 2
        assert "zebra" in commands
        assert "alpha" in commands

    def test_execute_command_with_callable_handler(self) -> None:
        """Test execute_command works with callable handler."""
        service = BasicFlextCliCommandService()
        context = FlextCliExecutionContext()

        def test_handler(context: FlextCliExecutionContext, **kwargs: object) -> str:
            return "success"

        service.register_command("test", test_handler)

        result = service.execute_command("test", context)

        assert isinstance(result, FlextResult)
        assert result.is_success
        assert result.value == "success"

    def test_execute_command_with_flext_result_handler(self) -> None:
        """Test execute_command works with handler returning FlextResult."""
        service = BasicFlextCliCommandService()
        context = FlextCliExecutionContext()

        def result_handler(
            context: FlextCliExecutionContext, **kwargs: object
        ) -> FlextResult[str]:
            return FlextResult[str].ok("flext_success")

        service.register_command("result_test", result_handler)

        result = service.execute_command("result_test", context)

        assert isinstance(result, FlextResult)
        assert result.is_success
        assert result.value == "flext_success"

    def test_execute_command_not_found(self) -> None:
        """Test execute_command returns failure for unknown command."""
        service = BasicFlextCliCommandService()
        context = FlextCliExecutionContext()

        result = service.execute_command("nonexistent", context)

        assert isinstance(result, FlextResult)
        assert result.is_failure
        assert "Command 'nonexistent' not found" in result.error

    def test_execute_command_with_exception(self) -> None:
        """Test execute_command handles exceptions properly."""
        service = BasicFlextCliCommandService()
        context = FlextCliExecutionContext()

        def failing_handler(context: FlextCliExecutionContext, **kwargs: object) -> str:
            msg = "Test exception"
            raise ValueError(msg)

        service.register_command("failing", failing_handler)

        result = service.execute_command("failing", context)

        assert isinstance(result, FlextResult)
        assert result.is_failure
        assert "Command execution failed" in result.error
        assert "Test exception" in result.error

    def test_execute_command_with_non_callable_handler(self) -> None:
        """Test execute_command fails with non-callable handler."""
        service = BasicFlextCliCommandService()
        context = FlextCliExecutionContext()

        # Directly set a non-callable to simulate edge case
        service.commands["bad"] = "not_callable"

        result = service.execute_command("bad", context)

        assert isinstance(result, FlextResult)
        assert result.is_failure
        assert "Handler is not callable" in result.error

    def test_execute_command_with_kwargs(self) -> None:
        """Test execute_command passes kwargs to handler."""
        service = BasicFlextCliCommandService()
        context = FlextCliExecutionContext()

        def kwargs_handler(context: FlextCliExecutionContext, **kwargs: object) -> str:
            return f"received: {kwargs.get('test_param', 'none')}"

        service.register_command("kwargs_test", kwargs_handler)

        result = service.execute_command("kwargs_test", context, test_param="value123")

        assert isinstance(result, FlextResult)
        assert result.is_success
        assert result.value == "received: value123"


class TestBasicFlextCliSessionService:
    """Test BasicFlextCliSessionService with REAL execution."""

    def test_init_creates_empty_sessions_dict(self) -> None:
        """Test service initialization creates empty sessions dict."""
        service = BasicFlextCliSessionService()
        assert hasattr(service, "sessions")
        assert isinstance(service.sessions, dict)
        assert len(service.sessions) == 0

    def test_create_session_creates_new_session(self) -> None:
        """Test create_session creates new session."""
        service = BasicFlextCliSessionService()

        result = service.create_session("test_user")

        assert isinstance(result, FlextResult)
        assert result.is_success
        session_id = result.value

        assert isinstance(session_id, str)
        assert session_id in service.sessions

        session_data = service.sessions[session_id]
        assert session_data["id"] == session_id
        assert session_data["user_id"] == "test_user"
        assert session_data["active"] is True

    def test_get_session_returns_existing_session(self) -> None:
        """Test get_session returns existing session with commands_count."""
        service = BasicFlextCliSessionService()

        # Create a session first
        create_result = service.create_session("test_user")
        session_id = create_result.value

        # Get the session
        result = service.get_session(session_id)

        assert isinstance(result, FlextResult)
        assert result.is_success
        session_data = result.value

        assert session_data["id"] == session_id
        assert session_data["user_id"] == "test_user"
        assert "commands_count" in session_data
        assert session_data["commands_count"] == 0

    def test_get_session_not_found(self) -> None:
        """Test get_session returns failure for unknown session."""
        service = BasicFlextCliSessionService()

        result = service.get_session("nonexistent_session")

        assert isinstance(result, FlextResult)
        assert result.is_failure
        assert "Session 'nonexistent_session' not found" in result.error

    def test_end_session_success(self) -> None:
        """Test end_session marks session as inactive."""
        service = BasicFlextCliSessionService()

        # Create a session first
        create_result = service.create_session("test_user")
        session_id = create_result.value

        # End the session
        result = service.end_session(session_id)

        assert isinstance(result, FlextResult)
        assert result.is_success

        # Verify session is marked inactive (not removed)
        assert session_id in service.sessions
        assert service.sessions[session_id]["active"] is False

    def test_end_session_not_found(self) -> None:
        """Test end_session returns failure for unknown session."""
        service = BasicFlextCliSessionService()

        result = service.end_session("nonexistent_session")

        assert isinstance(result, FlextResult)
        assert result.is_failure
        assert "Session 'nonexistent_session' not found" in result.error

    def test_session_workflow_integration(self) -> None:
        """Test complete session workflow integration."""
        service = BasicFlextCliSessionService()

        # Create session
        create_result = service.create_session("integration_user")
        assert create_result.is_success
        session_id = create_result.value

        # Get session
        get_result = service.get_session(session_id)
        assert get_result.is_success
        assert get_result.value["user_id"] == "integration_user"

        # End session
        end_result = service.end_session(session_id)
        assert end_result.is_success

        # Verify session still exists but is inactive
        final_get = service.get_session(session_id)
        assert final_get.is_success
        assert final_get.value["active"] is False

    def test_session_data_contains_all_required_fields(self) -> None:
        """Test session data contains all required fields."""
        service = BasicFlextCliSessionService()

        result = service.create_session("field_test_user")
        session_id = result.value

        session_data = service.sessions[session_id]

        # Check all required fields are present
        required_fields = ["id", "user_id", "created_at", "active"]
        for field in required_fields:
            assert field in session_data, f"Required field '{field}' missing"

        # Get session should add commands_count
        get_result = service.get_session(session_id)
        get_data = get_result.value
        assert "commands_count" in get_data


class TestServicesModuleIntegration:
    """Test services module integration points."""

    def test_services_can_work_together(self) -> None:
        """Test command and session services can work together."""
        command_service = BasicFlextCliCommandService()
        session_service = BasicFlextCliSessionService()

        # Create a session
        session_result = session_service.create_session("integration_test")
        assert session_result.is_success

        # Register a command
        def test_command(context: FlextCliExecutionContext, **kwargs: object) -> str:
            return "integration_success"

        command_service.register_command("integration_cmd", test_command)

        # Execute command
        context = FlextCliExecutionContext()
        cmd_result = command_service.execute_command("integration_cmd", context)

        assert cmd_result.is_success
        assert cmd_result.value == "integration_success"

    def test_module_constants_and_imports(self) -> None:
        """Test module has expected constants and imports."""
        # Verify services can be instantiated
        command_service = BasicFlextCliCommandService()
        session_service = BasicFlextCliSessionService()

        assert isinstance(command_service, BasicFlextCliCommandService)
        assert isinstance(session_service, BasicFlextCliSessionService)

        # Verify they have expected attributes
        assert hasattr(command_service, "commands")
        assert hasattr(command_service, "register_command")
        assert hasattr(command_service, "execute_command")
        assert hasattr(command_service, "list_commands")

        assert hasattr(session_service, "sessions")
        assert hasattr(session_service, "create_session")
        assert hasattr(session_service, "get_session")
        assert hasattr(session_service, "end_session")
