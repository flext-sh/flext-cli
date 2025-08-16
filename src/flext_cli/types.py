"""Compatibility re-exports for tests expecting flext_cli.types.

This module re-exports selected classes and types from the new locations.
"""
from __future__ import annotations

from flext_cli.cli_types import (
    CommandStatus as FlextCliCommandStatus,
    CommandType as FlextCliCommandType,
    OutputFormat as FlextCliOutputFormat,
    PluginStatus as FlextCliPluginStatus,
    PositiveIntType,
)
from flext_cli.core.types import URL, URLType
from flext_cli.models import (
    FlextCliCommand,
    FlextCliConfiguration as FlextCliConfig,
    FlextCliContext,
    FlextCliPlugin,
    FlextCliSession,
)

# Legacy testing aliases for type variables used in tests
TCliData = dict[str, object]
TCliPath = str
TCliFormat = str
TCliHandler = object
TCliConfig = dict[str, object]
TCliArgs = dict[str, object]

__all__ = [
    "URL",
    "FlextCliCommand",
    "FlextCliCommandStatus",
    "FlextCliCommandType",
    "FlextCliConfig",
    "FlextCliContext",
    "FlextCliOutputFormat",
    "FlextCliPlugin",
    "FlextCliPluginStatus",
    "FlextCliSession",
    "PositiveIntType",
    # Legacy aliases
    "TCliArgs",
    "TCliConfig",
    "TCliData",
    "TCliFormat",
    "TCliHandler",
    "TCliPath",
    "URLType",
]
