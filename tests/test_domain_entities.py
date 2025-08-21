"""Tests for domain entities in FLEXT CLI Library.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import tempfile
from datetime import UTC, datetime

from flext_cli import (
    CLICommand,
    CLIPlugin,
    CLISession,
    CommandStatus,
    CommandType,
)

# Constants
EXPECTED_BULK_SIZE = 2
EXPECTED_DATA_COUNT = 3


class TestCLICommand:
    """Test cases for CLICommand entity."""

    def test_command_creation(self, sample_command: CLICommand) -> None:
        """Test CLI command creation."""
        if sample_command.name != "test-command":
            raise AssertionError(
                f"Expected {'test-command'}, got {sample_command.name}",
            )
        assert sample_command.description == "A test command"
        if sample_command.command_type != CommandType.SYSTEM:
            raise AssertionError(
                f"Expected {CommandType.SYSTEM}, got {sample_command.command_type}",
            )
        assert sample_command.command_line == "echo hello"
        if sample_command.command_status != CommandStatus.PENDING:
            raise AssertionError(
                f"Expected {CommandStatus.PENDING}, got {sample_command.command_status}",
            )

    def test_command_execution_lifecycle(self, sample_command: CLICommand) -> None:
        """Test command execution lifecycle."""
        # Initial state
        assert not sample_command.is_completed
        assert not sample_command.successful
        assert sample_command.started_at is None

        # Start execution - immutable pattern returns FlextResult[CLICommand]
        running_result = sample_command.start_execution()
        assert running_result.success, f"Start execution failed: {running_result.error}"
        running_command = running_result.value
        assert running_command is not None
        if running_command.command_status != CommandStatus.RUNNING:
            raise AssertionError(
                f"Expected {CommandStatus.RUNNING}, got {running_command.command_status}",
            )
        assert running_command.started_at is not None
        assert not running_command.is_completed

        # Complete execution successfully - immutable pattern returns FlextResult[CLICommand]
        completed_result = running_command.complete_execution(
            exit_code=0,
            stdout="hello",
            stderr="",
        )
        assert completed_result.success, (
            f"Complete execution failed: {completed_result.error}"
        )
        completed_command = completed_result.value
        assert completed_command is not None
        if completed_command.command_status != CommandStatus.COMPLETED:
            raise AssertionError(
                f"Expected {CommandStatus.COMPLETED}, got {completed_command.command_status}",
            )
        assert completed_command.exit_code == 0
        if completed_command.stdout != "hello":
            raise AssertionError(f"Expected {'hello'}, got {completed_command.stdout}")
        assert completed_command.is_completed
        assert completed_command.successful
        assert completed_command.duration_seconds is not None

    def test_command_failed_execution(self, sample_command: CLICommand) -> None:
        """Test command failed execution."""
        # Immutable pattern - each method returns FlextResult[CLICommand]
        running_result = sample_command.start_execution()
        assert running_result.success, f"Start execution failed: {running_result.error}"
        running_command = running_result.value
        assert running_command is not None

        failed_result = running_command.complete_execution(
            exit_code=1,
            stdout="",
            stderr="Error occurred",
        )
        assert failed_result.success, (
            f"Complete execution failed: {failed_result.error}"
        )
        failed_command = failed_result.value
        assert failed_command is not None

        if failed_command.command_status != CommandStatus.FAILED:
            raise AssertionError(
                f"Expected {CommandStatus.FAILED}, got {failed_command.command_status}",
            )
        assert failed_command.exit_code == 1
        if failed_command.stderr != "Error occurred":
            raise AssertionError(
                f"Expected {'Error occurred'}, got {failed_command.stderr}",
            )
        assert failed_command.is_completed
        assert not failed_command.successful

    def test_command_cancellation_real(self) -> None:
        """Test command cancellation with real object."""
        sample_command = CLICommand(
            id="test_cmd_cancel",
            name="test-command",
            description="A test command",
            command_type=CommandType.SYSTEM,
            command_line="echo hello",
        )

        # Immutable pattern - each method returns FlextResult[CLICommand]
        running_result = sample_command.start_execution()
        assert running_result.success, f"Start execution failed: {running_result.error}"
        running_command = running_result.value
        assert running_command is not None

        cancelled_result = running_command.cancel_execution()
        assert cancelled_result.success, (
            f"Cancel execution failed: {cancelled_result.error}"
        )
        cancelled_command = cancelled_result.value
        assert cancelled_command is not None

        if cancelled_command.command_status != CommandStatus.CANCELLED:
            raise AssertionError(
                f"Expected {CommandStatus.CANCELLED}, got {cancelled_command.command_status}",
            )
        assert cancelled_command.is_completed
        assert not cancelled_command.successful
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
        assert not command.successful  # Not completed successfully

        # Test completed status
        running_result = command.start_execution()
        assert running_result.success, f"Start execution failed: {running_result.error}"
        running_command = running_result.value
        assert running_command is not None

        completed_result = running_command.complete_execution(exit_code=0)
        assert completed_result.success, (
            f"Complete execution failed: {completed_result.error}"
        )
        completed_command = completed_result.value
        assert completed_command is not None
        assert completed_command.is_completed
        assert completed_command.successful

        # Test failed status
        running_result2 = command.start_execution()
        assert running_result2.success, (
            f"Start execution failed: {running_result2.error}"
        )
        running_command2 = running_result2.value
        assert running_command2 is not None

        failed_result = running_command2.complete_execution(exit_code=1)
        assert failed_result.success, (
            f"Complete execution failed: {failed_result.error}"
        )
        failed_command = failed_result.value
        assert failed_command is not None
        assert failed_command.is_completed
        assert not failed_command.successful

    def test_duration_calculation_real(self) -> None:
        """Test duration calculation with real time implementation."""
        # Create command and start execution
        command = CLICommand(
            id="test_duration",
            name="test",
            command_line="test",
        )

        # Start execution to set started_at
        running_result = command.start_execution()
        assert running_result.success, f"Start execution failed: {running_result.error}"
        running_command = running_result.value
        assert running_command is not None
        assert running_command.started_at is not None

        # Complete execution and verify duration exists
        completed_result = running_command.complete_execution(exit_code=0)
        assert completed_result.success, (
            f"Complete execution failed: {completed_result.error}"
        )
        completed_command = completed_result.value
        assert completed_command is not None

        # Duration should be calculated and be a reasonable small value
        assert completed_command.duration_seconds is not None
        assert isinstance(completed_command.duration_seconds, (int, float))
        assert completed_command.duration_seconds >= 0.0
        # Should be very small since execution is immediate
        assert completed_command.duration_seconds < 1.0


class TestCLIPlugin:
    """Test cases for CLIPlugin entity."""

    def test_plugin_creation_real(self) -> None:
        """Test plugin creation with real object."""
        sample_plugin = CLIPlugin(
            id="test_plugin_001",
            name="test-plugin",
            entry_point="test_plugin.main",
            plugin_version="0.9.0",
            enabled=True,
            installed=False,
        )

        if sample_plugin.name != "test-plugin":
            raise AssertionError(f"Expected {'test-plugin'}, got {sample_plugin.name}")
        assert (
            sample_plugin.plugin_version == "0.9.0"
        )  # Using correct plugin_version field
        if sample_plugin.entry_point != "test_plugin.main":
            raise AssertionError(
                f"Expected {'test_plugin.main'}, got {sample_plugin.entry_point}",
            )
        if not (sample_plugin.enabled):
            raise AssertionError(f"Expected True, got {sample_plugin.enabled}")
        if sample_plugin.installed:
            raise AssertionError(f"Expected False, got {sample_plugin.installed}")

    def test_plugin_lifecycle_real(self) -> None:
        """Test plugin lifecycle operations with real object."""
        sample_plugin = CLIPlugin(
            id="test_plugin_002",
            name="test-plugin",
            entry_point="test_plugin.main",
            plugin_version="0.9.0",
            enabled=True,
            installed=False,
        )

        # Install plugin - FlextResult pattern
        install_result = sample_plugin.install()
        assert install_result.success, f"Install failed: {install_result.error}"
        installed_plugin = install_result.value
        if not (installed_plugin.installed):
            raise AssertionError(f"Expected True, got {installed_plugin.installed}")
        assert installed_plugin.enabled is True

        # Disable plugin - FlextResult pattern
        disable_result = installed_plugin.disable()
        assert disable_result.success, f"Disable failed: {disable_result.error}"
        disabled_plugin = disable_result.value
        if disabled_plugin.enabled:
            raise AssertionError(f"Expected False, got {disabled_plugin.enabled}")
        if not (disabled_plugin.installed):
            raise AssertionError(f"Expected True, got {disabled_plugin.installed}")

        # Enable plugin - FlextResult pattern
        enable_result = disabled_plugin.enable()
        assert enable_result.success, f"Enable failed: {enable_result.error}"
        enabled_plugin = enable_result.value
        if not (enabled_plugin.enabled):
            raise AssertionError(f"Expected True, got {enabled_plugin.enabled}")

        # Uninstall plugin - FlextResult pattern
        uninstall_result = enabled_plugin.uninstall()
        assert uninstall_result.success, f"Uninstall failed: {uninstall_result.error}"
        uninstalled_plugin = uninstall_result.value
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
            raise AssertionError(f"Expected {'click'} in {plugin.dependencies}")
        assert "rich" in plugin.dependencies
        if "requests" not in plugin.dependencies:
            raise AssertionError(f"Expected {'requests'} in {plugin.dependencies}")


class TestCLISession:
    """Test cases for CLISession entity."""

    def test_session_creation_real(self) -> None:
        """Test session creation with real object."""
        sample_session = CLISession(
            id="test_session_003",
            session_id="test-session-123",
            working_directory=tempfile.gettempdir(),
            environment={"TEST": "true"},
            active=True,
        )

        if sample_session.session_id != "test-session-123":
            raise AssertionError(
                f"Expected {'test-session-123'}, got {sample_session.session_id}",
            )
        assert sample_session.working_directory == tempfile.gettempdir()
        if sample_session.environment["TEST"] != "true":
            raise AssertionError(
                f"Expected {'true'}, got {sample_session.environment['TEST']}",
            )
        if not (sample_session.active):
            raise AssertionError(f"Expected True, got {sample_session.active}")
        if len(sample_session.commands_executed) != 0:
            raise AssertionError(
                f"Expected {0}, got {len(sample_session.commands_executed)}",
            )

    def test_session_command_tracking_real(self) -> None:
        """Test session command tracking with real object."""
        sample_session = CLISession(
            id="test_session_004",
            session_id="test-session-456",
            working_directory=tempfile.gettempdir(),
            environment={"TEST": "true"},
            active=True,
        )

        # Add commands to session
        command_id_1 = "cmd-1"
        command_id_2 = "cmd-2"

        # Sessions are immutable, so methods return FlextResult with new instances
        result1 = sample_session.add_command(command_id_1)
        assert result1.success, f"Add command failed: {result1.error}"
        session_with_cmd1 = result1.value
        if len(session_with_cmd1.commands_executed) != 1:
            raise AssertionError(
                f"Expected {1}, got {len(session_with_cmd1.commands_executed)}",
            )
        assert session_with_cmd1.current_command == command_id_1

        result2 = session_with_cmd1.add_command(command_id_2)
        assert result2.success, f"Add command failed: {result2.error}"
        session_with_cmd2 = result2.value
        if len(session_with_cmd2.commands_executed) != EXPECTED_BULK_SIZE:
            raise AssertionError(
                f"Expected {2}, got {len(session_with_cmd2.commands_executed)}",
            )
        assert session_with_cmd2.current_command == command_id_2

    def test_session_end_real(self) -> None:
        """Test session ending with real object."""
        sample_session = CLISession(
            id="test_session_005",
            session_id="test-session-789",
            working_directory=tempfile.gettempdir(),
            environment={"TEST": "true"},
            active=True,
        )

        # Sessions are immutable, so methods return FlextResult with new instances
        result1 = sample_session.add_command("cmd-1")
        assert result1.success, f"Add command failed: {result1.error}"
        session_with_command = result1.value

        result2 = session_with_command.end_session()
        assert result2.success, f"End session failed: {result2.error}"
        ended_session = result2.value

        if ended_session.active:
            raise AssertionError(f"Expected False, got {ended_session.active}")
        assert ended_session.current_command is None

    def test_session_activity_tracking_real(self) -> None:
        """Test session activity tracking with real timestamp implementation."""
        # Record time before creating session
        before_time = datetime.now(tz=UTC)

        session = CLISession(id="test_session_001", session_id="test")
        result = session.add_command("cmd-1")
        assert result.success, f"Add command failed: {result.error}"
        updated_session = result.value

        # Record time after session update
        after_time = datetime.now(tz=UTC)

        # Verify last_activity is within reasonable time range
        assert updated_session.last_activity is not None
        assert isinstance(updated_session.last_activity, datetime)
        assert before_time <= updated_session.last_activity <= after_time

        # Time difference should be very small (less than 1 second)
        time_diff = updated_session.last_activity - before_time
        assert time_diff.total_seconds() < 1.0


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
