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

        type CommandDefinition = dict[str, str | list[str] | dict[str, object]]
        type CommandPipeline = list[dict[str, FlextTypes.Core.JsonValue]]
        type CommandRegistry = dict[str, CommandDefinition]
        type CommandContext = dict[str, FlextTypes.Core.JsonValue | object]
        type CommandResult = dict[str, FlextTypes.Core.JsonValue | bool]
        type CommandMetadata = dict[str, str | int | list[str]]

    # =========================================================================
    # CLI CONFIGURATION TYPES - Complex configuration types
    # =========================================================================

    class Configuration:
        """CLI configuration complex types."""

        type CliConfigSchema = dict[str, dict[str, FlextTypes.Core.ConfigValue]]
        type ProfileConfiguration = dict[str, FlextTypes.Core.ConfigDict]
        type EnvironmentConfig = dict[
            str, FlextTypes.Core.ConfigValue | dict[str, object]
        ]
        type SessionConfiguration = dict[str, FlextTypes.Core.JsonValue | bool]
        type AuthenticationConfig = dict[str, str | int | bool | list[str]]

    # =========================================================================
    # CLI OUTPUT TYPES - Complex output formatting types
    # =========================================================================

    class Output:
        """CLI output formatting complex types."""

        type FormatterConfig = dict[
            str, FlextTypes.Output.OutputFormat | dict[str, str]
        ]
        type TableConfiguration = dict[str, str | int | list[str] | bool]
        type ProgressBarConfig = dict[str, str | int | bool]
        type OutputPipeline = list[dict[str, FlextTypes.Output.OutputFormat | object]]
        type RenderingOptions = dict[str, bool | str | int | list[str]]

    # =========================================================================
    # CLI PROCESSING TYPES - Complex processing types
    # =========================================================================

    class Processing:
        """CLI processing complex types."""

        type BatchOperation = dict[str, list[dict[str, FlextTypes.Core.JsonValue]]]
        type PipelineDefinition = list[dict[str, str | dict[str, object]]]
        type WorkflowConfiguration = dict[
            str, FlextTypes.Processing.ProcessingStatus | object
        ]
        type TaskConfiguration = dict[str, FlextTypes.Core.JsonValue | bool]

    # =========================================================================
    # CLI DATA TYPES - Complex data processing types
    # =========================================================================

    class Data:
        """CLI data processing complex types."""

        type PandasReadCsvKwargs = dict[str, str | int | bool | object]
        type PyArrowReadTableKwargs = dict[str, str | int | bool | object]
        type PyArrowWriteTableKwargs = dict[str, str | int | bool | object]
        type CliDataDict = dict[str, FlextTypes.Core.JsonValue]
        type CliCommandData = dict[str, FlextTypes.Core.JsonValue]
        type CliCommandResult = dict[str, FlextTypes.Core.JsonValue | bool]
        type CliCommandArgs = dict[str, FlextTypes.Core.JsonValue]
        type CliFormatData = dict[str, FlextTypes.Core.JsonValue]
        type CliConfigData = dict[str, FlextTypes.Core.JsonValue]
        type AuthConfigData = dict[str, str | int | bool]
        type DebugInfoData = dict[str, FlextTypes.Core.JsonValue | bool]


# Module-level type aliases for direct access
PandasReadCsvKwargs = FlextCliTypes.Data.PandasReadCsvKwargs
PyArrowReadTableKwargs = FlextCliTypes.Data.PyArrowReadTableKwargs
PyArrowWriteTableKwargs = FlextCliTypes.Data.PyArrowWriteTableKwargs


# =============================================================================
# PUBLIC API EXPORTS - CLI TypeVars and types
# =============================================================================

__all__: list[str] = [
    # CLI Types class
    "FlextCliTypes",
    # CLI-specific TypeVars
    "TCliCommand",
    "TCliConfig",
    "TCliContext",
    "TCliFormatter",
    "TCliOutput",
    "TCliPlugin",
    "TCliResult",
    "TCliSession",
]
