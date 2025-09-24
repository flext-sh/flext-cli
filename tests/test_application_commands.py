"""FLEXT CLI Application Commands Tests.

Test CLI command and session models.

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
        assert not cmd.output
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

        # Verify the error message (Pydantic validation error)
        assert "String should have at least 1 character" in str(exc_info.value)


class TestCommandStatus:
    """Test CommandStatus enum."""

    def test_command_status_values(self) -> None:
        """Test CommandStatus enum values."""
        assert FlextCliConstants.STATUS_PENDING == "pending"
        assert FlextCliConstants.STATUS_RUNNING == "running"
        assert FlextCliConstants.STATUS_COMPLETED == "completed"
        assert FlextCliConstants.STATUS_FAILED == "failed"

    def test_command_status_is_string_enum(self) -> None:
        """Test CommandStatus is string enum."""
        status = FlextCliConstants.STATUS_RUNNING
        assert isinstance(status, str)
        assert str(status) == "running"


class TestFlextCliSession:
    """Test FlextCliSession class - REAL implementation testing."""

    def test_session_initialization(self) -> None:
        """Test session initialization."""
        session = FlextCliModels.CliSession(user_id="test_user")

        assert session.user_id == "test_user"
        assert session.session_id is not None  # Auto-generated
        assert session.start_time is not None
        assert session.status == "active"
        assert session.commands_executed == 0

    def test_session_business_rules_validation(self) -> None:
        """Test session business rules validation."""
        session = FlextCliModels.CliSession(user_id="test_user")

        result = session.validate_business_rules()

        assert result.is_success

    def test_session_with_invalid_status(self) -> None:
        """Test session validation with invalid status."""
        session = FlextCliModels.CliSession(
            user_id="test_user", status="invalid_status"
        )

        result = session.validate_business_rules()

        assert result.is_failure
        assert "Invalid status" in (result.error or "")

    def test_session_validation(self) -> None:
        """Test session business rule validation."""
        session = FlextCliModels.CliSession(user_id="test_user")

        validation_result = session.validate_business_rules()

        # Session validation should succeed with valid session
        assert validation_result.is_success
