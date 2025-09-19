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

    class Http(BaseModel):
        """HTTP client configuration - only used fields (no redundant Config suffix)."""

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

    class Files(BaseModel):
        """File and directory configuration - only used fields (no redundant Config suffix)."""

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

    class System(BaseModel):
        """System and environment configuration - only used fields (no redundant Config suffix)."""

        env_prefix: str = Field(default="FLEXT_CLI_", frozen=True)
        default_editor: str = Field(default="nano", min_length=1)
        project_version: str = Field(default="0.9.0", pattern=r"^\d+\.\d+\.\d+")

        @computed_field
        def editor_command(self) -> str:
            """Get editor command from environment or default."""
            return os.environ.get("EDITOR", self.default_editor)

    class Timeouts(BaseModel):
        """Timeout configuration - only used fields (no redundant Config suffix)."""

        default_command_timeout: int = Field(default=30, ge=1, le=3600)
        default_api_timeout: int = Field(default=60, ge=1, le=3600)
        default_dev_timeout: int = Field(default=120, ge=1, le=7200)

    class Limits(BaseModel):
        """Limits configuration - only used fields (no redundant Config suffix)."""

        max_commands_per_session: int = Field(default=10_000, ge=1, le=100_000)
        max_timeout_seconds: int = Field(default=3600, ge=1, le=86_400)
        max_error_rate_percent: float = Field(default=50.0, ge=0.0, le=100.0)

    class Security(BaseModel):
        """Security configuration - only used fields (no redundant Config suffix)."""

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

    class Output(StrEnum):
        """Output formats - used by tests and CLI (no redundant Format suffix)."""

        TABLE = "table"
        JSON = "json"
        YAML = "yaml"
        CSV = "csv"
        PLAIN = "plain"

    class Plugin(StrEnum):
        """Plugin status enumeration (no redundant Status suffix)."""

        ACTIVE = "active"
        INACTIVE = "inactive"
        ERROR = "error"
        LOADING = "loading"

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

    # Log level constants for backward compatibility
    LOG_LEVEL_DEBUG = LogLevel.DEBUG
    LOG_LEVEL_INFO = LogLevel.INFO
    LOG_LEVEL_WARNING = LogLevel.WARNING
    LOG_LEVEL_ERROR = LogLevel.ERROR
    LOG_LEVEL_CRITICAL = LogLevel.CRITICAL

    class ErrorCode(StrEnum):
        """Error code enumeration for CLI exception categorization."""

        # General errors
        CLI_ERROR = "CLI_ERROR"

        # Input/validation errors
        VALIDATION_ERROR = "CLI_VALIDATION_ERROR"
        ARGUMENT_ERROR = "CLI_ARGUMENT_ERROR"

        # Configuration errors
        CONFIGURATION_ERROR = "CLI_CONFIGURATION_ERROR"
        CONTEXT_ERROR = "CLI_CONTEXT_ERROR"

        # Network/connectivity errors
        CONNECTION_ERROR = "CLI_CONNECTION_ERROR"
        AUTHENTICATION_ERROR = "CLI_AUTHENTICATION_ERROR"
        TIMEOUT_ERROR = "CLI_TIMEOUT_ERROR"

        # Processing errors
        PROCESSING_ERROR = "CLI_PROCESSING_ERROR"
        COMMAND_ERROR = "CLI_COMMAND_ERROR"

        # File/storage errors
        FILE_ERROR = "CLI_FILE_ERROR"
        PERMISSION_ERROR = "CLI_PERMISSION_ERROR"

        # Format errors
        FORMAT_ERROR = "CLI_FORMAT_ERROR"
        OUTPUT_ERROR = "CLI_OUTPUT_ERROR"

        # Service/dependency errors
        SERVICE_ERROR = "CLI_SERVICE_ERROR"
        DEPENDENCY_ERROR = "CLI_DEPENDENCY_ERROR"

    # =============================================================================
    # DEFAULT INSTANCES - Ready-to-use configurations (SINGLE SOURCE OF TRUTH)
    # =============================================================================

    # Pre-configured instances for immediate use
    HTTP: ClassVar[Http] = Http()
    FILES: ClassVar[Files] = Files()
    SYSTEM: ClassVar[System] = System()
    TIMEOUTS: ClassVar[Timeouts] = Timeouts()
    LIMITS: ClassVar[Limits] = Limits()
    SECURITY: ClassVar[Security] = Security()

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
    VALID_OUTPUT_FORMATS: ClassVar[list[str]] = [fmt.value for fmt in Output]

    # Timeout constants
    MAX_COMMAND_TIMEOUT: ClassVar[int] = LIMITS.max_timeout_seconds

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
    # Command status constants
    STATUS_PENDING: ClassVar[str] = CommandStatus.PENDING.value
    STATUS_RUNNING: ClassVar[str] = CommandStatus.RUNNING.value
    STATUS_COMPLETED: ClassVar[str] = CommandStatus.COMPLETED.value
    STATUS_FAILED: ClassVar[str] = CommandStatus.FAILED.value
    STATUS_CANCELLED: ClassVar[str] = CommandStatus.CANCELLED.value

    # Test compatibility aliases
    OutputFormat: ClassVar[type[Output]] = Output
    TimeoutConfig: ClassVar[type[Timeouts]] = Timeouts
    LimitsConfig: ClassVar[type[Limits]] = Limits
    OutputConfig: ClassVar[type[Output]] = Output


__all__ = ["FlextCliConstants"]
