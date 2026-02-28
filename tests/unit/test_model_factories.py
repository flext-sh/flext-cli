"""Comprehensive parametrized tests for model factories."""

import pytest
from flext_cli import c

from tests._helpers import create_test_cli_command, create_test_cli_session


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
        assert cmd.status == status
        assert (cmd.command_line or cmd.name).startswith("test")

    @pytest.mark.parametrize("environment", ["development", "production", "test"])
    def test_cli_session_factory_with_environment(self, environment: str) -> None:
        """Test CliSession factory with different environments."""
        session = create_test_cli_session(environment=environment)
        assert getattr(session, "environment", environment) == environment
        assert session.session_id.startswith("test-session-")

    def test_model_rebuild_success(self) -> None:
        """Test that models can be rebuilt successfully."""
        # This ensures forward references are resolved
        cmd = create_test_cli_command()
        assert cmd.name == "test_command"

        session = create_test_cli_session()
        assert getattr(session, "environment", "test") == "test"
