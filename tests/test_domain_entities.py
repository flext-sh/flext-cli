"""Tests for domain entities in FLEXT CLI Library.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

# Constants
EXPECTED_BULK_SIZE = 2
EXPECTED_DATA_COUNT = 3

from datetime import UTC, datetime
from unittest.mock import patch

from flext_cli import (
    CLICommand,
    CLIPlugin,
    CLISession,
    CommandStatus,
    CommandType,
)


class TestCLICommand:
    """Test cases for CLICommand entity."""

    def test_command_creation(self, sample_command: CLICommand) -> None:
        """Test CLI command creation."""
        if sample_command.name != "test-command":
            raise AssertionError(f"Expected {"test-command"}, got {sample_command.name}")
        assert sample_command.description == "A test command"
        if sample_command.command_type != CommandType.SYSTEM:
            raise AssertionError(f"Expected {CommandType.SYSTEM}, got {sample_command.command_type}")
        assert sample_command.command_line == "echo hello"
        if sample_command.command_status != CommandStatus.PENDING:
            raise AssertionError(f"Expected {CommandStatus.PENDING}, got {sample_command.command_status}")

    def test_command_execution_lifecycle(self, sample_command: CLICommand) -> None:
        """Test command execution lifecycle."""
        # Initial state
        assert not sample_command.is_completed
        assert not sample_command.is_successful
        assert sample_command.started_at is None

        # Start execution - immutable pattern returns new instance
        running_command = sample_command.start_execution()
        if running_command.command_status != CommandStatus.RUNNING:
            raise AssertionError(f"Expected {CommandStatus.RUNNING}, got {running_command.command_status}")
        assert running_command.started_at is not None
        assert not running_command.is_completed

        # Complete execution successfully - immutable pattern returns new instance
        completed_command = running_command.complete_execution(
            exit_code=0,
            stdout="hello",
            stderr="",
        )
        if completed_command.command_status != CommandStatus.COMPLETED:
            raise AssertionError(f"Expected {CommandStatus.COMPLETED}, got {completed_command.command_status}")
        assert completed_command.exit_code == 0
        if completed_command.stdout != "hello":
            raise AssertionError(f"Expected {"hello"}, got {completed_command.stdout}")
        assert completed_command.is_completed
        assert completed_command.is_successful
        assert completed_command.duration_seconds is not None

    def test_command_failed_execution(self, sample_command: CLICommand) -> None:
        """Test command failed execution."""
        # Immutable pattern - each method returns new instance
        running_command = sample_command.start_execution()
        failed_command = running_command.complete_execution(
            exit_code=1,
            stdout="",
            stderr="Error occurred",
        )

        if failed_command.command_status != CommandStatus.FAILED:

            raise AssertionError(f"Expected {CommandStatus.FAILED}, got {failed_command.command_status}")
        assert failed_command.exit_code == 1
        if failed_command.stderr != "Error occurred":
            raise AssertionError(f"Expected {"Error occurred"}, got {failed_command.stderr}")
        assert failed_command.is_completed
        assert not failed_command.is_successful

    def test_command_cancellation(self, sample_command: CLICommand) -> None:
        """Test command cancellation."""
        # Immutable pattern - each method returns new instance
        running_command = sample_command.start_execution()
        cancelled_command = running_command.cancel_execution()

        if cancelled_command.command_status != CommandStatus.CANCELLED:

            raise AssertionError(f"Expected {CommandStatus.CANCELLED}, got {cancelled_command.command_status}")
        assert cancelled_command.is_completed
        assert not cancelled_command.is_successful
        assert cancelled_command.duration_seconds is not None

    def test_command_status_properties(self) -> None:
        """Test command status properties."""
        command = CLICommand(
            id="test_cmd_status",
            name="test",
            command_line="test",
        )

        # Test status properties based on initial state
        assert not command.is_completed  # PENDING is not completed
        assert not command.is_successful  # Not completed successfully

        # Test completed status
        completed_command = command.complete_execution(exit_code=0)
        assert completed_command.is_completed
        assert completed_command.is_successful

        # Test failed status
        failed_command = command.complete_execution(exit_code=1)
        assert failed_command.is_completed
        assert not failed_command.is_successful

    @patch("flext_cli.domain.entities.datetime")
    def test_duration_calculation(self, mock_datetime: any) -> None:
        """Test duration calculation."""
        start_time = datetime(2025, 1, 1, 10, 0, 0, tzinfo=UTC)
        end_time = datetime(2025, 1, 1, 10, 0, 5, tzinfo=UTC)  # 5 seconds later

        mock_datetime.now.side_effect = [start_time, end_time]

        command = CLICommand(id="test_duration", name="test", command_line="test")
        # Immutable pattern - use returned instances
        running_command = command.start_execution()
        completed_command = running_command.complete_execution(exit_code=0)

        if completed_command.duration_seconds != 5.0:

            raise AssertionError(f"Expected {5.0}, got {completed_command.duration_seconds}")


class TestCLIPlugin:
    """Test cases for CLIPlugin entity."""

    def test_plugin_creation(self, sample_plugin: CLIPlugin) -> None:
        """Test plugin creation."""
        if sample_plugin.name != "test-plugin":
            raise AssertionError(f"Expected {"test-plugin"}, got {sample_plugin.name}")
        assert sample_plugin.version == "0.8.0"  # Corrected version
        if sample_plugin.entry_point != "test_plugin.main":
            raise AssertionError(f"Expected {"test_plugin.main"}, got {sample_plugin.entry_point}")
        if not (sample_plugin.enabled):
            raise AssertionError(f"Expected True, got {sample_plugin.enabled}")
        if sample_plugin.installed:
            raise AssertionError(f"Expected False, got {sample_plugin.installed}")

    def test_plugin_lifecycle(self, sample_plugin: CLIPlugin) -> None:
        """Test plugin lifecycle operations."""
        # Install plugin - immutable pattern returns new instance
        installed_plugin = sample_plugin.install()
        if not (installed_plugin.installed):
            raise AssertionError(f"Expected True, got {installed_plugin.installed}")
        assert installed_plugin.enabled is True

        # Disable plugin - immutable pattern returns new instance
        disabled_plugin = installed_plugin.disable()
        if disabled_plugin.enabled:
            raise AssertionError(f"Expected False, got {disabled_plugin.enabled}")
        if not (disabled_plugin.installed):
            raise AssertionError(f"Expected True, got {disabled_plugin.installed}")

        # Enable plugin - immutable pattern returns new instance
        enabled_plugin = disabled_plugin.enable()
        if not (enabled_plugin.enabled):
            raise AssertionError(f"Expected True, got {enabled_plugin.enabled}")

        # Uninstall plugin - immutable pattern returns new instance
        uninstalled_plugin = enabled_plugin.uninstall()
        if uninstalled_plugin.installed:
            raise AssertionError(f"Expected False, got {uninstalled_plugin.installed}")
        assert uninstalled_plugin.enabled is False

    def test_plugin_with_dependencies(self) -> None:
        """Test plugin with dependencies."""
        plugin = CLIPlugin(
            id="complex_plugin_001",
            name="complex-plugin",
            entry_point="complex.main",
            dependencies=["click", "rich", "requests"],
        )

        if len(plugin.dependencies) != EXPECTED_DATA_COUNT:

            raise AssertionError(f"Expected {3}, got {len(plugin.dependencies)}")
        if "click" not in plugin.dependencies:
            raise AssertionError(f"Expected {"click"} in {plugin.dependencies}")
        assert "rich" in plugin.dependencies
        if "requests" not in plugin.dependencies:
            raise AssertionError(f"Expected {"requests"} in {plugin.dependencies}")


class TestCLISession:
    """Test cases for CLISession entity."""

    def test_session_creation(self, sample_session: CLISession) -> None:
        """Test session creation."""
        if sample_session.session_id != "test-session-123":
            raise AssertionError(f"Expected {"test-session-123"}, got {sample_session.session_id}")
        assert sample_session.working_directory == "/tmp"
        if sample_session.environment["TEST"] != "true":
            raise AssertionError(f"Expected {"true"}, got {sample_session.environment["TEST"]}")
        if not (sample_session.active):
            raise AssertionError(f"Expected True, got {sample_session.active}")
        if len(sample_session.commands_executed) != 0:
            raise AssertionError(f"Expected {0}, got {len(sample_session.commands_executed)}")

    def test_session_command_tracking(self, sample_session: CLISession) -> None:
        """Test session command tracking."""
        # Add commands to session
        command_id_1 = "cmd-1"
        command_id_2 = "cmd-2"

        # Sessions are immutable, so methods return new instances
        session_with_cmd1 = sample_session.add_command(command_id_1)
        if len(session_with_cmd1.commands_executed) != 1:
            raise AssertionError(f"Expected {1}, got {len(session_with_cmd1.commands_executed)}")
        assert session_with_cmd1.current_command == command_id_1

        session_with_cmd2 = session_with_cmd1.add_command(command_id_2)
        if len(session_with_cmd2.commands_executed) != EXPECTED_BULK_SIZE:
            raise AssertionError(f"Expected {2}, got {len(session_with_cmd2.commands_executed)}")
        assert session_with_cmd2.current_command == command_id_2

    def test_session_end(self, sample_session: CLISession) -> None:
        """Test session ending."""
        # Sessions are immutable, so methods return new instances
        session_with_command = sample_session.add_command("cmd-1")
        ended_session = session_with_command.end_session()

        if ended_session.active:

            raise AssertionError(f"Expected False, got {ended_session.active}")
        assert ended_session.current_command is None

    @patch("flext_cli.domain.entities.datetime")
    def test_session_activity_tracking(self, mock_datetime: any) -> None:
        """Test session activity tracking."""
        activity_time = datetime(2025, 1, 1, 12, 0, 0)
        mock_datetime.now.return_value = activity_time

        session = CLISession(id="test_session_001", session_id="test")
        updated_session = session.add_command("cmd-1")

        if updated_session.last_activity != activity_time:

            raise AssertionError(f"Expected {activity_time}, got {updated_session.last_activity}")


class TestCommandStatus:
    """Test CommandStatus enum."""

    def test_all_statuses(self) -> None:
        """Test all command statuses."""
        statuses = [
            CommandStatus.PENDING,
            CommandStatus.RUNNING,
            CommandStatus.COMPLETED,
            CommandStatus.FAILED,
            CommandStatus.CANCELLED,
        ]

        for status in statuses:
            assert isinstance(status, CommandStatus)
            assert isinstance(status.value, str)


class TestCommandType:
    """Test CommandType enum."""

    def test_all_types(self) -> None:
        """Test all command types."""
        types = [
            CommandType.SYSTEM,
            CommandType.PIPELINE,
            CommandType.PLUGIN,
            CommandType.DATA,
            CommandType.CONFIG,
            CommandType.AUTH,
            CommandType.MONITORING,
        ]

        for cmd_type in types:
            assert isinstance(cmd_type, CommandType)
            assert isinstance(cmd_type.value, str)
