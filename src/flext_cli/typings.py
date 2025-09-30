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


class FlextCliTypes(FlextTypes):
    """CLI-specific type definitions extending FlextTypes.

    Contains complex CLI-specific types that add business value.
    Follows FLEXT pattern: domain-specific complex types only, no simple aliases.
    Uses Python 3.13+ type syntax and patterns.
    """

    # =========================================================================
    # CLI COMMAND TYPES - Complex command processing types
    # =========================================================================

    class Command:
        """CLI command-specific complex types."""

        CommandDefinition = dict[
            str, str | list[str] | dict[str, FlextTypes.Core.JsonValue]
        ]
        CommandPipeline = list[dict[str, FlextTypes.Core.JsonValue]]
        CommandRegistry = dict[
            str, dict[str, str | list[str] | dict[str, FlextTypes.Core.JsonValue]]
        ]
        CommandContext = dict[str, FlextTypes.Core.JsonValue]
        CommandResult = dict[str, object]
        CommandMetadata = dict[str, str | int | list[str]]
        CommandArgs = list[str]
        CommandNames = list[str]

    class CliCommandResult:
        """CLI command result type definitions."""

        # Core command result types
        CommandResultData = dict[str, FlextTypes.Core.JsonValue]
        CommandResultStatus = Literal["success", "failure", "error"]
        CommandResultMetadata = dict[str, str | int | bool]

    # =========================================================================
    # CLI CONFIGURATION TYPES - Complex configuration types
    # =========================================================================

    class Configuration:
        """CLI configuration complex types."""

        CliConfigSchema = dict[str, dict[str, FlextTypes.Core.ConfigValue]]
        ProfileConfiguration = dict[str, object]
        EnvironmentConfig = dict[
            str, FlextTypes.Core.ConfigValue | dict[str, FlextTypes.Core.ConfigValue]
        ]
        SessionConfiguration = dict[
            str, str | int | float | bool | list[object] | dict[str, object] | None
        ]
        AuthenticationConfig = dict[str, str | int | bool | list[str]]
        LogConfig = dict[str, str | None]

    # =========================================================================
    # CLI OUTPUT TYPES - Complex output formatting types
    # =========================================================================

    class Output(FlextTypes.Output):
        """CLI output formatting complex types extending FlextTypes.Output."""

        FormatterConfig = dict[str, FlextTypes.Output.OutputFormat | dict[str, str]]
        TableConfiguration = dict[str, str | int | list[str] | bool]
        ProgressBarConfig = dict[str, str | int | bool]
        OutputPipeline = list[
            dict[str, FlextTypes.Output.OutputFormat | FlextTypes.Core.JsonValue]
        ]
        RenderingOptions = dict[str, bool | str | int | list[str]]

    # =========================================================================
    # CLI PROCESSING TYPES - Complex processing types
    # =========================================================================

    class Processing(FlextTypes.Processing):
        """CLI processing complex types extending FlextTypes.Processing."""

        BatchOperation = dict[str, list[dict[str, FlextTypes.Core.JsonValue]]]
        PipelineDefinition = list[dict[str, str | dict[str, FlextTypes.Core.JsonValue]]]
        WorkflowConfiguration = dict[
            str, FlextTypes.Processing.ProcessingStatus | FlextTypes.Core.JsonValue
        ]
        TaskConfiguration = dict[
            str, str | int | float | bool | list[object] | dict[str, object] | None
        ]

    # =========================================================================
    # CLI DATA TYPES - Complex data processing types
    # =========================================================================

    class Data:
        """CLI data processing complex types."""

        PandasReadCsvKwargs = dict[str, str | int | bool | object]
        PyArrowReadTableKwargs = dict[str, str | int | bool | object]
        PyArrowWriteTableKwargs = dict[str, str | int | bool | object]
        CliDataDict = dict[str, FlextTypes.Core.JsonValue]
        CliCommandData = dict[str, FlextTypes.Core.JsonValue]
        CliCommandResult = dict[
            str, str | int | float | bool | list[object] | dict[str, object] | None
        ]
        CliCommandArgs = dict[str, FlextTypes.Core.JsonValue]
        CliFormatData = dict[str, FlextTypes.Core.JsonValue]
        CliConfigData = dict[str, FlextTypes.Core.JsonValue]
        AuthConfigData = dict[str, str | int | bool]
        DebugInfoData = dict[
            str,
            str
            | int
            | float
            | bool
            | list[object]
            | dict[str, object]
            | list[str]
            | dict
            | None,
        ]
        ErrorList = list[str]
        FileList = list[str]
        CsvData = list[dict[str, str]]
        ConnectivityInfo = dict[str, str]
        TableHeaders = list[str]
        TableRows = list[list[str]]
        PathInfoList = list[dict[str, FlextTypes.Core.JsonValue]]

    class PandasTypes:
        """Pandas-specific type definitions for CLI data processing."""

        PandasToCsvKwargs = dict[str, str | int | bool | object]

    # =========================================================================
    # CLI AUTH TYPES - Authentication and authorization types
    # =========================================================================

    class Auth:
        """CLI authentication complex types."""

        PermissionList = list[str]
        RoleList = list[str]
        SessionData = dict[str, str | int | bool]
        CredentialsData = dict[str, FlextTypes.Core.JsonValue]
        UserData = dict[str, FlextTypes.Core.JsonValue]
        AuthResult = dict[str, FlextTypes.Core.JsonValue]
        UserList = list[dict[str, FlextTypes.Core.JsonValue]]

    # =========================================================================
    # CLI HTTP TYPES - HTTP-related types
    # =========================================================================

    class Http:
        """CLI HTTP complex types."""

        Headers = dict[str, str]
        ResponseData = dict[str, object]
        RequestData = dict[str, object]

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
        CliProjectConfig = dict[str, FlextTypes.Core.ConfigValue]
        CommandLineConfig = dict[str, str | int | bool | list[str]]
        InteractiveConfig = dict[
            str, bool | str | dict[str, FlextTypes.Core.ConfigValue]
        ]
        OutputConfig = dict[
            str, FlextTypes.Output.OutputFormat | FlextTypes.Core.ConfigValue
        ]


# =============================================================================
# PUBLIC API EXPORTS - CLI TypeVars and types
# =============================================================================

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
