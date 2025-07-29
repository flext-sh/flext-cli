"""FLEXT CLI Core - Centralized CLI utilities for all FLEXT projects.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

This package provides standardized CLI components for use across all FLEXT modules.
"""

from __future__ import annotations

# Base classes
from flext_cli.core.base import (
    BaseCLI,
    CLIContext,
    CLIResultRenderer,
    RichCLIRenderer,
    handle_service_result,
    with_context,
)

# Decorators
from flext_cli.core.decorators import (
    async_command,
    confirm_action,
    measure_time,
    require_auth,
    retry,
    validate_config,
    with_spinner,
)

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
