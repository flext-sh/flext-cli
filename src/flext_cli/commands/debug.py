"""Debug commands shim for tests.

Exposes a module matching legacy path and re-exports from `cmd_debug`.
"""

from __future__ import annotations

import sys
from pathlib import Path

from rich.table import Table

from flext_cli.cmd_debug import (
    FLEXT_API_AVAILABLE,
    SENSITIVE_VALUE_PREVIEW_LENGTH,
    _validate_dependencies,
    connectivity,
    debug_cmd,
    env,
    get_config,
    get_default_cli_client,
    paths,
    performance,
    trace,
    validate,
)

__all__ = [
    "FLEXT_API_AVAILABLE",
    "SENSITIVE_VALUE_PREVIEW_LENGTH",
    "Path",
    "Table",
    "_validate_dependencies",
    "connectivity",
    "debug_cmd",
    "env",
    "get_config",
    "get_default_cli_client",
    "paths",
    "performance",
    # Re-exports for tests patching
    "sys",
    "trace",
    "validate",
]
