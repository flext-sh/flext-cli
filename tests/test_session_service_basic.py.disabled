"""Basic tests for CLI Session Service.

Focus on real functionality testing to improve coverage.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from uuid import uuid4

import pytest

from flext_cli.models import FlextCliModels
from flext_cli.session_service import FlextCliSessionService
from flext_core import FlextResult


class TestFlextCliSessionService:
    """Test FlextCliSessionService basic functionality."""

    def test_session_service_initialization(self) -> None:
        """Test FlextCliSessionService can be initialized."""
        service = FlextCliSessionService()
        assert service is not None

    def test_session_service_execute(self) -> None:
        """Test FlextCliSessionService execute method."""
        service = FlextCliSessionService()
        result = service.execute()
        assert isinstance(result, FlextResult)
        assert result.is_success

        data = result.unwrap()
        assert "active_sessions" in data
        assert "tracking_enabled" in data
        assert data["tracking_enabled"] is True
        assert isinstance(data["active_sessions"], int)

    def test_create_session_success(self) -> None:
        """Test creating a session successfully."""
        service = FlextCliSessionService()
        result = service.create_session(user_id="test_user")

        assert result.is_success
        session = result.unwrap()
        assert isinstance(session, FlextCliModels.CliSession)
        assert session.user_id == "test_user"
        assert session.session_id is not None
        assert session.start_time is not None
        assert session.end_time is None

    def test_create_session_without_user(self) -> None:
        """Test creating a session without user ID."""
        service = FlextCliSessionService()
        result = service.create_session()

        assert result.is_success
        session = result.unwrap()
        assert session.user_id is None

    def test_create_session_with_none_user(self) -> None:
        """Test creating a session with None user ID."""
        service = FlextCliSessionService()
        result = service.create_session(user_id=None)

        assert result.is_success
        session = result.unwrap()
        assert session.user_id is None

    def test_create_session_with_empty_user(self) -> None:
        """Test creating a session with empty user ID."""
        service = FlextCliSessionService()
        result = service.create_session(user_id="")

        assert result.is_success
        session = result.unwrap()
        assert session.user_id is None

    def test_end_session_success(self) -> None:
        """Test ending a session successfully."""
        service = FlextCliSessionService()

        # Create a session first
        create_result = service.create_session(user_id="test_user")
        assert create_result.is_success
        session = create_result.unwrap()

        # End the session
        end_result = service.end_session(session.session_id)
        assert end_result.is_success

        ended_session = end_result.unwrap()
        assert ended_session.session_id == session.session_id
        assert ended_session.end_time is not None

    def test_end_session_not_found(self) -> None:
        """Test ending a non-existent session."""
        service = FlextCliSessionService()
        fake_session_id = str(uuid4())

        result = service.end_session(fake_session_id)
        assert result.is_failure
        assert "Session not found" in str(result.error)

    def test_end_session_invalid_id(self) -> None:
        """Test ending a session with invalid ID."""
        service = FlextCliSessionService()

        result = service.end_session("invalid-id")
        assert result.is_failure
        assert "Invalid session ID format" in str(result.error)

        result = service.end_session("")
        assert result.is_failure
        assert "Session ID must be a non-empty string" in str(result.error)

    def test_get_session_success(self) -> None:
        """Test getting a session successfully."""
        service = FlextCliSessionService()

        # Create a session first
        create_result = service.create_session(user_id="test_user")
        assert create_result.is_success
        created_session = create_result.unwrap()

        # Get the session
        get_result = service.get_session(created_session.session_id)
        assert get_result.is_success

        retrieved_session = get_result.unwrap()
        assert retrieved_session.session_id == created_session.session_id
        assert retrieved_session.user_id == "test_user"

    def test_get_session_not_found(self) -> None:
        """Test getting a non-existent session."""
        service = FlextCliSessionService()
        fake_session_id = str(uuid4())

        result = service.get_session(fake_session_id)
        assert result.is_failure
        assert "Session not found" in str(result.error)

    def test_list_active_sessions(self) -> None:
        """Test listing active sessions."""
        service = FlextCliSessionService()

        # Initially empty
        result = service.list_active_sessions()
        assert result.is_success
        assert len(result.unwrap()) == 0

        # Create some sessions
        service.create_session(user_id="user1")
        service.create_session(user_id="user2")

        # List sessions
        result = service.list_active_sessions()
        assert result.is_success
        sessions = result.unwrap()
        assert len(sessions) == 2

        # Verify session details
        user_ids = [session.user_id for session in sessions]
        assert "user1" in user_ids
        assert "user2" in user_ids

    def test_get_session_statistics(self) -> None:
        """Test getting session statistics."""
        service = FlextCliSessionService()

        # Create some sessions
        service.create_session(user_id="user1")
        service.create_session(user_id="user1")  # Same user
        service.create_session(user_id="user2")
        service.create_session()  # Anonymous

        stats_result = service.get_session_statistics()
        assert stats_result.is_success

        stats = stats_result.unwrap()
        assert stats["total_active_sessions"] == 4
        assert "average_duration_seconds" in stats
        assert "longest_session_seconds" in stats
        assert "shortest_session_seconds" in stats
        assert "sessions_by_user" in stats

        # Check user breakdown
        sessions_by_user = stats["sessions_by_user"]
        assert sessions_by_user["user1"] == 2
        assert sessions_by_user["user2"] == 1
        assert sessions_by_user["anonymous"] == 1

    def test_configure_session_tracking(self) -> None:
        """Test configuring session tracking."""
        service = FlextCliSessionService()

        # Create some sessions
        service.create_session(user_id="user1")
        service.create_session(user_id="user2")

        # Verify sessions exist
        list_result = service.list_active_sessions()
        assert list_result.is_success
        assert len(list_result.unwrap()) == 2

        # Disable tracking
        config_result = service.configure_session_tracking(enabled=False)
        assert config_result.is_success

        # Verify sessions are cleared and tracking disabled
        list_result = service.list_active_sessions()
        assert list_result.is_failure
        assert "Session tracking is disabled" in str(list_result.error)

        # Re-enable tracking
        config_result = service.configure_session_tracking(enabled=True)
        assert config_result.is_success

        # Verify tracking works again
        list_result = service.list_active_sessions()
        assert list_result.is_success
        assert len(list_result.unwrap()) == 0  # Sessions were cleared

    def test_clear_all_sessions(self) -> None:
        """Test clearing all sessions."""
        service = FlextCliSessionService()

        # Create some sessions
        service.create_session(user_id="user1")
        service.create_session(user_id="user2")
        service.create_session(user_id="user3")

        # Clear all sessions
        clear_result = service.clear_all_sessions()
        assert clear_result.is_success
        assert clear_result.unwrap() == 3  # Number of cleared sessions

        # Verify sessions are empty
        list_result = service.list_active_sessions()
        assert list_result.is_success
        assert len(list_result.unwrap()) == 0

    def test_disabled_tracking_operations(self) -> None:
        """Test operations when tracking is disabled."""
        service = FlextCliSessionService()

        # Disable tracking
        service.configure_session_tracking(enabled=False)

        # Test various operations fail appropriately
        fake_session_id = str(uuid4())

        operations = [
            lambda: service.create_session(user_id="test"),
            lambda: service.end_session(fake_session_id),
            lambda: service.get_session(fake_session_id),
            service.list_active_sessions,
            service.get_session_statistics,
            service.clear_all_sessions,
        ]

        for operation in operations:
            result = operation()
            assert result.is_failure
            assert "Session tracking is disabled" in str(result.error)


class TestFlextCliSessionServiceHelpers:
    """Test FlextCliSessionService nested helper classes."""

    def test_session_validation_helper_session_id(self) -> None:
        """Test _SessionValidationHelper session ID validation."""
        # Test valid session ID
        valid_id = str(uuid4())
        result = FlextCliSessionService._SessionValidationHelper.validate_session_id(
            valid_id
        )
        assert result.is_success
        assert result.unwrap() == valid_id

        # Test invalid session ID
        result = FlextCliSessionService._SessionValidationHelper.validate_session_id("")
        assert result.is_failure
        assert "Session ID must be a non-empty string" in str(result.error)

        result = FlextCliSessionService._SessionValidationHelper.validate_session_id(
            "invalid-uuid"
        )
        assert result.is_failure
        assert "Invalid session ID format" in str(result.error)

        result = FlextCliSessionService._SessionValidationHelper.validate_session_id(
            None
        )
        assert result.is_failure

    def test_session_validation_helper_user_id(self) -> None:
        """Test _SessionValidationHelper user ID validation."""
        # Test None user ID
        result = FlextCliSessionService._SessionValidationHelper.validate_user_id(None)
        assert result.is_success
        assert result.unwrap() is None

        # Test valid string user ID
        result = FlextCliSessionService._SessionValidationHelper.validate_user_id(
            "test_user"
        )
        assert result.is_success
        assert result.unwrap() == "test_user"

        # Test empty string user ID
        result = FlextCliSessionService._SessionValidationHelper.validate_user_id("")
        assert result.is_success
        assert result.unwrap() is None

        # Test whitespace-only user ID
        result = FlextCliSessionService._SessionValidationHelper.validate_user_id("   ")
        assert result.is_success
        assert result.unwrap() is None

        # Test non-string user ID
        result = FlextCliSessionService._SessionValidationHelper.validate_user_id(123)
        assert result.is_success
        assert result.unwrap() == "123"

    def test_session_state_helper_create_metadata(self) -> None:
        """Test _SessionStateHelper create session metadata."""
        # Test with user ID
        session = FlextCliSessionService._SessionStateHelper.create_session_metadata(
            "test_user"
        )
        assert isinstance(session, FlextCliModels.CliSession)
        assert session.user_id == "test_user"
        assert session.session_id is not None
        assert session.id == session.session_id
        assert session.start_time is not None
        assert session.end_time is None

        # Test without user ID
        session = FlextCliSessionService._SessionStateHelper.create_session_metadata(
            None
        )
        assert session.user_id is None

    def test_session_state_helper_calculate_duration(self) -> None:
        """Test _SessionStateHelper calculate session duration."""
        from datetime import timedelta

        # Create a session with start time
        session = FlextCliSessionService._SessionStateHelper.create_session_metadata(
            "test"
        )

        # Test duration calculation for active session (no end time)
        duration = (
            FlextCliSessionService._SessionStateHelper.calculate_session_duration(
                session
            )
        )
        assert isinstance(duration, float)
        assert duration >= 0

        # Test duration calculation for ended session
        session.end_time = session.start_time + timedelta(seconds=30)
        duration = (
            FlextCliSessionService._SessionStateHelper.calculate_session_duration(
                session
            )
        )
        assert duration == 30.0


class TestFlextCliSessionServiceIntegration:
    """Test FlextCliSessionService integration scenarios."""

    def test_complete_session_workflow(self) -> None:
        """Test complete session workflow from creation to end."""
        service = FlextCliSessionService()

        # Create session
        create_result = service.create_session(user_id="workflow_user")
        assert create_result.is_success
        session = create_result.unwrap()

        # Get session
        get_result = service.get_session(session.session_id)
        assert get_result.is_success
        assert get_result.unwrap().session_id == session.session_id

        # Check it's in active sessions
        list_result = service.list_active_sessions()
        assert list_result.is_success
        assert len(list_result.unwrap()) == 1

        # Get statistics
        stats_result = service.get_session_statistics()
        assert stats_result.is_success
        assert stats_result.unwrap()["total_active_sessions"] == 1

        # End session
        end_result = service.end_session(session.session_id)
        assert end_result.is_success

        # Verify session is no longer active
        list_result = service.list_active_sessions()
        assert list_result.is_success
        assert len(list_result.unwrap()) == 0

    def test_session_service_state_management(self) -> None:
        """Test session service state management."""
        service = FlextCliSessionService()

        # Test initial state
        execute_result = service.execute()
        assert execute_result.is_success
        state = execute_result.unwrap()
        assert state["active_sessions"] == 0
        assert state["tracking_enabled"] is True

        # Add sessions and verify state changes
        service.create_session(user_id="user1")
        execute_result = service.execute()
        assert execute_result.unwrap()["active_sessions"] == 1

        service.create_session(user_id="user2")
        execute_result = service.execute()
        assert execute_result.unwrap()["active_sessions"] == 2

    def test_session_user_grouping(self) -> None:
        """Test session grouping by user."""
        service = FlextCliSessionService()

        # Create sessions for different users
        service.create_session(user_id="alice")
        service.create_session(user_id="alice")
        service.create_session(user_id="bob")
        service.create_session()  # anonymous

        # Get statistics
        stats_result = service.get_session_statistics()
        assert stats_result.is_success
        stats = stats_result.unwrap()

        sessions_by_user = stats["sessions_by_user"]
        assert sessions_by_user["alice"] == 2
        assert sessions_by_user["bob"] == 1
        assert sessions_by_user["anonymous"] == 1

    def test_error_handling_comprehensive(self) -> None:
        """Test comprehensive error handling scenarios."""
        service = FlextCliSessionService()

        # Test various error scenarios don't crash the service
        invalid_session_id = "invalid-uuid"
        fake_session_id = str(uuid4())

        error_operations = [
            lambda: service.end_session(""),
            lambda: service.end_session(invalid_session_id),
            lambda: service.get_session(fake_session_id),
            lambda: service.end_session(fake_session_id),
        ]

        for operation in error_operations:
            try:
                result = operation()
                assert isinstance(result, FlextResult)
                assert result.is_failure
            except Exception as e:
                pytest.fail(f"Operation raised unhandled exception: {e}")

    def test_private_helper_method(self) -> None:
        """Test private helper method _get_sessions_by_user."""
        service = FlextCliSessionService()

        # Create sessions
        service.create_session(user_id="user1")
        service.create_session(user_id="user1")
        service.create_session(user_id="user2")
        service.create_session()  # anonymous

        # Access private method (for testing purposes)
        user_counts = service._get_sessions_by_user()
        assert user_counts["user1"] == 2
        assert user_counts["user2"] == 1
        assert user_counts["anonymous"] == 1
