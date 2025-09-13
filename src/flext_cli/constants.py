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

from pydantic import BaseModel, Field, computed_field

from flext_cli.utils import (
    bounded_str_field,
    frozen_str_field,
    port_field,
    positive_int_field,
    size_field,
    timeout_field,
)


class FlextCliConstants:
    """CLI constants structured as Pydantic models extending flext-core patterns."""

    class TimeoutConfig(BaseModel):
        """Timeout and duration configuration with validation."""

        default_command_timeout: int = timeout_field(30)
        max_command_timeout: int = timeout_field(300)
        min_command_timeout: int = timeout_field(1, max_timeout=60)
        default_api_timeout: int = timeout_field(30, max_timeout=300)
        default_read_timeout: int = timeout_field(60, max_timeout=300)
        default_dev_timeout: int = timeout_field(60, max_timeout=300)
        production_api_timeout: int = timeout_field(
            120, min_timeout=30, max_timeout=600
        )
        session_timeout_minutes: int = positive_int_field(60, max_val=1440)
        token_expiry_hours: int = positive_int_field(24, max_val=168)
        refresh_expiry_days: int = positive_int_field(30, max_val=365)
        milliseconds_per_second: float = Field(default=1000.0, frozen=True)

    class LimitsConfig(BaseModel):
        """Size and validation limits with constraints."""

        max_history_size: int = positive_int_field(1000, max_val=100_000)
        max_output_size: int = size_field(1_048_576)
        max_table_rows: int = positive_int_field(1000, max_val=10_000)
        max_filename_length: int = positive_int_field(255, max_val=255)
        max_profile_name_length: int = positive_int_field(50, max_val=100)
        max_config_key_length: int = positive_int_field(100, max_val=200)
        max_config_value_length: int = positive_int_field(1000, max_val=10_000)
        max_commands_per_session: int = positive_int_field(10_000, max_val=100_000)
        max_env_var_display_length: int = positive_int_field(60, max_val=200)
        max_timeout_seconds: int = timeout_field(3600, max_timeout=86_400)

    class DataStructureConfig(BaseModel):
        """Data structure configuration for tuple processing."""

        tuple_pair_length: int = positive_int_field(2, min_val=2, max_val=10)
        min_service_id_length: int = positive_int_field(10, max_val=50)

    class OutputConfig(BaseModel):
        """Output formatting configuration."""

        default_output_format: str = bounded_str_field(
            "table", pattern=r"^(table|json|yaml|csv)$"
        )
        default_output_width: int = positive_int_field(120, min_val=40, max_val=400)
        default_progress_bar_width: int = positive_int_field(
            40, min_val=10, max_val=100
        )
        default_table_padding: int = positive_int_field(1, min_val=0, max_val=10)
        high_priority_value: int = positive_int_field(1000, max_val=10_000)
        default_retries: int = positive_int_field(3, min_val=0, max_val=10)
        min_length: int = positive_int_field(1, max_val=10)
        default_token_min_length: int = positive_int_field(10, max_val=100)

    class SecurityConfig(BaseModel):
        """Security and privacy configuration."""

        sensitive_value_preview_length: int = positive_int_field(4, max_val=10)
        min_path_length_for_masking: int = positive_int_field(4, max_val=20)
        max_config_key_length: int = positive_int_field(100, min_val=10, max_val=1000)
        max_output_size: int = size_field(1_048_576)  # 1MB

    class HttpConfig(BaseModel):
        """HTTP client configuration with security defaults."""

        http_scheme: str = frozen_str_field("http")
        https_scheme: str = frozen_str_field("https")
        default_host: str = bounded_str_field("localhost", min_len=1)
        default_port: int = port_field(8081)
        default_api_port: int = port_field(8080)
        fallback_api_port: int = port_field(8000)
        content_type_json: str = frozen_str_field("application/json")
        header_content_type: str = frozen_str_field("Content-Type")
        header_accept: str = frozen_str_field("Accept")
        header_authorization: str = frozen_str_field("Authorization")
        auth_bearer_prefix: str = frozen_str_field("Bearer")

        @computed_field
        @property
        def default_api_url(self) -> str:
            """Generate default API URL from configuration."""
            return f"{self.http_scheme}://{self.default_host}:{self.default_api_port}"

        @computed_field
        @property
        def fallback_api_url(self) -> str:
            """Generate fallback API URL from configuration."""
            return f"{self.http_scheme}://{self.default_host}:{self.fallback_api_port}"

    class FileConfig(BaseModel):
        """File and directory configuration with security."""

        flext_dir_name: str = bounded_str_field(".flext", min_len=1)
        config_file_name: str = bounded_str_field("config.yaml", min_len=1)
        default_encoding: str = frozen_str_field("utf-8")
        test_write_file_name: str = bounded_str_field(".flext_test_write", min_len=1)
        cache_dir_name: str = bounded_str_field("cache", min_len=1)
        logs_dir_name: str = bounded_str_field("logs", min_len=1)
        data_dir_name: str = bounded_str_field("data", min_len=1)
        auth_dir_name: str = bounded_str_field("auth", min_len=1)

        @computed_field
        @property
        def token_file_name(self) -> str:
            """Get token file name from environment or default."""
            return os.environ.get("FLEXT_CLI_TOKEN_FILE_NAME", "token.json")

        @computed_field
        @property
        def refresh_token_file_name(self) -> str:
            """Get refresh token file name from environment or default."""
            return os.environ.get(
                "FLEXT_CLI_REFRESH_TOKEN_FILE_NAME",
                "refresh_token.json",
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

        interactive_feature_help: str = bounded_str_field(
            "Interactive commands: REPL, completion, history", min_len=1
        )
        info_use_help: str = bounded_str_field(
            "Use --help for more information", min_len=1
        )
        version_cli: str = bounded_str_field("FLEXT CLI", min_len=1)
        version_python: str = bounded_str_field("Python", min_len=1)
        version_flext_core: str = bounded_str_field("FLEXT Core", min_len=1)
        service_name_api: str = bounded_str_field("FLEXT CLI API", min_len=1)
        table_title_config: str = bounded_str_field(
            "FLEXT Configuration v0.7.0", min_len=1
        )
        table_title_paths: str = bounded_str_field(
            "FLEXT Configuration Paths", min_len=1
        )
        table_title_metrics: str = bounded_str_field(
            "System Performance Metrics", min_len=1
        )
        table_title_env_vars: str = bounded_str_field(
            "FLEXT Environment Variables", min_len=1
        )
        table_title_cli_paths: str = bounded_str_field("FLEXT CLI Paths", min_len=1)
        debug_flext_core_not_detected: str = bounded_str_field(
            "FLEXT Core version not detected", min_len=1
        )
        debug_information: str = bounded_str_field("Debug Information", min_len=1)
        debug_configuration: str = bounded_str_field("Configuration", min_len=1)
        debug_python_executable: str = bounded_str_field("Python Executable", min_len=1)
        debug_platform: str = bounded_str_field("Platform", min_len=1)
        debug_service_connectivity: str = bounded_str_field(
            "Service connectivity check", min_len=1
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
