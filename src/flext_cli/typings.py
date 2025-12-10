"""FlextCli type definitions module - PEP 695 type aliases."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from typing import ParamSpec, Protocol, TypeVar

from flext_core import FlextTypes, r
from pydantic import BaseModel

# ═══════════════════════════════════════════════════════════════════════════
# TYPEVARS: Only object allowed outside the class
# ═══════════════════════════════════════════════════════════════════════════
# Reuse from FlextTypes when available
# Centralize all TypeVars here for massive reuse

# CLI domain TypeVars
FlextCliCommandT = TypeVar("FlextCliCommandT")
FlextCliConfigT = TypeVar("FlextCliConfigT")
FlextCliOutputT = TypeVar("FlextCliOutputT")
FlextCliResultT = TypeVar("FlextCliResultT")
FlextCliSessionT = TypeVar("FlextCliSessionT")
FlextCliContextT = TypeVar("FlextCliContextT")
FlextCliPluginT = TypeVar("FlextCliPluginT")
FlextCliFormatterT = TypeVar("FlextCliFormatterT")

# Model TypeVar for CLI commands
FlextCliModelT = TypeVar("FlextCliModelT", bound=BaseModel)

# Type aliases for better pyrefly compatibility
FormatableResult = (
    dict[str, FlextTypes.JsonValue]
    | list[FlextTypes.JsonValue]
    | tuple[FlextTypes.JsonValue, ...]
    | FlextTypes.JsonValue
    | r[FlextTypes.GeneralValueType]
)

ResultFormatter = Callable[[FormatableResult, str], None]


# ═══════════════════════════════════════════════════════════════════════════
# SINGLE CLASS WITH NESTED CLASSES
# ═══════════════════════════════════════════════════════════════════════════
class FlextCliTypes(FlextTypes):
    """FlextCli type definitions extending FlextTypes via inheritance.

    RULES:
    ───────
    1. TypeVars outside the class (only case allowed)
    2. PEP 695 type aliases inside nested classes
    3. Complex types composed with Protocols
    4. ZERO simple aliases - use direct types
    5. Inheritance from FlextTypes, no duplication
    """

    class Cli:
        """CLI types namespace for cross-project access.

        Provides organized access to all CLI types for other FLEXT projects.
        Usage: Other projects can reference `t.Cli.Command.*`, `t.Cli.Output.*`, etc.
        This enables consistent namespace patterns for cross-project type access.

        Note: Namespace composition via inheritance - no aliases needed.
        Access parent namespaces directly through inheritance.
        """

        # Top-level type aliases - direct inheritance from FlextTypes (no duplication)
        # CliJsonValue uses GeneralValueType for compatibility with Mapper conversions
        # (GeneralValueType includes datetime, JsonValue does not)
        type CliJsonValue = FlextTypes.GeneralValueType
        type CliJsonDict = FlextTypes.Json.JsonDict
        type CliJsonList = Sequence[FlextTypes.GeneralValueType]

        # Types namespace - extends FlextTypes.Types for full hierarchy exposure
        # All parent types are available through inheritance
        class Types(FlextTypes.Types):
            """Types namespace - extends FlextTypes.Types for full hierarchy exposure.

            All parent types are available through inheritance.
            Access JsonDict via t.Json.JsonDict or t.Types.Json.JsonDict.
            """

        # Json namespace - extends FlextTypes.Json for full hierarchy exposure
        # JsonDict is inherited from FlextTypes.Json, no need to redefine
        class Json(FlextTypes.Json):
            """JSON types namespace - extends FlextTypes.Json for full hierarchy exposure."""

        class CliJson(FlextTypes.Json):
            """CLI JSON types - extends FlextTypes.Json via inheritance for full hierarchy exposure."""

            # Additional CLI-specific types using FlextTypes.JsonValue
            type Handler[T] = Callable[[FlextTypes.JsonValue], r[T]]
            type Transformer = Callable[[FlextTypes.JsonValue], FlextTypes.JsonValue]
            type Filter = Callable[[FlextTypes.JsonValue], bool]
            type Processor = Callable[
                [Sequence[FlextTypes.JsonValue]],
                r[Sequence[FlextTypes.JsonValue]],
            ]

        class Command:
            """Command-related type aliases."""

            # ParamSpec for CLI command signatures
            P_CliCommand = ParamSpec("P_CliCommand")

            # Concrete types instead of TypeVars
            # Use GeneralValueType instead of object for better type safety
            type Handler[T] = Callable[[FlextTypes.GeneralValueType], r[T]]
            type Processor = Callable[[FlextTypes.GeneralValueType], r[bool]]
            type Collection = Sequence[FlextTypes.GeneralValueType]
            type BatchProcessor = Callable[[Sequence[FlextTypes.GeneralValueType]], r[int]]

        class CliConfig(FlextTypes.Config):
            """Configuration-related type aliases - extends FlextTypes.Config via inheritance for full hierarchy exposure."""

            type Validator = Callable[[FlextTypes.GeneralValueType], r[bool]]
            type Builder = Callable[
                [FlextTypes.Json.JsonDict],
                r[FlextTypes.GeneralValueType],
            ]

            # Configuration value types - reuse FlextTypes
            type ScalarValue = t.ScalarValue
            type ListValue = Sequence[t.ScalarValue]
            type DictValue = Mapping[
                str,
                t.ScalarValue | Sequence[t.ScalarValue],
            ]
            type ConfigValue = FlextTypes.GeneralValueType

            # Typed settings
            type SettingsDict = FlextTypes.Json.JsonDict

        # FlexibleValue type alias - inherits from FlextTypes for compatibility
        # FlexibleValue is a subset of GeneralValueType (scalars, sequences, mappings)
        # Note: Using FlextTypes.FlexibleValue directly to avoid override issues

        class Output:
            """Output-related type aliases."""

            # Use GeneralValueType instead of object for better type safety
            type Formatter = Callable[[FlextTypes.GeneralValueType], str]
            type Renderer[T] = Callable[[T], r[str]]
            type StreamWriter = Callable[[str], None]

        class Result:
            """Result-related type aliases."""

            # Use GeneralValueType instead of object for better type safety
            type Processor = Callable[
                [FlextTypes.GeneralValueType],
                r[FlextTypes.GeneralValueType],
            ]
            type Aggregator = Callable[
                [Sequence[FlextTypes.GeneralValueType]],
                r[FlextTypes.GeneralValueType],
            ]

        class Session:
            """Session-related type aliases."""

            # Use GeneralValueType instead of object for better type safety
            type Manager = Callable[[], r[FlextTypes.GeneralValueType]]
            type Validator = Callable[[FlextTypes.GeneralValueType], bool]

        class Context:
            """Context-related type aliases."""

            # Use JsonDict instead of dict[str, object] and GeneralValueType instead of object
            type Builder = Callable[
                [FlextTypes.Json.JsonDict],
                r[FlextTypes.GeneralValueType],
            ]
            type Provider = Callable[[], FlextTypes.GeneralValueType]

        class Plugin:
            """Plugin-related type aliases."""

            # Use GeneralValueType instead of object for better type safety
            type Loader = Callable[[str], r[FlextTypes.GeneralValueType]]
            type Registry = Mapping[str, FlextTypes.GeneralValueType]

        class Formatting:
            """Formatting-related type aliases."""

            # Use GeneralValueType instead of object for better type safety
            type Factory = Callable[[str], r[FlextTypes.GeneralValueType]]
            type Chain = Sequence[FlextTypes.GeneralValueType]

        class Data:
            """Data-related type aliases - using FlextTypes.Json.JsonDict for consistency."""

            # Core data types - use FlextTypes.Json.JsonDict instead of dict[str, object]
            type CliDataDict = FlextTypes.Json.JsonDict
            type CliFormatData = FlextTypes.Json.JsonDict
            type CliConfigData = FlextTypes.Json.JsonDict
            type CliCommandResult = FlextTypes.Json.JsonDict
            type CliCommandMetadata = FlextTypes.Json.JsonDict
            type DebugInfoData = FlextTypes.Json.JsonDict

            # Execution types
            type ExecutionKwargs = FlextTypes.Json.JsonDict

            # Table data types - for compatibility with examples
            type TableRows = Sequence[FlextTypes.Json.JsonDict]
            type TabularData = (
                Sequence[FlextTypes.Json.JsonDict] | FlextTypes.Json.JsonDict
            )
            type CliConfigMapping = Mapping[str, FlextTypes.GeneralValueType]

        class Pydantic:
            """Pydantic-related type aliases."""

            # IncEx type alias for Pydantic include/exclude parameters
            # Structurally compatible with Pydantic's internal IncEx type
            type IncEx = set[str] | dict[str, set[str]] | Mapping[str, set[str]] | None

        class Configuration:
            """Configuration schema type aliases - using FlextTypes.Json.JsonDict."""

            type CliConfigSchema = FlextTypes.Json.JsonDict
            type SessionConfiguration = FlextTypes.Json.JsonDict
            type ProfileConfiguration = FlextTypes.Json.JsonDict

        class CliCommand:
            """Command definition type aliases - using FlextTypes.Json.JsonDict."""

            type CommandDefinition = FlextTypes.Json.JsonDict
            type CommandResult = FlextTypes.Json.JsonDict
            type CommandContext = FlextTypes.Json.JsonDict

        class Display:
            """Rich display type aliases using Protocols.

            Protocol-dependent type aliases have been moved to models.py (Tier 1).
            Use m.Cli.Display.RichTable, m.Cli.Display.RichTree, m.Cli.Display.Console
            for type annotations referencing protocol types.
            """

        class Callable:
            """Callable type aliases - now properly typed."""

            # FormatableResult and ResultFormatter defined at module level for pyrefly compatibility
            # See module-level definitions above

            # HandlerFunction: Generic handler with FlextResult return type
            class HandlerFunction(Protocol):
                """Protocol for handler functions returning FlextResult."""

                def __call__(
                    self,
                    *args: object,
                    **kwargs: object,
                ) -> r[FlextTypes.GeneralValueType]:
                    """Call handler with arguments and return FlextResult."""
                    ...

        class Auth:
            """Authentication type aliases."""

            type CredentialsData = Mapping[str, str]

        class Workflow:
            """Workflow type aliases - using FlextTypes.Json.JsonDict."""

            type WorkflowStepResult = FlextTypes.Json.JsonDict
            type WorkflowProgress = FlextTypes.Json.JsonDict

        class Interactive:
            """Interactive display type aliases using Protocols.

            Protocol-dependent type aliases have been moved to models.py (Tier 1).
            Use m.Cli.Interactive.Progress for type annotations referencing protocol types.
            """

        class Tables:
            """Table-related type aliases."""

            # Table data types - reuse FlextTypes types for consistency
            # Supports both sequences and mappings for table data
            # Compatible with Iterable for tabulate integration
            type TableData = (
                Sequence[FlextTypes.Json.JsonDict]
                | FlextTypes.Json.JsonDict
                | Sequence[Sequence[FlextTypes.GeneralValueType]]
                | Mapping[str, FlextTypes.GeneralValueType]
            )
            type TableRows = Sequence[FlextTypes.Json.JsonDict]


# Alias for simplified usage
t = FlextCliTypes


# Namespace composition via class inheritance
# Cli namespace provides access to nested classes through inheritance
# Access patterns:
# - t.Cli.* for CLI-specific types
# - t.Command.* for command types
# - t.Output.* for output types
# - t.Core.* for core types (inherited from parent)
# - t.Data.* for convenience (same as t.Cli.Data.*)

__all__ = [
    "FlextCliCommandT",
    "FlextCliConfigT",
    "FlextCliContextT",
    "FlextCliFormatterT",
    "FlextCliModelT",
    "FlextCliOutputT",
    "FlextCliPluginT",
    "FlextCliResultT",
    "FlextCliSessionT",
    "FlextCliTypes",
    "t",
]
