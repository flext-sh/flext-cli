"""FLEXT CLI Models - Ultra simplified version.

Minimal CLI models using only standard Python, no complex dependencies.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum

object
from uuid import uuid4


# Simple enumerations
class CommandStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class FlextCliOutputFormat(StrEnum):
    JSON = "json"
    CSV = "csv"
    YAML = "yaml"
    TABLE = "table"
    PLAIN = "plain"


# Simple FlextResult without dependencies
class FlextResult:
    """Railway-oriented FlextResult implementing proven flext-core patterns."""

    def __init__(self, value: object = None, error: str | None = None) -> None:
        self._value = value
        self._error = error
        self._success = error is None

    @property
    def value(self) -> object:
        """Get success value - use after checking is_success."""
        return self._value

    @property
    def error(self) -> str | None:
        """Get error message if failed."""
        return self._error

    @property
    def is_success(self) -> bool:
        """Check if operation succeeded."""
        return self._success

    @property
    def success(self) -> bool:
        """Alias for is_success - flext-core compatibility."""
        return self._success

    @property
    def is_failure(self) -> bool:
        """Check if operation failed."""
        return not self._success

    def unwrap(self) -> object:
        """Safely unwrap value after success check - FLEXT pattern."""
        if not self.is_success:
            msg = f"Cannot unwrap failed result: {self._error}"
            raise RuntimeError(msg)
        return self._value

    def unwrap_or(self, default: object) -> object:
        """Return value if success, otherwise default - LEGACY compatibility."""
        return self._value if self.is_success else default

    @classmethod
    def ok(cls, value: object = None) -> FlextResult:
        """Create successful result - FLEXT pattern."""
        return cls(value=value, error=None)

    @classmethod
    def fail(cls, error: str) -> FlextResult:
        """Create failed result - FLEXT pattern."""
        return cls(value=None, error=error)

    # Railway-oriented programming methods - PROVEN FLEXT PATTERNS
    def flat_map(self, func):
        """Chain operations that return FlextResult - railway pattern."""
        if self.is_failure:
            return self
        try:
            result = func(self._value)
            return result if isinstance(result, FlextResult) else FlextResult.ok(result)
        except Exception as e:
            return FlextResult.fail(str(e))

    def map(self, func):
        """Transform success value - railway pattern."""
        if self.is_failure:
            return self
        try:
            new_value = func(self._value)
            return FlextResult.ok(new_value)
        except Exception as e:
            return FlextResult.fail(str(e))

    def map_error(self, func):
        """Transform error message - railway pattern."""
        if self.is_success:
            return self
        try:
            new_error = func(self._error)
            return FlextResult.fail(new_error)
        except Exception as e:
            return FlextResult.fail(str(e))


# Simple CLI Command using plain Python class
class FlextCliCommand:
    """Minimal CLI command using plain Python."""

    def __init__(self, command_line: str, **kwargs) -> None:
        self.id = kwargs.get("id", str(uuid4()))
        self.command_line = command_line
        self.status = kwargs.get("status", CommandStatus.PENDING)
        self.output = kwargs.get("output", "")
        self.exit_code = kwargs.get("exit_code")
        self.started_at = kwargs.get("started_at")
        self.completed_at = kwargs.get("completed_at")

    def validate_business_rules(self) -> FlextResult:
        """Validate command business rules using railway pattern."""
        # Railway-oriented validation chain
        return (
            self._validate_command_line()
            .flat_map(lambda _: self._validate_status())
            .map(lambda _: None)  # Success returns None
        )

    def _validate_command_line(self) -> FlextResult:
        """Internal validation for command line."""
        if not self.command_line.strip():
            return FlextResult.fail("Command line cannot be empty")
        return FlextResult.ok(self.command_line)

    def _validate_status(self) -> FlextResult:
        """Internal validation for command status."""
        if self.status not in CommandStatus:
            return FlextResult.fail(f"Invalid status: {self.status}")
        return FlextResult.ok(self.status)

    def start_execution(self) -> FlextResult:
        """Start command execution using railway pattern."""
        return (
            self.validate_business_rules()
            .flat_map(lambda _: self._check_can_start())
            .flat_map(lambda _: self._perform_start())
        )

    def _check_can_start(self) -> FlextResult:
        """Check if command can be started."""
        if self.status != CommandStatus.PENDING:
            return FlextResult.fail(f"Cannot start command in {self.status} state")
        return FlextResult.ok(self)

    def _perform_start(self) -> FlextResult:
        """Perform the actual start operation."""
        try:
            self.status = CommandStatus.RUNNING
            self.started_at = datetime.now(UTC)
            return FlextResult.ok(self)
        except Exception as e:
            return FlextResult.fail(f"Failed to start command: {e}")


# Simple Session using plain Python class
class FlextCliSession:
    """Minimal CLI session using plain Python."""

    def __init__(self, **kwargs) -> None:
        self.id = kwargs.get("id", str(uuid4()))
        self.user_id = kwargs.get("user_id")
        self.started_at = kwargs.get("started_at", datetime.now(UTC))
        self.command_history: list[str] = kwargs.get("command_history", [])

    def add_command(self, command_id: str) -> FlextResult:
        """Add command to session history using railway pattern."""
        return (
            self._validate_command_id(command_id)
            .flat_map(lambda cmd_id: self._validate_session_state())
            .flat_map(lambda _: self._perform_add_command(command_id))
        )

    def _validate_command_id(self, command_id: str) -> FlextResult:
        """Validate command ID."""
        if not command_id or not command_id.strip():
            return FlextResult.fail("Command ID cannot be empty")
        return FlextResult.ok(command_id)

    def _validate_session_state(self) -> FlextResult:
        """Validate session can accept new commands."""
        if not self.id:
            return FlextResult.fail("Invalid session - no ID")
        return FlextResult.ok(self)

    def _perform_add_command(self, command_id: str) -> FlextResult:
        """Perform the actual command addition."""
        try:
            self.command_history.append(command_id)
            return FlextResult.ok(self)
        except Exception as e:
            return FlextResult.fail(f"Failed to add command: {e}")


# Re-export the essentials
__all__ = [
    "CommandStatus",
    "FlextCliCommand",
    "FlextCliOutputFormat",
    "FlextCliSession",
    "FlextResult",
]
