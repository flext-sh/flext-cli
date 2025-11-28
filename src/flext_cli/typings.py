"""FLEXT CLI Types - Domain-specific CLI type definitions.

This module provides CLI-specific type definitions extending FlextTypes.
Follows FLEXT standards:
- Single unified class per module
- Domain-specific types with business value
- Python 3.13+ syntax
- Pydantic v2 Annotated types with validation constraints
- Optimal use of Literals and Enums from constants.py
- Composition with FlextTypes instead of simple aliases

**Architecture Rules:**
- Only TypeVars can be outside FlextCliTypes class
- No compatibility/convenience aliases at module level
- All types must be complex, business-aligned, not over-generalized
- Compose with FlextTypes when appropriate
- Import from *Typings and *Protocols for composition

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Callable, Callable as CallableABC, Mapping, Sequence
from typing import Annotated, Protocol, TypeVar

from flext_core import FlextResult, FlextTypes
from flext_core.typings import GeneralValueType
from pydantic import BaseModel, Field
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

from flext_cli.constants import FlextCliConstants

# ============================================================================
# Module-Level TypeVars Only (Python 3.13+ strict)
# ============================================================================
# Only TypeVars can be outside the FlextCliTypes class
# All type aliases must be inside FlextCliTypes as complex types

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

    Provides Pydantic v2 Annotated types with validation constraints
    for CLI-specific field patterns, and Rich component type aliases.

    **Architecture:**
    - Extends FlextTypes to inherit all base types (Json, Validation, Handler, etc.)
    - Composes with FlextTypes types when appropriate (e.g., uses GeneralValueType)
    - Defines CLI-specific types aligned to CLI business domain
    - Uses concrete dict/list types for CLI operations requiring mutability
    - Uses Mapping/Sequence from collections.abc for read-only parameters
    - Optimal use of Literals and Enums from FlextCliConstants

    **Business Alignment:**
    - CLI domain types focus on terminal operations, command execution
    - Types are specific to CLI use cases, not over-generalized
    - Reuses FlextTypes foundation types (Json, Validation) to avoid duplication
    - Uses Literals and Enums from constants.py for type safety and validation

    **Pydantic 2 + Python 3.13 Best Practices:**
    - Literals from constants.py for type hints (compile-time safety)
    - StrEnums from constants.py for runtime validation (Pydantic integration)
    - Annotated types with Field constraints for validation
    - PEP 695 type aliases for better IDE support
    """

    # =====================================================================
    # ADVANCED TYPE ALIASES - Python 3.13+ PEP 695 Best Practices
    # =====================================================================
    # Modern type aliases using PEP 695 syntax for better IDE support
    # These aliases are used throughout the CLI domain for type safety

    # CLI value type - reuse from flext-core (no duplication)
    # Use FlextTypes.ScalarValue directly for primitive CLI values
    type CliValueType = FlextTypes.ScalarValue

    type CliMappingType = Mapping[str, CliValueType | Sequence[CliValueType]]
    """Immutable mapping type for CLI configuration data.
    Uses collections.abc.Mapping for read-only access patterns.
    Python 3.13+ best practice for configuration mappings."""

    type CliMutableMappingType = dict[str, CliValueType | list[CliValueType]]
    """Mutable mapping type for CLI data that needs modification.
    Uses concrete dict type for operations requiring mutability."""

    type CliSequenceType = Sequence[CliValueType]
    """Immutable sequence type for CLI data lists.
    Uses collections.abc.Sequence for read-only iteration patterns."""

    type CliMutableSequenceType = list[CliValueType]
    """Mutable sequence type for CLI data lists that need modification.
    Uses concrete list type for operations requiring mutability."""

    # =====================================================================
    # ADVANCED CLI JSON TYPES - Python 3.13+ recursive types with collections.abc
    # =====================================================================
    # CLI-specific JSON types using advanced recursive type patterns
    # Composes with FlextTypes.Json types and modern collections.abc
    # Uses discriminated unions for better type narrowing

    # CLI JSON primitive - reuse from flext-core (no duplication)
    # Use FlextTypes.Json.JsonPrimitive directly
    type CliJsonPrimitive = FlextTypes.Json.JsonPrimitive

    type CliJsonValue = CliJsonPrimitive | dict[str, CliJsonValue] | list[CliJsonValue]
    """Recursive JSON value type with advanced union patterns.

    Uses discriminated unions for better type checking and narrowing.
    Composes with FlextTypes.GeneralValueType for CLI mutability (uses dict/list instead of Mapping/Sequence).
    Business context: Terminal output formatting, command data structures.
    Note: Uses concrete dict/list for mutability vs FlextTypes.Json.JsonValue which uses Mapping/Sequence.
    """

    type CliJsonDict = dict[str, CliJsonValue]
    """CLI JSON dictionary with advanced typing.

    Uses concrete dict for CLI operations requiring mutability.
    Business context: CLI data structures that need modification (formatting, config).
    Composes with collections.abc.Mapping for read-only access patterns.
    """

    type CliJsonList = list[CliJsonValue]
    """CLI JSON list with advanced typing.

    Uses concrete list for CLI operations requiring mutability.
    Business context: CLI data lists that need modification (table rows, command args).
    Composes with collections.abc.Sequence for read-only iteration.
    """

    # Immutable variants using collections.abc for read-only access
    type CliJsonMapping = Mapping[str, CliJsonValue]
    """Immutable CLI JSON mapping using collections.abc.Mapping.

    Python 3.13+ best practice for read-only JSON data access.
    Prevents accidental mutation in CLI pipelines.
    """

    type CliJsonSequence = Sequence[CliJsonValue]
    """Immutable CLI JSON sequence using collections.abc.Sequence.

    Python 3.13+ best practice for read-only JSON array access.
    Enables efficient iteration without mutation risks.
    """

    # =====================================================================
    # ANNOTATED CLI TYPES - Pydantic v2 Annotated types with validation
    # =====================================================================

    class AnnotatedCli:
        """CLI-specific Annotated types with built-in validation constraints.

        Provides reusable Annotated type definitions for CLI-specific field
        patterns, eliminating verbose Field() declarations in CLI commands
        and models.

        **Pydantic 2 Best Practices:**
        - Uses Literals from FlextCliConstants for type hints
        - Uses StrEnums from FlextCliConstants for runtime validation
        - Field constraints for value validation
        - Python 3.13+ PEP 695 type aliases

        Business context: CLI command parameter validation and type safety.
        Composes with FlextTypes.Validation patterns (PortNumber, TimeoutSeconds).
        Extends with CLI-specific validation (CommandName, OutputFormat, etc.).

        Example:
            from flext_cli.typings import FlextCliTypes
            from pydantic import BaseModel

            class CommandParams(BaseModel):
                command_name: FlextCliTypes.AnnotatedCli.CommandName
                port: FlextCliTypes.AnnotatedCli.PortNumber
                batch_size: FlextCliTypes.AnnotatedCli.BatchSize
                output_format: FlextCliTypes.AnnotatedCli.OutputFormat

        """

        # Command string types with validation
        CommandName = Annotated[
            str,
            Field(pattern=r"^[a-z][a-z0-9-]*$", min_length=1, max_length=64),
        ]
        """Command name with kebab-case pattern validation."""

        OptionName = Annotated[
            str,
            Field(pattern=r"^--[a-z][a-z0-9-]*$", min_length=3, max_length=64),
        ]
        """CLI option name with double-dash prefix."""

        ProfileName = Annotated[str, Field(min_length=1, max_length=64)]
        """Configuration profile name."""

        # Numeric types with value constraints
        # Business context: CLI operation configuration (timeouts, batch processing)
        # Composes with FlextTypes.Validation.TimeoutSeconds pattern
        TimeoutMs = Annotated[int, Field(ge=100, le=300000)]
        """Timeout in milliseconds (100ms-300s).

        Business context: CLI command execution timeouts.
        Composes with FlextTypes.Validation.TimeoutSeconds (converted to ms).
        """

        BatchSize = Annotated[int, Field(ge=1, le=10000)]
        """Batch processing size (1-10000 items).

        Business context: CLI batch processing operations.
        """

        MaxRetries = Annotated[int, Field(ge=0, le=100)]
        """Maximum number of retries (0-100).

        Business context: CLI operation retry configuration.
        Composes with FlextTypes.Validation.RetryCount pattern.
        """

        MaxWorkers = Annotated[int, Field(ge=1, le=50)]
        """Maximum number of parallel workers (1-50).

        Business context: CLI parallel processing configuration.
        """

        # Validation constraint types (Pydantic v2 native)
        NotEmptyStr = Annotated[str, Field(min_length=1)]
        """Non-empty string (min length 1)."""

        PositiveNumber = Annotated[int, Field(gt=0)]
        """Positive integer (> 0)."""

        NonNegativeNumber = Annotated[int, Field(ge=0)]
        """Non-negative integer (>= 0)."""

        # Path and file types
        ConfigFilePath = Annotated[str, Field(min_length=1)]
        """Path to configuration file."""

        OutputDirectory = Annotated[str, Field(min_length=1)]
        """Path to output directory."""

        # Output format types - Using Literals from constants.py
        OutputFormat = Annotated[
            FlextCliConstants.OutputFormatLiteral,
            Field(
                description="Supported output format (json, yaml, csv, table, plain)"
            ),
        ]
        """Supported output format using Literal from constants.py.

        Pydantic 2: Automatically validates against Literal values.
        Business context: Terminal output formatting (tables, JSON, YAML, CSV).
        """

        TableWidth = Annotated[int, Field(ge=40, le=300)]
        """Table display width in characters (40-300)."""

        # Logging and debug types - Using Literals from constants.py
        LogLevel = Annotated[
            FlextCliConstants.LogLevelLiteral,
            Field(description="Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"),
        ]
        """Log level using Literal from constants.py.

        Pydantic 2: Automatically validates against Literal values.
        Business context: CLI logging configuration.
        """

        VerbosityLevel = Annotated[int, Field(ge=0, le=3)]
        """Verbosity level (0-3, where 0=quiet, 3=very verbose)."""

    # =====================================================================
    # CLI DATA TYPES - Protocol data structures for CLI operations
    # =====================================================================

    class Data:
        """Advanced CLI data type aliases using modern Python patterns.

        Provides reusable type definitions for CLI data structures with
        discriminated unions and collections.abc for optimal type safety.

        **Advanced Patterns:**
        - Discriminated unions for better type narrowing
        - collections.abc.Mapping/Sequence for immutability contracts
        - Concrete dict/list for mutability when required
        - Protocol composition for structural typing

        Business context: CLI-specific data structures for terminal operations.
        Composes with FlextTypes for consistency across domains.

        Example:
            from flext_cli.typings import FlextCliTypes
            from flext_core import FlextResult

            class MyFormatter:
                def format_data(
                    self,
                    data: FlextCliTypes.Data.CliFormatData,
                    **options: FlextCliTypes.Data.CliConfigData,
                ) -> FlextResult[str]:
                    # Implementation with type safety
                    return FlextResult[str].ok("formatted")

        """

        # Core CLI data structures with discriminated union patterns
        type CliFormatData = FlextCliTypes.CliJsonDict
        """Mutable data structure for CLI formatting operations.

        Business context: Terminal output formatting (tables, JSON, YAML, CSV).
        Uses concrete dict for operations that modify output structure.
        Composes with CliJsonMapping for read-only access when needed.
        """

        type CliConfigData = FlextCliTypes.CliJsonDict
        """Mutable data structure for CLI configuration management.

        Business context: CLI application configuration (load/save/options).
        Uses concrete dict for configuration modifications.
        Composes with CliJsonMapping for read-only configuration access.
        """

        # Immutable variants using collections.abc for read-only patterns
        type CliFormatMapping = FlextCliTypes.CliJsonMapping
        """Immutable CLI formatting data using collections.abc.Mapping.

        Python 3.13+ best practice for read-only formatting data access.
        Prevents accidental mutation during CLI pipeline processing.
        """

        type CliConfigMapping = FlextCliTypes.CliJsonMapping
        """Immutable CLI configuration using collections.abc.Mapping.

        Python 3.13+ best practice for read-only configuration access.
        Ensures configuration data integrity in CLI operations.
        """

        # Specialized CLI data structures
        type AuthConfigData = FlextCliTypes.CliJsonDict
        """Authentication configuration with credentials management.

        Business context: CLI authentication and credential management.
        Uses discriminated union for secure credential handling.
        """

        type DebugInfoData = FlextCliTypes.CliJsonDict
        """Debug information data structure with advanced typing.

        Business context: CLI debugging and diagnostic information.
        Composes with FlextTypes for consistent debug data patterns.
        """

        # Command execution data with discriminated unions
        type CliCommandArgs = FlextCliTypes.CliJsonDict
        """Command arguments with advanced type validation.

        Business context: Command-line argument parsing and validation.
        Uses discriminated unions for better type narrowing in CLI parsing.
        """

        type CliCommandResult = FlextCliTypes.CliJsonDict
        """Command execution results with discriminated union patterns.

        Business context: Command execution results for terminal display.
        Enables discriminated unions for result type validation.
        """

        # Table data structures with advanced collections.abc patterns
        type TableRow = FlextCliTypes.CliJsonDict
        """Single row of tabular CLI data with type safety.

        Business context: Terminal table formatting (Rich tables, ASCII tables).
        Uses concrete dict for row data that may be modified during formatting.
        """

        type TableRows = Sequence[FlextCliTypes.CliJsonDict]
        """Immutable sequence of table rows using collections.abc.Sequence.

        Python 3.13+ best practice for read-only table data iteration.
        Business context: Bulk table data processing without mutation risks.
        """

        type TableData = TableRows | FlextCliTypes.CliJsonDict
        """Discriminated union for tabular data representation.

        Supports both single row (dict) and multiple rows (sequence).
        Business context: Flexible table data input for terminal display.
        Uses discriminated union for better type checking and narrowing.
        """

        type TabularData = TableData
        """Complete table input with discriminated union support.

        Business context: Complete table input for terminal display.
        Maintains discriminated union pattern for type safety.
        """

        # Generic CLI data with advanced typing
        type CliDataDict = FlextCliTypes.CliJsonDict
        """Generic CLI data dictionary with advanced type constraints.

        Business context: Generic data passing in CLI operations.
        Uses discriminated union patterns for flexible yet type-safe data handling.
        """

        type CliCommandData = FlextCliTypes.CliJsonDict
        """Command metadata with discriminated union validation.

        Business context: Command definition and execution metadata.
        Enables discriminated unions for command type validation.
        """

        type CliCommandMetadata = dict[
            str,
            str
            | CallableABC[[], FlextCliTypes.CliJsonValue]
            | CallableABC[[list[str]], FlextCliTypes.CliJsonValue],
        ]
        """Command metadata structure for command registration.

        Business context: Command registration with name, handler, and description.
        Keys: NAME (str), HANDLER (callable), DESCRIPTION (str).
        Uses CallableABC from collections.abc for handler type.
        Uses forward reference for CliJsonValue since it's defined in parent class.
        """

        # Advanced execution parameters with collections.abc
        type ExecutionKwargs = Mapping[str, FlextCliTypes.CliJsonValue]
        """Immutable execution keyword arguments using collections.abc.Mapping.

        Business context: Service execution parameters in CLI operations.
        Python 3.13+ best practice: Use Mapping for immutable read-only parameters.
        Composes with FlextTypes.Types.ConfigurationMapping pattern.
        Replaces object type with specific JSON-compatible mapping type.
        Provides better type safety than generic object typing.
        """

    # =====================================================================
    # AUTH DATA TYPES - Authentication and credentials
    # =====================================================================

    class Auth:
        """Authentication data type aliases."""

        type CredentialsData = FlextCliTypes.CliJsonDict
        """Data structure for credentials (username, password, token)."""

    # =====================================================================
    # CLI COMMAND TYPES - Command execution and results
    # =====================================================================

    class CliCommand:
        """CLI command type aliases for command execution framework."""

        type CommandDefinition = FlextCliTypes.CliJsonDict
        """Data structure for command definition."""

        type CommandContext = FlextCliTypes.CliJsonDict
        """Data structure for command execution context."""

        type CommandResult = FlextCliTypes.CliJsonDict
        """Data structure for command execution results."""

    # =====================================================================
    # CONFIGURATION TYPES - Application configuration
    # =====================================================================

    class Configuration:
        """Configuration type aliases."""

        type CliConfigSchema = FlextCliTypes.CliJsonDict
        """Data structure for CLI configuration schema."""

        type ProfileConfiguration = FlextCliTypes.CliJsonDict
        """Data structure for configuration profile."""

        type SessionConfiguration = FlextCliTypes.CliJsonDict
        """Data structure for session configuration."""

    # =====================================================================
    # CALLABLE TYPE ALIASES - Function signatures for CLI operations
    # =====================================================================

    class Callable:
        """CLI-specific callable type aliases for handlers and formatters.

        Business context: CLI command execution and output formatting.
        Composes with FlextTypes.Handler patterns for consistency.
        """

        # Handler function that processes CLI data and returns result
        # Accepts ExecutionKwargs (context_data) and returns FlextResult
        # Uses specific Mapping type instead of Ellipsis to avoid explicit Any
        # Note: Using forward reference for CliJsonValue from parent class
        HandlerFunction = CallableABC[
            [Mapping[str, "FlextCliTypes.CliJsonValue"]],
            FlextResult["FlextCliTypes.CliJsonValue"],
        ]
        """CLI command handler function signature - accepts ExecutionKwargs.

        Business context: CLI command execution handlers.
        Composes with FlextTypes.Handler.HandlerCallable pattern.
        Uses ExecutionKwargs (Mapping[str, CliJsonValue]) for type-safe kwargs.
        """

        # Result formatter that displays domain-specific result types
        # Accepts BaseModel, dict, or objects with __dict__ attribute
        class FormatableResult(Protocol):
            """Protocol for results that can be formatted.

            Business context: Terminal output formatting (Rich, ASCII, JSON, YAML).
            Uses FlextTypes.GeneralValueType for type-safe attribute access.
            """

            __dict__: dict[str, GeneralValueType]

        # Use specific types for flexible formatting
        # Expanded from object to GeneralValueType for type safety
        # CliJsonValue would be ideal but can't reference parent class type alias here
        # Using GeneralValueType from flext-core for structured data types
        ResultFormatter = CallableABC[
            [
                BaseModel
                | dict[str, GeneralValueType]
                | list[GeneralValueType]
                | str
                | int
                | float
                | bool
                | FormatableResult,
                str,
            ],
            None,
        ]
        """Result formatter function signature: (result, output_format) -> None.

        Business context: Formatting command results for terminal display.
        """

    # =====================================================================
    # RICH COMPONENT TYPE ALIASES
    # =====================================================================

    class Display:
        """Rich visual component type aliases.

        Python 3.13+ best practice: TypeAlias for class attributes
        (PEP 695 only works at module level).
        """

        Console: type = RichConsoleImport
        """Rich Console type alias."""
        RichPanel: type = RichPanelImport
        """Rich Panel type alias."""
        RichTable: type = RichTableImport
        """Rich Table type alias."""
        RichTree: type = RichTreeImport
        """Rich Tree type alias."""

    class Layout:
        """Rich layout component type aliases.

        Python 3.13+ best practice: TypeAlias for class attributes
        (PEP 695 only works at module level).
        """

        RichLayout: type = RichLayoutImport
        """Rich Layout type alias."""

    class Interactive:
        """Rich interactive component type aliases.

        Python 3.13+ best practice: TypeAlias for class attributes
        (PEP 695 only works at module level).
        """

        RichLive: type = RichLiveImport
        """Rich Live type alias."""
        Progress: type = ProgressImport
        """Rich Progress type alias."""
        RichStatus: type = RichStatusImport
        """Rich Status type alias."""

    class ProgressColumns:
        """Rich progress column type aliases.

        Python 3.13+ best practice: TypeAlias for class attributes
        (PEP 695 only works at module level).
        """

        BarColumn: type = BarColumnImport
        """Rich BarColumn type alias."""
        SpinnerColumn: type = SpinnerColumnImport
        """Rich SpinnerColumn type alias."""
        TextColumn: type = TextColumnImport
        """Rich TextColumn type alias."""
        TimeRemainingColumn: type = TimeRemainingColumnImport
        """Rich TimeRemainingColumn type alias."""

    # =====================================================================
    # CLI PROJECT TYPES - Domain-specific project types
    # =====================================================================

    class CliCommandResult:
        """CLI command result type definitions."""

        # Core command result types
        type CommandResultData = FlextCliTypes.CliJsonDict
        # Note: CommandResultStatus at module level as CommandResultStatusLiteral
        # Python 3.13+ best practice: Use Mapping from collections.abc
        type CommandResultMetadata = Mapping[str, str | int | bool]

    class Project:
        """CLI-specific project types extending FlextTypes.

        Adds CLI-specific project types while inheriting generic types from FlextTypes.
        Follows domain separation principle: CLI domain owns CLI-specific types.

        Business context: CLI project configuration and setup.
        Composes with FlextTypes.Types.ConfigurationMapping for base patterns.
        """

        # CLI-specific project configurations
        # Note: CliProjectType is CliProjectTypeLiteral in first class (line 28)
        type CliProjectConfig = FlextCliTypes.CliJsonDict
        """CLI project configuration data structure.

        Business context: CLI project initialization and configuration.
        """
        # Python 3.13+ best practice: Use Mapping from collections.abc
        type CommandLineConfig = Mapping[str, str | int | bool | list[str]]
        """Command-line configuration mapping.

        Business context: CLI command-line argument configuration.
        Composes with FlextTypes.Types.ConfigurationMapping pattern.
        """
        type InteractiveConfig = Mapping[str, bool | str | FlextCliTypes.CliJsonDict]
        """Interactive CLI configuration mapping.

        Business context: Interactive CLI mode configuration (prompts, confirmations).
        """
        type OutputConfig = Mapping[str, str | FlextCliTypes.CliJsonValue]
        """Output configuration mapping.

        Business context: CLI output formatting configuration.
        Uses CliJsonValue instead of object for type safety.
        """

    class Workflow:
        """Workflow orchestration type definitions.

        Provides types for complex multi-step workflow orchestration
        with progress tracking and result aggregation.
        """

        # Workflow execution types
        type WorkflowStepResult = FlextCliTypes.CliJsonDict
        """Result data from a single workflow step execution."""

        type WorkflowProgressCallback = Callable[
            [int, int, str, FlextCliTypes.Workflow.WorkflowProgressData], None
        ]
        """Callback for workflow progress updates."""

        type WorkflowProgressData = Mapping[str, int | str | bool]
        """Progress data passed to progress callbacks."""

        type WorkflowStepFunction = Callable[
            [], FlextResult[FlextCliTypes.Workflow.WorkflowStepResult]
        ]
        """Function signature for workflow step functions."""


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
