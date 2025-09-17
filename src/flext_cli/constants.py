"""FLEXT CLI Constants - Cleaned up to include only used constants.

Single source of truth for configuration with only actively used constants.
Eliminates unused constants to maintain clean, focused codebase.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import os
from enum import StrEnum
from typing import ClassVar

from pydantic import BaseModel, Field, computed_field


class FlextCliConstants:
    """CLI constants with only actively used constants in the codebase."""

    class HttpConfig(BaseModel):
        """HTTP client configuration - only used fields."""

        http_scheme: str = Field(default="http", frozen=True)
        default_host: str = Field(default="localhost", min_length=1)
        default_api_port: int = Field(default=8080, ge=1, le=65535)
        fallback_api_port: int = Field(default=8000, ge=1, le=65535)
        content_type_json: str = Field(default="application/json", frozen=True)
        header_content_type: str = Field(default="Content-Type", frozen=True)
        header_accept: str = Field(default="Accept", frozen=True)
        header_authorization: str = Field(default="Authorization", frozen=True)
        auth_bearer_prefix: str = Field(default="Bearer", frozen=True)

        @computed_field
        def default_api_url(self) -> str:
            """Generate default API URL from configuration."""
            return f"{self.http_scheme}://{self.default_host}:{self.default_api_port}"

        @computed_field
        def fallback_api_url(self) -> str:
            """Generate fallback API URL from configuration."""
            return f"{self.http_scheme}://{self.default_host}:{self.fallback_api_port}"

    class FileConfig(BaseModel):
        """File and directory configuration - only used fields."""

        flext_dir_name: str = Field(default=".flext", min_length=1)
        config_file_name: str = Field(default="config.yaml", min_length=1)
        default_encoding: str = Field(default="utf-8", frozen=True)
        auth_dir_name: str = Field(default="auth", min_length=1)
        cache_dir_name: str = Field(default="cache", min_length=1)
        logs_dir_name: str = Field(default="logs", min_length=1)
        data_dir_name: str = Field(default="data", min_length=1)

        @computed_field
        def token_file_name(self) -> str:
            """Get token file name from environment or default."""
            return os.environ.get("FLEXT_CLI_TOKEN_FILE_NAME", "token.json")

        @computed_field
        def refresh_token_file_name(self) -> str:
            """Get refresh token file name from environment or default."""
            return os.environ.get(
                "FLEXT_CLI_REFRESH_TOKEN_FILE_NAME",
                "refresh_token.json",
            )

    class SystemConfig(BaseModel):
        """System and environment configuration - only used fields."""

        env_prefix: str = Field(default="FLEXT_CLI_", frozen=True)
        default_editor: str = Field(default="nano", min_length=1)
        project_version: str = Field(default="0.9.0", pattern=r"^\d+\.\d+\.\d+")

        @computed_field
        def editor_command(self) -> str:
            """Get editor command from environment or default."""
            return os.environ.get("EDITOR", self.default_editor)

    class TimeoutConfig(BaseModel):
        """Timeout configuration - only used fields."""

        default_command_timeout: int = Field(default=30, ge=1, le=3600)
        default_api_timeout: int = Field(default=60, ge=1, le=3600)
        default_dev_timeout: int = Field(default=120, ge=1, le=7200)

    class LimitsConfig(BaseModel):
        """Limits configuration - only used fields."""

        max_commands_per_session: int = Field(default=10_000, ge=1, le=100_000)
        max_timeout_seconds: int = Field(default=3600, ge=1, le=86_400)
        max_error_rate_percent: float = Field(default=50.0, ge=0.0, le=100.0)

    class OutputConfig(BaseModel):
        """Output configuration - only used fields."""

        default_output_format: str = Field(
            default="table", pattern=r"^(table|json|yaml|csv)$"
        )

    class SecurityConfig(BaseModel):
        """Security configuration - only used fields."""

        sensitive_value_preview_length: int = Field(default=4, ge=1, le=10)
        max_filename_length: int = Field(default=255, ge=1, le=1000)

    class HttpMethod(StrEnum):
        """HTTP methods - only used values."""

        GET = "GET"
        POST = "POST"
        PUT = "PUT"
        DELETE = "DELETE"

    class ProfileName(StrEnum):
        """Profile names - only used values."""

        DEFAULT = "default"

    class CommandStatus(StrEnum):
        """Command statuses - only used values."""

        PENDING = "PENDING"
        RUNNING = "RUNNING"
        COMPLETED = "COMPLETED"
        FAILED = "FAILED"
        CANCELLED = "CANCELLED"

    class OutputFormat(StrEnum):
        """Output formats - used by tests and CLI."""

        TABLE = "table"
        JSON = "json"
        YAML = "yaml"
        CSV = "csv"
        PLAIN = "plain"

    class FeatureFlags:
        """Feature toggles for progressive rollouts."""

        @staticmethod
        def _env_enabled(flag_name: str, default: str = "1") -> bool:
            value = os.environ.get(flag_name, default)
            return value.lower() not in {"0", "false", "no"}

        ENABLE_DISPATCHER: ClassVar[bool] = _env_enabled(
            "FLEXT_CLI_ENABLE_DISPATCHER",
        )

    class LogLevel(StrEnum):
        """Log levels - used by tests."""

        DEBUG = "DEBUG"
        INFO = "INFO"
        WARNING = "WARNING"
        ERROR = "ERROR"
        CRITICAL = "CRITICAL"

    # =============================================================================
    # DEFAULT INSTANCES - Ready-to-use configurations (SINGLE SOURCE OF TRUTH)
    # =============================================================================

    # Pre-configured instances for immediate use
    HTTP: ClassVar[HttpConfig] = HttpConfig()
    FILES: ClassVar[FileConfig] = FileConfig()
    SYSTEM: ClassVar[SystemConfig] = SystemConfig()
    TIMEOUTS: ClassVar[TimeoutConfig] = TimeoutConfig()
    LIMITS: ClassVar[LimitsConfig] = LimitsConfig()
    OUTPUT: ClassVar[OutputConfig] = OutputConfig()
    SECURITY: ClassVar[SecurityConfig] = SecurityConfig()

    # =============================================================================
    # COMPATIBILITY ALIASES - Direct access to nested properties
    # =============================================================================

    # File system constants
    FLEXT_DIR_NAME: ClassVar[str] = FILES.flext_dir_name
    AUTH_DIR_NAME: ClassVar[str] = FILES.auth_dir_name
    TOKEN_FILE_NAME: ClassVar[str] = (
        "token.json"  # Direct value instead of computed field
    )
    REFRESH_TOKEN_FILE_NAME: ClassVar[str] = (
        "refresh_token.json"  # Direct value instead of computed field
    )

    # API constants
    FALLBACK_API_URL: ClassVar[str] = (
        f"{HTTP.http_scheme}://{HTTP.default_host}:{HTTP.fallback_api_port}"  # Direct construction
    )

    # Service constants
    SERVICE_NAME_API: ClassVar[str] = "flext-api"

    # Validation constants
    VALID_PIPELINE_STATUSES: ClassVar[list[str]] = [
        status.value for status in CommandStatus
    ]
    VALID_OUTPUT_FORMATS: ClassVar[list[str]] = [fmt.value for fmt in OutputFormat]

    # Timeout constants
    MAX_COMMAND_TIMEOUT: ClassVar[int] = LIMITS.max_timeout_seconds
    # Command status aliases (for backward compatibility with tests)
    STATUS_PENDING: ClassVar[str] = CommandStatus.PENDING.value
    STATUS_RUNNING: ClassVar[str] = CommandStatus.RUNNING.value
    STATUS_COMPLETED: ClassVar[str] = CommandStatus.COMPLETED.value
    STATUS_FAILED: ClassVar[str] = CommandStatus.FAILED.value
    STATUS_CANCELLED: ClassVar[str] = CommandStatus.CANCELLED.value

    # Additional missing constants used by tests
    VALID_COMMAND_STATUSES: ClassVar[tuple[str, ...]] = tuple(
        status.value for status in CommandStatus
    )
    DEFAULT_COMMAND_TIMEOUT: ClassVar[int] = TIMEOUTS.default_command_timeout
    MAX_FILENAME_LENGTH: ClassVar[int] = SECURITY.max_filename_length

    # Missing API and configuration constants
    DEFAULT_API_URL: ClassVar[str] = "http://localhost:8000"
    DEFAULT_PROFILE: ClassVar[str] = ProfileName.DEFAULT.value
    CONFIG_FILE_NAME: ClassVar[str] = "config.toml"

    # Log level aliases (for backward compatibility with tests)
    LOG_LEVEL_DEBUG: ClassVar[str] = LogLevel.DEBUG.value
    LOG_LEVEL_INFO: ClassVar[str] = LogLevel.INFO.value
    LOG_LEVEL_WARNING: ClassVar[str] = LogLevel.WARNING.value
    LOG_LEVEL_ERROR: ClassVar[str] = LogLevel.ERROR.value
    LOG_LEVEL_CRITICAL: ClassVar[str] = LogLevel.CRITICAL.value


__all__ = ["FlextCliConstants"]
