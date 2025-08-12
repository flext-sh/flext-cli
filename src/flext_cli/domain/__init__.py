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
try:
    # Create a runtime alias object with extra attribute for compatibility
    PluginStatus = _PluginState  # type: ignore[assignment]
    # Attach INACTIVE as alias to UNLOADED on the enum class dynamically
    PluginStatus.INACTIVE = PluginStatus.UNLOADED  # type: ignore[attr-defined]
except Exception:  # pragma: no cover - fallback
    PluginStatus = _PluginState  # type: ignore[assignment]


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
