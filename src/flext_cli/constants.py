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

    # Project identification (Final attributes inherited from FlextConstants)
    # PROJECT_PREFIX inherited from FlextConstants
    # PROJECT_NAME inherited from FlextConstants

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
        VALIDATION_ERROR = "CLI_VALIDATION_ERROR"
        CONFIGURATION_ERROR = "CLI_CONFIGURATION_ERROR"
        CONNECTION_ERROR = "CLI_CONNECTION_ERROR"
        AUTHENTICATION_ERROR = "CLI_AUTHENTICATION_ERROR"
        COMMAND_ERROR = "CLI_COMMAND_ERROR"
        TIMEOUT_ERROR = "CLI_TIMEOUT_ERROR"
        FORMAT_ERROR = "CLI_FORMAT_ERROR"

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

    class PipelineDefaults:
        """Pipeline and batch processing defaults."""

        MIN_STEP_TIMEOUT_SECONDS: Final[int] = 10
        MAX_BATCH_SIZE_PARALLEL: Final[int] = 100
        STEP_BASELINE_DURATION_SECONDS: Final[int] = 30
        RETRY_OVERHEAD_SECONDS: Final[int] = 10

    class NetworkDefaults:
        """Network-related defaults for CLI operations."""

        DEFAULT_API_URL: Final[str] = (
            f"http://{FlextConstants.Platform.DEFAULT_HOST}:{FlextConstants.Platform.FLEXT_API_PORT}/api"
        )
        DEFAULT_TIMEOUT: Final[int] = 30
        DEFAULT_MAX_RETRIES: Final[int] = 3
        CONNECT_TIMEOUT: Final[int] = 10
        READ_TIMEOUT: Final[int] = 60

    class PhoneValidation:
        """Phone number validation constants."""

        MIN_INTERNATIONAL_DIGITS: Final[int] = 10
        MAX_INTERNATIONAL_DIGITS: Final[int] = 15
        US_PHONE_DIGITS: Final[int] = 10

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

    class HttpMethods(StrEnum):
        """HTTP method constants."""

        GET = "GET"
        POST = "POST"
        PUT = "PUT"
        DELETE = "DELETE"
        PATCH = "PATCH"
        HEAD = "HEAD"
        OPTIONS = "OPTIONS"

    HTTP_METHODS_LIST: Final[list[str]] = [
        "GET",
        "POST",
        "PUT",
        "DELETE",
        "PATCH",
        "HEAD",
        "OPTIONS",
    ]

    class MessageTypes(StrEnum):
        """Message type constants for CLI output."""

        INFO = "info"
        ERROR = "error"
        WARNING = "warning"
        SUCCESS = "success"
        DEBUG = "debug"

    MESSAGE_TYPES_LIST: Final[list[str]] = [
        MessageTypes.INFO.value,
        MessageTypes.ERROR.value,
        MessageTypes.WARNING.value,
        MessageTypes.SUCCESS.value,
        MessageTypes.DEBUG.value,
    ]

    class TIMEOUTS:
        """Timeout constants."""

        DEFAULT: Final[int] = 30
        CONNECTION: Final[int] = 10
        READ: Final[int] = 30
        WRITE: Final[int] = 30
        COMMAND: Final[int] = 300

    # Status constants for service operations
    OPERATIONAL: Final[str] = "operational"
    AVAILABLE: Final[str] = "available"

    # Service names
    FLEXT_CLI: Final[str] = "flext-cli"

    # User IDs for testing
    USER1: Final[str] = "user1"
    USER2: Final[str] = "user2"

    # Table column names
    VALUE: Final[str] = "Value"

    # Additional status constants
    CONNECTED: Final[str] = "connected"
    HEALTHY: Final[str] = "healthy"
    TRACE: Final[str] = "trace"

    # Default values
    DEFAULT: Final[str] = "default"
    TABLE: Final[str] = "table"

    # Directory labels
    HOME: Final[str] = "Home"
    CONFIG: Final[str] = "Config"
    CACHE: Final[str] = "Cache"
    LOGS: Final[str] = "Logs"

    # MIME types
    APPLICATION_JSON: Final[str] = "application/json"
    APPLICATION_YAML: Final[str] = "application/x-yaml"
    TEXT_CSV: Final[str] = "text/csv"
    TEXT_TSV: Final[str] = "text/tab-separated-values"

    # Format names
    TSV: Final[str] = "tsv"

    # Service names
    FLEXT_CLI_FILE_TOOLS: Final[str] = "flext-cli-file-tools"


__all__ = [
    "FlextCliConstants",
]
