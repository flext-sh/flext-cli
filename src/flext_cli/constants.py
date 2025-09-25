"""FLEXT CLI Constants - Centralized constants, enums, and literals.

Domain-specific constants extending flext-core standardization for CLI operations.
All literals, strings, numbers, enums, and configuration defaults centralized here.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from enum import StrEnum
from typing import Final

from flext_core import FlextConstants


class FlextCliConstants(FlextConstants):
    """CLI constants extending flext-core standardization for CLI domain.

    Centralizes all CLI-specific constants, enums, literals, and defaults
    without duplication or wrappers, using direct access patterns.
    """

    # Project identification (inherited from BaseProjectConstants)
    PROJECT_PREFIX: Final[str] = "FLEXT_CLI"
    PROJECT_NAME: Final[str] = "FLEXT CLI"

    # Directory and file names
    FLEXT_DIR_NAME: Final[str] = ".flext"
    AUTH_DIR_NAME: Final[str] = "auth"
    TOKEN_FILE_NAME: Final[str] = "token.json"
    REFRESH_TOKEN_FILE_NAME: Final[str] = "refresh_token.json"

    class CommandStatus(StrEnum):
        """Command execution status enum."""

        PENDING = "pending"
        RUNNING = "running"
        COMPLETED = "completed"
        FAILED = "failed"

    class OutputFormats(StrEnum):
        """Output format options for CLI operations."""

        JSON = "json"
        YAML = "yaml"
        CSV = "csv"
        TABLE = "table"
        PLAIN = "plain"

    class ErrorCodes(StrEnum):
        """CLI error codes."""

        CLI_ERROR = "CLI_ERROR"
        VALIDATION_ERROR = "VALIDATION_ERROR"
        CONFIGURATION_ERROR = "CONFIGURATION_ERROR"
        CONNECTION_ERROR = "CONNECTION_ERROR"
        AUTHENTICATION_ERROR = "AUTHENTICATION_ERROR"
        COMMAND_ERROR = "COMMAND_ERROR"
        TIMEOUT_ERROR = "TIMEOUT_ERROR"
        FORMAT_ERROR = "FORMAT_ERROR"

    class ExitCodes:
        """CLI exit codes."""

        SUCCESS: Final[int] = 0
        FAILURE: Final[int] = 1
        CONFIG_ERROR: Final[int] = 2
        COMMAND_ERROR: Final[int] = 3
        TIMEOUT_ERROR: Final[int] = 4
        AUTHENTICATION_ERROR: Final[int] = 5

    class CliDefaults:
        """CLI default values."""

        CONFIG_FILE: Final[str] = "config.json"
        MAX_WIDTH: Final[int] = 120
        DEFAULT_MAX_WIDTH: Final[int] = 120
        DEFAULT_PROFILE: Final[str] = "default"
        DEFAULT_OUTPUT_FORMAT: Final[str] = "table"
        DEFAULT_TIMEOUT: Final[int] = 30

    class NetworkDefaults:
        """Network-related defaults for CLI operations."""

        DEFAULT_API_URL: Final[str] = "http://localhost:8080/api"
        DEFAULT_TIMEOUT: Final[int] = 30
        DEFAULT_MAX_RETRIES: Final[int] = 3
        CONNECT_TIMEOUT: Final[int] = 10
        READ_TIMEOUT: Final[int] = 60

    # Constant lists for validation and iteration
    OUTPUT_FORMATS_LIST: Final[list[str]] = [
        OutputFormats.JSON.value,
        OutputFormats.YAML.value,
        OutputFormats.CSV.value,
        OutputFormats.TABLE.value,
        OutputFormats.PLAIN.value,
    ]

    LOG_LEVELS_LIST: Final[list[str]] = [
        "DEBUG",
        "INFO",
        "WARNING",
        "ERROR",
        "CRITICAL",
    ]

    COMMAND_STATUSES_LIST: Final[list[str]] = [
        CommandStatus.PENDING.value,
        CommandStatus.RUNNING.value,
        CommandStatus.COMPLETED.value,
        CommandStatus.FAILED.value,
    ]

    ERROR_CODES_LIST: Final[list[str]] = [
        ErrorCodes.CLI_ERROR.value,
        ErrorCodes.VALIDATION_ERROR.value,
        ErrorCodes.CONFIGURATION_ERROR.value,
        ErrorCodes.CONNECTION_ERROR.value,
        ErrorCodes.AUTHENTICATION_ERROR.value,
        ErrorCodes.COMMAND_ERROR.value,
        ErrorCodes.TIMEOUT_ERROR.value,
        ErrorCodes.FORMAT_ERROR.value,
    ]

    # Legacy constants from application_commands.py
    STATUS_PENDING: Final[str] = CommandStatus.PENDING.value
    STATUS_RUNNING: Final[str] = CommandStatus.RUNNING.value
    STATUS_COMPLETED: Final[str] = CommandStatus.COMPLETED.value
    STATUS_FAILED: Final[str] = CommandStatus.FAILED.value

    class Commands:
        """CLI command name constants."""

        AUTH: Final[str] = "auth"
        CONFIG: Final[str] = "config"
        DEBUG: Final[str] = "debug"
        FORMAT: Final[str] = "format"
        EXPORT: Final[str] = "export"

    class Auth:
        """CLI authentication constants."""

        TOKEN_FILENAME: Final[str] = "token.json"
        CONFIG_FILENAME: Final[str] = "auth.json"

    class Session:
        """CLI session constants."""

        DEFAULT_TIMEOUT: Final[int] = 3600
        MAX_COMMANDS: Final[int] = 1000

    class Services:
        """CLI service name constants."""

        API: Final[str] = "api"
        FORMATTER: Final[str] = "formatter"
        AUTH: Final[str] = "auth"

    class Protocols:
        """CLI protocol constants."""

        HTTP: Final[str] = "http"
        HTTPS: Final[str] = "https"

    class HTTP:
        """HTTP-related constants."""

        DEFAULT_TIMEOUT: Final[int] = 30
        MAX_RETRIES: Final[int] = 3
        RETRY_DELAY: Final[int] = 1
        USER_AGENT: Final[str] = "FlextCLI/1.0"

    class TIMEOUTS:
        """Timeout constants."""

        DEFAULT: Final[int] = 30
        CONNECTION: Final[int] = 10
        READ: Final[int] = 30
        WRITE: Final[int] = 30
        COMMAND: Final[int] = 300


__all__ = [
    "FlextCliConstants",
]
