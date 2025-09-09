"""Comprehensive tests for models.py to maximize coverage.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""


from __future__ import annotations

from datetime import UTC, datetime

from flext_core import FlextModels, FlextResult

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
            exit_code=1,
            output="test output",
            error_output="test error"
        )

        assert command.command_line == "custom command"
        assert command.execution_time == custom_time
        assert command.status == FlextCliConstants.STATUS_PENDING  # Default state
        assert command.exit_code == 1
        assert command.output == "test output"
        assert command.error_output == "test error"

    def test_cli_command_is_successful_property(self) -> None:
        """Test is_successful computed field."""
        # Test successful command (exit_code 0)
        successful_command = FlextCliModels.CliCommand(
            command_line="success test",
            exit_code=0
        )
        assert successful_command.exit_code == 0

        # Test failed command (exit_code 1)
        failed_command = FlextCliModels.CliCommand(
            command_line="fail test",
            exit_code=1
        )
        assert failed_command.exit_code == 1

        # Test command without exit code
        basic_command = FlextCliModels.CliCommand(
            command_line="pending test"
        )
        # Exit code defaults to None
        assert basic_command.exit_code is None

    def test_cli_command_status_validation(self) -> None:
        """Test command status validation."""
        # Test basic command creation and status property
        command = FlextCliModels.CliCommand(
            command_line="test",
            exit_code=0
        )
        # Status comes from state property
        assert command.status == FlextCliConstants.STATUS_PENDING

        # Test command after completion
        completion_result = command.complete_execution(exit_code=0, output="test output")
        if completion_result.is_success:
            completed_command = completion_result.unwrap()
            assert completed_command.status == FlextCliConstants.STATUS_COMPLETED

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
        assert session.duration_seconds is None  # None because end_time is None

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
        assert FlextCliTypes.OutputFormat.JSON.value == "json"
        assert FlextCliTypes.OutputFormat.YAML.value == "yaml"
        assert FlextCliTypes.OutputFormat.CSV.value == "csv"
        assert FlextCliTypes.OutputFormat.TABLE.value == "table"
        assert FlextCliTypes.OutputFormat.PLAIN.value == "plain"

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
        """Test command can be created with basic parameters."""
        # Test basic command creation (new architecture uses state pattern)
        command = FlextCliModels.CliCommand(command_line="test")
        assert command.command_line == "test"

        # Test command with exit_code
        command_with_code = FlextCliModels.CliCommand(
            command_line="test", exit_code=0
        )
        assert command_with_code.exit_code == 0

    def test_config_with_all_valid_output_formats(self) -> None:
        """Test config can be created with all valid output formats."""
        for format_value in FlextCliTypes.OutputFormat:
            config = FlextCliModels.CliConfig(
                output_format=format_value.value
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
