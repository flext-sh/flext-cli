"""FLEXT CLI Types - Domain-specific CLI type definitions.

This module provides CLI-specific type definitions extending FlextTypes.
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

from flext_core import FlextTypes
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

# Type aliases for module-level types (used outside class definitions)
type CsvData = list[FlextTypes.StringDict]
type ErrorList = FlextTypes.StringList
type ConnectivityInfo = FlextTypes.StringDict
type FileList = FlextTypes.StringList
type TableHeaders = FlextTypes.StringList
type CommandArgs = FlextTypes.StringList

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


class FlextCliTypes(FlextTypes):
    """CLI-specific type definitions extending FlextTypes.

    Contains complex CLI-specific types that add business value.
    Follows FLEXT pattern: domain-specific complex types only, no simple aliases.
    Uses Python 3.13+ type syntax and patterns.
    """

    # =========================================================================
    # CLI COMMAND TYPES - Complex command processing types
    # Note: StringList available via FlextTypes.StringList
    # =========================================================================

    class CliCommand:
        """CLI command-specific complex types."""

        type CommandDefinition = dict[
            str, str | FlextTypes.StringList | dict[str, FlextTypes.JsonValue]
        ]
        type CommandPipeline = list[dict[str, FlextTypes.JsonValue]]
        type CommandRegistry = dict[
            str,
            dict[
                str,
                str | FlextTypes.StringList | dict[str, FlextTypes.JsonValue],
            ],
        ]
        type CommandContext = dict[str, FlextTypes.JsonValue]
        type CommandResult = FlextTypes.Dict
        type CommandMetadata = dict[str, str | int | FlextTypes.StringList]
        type CommandArgs = FlextTypes.StringList
        type CommandNames = FlextTypes.StringList

    class CliCommandResult:
        """CLI command result type definitions."""

        # Core command result types
        CommandResultData = dict[str, FlextTypes.JsonValue]
        # CommandResultStatus defined in FlextCliConstants.CliCommandResult
        CommandResultMetadata = dict[str, str | int | bool]

    # =========================================================================
    # CLI CONFIGURATION TYPES - Complex configuration types
    # =========================================================================

    class Configuration:
        """CLI configuration complex types."""

        type CliConfigSchema = dict[str, dict[str, FlextTypes.ConfigValue]]
        type ProfileConfiguration = FlextTypes.Dict
        type EnvironmentConfig = dict[
            str, FlextTypes.ConfigValue | dict[str, FlextTypes.ConfigValue]
        ]
        type SessionConfiguration = dict[
            str,
            str | int | float | bool | FlextTypes.List | FlextTypes.Dict | None,
        ]
        type AuthenticationConfig = dict[str, str | int | bool | FlextTypes.StringList]
        type LogConfig = dict[str, str | None]

    # =========================================================================
    # CLI OUTPUT TYPES - Complex output formatting types
    # =========================================================================

    class Output(FlextTypes.Output):
        """CLI output formatting complex types extending FlextTypes.Output."""

        FormatterConfig = dict[
            str, FlextTypes.Output.OutputFormat | FlextTypes.StringDict
        ]
        TableConfiguration = dict[str, str | int | FlextTypes.StringList | bool]
        ProgressBarConfig = dict[str, str | int | bool]
        OutputPipeline = list[
            dict[str, FlextTypes.Output.OutputFormat | FlextTypes.JsonValue]
        ]
        RenderingOptions = dict[str, bool | str | int | FlextTypes.StringList]

    # =========================================================================
    # CLI PROCESSING TYPES - Complex processing types
    # =========================================================================

    class Processing(FlextTypes.Processing):
        """CLI processing complex types extending FlextTypes.Processing."""

        BatchOperation = dict[str, list[dict[str, FlextTypes.JsonValue]]]
        PipelineDefinition = list[dict[str, str | dict[str, FlextTypes.JsonValue]]]
        WorkflowConfiguration = dict[
            str, FlextTypes.Processing.ProcessingStatus | FlextTypes.JsonValue
        ]
        TaskConfiguration = dict[
            str,
            str | int | float | bool | FlextTypes.List | FlextTypes.Dict | None,
        ]

    # =========================================================================
    # CLI DATA TYPES - Complex data processing types
    # =========================================================================

    class Data:
        """CLI data processing complex types."""

        PandasReadCsvKwargs = dict[str, str | int | bool | object]
        PyArrowReadTableKwargs = dict[str, str | int | bool | object]
        PyArrowWriteTableKwargs = dict[str, str | int | bool | object]
        CliDataDict = dict[str, FlextTypes.JsonValue]
        CliCommandData = dict[str, FlextTypes.JsonValue]
        CliCommandResult = dict[
            str,
            str | int | float | bool | FlextTypes.List | FlextTypes.Dict | None,
        ]
        CliCommandArgs = dict[str, FlextTypes.JsonValue]
        CliFormatData = dict[str, FlextTypes.JsonValue]
        CliConfigData = dict[str, FlextTypes.JsonValue]
        AuthConfigData = dict[str, str | int | bool]
        DebugInfoData = dict[
            str,
            str
            | int
            | float
            | bool
            | FlextTypes.List
            | FlextTypes.Dict
            | FlextTypes.StringList
            | None,
        ]
        ErrorList = FlextTypes.StringList
        FileList = FlextTypes.StringList
        CsvData = list[FlextTypes.StringDict]
        ConnectivityInfo = FlextTypes.StringDict
        TableHeaders = FlextTypes.StringList
        TableRows = list[FlextTypes.StringList]
        PathInfoList = list[dict[str, FlextTypes.JsonValue]]

    class PandasTypes:
        """Pandas-specific type definitions for CLI data processing."""

        PandasToCsvKwargs = dict[str, str | int | bool | object]

    # =========================================================================
    # CLI AUTH TYPES - Authentication and authorization types
    # =========================================================================

    class Auth:
        """CLI authentication complex types."""

        PermissionList = FlextTypes.StringList
        RoleList = FlextTypes.StringList
        SessionData = dict[str, str | int | bool]
        CredentialsData = dict[str, FlextTypes.JsonValue]
        UserData = dict[str, FlextTypes.JsonValue]
        AuthResult = dict[str, FlextTypes.JsonValue]
        UserList = list[dict[str, FlextTypes.JsonValue]]

    # =========================================================================
    # CLI HTTP TYPES - HTTP-related types
    # =========================================================================

    class Http:
        """CLI HTTP complex types."""

        Headers = FlextTypes.StringDict
        ResponseData = FlextTypes.Dict
        RequestData = FlextTypes.Dict

    # =========================================================================
    # CLI PROJECT TYPES - Domain-specific project types extending FlextTypes
    # =========================================================================

    class Project(FlextTypes.Project):
        """CLI-specific project types extending FlextTypes.Project.

        Adds CLI-specific project types while inheriting generic types from FlextTypes.
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

        # Type aliases from module-level imports using Python 3.12+ type statement
        type Console = RichConsoleImport
        type RichPanel = RichPanelImport
        type RichTable = RichTableImport
        type RichTree = RichTreeImport

    class Layout:
        """Rich layout component type aliases for CLI layout.

        Type aliases for Rich library layout components - re-exported from formatters.
        Follows ZERO TOLERANCE principle: NO direct Rich imports in user code.
        """

        # Type alias from module-level import using Python 3.12+ type statement
        type RichLayout = RichLayoutImport

    class Interactive:
        """Rich interactive component type aliases for CLI interaction.

        Type aliases for Rich library interactive components - re-exported from formatters.
        Follows ZERO TOLERANCE principle: NO direct Rich imports in user code.
        """

        # Type aliases from module-level imports using Python 3.12+ type statement
        type RichLive = RichLiveImport
        type Progress = ProgressImport
        type RichStatus = RichStatusImport

    class ProgressColumns:
        """Rich progress column type aliases for CLI progress tracking.

        Type aliases for Rich library progress column components - re-exported from formatters.
        Follows ZERO TOLERANCE principle: NO direct Rich imports in user code.
        """

        # Type aliases from module-level imports using Python 3.12+ type statement
        type BarColumn = BarColumnImport
        type SpinnerColumn = SpinnerColumnImport
        type TextColumn = TextColumnImport
        type TimeRemainingColumn = TimeRemainingColumnImport


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

__all__: FlextTypes.StringList = [
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
