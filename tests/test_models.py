"""Comprehensive tests for models.py to maximize coverage.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from flext_core import FlextModels, FlextResult
from pydantic_core import ValidationError

from flext_cli.constants import FlextCliConstants
from flext_cli.models import FlextCliModels
from flext_cli.typings import FlextCliTypes


class TestFlextCliModelsCliCommand:
    """Test FlextCliModels.CliCommand functionality."""

    def test_cli_command_creation_with_defaults(self) -> None:
        """Test CLI command creation with default values."""
        command = FlextCliModels.CliCommand(command_line="test command")

        assert command.command_line == "test command"
        assert command.status == FlextCliConstants.STATUS_PENDING
        assert command.exit_code is None
        assert command.output == ""
        assert command.error_output == ""
        assert isinstance(command.execution_time, datetime)
        assert command.execution_time.tzinfo == UTC

    def test_cli_command_creation_with_custom_values(self) -> None:
        """Test CLI command creation with custom values."""
        custom_time = datetime.now(UTC)
        command = FlextCliModels.CliCommand(
            command_line="custom command",
            execution_time=custom_time,
            status=FlextCliConstants.STATUS_RUNNING,
            exit_code=1,
            output="test output",
            error_output="test error"
        )

        assert command.command_line == "custom command"
        assert command.execution_time == custom_time
        assert command.status == FlextCliConstants.STATUS_RUNNING
        assert command.exit_code == 1
        assert command.output == "test output"
        assert command.error_output == "test error"

    def test_cli_command_is_successful_property(self) -> None:
        """Test is_successful computed field."""
        # Test successful command
        successful_command = FlextCliModels.CliCommand(
            command_line="success test",
            status=FlextCliConstants.STATUS_COMPLETED,
            exit_code=0
        )
        assert successful_command.is_successful is True

        # Test failed command
        failed_command = FlextCliModels.CliCommand(
            command_line="fail test",
            status=FlextCliConstants.STATUS_FAILED,
            exit_code=1
        )
        assert failed_command.is_successful is False

        # Test pending command
        pending_command = FlextCliModels.CliCommand(
            command_line="pending test",
            status=FlextCliConstants.STATUS_PENDING
        )
        assert pending_command.is_successful is False

    def test_cli_command_status_validation(self) -> None:
        """Test command status validation."""
        # Valid status
        command = FlextCliModels.CliCommand(
            command_line="test",
            status=FlextCliConstants.STATUS_COMPLETED
        )
        assert command.status == FlextCliConstants.STATUS_COMPLETED

        # Invalid status should raise ValidationError
        with pytest.raises(ValidationError):
            FlextCliModels.CliCommand(
                command_line="test",
                status="INVALID_STATUS"
            )

    def test_cli_command_start_execution_method(self) -> None:
        """Test start_execution domain method."""
        command = FlextCliModels.CliCommand(command_line="test command")
        result = command.start_execution()

        # Should return FlextResult
        assert isinstance(result, FlextResult)

    def test_cli_command_validate_business_rules_method(self) -> None:
        """Test validate_business_rules domain method."""
        command = FlextCliModels.CliCommand(command_line="test command")
        result = command.validate_business_rules()

        # Should return FlextResult
        assert isinstance(result, FlextResult)


class TestFlextCliModelsCliSession:
    """Test FlextCliModels.CliSession functionality."""

    def test_cli_session_creation_with_defaults(self) -> None:
        """Test CLI session creation with default values."""
        session = FlextCliModels.CliSession()

        assert isinstance(session.start_time, datetime)
        assert session.start_time.tzinfo == UTC
        assert session.end_time is None
        assert session.user_id is None
        assert len(session.commands) == 0
        assert isinstance(session.duration_seconds, float)

    def test_cli_session_creation_with_user_id(self) -> None:
        """Test CLI session creation with user ID."""
        session = FlextCliModels.CliSession(user_id="test_user")

        assert session.user_id == "test_user"
        assert isinstance(session.start_time, datetime)

    def test_cli_session_validate_business_rules_method(self) -> None:
        """Test validate_business_rules domain method."""
        session = FlextCliModels.CliSession(user_id="test_user")
        result = session.validate_business_rules()

        # Should return FlextResult
        assert isinstance(result, FlextResult)


class TestFlextCliModelsCliConfig:
    """Test FlextCliModels.CliConfig functionality."""

    def test_cli_config_creation_with_defaults(self) -> None:
        """Test CLI config creation with default values."""
        config = FlextCliModels.CliConfig()

        assert config.profile == "default"
        assert config.output_format == "table"
        assert config.debug_mode is False
        assert config.timeout_seconds == 30

    def test_cli_config_creation_with_custom_values(self) -> None:
        """Test CLI config creation with custom values."""
        config = FlextCliModels.CliConfig(
            profile="development",
            output_format="json",
            debug_mode=True,
            timeout_seconds=60
        )

        assert config.profile == "development"
        assert config.output_format == "json"
        assert config.debug_mode is True
        assert config.timeout_seconds == 60


class TestFlextCliTypesOutputFormat:
    """Test FlextCliTypes.OutputFormat functionality."""

    def test_output_format_values(self) -> None:
        """Test all output format values."""
        assert FlextCliTypes.OutputFormat.JSON == "json"
        assert FlextCliTypes.OutputFormat.YAML == "yaml"
        assert FlextCliTypes.OutputFormat.CSV == "csv"
        assert FlextCliTypes.OutputFormat.TABLE == "table"
        assert FlextCliTypes.OutputFormat.PLAIN == "plain"

    def test_output_format_enum_usage(self) -> None:
        """Test output format enum can be used in validation."""
        # Should work with CLI config
        config = FlextCliModels.CliConfig(
            output_format=FlextCliTypes.OutputFormat.JSON
        )
        assert config.output_format == "json"


class TestFlextCliConstants:
    """Test FlextCliConstants functionality."""

    def test_command_status_constants(self) -> None:
        """Test command status constants are defined."""
        assert FlextCliConstants.STATUS_PENDING == "PENDING"
        assert FlextCliConstants.STATUS_RUNNING == "RUNNING"
        assert FlextCliConstants.STATUS_COMPLETED == "COMPLETED"
        assert FlextCliConstants.STATUS_FAILED == "FAILED"
        assert FlextCliConstants.STATUS_CANCELLED == "CANCELLED"

    def test_valid_command_statuses(self) -> None:
        """Test valid command statuses tuple."""
        assert isinstance(FlextCliConstants.VALID_COMMAND_STATUSES, tuple)
        assert FlextCliConstants.STATUS_PENDING in FlextCliConstants.VALID_COMMAND_STATUSES
        assert FlextCliConstants.STATUS_COMPLETED in FlextCliConstants.VALID_COMMAND_STATUSES

    def test_timeout_constants(self) -> None:
        """Test timeout constants are defined."""
        assert isinstance(FlextCliConstants.DEFAULT_COMMAND_TIMEOUT, int)
        assert isinstance(FlextCliConstants.MAX_COMMAND_TIMEOUT, int)
        assert FlextCliConstants.DEFAULT_COMMAND_TIMEOUT > 0
        assert FlextCliConstants.MAX_COMMAND_TIMEOUT > FlextCliConstants.DEFAULT_COMMAND_TIMEOUT


class TestFlextCliModelsIntegration:
    """Test integration between models, constants, and types."""

    def test_command_with_all_valid_statuses(self) -> None:
        """Test command can be created with all valid statuses."""
        for status in FlextCliConstants.VALID_COMMAND_STATUSES:
            command = FlextCliModels.CliCommand(
                command_line="test",
                status=status
            )
            assert command.status == status

    def test_config_with_all_valid_output_formats(self) -> None:
        """Test config can be created with all valid output formats."""
        for format_value in FlextCliTypes.OutputFormat:
            config = FlextCliModels.CliConfig(
                output_format=format_value
            )
            assert config.output_format == format_value.value

    def test_models_inherit_from_flext_core(self) -> None:
        """Test that models properly inherit from flext-core."""
        # Commands should inherit from FlextModels.Entity
        command = FlextCliModels.CliCommand(command_line="test")
        assert isinstance(command, FlextModels.Entity)

        # Sessions should inherit from FlextModels.Entity
        session = FlextCliModels.CliSession()
        assert isinstance(session, FlextModels.Entity)

        # Configs should inherit from FlextModels.Entity
        config = FlextCliModels.CliConfig()
        assert isinstance(config, FlextModels.Entity)
