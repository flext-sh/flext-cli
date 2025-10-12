"""FLEXT CLI Types - Domain-specific CLI type definitions.

This module provides CLI-specific type definitions extending FlextCore.Types.
Follows FLEXT standards:
- Single unified class per module
- Domain-specific complex types only
- Python 3.13+ syntax
- No simple aliases to primitive types

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TypeVar

from flext_core import FlextCore

# Rich library imports - centralized at module top for PLC0415 compliance
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

# Type aliases for module-level types (used outside class definitions)
type CsvData = list[FlextCore.Types.StringDict]
type ErrorList = FlextCore.Types.StringList
type ConnectivityInfo = FlextCore.Types.StringDict
type FileList = FlextCore.Types.StringList
type TableHeaders = FlextCore.Types.StringList
type CommandArgs = FlextCore.Types.StringList

# =============================================================================
# CLI-SPECIFIC TYPE VARIABLES - Domain-specific TypeVars for CLI operations
# =============================================================================

# CLI domain TypeVars
TCliCommand = TypeVar("TCliCommand")
TCliConfig = TypeVar("TCliConfig")
TCliOutput = TypeVar("TCliOutput")
TCliResult = TypeVar("TCliResult")
TCliSession = TypeVar("TCliSession")
TCliContext = TypeVar("TCliContext")
TCliPlugin = TypeVar("TCliPlugin")
TCliFormatter = TypeVar("TCliFormatter")

# Generic TypeVar for utility functions
T = TypeVar("T")


class FlextCliTypes(FlextCore.Types):
    """CLI-specific type definitions extending FlextCore.Types.

    Contains complex CLI-specific types that add business value.
    Follows FLEXT pattern: domain-specific complex types only, no simple aliases.
    Uses Python 3.13+ type syntax and patterns.
    """

    # =========================================================================
    # CLI COMMAND TYPES - Complex command processing types
    # Note: StringList available via FlextCore.Types.StringList
    # =========================================================================

    class CliCommand:
        """CLI command-specific complex types."""

        type CommandDefinition = dict[
            str, str | FlextCore.Types.StringList | dict[str, FlextCore.Types.JsonValue]
        ]
        type CommandPipeline = list[dict[str, FlextCore.Types.JsonValue]]
        type CommandRegistry = dict[
            str,
            dict[
                str,
                str | FlextCore.Types.StringList | dict[str, FlextCore.Types.JsonValue],
            ],
        ]
        type CommandContext = dict[str, FlextCore.Types.JsonValue]
        type CommandResult = FlextCore.Types.Dict
        type CommandMetadata = dict[str, str | int | FlextCore.Types.StringList]
        type CommandArgs = FlextCore.Types.StringList
        type CommandNames = FlextCore.Types.StringList

    class CliCommandResult:
        """CLI command result type definitions."""

        # Core command result types
        CommandResultData = dict[str, FlextCore.Types.JsonValue]
        # CommandResultStatus defined in FlextCliConstants.CliCommandResult
        CommandResultMetadata = dict[str, str | int | bool]

    # =========================================================================
    # CLI CONFIGURATION TYPES - Complex configuration types
    # =========================================================================

    class Configuration:
        """CLI configuration complex types."""

        type CliConfigSchema = dict[str, dict[str, FlextCore.Types.ConfigValue]]
        type ProfileConfiguration = FlextCore.Types.Dict
        type EnvironmentConfig = dict[
            str, FlextCore.Types.ConfigValue | dict[str, FlextCore.Types.ConfigValue]
        ]
        type SessionConfiguration = dict[
            str,
            str
            | int
            | float
            | bool
            | FlextCore.Types.List
            | FlextCore.Types.Dict
            | None,
        ]
        type AuthenticationConfig = dict[
            str, str | int | bool | FlextCore.Types.StringList
        ]
        type LogConfig = dict[str, str | None]

    # =========================================================================
    # CLI OUTPUT TYPES - Complex output formatting types
    # =========================================================================

    class Output(FlextCore.Types.Output):
        """CLI output formatting complex types extending FlextCore.Types.Output."""

        FormatterConfig = dict[
            str, FlextCore.Types.Output.OutputFormat | FlextCore.Types.StringDict
        ]
        TableConfiguration = dict[str, str | int | FlextCore.Types.StringList | bool]
        ProgressBarConfig = dict[str, str | int | bool]
        OutputPipeline = list[
            dict[str, FlextCore.Types.Output.OutputFormat | FlextCore.Types.JsonValue]
        ]
        RenderingOptions = dict[str, bool | str | int | FlextCore.Types.StringList]

    # =========================================================================
    # CLI PROCESSING TYPES - Complex processing types
    # =========================================================================

    class Processing(FlextCore.Types.Processing):
        """CLI processing complex types extending FlextCore.Types.Processing."""

        BatchOperation = dict[str, list[dict[str, FlextCore.Types.JsonValue]]]
        PipelineDefinition = list[dict[str, str | dict[str, FlextCore.Types.JsonValue]]]
        WorkflowConfiguration = dict[
            str, FlextCore.Types.Processing.ProcessingStatus | FlextCore.Types.JsonValue
        ]
        TaskConfiguration = dict[
            str,
            str
            | int
            | float
            | bool
            | FlextCore.Types.List
            | FlextCore.Types.Dict
            | None,
        ]

    # =========================================================================
    # CLI DATA TYPES - Complex data processing types
    # =========================================================================

    class Data:
        """CLI data processing complex types."""

        PandasReadCsvKwargs = dict[str, str | int | bool | object]
        PyArrowReadTableKwargs = dict[str, str | int | bool | object]
        PyArrowWriteTableKwargs = dict[str, str | int | bool | object]
        CliDataDict = dict[str, FlextCore.Types.JsonValue]
        CliCommandData = dict[str, FlextCore.Types.JsonValue]
        CliCommandResult = dict[
            str,
            str
            | int
            | float
            | bool
            | FlextCore.Types.List
            | FlextCore.Types.Dict
            | None,
        ]
        CliCommandArgs = dict[str, FlextCore.Types.JsonValue]
        CliFormatData = dict[str, FlextCore.Types.JsonValue]
        CliConfigData = dict[str, FlextCore.Types.JsonValue]
        AuthConfigData = dict[str, str | int | bool]
        DebugInfoData = dict[
            str,
            str
            | int
            | float
            | bool
            | FlextCore.Types.List
            | FlextCore.Types.Dict
            | FlextCore.Types.StringList
            | None,
        ]
        ErrorList = FlextCore.Types.StringList
        FileList = FlextCore.Types.StringList
        CsvData = list[FlextCore.Types.StringDict]
        ConnectivityInfo = FlextCore.Types.StringDict
        TableHeaders = FlextCore.Types.StringList
        TableRows = list[FlextCore.Types.StringList]
        PathInfoList = list[dict[str, FlextCore.Types.JsonValue]]

    class PandasTypes:
        """Pandas-specific type definitions for CLI data processing."""

        PandasToCsvKwargs = dict[str, str | int | bool | object]

    # =========================================================================
    # CLI AUTH TYPES - Authentication and authorization types
    # =========================================================================

    class Auth:
        """CLI authentication complex types."""

        PermissionList = FlextCore.Types.StringList
        RoleList = FlextCore.Types.StringList
        SessionData = dict[str, str | int | bool]
        CredentialsData = dict[str, FlextCore.Types.JsonValue]
        UserData = dict[str, FlextCore.Types.JsonValue]
        AuthResult = dict[str, FlextCore.Types.JsonValue]
        UserList = list[dict[str, FlextCore.Types.JsonValue]]

    # =========================================================================
    # CLI HTTP TYPES - HTTP-related types
    # =========================================================================

    class Http:
        """CLI HTTP complex types."""

        Headers = FlextCore.Types.StringDict
        ResponseData = FlextCore.Types.Dict
        RequestData = FlextCore.Types.Dict

    # =========================================================================
    # CLI PROJECT TYPES - Domain-specific project types extending FlextCore.Types
    # =========================================================================

    class Project(FlextCore.Types.Project):
        """CLI-specific project types extending FlextCore.Types.Project.

        Adds CLI-specific project types while inheriting generic types from FlextCore.Types.
        Follows domain separation principle: CLI domain owns CLI-specific types.
        CLI-specific types defined in FlextCliConstants.Project.
        """

    # =========================================================================
    # CLI DISPLAY TYPES - Rich visual component type aliases
    # =========================================================================

    class Display:
        """Rich visual component type aliases for CLI display.

        Type aliases for Rich library visual components - re-exported from formatters.
        Follows ZERO TOLERANCE principle: NO direct Rich imports in user code.
        """

        # Type aliases from module-level imports
        RichPanel = RichPanelImport
        RichTable = RichTableImport
        RichTree = RichTreeImport

    class Layout:
        """Rich layout component type aliases for CLI layout.

        Type aliases for Rich library layout components - re-exported from formatters.
        Follows ZERO TOLERANCE principle: NO direct Rich imports in user code.
        """

        # Type alias from module-level import
        RichLayout = RichLayoutImport

    class Interactive:
        """Rich interactive component type aliases for CLI interaction.

        Type aliases for Rich library interactive components - re-exported from formatters.
        Follows ZERO TOLERANCE principle: NO direct Rich imports in user code.
        """

        # Type aliases from module-level imports
        RichLive = RichLiveImport
        Progress = ProgressImport
        RichStatus = RichStatusImport

    class ProgressColumns:
        """Rich progress column type aliases for CLI progress tracking.

        Type aliases for Rich library progress column components - re-exported from formatters.
        Follows ZERO TOLERANCE principle: NO direct Rich imports in user code.
        """

        # Type aliases from module-level imports
        BarColumn = BarColumnImport
        SpinnerColumn = SpinnerColumnImport
        TextColumn = TextColumnImport
        TimeRemainingColumn = TimeRemainingColumnImport


# =============================================================================
# MODULE-LEVEL ALIASES - For convenient imports from flext_cli
# =============================================================================

# Re-export Rich components from FlextCliTypes nested classes
RichTable = FlextCliTypes.Display.RichTable
RichTree = FlextCliTypes.Display.RichTree
RichPanel = FlextCliTypes.Display.RichPanel
RichLayout = FlextCliTypes.Layout.RichLayout
RichLive = FlextCliTypes.Interactive.RichLive
RichStatus = FlextCliTypes.Interactive.RichStatus
Progress = FlextCliTypes.Interactive.Progress
BarColumn = FlextCliTypes.ProgressColumns.BarColumn
SpinnerColumn = FlextCliTypes.ProgressColumns.SpinnerColumn
TextColumn = FlextCliTypes.ProgressColumns.TextColumn
TimeRemainingColumn = FlextCliTypes.ProgressColumns.TimeRemainingColumn

# =============================================================================
# PUBLIC API EXPORTS - CLI TypeVars and types
# =============================================================================

__all__: FlextCore.Types.StringList = [
    "BarColumn",
    "FlextCliTypes",
    "Progress",
    "RichLayout",
    "RichLive",
    "RichPanel",
    "RichStatus",
    # Rich component type aliases from FlextCliTypes nested classes
    "RichTable",
    "RichTree",
    "SpinnerColumn",
    "TCliCommand",
    "TCliConfig",
    "TCliContext",
    "TCliFormatter",
    "TCliOutput",
    "TCliPlugin",
    "TCliResult",
    "TCliSession",
    "TextColumn",
    "TimeRemainingColumn",
]
