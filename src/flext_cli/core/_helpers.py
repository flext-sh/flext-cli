"""Internal helpers for FlextCli core modules.

Centralized utility functions to eliminate code duplication.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Any

from flext_core import FlextResult


def flext_cli_success(data: Any = None) -> FlextResult[Any]:
    """Create success FlextResult."""
    return FlextResult(success=True, data=data, error=None)


def flext_cli_fail(error: str) -> FlextResult[Any]:
    """Create failure FlextResult."""
    return FlextResult(success=False, data=None, error=error)
