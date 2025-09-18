"""FLEXT CLI Types - Centralized typings following flext-core patterns.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from pathlib import Path
from typing import Literal, TypedDict
from uuid import UUID

from pydantic import BaseModel, Field

from flext_cli.constants import FlextCliConstants
from flext_core import E, F, FlextResult, FlextTypes, P, R, T, U, V


class FlextCliTypes:
    """Direct CLI type system using FlextTypes as foundation.

    Uses FlextTypes directly without aliases, prioritizing local library types.
    Unified class containing ALL CLI types including output formats.
    """

    # =============================================================================
    # CLI OUTPUT FORMATS - String enum for type safety
    # =============================================================================

    class OutputFormat(StrEnum):
        """Supported CLI output formats (string enum for type safety in tests)."""

        JSON = "json"
        YAML = "yaml"
        CSV = "csv"
        TABLE = "table"
        PLAIN = "plain"

    # =============================================================================
    # CLI COMMAND TYPES - Direct usage of FlextTypes.Commands
    # =============================================================================

    class Commands:
        """CLI command types using FlextTypes.Commands directly."""

        # CLI-specific command types - proper enum for test compatibility
        class CommandStatusEnum(StrEnum):
            """Command status enumeration."""

            PENDING = "PENDING"
            RUNNING = "RUNNING"
            COMPLETED = "COMPLETED"
            FAILED = "FAILED"
            CANCELLED = "CANCELLED"

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

    class PluginStatusEnum(StrEnum):
        """Plugin status enumeration."""

        ACTIVE = "active"
        INACTIVE = "inactive"
        ERROR = "error"
        LOADING = "loading"

    # =============================================================================
    # CLI PROTOCOLS - Type protocols for CLI interfaces
    # =============================================================================

    class Protocols:
        """CLI protocol types for interface definitions."""

        class CliProcessor:
            """Protocol for CLI data processors."""

            def process(self, data: object) -> object:
                """Process CLI data."""
                raise NotImplementedError

        class CliValidator:
            """Protocol for CLI validators."""

            def validate(self, data: object) -> bool:
                """Validate CLI data."""
                raise NotImplementedError

        class CliFormatter:
            """Protocol for CLI formatters."""

            def format(self, data: object) -> str:
                """Format CLI data."""
                raise NotImplementedError

        class CliAuthenticator:
            """Protocol for CLI authenticators."""

            def authenticate(self, credentials: dict[str, str]) -> bool:
                """Authenticate CLI user."""
                raise NotImplementedError


# Top-level aliases for test compatibility
PluginStatus = FlextCliTypes.PluginStatusEnum
CommandStatus = FlextCliTypes.Commands.CommandStatusEnum

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
    "CommandStatus",
    "E",
    "F",
    "Field",
    "FlextCliConstants",
    "FlextCliTypes",
    "FlextTypes",
    "P",
    "Path",
    "PluginStatus",
    "R",
    "T",
    "TypedDict",
    "U",
    "URLType",
    "V",
    "datetime",
]
