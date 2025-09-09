"""FLEXT CLI Constants - Structured configuration using Pydantic models.

Replaces loose constants with structured Pydantic models following flext-core patterns.
Eliminates loose constants in favor of type-safe, validated configuration structures.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import os
from enum import StrEnum
from typing import ClassVar, Final

from pydantic import BaseModel, Field


class FlextCliConstants:
    """CLI constants structured as Pydantic models extending flext-core patterns."""

    class TimeoutConfig(BaseModel):
        """Timeout and duration configuration with validation."""

        default_command_timeout: int = Field(default=30, ge=1, le=3600)
        max_command_timeout: int = Field(default=300, ge=1, le=3600)
        min_command_timeout: int = Field(default=1, ge=1, le=60)
        default_api_timeout: int = Field(default=30, ge=1, le=300)
        default_read_timeout: int = Field(default=60, ge=1, le=300)
        default_dev_timeout: int = Field(default=60, ge=1, le=300)
        production_api_timeout: int = Field(default=120, ge=30, le=600)
        session_timeout_minutes: int = Field(default=60, ge=1, le=1440)
        token_expiry_hours: int = Field(default=24, ge=1, le=168)
        refresh_expiry_days: int = Field(default=30, ge=1, le=365)
        milliseconds_per_second: float = Field(default=1000.0, frozen=True)

    class LimitsConfig(BaseModel):
        """Size and validation limits with constraints."""

        max_history_size: int = Field(default=1000, ge=1, le=100000)
        max_output_size: int = Field(default=1_048_576, ge=1024, le=10_485_760)
        max_table_rows: int = Field(default=1000, ge=1, le=10000)
        max_filename_length: int = Field(default=255, ge=1, le=255)
        max_profile_name_length: int = Field(default=50, ge=1, le=100)
        max_config_key_length: int = Field(default=100, ge=1, le=200)
        max_config_value_length: int = Field(default=1000, ge=1, le=10000)
        max_commands_per_session: int = Field(default=10_000, ge=1, le=100_000)
        max_env_var_display_length: int = Field(default=60, ge=1, le=200)
        max_timeout_seconds: int = Field(default=3600, ge=1, le=86400)

    class DataStructureConfig(BaseModel):
        """Data structure configuration for tuple processing."""

        tuple_pair_length: int = Field(default=2, ge=2, le=10)
        min_service_id_length: int = Field(default=10, ge=1, le=50)

    class OutputConfig(BaseModel):
        """Output formatting configuration."""

        default_output_format: str = Field(
            default="table", pattern=r"^(table|json|yaml|csv)$"
        )
        default_output_width: int = Field(default=120, ge=40, le=400)
        default_progress_bar_width: int = Field(default=40, ge=10, le=100)
        default_table_padding: int = Field(default=1, ge=0, le=10)
        high_priority_value: int = Field(default=1000, ge=1, le=10000)
        default_retries: int = Field(default=3, ge=0, le=10)
        min_length: int = Field(default=1, ge=1, le=10)
        default_token_min_length: int = Field(default=10, ge=1, le=100)

    class SecurityConfig(BaseModel):
        """Security and privacy configuration."""

        sensitive_value_preview_length: int = Field(default=4, ge=1, le=10)
        min_path_length_for_masking: int = Field(default=4, ge=1, le=20)
        max_config_key_length: int = Field(default=100, ge=10, le=1000)
        max_output_size: int = Field(default=1048576, ge=1024, le=10485760)  # 1MB

    class HttpConfig(BaseModel):
        """HTTP client configuration with security defaults."""

        http_scheme: str = Field(default="http", frozen=True)
        https_scheme: str = Field(default="https", frozen=True)
        default_host: str = Field(default="localhost", min_length=1)
        default_port: int = Field(default=8081, ge=1, le=65535)
        default_api_port: int = Field(default=8080, ge=1, le=65535)
        fallback_api_port: int = Field(default=8000, ge=1, le=65535)
        content_type_json: str = Field(default="application/json", frozen=True)
        header_content_type: str = Field(default="Content-Type", frozen=True)
        header_accept: str = Field(default="Accept", frozen=True)
        header_authorization: str = Field(default="Authorization", frozen=True)
        auth_bearer_prefix: str = Field(default="Bearer", frozen=True)

        @property
        def default_api_url(self) -> str:
            """Generate default API URL from configuration."""
            return f"{self.http_scheme}://{self.default_host}:{self.default_api_port}"

        @property
        def fallback_api_url(self) -> str:
            """Generate fallback API URL from configuration."""
            return f"{self.http_scheme}://{self.default_host}:{self.fallback_api_port}"

    class FileConfig(BaseModel):
        """File and directory configuration with security."""

        flext_dir_name: str = Field(default=".flext", min_length=1)
        config_file_name: str = Field(default="config.yaml", min_length=1)
        default_encoding: str = Field(default="utf-8", frozen=True)
        test_write_file_name: str = Field(default=".flext_test_write", min_length=1)
        cache_dir_name: str = Field(default="cache", min_length=1)
        logs_dir_name: str = Field(default="logs", min_length=1)
        data_dir_name: str = Field(default="data", min_length=1)
        auth_dir_name: str = Field(default="auth", min_length=1)

        @property
        def token_file_name(self) -> str:
            """Get token file name from environment or default."""
            return os.environ.get("FLEXT_CLI_TOKEN_FILE_NAME", "token.json")

        @property
        def refresh_token_file_name(self) -> str:
            """Get refresh token file name from environment or default."""
            return os.environ.get(
                "FLEXT_CLI_REFRESH_TOKEN_FILE_NAME", "refresh_token.json"
            )

    class OutputFormat(StrEnum):
        """Valid output formats."""

        TABLE = "table"
        JSON = "json"
        YAML = "yaml"
        CSV = "csv"
        PLAIN = "plain"

    class LogLevel(StrEnum):
        """Valid log levels."""

        DEBUG = "DEBUG"
        INFO = "INFO"
        WARNING = "WARNING"
        ERROR = "ERROR"
        CRITICAL = "CRITICAL"

    class CommandStatus(StrEnum):
        """Valid command statuses."""

        PENDING = "PENDING"
        RUNNING = "RUNNING"
        COMPLETED = "COMPLETED"
        FAILED = "FAILED"
        CANCELLED = "CANCELLED"

    class PipelineStatus(StrEnum):
        """Valid pipeline statuses."""

        ACTIVE = "active"
        INACTIVE = "inactive"
        PENDING = "pending"

    class ProfileName(StrEnum):
        """Valid profile names."""

        DEFAULT = "default"
        DEVELOPMENT = "development"
        PRODUCTION = "production"

    class HttpMethod(StrEnum):
        """Valid HTTP methods."""

        GET = "GET"
        POST = "POST"
        PUT = "PUT"
        DELETE = "DELETE"
        PATCH = "PATCH"

    class MessageConfig(BaseModel):
        """User-facing CLI message configuration."""

        interactive_feature_help: str = Field(
            default="Interactive commands: REPL, completion, history", min_length=1
        )
        info_use_help: str = Field(
            default="Use --help for more information", min_length=1
        )
        version_cli: str = Field(default="FLEXT CLI", min_length=1)
        version_python: str = Field(default="Python", min_length=1)
        version_flext_core: str = Field(default="FLEXT Core", min_length=1)
        service_name_api: str = Field(default="FLEXT CLI API", min_length=1)
        table_title_config: str = Field(
            default="FLEXT Configuration v0.7.0", min_length=1
        )
        table_title_paths: str = Field(
            default="FLEXT Configuration Paths", min_length=1
        )
        table_title_metrics: str = Field(
            default="System Performance Metrics", min_length=1
        )
        table_title_env_vars: str = Field(
            default="FLEXT Environment Variables", min_length=1
        )
        table_title_cli_paths: str = Field(default="FLEXT CLI Paths", min_length=1)
        debug_flext_core_not_detected: str = Field(
            default="FLEXT Core version not detected", min_length=1
        )
        debug_information: str = Field(default="Debug Information", min_length=1)
        debug_configuration: str = Field(default="Configuration", min_length=1)
        debug_python_executable: str = Field(default="Python Executable", min_length=1)
        debug_platform: str = Field(default="Platform", min_length=1)
        debug_service_connectivity: str = Field(
            default="Service connectivity check", min_length=1
        )

    # =============================================================================
    # DEFAULT INSTANCES - Ready-to-use configurations
    # =============================================================================

    # Pre-configured instances for immediate use
    TIMEOUTS: ClassVar[TimeoutConfig] = TimeoutConfig()
    LIMITS: ClassVar[LimitsConfig] = LimitsConfig()
    OUTPUT: ClassVar[OutputConfig] = OutputConfig()
    SECURITY: ClassVar[SecurityConfig] = SecurityConfig()
    HTTP: ClassVar[HttpConfig] = HttpConfig()
    FILES: ClassVar[FileConfig] = FileConfig()
    MESSAGES: ClassVar[MessageConfig] = MessageConfig()

    # =============================================================================
    # BACKWARD COMPATIBILITY - Deprecated, use structured configs above
    # =============================================================================

    # Timeouts (DEPRECATED: Use TIMEOUTS.field_name instead)
    DEFAULT_COMMAND_TIMEOUT: Final[int] = TIMEOUTS.default_command_timeout
    MAX_COMMAND_TIMEOUT: Final[int] = TIMEOUTS.max_command_timeout
    MIN_COMMAND_TIMEOUT: Final[int] = TIMEOUTS.min_command_timeout
    DEFAULT_API_TIMEOUT: Final[int] = TIMEOUTS.default_api_timeout

    # Limits (DEPRECATED: Use LIMITS.field_name instead)
    MAX_HISTORY_SIZE: Final[int] = LIMITS.max_history_size

    # Output (DEPRECATED: Use OUTPUT.field_name instead)
    DEFAULT_OUTPUT_FORMAT: Final[str] = OUTPUT.default_output_format
    DEFAULT_OUTPUT_WIDTH: Final[int] = OUTPUT.default_output_width

    # HTTP (DEPRECATED: Use HTTP.field_name instead)
    DEFAULT_HOST: Final[str] = HTTP.default_host
    DEFAULT_PORT: Final[int] = HTTP.default_port
    DEFAULT_API_URL: Final[str] = HTTP.default_api_url
    FALLBACK_API_URL: Final[str] = HTTP.fallback_api_url
    CONTENT_TYPE_JSON: Final[str] = HTTP.content_type_json
    HEADER_CONTENT_TYPE: Final[str] = HTTP.header_content_type
    HEADER_ACCEPT: Final[str] = HTTP.header_accept
    HEADER_AUTHORIZATION: Final[str] = HTTP.header_authorization
    AUTH_BEARER_PREFIX: Final[str] = HTTP.auth_bearer_prefix
    HTTP_SCHEME: Final[str] = HTTP.http_scheme
    HTTPS_SCHEME: Final[str] = HTTP.https_scheme
    DEFAULT_API_PORT: Final[int] = HTTP.default_api_port
    FALLBACK_API_PORT: Final[int] = HTTP.fallback_api_port

    # Security (DEPRECATED: Use SECURITY.field_name instead)
    SENSITIVE_VALUE_PREVIEW_LENGTH: Final[int] = SECURITY.sensitive_value_preview_length
    MIN_PATH_LENGTH_FOR_MASKING: Final[int] = SECURITY.min_path_length_for_masking
    MAX_CONFIG_KEY_LENGTH: Final[int] = SECURITY.max_config_key_length
    MAX_OUTPUT_SIZE: Final[int] = SECURITY.max_output_size

    # Files (DEPRECATED: Use FILES.field_name instead)
    FLEXT_DIR_NAME: Final[str] = FILES.flext_dir_name
    CONFIG_FILE_NAME: Final[str] = FILES.config_file_name
    DEFAULT_ENCODING: Final[str] = FILES.default_encoding
    TEST_WRITE_FILE_NAME: Final[str] = FILES.test_write_file_name
    CACHE_DIR_NAME: Final[str] = FILES.cache_dir_name
    LOGS_DIR_NAME: Final[str] = FILES.logs_dir_name
    DATA_DIR_NAME: Final[str] = FILES.data_dir_name
    AUTH_DIR_NAME: Final[str] = FILES.auth_dir_name
    TOKEN_FILE_NAME: Final[str] = FILES.token_file_name
    REFRESH_TOKEN_FILE_NAME: Final[str] = FILES.refresh_token_file_name

    # Messages (DEPRECATED: Use MESSAGES.field_name instead)
    SERVICE_NAME_API: Final[str] = MESSAGES.service_name_api
    TABLE_TITLE_CONFIG: Final[str] = MESSAGES.table_title_config
    TABLE_TITLE_PATHS: Final[str] = MESSAGES.table_title_paths
    TABLE_TITLE_METRICS: Final[str] = MESSAGES.table_title_metrics
    TABLE_TITLE_ENV_VARS: Final[str] = MESSAGES.table_title_env_vars
    TABLE_TITLE_CLI_PATHS: Final[str] = MESSAGES.table_title_cli_paths

    # More timeouts and limits
    DEFAULT_READ_TIMEOUT: Final[int] = TIMEOUTS.default_read_timeout
    DEFAULT_DEV_TIMEOUT: Final[int] = TIMEOUTS.default_dev_timeout
    PRODUCTION_API_TIMEOUT: Final[int] = TIMEOUTS.production_api_timeout
    SESSION_TIMEOUT_MINUTES: Final[int] = TIMEOUTS.session_timeout_minutes
    TOKEN_EXPIRY_HOURS: Final[int] = TIMEOUTS.token_expiry_hours
    REFRESH_EXPIRY_DAYS: Final[int] = TIMEOUTS.refresh_expiry_days
    MILLISECONDS_PER_SECOND: Final[float] = TIMEOUTS.milliseconds_per_second

    MAX_TABLE_ROWS: Final[int] = LIMITS.max_table_rows
    MAX_FILENAME_LENGTH: Final[int] = LIMITS.max_filename_length
    MAX_PROFILE_NAME_LENGTH: Final[int] = LIMITS.max_profile_name_length
    MAX_CONFIG_VALUE_LENGTH: Final[int] = LIMITS.max_config_value_length
    MAX_COMMANDS_PER_SESSION: Final[int] = LIMITS.max_commands_per_session
    MAX_ENV_VAR_DISPLAY_LENGTH: Final[int] = LIMITS.max_env_var_display_length
    MAX_TIMEOUT_SECONDS: Final[int] = LIMITS.max_timeout_seconds

    # More output config
    HIGH_PRIORITY_VALUE: Final[int] = OUTPUT.high_priority_value
    DEFAULT_RETRIES: Final[int] = OUTPUT.default_retries
    MIN_LENGTH: Final[int] = OUTPUT.min_length
    DEFAULT_TOKEN_MIN_LENGTH: Final[int] = OUTPUT.default_token_min_length
    DEFAULT_PROGRESS_BAR_WIDTH: Final[int] = OUTPUT.default_progress_bar_width
    DEFAULT_TABLE_PADDING: Final[int] = OUTPUT.default_table_padding

    # Status constants (DEPRECATED: Use StrEnum classes instead)
    STATUS_PENDING: Final[str] = CommandStatus.PENDING
    STATUS_RUNNING: Final[str] = CommandStatus.RUNNING
    STATUS_COMPLETED: Final[str] = CommandStatus.COMPLETED
    STATUS_FAILED: Final[str] = CommandStatus.FAILED
    STATUS_CANCELLED: Final[str] = CommandStatus.CANCELLED

    # Log level constants (DEPRECATED: Use LogLevel enum instead)
    LOG_LEVEL_DEBUG: Final[str] = LogLevel.DEBUG
    LOG_LEVEL_INFO: Final[str] = LogLevel.INFO
    LOG_LEVEL_WARNING: Final[str] = LogLevel.WARNING
    LOG_LEVEL_ERROR: Final[str] = LogLevel.ERROR
    LOG_LEVEL_CRITICAL: Final[str] = LogLevel.CRITICAL

    # Profile constants (DEPRECATED: Use ProfileName enum instead)
    DEFAULT_PROFILE: Final[str] = ProfileName.DEFAULT
    DEVELOPMENT_PROFILE: Final[str] = ProfileName.DEVELOPMENT
    PRODUCTION_PROFILE: Final[str] = ProfileName.PRODUCTION

    # HTTP method constants (DEPRECATED: Use HttpMethod enum instead)
    HTTP_GET: Final[str] = HttpMethod.GET
    HTTP_POST: Final[str] = HttpMethod.POST
    HTTP_PUT: Final[str] = HttpMethod.PUT
    HTTP_DELETE: Final[str] = HttpMethod.DELETE
    HTTP_PATCH: Final[str] = HttpMethod.PATCH

    # Enums (DEPRECATED: Use StrEnum classes instead)
    VALID_OUTPUT_FORMATS: Final[tuple[str, ...]] = tuple(f.value for f in OutputFormat)
    VALID_LOG_LEVELS: Final[tuple[str, ...]] = tuple(f.value for f in LogLevel)
    VALID_COMMAND_STATUSES: Final[tuple[str, ...]] = tuple(
        f.value for f in CommandStatus
    )
    VALID_PIPELINE_STATUSES: Final[tuple[str, ...]] = tuple(
        f.value for f in PipelineStatus
    )


__all__ = ["FlextCliConstants"]
