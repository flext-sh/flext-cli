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

import typing
from typing import Annotated, TypeVar

from flext_core import FlextResult, FlextTypes
from pydantic import Field
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

# Module-level TypeVars
TCliCommand = TypeVar("TCliCommand")
TCliConfig = TypeVar("TCliConfig")
TCliOutput = TypeVar("TCliOutput")
TCliResult = TypeVar("TCliResult")
TCliSession = TypeVar("TCliSession")
TCliContext = TypeVar("TCliContext")
TCliPlugin = TypeVar("TCliPlugin")
TCliFormatter = TypeVar("TCliFormatter")


class FlextCliTypes(FlextTypes):
    """CLI-specific type definitions extending FlextTypes.

    Provides Pydantic v2 Annotated types with validation constraints
    for CLI-specific field patterns, and Rich component type aliases.
    """

    # =====================================================================
    # CORE TYPE ALIASES - Direct use of FlextTypes domain types
    # =====================================================================
    # Note: JsonValue is inherited from FlextTypes and not redefined here
    # to avoid override conflicts. Use FlextTypes.JsonValue directly.

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
            str, Field(pattern=r"^[a-z][a-z0-9-]*$", min_length=1, max_length=64)
        ]
        """Command name with kebab-case pattern validation."""

        OptionName = Annotated[
            str, Field(pattern=r"^--[a-z][a-z0-9-]*$", min_length=3, max_length=64)
        ]
        """CLI option name with double-dash prefix."""

        ProfileName = Annotated[str, Field(min_length=1, max_length=64)]
        """Configuration profile name."""

        # Numeric types with value constraints
        PortNumber = Annotated[int, Field(ge=1, le=65535)]
        """Port number (valid range: 1-65535)."""

        TimeoutMs = Annotated[int, Field(ge=100, le=300000)]
        """Timeout in milliseconds (100ms-300s)."""

        BatchSize = Annotated[int, Field(ge=1, le=10000)]
        """Batch processing size (1-10000 items)."""

        MaxRetries = Annotated[int, Field(ge=0, le=100)]
        """Maximum number of retries (0-100)."""

        MaxWorkers = Annotated[int, Field(ge=1, le=50)]
        """Maximum number of parallel workers (1-50)."""

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
            str, Field(pattern=r"^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")
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
        CliFormatData = dict[str, FlextTypes.JsonValue]
        """Data structure for CLI formatting operations."""

        CliConfigData = dict[str, FlextTypes.JsonValue]
        """Data structure for CLI configuration (load/save/options)."""

        AuthConfigData = dict[str, FlextTypes.JsonValue]
        """Data structure for authentication configuration and credentials."""

        DebugInfoData = dict[str, FlextTypes.JsonValue]
        """Data structure for debug information."""

        CliCommandArgs = dict[str, FlextTypes.JsonValue]
        """Data structure for CLI command arguments and kwargs."""

        CliCommandResult = dict[str, FlextTypes.JsonValue]
        """Data structure for CLI command execution results."""

        # Additional CLI data structures
        CliDataDict = dict[str, FlextTypes.JsonValue]
        """Generic CLI data dictionary for flexible data passing."""

        CliCommandData = dict[str, FlextTypes.JsonValue]
        """Data structure for CLI command data and metadata."""

    # =====================================================================
    # AUTH DATA TYPES - Authentication and credentials
    # =====================================================================

    class Auth:
        """Authentication data type aliases."""

        CredentialsData = dict[str, FlextTypes.JsonValue]
        """Data structure for credentials (username, password, token)."""

    # =====================================================================
    # CLI COMMAND TYPES - Command execution and results
    # =====================================================================

    class CliCommand:
        """CLI command type aliases for command execution framework."""

        CommandDefinition = dict[str, FlextTypes.JsonValue]
        """Data structure for command definition."""

        CommandContext = dict[str, FlextTypes.JsonValue]
        """Data structure for command execution context."""

        CommandResult = dict[str, FlextTypes.JsonValue]
        """Data structure for command execution results."""

    # =====================================================================
    # CONFIGURATION TYPES - Application configuration
    # =====================================================================

    class Configuration:
        """Configuration type aliases."""

        CliConfigSchema = dict[str, FlextTypes.JsonValue]
        """Data structure for CLI configuration schema."""

        ProfileConfiguration = dict[str, FlextTypes.JsonValue]
        """Data structure for configuration profile."""

        SessionConfiguration = dict[str, FlextTypes.JsonValue]
        """Data structure for session configuration."""

    # =====================================================================
    # CALLABLE TYPE ALIASES - Function signatures for CLI operations
    # =====================================================================

    class Callable:
        """CLI-specific callable type aliases for handlers and formatters."""

        # Handler function that processes CLI data and returns result
        HandlerFunction = typing.Callable[
            [FlextTypes.JsonValue], FlextResult[FlextTypes.JsonValue]
        ]
        """CLI command handler function signature."""

        # Result formatter that displays domain-specific result types
        ResultFormatter = typing.Callable[[object, str], None]
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
