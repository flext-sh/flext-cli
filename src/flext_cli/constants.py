"""FLEXT CLI Constants - Centralized constants, enums, and literals.

Domain-specific constants extending flext-core standardization for CLI operations.
All literals, strings, numbers, enums, and configuration defaults centralized here.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from enum import StrEnum
from pathlib import Path
from typing import Final

from flext_core import FlextConstants


class FlextCliConstants:
    """CLI constants extending flext-core standardization for CLI domain.

    Centralizes all CLI-specific constants, enums, literals, and defaults
    without duplication or wrappers, using direct access patterns.
    """

    class Network:
        """Network-related constants extending flext-core."""

        # Inherit from flext-core
        DEFAULT_TIMEOUT: Final[int] = FlextConstants.Network.DEFAULT_TIMEOUT
        DEFAULT_API_PORT: Final[int] = FlextConstants.Platform.FLEXT_API_PORT

    class Files:
        """File operation constants for CLI operations."""

        default_encoding: Final[str] = "utf-8"
        default_mode: Final[str] = "r"

    # Directory and file names
    FLEXT_DIR_NAME: Final[str] = ".flext"
    AUTH_DIR_NAME: Final[str] = "auth"
    TOKEN_FILE_NAME: Final[str] = "token.json"
    REFRESH_TOKEN_FILE_NAME: Final[str] = "refresh_token.json"

    class Defaults:
        """Default configuration values for CLI operations."""

        OUTPUT_FORMAT: Final[str] = "table"
        LOG_LEVEL: Final[str] = "INFO"
        CONFIG_DIR: Final[Path] = Path.home() / ".flext"
        CONFIG_FILE: Final[str] = "flext.toml"
        PROFILE: Final[str] = "default"
        MAX_WIDTH: Final[int] = 120
        SHOW_HEADERS: Final[bool] = True
        COLOR_OUTPUT: Final[bool] = True

    class ExitCodes:
        """CLI exit codes for process management."""

        SUCCESS: Final[int] = 0
        FAILURE: Final[int] = 1
        CONFIG_ERROR: Final[int] = 2
        COMMAND_ERROR: Final[int] = 3

    class OutputFormats(StrEnum):
        """Available output formats for CLI data display."""

        TABLE = "table"
        JSON = "json"
        YAML = "yaml"
        CSV = "csv"
        PLAIN = "plain"

    class CommandStatus(StrEnum):
        """CLI command execution status values."""

        PENDING = "pending"
        RUNNING = "running"
        COMPLETED = "completed"
        FAILED = "failed"

    class LogLevels(StrEnum):
        """Available logging levels for CLI operations."""

        DEBUG = "DEBUG"
        INFO = "INFO"
        WARNING = "WARNING"
        ERROR = "ERROR"
        CRITICAL = "CRITICAL"

    class ErrorCodes(StrEnum):
        """CLI-specific error codes for categorization."""

        CLI_ERROR = "CLI_ERROR"
        VALIDATION_ERROR = "VALIDATION_ERROR"
        CONFIGURATION_ERROR = "CONFIGURATION_ERROR"
        CONNECTION_ERROR = "CONNECTION_ERROR"
        AUTHENTICATION_ERROR = "AUTHENTICATION_ERROR"
        COMMAND_ERROR = "COMMAND_ERROR"
        TIMEOUT_ERROR = "TIMEOUT_ERROR"
        FORMAT_ERROR = "FORMAT_ERROR"

    # HTTP constants for API operations
    class HTTP:
        """HTTP-related constants for CLI API operations."""
        
        GET = "GET"
        POST = "POST"
        PUT = "PUT"
        DELETE = "DELETE"
        PATCH = "PATCH"
        HEAD = "HEAD"
        OPTIONS = "OPTIONS"

    # Timeout constants
    class TIMEOUTS:
        """Timeout-related constants for CLI operations."""
        
        DEFAULT: Final[int] = 30
        SHORT: Final[int] = 5
        MEDIUM: Final[int] = 30
        LONG: Final[int] = 300
        EXTENDED: Final[int] = 600

    # Status constants for backward compatibility
    STATUS_PENDING: Final[str] = CommandStatus.PENDING.value
    STATUS_RUNNING: Final[str] = CommandStatus.RUNNING.value
    STATUS_COMPLETED: Final[str] = CommandStatus.COMPLETED.value
    STATUS_FAILED: Final[str] = CommandStatus.FAILED.value

    # Static lists derived from enums
    OUTPUT_FORMATS_LIST: Final[list[str]] = [
        format_type.value for format_type in OutputFormats
    ]
    COMMAND_STATUSES_LIST: Final[list[str]] = [status.value for status in CommandStatus]
    LOG_LEVELS_LIST: Final[list[str]] = [level.value for level in LogLevels]
    ERROR_CODES_LIST: Final[list[str]] = [code.value for code in ErrorCodes]


__all__ = [
    "FlextCliConstants",
]
