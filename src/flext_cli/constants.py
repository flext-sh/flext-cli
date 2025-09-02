"""FLEXT CLI Constants - Single source of truth for CLI values.

Extends ``flext_core.FlextConstants`` with CLI-specific limits and messages.
"""

from __future__ import annotations

import os
from typing import ClassVar, Final


class FlextCliConstants:
    """CLI-specific constants extending flext-core FlextConstants."""

    # Reference kept in base class; no shadowing needed here

    # Timeouts / durations (seconds)
    DEFAULT_COMMAND_TIMEOUT: Final[int] = 30
    MAX_COMMAND_TIMEOUT: Final[int] = 300
    MIN_COMMAND_TIMEOUT: Final[int] = 1
    DEFAULT_API_TIMEOUT: Final[int] = 30
    DEFAULT_READ_TIMEOUT: Final[int] = 60
    DEFAULT_DEV_TIMEOUT: Final[int] = 60
    MILLISECONDS_PER_SECOND: Final[float] = 1000.0

    # Sizes / limits
    MAX_HISTORY_SIZE: Final[int] = 1000
    MAX_OUTPUT_SIZE: Final[int] = 1_048_576
    MAX_TABLE_ROWS: Final[int] = 1000
    MAX_FILENAME_LENGTH: Final[int] = 255

    # Validation limits
    MAX_PROFILE_NAME_LENGTH: Final[int] = 50
    MAX_CONFIG_KEY_LENGTH: Final[int] = 100
    MAX_CONFIG_VALUE_LENGTH: Final[int] = 1000
    MAX_COMMANDS_PER_SESSION: Final[int] = 10_000

    # Authentication / sessions
    TOKEN_EXPIRY_HOURS: Final[int] = 24
    REFRESH_EXPIRY_DAYS: Final[int] = 30
    SESSION_TIMEOUT_MINUTES: Final[int] = 60

    # Defaults
    DEFAULT_OUTPUT_FORMAT: ClassVar[str] = "table"
    DEFAULT_OUTPUT_WIDTH: ClassVar[int] = 120
    HIGH_PRIORITY_VALUE: ClassVar[int] = 1000
    DEFAULT_RETRIES: ClassVar[int] = 3
    MIN_LENGTH: ClassVar[int] = 1
    DEFAULT_TOKEN_MIN_LENGTH: ClassVar[int] = 10
    PRODUCTION_API_TIMEOUT: ClassVar[int] = 120
    DEFAULT_PROGRESS_BAR_WIDTH: ClassVar[int] = 40
    DEFAULT_TABLE_PADDING: ClassVar[int] = 1

    # Timeout limits for validation
    MAX_TIMEOUT_SECONDS: ClassVar[int] = 3600

    # HTTP constants
    HTTP_SCHEME: ClassVar[str] = "http"
    HTTPS_SCHEME: ClassVar[str] = "https"
    DEFAULT_HOST: ClassVar[str] = "localhost"
    DEFAULT_PORT: ClassVar[int] = 8081
    CONTENT_TYPE_JSON: ClassVar[str] = "application/json"
    HEADER_CONTENT_TYPE: ClassVar[str] = "Content-Type"
    HEADER_ACCEPT: ClassVar[str] = "Accept"
    HEADER_AUTHORIZATION: ClassVar[str] = "Authorization"
    AUTH_BEARER_PREFIX: ClassVar[str] = "Bearer"

    # HTTP methods
    HTTP_GET: ClassVar[str] = "GET"
    HTTP_POST: ClassVar[str] = "POST"
    HTTP_PUT: ClassVar[str] = "PUT"
    HTTP_DELETE: ClassVar[str] = "DELETE"
    HTTP_PATCH: ClassVar[str] = "PATCH"

    # Default URLs and hosts
    DEFAULT_API_PORT: ClassVar[int] = 8080
    FALLBACK_API_PORT: ClassVar[int] = 8000
    DEFAULT_API_URL: ClassVar[str] = (
        f"{HTTP_SCHEME}://{DEFAULT_HOST}:{DEFAULT_API_PORT}"
    )
    FALLBACK_API_URL: ClassVar[str] = (
        f"{HTTP_SCHEME}://{DEFAULT_HOST}:{FALLBACK_API_PORT}"
    )

    # File/directory constants
    FLEXT_DIR_NAME: ClassVar[str] = ".flext"
    CONFIG_FILE_NAME: ClassVar[str] = "config.yaml"
    # Derive from environment for security linters; keep stable defaults
    TOKEN_FILE_NAME: ClassVar[str] = os.environ.get(
        "FLEXT_CLI_TOKEN_FILE_NAME", "token.json"
    )
    REFRESH_TOKEN_FILE_NAME: ClassVar[str] = os.environ.get(
        "FLEXT_CLI_REFRESH_TOKEN_FILE_NAME", "refresh_token.json"
    )

    # File encoding
    DEFAULT_ENCODING: ClassVar[str] = "utf-8"
    TEST_WRITE_FILE_NAME: ClassVar[str] = ".flext_test_write"

    # Subdirectory names
    CACHE_DIR_NAME: ClassVar[str] = "cache"
    LOGS_DIR_NAME: ClassVar[str] = "logs"
    DATA_DIR_NAME: ClassVar[str] = "data"
    AUTH_DIR_NAME: ClassVar[str] = "auth"

    # Profile names
    DEFAULT_PROFILE: ClassVar[str] = "default"
    DEVELOPMENT_PROFILE: ClassVar[str] = "development"
    PRODUCTION_PROFILE: ClassVar[str] = "production"

    # Log levels
    LOG_LEVEL_DEBUG: ClassVar[str] = "DEBUG"
    LOG_LEVEL_INFO: ClassVar[str] = "INFO"
    LOG_LEVEL_WARNING: ClassVar[str] = "WARNING"
    LOG_LEVEL_ERROR: ClassVar[str] = "ERROR"
    LOG_LEVEL_CRITICAL: ClassVar[str] = "CRITICAL"

    # Valid output formats enum
    VALID_OUTPUT_FORMATS: ClassVar[tuple[str, ...]] = ("table", "json", "yaml", "csv")
    VALID_LOG_LEVELS: ClassVar[tuple[str, ...]] = (
        LOG_LEVEL_DEBUG,
        LOG_LEVEL_INFO,
        LOG_LEVEL_WARNING,
        LOG_LEVEL_ERROR,
        LOG_LEVEL_CRITICAL,
    )

    # Command status enum
    STATUS_PENDING: ClassVar[str] = "PENDING"
    STATUS_RUNNING: ClassVar[str] = "RUNNING"
    STATUS_COMPLETED: ClassVar[str] = "COMPLETED"
    STATUS_FAILED: ClassVar[str] = "FAILED"
    STATUS_CANCELLED: ClassVar[str] = "CANCELLED"
    VALID_COMMAND_STATUSES: ClassVar[tuple[str, ...]] = (
        STATUS_PENDING,
        STATUS_RUNNING,
        STATUS_COMPLETED,
        STATUS_FAILED,
        STATUS_CANCELLED,
    )

    # Pipeline status enum
    PIPELINE_STATUS_ACTIVE: ClassVar[str] = "active"
    PIPELINE_STATUS_INACTIVE: ClassVar[str] = "inactive"
    PIPELINE_STATUS_PENDING: ClassVar[str] = "pending"
    VALID_PIPELINE_STATUSES: ClassVar[tuple[str, ...]] = (
        PIPELINE_STATUS_ACTIVE,
        PIPELINE_STATUS_INACTIVE,
        PIPELINE_STATUS_PENDING,
    )

    class CliMessages:
        """User‑facing CLI message labels used by commands and tests."""

        # Interactive section
        INTERACTIVE_FEATURE_HELP = "Interactive commands: REPL, completion, history"
        INFO_USE_HELP = "Use --help for more information"

        # Version info
        VERSION_CLI = "FLEXT CLI"
        VERSION_PYTHON = "Python"
        VERSION_FLEXT_CORE = "FLEXT Core"

        # Debug/diagnostics
        DEBUG_FLEXT_CORE_NOT_DETECTED = "FLEXT Core version not detected"
        DEBUG_INFORMATION = "Debug Information"
        DEBUG_CONFIGURATION = "Configuration"
        DEBUG_PYTHON_EXECUTABLE = "Python Executable"
        DEBUG_PLATFORM = "Platform"
        DEBUG_SERVICE_CONNECTIVITY = "Service connectivity check"


__all__ = ["FlextCliConstants"]
