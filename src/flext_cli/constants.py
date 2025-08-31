"""FLEXT CLI Constants - Single unique CLI constants class.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import ClassVar

from flext_core import FlextConstants


class FlextCliConstants(FlextConstants):
    """CLI-specific constants extending flext-core FlextConstants.

    Single unique class for the module following flext-core inheritance patterns.
    All functionality should be available through FlextConstants base class.
    """

    # Reference to flext-core constants for inheritance
    Core: ClassVar = FlextConstants


# =============================================================================
# EXPORTS - Single unique class following user requirements
# =============================================================================

__all__ = [
    "FlextCliConstants",
]
