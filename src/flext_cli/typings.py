"""FLEXT CLI Types - Direct CLI type system using FlextTypes foundation.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from pathlib import Path
from typing import Literal, Protocol, TypedDict
from uuid import UUID

from flext_core import FlextResult


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
            "PENDING", "RUNNING", "COMPLETED", "FAILED", "CANCELLED"
        ]

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
        """CLI configuration types extending FlextTypes.Config."""

        # CLI-specific config types - direct definitions
        CliProfile = str
        CliOutputFormat = Literal["table", "json", "yaml", "csv"]
        CliLogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        CliTimeout = int
        CliConfigPath = Path

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
            "authenticated", "unauthenticated", "expired", "invalid"
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
        """CLI session types extending FlextTypes.Core."""

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
                self, request: str | dict[str, object]
            ) -> FlextResult[object]: ...
            def build(
                self, domain: object, *, correlation_id: str
            ) -> str | dict[str, object]: ...

        class CliValidator(Protocol):
            """Protocol for CLI validators."""

            def validate(
                self, data: dict[str, object] | str | float
            ) -> FlextResult[None]: ...

        class CliFormatter(Protocol):
            """Protocol for CLI formatters."""

            def format(
                self, data: dict[str, object] | list[object] | str, format_type: str
            ) -> FlextResult[str]: ...

        class CliAuthenticator(Protocol):
            """Protocol for CLI authenticators."""

            def authenticate(
                self, credentials: dict[str, str]
            ) -> FlextResult[FlextCliTypes.Auth.CliAuthContext]: ...
            def is_authenticated(self) -> bool: ...


# =============================================================================
# EXPORTS - Single unified class following user requirements
# =============================================================================

__all__ = [
    "FlextCliTypes",
]
