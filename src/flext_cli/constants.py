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

from flext_core import FlextConstants


class FlextCliConstants:
    """CLI domain-specific constants only - universal constants imported from flext-core."""

    # Use universal constants instead of duplicating
    DEFAULT_TIMEOUT = FlextConstants.Network.DEFAULT_TIMEOUT
    DEFAULT_API_PORT = FlextConstants.Platform.FLEXT_API_PORT

    # =========================================================================
    # CLI-SPECIFIC CONSTANTS ONLY - No universal duplications
    # =========================================================================

    class Http(BaseModel):
        """HTTP client configuration - CLI-specific settings."""

        http_scheme: str = Field(default="http", frozen=True)
        default_host: str = Field(default="localhost", min_length=1)
        default_api_port: int = Field(
            default=FlextConstants.Platform.FLEXT_API_PORT, ge=1, le=65535
        )
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
        """File and directory configuration - CLI-specific settings."""

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
                "FLEXT_CLI_REFRESH_TOKEN_FILE_NAME", "refresh_token.json"
            )

    class System(BaseModel):
        """System and environment configuration - CLI-specific settings."""

        env_prefix: str = Field(default="FLEXT_CLI_", frozen=True)
        default_editor: str = Field(default="nano", min_length=1)
        project_version: str = Field(default="0.9.0", pattern=r"^\d+\.\d+\.\d+")

        @computed_field
        def editor_command(self) -> str:
            """Get editor command from environment or default."""
            return os.environ.get("EDITOR", self.default_editor)

    class Timeouts:
        """Timeout configuration - CLI-specific extensions of universal timeouts."""

        # Use universal timeout as base
        default_command_timeout: int = 60  # FlextConstants.Network.DEFAULT_TIMEOUT
        default_api_timeout: int = 60
        default_dev_timeout: int = 120

    class Limits:
        """Limits configuration - CLI-specific limits."""

        max_commands_per_session: int = 10_000
        max_timeout_seconds: int = 3600
        max_error_rate_percent: float = 50.0
        dataset_tuple_length: int = 2

    class Security(BaseModel):
        """Security configuration - CLI-specific security settings."""

        sensitive_value_preview_length: int = Field(default=4, ge=1, le=10)
        max_filename_length: int = Field(default=255, ge=1, le=1000)

    class Errors:
        """CLI-specific error codes - extend universal error codes."""

        # Base universal error from flext-core, prefixed for CLI domain
        CLI_ERROR: Final[str] = "CLI_ERROR"
        VALIDATION_ERROR: Final[str] = f"CLI_{FlextConstants.Errors.VALIDATION_ERROR}"
        CONFIGURATION_ERROR: Final[str] = f"CLI_{FlextConstants.Errors.CONFIG_ERROR}"
        CONNECTION_ERROR: Final[str] = f"CLI_{FlextConstants.Errors.CONNECTION_ERROR}"
        TIMEOUT_ERROR: Final[str] = f"CLI_{FlextConstants.Errors.TIMEOUT_ERROR}"

        # CLI-specific errors
        ARGUMENT_ERROR: Final[str] = "CLI_ARGUMENT_ERROR"
        CONTEXT_ERROR: Final[str] = "CLI_CONTEXT_ERROR"
        AUTHENTICATION_ERROR: Final[str] = "CLI_AUTHENTICATION_ERROR"
        PROCESSING_ERROR: Final[str] = "CLI_PROCESSING_ERROR"
        COMMAND_ERROR: Final[str] = "CLI_COMMAND_ERROR"
        FILE_ERROR: Final[str] = "CLI_FILE_ERROR"
        PERMISSION_ERROR: Final[str] = "CLI_PERMISSION_ERROR"
        FORMAT_ERROR: Final[str] = "CLI_FORMAT_ERROR"
        OUTPUT_ERROR: Final[str] = "CLI_OUTPUT_ERROR"
        SERVICE_ERROR: Final[str] = "CLI_SERVICE_ERROR"
        DEPENDENCY_ERROR: Final[str] = "CLI_DEPENDENCY_ERROR"

    class Enums:
        """CLI-specific enumerations."""

        class HttpMethod(StrEnum):
            """HTTP methods - CLI-specific usage."""

            GET = "GET"
            POST = "POST"
            PUT = "PUT"
            DELETE = "DELETE"

        class ProfileName(StrEnum):
            """Profile names - CLI-specific."""

            DEFAULT = "default"

        class CommandStatus(StrEnum):
            """Command statuses - CLI-specific."""

            PENDING = "PENDING"
            RUNNING = "RUNNING"
            COMPLETED = "COMPLETED"
            FAILED = "FAILED"
            CANCELLED = "CANCELLED"

        class Output(StrEnum):
            """Output formats - CLI-specific."""

            TABLE = "table"
            JSON = "json"
            YAML = "yaml"
            CSV = "csv"
            PLAIN = "plain"

        class Plugin(StrEnum):
            """Plugin status enumeration - CLI-specific."""

            ACTIVE = "active"
            INACTIVE = "inactive"
            ERROR = "error"
            LOADING = "loading"

        class ErrorCode(StrEnum):
            """Error codes enumeration - CLI-specific."""

            CLI_ERROR = "CLI_ERROR"
            VALIDATION_ERROR = "CLI_VALIDATION_ERROR"
            CONFIGURATION_ERROR = "CLI_CONFIGURATION_ERROR"
            CONNECTION_ERROR = "CLI_CONNECTION_ERROR"
            TIMEOUT_ERROR = "CLI_TIMEOUT_ERROR"
            ARGUMENT_ERROR = "CLI_ARGUMENT_ERROR"
            CONTEXT_ERROR = "CLI_CONTEXT_ERROR"
            AUTHENTICATION_ERROR = "CLI_AUTHENTICATION_ERROR"
            PROCESSING_ERROR = "CLI_PROCESSING_ERROR"
            COMMAND_ERROR = "CLI_COMMAND_ERROR"
            FORMAT_ERROR = "CLI_FORMAT_ERROR"

    class TimeoutConfig(BaseModel):
        """Timeout configuration for CLI operations."""

        default_api_timeout: int = Field(default=30, ge=1, le=300, description="API request timeout in seconds")
        default_command_timeout: int = Field(default=60, ge=1, le=3600, description="Command execution timeout in seconds")
        default_connection_timeout: int = Field(default=10, ge=1, le=60, description="Connection timeout in seconds")
        default_dev_timeout: int = Field(default=120, ge=1, le=600, description="Development timeout in seconds")

    class LimitsConfig(BaseModel):
        """Limits configuration for CLI operations."""

        max_file_size: int = Field(default=100*1024*1024, ge=1, description="Maximum file size in bytes")
        max_records: int = Field(default=10000, ge=1, description="Maximum number of records to process")
        max_concurrent: int = Field(default=10, ge=1, le=100, description="Maximum concurrent operations")

    class OutputConfig(BaseModel):
        """Output configuration for CLI operations."""

        default_format: str = Field(default="table", description="Default output format")
        max_width: int = Field(default=120, ge=40, le=200, description="Maximum output width")
        show_progress: bool = Field(default=True, description="Show progress indicators")

    class FeatureFlags:
        """CLI-specific feature toggles."""

        @staticmethod
        def _env_enabled(flag_name: str, default: str = "1") -> bool:
            value = os.environ.get(flag_name, default)
            return value.lower() not in {"0", "false", "no"}

        ENABLE_DISPATCHER: ClassVar[bool] = _env_enabled("FLEXT_CLI_ENABLE_DISPATCHER")

    # =============================================================================
    # DEFAULT INSTANCES - Ready-to-use configurations
    # =============================================================================

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
    TOKEN_FILE_NAME: ClassVar[str] = "token.json"
    REFRESH_TOKEN_FILE_NAME: ClassVar[str] = "refresh_token.json"

    # API constants
    DEFAULT_API_URL: ClassVar[str] = "http://localhost:8000"
    FALLBACK_API_URL: ClassVar[str] = (
        f"{HTTP.http_scheme}://{HTTP.default_host}:{HTTP.fallback_api_port}"
    )

    # Service constants
    SERVICE_NAME_API: ClassVar[str] = "flext-api"

    # Validation constants
    VALID_PIPELINE_STATUSES: ClassVar[list[str]] = [
        status.value for status in Enums.CommandStatus
    ]
    VALID_OUTPUT_FORMATS: ClassVar[list[str]] = [fmt.value for fmt in Enums.Output]
    VALID_COMMAND_STATUSES: ClassVar[tuple[str, ...]] = tuple(
        status.value for status in Enums.CommandStatus
    )

    # Timeout constants using universal base
    DEFAULT_COMMAND_TIMEOUT: ClassVar[int] = TIMEOUTS.default_command_timeout
    MAX_COMMAND_TIMEOUT: ClassVar[int] = LIMITS.max_timeout_seconds
    MAX_FILENAME_LENGTH: ClassVar[int] = SECURITY.max_filename_length

    # Configuration constants
    DEFAULT_PROFILE: ClassVar[str] = Enums.ProfileName.DEFAULT.value
    CONFIG_FILE_NAME: ClassVar[str] = "config.toml"

    # Command status constants
    STATUS_PENDING: ClassVar[str] = Enums.CommandStatus.PENDING.value
    STATUS_RUNNING: ClassVar[str] = Enums.CommandStatus.RUNNING.value
    STATUS_COMPLETED: ClassVar[str] = Enums.CommandStatus.COMPLETED.value
    STATUS_FAILED: ClassVar[str] = Enums.CommandStatus.FAILED.value
    STATUS_CANCELLED: ClassVar[str] = Enums.CommandStatus.CANCELLED.value


__all__ = ["FlextCliConstants"]
