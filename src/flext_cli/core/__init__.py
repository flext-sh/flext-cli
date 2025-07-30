"""FLEXT CLI Core - Centralized CLI utilities for all FLEXT projects.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

This package provides standardized CLI components for use across all FLEXT modules.
"""

from __future__ import annotations

# Base classes
from flext_cli.core.base import (
    CLIContext,
    handle_service_result,
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
    "CLIContext",
    # Helpers
    "CLIHelper",
    # Decorators
    "async_command",
    "confirm_action",
    "handle_service_result",
    "measure_time",
    "require_auth",
    "retry",
    "validate_config",
    "with_spinner",
]

__version__ = "0.9.0"
