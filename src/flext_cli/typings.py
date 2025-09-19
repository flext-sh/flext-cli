"""FLEXT CLI Types - Centralized typings following flext-core patterns.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Literal, Protocol, TypedDict
from uuid import UUID

from pydantic import BaseModel, Field

from flext_cli.constants import FlextCliConstants
from flext_core import E, F, FlextResult, FlextTypes, P, R, T, U, V


class FlextCliTypes:
    """Direct CLI type system using FlextTypes as foundation.

    Uses FlextTypes directly without aliases, prioritizing local library types.
    Unified class containing ALL CLI types including output formats.
    """

    class Commands:
        """CLI command types using FlextTypes.Commands directly."""

        # Also keep the Literal type for type annotations
        CliCommandStatus = Literal[
            "PENDING",
            "RUNNING",
            "COMPLETED",
            "FAILED",
            "CANCELLED",
        ]

        # Command state classes
        class PendingState:
            """Pending command state."""

            status: str = "PENDING"
            message: str = "Command is pending execution"

        class RunningState:
            """Running command state."""

            status: str = "RUNNING"
            message: str = "Command is currently running"

        class CompletedState:
            """Completed command state."""

            status: str = "COMPLETED"
            message: str = "Command completed successfully"

        class FailedState:
            """Failed command state."""

            status: str = "FAILED"
            message: str = "Command execution failed"

        # CLI command execution context
        class CliCommandContext(TypedDict):
            """CLI command execution context."""

            command_id: UUID
            command_line: str
            execution_time: datetime
            timeout_seconds: int
            retry_count: int
            correlation_id: str

    # =============================================================================
    # CLI CONFIGURATION TYPES - Using FlextTypes.Config as foundation
    # =============================================================================

    class Config:
        """CLI configuration types leveraging FlextTypes.Config (reduced bloat)."""

        # Use flext-core types where possible
        CliLogLevel = FlextTypes.Config.LogLevel
        CliConfigDict = FlextTypes.Config.ConfigDict

        # CLI-specific extensions only
        CliProfile = str
        CliOutputFormat = Literal["table", "json", "yaml", "csv"]
        CliTimeout = int
        CliConfigPath = Path

        # Profile classes for different environments
        class DevelopmentProfile:
            """Development profile configuration."""

            name: str = "development"
            debug_mode: bool = True
            log_level: str = "DEBUG"

        class ProductionProfile:
            """Production profile configuration."""

            name: str = "production"
            debug_mode: bool = False
            log_level: str = "INFO"

        class TestingProfile:
            """Testing profile configuration."""

            name: str = "testing"
            debug_mode: bool = True
            log_level: str = "DEBUG"

        # CLI configuration context
        class CliConfigContext(TypedDict):
            """CLI configuration context."""

            profile: str
            output_format: str
            debug_mode: bool
            config_path: Path
            environment: str
            updated_at: datetime

    # =============================================================================
    # CLI OUTPUT FORMAT TYPES - For tests compatibility
    # =============================================================================

    class OutputFormat:
        """CLI output format enumeration for test compatibility."""

        JSON = "json"
        YAML = "yaml"
        CSV = "csv"
        TABLE = "table"
        PLAIN = "plain"

    # =============================================================================
    # CLI AUTHENTICATION TYPES - Using FlextTypes.Auth as foundation
    # =============================================================================

    class Auth:
        """CLI authentication types extending FlextTypes.Auth."""

        # CLI-specific auth types - direct definitions
        CliUsername = str
        CliPassword = str
        CliAuthUrl = str
        CliTokenPath = Path
        CliAuthStatus = Literal[
            "authenticated",
            "unauthenticated",
            "expired",
            "invalid",
        ]

        # CLI authentication context
        class CliAuthContext(TypedDict):
            """CLI authentication context."""

            username: str | None
            auth_url: str
            token_path: Path
            refresh_path: Path
            auth_status: str
            expires_at: datetime | None

    # =============================================================================
    # CLI SESSION TYPES - Using FlextTypes.Core as foundation
    # =============================================================================

    class Session:
        """CLI session types using standard Python types."""

        # CLI-specific session types - direct definitions
        CliSessionId = UUID
        CliUserId = str | None
        CliSessionDuration = float | None
        CliCommandsCount = int
        CliSessionStatus = Literal["active", "ended", "timeout", "error"]

        # CLI session context
        class CliSessionContext(TypedDict):
            """CLI session context."""

            session_id: UUID
            user_id: str | None
            start_time: datetime
            end_time: datetime | None
            duration_seconds: float | None
            commands_count: int
            status: str

    # =============================================================================
    # CLI SERVICE TYPES - Using FlextTypes.Container as foundation
    # =============================================================================

    class Services:
        """CLI service types extending FlextTypes.Container."""

        # CLI-specific service types - direct definitions
        CliServiceName = str
        CliProcessorTimeout = int
        CliServiceMetrics = dict[str, int | float | str | bool]
        CliCorrelationId = str

        # CLI service context
        class CliServiceContext(TypedDict):
            """CLI service context."""

            service_name: str
            correlation_id: str
            started_at: datetime
            timeout_seconds: int
            retry_count: int
            metrics: dict[str, int | float | str | bool]

    # =============================================================================
    # CLI RESULT TYPES - Using FlextResult patterns
    # =============================================================================

    class Results:
        """CLI result types using FlextResult patterns."""

        # CLI-specific result types using FlextResult - direct definitions
        CliCommandResult = "FlextResult[FlextCliTypes.Commands.CliCommandContext]"
        CliConfigResult = "FlextResult[FlextCliTypes.Config.CliConfigContext]"
        CliAuthResult = "FlextResult[FlextCliTypes.Auth.CliAuthContext]"
        CliSessionResult = "FlextResult[FlextCliTypes.Session.CliSessionContext]"
        CliServiceResult = "FlextResult[FlextCliTypes.Services.CliServiceContext]"

        # Batch result types - direct definitions
        CliBatchResult = FlextResult[list[dict[str, int | float | str | bool]]]

        # Validation result types - direct definitions
        CliValidationResult = FlextResult[None]

    # =============================================================================
    # PLUGIN STATUS TYPES - Nested for unified class pattern
    # =============================================================================

    # =============================================================================
    # CLI PROTOCOLS - Type protocols for CLI interfaces
    # =============================================================================

    class Protocols:
        """CLI protocol types for interface definitions."""

        class CliProcessor(Protocol):
            """Protocol for CLI data processors."""

            def process(self, data: object) -> object:
                """Process CLI data."""
                ...

        class CliValidator(Protocol):
            """Protocol for CLI validators."""

            def validate(self, data: object) -> bool:
                """Validate CLI data."""
                ...

        class CliFormatter(Protocol):
            """Protocol for CLI formatters."""

            def format(self, data: object) -> str:
                """Format CLI data."""
                ...

        class CliAuthenticator(Protocol):
            """Protocol for CLI authenticators."""

            def authenticate(self, credentials: dict[str, str]) -> bool:
                """Authenticate CLI user."""
                ...

    # =============================================================================
    # CLI MAIN TYPES - Moved from cli.py for centralization
    # =============================================================================

    class CliOptions(TypedDict):
        """CLI options structure from SOURCE OF TRUTH."""

        profile: str
        output_format: str
        debug: bool
        quiet: bool
        log_level: str | None

    class VersionInfo(TypedDict):
        """Version information structure."""

        cli_version: str
        core_version: str | None
        python_version: str
        platform: str

    class CliContext(TypedDict):
        """CLI execution context structure."""

        config: object  # FlextCliConfig but avoid circular import
        debug_mode: bool
        quiet_mode: bool
        profile: str
        output_format: str

    # =============================================================================
    # AUTH TYPES - Moved from auth.py
    # =============================================================================

    class UserData(TypedDict):
        """User data structure."""

        username: str
        email: str | None
        id: str | None

    class AuthStatus(TypedDict):
        """Authentication status structure."""

        authenticated: bool
        username: str | None
        expires_at: str | None
        token_file: str
        token_exists: bool
        refresh_token_file: str
        refresh_token_exists: bool
        auto_refresh: bool

    class LoginCredentials(TypedDict):
        """Login credentials structure."""

        username: str
        password: str

    class TokenPaths(TypedDict):
        """Token file paths structure."""

        token_path: Path
        refresh_token_path: Path

    class TokenData(TypedDict):
        """Token data structure."""

        access_token: str
        refresh_token: str | None
        expires_at: str | None

    # =============================================================================
    # DEBUG TYPES - Moved from debug.py
    # =============================================================================

    class SystemMetrics(TypedDict):
        """System metrics structure."""

        cpu_usage: str | float
        memory_usage: str | float
        disk_usage: str | float
        response_time: str | float

    class PathInfo(TypedDict):
        """Path information structure."""

        label: str
        path: Path
        exists: bool

    class EnvironmentInfo(TypedDict):
        """Environment variable information structure."""

        variables: dict[str, str]
        masked_count: int
        total_count: int


# URL types for test compatibility
URL = str
URLType = str


# No aliases - use direct imports


# ARCHITECTURAL COMPLIANCE: All aliases removed - use full qualified names


# Minimal exports - only actually used types
__all__ = [
    "URL",
    "UUID",
    "BaseModel",
    "E",
    "F",
    "Field",
    "FlextCliConstants",
    "FlextCliTypes",
    "FlextTypes",
    "P",
    "Path",
    "R",
    "T",
    "TypedDict",
    "U",
    "URLType",
    "V",
    "datetime",
]
