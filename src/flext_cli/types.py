"""Types facade exposing public, stable names.

This consolidates and standardizes public exports expected by dependents/tests,
while delegating implementation to modern modules.
"""

from __future__ import annotations

from flext_cli.cli_types import (  # noqa: F401
    CommandStatus,
    CommandType,
    FlextCliRenderResult,
    FlextCliTableResult,
    OutputFormat,
    PathType,  # re-export for convenience
    PluginStatus,
    PositiveIntType,  # re-export for convenience
    SessionStatus,
    URLType,  # re-export for convenience
)
from flext_cli.config import CLIConfig as FlextCliConfig
from flext_cli.domain.cli_context import (
    CLIContext,
    CLIExecutionContext,
)
from flext_cli.domain.entities import (
    CLICommand,
    CLICommand as FlextCliCommand,
    CLIPlugin,
    CLISession,
)

# Legacy type aliases from legacy module to satisfy tests
from flext_cli.legacy import (
    FlextCliCommandType,
    TCliArgs,
    TCliConfig,
    TCliData,
    TCliFormat,
    TCliHandler,
    TCliPath,
)

# Legacy enums expected by tests under these names
from flext_cli.models import (
    FlextCliCommandStatus,
    FlextCliContext,
    FlextCliOutputFormat,
    FlextCliPlugin,
    FlextCliPluginState,
    FlextCliSession,
    FlextCliSessionState,
)

__all__ = [
    "CLICommand",
    "CLIContext",
    "CLIExecutionContext",
    "CLIPlugin",
    "CLISession",
    # Enums and statuses
    "CommandStatus",
    "CommandType",
    "FlextCliCommand",
    "FlextCliCommandStatus",
    # Legacy type aliases
    "FlextCliCommandType",
    # Primary public API
    "FlextCliConfig",
    "FlextCliContext",
    "FlextCliOutputFormat",
    "FlextCliPlugin",
    "FlextCliPluginState",
    "FlextCliSession",
    "FlextCliSessionState",
    # Formatting types
    "OutputFormat",
    "PathType",
    "PluginStatus",
    "PositiveIntType",
    "SessionStatus",
    "TCliArgs",
    "TCliConfig",
    "TCliData",
    "TCliFormat",
    "TCliHandler",
    "TCliPath",
    # Click param types
    "URLType",
]
