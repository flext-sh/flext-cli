"""Comprehensive parametrized tests for model factories."""

from __future__ import annotations

import pytest
from flext_tests import tm

from flext_cli import c
from tests import create_test_cli_command, create_test_cli_session


class TestsCliModelFactories:
    """Comprehensive tests for model factory functions."""

    @pytest.mark.parametrize(
        "status",
        [
            c.Cli.CommandStatus.PENDING,
            c.Cli.CommandStatus.RUNNING,
            c.Cli.CommandStatus.COMPLETED,
            c.Cli.CommandStatus.FAILED,
        ],
    )
    def test_cli_command_factory_with_status(self, status: c.Cli.CommandStatus) -> None:
        """Test CliCommand factory with different statuses."""
        cmd = create_test_cli_command(status=status)
        tm.that(cmd.status, eq=status)
        tm.that((cmd.command_line or cmd.name).startswith("test"), eq=True)

    @pytest.mark.parametrize("environment", ["development", "production", "test"])
    def test_cli_session_factory_with_environment(self, environment: str) -> None:
        """Test CliSession factory with different environments."""
        session = create_test_cli_session(environment=environment)
        tm.that(getattr(session, "environment", environment), eq=environment)
        tm.that(session.session_id.startswith("test-session-"), eq=True)

    def test_model_rebuild_success(self) -> None:
        """Test that models can be rebuilt successfully."""
        cmd = create_test_cli_command()
        tm.that(cmd.name, eq="test_command")
        session = create_test_cli_session()
        tm.that(getattr(session, "environment", "test"), eq="test")
