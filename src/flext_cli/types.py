"""Type definitions for flext-cli."""

from typing import Protocol, TypeVar

from flext_cli.models import (
    FlextCliCommandStatus,
    FlextCliContext,
    FlextCliOutputFormat,
    FlextCliPlugin,
    FlextCliPluginState,
    FlextCliSession,
    FlextCliSessionState,
)

TCliPath = str
TCliFormat = str

_TResult = TypeVar("_TResult")


class TCliHandler(Protocol[_TResult]):  # type: ignore[misc]
    """Protocol for CLI command handlers."""

    def __call__(self, *args: object, **kwargs: object) -> _TResult: ...


TCliConfig = dict[str, object]
TCliArgs = dict[str, object]

# Legacy enums expected by tests under these names

__all__ = [
    # Models imported from flext_cli.models
    "FlextCliCommandStatus",
    "FlextCliContext",
    "FlextCliOutputFormat",
    "FlextCliPlugin",
    "FlextCliPluginState",
    "FlextCliSession",
    "FlextCliSessionState",
    # Local type definitions
    "TCliArgs",
    "TCliConfig",
    "TCliFormat",
    "TCliHandler",
    "TCliPath",
    "_TResult",
]
