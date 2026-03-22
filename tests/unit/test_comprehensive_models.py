"""Comprehensive parametrized unit tests for 100% coverage."""

from __future__ import annotations

from datetime import datetime

import pytest
from flext_tests import tm
from pydantic import ValidationError

from flext_cli import c, m, t
from tests._helpers import (
    create_test_cli_command,
    create_test_cli_session,
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
        cmd = create_test_cli_command(status=status)
        tm.that(cmd.status, eq=status)
        tm.that(cmd.is_pending, eq=(status == c.Cli.CommandStatus.PENDING))
        tm.that(cmd.is_running, eq=(status == c.Cli.CommandStatus.RUNNING))
        tm.that(cmd.is_completed, eq=(status == c.Cli.CommandStatus.COMPLETED))
        tm.that(cmd.is_failed, eq=(status == c.Cli.CommandStatus.FAILED))

    @pytest.mark.parametrize("edge_case", generate_edge_case_data())
    def test_command_edge_cases(self, edge_case: dict[str, t.NormalizedValue]) -> None:
        """Test command creation with comprehensive edge cases."""
        cmd = create_test_cli_command(**edge_case)
        for key, value in edge_case.items():
            if key != "description":
                attr_value: t.NormalizedValue = getattr(cmd, key)
                tm.that(attr_value, eq=value)
        tm.that("test" in (cmd.command_line or cmd.name), eq=True)
        tm.that(isinstance(cmd.created_at, datetime), eq=True)

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
        session = create_test_cli_session(status=status)
        tm.that(session.status, eq=status)
        tm.that(session.session_id is not None, eq=True)
        if hasattr(session, "commands"):
            tm.that(len(session.commands), eq=0)
        else:
            tm.that(session.commands_executed, eq=0)

    def test_session_command_filtering(self) -> None:
        """Test session command filtering by status."""
        cmd1 = create_test_cli_command(name="cmd1", status=c.Cli.CommandStatus.PENDING)
        cmd2 = create_test_cli_command(
            name="cmd2", status=c.Cli.CommandStatus.COMPLETED
        )
        session = m.Cli.CliSession.model_construct(
            session_id="test-session",
            status=c.Cli.SessionStatus.ACTIVE,
            commands=[cmd1, cmd2],
        )
        pending = session.commands_by_status(c.Cli.CommandStatus.PENDING.value)
        completed = session.commands_by_status(c.Cli.CommandStatus.COMPLETED.value)
        tm.that(isinstance(pending, list), eq=True)
        tm.that(isinstance(completed, list), eq=True)
        if isinstance(pending, list) and isinstance(completed, list):
            tm.that(len(pending), eq=1)
            tm.that(len(completed), eq=1)
            tm.that(pending[0].name, eq="cmd1")
            tm.that(completed[0].name, eq="cmd2")

    @pytest.mark.parametrize("commands_count", [1, 5, 10, 50])
    def test_session_with_multiple_commands(self, commands_count: int) -> None:
        """Test session creation with multiple commands."""
        commands = [
            create_test_cli_command(name=f"cmd{i}") for i in range(commands_count)
        ]
        session = m.Cli.CliSession.model_construct(
            session_id="test-session",
            status=c.Cli.SessionStatus.ACTIVE,
            commands=commands,
        )
        tm.that(len(session.commands), eq=commands_count)


class TestsCliModelValidation:
    """Tests focusing on model validation edge cases."""

    def test_command_validation_rules(self) -> None:
        """Test command validation business rules."""
        cmd = create_test_cli_command()
        tm.that(cmd.name, eq="test_command")
        tm.that(cmd.status, eq="pending")
        cmd_custom = create_test_cli_command(name="custom", status="running")
        tm.that(cmd_custom.name, eq="custom")
        tm.that(cmd_custom.status, eq="running")

    def test_session_validation_rules(self) -> None:
        """Test session validation business rules."""
        session = create_test_cli_session()
        tm.that(session.status, eq="active")
        with pytest.raises(ValidationError):
            m.Cli.CliSession(session_id="test", status="invalid_status")


class TestsCliModelSerialization:
    """Tests for model serialization/deserialization."""

    def test_command_serialization(self) -> None:
        """Test command JSON serialization with real data."""
        cmd = create_test_cli_command()
        json_data = cmd.model_dump()
        tm.that("unique_id" in json_data, eq=True)
        tm.that("name" in json_data, eq=True)
        tm.that("status" in json_data, eq=True)
        tm.that("created_at" in json_data, eq=True)
        cmd_copy = m.Cli.CliCommand.model_construct(**json_data)
        tm.that(cmd_copy.unique_id, eq=cmd.unique_id)

    def test_session_serialization(self) -> None:
        """Test session JSON serialization with real data."""
        session = create_test_cli_session()
        json_data = session.model_dump()
        tm.that("session_id" in json_data, eq=True)
        tm.that("status" in json_data, eq=True)
        tm.that("commands" in json_data or "commands_executed" in json_data, eq=True)
        session_copy = m.Cli.CliSession.model_construct(**json_data)
        tm.that(session_copy.session_id, eq=session.session_id)
