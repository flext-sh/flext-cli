"""FLEXT CLI Types - Centralized typings following flext-core patterns.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from pathlib import Path
from typing import Literal, Protocol, TypedDict, TypeVar
from uuid import UUID

from flext_core import FlextResult, FlextTypes
from pydantic import BaseModel, Field

from flext_cli.constants import FlextCliConstants
from flext_cli.utils import BASE_CONFIG_DICT


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

        # CLI-specific command types - direct definitions
        CliCommandStatus = Literal[
            "PENDING",
            "RUNNING",
            "COMPLETED",
            "FAILED",
            "CANCELLED",
        ]

        # Advanced Pydantic v2 discriminated union for command states
        # Imports moved to top level to fix F821 errors

        class PendingState(BaseModel):
            """Command in pending state."""

            model_config = BASE_CONFIG_DICT

            status: Literal["PENDING"] = "PENDING"
            queued_at: datetime = Field()

        class RunningState(BaseModel):
            """Command in running state."""

            model_config = BASE_CONFIG_DICT

            status: Literal["RUNNING"] = "RUNNING"
            started_at: datetime = Field()
            process_id: int | None = None

        class CompletedState(BaseModel):
            """Command completed successfully."""

            model_config = BASE_CONFIG_DICT

            status: Literal["COMPLETED"] = "COMPLETED"
            completed_at: datetime = Field()
            exit_code: int = 0
            output: str = ""

        class FailedState(BaseModel):
            """Command failed with error."""

            model_config = BASE_CONFIG_DICT

            status: Literal["FAILED"] = "FAILED"
            failed_at: datetime = Field()
            exit_code: int
            error_output: str

        # Discriminated union for type-safe command state management
        CommandState = PendingState | RunningState | CompletedState | FailedState

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

        # Streamlined Pydantic v2 profiles with modern ConfigDict
        class BaseProfile(BaseModel):
            """Base profile with common settings."""

            model_config = BASE_CONFIG_DICT

            profile: str
            debug: bool = False
            log_level: str = "INFO"
            output_format: str = "json"

        class DevelopmentProfile(BaseProfile):
            """Development environment configuration."""

            profile: Literal["development"] = "development"
            debug: bool = True
            log_level: Literal["DEBUG"] = "DEBUG"
            output_format: Literal["table", "json"] = "table"

        class ProductionProfile(BaseProfile):
            """Production environment configuration."""

            profile: Literal["production"] = "production"
            timeout_seconds: int = Field(ge=30, le=300, default=60)

        class TestingProfile(BaseProfile):
            """Testing environment configuration."""

            profile: Literal["testing"] = "testing"
            mock_services: bool = True

        # Discriminated union for type-safe configuration management
        ConfigProfile = DevelopmentProfile | ProductionProfile | TestingProfile

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
    # CLI PROTOCOL DEFINITIONS - Advanced Python 3.13+ patterns
    # =============================================================================

    class Protocols:
        """CLI protocol definitions for type safety."""

        class CliProcessor(Protocol):
            """Protocol for CLI processors."""

            def process(
                self,
                request: str | dict[str, object],
            ) -> FlextResult[object]:
                """Process CLI request."""
                ...

            def build(
                self,
                domain: object,
                *,
                correlation_id: str,
            ) -> str | dict[str, object]:
                """Build CLI response."""
                ...

        class CliValidator(Protocol):
            """Protocol for CLI validators."""

            def validate(
                self,
                data: dict[str, object] | str | float,
            ) -> FlextResult[None]:
                """Validate CLI data."""
                ...

        class CliFormatter(Protocol):
            """Protocol for CLI formatters."""

            def format(
                self,
                data: dict[str, object] | list[object] | str,
                format_type: str,
            ) -> FlextResult[str]:
                """Format CLI data with specified type."""
                ...

        class CliAuthenticator(Protocol):
            """Protocol for CLI authenticators."""

            def authenticate(
                self,
                credentials: dict[str, str],
            ) -> FlextResult[FlextCliTypes.Auth.CliAuthContext]:
                """Authenticate CLI user."""
                ...

            def is_authenticated(self) -> bool:
                """Check authentication status."""
                ...

    # =============================================================================
    # PLUGIN STATUS TYPES - Nested for unified class pattern
    # =============================================================================

    class PluginStatusEnum(StrEnum):
        """Plugin status enumeration."""

        ACTIVE = "active"
        INACTIVE = "inactive"
        ERROR = "error"
        LOADING = "loading"


# No aliases - use direct imports


# Unified command types (reduce duplication)
CommandStatus = FlextCliConstants.CommandStatus
# CommandType removed - redundant with CommandStatus

# Plugin status alias
PluginStatus = FlextCliTypes.PluginStatusEnum

# Essential type aliases only (eliminate dead code)
URL = str  # Consolidated URL type - actually used

# Type variables for generic programming
E = TypeVar("E")
F = TypeVar("F")
P = TypeVar("P")
R = TypeVar("R")
T = TypeVar("T")
U = TypeVar("U")
V = TypeVar("V")


# Minimal exports - only actually used types
__all__ = [
    "URL",
    "UUID",
    "BaseModel",
    "CommandStatus",
    "E",
    "F",
    "FlextCliConstants",
    "FlextCliTypes",
    "FlextTypes",
    "P",
    "PluginStatus",
    "R",
    "T",
    "TypedDict",
    "U",
    "V",
    "datetime",
]
