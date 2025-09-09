"""Tests for application commands.

Tests command-related domain models and functionality.




Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""


from __future__ import annotations

import pytest
from pydantic import ValidationError

from flext_cli import FlextCliConstants, FlextCliModels


class TestCLICommand:
    """Test CLICommand class - REAL implementation testing."""

    def test_init_with_required_parameters(self) -> None:
        """Test CLI command initialization with required parameters."""
        cmd = FlextCliModels.CliCommand(command_line="echo hello")

        assert cmd.command_line == "echo hello"
        assert cmd.status == FlextCliConstants.STATUS_PENDING
        assert cmd.output == ""
        assert cmd.exit_code is None
        assert cmd.id is not None  # Auto-generated UUID

    def test_command_validation(self) -> None:
        """Test command business rule validation."""
        cmd = FlextCliModels.CliCommand(command_line="echo test")

        validation_result = cmd.validate_business_rules()

        assert validation_result.is_success

    def test_start_execution(self) -> None:
        """Test command execution start."""
        cmd = FlextCliModels.CliCommand(command_line="echo test")

        result = cmd.start_execution()

        assert result.is_success
        assert cmd.status == FlextCliConstants.STATUS_RUNNING

    def test_empty_command_line_validation(self) -> None:
        """Test validation fails for empty command line."""
        # Model now properly validates at creation time (improved defensive programming)
        with pytest.raises(ValidationError) as exc_info:
            FlextCliModels.CliCommand(command_line="")

        # Verify the error message
        assert "Command line cannot be empty" in str(exc_info.value)


class TestCommandStatus:
    """Test CommandStatus enum."""

    def test_command_status_values(self) -> None:
        """Test CommandStatus enum values."""
        assert FlextCliConstants.STATUS_PENDING == "PENDING"
        assert FlextCliConstants.STATUS_RUNNING == "RUNNING"
        assert FlextCliConstants.STATUS_COMPLETED == "COMPLETED"
        assert FlextCliConstants.STATUS_FAILED == "FAILED"
        assert FlextCliConstants.STATUS_CANCELLED == "CANCELLED"

    def test_command_status_is_string_enum(self) -> None:
        """Test CommandStatus is string enum."""
        status = FlextCliConstants.STATUS_RUNNING
        assert isinstance(status, str)
        assert str(status) == "RUNNING"


class TestFlextCliSession:
    """Test FlextCliSession class - REAL implementation testing."""

    def test_session_initialization(self) -> None:
        """Test session initialization."""
        session = FlextCliModels.CliSession(user_id="test_user")

        assert session.user_id == "test_user"
        assert session.id is not None  # Auto-generated UUID
        assert session.commands == []
        assert session.start_time is not None

    def test_add_command_to_session(self) -> None:
        """Test adding command to session history."""
        session = FlextCliModels.CliSession(user_id="test_user")
        command = FlextCliModels.CliCommand(command_line="echo test")

        result = session.add_command(command)

        assert result.is_success
        assert command in session.commands

    def test_add_empty_command_line_validation(self) -> None:
        """Test validation prevents creating commands with empty command line."""
        session = FlextCliModels.CliSession(user_id="test_user")

        # Model now properly validates at creation time (improved defensive programming)
        with pytest.raises(ValidationError) as exc_info:
            FlextCliModels.CliCommand(command_line="")  # Empty command line

        # Verify the validation error
        assert "Command line cannot be empty" in str(exc_info.value)

        # Session remains valid since invalid command was never created
        validation_result = session.validate_business_rules()
        assert validation_result.is_success

    def test_session_validation(self) -> None:
        """Test session business rule validation."""
        session = FlextCliModels.CliSession(user_id="test_user")

        validation_result = session.validate_business_rules()

        # Session validation should succeed with valid session
        assert validation_result.is_success
