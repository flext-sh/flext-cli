"""Comprehensive parametrized unit tests for 100% coverage."""

from __future__ import annotations

from datetime import datetime

import pytest
from flext_tests import tm

from flext_cli import c, m, t
from tests._helpers import (
    create_test_cli_command,
    create_test_cli_session,
    generate_edge_case_data,
)


class TestsCliComprehensiveModels:
    """Comprehensive tests covering all model functionality with real data."""

    @pytest.mark.parametrize("edge_case", generate_edge_case_data())
    def test_command_edge_cases(self, edge_case: t.ContainerMapping) -> None:
        """Test command creation with comprehensive edge cases."""
        cmd = create_test_cli_command(**edge_case)  # type: ignore[arg-type]
        for key, value in edge_case.items():
            if key != "description":
                attr_value: t.NormalizedValue = getattr(cmd, key)
                tm.that(attr_value, eq=value)
        tm.that((cmd.command_line or cmd.name), has="test")
        tm.that(cmd.created_at, is_=datetime)

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
        tm.that(session.session_id, none=False)
        if hasattr(session, "commands"):
            tm.that(len(session.commands), eq=0)
        else:
            tm.that(session.commands_executed, eq=0)

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


class TestsCliModelSerialization:
    """Tests for model serialization/deserialization."""

    def test_command_serialization(self) -> None:
        """Test command JSON serialization with real data."""
        cmd = create_test_cli_command()
        json_data = cmd.model_dump()
        tm.that(json_data, has="unique_id")
        tm.that(json_data, has="name")
        tm.that(json_data, has="status")
        tm.that(json_data, has="created_at")
        cmd_copy = m.Cli.CliCommand.model_construct(**json_data)
        tm.that(cmd_copy.unique_id, eq=cmd.unique_id)

    def test_session_serialization(self) -> None:
        """Test session JSON serialization with real data."""
        session = create_test_cli_session()
        json_data = session.model_dump()
        tm.that(json_data, has="session_id")
        tm.that(json_data, has="status")
        tm.that("commands" in json_data or "commands_executed" in json_data, eq=True)
        session_copy = m.Cli.CliSession.model_construct(**json_data)
        tm.that(session_copy.session_id, eq=session.session_id)
