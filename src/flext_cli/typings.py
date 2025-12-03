"""FlextCli type definitions module - PEP 695 type aliases."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from typing import TypeVar

from flext_core import r, t

from flext_cli.protocols import FlextCliProtocols

# ═══════════════════════════════════════════════════════════════════════════
# TYPEVARS: Único objeto permitido fora da classe
# ═══════════════════════════════════════════════════════════════════════════
# Reutilize de t quando existir

TCliCommand = TypeVar("TCliCommand")
TCliConfig = TypeVar("TCliConfig")
TCliOutput = TypeVar("TCliOutput")
TCliResult = TypeVar("TCliResult")
TCliSession = TypeVar("TCliSession")
TCliContext = TypeVar("TCliContext")
TCliPlugin = TypeVar("TCliPlugin")
TCliFormatter = TypeVar("TCliFormatter")


# ═══════════════════════════════════════════════════════════════════════════
# CLASSE ÚNICA COM NESTED CLASSES
# ═══════════════════════════════════════════════════════════════════════════
class FlextCliTypes(t):
    """FlextCli type definitions composing with t.

    REGRAS:
    ───────
    1. TypeVars fora da classe (único caso permitido)
    2. Type aliases PEP 695 dentro de nested classes
    3. Tipos complexos compostos com Protocols
    4. ZERO aliases simples - use tipos diretos
    5. Composição com t, não duplicação
    """

    # Top-level type aliases - direct composition with t (no duplication)
    # CliJsonValue uses GeneralValueType for compatibility with DataMapper conversions
    # (GeneralValueType includes datetime, JsonValue does not)
    type CliJsonValue = t.GeneralValueType
    type CliJsonDict = t.JsonDict
    type CliJsonList = Sequence[t.GeneralValueType]

    class CliJson:
        """CLI JSON types - direct composition with t.Json (no duplication)."""

        # Direct aliases to t.Json for consistency
        type Value = t.Json.JsonValue
        type Dict = t.Json.JsonDict
        type List = t.Json.JsonList

        # Tipos genéricos usando t.JsonValue
        type Handler[T] = Callable[[t.JsonValue], r[T]]
        type Transformer = Callable[[t.JsonValue], t.JsonValue]
        type Filter = Callable[[t.JsonValue], bool]
        type Processor = Callable[
            [Sequence[t.JsonValue]],
            r[Sequence[t.JsonValue]],
        ]

    class Command:
        """Command-related type aliases."""

        # Tipos concretos ao invés de TypeVars
        # Use GeneralValueType instead of object for better type safety
        type Handler[T] = Callable[[t.GeneralValueType], r[T]]
        type Processor = Callable[[t.GeneralValueType], r[bool]]
        type Collection = Sequence[t.GeneralValueType]
        type BatchProcessor = Callable[[Collection], r[int]]

    class CliConfig:
        """Configuration-related type aliases - using t directly."""

        type Validator = Callable[[t.GeneralValueType], r[bool]]
        type Builder = Callable[[t.JsonDict], r[t.GeneralValueType]]

        # Tipos de valores de configuração - reuse t
        type ScalarValue = t.ScalarValue
        type ListValue = Sequence[t.ScalarValue]
        type DictValue = Mapping[str, t.ScalarValue | Sequence[t.ScalarValue]]
        type ConfigValue = t.GeneralValueType

        # Settings tipados
        type SettingsDict = t.JsonDict

    class Output:
        """Output-related type aliases."""

        # Use GeneralValueType instead of object for better type safety
        type Formatter = Callable[[t.GeneralValueType], str]
        type Renderer[T] = Callable[[T], r[str]]
        type StreamWriter = Callable[[str], None]

    class Result:
        """Result-related type aliases."""

        # Use GeneralValueType instead of object for better type safety
        type Processor = Callable[[t.GeneralValueType], r[t.GeneralValueType]]
        type Aggregator = Callable[
            [Sequence[t.GeneralValueType]],
            r[t.GeneralValueType],
        ]

    class Session:
        """Session-related type aliases."""

        # Use GeneralValueType instead of object for better type safety
        type Manager = Callable[[], r[t.GeneralValueType]]
        type Validator = Callable[[t.GeneralValueType], bool]

    class Context:
        """Context-related type aliases."""

        # Use JsonDict instead of dict[str, object] and GeneralValueType instead of object
        type Builder = Callable[[t.JsonDict], r[t.GeneralValueType]]
        type Provider = Callable[[], t.GeneralValueType]

    class Plugin:
        """Plugin-related type aliases."""

        # Use GeneralValueType instead of object for better type safety
        type Loader = Callable[[str], r[t.GeneralValueType]]
        type Registry = Mapping[str, t.GeneralValueType]

    class Formatting:
        """Formatting-related type aliases."""

        # Use GeneralValueType instead of object for better type safety
        type Factory = Callable[[str], r[t.GeneralValueType]]
        type Chain = Sequence[t.GeneralValueType]

    class Data:
        """Data-related type aliases - using t.JsonDict for consistency."""

        # Core data types - use t.JsonDict instead of dict[str, object]
        type CliDataDict = t.JsonDict
        type CliFormatData = t.JsonDict
        type CliConfigData = t.JsonDict
        type CliCommandResult = t.JsonDict
        type CliCommandMetadata = t.JsonDict
        type DebugInfoData = t.JsonDict

        # Execution types
        type ExecutionKwargs = t.JsonDict

        # Table data types - for compatibility with examples
        type TableRows = Sequence[t.JsonDict]
        type TabularData = Sequence[t.JsonDict] | t.JsonDict
        type CliConfigMapping = Mapping[str, t.GeneralValueType]

    class Configuration:
        """Configuration schema type aliases - using t.JsonDict."""

        type CliConfigSchema = t.JsonDict
        type SessionConfiguration = t.JsonDict
        type ProfileConfiguration = t.JsonDict

    class CliCommand:
        """Command definition type aliases - using t.JsonDict."""

        type CommandDefinition = t.JsonDict
        type CommandResult = t.JsonDict
        type CommandContext = t.JsonDict

    class Display:
        """Rich display type aliases using Protocols instead of object."""

        # Use FlextCliProtocols.Display for proper typing
        type RichTable = FlextCliProtocols.Display.RichTableProtocol
        type RichTree = FlextCliProtocols.Display.RichTreeProtocol
        type Console = FlextCliProtocols.Display.RichConsoleProtocol

    class Callable:
        """Callable type aliases - now properly typed."""

        # FormatableResult: Types that can be formatted for display
        # Can be dict, list, tuple, str, int, float, bool, None, or FlextResult
        type FormatableResult = (
            dict[str, t.JsonValue]
            | list[t.JsonValue]
            | tuple[t.JsonValue, ...]
            | t.JsonValue
            | r[t.GeneralValueType]
        )

        # ResultFormatter: Function that takes a formattable result and format string
        type ResultFormatter = Callable[[FormatableResult, str], None]

        # HandlerFunction: Generic handler with FlextResult return type
        type HandlerFunction = Callable[..., r[t.GeneralValueType]]

    class Auth:
        """Authentication type aliases."""

        type CredentialsData = Mapping[str, str]

    class Workflow:
        """Workflow type aliases - using t.JsonDict."""

        type WorkflowStepResult = t.JsonDict
        type WorkflowProgress = t.JsonDict

    class Interactive:
        """Interactive display type aliases using Protocols."""

        # Progress uses RichProgressProtocol for typing
        type Progress = FlextCliProtocols.Interactive.RichProgressProtocol
