"""Tests for FlextCli functional patterns - Real API only.

Tests consolidated functionality using actual implemented methods.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from datetime import UTC, datetime

from flext_cli import (
    FlextCliApi,
    FlextCliCommands,
    FlextCliConfig,
    FlextCliConstants,
    FlextCliModels,
)
from flext_core import FlextResult


class TestFlextCliModels:
    """Test FlextCliModels with real API."""

    def test_models_exist(self) -> None:
        """Test that real models exist."""
        assert hasattr(FlextCliModels, "CliCommand")
        assert hasattr(FlextCliModels, "CliSession")
        assert hasattr(FlextCliModels, "CliFormatters")
        assert hasattr(FlextCliModels, "FormatOptions")

    def test_command_creation(self) -> None:
        """Test real command creation."""
        command = FlextCliModels.CliCommand(
            id="test-123",
            command_line="echo hello",
            created_at=datetime.now(UTC),
        )

        assert command.id == "test-123"
        assert command.command == "echo hello"
        assert isinstance(command.created_at, datetime)

    def test_command_execution_workflow(self) -> None:
        """Test real command execution workflow."""
        command = FlextCliModels.CliCommand(
            id="test-cmd",
            command_line="test",
            created_at=datetime.now(UTC),
        )

        assert command.status == FlextCliConstants.CommandStatus.PENDING.value

        start_result = command.start_execution()
        assert start_result.is_success
        assert command.status == FlextCliConstants.CommandStatus.RUNNING.value

        complete_result = command.complete_execution(exit_code=0, output="success")
        assert complete_result.is_success
        assert command.status == FlextCliConstants.CommandStatus.COMPLETED.value

    def test_session_creation(self) -> None:
        """Test real session functionality."""
        session = FlextCliModels.CliSession(
            id="test-session",
            user_id="test-user",
            start_time=datetime.now(UTC),
        )

        assert session.id == "test-session"
        assert session.user_id == "test-user"
        assert session.commands_executed == 0
        assert session.status == "active"


class TestFlextCliConstants:
    """Test FlextCliConstants with real API."""

    def test_command_status_constants(self) -> None:
        """Test real command status constants."""
        assert hasattr(FlextCliConstants, "CommandStatus")
        assert hasattr(FlextCliConstants.CommandStatus, "PENDING")
        assert hasattr(FlextCliConstants.CommandStatus, "RUNNING")
        assert hasattr(FlextCliConstants.CommandStatus, "COMPLETED")
        assert hasattr(FlextCliConstants.CommandStatus, "FAILED")

    def test_output_format_constants(self) -> None:
        """Test real output format constants."""
        assert hasattr(FlextCliConstants, "OutputFormats")
        assert hasattr(FlextCliConstants.OutputFormats, "JSON")
        assert hasattr(FlextCliConstants.OutputFormats, "TABLE")

    def test_error_codes_exist(self) -> None:
        """Test real error codes."""
        assert hasattr(FlextCliConstants, "ErrorCodes")
        assert hasattr(FlextCliConstants.ErrorCodes, "CLI_ERROR")
        assert hasattr(FlextCliConstants.ErrorCodes, "VALIDATION_ERROR")

    def test_exit_codes_exist(self) -> None:
        """Test real exit codes."""
        assert hasattr(FlextCliConstants, "ExitCodes")
        assert hasattr(FlextCliConstants.ExitCodes, "SUCCESS")
        assert hasattr(FlextCliConstants.ExitCodes, "FAILURE")
        assert hasattr(FlextCliConstants.ExitCodes, "CONFIG_ERROR")
        assert hasattr(FlextCliConstants.ExitCodes, "COMMAND_ERROR")

    def test_constant_lists(self) -> None:
        """Test constant lists."""
        assert hasattr(FlextCliConstants, "OUTPUT_FORMATS_LIST")
        assert hasattr(FlextCliConstants, "COMMAND_STATUSES_LIST")
        assert hasattr(FlextCliConstants, "ERROR_CODES_LIST")

        assert isinstance(FlextCliConstants.OUTPUT_FORMATS_LIST, list)
        assert isinstance(FlextCliConstants.COMMAND_STATUSES_LIST, list)
        assert isinstance(FlextCliConstants.ERROR_CODES_LIST, list)


class TestFlextCliIntegration:
    """Test FlextCli integration patterns."""

    def test_command_with_constants(self) -> None:
        """Test using commands with constants."""
        command = FlextCliModels.CliCommand(
            id="int-test",
            command_line="integration test",
            status=FlextCliConstants.CommandStatus.PENDING.value,
            created_at=datetime.now(UTC),
        )

        assert command.status == FlextCliConstants.CommandStatus.PENDING.value

    def test_config_with_format_constants(self) -> None:
        """Test config with output format constants."""
        config = FlextCliConfig.MainConfig(
            profile="test",
            output_format=FlextCliConstants.OutputFormats.JSON.value,
            debug=True,
        )

        assert config.output_format == FlextCliConstants.OutputFormats.JSON.value

    def test_session_validation(self) -> None:
        """Test session validation with business rules."""
        session = FlextCliModels.CliSession(
            id="val-test",
            start_time=datetime.now(UTC),
        )

        result = session.validate_business_rules()
        assert isinstance(result, FlextResult)
        assert result.is_success


class TestFlextCliExports:
    """Test FlextCli module exports."""

    def test_main_imports_available(self) -> None:
        """Test that main imports are available."""
        assert FlextCliApi is not None
        assert FlextCliCommands is not None

    def test_models_import(self) -> None:
        """Test models import."""
        assert FlextCliModels is not None
        assert hasattr(FlextCliModels, "CliCommand")
        assert hasattr(FlextCliModels, "CliSession")

    def test_constants_import(self) -> None:
        """Test constants import."""
        assert FlextCliConstants is not None
        assert hasattr(FlextCliConstants, "CommandStatus")
        assert hasattr(FlextCliConstants, "OutputFormats")
