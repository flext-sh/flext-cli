"""Type definitions for flext-cli."""

from typing import Protocol, TypeVar

from flext_cli.cli_config import CLIConfig as FlextCliConfig
from flext_cli.models import (
    FlextCliCommand,
    FlextCliCommandStatus,
    FlextCliCommandType,
    FlextCliContext,
    FlextCliOutputFormat,
    FlextCliPlugin,
    FlextCliPluginState,
    FlextCliSession,
    FlextCliSessionState,
)

TCliPath = str
TCliFormat = str
TCliData = dict[str, object] | list[object] | str | int | float | bool | None

_TResult = TypeVar("_TResult")


class TCliHandler(Protocol[_TResult]):  # type: ignore[misc]
    """Protocol for CLI command handlers."""

    def __call__(self, *args: object, **kwargs: object) -> _TResult: ...


TCliConfig = dict[str, object]
TCliArgs = dict[str, object]

# Legacy enums expected by tests under these names

__all__ = [
    # Models imported from flext_cli.models (sorted)
    "FlextCliCommand",
    "FlextCliCommandStatus",
    "FlextCliCommandType",
    "FlextCliConfig",
    "FlextCliContext",
    "FlextCliOutputFormat",
    "FlextCliPlugin",
    "FlextCliPluginState",
    "FlextCliSession",
    "FlextCliSessionState",
    # Local type definitions (sorted)
    "TCliArgs",
    "TCliConfig",
    "TCliData",
    "TCliFormat",
    "TCliHandler",
    "TCliPath",
    "_TResult",
]
