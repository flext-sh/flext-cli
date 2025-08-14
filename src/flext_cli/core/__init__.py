"""Core primitives for the FLEXT CLI package.

Exposes selected symbols for test patching convenience (backward-compat).
"""

from __future__ import annotations

from flext_core import FlextUtilities as FlextUtilities  # reexport for tests

# Reexport CLI models so tests can patch via flext_cli.core.FlextCli* names
from flext_cli.models import (
    FlextCliCommand as FlextCliCommand,
    FlextCliPlugin as FlextCliPlugin,
    FlextCliSession as FlextCliSession,
)

__all__ = [
    "FlextCliCommand",
    "FlextCliPlugin",
    "FlextCliSession",
    "FlextUtilities",
]
