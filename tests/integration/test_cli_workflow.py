"""Integration tests for complete CLI workflows."""

from __future__ import annotations

from flext_cli import c, m
from tests._helpers import create_test_cli_command


class TestsCliWorkflowIntegration:
    """Integration tests for CLI workflows."""

    def test_command_registration_and_execution_workflow(self) -> None:
        """Test complete workflow: register command -> create session with command -> verify."""
        cmd = create_test_cli_command()
        session = m.Cli.CliSession.model_construct(
            session_id="test-session",
            user_id="",
            status=c.Cli.SessionStatus.ACTIVE,
            commands=(cmd,),
            start_time=None,
            end_time=None,
            last_activity=None,
            internal_duration_seconds=0.0,
            commands_executed=0,
        )
        assert len(session.commands) == 1
        assert session.commands[0].command_line == cmd.command_line

    def test_end_to_end_cli_processing_workflow(self) -> None:
        """Test end-to-end CLI processing workflow."""
