"""Comprehensive parametrized unit tests for 100% coverage."""

from datetime import datetime

import pytest
from flext_cli import t
from flext_cli.constants import c
from flext_cli.models import m
from pydantic import ValidationError

from tests._helpers import (
    create_real_cli_command,
    create_real_cli_session,
    create_test_cli_command,
    generate_edge_case_data,
)


class TestsCliComprehensiveModels:
    """Comprehensive tests covering all model functionality with real data."""

    @pytest.mark.parametrize(
        "status",
        [
            c.Cli.CommandStatus.PENDING,
            c.Cli.CommandStatus.RUNNING,
            c.Cli.CommandStatus.COMPLETED,
            c.Cli.CommandStatus.FAILED,
            c.Cli.CommandStatus.CANCELLED,
        ],
    )
    def test_command_status_transitions(self, status: c.Cli.CommandStatus) -> None:
        """Test all possible command status transitions with real data."""
        cmd = create_real_cli_command(status=status)
        assert cmd.status == status

        # Test computed fields work with real data
        assert cmd.is_pending == (status == c.Cli.CommandStatus.PENDING)
        assert cmd.is_running == (status == c.Cli.CommandStatus.RUNNING)
        assert cmd.is_completed == (status == c.Cli.CommandStatus.COMPLETED)
        assert cmd.is_failed == (status == c.Cli.CommandStatus.FAILED)

    @pytest.mark.parametrize("edge_case", generate_edge_case_data())
    def test_command_edge_cases(self, edge_case: dict[str, t.GeneralValueType]) -> None:
        """Test command creation with comprehensive edge cases."""
        cmd = create_test_cli_command(**edge_case)

        # Verify all fields are properly set
        for key, value in edge_case.items():
            if key != "description":  # Skip test metadata
                assert getattr(cmd, key) == value

        # Verify command is valid and functional
        assert "test" in (cmd.command_line or cmd.name)
        assert isinstance(cmd.created_at, datetime)

    @pytest.mark.parametrize(
        "status",
        [
            c.Cli.SessionStatus.ACTIVE,
            c.Cli.SessionStatus.COMPLETED,
            c.Cli.SessionStatus.TERMINATED,
        ],
    )
    def test_session_statuses(self, status: c.Cli.SessionStatus) -> None:
        """Test session creation with different statuses."""
        session = create_real_cli_session(status=status)
        assert session.status == status

        # Test session has expected attributes
        assert session.session_id is not None
        assert len(session.commands) == 0  # No commands added yet

    def test_session_command_filtering(self) -> None:
        """Test session command filtering by status."""
        # Create session with commands using model_construct to pass commands list
        cmd1 = create_real_cli_command(name="cmd1", status=c.Cli.CommandStatus.PENDING)
        cmd2 = create_real_cli_command(
            name="cmd2", status=c.Cli.CommandStatus.COMPLETED
        )

        session = m.Cli.CliSession.model_construct(
            session_id="test-session",
            status=c.Cli.SessionStatus.ACTIVE,
            commands=[cmd1, cmd2],
        )

        # Test filtering with commands_by_status method
        pending = session.commands_by_status(c.Cli.CommandStatus.PENDING.value)
        completed = session.commands_by_status(c.Cli.CommandStatus.COMPLETED.value)

        assert isinstance(pending, list)
        assert isinstance(completed, list)
        assert len(pending) == 1
        assert len(completed) == 1
        assert pending[0].name == "cmd1"
        assert completed[0].name == "cmd2"

    @pytest.mark.parametrize("commands_count", [1, 5, 10, 50])
    def test_session_with_multiple_commands(self, commands_count: int) -> None:
        """Test session creation with multiple commands."""
        commands = [
            create_real_cli_command(name=f"cmd{i}") for i in range(commands_count)
        ]

        session = m.Cli.CliSession.model_construct(
            session_id="test-session",
            status=c.Cli.SessionStatus.ACTIVE,
            commands=commands,
        )

        assert len(session.commands) == commands_count


class TestsCliModelValidation:
    """Tests focusing on model validation edge cases."""

    def test_command_validation_rules(self) -> None:
        """Test command validation business rules."""
        # Valid command creation
        cmd = create_real_cli_command()
        assert cmd.name == "test_command"
        assert cmd.status == "pending"

        # Test that model_construct bypasses validation (expected behavior)
        cmd_custom = create_real_cli_command(name="custom", status="running")
        assert cmd_custom.name == "custom"
        assert cmd_custom.status == "running"

    def test_session_validation_rules(self) -> None:
        """Test session validation business rules."""
        # Valid session
        session = create_real_cli_session()
        assert session.status == "active"

        # Test invalid status raises error when using full validation
        with pytest.raises(ValidationError):
            m.Cli.CliSession(
                session_id="test",
                status="invalid_status",
            )


class TestsCliModelSerialization:
    """Tests for model serialization/deserialization."""

    def test_command_serialization(self) -> None:
        """Test command JSON serialization with real data."""
        cmd = create_real_cli_command()
        json_data = cmd.model_dump()

        # Verify all expected fields are present
        assert "unique_id" in json_data  # unique_id is the actual field name
        assert "name" in json_data
        assert "status" in json_data
        assert "created_at" in json_data

        # Test round-trip
        cmd_copy = m.Cli.CliCommand.model_construct(**json_data)
        assert cmd_copy.unique_id == cmd.unique_id

    def test_session_serialization(self) -> None:
        """Test session JSON serialization with real data."""
        session = create_real_cli_session()
        json_data = session.model_dump()

        assert "session_id" in json_data
        assert "status" in json_data
        assert "commands" in json_data

        # Test round-trip
        session_copy = m.Cli.CliSession.model_construct(**json_data)
        assert session_copy.session_id == session.session_id
