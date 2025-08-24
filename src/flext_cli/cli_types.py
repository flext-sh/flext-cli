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

# =============================================================================
# CLI-SPECIFIC ENUMERATIONS
# =============================================================================

class CommandType(StrEnum):
    """CLI command type enumeration."""

    SYSTEM = "system"
    USER = "user"
    PLUGIN = "plugin"
    INTERACTIVE = "interactive"
    BATCH = "batch"
    DEBUG = "debug"
    PIPELINE = "pipeline"
    DATA = "data"
    CONFIG = "config"
    AUTH = "auth"
    MONITORING = "monitoring"


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


class FlextCliOutputFormat(StrEnum):
    """CLI output format enumeration."""

    JSON = "json"
    CSV = "csv"
    YAML = "yaml"
    TABLE = "table"
    PLAIN = "plain"


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
        SettingsDict = FlextCoreTypes.Core.Dict

        # Click integration types
        ClickContext = click.Context
        ClickCommand = click.Command
        ClickGroup = click.Group
        ClickParameter = click.Parameter

        # Rich integration types
        RichTable = Table
        ConsoleProtocol = Protocol

        # Processing types
        ProcessingResults = dict[str, object]
        SetupResults = dict[str, object]
        CommandResult = dict[str, object]

        # Handler types - CLI command and result handlers
        CommandHandler = Callable[[dict[str, object]], object]
        ResultHandler = Callable[[object], FlextResult[object]]

        # Validation types
        ValidationResult = FlextResult[bool]
        ValidationError = FlextResult[None]

        # File operation types
        PathType = Path | str
        FileContent = str | bytes
        FileResult = FlextResult[str]

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
        cls,
        *,
        success: bool,
        data: object = None,
        error: str | None = None
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
ConfigDict = FlextCliTypes.Cli.ConfigDict
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
RichTable = FlextCliTypes.Cli.RichTable

# Handler types - preservar aliases
CommandHandler = FlextCliTypes.Cli.CommandHandler
ResultHandler = FlextCliTypes.Cli.ResultHandler

# Legacy FlextTypes compatibility
FlextTypes = FlextCoreTypes
CoreFlextTypes = FlextCoreTypes

# =============================================================================
# EXPORTS - Comprehensive type system with backward compatibility
# =============================================================================

__all__ = [
    "ClickCommand",
    "ClickContext",
    "ClickGroup",
    "ClickParameter",
    "CommandHandler",
    "CommandResult",
    "CommandStatus",
    "CommandType",
    "ConfigData",
    "ConfigDict",
    "CoreFlextTypes",
    "E",
    "EntityId",
    "F",
    "FileContent",
    "FileResult",
    "FlextCliCommandStatus",
    "FlextCliCommandType",
    "FlextCliOutputFormat",
    "FlextCliPluginStatus",
    "FlextCliSessionStatus",
    "FlextCliTypes",
    "FlextTypes",
    "P",
    "PathType",
    "PluginStatus",
    "ProcessingResults",
    "R",
    "ResultHandler",
    "RichTable",
    "SessionStatus",
    "SettingsDict",
    "SetupResults",
    "TUserId",
    "ValidationResult",
]
