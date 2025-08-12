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
from typing import Literal, Protocol, TypeVar

import click

try:  # pragma: no cover - import bridge
    from flext_core import FlextEntityId, FlextResult  # type: ignore
except Exception:  # pragma: no cover
    FlextEntityId = str  # type: ignore[assignment]
    class FlextResult:  # type: ignore[no-redef]
        def __class_getitem__(cls, _item):
            return cls

        def __init__(self, success: bool, data: object | None = None, error: str | None = None) -> None:
            self.success = success
            self.is_success = success
            self.is_failure = not success
            self.data = data
            self.error = error

        @staticmethod
        def ok(data: object | None) -> FlextResult:
            return FlextResult(True, data, None)

        @staticmethod
        def fail(error: str) -> FlextResult:
            return FlextResult(False, None, error)

        def unwrap(self) -> object:
            if not self.success:
                raise RuntimeError(self.error or "unwrap failed")
            return self.data
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

    UNLOADED = "unloaded"
    LOADING = "loading"
    LOADED = "loaded"
    ACTIVE = "active"
    DISABLED = "disabled"
    ERROR = "error"


class OutputFormat(StrEnum):
    """CLI output format enumeration."""

    JSON = "json"
    CSV = "csv"
    YAML = "yaml"
    TABLE = "table"
    PLAIN = "plain"


# =============================================================================
# TYPE ALIASES - Consolidated from multiple modules
# =============================================================================

# Entity identifiers
type EntityId = FlextEntityId
type TUserId = str

# Configuration types
type ConfigDict = dict[str, object]
type EnvironmentDict = dict[str, str]

# Command execution types
type CommandArgs = list[str]
type CommandOptions = dict[str, object]
type ExitCode = int

# Output types
type OutputData = str | dict[str, object] | list[object]
type ErrorMessage = str

# Path types
type WorkingDirectory = Path
type ConfigPath = Path

# Time types
type TimeoutSeconds = int
type DurationSeconds = float

# Plugin types
type PluginName = str
type EntryPoint = str
type PluginVersion = str

# Session types
type SessionId = str
type SessionData = dict[str, object]

# CLI context types
type ContextParams = dict[str, object]
type UserInput = str


# =============================================================================
# CLICK PARAMETER TYPES - From core/types.py
# =============================================================================


class PositiveIntType(click.ParamType):
    """Click parameter type for positive integers."""

    name = "positive_int"

    def convert(
        self,
        value: object,
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

        # Fall back to explicit raise to satisfy linters
        msg = f"'{value}' is not a valid positive integer"
        raise click.BadParameter(msg)


class URLType(click.ParamType):
    """Click parameter type for URL validation."""

    name = "url"

    def convert(
        self,
        value: object,
        param: click.Parameter | None,
        ctx: click.Context | None,
    ) -> str:
        """Convert and validate URL."""
        if not isinstance(value, str):
            self.fail(f"URL must be a string, got {type(value).__name__}", param, ctx)

        # Basic URL validation
        if not value.startswith(("http://", "https://", "ftp://")):
            self.fail(
                f"URL must start with http://, https://, or ftp://, got '{value}'", param, ctx,
            )

        # Require scheme and non-empty netloc (basic check)
        parts = value.split("://", 1)
        if len(parts) != 2 or parts[1].strip() == "":
            self.fail(f"Invalid URL format: '{value}'", param, ctx)

        return value


class PathType(click.ParamType):
    """Click parameter type for path validation."""

    name = "path"

    def __init__(
        self, *, exists: bool = False, dir_okay: bool = True, file_okay: bool = True,
    ) -> None:
        """Initialize path type with validation options."""
        self.exists = exists
        self.dir_okay = dir_okay
        self.file_okay = file_okay

    def convert(
        self,
        value: object,
        param: click.Parameter | None,
        ctx: click.Context | None,
    ) -> Path:
        """Convert and validate path."""
        if isinstance(value, Path):
            path = value
        elif isinstance(value, str):
            path = Path(value)
        else:
            self.fail(
                f"Path must be string or Path, got {type(value).__name__}", param, ctx,
            )

        if self.exists and not path.exists():
            self.fail(f"Path does not exist: '{path}'", param, ctx)

        if self.exists:
            if path.is_file() and not self.file_okay:
                self.fail(f"Path is a file but files not allowed: '{path}'", param, ctx)

            if path.is_dir() and not self.dir_okay:
                self.fail(
                    f"Path is a directory but directories not allowed: '{path}'",
                    param,
                    ctx,
                )

        return path


class ProfileType(click.ParamType):
    """Click parameter type for profile name validation."""

    name = "profile"

    def convert(
        self,
        value: object,
        param: click.Parameter | None,
        ctx: click.Context | None,
    ) -> str:
        """Convert and validate profile name."""
        if not isinstance(value, str):
            self.fail(
                f"Profile must be a string, got {type(value).__name__}", param, ctx,
            )

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
type FlextCliOperationType = Literal[
    "create", "read", "update", "delete", "process", "validate",
]

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
type CommandResult = FlextResult[OutputData]
type ValidationResult = FlextResult[bool]
type ConfigResult = FlextResult[ConfigDict]
type PluginResult = FlextResult[PluginName]
type SessionResult = FlextResult[SessionId]
type ConfigurationResult = FlextResult[ConfigDict]
type ProcessingResult = FlextResult[OutputData]
type FileOperationResult = FlextResult[Path]
type NetworkResult = FlextResult[dict[str, object]]


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

    def save_file(
        self, data: FlextCliDataDict, path: FlextCliFilePath,
    ) -> FlextCliResult[None]:
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

    def show_progress[T](
        self, items: list[T], operation_name: str,
    ) -> FlextCliResult[list[T]]:
        """Show progress for operation."""
        ...

    def confirm_action(
        self, message: str, *, default: bool = False,
    ) -> FlextCliResult[bool]:
        """Get user confirmation."""
        ...


class FlextCliConfigProvider(Protocol):
    """Protocol for configuration management - standardizes config access."""

    def get_value(
        self, key: str, *, default: str | int | bool | None = None,
    ) -> str | int | bool | None:
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
    "CommandArgs",
    "CommandOptions",
    # Legacy result types (for backward compatibility)
    "CommandResult",
    "CommandStatus",
    # Basic enumerations
    "CommandType",
    "ConfigDict",
    "ConfigPath",
    "ConfigResult",
    "ConfigurationResult",
    "ContextParams",
    "DurationSeconds",
    # Basic type aliases
    "EntityId",
    "EntryPoint",
    "EnvironmentDict",
    "ErrorMessage",
    "ExitCode",
    "FileOperationResult",
    "FlextCliArguments",
    # Command types
    "FlextCliCommand",
    "FlextCliCommandPipeline",
    "FlextCliCommandRegistry",
    "FlextCliConfigDict",
    "FlextCliConfigProvider",
    # Data types
    "FlextCliDataDict",
    # Collection types
    "FlextCliDataList",
    # Protocol types
    "FlextCliDataProcessor",
    "FlextCliDataResult",
    "FlextCliDirectoryPath",
    # Factory types
    "FlextCliEntityFactory",
    "FlextCliEnvironment",
    "FlextCliErrorCallback",
    "FlextCliErrorDict",
    "FlextCliExecuteResult",
    "FlextCliFileHandler",
    "FlextCliFilePath",
    "FlextCliFileResult",
    # Specialized result types
    "FlextCliLoadResult",
    "FlextCliLogLevel",
    "FlextCliMetadataDict",
    # Operation types
    "FlextCliOperation",
    "FlextCliOperationList",
    "FlextCliOperationResult",
    "FlextCliOperationType",
    "FlextCliOptionalPath",
    # Literal types
    "FlextCliOutputFormat",
    # Path types
    "FlextCliPathLike",
    "FlextCliPathList",
    "FlextCliProcessResult",
    "FlextCliProcessor",
    "FlextCliProgressCallback",
    "FlextCliRenderResult",
    # Advanced FlextResult types
    "FlextCliResult",
    "FlextCliSaveResult",
    "FlextCliServiceFactory",
    # Configuration types
    "FlextCliSettings",
    "FlextCliSimpleValidatorProtocol",
    "FlextCliStatusType",
    "FlextCliStringList",
    # Callback types
    "FlextCliSuccessCallback",
    "FlextCliTableResult",
    "FlextCliTransformer",
    "FlextCliUIRenderer",
    "FlextCliValidateResult",
    "FlextCliValidationResult",
    "FlextCliValidationType",
    "FlextCliValidator",
    "FlextCliValidatorFactory",
    "K",
    "NetworkResult",
    "OutputData",
    "OutputFormat",
    "PathType",
    "PluginName",
    "PluginResult",
    "PluginStatus",
    "PluginVersion",
    # Click parameter types
    "PositiveIntType",
    "ProcessingResult",
    "ProfileType",
    "SessionData",
    "SessionId",
    "SessionResult",
    "SessionStatus",
    # Type variables
    "T",
    "TUserId",
    "TimeoutSeconds",
    "U",
    "URLType",
    "UserInput",
    "V",
    "ValidationResult",
    "WorkingDirectory",
]
