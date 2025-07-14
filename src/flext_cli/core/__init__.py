"""FLEXT CLI Core - Centralized CLI utilities for all FLEXT projects.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

This package provides standardized CLI components for use across all FLEXT modules.
"""

# Base classes
from flext_cli.core.base import BaseCLI
from flext_cli.core.base import CLIContext
from flext_cli.core.base import CLIResultRenderer
from flext_cli.core.base import RichCLIRenderer
from flext_cli.core.base import handle_service_result
from flext_cli.core.base import with_context

# Decorators
from flext_cli.core.decorators import async_command
from flext_cli.core.decorators import confirm_action
from flext_cli.core.decorators import measure_time
from flext_cli.core.decorators import require_auth
from flext_cli.core.decorators import retry
from flext_cli.core.decorators import validate_config
from flext_cli.core.decorators import with_spinner

# Helpers
from flext_cli.core.helpers import CLIHelper

__all__ = [
    # Base classes
    "BaseCLI",
    "CLIContext",
    # Helpers
    "CLIHelper",
    "CLIResultRenderer",
    "RichCLIRenderer",
    # Decorators
    "async_command",
    "confirm_action",
    "handle_service_result",
    "measure_time",
    "require_auth",
    "retry",
    "validate_config",
    "with_context",
    "with_spinner",
]

__version__ = "0.7.0"
