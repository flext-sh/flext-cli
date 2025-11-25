"""FLEXT CLI Types - Domain-specific CLI type definitions.

This module provides CLI-specific type definitions extending FlextTypes.
Follows FLEXT standards:
- Single unified class per module
- Domain-specific types with business value
- Python 3.13+ syntax
- Pydantic v2 Annotated types with validation constraints

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Callable as CallableABC, Sequence
from typing import Annotated, Literal, ParamSpec, Protocol, TypeAlias, TypeVar

from flext_core import FlextResult, FlextTypes
from pydantic import BaseModel, Field
from rich.console import Console as RichConsoleImport
from rich.layout import Layout as RichLayoutImport
from rich.live import Live as RichLiveImport
from rich.panel import Panel as RichPanelImport
from rich.progress import (
    BarColumn as BarColumnImport,
    Progress as ProgressImport,
    SpinnerColumn as SpinnerColumnImport,
    TextColumn as TextColumnImport,
    TimeRemainingColumn as TimeRemainingColumnImport,
)
from rich.status import Status as RichStatusImport
from rich.table import Table as RichTableImport
from rich.tree import Tree as RichTreeImport

P = ParamSpec("P")

# Module-level TypeVars
TCliCommand = TypeVar("TCliCommand")
TCliConfig = TypeVar("TCliConfig")
TCliOutput = TypeVar("TCliOutput")
TCliResult = TypeVar("TCliResult")
TCliSession = TypeVar("TCliSession")
TCliContext = TypeVar("TCliContext")
TCliPlugin = TypeVar("TCliPlugin")
TCliFormatter = TypeVar("TCliFormatter")

# Type aliases for CLI data structures
# Compatible with mypy and replaces CliJsonValue usage
type CliJsonValue = str | int | float | bool | dict[str, object] | list[object] | None
CliJsonDict: TypeAlias = dict[str, CliJsonValue]
CliJsonList: TypeAlias = list[CliJsonValue]


class FlextCliTypes(FlextTypes):
    """CLI-specific type definitions extending FlextTypes.

    Provides Pydantic v2 Annotated types with validation constraints
    for CLI-specific field patterns, and Rich component type aliases.
    """

    # =====================================================================
    # CORE TYPE ALIASES - Direct use of FlextTypes domain types
    # =====================================================================
    # Note: JsonValue is inherited from FlextTypes and not redefined here
    # to avoid override conflicts. Use CliJsonValue directly.

    # =====================================================================
    # ANNOTATED CLI TYPES - Pydantic v2 Annotated types with validation
    # =====================================================================

    class AnnotatedCli:
        """CLI-specific Annotated types with built-in validation constraints.

        Provides reusable Annotated type definitions for CLI-specific field
        patterns, eliminating verbose Field() declarations in CLI commands
        and models.

        Example:
            from flext_cli.typings import FlextCliTypes
            from pydantic import BaseModel

            class CommandParams(BaseModel):
                command_name: FlextCliTypes.AnnotatedCli.CommandName
                port: FlextCliTypes.AnnotatedCli.PortNumber
                batch_size: FlextCliTypes.AnnotatedCli.BatchSize

        """

        # Command string types with validation
        CommandName = Annotated[
            str,
            Field(pattern=r"^[a-z][a-z0-9-]*$", min_length=1, max_length=64),
        ]
        """Command name with kebab-case pattern validation."""

        OptionName = Annotated[
            str,
            Field(pattern=r"^--[a-z][a-z0-9-]*$", min_length=3, max_length=64),
        ]
        """CLI option name with double-dash prefix."""

        ProfileName = Annotated[str, Field(min_length=1, max_length=64)]
        """Configuration profile name."""

        # Numeric types with value constraints
        TimeoutMs = Annotated[int, Field(ge=100, le=300000)]
        """Timeout in milliseconds (100ms-300s)."""

        BatchSize = Annotated[int, Field(ge=1, le=10000)]
        """Batch processing size (1-10000 items)."""

        MaxRetries = Annotated[int, Field(ge=0, le=100)]
        """Maximum number of retries (0-100)."""

        MaxWorkers = Annotated[int, Field(ge=1, le=50)]
        """Maximum number of parallel workers (1-50)."""

        # Validation constraint types (Pydantic v2 native)
        NotEmptyStr = Annotated[str, Field(min_length=1)]
        """Non-empty string (min length 1)."""

        PositiveNumber = Annotated[int, Field(gt=0)]
        """Positive integer (> 0)."""

        NonNegativeNumber = Annotated[int, Field(ge=0)]
        """Non-negative integer (>= 0)."""

        # Enum-like types using Literal (Pydantic v2 native)
        # CRITICAL: Mirrors FlextCliConstants values (avoid circular import)
        OutputFormatEnum = Literal["json", "yaml", "csv", "table", "plain"]
        """Output format options - mirrors FlextCliConstants.OutputFormatLiteral."""

        LogLevelEnum = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        """Log level options - mirrors FlextCliConstants.LogLevelLiteral."""

        CommandStatusEnum = Literal[
            "pending", "running", "completed", "failed", "cancelled"
        ]
        """Command execution status options - mirrors FlextCliConstants.CommandStatusLiteral."""

        # Path and file types
        ConfigFilePath = Annotated[str, Field(min_length=1)]
        """Path to configuration file."""

        OutputDirectory = Annotated[str, Field(min_length=1)]
        """Path to output directory."""

        # Output format types
        OutputFormat = Annotated[str, Field(pattern=r"^(json|yaml|csv|table|plain)$")]
        """Supported output format (json, yaml, csv, table, plain)."""

        TableWidth = Annotated[int, Field(ge=40, le=300)]
        """Table display width in characters (40-300)."""

        # Logging and debug types
        LogLevel = Annotated[
            str,
            Field(pattern=r"^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$"),
        ]
        """Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)."""

        VerbosityLevel = Annotated[int, Field(ge=0, le=3)]
        """Verbosity level (0-3, where 0=quiet, 3=very verbose)."""

    # =====================================================================
    # CLI DATA TYPES - Protocol data structures for CLI operations
    # =====================================================================

    class Data:
        """CLI data type aliases for protocol operations.

        Provides reusable type definitions for CLI data structures used in
        protocols and handlers. All data types are dict-based for flexibility
        and compatibility with JSON serialization.

        Example:
            from flext_cli.typings import FlextCliTypes
            from flext_core import FlextResult

            class MyFormatter:
                def format_data(
                    self,
                    data: FlextCliTypes.Data.CliFormatData,
                    **options: FlextCliTypes.Data.CliConfigData,
                ) -> FlextResult[str]:
                    # Implementation
                    return FlextResult[str].ok("formatted")

        """

        # Data structures for CLI formatting and configuration
        CliFormatData: TypeAlias = CliJsonDict
        """Data structure for CLI formatting operations."""

        CliConfigData: TypeAlias = CliJsonDict
        """Data structure for CLI configuration (load/save/options)."""

        AuthConfigData: TypeAlias = CliJsonDict
        """Data structure for authentication configuration and credentials."""

        DebugInfoData: TypeAlias = CliJsonDict
        """Data structure for debug information."""

        CliCommandArgs: TypeAlias = CliJsonDict
        """Data structure for CLI command arguments and kwargs."""

        CliCommandResult: TypeAlias = CliJsonDict
        """Data structure for CLI command execution results."""

        # Additional CLI data structures
        CliDataDict: TypeAlias = CliJsonDict
        """Generic CLI data dictionary for flexible data passing."""

        TableRow: TypeAlias = CliJsonDict
        """Single row of tabular CLI data."""

        TableData: TypeAlias = Sequence[CliJsonDict] | CliJsonDict
        """Tabular data represented as a sequence of dictionaries or a single row."""

        TabularData: TypeAlias = TableData
        """Complete table input supporting rows defined as dictionaries."""

        CliCommandData: TypeAlias = CliJsonDict
        """Data structure for CLI command data and metadata."""

    # =====================================================================
    # AUTH DATA TYPES - Authentication and credentials
    # =====================================================================

    class Auth:
        """Authentication data type aliases."""

        CredentialsData: TypeAlias = CliJsonDict
        """Data structure for credentials (username, password, token)."""

    # =====================================================================
    # CLI COMMAND TYPES - Command execution and results
    # =====================================================================

    class CliCommand:
        """CLI command type aliases for command execution framework."""

        CommandDefinition: TypeAlias = CliJsonDict
        """Data structure for command definition."""

        CommandContext: TypeAlias = CliJsonDict
        """Data structure for command execution context."""

        CommandResult: TypeAlias = CliJsonDict
        """Data structure for command execution results."""

    # =====================================================================
    # CONFIGURATION TYPES - Application configuration
    # =====================================================================

    class Configuration:
        """Configuration type aliases."""

        CliConfigSchema: TypeAlias = CliJsonDict
        """Data structure for CLI configuration schema."""

        ProfileConfiguration: TypeAlias = CliJsonDict
        """Data structure for configuration profile."""

        SessionConfiguration: TypeAlias = CliJsonDict
        """Data structure for session configuration."""

    # =====================================================================
    # CALLABLE TYPE ALIASES - Function signatures for CLI operations
    # =====================================================================

    class Callable:
        """CLI-specific callable type aliases for handlers and formatters."""

        # Handler function that processes CLI data and returns result
        # Accepts **kwargs (context_data) and returns FlextResult
        HandlerFunction = CallableABC[..., FlextResult[CliJsonValue]]
        """CLI command handler function signature - accepts **kwargs."""

        # Result formatter that displays domain-specific result types
        # Accepts BaseModel, dict, or objects with __dict__ attribute
        class FormatableResult(Protocol):
            """Protocol for results that can be formatted."""

            __dict__: dict[str, object]

        ResultFormatter = CallableABC[
            [BaseModel | CliJsonValue | FormatableResult, str],
            None,
        ]
        """Result formatter function signature: (result, output_format) -> None."""

    # =====================================================================
    # RICH COMPONENT TYPE ALIASES
    # =====================================================================

    class Display:
        """Rich visual component type aliases."""

        type Console = RichConsoleImport
        type RichPanel = RichPanelImport
        type RichTable = RichTableImport
        type RichTree = RichTreeImport

    class Layout:
        """Rich layout component type aliases."""

        type RichLayout = RichLayoutImport

    class Interactive:
        """Rich interactive component type aliases."""

        type RichLive = RichLiveImport
        type Progress = ProgressImport
        type RichStatus = RichStatusImport

    class ProgressColumns:
        """Rich progress column type aliases."""

        type BarColumn = BarColumnImport
        type SpinnerColumn = SpinnerColumnImport
        type TextColumn = TextColumnImport
        type TimeRemainingColumn = TimeRemainingColumnImport

    # =====================================================================
    # CLI PROJECT TYPES - Domain-specific project types
    # =====================================================================
    # Project class removed to avoid override conflicts with FlextTypes.Project
    # CLI-specific project type aliases can be added here if needed


__all__: list[str] = [
    "CliJsonDict",
    "CliJsonList",
    "CliJsonValue",
    "FlextCliTypes",
    "TCliCommand",
    "TCliConfig",
    "TCliContext",
    "TCliFormatter",
    "TCliOutput",
    "TCliPlugin",
    "TCliResult",
    "TCliSession",
]
