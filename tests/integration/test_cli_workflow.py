"""Integration tests for complete CLI workflows."""

from tests._helpers import create_test_cli_command

from flext_cli.constants import c
from flext_cli.models import m


class TestsCliWorkflowIntegration:
    """Integration tests for CLI workflows."""

    def test_command_registration_and_execution_workflow(self) -> None:
        """Test complete workflow: register command -> create session with command -> verify."""
        # Create command
        cmd = create_test_cli_command()

        # Create session with command using model_construct (frozen model)
        session = m.Cli.CliSession.model_construct(
            session_id="test-session",
            status=c.Cli.SessionStatus.ACTIVE,
            commands=[cmd],
        )

        # Verify command is in session
        assert len(session.commands) == 1
        assert session.commands[0].command_id == cmd.command_id

    def test_session_command_filtering_by_status(self) -> None:
        """Test filtering commands by status in session."""
        # Create commands with different statuses
        pending_cmd = create_test_cli_command(status=c.Cli.CommandStatus.PENDING)
        running_cmd = create_test_cli_command(
            name="running-cmd", status=c.Cli.CommandStatus.RUNNING
        )
        completed_cmd = create_test_cli_command(
            name="completed-cmd", status=c.Cli.CommandStatus.COMPLETED
        )

        # Create session with all commands
        session = m.Cli.CliSession.model_construct(
            session_id="test-session",
            status=c.Cli.SessionStatus.ACTIVE,
            commands=[pending_cmd, running_cmd, completed_cmd],
        )

        # Test filtering using status value strings
        pending = session.commands_by_status(c.Cli.CommandStatus.PENDING.value)
        running = session.commands_by_status(c.Cli.CommandStatus.RUNNING.value)
        completed = session.commands_by_status(c.Cli.CommandStatus.COMPLETED.value)

        assert len(pending) == 1
        assert len(running) == 1
        assert len(completed) == 1

    def test_end_to_end_cli_processing_workflow(self) -> None:
        """Test end-to-end CLI processing workflow."""
        # This would test the complete flow from input to output
        # Using real implementations, not mocks
