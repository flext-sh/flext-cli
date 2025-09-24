"""Tests for models.py - Real API only.

Tests FlextCliModels using actual implemented structure.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from datetime import UTC, datetime

from flext_cli.config import FlextCliConfig
from flext_cli.constants import FlextCliConstants
from flext_cli.models import FlextCliModels
from flext_core import FlextResult


class TestFlextCliModelsCliCommand:
    """Test FlextCliModels.CliCommand functionality - real API."""

    def test_cli_command_creation_basic(self) -> None:
        """Test CLI command creation with required fields."""
        command = FlextCliModels.CliCommand(
            id="cmd-001",
            command="test",
            created_at=datetime.now(UTC),
        )

        assert command.id == "cmd-001"
        assert command.command == "test"
        assert command.status == FlextCliConstants.CommandStatus.PENDING
        assert command.exit_code is None
        assert not command.output
        assert not command.error_output
        assert isinstance(command.created_at, datetime)

    def test_cli_command_with_all_fields(self) -> None:
        """Test CLI command creation with all fields."""
        custom_time = datetime.now(UTC)
        command = FlextCliModels.CliCommand(
            id="cmd-002",
            command="custom",
            args=["arg1", "arg2"],
            status=FlextCliConstants.CommandStatus.COMPLETED,
            created_at=custom_time,
            exit_code=0,
            output="test output",
            error_output="test error",
        )

        assert command.id == "cmd-002"
        assert command.command == "custom"
        assert command.args == ["arg1", "arg2"]
        assert command.status == FlextCliConstants.CommandStatus.COMPLETED
        assert command.created_at == custom_time
        assert command.exit_code == 0
        assert command.output == "test output"
        assert command.error_output == "test error"

    def test_cli_command_properties(self) -> None:
        """Test CLI command computed properties."""
        command = FlextCliModels.CliCommand(
            id="cmd-003",
            command="echo",
            args=["hello", "world"],
            created_at=datetime.now(UTC),
        )

        # Test command_line property - returns just command, not including args
        command_line = command.command_line
        assert command_line == "echo"
        assert command.args == ["hello", "world"]  # Args stored separately

        # Test execution_time property
        execution_time = command.execution_time
        assert isinstance(execution_time, datetime)

    def test_cli_command_validate_business_rules(self) -> None:
        """Test validate_business_rules method."""
        command = FlextCliModels.CliCommand(
            id="cmd-004",
            command="test",
            created_at=datetime.now(UTC),
        )
        result = command.validate_business_rules()

        assert isinstance(result, FlextResult)
        assert result.is_success

    def test_cli_command_start_execution(self) -> None:
        """Test start_execution method."""
        command = FlextCliModels.CliCommand(
            id="cmd-005",
            command="test",
            created_at=datetime.now(UTC),
        )
        result = command.start_execution()

        assert isinstance(result, FlextResult)
        assert result.is_success

    def test_cli_command_complete_execution(self) -> None:
        """Test complete_execution method."""
        command = FlextCliModels.CliCommand(
            id="cmd-006",
            command="test",
            created_at=datetime.now(UTC),
        )
        command.start_execution()  # Must be running first
        result = command.complete_execution(
            exit_code=0,
            output="success",
        )

        assert isinstance(result, FlextResult)
        assert result.is_success


class TestFlextCliModelsCliSession:
    """Test FlextCliModels.CliSession functionality - real API."""

    def test_cli_session_creation_basic(self) -> None:
        """Test CLI session creation with required fields."""
        session = FlextCliModels.CliSession(
            id="session-001",
            start_time=datetime.now(UTC),
        )

        assert session.id == "session-001"
        assert isinstance(session.start_time, datetime)
        assert session.end_time is None
        assert session.duration_seconds == 0.0  # Defaults to 0.0, not None
        assert session.commands_executed == 0
        assert session.user_id is None

    def test_cli_session_with_user_id(self) -> None:
        """Test CLI session creation with user ID."""
        session = FlextCliModels.CliSession(
            id="session-002",
            user_id="test_user",
            start_time=datetime.now(UTC),
        )

        assert session.id == "session-002"
        assert session.user_id == "test_user"
        assert isinstance(session.start_time, datetime)

    def test_cli_session_validate_business_rules(self) -> None:
        """Test validate_business_rules method."""
        session = FlextCliModels.CliSession(
            id="session-003",
            user_id="test_user",
            start_time=datetime.now(UTC),
        )
        result = session.validate_business_rules()

        assert isinstance(result, FlextResult)
        assert result.is_success


class TestFlextCliModelsCliConfig:
    """Test FlextCliConfig functionality - real API."""

    def test_cli_config_creation_with_defaults(self) -> None:
        """Test CLI config creation with default values."""
        config = FlextCliConfig.MainConfig()

        assert config.profile == "default"
        assert config.output_format == "table"
        assert config.debug_mode is False

    def test_cli_config_creation_with_custom_values(self) -> None:
        """Test CLI config creation with custom values."""
        config = FlextCliConfig.MainConfig(
            profile="development",
            output_format="json",
            debug=True,
        )

        assert config.profile == "development"
        assert config.output_format == "json"
        assert config.debug_mode is True

    def test_cli_config_validate_business_rules(self) -> None:
        """Test validate_business_rules method."""
        config = FlextCliConfig.MainConfig(
            profile="test",
            output_format="json",
        )
        result = config.validate_output_format("json")

        assert isinstance(result, FlextResult)
        assert result.is_success

    def test_cli_session_add_command(self) -> None:
        """Test add_command method."""
        session = FlextCliModels.CliSession(
            id="session-003",
            start_time=datetime.now(UTC),
        )

        command = FlextCliModels.CliCommand(
            id="cmd-007",
            command="test",
            created_at=datetime.now(UTC),
        )

        result = session.add_command(command)

        assert isinstance(result, FlextResult)
        assert result.is_success
        assert len(session.commands) == 1
        assert session.commands_executed == 1
        assert session.commands[0].id == "cmd-007"


class TestFlextCliModelsCliOptions:
    """Test FlextCliModels.CliOptions functionality - real API."""

    def test_cli_options_creation(self) -> None:
        """Test CLI options creation."""
        from flext_cli.constants import FlextCliConstants

        config = FlextCliConfig.MainConfig(
            output_format="json",
            debug=True,
            no_color=False,
        )

        options = FlextCliConfig.CliOptions(
            output_format=config.output_format,
            debug=config.debug,
            max_width=FlextCliConstants.CliDefaults.MAX_WIDTH,
            no_color=config.no_color,
        )

        assert options.output_format == "json"
        assert options.debug is True
        assert options.max_width == 120
        assert options.no_color is False
