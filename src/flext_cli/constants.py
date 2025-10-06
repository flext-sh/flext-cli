"""FLEXT CLI Constants - Centralized constants, enums, and literals.

Domain-specific constants extending flext-core standardization for CLI operations.
All literals, strings, numbers, enums, and configuration defaults centralized here.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from enum import StrEnum
from typing import Final

from flext_core import FlextConstants, FlextTypes


class FlextCliConstants(FlextConstants):
    """CLI constants extending flext-core standardization for CLI domain.

    Centralizes all CLI-specific constants, enums, literals, and defaults
    without duplication or wrappers, using direct access patterns.
    """

    # Directory and file names
    FLEXT_DIR_NAME: Final[str] = ".flext"
    AUTH_DIR_NAME: Final[str] = "auth"
    TOKEN_FILE_NAME: Final[str] = "token.json"
    REFRESH_TOKEN_FILE_NAME: Final[str] = "refresh_token.json"

    # Default paths
    DEFAULT_FLEXT_DIR: Final[str] = f"~/{FLEXT_DIR_NAME}"
    DEFAULT_TOKEN_PATH: Final[str] = f"{DEFAULT_FLEXT_DIR}/{TOKEN_FILE_NAME}"
    DEFAULT_REFRESH_TOKEN_PATH: Final[str] = (
        f"{DEFAULT_FLEXT_DIR}/{REFRESH_TOKEN_FILE_NAME}"
    )

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
    OUTPUT_FORMATS_LIST: Final[FlextTypes.StringList] = [
        OutputFormats.JSON.value,
        OutputFormats.YAML.value,
        OutputFormats.CSV.value,
        OutputFormats.TABLE.value,
        OutputFormats.PLAIN.value,
    ]

    LOG_LEVELS_LIST: Final[FlextTypes.StringList] = [
        "DEBUG",
        "INFO",
        "WARNING",
        "ERROR",
        "CRITICAL",
    ]

    COMMAND_STATUSES_LIST: Final[FlextTypes.StringList] = [
        CommandStatus.PENDING.value,
        CommandStatus.RUNNING.value,
        CommandStatus.COMPLETED.value,
        CommandStatus.FAILED.value,
    ]

    ERROR_CODES_LIST: Final[FlextTypes.StringList] = [
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

    class Shell:
        """Shell-specific constants."""

        # Built-in shell commands
        EXIT: Final[str] = "exit"
        QUIT: Final[str] = "quit"
        Q: Final[str] = "q"
        HISTORY: Final[str] = "history"
        CLEAR: Final[str] = "clear"
        HELP: Final[str] = "help"
        COMMANDS: Final[str] = "commands"
        SESSION: Final[str] = "session"

        # Shell command list
        BUILTIN_COMMANDS: Final[FlextTypes.StringList] = [
            EXIT,
            QUIT,
            Q,
            HISTORY,
            CLEAR,
            HELP,
            COMMANDS,
            SESSION,
        ]

        # Default prompt
        DEFAULT_PROMPT: Final[str] = "> "

    class Auth:
        """CLI authentication constants."""

        TOKEN_FILENAME: Final[str] = "token.json"
        CONFIG_FILENAME: Final[str] = "auth.json"
        MIN_USERNAME_LENGTH: Final[int] = 3
        MIN_PASSWORD_LENGTH: Final[int] = 6

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

    HTTP_METHODS_LIST: Final[FlextTypes.StringList] = [
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

    MESSAGE_TYPES_LIST: Final[FlextTypes.StringList] = [
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

    # File formats configuration
    FILE_FORMATS: Final[dict[str, dict[str, list[str]]]] = {
        "json": {"extensions": ["json"]},
        "yaml": {"extensions": ["yaml", "yml"]},
        "csv": {"extensions": ["csv"]},
        "tsv": {"extensions": ["tsv"]},
        "toml": {"extensions": ["toml"]},
        "xml": {"extensions": ["xml"]},
    }

    # Service names
    FLEXT_CLI_FILE_TOOLS: Final[str] = "flext-cli-file-tools"

    # Version constants
    VERSION: Final[str] = "2.0.0"

    # Table formats for tabulate integration
    TABLE_FORMATS: Final[FlextTypes.StringDict] = {
        "plain": "Minimal formatting, no borders",
        "simple": "Simple ASCII borders",
        "grid": "Grid-style ASCII table",
        "fancy_grid": "Fancy grid with double lines",
        "pipe": "Markdown pipe table",
        "orgtbl": "Emacs org-mode table",
        "jira": "Jira markup table",
        "presto": "Presto SQL output",
        "pretty": "Pretty ASCII table",
        "psql": "PostgreSQL psql output",
        "rst": "reStructuredText grid",
        "mediawiki": "MediaWiki markup",
        "moinmoin": "MoinMoin markup",
        "youtrack": "YouTrack markup",
        "html": "HTML table",
        "unsafehtml": "Unsafe HTML table",
        "latex": "LaTeX table",
        "latex_raw": "Raw LaTeX table",
        "latex_booktabs": "LaTeX booktabs table",
        "latex_longtable": "LaTeX longtable",
        "textile": "Textile markup",
        "tsv": "Tab-separated values",
    }


__all__ = [
    "FlextCliConstants",
]
