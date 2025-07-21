"""FLEXT CLI - Developer Command Line Interface.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

Built on flext-core foundation for robust command-line functionality.
Uses modern Python 3.13 patterns and clean architecture.
"""

from __future__ import annotations

import contextlib

__version__ = "0.1.0"

# Domain layer exports
# Core layer exports
from flext_cli.core.base import (
    BaseCLI,
    CLIContext,
    CLIResultRenderer,
    RichCLIRenderer,
    handle_service_result,
    with_context,
)
from flext_cli.domain.entities import (
    CLICommand,
    CLIConfig,
    CLIPlugin,
    CLISession,
    CommandStatus,
    CommandType,
)

# Application layer exports (when available)
with contextlib.suppress(ImportError):
    from flext_cli.domain.cli_services import CLIServiceContainer

# CLI exports (when available)
with contextlib.suppress(ImportError):
    from flext_cli.cli import cli
    from flext_cli.client import FlextApiClient

# Core exports that are always available
__all__ = [
    "BaseCLI",
    "CLICommand",
    "CLIConfig",
    "CLIContext",
    "CLIPlugin",
    "CLIResultRenderer",
    "CLIServiceContainer",
    "CLISession",
    "CommandStatus",
    "CommandType",
    "FlextApiClient",
    "RichCLIRenderer",
    "__version__",
    "cli",
    "handle_service_result",
    "with_context",
]
