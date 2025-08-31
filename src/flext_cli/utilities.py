"""FLEXT CLI Utilities - Single unique CLI utilities class.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import ClassVar

from flext_core import FlextUtilities


class FlextCliUtilities(FlextUtilities):
    """CLI-specific utilities extending flext-core FlextUtilities.

    Single unique class for the module following flext-core inheritance patterns.
    All functionality should be available through FlextUtilities base class.
    """

    # Reference to flext-core utilities for inheritance
    Core: ClassVar = FlextUtilities


# =============================================================================
# EXPORTS - Single unique class following user requirements
# =============================================================================

__all__ = [
    "FlextCliUtilities",
]
