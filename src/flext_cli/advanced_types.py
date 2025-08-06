"""FlextCli Advanced Types - Enhanced Type Safety and Developer Experience.

This module provides advanced type definitions that eliminate type-related
boilerplate and enhance IDE support following modern Python typing patterns.

Type Categories:
    - FlextCliProtocols: Interface definitions for dependency injection
    - FlextCliTypeAliases: Complex type simplification
    - FlextCliGenerics: Generic types for type-safe operations
    - FlextCliLiterals: Literal types for enhanced type safety

Usage Pattern:
    def process_data(
        data: FlextCliDataDict,
        processor: FlextCliDataProcessor,
        output_format: FlextCliOutputFormat = "json"
    ) -> FlextCliOperationResult[str]:
        # Full type safety with minimal annotations

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Literal, Protocol, TypeVar

from flext_core import FlextResult
from rich.console import Console
from rich.table import Table

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

# Common Data Types (eliminates dict[str, Any] boilerplate with specific types)
type FlextCliDataDict = dict[str, str | int | float | bool | None]
type FlextCliConfigDict = dict[str, str | int | float | bool | None]
type FlextCliMetadataDict = dict[str, str | int | float | bool]
type FlextCliErrorDict = dict[str, str]

# File and Path Types (eliminates Union[str, Path] boilerplate)
type FlextCliPathLike = str | Path
type FlextCliFilePath = str | Path
type FlextCliDirectoryPath = str | Path
type FlextCliOptionalPath = str | Path | None

# Operation Types - using generic types instead of Any
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

# Collection Types - using generic types
type FlextCliDataList = list[FlextCliDataDict]
type FlextCliStringList = list[str]
type FlextCliPathList = list[FlextCliPathLike]
type FlextCliOperationList[T] = list[FlextCliOperation[T]]


# Protocol Definitions (Interface Types)
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


class FlextCliValidatorProtocol(Protocol):
    """Protocol for validation operations - standardizes validation interface."""

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


# Functional Types (Higher-Order Functions) - avoiding ellipsis
type FlextCliDecorator[T] = Callable[[Callable[[object], T]], Callable[[object], T]]
type FlextCliMiddleware[T] = Callable[[FlextCliOperation[T]], FlextCliOperation[T]]
type FlextCliHook = Callable[[FlextCliDataDict], FlextCliResult[None]]

# Callback Types
type FlextCliSuccessCallback[T] = Callable[[T], None]
type FlextCliErrorCallback = Callable[[str], None]
type FlextCliProgressCallback = Callable[[int, int], None]

# Configuration Types - using specific types instead of Any
type FlextCliSettings = dict[str, str | int | float | bool | None]
type FlextCliEnvironment = dict[str, str]
type FlextCliArguments = dict[str, str | int | float | bool | None]

# Complex Composite Types
type FlextCliOperationContext = dict[str, FlextCliConfigDict | FlextCliDataDict | Console | FlextCliPathLike]

type FlextCliExecutionPlan[T] = list[tuple[
    FlextCliOperation[T],
    str,  # operation_name
    FlextCliConfigDict,  # options
]]

type FlextCliValidationRules = dict[str, FlextCliValidationType | FlextCliValidatorProtocol | Callable[[object], bool]]

type FlextCliBatchOperation[T] = tuple[
    FlextCliOperation[T],
    str,  # name
    FlextCliConfigDict,  # options
    FlextCliSuccessCallback[T] | None,  # success_callback
    FlextCliErrorCallback | None,  # error_callback
]

# Specialized Result Types for Common Operations
type FlextCliLoadResult = FlextResult[FlextCliDataDict]
type FlextCliSaveResult = FlextResult[None]
type FlextCliValidateResult = FlextResult[bool]
type FlextCliProcessResult = FlextResult[FlextCliDataDict]
type FlextCliExecuteResult = FlextResult[str]
type FlextCliRenderResult = FlextResult[Table]

# Utility Types for Advanced Patterns
type FlextCliMaybeResult[T] = FlextResult[T] | None
type FlextCliEitherResult[T, U] = FlextResult[T] | FlextResult[U]
type FlextCliChainableResult[T] = FlextResult[T]

# Factory Types - using specific parameters
type FlextCliEntityFactory[T] = Callable[[FlextCliConfigDict], FlextCliResult[T]]
type FlextCliServiceFactory[T] = Callable[[FlextCliConfigDict], T]
type FlextCliValidatorFactory = Callable[[str], FlextCliValidatorProtocol]

# Mapping Types (eliminates verbose dict annotations)
type FlextCliFieldMap = dict[str, str]
type FlextCliTypeMap = dict[str, type]
type FlextCliValidationMap = dict[str, FlextCliValidationType]
type FlextCliTransformationMap[T, U] = dict[str, FlextCliTransformer[T, U]]

# Command Pattern Types - using generic types
type FlextCliCommand[T] = Callable[[], FlextCliResult[T]]
type FlextCliCommandRegistry[T] = dict[str, FlextCliCommand[T]]
type FlextCliCommandPipeline[T] = list[FlextCliCommand[T]]

# Export all types
__all__ = [
    "FlextCliBatchOperation",
    # Command Types
    "FlextCliCommand",
    "FlextCliCommandPipeline",
    "FlextCliCommandRegistry",
    "FlextCliConfigDict",
    "FlextCliConfigProvider",
    # Data Types
    "FlextCliDataDict",
    # Collection Types
    "FlextCliDataList",
    # Protocol Types
    "FlextCliDataProcessor",
    "FlextCliDataResult",
    # Functional Types
    "FlextCliDecorator",
    "FlextCliDirectoryPath",
    # Factory Types
    "FlextCliEntityFactory",
    "FlextCliErrorCallback",
    "FlextCliErrorDict",
    "FlextCliExecuteResult",
    "FlextCliExecutionPlan",
    # Mapping Types
    "FlextCliFieldMap",
    "FlextCliFileHandler",
    "FlextCliFilePath",
    "FlextCliFileResult",
    "FlextCliHook",
    # Specialized Results
    "FlextCliLoadResult",
    "FlextCliLogLevel",
    "FlextCliMetadataDict",
    "FlextCliMiddleware",
    # Operation Types
    "FlextCliOperation",
    # Composite Types
    "FlextCliOperationContext",
    "FlextCliOperationList",
    "FlextCliOperationResult",
    "FlextCliOperationType",
    "FlextCliOptionalPath",
    # Literal Types
    "FlextCliOutputFormat",
    # Path Types
    "FlextCliPathLike",
    "FlextCliPathList",
    "FlextCliProcessResult",
    "FlextCliProcessor",
    "FlextCliProgressCallback",
    "FlextCliRenderResult",
    # Result Types
    "FlextCliResult",
    "FlextCliSaveResult",
    "FlextCliServiceFactory",
    "FlextCliStatusType",
    "FlextCliStringList",
    # Callback Types
    "FlextCliSuccessCallback",
    "FlextCliTableResult",
    "FlextCliTransformationMap",
    "FlextCliTransformer",
    "FlextCliTypeMap",
    "FlextCliUIRenderer",
    "FlextCliValidateResult",
    "FlextCliValidationMap",
    "FlextCliValidationResult",
    "FlextCliValidationRules",
    "FlextCliValidationType",
    "FlextCliValidatorFactory",
    "FlextCliValidatorProtocol",
    "K",
    # Type Variables
    "T",
    "U",
    "V",
]
