"""FLEXT CLI Types - Complete type system consolidating all CLI types.

This module consolidates all CLI-related types from multiple scattered files
into a single, well-organized module following PEP8 naming conventions.

Consolidated from:
    - types.py (root level)
    - core/types.py (Click parameter types)
    - Various type definitions across modules

Design Principles:
    - PEP8 naming: cli_types.py (not types.py for clarity)
    - Single source of truth for all CLI types
    - Extends flext-core types where appropriate
    - Type safety with Python 3.13+ features
    - Zero duplication

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Callable
from enum import StrEnum
from pathlib import Path
from typing import Any, Literal, Protocol, TypeAlias, TypeVar

import click
from flext_core import FlextEntityId, FlextResult
from rich.table import Table

# =============================================================================
# CONSOLIDATED ENUMS - From multiple files
# =============================================================================


class CommandType(StrEnum):
    """CLI command type enumeration."""

    SYSTEM = "system"
    USER = "user"
    PLUGIN = "plugin"
    INTERACTIVE = "interactive"
    BATCH = "batch"
    DEBUG = "debug"


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

    UNLOADED = "unloaded"
    LOADING = "loading"
    LOADED = "loaded"
    ACTIVE = "active"
    DISABLED = "disabled"
    ERROR = "error"


class OutputFormat(StrEnum):
    """CLI output format enumeration."""

    TEXT = "text"
    JSON = "json"
    XML = "xml"
    CSV = "csv"
    YAML = "yaml"
    TABLE = "table"


# =============================================================================
# TYPE ALIASES - Consolidated from multiple modules
# =============================================================================

# Entity identifiers
EntityId: TypeAlias = FlextEntityId
TUserId: TypeAlias = str

# Configuration types
ConfigDict: TypeAlias = dict[str, Any]
EnvironmentDict: TypeAlias = dict[str, str]

# Command execution types
CommandArgs: TypeAlias = list[str]
CommandOptions: TypeAlias = dict[str, Any]
ExitCode: TypeAlias = int

# Output types
OutputData: TypeAlias = str | dict[str, Any] | list[Any]
ErrorMessage: TypeAlias = str

# Path types
WorkingDirectory: TypeAlias = Path
ConfigPath: TypeAlias = Path

# Time types
TimeoutSeconds: TypeAlias = int
DurationSeconds: TypeAlias = float

# Plugin types
PluginName: TypeAlias = str
EntryPoint: TypeAlias = str
PluginVersion: TypeAlias = str

# Session types
SessionId: TypeAlias = str
SessionData: TypeAlias = dict[str, Any]

# CLI context types
ContextParams: TypeAlias = dict[str, Any]
UserInput: TypeAlias = str


# =============================================================================
# CLICK PARAMETER TYPES - From core/types.py
# =============================================================================


class PositiveIntType(click.ParamType):
    """Click parameter type for positive integers."""

    name = "positive_int"

    def convert(
        self,
        value: Any,
        param: click.Parameter | None,
        ctx: click.Context | None,
    ) -> int:
        """Convert and validate positive integer."""
        if isinstance(value, int):
            if value > 0:
                return value
            self.fail(f"Value must be positive, got {value}", param, ctx)

        if isinstance(value, str):
            try:
                int_val = int(value)
                if int_val > 0:
                    return int_val
                self.fail(f"Value must be positive, got {int_val}", param, ctx)
            except ValueError:
                self.fail(f"'{value}' is not a valid integer", param, ctx)

        self.fail(f"'{value}' is not a valid positive integer", param, ctx)


class URLType(click.ParamType):
    """Click parameter type for URL validation."""

    name = "url"

    def convert(
        self,
        value: Any,
        param: click.Parameter | None,
        ctx: click.Context | None,
    ) -> str:
        """Convert and validate URL."""
        if not isinstance(value, str):
            self.fail(f"URL must be a string, got {type(value).__name__}", param, ctx)

        # Basic URL validation
        if not value.startswith(("http://", "https://")):
            self.fail(f"URL must start with http:// or https://, got '{value}'", param, ctx)

        if not value.count("://") == 1:
            self.fail(f"Invalid URL format: '{value}'", param, ctx)

        return value


class PathType(click.ParamType):
    """Click parameter type for path validation."""

    name = "path"

    def __init__(self, exists: bool = False, dir_okay: bool = True, file_okay: bool = True):
        """Initialize path type with validation options."""
        self.exists = exists
        self.dir_okay = dir_okay
        self.file_okay = file_okay

    def convert(
        self,
        value: Any,
        param: click.Parameter | None,
        ctx: click.Context | None,
    ) -> Path:
        """Convert and validate path."""
        if isinstance(value, Path):
            path = value
        elif isinstance(value, str):
            path = Path(value)
        else:
            self.fail(f"Path must be string or Path, got {type(value).__name__}", param, ctx)

        if self.exists and not path.exists():
            self.fail(f"Path does not exist: '{path}'", param, ctx)

        if self.exists:
            if path.is_file() and not self.file_okay:
                self.fail(f"Path is a file but files not allowed: '{path}'", param, ctx)

            if path.is_dir() and not self.dir_okay:
                self.fail(f"Path is a directory but directories not allowed: '{path}'", param, ctx)

        return path


class ProfileType(click.ParamType):
    """Click parameter type for profile name validation."""

    name = "profile"

    def convert(
        self,
        value: Any,
        param: click.Parameter | None,
        ctx: click.Context | None,
    ) -> str:
        """Convert and validate profile name."""
        if not isinstance(value, str):
            self.fail(f"Profile must be a string, got {type(value).__name__}", param, ctx)

        # Validate profile name format
        if not value.replace("_", "a").replace("-", "a").isalnum():
            self.fail(
                f"Profile name must contain only alphanumeric, underscore, and dash characters, got '{value}'",
                param,
                ctx,
            )

        if len(value.strip()) == 0:
            self.fail("Profile name cannot be empty", param, ctx)

        return value.strip()


# =============================================================================
# ADVANCED TYPE DEFINITIONS - From advanced_types.py consolidation
# =============================================================================

# Type Variables for Generics
T = TypeVar("T")
U = TypeVar("U")
K = TypeVar("K")
V = TypeVar("V")

# Enhanced FlextResult alias with common patterns
type FlextCliResult[T] = FlextResult[T]
type FlextCliOperationResult[T] = FlextResult[T]
type FlextCliValidationResult = FlextResult[bool]
type FlextCliDataResult = FlextResult[dict[str, str | int | float | bool | None]]
type FlextCliFileResult = FlextResult[str]
type FlextCliTableResult = FlextResult[Table]

# Common Data Types (eliminates dict[str, Any] boilerplate)
type FlextCliDataDict = dict[str, str | int | float | bool | None]
type FlextCliConfigDict = dict[str, str | int | float | bool | None]
type FlextCliMetadataDict = dict[str, str | int | float | bool]
type FlextCliErrorDict = dict[str, str]

# File and Path Types
type FlextCliPathLike = str | Path
type FlextCliFilePath = str | Path
type FlextCliDirectoryPath = str | Path
type FlextCliOptionalPath = str | Path | None

# Operation Types - using generic types
type FlextCliOperation[T] = Callable[[], FlextCliResult[T]]
type FlextCliValidator[T] = Callable[[T], FlextCliValidationResult]
type FlextCliTransformer[T, U] = Callable[[T], FlextCliResult[U]]
type FlextCliProcessor = Callable[[FlextCliDataDict], FlextCliDataResult]

# Literal Types for Enhanced Type Safety
type FlextCliOutputFormat = Literal["json", "yaml", "toml", "csv", "table", "plain"]
type FlextCliLogLevel = Literal["debug", "info", "warning", "error", "critical"]
type FlextCliValidationType = Literal["email", "url", "path", "file", "uuid", "port"]
type FlextCliStatusType = Literal["success", "error", "warning", "info", "pending"]
type FlextCliOperationType = Literal["create", "read", "update", "delete", "process", "validate"]

# Collection Types
type FlextCliDataList = list[FlextCliDataDict]
type FlextCliStringList = list[str]
type FlextCliPathList = list[FlextCliPathLike]
type FlextCliOperationList[T] = list[FlextCliOperation[T]]

# Configuration Types
type FlextCliSettings = dict[str, str | int | float | bool | None]
type FlextCliEnvironment = dict[str, str]
type FlextCliArguments = dict[str, str | int | float | bool | None]

# Specialized Result Types for Common Operations
type FlextCliLoadResult = FlextResult[FlextCliDataDict]
type FlextCliSaveResult = FlextResult[None]
type FlextCliValidateResult = FlextResult[bool]
type FlextCliProcessResult = FlextResult[FlextCliDataDict]
type FlextCliExecuteResult = FlextResult[str]
type FlextCliRenderResult = FlextResult[Table]

# Callback Types
type FlextCliSuccessCallback[T] = Callable[[T], None]
type FlextCliErrorCallback = Callable[[str], None]
type FlextCliProgressCallback = Callable[[int, int], None]

# Factory Types
type FlextCliEntityFactory[T] = Callable[[FlextCliConfigDict], FlextCliResult[T]]
type FlextCliServiceFactory[T] = Callable[[FlextCliConfigDict], T]
type FlextCliValidatorFactory = Callable[[str], FlextCliSimpleValidatorProtocol]

# Command Pattern Types
type FlextCliCommand[T] = Callable[[], FlextCliResult[T]]
type FlextCliCommandRegistry[T] = dict[str, FlextCliCommand[T]]
type FlextCliCommandPipeline[T] = list[FlextCliCommand[T]]

# Legacy CLI-specific result types using FlextResult (for backward compatibility)
CommandResult: TypeAlias = FlextResult[OutputData]
ValidationResult: TypeAlias = FlextResult[bool]
ConfigResult: TypeAlias = FlextResult[ConfigDict]
PluginResult: TypeAlias = FlextResult[PluginName]
SessionResult: TypeAlias = FlextResult[SessionId]
ConfigurationResult: TypeAlias = FlextResult[ConfigDict]
ProcessingResult: TypeAlias = FlextResult[OutputData]
FileOperationResult: TypeAlias = FlextResult[Path]
NetworkResult: TypeAlias = FlextResult[dict[str, Any]]


# =============================================================================
# PROTOCOL DEFINITIONS - Interface types for dependency injection
# =============================================================================

class FlextCliDataProcessor(Protocol):
    """Protocol for data processing operations - enables dependency injection."""

    def process(self, data: FlextCliDataDict) -> FlextCliDataResult:
        """Process data and return result."""
        ...

    def validate(self, data: FlextCliDataDict) -> FlextCliValidationResult:
        """Validate data structure."""
        ...


class FlextCliFileHandler(Protocol):
    """Protocol for file operations - standardizes file handling interface."""

    def load_file(self, path: FlextCliFilePath) -> FlextCliDataResult:
        """Load file and return parsed data."""
        ...

    def save_file(self, data: FlextCliDataDict, path: FlextCliFilePath) -> FlextCliResult[None]:
        """Save data to file."""
        ...


class FlextCliSimpleValidatorProtocol(Protocol):
    """Protocol for simple validation operations - standardizes basic validation interface."""

    def validate(self, value: object) -> FlextCliValidationResult:
        """Validate value and return result."""
        ...

    def get_error_message(self) -> str:
        """Get human-readable error message."""
        ...


class FlextCliUIRenderer(Protocol):
    """Protocol for UI rendering - standardizes user interface operations."""

    def render_table(self, data: FlextCliDataList, title: str) -> FlextCliTableResult:
        """Render data as table."""
        ...

    def show_progress[T](self, items: list[T], operation_name: str) -> FlextCliResult[list[T]]:
        """Show progress for operation."""
        ...

    def confirm_action(self, message: str, *, default: bool = False) -> FlextCliResult[bool]:
        """Get user confirmation."""
        ...


class FlextCliConfigProvider(Protocol):
    """Protocol for configuration management - standardizes config access."""

    def get_value(self, key: str, *, default: str | int | bool | None = None) -> str | int | bool | None:
        """Get configuration value."""
        ...

    def set_value(self, key: str, *, value: str | int | bool) -> None:
        """Set configuration value."""
        ...

    def load_from_file(self, path: FlextCliFilePath) -> FlextCliResult[None]:
        """Load configuration from file."""
        ...


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Basic enumerations
    "CommandType",
    "CommandStatus",
    "SessionStatus",
    "PluginStatus",
    "OutputFormat",
    # Basic type aliases
    "EntityId",
    "TUserId",
    "ConfigDict",
    "EnvironmentDict",
    "CommandArgs",
    "CommandOptions",
    "ExitCode",
    "OutputData",
    "ErrorMessage",
    "WorkingDirectory",
    "ConfigPath",
    "TimeoutSeconds",
    "DurationSeconds",
    "PluginName",
    "EntryPoint",
    "PluginVersion",
    "SessionId",
    "SessionData",
    "ContextParams",
    "UserInput",
    # Click parameter types
    "PositiveIntType",
    "URLType",
    "PathType",
    "ProfileType",
    # Legacy result types (for backward compatibility)
    "CommandResult",
    "ValidationResult",
    "ConfigResult",
    "PluginResult",
    "SessionResult",
    "ConfigurationResult",
    "ProcessingResult",
    "FileOperationResult",
    "NetworkResult",
    # Type variables
    "T", "U", "K", "V",
    # Advanced FlextResult types
    "FlextCliResult",
    "FlextCliOperationResult",
    "FlextCliValidationResult",
    "FlextCliDataResult",
    "FlextCliFileResult",
    "FlextCliTableResult",
    # Data types
    "FlextCliDataDict",
    "FlextCliConfigDict",
    "FlextCliMetadataDict",
    "FlextCliErrorDict",
    # Path types
    "FlextCliPathLike",
    "FlextCliFilePath",
    "FlextCliDirectoryPath",
    "FlextCliOptionalPath",
    # Operation types
    "FlextCliOperation",
    "FlextCliValidator",
    "FlextCliTransformer",
    "FlextCliProcessor",
    # Literal types
    "FlextCliOutputFormat",
    "FlextCliLogLevel",
    "FlextCliValidationType",
    "FlextCliStatusType",
    "FlextCliOperationType",
    # Collection types
    "FlextCliDataList",
    "FlextCliStringList",
    "FlextCliPathList",
    "FlextCliOperationList",
    # Configuration types
    "FlextCliSettings",
    "FlextCliEnvironment",
    "FlextCliArguments",
    # Specialized result types
    "FlextCliLoadResult",
    "FlextCliSaveResult",
    "FlextCliValidateResult",
    "FlextCliProcessResult",
    "FlextCliExecuteResult",
    "FlextCliRenderResult",
    # Callback types
    "FlextCliSuccessCallback",
    "FlextCliErrorCallback",
    "FlextCliProgressCallback",
    # Factory types
    "FlextCliEntityFactory",
    "FlextCliServiceFactory",
    "FlextCliValidatorFactory",
    # Command types
    "FlextCliCommand",
    "FlextCliCommandRegistry",
    "FlextCliCommandPipeline",
    # Protocol types
    "FlextCliDataProcessor",
    "FlextCliFileHandler",
    "FlextCliSimpleValidatorProtocol",
    "FlextCliUIRenderer",
    "FlextCliConfigProvider",
]
