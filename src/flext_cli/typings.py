"""FlextCli type definitions module - PEP 695 type aliases."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from typing import TypeVar

from flext_core import FlextResult, FlextTypes

from flext_cli.protocols import FlextCliProtocols

# ═══════════════════════════════════════════════════════════════════════════
# TYPEVARS: Único objeto permitido fora da classe
# ═══════════════════════════════════════════════════════════════════════════
# Reutilize de FlextTypes quando existir

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
class FlextCliTypes(FlextTypes):
    """FlextCli type definitions composing with FlextTypes.

    REGRAS:
    ───────
    1. TypeVars fora da classe (único caso permitido)
    2. Type aliases PEP 695 dentro de nested classes
    3. Tipos complexos compostos com Protocols
    4. ZERO aliases simples - use tipos diretos
    5. Composição com FlextTypes, não duplicação
    """

    # Top-level type aliases - direct composition with FlextTypes (no duplication)
    # CliJsonValue uses GeneralValueType for compatibility with DataMapper conversions
    # (GeneralValueType includes datetime, JsonValue does not)
    type CliJsonValue = FlextTypes.GeneralValueType
    type CliJsonDict = FlextTypes.JsonDict
    type CliJsonList = Sequence[FlextTypes.GeneralValueType]

    class Json:
        """CLI JSON types - direct composition with FlextTypes.Json (no duplication)."""

        # Direct aliases to FlextTypes.Json for consistency
        type Value = FlextTypes.Json.JsonValue
        type Dict = FlextTypes.Json.JsonDict
        type List = FlextTypes.Json.JsonList

        # Tipos genéricos usando FlextTypes.JsonValue
        type Handler[T] = Callable[[FlextTypes.JsonValue], FlextResult[T]]
        type Transformer = Callable[[FlextTypes.JsonValue], FlextTypes.JsonValue]
        type Filter = Callable[[FlextTypes.JsonValue], bool]
        type Processor = Callable[[Sequence[FlextTypes.JsonValue]], FlextResult[Sequence[FlextTypes.JsonValue]]]

    class Command:
        """Command-related type aliases."""

        # Tipos concretos ao invés de TypeVars
        # Use GeneralValueType instead of object for better type safety
        type Handler[T] = Callable[[FlextTypes.GeneralValueType], FlextResult[T]]
        type Processor = Callable[[FlextTypes.GeneralValueType], FlextResult[bool]]
        type Collection = Sequence[FlextTypes.GeneralValueType]
        type BatchProcessor = Callable[[Collection], FlextResult[int]]

    class Config:
        """Configuration-related type aliases - using FlextTypes directly."""

        type Validator = Callable[[FlextTypes.GeneralValueType], FlextResult[bool]]
        type Builder = Callable[[FlextTypes.JsonDict], FlextResult[FlextTypes.GeneralValueType]]

        # Tipos de valores de configuração - reuse FlextTypes
        type ScalarValue = FlextTypes.ScalarValue
        type ListValue = Sequence[FlextTypes.ScalarValue]
        type DictValue = Mapping[str, FlextTypes.ScalarValue | Sequence[FlextTypes.ScalarValue]]
        type ConfigValue = FlextTypes.GeneralValueType

        # Settings tipados
        type SettingsDict = FlextTypes.JsonDict

    class Output:
        """Output-related type aliases."""

        # Use GeneralValueType instead of object for better type safety
        type Formatter = Callable[[FlextTypes.GeneralValueType], str]
        type Renderer[T] = Callable[[T], FlextResult[str]]
        type StreamWriter = Callable[[str], None]

    class Result:
        """Result-related type aliases."""

        # Use GeneralValueType instead of object for better type safety
        type Processor = Callable[[FlextTypes.GeneralValueType], FlextResult[FlextTypes.GeneralValueType]]
        type Aggregator = Callable[[Sequence[FlextTypes.GeneralValueType]], FlextResult[FlextTypes.GeneralValueType]]

    class Session:
        """Session-related type aliases."""

        # Use GeneralValueType instead of object for better type safety
        type Manager = Callable[[], FlextResult[FlextTypes.GeneralValueType]]
        type Validator = Callable[[FlextTypes.GeneralValueType], bool]

    class Context:
        """Context-related type aliases."""

        # Use JsonDict instead of dict[str, object] and GeneralValueType instead of object
        type Builder = Callable[[FlextTypes.JsonDict], FlextResult[FlextTypes.GeneralValueType]]
        type Provider = Callable[[], FlextTypes.GeneralValueType]

    class Plugin:
        """Plugin-related type aliases."""

        # Use GeneralValueType instead of object for better type safety
        type Loader = Callable[[str], FlextResult[FlextTypes.GeneralValueType]]
        type Registry = Mapping[str, FlextTypes.GeneralValueType]

    class Formatting:
        """Formatting-related type aliases."""

        # Use GeneralValueType instead of object for better type safety
        type Factory = Callable[[str], FlextResult[FlextTypes.GeneralValueType]]
        type Chain = Sequence[FlextTypes.GeneralValueType]

    class Data:
        """Data-related type aliases - using FlextTypes.JsonDict for consistency."""

        # Core data types - use FlextTypes.JsonDict instead of dict[str, object]
        type CliDataDict = FlextTypes.JsonDict
        type CliFormatData = FlextTypes.JsonDict
        type CliConfigData = FlextTypes.JsonDict
        type CliCommandResult = FlextTypes.JsonDict
        type CliCommandMetadata = FlextTypes.JsonDict
        type DebugInfoData = FlextTypes.JsonDict

        # Execution types
        type ExecutionKwargs = FlextTypes.JsonDict

    class Configuration:
        """Configuration schema type aliases - using FlextTypes.JsonDict."""

        type CliConfigSchema = FlextTypes.JsonDict
        type SessionConfiguration = FlextTypes.JsonDict
        type ProfileConfiguration = FlextTypes.JsonDict

    class CliCommand:
        """Command definition type aliases - using FlextTypes.JsonDict."""

        type CommandDefinition = FlextTypes.JsonDict
        type CommandResult = FlextTypes.JsonDict
        type CommandContext = FlextTypes.JsonDict

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
            dict[str, FlextTypes.JsonValue]
            | list[FlextTypes.JsonValue]
            | tuple[FlextTypes.JsonValue, ...]
            | FlextTypes.JsonValue
            | FlextResult[FlextTypes.GeneralValueType]
        )

        # ResultFormatter: Function that takes a formattable result and format string
        type ResultFormatter = Callable[[FormatableResult, str], None]

        # HandlerFunction: Generic handler with FlextResult return type
        type HandlerFunction = Callable[..., FlextResult[FlextTypes.GeneralValueType]]

    class Auth:
        """Authentication type aliases."""

        type CredentialsData = Mapping[str, str]

    class Workflow:
        """Workflow type aliases - using FlextTypes.JsonDict."""

        type WorkflowStepResult = FlextTypes.JsonDict
        type WorkflowProgress = FlextTypes.JsonDict

    class Interactive:
        """Interactive display type aliases using Protocols."""

        # Progress uses RichProgressProtocol for typing
        type Progress = FlextCliProtocols.Interactive.RichProgressProtocol
