"""FLEXT CLI Types - Hierarchical type system inheriting from FlextCoreTypes.

This module implements the FlextCliTypes class following the Flext[Area][Module] pattern,
inheriting from FlextCoreTypes and providing CLI-specific type extensions with all
current functionality available as internal aliases.

English code with Portuguese comments following FLEXT standards.
"""

from __future__ import annotations

from collections.abc import Callable
from enum import StrEnum
from pathlib import Path
from typing import Protocol

import click
from flext_core import E, F, FlextCoreTypes, FlextEntityId, FlextResult, P, R
from rich.table import Table

# Move FlextCliOutputFormat here to avoid circular dependencies


class FlextCliOutputFormat(StrEnum):
    """CLI output format enumeration."""

    TABLE = "table"
    JSON = "json"
    YAML = "yaml"
    CSV = "csv"
    PLAIN = "plain"


class CommandType(StrEnum):
    """CLI command type enumeration."""

    SYSTEM = "system"
    INTERACTIVE = "interactive"
    BATCH = "batch"


class CommandStatus(StrEnum):
    """CLI command status enumeration."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class SessionStatus(StrEnum):
    """CLI session status enumeration."""

    ACTIVE = "active"
    IDLE = "idle"
    SUSPENDED = "suspended"
    TERMINATED = "terminated"
    ERROR = "error"


class PluginStatus(StrEnum):
    """CLI plugin status enumeration."""

    INACTIVE = "inactive"
    UNLOADED = "unloaded"
    LOADING = "loading"
    LOADED = "loaded"
    ACTIVE = "active"
    DISABLED = "disabled"
    ERROR = "error"


# FlextCliOutputFormat moved to models.py to avoid circular import


# =============================================================================
# FLEXT CLI TYPES - Main hierarchical class inheriting from FlextCoreTypes
# =============================================================================


class FlextCliTypes(FlextCoreTypes):
    """CLI-specific type system inheriting from FlextCoreTypes.

    This class implements the Flext[Area][Module] pattern, providing hierarchical
    inheritance from flext-core types while adding CLI-specific type extensions.
    All current functionality is preserved through internal aliases.

    Herança hierárquica de FlextCoreTypes conforme padrão FLEXT.
    Mantém compatibilidade completa através de aliases internos.
    """

    # =============================================================================
    # CLI-SPECIFIC TYPE CATEGORIES - Extending core types
    # =============================================================================

    class Cli:
        """CLI-specific type definitions and aliases."""

        # Command-related types
        CommandType = CommandType
        CommandStatus = CommandStatus
        SessionStatus = SessionStatus
        PluginStatus = PluginStatus
        OutputFormat = FlextCliOutputFormat

        # Entity identifiers - aliases para compatibilidade
        EntityId = FlextEntityId
        TUserId = str

        # Configuration types - usando FlextCoreTypes como base
        ConfigDict = FlextCoreTypes.Core.Dict
        ConfigData = FlextCoreTypes.Core.Dict
        ConfigResult = FlextResult[dict[str, object]]
        SettingsDict = FlextCoreTypes.Core.Dict
        EnvironmentDict = dict[str, str]  # Environment variables

        # Click integration types
        ClickContext = click.Context
        ClickCommand = click.Command
        ClickGroup = click.Group
        ClickParameter = click.Parameter
        ClickPath = click.Path

        # Rich integration types
        RichTable = Table
        ConsoleProtocol = Protocol

        # Processing types
        ProcessingResults = dict[str, object]
        SetupResults = dict[str, object]
        CommandResult = dict[str, object]

        # Handler types - CLI command and result handlers
        CommandArgs = dict[str, object]  # Command arguments
        CommandOptions = dict[str, object]  # Command options
        CommandHandler = Callable[[dict[str, object]], object]
        ResultHandler = Callable[[object], FlextResult[object]]

        # Validation types
        ValidationResult = FlextResult[bool]
        ValidationError = FlextResult[None]

        # File operation types
        PathType = Path | str
        FileContent = str | bytes
        FileResult = FlextResult[str]
        FlextCliFileHandler = object  # File handler placeholder
        ExistingDir = Path  # Path that must exist as directory
        ExistingFile = Path  # Path that must exist as file
        NewFile = Path  # Path for new file

        # Data types - CLI data handling
        DataType = FlextCoreTypes.Core.Data
        OutputData = str | dict[str, object] | list[object]

        # URL types
        URL = str  # URL strings
        URLType = str  # URL type alias

        # CLI specific types
        ErrorMessage = str  # Error message type
        ExitCode = int  # Process exit code
        PositiveInt = int  # Positive integer constraint
        PositiveIntType = int  # Positive integer type alias
        ProfileType = str  # Profile name type

    # =============================================================================
    # INTERNAL ALIASES - All current functionality preserved
    # =============================================================================

    @classmethod
    def get_command_type(cls) -> type[CommandType]:
        """Get CLI command type enumeration.

        Returns:
            CommandType enumeration class

        """
        return cls.Cli.CommandType

    @classmethod
    def get_command_status(cls) -> type[CommandStatus]:
        """Get CLI command status enumeration.

        Returns:
            CommandStatus enumeration class

        """
        return cls.Cli.CommandStatus

    @classmethod
    def get_session_status(cls) -> type[SessionStatus]:
        """Get CLI session status enumeration.

        Returns:
            SessionStatus enumeration class

        """
        return cls.Cli.SessionStatus

    @classmethod
    def get_plugin_status(cls) -> type[PluginStatus]:
        """Get CLI plugin status enumeration.

        Returns:
            PluginStatus enumeration class

        """
        return cls.Cli.PluginStatus

    @classmethod
    def get_output_format(cls) -> type[FlextCliOutputFormat]:
        """Get CLI output format enumeration.

        Returns:
            FlextCliOutputFormat enumeration class

        """
        return cls.Cli.OutputFormat

    @classmethod
    def create_config_dict(cls, **kwargs: object) -> dict[str, object]:
        """Create configuration dictionary with type safety.

        Args:
            **kwargs: Configuration parameters

        Returns:
            Type-safe configuration dictionary

        """
        return dict(kwargs)

    @classmethod
    def create_processing_result(
        cls, *, success: bool, data: object = None, error: str | None = None
    ) -> dict[str, object]:
        """Create processing result dictionary.

        Args:
            success: Operation success status
            data: Result data
            error: Error message if any

        Returns:
            Processing result dictionary

        """
        return {
            "success": success,
            "data": data,
            "error": error,
        }

    @classmethod
    def validate_entity_id(cls, entity_id: str) -> FlextResult[bool]:
        """Validate entity ID format.

        Args:
            entity_id: Entity ID to validate

        Returns:
            Validation result

        """
        if not entity_id or not entity_id.strip():
            return FlextResult[bool].fail("Entity ID cannot be empty")
        is_valid = True
        return FlextResult.ok(is_valid)


# =============================================================================
# BACKWARD COMPATIBILITY ALIASES - All current exports preserved
# =============================================================================

# Enumerations - manter compatibilidade total
FlextCliCommandType = CommandType
FlextCliCommandStatus = CommandStatus
FlextCliSessionStatus = SessionStatus
FlextCliPluginStatus = PluginStatus

# Type aliases - preservar aliases existentes
EntityId = FlextCliTypes.Cli.EntityId
TUserId = FlextCliTypes.Cli.TUserId
type ConfigDict = dict[str, object]
ConfigData = FlextCliTypes.Cli.ConfigData
SettingsDict = FlextCliTypes.Cli.SettingsDict
ProcessingResults = FlextCliTypes.Cli.ProcessingResults
SetupResults = FlextCliTypes.Cli.SetupResults
CommandResult = FlextCliTypes.Cli.CommandResult
ValidationResult = FlextCliTypes.Cli.ValidationResult
PathType = FlextCliTypes.Cli.PathType
FileContent = FlextCliTypes.Cli.FileContent
FileResult = FlextCliTypes.Cli.FileResult

# Click and Rich types - manter aliases existentes
ClickContext = FlextCliTypes.Cli.ClickContext
ClickCommand = FlextCliTypes.Cli.ClickCommand
ClickGroup = FlextCliTypes.Cli.ClickGroup
ClickParameter = FlextCliTypes.Cli.ClickParameter
ClickPath = FlextCliTypes.Cli.ClickPath
RichTable = FlextCliTypes.Cli.RichTable

# Handler types - preservar aliases
CommandArgs = FlextCliTypes.Cli.CommandArgs
CommandOptions = FlextCliTypes.Cli.CommandOptions
CommandHandler = FlextCliTypes.Cli.CommandHandler
ResultHandler = FlextCliTypes.Cli.ResultHandler

# Type aliases - Python 3.13+ type syntax
type FlextCliDataType = str | dict[str, object] | list[object] | object
type OutputData = str | dict[str, object] | list[object]

# URL types
type URL = str
type URLType = str

# Configuration and environment types
type ConfigResult = FlextResult[dict[str, object]]
type EnvironmentDict = dict[str, str]

# File operation types
type FlextCliFileHandler = object
type ExistingDir = Path
type ExistingFile = Path
type NewFile = Path

# CLI specific types
type ErrorMessage = str
type ExitCode = int
type PositiveInt = int
type PositiveIntType = int
type ProfileType = str

# Legacy FlextTypes compatibility
FlextTypes = FlextCoreTypes
CoreFlextTypes = FlextCoreTypes

# =============================================================================
# EXPORTS - Comprehensive type system with backward compatibility
# =============================================================================

__all__ = [
    "URL",
    "ClickCommand",
    "ClickContext",
    "ClickGroup",
    "ClickParameter",
    "ClickPath",
    "CommandArgs",
    "CommandHandler",
    "CommandOptions",
    "CommandResult",
    "CommandStatus",
    "CommandType",
    "ConfigData",
    "ConfigDict",
    "ConfigResult",
    "CoreFlextTypes",
    "E",
    "EntityId",
    "EnvironmentDict",
    "ErrorMessage",
    "ExistingDir",
    "ExistingFile",
    "ExitCode",
    "F",
    "FileContent",
    "FileResult",
    "FlextCliCommandStatus",
    "FlextCliCommandType",
    "FlextCliDataType",
    "FlextCliFileHandler",
    "FlextCliOutputFormat",
    "FlextCliPluginStatus",
    "FlextCliSessionStatus",
    "FlextCliTypes",
    "FlextTypes",
    "NewFile",
    "OutputData",
    "P",
    "PathType",
    "PluginStatus",
    "PositiveInt",
    "PositiveIntType",
    "ProcessingResults",
    "ProfileType",
    "R",
    "ResultHandler",
    "RichTable",
    "SessionStatus",
    "SettingsDict",
    "SetupResults",
    "TUserId",
    "URLType",
    "ValidationResult",
]
