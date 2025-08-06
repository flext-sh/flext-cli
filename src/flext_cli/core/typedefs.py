"""FlextCli Type Definitions - Zero-Boilerplate Foundation Types.

This module provides essential type definitions for massive boilerplate reduction
in CLI applications. All types use FlextCli prefix and follow flext-core patterns.

Core Benefits:
    - Type-safe CLI patterns with 85% boilerplate reduction
    - Full flext-core FlextResult integration
    - Rich console and progress types for UI
    - Zero-configuration validation patterns

Examples:
    >>> from flext_cli import FlextCliCommand, flext_cli_execute_command
    >>>
    >>> @flext_cli_execute_command
    >>> def my_command() -> FlextResult[str]:
    ...     return FlextResult.ok("Success")

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Callable
from enum import Enum
from pathlib import Path
from typing import Protocol, TypedDict

from flext_core import FlextResult
from rich.console import Console
from rich.progress import Progress

# Core FlextCli Type Aliases (no duplication with flext-core)
type FlextCliResult[T] = FlextResult[T]
type FlextCliPath = str | Path
type FlextCliConsole = Console
type FlextCliProgress = Progress


# Command Status and Types
class FlextCliCommandStatus(Enum):
    """FlextCli command execution status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class FlextCliCommandType(Enum):
    """FlextCli command type classification."""

    INTERACTIVE = "interactive"
    BATCH = "batch"
    DAEMON = "daemon"
    ONESHOT = "oneshot"


class FlextCliOutputFormat(Enum):
    """FlextCli output format options."""

    TABLE = "table"
    JSON = "json"
    YAML = "yaml"
    CSV = "csv"
    PLAIN = "plain"


class FlextCliLogLevel(Enum):
    """FlextCli logging levels."""

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


# Configuration Types
class FlextCliConfigData(TypedDict, total=False):
    """FlextCli configuration data structure."""

    profile: str
    debug: bool
    log_level: str
    output_format: str
    api_base_url: str | None
    auth_token: str | None
    config_path: str | None
    timeout: int | None


class FlextCliValidationType(Enum):
    """FlextCli input validation types."""

    EMAIL = "email"
    URL = "url"
    PATH = "path"
    FILE = "file"
    DIR = "dir"
    UUID = "uuid"
    PORT = "port"


class FlextCliValidationRule(TypedDict):
    """FlextCli validation rule definition."""

    field: str
    validation_type: str
    required: bool
    default: object | None
    error_message: str | None


# Handler Types
type FlextCliCommandHandler = Callable[[], FlextCliResult[object]]
type FlextCliValidationHandler = Callable[[str], FlextCliResult[bool]]
type FlextCliProgressHandler = Callable[[int, int], None]


# Protocol Definitions
class FlextCliCommandProtocol(Protocol):
    """FlextCli command protocol."""

    name: str
    description: str

    def execute(self) -> FlextCliResult[object]:
        """Execute the command with FlextResult pattern."""
        ...


class FlextCliConfigProtocol(Protocol):
    """FlextCli configuration protocol."""

    profile: str
    debug: bool

    def load_config(self, path: str | None = None) -> FlextCliResult[None]:
        """Load configuration from path using FlextResult pattern."""
        ...


# Modern Type Patterns
FlextCliCommonTypes = str | int | float | bool | Path
FlextCliOptionalTypes = FlextCliCommonTypes | None

type FlextCliDecorator = Callable[[Callable[[object], object]], Callable[[object], FlextCliResult[object]]]
type FlextCliValidator = Callable[[object], FlextCliResult[bool]]


# Utility Functions
def flext_cli_command_result(data: object) -> FlextCliResult[object]:
    """Create successful FlextCli command result."""
    return FlextResult.ok(data)


def flext_cli_command_error(error: str) -> FlextCliResult[object]:
    """Create FlextCli command error result."""
    return FlextResult.fail(error)
