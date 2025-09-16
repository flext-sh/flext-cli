"""FLEXT CLI Constants - Cleaned up to include only used constants.

Single source of truth for configuration with only actively used constants.
Eliminates unused constants to maintain clean, focused codebase.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import os
from enum import StrEnum
from typing import ClassVar, Final

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

    class LimitsConfig(BaseModel):
        """Limits configuration - only used fields."""

        max_commands_per_session: int = Field(default=10_000, ge=1, le=100_000)
        max_timeout_seconds: int = Field(default=3600, ge=1, le=86_400)

    class OutputConfig(BaseModel):
        """Output configuration - only used fields."""

        default_output_format: str = Field(
            default="table", pattern=r"^(table|json|yaml|csv)$"
        )

    class SecurityConfig(BaseModel):
        """Security configuration - only used fields."""

        sensitive_value_preview_length: int = Field(default=4, ge=1, le=10)

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
    # BACKWARD COMPATIBILITY - Only for actually used constants
    # =============================================================================

    # HTTP (DEPRECATED: Use HTTP.field_name instead)
    DEFAULT_ENCODING: Final[str] = FILES.default_encoding
    FALLBACK_API_URL: str = str(HTTP.fallback_api_url)
    FLEXT_DIR_NAME: Final[str] = FILES.flext_dir_name
    AUTH_DIR_NAME: Final[str] = FILES.auth_dir_name
    TOKEN_FILE_NAME: str = str(FILES.token_file_name)
    REFRESH_TOKEN_FILE_NAME: str = str(FILES.refresh_token_file_name)

    # System (DEPRECATED: Use SYSTEM.field_name instead)
    SERVICE_NAME_API: Final[str] = "FLEXT CLI API"

    # Status constants (DEPRECATED: Use CommandStatus enum instead)
    STATUS_PENDING: Final[str] = CommandStatus.PENDING
    STATUS_RUNNING: Final[str] = CommandStatus.RUNNING
    STATUS_COMPLETED: Final[str] = CommandStatus.COMPLETED
    STATUS_FAILED: Final[str] = CommandStatus.FAILED

    # Limits (DEPRECATED: Use LIMITS.field_name instead)
    MAX_COMMANDS_PER_SESSION: Final[int] = LIMITS.max_commands_per_session
    MAX_COMMAND_TIMEOUT: Final[int] = 300  # Used in one place

    # Output formats tuple (DEPRECATED: Use OutputFormat enum instead)
    VALID_OUTPUT_FORMATS: Final[tuple[str, ...]] = ("table", "json", "yaml", "csv")

    # Pipeline statuses tuple (DEPRECATED: Use PipelineStatus enum instead)
    VALID_PIPELINE_STATUSES: Final[tuple[str, ...]] = ("active", "inactive", "pending")


__all__ = ["FlextCliConstants"]
