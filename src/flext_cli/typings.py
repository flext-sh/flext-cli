"""FlextCli type definitions module - PEP 695 type aliases."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from typing import TypeVar

from flext_core import FlextResult, FlextTypes

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

    class Json:
        """CLI JSON types with collections.abc patterns."""

        # Tipos usando collections.abc (não typing)
        type Value = dict[str, Value] | list[Value] | str | int | float | bool | None
        type Dict = dict[str, Value]
        type List = list[Value]

        # Tipos genéricos
        type Handler[T] = Callable[[Value], FlextResult[T]]
        type Transformer = Callable[[Value], Value]
        type Filter = Callable[[Value], bool]
        type Processor = Callable[[List], FlextResult[List]]

    class Command:
        """Command-related type aliases."""

        # Tipos concretos ao invés de TypeVars
        type Handler[T] = Callable[[object], FlextResult[T]]
        type Processor = Callable[[object], FlextResult[bool]]
        type Collection = Sequence[object]
        type BatchProcessor = Callable[[Collection], FlextResult[int]]

    class Config:
        """Configuration-related type aliases."""

        type Validator = Callable[[object], FlextResult[bool]]
        type Builder = Callable[[dict[str, object]], FlextResult[object]]

        # Tipos de valores de configuração
        type ScalarValue = str | int | float | bool
        type ListValue = Sequence[ScalarValue]
        type DictValue = Mapping[str, ScalarValue | ListValue]
        type ConfigValue = ScalarValue | ListValue | DictValue

        # Settings tipados
        type SettingsDict = Mapping[str, ConfigValue]

    class Output:
        """Output-related type aliases."""

        type Formatter = Callable[[object], str]
        type Renderer[T] = Callable[[T], FlextResult[str]]
        type StreamWriter = Callable[[str], None]

    class Result:
        """Result-related type aliases."""

        type Processor = Callable[[object], FlextResult[object]]
        type Aggregator = Callable[[Sequence[object]], FlextResult[object]]

    class Session:
        """Session-related type aliases."""

        type Manager = Callable[[], FlextResult[object]]
        type Validator = Callable[[object], bool]

    class Context:
        """Context-related type aliases."""

        type Builder = Callable[[dict[str, object]], FlextResult[object]]
        type Provider = Callable[[], object]

    class Plugin:
        """Plugin-related type aliases."""

        type Loader = Callable[[str], FlextResult[object]]
        type Registry = Mapping[str, object]

    class Formatting:
        """Formatting-related type aliases."""

        type Factory = Callable[[str], FlextResult[object]]
        type Chain = Sequence[object]

    class Data:
        """Data-related type aliases."""

        # Core data types
        type CliDataDict = dict[str, object]
        type CliConfigData = dict[str, object]
        type CliCommandResult = dict[str, object]
        type CliCommandMetadata = dict[str, object]
        type DebugInfoData = dict[str, object]

        # Execution types
        type ExecutionKwargs = dict[str, object]
