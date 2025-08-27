"""Comprehensive tests for models.py to maximize coverage.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import tempfile
from datetime import UTC, datetime
from pathlib import Path

# unittest.mock import removed - using real functionality tests instead
import pytest
from pydantic_core import ValidationError

from flext_cli.cli_types import FlextCliOutputFormat
from flext_cli.context import FlextCliContext
from flext_cli.models import (
    MAX_EXIT_CODE,
    MAX_TIMEOUT_SECONDS,
    MIN_EXIT_CODE,
    CommandStatus,
    FlextCliCommand,
    FlextCliCommandStatus,
    FlextCliCommandType,
    FlextCliConfiguration,
    FlextCliOutput,
    FlextCliPlugin,
    FlextCliPluginState,
    FlextCliSession,
    FlextCliSessionState,
    FlextCliWorkspace,
    PluginStatus,
    SessionStatus,
    _now_utc,
)


class TestUtilityFunctions:
    """Test utility functions."""

    def test_now_utc(self) -> None:
        """Test _now_utc utility function."""
        result = _now_utc()
        assert isinstance(result, datetime)
        assert result.tzinfo == UTC


class TestConstants:
    """Test constants."""

    def test_constants_defined(self) -> None:
        """Test constants are properly defined."""
        assert MAX_TIMEOUT_SECONDS == 60 * 60 * 24  # 24 hours
        assert MIN_EXIT_CODE == 0
        assert MAX_EXIT_CODE == 255


class TestEnumerations:
    """Test enumeration classes."""

    def test_flext_cli_command_type_values(self) -> None:
        """Test all command type values."""
        assert FlextCliCommandType.SYSTEM == "system"
        assert FlextCliCommandType.PIPELINE == "pipeline"
        assert FlextCliCommandType.PLUGIN == "plugin"
        assert FlextCliCommandType.DATA == "data"
        assert FlextCliCommandType.CONFIG == "config"
        assert FlextCliCommandType.AUTH == "auth"
        assert FlextCliCommandType.MONITORING == "monitoring"
        assert FlextCliCommandType.CLI == "cli"
        assert FlextCliCommandType.SCRIPT == "script"
        assert FlextCliCommandType.SQL == "sql"

    def test_flext_cli_command_status_values(self) -> None:
        """Test all command status values."""
        assert FlextCliCommandStatus.PENDING == "pending"
        assert FlextCliCommandStatus.RUNNING == "running"
        assert FlextCliCommandStatus.COMPLETED == "completed"
        assert FlextCliCommandStatus.FAILED == "failed"
        assert FlextCliCommandStatus.CANCELLED == "cancelled"

    def test_flext_cli_session_state_values(self) -> None:
        """Test all session state values."""
        assert FlextCliSessionState.ACTIVE == "active"
        assert FlextCliSessionState.IDLE == "idle"
        assert FlextCliSessionState.SUSPENDED == "suspended"
        assert FlextCliSessionState.COMPLETED == "completed"
        assert FlextCliSessionState.TERMINATED == "terminated"
        assert FlextCliSessionState.ERROR == "error"

    def test_flext_cli_plugin_state_values(self) -> None:
        """Test all plugin state values."""
        assert FlextCliPluginState.UNLOADED == "unloaded"
        assert FlextCliPluginState.LOADING == "loading"
        assert FlextCliPluginState.LOADED == "loaded"
        assert FlextCliPluginState.ACTIVE == "active"
        assert FlextCliPluginState.DISABLED == "disabled"
        assert FlextCliPluginState.ERROR == "error"

    def test_plugin_status_values(self) -> None:
        """Test plugin status enumeration."""
        assert PluginStatus.INACTIVE == "inactive"
        assert PluginStatus.UNLOADED == "unloaded"
        assert PluginStatus.LOADING == "loading"
        assert PluginStatus.LOADED == "loaded"
        assert PluginStatus.ACTIVE == "active"
        assert PluginStatus.DISABLED == "disabled"
        assert PluginStatus.ERROR == "error"

    def test_flext_cli_output_format_values(self) -> None:
        """Test all output format values."""
        assert FlextCliOutputFormat.JSON == "json"
        assert FlextCliOutputFormat.CSV == "csv"
        assert FlextCliOutputFormat.YAML == "yaml"
        assert FlextCliOutputFormat.TABLE == "table"
        assert FlextCliOutputFormat.PLAIN == "plain"

    def test_status_aliases(self) -> None:
        """Test status enumeration aliases."""
        assert CommandStatus == FlextCliCommandStatus
        assert SessionStatus == FlextCliSessionState


class TestFlextCliContext:
    """Test FlextCliContext value object."""

    def test_context_creation_minimal(self) -> None:
        """Test creating context with minimal fields."""
        context = FlextCliContext()

        assert context.config is not None
        assert context.console is not None
        assert context.working_directory is None
        assert context.user_id is None
        assert context.session_id is None
        assert context.timeout_seconds == 300
        assert isinstance(context.environment_variables, dict)
        assert isinstance(context.configuration, dict)

    def test_context_creation_with_data(self) -> None:
        """Test creating context with data."""
        with tempfile.TemporaryDirectory() as temp_dir:
            context = FlextCliContext(
                working_directory=Path(temp_dir),
                environment_variables={"TEST": "value"},
                user_id="test-user",
                session_id="test-session",
                configuration={"key": "value"},
                timeout_seconds=600,
            )

            assert context.working_directory == Path(temp_dir)
            assert context.environment_variables == {"TEST": "value"}
            assert context.user_id == "test-user"
            assert context.session_id == "test-session"
            assert context.configuration == {"key": "value"}
            assert context.timeout_seconds == 600

    def test_context_validation_invalid_working_directory(self) -> None:
        """Test context validation with invalid working directory."""
        with pytest.raises(ValueError, match="Working directory does not exist"):
            FlextCliContext(working_directory=Path("/nonexistent/path"))

    def test_context_validation_empty_user_id(self) -> None:
        """Test context validation with empty user ID."""
        with pytest.raises(ValueError, match="User ID cannot be empty string"):
            FlextCliContext(user_id="   ")

    def test_context_validation_whitespace_user_id(self) -> None:
        """Test context validation strips whitespace from user ID."""
        context = FlextCliContext(user_id="  test-user  ")
        assert context.user_id == "test-user"

    def test_context_properties(self) -> None:
        """Test context convenience properties."""
        context = FlextCliContext()

        # Properties should default to False when config has no debug/quiet
        assert context.is_debug is False
        assert context.is_quiet is False

    def test_context_with_environment(self) -> None:
        """Test context with_environment method."""
        context = FlextCliContext(environment_variables={"EXISTING": "value"})

        new_context = context.with_environment(NEW="new_value", OTHER="other")

        assert new_context.environment_variables == {
            "EXISTING": "value",
            "NEW": "new_value",
            "OTHER": "other",
        }
        # Original context unchanged
        assert context.environment_variables == {"EXISTING": "value"}

    def test_context_with_working_directory(self) -> None:
        """Test context with_working_directory method."""
        context = FlextCliContext()

        with tempfile.TemporaryDirectory() as temp_dir:
            new_context = context.with_working_directory(Path(temp_dir))

            assert new_context.working_directory == Path(temp_dir)
            assert context.working_directory is None

    def test_context_validate_business_rules_success(self) -> None:
        """Test context business rules validation success."""
        context = FlextCliContext(timeout_seconds=300)

        result = context.validate_business_rules()

        assert result.is_success

    def test_context_validate_business_rules_timeout_exceeded(self) -> None:
        """Test context business rules validation with timeout exceeded."""
        context = FlextCliContext(timeout_seconds=MAX_TIMEOUT_SECONDS + 1)

        result = context.validate_business_rules()

        assert not result.is_success
        assert "timeout" in result.error.lower()


class TestFlextCliOutput:
    """Test FlextCliOutput value object."""

    def test_output_creation_minimal(self) -> None:
        """Test creating output with minimal fields."""
        output = FlextCliOutput()

        assert output.stdout == ""
        assert output.stderr == ""
        assert output.exit_code is None
        assert output.execution_time_seconds is None
        assert output.output_format == FlextCliOutputFormat.PLAIN
        assert isinstance(output.metadata, dict)
        assert isinstance(output.captured_at, datetime)

    def test_output_creation_with_data(self) -> None:
        """Test creating output with data."""
        now = datetime.now(UTC)

        output = FlextCliOutput(
            stdout="test output",
            stderr="test error",
            exit_code=0,
            execution_time_seconds=1.5,
            output_format=FlextCliOutputFormat.JSON,
            metadata={"key": "value"},
            captured_at=now,
        )

        assert output.stdout == "test output"
        assert output.stderr == "test error"
        assert output.exit_code == 0
        assert output.execution_time_seconds == 1.5
        assert output.output_format == FlextCliOutputFormat.JSON
        assert output.metadata == {"key": "value"}
        assert output.captured_at == now

    def test_output_properties_success(self) -> None:
        """Test output properties for successful execution."""
        output = FlextCliOutput(exit_code=0, stdout="output", stderr="")

        assert output.is_success is True
        assert output.is_error is False
        assert output.has_output is True

    def test_output_properties_error(self) -> None:
        """Test output properties for failed execution."""
        output = FlextCliOutput(exit_code=1, stdout="", stderr="error")

        assert output.is_success is False
        assert output.is_error is True
        assert output.has_output is True

    def test_output_properties_no_output(self) -> None:
        """Test output properties with no output."""
        output = FlextCliOutput(exit_code=0, stdout="", stderr="")

        assert output.is_success is True
        assert output.is_error is False
        assert output.has_output is False

    def test_output_validate_business_rules_success(self) -> None:
        """Test output business rules validation success."""
        output = FlextCliOutput(exit_code=0, execution_time_seconds=1.0)

        result = output.validate_business_rules()

        assert result.is_success

    def test_output_validate_business_rules_invalid_exit_code(self) -> None:
        """Test output business rules validation with invalid exit code."""
        output = FlextCliOutput(exit_code=MAX_EXIT_CODE + 1)

        result = output.validate_business_rules()

        assert not result.is_success

    def test_output_validate_business_rules_negative_time(self) -> None:
        """Test output business rules validation with negative execution time."""
        output = FlextCliOutput(execution_time_seconds=-1.0)

        result = output.validate_business_rules()

        assert not result.is_success

    def test_output_format_output_json(self) -> None:
        """Test format_output method with JSON format."""
        output = FlextCliOutput(
            stdout="test output",
            stderr="test error",
            exit_code=0,
            execution_time_seconds=1.5,
            output_format=FlextCliOutputFormat.JSON,
        )

        formatted = output.format_output()

        assert "stdout" in formatted
        assert "stderr" in formatted
        assert "exit_code" in formatted
        assert "execution_time" in formatted

    def test_output_format_output_plain(self) -> None:
        """Test format_output method with plain format."""
        output = FlextCliOutput(
            stdout="test output",
            stderr="test error",
            exit_code=0,
            output_format=FlextCliOutputFormat.PLAIN,
        )

        formatted = output.format_output()

        assert "STDOUT:" in formatted
        assert "STDERR:" in formatted
        assert "EXIT CODE: 0" in formatted

    def test_output_format_output_empty_streams(self) -> None:
        """Test format_output method with empty streams."""
        output = FlextCliOutput(stdout="", stderr="", exit_code=0)

        formatted = output.format_output()

        assert "EXIT CODE: 0" in formatted
        assert "STDOUT:" not in formatted
        assert "STDERR:" not in formatted


class TestFlextCliConfiguration:
    """Test FlextCliConfiguration value object."""

    def test_configuration_creation_minimal(self) -> None:
        """Test creating configuration with minimal fields."""
        config = FlextCliConfiguration()

        assert config.profile_name == "default"
        assert config.log_level == "INFO"
        assert config.default_timeout == 300
        assert config.output_format == FlextCliOutputFormat.TABLE
        assert config.config_file_path is None
        assert config.cache_directory is None
        assert isinstance(config.plugin_directories, list)
        assert isinstance(config.environment_overrides, dict)
        assert isinstance(config.features_enabled, list)

    def test_configuration_creation_with_data(self) -> None:
        """Test creating configuration with data."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = FlextCliConfiguration(
                profile_name="production",
                log_level="DEBUG",
                default_timeout=600,
                output_format=FlextCliOutputFormat.JSON,
                config_file_path=Path(temp_dir) / "config.yaml",
                cache_directory=Path(temp_dir) / "cache",
                plugin_directories=[Path(temp_dir)],
                environment_overrides={"ENV": "prod"},
                features_enabled=["feature1", "feature2"],
            )

            assert config.profile_name == "production"
            assert config.log_level == "DEBUG"
            assert config.default_timeout == 600
            assert config.output_format == FlextCliOutputFormat.JSON
            assert config.config_file_path == Path(temp_dir) / "config.yaml"
            assert config.cache_directory == Path(temp_dir) / "cache"
            assert config.plugin_directories == [Path(temp_dir)]
            assert config.environment_overrides == {"ENV": "prod"}
            assert config.features_enabled == ["feature1", "feature2"]

    def test_configuration_validate_log_level_valid(self) -> None:
        """Test configuration log level validation with valid levels."""
        for level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            config = FlextCliConfiguration(log_level=level)
            assert config.log_level == level.upper()

    def test_configuration_validate_log_level_invalid(self) -> None:
        """Test configuration log level validation with invalid level."""
        with pytest.raises(ValueError, match="Log level must be one of"):
            FlextCliConfiguration(log_level="INVALID")

    def test_configuration_validate_profile_name_valid(self) -> None:
        """Test configuration profile name validation with valid names."""
        valid_names = ["default", "prod", "dev-1", "test_env"]
        for name in valid_names:
            config = FlextCliConfiguration(profile_name=name)
            assert config.profile_name == name

    def test_configuration_validate_profile_name_invalid(self) -> None:
        """Test configuration profile name validation with invalid name."""
        with pytest.raises(ValueError, match="must contain only alphanumeric"):
            FlextCliConfiguration(profile_name="invalid@name")

    def test_configuration_is_feature_enabled(self) -> None:
        """Test is_feature_enabled method."""
        config = FlextCliConfiguration(features_enabled=["feature1", "feature2"])

        assert config.is_feature_enabled("feature1") is True
        assert config.is_feature_enabled("feature3") is False

    def test_configuration_with_feature(self) -> None:
        """Test with_feature method."""
        config = FlextCliConfiguration(features_enabled=["feature1"])

        new_config = config.with_feature("feature2")

        assert "feature2" in new_config.features_enabled
        assert "feature1" in new_config.features_enabled
        # Original config unchanged
        assert config.features_enabled == ["feature1"]

    def test_configuration_with_feature_duplicate(self) -> None:
        """Test with_feature method with duplicate feature."""
        config = FlextCliConfiguration(features_enabled=["feature1"])

        new_config = config.with_feature("feature1")

        # Should not create duplicates
        assert new_config.features_enabled.count("feature1") == 1

    def test_configuration_validate_business_rules_success(self) -> None:
        """Test configuration business rules validation success."""
        config = FlextCliConfiguration()

        result = config.validate_business_rules()

        assert result.is_success

    def test_configuration_validate_business_rules_invalid_config_path(self) -> None:
        """Test configuration business rules validation with invalid config path."""
        config = FlextCliConfiguration(
            config_file_path=Path("/nonexistent/directory/config.yaml")
        )

        result = config.validate_business_rules()

        assert not result.is_success
        assert "Config file directory does not exist" in result.error

    def test_configuration_validate_business_rules_invalid_plugin_dir(self) -> None:
        """Test configuration business rules validation with invalid plugin directory."""
        config = FlextCliConfiguration(
            plugin_directories=[Path("/nonexistent/plugins")]
        )

        result = config.validate_business_rules()

        assert not result.is_success
        assert "Plugin directory does not exist" in result.error


class TestFlextCliCommand:
    """Test FlextCliCommand entity."""

    def test_command_creation_minimal(self) -> None:
        """Test creating command with minimal fields."""
        command = FlextCliCommand(id="test-cmd", command_line="echo hello")

        assert command.command_line == "echo hello"
        assert command.status == FlextCliCommandStatus.PENDING
        assert str(command.id) == "test-cmd"  # id is FlextEntityId type
        assert command.name is None
        assert command.description is None
        assert isinstance(command.arguments, (list, dict))
        assert command.context is None

    def test_command_creation_with_data(self) -> None:
        """Test creating command with full data."""
        now = datetime.now(UTC)
        context = FlextCliContext()

        command = FlextCliCommand(
            id="cmd-full-test",
            name="test-command",
            description="Test command",
            command_line="echo hello world",
            arguments=["hello", "world"],
            status=FlextCliCommandStatus.RUNNING,
            context=context,
            command_type=FlextCliCommandType.SYSTEM,
            output="hello world",
            stderr="",
            exit_code=0,
            started_at=now,
            completed_at=now,
            process_id=12345,
        )

        assert command.name == "test-command"
        assert command.description == "Test command"
        assert command.command_line == "echo hello world"
        assert command.arguments == ["hello", "world"]
        assert command.status == FlextCliCommandStatus.RUNNING
        assert command.context == context
        assert command.command_type == FlextCliCommandType.SYSTEM
        assert command.output == "hello world"
        assert command.stderr == ""
        assert command.exit_code == 0
        assert command.started_at == now
        assert command.completed_at == now
        assert command.process_id == 12345

    def test_command_command_type_coercion(self) -> None:
        """Test command type coercion from different inputs."""
        # From string
        command1 = FlextCliCommand(
            id="test-cmd", command_line="test", command_type="system"
        )
        assert command1.command_type == FlextCliCommandType.SYSTEM

        # From enum
        command2 = FlextCliCommand(
            id="test-cmd",
            command_line="test",
            command_type=FlextCliCommandType.PIPELINE,
        )
        assert command2.command_type == FlextCliCommandType.PIPELINE

    def test_command_command_type_coercion_invalid(self) -> None:
        """Test command type coercion with invalid input."""
        with pytest.raises(ValueError, match="Invalid command_type"):
            FlextCliCommand(id="test-cmd", command_line="test", command_type="invalid")

    def test_command_is_terminal_state(self) -> None:
        """Test is_terminal_state property."""
        # Non-terminal states
        pending = FlextCliCommand(
            id="test-cmd", command_line="test", status=FlextCliCommandStatus.PENDING
        )
        running = FlextCliCommand(
            id="test-cmd", command_line="test", status=FlextCliCommandStatus.RUNNING
        )

        assert not pending.is_terminal_state
        assert not running.is_terminal_state

        # Terminal states
        completed = FlextCliCommand(
            id="test-cmd", command_line="test", status=FlextCliCommandStatus.COMPLETED
        )
        failed = FlextCliCommand(
            id="test-cmd", command_line="test", status=FlextCliCommandStatus.FAILED
        )
        cancelled = FlextCliCommand(
            id="test-cmd", command_line="test", status=FlextCliCommandStatus.CANCELLED
        )

        assert completed.is_terminal_state
        assert failed.is_terminal_state
        assert cancelled.is_terminal_state

    def test_command_execution_duration(self) -> None:
        """Test execution_duration property."""
        start = datetime.now(UTC)
        end = start.replace(second=start.second + 5)  # 5 seconds later

        command = FlextCliCommand(
            command_line="test", started_at=start, completed_at=end
        )

        assert command.execution_duration == 5.0

    def test_command_execution_duration_none(self) -> None:
        """Test execution_duration property with missing timestamps."""
        command = FlextCliCommand(id="test-cmd", command_line="test")

        assert command.execution_duration is None

    def test_command_validate_business_rules_success(self) -> None:
        """Test command business rules validation success."""
        command = FlextCliCommand(id="test-cmd", command_line="echo test")

        result = command.validate_business_rules()

        assert result.is_success

    def test_command_validate_business_rules_empty_command_line(self) -> None:
        """Test command business rules validation - Pydantic prevents empty command lines."""
        # Pydantic validation prevents creating commands with empty/whitespace command_line
        with pytest.raises(ValidationError):
            FlextCliCommand(id="test-cmd", command_line="   ")

    def test_command_validate_business_rules_invalid_timestamps(self) -> None:
        """Test command business rules validation with invalid timestamps."""
        start = datetime.now(UTC)
        end = start.replace(second=start.second - 5)  # 5 seconds before start

        command = FlextCliCommand(
            command_line="test", started_at=start, completed_at=end
        )

        result = command.validate_business_rules()

        assert not result.is_success

    def test_command_validate_business_rules_running_without_start(self) -> None:
        """Test command business rules validation for running without start time."""
        command = FlextCliCommand(
            command_line="test", status=FlextCliCommandStatus.RUNNING, started_at=None
        )

        result = command.validate_business_rules()

        assert not result.is_success

    def test_command_validate_business_rules_terminal_without_completion(self) -> None:
        """Test command business rules validation for terminal state without completion."""
        command = FlextCliCommand(
            command_line="test",
            status=FlextCliCommandStatus.COMPLETED,
            completed_at=None,
        )

        result = command.validate_business_rules()

        assert not result.is_success

    def test_command_convenience_properties(self) -> None:
        """Test command convenience properties."""
        running_cmd = FlextCliCommand(
            command_line="test", status=FlextCliCommandStatus.RUNNING
        )
        completed_cmd = FlextCliCommand(
            command_line="test", status=FlextCliCommandStatus.COMPLETED, exit_code=0
        )
        failed_cmd = FlextCliCommand(
            command_line="test", status=FlextCliCommandStatus.FAILED, exit_code=1
        )

        assert running_cmd.flext_cli_is_running is True
        assert running_cmd.is_running is True
        assert completed_cmd.flext_cli_successful is True
        assert completed_cmd.successful is True
        assert failed_cmd.flext_cli_successful is False

    def test_command_start_execution_convenience(self) -> None:
        """Test command flext_cli_start_execution convenience method."""
        command = FlextCliCommand(id="test-cmd", command_line="test")

        result = command.flext_cli_start_execution()

        assert result is True
        assert command.started_at is not None

        # Second call should return False
        result2 = command.flext_cli_start_execution()
        assert result2 is False

    def test_command_complete_execution_convenience(self) -> None:
        """Test command flext_cli_complete_execution convenience method."""
        command = FlextCliCommand(id="test-cmd", command_line="test")

        result = command.flext_cli_complete_execution(
            exit_code=0, stdout="output", stderr="error"
        )

        assert result is True
        assert command.output == "output"
        assert command.stderr == "error"
        assert command.exit_code == 0
        assert command.completed_at is not None

    def test_command_start_execution_full(self) -> None:
        """Test command start_execution method."""
        command = FlextCliCommand(id="test-cmd", command_line="echo test")

        result = command.start_execution()

        assert result.is_success
        updated_command = result.value
        assert updated_command.status == FlextCliCommandStatus.RUNNING
        assert updated_command.started_at is not None

    def test_command_start_execution_invalid_status(self) -> None:
        """Test command start_execution with invalid status."""
        command = FlextCliCommand(
            command_line="test", status=FlextCliCommandStatus.RUNNING
        )

        result = command.start_execution()

        assert not result.is_success

    def test_command_complete_execution_full(self) -> None:
        """Test command complete_execution method."""
        command = FlextCliCommand(id="test-cmd", command_line="echo test")

        result = command.complete_execution(
            exit_code=0, stdout="test output", stderr=""
        )

        assert result.is_success
        updated_command = result.value
        assert updated_command.status == FlextCliCommandStatus.COMPLETED
        assert updated_command.output == "test output"
        assert updated_command.exit_code == 0
        assert updated_command.completed_at is not None

    def test_command_complete_execution_failed(self) -> None:
        """Test command complete_execution with failure."""
        command = FlextCliCommand(id="test-cmd", command_line="failing command")

        result = command.complete_execution(
            exit_code=1, stdout="", stderr="command failed"
        )

        assert result.is_success
        updated_command = result.value
        assert updated_command.status == FlextCliCommandStatus.FAILED
        assert updated_command.stderr == "command failed"
        assert updated_command.exit_code == 1

    def test_command_cancel_execution(self) -> None:
        """Test command cancel_execution method."""
        command = FlextCliCommand(
            command_line="test", status=FlextCliCommandStatus.RUNNING
        )

        result = command.cancel_execution()

        assert result.is_success
        updated_command = result.value
        assert updated_command.status == FlextCliCommandStatus.CANCELLED
        assert updated_command.completed_at is not None

    def test_command_cancel_execution_invalid_status(self) -> None:
        """Test command cancel_execution with invalid status."""
        command = FlextCliCommand(
            id="test-cmd", command_line="test", status=FlextCliCommandStatus.PENDING
        )

        result = command.cancel_execution()

        assert not result.is_success

    def test_command_status_property_mapping(self) -> None:
        """Test command_status property mapping."""
        # Test explicit status mapping
        completed = FlextCliCommand(
            id="completed-cmd",
            command_line="test",
            status=FlextCliCommandStatus.COMPLETED,
        )
        assert completed.command_status == CommandStatus.COMPLETED

        # Test derived status from timestamps
        command_with_timestamps = FlextCliCommand(
            id="timestamp-cmd",
            command_line="test",
            status=FlextCliCommandStatus.PENDING,  # Will be overridden by timestamps
            started_at=datetime.now(UTC),
            completed_at=datetime.now(UTC),
            exit_code=0,
        )
        assert command_with_timestamps.command_status == CommandStatus.COMPLETED

    def test_command_stdout_property(self) -> None:
        """Test command stdout property alias."""
        command = FlextCliCommand(
            id="test-cmd", command_line="test", output="test output"
        )

        assert command.stdout == "test output"

    def test_command_is_completed_property(self) -> None:
        """Test command is_completed property."""
        completed = FlextCliCommand(
            id="completed-cmd-2",
            command_line="test",
            status=FlextCliCommandStatus.COMPLETED,
        )
        failed = FlextCliCommand(
            id="failed-cmd", command_line="test", status=FlextCliCommandStatus.FAILED
        )
        running = FlextCliCommand(
            id="running-cmd", command_line="test", status=FlextCliCommandStatus.RUNNING
        )

        assert completed.is_completed is True
        assert failed.is_completed is True
        assert running.is_completed is False


class TestFlextCliSession:
    """Test FlextCliSession entity."""

    def test_session_creation_minimal(self) -> None:
        """Test creating session with minimal fields."""
        session = FlextCliSession(id="test-session")

        assert str(session.id) == "test-session"  # id is FlextEntityId type
        assert session.user_id is None
        assert session.state == FlextCliSessionState.ACTIVE
        assert isinstance(session.context, FlextCliContext)
        assert isinstance(session.configuration, FlextCliConfiguration)
        assert isinstance(session.command_history, list)
        assert session.current_command_id is None
        assert isinstance(session.session_data, dict)
        assert isinstance(session.started_at, datetime)
        assert isinstance(session.last_activity_at, datetime)
        assert session.ended_at is None

    def test_session_creation_with_data(self) -> None:
        """Test creating session with data."""
        now = datetime.now(UTC)
        context = FlextCliContext()
        config = FlextCliConfiguration()

        session = FlextCliSession(
            user_id="test-user",
            state=FlextCliSessionState.ACTIVE,
            context=context,
            configuration=config,
            session_id="test-session",
            command_history=["cmd1", "cmd2"],
            current_command_id="cmd2",
            session_data={"key": "value"},
            started_at=now,
            last_activity_at=now,
        )

        assert session.user_id == "test-user"
        assert session.state == FlextCliSessionState.ACTIVE
        assert session.context == context
        assert session.configuration == config
        assert session.session_id == "test-session"
        assert session.command_history == ["cmd1", "cmd2"]
        assert session.current_command_id == "cmd2"
        assert session.session_data == {"key": "value"}
        assert session.started_at == now
        assert session.last_activity_at == now

    def test_session_is_active_property(self) -> None:
        """Test session is_active property."""
        active = FlextCliSession(state=FlextCliSessionState.ACTIVE)
        suspended = FlextCliSession(state=FlextCliSessionState.SUSPENDED)

        assert active.is_active is True
        assert suspended.is_active is False

    def test_session_convenience_properties(self) -> None:
        """Test session convenience properties."""
        session = FlextCliSession(
            state=FlextCliSessionState.ACTIVE,
            current_command_id="cmd123",
            command_history=["cmd1", "cmd2", "cmd3"],
        )

        assert session.session_status == SessionStatus.ACTIVE
        assert session.current_command == "cmd123"
        assert session.commands_executed_count == 3
        assert session.commands_executed == ["cmd1", "cmd2", "cmd3"]

    def test_session_session_duration(self) -> None:
        """Test session session_duration property."""
        start = datetime.now(UTC)
        end = start.replace(second=start.second + 10)

        # Active session (no end time - should use current time)
        active_session = FlextCliSession(id="active-session", started_at=start)
        duration = active_session.session_duration
        assert duration is not None
        assert duration >= 0

        # Ended session
        ended_session = FlextCliSession(
            id="ended-session", started_at=start, ended_at=end
        )
        assert ended_session.session_duration == 10.0

    def test_session_validate_business_rules_success(self) -> None:
        """Test session business rules validation success."""
        session = FlextCliSession(id="test-session")

        result = session.validate_business_rules()

        assert result.is_success

    def test_session_validate_business_rules_invalid_timestamps(self) -> None:
        """Test session business rules validation with invalid timestamps."""
        start = datetime.now(UTC)
        end = start.replace(second=start.second - 5)

        session = FlextCliSession(started_at=start, ended_at=end)

        result = session.validate_business_rules()

        assert not result.is_success

    def test_session_validate_business_rules_activity_before_start(self) -> None:
        """Test session business rules validation with activity before start."""
        start = datetime.now(UTC)
        activity = start.replace(second=start.second - 5)

        session = FlextCliSession(started_at=start, last_activity_at=activity)

        result = session.validate_business_rules()

        assert not result.is_success

    def test_session_validate_business_rules_command_not_in_history(self) -> None:
        """Test session business rules validation with current command not in history."""
        session = FlextCliSession(
            command_history=["cmd1", "cmd2"], current_command_id="cmd3"
        )

        result = session.validate_business_rules()

        assert not result.is_success

    def test_session_add_command(self) -> None:
        """Test session add_command method."""
        session = FlextCliSession(id="test-session")
        command_id = "new-command"

        result = session.add_command(command_id)

        assert result.is_success
        updated_session = result.value
        assert command_id in updated_session.command_history
        assert updated_session.current_command_id == command_id
        assert updated_session.last_activity_at > session.last_activity_at

    def test_session_add_command_inactive_session(self) -> None:
        """Test session add_command with inactive session."""
        session = FlextCliSession(state=FlextCliSessionState.SUSPENDED)
        command_id = "new-command"

        result = session.add_command(command_id)

        assert not result.is_success

    def test_session_record_command_convenience(self) -> None:
        """Test session flext_cli_record_command convenience method."""
        session = FlextCliSession(id="test-session")

        result = session.flext_cli_record_command("test-command")

        assert result is True
        assert "test-command" in [str(cmd) for cmd in session.command_history]

    def test_session_suspend_session(self) -> None:
        """Test session suspend_session method."""
        session = FlextCliSession(state=FlextCliSessionState.ACTIVE)

        result = session.suspend_session()

        assert result.is_success
        updated_session = result.value
        assert updated_session.state == FlextCliSessionState.SUSPENDED
        assert updated_session.current_command_id is None

    def test_session_suspend_session_not_active(self) -> None:
        """Test session suspend_session with non-active session."""
        session = FlextCliSession(state=FlextCliSessionState.SUSPENDED)

        result = session.suspend_session()

        assert not result.is_success

    def test_session_resume_session(self) -> None:
        """Test session resume_session method."""
        session = FlextCliSession(state=FlextCliSessionState.SUSPENDED)

        result = session.resume_session()

        assert result.is_success
        updated_session = result.value
        assert updated_session.state == FlextCliSessionState.ACTIVE

    def test_session_resume_session_not_suspended(self) -> None:
        """Test session resume_session with non-suspended session."""
        session = FlextCliSession(state=FlextCliSessionState.ACTIVE)

        result = session.resume_session()

        assert not result.is_success

    def test_session_terminate_session(self) -> None:
        """Test session terminate_session method."""
        session = FlextCliSession(state=FlextCliSessionState.ACTIVE)

        result = session.terminate_session()

        assert result.is_success
        updated_session = result.value
        assert updated_session.state == FlextCliSessionState.COMPLETED
        assert updated_session.current_command_id is None
        assert updated_session.ended_at is not None

    def test_session_terminate_already_terminated(self) -> None:
        """Test session terminate_session with already terminated session."""
        session = FlextCliSession(state=FlextCliSessionState.TERMINATED)

        result = session.terminate_session()

        assert not result.is_success

    def test_session_end_session_alias(self) -> None:
        """Test session end_session alias method."""
        session = FlextCliSession(state=FlextCliSessionState.ACTIVE)

        result = session.end_session()

        assert result.is_success
        updated_session = result.value
        assert updated_session.state == FlextCliSessionState.COMPLETED


class TestFlextCliPlugin:
    """Test FlextCliPlugin entity."""

    def test_plugin_creation_minimal(self) -> None:
        """Test creating plugin with minimal fields."""
        plugin = FlextCliPlugin(name="test-plugin", entry_point="test_plugin:main")

        assert str(plugin.id) == "test-plugin"  # id is FlextEntityId type
        assert plugin.name == "test-plugin"
        assert plugin.entry_point == "test_plugin:main"
        assert plugin.state == FlextCliPluginState.UNLOADED
        assert plugin.enabled is True
        assert plugin.description is None
        assert plugin.plugin_version == "0.1.0"

    def test_plugin_creation_with_data(self) -> None:
        """Test creating plugin with full data."""
        now = datetime.now(UTC)

        plugin = FlextCliPlugin(
            name="advanced-plugin",
            description="Advanced plugin with features",
            plugin_version="1.2.3",
            entry_point="advanced_plugin.main:start",
            state=FlextCliPluginState.LOADED,
            enabled=True,
            author="Test Author",
            license="MIT",
            dependencies=["dep1", "dep2"],
            commands=["cmd1", "cmd2"],
            configuration={"setting": "value"},
            plugin_directory=Path("/plugins/advanced"),
            loaded_at=now,
            last_error=None,
        )

        assert plugin.name == "advanced-plugin"
        assert plugin.description == "Advanced plugin with features"
        assert plugin.plugin_version == "1.2.3"
        assert plugin.entry_point == "advanced_plugin.main:start"
        assert plugin.state == FlextCliPluginState.LOADED
        assert plugin.enabled is True
        assert plugin.author == "Test Author"
        assert plugin.license == "MIT"
        assert plugin.dependencies == ["dep1", "dep2"]
        assert plugin.commands == ["cmd1", "cmd2"]
        assert plugin.configuration == {"setting": "value"}
        assert plugin.loaded_at == now

    def test_plugin_validate_entry_point_valid(self) -> None:
        """Test plugin entry point validation with valid formats."""
        valid_entry_points = [
            "module:function",
            "package.module:function",
            "deep.package.module:function",
            "module.path",  # Without colon
        ]

        for entry_point in valid_entry_points:
            plugin = FlextCliPlugin(
                id="test-plugin", name="test", entry_point=entry_point
            )
            assert plugin.entry_point == entry_point

    def test_plugin_validate_entry_point_invalid(self) -> None:
        """Test plugin entry point validation with invalid formats."""
        invalid_entry_points = [
            ":",  # Empty parts
            "module:",  # Empty function
            ":function",  # Empty module
            "function",  # No module path and no colon
        ]

        for entry_point in invalid_entry_points:
            with pytest.raises(ValueError):
                FlextCliPlugin(id="test-plugin", name="test", entry_point=entry_point)

    def test_plugin_properties(self) -> None:
        """Test plugin convenience properties."""
        unloaded = FlextCliPlugin(
            id="test-plugin", name="test", entry_point="test:main"
        )
        loaded = FlextCliPlugin(
            id="loaded-plugin",
            name="test",
            entry_point="test:main",
            state=FlextCliPluginState.LOADED,
        )
        active = FlextCliPlugin(
            id="active-plugin",
            name="test",
            entry_point="test:main",
            state=FlextCliPluginState.ACTIVE,
        )

        assert not unloaded.is_loaded
        assert not unloaded.is_active
        assert loaded.is_loaded
        assert not loaded.is_active
        assert active.is_loaded
        assert active.is_active

    def test_plugin_status_property_mapping(self) -> None:
        """Test plugin plugin_status property mapping."""
        unloaded = FlextCliPlugin(
            id="unloaded-plugin",
            name="test",
            entry_point="test:main",
            state=FlextCliPluginState.UNLOADED,
        )
        disabled = FlextCliPlugin(
            id="disabled-plugin",
            name="test",
            entry_point="test:main",
            state=FlextCliPluginState.DISABLED,
        )
        active = FlextCliPlugin(
            id="active-plugin-2",
            name="test",
            entry_point="test:main",
            state=FlextCliPluginState.ACTIVE,
        )

        assert unloaded.plugin_status == PluginStatus.INACTIVE
        assert disabled.plugin_status == PluginStatus.INACTIVE
        assert active.plugin_status == PluginStatus.ACTIVE

    def test_plugin_convenience_methods(self) -> None:
        """Test plugin convenience methods."""
        plugin = FlextCliPlugin(id="test-plugin", name="test", entry_point="test:main")

        # Test installed property
        assert not plugin.installed  # Not loaded yet

        # Test enable/disable
        result = plugin.disable()
        assert result.is_success
        disabled_plugin = result.value
        assert not disabled_plugin.enabled

        enable_result = disabled_plugin.enable()
        assert enable_result.is_success
        enabled_plugin = enable_result.value
        assert enabled_plugin.enabled

    def test_plugin_validate_business_rules_success(self) -> None:
        """Test plugin business rules validation success."""
        plugin = FlextCliPlugin(
            id="test-plugin", name="test-plugin", entry_point="test:main"
        )

        result = plugin.validate_business_rules()

        assert result.is_success

    def test_plugin_validate_business_rules_empty_name(self) -> None:
        """Test plugin business rules validation - Pydantic prevents empty names."""
        with pytest.raises(ValidationError):
            FlextCliPlugin(id="test-plugin", name="   ", entry_point="test:main")

    def test_plugin_validate_business_rules_empty_entry_point(self) -> None:
        """Test plugin business rules validation - Pydantic prevents empty entry points."""
        with pytest.raises(ValidationError):
            FlextCliPlugin(id="test-plugin", name="test", entry_point="   ")

    def test_plugin_validate_business_rules_active_without_loaded_at(self) -> None:
        """Test plugin business rules validation for active plugin without loaded_at."""
        plugin = FlextCliPlugin(
            id="invalid-plugin",
            name="test",
            entry_point="test:main",
            state=FlextCliPluginState.ACTIVE,
            loaded_at=None,
        )

        result = plugin.validate_business_rules()

        assert not result.is_success

    def test_plugin_load_plugin(self) -> None:
        """Test plugin load_plugin method."""
        plugin = FlextCliPlugin(id="test-plugin", name="test", entry_point="test:main")

        result = plugin.load_plugin()

        assert result.is_success
        loaded_plugin = result.value
        assert loaded_plugin.state == FlextCliPluginState.LOADED
        assert loaded_plugin.loaded_at is not None
        assert loaded_plugin.last_error is None

    def test_plugin_load_plugin_invalid_state(self) -> None:
        """Test plugin load_plugin with invalid state."""
        plugin = FlextCliPlugin(
            name="test", entry_point="test:main", state=FlextCliPluginState.LOADED
        )

        result = plugin.load_plugin()

        assert not result.is_success

    def test_plugin_activate_plugin_from_loaded(self) -> None:
        """Test plugin activate_plugin from loaded state."""
        plugin = FlextCliPlugin(
            name="test", entry_point="test:main", state=FlextCliPluginState.LOADED
        )

        result = plugin.activate_plugin()

        assert result.is_success
        active_plugin = result.value
        assert active_plugin.state == FlextCliPluginState.ACTIVE

    def test_plugin_activate_plugin_from_unloaded(self) -> None:
        """Test plugin activate_plugin from unloaded state (should load first)."""
        plugin = FlextCliPlugin(
            name="test", entry_point="test:main", state=FlextCliPluginState.UNLOADED
        )

        result = plugin.activate_plugin()

        assert result.is_success
        active_plugin = result.value
        assert active_plugin.state == FlextCliPluginState.ACTIVE
        assert active_plugin.loaded_at is not None

    def test_plugin_deactivate_plugin(self) -> None:
        """Test plugin deactivate_plugin method."""
        plugin = FlextCliPlugin(
            name="test", entry_point="test:main", state=FlextCliPluginState.ACTIVE
        )

        result = plugin.deactivate_plugin()

        assert result.is_success
        deactivated_plugin = result.value
        assert deactivated_plugin.state == FlextCliPluginState.UNLOADED
        assert deactivated_plugin.loaded_at is None

    def test_plugin_unload_plugin(self) -> None:
        """Test plugin unload_plugin method."""
        plugin = FlextCliPlugin(
            name="test", entry_point="test:main", state=FlextCliPluginState.LOADED
        )

        result = plugin.unload_plugin()

        assert result.is_success
        unloaded_plugin = result.value
        assert unloaded_plugin.state == FlextCliPluginState.UNLOADED
        assert unloaded_plugin.loaded_at is None

    def test_plugin_unload_plugin_from_active(self) -> None:
        """Test plugin unload_plugin from active state (should deactivate first)."""
        plugin = FlextCliPlugin(
            name="test", entry_point="test:main", state=FlextCliPluginState.ACTIVE
        )

        result = plugin.unload_plugin()

        assert result.is_success
        unloaded_plugin = result.value
        assert unloaded_plugin.state == FlextCliPluginState.UNLOADED

    def test_plugin_unload_already_unloaded(self) -> None:
        """Test plugin unload_plugin with already unloaded plugin."""
        plugin = FlextCliPlugin(
            name="test", entry_point="test:main", state=FlextCliPluginState.UNLOADED
        )

        result = plugin.unload_plugin()

        assert not result.is_success

    def test_plugin_convenience_aliases(self) -> None:
        """Test plugin convenience method aliases."""
        plugin = FlextCliPlugin(id="test-plugin", name="test", entry_point="test:main")

        # Test activate alias
        activate_result = plugin.activate()
        assert activate_result.is_success

        active_plugin = activate_result.value

        # Test deactivate alias
        deactivate_result = active_plugin.deactivate()
        assert deactivate_result.is_success

    def test_plugin_install_uninstall_convenience(self) -> None:
        """Test plugin install/uninstall convenience methods."""
        plugin = FlextCliPlugin(id="test-plugin", name="test", entry_point="test:main")

        # Test install (should load plugin)
        install_result = plugin.install()
        assert install_result.is_success
        installed_plugin = install_result.value
        assert installed_plugin.state == FlextCliPluginState.LOADED

        # Test uninstall
        uninstall_result = installed_plugin.uninstall()
        assert uninstall_result.is_success
        uninstalled_plugin = uninstall_result.value
        assert uninstalled_plugin.state == FlextCliPluginState.UNLOADED
        assert not uninstalled_plugin.enabled


class TestFlextCliWorkspace:
    """Test FlextCliWorkspace aggregate root."""

    def test_workspace_creation_minimal(self) -> None:
        """Test creating workspace with minimal fields."""
        workspace = FlextCliWorkspace(id="test-workspace", name="test-workspace")

        assert workspace.name == "test-workspace"
        assert workspace.description is None
        assert isinstance(workspace.configuration, FlextCliConfiguration)
        assert isinstance(workspace.session_ids, list)
        assert isinstance(workspace.plugin_ids, list)
        assert isinstance(workspace.workspace_data, dict)

    def test_workspace_creation_with_data(self) -> None:
        """Test creating workspace with full data."""
        config = FlextCliConfiguration()

        workspace = FlextCliWorkspace(
            name="advanced-workspace",
            description="Advanced workspace",
            configuration=config,
            session_ids=["session1", "session2"],
            plugin_ids=["plugin1", "plugin2"],
            workspace_data={"setting": "value"},
        )

        assert workspace.name == "advanced-workspace"
        assert workspace.description == "Advanced workspace"
        assert workspace.configuration == config
        assert workspace.session_ids == ["session1", "session2"]
        assert workspace.plugin_ids == ["plugin1", "plugin2"]
        assert workspace.workspace_data == {"setting": "value"}

    def test_workspace_validate_business_rules_success(self) -> None:
        """Test workspace business rules validation success."""
        workspace = FlextCliWorkspace(id="test-workspace", name="test-workspace")

        result = workspace.validate_business_rules()

        assert result.is_success

    def test_workspace_validate_business_rules_empty_name(self) -> None:
        """Test workspace business rules validation with empty name."""
        workspace = FlextCliWorkspace(id="test-workspace", name="   ")

        result = workspace.validate_business_rules()

        assert not result.is_success

    def test_workspace_add_session(self) -> None:
        """Test workspace add_session method."""
        workspace = FlextCliWorkspace(id="test-workspace", name="test-workspace")
        session_id = "new-session"

        result = workspace.add_session(session_id)

        assert result.is_success
        updated_workspace = result.value
        assert session_id in updated_workspace.session_ids

    def test_workspace_add_session_duplicate(self) -> None:
        """Test workspace add_session with duplicate session."""
        session_id = "existing-session"
        workspace = FlextCliWorkspace(name="test-workspace", session_ids=[session_id])

        result = workspace.add_session(session_id)

        assert not result.is_success

    def test_workspace_remove_session(self) -> None:
        """Test workspace remove_session method."""
        session_id = "existing-session"
        workspace = FlextCliWorkspace(
            name="test-workspace", session_ids=[session_id, "other-session"]
        )

        result = workspace.remove_session(session_id)

        assert result.is_success
        updated_workspace = result.value
        assert session_id not in updated_workspace.session_ids
        assert "other-session" in updated_workspace.session_ids

    def test_workspace_remove_session_not_found(self) -> None:
        """Test workspace remove_session with non-existent session."""
        workspace = FlextCliWorkspace(id="test-workspace", name="test-workspace")
        session_id = "nonexistent-session"

        result = workspace.remove_session(session_id)

        assert not result.is_success

    def test_workspace_install_plugin(self) -> None:
        """Test workspace install_plugin method."""
        workspace = FlextCliWorkspace(id="test-workspace", name="test-workspace")
        plugin_id = "new-plugin"

        result = workspace.install_plugin(plugin_id)

        assert result.is_success
        updated_workspace = result.value
        assert plugin_id in updated_workspace.plugin_ids

    def test_workspace_install_plugin_duplicate(self) -> None:
        """Test workspace install_plugin with duplicate plugin."""
        plugin_id = "existing-plugin"
        workspace = FlextCliWorkspace(name="test-workspace", plugin_ids=[plugin_id])

        result = workspace.install_plugin(plugin_id)

        assert not result.is_success


class TestModelRebuild:
    """Test model rebuild functionality."""

    def test_model_rebuild_called(self) -> None:
        """Test that model_rebuild is called for all models."""
        # This test ensures the rebuild calls at the end of the file work
        # The models should be properly configured after rebuild

        # Test that we can create instances without issues
        context = FlextCliContext()
        output = FlextCliOutput()
        config = FlextCliConfiguration()
        command = FlextCliCommand(id="test-cmd", command_line="test")
        session = FlextCliSession(id="session-123")
        plugin = FlextCliPlugin(id="test-plugin", name="test", entry_point="test:main")
        workspace = FlextCliWorkspace(id="test-workspace", name="test")

        # All should be valid instances
        assert isinstance(context, FlextCliContext)
        assert isinstance(output, FlextCliOutput)
        assert isinstance(config, FlextCliConfiguration)
        assert isinstance(command, FlextCliCommand)
        assert isinstance(session, FlextCliSession)
        assert isinstance(plugin, FlextCliPlugin)
        assert isinstance(workspace, FlextCliWorkspace)


class TestIntegration:
    """Test integration scenarios between models."""

    def test_command_session_integration(self) -> None:
        """Test integration between command and session."""
        # Create instances with explicit string IDs
        session = FlextCliSession(id="session-123")
        command = FlextCliCommand(id="test-cmd", command_line="echo test")

        # Add command to session
        add_result = session.add_command(command.id)
        assert add_result.is_success

        updated_session = add_result.value
        assert command.id in updated_session.command_history

    def test_plugin_workspace_integration(self) -> None:
        """Test integration between plugin and workspace."""
        workspace = FlextCliWorkspace(id="test-workspace", name="test-workspace")
        plugin = FlextCliPlugin(
            id="test-plugin", name="test-plugin", entry_point="test:main"
        )

        # Install plugin in workspace
        install_result = workspace.install_plugin(plugin.id)
        assert install_result.is_success

        updated_workspace = install_result.value
        assert plugin.id in updated_workspace.plugin_ids

    def test_context_command_integration(self) -> None:
        """Test integration between context and command."""
        context = FlextCliContext(user_id="test-user", timeout_seconds=600)
        command = FlextCliCommand(
            command_line="echo test", context=context, id="command-789"
        )

        assert command.context == context
        assert command.context.user_id == "test-user"

    def test_timestamp_consistency_real(self) -> None:
        """Test real timestamp behavior across models without mocking."""
        # Record time before creating models
        before_time = datetime.now(tz=UTC)

        # Create models that use _now_utc
        session = FlextCliSession(id="session-456")

        # Record time after creating models
        after_time = datetime.now(tz=UTC)

        # Verify that started_at is within the expected time range
        assert session.started_at is not None
        assert before_time <= session.started_at <= after_time

        # Test that timestamps are reasonably close (within 1 second)
        time_diff = session.started_at - before_time
        assert time_diff.total_seconds() < 1.0
