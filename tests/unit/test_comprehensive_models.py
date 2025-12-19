"""Comprehensive parametrized unit tests for 100% coverage."""

from datetime import datetime
from typing import Any

import pytest

from flext_cli.constants import FlextCliConstants as c
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
    def test_command_edge_cases(self, edge_case: dict[str, Any]) -> None:
        """Test command creation with comprehensive edge cases."""
        cmd = create_test_cli_command(**edge_case)

        # Verify all fields are properly set
        for key, value in edge_case.items():
            if key != "description":  # Skip test metadata
                assert getattr(cmd, key) == value

        # Verify command is valid and functional
        assert cmd.command_id.startswith("cmd-")
        assert isinstance(cmd.created_at, datetime)

    @pytest.mark.parametrize(
        "environment", ["development", "production", "staging", "test", "ci"]
    )
    def test_session_environments(self, environment: str) -> None:
        """Test session creation across all environments."""
        session = create_real_cli_session(environment=environment)
        assert session.environment == environment

        # Test computed fields
        assert session.is_active == (session.status == c.Cli.SessionStatus.ACTIVE)
        assert session.total_commands == 0  # No commands added yet

    def test_session_command_management(self) -> None:
        """Test complete session command management workflow."""
        session = create_real_cli_session()
        cmd1 = create_real_cli_command(name="cmd1")
        cmd2 = create_real_cli_command(
            name="cmd2", status=c.Cli.CommandStatus.COMPLETED
        )

        # Add commands
        session.add_command(cmd1)
        session.add_command(cmd2)

        # Verify state
        assert session.total_commands == 2
        assert session.completed_commands == 1
        assert session.pending_commands == 1

        # Test filtering
        pending = session.commands_by_status(c.Cli.CommandStatus.PENDING)
        completed = session.commands_by_status(c.Cli.CommandStatus.COMPLETED)

        assert len(pending) == 1
        assert len(completed) == 1
        assert pending[0].name == "cmd1"
        assert completed[0].name == "cmd2"

    @pytest.mark.parametrize("concurrency", [1, 5, 10, 50])
    def test_session_concurrency_limits(self, concurrency: int) -> None:
        """Test session concurrency limit handling."""
        session = create_real_cli_session(max_concurrent_commands=concurrency)
        assert session.max_concurrent_commands == concurrency

        # Add commands up to limit
        for i in range(concurrency):
            cmd = create_real_cli_command(name=f"cmd{i}")
            session.add_command(cmd)

        assert session.total_commands == concurrency
        assert session.can_add_command() == (concurrency < 50)  # Test limit logic


class TestsCliModelValidation:
    """Tests focusing on model validation edge cases."""

    def test_command_validation_rules(self) -> None:
        """Test command validation business rules."""
        # Valid command
        cmd = create_real_cli_command()
        assert cmd.name == "test_command"

        # Test timeout validation (should be positive)
        with pytest.raises(ValueError):
            create_real_cli_command(timeout=-1.0)

    def test_session_validation_rules(self) -> None:
        """Test session validation business rules."""
        session = create_real_cli_session()
        assert session.environment == "test"

        # Test concurrency validation
        with pytest.raises(ValueError):
            create_real_cli_session(max_concurrent_commands=-1)


class TestsCliModelSerialization:
    """Tests for model serialization/deserialization."""

    def test_command_serialization(self) -> None:
        """Test command JSON serialization with real data."""
        cmd = create_real_cli_command()
        json_data = cmd.model_dump()

        # Verify all expected fields are present
        assert "command_id" in json_data
        assert "name" in json_data
        assert "status" in json_data
        assert "created_at" in json_data

        # Test round-trip
        cmd_copy = m.Cli.CliCommand.model_construct(**json_data)
        assert cmd_copy.command_id == cmd.command_id

    def test_session_serialization(self) -> None:
        """Test session JSON serialization with real data."""
        session = create_real_cli_session()
        json_data = session.model_dump()

        assert "session_id" in json_data
        assert "environment" in json_data
        assert "commands" in json_data

        # Test round-trip
        session_copy = m.Cli.CliSession.model_construct(**json_data)
        assert session_copy.session_id == session.session_id
