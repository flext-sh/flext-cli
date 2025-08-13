"""Domain compatibility package for legacy imports.

Re-exports modern entities and services using names expected by legacy tests.
"""

from __future__ import annotations

from flext_cli import (
    CLICommand,
    CLIConfiguration,
    CLIContext,
    CLIOutput,
    CLIPlugin,
    CLISession,
    FlextCliCommandStatus as CommandStatus,
    FlextCliPluginState as _PluginState,
    FlextCliSessionState as SessionStatus,
)
from flext_cli.cli_config import CLIConfig
from flext_cli.domain.entities import CommandType

# Provide a PluginStatus that includes legacy INACTIVE alias mapping to UNLOADED
# Direct alias; INACTIVE alias removed for typing strictness compatibility
PluginStatus = _PluginState


__all__ = [
    "CLICommand",
    "CLIConfig",
    "CLIConfiguration",
    "CLIContext",
    "CLIOutput",
    "CLIPlugin",
    "CLISession",
    "CommandStatus",
    "CommandType",
    "PluginStatus",
    "SessionStatus",
]
