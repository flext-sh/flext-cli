"""Integration tests for complete CLI workflows."""

from tests._helpers import create_test_cli_command, create_test_cli_session

from flext_cli.constants import FlextCliConstants as c


class TestsCliWorkflowIntegration:
    """Integration tests for CLI workflows."""

    def test_command_registration_and_execution_workflow(self) -> None:
        """Test complete workflow: register command -> execute -> verify results."""
        # Create command and session
        cmd = create_test_cli_command()
        session = create_test_cli_session()

        # Add command to session
        session.add_command(cmd)

        # Verify command is in session
        assert len(session.commands) == 1
        assert session.commands[0].command_id == cmd.command_id

        # Test computed fields
        assert session.total_commands == 1
        assert session.completed_commands == 0

    def test_session_command_filtering_by_status(self) -> None:
        """Test filtering commands by status in session."""
        session = create_test_cli_session()

        # Add commands with different statuses
        pending_cmd = create_test_cli_command(status=c.Cli.CommandStatus.PENDING)
        running_cmd = create_test_cli_command(
            command_id="running-123", status=c.Cli.CommandStatus.RUNNING
        )
        completed_cmd = create_test_cli_command(
            command_id="completed-123", status=c.Cli.CommandStatus.COMPLETED
        )

        session.add_command(pending_cmd)
        session.add_command(running_cmd)
        session.add_command(completed_cmd)

        # Test filtering
        pending = session.commands_by_status(c.Cli.CommandStatus.PENDING)
        running = session.commands_by_status(c.Cli.CommandStatus.RUNNING)
        completed = session.commands_by_status(c.Cli.CommandStatus.COMPLETED)

        assert len(pending) == 1
        assert len(running) == 1
        assert len(completed) == 1

    def test_end_to_end_cli_processing_workflow(self) -> None:
        """Test end-to-end CLI processing workflow."""
        # This would test the complete flow from input to output
        # Using real implementations, not mocks
