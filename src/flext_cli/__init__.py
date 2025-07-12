"""FLEXT CLI - Developer Command Line Interface.

Copyright (c) 2025 FLEXT Team. All rights reserved.

Built on flext-core foundation for robust command-line functionality.
Uses modern Python 3.13 patterns and clean architecture.
"""

from __future__ import annotations

__version__ = "0.1.0"

# Domain layer exports
from flext_cli.core.base import BaseCLI

# Core layer exports
from flext_cli.core.base import CLIContext
from flext_cli.core.base import CLIResultRenderer
from flext_cli.core.base import RichCLIRenderer
from flext_cli.core.base import handle_service_result
from flext_cli.core.base import with_context
from flext_cli.domain.entities import CLICommand
from flext_cli.domain.entities import CLIConfig
from flext_cli.domain.entities import CLIPlugin
from flext_cli.domain.entities import CLISession
from flext_cli.domain.entities import CommandStatus
from flext_cli.domain.entities import CommandType

# Application layer exports (when available)
try:
    from flext_cli.application.services import CLIService
    from flext_cli.application.services import CommandService
except ImportError:
    # Application layer not yet refactored
    pass

# CLI exports (when available)
try:
    from flext_cli.cli import cli
    from flext_cli.client import FlextApiClient
except ImportError:
    # CLI modules have syntax errors, will be refactored
    pass

# Core exports that are always available
__all__ = [
    "BaseCLI",
    # Domain entities
    "CLICommand",
    "CLIConfig",
    # Core components
    "CLIContext",
    "CLIPlugin",
    "CLIResultRenderer",
    "CLIService",
    "CLISession",
    # Application services (when available)
    "CommandService",
    "CommandStatus",
    "CommandType",
    "FlextApiClient",
    "RichCLIRenderer",
    # Version
    "__version__",
    # CLI components (when available)
    "cli",
    "handle_service_result",
    "with_context",
]
