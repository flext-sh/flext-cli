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

from typing import Literal, TypeVar

from flext_core import FlextCore

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
            str, str | FlextCore.Types.StringList | dict[str, FlextCore.Types.JsonValue]
        ]
        CommandPipeline = list[dict[str, FlextCore.Types.JsonValue]]
        CommandRegistry = dict[
            str,
            dict[
                str,
                str | FlextCore.Types.StringList | dict[str, FlextCore.Types.JsonValue],
            ],
        ]
        CommandContext = dict[str, FlextCore.Types.JsonValue]
        CommandResult = FlextCore.Types.Dict
        CommandMetadata = dict[str, str | int | FlextCore.Types.StringList]
        CommandArgs = FlextCore.Types.StringList
        CommandNames = FlextCore.Types.StringList

    class CliCommandResult:
        """CLI command result type definitions."""

        # Core command result types
        CommandResultData = dict[str, FlextCore.Types.JsonValue]
        CommandResultStatus = Literal["success", "failure", "error"]
        CommandResultMetadata = dict[str, str | int | bool]

    # =========================================================================
    # CLI CONFIGURATION TYPES - Complex configuration types
    # =========================================================================

    class Configuration:
        """CLI configuration complex types."""

        CliConfigSchema = dict[str, dict[str, FlextCore.Types.ConfigValue]]
        ProfileConfiguration = FlextCore.Types.Dict
        EnvironmentConfig = dict[
            str, FlextCore.Types.ConfigValue | dict[str, FlextCore.Types.ConfigValue]
        ]
        SessionConfiguration = dict[
            str,
            str
            | int
            | float
            | bool
            | FlextCore.Types.List
            | FlextCore.Types.Dict
            | None,
        ]
        AuthenticationConfig = dict[str, str | int | bool | FlextCore.Types.StringList]
        LogConfig = dict[str, str | None]

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
                | dict[str, object]
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
        CliProjectConfig = dict[str, FlextCore.Types.ConfigValue]
        CommandLineConfig = dict[str, str | int | bool | FlextCore.Types.StringList]
        InteractiveConfig = dict[
            str, bool | str | dict[str, FlextCore.Types.ConfigValue]
        ]
        OutputConfig = dict[
            str, FlextCore.Types.Output.OutputFormat | FlextCore.Types.ConfigValue
        ]


# =============================================================================
# PUBLIC API EXPORTS - CLI TypeVars and types
# =============================================================================

__all__: FlextCore.Types.StringList = [
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
