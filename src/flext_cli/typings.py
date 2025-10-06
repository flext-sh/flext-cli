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

from typing import Literal, TypeVar

from flext_core import FlextTypes

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
    # MISSING TYPES FROM FLEXT-CORE - Define locally until fixed upstream
    # =========================================================================

    # StringList type (missing from flext-core)
    StringList = list[str]

    # =========================================================================
    # CLI COMMAND TYPES - Complex command processing types
    # =========================================================================

    class CliCommand:
        """CLI command-specific complex types."""

        CommandDefinition = dict[
            str, str | FlextTypes.StringList | dict[str, FlextTypes.JsonValue]
        ]
        CommandPipeline = list[dict[str, FlextTypes.JsonValue]]
        CommandRegistry = dict[
            str,
            dict[str, str | FlextTypes.StringList | dict[str, FlextTypes.JsonValue]],
        ]
        CommandContext = dict[str, FlextTypes.JsonValue]
        CommandResult = FlextTypes.Dict
        CommandMetadata = dict[str, str | int | FlextTypes.StringList]
        CommandArgs = FlextTypes.StringList
        CommandNames = FlextTypes.StringList

    class CliCommandResult:
        """CLI command result type definitions."""

        # Core command result types
        CommandResultData = dict[str, FlextTypes.JsonValue]
        CommandResultStatus = Literal["success", "failure", "error"]
        CommandResultMetadata = dict[str, str | int | bool]

    # =========================================================================
    # CLI CONFIGURATION TYPES - Complex configuration types
    # =========================================================================

    class Configuration:
        """CLI configuration complex types."""

        CliConfigSchema = dict[str, dict[str, FlextTypes.ConfigValue]]
        ProfileConfiguration = FlextTypes.Dict
        EnvironmentConfig = dict[
            str, FlextTypes.ConfigValue | dict[str, FlextTypes.ConfigValue]
        ]
        SessionConfiguration = dict[
            str, str | int | float | bool | FlextTypes.List | FlextTypes.Dict | None
        ]
        AuthenticationConfig = dict[str, str | int | bool | FlextTypes.StringList]
        LogConfig = dict[str, str | None]

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
            str, str | int | float | bool | FlextTypes.List | FlextTypes.Dict | None
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
            str, str | int | float | bool | FlextTypes.List | FlextTypes.Dict | None
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
            | dict
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
        """

        # CLI-specific project types extending the generic ones
        CliProjectType = Literal[
            # CLI-specific types
            "cli-tool",
            "console-app",
            "terminal-ui",
            "command-runner",
            "interactive-cli",
            "batch-processor",
            "cli-wrapper",
        ]

        # CLI-specific project configurations
        CliProjectConfig = dict[str, FlextTypes.ConfigValue]
        CommandLineConfig = dict[str, str | int | bool | FlextTypes.StringList]
        InteractiveConfig = dict[str, bool | str | dict[str, FlextTypes.ConfigValue]]
        OutputConfig = dict[
            str, FlextTypes.Output.OutputFormat | FlextTypes.ConfigValue
        ]


# =============================================================================
# PUBLIC API EXPORTS - CLI TypeVars and types
# =============================================================================

__all__: FlextTypes.StringList = [
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
